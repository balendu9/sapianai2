# 🤖 AI Service Testing Guide

## **What You Need to Test the AI Service**

### **1. Required API Key**
You need a **Google Gemini API key** to test the AI service:

#### **Get Your API Key:**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" 
4. Create a new API key
5. Copy the key

#### **Set the API Key:**
```bash
# Option 1: Environment variable
export GEMINI_API_KEY="your-api-key-here"

# Option 2: Create .env file
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

### **2. Test the AI Service**

#### **Run the Test Script:**
```bash
python test_ai_service.py
```

This will test:
- ✅ Character response generation
- ✅ Message scoring
- ✅ Quest opening messages
- ✅ Different character types
- ✅ Error handling
- ✅ API endpoint integration

### **3. What the AI Service Does**

#### **Core Functions:**
1. **Generate Character Responses** - Creates AI responses based on quest character properties
2. **Score User Messages** - Evaluates user responses on creativity, depth, etc.
3. **Generate Opening Messages** - Creates quest introduction messages
4. **Character Customization** - Supports different character personalities and styles

#### **Character Properties Supported:**
- `character_name` - Name of the AI character
- `personality` - Character's personality traits
- `background` - Character's backstory
- `character_quirks` - Unique character traits
- `special_abilities` - Character's special powers
- `speaking_style` - How the character talks
- `hints_style` - How the character gives hints
- `interaction_style` - How the character interacts

### **4. API Endpoints That Use AI**

#### **Quest Creation:**
```http
POST /api/quests/json
```
- Automatically generates opening AI message
- Uses quest properties to create character

#### **Messaging:**
```http
POST /api/messaging/quest/{quest_id}/message
```
- Generates AI character responses
- Scores user messages
- Updates leaderboard

#### **Daily AI Messages:**
```http
POST /api/daily-ai-messages/generate
```
- Generates daily engagement messages
- Personalized for each user

### **5. Example Quest Data for Testing**

```json
{
  "title": "The Oracle's Challenge",
  "description": "A philosophical quest with an AI oracle",
  "context": "You encounter a mysterious oracle who challenges your thinking",
  "properties": {
    "character_name": "The Oracle",
    "personality": "mysterious and wise",
    "background": "Ancient being of knowledge",
    "character_quirks": ["speaks in riddles", "loves philosophical questions"],
    "special_abilities": ["foresight", "wisdom"]
  },
  "instructions": {
    "speaking_style": "poetic and enigmatic",
    "hints_style": "cryptic and mysterious",
    "interaction_style": "challenging and thought-provoking",
    "example_responses": [
      "The path you seek lies within the question itself...",
      "Wisdom comes not from answers, but from understanding the question."
    ]
  },
  "additional_text": {
    "backstory": "The Oracle has guided seekers for millennia through philosophical challenges."
  }
}
```

### **6. Testing Checklist**

#### **Before Testing:**
- [ ] API key is set
- [ ] Server is running (`uvicorn app.main:app --reload`)
- [ ] Internet connection is available
- [ ] All dependencies are installed

#### **During Testing:**
- [ ] AI responses are generated
- [ ] Character personality is consistent
- [ ] Scoring system works
- [ ] Error handling works
- [ ] API endpoints respond correctly

#### **After Testing:**
- [ ] Check logs for any errors
- [ ] Verify AI responses are appropriate
- [ ] Test different character types
- [ ] Verify scoring accuracy

### **7. Troubleshooting**

#### **Common Issues:**

**"API Key not configured"**
- Set GEMINI_API_KEY environment variable
- Check .env file exists and has the key

**"Cannot connect to API server"**
- Start server: `uvicorn app.main:app --reload`
- Check if port 8000 is available

**"AI responses are generic"**
- Check quest properties are detailed
- Verify character customization is working

**"Scoring not working"**
- Check scoring criteria in quest instructions
- Verify JSON parsing is working

### **8. Expected AI Behavior**

#### **Character Responses:**
- Should match the character's personality
- Should use the specified speaking style
- Should reference character background and abilities
- Should stay in character consistently

#### **Scoring:**
- Should evaluate on creativity, depth, originality, etc.
- Should provide feedback explaining the score
- Should use the specified scoring criteria weights

#### **Opening Messages:**
- Should introduce the character
- Should set up the quest scenario
- Should be engaging and immersive
- Should match the character's style

### **9. Performance Expectations**

- **Response Time:** 2-5 seconds per AI call
- **Token Usage:** ~500-1000 tokens per response
- **Rate Limits:** Follows Google Gemini API limits
- **Cost:** ~$0.001-0.005 per response (approximate)

### **10. Next Steps After Testing**

1. **Customize Characters:** Create unique character personalities
2. **Adjust Scoring:** Fine-tune scoring criteria for your needs
3. **Test Edge Cases:** Try unusual inputs and scenarios
4. **Monitor Performance:** Check response times and quality
5. **Scale Testing:** Test with multiple concurrent users

The AI service is the core of your quest system - make sure it's working perfectly! 🚀
