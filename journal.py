import streamlit as st
import os
import json
from datetime import datetime
from utils import get_user_data_path

def save_journal_entry(username, entry, mood=None, tags=None):
    """Save a journal entry to a JSON file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.now().strftime("%Y-%m-%d")
    journal_path = get_user_data_path(f"journals/{username}_journal.json")
    
    # Load existing entries if file exists
    if os.path.exists(journal_path):
        with open(journal_path, 'r') as f:
            try:
                entries = json.load(f)
            except:
                entries = []
    else:
        entries = []
    
    # Add new entry
    entry_data = {
        "timestamp": timestamp,
        "date": date,
        "entry": entry,
        "mood": mood,
        "tags": tags or []
    }
    
    entries.append(entry_data)
    
    # Save updated entries
    with open(journal_path, 'w') as f:
        json.dump(entries, f, indent=2)
    
    return timestamp

def get_journal_entries(username):
    """Retrieve journal entries for a user"""
    journal_path = get_user_data_path(f"journals/{username}_journal.json")
    
    if not os.path.exists(journal_path):
        return []
    
    with open(journal_path, 'r') as f:
        try:
            entries = json.load(f)
            # Sort by timestamp (newest first)
            entries.sort(key=lambda x: x["timestamp"], reverse=True)
            return entries
        except:
            return []

def delete_journal_entry(username, index):
    """Delete a journal entry by index"""
    journal_path = get_user_data_path(f"journals/{username}_journal.json")
    
    # Load entries
    entries = get_journal_entries(username)
    if index < len(entries):
        # Remove the entry
        entries.pop(index)
        
        # Save updated entries
        with open(journal_path, 'w') as f:
            json.dump(entries, f, indent=2)
        
        return True
    return False

def journal_page():
    """Display the journal interface"""
    st.title("📝 Reflection Journal")
    
    tab1, tab2 = st.tabs(["Write", "View Entries"])
    
    with tab1:
        st.header("New Journal Entry")
        
        # Entry form
        journal_entry = st.text_area("What would you like to record today?", height=200,
                                    placeholder="Write your thoughts here...")
        
        # Mood and tags
        col1, col2 = st.columns(2)
        with col1:
            mood = st.select_slider(
                "How are you feeling today?",
                options=["Very Low", "Low", "Neutral", "Good", "Excellent"],
                value="Neutral"
            )
        
        with col2:
            tags_input = st.text_input("Tags (comma separated)", 
                                      placeholder="e.g., work, family, goals")
            tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
        
        # Save button
        if st.button("Save Entry", use_container_width=True):
            if journal_entry:
                timestamp = save_journal_entry(st.session_state.username, journal_entry, mood, tags)
                st.success(f"Entry saved at {timestamp}")
            else:
                st.warning("Please write something before saving.")
    
    with tab2:
        st.header("Previous Entries")
        entries = get_journal_entries(st.session_state.username)
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            mood_filter = st.multiselect(
                "Filter by mood",
                options=["Very Low", "Low", "Neutral", "Good", "Excellent"],
                default=[]
            )
        
        with col2:
            # Get unique tags from all entries
            all_tags = set()
            for entry in entries:
                if "tags" in entry and entry["tags"]:
                    all_tags.update(entry["tags"])
            
            tag_filter = st.multiselect("Filter by tags", options=sorted(list(all_tags)), default=[])
        
        # Apply filters
        if mood_filter or tag_filter:
            filtered_entries = []
            for entry in entries:
                include = True
                
                if mood_filter and ("mood" not in entry or entry["mood"] not in mood_filter):
                    include = False
                
                if tag_filter and ("tags" not in entry or not any(tag in entry["tags"] for tag in tag_filter)):
                    include = False
                
                if include:
                    filtered_entries.append(entry)
            
            display_entries = filtered_entries
        else:
            display_entries = entries
        
        # Show entries count
        st.write(f"Showing {len(display_entries)} of {len(entries)} entries")
        
        # Display entries
        if not display_entries:
            st.info("No journal entries match your filters. Try adjusting them or start writing to see entries here.")
        
        for i, entry in enumerate(display_entries):
            # Format the header with mood if available
            header = f"Entry from {entry['timestamp']}"
            if "mood" in entry and entry["mood"]:
                header += f" | Mood: {entry['mood']}"
            
            with st.expander(header):
                st.write(entry["entry"])
                
                # Display tags if available
                if "tags" in entry and entry["tags"]:
                    st.write("Tags: " + ", ".join(entry["tags"]))
                
                if st.button("Delete Entry", key=f"del_{i}"):
                    if delete_journal_entry(st.session_state.username, entries.index(entry)):
                        st.success("Entry deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to delete entry.")