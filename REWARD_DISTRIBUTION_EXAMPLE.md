# 🏆 Reward Distribution System - Complete Example

## **Quest Setup:**
```json
{
  "initial_pool": 1000.0,
  "treasury_percentage": 10.0,
  "user_percentage": 90.0,
  "rank_distribution": {
    "1": 50.0,       // 1st place gets 50%
    "2-13": 40.0,    // 2nd-13th place split 40% among actual participants
    "14-50": 10.0    // 14th-50th place split 10% among actual participants
  }
}
```

## **User Payments During Quest:**
- User A pays 100 PI → 90 PI goes to user pool, 10 PI to treasury
- User B pays 50 PI → 45 PI goes to user pool, 5 PI to treasury
- User C pays 200 PI → 180 PI goes to user pool, 20 PI to treasury
- **Total User Pool Contributions**: 90 + 45 + 180 = 315 PI

## **Total Quest Pool Calculation:**
```
Total Quest Pool = Initial Pool + User Pool Contributions
Total Quest Pool = 1000 + 315 = 1315 PI
```

## **Final Leaderboard (when someone reaches 100%):**
**Scenario 1: Only 5 people in ranks 2-13**
1. **User C** - 100% score → Gets 50% of 1315 = **657.5 PI**
2. **User A** - 95% score → Gets 8% of 1315 = **105.2 PI** (40% ÷ 5 = 8% each)
3. **User B** - 90% score → Gets 8% of 1315 = **105.2 PI**
4. **User D** - 85% score → Gets 8% of 1315 = **105.2 PI**
5. **User E** - 80% score → Gets 8% of 1315 = **105.2 PI**
6. **User F** - 75% score → Gets 8% of 1315 = **105.2 PI**

**Scenario 2: 8 people in ranks 2-13**
1. **User C** - 100% score → Gets 50% of 1315 = **657.5 PI**
2. **User A** - 95% score → Gets 5% of 1315 = **65.75 PI** (40% ÷ 8 = 5% each)
3. **User B** - 90% score → Gets 5% of 1315 = **65.75 PI**
4. **User D** - 85% score → Gets 5% of 1315 = **65.75 PI**
5. **User E** - 80% score → Gets 5% of 1315 = **65.75 PI**
6. **User F** - 75% score → Gets 5% of 1315 = **65.75 PI**
7. **User G** - 70% score → Gets 5% of 1315 = **65.75 PI**
8. **User H** - 65% score → Gets 5% of 1315 = **65.75 PI**
9. **User I** - 60% score → Gets 5% of 1315 = **65.75 PI**

## **Automatic Balance Updates:**
- **User C's wallet**: +657.5 PI (automatically added)
- **User A's wallet**: +131.5 PI (automatically added)
- **User B's wallet**: +131.5 PI (automatically added)
- And so on...

## **Key Features:**
✅ **100% Pool Distribution**: Always distributes exactly 100% of the total pool
✅ **Dynamic Range Distribution**: Counts actual participants in each range
✅ **Automatic Balances**: Users get rewards instantly in their wallets
✅ **Total Pool**: Includes both initial pool + user contributions
✅ **Fair Splitting**: Ranges are divided equally among actual participants
✅ **Real-time**: Happens immediately when quest ends
✅ **No Waste**: No rewards left unclaimed - every PI goes to participants

## **Example Range Calculations:**
- **"2-13": 40%** → 5 actual participants → 40% ÷ 5 = 8% each
- **"2-13": 40%** → 8 actual participants → 40% ÷ 8 = 5% each
- **"14-50": 10%** → 3 actual participants → 10% ÷ 3 = 3.33% each

## **Dynamic Distribution Logic:**
1. **Count Participants**: Count how many people are actually in each range
2. **Split Percentage**: Divide the range percentage by actual participant count
3. **Fair Distribution**: Each person in the range gets the same percentage
4. **Flexible Ranges**: Works with any range size (2-13, 14-50, etc.)

This ensures fair distribution where ranges split their percentage equally among the actual number of participants in that range! 🎯
