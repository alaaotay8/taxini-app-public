# Token Validation Fix - Development vs Production Mode

## The Problem

Users were getting **401 Unauthorized** errors immediately after logging in, with the error message:
```
Token validation failed: invalid JWT: unable to parse or verify signature
```

## Root Cause Analysis

The application has **two different token generation modes**:

### Development Mode (TAXINI_DEVELOPMENT_MODE=true)
- **Login**: Backend generates a **custom JWT token** using `jwt.encode()` with the app's `JWT_SECRET`
- **Token Structure**: 
  ```json
  {
    "sub": "user_id",
    "phone": "+216...",
    "role": "rider",
    "exp": 1234567890
  }
  ```

### Production Mode (TAXINI_DEVELOPMENT_MODE=false)
- **Login**: Backend uses **Supabase OTP** and returns a **Supabase JWT token**
- **Token Structure**: Supabase's own JWT format with `auth_id` and session data

## The Bug

**Before the fix**, the token validation logic **always tried to validate tokens with Supabase**, regardless of mode:

```python
# ❌ OLD CODE - Always uses Supabase validation
def get_user_by_token(access_token: str):
    client = supabase_client.ensure_supabase_client()
    response = client.auth.get_user(access_token)  # ❌ Fails for custom JWT!
```

**What happened:**
1. ✅ User logs in → Backend generates custom JWT token
2. ✅ Frontend stores token and makes request to `/api/v1/riders/active-trip`
3. ❌ Backend tries to validate custom JWT with Supabase
4. ❌ Supabase rejects the token (it didn't issue it!)
5. ❌ Backend returns 401 Unauthorized
6. ❌ Frontend auto-logout kicks in (now removed)

## The Fix

**After the fix**, the token validation respects the mode:

```python
# ✅ NEW CODE - Mode-aware validation
def get_user_by_token(access_token: str):
    if settings.development_mode:
        # Validate custom JWT with app's JWT_SECRET
        payload = jwt.decode(
            access_token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm]
        )
        return {
            "success": True,
            "user": {
                "id": payload.get("sub"),
                "phone": payload.get("phone"),
                "role": payload.get("role")
            }
        }
    else:
        # Validate Supabase JWT
        client = supabase_client.ensure_supabase_client()
        response = client.auth.get_user(access_token)
        return normalized_response
```

## Files Modified

### 1. `/home/alaao/Taxini/src/services/auth.py`
- **Function**: `get_user_by_token()`
- **Change**: Added development mode check to decode custom JWT locally
- **Benefits**: 
  - Custom JWTs validated correctly
  - Expired tokens properly detected
  - No dependency on Supabase in dev mode

### 2. `/home/alaao/Taxini-Frontend/src/services/api.js`
- **Change**: Removed auto-logout on 401 errors
- **Reason**: Root cause fixed, no need for workaround
- **Benefits**: Cleaner error handling, no logout loops

## Testing the Fix

### 1. Clear Old Tokens
```bash
# In browser console (F12)
localStorage.clear()
location.reload()
```

### 2. Login Again
- Phone: `+21612345001`
- OTP: `123456` (development mode)

### 3. Verify Token Works
- Check that you stay logged in
- Try creating a trip
- Check that API requests don't return 401

### 4. Check Backend Logs
You should see:
```
🔓 DEVELOPMENT MODE: OTP = 123456 for phone +21612345001
🔓 DEVELOPMENT MODE: OTP verified for phone +21612345001
```

## Environment Configuration

Make sure these are set in `/home/alaao/Taxini/.env`:

```bash
# Required for development mode
TAXINI_DEVELOPMENT_MODE=true
TAXINI_JWT_SECRET=your-secret-key-here
TAXINI_JWT_ALGORITHM=HS256
TAXINI_JWT_EXPIRATION_MINUTES=1440
```

## Production Deployment Notes

In production (TAXINI_DEVELOPMENT_MODE=false):
- Custom JWT logic is **skipped**
- All authentication goes through **Supabase**
- Tokens validated with `client.auth.get_user()`
- Users must be in Supabase auth table

## Why This Matters

This fix is critical because:
1. **Development workflow**: Developers can test without Supabase SMS credits
2. **Token consistency**: Same token format throughout the request lifecycle
3. **Security**: Proper JWT validation with expiration checks
4. **User experience**: No unexpected logouts

## Related Issues

- **JWT Token Issue**: [JWT_TOKEN_ISSUE_FIXED.md](./JWT_TOKEN_ISSUE_FIXED.md) - Old tokens with deleted user IDs
- **No Drivers Fix**: [NO_DRIVERS_FIX.md](./NO_DRIVERS_FIX.md) - Driver visibility issues

## Technical Details

### JWT Payload Structure (Development Mode)
```json
{
  "sub": "uuid-of-user",           // User ID from users table
  "phone": "+21612345001",         // User's phone number
  "role": "rider",                 // User role (rider/driver/admin)
  "exp": 1734567890                // Expiration timestamp
}
```

### Token Validation Flow
```
Frontend Request
    ↓
Authorization: Bearer <token>
    ↓
Backend: api.py (request interceptor)
    ↓
AuthService.get_current_user_dependency()
    ↓
AuthService.get_user_by_token(token)
    ↓
[IF development_mode]
    → jwt.decode(token, JWT_SECRET) ✅
[ELSE]
    → client.auth.get_user(token) ✅
    ↓
CurrentUser object returned to endpoint
```

## Troubleshooting

### Still getting 401 errors?
1. Clear localStorage: `localStorage.clear()`
2. Check backend logs for token validation messages
3. Verify `TAXINI_DEVELOPMENT_MODE=true` in `.env`
4. Restart backend: `pkill -f uvicorn && uvicorn main:app --reload`

### Token expired error?
- Development tokens expire after 1440 minutes (24 hours)
- Increase with `TAXINI_JWT_EXPIRATION_MINUTES` if needed
- Or just login again to get a new token

### Supabase errors in development?
- Safe to ignore if `TAXINI_DEVELOPMENT_MODE=true`
- Token validation doesn't use Supabase in dev mode
- Check that `.env` has `DEVELOPMENT_MODE=true`
