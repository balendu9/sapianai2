# 🌍 Global Leaderboard & Ads System - Complete Documentation

## **1. Global Leaderboard System**

### **Overview:**
- **Global Score**: Average of all quest scores per user
- **Formula**: `(Sum of all quest scores) / (Total quests participated)`
- **Daily Bonuses**: Top 3 users get daily rewards (admin configurable)

### **Key Features:**
✅ **Cross-Quest Scoring**: Aggregates scores from all quests
✅ **Daily Bonuses**: Top 3 users get daily rewards
✅ **Admin Configurable**: Set bonus amounts per rank
✅ **Real-time Updates**: Updates when quests end
✅ **Fair Ranking**: Based on average performance

### **API Endpoints:**

#### **Get Global Leaderboard:**
```http
GET /api/global-leaderboard/?limit=10
```

#### **Update Global Leaderboard:**
```http
POST /api/global-leaderboard/update
```

#### **Process Daily Bonuses:**
```http
POST /api/global-leaderboard/daily-bonuses/process
```

#### **Set Bonus Configuration:**
```http
POST /api/global-leaderboard/daily-bonuses/config
{
  "rank_1_amount": 100.0,
  "rank_2_amount": 50.0,
  "rank_3_amount": 25.0,
  "currency": "PI"
}
```

#### **Get User Global Stats:**
```http
GET /api/global-leaderboard/user/{user_id}
```

---

## **2. Ads System**

### **Overview:**
- **Ad Verification**: Token-based system for ad completion
- **Credit Rewards**: Users earn credits for watching ads
- **Rate Limiting**: Daily limits and cooldowns
- **Provider Support**: Google AdMob, Unity Ads, etc.

### **Key Features:**
✅ **Token Verification**: Secure ad completion tracking
✅ **Rate Limiting**: Daily limits and cooldowns
✅ **Credit Rewards**: Automatic credit distribution
✅ **Provider Agnostic**: Works with any ad provider
✅ **Admin Configurable**: Set limits and rewards

### **API Endpoints:**

#### **Create Ad Verification:**
```http
POST /api/ads/verify?user_id={user_id}&quest_id={quest_id}&ad_provider=google
```

#### **Verify Ad Completion:**
```http
POST /api/ads/complete
{
  "verification_token": "uuid-token",
  "verification_data": {
    "ad_loaded": true,
    "ad_completed": true
  }
}
```

#### **Get User Ad Stats:**
```http
GET /api/ads/stats/{user_id}
```

#### **Check Ad Eligibility:**
```http
GET /api/ads/eligibility/{user_id}?quest_id={quest_id}
```

#### **Set Ad Configuration:**
```http
POST /api/ads/config
{
  "ad_provider": "google",
  "ad_unit_id": "ca-app-pub-xxx/xxx",
  "reward_per_ad": 1.0,
  "daily_limit_per_user": 10,
  "cooldown_minutes": 5
}
```

---

## **3. Complete Flow Examples**

### **Global Leaderboard Flow:**
1. **User participates in quests** → Scores tracked per quest
2. **Quest ends** → Global leaderboard updates automatically
3. **Daily at 00:00 UTC** → Process daily bonuses for top 3
4. **Users get rewards** → Automatically added to wallet

### **Ads Flow:**
1. **User wants credits** → Call `/api/ads/verify`
2. **System checks eligibility** → Cooldown, daily limits
3. **User watches ad** → Gets verification token
4. **Ad completes** → Call `/api/ads/complete` with token
5. **System verifies** → Rewards user with credits

---

## **4. Database Models**

### **Global Leaderboard:**
- `GlobalLeaderboard`: User rankings and scores
- `DailyBonus`: Daily bonus records
- `DailyBonusConfig`: Admin configuration

### **Ads System:**
- `AdReward`: Ad completion tracking
- `AdConfig`: Ad configuration
- `AdVerification`: Verification tokens

---

## **5. Configuration Examples**

### **Daily Bonus Configuration:**
```json
{
  "rank_1_amount": 100.0,    // 1st place gets 100 PI
  "rank_2_amount": 50.0,     // 2nd place gets 50 PI
  "rank_3_amount": 25.0,     // 3rd place gets 25 PI
  "currency": "PI"
}
```

### **Ads Configuration:**
```json
{
  "ad_provider": "google",
  "ad_unit_id": "ca-app-pub-xxx/xxx",
  "reward_per_ad": 1.0,      // 1 credit per ad
  "daily_limit_per_user": 10, // Max 10 ads per day
  "cooldown_minutes": 5      // 5 min between ads
}
```

---

## **6. Integration with Existing Systems**

### **Credits System:**
- Ads reward users with credits
- Credits are spent on quest messages
- Daily bonuses add to wallet balance

### **Quest System:**
- Quest scores contribute to global leaderboard
- Global leaderboard updates when quests end
- Ads can be watched for specific quests

### **Wallet System:**
- Daily bonuses add to user wallet
- Ad rewards add to user credits
- All transactions are logged

---

## **7. Admin Functions**

### **Global Leaderboard:**
- Set daily bonus amounts
- Process daily bonuses
- Update global leaderboard
- View user statistics

### **Ads System:**
- Configure ad providers
- Set reward amounts
- Set daily limits and cooldowns
- Monitor ad statistics

---

## **8. Security Features**

### **Ad Verification:**
- Token-based verification
- Time-limited tokens (10 minutes)
- Provider-specific verification
- Duplicate prevention

### **Rate Limiting:**
- Daily ad limits per user
- Cooldown between ads
- Verification token expiration
- Fraud prevention

---

## **9. Monitoring & Analytics**

### **Global Leaderboard:**
- User participation tracking
- Score distribution analysis
- Daily bonus distribution
- Performance metrics

### **Ads System:**
- Ad completion rates
- User engagement metrics
- Revenue tracking
- Fraud detection

---

## **10. Future Enhancements**

### **Planned Features:**
- Real-time leaderboard updates
- Advanced ad fraud detection
- Multi-currency support
- Advanced analytics dashboard
- Push notifications for bonuses

This system provides a complete solution for global competition and ad-based monetization! 🚀
