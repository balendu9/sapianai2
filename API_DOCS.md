# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Most endpoints require Bearer token authentication:
```bash
Authorization: Bearer <your_jwt_token>
```

## Endpoints Overview

### Quest Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/quests/` | List all quests | No |
| POST | `/api/quests/` | Create quest | Admin |
| GET | `/api/quests/{quest_id}` | Get quest details | No |
| PUT | `/api/quests/{quest_id}` | Update quest | Admin |
| DELETE | `/api/quests/{quest_id}` | Delete quest | Admin |
| GET | `/api/quests/search` | Search quests | No |
| GET | `/api/quests/active` | Get active quests | No |
| GET | `/api/quests/{quest_id}/status` | Get quest status | No |
| POST | `/api/quests/{quest_id}/start` | Start quest | No |
| POST | `/api/quests/{quest_id}/end` | End quest | No |
| POST | `/api/quests/{quest_id}/pause` | Pause quest | Admin |
| POST | `/api/quests/{quest_id}/resume` | Resume quest | Admin |
| GET | `/api/quests/{quest_id}/info` | Get quest info | No |
| PUT | `/api/quests/{quest_id}/info` | Update quest info | Admin |
| GET | `/api/quests/{quest_id}/admin-info` | Get admin quest info | Admin |
| POST | `/api/quests/check-expired-quests` | Trigger expired quest check | Admin |

### User Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/{user_id}` | Get user details | No |
| POST | `/api/users/` | Create user | No |
| GET | `/api/users/{user_id}/inputs` | Get user inputs | No |
| POST | `/api/users/{user_id}/claim-daily-inputs` | Claim daily inputs | No |

### Quest Participation
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/quests/{quest_id}/join` | Join quest | No |
| GET | `/api/quests/{quest_id}/participants` | Get participants | No |
| DELETE | `/api/quests/{quest_id}/leave` | Leave quest | No |
| GET | `/api/quests/{quest_id}/opening-message` | Get opening message | No |

### Messaging
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/quests/{quest_id}/messages` | Send message | No |
| GET | `/api/quests/{quest_id}/messages` | Get messages | No |

### Leaderboard
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/leaderboard/` | Global leaderboard | No |
| GET | `/api/leaderboard/{quest_id}` | Quest leaderboard | No |

### Treasury
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/treasury/` | Treasury info | No |
| GET | `/api/treasury/{user_id}/transactions` | User transactions | No |

### Analytics
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/analytics/` | Platform analytics | Admin |

### Daily Bonuses
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/daily-bonuses/{user_id}` | Get daily bonus | No |
| POST | `/api/daily-bonuses/{user_id}/claim` | Claim daily bonus | No |

### Wallet Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/wallet/{user_id}/balance` | Get wallet balance | No |
| GET | `/api/wallet/{user_id}/transactions` | Get transactions | No |
| POST | `/api/wallet/{user_id}/withdraw` | Withdraw funds | No |
| POST | `/api/wallet/distribute-quest-rewards` | Distribute rewards | Admin |
| GET | `/api/wallet/{user_id}/pending-withdrawals` | Get pending withdrawals | No |
| POST | `/api/wallet/pi-webhook` | Pi backend webhook | No |
| POST | `/api/wallet/pi-payment-confirmation` | Pi payment confirmation | No |

### Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/token` | Admin login | No |
| GET | `/api/auth/me` | Get current admin | Admin |
| POST | `/api/auth/logout` | Admin logout | Admin |
| POST | `/api/auth/verify-token` | Verify token | Admin |

### Daily AI Messages
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/daily-ai-messages/{user_id}/messages` | Get user messages | No |
| POST | `/api/daily-ai-messages/{user_id}/messages` | Send manual message | No |
| PUT | `/api/daily-ai-messages/{user_id}/settings` | Update settings | No |
| GET | `/api/daily-ai-messages/{user_id}/settings` | Get settings | No |
| GET | `/api/daily-ai-messages/stats` | Get message stats | No |
| POST | `/api/daily-ai-messages/{message_id}/mark-read` | Mark as read | No |
| POST | `/api/daily-ai-messages/trigger-daily-messages` | Trigger messages | No |

### System
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | Root endpoint | No |
| GET | `/health` | Health check | No |

## Response Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

## Rate Limiting
Currently no rate limiting implemented. Consider implementing for production.

## CORS
Configured to allow all origins in development. Update for production security.
