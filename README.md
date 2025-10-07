# Sapien AI-Quest Backend

FastAPI backend for the philosophical AI storytelling game with economy and leaderboards.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Create admin user
python create_admin.py

# Run development server
uvicorn app.main:app --reload
```

## Documentation

- **API Documentation**: [API_DOCS.md](API_DOCS.md)
- **AI Service**: [AI_SERVICE_DOC.md](AI_SERVICE_DOC.md)
- **Router Details**: [ROUTERS_DOCS.md](ROUTERS_DOCS.md)
- **General Info**: [GENERAL_DOCS.md](GENERAL_DOCS.md)

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Key Features

- **Quest Management**: Full CRUD with status control (active/ended/stalled)
- **AI Integration**: Gemini-powered character responses and scoring
- **User System**: Pi Network integration with activity tracking
- **Economy**: Wallet system with reward distribution
- **Monetization**: Paid inputs, ad integration, spin wheel system
- **Notifications**: In-app notification system for user engagement
- **Daily AI Messages**: Automated user engagement
- **Admin Controls**: JWT-protected management endpoints
- **Background Tasks**: Automated quest management via cron jobs

## Environment Variables

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/sapien_ai_quest
GEMINI_API_KEY=your_gemini_api_key
# Redis removed - using external cron jobs instead
```

## Deployment

### Railway
```bash
railway login
railway up
railway add postgresql
# Redis no longer needed - using external cron jobs
```

### Fly.io (Recommended - Free)
```bash
fly launch
fly deploy
# Add PostgreSQL database
fly postgres create
```

### Background Tasks Setup
```bash
# Set up cron jobs at cron-job.org:
# 1. Daily AI Messages: POST /api/cron/daily-ai-messages (Daily at 2 PM UTC)
# 2. Quest Expiration: POST /api/cron/check-expired-quests (Every 5 minutes)
```

### Docker
```bash
docker build -t sapienai-backend .
docker run -p 8000:8000 sapienai-backend
```
