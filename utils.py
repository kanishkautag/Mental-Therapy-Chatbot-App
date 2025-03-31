import os
import streamlit as st

# Modern theme definitions inspired by Gnome and Hyprland
# --- Keep all your existing imports and functions above this ---
# (os, streamlit, create_directories, get_user_data_path, apply_theme, color functions, etc.)

# ==============================================================================
# Refined Theme Definitions (Focus on Color Palettes)
# ==============================================================================
THEMES = {
    # --- Dark Themes ---
    "Catppuccin Mocha": { # Popular, soft dark theme
        "primary_color": "#cba6f7",      # Lavender (Accent)
        "background_color": "#1e1e2e",  # Base (Background)
        "text_color": "#cad3f5",        # Text (Slightly adjusted for potentially better contrast)
        "font": "'JetBrains Mono', monospace" # Good coding font
    },
    "Nord": { # Cool, subdued dark theme
        "primary_color": "#88c0d0",      # Frost 3 - Blue/Cyan (Accent)
        "background_color": "#2e3440",  # Polar Night 1 (Darkest Background)
        "text_color": "#e5e9f0",        # Snow Storm 2 (Readable light text)
        "font": "'Inter', sans-serif"   # Clean sans-serif
    },
    "Gruvbox Dark": { # Retro, warm dark theme
        "primary_color": "#fe8019",      # Orange (Accent)
        "background_color": "#282828",  # Hard Dark Background
        "text_color": "#ebdbb2",        # Light Text
        "font": "'Fira Code', monospace" # Often paired with Gruvbox
    },
    "Solarized Dark": { # Classic high-contrast dark theme
        "primary_color": "#268bd2",      # Blue (Accent)
        "background_color": "#002b36",  # Base03 (Dark Background)
        "text_color": "#93a1a1",        # Base1 (Subdued but readable text)
        "font": "'Source Code Pro', monospace"
    },
    "Dracula": { # Popular vibrant dark theme
        "primary_color": "#bd93f9",      # Purple (Accent)
        "background_color": "#282a36",  # Background
        "text_color": "#f8f8f2",        # Foreground (Bright text)
        "font": "'JetBrains Mono', monospace"
    },
     "Tokyo Night": { # Balanced dark theme
        "primary_color": "#7aa2f7",      # Blue (Accent)
        "background_color": "#1a1b26",  # Background
        "text_color": "#c0caf5",        # Foreground (Readable light text)
        "font": "'Roboto Mono', monospace" # Common choice
    },
    "Arc Dark": { # Clean dark theme
        "primary_color": "#5294e2",      # Arc Blue (Accent)
        "background_color": "#2f343f",  # Background
        "text_color": "#d3dae3",        # Light Text
        "font": "'Nunito Sans', sans-serif" # Clean sans-serif
    },

}

# --- Keep all your existing functions below this ---
# (create_directories, get_user_data_path, apply_theme, color functions, format_timestamp, etc.)

def create_directories():
    """Create necessary directories for data storage"""
    dirs = [
        "user_data",
        "user_data/journals",
        "user_data/chats",
        "user_data/mood_data"
    ]
    
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

def get_user_data_path(filename):
    """Construct a path to a user data file"""
    return os.path.join("user_data", filename)

def apply_theme(theme_name):
    """Apply theme settings to Streamlit"""
    if theme_name not in THEMES:
        theme_name = "Adwaita Light"
    
    theme = THEMES[theme_name]
    
    # Apply theme using Streamlit's custom theming
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&family=JetBrains+Mono:wght@400;700&family=Fira+Sans:wght@400;500;700&family=Source+Code+Pro:wght@400;700&family=Inter:wght@400;500;700&family=Roboto:wght@300;400;500;700&display=swap');
        
        :root {{
            --primary-color: {theme["primary_color"]};
            --background-color: {theme["background_color"]};
            --text-color: {theme["text_color"]};
            --font: {theme["font"]};
            --card-bg-color: {adjust_color_brightness(theme["background_color"], 15 if is_dark_theme(theme["background_color"]) else -5)};
            --hover-color: {adjust_color_brightness(theme["primary_color"], -20)};
            --border-color: {adjust_color_brightness(theme["background_color"], 30 if is_dark_theme(theme["background_color"]) else -15)};
        }}
        
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: var(--font);
        }}
        
        .stButton>button {{
            background-color: var(--primary-color);
            color: {get_contrast_color(theme["primary_color"])};
            border-radius: 8px;
            border: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            transition: all 0.2s ease;
        }}
        
        .stButton>button:hover {{
            background-color: var(--hover-color);
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background-color: {adjust_color_brightness(theme["background_color"], 10 if is_dark_theme(theme["background_color"]) else -3)};
            color: var(--text-color);
            font-family: var(--font);
        }}
        
        .stSidebar {{
            background-color: {adjust_color_brightness(theme["background_color"], 10 if is_dark_theme(theme["background_color"]) else -8)};
            border-right: 1px solid var(--border-color);
        }}
        
        .stSidebar .stButton>button {{
            width: 100%;
        }}
        
        .stExpander {{
            border-radius: 8px;
            border: 1px solid var(--border-color);
            background-color: var(--card-bg-color);
            margin-bottom: 1rem;
            overflow: hidden;
        }}
        
        .stTabs {{
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
            background-color: {adjust_color_brightness(theme["background_color"], 5 if is_dark_theme(theme["background_color"]) else -3)};
            border-radius: 8px 8px 0 0;
            padding: 0 4px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: 10px 16px;
            margin: 4px 4px 0 0;
            background-color: {adjust_color_brightness(theme["background_color"], 15 if is_dark_theme(theme["background_color"]) else -5)};
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: var(--primary-color) !important;
            color: {get_contrast_color(theme["primary_color"])} !important;
            font-weight: 500;
        }}
        
        .stTabs [data-baseweb="tab-panel"] {{
            background-color: var(--card-bg-color);
            border-radius: 0 0 8px 8px;
            border: 1px solid var(--border-color);
            border-top: none;
            padding: 1rem;
        }}
        
        h1, h2, h3 {{
            color: {adjust_color_brightness(theme["text_color"], 20 if is_dark_theme(theme["background_color"]) else -20)};
            font-weight: 700;
        }}
        
        .element-container {{
            margin-bottom: 1rem;
        }}
        
        /* Improve select boxes */
        .stSelectbox label,
        .stMultiselect label {{
            color: var(--text-color);
        }}
        
        .stSelectbox div[data-baseweb="select"] div,
        .stMultiselect div[data-baseweb="select"] div {{
            background-color: var(--card-bg-color);
            border-color: var(--border-color);
            color: var(--text-color);
        }}
        
        /* Streamlit chat styling */
        .stChatMessage {{
            background-color: var(--card-bg-color);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            border: 1px solid var(--border-color);
        }}
        
        .stChatInputContainer {{
            border-radius: 12px;
            border: 1px solid var(--border-color);
            background-color: var(--card-bg-color);
            padding: 0.5rem;
        }}
    </style>
    """, unsafe_allow_html=True)

def is_dark_theme(color_hex):
    """Determine if a color is dark based on its hex value"""
    # Convert hex to RGB
    h = color_hex.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    # Calculate perceived brightness (ITU-R BT.709)
    brightness = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    
    return brightness < 0.5

def get_contrast_color(color_hex):
    """Get black or white depending on what would contrast best with the input color"""
    # Convert hex to RGB
    h = color_hex.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    # Calculate perceived brightness (ITU-R BT.709)
    brightness = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    
    return "#ffffff" if brightness < 0.6 else "#000000"

def adjust_color_brightness(color_hex, brightness_offset=0):
    """Adjust the brightness of a hex color"""
    # Convert hex to RGB
    h = color_hex.lstrip('#')
    r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    
    # Adjust brightness
    r = max(0, min(255, r + brightness_offset))
    g = max(0, min(255, g + brightness_offset))
    b = max(0, min(255, b + brightness_offset))
    
    # Convert back to hex
    return f"#{r:02x}{g:02x}{b:02x}"

def format_timestamp(timestamp_str):
    """Format a timestamp string for display"""
    try:
        from datetime import datetime
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except:
        return timestamp_str