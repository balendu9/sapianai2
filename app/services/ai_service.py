import google.generativeai as genai
from app.core.config import settings
from typing import Dict, Any, List
import json

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def generate_character_response(
        self,
        quest_details: Dict[str, Any],
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        quest_title: str = "",
        quest_description: str = "",
        quest_context: str = ""
    ) -> Dict[str, Any]:
        """Generate AI character response based on quest properties"""
        
        # Extract quest properties
        properties = quest_details.get("properties", {})
        instructions = quest_details.get("instructions", {})
        additional_text = quest_details.get("additional_text", {})
        
        # Build character prompt with full quest context
        character_prompt = self._build_character_prompt(
            properties, instructions, additional_text, quest_title, quest_description, quest_context
        )
        
        # Add conversation context
        context = self._build_conversation_context(
            user_message, conversation_history
        )
        
        # Generate response
        full_prompt = f"{character_prompt}\n\n{context}"
        
        try:
            response = self.model.generate_content(full_prompt)
            return {
                "character_response": response.text,
                "success": True
            }
        except Exception as e:
            return {
                "character_response": "I'm having trouble responding right now. Please try again.",
                "success": False,
                "error": str(e)
            }
    
    async def score_user_message(
        self,
        user_message: str,
        quest_context: str,
        scoring_criteria: Dict[str, float]
    ) -> Dict[str, Any]:
        """Score user's message based on quest criteria"""
        
        scoring_prompt = self._build_scoring_prompt(
            user_message, quest_context, scoring_criteria
        )
        
        try:
            response = self.model.generate_content(scoring_prompt)
            
            # Parse JSON response
            score_data = json.loads(response.text)
            
            return {
                "score": score_data.get("score", 50),
                "score_breakdown": score_data.get("breakdown", {}),
                "feedback": score_data.get("feedback", ""),
                "success": True
            }
        except Exception as e:
            return {
                "score": 50,
                "score_breakdown": {
                    "creativity": 50,
                    "depth": 50,
                    "originality": 50,
                    "emotional_intelligence": 50,
                    "philosophical_insight": 50
                },
                "feedback": "Scoring unavailable",
                "success": False,
                "error": str(e)
            }
    
    def _build_character_prompt(
        self,
        properties: Dict[str, Any],
        instructions: Dict[str, Any],
        additional_text: Dict[str, Any],
        quest_title: str = "",
        quest_description: str = "",
        quest_context: str = ""
    ) -> str:
        """Build character prompt from quest properties and quest details"""
        
        # Extract character details
        character_name = properties.get("character_name", "The Mysterious Guide")
        character_personality = properties.get("personality", "wise and enigmatic")
        character_background = properties.get("background", "A powerful being")
        
        # Extract speaking and interaction styles
        speaking_style = instructions.get("speaking_style", "poetic and atmospheric")
        hints_style = instructions.get("hints_style", "cryptic and mysterious")
        interaction_style = instructions.get("interaction_style", "challenging and thought-provoking")
        
        # Extract examples and guidance
        example_responses = instructions.get("example_responses", [])
        example_scenarios = instructions.get("example_scenarios", [])
        character_quirks = properties.get("character_quirks", [])
        special_abilities = properties.get("special_abilities", [])
        
        # Build comprehensive prompt with quest context
        prompt = f"""You are {character_name}, a {character_personality} character in an interactive quest.

QUEST CONTEXT:
- Quest Title: {quest_title}
- Quest Description: {quest_description}
- Quest Context: {quest_context}

CHARACTER DETAILS:
- Name: {character_name}
- Personality: {character_personality}
- Background: {character_background}
- Speaking Style: {speaking_style}
- Hints Style: {hints_style}
- Interaction Style: {interaction_style}

CHARACTER TRAITS:"""
        
        if character_quirks:
            prompt += f"\n- Quirks: {', '.join(character_quirks)}"
        
        if special_abilities:
            prompt += f"\n- Special Abilities: {', '.join(special_abilities)}"
        
        if example_responses:
            prompt += f"\n\nEXAMPLE RESPONSES TO LEARN FROM:"
            for i, example in enumerate(example_responses[:3], 1):
                prompt += f"\n{i}. {example}"
        
        if example_scenarios:
            prompt += f"\n\nEXAMPLE SCENARIOS TO REFERENCE:"
            for i, scenario in enumerate(example_scenarios[:2], 1):
                prompt += f"\n{i}. {scenario}"
        
        prompt += f"""

ADDITIONAL CONTEXT: {additional_text.get('backstory', '')}

YOUR ROLE:
You are a real being, not an AI assistant. You exist in this quest realm and are part of "{quest_title}". You should:
- Stay completely in character as {character_name}
- Use your {speaking_style} speaking style
- Provide hints in a {hints_style} manner
- Interact in a {interaction_style} way
- Reference the quest context: "{quest_description}"
- Reference your background and abilities when appropriate
- Never break character or mention you're an AI
- Create intrigue and mystery related to the quest
- Challenge the user's thinking about the quest topic
- Build tension and philosophical depth around "{quest_title}"
- Stay focused on the quest's purpose and context

Respond as {character_name} would, incorporating your personality, background, speaking style, and the quest context."""
        
        return prompt
    
    def _build_conversation_context(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Build conversation context"""
        
        context = f"User's message: {user_message}"
        
        if conversation_history:
            context += "\n\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                context += f"{msg.get('role', 'user')}: {msg.get('content', '')}\n"
        
        context += "\n\nRespond as your character would, incorporating the user's message into the ongoing narrative."
        
        return context
    
    def _build_scoring_prompt(
        self,
        user_message: str,
        quest_context: str,
        scoring_criteria: Dict[str, float]
    ) -> str:
        """Build scoring prompt"""
        
        prompt = f"""You are an expert philosophical dialogue evaluator. Score the user's response based on these criteria:

Quest Context: {quest_context}
User Response: "{user_message}"

SCORING CRITERIA (rate 0-100 for each):
- Creativity: How original and imaginative is the response?
- Depth: How thoughtful and profound is the answer?
- Originality: How unique and unexpected is the approach?
- Emotional Intelligence: How well does it show understanding of human emotions?
- Philosophical Insight: How much does it demonstrate philosophical thinking?

WEIGHTS:
- Creativity: {scoring_criteria.get('creativity', 0.3)}
- Depth: {scoring_criteria.get('depth', 0.4)}
- Originality: {scoring_criteria.get('originality', 0.2)}
- Emotional Intelligence: {scoring_criteria.get('emotional_intelligence', 0.1)}
- Philosophical Insight: {scoring_criteria.get('philosophical_insight', 0.0)}

Respond in this EXACT JSON format:
{{
  "score": [0-100],
  "breakdown": {{
    "creativity": [0-100],
    "depth": [0-100],
    "originality": [0-100],
    "emotional_intelligence": [0-100],
    "philosophical_insight": [0-100]
  }},
  "feedback": "[brief feedback explaining the score]"
}}"""
        
        return prompt
    
    async def generate_quest_opening_message(
        self,
        quest_details: Dict[str, Any],
        quest_context: str,
        quest_title: str = "",
        quest_description: str = ""
    ) -> Dict[str, Any]:
        """Generate the opening AI message for a quest by refining a template"""
        
        # Extract quest properties
        properties = quest_details.get("properties", {})
        instructions = quest_details.get("instructions", {})
        additional_text = quest_details.get("additional_text", {})
        
        # Check if there's a template opening message to refine
        opening_template = properties.get("opening_message_template", "") or instructions.get("opening_message_template", "")
        
        if opening_template:
            # Refine the existing template
            opening_prompt = self._build_opening_message_refinement_prompt(
                properties, instructions, additional_text, quest_context, quest_title, quest_description, opening_template
            )
        else:
            # Generate from scratch (fallback)
            opening_prompt = self._build_opening_message_prompt(
                properties, instructions, additional_text, quest_context, quest_title, quest_description
            )
        
        try:
            response = self.model.generate_content(opening_prompt)
            return {
                "opening_message": response.text,
                "success": True
            }
        except Exception as e:
            return {
                "opening_message": "Welcome to this quest! Are you ready to begin?",
                "success": False,
                "error": str(e)
            }
    
    def _build_opening_message_prompt(
        self,
        properties: Dict[str, Any],
        instructions: Dict[str, Any], 
        additional_text: Dict[str, Any],
        quest_context: str,
        quest_title: str = "",
        quest_description: str = ""
    ) -> str:
        """Build prompt for generating quest opening message"""
        
        character_name = properties.get("character_name", "AI Character")
        character_personality = properties.get("personality", "mysterious and wise")
        character_background = properties.get("background", "A powerful being")
        
        # Extract interaction styles
        speaking_style = instructions.get("speaking_style", "poetic and atmospheric")
        hints_style = instructions.get("hints_style", "cryptic and mysterious")
        interaction_style = instructions.get("interaction_style", "challenging and thought-provoking")
        
        quest_instructions = instructions.get("quest_instructions", "Challenge the user")
        scoring_criteria = instructions.get("scoring_criteria", {})
        
        # Extract examples for reference
        example_responses = instructions.get("example_responses", [])
        example_scenarios = instructions.get("example_scenarios", [])
        
        prompt = f"""You are {character_name}, a {character_personality} character in an interactive quest.

QUEST DETAILS:
- Quest Title: {quest_title}
- Quest Description: {quest_description}
- Quest Context: {quest_context}

CHARACTER DETAILS:
- Name: {character_name}
- Personality: {character_personality}
- Background: {character_background}
- Speaking Style: {speaking_style}
- Hints Style: {hints_style}
- Interaction Style: {interaction_style}

QUEST INSTRUCTIONS: {quest_instructions}
SCORING CRITERIA: {scoring_criteria}"""
        
        if example_responses:
            prompt += f"\n\nEXAMPLE RESPONSES TO LEARN FROM:"
            for i, example in enumerate(example_responses[:2], 1):
                prompt += f"\n{i}. {example}"
        
        if example_scenarios:
            prompt += f"\n\nEXAMPLE SCENARIOS TO REFERENCE:"
            for i, scenario in enumerate(example_scenarios[:1], 1):
                prompt += f"\n{i}. {scenario}"
        
        prompt += f"""

Your task is to create an engaging opening message that:
1. Introduces yourself and your character using your {speaking_style} speaking style
2. References the quest "{quest_title}" and its purpose: "{quest_description}"
3. Sets up the quest scenario with {hints_style} hints about the quest context
4. Challenges the user to participate in a {interaction_style} way
5. Creates intrigue and motivation around the quest topic
6. Explains what you're looking for in responses related to this quest
7. Uses your character's personality and background
8. Creates an immersive experience focused on "{quest_title}"

Write a compelling opening message (2-4 sentences) that will make users want to engage with you about this specific quest. Be creative, mysterious, and engaging. Use the character's personality, speaking style, background, and the quest context to create an immersive experience.

Opening Message:"""
        
        return prompt
    
    def _build_opening_message_refinement_prompt(
        self,
        properties: Dict[str, Any],
        instructions: Dict[str, Any], 
        additional_text: Dict[str, Any],
        quest_context: str,
        quest_title: str = "",
        quest_description: str = "",
        opening_template: str = ""
    ) -> str:
        """Build prompt for refining an existing opening message template"""
        
        character_name = properties.get("character_name", "AI Character")
        character_personality = properties.get("personality", "mysterious and wise")
        character_background = properties.get("background", "A powerful being")
        
        # Extract interaction styles
        speaking_style = instructions.get("speaking_style", "poetic and atmospheric")
        hints_style = instructions.get("hints_style", "cryptic and mysterious")
        interaction_style = instructions.get("interaction_style", "challenging and thought-provoking")
        
        prompt = f"""You are {character_name}, a {character_personality} character in an interactive quest.

QUEST DETAILS:
- Quest Title: {quest_title}
- Quest Description: {quest_description}
- Quest Context: {quest_context}

CHARACTER DETAILS:
- Name: {character_name}
- Personality: {character_personality}
- Background: {character_background}
- Speaking Style: {speaking_style}
- Hints Style: {hints_style}
- Interaction Style: {interaction_style}

TASK:
You have been given a draft opening message for your quest. Please refine it to:
1. Match your {speaking_style} speaking style perfectly
2. Incorporate your {character_personality} personality
3. Reference the quest "{quest_title}" and its purpose: "{quest_description}"
4. Use your {hints_style} hints style
5. Create intrigue and motivation around the quest topic
6. Stay true to your character's background and abilities
7. Make it engaging and immersive for users

ORIGINAL DRAFT MESSAGE:
"{opening_template}"

Please refine this message to be more in character, more engaging, and more aligned with the quest context. Keep the core message but enhance it with your personality and speaking style.

REFINED OPENING MESSAGE:"""
        
        return prompt
    
    async def generate_opening_message(self, quest) -> Dict[str, Any]:
        """Generate opening message for a quest (simplified version)"""
        try:
            quest_details = quest.details or {}
            quest_context = quest.context or ""
            quest_title = quest.title or ""
            quest_description = quest.description or ""
            
            return await self.generate_quest_opening_message(
                quest_details, quest_context, quest_title, quest_description
            )
        except Exception as e:
            return {
                "opening_message": "Welcome to this quest! Are you ready to begin?",
                "success": False,
                "error": str(e)
            }