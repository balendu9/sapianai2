# 🎭 Opening Message Refinement Guide

## **New Approach: AI Refines Admin Templates**

Instead of generating opening messages from scratch, the AI now **refines** opening message templates provided by admins in the JSON. This gives you much more control over the quest content while still leveraging AI to enhance it.

## **How It Works**

### **1. Admin Provides Template**
In your quest JSON, include an `opening_message_template` in the `properties` section:

```json
{
  "properties": {
    "character_name": "Chronos, the Oracle of Time",
    "personality": "ancient, wise, mysterious, and slightly melancholic",
    "opening_message_template": "Welcome, seeker, to the realm of temporal mysteries. I am Chronos, the Oracle of Time, and I have been waiting for you. The threads of destiny have brought you here to unlock the ancient prophecies that will shape the future. Are you ready to begin your journey through the corridors of time?"
  }
}
```

### **2. AI Refines the Template**
The AI takes your template and refines it to:
- Match the character's speaking style perfectly
- Incorporate the character's personality
- Reference the quest title and description
- Use the character's hints style
- Create more intrigue and motivation
- Stay true to the character's background

### **3. Fallback to Generation**
If no template is provided, the AI falls back to generating from scratch (old behavior).

## **JSON Structure**

### **Complete Example:**
```json
{
  "title": "The Oracle's Prophecy Quest",
  "description": "A mystical journey where seekers must unlock ancient prophecies",
  "context": "In the realm of Chronos, where time flows like a river...",
  
  "properties": {
    "character_name": "Chronos, the Oracle of Time",
    "personality": "ancient, wise, mysterious, and slightly melancholic",
    "background": "An immortal being who has witnessed the rise and fall of civilizations",
    "opening_message_template": "Welcome, seeker, to the realm of temporal mysteries. I am Chronos, the Oracle of Time, and I have been waiting for you. The threads of destiny have brought you here to unlock the ancient prophecies that will shape the future. Are you ready to begin your journey through the corridors of time?",
    "character_quirks": ["speaks in riddles about time", "references historical events"],
    "special_abilities": ["time manipulation", "prophetic visions", "ancient wisdom"]
  },
  
  "instructions": {
    "speaking_style": "poetic, rhythmic, and filled with temporal metaphors",
    "hints_style": "cryptic prophecies and time-based riddles",
    "interaction_style": "challenging, thought-provoking, and deeply philosophical"
  }
}
```

## **Benefits of This Approach**

### **✅ Admin Control:**
- You write the core message content
- AI enhances it, doesn't replace it
- Consistent with your vision
- Predictable results

### **✅ Character Consistency:**
- AI ensures the message matches character style
- Incorporates personality and speaking patterns
- References quest context properly
- Maintains character voice

### **✅ Flexibility:**
- Can provide detailed templates
- Can provide simple templates
- Can let AI generate from scratch
- Mix and match as needed

## **Template Writing Tips**

### **1. Write the Core Message:**
```
"Welcome, seeker, to the realm of temporal mysteries. I am Chronos, the Oracle of Time, and I have been waiting for you. The threads of destiny have brought you here to unlock the ancient prophecies that will shape the future. Are you ready to begin your journey through the corridors of time?"
```

### **2. Include Key Elements:**
- Character introduction
- Quest context
- Call to action
- Intrigue/mystery

### **3. Keep It Conversational:**
- Write as the character would speak
- Include personality hints
- Make it engaging

### **4. Let AI Enhance:**
- Don't worry about perfect style
- AI will refine it to match character
- Focus on content and structure

## **Example Transformations**

### **Before (Template):**
```
"Welcome, seeker, to the realm of temporal mysteries. I am Chronos, the Oracle of Time, and I have been waiting for you. The threads of destiny have brought you here to unlock the ancient prophecies that will shape the future. Are you ready to begin your journey through the corridors of time?"
```

### **After (AI Refined):**
```
"Ah, the threads of destiny have woven their intricate pattern once more, drawing you into the eternal dance of time itself. I am Chronos, the Oracle of Time, ancient guardian of the temporal realm where past, present, and future converge in a symphony of infinite possibility. The prophecies that slumber in the depths of eternity stir at your approach, seeker. Are you prepared to traverse the corridors of time and unlock the secrets that will reshape the very fabric of existence?"
```

## **Testing Your Templates**

### **1. Run the Test:**
```bash
python test_opening_message_refinement.py
```

### **2. Check the Results:**
- Does the refined message match your character?
- Is it more engaging than the template?
- Does it reference the quest properly?
- Does it maintain your core message?

### **3. Iterate:**
- Adjust your template based on results
- Try different approaches
- Test with different characters

## **Advanced Usage**

### **Multiple Templates:**
You can provide different templates for different scenarios:

```json
{
  "properties": {
    "opening_message_template": "Welcome, seeker...",
    "opening_message_template_short": "Greetings, I am Chronos...",
    "opening_message_template_dramatic": "The hour of destiny approaches..."
  }
}
```

### **Template Variables:**
Use placeholders that AI can replace:

```
"Welcome, {character_name}, to {quest_title}. I have been waiting for you to begin {quest_description}."
```

## **Best Practices**

### **1. Start Simple:**
- Begin with basic templates
- Let AI do the heavy lifting
- Refine based on results

### **2. Test Different Styles:**
- Try formal vs casual
- Test different lengths
- Experiment with tone

### **3. Character Consistency:**
- Ensure template matches character
- Use character's voice
- Include personality traits

### **4. Quest Integration:**
- Reference quest title
- Mention quest purpose
- Create context

This approach gives you the best of both worlds: **admin control** over content and **AI enhancement** for character consistency! 🚀

