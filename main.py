import streamlit as st
import os
import glob
from journal import journal_page
from chat_agent import chat_page
from mood_tracker import mood_tracker_page
from resources import resources_page
# --- MODIFIED IMPORT ---
# from calming_frequency import calming_frequency_page  # Old import
from lofi_player import lofi_sounds_page  # New import for the lofi player page
# --- END MODIFICATION ---
from utils import apply_theme, create_directories, THEMES
import re # Import re for username validation

# Ensure necessary directories exist
create_directories()

def get_existing_users():
    """Get a list of existing users based on journal files"""
    # Ensure the directory exists before searching
    journal_dir = "user_data/journals"
    os.makedirs(journal_dir, exist_ok=True) # Create if it doesn't exist
    
    journal_files = glob.glob(os.path.join(journal_dir, "*_journal.json")) # Use os.path.join
    users = []
    for file in journal_files:
        # Extract username from filename
        filename = os.path.basename(file)
        # Handle potential empty filenames or unexpected formats
        if filename.endswith("_journal.json"):
            username = filename[:-len("_journal.json")] # More robust removal
            if username: # Ensure username is not empty after stripping
                users.append(username)
    return sorted(list(set(users))) # Use set to avoid duplicates just in case

def main():
    st.set_page_config(
        page_title="Mind Companion", # Simplified title
        page_icon="🧠",
        layout="wide"
    )

    # Initialize session state variables if not already present
    if "theme" not in st.session_state:
        st.session_state.theme = "Tokyo Night"  # Set a default theme
    if "username" not in st.session_state:
        st.session_state.username = None # Initialize username as None

    # Apply selected theme
    apply_theme(st.session_state.theme)

    # --- Removed custom CSS for radio buttons, using default Streamlit styling ---
    # st.markdown("""...""", unsafe_allow_html=True) # Removed custom CSS block

    # Check if username is set (changed logic slightly for clarity)
    if not st.session_state.username or st.session_state.username == "Guest":
        # Username selection/creation page
        st.title("🧠 Mind Companion")
        st.header("Welcome!")
        st.subheader("Please select or create a profile to continue")

        # Get existing users
        existing_users = get_existing_users()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("👤 Select Existing Profile")

            if existing_users:
                # Add a placeholder option
                options = [""] + existing_users
                selected_user = st.selectbox(
                    "Choose your profile:",
                    options=options,
                    format_func=lambda x: "Select a profile..." if x == "" else x,
                    key="select_existing_user" # Added key
                )

                if selected_user: # Check if a user (not the placeholder) is selected
                    if st.button("Continue", key="continue_existing"):
                        st.session_state.username = selected_user
                        st.rerun()
            else:
                st.info("No existing profiles found. Create a new one below.")

        with col2:
            st.subheader("➕ Create New Profile")
            new_username = st.text_input("Enter a profile name:", key="new_username_input") # Changed label

            if new_username: # Only show button if there's input
                if st.button("Create and Continue", key="create_new"):
                    # Validate username (allow spaces, but sanitize for filenames later if needed)
                    # Simple validation: not empty and not too long
                    clean_username = new_username.strip()
                    if not clean_username:
                         st.error("Profile name cannot be empty.")
                    elif len(clean_username) > 50:
                         st.error("Profile name is too long (max 50 characters).")
                    # Check if username already exists (case-insensitive)
                    elif clean_username.lower() in [u.lower() for u in existing_users]:
                        st.error(f"Profile name '{clean_username}' already exists. Please choose another.")
                    else:
                        # Basic check for problematic characters if needed for filenames
                        # This regex allows letters, numbers, spaces, hyphens, underscores
                        if not re.match("^[a-zA-Z0-9 _-]+$", clean_username):
                             st.error("Profile name can only contain letters, numbers, spaces, underscores, and hyphens.")
                        else:
                            st.session_state.username = clean_username
                            # Optionally: create placeholder files immediately
                            # create_user_files(clean_username)
                            st.success(f"Profile '{clean_username}' created!")
                            st.rerun()

        # Quick start as guest (moved below profile sections)
        st.divider()
        if st.button("Continue as Guest", key="guest_login"):
            st.session_state.username = "Guest"
            st.rerun()

        # Theme preview and selection (moved to bottom)
        st.divider()
        st.subheader("🎨 Choose a Theme")
        selected_theme_login = st.radio(
            "Select theme:",
            list(THEMES.keys()),
            index=list(THEMES.keys()).index(st.session_state.theme), # Show current selection
            horizontal=True, # Make radio buttons horizontal
            key="theme_select_login"
        )
        if selected_theme_login != st.session_state.theme:
            st.session_state.theme = selected_theme_login
            st.rerun()

    else:
        # Main application interface
        with st.sidebar:
            st.title("🧠 Mind Companion")
            st.success(f"Profile: **{st.session_state.username}**")

            # Switch Profile button
            if st.button("Switch Profile / Log Out", use_container_width=True):
                # Clear relevant session state items
                for key in ["username", "messages", "journal_entries", "mood_data"]: # Add other keys if needed
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

            st.divider()

            # Navigation
            pages = {
                "💬 Chat Support": chat_page,
                "📝 Journal": journal_page,
                "📊 Mood Calendar": mood_tracker_page,
                # --- MODIFIED PAGE ENTRY ---
                "🎧 Lofi Sounds": lofi_sounds_page, # Renamed key and uses the new function
                # --- END MODIFICATION ---
                "📚 Resources": resources_page
            }

            # Use icons in radio buttons (optional but nice)
            page_keys_with_icons = {
                 "💬 Chat Support": "💬 Chat Support",
                 "📝 Journal": "📝 Journal",
                 "📊 Mood Calendar": "📊 Mood Calendar",
                 "🎧 Lofi Sounds": "🎧 Lofi Sounds",
                 "📚 Resources": "📚 Resources",
            }

            selected_page_key = st.radio(
                "Navigation",
                list(page_keys_with_icons.keys()),
                format_func=lambda key: page_keys_with_icons[key], # Display text with icon
                key="nav_radio"
            )

            st.divider()

            # Theme selection
            theme_options = list(THEMES.keys())
            current_theme_index = theme_options.index(st.session_state.theme) if st.session_state.theme in theme_options else 0
            selected_theme = st.selectbox(
                "Theme", theme_options, index=current_theme_index, key="theme_select_sidebar"
            )

            if selected_theme != st.session_state.theme:
                st.session_state.theme = selected_theme
                st.rerun()

            st.divider()

            # About section
            st.info(
                "This app provides tools for reflection and relaxation. Remember, it's not a substitute for professional help."
            )

        # Display selected page
        if selected_page_key in pages:
            pages[selected_page_key]() # Call the function associated with the selected key
        else:
            st.error("Page not found.") # Fallback


if __name__ == "__main__":
    main()