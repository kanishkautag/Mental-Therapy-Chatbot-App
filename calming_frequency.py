import streamlit as st

def calming_frequency_page():
    """Display a page with calming frequency sounds"""
    st.title("🎵 Calming Frequencies")
    st.markdown("""
    Listening to specific frequencies can help promote relaxation and focus.
    Choose a frequency below and adjust the volume as needed.
    """)
    
    # Frequency selection
    frequencies = {
        "432 Hz - Relaxation": 432,
        "528 Hz - Transformation": 528,
        "639 Hz - Connection": 639,
        "741 Hz - Expression": 741,
        "852 Hz - Intuition": 852,
        "396 Hz - Liberation": 396,
        "417 Hz - Facilitation": 417
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_frequency = st.selectbox("Select a frequency:", list(frequencies.keys()))
        volume = st.slider("Volume", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        duration = st.slider("Duration (minutes)", min_value=1, max_value=60, value=10, step=1)
    
    with col2:
        st.markdown(f"""
        ### {selected_frequency.split(' - ')[0]}
        *{selected_frequency.split(' - ')[1]}*
        
        This frequency may help with:
        - {get_benefits(selected_frequency)}
        """)
    
    # Play button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Play", use_container_width=True):
            frequency_value = frequencies[selected_frequency]
            
            # Create JavaScript for playing a tone
            js = f"""
            <script>
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                let oscillator = null;
                
                function playTone() {{
                    // Stop any existing tone
                    if (oscillator) {{
                        oscillator.stop();
                        oscillator.disconnect();
                    }}
                    
                    // Create new oscillator
                    oscillator = audioContext.createOscillator();
                    oscillator.type = 'sine';
                    oscillator.frequency.value = {frequency_value};
                    
                    // Create gain node for volume control
                    const gainNode = audioContext.createGain();
                    gainNode.gain.value = {volume};
                    
                    // Connect nodes
                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);
                    
                    // Start oscillator and schedule stop
                    oscillator.start();
                    setTimeout(() => {{
                        if (oscillator) {{
                            oscillator.stop();
                            oscillator.disconnect();
                            oscillator = null;
                            document.getElementById('playStatus').innerHTML = 'Sound stopped';
                        }}
                    }}, {duration * 60 * 1000});
                    
                    document.getElementById('playStatus').innerHTML = 'Playing {selected_frequency} for {duration} minutes...';
                }}
                
                // Call the function
                playTone();
            </script>
            <div id="playStatus">Playing {selected_frequency} for {duration} minutes...</div>
            """
            
            st.components.v1.html(js, height=100)
    
    with col2:
        # Stop button
        if st.button("⏹️ Stop", use_container_width=True):
            stop_js = """
            <script>
                if (typeof oscillator !== 'undefined' && oscillator) {
                    oscillator.stop();
                    oscillator.disconnect();
                    oscillator = null;
                    document.getElementById('stopStatus').innerHTML = 'Sound stopped';
                }
            </script>
            <div id="stopStatus">Stopped</div>
            """
            st.components.v1.html(stop_js, height=50)
    
    # Information about frequencies
    with st.expander("About Sound Frequencies"):
        st.markdown("""
        ### Benefits of Different Frequencies
        
        - **432 Hz**: Often associated with natural vibrations, may promote relaxation and reduce anxiety
        - **528 Hz**: Known as the "love frequency," associated with healing and transformation
        - **639 Hz**: Said to enhance communication and understanding
        - **741 Hz**: May promote expression and solutions to problems
        - **852 Hz**: Associated with intuition and returning to spiritual order
        - **396 Hz**: Thought to help release fear and guilt
        - **417 Hz**: Associated with facilitating change
        
        *Note: While many people find these frequencies calming, scientific evidence for specific effects varies.*
        
        ### How to Use
        
        1. Select a frequency that matches your current needs
        2. Find a quiet place where you can relax
        3. Use headphones for the best experience
        4. Start with 5-10 minute sessions
        5. Practice deep breathing while listening
        """)
        
        st.markdown("""
        ### Tips for Better Results
        
        - Try different frequencies to see which resonates best with you
        - Use regularly for potential cumulative benefits
        - Combine with meditation or journaling for enhanced effects
        - Some people prefer to listen while falling asleep
        """)

def get_benefits(frequency_name):
    """Return specific benefits based on the selected frequency"""
    benefits = {
        "432 Hz - Relaxation": "Reducing anxiety, promoting calm, enhancing sleep quality",
        "528 Hz - Transformation": "Promoting healing, enhancing clarity, facilitating positive change",
        "639 Hz - Connection": "Improving relationships, enhancing empathy, promoting harmony",
        "741 Hz - Expression": "Solving problems, creative thinking, emotional expression",
        "852 Hz - Intuition": "Awakening intuition, spiritual awareness, mental clarity",
        "396 Hz - Liberation": "Releasing fear and guilt, grounding, breaking negative patterns",
        "417 Hz - Facilitation": "Facilitating change, undoing situations, breaking negative habits"
    }
    
    return benefits.get(frequency_name, "General relaxation and focus")