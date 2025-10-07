# Cron Jobs Setup Guide

## Overview
Your application now uses **external cron jobs** instead of Redis + Celery for background tasks. This is simpler, cheaper, and more reliable.

## Available Cron Endpoints

### 1. Daily AI Messages
- **URL**: `POST https://your-app-url.com/api/cron/daily-ai-messages`
- **Purpose**: Sends automated AI messages to inactive users
- **Frequency**: Daily (recommended: 2 PM UTC)
- **Authentication**: None required (internal endpoint)

### 2. Check Expired Quests
- **URL**: `POST https://your-app-url.com/api/cron/check-expired-quests`
- **Purpose**: Automatically ends expired quests and distributes rewards
- **Frequency**: Every 5 minutes (recommended)
- **Authentication**: None required (internal endpoint)

## Setup with cron-job.org

### Step 1: Create Account
1. Go to [cron-job.org](https://cron-job.org)
2. Sign up for a free account
3. Verify your email

### Step 2: Add Daily AI Messages Job
1. Click "Create Cronjob"
2. **URL**: `https://your-app-url.com/api/cron/daily-ai-messages`
3. **Method**: POST
4. **Schedule**: 
   - **Minutes**: 0
   - **Hours**: 14 (2 PM UTC)
   - **Days**: *
   - **Months**: *
   - **Weekdays**: *
5. **Title**: "Daily AI Messages"
6. Click "Create"

### Step 3: Add Quest Expiration Job
1. Click "Create Cronjob"
2. **URL**: `https://your-app-url.com/api/cron/check-expired-quests`
3. **Method**: POST
4. **Schedule**: 
   - **Minutes**: */5 (every 5 minutes)
   - **Hours**: *
   - **Days**: *
   - **Months**: *
   - **Weekdays**: *
5. **Title**: "Check Expired Quests"
6. Click "Create"

### Step 4: Monitor Jobs
- Check the "Logs" tab to see if jobs are running successfully
- Look for HTTP 200 responses
- Monitor your application logs for any errors

## Alternative Cron Services

If cron-job.org doesn't work for you, here are other free alternatives:

### 1. EasyCron
- **URL**: [easycron.com](https://www.easycron.com)
- **Free Tier**: 20 executions/month
- **Features**: Good monitoring, detailed logs

### 2. Cronitor
- **URL**: [cronitor.io](https://cronitor.io)
- **Free Tier**: 5 monitors
- **Features**: Excellent monitoring and alerting

### 3. Uptime Robot
- **URL**: [uptimerobot.com](https://uptimerobot.com)
- **Free Tier**: 50 monitors
- **Features**: Good for monitoring + basic cron

## Testing Your Setup

### Test Daily AI Messages
```bash
curl -X POST https://your-app-url.com/api/cron/daily-ai-messages
```

### Test Quest Expiration
```bash
curl -X POST https://your-app-url.com/api/cron/check-expired-quests
```

Expected Response:
```json
{
  "status": "success",
  "messages_sent": 0,
  "total_users_checked": 0,
  "timestamp": "2024-01-01T12:00:00"
}
```

## Benefits of This Approach

✅ **No Redis dependency** - simpler deployment
✅ **No Celery complexity** - easier to maintain
✅ **Free cron services** - no additional costs
✅ **Reliable scheduling** - external service handles timing
✅ **Easy monitoring** - see job execution logs
✅ **Simple debugging** - just HTTP endpoints

## Troubleshooting

### Common Issues

1. **Jobs not running**: Check your app URL is correct and accessible
2. **HTTP 500 errors**: Check your app logs for database or AI service issues
3. **No users found**: This is normal if you don't have inactive users yet
4. **AI service errors**: Make sure your GEMINI_API_KEY is set correctly

### Monitoring
- Check cron-job.org logs regularly
- Monitor your application logs
- Set up alerts for failed jobs (if available)

## Migration Notes

- **Old Celery tasks**: Removed from codebase
- **Redis dependency**: Completely removed
- **Background processing**: Now handled by external cron jobs
- **Functionality**: Exactly the same, just triggered differently
