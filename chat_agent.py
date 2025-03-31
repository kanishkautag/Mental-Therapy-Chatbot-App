import streamlit as st
from langchain_openai import ChatOpenAI
from streamlit_chat import message
import os
import json
from datetime import datetime
from utils import get_user_data_path
import traceback # Import for detailed error logging

# Configure the LLM
def get_llm():
    # Keep settings, maybe reduce max_tokens if issue persists after prompt changes
    return ChatOpenAI(
        model="llama3.2:1b",
        base_url="http://localhost:11434/v1",
        temperature=0.2, # Slightly lower temperature to encourage focus
        max_tokens=150,  # Reduced max_tokens further as a precaution
        openai_api_key="NA",
        frequency_penalty=0.5,
        presence_penalty=0.4
    )

# Create separate LLM instances
empathy_llm = get_llm()
practical_llm = get_llm()
supervisor_llm = get_llm()

# --- Revised Prompts ---

def get_empathy_response(user_input):
    prompt = f"""Your PRIMARY TASK: Respond briefly and appropriately to the user.

    RULES (Follow STRICTLY):
    1. PLAIN TEXT ONLY. No markdown, JSON, lists.
    2. **DEFAULT RESPONSE:** If the input is a greeting ("hi", "hello", "whats up"), neutral, or unclear, reply with ONE simple, open question inviting more detail. Example: "Hi there, what's on your mind?" or "Hello, how can I help today?"
    3. **EXCEPTION:** If the user *clearly* expresses significant distress or negative emotion (e.g., "I feel awful", "I'm so stressed"), THEN validate this feeling briefly (1 sentence). Example: "It sounds like things are really difficult right now."
    4. **CRITICAL: DO NOT ASSUME distress from simple greetings.** Stick to the default response unless distress is obvious and explicitly stated by the user.
    5. MAX 1-2 short sentences.
    6. NO advice, NO solutions, NO interpretations, NO AI feelings.
    7. Professional, calm tone.

    USER INPUT: {user_input}

    YOUR RESPONSE (Plain text, Max 2 sentences):"""
    response = empathy_llm.invoke(prompt)
    return response.content.strip()

def get_practical_response(user_input):
    prompt = f"""Your ONLY TASK: Provide ONE actionable suggestion IF the user clearly asks for help or describes a solvable problem. Otherwise, output 'NO_ACTION_NEEDED'.

    RULES (Follow STRICTLY):
    1. PLAIN TEXT ONLY. No markdown, JSON, lists.
    2. **Analyze input:** Does it contain a clear problem needing a practical step OR a direct request for advice? Check carefully.
    3. **If YES:** Output ONE brief, concrete suggestion (1 sentence). Start with "You might consider...". Example: "You might consider writing down your main concerns."
    4. **If NO (e.g., input is "hi", "whats up", "hello", just venting, vague): Output the literal text `NO_ACTION_NEEDED` and NOTHING ELSE.** Do not add any other words or explanation. This is the required output for non-problem inputs.
    5. NO emotional validation, NO questions. MAX 1 sentence if giving advice.

    USER INPUT: {user_input}

    YOUR RESPONSE (Plain text: 1 suggestion OR 'NO_ACTION_NEEDED'):"""
    response = practical_llm.invoke(prompt)
    # Explicitly check if the output is exactly the marker, otherwise return marker
    # This helps if the LLM adds extra spaces or minor deviations
    if "NO_ACTION_NEEDED" in response.content.strip():
         return "NO_ACTION_NEEDED"
    # If it contains actual advice (and isn't the marker), return it
    elif len(response.content.strip()) > 0 and response.content.strip() != "NO_ACTION_NEEDED":
         return response.content.strip()
    # Default back to marker if output is empty or unexpected
    else:
         return "NO_ACTION_NEEDED"


def combine_responses(user_input, empathy_response, practical_response):
    # Decide upfront based on the practical response marker
    if practical_response == "NO_ACTION_NEEDED":
        # If no action needed, the final response is just the empathy part.
        # We don't even need to call the supervisor LLM in this case.
        print("[DEBUG] Combine_Responses: Practical is NO_ACTION_NEEDED. Returning empathy only.")
        return empathy_response
    else:
        # Only call the supervisor if there is practical advice to combine
        print("[DEBUG] Combine_Responses: Practical advice found. Calling Supervisor LLM.")
        prompt = f"""Your TASK: Combine the Empathy and Practical components into a single, short, natural response.

        EMPATHY COMPONENT: {empathy_response}
        PRACTICAL COMPONENT: {practical_response}

        RULES (Follow STRICTLY):
        1. Start with the `EMPATHY COMPONENT`.
        2. Add ONE natural transition phrase (like "Perhaps," or "Maybe also," or "If you're feeling up to it,").
        3. Append the suggestion from the `PRACTICAL COMPONENT`.
        4. Make it sound like a single, coherent thought. DO NOT just list the components.
        5. **Tone:** Calm, supportive, professional. Not overly familiar or emotional.
        6. **Length:** ABSOLUTE MAXIMUM 3 sentences total. Check your final output length.
        7. **Format:** PLAIN TEXT ONLY. No markdown, JSON, lists, etc.
        8. **Content:** NO mentioning components, AI, system structure. NO AI feelings. Only use the provided text.

        USER INPUT CONTEXT (for reference only): {user_input}

        YOUR COMBINED RESPONSE (Plain text, Max 3 sentences):"""
        response = supervisor_llm.invoke(prompt)
        cleaned_response = response.content.strip()
        return cleaned_response

# --- generate_response with DEBUGGING ---
def generate_response(user_input):
    try:
        print(f"\n--- Generating response for: '{user_input}' ---") # DEBUG START

        empathy_response = get_empathy_response(user_input)
        # Add extra check for empty response
        if not empathy_response:
            print("[DEBUG] Empathy Response was EMPTY. Using fallback.")
            empathy_response = "I'm processing that. How are you feeling about it?" # Basic fallback
        print(f"[DEBUG] Empathy Response Raw: '{empathy_response}'") # DEBUG EMPATHY

        practical_response = get_practical_response(user_input)
        print(f"[DEBUG] Practical Response Raw: '{practical_response}'") # DEBUG PRACTICAL

        # Simplified logic: Combine function now handles the NO_ACTION_NEEDED case internally
        final_combined_response = combine_responses(user_input, empathy_response, practical_response)
        print(f"[DEBUG] Combined Response Raw: '{final_combined_response}'") # DEBUG SUPERVISOR/COMBINED

        validated_response = validate_response(final_combined_response)
        print(f"[DEBUG] Final Validated Response: '{validated_response}'") # DEBUG FINAL
        print("--- End Response Generation ---") # DEBUG END

        # Final check for empty response after validation
        if not validated_response:
            print("[DEBUG] Validated response is empty. Returning generic fallback.")
            return "I'm not sure how to respond to that. Could you tell me more?"

        return validated_response

    except Exception as e:
        print(f"ERROR during response generation: {e}")
        traceback.print_exc() # Print detailed stack trace to console
        return f"I seem to be having a little trouble formulating a response right now. Perhaps try phrasing that differently? (Error: {str(e)})"


# --- validate_response Function (Removed Duplicate) ---
def validate_response(text: str) -> str:
    """Clean up common LLM artifacts - keep this robust"""
    if not isinstance(text, str): # Handle non-string input
        print(f"[DEBUG] validate_response received non-string input: {type(text)}")
        return "I encountered an unexpected issue processing the response."
        
    cleaned = text.strip()

    # Remove the marker if it somehow survived (shouldn't due to new logic)
    cleaned = cleaned.replace("NO_ACTION_NEEDED", "")

    # Remove common conversational filler sometimes added by models
    common_fillers = [
        "Okay, here is the combined response:", "Here is the combined response:", "Combined response:",
        "Here's the empathetic response:", "Empathetic response:", "Okay, here is the empathetic response:",
        "Here's the practical response:", "Practical response:", "Okay, here is the practical response:",
        "Okay, here is that response:", "Okay, here's that:", "Here you go:", "Okay.", "Sure.", "Certainly.",
        "Combined Response:", "Response:", "Empathetic:", "Practical:" # More potential prefixes
    ]
    # Make check case-insensitive and loop through potential prefixes
    lower_cleaned = cleaned.lower()
    for filler in common_fillers:
        if lower_cleaned.startswith(filler.lower()):
            cleaned = cleaned[len(filler):].lstrip(' :') # Remove filler and potential following colon/space
            lower_cleaned = cleaned.lower() # Update lower_cleaned for next iteration

    # Remove markdown artifacts more aggressively
    cleaned = cleaned.replace("**", "").replace("__", "").replace("*", "").replace("#", "")

    # Remove any JSON-like or code block artifacts
    for marker in ['```json', '```', '{', '}', '[', ']']:
         cleaned = cleaned.replace(marker, "")
         
    # Avoid removing all quotes, but remove if they enclose the whole string
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
    if cleaned.startswith("'") and cleaned.endswith("'"):
        cleaned = cleaned[1:-1]

    # Remove extra internal whitespace
    cleaned = ' '.join(cleaned.split())

    # Avoid returning an empty string if everything got stripped
    if not cleaned.strip(): # Check if string is empty or just whitespace
        print("[DEBUG] validate_response resulted in empty string.")
        return "I'm processing your message." # Fallback for empty result

    return cleaned.strip() # Ensure no trailing/leading whitespace slips through


# --- Utility Function Placeholder (Ensure it exists in utils.py or here) ---
def get_user_data_path(relative_path=""):
    """Gets the absolute path to a user data file/directory."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    except NameError: # Handle case where __file__ is not defined (e.g., interactive session)
        script_dir = os.getcwd()
    data_dir = os.path.join(script_dir, "user_data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, relative_path)

# --- Chat History Functions (Keep as they are) ---
def save_chat_history(username, messages):
    """Save chat history to a file"""
    data_dir = get_user_data_path("chats") # Ensure base directory exists
    os.makedirs(data_dir, exist_ok=True)
    # Sanitize username for filename if necessary, although validation should prevent bad chars
    safe_username = "".join(c for c in username if c.isalnum() or c in ('_', '-')).rstrip()
    if not safe_username: safe_username = "default_user" # Fallback
    chat_path = os.path.join(data_dir, f"{safe_username}_chat.json") # Use os.path.join

    try:
        with open(chat_path, 'w', encoding='utf-8') as f: # Specify encoding
            json.dump(messages, f, indent=2, ensure_ascii=False) # Use ensure_ascii=False for broader char support
    except Exception as e:
        print(f"Error saving chat history for {username}: {e}") # Print error
        # Avoid crashing the app, maybe show a warning in UI if possible
        # st.error(f"Error saving chat history: {e}") # Be cautious with st calls outside main thread

def load_chat_history(username):
    """Load chat history from a file"""
     # Sanitize username for filename if necessary
    safe_username = "".join(c for c in username if c.isalnum() or c in ('_', '-')).rstrip()
    if not safe_username: safe_username = "default_user" # Fallback
    chat_path = get_user_data_path(f"chats/{safe_username}_chat.json") # Correct path generation

    if not os.path.exists(chat_path):
        return []

    try:
        with open(chat_path, 'r', encoding='utf-8') as f: # Specify encoding
            content = f.read()
            if not content: # Handle empty file
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        print(f"Warning: Chat history file for {username} is corrupted. Starting fresh.")
        # st.warning(f"Chat history file for {username} is corrupted. Starting fresh.")
        return []
    except Exception as e:
        print(f"Error loading chat history for {username}: {e}")
        # st.error(f"Error loading chat history: {e}")
        return [] # Return empty list on other errors too


# --- Chat Page Function (Keep as is) ---
def get_llm():
    return ChatOpenAI(
        model="llama3.2:1b", base_url="http://localhost:11434/v1",
        temperature=0.2, max_tokens=150, openai_api_key="NA",
        frequency_penalty=0.5, presence_penalty=0.4
    )
empathy_llm = get_llm()
practical_llm = get_llm()
supervisor_llm = get_llm()

# --- Your prompt functions (get_empathy_response, get_practical_response, combine_responses) here ---
# --- Your generate_response and validate_response functions here ---
# --- Your save/load_chat_history and get_user_data_path functions here ---


# =============================================================================
# REVISED CHAT PAGE USING NATIVE STREAMLIT CHAT ELEMENTS
# =============================================================================
def chat_page():
    """Display the chat interface using native st.chat_message"""

    if "username" not in st.session_state or not st.session_state.username:
        st.warning("Please select or create a profile first.")
        st.stop()

    st.title("💬 Chat Support")

    # --- CUSTOM CSS FOR LARGER FONT and Styling ---
    st.markdown("""
    <style>
        /* Target the markdown container within chat messages */
        div[data-testid="stChatMessage"] div[data-testid="stMarkdownContainer"] p {
            font-size: 1.2rem; /* Significantly larger font size */
            line-height: 1.6; /* Improve readability */
        }
        /* Target the chat input textarea */
        div[data-testid="stChatInput"] textarea {
            font-size: 1.1rem; /* Slightly larger font for input */
        }
        /* Add more spacing below each chat message */
        div[data-testid="stVerticalBlock"] {
            margin-bottom: 1rem; /* Add space between messages */
        }
    </style>
    """, unsafe_allow_html=True)
    # --- END CUSTOM CSS ---

    # Initialize or load chat history (no change needed here)
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history(st.session_state.username)
        # Add a default assistant message if history is empty
        if not st.session_state.messages:
            st.session_state.messages.append(
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            )

    # Display chat messages using st.chat_message
    # No need for a separate scrollable container usually, as the page scrolls
    for i, msg in enumerate(st.session_state.messages):
        # Use the 'role' ("user" or "assistant") to determine message alignment and icon
        with st.chat_message(msg["role"]):
            # Display the content using st.markdown (handles formatting)
            st.markdown(msg["content"]) # Apply markdown formatting within the message

    # --- NATIVE CHAT INPUT WIDGET ---
    # This replaces the st.form and st.text_area for input
    # It pins to the bottom by default in recent Streamlit versions
    if prompt := st.chat_input("What's on your mind?"): # Assigns input to 'prompt' if user enters text
        # 1. Add user message to session state and display it
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Generate assistant response
        with st.spinner("Thinking..."):
            # Use the actual content from the prompt variable
            assistant_response = generate_response(prompt)

        # 3. Add assistant response to session state and display it
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

        # 4. Save history
        save_chat_history(st.session_state.username, st.session_state.messages)

        # 5. No st.rerun() needed here - st.chat_input handles the flow better

    # Clear chat button (optional, keep if desired)
    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared. How can I help you now?"}
        ]
        save_chat_history(st.session_state.username, [])
        st.success("Chat history cleared.")
        # Need to rerun here because button click doesn't automatically update message display
        st.rerun()

# --- Main execution (Example) ---
# if __name__ == "__main__":
#     # Simulate session state for testing if needed
#     if "username" not in st.session_state:
#         st.session_state.username = "test_user"
#     chat_page()