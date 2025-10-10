#!/bin/bash

# 🚀 MedTechAI RCM Backend - Render Deployment Script
# This script helps you deploy your FastAPI backend to Render

set -e  # Exit on any error

echo "🚀 MedTechAI RCM Backend - Render Deployment"
echo "============================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: This directory is not a git repository"
    echo "Please run: git init && git add . && git commit -m 'Initial commit'"
    exit 1
fi

# Check if files are committed
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Uncommitted changes detected. Committing them now..."
    git add .
    git commit -m "Prepare for Render deployment - $(date)"
fi

# Check if remote origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "❌ Error: No GitHub remote found"
    echo "Please add your GitHub repository:"
    echo "git remote add origin https://github.com/yourusername/your-repo.git"
    exit 1
fi

echo "✅ Git repository is ready"
echo ""

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main

echo ""
echo "🎉 Code pushed to GitHub successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to https://render.com"
echo "2. Sign up/login with GitHub"
echo "3. Click 'New +' → 'Blueprint'"
echo "4. Connect your GitHub repository"
echo "5. Render will auto-detect render.yaml configuration"
echo "6. If Docker build fails, try the simple version:"
echo "   - Rename render-simple.yaml to render.yaml"
echo "   - Push changes and redeploy"
echo "7. Add your environment variables:"
echo "   - OPENAI_API_KEY=your-key-here"
echo "   - ANTHROPIC_API_KEY=your-key-here (optional)"
echo "   - GOOGLE_API_KEY=your-key-here (optional)"
echo "8. Click 'Create Blueprint'"
echo ""
echo "🌐 Your backend will be available at:"
echo "https://medtechai-rcm-backend.onrender.com"
echo ""
echo "📚 For detailed instructions, see: RENDER_DEPLOYMENT_GUIDE.md"
echo ""
echo "✨ Happy deploying!"
