# 🚀 Vercel Deployment Guide - MedTechAI RCM Frontend

Complete guide for deploying the React + Vite frontend to Vercel.

---

## 📋 Prerequisites

- [x] Vercel account (free tier works)
- [x] GitHub repository with your code
- [x] Node.js 18+ installed locally
- [x] Backend API deployed (or use mock data)

---

## 🎯 Quick Start (3 Steps)

### 1. Prepare Your Frontend

All necessary files are already created:
- ✅ `vercel.json` - Vercel configuration
- ✅ `.env.example` - Environment template
- ✅ `.gitignore` - Git ignore rules
- ✅ `.nvmrc` - Node.js version lock
- ✅ `README.md` - Documentation

### 2. Push to GitHub

```bash
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC

git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

### 3. Deploy on Vercel

**Option A: Using Vercel Dashboard (Easiest)**

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend/dlrcm-main`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
4. Add Environment Variables (see below)
5. Click "Deploy"

**Option B: Using Vercel CLI**

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend/dlrcm-main
vercel

# For production
vercel --prod
```

---

## 🔐 Environment Variables

### Required Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Value (Development) | Value (Production) |
|----------|-------------------|-------------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | `https://your-backend.vercel.app` |
| `VITE_ENV` | `development` | `production` |
| `VITE_ENABLE_MOCK_DATA` | `true` | `false` |
| `VITE_ENABLE_ANALYTICS` | `false` | `true` |

### How to Add in Vercel

1. Go to your project in Vercel
2. Click **Settings** → **Environment Variables**
3. Add each variable:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://your-backend-api.com`
   - **Environment**: Production (or All)
4. Click **Save**
5. Redeploy to apply changes

---

## ⚙️ Detailed Configuration

### 1. vercel.json

Already created at `frontend/dlrcm-main/vercel.json`:

```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

**What it does**:
- ✅ Configures Vite build process
- ✅ Sets up SPA routing (all routes → index.html)
- ✅ Optimizes asset caching (1 year for static files)
- ✅ Ensures fast page loads

### 2. .nvmrc

Locks Node.js version to 20 LTS:

```
20
```

**Why**: Ensures consistent builds across local and Vercel.

### 3. .gitignore

Excludes sensitive and build files:

```
node_modules/
dist/
.env
.env.local
.vercel/
```

### 4. .env.example

Template for environment variables:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENV=development
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_MOCK_DATA=true
```

---

## 🔧 Vercel Project Settings

### General Settings

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend/dlrcm-main` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |
| **Node.js Version** | 20.x (from .nvmrc) |

### Build & Development Settings

```
Build Command: npm run build
Output Directory: dist
Install Command: npm install
Development Command: npm run dev
```

### Git Settings

```
Production Branch: main
Auto-deploy: Enabled
Comments on Pull Requests: Enabled
```

---

## 🌐 Domain Configuration

### Default Vercel Domain

After deployment, you'll get:
```
https://your-project.vercel.app
```

### Custom Domain (Optional)

1. Go to **Settings** → **Domains**
2. Add your domain: `rcm.yourdomain.com`
3. Update DNS records as instructed
4. SSL certificate is auto-provisioned

---

## 🔌 Backend Integration

### CORS Configuration

Your FastAPI backend needs to allow requests from Vercel:

**File**: `app/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

# Add your Vercel domain
origins = [
    "http://localhost:5173",  # Local dev
    "https://your-project.vercel.app",  # Vercel production
    "https://rcm.yourdomain.com",  # Custom domain (if any)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Update API Base URL

After deploying backend, update the environment variable:

```
VITE_API_BASE_URL=https://your-backend.vercel.app
```

Redeploy frontend to apply.

---

## 📦 Deployment Workflow

### Automatic Deployments

Vercel automatically deploys:
- ✅ **Production**: On push to `main` branch
- ✅ **Preview**: On pull requests
- ✅ **Development**: On push to other branches

### Manual Deployment

```bash
# From frontend/dlrcm-main
vercel --prod
```

### Rollback

1. Go to **Deployments** in Vercel Dashboard
2. Find a previous successful deployment
3. Click **⋮** → **Promote to Production**

---

## 🚀 Performance Optimization

Already configured:

### Build Optimizations
- ✅ Code splitting via Vite
- ✅ Tree shaking (removes unused code)
- ✅ Minification (JS, CSS, HTML)
- ✅ Modern browser targets (ES2020+)

### Runtime Optimizations
- ✅ Asset caching (1 year for static files)
- ✅ Compression (Brotli + Gzip)
- ✅ CDN distribution (Vercel Edge Network)
- ✅ Automatic HTTPS

### Lighthouse Score Expected
- Performance: 95+
- Accessibility: 90+
- Best Practices: 95+
- SEO: 90+

---

## 🐛 Troubleshooting

### Issue 1: Build Fails

**Error**: `npm install` fails on Vercel

**Solutions**:
1. Check `package.json` for syntax errors
2. Ensure `.nvmrc` specifies Node.js 20
3. Clear Vercel cache: Settings → General → Clear Build Cache
4. Try local build: `npm run build`

**Verify locally**:
```bash
cd frontend/dlrcm-main
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue 2: Environment Variables Not Working

**Error**: `import.meta.env.VITE_API_BASE_URL` is `undefined`

**Solutions**:
1. Ensure variable name starts with `VITE_`
2. Redeploy after adding variables (not automatic)
3. Check variable is set for correct environment (Production/Preview/Development)
4. Restart local dev server if testing locally

**Verify**:
```bash
# In your component
console.log(import.meta.env.VITE_API_BASE_URL);
```

### Issue 3: 404 on Page Refresh

**Error**: Refreshing `/dashboard` returns 404

**Solution**: Already fixed in `vercel.json` with rewrite rule:
```json
"rewrites": [
  {
    "source": "/(.*)",
    "destination": "/index.html"
  }
]
```

If still happening, verify `vercel.json` is in the root directory.

### Issue 4: CORS Errors

**Error**: `Access-Control-Allow-Origin` error in browser console

**Solutions**:
1. Add Vercel domain to backend CORS origins
2. Ensure backend is deployed and accessible
3. Check backend API URL is correct in `VITE_API_BASE_URL`

**Test backend**:
```bash
curl https://your-backend.vercel.app/health
```

### Issue 5: Build Takes Too Long

**Symptom**: Build exceeds 10 minutes

**Solutions**:
1. Remove unused dependencies: `npm prune`
2. Check for large files in `node_modules`
3. Upgrade to Vercel Pro (longer build timeout)
4. Use `.vercelignore` to exclude unnecessary files

### Issue 6: Blank Page After Deployment

**Error**: White screen, no errors in console

**Solutions**:
1. Check browser console for errors
2. Verify build output: `npm run build && npm run preview`
3. Check base URL in `vite.config.ts`:
   ```typescript
   export default defineConfig({
     base: '/',  // Should be '/' for Vercel
   });
   ```
4. Check `index.html` loads correctly

---

## 📊 Monitoring & Analytics

### Vercel Analytics (Built-in)

Enable in Vercel Dashboard:
1. Go to **Analytics** tab
2. Click **Enable Analytics**
3. View real-time metrics:
   - Page views
   - Unique visitors
   - Performance scores
   - Top pages

### Web Vitals

Vercel automatically tracks:
- **LCP** (Largest Contentful Paint)
- **FID** (First Input Delay)
- **CLS** (Cumulative Layout Shift)
- **TTFB** (Time to First Byte)

### Custom Analytics

Add Google Analytics (optional):

```typescript
// src/analytics.ts
export const trackPageView = (url: string) => {
  if (import.meta.env.VITE_ENABLE_ANALYTICS === 'true') {
    window.gtag?.('config', 'GA_MEASUREMENT_ID', {
      page_path: url,
    });
  }
};
```

---

## 🔒 Security Best Practices

### Already Configured
- ✅ HTTPS enforced (automatic)
- ✅ Security headers via Vercel
- ✅ Environment variables encrypted
- ✅ `.env` files gitignored

### Additional Recommendations

1. **Content Security Policy** (add to `vercel.json`):
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-inline'"
        }
      ]
    }
  ]
}
```

2. **API Key Protection**:
   - Never expose API keys in frontend code
   - Use backend proxy for sensitive API calls
   - Rotate keys regularly

---

## 📝 Deployment Checklist

### Before First Deployment

- [ ] All files committed to Git
- [ ] `.env.example` created (not `.env`)
- [ ] `vercel.json` configured
- [ ] `.nvmrc` present
- [ ] `.gitignore` includes `node_modules`, `dist`, `.env`
- [ ] Backend API deployed and accessible
- [ ] CORS configured on backend

### During Deployment

- [ ] Root Directory set to `frontend/dlrcm-main`
- [ ] Environment variables added
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist`
- [ ] Framework preset: Vite

### After Deployment

- [ ] Visit deployed URL
- [ ] Test all routes
- [ ] Check browser console for errors
- [ ] Verify API calls work
- [ ] Test on mobile device
- [ ] Check Lighthouse score
- [ ] Enable Analytics

---

## 🎓 Advanced Topics

### Preview Deployments

Every pull request gets a unique preview URL:
```
https://your-project-git-feature-branch.vercel.app
```

**Benefits**:
- Test changes before merging
- Share with team for feedback
- Automatic cleanup after merge

### Environment-Specific Variables

Set different values per environment:

| Environment | When Used |
|-------------|-----------|
| **Production** | Main branch deployments |
| **Preview** | Pull request deployments |
| **Development** | Local development |

Example:
```
VITE_API_BASE_URL (Production) = https://api.prod.com
VITE_API_BASE_URL (Preview) = https://api.staging.com
VITE_API_BASE_URL (Development) = http://localhost:8000
```

### Custom Build Configuration

For advanced setups, modify `vercel.json`:

```json
{
  "build": {
    "env": {
      "NODE_OPTIONS": "--max_old_space_size=4096"
    }
  },
  "functions": {
    "api/**/*.ts": {
      "maxDuration": 10
    }
  }
}
```

---

## 📚 Resources

- **Vercel Docs**: https://vercel.com/docs
- **Vite Docs**: https://vitejs.dev/guide/
- **React Docs**: https://react.dev/
- **Vercel CLI**: https://vercel.com/docs/cli
- **Vercel Support**: support@vercel.com

---

## 🆘 Getting Help

### Community Support
- [Vercel Discord](https://vercel.com/discord)
- [Vercel GitHub Discussions](https://github.com/vercel/vercel/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/vercel)

### Direct Support
- Email: support@vercel.com
- Dashboard: Click "Help" button

---

## ✅ Summary

### What We've Set Up

1. ✅ **vercel.json** - Deployment configuration
2. ✅ **.env.example** - Environment template
3. ✅ **.nvmrc** - Node version lock
4. ✅ **.gitignore** - Git exclusions
5. ✅ **README.md** - Documentation
6. ✅ **Optimized build** - Performance configured

### Next Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Vercel deployment config"
   git push origin main
   ```

2. **Deploy on Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import repository
   - Configure root directory: `frontend/dlrcm-main`
   - Add environment variables
   - Deploy!

3. **Test Deployment**
   - Visit your Vercel URL
   - Test all features
   - Check browser console
   - Verify API integration

---

**🎉 You're ready to deploy!**

Any questions? Check the troubleshooting section or reach out to the team.

---

**Last Updated**: October 2, 2024  
**Version**: 1.0  
**Author**: MedTechAI Team

