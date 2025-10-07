# General Documentation

## Project Structure
```
sapienai/
├── app/
│   ├── core/           # Configuration and settings
│   ├── models/         # Database models
│   ├── routers/        # API endpoints
│   ├── schemas/        # Pydantic models
│   ├── services/       # Business logic
│   └── tasks/          # Background tasks
├── requirements.txt    # Dependencies
├── create_admin.py     # Admin user creation
└── test_api.py        # API testing
```

## Technology Stack
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT with bcrypt
- **AI Integration**: Google Gemini API
- **Background Tasks**: External cron jobs (cron-job.org)
- **Monetization**: Pi Network integration, spin wheel system
- **Notifications**: In-app notification system
- **Documentation**: Swagger UI / ReDoc

## Environment Setup

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sapien_ai_quest

# AI Service
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro

# Authentication
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis removed - using external cron jobs instead
# REDIS_URL=redis://localhost:6379/0
```

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Create admin user
python create_admin.py

# Run the server
uvicorn app.main:app --reload
```

## Database Schema

### Core Tables
- **users**: User accounts and activity tracking
- **quests**: Quest definitions and status
- **quest_participants**: User participation in quests
- **chat_messages**: AI conversation history
- **user_wallets**: User financial accounts
- **wallet_transactions**: Financial transaction records
- **daily_ai_messages**: Automated engagement messages
- **notifications**: In-app user notifications
- **spin_wheels**: Spin wheel configurations and prizes
- **spin_attempts**: User spin wheel attempts and rewards
- **quest_inputs**: Free, paid, ad, and spin-earned inputs
- **admin_users**: Admin authentication

### Key Relationships
- Users participate in multiple quests
- Quests have multiple participants
- Messages belong to quests and users
- Wallets track user financial activity
- Transactions link to quests and users

## Security Features

### Authentication
- JWT-based admin authentication
- Password hashing with bcrypt
- Token expiration handling
- Role-based access control

### Input Validation
- Pydantic model validation
- File upload restrictions
- SQL injection prevention
- XSS protection

### Data Protection
- Database connection pooling
- Transaction rollback on errors
- Input sanitization
- Error message sanitization

## Performance Considerations

### Database Optimization
- Connection pooling with SQLAlchemy
- Indexed foreign keys
- Efficient query patterns
- Transaction management

### Caching Strategy
- Database query optimization
- AI response caching
- Efficient connection pooling

### Background Tasks
- **Daily AI Messages**: Automated user engagement (2 PM UTC daily)
- **Quest Expiration**: Automatic quest ending (every 5 minutes)
- **Reward Distribution**: Automatic prize distribution on quest completion
- **External Cron Jobs**: Using cron-job.org for reliable scheduling

### Scalability
- Async/await patterns
- Background task processing
- Horizontal scaling support
- Load balancing ready

## Monitoring and Logging

### Health Checks
- Database connectivity testing
- AI service availability
- System resource monitoring
- External cron job status

### Error Tracking
- Comprehensive error logging
- Performance metrics
- User activity tracking
- System health monitoring

## Deployment Considerations

### Production Requirements
- PostgreSQL database
- Python 3.9+
- Environment variable configuration
- SSL/TLS certificates
- External cron job service (cron-job.org)

### Security Hardening
- CORS configuration
- Rate limiting implementation
- Input validation
- Error message sanitization
- Database security

### Backup Strategy
- Database backups
- Configuration backups
- Log file rotation
- Disaster recovery plan

## Development Guidelines

### Code Standards
- Type hints throughout
- Comprehensive docstrings
- Error handling patterns
- Consistent naming conventions

### Testing Strategy
- Unit tests for business logic
- Integration tests for API endpoints
- Database transaction testing
- AI service mocking

### Documentation
- API documentation with Swagger
- Code comments and docstrings
- Architecture documentation
- Deployment guides
