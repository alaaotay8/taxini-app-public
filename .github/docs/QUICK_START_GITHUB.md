# 🚀 Quick Start: GitHub Deployment

This is a **simplified guide** to get your project on GitHub fast.

## Prerequisites

- Git installed: `sudo apt install git` (if not already installed)
- GitHub account
- All code tested and working locally

---

## Option 1: Automated Setup (Recommended)

```bash
# Make the script executable
chmod +x ~/setup-github.sh

# Run the setup script
bash ~/setup-github.sh

# Follow the on-screen instructions
```

The script will:
- ✅ Create proper directory structure
- ✅ Copy backend and frontend
- ✅ Create .gitignore
- ✅ Sanitize environment files
- ✅ Initialize git repository
- ✅ Create initial commit

---

## Option 2: Manual Setup

### Step 1: Create Structure

```bash
# Create project directory
mkdir -p ~/taxini-app
cd ~/taxini-app

# Copy backend and frontend
cp -r ~/Taxini backend
cp -r ~/Taxini-Frontend frontend

# Create docs folder
mkdir -p docs
```

### Step 2: Copy Documentation

```bash
# Copy existing docs
cp ~/SECURITY_ENHANCEMENTS.md docs/SECURITY.md
cp ~/PERFORMANCE_OPTIMIZATIONS.md docs/PERFORMANCE.md
cp ~/CODE_CLEANUP_SUMMARY.md docs/ARCHITECTURE.md
```

### Step 3: Create Environment Templates

```bash
# Backend
cd backend
cp .env .env.example
# Edit .env.example and replace secrets with placeholders

# Frontend
cd ../frontend
cp .env .env.example
# Edit .env.example and replace secrets with placeholders

cd ..
```

### Step 4: Initialize Git

```bash
cd ~/taxini-app

# Create .gitignore
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
echo "" >> .gitignore
curl -o temp.gitignore https://raw.githubusercontent.com/github/gitignore/main/Node.gitignore
cat temp.gitignore >> .gitignore
rm temp.gitignore

# Add critical ignores
cat >> .gitignore << 'EOF'
.env
.env.local
**/.env
TEST_CREDENTIALS.txt
**/TEST_CREDENTIALS.txt
EOF

# Initialize git
git init
git add .
git commit -m "Initial commit: Taxini platform"
```

---

## Step 5: Create GitHub Repository

### On GitHub Website:

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `taxini-app`
3. Description: `Modern taxi booking platform - FastAPI + Vue 3`
4. Choose **Public** or **Private**
5. **⚠️ Important:** Do NOT check "Add README", "Add .gitignore", or "Choose license"
6. Click **Create repository**

---

## Step 6: Push to GitHub

```bash
cd ~/taxini-app

# Add remote (REPLACE YOUR_USERNAME with your GitHub username!)
git remote add origin https://github.com/YOUR_USERNAME/taxini-app.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### If You Get Authentication Error:

Use a Personal Access Token (PAT):

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Select scopes: `repo`, `workflow`
4. Generate and copy token
5. When pushing, use token as password:
   ```bash
   git push -u origin main
   # Username: YOUR_USERNAME
   # Password: YOUR_TOKEN
   ```

---

## Step 7: Deploy (Choose One)

### Railway (Easiest - Recommended)

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select `taxini-app`
5. Click **"+ New"** → Add **Backend Service**:
   - Root Directory: `backend`
   - Start Command: `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
6. Click **"+ New"** → Add **Frontend Service**:
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview`
7. Click **"+ New"** → Add **PostgreSQL Database**
8. Add environment variables (see below)
9. Deploy! 🚀

### Vercel (Frontend Only)

```bash
cd ~/taxini-app/frontend
npm install -g vercel
vercel login
vercel --prod
```

---

## Environment Variables for Deployment

### Backend (Railway)

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
TAXINI_JWT_SECRET=your-super-secret-jwt-key
TAXINI_API_KEY=your-api-key
TAXINI_MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token
TAXINI_DEVELOPMENT_MODE=false
```

### Frontend (Railway/Vercel)

```
VITE_API_BASE_URL=https://your-backend-url.railway.app/api/v1
VITE_API_KEY=your-api-key
VITE_MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token
```

---

## Verification Checklist

After deployment:

- [ ] Visit backend docs: `https://your-backend.railway.app/docs`
- [ ] Visit frontend: `https://your-frontend.railway.app`
- [ ] Test user registration
- [ ] Test login
- [ ] Test creating a trip
- [ ] Check database has data

---

## Common Issues

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/taxini-app.git
```

### "Permission denied (publickey)"
Use HTTPS instead of SSH, or [setup SSH keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

### ".env files are committed to git"
```bash
# Remove from git history
git rm --cached .env backend/.env frontend/.env
git commit -m "Remove .env files"
git push
```

### "Backend can't connect to database"
Check `DATABASE_URL` environment variable in Railway dashboard

---

## Need More Help?

- Full guide: See `DEPLOYMENT_GUIDE.md`
- Documentation: Check `docs/` folder
- Backend API: Visit `/docs` endpoint

---

**Happy deploying! 🎉**
