# Money Saver API - Project Overview

## 🎯 Project Purpose
A FastAPI-based backend service for a money saving application that helps users create and track saving plans with automated weekly reminders via email.

## 🏗️ Architecture Overview

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Supabase Auth
- **ORM**: SQLAlchemy 2.0 (async)
- **Email**: SMTP with Jinja2 templates
- **Scheduling**: APScheduler for automated reminders
- **Deployment**: Docker + Render

### Key Integrations
- **Supabase**: Authentication, database hosting, real-time features
- **Email Service**: SMTP (Gmail) for weekly reminder notifications
- **Database Migrations**: Alembic for schema versioning

## 📁 Project Structure

```
fastapi-money-saver/
├── app/
│   ├── api/                    # API layer
│   │   ├── dependencies.py     # Auth & dependency injection
│   │   └── routes/            
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── savings.py     # Savings plan CRUD operations  
│   │       └── email.py       # Email preferences & testing
│   ├── core/                  # Core configurations
│   │   ├── config.py         # Environment variables & settings
│   │   ├── database.py       # SQLAlchemy async setup
│   │   └── supabase.py       # Supabase client configuration
│   ├── models/               # SQLAlchemy database models
│   │   ├── user.py          # User model with email preferences
│   │   └── savings.py       # SavingPlan & WeeklyAmount models
│   ├── schemas/             # Pydantic data validation schemas
│   │   ├── auth.py         # Authentication request/response models
│   │   ├── user.py         # User data models
│   │   └── savings.py      # Savings plan data models
│   ├── services/           # Business logic layer
│   │   ├── supabase_service.py    # User sync & Supabase operations
│   │   ├── savings_service.py     # Savings plan business logic
│   │   ├── email_service.py       # Email sending functionality
│   │   ├── reminder_service.py    # Weekly reminder logic
│   │   ├── scheduler_service.py   # APScheduler management
│   │   └── token_service.py       # JWT token utilities
│   ├── templates/
│   │   └── emails/              # Email templates
│   │       ├── weekly_reminder.html
│   │       └── weekly_reminder.txt
│   ├── utils/                   # Utility functions
│   └── main.py                 # FastAPI application entry point
├── migrations/                 # Alembic database migrations
├── tests/                     # Test suite
├── Dockerfile                # Container configuration
├── requirements.txt          # Python dependencies  
├── alembic.ini              # Database migration configuration
└── docker-compose.yml       # Local development setup
```

## 🛣️ API Routes & Endpoints

### Authentication (`/api/v1/auth/`)
- `POST /sync-user` - Sync Supabase user to local database
- `GET /me` - Get current authenticated user info
- `POST /verify-token` - Verify JWT token validity

### Savings Plans (`/api/v1/savings/`)
- `POST /plans` - Create new saving plan
- `GET /plans` - List user's saving plans (with pagination)
- `GET /plans/{plan_id}` - Get specific saving plan details
- `PUT /plans/{plan_id}` - Update saving plan
- `DELETE /plans/{plan_id}` - Delete saving plan
- `POST /plans/{plan_id}/weekly-amounts` - Add weekly amounts to plan
- `PUT /plans/{plan_id}/weekly-amounts/{week_id}` - Update specific week amount
- `GET /plans/{plan_id}/stats` - Get plan statistics & progress

### Email Management (`/api/v1/email/`)
- `GET /preferences` - Get user email notification preferences
- `PUT /preferences` - Update email notification settings
- `POST /test` - Send test email (development/admin)
- `POST /trigger-reminders` - Manually trigger weekly reminders

### System Endpoints
- `GET /` - API information & health check links
- `GET /health` - Comprehensive health check (DB, Supabase, email, scheduler)
- `GET /docs` - Interactive API documentation (Swagger UI)

## 💾 Database Schema

### Users Table
```sql
users:
  id (UUID, Primary Key)
  email (String, Unique)
  full_name (String, Optional)  
  email_notifications (Boolean, Default: True)
  last_reminder_sent (DateTime, Optional)
  created_at (DateTime)
  updated_at (DateTime)
```

### Saving Plans Table
```sql
saving_plans:
  id (UUID, Primary Key)
  user_id (UUID, Foreign Key -> users.id)
  name (String)
  target_amount (Decimal)
  start_date (Date)
  end_date (Date)
  total_weeks (Integer)
  is_active (Boolean, Default: True)
  created_at (DateTime)
  updated_at (DateTime)
```

### Weekly Amounts Table
```sql
weekly_amounts:
  id (UUID, Primary Key)
  saving_plan_id (UUID, Foreign Key -> saving_plans.id)
  week_number (Integer)
  week_index (Integer, Nullable) # Index within the plan
  amount (Decimal)
  week_start_date (Date)
  week_end_date (Date)
  is_completed (Boolean, Default: False)
  created_at (DateTime)
  updated_at (DateTime)
```

## 🔐 Authentication Flow

1. **Frontend Authentication**: User authenticates with Supabase Auth
2. **Token Verification**: API verifies Supabase JWT tokens
3. **User Sync**: `/auth/sync-user` ensures user exists in local database  
4. **Protected Routes**: All savings endpoints require valid authentication
5. **Current User Context**: `get_current_user` dependency provides user context

## 📧 Email System

### Weekly Reminder System
- **Scheduler**: APScheduler runs background tasks
- **Default Schedule**: Mondays at 9:00 AM UTC
- **Template Engine**: Jinja2 for HTML/text email templates
- **Content**: Personalized reminders with user's saving plans progress
- **Opt-out**: Users can disable email notifications

### Email Configuration
- **SMTP Provider**: Gmail (configurable)
- **Templates**: HTML + plain text versions
- **Variables**: User name, saving plans, weekly amounts, progress stats

## 🔧 Configuration & Environment Variables

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# Security
SECRET_KEY=your_jwt_secret_key

# Email (Optional - disables email features if not set)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

# Server Configuration
PORT=10000 (for Render deployment)
DEBUG=false
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Optional Configuration
```bash
# Email Scheduling
REMINDER_DAY=monday
REMINDER_HOUR=9
REMINDER_MINUTE=0
EMAIL_ENABLED=true

# Logging
LOG_LEVEL=INFO
```

## 🚀 Deployment (Render)

### Pre-deployment Checklist
- ✅ Dockerfile optimized for Render (port 10000)
- ✅ Environment variables configured in Render dashboard
- ✅ Supabase project set up with database
- ✅ Email SMTP credentials (if using email features)
- ✅ GitHub repository connected to Render

### Deployment Flow
1. **GitHub Integration**: Auto-deploy on push to main branch
2. **Docker Build**: Render builds using Dockerfile
3. **Environment Variables**: Set in Render dashboard
4. **Database Migrations**: Run automatically or manually via Alembic
5. **Health Checks**: `/health` endpoint for monitoring

## 🧪 Testing

### Test Structure
- `tests/conftest.py` - Test configuration & fixtures
- `tests/test_savings_api.py` - Savings endpoints testing
- Coverage reports in `htmlcov/`

### Running Tests
```bash
pytest                    # Run all tests
pytest --cov=app         # Run with coverage
pytest -v               # Verbose output
```

## 📊 Key Features

### Savings Management
- **Flexible Plans**: Create saving plans with custom amounts and dates
- **Weekly Tracking**: Track weekly saving amounts and progress
- **Plan Statistics**: Calculate completion percentage, remaining amounts
- **Active/Inactive States**: Enable/disable plans without deletion

### Email Reminders  
- **Automated Scheduling**: Weekly reminders sent automatically
- **Personalized Content**: Custom email content per user
- **User Preferences**: Opt-in/opt-out email notifications
- **Template System**: Professional HTML email templates

### Health Monitoring
- **Comprehensive Health Check**: Database, Supabase, email service status
- **Service Monitoring**: Scheduler status, configuration validation  
- **Error Handling**: Detailed error responses and logging

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication via Supabase
- **User Isolation**: Each user can only access their own data
- **Input Validation**: Pydantic schemas for all API inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **CORS Configuration**: Configurable origin restrictions
- **No Sensitive Data Logging**: Careful handling of authentication tokens

## 🐳 Docker Configuration

### Production Dockerfile Features
- **Python 3.11 Slim**: Optimized base image
- **Non-root User**: Security best practice
- **Multi-stage Build**: Dependencies installed separately  
- **Health Checks**: Built-in health monitoring
- **Environment Variables**: Full configuration via env vars

### Local Development
- `docker-compose.yml` for local development environment
- Volume mounting for live code reloading
- Local PostgreSQL container (optional, can use Supabase)

## 📈 Performance Considerations

- **Async Database**: SQLAlchemy async for high concurrency
- **Connection Pooling**: Database connection optimization
- **Caching**: LRU cache for settings and frequently accessed data
- **Efficient Queries**: Optimized database queries with proper indexing
- **Background Tasks**: APScheduler for non-blocking background operations

## 🛠️ Development Workflow

1. **Local Setup**: Use Docker Compose or virtual environment
2. **Database Migrations**: Alembic for schema changes
3. **API Testing**: FastAPI's automatic OpenAPI docs at `/docs`
4. **Code Quality**: Black, isort, flake8, mypy for code formatting
5. **Testing**: Pytest with async support and coverage reporting

## 🔍 Monitoring & Logging

- **Structured Logging**: Consistent log format across services
- **Health Endpoints**: Real-time service status monitoring
- **Error Tracking**: Comprehensive exception handling
- **Database Health**: Connection testing and query monitoring
- **Email Service Status**: SMTP connection and send rate monitoring

## 🚨 Common Issues & Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` format and credentials
- Check Supabase connection pooling limits
- Monitor connection pool status via health check

### Email Service Issues  
- Verify Gmail app passwords (not regular password)
- Check SMTP settings and TLS configuration
- Monitor email service status in health check

### Authentication Issues
- Verify Supabase project configuration
- Check JWT token expiration and refresh logic
- Validate CORS origins for frontend integration

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Supabase Docs**: https://supabase.com/docs
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Alembic Migrations**: https://alembic.sqlalchemy.org/
- **Render Deployment**: https://render.com/docs

*This API serves as a robust backend for money saving applications with comprehensive user management, savings tracking, and automated reminder systems.*