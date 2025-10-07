Core Concepts
A Quest = an AI chat session with a theme/character (e.g., Dragon Warrior).


Users join quests created by the admin.


Each reply is scored.


Quests end with prize pool distribution.


Users can continue chatting with past quests after they end (non-scored/free chat mode).


Daily mechanics: daily bonuses, hints, free/paid inputs.


Monetization: users pay for extra inputs beyond free quota, or earn them via ads or spin-to-win.



Tables Overview
1. users
Stores registered players.
Column
Type
Notes
user_id (PK)
UUID
Unique user ID
username
VARCHAR
Display name
email
VARCHAR
Optional
created_at
TIMESTAMP
Account creation


2. quests
Admin-created AI chat quests.
Column
Type
Notes
quest_id (PK)
UUID
Unique quest ID
details
JSONB
Holds title, description, context, properties, instructions, hints
reward_amount
INT
Base reward pool (starting prize)
distribution_rules
JSONB
Custom reward distribution (percentages per rank/tier, pool vs treasury split)
start_date
TIMESTAMP
Quest start
end_date
TIMESTAMP
Quest end
created_at
TIMESTAMP
When added
profile_image_url
TEXT
Optional profile image for the AI quest
media_url
TEXT
Optional image/video asset for the quest

➡️ Example distribution_rules JSON:
{
  "distribution": [
    { "rank": 1, "percent": 40 },
    { "rank": 2, "percent": 10 },
    { "rank_range": [3, 10], "percent": 5 },
    { "rank_range": [11, 30], "percent": 3 }
  ],
  "pool_split": { "to_prize_pool": 80, "to_treasury": 20 },
  "starting_prize_pool": 1000
}


3. quest_participants
Tracks user participation in quests.
Column
Type
Notes
qp_id (PK)
UUID


quest_id (FK)
UUID


user_id (FK)
UUID


score
INT
Latest/total score
reply_log
JSONB
History of replies + scores
joined_at
TIMESTAMP
When user joined
last_reply_at
TIMESTAMP
Updated when user replies
last_hint_sent
TIMESTAMP
Last time a hint was sent


4. quest_inputs
Tracks free, paid, and earned inputs.
Column
Type
Notes
input_id (PK)
UUID


quest_id (FK)
UUID


user_id (FK)
UUID


date
DATE
Which day
input_type
VARCHAR
free / paid / ad / spin
count
INT
Number of inputs granted
payment_amount
DECIMAL
If paid, how much
created_at
TIMESTAMP



➡️ Each user gets free inputs per day (e.g., 2). Extra inputs are tracked here when purchased or earned.

5. quest_pools
Tracks pool growth and treasury allocation.
Column
Type
Notes
pool_id (PK)
UUID


quest_id (FK)
UUID


source
VARCHAR
user_payment / admin_fund / bonus_event
amount
DECIMAL
Total contribution
split_to_pool
DECIMAL
Added to prize pool
split_to_treasury
DECIMAL
Sent to treasury
created_at
TIMESTAMP




6. quest_rewards
Final payouts when quest ends.
Column
Type
Notes
reward_id (PK)
UUID


quest_id (FK)
UUID


user_id (FK)
UUID
Participant rewarded
rank
INT
Final rank
percent
DECIMAL
% share of pool
amount
DECIMAL
Tokens/points awarded
distributed_at
TIMESTAMP




7. leaderboards
Stores cached ranks.
Column
Type
Notes
leaderboard_id (PK)
UUID


quest_id (FK)
UUID
Null for global leaderboard
user_id (FK)
UUID
Player
score
INT
Aggregated score
rank
INT
Cached rank
updated_at
TIMESTAMP




8. daily_bonus
Tracks daily reward claims.
Column
Type
Notes
bonus_id (PK)
UUID


user_id (FK)
UUID


date_claimed
DATE


reward_amount
INT
Bonus amount
claimed_at
TIMESTAMP




Flows
Prize Distribution
On end_date, calculate leaderboard ranks.


Apply distribution_rules: assign % to ranks/ranges.


Insert payouts into quest_rewards.


Update user balances/wallets.


Inputs
Each day, user gets 2 free inputs (recorded in quest_inputs).


Extra inputs cost $1 → logged as paid in quest_inputs.


Watching ads or spin wheel → logged as ad or spin in quest_inputs.


Pool updates in quest_pools with pool/treasury split.


Daily Bonus
Users claim once per day (one row in daily_bonus).


Daily Hints
Scheduler checks quest_participants.


If last_reply_at < today and last_hint_sent < today → send hint, update last_hint_sent.


Past Quests
Users can continue chatting after end_date.


reply_log keeps history.


Rewards/leaderboards frozen post-end.



✅ This schema supports flexible prize pools, monetization via paid/ad/spin inputs, per-quest reward rules, daily bonuses, inactivity hints, and ongoing chat access for past quests.

SQL: Postgres CREATE TABLE statements (UUID-based)
-- Requires the pgcrypto extension for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- Users
CREATE TABLE users (
  user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(200),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Quests
CREATE TABLE quests (
  quest_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  details JSONB NOT NULL,
  reward_amount NUMERIC(12,2) DEFAULT 0,
  distribution_rules JSONB,
  start_date TIMESTAMP WITH TIME ZONE,
  end_date TIMESTAMP WITH TIME ZONE,
  profile_image_url TEXT,
  media_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Quest Participants
CREATE TABLE quest_participants (
  qp_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  score INTEGER DEFAULT 0,
  reply_log JSONB DEFAULT '[]'::jsonb,
  joined_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  last_reply_at TIMESTAMP WITH TIME ZONE,
  last_hint_sent TIMESTAMP WITH TIME ZONE,
  UNIQUE(quest_id, user_id)
);


-- Quest Inputs
CREATE TABLE quest_inputs (
  input_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  input_date DATE NOT NULL,
  input_type VARCHAR(20) NOT NULL,
  count INTEGER DEFAULT 0,
  payment_amount NUMERIC(12,2) DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Quest Pools
CREATE TABLE quest_pools (
  pool_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
  source VARCHAR(50) NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  split_to_pool NUMERIC(12,2) NOT NULL,
  split_to_treasury NUMERIC(12,2) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Quest Rewards
CREATE TABLE quest_rewards (
  reward_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  rank INTEGER NOT NULL,
  percent NUMERIC(5,2) NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  distributed_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Leaderboards
CREATE TABLE leaderboards (
  leaderboard_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID REFERENCES quests(quest_id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  score INTEGER DEFAULT 0,
  rank INTEGER,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Daily Bonus
CREATE TABLE daily_bonus (
  bonus_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
  date_claimed DATE NOT NULL,
  reward_amount INTEGER DEFAULT 0,
  claimed_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  UNIQUE(user_id, date_claimed)
);


-- Chat Messages
CREATE TABLE chat_messages (
  message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
  user_id UUID,
  content TEXT NOT NULL,
  score INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);


-- Prize Distribution Rules (optional detailed table)
CREATE TABLE prize_distribution_rules (
  rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  quest_id UUID NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
  position_start INTEGER NOT NULL,
  position_end INTEGER NOT NULL,
  percent NUMERIC(5,2) NOT NULL
);


-- Quest Pools Aggregated View (optional materialized view suggestion)
-- CREATE MATERIALIZED VIEW quest_pool_totals AS ...





