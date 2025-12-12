# 🚀 GitHub Setup & Deployment Guide

This guide will walk you through preparing your Taxini project for GitHub and deployment.

## 📋 Table of Contents
1. [Project Structure Setup](#project-structure-setup)
2. [Git Configuration](#git-configuration)
3. [GitHub Repository Setup](#github-repository-setup)
4. [Deployment Options](#deployment-options)
5. [Post-Deployment](#post-deployment)

---

## 1. Project Structure Setup

We'll create a **monorepo** (single repository) structure with both frontend and backend:

### Step 1.1: Create Project Directory Structure

```bash
# Create main project directory
mkdir -p ~/taxini-app
cd ~/taxini-app

# Copy backend (rename from Taxini to backend)
cp -r ~/Taxini backend

# Copy frontend (rename from Taxini-Frontend to frontend)
cp -r ~/Taxini-Frontend frontend

# Copy documentation
mkdir -p docs
cp ~/SECURITY_ENHANCEMENTS.md docs/SECURITY.md
cp ~/PERFORMANCE_OPTIMIZATIONS.md docs/PERFORMANCE.md
cp ~/CODE_CLEANUP_SUMMARY.md docs/CODE_CLEANUP_SUMMARY.md
cp ~/APPLICATION_IMPROVEMENTS_SUMMARY.md docs/IMPROVEMENTS.md
```

### Step 1.2: Clean Up Sensitive Files

```bash
cd ~/taxini-app

# Remove test credentials
rm -f TEST_CREDENTIALS.txt

# Create environment example files (without sensitive data)
cd backend
cp .env .env.example
# Edit .env.example and replace actual secrets with placeholders
# Example: JWT_SECRET=your-super-secret-jwt-key-change-this

cd ../frontend
cp .env .env.example
# Edit .env.example and replace actual secrets with placeholders
```

---

## 2. Git Configuration

### Step 2.1: Create .gitignore Files

Create `~/taxini-app/.gitignore`:

```bash
cat > ~/taxini-app/.gitignore << 'EOF'
# Environment variables (NEVER commit these!)
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.venv/
venv/
ENV/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
.cache/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Test credentials (CRITICAL - never commit!)
TEST_CREDENTIALS.txt
test_credentials.*

# Deployment
.vercel
.netlify
railway.json

# Temporary files
*.tmp
*.temp
.temp/
tmp/
EOF
```

### Step 2.2: Initialize Git Repository

```bash
cd ~/taxini-app

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Taxini taxi booking platform

- FastAPI backend with PostgreSQL
- Vue 3 frontend with Mapbox integration
- Real-time location tracking
- Trip management for riders and drivers
- Admin dashboard
- Comprehensive documentation"
```

---

## 3. GitHub Repository Setup

### Step 3.1: Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click the **"+"** icon → **"New repository"**
3. Repository settings:
   - **Name**: `taxini-app` (or your preferred name)
   - **Description**: "Modern taxi booking platform with real-time tracking - FastAPI + Vue 3"
   - **Visibility**: Choose **Public** or **Private**
   - ⚠️ **Do NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

### Step 3.2: Connect Local Repository to GitHub

```bash
cd ~/taxini-app

# Add GitHub remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/taxini-app.git

# Verify remote was added
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3.3: Set Up Repository Settings on GitHub

1. Go to your repository on GitHub
2. Click **"Settings"** tab
3. Under **"Security"**:
   - Enable **"Vulnerability alerts"**
   - Enable **"Dependabot security updates"**

4. Under **"Secrets and variables"** → **"Actions"**:
   - Add repository secrets (for CI/CD if needed):
     - `DATABASE_URL`
     - `JWT_SECRET`
     - `API_KEY`
     - `MAPBOX_ACCESS_TOKEN`
     - etc.

---

## 4. Deployment Options

### Option A: Railway (Recommended - Easiest for Monorepo)

**Advantages:**
- ✅ Supports monorepo out of the box
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy PostgreSQL database
- ✅ Simple environment variable management

**Steps:**

1. **Go to [Railway.app](https://railway.app)**

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub
   - Select `taxini-app` repository

3. **Add Services**

   **Backend Service:**
   - Click "+ New"
   - Select "GitHub Repo"
   - Service name: `backend`
   - Settings:
     - Root Directory: `backend`
     - Build Command: (leave empty)
     - Start Command: `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variables:
     ```
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     JWT_SECRET=your-super-secret-key
     API_KEY=your-api-key
     MAPBOX_ACCESS_TOKEN=your-mapbox-token
     DEVELOPMENT_MODE=false
     ```

   **Frontend Service:**
   - Click "+ New"
   - Select "GitHub Repo"
   - Service name: `frontend`
   - Settings:
     - Root Directory: `frontend`
     - Build Command: `npm install && npm run build`
     - Start Command: `npm run preview`
   - Add Environment Variables:
     ```
     VITE_API_BASE_URL=https://your-backend-url.railway.app/api/v1
     VITE_API_KEY=your-api-key
     VITE_MAPBOX_ACCESS_TOKEN=your-mapbox-token
     ```

4. **Add PostgreSQL Database**
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway will automatically set `DATABASE_URL` for backend

5. **Deploy**
   - Both services will deploy automatically
   - Get your URLs from the "Settings" → "Domains" section

---

### Option B: Vercel (Frontend) + Render (Backend)

**Advantages:**
- ✅ Vercel excels at frontend
- ✅ Render has good free tier for backend
- ✅ Independent scaling

**Frontend on Vercel:**

```bash
cd ~/taxini-app/frontend

# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod

# Follow prompts:
# - Set root directory: frontend
# - Build command: npm run build
# - Output directory: dist
```

Add environment variables in Vercel dashboard:
- `VITE_API_BASE_URL`
- `VITE_API_KEY`
- `VITE_MAPBOX_ACCESS_TOKEN`

**Backend on Render:**

1. Go to [Render.com](https://render.com)
2. "New" → "Web Service"
3. Connect GitHub repository
4. Settings:
   - Name: `taxini-backend`
   - Root Directory: `backend`
   - Build Command: `pip install -e .`
   - Start Command: `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

---

### Option C: Docker Deployment (Advanced)

Create `~/taxini-app/docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: taxini
      POSTGRES_USER: taxini
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    command: uvicorn src.app:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://taxini:${DB_PASSWORD}@postgres:5432/taxini
      JWT_SECRET: ${JWT_SECRET}
      API_KEY: ${API_KEY}
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    command: npm run preview
    ports:
      - "5173:5173"
    environment:
      VITE_API_BASE_URL: http://localhost:8000/api/v1
      VITE_API_KEY: ${API_KEY}

volumes:
  postgres_data:
```

Deploy with:
```bash
docker-compose up -d
```

---

## 5. Post-Deployment

### Step 5.1: Verify Deployment

Test your deployed application:

```bash
# Test backend health
curl https://your-backend-url.com/health

# Test backend API docs
# Visit: https://your-backend-url.com/docs

# Test frontend
# Visit: https://your-frontend-url.com
```

### Step 5.2: Set Up Custom Domain (Optional)

**For Railway:**
1. Go to service settings
2. "Networking" → "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

**For Vercel:**
```bash
vercel domains add yourdomain.com
```

### Step 5.3: Configure Production Settings

Update production environment variables:
- Set `DEVELOPMENT_MODE=false` in backend
- Set `DEBUG=false` in backend
- Use production database URLs
- Enable CORS for your frontend domain only

### Step 5.4: Set Up Monitoring (Recommended)

**Backend Monitoring:**
- Railway has built-in logs
- Add Sentry for error tracking:
  ```bash
  cd backend
  uv pip install sentry-sdk[fastapi]
  ```

**Frontend Monitoring:**
- Vercel has built-in analytics
- Add Sentry for error tracking:
  ```bash
  cd frontend
  npm install @sentry/vue
  ```

---

## 📋 Deployment Checklist

Before going live, ensure:

- [ ] All sensitive data is in environment variables (not in code)
- [ ] `.env` files are in `.gitignore`
- [ ] Database migrations are run
- [ ] CORS is configured correctly
- [ ] HTTPS is enabled
- [ ] API rate limiting is configured
- [ ] Error logging is set up
- [ ] Backup strategy is in place
- [ ] Health check endpoints work
- [ ] Documentation is up to date

---

## 🔧 Useful Commands

```bash
# Update both frontend and backend
git pull origin main

# Deploy backend changes (if using Railway)
git add backend/
git commit -m "Update backend"
git push origin main
# Railway auto-deploys

# Deploy frontend changes (if using Vercel)
cd frontend
vercel --prod

# View backend logs (Railway)
# Use Railway dashboard or CLI

# View database (Railway)
# Use Railway dashboard → Connect → Database URL
```

---

## 🆘 Troubleshooting

**Problem: Backend can't connect to database**
- Check `DATABASE_URL` environment variable
- Ensure database service is running
- Check firewall/security group settings

**Problem: Frontend can't reach backend**
- Check `VITE_API_BASE_URL` is correct
- Verify CORS settings in backend
- Check API_KEY matches

**Problem: Build fails**
- Check Node/Python versions
- Clear cache and rebuild
- Check for missing dependencies

**Problem: Environment variables not working**
- Vercel: Prefix with `VITE_`
- Railway: Check service-specific variables
- Restart services after adding variables

---

## 📞 Support

If you encounter issues:
1. Check Railway/Vercel/Render logs
2. Review GitHub Issues
3. Check documentation in `/docs` folder
4. Search community forums

---

**Good luck with your deployment! 🚀**
