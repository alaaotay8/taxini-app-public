# 🚕 Taxini - Modern Taxi Booking Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

A full-stack, real-time taxi booking application built with **Vue 3** (frontend) and **FastAPI** (backend), featuring live GPS tracking, Mapbox integration, and real-time notifications.

## 🌟 Features

### For Riders
- 📍 **Real-time Location Tracking** - Live driver location with ETA updates
- 🗺️ **Interactive Map Interface** - Powered by Mapbox with route visualization
- 💰 **Transparent Pricing** - Upfront cost estimates (Tunisian pricing standards)
- ⭐ **Driver Rating System** - Rate drivers and view their ratings
- 📱 **Trip History** - Track all past trips and receipts
- 🔔 **Live Notifications** - Real-time updates on trip status

### For Drivers
- 📲 **Trip Request Management** - Accept or decline incoming requests
- 🧭 **Turn-by-Turn Navigation** - Visual route guidance to pickup and destination
- 💵 **Earnings Dashboard** - Real-time earnings tracking with commission breakdown
- 📊 **Trip Statistics** - Daily/weekly/monthly performance metrics
- 🚗 **Online/Offline Toggle** - Control availability with one tap
- 🎯 **Smart Routing** - Optimized routes with approach fee calculation

### Admin Features
- 👥 **User Management** - Approve/manage drivers and riders
- 📈 **Analytics Dashboard** - Platform-wide statistics and insights
- 🔧 **System Configuration** - Manage pricing, commissions, and settings
- 🎫 **Support System** - Handle tickets and customer support

## 🏗️ Architecture

```
taxini-app/
├── backend/              # FastAPI Python Backend
│   ├── src/
│   │   ├── api/         # REST API endpoints
│   │   ├── models/      # SQLModel database models
│   │   ├── services/    # Business logic layer
│   │   ├── core/        # Configuration & security
│   │   └── db/          # Database connection & migrations
│   ├── tests/           # Backend test suite
│   └── pyproject.toml   # Python dependencies
│
├── frontend/            # Vue 3 Frontend
│   ├── src/
│   │   ├── views/       # Page components
│   │   ├── components/  # Reusable UI components
│   │   ├── composables/ # Vue composition functions
│   │   ├── services/    # API clients & utilities
│   │   └── stores/      # State management (Pinia)
│   ├── public/          # Static assets
│   └── package.json     # Node dependencies
│
├── docs/                # Project Documentation
│   ├── SECURITY.md      # Security best practices
│   ├── PERFORMANCE.md   # Performance optimizations
│   └── IMPROVEMENTS.md  # Feature improvements log
│
└── .github/             # GitHub Configuration
    └── docs/            # Deployment Documentation
        ├── DEPLOYMENT_GUIDE.md           # Full deployment guide
        ├── QUICK_START_GITHUB.md         # Quick GitHub setup
        ├── COMMAND_CHEATSHEET.md         # Command reference
        └── GITHUB_DEPLOYMENT_SUMMARY.md  # Deployment summary
```

## 📚 Documentation

- **[Deployment Guide](.github/docs/DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[Quick Start GitHub](.github/docs/QUICK_START_GITHUB.md)** - Fast GitHub setup
- **[Command Cheatsheet](.github/docs/COMMAND_CHEATSHEET.md)** - Common commands
- **[Security](docs/SECURITY.md)** - Security best practices
- **[Performance](docs/PERFORMANCE.md)** - Performance optimizations
- **[Backend API Docs](http://localhost:8000/docs)** - Interactive API documentation (when running)
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with `uv` package manager
- **Node.js 18+** with npm
- **PostgreSQL 14+** database
- **Mapbox API Key** (get free at [mapbox.com](https://www.mapbox.com))

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/taxini-app.git
cd taxini-app
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies with uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Or use pip
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration (database, API keys, etc.)

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration (API URL, Mapbox token, etc.)

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 🔧 Configuration

### Backend Environment Variables

Create `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/taxini

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080

# API Security
API_KEY=your-api-key-for-frontend-backend-communication

# Supabase (Optional - for real-time features)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Mapbox (for geocoding)
MAPBOX_ACCESS_TOKEN=pk.your_mapbox_token

# Development
DEVELOPMENT_MODE=true
DEBUG=true
```

### Frontend Environment Variables

Create `frontend/.env` file:

```env
# Backend API
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_KEY=your-api-key-matching-backend

# Mapbox
VITE_MAPBOX_ACCESS_TOKEN=pk.your_mapbox_token
VITE_MAPBOX_STYLE=mapbox://styles/mapbox/dark-v11

# Supabase (Optional)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key

# Default Location (Tunis, Tunisia)
VITE_DEFAULT_LAT=36.8065
VITE_DEFAULT_LNG=10.1815
```

## 📚 Documentation

- **[API Documentation](./docs/API.md)** - Complete REST API reference
- **[Security Guide](./docs/SECURITY.md)** - Authentication, authorization, and security best practices
- **[Performance Optimizations](./docs/PERFORMANCE.md)** - Caching, optimization strategies
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Code Cleanup Summary](./docs/CODE_CLEANUP_SUMMARY.md)** - Architecture and maintenance guide

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest                    # Run all tests
pytest tests/test_auth.py # Run specific test file
pytest -v                 # Verbose output
pytest --cov=src         # With coverage report
```

### Frontend Tests

```bash
cd frontend
npm run test              # Run unit tests
npm run test:e2e         # Run end-to-end tests (if configured)
```

## 🚢 Deployment

### Option 1: Deploy to Railway (Recommended for Full Stack)

1. **Prepare for deployment:**
```bash
# Ensure all environment variables are documented
# Commit and push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy on Railway:**
   - Go to [Railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Add two services:
     - **Backend**: Root directory = `backend`, Start command = `uvicorn src.app:app --host 0.0.0.0 --port $PORT`
     - **Frontend**: Root directory = `frontend`, Build command = `npm run build`, Start command = `npm run preview`
   - Add PostgreSQL database
   - Configure environment variables for each service

### Option 2: Deploy Separately

**Backend (Render/Railway/Fly.io):**
```bash
# See .github/docs/DEPLOYMENT_GUIDE.md for detailed instructions
```

**Frontend (Vercel/Netlify):**
```bash
# Build production bundle
cd frontend
npm run build

# Deploy to Vercel
npx vercel --prod

# Or deploy to Netlify
npm install -g netlify-cli
netlify deploy --prod
```

**📚 Full deployment documentation:** See [`.github/docs/DEPLOYMENT_GUIDE.md`](.github/docs/DEPLOYMENT_GUIDE.md)

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM with Pydantic integration
- **PostgreSQL** - Primary database
- **Alembic** - Database migrations
- **JWT** - Authentication
- **Uvicorn** - ASGI server

### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Vite** - Fast build tool and dev server
- **Pinia** - State management
- **Mapbox GL JS** - Interactive maps
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS

### Infrastructure
- **Supabase** - Real-time database features (optional)
- **Mapbox** - Geocoding and mapping services
- **uv** - Fast Python package manager

## 💳 Pricing Configuration (Tunisia)

The platform uses Tunisian taxi pricing standards:

- **Approach Fee (FA)**: 0.500 TND/km from driver to pickup
- **Meter Base**: 5.00 TND starting fare
- **Meter Rate**: 2.50 TND/km for trip distance
- **Platform Commission**: 20% from total fare

Example calculation:
```
Driver is 3 km from rider, trip is 5 km:
- Approach Fee: 3 × 0.500 = 1.50 TND
- Meter Cost: 5.00 + (5 × 2.50) = 17.50 TND
- Total: 19.00 TND
- Driver earns: 19.00 × 80% = 15.20 TND (after commission)
```

## 🔐 Security Features

- 🔒 **JWT Authentication** - Secure token-based auth
- 🛡️ **API Key Protection** - Backend endpoint security
- 🔑 **Password Hashing** - Bcrypt for password storage
- ⏱️ **Rate Limiting** - Prevent API abuse
- 🚫 **SQL Injection Prevention** - Parameterized queries
- 🔍 **Input Validation** - Pydantic schemas
- 📝 **Audit Logging** - Track important actions

See [SECURITY.md](./docs/SECURITY.md) for detailed security documentation.

## 📊 Performance Features

- ⚡ **Lazy Loading** - Components loaded on demand
- 🗄️ **Response Caching** - Reduced database queries
- 📡 **Adaptive Polling** - Smart API request intervals
- 🎯 **Debounced Updates** - Throttled location tracking
- 📦 **Code Splitting** - Smaller bundle sizes
- 🖼️ **Image Optimization** - Optimized static assets

See [PERFORMANCE.md](./docs/PERFORMANCE.md) for optimization details.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure:
- All tests pass
- Code follows the existing style
- Documentation is updated
- Commit messages are clear

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/YOUR_USERNAME)

## 🙏 Acknowledgments

- Mapbox for mapping services
- FastAPI community for excellent documentation
- Vue.js team for the amazing framework
- All contributors and testers

## 📞 Support

For issues, questions, or suggestions:
- 📧 Email: support@taxini.app
- 🐛 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/taxini-app/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/YOUR_USERNAME/taxini-app/discussions)

## 🗺️ Roadmap

- [ ] iOS/Android mobile apps (React Native)
- [ ] Real-time chat between driver and rider
- [ ] Scheduled rides (book in advance)
- [ ] Multiple payment methods
- [ ] Driver incentive programs
- [ ] Ride-sharing options
- [ ] Multi-language support
- [ ] Dark/light theme toggle
- [ ] Admin analytics dashboard
- [ ] Integration with payment gateways

---

**Made with ❤️ for the Tunisian taxi industry**
