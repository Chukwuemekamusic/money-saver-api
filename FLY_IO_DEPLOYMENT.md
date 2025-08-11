# Deploying FastAPI Money Saver to Fly.io

## Prerequisites
- Fly.io account (free signup at https://fly.io)
- flyctl CLI installed
- Git repository
- Supabase project already set up

## Step 1: Install Fly.io CLI
```bash
# macOS
brew install flyctl

# Or download from https://fly.io/docs/hands-on/install-flyctl/
```

## Step 2: Login to Fly.io
```bash
flyctl auth login
```

## Step 3: Prepare Your Application
1. Ensure your `Dockerfile` is optimized for production
2. Create/update `.dockerignore` file
3. Set up environment variables configuration

## Step 4: Initialize Fly.io App
```bash
cd fastapi-money-saver
flyctl launch
```
This will:
- Scan your Dockerfile
- Create `fly.toml` configuration file
- Prompt for app name and region selection
- **Don't deploy yet** when prompted

## Step 5: Configure Environment Variables
```bash
# Set your Supabase credentials
flyctl secrets set SUPABASE_URL="your_supabase_url"
flyctl secrets set SUPABASE_KEY="your_supabase_anon_key"
flyctl secrets set SUPABASE_SERVICE_ROLE_KEY="your_service_role_key"

# Set other required environment variables
flyctl secrets set SECRET_KEY="your_secret_key"
flyctl secrets set DATABASE_URL="your_supabase_postgres_url"

# Email service credentials (if using)
flyctl secrets set SMTP_SERVER="your_smtp_server"
flyctl secrets set SMTP_PORT="587"
flyctl secrets set SMTP_USERNAME="your_email"
flyctl secrets set SMTP_PASSWORD="your_email_password"
```

## Step 6: Update fly.toml Configuration
Edit the generated `fly.toml` file:

```toml
app = "your-app-name"
primary_region = "your-region"

[build]

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[vm]]
  memory = '512mb'
  cpu_kind = 'shared'
  cpus = 1

[env]
  PORT = "8000"
```

## Step 7: Update Dockerfile (if needed)
Ensure your Dockerfile exposes port 8000:
```dockerfile
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Step 8: Test Local Build
```bash
# Test Docker build locally
docker build -t fastapi-money-saver .
docker run -p 8000:8000 fastapi-money-saver
```

## Step 9: Deploy to Fly.io
```bash
flyctl deploy
```

## Step 10: Verify Deployment
```bash
# Check app status
flyctl status

# View logs
flyctl logs

# Open app in browser
flyctl open
```

## Step 11: Database Migration (if needed)
If you need to run Alembic migrations:
```bash
# SSH into your app
flyctl ssh console

# Run migrations
alembic upgrade head
```

## Step 12: Set Up Custom Domain (Optional)
```bash
# Add custom domain
flyctl certs add yourdomain.com

# Check certificate status
flyctl certs show yourdomain.com
```

## Important Notes

### Environment Variables Required:
- `SUPABASE_URL`
- `SUPABASE_KEY` 
- `SUPABASE_SERVICE_ROLE_KEY`
- `SECRET_KEY`
- `DATABASE_URL`
- Email service credentials (if using email features)

### Fly.io Free Tier Limits:
- 3 shared-cpu-1x 256mb VMs
- 160GB/month outbound data transfer
- Apps sleep after inactivity (auto-wake on request)

### Troubleshooting:
- Check logs: `flyctl logs`
- SSH into app: `flyctl ssh console`
- Scale app: `flyctl scale count 1`
- Restart app: `flyctl restart`

### Cost Optimization:
- Use `auto_stop_machines = true` to save costs
- Set `min_machines_running = 0` for development
- Monitor usage: `flyctl dashboard`

## Files to Review Before Deployment:
1. `Dockerfile` - ensure production-ready
2. `requirements.txt` - verify all dependencies
3. `app/core/config.py` - check environment variable handling
4. `alembic.ini` - database connection settings
5. `.dockerignore` - exclude unnecessary files

## Next Steps After Deployment:
1. Test all API endpoints
2. Verify email functionality
3. Check scheduled tasks (if any)
4. Monitor application logs
5. Set up monitoring/alerts (optional)

---

**Ready to proceed?** Review this guide and let me know when you want to start the deployment process.