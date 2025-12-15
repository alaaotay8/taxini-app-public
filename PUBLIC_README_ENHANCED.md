# 🚕 Taxini - Modern Taxi Booking Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

> **A production-ready, full-stack taxi booking platform showcasing modern web development practices, clean architecture, and real-time features.**

This repository demonstrates professional-grade code architecture, best practices, and scalable design patterns. Built with Vue 3, FastAPI, and PostgreSQL.

---

## 🎯 What Makes This Special

### 🏗️ Clean Architecture
- **Modular Design**: Clear separation of concerns with layered architecture
- **Type Safety**: Full TypeScript/Python type hints throughout
- **API-First**: RESTful design with comprehensive OpenAPI documentation
- **Real-time**: WebSocket integration for live location and notifications

### ⚡ Technical Excellence
- **Modern Stack**: Vue 3 Composition API, FastAPI, SQLModel ORM
- **Performance**: Query optimization, response caching, lazy loading
- **Security**: JWT authentication, input validation, SQL injection prevention
- **Testing**: Comprehensive test coverage with pytest and Vitest

### 🚀 Production-Ready
- **Scalable**: Designed for horizontal scaling and high availability
- **Documented**: Extensive documentation with examples and guides
- **Deployable**: One-click deployment to Railway, Vercel, or Netlify
- **Maintainable**: Clean code following SOLID principles

---

## 🌟 Core Features

### For Riders 🙋
- 📍 **Real-time GPS Tracking** - Live driver location with ETA updates
- 🗺️ **Interactive Maps** - Powered by Mapbox with route visualization
- 💰 **Transparent Pricing** - Upfront cost estimates before booking
- ⭐ **Rating System** - Rate drivers and view their ratings
- 📱 **Trip History** - Complete trip records and receipts
- 🔔 **Live Notifications** - Real-time updates on trip status

### For Drivers 🚗
- 📲 **Trip Management** - Accept or decline incoming requests
- 🧭 **Navigation** - Turn-by-turn route guidance
- 💵 **Earnings Dashboard** - Real-time earnings with commission breakdown
- 📊 **Statistics** - Daily/weekly/monthly performance metrics
- 🚦 **Online/Offline Toggle** - Control availability instantly
- 🎯 **Smart Routing** - Optimized routes with distance calculations

### For Admins 👨‍💼
- 👥 **User Management** - Approve and manage drivers and riders
- 📈 **Analytics Dashboard** - Platform-wide statistics
- 🔧 **System Configuration** - Manage pricing and settings
- 🎫 **Support System** - Handle tickets and customer support

---

## 🛠️ Technology Stack

### Backend
```
FastAPI      - Modern Python web framework with async support
SQLModel     - SQL database ORM with Pydantic integration
PostgreSQL   - Robust relational database
Alembic      - Database migrations and version control
JWT          - Secure token-based authentication
Uvicorn      - Lightning-fast ASGI server
```

### Frontend
```
Vue 3        - Progressive JavaScript framework with Composition API
Vite         - Next-generation frontend build tool
Pinia        - Intuitive state management
Mapbox GL    - Interactive maps and geocoding
Axios        - Promise-based HTTP client
Tailwind CSS - Utility-first CSS framework
```

### Infrastructure
```
Supabase     - Real-time database features (optional)
Mapbox       - Geocoding and mapping services
uv           - Ultra-fast Python package manager
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Views   │  │Components│  │Composables│  │  Stores  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └─────────────┴─────────────┴─────────────┘           │
│                         │                                    │
│                    API Services                              │
└─────────────────────────┼───────────────────────────────────┘
                          │
                    REST API / WebSocket
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │API Routes│  │ Services │  │  Models  │  │   Core   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └─────────────┴─────────────┴─────────────┘           │
│                         │                                    │
│                    Database Layer                            │
└─────────────────────────┼───────────────────────────────────┘
                          │
                    PostgreSQL
```

### Key Design Patterns

- **Repository Pattern**: Clean data access abstraction
- **Service Layer**: Business logic separation
- **Dependency Injection**: Loose coupling and testability
- **API Gateway**: Centralized request handling
- **State Management**: Predictable state updates with Pinia
- **Composition API**: Reusable logic with Vue composables

---

## 📚 Project Structure

```
taxini-app/
├── backend/                    # FastAPI Python Backend
│   ├── src/
│   │   ├── api/v1/            # REST API endpoints
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── trips.py       # Trip management
│   │   │   ├── drivers.py     # Driver operations
│   │   │   └── riders.py      # Rider operations
│   │   ├── models/            # SQLModel database models
│   │   │   ├── user.py        # User model
│   │   │   ├── trip.py        # Trip model
│   │   │   └── driver.py      # Driver model
│   │   ├── services/          # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── trip_service.py
│   │   │   └── notification_service.py
│   │   ├── core/              # Configuration & security
│   │   │   ├── config.py      # App configuration
│   │   │   └── security.py    # Security utilities
│   │   └── db/                # Database connection
│   ├── tests/                 # Backend test suite
│   └── pyproject.toml         # Python dependencies
│
├── frontend/                  # Vue 3 Frontend
│   ├── src/
│   │   ├── views/            # Page components
│   │   │   ├── auth/         # Login, Signup
│   │   │   ├── rider/        # Rider dashboard
│   │   │   └── driver/       # Driver dashboard
│   │   ├── components/       # Reusable UI components
│   │   ├── composables/      # Vue composition functions
│   │   │   ├── useMap.js     # Map integration
│   │   │   ├── useTrip.js    # Trip management
│   │   │   └── useAuth.js    # Authentication
│   │   ├── services/         # API clients
│   │   │   ├── api.js        # Axios instance
│   │   │   ├── authService.js
│   │   │   └── tripService.js
│   │   ├── stores/           # Pinia state management
│   │   │   ├── auth.js       # Auth state
│   │   │   └── trip.js       # Trip state
│   │   └── router/           # Vue Router config
│   └── package.json          # Node dependencies
│
└── docs/                     # Documentation
    ├── API.md               # API documentation
    ├── ARCHITECTURE.md      # Architecture guide
    └── DEPLOYMENT.md        # Deployment guide
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** with `uv` package manager
- **Node.js 18+** with npm
- **PostgreSQL 14+** database
- **Mapbox API Key** ([Get free key](https://www.mapbox.com))

### 1️⃣ Clone & Setup

```bash
# Clone repository
git clone https://github.com/alaaotay8/taxini-app.git
cd taxini-app
```

### 2️⃣ Backend Setup

```bash
cd backend

# Install dependencies with uv (recommended)
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your database URL and API keys

# Run migrations
alembic upgrade head

# Start server
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

**Backend running at:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### 3️⃣ Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with your API URL and Mapbox token

# Start dev server
npm run dev
```

**Frontend running at:** `http://localhost:5173`

---

## 🔧 Configuration

### Backend Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/taxini

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080

# API Security
API_KEY=your-api-key-for-frontend-backend-communication

# Mapbox (for geocoding)
MAPBOX_ACCESS_TOKEN=pk.your_mapbox_token

# Development
DEVELOPMENT_MODE=true
DEBUG=true
```

### Frontend Environment Variables

```env
# Backend API
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_KEY=your-api-key-matching-backend

# Mapbox
VITE_MAPBOX_ACCESS_TOKEN=pk.your_mapbox_token
VITE_MAPBOX_STYLE=mapbox://styles/mapbox/dark-v11

# Default Location (Tunis, Tunisia)
VITE_DEFAULT_LAT=36.8065
VITE_DEFAULT_LNG=10.1815
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest                     # Run all tests
pytest tests/test_auth.py  # Run specific test
pytest -v                  # Verbose output
pytest --cov=src          # Coverage report
```

### Frontend Tests

```bash
cd frontend
npm run test              # Unit tests
npm run test:e2e         # E2E tests
```

---

## 🚢 Deployment

### Deploy to Railway (Recommended)

1. **Push to GitHub**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy on Railway**
   - Visit [Railway.app](https://railway.app)
   - Create new project from GitHub repo
   - Add PostgreSQL database
   - Configure environment variables
   - Deploy!

### Deploy to Vercel (Frontend)

```bash
cd frontend
npm run build
npx vercel --prod
```

**Full deployment guide:** [`.github/docs/DEPLOYMENT_GUIDE.md`](.github/docs/DEPLOYMENT_GUIDE.md)

---

## 💡 Key Features Showcase

### 1. Real-time Location Tracking

```javascript
// Composable for real-time driver location
export function useDriverLocation() {
  const location = ref(null)
  
  const watchLocation = () => {
    navigator.geolocation.watchPosition(
      (position) => {
        location.value = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        }
        // Update backend via WebSocket or API
        updateLocationOnServer(location.value)
      },
      { enableHighAccuracy: true }
    )
  }
  
  return { location, watchLocation }
}
```

### 2. JWT Authentication

```python
# Secure token-based authentication
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return await get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 3. State Management with Pinia

```javascript
// Clean, type-safe state management
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)
  
  async function login(credentials) {
    const response = await authService.login(credentials)
    user.value = response.user
    return response
  }
  
  return { user, isAuthenticated, login }
})
```

---

## 🔐 Security Features

- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Password Hashing** - Bcrypt for password storage
- ✅ **Input Validation** - Pydantic schemas
- ✅ **SQL Injection Prevention** - Parameterized queries
- ✅ **CORS Configuration** - Controlled cross-origin requests
- ✅ **Rate Limiting** - API abuse prevention
- ✅ **HTTPS Only** - Secure communication in production

---

## 📊 Performance Optimizations

- ⚡ **Lazy Loading** - Components loaded on demand
- 🗄️ **Response Caching** - Reduced database queries
- 📡 **Debounced Updates** - Throttled location tracking
- 📦 **Code Splitting** - Smaller bundle sizes
- 🎯 **Query Optimization** - Indexed database queries
- 🔄 **Connection Pooling** - Efficient database connections

---

## 📖 Learning Resources

This project demonstrates:

- **Vue 3 Composition API** - Modern reactive programming
- **FastAPI Best Practices** - Async Python web development
- **SQLModel ORM** - Type-safe database operations
- **RESTful API Design** - Clean endpoint architecture
- **Real-time Features** - WebSocket implementation
- **State Management** - Pinia patterns
- **Authentication Flow** - JWT implementation
- **Map Integration** - Mapbox GL JS usage

---

## 🎓 Advanced Features (Available on Request)

This public repository showcases core architecture and technical skills. Additional proprietary features available in private repository include:

- 🧠 **AI-Powered Driver Matching** - Machine learning algorithms
- 📈 **Dynamic Pricing Engine** - Surge pricing and optimization
- 🔍 **Fraud Detection System** - Advanced security measures
- 📊 **Advanced Analytics** - Business intelligence and reporting
- 🚀 **Performance Optimizations** - Proprietary caching strategies
- 🏢 **Enterprise Features** - White-label and multi-tenant support

**Interested in advanced features?** Contact me for demo and licensing options.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 👨‍💻 About the Developer

Built by **Alaa Otay** - Full-stack developer specializing in modern web applications with Vue.js and Python.

- 🌐 **Portfolio:** [Your Portfolio URL]
- 💼 **LinkedIn:** [Your LinkedIn]
- 📧 **Email:** [Your Email]
- 🐙 **GitHub:** [@alaaotay8](https://github.com/alaaotay8)

---

## 🙏 Acknowledgments

- **Mapbox** - Mapping and geocoding services
- **FastAPI** - Excellent framework and documentation
- **Vue.js** - Amazing reactive framework
- **Open Source Community** - Inspiration and support

---

## 📞 Contact & Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/alaaotay8/taxini-app/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/alaaotay8/taxini-app/discussions)
- 📧 **Email:** support@taxini.app

---

**⭐ If you find this project helpful, please give it a star!**

**Made with ❤️ for the developer community**
