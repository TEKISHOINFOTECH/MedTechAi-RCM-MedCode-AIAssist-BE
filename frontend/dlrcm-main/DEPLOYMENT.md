# Deployment Guide for Vercel

## Quick Deploy to Vercel

### Option 1: Deploy from GitHub (Recommended)
1. Push your code to a GitHub repository
2. Connect your repository to Vercel
3. Vercel will automatically detect it's a Vite project
4. Add environment variables in Vercel dashboard (see below)

### Option 2: Deploy using Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow the prompts
```

## Environment Variables Setup

### Required for AI Features (Optional)
Add these in your Vercel dashboard under **Project Settings > Environment Variables**:

1. Go to your Vercel project dashboard
2. Click on **Settings** tab
3. Click on **Environment Variables** in the sidebar
4. Add these variables:

| Name | Value | Environment |
|------|-------|-------------|
| `VITE_SUPABASE_URL` | `https://your-project-id.supabase.co` | Production, Preview, Development |
| `VITE_SUPABASE_ANON_KEY` | `your-anon-key-here` | Production, Preview, Development |

**Important:** Make sure to select all three environments (Production, Preview, Development) when adding the variables.

### How to get Supabase credentials:
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings > API
4. Copy the Project URL and anon/public key

## Build Configuration

The project is already configured for Vercel with:
- ✅ `vercel.json` - Vercel configuration
- ✅ `vite.config.ts` - Optimized build settings
- ✅ Code splitting for better performance
- ✅ SPA routing support

## Features Status

### ✅ Works without Supabase:
- Dashboard with mock data
- Claims review interface
- File upload UI
- Settings page
- Basic claim editing

### ⚠️ Requires Supabase:
- AI-powered SOAP notes improvement
- ICD-10 code suggestions
- CPT code suggestions
- Real-time AI insights

## Performance Optimizations

The build includes:
- Code splitting (vendor, router, supabase chunks)
- Gzip compression
- Optimized bundle sizes
- No source maps in production

## Troubleshooting

### Build fails?
- Check that all dependencies are in `package.json`
- Ensure TypeScript compilation passes: `npm run typecheck`

### Environment variables not working?
- Make sure they start with `VITE_`
- Redeploy after adding new environment variables
- Check Vercel function logs for errors
- Verify variables are added to all environments (Production, Preview, Development)
- If you see "references Secret which does not exist" error, ignore it - the app will work without Supabase

### Routing issues?
- The `vercel.json` includes SPA fallback routing
- All routes will serve `index.html`

## Support

If you encounter issues:
1. Check the Vercel deployment logs
2. Test locally with `npm run build && npm run preview`
3. Verify environment variables are set correctly

