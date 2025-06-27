import os
import streamlit as st
import requests
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import re
import random
from datetime import datetime

# Load environment variables
load_dotenv()

# Set API keys from environment variables
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Set page config
st.set_page_config(
    page_title="MindfulCompanion",
    page_icon="🧠",
    layout="wide"
)

# Define therapeutic approaches
THERAPY_APPROACHES = {
    "CBT": "Cognitive Behavioral Therapy - Focuses on changing unhelpful thinking patterns",
    "DBT": "Dialectical Behavior Therapy - Emphasizes mindfulness, distress tolerance, and emotional regulation",
    "ACT": "Acceptance and Commitment Therapy - Focuses on accepting thoughts while changing behaviors",
    "Mindfulness": "Focuses on being present and attentive to your thoughts and feelings without judgment",
    "Supportive": "Provides emotional support and encouragement without specific therapeutic techniques"
}

# Define coping strategies
COPING_STRATEGIES = {
    "stressed": [
        "Deep breathing exercises (4-7-8 technique)",
        "Progressive muscle relaxation",
        "Short mindfulness meditation",
        "Brief physical activity (stretch, walk)",
        "Grounding techniques using 5 senses"
    ],
    "anxious": [
        "Box breathing (4-4-4-4 pattern)",
        "Body scan meditation",
        "Reality testing thoughts",
        "Creating a worry schedule",
        "HALT check (Hungry, Angry, Lonely, Tired)"
    ],
    "sad": [
        "Behavioral activation (small positive activities)",
        "Gratitude practice (3 things)",
        "Pleasant memory visualization",
        "Light physical exercise",
        "Connecting with supportive people"
    ],
    "angry": [
        "Time-out technique",
        "Physical outlet (exercise, pillow punching)",
        "Thought challenging",
        "Distraction techniques",
        "STOP technique (Stop, Take a breath, Observe, Proceed)"
    ],
    "overwhelmed": [
        "Task chunking and prioritization",
        "Boundary setting practice",
        "Sensory grounding (focusing on one sense)",
        "Brief mindfulness break",
        "Self-compassion practice"
    ]
}

# Define agent classes
class TherapyContextAgent:
    """Agent to understand user's emotional state and therapy needs"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def analyze_message(self, user_message: str, conversation_history: List[Dict[str, Any]], 
                        user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the user message to understand emotional needs and determine appropriate response type"""
        
        # Format conversation history for context
        history_context = ""
        if conversation_history:
            history_context = "Conversation history:\n"
            for message in conversation_history[-5:]:  # Last 5 messages for context
                role = "User" if message["role"] == "user" else "Assistant"
                if isinstance(message["content"], str):
                    history_context += f"{role}: {message['content']}\n"
                else:
                    # If content is a dict (structured response), extract text
                    text_content = message["content"].get("text", "") if isinstance(message["content"], dict) else ""
                    history_context += f"{role}: {text_content}\n"
        
        # Include user profile information
        profile_context = ""
        if user_profile:
            profile_context = "User profile information:\n"
            profile_context += f"- Interests: {', '.join(user_profile.get('interests', []))}\n"
            profile_context += f"- Previous emotional states: {', '.join(list(user_profile.get('emotional_patterns', {}).keys()))}\n"
            profile_context += f"- Previous therapy approaches: {', '.join(user_profile.get('previous_approaches', []))}\n"
            profile_context += f"- Identified stressors: {', '.join(user_profile.get('identified_stressors', []))}\n"
        
        prompt = f"""
        You are a professional mental health support assistant analyzing a user message to determine the appropriate therapeutic response.
        
        {history_context}
        
        {profile_context}
        
        User's current message: "{user_message}"
        
        Analyze this message to determine:
        1. The user's emotional state
        2. The most appropriate therapeutic approach (CBT, DBT, ACT, Mindfulness, Supportive)
        3. Whether follow-up therapeutic questions are needed
        4. If coping strategies should be suggested
        5. If external content recommendations would be helpful
        
        Return a JSON with these fields:
        - emotional_state: string (e.g., "stressed", "anxious", "sad", "neutral", "happy")
        - emotional_intensity: integer (1-5, where 5 is most intense)
        - therapeutic_approach: string (one of: "CBT", "DBT", "ACT", "Mindfulness", "Supportive")
        - needs_followup: boolean (true if clarifying questions would help)
        - followup_question: string (specific therapeutic question to ask if needs_followup is true)
        - suggest_coping_strategies: boolean (true if specific coping strategies would be helpful)
        - recommend_content: boolean (true if suggesting external content would be helpful)
        - content_categories: list of strings (e.g., ["relaxation", "entertainment", "exercise", "learning"])
        - detected_interests: list of strings (interests mentioned or inferred from conversation)
        - potential_stressors: list of strings (stressors mentioned or inferred from conversation)
        - sensitivity_level: integer (1-5, where 5 indicates a highly sensitive topic requiring careful handling)
        
        Answer in valid JSON format only.
        """
        
        response = self.model.generate_content(prompt)
        try:
            # Extract JSON from response
            json_str = response.text
            # Handle potential JSON formatting issues
            json_str = re.sub(r'```json', '', json_str) 
            json_str = re.sub(r'```', '', json_str)
            json_str = json_str.strip()
            return json.loads(json_str)
        except Exception as e:
            st.error(f"Error parsing context analysis: {e}")
            # Return default response if parsing fails
            return {
                "emotional_state": "neutral",
                "emotional_intensity": 2,
                "therapeutic_approach": "Supportive",
                "needs_followup": False,
                "followup_question": "",
                "suggest_coping_strategies": False,
                "recommend_content": False,
                "content_categories": [],
                "detected_interests": [],
                "potential_stressors": [],
                "sensitivity_level": 2
            }

class TherapeuticQuestionAgent:
    """Agent to generate meaningful therapeutic follow-up questions"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_question(self, 
                         user_message: str, 
                         conversation_history: List[Dict[str, Any]],
                         context_analysis: Dict[str, Any],
                         therapeutic_approach: str) -> str:
        """Generate an appropriate therapeutic follow-up question"""
        
        # Format conversation history
        history_context = ""
        if conversation_history:
            history_context = "Recent conversation:\n"
            for message in conversation_history[-5:]:
                role = "User" if message["role"] == "user" else "Assistant"
                if isinstance(message["content"], str):
                    history_context += f"{role}: {message['content']}\n"
                else:
                    # If content is a dict (structured response), extract text
                    text_content = message["content"].get("text", "") if isinstance(message["content"], dict) else ""
                    history_context += f"{role}: {text_content}\n"
        
        # Therapeutic approach guidance
        approach_guidance = ""
        if therapeutic_approach == "CBT":
            approach_guidance = "Focus on identifying thought patterns and cognitive distortions. Ask questions that help recognize connections between thoughts, feelings, and behaviors."
        elif therapeutic_approach == "DBT":
            approach_guidance = "Focus on mindfulness, emotional regulation, and distress tolerance. Ask questions that promote acceptance and change."
        elif therapeutic_approach == "ACT":
            approach_guidance = "Focus on acceptance, defusion from thoughts, and values-based action. Ask questions that promote psychological flexibility."
        elif therapeutic_approach == "Mindfulness":
            approach_guidance = "Focus on present-moment awareness without judgment. Ask questions that encourage observation of thoughts and feelings."
        else:  # Supportive
            approach_guidance = "Focus on validation, empathy, and support. Ask questions that show understanding and build rapport."
        
        prompt = f"""
        You are a professional mental health therapist having a therapeutic conversation with a client.
        
        {history_context}
        
        Client's current message: "{user_message}"
        
        Context analysis:
        - Emotional state: {context_analysis["emotional_state"]}
        - Emotional intensity: {context_analysis.get("emotional_intensity", 3)}/5
        - Therapeutic approach: {therapeutic_approach}
        - Sensitivity level: {context_analysis.get("sensitivity_level", 3)}/5
        
        {approach_guidance}
        
        Generate a single, thoughtful therapeutic question that:
        1. Aligns with the {therapeutic_approach} approach
        2. Helps deepen the therapeutic process
        3. Is open-ended and encourages reflection
        4. Feels natural and conversational, not clinical
        5. Is appropriate given the emotional state and sensitivity level
        
        Return only the question text without explanations or additional context.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            st.error(f"Error generating therapeutic question: {e}")
            # Return a generic follow-up question if generation fails
            return "Could you tell me more about how you're experiencing those feelings right now?"

class CopingStrategyAgent:
    """Agent to suggest appropriate coping strategies based on emotional state"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.coping_strategies = COPING_STRATEGIES
    
    def get_strategies(self, 
                      emotional_state: str, 
                      therapeutic_approach: str,
                      user_profile: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get personalized coping strategies based on emotional state and therapeutic approach"""
        
        # Get base strategies for the emotional state
        base_strategies = self.coping_strategies.get(emotional_state, self.coping_strategies.get("stressed", []))
        
        # Get user's previously tried strategies
        previously_tried = user_profile.get("tried_strategies", [])
        
        prompt = f"""
        You are a professional mental health therapist suggesting personalized coping strategies.
        
        Client's current emotional state: {emotional_state}
        Therapeutic approach being used: {therapeutic_approach}
        
        Base coping strategies for this state:
        {', '.join(base_strategies)}
        
        Previously tried strategies:
        {', '.join(previously_tried) if previously_tried else "None recorded"}
        
        Create 3 personalized coping strategies that:
        1. Are appropriate for the {emotional_state} emotional state
        2. Align with the {therapeutic_approach} approach
        3. Are specific, actionable, and easy to implement
        4. Include one strategy focused on physical regulation
        5. Include one strategy focused on cognitive/mental approach
        6. Include one strategy focused on emotional processing
        
        For each strategy, provide:
        - A clear name/title (5 words or less)
        - A brief description (1-2 sentences)
        - A concrete implementation step (how to do it right now)
        
        Format as a list of JSON objects with "name", "description", and "implementation" keys.
        """
        
        try:
            response = self.model.generate_content(prompt)
            
            # Parse the response to get the strategies
            strategies_text = response.text
            # Extract JSON from the text (may be in a code block)
            strategies_text = re.sub(r'```json', '', strategies_text)
            strategies_text = re.sub(r'```', '', strategies_text)
            strategies_text = strategies_text.strip()
            
            strategies = json.loads(strategies_text)
            return strategies
        except Exception as e:
            st.error(f"Error generating coping strategies: {e}")
            # Return default strategies if parsing fails
            return [
                {
                    "name": "Deep Breathing",
                    "description": "Slow, deep breathing to activate the parasympathetic nervous system and reduce stress.",
                    "implementation": "Breathe in for 4 counts, hold for 2, exhale for 6. Repeat 5 times."
                },
                {
                    "name": "Grounding Exercise",
                    "description": "Connect with the present moment using your senses to reduce anxiety.",
                    "implementation": "Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste."
                },
                {
                    "name": "Positive Reframing",
                    "description": "Shift perspective on a challenging situation to find meaning or opportunity.",
                    "implementation": "Write down one challenging situation and three potential positives or lessons from it."
                }
            ]

class ContentRecommendationAgent:
    """Agent to recommend external content based on user needs"""
    
    def __init__(self):
        self.serper_api_key = SERPER_API_KEY
    
    def search_youtube(self, query: str, num_results: int = 2) -> List[Dict[str, Any]]:
        """Search for YouTube videos using Serper API"""
        url = "https://google.serper.dev/videos"
        
        payload = json.dumps({
            "q": query,
            "num": num_results
        })
        
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            results = response.json()
            
            video_results = []
            if "videos" in results:
                for video in results["videos"]:
                    # Extract YouTube ID from link
                    video_id = None
                    link = video.get("link", "")
                    if "youtube.com/watch?v=" in link:
                        video_id = link.split("youtube.com/watch?v=")[1].split("&")[0]
                    elif "youtu.be/" in link:
                        video_id = link.split("youtu.be/")[1].split("?")[0]
                        
                    video_results.append({
                        "title": video.get("title", ""),
                        "link": link,
                        "video_id": video_id,
                        "source": "YouTube",
                        "snippet": video.get("snippet", ""),
                        "thumbnail": video.get("thumbnail", ""),
                        "type": "video"
                    })
                    
            return video_results
            
        except Exception as e:
            st.error(f"Error in YouTube search: {e}")
            return []
    
    def search_web(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Search for web content using Serper API"""
        url = "https://google.serper.dev/search"
        
        payload = json.dumps({
            "q": query,
            "num": num_results
        })
        
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            results = response.json()
            
            web_results = []
            if "organic" in results:
                for result in results["organic"]:
                    web_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", ""),
                        "type": "web"
                    })
                    
            return web_results
            
        except Exception as e:
            st.error(f"Error in web search: {e}")
            return []
    
    def get_meditation_resources(self, duration: str = "short", style: str = "guided") -> List[Dict[str, Any]]:
        """Get meditation resources based on duration and style"""
        search_query = f"{duration} {style} meditation"
        return self.search_youtube(search_query, 2)
    
    def get_therapy_resources(self, approach: str, issue: str = None) -> List[Dict[str, Any]]:
        """Get therapy resources based on approach and issue"""
        search_query = f"{approach} therapy techniques"
        if issue:
            search_query += f" for {issue}"
        return self.search_youtube(search_query, 2)
    
    def get_mental_health_articles(self, topic: str) -> List[Dict[str, Any]]:
        """Get mental health articles from reputable sources"""
        search_query = f"{topic} mental health articles"
        return self.search_web(search_query, 3)
    
    def get_podcast_recommendations(self, topic: str) -> List[Dict[str, Any]]:
        """Get podcast recommendations based on topic"""
        search_query = f"best podcasts for {topic} mental health"
        return self.search_web(search_query, 3)
    
    def get_relaxation_music(self) -> List[Dict[str, Any]]:
        """Get relaxation music recommendations"""
        search_query = "relaxation music for anxiety stress relief"
        return self.search_youtube(search_query, 2)
    
    def get_recommendations(self, 
                          context_analysis: Dict[str, Any], 
                          user_interests: List[str], 
                          emotional_state: str,
                          therapeutic_approach: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get personalized recommendations based on therapeutic context"""
        
        recommendations = {}
        
        # Check if we have specific content categories from context analysis
        content_categories = context_analysis.get("content_categories", [])
        interests = user_interests + context_analysis.get("detected_interests", [])
        
        # Remove duplicates
        interests = list(set(interests))
        
        # Limit the number of recommendations based on emotional state
        # High emotional intensity = fewer recommendations
        emotional_intensity = context_analysis.get("emotional_intensity", 3)
        max_categories = 6 - emotional_intensity  # 1-5 scale: higher intensity = fewer recommendations
        
        # Always prioritize therapeutic content if sensitivity is high
        sensitivity = context_analysis.get("sensitivity_level", 3)
        if sensitivity >= 4:
            content_categories = ["therapy_resources", "meditation"] + content_categories
        
        # Add therapy resources if appropriate
        stressors = context_analysis.get("potential_stressors", [])
        if therapeutic_approach in ["CBT", "DBT", "ACT"] and stressors:
            recommendations["therapy_resources"] = self.get_therapy_resources(
                therapeutic_approach, 
                stressors[0] if stressors else None
            )
        
        # Add meditation resources for high emotional intensity
        if emotional_intensity >= 3 or "meditation" in content_categories:
            recommendations["meditation"] = self.get_meditation_resources()
        
        # Add mental health articles if appropriate
        if "learning" in content_categories or "education" in content_categories:
            topic = stressors[0] if stressors else emotional_state
            recommendations["mental_health_articles"] = self.get_mental_health_articles(topic)
        
        # Add relaxation music for stressed or anxious states
        if emotional_state in ["stressed", "anxious"] or "relaxation" in content_categories:
            recommendations["relaxation_music"] = self.get_relaxation_music()
        
        # Limit the maximum number of categories
        if len(recommendations) > max_categories:
            # Keep only the first max_categories items
            recommendations = dict(list(recommendations.items())[:max_categories])
        
        return recommendations

class TherapeuticResponseAgent:
    """Agent to craft therapeutic responses"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def craft_response(self, 
                      user_message: str,
                      conversation_history: List[Dict[str, Any]],
                      context_analysis: Dict[str, Any],
                      coping_strategies: List[Dict[str, str]] = None,
                      content_recommendations: Dict[str, List[Dict[str, Any]]] = None,
                      follow_up_question: str = None) -> Dict[str, Any]:
        """Craft a therapeutic response based on all available information"""
        
        # Format conversation history
        history_context = ""
        if conversation_history:
            recent_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
            history_context = "Recent conversation:\n"
            for message in recent_history:
                role = "User" if message["role"] == "user" else "Assistant"
                if isinstance(message["content"], str):
                    history_context += f"{role}: {message['content']}\n"
                else:
                    # If content is a dict (structured response), extract text
                    text_content = message["content"].get("text", "") if isinstance(message["content"], dict) else ""
                    history_context += f"{role}: {text_content}\n"
        
        # Format recommendations for context
        recommendations_context = ""
        if content_recommendations:
            recommendations_context = "Content recommendations available:\n"
            for category, items in content_recommendations.items():
                if items:
                    recommendations_context += f"- {category.replace('_', ' ').capitalize()}: {len(items)} items\n"
        
        # Format coping strategies for context
        strategies_context = ""
        if coping_strategies:
            strategies_context = "Coping strategies to suggest:\n"
            for strategy in coping_strategies:
                strategies_context += f"- {strategy['name']}: {strategy['description']}\n"
        
        # Therapeutic approach guidance
        approach = context_analysis.get("therapeutic_approach", "Supportive")
        approach_guidance = ""
        if approach == "CBT":
            approach_guidance = "Use cognitive behavioral principles, focusing on the connection between thoughts, feelings, and behaviors. Help identify cognitive distortions and consider alternative perspectives."
        elif approach == "DBT":
            approach_guidance = "Integrate dialectical behavior therapy principles, balancing acceptance and change. Incorporate mindfulness, emotional regulation, distress tolerance, and interpersonal effectiveness skills."
        elif approach == "ACT":
            approach_guidance = "Use acceptance and commitment therapy principles, focusing on psychological flexibility. Encourage acceptance of difficult thoughts/feelings while taking values-based action."
        elif approach == "Mindfulness":
            approach_guidance = "Emphasize present-moment awareness and non-judgmental observation of thoughts and feelings. Incorporate mindfulness principles throughout the response."
        else:  # Supportive
            approach_guidance = "Provide emotional support, validation, and encouragement. Focus on building rapport and creating a safe space for expression."
        
        # Construct the prompt for response generation
        prompt = f"""
        You are MindfulCompanion, a professional mental health therapist providing support to a client.
        
        {history_context}
        
        Client's current message: "{user_message}"
        
        Context analysis:
        - Emotional state: {context_analysis.get("emotional_state", "neutral")}
        - Emotional intensity: {context_analysis.get("emotional_intensity", 3)}/5
        - Sensitivity level: {context_analysis.get("sensitivity_level", 3)}/5
        - Therapeutic approach: {approach}
        
        {approach_guidance}
        
        {strategies_context}
        
        {recommendations_context}
        
        Follow-up question (if needed): "{follow_up_question if follow_up_question else 'None'}"
        
        Craft a therapeutic response that:
        1. Shows empathy and understanding of the client's current emotional state
        2. Applies the appropriate therapeutic approach ({approach})
        3. Validates the client's experience without reinforcing negative patterns
        4. Introduces coping strategies (if provided) in a natural way
        5. Mentions content recommendations (if available) only if contextually appropriate
        6. Ends with the follow-up question if one was provided
        
        Guidelines:
        - Keep your response concise (2-3 paragraphs)
        - Use warm, conversational language while maintaining professional boundaries
        - Don't label or diagnose the client
        - If suggesting coping strategies, present them as gentle invitations to try, not prescriptions
        - End with the follow-up question if one is provided
        
        Return only the response text without additional explanations or context.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            return {
                "text": response_text,
                "has_followup": bool(follow_up_question),
                "followup_question": follow_up_question if follow_up_question else None,
                "has_coping_strategies": bool(coping_strategies),
                "coping_strategies": coping_strategies if coping_strategies else [],
                "has_recommendations": bool(content_recommendations and any(content_recommendations.values())),
                "recommendations": content_recommendations if content_recommendations else {},
                "context_analysis": context_analysis
            }
        except Exception as e:
            st.error(f"Error generating therapeutic response: {e}")
            # Return a simple response if generation fails
            return {
                "text": "I'm here to support you through this. Would you like to tell me more about what you're experiencing?",
                "has_followup": False,
                "followup_question": None,
                "has_coping_strategies": False,
                "coping_strategies": [],
                "has_recommendations": False,
                "recommendations": {},
                "context_analysis": context_analysis
            }

class MoodTrackerAgent:
    """Agent to track and visualize mood over time"""
    
    def __init__(self):
        pass
    
    def record_mood(self, user_profile: Dict[str, Any], emotional_state: str, emotional_intensity: int) -> Dict[str, Any]:
        """Record the user's current mood in their profile"""
        
        # Initialize mood tracking if not present
        if "mood_tracker" not in user_profile:
            user_profile["mood_tracker"] = []
        
        # Add the current mood
        user_profile["mood_tracker"].append({
            "timestamp": datetime.now().isoformat(),
            "emotional_state": emotional_state,
            "intensity": emotional_intensity
        })
        
        # Keep only the last 30 entries to avoid profile bloat
        user_profile["mood_tracker"] = user_profile["mood_tracker"][-30:]
        
        return user_profile
    
    def get_mood_summary(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of recent mood trends"""
        
        if "mood_tracker" not in user_profile or not user_profile["mood_tracker"]:
            return {
                "has_data": False,
                "message": "Not enough mood data collected yet. Continue talking with MindfulCompanion to track your mood over time."
            }
        
        mood_data = user_profile["mood_tracker"]
        
        # Count occurrences of each emotional state
        emotions = {}
        for entry in mood_data:
            state = entry["emotional_state"]
            if state in emotions:
                emotions[state] += 1
            else:
                emotions[state] = 1
        
        # Calculate average intensity
        avg_intensity = sum(entry["intensity"] for entry in mood_data) / len(mood_data)
        
        # Find most common emotion
        most_common = max(emotions.items(), key=lambda x: x[1])
        
        return {
            "has_data": True,
            "emotions": emotions,
            "most_common_emotion": most_common[0],
            "average_intensity": round(avg_intensity, 1),
            "num_entries": len(mood_data),
            "mood_data": mood_data
        }

class JournalAgent:
    """Agent to manage therapeutic journaling"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_prompt(self, context_analysis: Dict[str, Any]) -> str:
        """Generate an appropriate journaling prompt based on context"""
        
        emotional_state = context_analysis.get("emotional_state", "neutral")
        therapeutic_approach = context_analysis.get("therapeutic_approach", "Supportive")
        stressors = context_analysis.get("potential_stressors", [])
        
        prompt = f"""
        You are creating a therapeutic journaling prompt for someone experiencing {emotional_state}.
        The therapeutic approach being used is {therapeutic_approach}.
        
        Potential stressors identified: {', '.join(stressors) if stressors else 'None specifically identified'}
        
        Create a single, thoughtful journaling prompt that:
        1. Is appropriate for the {emotional_state} emotional state
        2. Aligns with {therapeutic_approach} therapeutic principles
        3. Encourages reflection and self-awareness
        4. Is specific enough to provide direction, but open enough for personal exploration
        5. Is supportive and non-judgmental
        
        Return only the journaling prompt without additional explanations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            st.error(f"Error generating journaling prompt: {e}")
            # Return a default prompt if generation fails
            return "Reflect on a moment today when you felt at peace. What contributed to that feeling, and how might you create more such moments?"
    
    def save_journal_entry(self, user_profile: Dict[str, Any], entry: str) -> Dict[str, Any]:
        """Save a journal entry to the user profile"""
        
        # Initialize journal if not present
        if "journal_entries" not in user_profile:
            user_profile["journal_entries"] = []
        
        # Add the current entry
        user_profile["journal_entries"].append({
            "timestamp": datetime.now().isoformat(),
            "entry": entry
        })
        
        return user_profile

class UserProfileManager:
    """Manages persistent user profile information"""
import os
import streamlit as st
import requests
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Set API keys from environment variables
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Set page config
st.set_page_config(
    page_title="Smart Search Assistant",
    page_icon="🔍",
    layout="wide"
)

# Define agent classes
class ContextCheckAgent:
    """Agent to determine if external search is needed based on user query"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def check_search_needed(self, user_query: str) -> Dict[str, Any]:
        """Determine if the query requires external search and what type"""
        prompt = f"""
        Analyze this user query: "{user_query}"
        
        Determine if it requires external information from:
        1. News articles/blogs (current events, factual information)
        2. YouTube videos (tutorials, explanations, demonstrations)
        3. No external information needed (opinion, conversation, coding help that doesn't require latest updates)
        
        Return a JSON with these fields:
        - needs_search: boolean (true if any external search is needed)
        - needs_news: boolean (true if news/articles/blogs would be helpful)
        - needs_videos: boolean (true if YouTube videos would be helpful)
        - search_query: string (optimized search query based on user input)
        - reason: string (brief explanation of your decision)
        
        Answer in valid JSON format only.
        """
        
        response = self.model.generate_content(prompt)
        try:
            # Extract JSON from response
            json_str = response.text
            # Handle potential JSON formatting issues
            json_str = re.sub(r'```json', '', json_str) 
            json_str = re.sub(r'```', '', json_str)
            json_str = json_str.strip()
            return json.loads(json_str)
        except Exception as e:
            st.error(f"Error parsing context check response: {e}")
            # Return default response if parsing fails
            return {
                "needs_search": False,
                "needs_news": False,
                "needs_videos": False,
                "search_query": user_query,
                "reason": "Failed to analyze query"
            }

class SerperSearchAgent:
    """Agent to search for news articles and web content"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search for web results using Serper API"""
        url = "https://google.serper.dev/search"
        
        payload = json.dumps({
            "q": query,
            "num": num_results
        })
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            results = response.json()
            
            # Extract organic search results
            organic_results = []
            if "organic" in results:
                for result in results["organic"]:
                    organic_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", "")
                    })
                    
            # Extract news results if available
            news_results = []
            if "news" in results:
                for result in results["news"]:
                    news_results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": result.get("source", ""),
                        "date": result.get("date", "")
                    })
            
            # Combine and return results, prioritizing news if available
            combined_results = news_results + organic_results
            return combined_results[:num_results]
            
        except Exception as e:
            st.error(f"Error in Serper search: {e}")
            return []

class YouTubeSearchAgent:
    """Agent to search for YouTube videos"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def search(self, query: str, num_results: int = 3) -> List[Dict[str, Any]]:
        """Search for YouTube videos using Serper API"""
        url = "https://google.serper.dev/videos"
        
        payload = json.dumps({
            "q": query,
            "num": num_results
        })
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            results = response.json()
            
            video_results = []
            if "videos" in results:
                for video in results["videos"]:
                    # Extract YouTube ID from link
                    video_id = None
                    link = video.get("link", "")
                    if "youtube.com/watch?v=" in link:
                        video_id = link.split("youtube.com/watch?v=")[1].split("&")[0]
                    elif "youtu.be/" in link:
                        video_id = link.split("youtu.be/")[1].split("?")[0]
                        
                    video_results.append({
                        "title": video.get("title", ""),
                        "link": link,
                        "video_id": video_id,
                        "source": video.get("source", "YouTube"),
                        "snippet": video.get("snippet", ""),
                        "thumbnail": video.get("thumbnail", "")
                    })
                    
            return video_results
            
        except Exception as e:
            st.error(f"Error in YouTube search: {e}")
            return []

class ResponseGenerationAgent:
    """Agent to compile and format final responses"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_response(self, 
                         user_query: str, 
                         web_results: List[Dict[str, Any]], 
                         video_results: List[Dict[str, Any]],
                         context_analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive response based on search results"""
        
        # Construct context from web results
        web_context = ""
        if web_results:
            web_context = "Web search results:\n"
            for i, result in enumerate(web_results, 1):
                web_context += f"{i}. {result['title']}\n"
                web_context += f"   Source: {result['source']}\n"
                web_context += f"   Summary: {result['snippet']}\n\n"
        
        # Construct context from video results
        video_context = ""
        if video_results:
            video_context = "Video search results:\n"
            for i, result in enumerate(video_results, 1):
                video_context += f"{i}. {result['title']}\n"
                video_context += f"   Source: {result['source']}\n"
                video_context += f"   Summary: {result['snippet']}\n\n"
        
        # Build the prompt for Gemini
        prompt = f"""
        User query: "{user_query}"
        
        {web_context}
        
        {video_context}
        
        Based on the search results above, provide a comprehensive response to the user's query.
        Include relevant information from the sources and cite them properly.
        
        If the search results don't contain enough information to answer the query fully,
        acknowledge the limitations and provide the best response possible based on available information.
        
        Format your response in markdown, with clear sections and proper attribution to sources.
        """
        
        # Generate response
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating your response. Please try again with a more specific query."

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize agents
@st.cache_resource
def load_agents():
    context_agent = ContextCheckAgent()
    serper_agent = SerperSearchAgent(SERPER_API_KEY)
    youtube_agent = YouTubeSearchAgent(SERPER_API_KEY)
    response_agent = ResponseGenerationAgent()
    return context_agent, serper_agent, youtube_agent, response_agent

context_agent, serper_agent, youtube_agent, response_agent = load_agents()

# UI elements
st.title("🔍 Smart Search Assistant")
st.markdown("Ask me anything! I'll search the web and YouTube for the most relevant information.")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "videos" in message:
            st.markdown(message["content"])
            
            # Display videos in a horizontal layout if available
            if message["videos"]:
                cols = st.columns(min(3, len(message["videos"])))
                for i, video in enumerate(message["videos"]):
                    with cols[i % 3]:
                        if video["video_id"]:
                            st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                        st.markdown(f"**{video['title']}**")
                        st.markdown(f"[Watch on YouTube]({video['link']})")
        else:
            st.markdown(message["content"])

# Get user input
user_query = st.chat_input("What would you like to know?")

if user_query:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Create a placeholder for the assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # 1. Context check
            context_analysis = context_agent.check_search_needed(user_query)
            
            web_results = []
            video_results = []
            
            # 2. Perform searches if needed
            if context_analysis["needs_search"]:
                search_query = context_analysis["search_query"]
                
                # Search for web content if needed
                if context_analysis["needs_news"]:
                    with st.spinner("Searching articles and news..."):
                        web_results = serper_agent.search(search_query)
                
                # Search for videos if needed
                if context_analysis["needs_videos"]:
                    with st.spinner("Searching videos..."):
                        video_results = youtube_agent.search(search_query)
            
            # 3. Generate final response
            with st.spinner("Generating response..."):
                response_text = response_agent.generate_response(
                    user_query, 
                    web_results, 
                    video_results,
                    context_analysis
                )
                
                # Display the response
                st.markdown(response_text)
                
                # Display videos in a horizontal layout if available
                if video_results:
                    st.markdown("### Related Videos")
                    cols = st.columns(min(3, len(video_results)))
                    for i, video in enumerate(video_results):
                        with cols[i % 3]:
                            if video["video_id"]:
                                st.video(f"https://www.youtube.com/watch?v={video['video_id']}")
                            st.markdown(f"**{video['title']}**")
                            st.markdown(f"[Watch on YouTube]({video['link']})")
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": response_text,
                "videos": video_results if video_results else []
            })
