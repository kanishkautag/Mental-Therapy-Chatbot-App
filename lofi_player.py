import streamlit as st

def lofi_sounds_page():
    """Display a page with embedded Lofi music streams"""
    st.title("🎧 Lofi Sounds for Focus & Relaxation")
    st.markdown("""
    Chill out, study, or just relax with some curated lofi music streams.
    Select a stream below and use the player controls to play, pause, and adjust volume.
    """)

    # --- Lofi Stream Selection ---
    # Find popular, reliable streams on YouTube (look for 'live' or long videos)
    # Get the video ID (the part after 'v=' in the URL)
    lofi_streams = {
        "Lofi Girl Radio ☕️ - Beats to Relax/Study to": "jfKfPfyJRdk",
        "Chillhop Radio 🐾 - Jazzy & Lofi Hip Hop Beats": "5yx6BWlEVcY",
        "Synthwave Radio 🌃 - Beats to Chill/Game to": "4xDzrJKXOOY",
        "Cozy Coffee Shop  Mellow Beats 🌧️": "lTRiuFIWV54",
        "Space Ambient Music LIVE 🪐": "tNkZsRW7h2c",
        # Add more streams if you like
    }

    selected_stream_name = st.selectbox(
        "Choose your vibe:",
        list(lofi_streams.keys())
    )

    # --- Display YouTube Player ---
    if selected_stream_name:
        video_id = lofi_streams[selected_stream_name]
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"

        st.markdown(f"### Now Playing: {selected_stream_name}")

        # Use st.video for easy embedding
        # Note: Autoplay might be restricted by browsers. Users usually need to click play.
        # Height can be adjusted as needed. 400 is often a good starting point.
        st.video(youtube_url)

        st.caption("Use the player controls above for play/pause and volume.")
        st.markdown("---") # Add a separator

    # --- Information Section ---
    with st.expander("Tips for Using Lofi Music"):
        st.markdown("""
        ### Why Lofi?

        Lofi (low-fidelity) music often features calming melodies, steady beats (usually without lyrics), and sometimes subtle background noise (like rain or vinyl crackle). Many people find it helps with:

        - **Focus:** The predictable, non-distracting nature can help concentration during work or study.
        - **Relaxation:** Creates a chill, cozy atmosphere, reducing stress and anxiety.
        - **Sleep:** Gentle lofi tracks can be a soothing background sound for falling asleep.
        - **Mood Setting:** Instantly makes a space feel more comfortable and calm.

        ### How to Use This Page

        1.  **Select a Stream:** Choose a vibe that matches your current mood or task.
        2.  **Press Play:** Click the play button on the video player that appears.
        3.  **Adjust Volume:** Use the volume control *within the YouTube player*.
        4.  **Minimize Distractions:** Let the music play in the background while you focus, relax, or unwind.
        5.  **Explore:** Try different streams to find your favorites!

        *Note: These are live streams or long videos hosted on YouTube. Availability may depend on the original creator.*
        """)

# --- Example of how to call this page in a multi-page app ---
# if __name__ == "__main__":
#     # Add navigation logic if needed, e.g., using a sidebar
#     page_options = {
#         "Chat": chat_page, # Assuming you have chat_page defined elsewhere
#         "Lofi Sounds": lofi_sounds_page
#     }
#     selected_page = st.sidebar.radio("Navigate", list(page_options.keys()))
#     page_options[selected_page]() # Run the selected page function

# Or just run this page directly for testing:
if __name__ == "__main__":
    lofi_sounds_page()