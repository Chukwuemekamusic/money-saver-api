# Deploying FastAPI Money Saver to Render

## Prerequisites

- Render account (free signup at https://render.com - **No credit card required**)
- GitHub/GitLab repository with your code
- Supabase project already set up

## Step 1: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (recommended) or email
3. No credit card required for free tier

## Step 2: Push Code to GitHub

Ensure your FastAPI project is in a GitHub repository:

```bash
# If not already done
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

## Step 3: Prepare Your Application

### Update Dockerfile (if needed)

Ensure your Dockerfile is production-ready:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
```

### Create .dockerignore

```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
venv/
htmlcov/
.env
.venv
```

## Step 4: Create Web Service on Render

1. **Login to Render Dashboard**

   - Go to https://dashboard.render.com

2. **Create New Web Service**

   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your FastAPI repository

3. **Configure Service Settings**

   - **Name**: `fastapi-money-saver` (or your preferred name)
   - **Environment**: `Docker`
   - **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
   - **Branch**: `main`
   - **Dockerfile Path**: Leave empty (auto-detected)

4. **Configure Build & Deploy**
   - **Build Command**: Leave empty (Docker handles this)
   - **Start Command**: Leave empty (defined in Dockerfile)

## Step 5: Set Environment Variables

In the Render dashboard, under "Environment" tab, add:

### Required Environment Variables:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SECRET_KEY=your_secret_key_for_jwt
DATABASE_URL=your_supabase_postgres_connection_string
```

### Email Service Variables (if using):

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email_address
EMAIL_PASSWORD=your_email_password
EMAIL_FROM=your_sender_email
EMAIL_ENABLED=true
REMINDER_DAY=monday
REMINDER_HOUR=9
REMINDER_MINUTE=0
```

### Optional Variables:

```
ENVIRONMENT=production
DEBUG=false
```

## Step 6: Update Your FastAPI Config

Ensure `app/core/config.py` handles Render's port requirements:

```python
import os

class Settings:
    # ... your existing settings ...

    # Render uses PORT environment variable
    port: int = int(os.getenv("PORT", 10000))

    # Database connection
    database_url: str = os.getenv("DATABASE_URL", "")

    # Supabase settings
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    supabase_service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
```

## Step 7: Deploy

1. **Review Configuration**

   - Double-check all environment variables
   - Verify Dockerfile and requirements.txt

2. **Create Service**

   - Click "Create Web Service"
   - Render will automatically start building and deploying

3. **Monitor Build Process**
   - Watch the build logs in real-time
   - Build typically takes 3-5 minutes

## Step 8: Verify Deployment

1. **Check Service Status**

   - Service should show "Live" status
   - Green indicator means successful deployment

2. **Test Your API**

   - Click on your service URL (e.g., `https://your-app-name.onrender.com`)
   - Test endpoints: `/docs` for Swagger UI

3. **Monitor Logs**
   - Use "Logs" tab to monitor application logs
   - Check for any errors or issues

## Step 9: Custom Domain (Optional)

1. **Add Custom Domain**

   - Go to "Settings" tab
   - Scroll to "Custom Domains"
   - Add your domain (e.g., `api.yourdomain.com`)

2. **Configure DNS**
   - Add CNAME record pointing to your Render URL
   - SSL certificate is automatically provided

## Step 10: Database Migration (if needed)

If you need to run Alembic migrations:

### Option 1: One-time Job

1. Create a "Background Worker" or "Cron Job"
2. Set command: `alembic upgrade head`
3. Run once to migrate database

### Option 2: Include in startup

Update your main.py to run migrations on startup:

```python
from alembic import command
from alembic.config import Config

@app.on_event("startup")
async def startup_event():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

## Important Notes

### Render Free Tier Limits:

- **750 hours/month** (enough for ~25 days of continuous running)
- **512 MB RAM**
- **0.1 CPU units**
- **Services sleep after 15 minutes** of inactivity (auto-wake on request)
- **500 GB/month bandwidth**

### Sleep Behavior:

- App sleeps after 15 minutes of no requests
- First request after sleep takes ~30 seconds to wake up
- Consider using a monitoring service to keep it awake if needed

### Environment Variables to Gather:

Before deployment, collect these from Supabase:

1. **Project URL**: `https://your-project.supabase.co`
2. **Anon Key**: From Supabase Settings → API
3. **Service Role Key**: From Supabase Settings → API
4. **Database URL**: From Supabase Settings → Database

### Automatic Deployments:

- Render automatically redeploys on git push to main branch
- No manual deployment needed after initial setup

## Troubleshooting

### Common Issues:

1. **Build fails**: Check requirements.txt and Dockerfile
2. **App crashes**: Check environment variables and logs
3. **Database connection fails**: Verify Supabase credentials
4. **Port issues**: Ensure app binds to `0.0.0.0:10000`

### Debugging:

- Use "Logs" tab for real-time logs
- Check "Events" tab for deployment history
- Use "Shell" tab for direct access (paid plans only)

### Performance Optimization:

- Keep Docker image size small
- Use `.dockerignore` to exclude unnecessary files
- Set appropriate resource limits

## Files to Review Before Deployment:

1. `Dockerfile` - ensure uses port 10000
2. `requirements.txt` - all dependencies listed
3. `app/core/config.py` - environment variables handled
4. `.dockerignore` - unnecessary files excluded
5. `alembic.ini` - database connection settings

## Post-Deployment Checklist:

- [ ] API endpoints working
- [ ] Database connection successful
- [ ] Email functionality working
- [ ] Authentication working
- [ ] Scheduled tasks running (if any)
- [ ] Custom domain configured (optional)

---

**Render Advantages:**
✅ No credit card required  
✅ Simple web-based deployment  
✅ Automatic HTTPS  
✅ GitHub integration  
✅ Free tier suitable for development

**Ready to proceed?** Review this guide and let me know when you want to start the deployment process.
