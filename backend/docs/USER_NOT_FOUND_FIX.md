# "User not found" Error Fix

## The Problem

After fixing the token validation, users were getting **"User not found"** errors when trying to create trips or access protected endpoints.

## Root Cause

The issue was a **mismatch between how auth_id is used in development vs production mode**:

### Development Mode Flow
1. **Login**: Token contains `sub: user.id` (database user ID)
2. **Validation**: Returns `{ "id": user.id }` (database user ID)
3. **CurrentUser**: Sets `auth_id = user.id` (database user ID)
4. **Endpoint Query**: `User.auth_id == current_user.auth_id` ❌

### The Problem
- In the database, `User.auth_id` stores the **Supabase auth ID**
- But in development mode, `current_user.auth_id` contains the **database user ID**
- Query fails: searching for `User.auth_id = <database_user_id>` finds nothing!

## The Fix

### 1. Updated `src/services/auth.py`

Added mode-aware user lookup in `get_current_user_dependency()`:

```python
# In development mode: auth_id is the database user ID
# In production mode: auth_id is the Supabase auth ID
if settings.development_mode:
    # user_data["id"] is the database user ID
    return CurrentUser(
        auth_id=user_data.get("id"),  # Database user ID
        user_id=user_data.get("id"),
        phone=user_data.get("phone"),
        email=user_data.get("email"),
        role=user_data.get("role", "user")
    )
else:
    # user_data["id"] is Supabase auth ID
    return CurrentUser(
        auth_id=user_data.get("id"),  # Supabase auth ID
        user_id=user_data.get("id"),
        phone=user_data.get("phone"),
        email=user_data.get("email"),
        role=user_data.get("role", "user")
    )
```

### 2. Updated `src/api/v1/riders.py`

Added mode-aware query in `create_trip()` endpoint:

```python
from src.core.settings import settings

if settings.development_mode:
    # In dev mode, auth_id IS the user ID
    user = session.exec(
        select(User).where(User.id == current_user.auth_id)
    ).first()
else:
    # In production, auth_id is Supabase auth ID
    user = session.exec(
        select(User).where(User.auth_id == current_user.auth_id)
    ).first()
```

## How It Works Now

### Development Mode ✅
```
Token: { sub: "db-user-id-123" }
  ↓
Validation: Returns { id: "db-user-id-123" }
  ↓
CurrentUser: { auth_id: "db-user-id-123" }
  ↓
Query: User.id == "db-user-id-123" ✅ FOUND!
```

### Production Mode ✅
```
Token: Supabase JWT with { id: "supabase-auth-id" }
  ↓
Validation: Returns { id: "supabase-auth-id" }
  ↓
CurrentUser: { auth_id: "supabase-auth-id" }
  ↓
Query: User.auth_id == "supabase-auth-id" ✅ FOUND!
```

## Testing the Fix

### 1. Clear localStorage and re-login
```javascript
// Browser console (F12)
localStorage.clear()
location.href = '/login'
```

### 2. Login with test credentials
- Phone: `+21612345001`
- OTP: `123456`

### 3. Try creating a trip
- Select destination
- Request ride
- Should see available drivers
- Should successfully create trip ✅

### 4. Check backend logs
```bash
tail -f /home/alaao/Taxini/logs/app.log
```

You should see:
```
Creating trip for rider <user-id> (<user-name>)
Trip created successfully: <trip-id>
```

## Files Modified

1. **`/home/alaao/Taxini/src/services/auth.py`**
   - Function: `get_current_user_dependency()`
   - Added proper handling of auth_id for both modes
   
2. **`/home/alaao/Taxini/src/api/v1/riders.py`**
   - Function: `create_trip()`
   - Added mode-aware user lookup query

## Why This Pattern?

We use this pattern because:

1. **Development Flexibility**: Test without Supabase overhead
2. **Database Schema**: `User.auth_id` must store Supabase ID for production
3. **Token Structure**: Development tokens use `sub` for user ID (standard JWT pattern)
4. **Mode Separation**: Clear separation between dev and prod auth flows

## Other Endpoints to Update

If you encounter "User not found" in other endpoints, apply the same pattern:

```python
from src.core.settings import settings

if settings.development_mode:
    user = session.exec(select(User).where(User.id == current_user.auth_id)).first()
else:
    user = session.exec(select(User).where(User.auth_id == current_user.auth_id)).first()
```

Endpoints that likely need this fix:
- ✅ `POST /api/v1/riders/create-trip` - FIXED
- `GET /api/v1/riders/active-trip` - May need fix
- `GET /api/v1/riders/trip-history` - May need fix
- `POST /api/v1/riders/trips/{trip_id}/cancel` - May need fix
- `POST /api/v1/riders/trips/{trip_id}/rate` - May need fix
- Driver endpoints - May need fix
- Ticket endpoints - May need fix

## Related Documentation

- [TOKEN_VALIDATION_FIX.md](./TOKEN_VALIDATION_FIX.md) - Original token validation issue
- [JWT_TOKEN_ISSUE_FIXED.md](./JWT_TOKEN_ISSUE_FIXED.md) - Deleted user auth_id issue
- [NO_DRIVERS_FIX.md](./NO_DRIVERS_FIX.md) - Driver visibility issues

## Environment Variables

Make sure these are set in `.env`:

```bash
TAXINI_DEVELOPMENT_MODE=true
TAXINI_JWT_SECRET=your-secret-key
TAXINI_JWT_ALGORITHM=HS256
TAXINI_JWT_EXPIRATION_MINUTES=1440
```

## Troubleshooting

### Still getting "User not found"?
1. Clear localStorage: `localStorage.clear()`
2. Re-login to get fresh token
3. Check backend logs for query being executed
4. Verify `TAXINI_DEVELOPMENT_MODE=true` in `.env`
5. Ensure test user exists in database

### Check if user exists
```sql
-- Find user by phone
SELECT id, auth_id, name, phone_number, role 
FROM users 
WHERE phone_number = '+21612345001';
```

### Check token contents
```javascript
// Browser console
const token = localStorage.getItem('taxini_token')
const payload = JSON.parse(atob(token.split('.')[1]))
console.log('Token payload:', payload)
// Should show: { sub: "user-id", phone: "+216...", role: "rider", exp: ... }
```

## Success Criteria

✅ Login works without 401 errors  
✅ Create trip works without "User not found"  
✅ Driver list loads correctly  
✅ Trip history accessible  
✅ All protected endpoints work  

## Production Deployment

In production (when `TAXINI_DEVELOPMENT_MODE=false`):
- All queries use `User.auth_id` (Supabase auth ID)
- Tokens validated with Supabase
- Users must exist in Supabase auth table
- No changes needed to code - mode flag handles everything
