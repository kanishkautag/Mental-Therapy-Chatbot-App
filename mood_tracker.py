import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import calendar
from utils import get_user_data_path
from journal import get_journal_entries

def get_mood_data(username):
    """Extract mood data from journal entries"""
    entries = get_journal_entries(username)
    
    # Convert mood to numeric
    mood_map = {
        "Very Low": 1,
        "Low": 2,
        "Neutral": 3,
        "Good": 4,
        "Excellent": 5
    }
    
    mood_data = []
    for entry in entries:
        if "mood" in entry and entry["mood"] and "date" in entry:
            mood_data.append({
                "date": entry["date"],
                "mood": entry["mood"],
                "mood_value": mood_map.get(entry["mood"], 3),
                "timestamp": entry["timestamp"]
            })
    
    return mood_data

def create_mood_calendar(mood_data, year=None, month=None):
    """Create a calendar heatmap of mood"""
    if not mood_data:
        return None
    
    # Set default year and month to current if not specified
    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month
    
    # Convert to dataframe
    df = pd.DataFrame(mood_data)
    df["date"] = pd.to_datetime(df["date"])
    
    # Filter to the selected month
    df = df[
        (df["date"].dt.year == year) & 
        (df["date"].dt.month == month)
    ]
    
    # If multiple entries per day, use the average
    daily_mood = df.groupby("date")["mood_value"].mean().reset_index()
    
    # Create the calendar data
    cal_data = []
    
    # Get the first day of the month and the number of days
    first_day = datetime(year, month, 1)
    last_day = first_day.replace(day=calendar.monthrange(year, month)[1])
    
    # Create a date range for the entire month
    date_range = pd.date_range(start=first_day, end=last_day)
    
    # Calculate week and day coordinates for the calendar
    for date in date_range:
        day_of_week = date.weekday()  # Monday=0, Sunday=6
        week_num = (date.day - 1 + first_day.weekday()) // 7
        
        # Find mood for this date if it exists
        mood_entry = daily_mood[daily_mood["date"] == pd.Timestamp(date)]
        mood_value = mood_entry["mood_value"].values[0] if not mood_entry.empty else None
        
        cal_data.append({
            "date": date,
            "day": date.day,
            "day_of_week": day_of_week,
            "week": week_num,
            "mood_value": mood_value
        })
    
    # Convert to dataframe
    cal_df = pd.DataFrame(cal_data)
    
    # Create the calendar grid with fixed labelExpr
    calendar_heatmap = alt.Chart(cal_df).mark_rect().encode(
        x=alt.X('day_of_week:O',
                axis=alt.Axis(title=None, labelAngle=0, values=list(range(7)), 
                              labelExpr="['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][datum.value]")),
        y=alt.Y('week:O', axis=alt.Axis(title=None, labels=False)),
        color=alt.Color('mood_value:Q', 
                       scale=alt.Scale(domain=[1, 5], range=['#ff9999', '#99ff99']),
                       legend=alt.Legend(title="Mood", 
                                        values=[1, 2, 3, 4, 5],
                                        labelExpr="['Very Low', 'Low', 'Neutral', 'Good', 'Excellent'][datum.value-1]")),
        tooltip=['date:T', 'mood_value:Q']
    ).properties(
        width=600,
        height=250
    )
    
    # Add day numbers
    day_labels = alt.Chart(cal_df).mark_text().encode(
        x='day_of_week:O',
        y='week:O',
        text='day:N',
        color=alt.condition(
            alt.datum.mood_value < 3,
            alt.value('black'),
            alt.value('black')
        )
    )
    
    return calendar_heatmap + day_labels

def mood_tracker_page():
    """Display the mood tracker interface"""
    st.title("📊 Mood Calendar")
    
    # Get mood data
    mood_data = get_mood_data(st.session_state.username)
    
    if not mood_data:
        st.info("No mood data available yet. Start adding mood to your journal entries to see your mood on the calendar.")
        return
    
    # Month and year selection
    now = datetime.now()
    years = list(range(now.year - 2, now.year + 1))
    months = list(range(1, 13))
    
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Year", years, index=years.index(now.year))
    
    with col2:
        selected_month = st.selectbox("Month", months, index=now.month - 1, 
                                     format_func=lambda m: calendar.month_name[m])
    
    # Display calendar
    mood_calendar = create_mood_calendar(mood_data, selected_year, selected_month)
    if mood_calendar:
        st.altair_chart(mood_calendar, use_container_width=True)
    
    # Simple legend explanation
    st.markdown("""
    **Mood Color Guide:**
    - 🟩 Green: Good/Excellent mood
    - 🟨 Yellow: Neutral mood
    - 🟥 Red: Low/Very Low mood
    """)
    
    # Add a simple monthly summary
    with st.expander("Monthly Summary"):
        df = pd.DataFrame(mood_data)
        df["date"] = pd.to_datetime(df["date"])
        
        # Filter to selected month
        month_df = df[
            (df["date"].dt.year == selected_year) &
            (df["date"].dt.month == selected_month)
        ]
        
        if not month_df.empty:
            avg_mood = month_df["mood_value"].mean()
            
            st.write(f"Average mood for {calendar.month_name[selected_month]} {selected_year}: **{avg_mood:.1f}/5**")
            
            mood_counts = month_df["mood"].value_counts()
            if not mood_counts.empty:
                most_common = mood_counts.idxmax()
                st.write(f"Most common mood: **{most_common}** ({mood_counts[most_common]} days)")
            
            days_logged = month_df["date"].dt.date.nunique()
            days_in_month = calendar.monthrange(selected_year, selected_month)[1]
            st.write(f"Days logged: **{days_logged}/{days_in_month}** days")
        else:
            st.write("No mood data available for this month.")