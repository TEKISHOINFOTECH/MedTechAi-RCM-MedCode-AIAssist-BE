#!/bin/bash

# MedTechAI RCM - Quick Deployment Script
# This script helps you deploy the frontend to Vercel

set -e

echo "🚀 MedTechAI RCM - Deployment Helper"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_success "Found project root directory"
echo ""

# Menu
echo "What would you like to deploy?"
echo ""
echo "1) Frontend to Vercel (Recommended - Quick & Easy)"
echo "2) Test Frontend Locally"
echo "3) Test Backend Locally"
echo "4) Full Local Stack (Frontend + Backend)"
echo "5) Generate requirements.txt for Backend Deployment"
echo "6) View Deployment Documentation"
echo "7) Exit"
echo ""

read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        print_info "Preparing Frontend for Vercel Deployment..."
        echo ""
        
        # Check if git is clean
        if [[ -n $(git status -s) ]]; then
            print_warning "You have uncommitted changes"
            echo ""
            git status -s
            echo ""
            read -p "Do you want to commit these changes? (y/n): " commit_choice
            
            if [ "$commit_choice" = "y" ]; then
                read -p "Enter commit message: " commit_msg
                git add .
                git commit -m "$commit_msg"
                print_success "Changes committed"
            fi
        fi
        
        # Push to GitHub
        print_info "Pushing to GitHub..."
        git push origin main
        print_success "Code pushed to GitHub"
        echo ""
        
        # Instructions for Vercel
        print_success "Next Steps:"
        echo ""
        echo "1. Go to: https://vercel.com/new"
        echo "2. Click 'Import Git Repository'"
        echo "3. Select your repository"
        echo "4. Configure:"
        echo "   - Framework Preset: Vite"
        echo "   - Root Directory: frontend/dlrcm-main"
        echo "   - Build Command: npm run build"
        echo "   - Output Directory: dist"
        echo ""
        echo "5. Add Environment Variables:"
        echo "   VITE_API_BASE_URL=http://localhost:8000"
        echo "   VITE_ENV=production"
        echo "   VITE_ENABLE_MOCK_DATA=true"
        echo ""
        echo "6. Click Deploy!"
        echo ""
        print_info "See VERCEL_DEPLOYMENT_GUIDE.md for detailed instructions"
        ;;
        
    2)
        print_info "Starting Frontend Development Server..."
        cd frontend/dlrcm-main
        
        if [ ! -d "node_modules" ]; then
            print_info "Installing dependencies..."
            npm install
        fi
        
        print_success "Starting at http://localhost:5173"
        npm run dev
        ;;
        
    3)
        print_info "Starting Backend API Server..."
        
        if [ ! -f ".env" ]; then
            print_warning ".env file not found"
            read -p "Do you want to create it from .env.example? (y/n): " create_env
            
            if [ "$create_env" = "y" ]; then
                cp env.example .env
                print_success ".env file created"
                print_warning "Please add your OPENAI_API_KEY to .env file"
                read -p "Press Enter to continue..."
            fi
        fi
        
        print_success "Starting at http://localhost:8000"
        print_info "API docs will be at http://localhost:8000/docs"
        uv run uvicorn app.main:app --reload --port 8000
        ;;
        
    4)
        print_info "Starting Full Local Stack..."
        
        # Start backend in background
        print_info "Starting Backend API on port 8000..."
        uv run uvicorn app.main:app --reload --port 8000 &
        BACKEND_PID=$!
        
        sleep 3
        
        # Start frontend
        print_info "Starting Frontend on port 5173..."
        cd frontend/dlrcm-main
        
        if [ ! -d "node_modules" ]; then
            print_info "Installing dependencies..."
            npm install
        fi
        
        npm run dev &
        FRONTEND_PID=$!
        
        echo ""
        print_success "Full stack running!"
        echo ""
        echo "🔗 Frontend: http://localhost:5173"
        echo "🔗 Backend API: http://localhost:8000"
        echo "🔗 API Docs: http://localhost:8000/docs"
        echo ""
        print_warning "Press Ctrl+C to stop both servers"
        
        # Wait for user interrupt
        trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
        wait
        ;;
        
    5)
        print_info "Generating requirements.txt for backend deployment..."
        uv pip compile pyproject.toml -o requirements.txt
        print_success "requirements.txt generated"
        echo ""
        print_info "This file can be used for:"
        echo "  - Vercel Python deployment"
        echo "  - Railway deployment"
        echo "  - Render deployment"
        echo "  - Docker builds"
        ;;
        
    6)
        print_info "Opening deployment documentation..."
        echo ""
        echo "Available guides:"
        echo ""
        echo "1. DEPLOYMENT_ACTION_PLAN.md - Complete deployment roadmap"
        echo "2. VERCEL_DEPLOYMENT_GUIDE.md - Detailed Vercel instructions"
        echo "3. FRONTEND_DEPLOYMENT_READY.md - Frontend deployment summary"
        echo "4. frontend/dlrcm-main/README.md - Frontend documentation"
        echo ""
        read -p "Which guide would you like to view? (1-4): " doc_choice
        
        case $doc_choice in
            1) cat DEPLOYMENT_ACTION_PLAN.md | less ;;
            2) cat VERCEL_DEPLOYMENT_GUIDE.md | less ;;
            3) cat FRONTEND_DEPLOYMENT_READY.md | less ;;
            4) cat frontend/dlrcm-main/README.md | less ;;
            *) print_error "Invalid choice" ;;
        esac
        ;;
        
    7)
        print_info "Goodbye!"
        exit 0
        ;;
        
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac


