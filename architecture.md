This document defines the database schema and admin dashboard structure for the Human vs AI app. It incorporates quests, participants, scoring, leaderboards, economy, treasury, daily bonuses, input monetization, and content media (profile images, videos, quest assets).

Core Entities
Users
user_id


username


email


created_at


Quests
quest_id


title


description


context


details (JSONB) → stores properties, instructions, additional_text


profile_image_url


media_url (image or video)


start_date


end_date


created_at


Quests are created by admins only.
Quest Economy
quest_economy_id


quest_id


starting_pool


treasury_percent


pool_percent


created_at


Defines how much goes into prize pool vs treasury.
Prize Distribution
distribution_id


quest_id


position_range (e.g., 1, 2, 3-10, 11-30)


percent → percent of pool for this position range


Participants
participant_id


user_id


quest_id


score


joined_at


Links users to quests, tracks scores.
User Inputs
input_id


user_id


quest_id


input_date


type (free, paid, ad, wheel)


amount (if paid)


created_at


Tracks how many inputs a user made and how they paid/unlocked them.
Treasury Ledger
ledger_id


quest_id


user_id


amount


source (quest_fee, extra_input, etc.)


created_at


Tracks how much is added to treasury from different sources.
Daily Bonus
bonus_id


user_id


bonus_date


amount


claimed


created_at


One daily bonus per user per day.
Chat Messages
message_id


quest_id


user_id (nullable → AI messages)


content


score


created_at


Stores chat history for each quest, scoring user replies.
Leaderboards
leaderboard_id


quest_id


user_id


total_score


rank


created_at


Used to display rankings per quest or globally.

Economy & Reward Distribution
Each quest has a starting prize pool.


Admin defines distribution rules (percentages by rank range).


Example distribution: 1st = 40%, 2nd = 10%, 3rd–10th = 5% each, 11th–30th = 3% each.


Extra inputs cost $1, but may also be unlocked by watching ads or spinning a wheel.


Admin decides how much of each payment goes to pool vs treasury.


Treasury transactions are logged in treasury_ledger.



Admin Dashboard (Next.js + TS)
Navigation (sidebar)
Quests → CRUD quests (create with form, list, edit, delete)


Leaderboard → global + per-quest ranking


Treasury → ledger, stats


Analytics → graphs of performance


Quest Creation Form
Inputs:


Title, Description, Context


Profile Image Upload


Quest Media Upload (image or video)


Properties (dynamic key/value with predefined + add new)


Instructions (dynamic key/value with predefined + add new)


Additional Text (dynamic key/value)


Features:


Preview all data before submission


Download JSON file before submitting


Submit → dummy action function


Leaderboard
Table of participants (username, score, rank)


Toggle between per quest and global view


Treasury
Table of transactions


Summary stats (total treasury, total rewards)


Analytics
Graphs with dummy data (using recharts):


Participation over time


Treasury growth


Average scores per quest



Updated SQL Schema (Postgres)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quests (
    quest_id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    context TEXT,
    details JSONB,
    profile_image_url TEXT,
    media_url TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quest_economy (
    quest_economy_id SERIAL PRIMARY KEY,
    quest_id INT NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
    starting_pool NUMERIC(12,2) DEFAULT 0,
    treasury_percent NUMERIC(5,2) DEFAULT 0,
    pool_percent NUMERIC(5,2) DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE prize_distribution (
    distribution_id SERIAL PRIMARY KEY,
    quest_id INT NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
    position_range TEXT NOT NULL,
    percent NUMERIC(5,2) NOT NULL
);

CREATE TABLE participants (
    participant_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    quest_id INT NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
    score NUMERIC(10,2) DEFAULT 0,
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, quest_id)
);

CREATE TABLE user_inputs (
    input_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    quest_id INT NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
    input_date DATE NOT NULL,
    type VARCHAR(20) NOT NULL,
    amount NUMERIC(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE treasury_ledger (
    ledger_id SERIAL PRIMARY KEY,
    quest_id INT NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
    user_id INT REFERENCES users(user_id),
    amount NUMERIC(12,2) NOT NULL,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE daily_bonus (
    bonus_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    bonus_date DATE NOT NULL,
    amount NUMERIC(12,2) DEFAULT 0,
    claimed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, bonus_date)
);

CREATE TABLE chat_messages (
    message_id SERIAL PRIMARY KEY,
    quest_id INT NOT NULL REFERENCES quests(quest_id) ON DELETE CASCADE,
    user_id INT REFERENCES users(user_id),
    content TEXT NOT NULL,
    score NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE leaderboard (
    leaderboard_id SERIAL PRIMARY KEY,
    quest_id INT REFERENCES quests(quest_id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    total_score NUMERIC(10,2) DEFAULT 0,
    rank INT,
    created_at TIMESTAMP DEFAULT NOW()
);



