# Router Documentation

## Router Structure
Each router handles a specific domain of the API with consistent patterns and error handling.

## Quest Router (`app/routers/quests.py`)
**Purpose**: Quest lifecycle management, status control, and information retrieval.

### Key Features
- **CRUD Operations**: Create, read, update, delete quests
- **Status Management**: Active, ended, stalled status with pause/resume
- **Admin Controls**: Protected endpoints for quest management
- **File Uploads**: Profile images and quest media handling
- **AI Integration**: Automatic opening message generation

### Status Flow
```
Created → Active → [Paused] → Active → Ended
                ↓
              Stalled
```

### Admin-Only Endpoints
- Quest creation, updates, deletion
- Quest pause/resume functionality
- Quest info updates
- Manual quest ending

## User Router (`app/routers/users.py`)
**Purpose**: User management and activity tracking.

### Key Features
- **User Registration**: Pi Network user ID integration
- **Activity Tracking**: Last activity timestamps
- **Input Management**: Daily input claiming system
- **Validation**: Comprehensive input validation

### User Creation Flow
1. Validate Pi Network user ID (required)
2. Check for existing user
3. Validate optional username/email
4. Create user with default settings

## Messaging Router (`app/routers/messaging.py`)
**Purpose**: AI chat functionality and message processing.

### Key Features
- **AI Integration**: Character response generation
- **Message Scoring**: Dynamic scoring based on quest criteria
- **Conversation History**: Context-aware responses
- **Real-time Processing**: Immediate AI responses

### Message Flow
1. User sends message
2. Validate message content
3. Check quest participation
4. Generate AI response
5. Score user message
6. Update participant score
7. Save both messages

## Participation Router (`app/routers/participation.py`)
**Purpose**: Quest participation management.

### Key Features
- **Quest Joining**: User participation registration
- **Participant Tracking**: Score and activity monitoring
- **Opening Messages**: Quest introduction retrieval
- **Leave Functionality**: Quest exit handling

## Leaderboard Router (`app/routers/leaderboard.py`)
**Purpose**: Ranking and competition display.

### Key Features
- **Global Rankings**: Platform-wide leaderboards
- **Quest Rankings**: Quest-specific leaderboards
- **Score Aggregation**: Total score calculations
- **Ranking Logic**: Position-based sorting

## Treasury Router (`app/routers/treasury.py`)
**Purpose**: Financial transaction management.

### Key Features
- **Transaction History**: User financial activity
- **Pool Contributions**: Quest pool tracking
- **Reward Distribution**: Prize allocation
- **Financial Analytics**: Transaction summaries

## Wallet Router (`app/routers/wallet.py`)
**Purpose**: User wallet and transaction management.

### Key Features
- **Balance Management**: Wallet balance tracking
- **Transaction Processing**: Withdrawal and deposit handling
- **Pi Network Integration**: External payment processing
- **Reward Distribution**: Quest completion rewards

### Transaction Types
- `deposit`: Pi Network payments
- `withdrawal`: User withdrawal requests
- `reward`: Quest completion rewards
- `bonus`: Daily bonus payments

## Analytics Router (`app/routers/analytics.py`)
**Purpose**: Platform analytics and reporting.

### Key Features
- **Admin-Only Access**: Protected analytics endpoints
- **Platform Metrics**: User and quest statistics
- **Performance Tracking**: System health monitoring
- **Business Intelligence**: Revenue and engagement metrics

## Authentication Router (`app/routers/auth.py`)
**Purpose**: Admin authentication and authorization.

### Key Features
- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt password security
- **Token Management**: Expiration and validation
- **Admin Protection**: Role-based access control

### Authentication Flow
1. Admin provides email/password
2. Validate credentials
3. Generate JWT token
4. Return token with expiration
5. Validate token on protected endpoints

## Daily AI Messages Router (`app/routers/daily_ai_messages.py`)
**Purpose**: Automated user engagement system.

### Key Features
- **Automated Messaging**: Scheduled AI messages
- **User Preferences**: Opt-in/opt-out functionality
- **Message Types**: General and quest-specific messages
- **Engagement Tracking**: Message read status

### Message Types
- `daily_reminder`: General engagement messages
- `quest_promotion`: Quest-specific character messages
- `manual`: Admin-sent messages

## Bonus Router (`app/routers/bonus.py`)
**Purpose**: Daily bonus system management.

### Key Features
- **Daily Bonuses**: User reward system
- **Bonus Tracking**: Claim status monitoring
- **Pi Network Integration**: External payment processing
- **Bonus Analytics**: Usage statistics

## Common Patterns

### Error Handling
All routers implement consistent error handling:
- Input validation with detailed error messages
- Database transaction rollback on errors
- HTTP status code standardization
- Comprehensive logging

### Authentication
Protected endpoints use dependency injection:
```python
current_admin: AdminUser = Depends(get_current_admin)
```

### Database Operations
Consistent database patterns:
- Session dependency injection
- Transaction management
- Error rollback handling
- Connection health checks

### Response Models
All endpoints use Pydantic schemas:
- Request validation
- Response serialization
- Type safety
- Documentation generation
