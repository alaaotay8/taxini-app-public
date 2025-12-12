# 📋 Command Cheatsheet

Quick reference for common commands during GitHub deployment.

---

## 🚀 Initial Setup

```bash
# Run automated setup script
bash ~/setup-github.sh

# OR manually create structure
mkdir -p ~/taxini-app && cd ~/taxini-app
cp -r ~/Taxini backend
cp -r ~/Taxini-Frontend frontend
mkdir -p docs
```

---

## 📤 Git Commands

```bash
# Initialize repository
cd ~/taxini-app
git init

# Stage all files
git add .

# Create first commit
git commit -m "Initial commit: Taxini platform"

# Add GitHub remote (REPLACE YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/taxini-app.git

# Push to GitHub
git branch -M main
git push -u origin main

# View remote URL
git remote -v

# Change remote URL if needed
git remote set-url origin https://github.com/YOUR_USERNAME/taxini-app.git
```

---

## 🔑 Generate Secure Keys

```bash
# Generate JWT secret (64 characters)
openssl rand -base64 64

# Generate API key (32 characters)
openssl rand -base64 32

# Generate random password
openssl rand -base64 24
```

---

## 🗂️ Project Navigation

```bash
# Go to project root
cd ~/taxini-app

# Backend directory
cd ~/taxini-app/backend

# Frontend directory
cd ~/taxini-app/frontend

# Documentation
cd ~/taxini-app/docs
```

---

## 🔍 Check Status

```bash
# Git status
git status

# View commit history
git log --oneline

# Check ignored files
git status --ignored

# View file differences
git diff

# View staged differences
git diff --staged
```

---

## 🔧 Fix Common Issues

```bash
# Remove .env from git if accidentally committed
git rm --cached .env
git rm --cached backend/.env
git rm --cached frontend/.env
git commit -m "Remove sensitive .env files"
git push

# Remove remote and re-add
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/taxini-app.git

# Force push (USE WITH CAUTION!)
git push -f origin main

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

---

## 🌐 Backend Commands

```bash
cd ~/taxini-app/backend

# Install dependencies (using uv)
uv pip install -e .

# Run backend locally
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# Run database migrations
alembic upgrade head

# Create admin user
uv run python scripts/create_admin.py

# Run tests
pytest tests/ -v
```

---

## 💻 Frontend Commands

```bash
cd ~/taxini-app/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

---

## 🐳 Docker Commands (Optional)

```bash
cd ~/taxini-app

# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild specific service
docker-compose up -d --build backend
```

---

## 🔄 Update and Deploy

```bash
# Make changes to code
# ...

# Stage changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# Railway auto-deploys on push!
# Or manually redeploy in Railway dashboard
```

---

## 🗄️ Database Commands

```bash
# Connect to local PostgreSQL
psql $TAXINI_SUPABASE_DB_URL

# Backup database
pg_dump $TAXINI_SUPABASE_DB_URL > backup.sql

# Restore database
psql $TAXINI_SUPABASE_DB_URL < backup.sql

# View database tables
psql $TAXINI_SUPABASE_DB_URL -c "\dt"

# Run SQL query
psql $TAXINI_SUPABASE_DB_URL -c "SELECT * FROM users LIMIT 5;"
```

---

## 🧪 Testing

```bash
# Backend tests
cd ~/taxini-app/backend
pytest tests/ -v --cov=src

# Frontend tests (if configured)
cd ~/taxini-app/frontend
npm test

# Test specific file
pytest tests/test_auth.py -v
```

---

## 📊 Monitoring

```bash
# View backend logs (Railway CLI)
railway logs --service backend

# View frontend logs
railway logs --service frontend

# Check service status
railway status

# View recent deployments
railway deployments
```

---

## 🔒 Security Checks

```bash
# Check for exposed secrets in git history
git log -S "password" --all
git log -S "secret" --all

# Scan for sensitive data
grep -r "password" .
grep -r "secret" .

# Audit npm packages
cd frontend
npm audit

# Audit Python packages
cd backend
pip-audit
```

---

## 🧹 Cleanup

```bash
# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -r {} +

# Remove node_modules
rm -rf frontend/node_modules

# Clean git untracked files (preview)
git clean -n

# Clean git untracked files (execute)
git clean -fd
```

---

## 📱 Local Network Testing

```bash
# Find your local IP
ip addr show | grep "inet " | grep -v 127.0.0.1

# Run backend on network IP
cd ~/taxini-app/backend
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

# Run frontend on network IP
cd ~/taxini-app/frontend
npm run dev -- --host 0.0.0.0

# Access from phone/other device:
# http://YOUR_LOCAL_IP:8000 (backend)
# http://YOUR_LOCAL_IP:5173 (frontend)
```

---

## ⚡ Quick Actions

```bash
# Full restart (local development)
cd ~/taxini-app/backend && uvicorn src.app:app --reload &
cd ~/taxini-app/frontend && npm run dev &

# Kill all running processes
pkill -f uvicorn
pkill -f "npm run dev"

# View running processes
ps aux | grep uvicorn
ps aux | grep node
```

---

Save this file for quick reference! 📌
