# AI Service Documentation

## Overview
The AI Service handles all AI-related functionality using Google's Gemini API for character responses, message scoring, and quest opening message generation.

## Configuration
```python
# Environment variables required
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro
```

## Core Methods

### `generate_character_response(quest_details, user_message, conversation_history)`
Generates AI character responses based on quest context and conversation history.

**Parameters:**
- `quest_details` (Dict): Quest properties, instructions, and additional text
- `user_message` (str): User's message to respond to
- `conversation_history` (List[Dict]): Previous conversation context

**Returns:**
```python
{
    "character_response": str,
    "success": bool,
    "error": str  # if success=False
}
```

### `score_user_message(user_message, quest_context, scoring_criteria)`
Scores user messages based on predefined criteria.

**Parameters:**
- `user_message` (str): Message to score
- `quest_context` (str): Quest context for scoring
- `scoring_criteria` (Dict[str, float]): Scoring weights

**Default Scoring Criteria:**
```python
{
    "creativity": 0.3,
    "depth": 0.4,
    "originality": 0.2,
    "emotional_intelligence": 0.1,
    "philosophical_insight": 0.0
}
```

**Returns:**
```python
{
    "score": int,  # 0-100
    "score_breakdown": Dict[str, int],
    "feedback": str,
    "success": bool,
    "error": str  # if success=False
}
```

### `generate_quest_opening_message(quest_details, quest_context)`
Generates the initial AI message for a quest.

**Parameters:**
- `quest_details` (Dict): Quest properties and instructions
- `quest_context` (str): Quest context description

**Returns:**
```python
{
    "opening_message": str,
    "success": bool,
    "error": str  # if success=False
}
```

## Prompt Engineering

### Character Response Prompts
Built dynamically based on:
- Character name and personality
- Quest context and background
- Conversation history (last 5 messages)
- User's current message

### Scoring Prompts
Structured to evaluate:
- **Creativity**: Originality and innovative thinking
- **Depth**: Philosophical insight and analysis
- **Originality**: Unique perspectives
- **Emotional Intelligence**: Empathy and understanding
- **Philosophical Insight**: Deep philosophical reasoning

### Opening Message Prompts
Designed to:
- Introduce the character
- Set up the quest scenario
- Create intrigue and motivation
- Explain response expectations

## Error Handling

### AI Service Failures
- **Fallback responses**: Default messages when AI fails
- **Error logging**: Detailed error tracking
- **Graceful degradation**: System continues without AI

### Common Issues
1. **API Rate Limits**: Implement exponential backoff
2. **Invalid Responses**: JSON parsing fallbacks
3. **Context Length**: Conversation history truncation
4. **Network Issues**: Retry mechanisms

## Performance Considerations

### Caching
- Character responses cached for similar inputs
- Quest context cached during quest lifecycle
- Conversation history limited to last 5 messages

### Optimization
- Async/await for non-blocking AI calls
- Batch processing for multiple requests
- Response streaming for long responses

## Integration Points

### Quest Creation
- Automatic opening message generation
- Character personality setup
- Quest context initialization

### Message Processing
- Real-time character responses
- Dynamic scoring based on quest criteria
- Conversation context maintenance

### Daily AI Messages
- Personalized engagement messages
- Quest-specific character interactions
- User activity-based content

## Monitoring

### Metrics Tracked
- AI response generation time
- Scoring accuracy and consistency
- User engagement with AI responses
- Error rates and failure types

### Logging
- All AI interactions logged
- Performance metrics recorded
- Error details captured
- User feedback integration

## Future Enhancements

### Planned Features
- **Multi-language support**: Character responses in different languages
- **Emotion detection**: AI responses based on user emotional state
- **Advanced scoring**: Machine learning-based scoring improvements
- **Character consistency**: Long-term character memory across quests
- **A/B testing**: Different AI response strategies
