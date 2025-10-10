# 🚀 Render Deployment Guide - MedTechAI RCM Backend

Complete guide for deploying the FastAPI backend to Render.

---

## 📋 Prerequisites

- [x] Render account (free tier works)
- [x] GitHub repository with your code
- [x] OpenAI API key (or other AI provider keys)
- [x] Python 3.12+ (for local testing)

---

## 🎯 Quick Start (5 Steps)

### 1. Prepare Your Backend

All necessary files are already created:
- ✅ `render.yaml` - Render configuration (Python-based)
- ✅ `render-docker.yaml` - Alternative Docker configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Environment template
- ✅ `pyproject.toml` - Python dependencies (source)

### 2. Push to GitHub

```bash
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC_UI_BE/MedTechAi-RCM-MedCode-AIAssist-BE

git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### 3. Create Render Account & Service

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click **"New +"** → **"Blueprint"**
4. Connect your GitHub repository
5. Render will auto-detect the `render.yaml` configuration

### 4. Configure Environment Variables

In Render Dashboard → Your Service → Environment:

| Variable | Value | Description |
|----------|-------|-------------|
| `OPENAI_API_KEY` | `sk-proj-...` | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Your Anthropic API key (optional) |
| `GOOGLE_API_KEY` | `AIza...` | Your Google API key (optional) |
| `SECRET_KEY` | `auto-generated` | JWT secret (auto-generated) |
| `ENVIRONMENT` | `production` | Environment setting |
| `DEBUG` | `false` | Debug mode |

### 5. Deploy

1. Click **"Create Blueprint"**
2. Render will automatically:
   - Create web service
   - Create PostgreSQL database
   - Deploy your application
   - Provide URLs

---

## ⚙️ Detailed Configuration

### 1. render.yaml

Already created with optimal settings:

```yaml
services:
  - type: web
    name: medtechai-rcm-backend
    env: python
    plan: free
    buildCommand: "uv sync"
    startCommand: "uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.5
      - key: ENVIRONMENT
        value: production
      - key: DEBUG
        value: false
      # ... more variables
```

**What it does**:
- ✅ Configures Python 3.12.5
- ✅ Sets up UV package manager
- ✅ Configures FastAPI with Uvicorn
- ✅ Creates PostgreSQL database
- ✅ Sets up environment variables

### 2. Database Configuration

Render automatically creates a PostgreSQL database:

```python
# Your app will automatically use the DATABASE_URL
DATABASE_URL = "postgresql://user:pass@host:port/dbname"
```

### 3. Environment Variables

**Required Variables**:

```env
# AI Services
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional
GOOGLE_API_KEY=AIza-your-key-here       # Optional

# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=auto-generated-by-render
LOG_LEVEL=INFO

# Database (auto-configured by Render)
DATABASE_URL=postgresql://...
```

---

## 🌐 Domain Configuration

### Default Render Domain

After deployment, you'll get:
```
https://medtechai-rcm-backend.onrender.com
```

### Custom Domain (Optional)

1. Go to **Settings** → **Custom Domains**
2. Add your domain: `api.yourdomain.com`
3. Update DNS records as instructed
4. SSL certificate is auto-provisioned

---

## 🔌 Frontend Integration

### Update Frontend Environment

In your Vercel frontend, update the environment variable:

```env
# In Vercel Dashboard → Environment Variables
VITE_API_BASE_URL=https://medtechai-rcm-backend.onrender.com
```

### CORS Configuration

Your FastAPI app already includes CORS middleware. Update it for production:

```python
# app/main.py
origins = [
    "http://localhost:5173",  # Local dev
    "https://your-frontend.vercel.app",  # Vercel production
    "https://yourdomain.com",  # Custom domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoring & Logs

### Built-in Monitoring

Render provides:
- **Real-time logs** in dashboard
- **Metrics** (CPU, memory, requests)
- **Health checks** at `/health`
- **Automatic restarts** on crashes

### Access Logs

```bash
# In Render Dashboard
Service → Logs → View Live Logs
```

### Health Check

Your app includes a health endpoint:
```
GET https://your-backend.onrender.com/health
```

---

## 🚀 Performance Optimization

### Already Configured

- ✅ **UV package manager** (faster than pip)
- ✅ **Python 3.12** (latest performance improvements)
- ✅ **Uvicorn ASGI server** (high performance)
- ✅ **PostgreSQL** (production database)
- ✅ **Connection pooling** (via SQLAlchemy)

### Render Optimizations

- ✅ **Auto-scaling** (based on traffic)
- ✅ **CDN** (global content delivery)
- ✅ **SSL termination** (automatic HTTPS)
- ✅ **Load balancing** (multiple instances)

---

## 🐛 Troubleshooting

### Issue 1: Build Fails

**Error**: `uv sync` fails on Render

**Solutions**:
1. Check `pyproject.toml` for syntax errors
2. Ensure all dependencies are listed
3. Check Python version compatibility
4. Review build logs in Render dashboard

**Verify locally**:
```bash
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue 2: Database Connection Fails

**Error**: `sqlalchemy.exc.OperationalError`

**Solutions**:
1. Check `DATABASE_URL` environment variable
2. Ensure database is created and running
3. Verify connection string format
4. Check database credentials

**Test connection**:
```bash
# In Render shell
uv run python -c "from app.core.database import engine; print(engine.url)"
```

### Issue 3: API Keys Not Working

**Error**: `openai.AuthenticationError`

**Solutions**:
1. Verify API keys in environment variables
2. Check key format (no extra spaces)
3. Ensure keys are set for correct environment
4. Test keys locally first

**Verify**:
```bash
# In Render shell
echo $OPENAI_API_KEY
```

### Issue 4: CORS Errors

**Error**: `Access-Control-Allow-Origin` error

**Solutions**:
1. Add frontend domain to CORS origins
2. Check frontend API base URL
3. Verify HTTPS/HTTP protocol match
4. Test API directly with curl

**Test API**:
```bash
curl https://your-backend.onrender.com/health
```

### Issue 5: Slow Response Times

**Symptom**: API responses > 5 seconds

**Solutions**:
1. Check database query performance
2. Optimize AI API calls (use faster models)
3. Add caching for frequent requests
4. Upgrade to paid Render plan

---

## 📦 Deployment Workflow

### Automatic Deployments

Render automatically deploys:
- ✅ **Production**: On push to `main` branch
- ✅ **Preview**: On pull requests (if configured)
- ✅ **Manual**: Via dashboard or CLI

### Manual Deployment

```bash
# Using Render CLI
npm install -g @render/cli
render login
render deploy
```

### Rollback

1. Go to **Deployments** in Render Dashboard
2. Find a previous successful deployment
3. Click **"Promote to Production"**

---

## 🔒 Security Best Practices

### Already Configured

- ✅ **HTTPS enforced** (automatic)
- ✅ **Environment variables encrypted**
- ✅ **Database credentials secured**
- ✅ **CORS properly configured**

### Additional Recommendations

1. **API Key Rotation**:
   - Rotate keys every 90 days
   - Use different keys for dev/prod
   - Monitor API usage

2. **Database Security**:
   - Use connection pooling
   - Enable SSL connections
   - Regular backups

3. **Application Security**:
   - Input validation (Pydantic)
   - Rate limiting (if needed)
   - Error handling

---

## 📝 Deployment Checklist

### Before First Deployment

- [ ] All files committed to Git
- [ ] `render.yaml` configured
- [ ] `pyproject.toml` has all dependencies
- [ ] Environment variables prepared
- [ ] API keys ready
- [ ] Database schema compatible

### During Deployment

- [ ] Blueprint created successfully
- [ ] Database provisioned
- [ ] Environment variables set
- [ ] Build completed without errors
- [ ] Health check passing

### After Deployment

- [ ] Visit deployed URL
- [ ] Test `/health` endpoint
- [ ] Test API endpoints
- [ ] Check logs for errors
- [ ] Update frontend API URL
- [ ] Test full integration

---

## 🎓 Advanced Topics

### Database Migrations

If using Alembic:

```bash
# In Render shell
uv run alembic upgrade head
```

### Background Jobs

Render supports background processes:

```yaml
# In render.yaml
services:
  - type: worker
    name: medtechai-rcm-worker
    env: python
    buildCommand: "uv sync"
    startCommand: "uv run python -m app.workers.main"
```

### Environment-Specific Deployments

Create separate services for staging:

```yaml
services:
  - type: web
    name: medtechai-rcm-staging
    envVars:
      - key: ENVIRONMENT
        value: staging
      - key: DEBUG
        value: true
```

---

## 📚 Resources

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **UV Docs**: https://docs.astral.sh/uv/
- **Render Support**: support@render.com

---

## 🆘 Getting Help

### Community Support

- [Render Discord](https://discord.gg/render)
- [Render GitHub Discussions](https://github.com/render-oss/render)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/render)

### Direct Support

- Email: support@render.com
- Dashboard: Click "Help" button

---

## ✅ Summary

### What We've Set Up

1. ✅ **render.yaml** - Deployment configuration
2. ✅ **Dockerfile.render** - Container configuration
3. ✅ **Environment variables** - Production settings
4. ✅ **Database setup** - PostgreSQL configuration
5. ✅ **CORS configuration** - Frontend integration
6. ✅ **Health checks** - Monitoring endpoints

### Next Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment config"
   git push origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Create new Blueprint
   - Connect GitHub repository
   - Configure environment variables
   - Deploy!

3. **Update Frontend**
   - Set `VITE_API_BASE_URL` in Vercel
   - Test full integration
   - Monitor logs

---

**🎉 Your backend is ready for Render!**

Any questions? Check the troubleshooting section or reach out to the team.

---

**Last Updated**: October 10, 2024  
**Version**: 1.0  
**Author**: MedTechAI Team
