import streamlit as st
import os
import glob
from journal import journal_page
from chat_agent import chat_page
from mood_tracker import mood_tracker_page
from resources import resources_page
from calming_frequency import calming_frequency_page  # New import
from utils import apply_theme, create_directories, THEMES

# Ensure necessary directories exist
create_directories()

def get_existing_users():
    """Get a list of existing users based on journal files"""
    journal_files = glob.glob("user_data/journals/*_journal.json")
    users = []
    for file in journal_files:
        # Extract username from filename
        filename = os.path.basename(file)
        username = filename.replace("_journal.json", "")
        if username:
            users.append(username)
    return sorted(users)

def main():
    st.set_page_config(
        page_title="Therapeutic Support Companion",
        page_icon="🧠",
        layout="wide"
    )
    
    # Initialize session state variables if not already present
    if "theme" not in st.session_state:
        st.session_state.theme = "Tokyo Night"  # Set a default theme
        
    # Apply selected theme
    apply_theme(st.session_state.theme)
    
    # Custom CSS for improved navigation
    st.markdown("""
    <style>
        .stRadio [role=radiogroup] {
            flex-direction: column;
            gap: 10px;
        }
        
        .stRadio [role=radiogroup] label {
            font-size: 18px !important;
            padding: 10px !important;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            width: 100%;
        }
        
        .stRadio [role=radiogroup] label:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Check if username is set
    if "username" not in st.session_state or st.session_state.username == "Guest":
        # Username selection/creation page
        st.title("🧠 Mind Companion")
        st.header("Welcome to your personal therapeutic support companion")
        
        # Get existing users
        existing_users = get_existing_users()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Select Existing Profile")
            
            if existing_users:
                selected_user = st.selectbox(
                    "Choose your profile:",
                    options=[""] + existing_users,
                    format_func=lambda x: "Select a profile..." if x == "" else x
                )
                
                if selected_user and st.button("Continue with Selected Profile", key="continue_existing"):
                    st.session_state.username = selected_user
                    st.rerun()
            else:
                st.info("No existing profiles found. Create a new one.")
        
        with col2:
            st.subheader("Create New Profile")
            new_username = st.text_input("Enter a name for your profile:", key="new_username")
            
            if new_username and st.button("Create New Profile", key="create_new"):
                # Validate username (no special chars that might cause filename issues)
                import re
                if not re.match("^[a-zA-Z0-9_-]+$", new_username):
                    st.error("Username can only contain letters, numbers, underscores, and hyphens.")
                else:
                    st.session_state.username = new_username
                    st.rerun()
        
        # Quick start as guest
        st.divider()
        if st.button("Continue as Guest", key="guest_login"):
            st.session_state.username = "Guest"
            st.rerun()
            
        # Theme preview and selection
        st.divider()
        st.subheader("Choose a Theme")
        
        # Create a grid of theme options
        theme_cols = st.columns(4)
        theme_options = list(THEMES.keys())
        
        for i, theme_name in enumerate(theme_options):
            with theme_cols[i % 4]:
                if st.button(theme_name, key=f"theme_{theme_name}"):
                    st.session_state.theme = theme_name
                    st.rerun()
    
    else:
        # Main application interface
        # Sidebar for navigation
        with st.sidebar:
            st.title("🧠 Mind Companion")
            
            # Display welcome message with username
            st.success(f"Welcome, {st.session_state.username}!")
            
            # User profile and switch option
            if st.button("Switch Profile"):
                st.session_state.username = "Guest"  # Reset username to trigger selection screen
                st.rerun()
            
            # Theme selection
            st.divider()
            theme_options = list(THEMES.keys())
            selected_theme = st.selectbox(
                "Choose Theme", theme_options, index=theme_options.index(st.session_state.theme)
            )
            
            if selected_theme != st.session_state.theme:
                st.session_state.theme = selected_theme
                st.rerun()
            
            st.divider()
            
            # Navigation - Enhanced with more prominent styling
            pages = {
                "💬 Chat Support": chat_page,
                "📝 Journal": journal_page,
                "📊 Mood Calendar": mood_tracker_page,  # Renamed to match simplified functionality
                "🎵 Calming Frequencies": calming_frequency_page,  # New page
                "📚 Resources": resources_page
            }
            
            selected_page = st.radio("Navigation", list(pages.keys()), key="nav_radio")
            
            st.divider()
            
            # About section
            st.markdown("### About This App")
            st.write(
                "This companion combines support with practical advice to help you process thoughts and feelings."
            )
            
            st.write(f"Profile: **{st.session_state.username}**")
        
        # Display selected page
        pages[selected_page]()

if __name__ == "__main__":
    main()