# Deployment Guide

## Overview

This guide covers deploying the Sapien AI-Quest API to production with all the latest features including notifications, spin wheel system, and external cron jobs.

## Prerequisites

- Python 3.9+
- PostgreSQL database
- Gemini API key
- Cron job service account (cron-job.org)

## Environment Variables

### Required Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# AI Service
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=your-secure-secret-key-here

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

### Optional Variables
```bash
# Access Token Expiration (default: 30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Upload Directory (default: uploads)
UPLOAD_DIR=uploads

# Max File Size (default: 10MB)
MAX_FILE_SIZE=10485760
```

## Deployment Options

### 1. Fly.io (Recommended - Free)

#### Setup
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly.io
fly auth login

# Initialize project
fly launch

# Add PostgreSQL database
fly postgres create

# Deploy
fly deploy
```

#### Environment Variables
```bash
# Set environment variables
fly secrets set GEMINI_API_KEY=your_key_here
fly secrets set SECRET_KEY=your_secret_here
fly secrets set ALLOWED_ORIGINS=https://your-frontend.com
```

#### Benefits
- ✅ **Free tier** with generous limits
- ✅ **Always running** (no sleep mode)
- ✅ **Global edge deployment**
- ✅ **Free PostgreSQL** database
- ✅ **Automatic SSL** certificates

### 2. Railway

#### Setup
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up

# Add PostgreSQL
railway add postgresql
```

#### Environment Variables
```bash
# Set in Railway dashboard or CLI
railway variables set GEMINI_API_KEY=your_key_here
railway variables set SECRET_KEY=your_secret_here
railway variables set ALLOWED_ORIGINS=https://your-frontend.com
```

#### Benefits
- ✅ **Easy deployment** from GitHub
- ✅ **Integrated database**
- ✅ **$5/month** pricing
- ✅ **Great developer experience**

### 3. Render

#### Setup
1. Connect your GitHub repository
2. Select "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Environment Variables
Set in Render dashboard:
- `GEMINI_API_KEY`
- `SECRET_KEY`
- `ALLOWED_ORIGINS`
- `DATABASE_URL` (from PostgreSQL service)

#### Benefits
- ✅ **Free tier** available
- ✅ **Easy GitHub integration**
- ⚠️ **Sleep mode** on free tier (wakes up quickly)

## Background Tasks Setup

### Using cron-job.org (Recommended)

#### 1. Create Account
- Go to [cron-job.org](https://cron-job.org)
- Sign up for free account
- Verify email

#### 2. Set Up Daily AI Messages
- **URL**: `https://your-app-url.com/api/cron/daily-ai-messages`
- **Method**: POST
- **Schedule**: 
  - Minutes: 0
  - Hours: 14 (2 PM UTC)
  - Days: *
  - Months: *
  - Weekdays: *
- **Title**: "Daily AI Messages"

#### 3. Set Up Quest Expiration Check
- **URL**: `https://your-app-url.com/api/cron/check-expired-quests`
- **Method**: POST
- **Schedule**:
  - Minutes: */5 (every 5 minutes)
  - Hours: *
  - Days: *
  - Months: *
  - Weekdays: *
- **Title**: "Check Expired Quests"

### Alternative Cron Services

#### EasyCron
- **URL**: [easycron.com](https://www.easycron.com)
- **Free Tier**: 20 executions/month
- **Features**: Good monitoring, detailed logs

#### Cronitor
- **URL**: [cronitor.io](https://cronitor.io)
- **Free Tier**: 5 monitors
- **Features**: Excellent monitoring and alerting

## Post-Deployment Setup

### 1. Create Admin User
```bash
# Run locally with production database URL
python create_admin.py
```

### 2. Test Endpoints
```bash
# Health check
curl https://your-app-url.com/health

# API documentation
# Visit: https://your-app-url.com/docs
```

### 3. Set Up Monitoring
- Monitor cron job execution logs
- Set up alerts for failed jobs
- Monitor application logs for errors

## Security Checklist

### ✅ Environment Variables
- [ ] All secrets stored in environment variables
- [ ] No hardcoded API keys or passwords
- [ ] `.env` file in `.gitignore`

### ✅ Database Security
- [ ] Strong database passwords
- [ ] Database access restricted to application
- [ ] Regular backups configured

### ✅ API Security
- [ ] CORS properly configured
- [ ] Rate limiting implemented (if needed)
- [ ] Input validation on all endpoints

### ✅ Monitoring
- [ ] Health checks configured
- [ ] Error logging implemented
- [ ] Cron job monitoring set up

## Troubleshooting

### Common Issues

#### 1. Cron Jobs Not Running
- Check cron service logs
- Verify URLs are accessible
- Ensure POST method is used

#### 2. Database Connection Issues
- Verify DATABASE_URL format
- Check database credentials
- Ensure database is accessible from deployment platform

#### 3. API Key Issues
- Verify GEMINI_API_KEY is set correctly
- Check API key permissions
- Ensure key hasn't expired

#### 4. CORS Issues
- Verify ALLOWED_ORIGINS includes your frontend domain
- Check for typos in domain names
- Ensure HTTPS is used in production

### Getting Help

1. **Check Logs**: Review application logs for detailed error messages
2. **Swagger UI**: Use `/docs` endpoint for API testing
3. **Health Check**: Use `/health` endpoint to verify system status
4. **Cron Monitoring**: Check cron service logs for background task issues

## Production Optimization

### Performance
- Enable database connection pooling
- Implement caching for frequently accessed data
- Monitor API response times

### Scalability
- Set up horizontal scaling if needed
- Monitor resource usage
- Implement load balancing for high traffic

### Backup Strategy
- Regular database backups
- Configuration file backups
- Log file rotation

## Support

For deployment issues:
1. Check the troubleshooting section above
2. Review application logs
3. Test endpoints using Swagger UI
4. Verify environment variables are set correctly
