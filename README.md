# Money Saver API

A FastAPI-based backend service for a personal finance application that helps users create and track saving plans with automated weekly email reminders.

## 🚀 Features

- **User Authentication** - Supabase Auth integration with JWT tokens
- **Savings Management** - Create, update, and track saving plans with weekly amounts
- **Automated Reminders** - Weekly email notifications to keep users motivated
- **Progress Tracking** - Real-time statistics and completion tracking
- **Health Monitoring** - Comprehensive health checks for all services
- **API Documentation** - Auto-generated OpenAPI docs with Swagger UI

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL (Supabase)
- **Authentication**: Supabase Auth + JWT
- **ORM**: SQLAlchemy 2.0 (async)
- **Email**: SMTP with Jinja2 templates
- **Scheduling**: APScheduler
- **Deployment**: Docker + Render

## 📁 Project Structure

```
app/
├── api/                    # API layer
│   ├── dependencies.py     # Auth & dependency injection
│   └── routes/
│       ├── auth.py        # Authentication endpoints
│       ├── savings.py     # Savings plan CRUD operations
│       └── email.py       # Email preferences & testing
├── core/                  # Core configurations
│   ├── config.py         # Environment variables & settings
│   ├── database.py       # SQLAlchemy async setup
│   └── supabase.py       # Supabase client configuration
├── models/               # SQLAlchemy database models
│   ├── user.py          # User model with email preferences
│   └── savings.py       # SavingPlan & WeeklyAmount models
├── schemas/             # Pydantic data validation schemas
│   ├── auth.py         # Authentication request/response models
│   ├── user.py         # User data models
│   └── savings.py      # Savings plan data models
├── services/           # Business logic layer
│   ├── supabase_service.py    # User sync & Supabase operations
│   ├── savings_service.py     # Savings plan business logic
│   ├── email_service.py       # Email sending functionality
│   ├── reminder_service.py    # Weekly reminder logic
│   ├── scheduler_service.py   # APScheduler management
│   └── token_service.py       # JWT token utilities
├── templates/
│   └── emails/              # Email templates (HTML + text)
└── main.py                 # FastAPI application entry point
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account and project
- PostgreSQL database (via Supabase)
- Email SMTP credentials (optional, for reminders)

### 1. Clone and Setup

```bash
git clone https://github.com/Chukwuemekamusic/money-saver-api.git
cd fastapi-money-saver
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# Database Configuration
DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres

# Security
SECRET_KEY=your-secret-key-for-jwt

# Server Configuration
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email Configuration (Optional)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_ENABLED=true
```

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 4. Run Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Or using Python module
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at:

- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

## 📚 API Endpoints

### Authentication

- `POST /api/v1/auth/sync-user` - Sync Supabase user to local database
- `GET /api/v1/auth/me` - Get current user information
- `POST /api/v1/auth/verify-token` - Verify JWT token

### Savings Management

- `POST /api/v1/savings/plans` - Create new saving plan
- `GET /api/v1/savings/plans` - List user's saving plans
- `GET /api/v1/savings/plans/{id}` - Get specific saving plan
- `PUT /api/v1/savings/plans/{id}` - Update saving plan
- `DELETE /api/v1/savings/plans/{id}` - Delete saving plan
- `POST /api/v1/savings/plans/{id}/weekly-amounts` - Add weekly amounts
- `GET /api/v1/savings/plans/{id}/stats` - Get plan statistics

### Email Management

- `GET /api/v1/email/preferences` - Get email preferences
- `PUT /api/v1/email/preferences` - Update email preferences
- `POST /api/v1/email/test` - Send test email

### System

- `GET /` - API information
- `GET /health` - Comprehensive health check
- `GET /docs` - Interactive API documentation

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_savings_api.py

# Verbose output
pytest -v
```

## 🐳 Docker Deployment

### Local Docker Build

```bash
# Build image
docker build -t money-saver-api .

# Run container
docker run -p 8000:8000 --env-file .env money-saver-api
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🚀 Production Deployment

### Deploy to Render

1. **Connect Repository**: Link your GitHub repo to Render
2. **Configure Service**:
   - Environment: Docker
   - Build Command: _Leave empty_
   - Start Command: _Leave empty_ (uses Dockerfile)
3. **Set Environment Variables**: Add all required env vars from `.env`
4. **Deploy**: Render will auto-deploy on git push

Detailed deployment guide: [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)

### Environment Variables for Production

```env
# Required
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
DATABASE_URL=postgresql://...
SECRET_KEY=your-production-secret-key

# Optional
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DEBUG=false
```

## 🔧 Development

### Code Quality

```bash
# Format code
black .
isort .

# Lint
flake8 .
mypy .
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Dependencies

```bash
# Install package
pip install package-name

# Update requirements
pip freeze > requirements.txt
```

## 📊 Monitoring & Health

### Health Check Endpoint

`GET /health` returns comprehensive status:

```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:00:00Z",
  "service": "Money Saver API",
  "version": "1.0.0",
  "supabase": { "status": "connected" },
  "database": { "status": "connected" },
  "email_service": { "enabled": true, "configured": true },
  "scheduler": { "running": true }
}
```

### Logging

- Application logs are structured using `structlog`
- Log level controlled by `LOG_LEVEL` environment variable
- Production logs are JSON formatted

## 🔐 Security

- **Authentication**: JWT tokens via Supabase Auth
- **Authorization**: User-based data isolation
- **Input Validation**: Pydantic schemas for all endpoints
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS**: Configurable origin restrictions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Format code (`black . && isort .`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pre-commit install
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md)
- **API Docs**: http://localhost:8000/docs (when running locally)
- **Issues**: Create a GitHub issue for bug reports or feature requests

## 🎯 Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Mobile push notifications
- [ ] Advanced reporting and analytics
- [ ] Multi-currency support
- [ ] Goal sharing and social features
- [ ] API rate limiting
- [ ] Advanced caching with Redis

---

**Built with ❤️ using FastAPI**

_A modern, fast, and feature-rich API for personal finance management._
