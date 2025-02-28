import streamlit as st

def resources_page():
    """Display mental health resources"""
    st.title("📚 Mental Health Resources")
    
    # Articles section
    st.header("Articles & Guides")
    
    # Create tabs for different resource categories
    tabs = st.tabs(["Self-Care", "Stress Management", "Sleep", "Mindfulness", "Mood"])
    
    with tabs[0]:  # Self-Care
        st.subheader("Self-Care Basics")
        
        st.markdown("""
        ### What is Self-Care?
        
        Self-care is any activity that we deliberately perform in order to take care of our mental, emotional, and physical health. Self-care is key to improved mood and reduced anxiety, and it's essential for a good relationship with yourself and others.
        
        ### Self-Care Strategies
        
        1. **Physical self-care**: Activities that improve your physical wellbeing
           - Regular exercise
           - Eating nutritious foods
           - Getting enough sleep
           - Attending to medical needs
        
        2. **Mental self-care**: Activities that stimulate your mind
           - Reading books
           - Learning new skills
           - Solving puzzles
           - Engaging in creative activities
        
        3. **Emotional self-care**: Understanding and coping with challenging emotions
           - Journaling
           - Talking with a friend or therapist
           - Practicing self-compassion
           - Setting healthy boundaries
        """)
        
        st.info("💡 **Tip**: Start small! Choose one self-care activity to practice daily for a week.")
    
    with tabs[1]:  # Stress Management
        st.subheader("Managing Stress Effectively")
        
        st.markdown("""
        ### Understanding Stress
        
        Stress is your body's reaction to pressure from certain situations or events in your life. When you feel threatened, a chemical reaction occurs in your body that allows you to act in a way to prevent injury. This reaction is known as "fight-or-flight," and it's meant to protect you.
        
        ### Healthy Stress Management Techniques
        
        - **Deep breathing**: Breathe in slowly through your nose for 4 counts, hold for 1 count, and exhale through your mouth for 5 counts. Repeat 5-10 times.
        
        - **Progressive muscle relaxation**: Tense each muscle group for 5 seconds, then relax for 30 seconds, working from your toes up to your head.
        
        - **Time management**: Prioritize tasks, break large projects into smaller steps, and learn to say no to additional commitments when necessary.
        
        - **Connect with others**: Share your concerns with friends, family members, or support groups.
        
        - **Limit exposure to stressors**: Identify sources of stress and create boundaries around them when possible.
        """)
        
        st.warning("⚠️ If stress is significantly impacting your daily functioning, consider consulting with a mental health professional.")
    
    with tabs[2]:  # Sleep
        st.subheader("Improving Sleep Quality")
        
        st.markdown("""
        ### Why Sleep Matters
        
        Sleep is essential for both physical and mental health. Quality sleep helps your brain function properly, improves learning, helps you regulate emotions, and supports healthy growth and development.
        
        ### Sleep Hygiene Tips
        
        - **Consistent schedule**: Go to bed and wake up at the same time every day, even on weekends.
        
        - **Create a restful environment**: Keep your bedroom quiet, dark, relaxing, and at a comfortable temperature.
        
        - **Limit exposure to screens**: Turn off electronic devices at least 30 minutes before bedtime.
        
        - **Watch your diet**: Avoid large meals, caffeine, and alcohol before bedtime.
        
        - **Physical activity**: Regular physical activity can help you fall asleep faster and enjoy deeper sleep.
        
        - **Relaxation techniques**: Try deep breathing, meditation, or gentle stretching before bed.
        """)
        
        st.info("💡 **Tip**: Create a bedtime routine to signal to your body that it's time to wind down.")
    
    with tabs[3]:  # Mindfulness
        st.subheader("Practicing Mindfulness")
        
        st.markdown("""
        ### What is Mindfulness?
        
        Mindfulness is the practice of purposely focusing your attention on the present moment—and accepting it without judgment. Mindfulness is now being examined scientifically and has been found to be a key element in stress reduction and overall happiness.
        
        ### Simple Mindfulness Exercises
        
        - **One-minute breathing**: Focus on your breath for just one minute. Notice the sensation as you inhale and exhale.
        
        - **Five senses exercise**: Notice five things you can see, four things you can touch, three things you can hear, two things you can smell, and one thing you can taste.
        
        - **Mindful eating**: Pay attention to the taste, sight, and texture of what you eat. Try to avoid distractions while eating.
        
        - **Body scan**: Mentally scan your body from head to toe, noticing any sensations without judgment.
        
        - **Mindful walking**: As you walk, pay attention to the sensation of your feet touching the ground and the rhythm of your breath.
        """)
        
        st.success("✨ Regular mindfulness practice can lead to decreased stress, improved focus, and better emotional regulation.")
    
    with tabs[4]:  # Mood
        st.subheader("Understanding and Managing Mood")
        
        st.markdown("""
        ### Mood Awareness
        
        Being aware of your moods and their patterns is the first step toward managing them effectively. Many factors can affect your mood, including sleep, nutrition, physical activity, stress, and social interactions.
        
        ### Mood Management Strategies
        
        - **Track your mood**: Notice patterns in your mood throughout the day and week. What triggers changes in your mood?
        
        - **Physical activity**: Regular exercise can significantly improve mood by releasing endorphins.
        
        - **Nutrition**: A balanced diet can help stabilize your mood. Pay attention to how different foods affect how you feel.
        
        - **Social connections**: Spending time with supportive people can improve your mood and provide different perspectives.
        
        - **Gratitude practice**: Take time each day to note things you're grateful for, even small pleasures.
        
        - **Challenge negative thinking**: Notice negative thought patterns and try to reframe them in a more balanced way.
        """)
        
        st.warning("⚠️ If you experience persistent low mood or mood swings that interfere with daily life, consider seeking professional help.")
    
    # Crisis Resources
    st.header("Crisis Resources")
    
    crisis_col1, crisis_col2 = st.columns(2)
    
    with crisis_col1:
        st.markdown("""
        ### Immediate Help
        
        - **National Suicide Prevention Lifeline**
          - Call: 988 or 1-800-273-8255
          - Available 24/7
        
        - **Crisis Text Line**
          - Text HOME to 741741
          - Available 24/7
        
        - **Emergency Services**
          - Call: 911 (US)
          - For immediate danger
        """)
    
    with crisis_col2:
        st.markdown("""
        ### Other Support Resources
        
        - **SAMHSA's National Helpline**
          - Call: 1-800-662-4357
          - For mental health/substance use treatment referrals
        
        - **National Alliance on Mental Illness (NAMI) Helpline**
          - Call: 1-800-950-6264
          - For information, referrals, and support
        
        - **Veterans Crisis Line**
          - Call: 988, then press 1
          - Text: 838255
        """)
    
    # Helpful Apps
    st.header("Helpful Apps & Tools")
    
    app_col1, app_col2, app_col3 = st.columns(3)
    
    with app_col1:
        st.subheader("Meditation & Mindfulness")
        st.markdown("""
        - **Headspace**
        - **Calm**
        - **Insight Timer**
        - **Ten Percent Happier**
        """)
    
    with app_col2:
        st.subheader("Mood Tracking")
        st.markdown("""
        - **Daylio**
        - **MoodKit**
        - **Moodnotes**
        - **eMoods**
        """)
    
    with app_col3:
        st.subheader("Sleep & Relaxation")
        st.markdown("""
        - **Sleep Cycle**
        - **Slumber**
        - **Pzizz**
        - **White Noise**
        """)
    
    # Disclaimer
    st.divider()
    st.caption("""
    **Disclaimer**: The information provided here is for educational purposes only and is not intended to be a substitute for professional medical advice, diagnosis, or treatment. 
    Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
    """)