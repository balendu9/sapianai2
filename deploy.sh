#!/bin/bash

# Sapien AI-Quest Backend Deployment Script
echo "🚀 Deploying Sapien AI-Quest Backend to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project
echo "📦 Creating Railway project..."
railway init

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
railway add postgresql

# Add Redis cache
echo "🔴 Adding Redis cache..."
railway add redis

# Set environment variables
echo "⚙️ Setting environment variables..."
railway variables set GEMINI_API_KEY=$GEMINI_API_KEY
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "📚 API Documentation: https://your-app.railway.app/docs"
echo "🔍 Health Check: https://your-app.railway.app/health"
