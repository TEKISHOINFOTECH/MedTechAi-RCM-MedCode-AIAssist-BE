# MedTechAI RCM - Frontend

Modern, enterprise-grade React + TypeScript + Vite frontend for Medical Revenue Cycle Management.

## 🚀 Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Routing**: React Router v7
- **Icons**: Lucide React
- **Linting**: ESLint 9

## 📦 Prerequisites

- Node.js 18+ (recommend v20 LTS)
- npm 9+ or pnpm 8+

## 🛠️ Local Development

### 1. Install Dependencies

```bash
cd frontend/dlrcm-main
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENV=development
VITE_ENABLE_MOCK_DATA=true
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

### 4. Build for Production

```bash
npm run build
```

Output: `dist/` directory

### 5. Preview Production Build

```bash
npm run preview
```

## 🌐 Vercel Deployment

### Option 1: Vercel CLI (Recommended)

#### Install Vercel CLI

```bash
npm install -g vercel
```

#### Login to Vercel

```bash
vercel login
```

#### Deploy

```bash
# From frontend/dlrcm-main directory
vercel

# For production
vercel --prod
```

### Option 2: GitHub Integration (Easiest)

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Vercel configuration"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Select `frontend/dlrcm-main` as the root directory
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `frontend/dlrcm-main`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
     - **Install Command**: `npm install`

3. **Add Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     VITE_API_BASE_URL=https://your-backend-api.vercel.app
     VITE_ENV=production
     VITE_ENABLE_ANALYTICS=true
     VITE_ENABLE_MOCK_DATA=false
     ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will automatically deploy on every push to `main`

### Option 3: Manual Vercel Configuration

If using a monorepo structure:

1. Create `vercel.json` (already created)
2. Set Root Directory in Vercel dashboard:
   - Settings → General → Root Directory: `frontend/dlrcm-main`

## 📁 Project Structure

```
frontend/dlrcm-main/
├── public/
│   └── medtechai-logo.png       # App logo
├── src/
│   ├── components/              # Reusable components
│   │   ├── Header.tsx
│   │   ├── Navigation.tsx
│   │   ├── Logo.tsx
│   │   ├── MetricsGrid.tsx
│   │   ├── RiskCard.tsx
│   │   ├── RiskChart.tsx
│   │   ├── AIInsights.tsx
│   │   └── RecentActivity.tsx
│   ├── pages/                   # Page components
│   │   ├── Dashboard.tsx
│   │   ├── UploadEDI.tsx
│   │   ├── ClaimsReview.tsx
│   │   └── Settings.tsx
│   ├── types/                   # TypeScript types
│   │   └── claim.ts
│   ├── App.tsx                  # Main app component
│   ├── main.tsx                 # Entry point
│   └── index.css                # Global styles
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── vercel.json                  # Vercel configuration
├── vite.config.ts               # Vite configuration
├── tailwind.config.js           # Tailwind configuration
├── tsconfig.json                # TypeScript configuration
└── package.json                 # Dependencies
```

## 🔧 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server (port 5173) |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |
| `npm run typecheck` | Check TypeScript types |

## 🎨 Features

### Current Features
- ✅ **Dashboard**: Overview of claims, denials, and metrics
- ✅ **EDI Upload**: Drag-and-drop file upload with validation
- ✅ **Claims Review**: Review and analyze processed claims
- ✅ **Settings**: Configure application preferences
- ✅ **Responsive Design**: Mobile, tablet, desktop optimized
- ✅ **Enterprise UI**: Professional, modern design
- ✅ **Dark Mode Ready**: Color scheme supports dark mode

### Planned Features
- 🔄 **API Integration**: Connect to FastAPI backend
- 🔄 **Real-time Updates**: WebSocket support
- 🔄 **Authentication**: User login/logout
- 🔄 **Role-based Access**: Permissions management
- 🔄 **Advanced Analytics**: Charts and visualizations

## 🔌 API Integration

### Backend Connection

Create an API client in `src/services/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = {
  async uploadEDI(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/uc1/pipeline/run`, {
      method: 'POST',
      body: formData,
    });
    
    return response.json();
  },
  
  async getClaims() {
    const response = await fetch(`${API_BASE_URL}/api/v1/claims`);
    return response.json();
  }
};
```

## 🌍 Environment Variables

| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` | Your deployed API |
| `VITE_ENV` | Environment | `development` | `production` |
| `VITE_ENABLE_MOCK_DATA` | Use mock data | `true` | `false` |
| `VITE_ENABLE_ANALYTICS` | Enable analytics | `false` | `true` |

**Note**: All environment variables must be prefixed with `VITE_` to be exposed to the browser.

## 🚨 Important Notes

### For Vercel Deployment

1. **Root Directory**: If deploying from a monorepo, set Root Directory to `frontend/dlrcm-main` in Vercel settings.

2. **Environment Variables**: Add all `VITE_*` variables in Vercel dashboard under Settings → Environment Variables.

3. **CORS**: Ensure your backend API allows requests from your Vercel domain:
   ```python
   # In your FastAPI backend
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.vercel.app"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **API URL**: Update `VITE_API_BASE_URL` to point to your deployed backend (not localhost).

5. **Build Time**: First build may take 2-3 minutes. Subsequent builds are faster with caching.

### Performance Optimization

Already configured:
- ✅ Asset caching (1 year for static assets)
- ✅ Code splitting via Vite
- ✅ Tree shaking for unused code
- ✅ Minification of JS/CSS
- ✅ Modern browser targets

## 🐛 Troubleshooting

### Build Fails on Vercel

**Problem**: `npm install` fails
**Solution**: Check Node.js version. Add `.nvmrc`:
```
20
```

**Problem**: TypeScript errors
**Solution**: Run `npm run typecheck` locally first

### Environment Variables Not Working

**Problem**: `import.meta.env.VITE_*` is undefined
**Solution**: 
1. Ensure variable starts with `VITE_`
2. Restart dev server after adding new variables
3. In Vercel, redeploy after adding variables

### CORS Errors in Production

**Problem**: API calls fail with CORS error
**Solution**: Add your Vercel domain to backend CORS settings

## 📚 Additional Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vercel Documentation](https://vercel.com/docs)
- [React Router](https://reactrouter.com/)

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/new-feature`
2. Make changes and test locally
3. Run linter: `npm run lint`
4. Commit: `git commit -m "Add new feature"`
5. Push: `git push origin feature/new-feature`
6. Create Pull Request

## 📝 License

Proprietary - MedTechAI Team

---

**Built with** ❤️ **by the MedTechAI Team**
