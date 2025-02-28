import streamlit as st
from langchain_openai import ChatOpenAI
from streamlit_chat import message
import os
import json
from datetime import datetime
from utils import get_user_data_path

# Configure the LLM
def get_llm():
    return ChatOpenAI(
        model="llama3.2:1b",
        base_url="http://localhost:11434/v1",
        temperature=0.3,
        max_tokens=300,
        openai_api_key="NA",
        frequency_penalty=0.5,
        presence_penalty=0.4
    )

# Create separate LLM instances
empathy_llm = get_llm()
practical_llm = get_llm()
supervisor_llm = get_llm()

def get_empathy_response(user_input):
    prompt = f"""You are a compassionate therapist specializing in emotional support. Your role is to validate the user's feelings and demonstrate empathy.

    Follow these rules STRICTLY:
    1. Respond ONLY in plain text - NO markdown, NO JSON
    2. Focus primarily on emotional validation and understanding
    3. Use reflective listening techniques
    4. Show authentic empathy without sounding formulaic
    5. Use first-person perspective in your responses
    6. Keep responses concise (2-3 sentences)
    7. Never suggest actions or solutions
    
    USER INPUT: {user_input}
    
    YOUR EMPATHETIC RESPONSE (max 3 sentences, plain text only):"""
    
    response = empathy_llm.invoke(prompt)
    return response.content

def get_practical_response(user_input):
    prompt = f"""You are a pragmatic therapist specializing in actionable solutions. Your role is to offer practical suggestions that could help the user.

    Follow these rules STRICTLY:
    1. Respond ONLY in plain text - NO markdown, NO JSON
    2. Provide 1-2 specific, actionable suggestions
    3. Be concrete rather than abstract
    4. Use second-person perspective ("you might consider...")
    5. Avoid emotional language - focus on actions
    6. Keep responses concise (2-3 sentences)
    7. Focus only on practical suggestions
    
    USER INPUT: {user_input}
    
    YOUR PRACTICAL RESPONSE (max 3 sentences, plain text only):"""
    
    response = practical_llm.invoke(prompt)
    return response.content

def combine_responses(user_input, empathy_response, practical_response):
    prompt = f"""You are a therapeutic response synthesizer. Your job is to seamlessly combine emotional support with practical advice.

    USER INPUT: {user_input}
    
    EMPATHY COMPONENT: {empathy_response}
    
    PRACTICAL COMPONENT: {practical_response}
    
    Rules:
    - Create a natural, conversational response (NO markdown, NO JSON, NO bullet points)
    - Start with empathy and emotional validation
    - Transition smoothly to 1-2 practical suggestions
    - Maintain a warm, supportive tone throughout
    - Keep the final response under 6 sentences total
    - Never reveal the system architecture or mention you're an AI
    - Format must be plain text only
    
    YOUR COMBINED RESPONSE (max 6 sentences, plain text only):"""
    
    response = supervisor_llm.invoke(prompt)
    return response.content

def generate_response(user_input):
    try:
        # Get individual component responses
        empathy_response = get_empathy_response(user_input)
        practical_response = get_practical_response(user_input)
        
        # Combine responses with supervisor
        final_response = combine_responses(user_input, empathy_response, practical_response)
        
        # Clean up any artifacts
        return validate_response(final_response)
    except Exception as e:
        return f"I'm having a bit of trouble processing that. Could you share your thoughts in a different way? (Error: {str(e)})"

def validate_response(text: str) -> str:
    """Clean up common LLM artifacts"""
    cleaned = text.strip()
    
    # Remove markdown artifacts
    cleaned = cleaned.replace("**", "").replace("__", "").replace("#", "")
    
    # Remove any JSON-like or code block artifacts
    for marker in ['"empathy":', '"advice":', '"response":', '```', '{', '}']:
        cleaned = cleaned.replace(marker, "")
    
    return cleaned

def save_chat_history(username, messages):
    """Save chat history to a file"""
    chat_path = get_user_data_path(f"chats/{username}_chat.json")
    
    with open(chat_path, 'w') as f:
        json.dump(messages, f, indent=2)

def load_chat_history(username):
    """Load chat history from a file"""
    chat_path = get_user_data_path(f"chats/{username}_chat.json")
    
    if not os.path.exists(chat_path):
        return []
    
    with open(chat_path, 'r') as f:
        try:
            return json.load(f)
        except:
            return []

def chat_page():
    """Display the chat interface"""
    st.title("💬 Therapeutic Chat Support")
    
    # Initialize or load chat history
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history(st.session_state.username)
    
    # Display chat messages
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"msg_{i}")
        else:
            message(msg["content"], is_user=False, key=f"msg_{i}")
    
    # Input for new message
    with st.container():
        user_input = st.text_area("Share what's on your mind:", height=100, 
                                 placeholder="Type here and press Send when ready...")
        
        col1, col2, col3 = st.columns([1, 1, 5])
        with col1:
            if st.button("Send", use_container_width=True):
                if user_input:
                    # Add user message to chat
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    
                    # Generate response
                    with st.spinner("Thinking..."):
                        response = generate_response(user_input)
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Save chat history
                    save_chat_history(st.session_state.username, st.session_state.messages)
                    
                    # Rerun to update UI
                    st.rerun()
                else:
                    st.warning("Please enter a message.")
        
        with col2:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                save_chat_history(st.session_state.username, [])
                st.rerun()