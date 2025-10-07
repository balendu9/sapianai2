1. Users Flow
Table: users


Description: Stores all registered players.


Connection:


Joins quests (quest_participants.user_id)


Makes inputs (quest_inputs.user_id)


Claims daily bonuses (daily_bonus.user_id)


Receives rewards (quest_rewards.user_id)


Messages are tracked in chat_messages.user_id


Notes: Each user has a unique UUID used as the primary key everywhere.



2. Quests Flow
Table: quests


Description: Admin-created AI chat sessions with properties, instructions, hints, media, start/end dates, reward distribution rules.


Connections:


Participants: quest_participants.quest_id → each user that joins the quest


Inputs: quest_inputs.quest_id → tracks free/paid/spin/ad inputs


Pools: quest_pools.quest_id → tracks contributions to prize pool and treasury


Rewards: quest_rewards.quest_id → calculated after quest ends


Leaderboard: leaderboards.quest_id → aggregate ranks per quest


Chat messages: chat_messages.quest_id → full chat log for that quest


Flow:
Admin creates a quest → details, media, distribution rules.


Quest becomes active on start_date.


Users join quest → recorded in quest_participants.


Users reply → messages stored in chat_messages with scores updated in quest_participants.score.


Daily mechanics: free inputs tracked in quest_inputs, bonuses in daily_bonus, hints sent based on last_reply_at/last_hint_sent.


Pool contributions logged in quest_pools as users make paid inputs or admin adds funds.


On end_date, calculate quest_rewards based on distribution_rules and leaderboard ranks.



3. Quest Participants Flow
Table: quest_participants


Description: Tracks each user in a quest and their score + chat history.


Connections:


user_id → connects to users


quest_id → connects to quests


reply_log → stores history of replies with scores


last_reply_at → used for sending hints


last_hint_sent → ensures hints are sent once per day


Flow:


When a user joins → new quest_participants row created.


Each message scored → score updated and appended to reply_log.


Daily hints scheduler checks last_reply_at/last_hint_sent.



4. Quest Inputs Flow
Table: quest_inputs


Description: Tracks free, paid, and earned inputs for a quest on a per-day basis.


Connections:


user_id → connects to users


quest_id → connects to quests


Flow:


Each user receives daily free inputs (e.g., 2).


Additional inputs: paid → $1, ad → earned from watching ads, spin → earned from spin wheel.


count and payment_amount recorded.


Pool updates reflected in quest_pools.



5. Quest Pools Flow
Table: quest_pools


Description: Tracks contributions to the prize pool and treasury.


Connections:


quest_id → connects to quests


source → user_payment, admin_fund, bonus_event


Flow:


When user pays for extra inputs → a row is added.


When admin adds funds → a row is added.


split_to_pool vs split_to_treasury calculated per row.


Summarized in the dashboard for each quest.



6. Quest Rewards Flow
Table: quest_rewards


Description: Final rewards distributed after quest ends.


Connections:


quest_id → connects to quests


user_id → connects to users


Calculated using quest_participants.score and quests.distribution_rules


Flow:


On quest end → leaderboard ranks determined.


Distribution rules applied → % of prize pool.


Row created in quest_rewards for each rewarded participant.


Updates wallets/balances externally.


Note: Only visible after quest ends; can be refreshed asynchronously in admin dashboard.



7. Leaderboards Flow
Table: leaderboards


Description: Cached ranks for quick display.


Connections:


quest_id → optional (null for global)


user_id → connects to users


Flow:


Aggregates scores from quest_participants and updates score + rank.


Can display global or per quest.



8. Daily Bonus Flow
Table: daily_bonus


Description: Tracks once-per-day bonus claims.


Connections:


user_id → connects to users


Flow:


Scheduler generates daily bonus.


Users claim → row created.


Checks prevent double claiming per day (UNIQUE(user_id, date_claimed)).



9. Chat Messages Flow
Table: chat_messages


Description: Stores all chat messages for quests.


Connections:


user_id → optional, null for AI messages


quest_id → connects to quests


Scores of user messages also reflected in quest_participants.score


Flow:


Each new message → appended to table.


Messages can be replayed after quest ends for past quest chats.



Overall Flow Diagram (Logical Connections)
users
 ├─< quest_participants >─ quests
 │        │                   │
 │        └─< chat_messages >─┘
 │
 ├─< quest_inputs >─┐
 │                  │
 │                  └─> quest_pools
 │
 ├─< daily_bonus >
 │
 └─< quest_rewards >─ quests
          │
          └─< leaderboards >─ quests

Legend:
─< = one-to-many relationship


└─ = many-to-one or optional

