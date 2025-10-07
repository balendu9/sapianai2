@echo off
echo 🚀 Deploying Sapien AI-Quest Backend to Railway...

REM Check if Railway CLI is installed
railway --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Railway CLI not found. Installing...
    npm install -g @railway/cli
)

REM Login to Railway
echo 🔐 Logging into Railway...
railway login

REM Create new project
echo 📦 Creating Railway project...
railway init

REM Add PostgreSQL database
echo 🗄️ Adding PostgreSQL database...
railway add postgresql

REM Add Redis cache
echo 🔴 Adding Redis cache...
railway add redis

REM Set environment variables
echo ⚙️ Setting environment variables...
railway variables set GEMINI_API_KEY=%GEMINI_API_KEY%
railway variables set SECRET_KEY=your-secret-key-here
railway variables set ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com

REM Deploy
echo 🚀 Deploying to Railway...
railway up

echo ✅ Deployment complete!
echo 📚 API Documentation: https://your-app.railway.app/docs
echo 🔍 Health Check: https://your-app.railway.app/health
