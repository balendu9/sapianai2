# Sapien AI-Quest API Documentation

## Overview

The Sapien AI-Quest API is a comprehensive backend system for a philosophical AI storytelling game with an integrated economy, leaderboards, and quest management system. The API handles user interactions, AI-powered conversations, payment processing, and reward distribution.

## Base URL
```
http://localhost:8000
```

## Authentication

The API uses JWT-based authentication for admin operations. Users are identified by their Pi Network user ID.

### Admin Authentication
- **Login**: `POST /api/auth/login`
- **Get Current Admin**: `GET /api/auth/me`
- **Headers**: `Authorization: Bearer <jwt_token>`

## Core Concepts

### 1. Users
- **Primary Key**: `user_id` (Pi Network ID)
- **Optional Fields**: `username`, `email`
- **No Password**: Authentication handled by Pi Network

### 2. Quests
- **Character-based AI interactions**
- **Percentage-based reward distribution**
- **Real-time payment splitting**
- **Lifecycle management** (active, paused, ended)

### 3. Economy
- **Treasury**: Platform revenue (10% of payments)
- **User Pool**: Prize money (90% of payments)
- **Real-time splitting** on each payment

## API Endpoints

### New Features (Latest Update)
- **In-App Notifications**: Complete notification system for user engagement
- **Spin Wheel System**: Gamification with configurable prizes and rewards
- **External Cron Jobs**: Background tasks via cron-job.org (no Redis needed)
- **Enhanced Monetization**: Paid inputs, ad integration, spin rewards

### Authentication Endpoints

#### `POST /api/auth/login`
**Description**: Admin login
**Body**:
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```
**Response**:
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "expires_in": 1800,
  "admin": {
    "admin_id": "uuid",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "is_active": true,
    "is_super_admin": true
  }
}
```

#### `GET /api/auth/me`
**Description**: Get current admin info
**Headers**: `Authorization: Bearer <token>`

### User Management

#### `POST /api/users/`
**Description**: Create a new user
**Body**:
```json
{
  "user_id": "pi_network_user_id",
  "username": "optional_username",
  "email": "optional@email.com"
}
```

#### `GET /api/users/{user_id}`
**Description**: Get user by ID
**Response**:
```json
{
  "user_id": "pi_network_user_id",
  "username": "username",
  "email": "email@example.com",
  "created_at": "2025-09-30T14:44:15",
  "total_score": 0.0,
  "quests_completed": 0
}
```

### Quest Management

#### `POST /api/quests/json`
**Description**: Create a new quest (JSON format - recommended)
**Headers**: `Authorization: Bearer <token>`
**Body**:
```json
{
  "title": "The Keeper of Secrets",
  "description": "I am the Keeper, guardian of treasures unseen...",
  "context": "An ancient presence that challenges seekers...",
  "properties": {
    "character_name": "The Keeper",
    "personality": "Enigmatic, skeptical, hard to convince",
    "background": "A timeless guardian of treasures and truths",
    "character_quirks": ["speaks in riddles", "tests patience"],
    "special_abilities": ["time manipulation", "truth detection"]
  },
  "instructions": {
    "speaking_style": "Cryptic, layered, and elusive",
    "hints_style": "Subtle riddles and paradoxes",
    "interaction_style": "Persuasion-driven, testing wit, patience, and reasoning",
    "response_length": "Medium (2-3 sentences)",
    "difficulty_level": "High"
  },
  "additional_text": {
    "teaser": "Few have passed my challenge. Speak with more than words—move the silence itself.",
    "opening_message": "Welcome, seeker. I have watched countless souls approach with empty promises. What makes you different?",
    "success_message": "Impressive. You have earned the right to know my secrets.",
    "failure_message": "Your words lack the weight of truth. Return when you have something meaningful to say."
  },
  "distribution_rules": {
    "rank_percentages": {
      "1": 40,
      "2": 20,
      "3": 15,
      "4-10": 15,
      "11+": 10
    },
    "participation_bonus": 5,
    "early_bird_bonus": 10
  },
  "initial_pool": 1000.0,
  "treasury_percentage": 10.0,
  "user_percentage": 90.0,
  "start_date": "2025-10-01T15:00:00",
  "end_date": "2025-10-15T18:00:00"
}
```

#### `GET /api/quests/`
**Description**: Get all quests
**Query Parameters**:
- `active_only`: boolean (default: true)

#### `GET /api/quests/{quest_id}`
**Description**: Get quest by ID

#### `PUT /api/quests/{quest_id}`
**Description**: Update quest
**Headers**: `Authorization: Bearer <token>`

#### `DELETE /api/quests/{quest_id}`
**Description**: Delete quest
**Headers**: `Authorization: Bearer <token>`

### Quest Participation

#### `POST /api/quests/{quest_id}/join`
**Description**: Join a quest
**Body**:
```json
{
  "user_id": "pi_network_user_id"
}
```

#### `DELETE /api/quests/{quest_id}/leave`
**Description**: Leave a quest
**Body**:
```json
{
  "user_id": "pi_network_user_id"
}
```

#### `GET /api/quests/{quest_id}/participants`
**Description**: Get quest participants

### AI Messaging

#### `POST /api/quests/{quest_id}/messages`
**Description**: Send message to AI character
**Body**:
```json
{
  "user_id": "pi_network_user_id",
  "content": "Hello Keeper, I seek your wisdom and the treasures you guard. May I prove my worth through words?"
}
```
**Response**:
```json
{
  "message_id": "uuid",
  "user_id": "pi_network_user_id",
  "quest_id": "uuid",
  "content": "User message",
  "ai_response": "AI character response",
  "score": 8.5,
  "timestamp": "2025-09-30T14:45:23"
}
```

#### `GET /api/quests/{quest_id}/messages/{user_id}`
**Description**: Get chat history for user in quest

### Payment System

#### `POST /api/payments/process-payment`
**Description**: Process user payment and split between treasury and pool
**Body**:
```json
{
  "user_id": "pi_network_user_id",
  "quest_id": "uuid",
  "amount": 1.0,
  "payment_type": "extra_input"
}
```
**Response**:
```json
{
  "success": true,
  "message": "Payment of $1.0 processed successfully",
  "split_details": {
    "total_amount": 1.0,
    "treasury_amount": 0.1,
    "pool_amount": 0.9,
    "treasury_percentage": 10.0,
    "user_percentage": 90.0
  },
  "new_pool_totals": {
    "quest_id": "uuid",
    "total_treasury": 0.1,
    "total_pool": 0.9,
    "total_collected": 1.0
  }
}
```

#### `GET /api/payments/quest/{quest_id}/pool-totals`
**Description**: Get current pool totals for a quest

#### `GET /api/payments/platform/totals`
**Description**: Get platform-wide treasury and pool totals

### Treasury Management

#### `GET /api/treasury/`
**Description**: Get treasury information
**Response**:
```json
{
  "total_treasury": 100.0,
  "total_prize_pools": 900.0,
  "rewards_distributed": 50.0,
  "recent_transactions": [
    {
      "pool_id": "uuid",
      "quest_id": "uuid",
      "source": "user_payment",
      "amount": 1.0,
      "split_to_treasury": 0.1,
      "split_to_pool": 0.9,
      "created_at": "2025-09-30T14:45:23"
    }
  ]
}
```

### Daily AI Messages

#### `GET /api/daily-ai-messages/stats`
**Description**: Get daily AI messages statistics

#### `GET /api/daily-ai-messages/{user_id}/messages`
**Description**: Get user's daily AI messages

#### `POST /api/daily-ai-messages/{user_id}/messages`
**Description**: Send manual daily AI message

#### `PUT /api/daily-ai-messages/{user_id}/settings`
**Description**: Update user's daily AI message settings

#### `GET /api/daily-ai-messages/{user_id}/settings`
**Description**: Get user's daily AI message settings

### Wallet System

#### `GET /api/wallet/{user_id}/balance`
**Description**: Get user wallet balance

#### `GET /api/wallet/{user_id}/transactions`
**Description**: Get user transaction history

#### `POST /api/wallet/{user_id}/withdraw`
**Description**: Request withdrawal

#### `GET /api/wallet/{user_id}/pending-withdrawals`
**Description**: Get pending withdrawals

### Leaderboard

#### `GET /api/leaderboard/`
**Description**: Get global leaderboard

#### `GET /api/leaderboard/{quest_id}`
**Description**: Get quest-specific leaderboard

### Analytics

#### `GET /api/analytics/platform`
**Description**: Get platform analytics
**Headers**: `Authorization: Bearer <token>`

## Data Flow

### 1. User Journey
```
1. User Registration → POST /api/users/
2. Browse Quests → GET /api/quests/
3. Join Quest → POST /api/quests/{quest_id}/join
4. Chat with AI → POST /api/quests/{quest_id}/messages
5. Make Payments → POST /api/payments/process-payment
6. Quest Ends → Rewards Distributed
```

### 2. Payment Flow
```
1. User pays $1.00
2. Immediate split:
   - Treasury: $0.10 (10%)
   - User Pool: $0.90 (90%)
3. Recorded in quest_pools table
4. Pool totals updated in real-time
```

### 3. Quest Lifecycle
```
1. Admin creates quest → POST /api/quests/json
2. Quest becomes active
3. Users join and participate
4. Admin can pause → PUT /api/quests/{quest_id}
5. Quest ends automatically or manually
6. Rewards distributed based on distribution_rules
```

## Database Schema

### Key Tables
- **users**: User information
- **quests**: Quest definitions and settings
- **quest_participants**: User participation in quests
- **quest_pools**: Payment splits and pool tracking
- **quest_rewards**: Final reward distributions
- **chat_messages**: AI conversation history
- **leaderboards**: Cached rankings
- **user_wallets**: User balance and transactions

## Error Handling

### Common Error Responses
```json
{
  "detail": "Error message"
}
```

### Status Codes
- **200**: Success
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **500**: Internal Server Error

## Rate Limiting
- No rate limiting currently implemented
- Consider implementing for production

## CORS
- Configured for development
- Update `ALLOWED_ORIGINS` in production

## Environment Variables
```env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Swagger UI
Visit `http://localhost:8000/docs` for interactive API documentation.

## Production Considerations

1. **Database**: Switch from SQLite to PostgreSQL
2. **Authentication**: Implement proper JWT secret management
3. **Rate Limiting**: Add rate limiting for API endpoints
4. **Logging**: Implement comprehensive logging
5. **Monitoring**: Add health checks and monitoring
6. **Security**: Implement proper CORS and security headers
7. **Background Tasks**: Set up external cron jobs at cron-job.org

## New API Endpoints

### Notification Endpoints

#### `GET /api/notifications/{user_id}/notifications`
**Description**: Get user's notifications
**Parameters**:
- `unread_only` (query): Filter for unread notifications only
- `limit` (query): Maximum number of notifications to return

#### `POST /api/notifications/{user_id}/notifications`
**Description**: Create a new notification for a user
**Body**:
```json
{
  "user_id": "user123",
  "title": "Quest Completed!",
  "message": "Congratulations! You won 100 Pi tokens!",
  "notification_type": "quest_win",
  "quest_id": "quest456",
  "metadata": {"reward_amount": 100}
}
```

#### `POST /api/notifications/{user_id}/notifications/mark-read`
**Description**: Mark notifications as read
**Body**:
```json
{
  "notification_ids": ["notif1", "notif2", "notif3"]
}
```

#### `GET /api/notifications/{user_id}/notifications/unread-count`
**Description**: Get count of unread notifications

#### `POST /api/notifications/admin/send-special-notification`
**Description**: Send special notification to users (admin only)
**Body**:
```json
{
  "target_type": "all_users", // or "specific_users", "quest_participants"
  "user_ids": ["user1", "user2"], // required if target_type is "specific_users"
  "quest_id": "quest123", // required if target_type is "quest_participants"
  "title": "Special Event!",
  "message": "A new quest has been released!",
  "notification_type": "special"
}
```

### Spin Wheel Endpoints

#### `GET /api/spin-wheel/wheels`
**Description**: Get all active spin wheels

#### `GET /api/spin-wheel/{user_id}/status`
**Description**: Get user's spin wheel status
**Response**:
```json
{
  "user_id": "user123",
  "spins_used_today": 1,
  "spins_remaining_today": 2,
  "last_spin_at": "2024-01-01T12:00:00",
  "can_spin": true
}
```

#### `POST /api/spin-wheel/{user_id}/spin/{wheel_id}`
**Description**: Spin the wheel for rewards
**Response**:
```json
{
  "attempt_id": "attempt123",
  "prize_won": {
    "name": "Bonus Inputs",
    "type": "inputs",
    "value": 5
  },
  "input_reward": 5,
  "pi_reward": 0.0,
  "message": "Congratulations! You won: Bonus Inputs (+5 inputs)"
}
```

#### `GET /api/spin-wheel/{user_id}/history`
**Description**: Get user's spin history

#### `POST /api/spin-wheel/admin/create-wheel`
**Description**: Create a new spin wheel (admin only)
**Body**:
```json
{
  "name": "Daily Bonus Wheel",
  "description": "Spin for daily rewards",
  "max_spins_per_day": 3,
  "spin_cost": 0.0,
  "prizes": [
    {
      "name": "Bonus Inputs",
      "description": "Extra inputs for quests",
      "type": "inputs",
      "value": 5,
      "probability": 0.5,
      "rarity": "common"
    },
    {
      "name": "Pi Tokens",
      "description": "Pi cryptocurrency",
      "type": "pi_tokens",
      "value": 10.0,
      "probability": 0.3,
      "rarity": "rare"
    }
  ]
}
```

### Cron Job Endpoints

#### `POST /api/cron/daily-ai-messages`
**Description**: Trigger daily AI messages (called by cron-job.org)
**Schedule**: Daily at 2 PM UTC

#### `POST /api/cron/check-expired-quests`
**Description**: Check for expired quests and end them (called by cron-job.org)
**Schedule**: Every 5 minutes

## Support

For issues or questions, refer to the Swagger UI documentation at `/docs` or check the server logs for detailed error information.
