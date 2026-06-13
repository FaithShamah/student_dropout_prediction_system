import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from dotenv import load_dotenv
from database import Database

warnings.filterwarnings("ignore")
load_dotenv()  # Load environment variables from .env file

SDPS_PRIMARY = "#0F4C81"   # Deep Indigo/Blue
SDPS_SECONDARY = "#008080" # Teal
SDPS_BLACK = "#1F2937"
SDPS_WHITE = "#FFFFFF"
SDPS_LIGHT = "#F3F4F6"
SDPS_SOFT_BLUE = "#E0E7FF"
SDPS_SOFT_TEAL = "#CCFBF1"
SDPS_SOFT_GRAY = "#F9FAFB"
SDPS_ACCENT = "#F59E0B"    # Amber/Gold accent

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "logo__2_-removebg-preview.png")

moderate_threshold = 0.40
high_threshold = 0.70


def load_logo_base64():
    if not os.path.exists(LOGO_PATH):
        return ""

    with open(LOGO_PATH, "rb") as logo_file:
        return base64.b64encode(logo_file.read()).decode("utf-8")


SDPS_LOGO_BASE64 = load_logo_base64()
SDPS_LOGO_HTML = (
    f'<img src="data:image/png;base64,{SDPS_LOGO_BASE64}" alt="SDPS logo" '
    'style="height:140px; width:140px; object-fit:contain; flex-shrink:0; border-radius: 50%; box-shadow: 0 8px 24px rgba(0,0,0,0.15); border: 4px solid #ffffff;" />'
    if SDPS_LOGO_BASE64
    else ""
)

# ============================================================================
# DATABASE SETUP
# ============================================================================
@st.cache_resource
def init_database():
    """Initialize Supabase database connection"""
    return Database()

@st.cache_resource
def get_database():
    """Return the cached database instance"""
    return init_database()

def init_admin_user():
    db = init_database()

    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@2026#")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")

    if not db.admin_exists():
        db.create_admin(admin_username, admin_password, admin_email)
    elif os.getenv("ADMIN_PASSWORD"):
        db.update_admin_credentials(admin_username, admin_password, admin_email)

    return db

# ============================================================================
# LEGACY CSV FUNCTIONS (for backward compatibility - can be removed later)
# ============================================================================
def load_prediction_history():
    """Load prediction history from database"""
    db = get_database()
    return db.get_all_predictions()


def save_prediction_history(history):
    """Legacy function - no longer needed with database"""
    pass  # Database saves predictions automatically


def build_history_dataframe(history):
    """Build dataframe from prediction history"""
    history_df = pd.DataFrame(history)
    if history_df.empty:
        return history_df

    history_df = history_df.reset_index(drop=False).rename(columns={"index": "_history_index"})
    if "timestamp" not in history_df.columns:
        history_df["timestamp"] = ""
    history_df["timestamp"] = history_df["timestamp"].fillna("").astype(str).replace({"nan": "", "None": ""})

    history_df["_timestamp_sort"] = pd.to_datetime(history_df["timestamp"], errors="coerce")
    history_df = history_df.sort_values(
        by=["_timestamp_sort", "timestamp"],
        ascending=False,
        na_position="last"
    ).drop(columns=["_timestamp_sort"])
    return history_df

# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def login_page():
    """Display professional login page"""
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .stTextInput label {
            font-weight: 600;
            color: #4a5568;
            font-size: 0.9em;
        }
        .stTextInput input {
            border-radius: 10px;
            border: 2px solid #e2e8f0;
            padding: 12px 16px;
            font-size: 0.95em;
            transition: border-color 0.2s;
        }
        .stTextInput input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .stButton button[kind="primary"] {
            border-radius: 10px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
            margin-top: 10px;
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        div[data-testid="stForm"] {
            background: #ffffff;
            padding: 45px 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        .login-header {
            text-align: center;
            margin-bottom: 35px;
        }
        .login-title {
            font-size: 1.8em;
            color: #2d3748;
            font-weight: 700;
            margin: 20px 0 0 0;
            line-height: 1;
            padding-bottom: 0;
        }
        .login-subtitle {
            font-size: 0.9em;
            color: #718096;
            font-weight: 600;
            margin: 0;
            padding-top: 2px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    SDPS_LOGO_BASE64 = load_logo_base64()
    SDPS_LOGO_HTML = (
        f'<img src="data:image/png;base64,{SDPS_LOGO_BASE64}" alt="SDPS" '
        'style="height:100px; width:100px; border-radius: 50%; box-shadow: 0 8px 20px rgba(0,0,0,0.15); border: 4px solid #ffffff;" />'
        if SDPS_LOGO_BASE64
        else ""
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("admin_login_form", clear_on_submit=False):
            st.markdown(f"""
                <div class="login-header">
                    <div style="text-align: center; margin-bottom: 20px;">
                        {SDPS_LOGO_HTML}
                    </div>
                    <h1 class="login-title">Admin Login</h1>
                    <p class="login-subtitle">Student Dropout Prediction System</p>
                </div>
            """, unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            submit_button = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if submit_button:
                if username and password:
                    db = get_database()
                    if db.verify_admin(username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("Authentication successful")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please check your username and password.")
                else:
                    st.warning("Please fill in all fields")    

def logout():
    """Handle logout"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

# ============================================================================
# STUDENT DROPOUT PREDICTION SYSTEM (SDPS)
# Final Year Project: ML-Based Predictive Analytics for Early Dropout Identification
# ============================================================================

# ============================================================================
# MAIN APPLICATION
# ============================================================================
# Initialize database and admin user
init_admin_user()

# Check authentication status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Show login page if not authenticated
if not st.session_state.logged_in:
    st.set_page_config(
        page_title="SDPS Login",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    login_page()
    st.stop()

# ============================================================================
# DASHBOARD (shown after successful login)
# ============================================================================
st.set_page_config(
    page_title="Student Dropout Risk Prediction | SDPS",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, #ffffff 0%, #fbf8f4 100%);
        color: #000000;
    }}
    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {SDPS_PRIMARY} 0%, #084070 100%);
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    }}
    [data-testid="stSidebar"] * {{
        color: #ffffff;
    }}
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stCaption {{
        color: #ffffff;
    }}
    [data-testid="stSidebar"] .stMarkdown h2 {{
        color: #ffffff;
        font-size: 1.2em;
        font-weight: 600;
        margin-top: 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    }}
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {{
        background-color: #ffffff !important;
        color: #1f1f1f !important;
        -webkit-text-fill-color: #1f1f1f !important;
        caret-color: #000000 !important;
        border: 1px solid #d1d5db !important;
        box-shadow: none !important;
        outline: none !important;
        appearance: none !important;
        -webkit-appearance: none !important;
        border-radius: 8px;
    }}
    [data-testid="stSidebar"] input:focus,
    [data-testid="stSidebar"] textarea:focus {{
        color: #1f1f1f !important;
        -webkit-text-fill-color: #1f1f1f !important;
        caret-color: #000000 !important;
        border: 1px solid {SDPS_SECONDARY} !important;
        box-shadow: 0 0 0 3px rgba(0, 128, 128, 0.1) !important;
        outline: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stTextInputRootElement"]:has(input[aria-label="Age at Enrollment"]) {{
        border: 1px solid #dbc4b3 !important;
        box-shadow: none !important;
        outline: none !important;
        border-radius: 12px;
        background-color: #ffffff !important;
    }}
    [data-testid="stSidebar"] [data-testid="stTextInputRootElement"]:has(input[aria-label="Age at Enrollment"]):focus-within {{
        border: 1px solid #dbc4b3 !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {{
        color: #b9aa9b !important;
        opacity: 0.86;
        font-style: italic;
        font-weight: 400;
        -webkit-text-fill-color: #b9aa9b !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        color: #1f1f1f !important;
        -webkit-text-fill-color: #1f1f1f !important;
        border: 1px solid #d1d5db !important;
        border-radius: 8px;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] input {{
        position: absolute !important;
        width: 0 !important;
        min-width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: 0 !important;
        opacity: 0 !important;
        caret-color: transparent !important;
        box-shadow: none !important;
        background: transparent !important;
        pointer-events: none !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] input:focus {{
        outline: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] [class*="singleValue"],
    [data-testid="stSidebar"] [data-baseweb="select"] [class*="SingleValue"],
    [data-testid="stSidebar"] [data-baseweb="select"] [class*="valueContainer"],
    [data-testid="stSidebar"] [data-baseweb="select"] [class*="ValueContainer"] {{
        color: #1f1f1f !important;
        -webkit-text-fill-color: #1f1f1f !important;
        cursor: pointer !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] span {{
        color: #1f1f1f !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"] [data-placeholder="true"] {{
        color: #b9aa9b !important;
        opacity: 0.86;
        font-style: italic;
        font-weight: 400;
        -webkit-text-fill-color: #b9aa9b !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="select"]:has(input[value=""]) > div:first-child > div:first-child {{
        color: #b9aa9b !important;
        opacity: 0.86;
        font-style: italic;
        font-weight: 400;
        -webkit-text-fill-color: #b9aa9b !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="menu"] {{
        background-color: #ffffff !important;
    }}
    [data-testid="stSidebar"] [role="option"] {{
        color: #1f1f1f !important;
        background-color: #ffffff !important;
    }}
    [data-testid="stSidebar"] [role="option"]:hover {{
        background-color: #f4e7db !important;
        color: #1f1f1f !important;
    }}
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {{
        background: {SDPS_SECONDARY};
    }}
    [data-testid="stSidebar"] .stButton>button {{
        background: linear-gradient(135deg, {SDPS_SECONDARY} 0%, #006666 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        padding: 10px 16px;
        transition: all 0.2s ease;
    }}
    [data-testid="stSidebar"] .stButton>button:hover {{
        background: linear-gradient(135deg, #006666 0%, {SDPS_SECONDARY} 100%);
        box-shadow: 0 4px 12px rgba(0, 128, 128, 0.3);
        transform: translateY(-1px);
    }}
    .hero-panel {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 24px;
        padding: 26px 28px;
        margin: 0 0 18px 0;
        background: linear-gradient(135deg, #ffffff 0%, #fff6ee 100%);
        border: 1px solid #eadbcc;
        border-radius: 22px;
        box-shadow: 0 14px 40px rgba(107, 50, 0, 0.08);
        flex-wrap: wrap;
    }}
    .hero-kicker {{
        margin: 0 0 8px 0;
        color: %s;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        font-weight: 700;
    }}
    .main-header {{
        font-size: 3.4em;
        color: {SDPS_ACCENT};
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.04em;
        line-height: 1.02;
    }}
    .subtitle {{
        font-size: 1.15em;
        color: #7a5a43;
        margin-top: -8px;
        margin-bottom: 10px;
    }}
    .hero-copy {{
        max-width: 760px;
        color: #5f5f5f;
        line-height: 1.6;
        margin: 0;
    }}
    .hero-meta {{
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 160px;
        flex: 0 0 160px;
    }}
    .hero-chip {{
        background: {SDPS_SECONDARY};
        color: #ffffff;
        border-radius: 999px;
        padding: 8px 12px;
        text-align: center;
        font-weight: 700;
        font-size: 0.82rem;
        line-height: 1.15;
        box-shadow: 0 8px 20px rgba(31, 111, 139, 0.12);
    }}
    .section-label {{
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #8a6b56;
        font-weight: 700;
        margin: 0 0 10px 0;
    }}
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 0 0 16px 0;
    }}
    .stat-card {{
        background: #ffffff;
        border: 1px solid #eadbcc;
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 8px 20px rgba(31, 111, 139, 0.05);
    }}
    .stat-label {{
        display: block;
        color: #6B3200;
        margin-bottom: 6px;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-weight: 700;
    }}
    .stat-value {{
        color: #1f1f1f;
        font-size: 1.15rem;
        font-weight: 800;
    }}
    .stat-note {{
        display: block;
        color: #5f5f5f;
        font-size: 0.92rem;
        margin-top: 6px;
        line-height: 1.4;
    }}
    .risk-high {{ 
        background-color: #fff1e1; 
        border-left: 5px solid #E67E00;
        padding: 15px; 
        border-radius: 10px; 
        margin: 10px 0;
    }}
    .risk-moderate {{ 
        background-color: #f4e7db; 
        border-left: 5px solid #6B3200;
        padding: 15px; 
        border-radius: 10px; 
        margin: 10px 0;
    }}
    .risk-low {{ 
        background-color: #fafafa; 
        border-left: 5px solid #6B3200;
        padding: 15px; 
        border-radius: 10px; 
        margin: 10px 0;
    }}
    .insight-box {{
        background-color: #f2f2f2;
        border-left: 4px solid #E67E00;
        padding: 12px;
        border-radius: 10px;
        margin: 10px 0;
    }}
    .notice-success {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: linear-gradient(135deg, #f4e7db 0%, #fff8ef 100%);
        border: 1px solid rgba(107, 50, 0, 0.18);
        border-left: 6px solid {SDPS_SECONDARY};
        color: #4f2400;
        border-radius: 14px;
        padding: 14px 16px;
        margin: 10px 0 14px 0;
        box-shadow: 0 10px 24px rgba(107, 50, 0, 0.08);
    }}
    .notice-success-icon {{
        width: 34px;
        height: 34px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        background: {SDPS_SECONDARY};
        color: #ffffff;
        font-size: 1rem;
        flex: 0 0 34px;
    }}
    .notice-success-title {{
        font-weight: 800;
        margin: 0;
        color: #4f2400;
    }}
    .notice-success-text {{
        margin: 2px 0 0 0;
        color: #6b4b35;
        font-size: 0.95rem;
    }}
    div[data-testid="stMetric"] {{
        background: #ffffff;
        border: 1px solid #eadbcc;
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: 0 6px 18px rgba(107, 50, 0, 0.06);
        min-height: 112px;
    }}
    div[data-testid="stMetric"] label {{
        color: #6B3200;
    }}
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
        display: flex;
        justify-content: space-between;
        gap: 16px;
        width: 100%;
        background: linear-gradient(180deg, rgba(255, 252, 248, 0.98) 0%, rgba(246, 240, 233, 0.96) 100%);
        padding: 8px;
        border-radius: 16px;
        border: 1px solid rgba(31, 111, 139, 0.12);
        position: relative;
        border-bottom: none !important;
        box-shadow: 0 10px 24px rgba(52, 72, 84, 0.08);
    }}
    
    /* Responsive design for mobile */
    @media (max-width: 768px) {{
        .hero-panel {{
            padding: 18px;
            gap: 14px;
            border-radius: 18px;
        }}
        .main-header {{
            font-size: 2.25rem;
            line-height: 1.08;
        }}
        .subtitle {{
            font-size: 1rem;
            margin-top: -4px;
        }}
        .hero-copy {{
            font-size: 0.96rem;
            line-height: 1.5;
        }}
        .hero-meta {{
            min-width: 112px;
            flex: 0 0 112px;
        }}
        .hero-meta img {{
            width: 96px !important;
            height: 96px !important;
        }}
        div[data-testid="stColumn"] {{
            min-width: 0 !important;
        }}
        div[data-testid="stMetric"] {{
            min-height: 96px;
            padding: 10px 12px;
        }}
        div[data-testid="stMetric"] label {{
            font-size: 0.82rem;
        }}
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
            font-size: 1rem;
        }}
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
            flex-direction: row !important;
            overflow-x: auto !important;
            gap: 8px;
            padding: 6px;
        }}
        div[data-testid="stTabs"] button[role="tab"] {{
            flex: 1 0 auto !important;
            width: 150px;
            padding: 0.75rem 0.9rem;
            font-size: 0.9rem;
        }}
        .notice-success {{
            align-items: flex-start;
            padding: 12px;
        }}
        .notice-success-icon {{
            width: 30px;
            height: 30px;
            flex: 0 0 30px;
        }}
    }}
    @media (max-width: 480px) {{
        .block-container {{
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }}
        .hero-panel {{
            padding: 16px;
        }}
        .main-header {{
            font-size: 1.85rem;
        }}
        .subtitle {{
            font-size: 0.92rem;
        }}
        .hero-copy {{
            font-size: 0.9rem;
        }}
        .hero-meta {{
            min-width: 92px;
            flex: 0 0 92px;
        }}
        .hero-meta img {{
            width: 82px !important;
            height: 82px !important;
        }}
        div[data-testid="stMetric"] {{
            min-height: 88px;
            padding: 9px 10px;
        }}
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
            font-size: 0.92rem;
        }}
        div[data-testid="stTabs"] button[role="tab"] {{
            width: 138px;
            font-size: 0.84rem;
        }}
    }}
    /* Hide Streamlit/BaseWeb's active tab underline indicator */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"],
    div[data-testid="stTabs"] [data-baseweb="tab"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab"] [data-baseweb="tab-border-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab"] [data-baseweb="tab-border"],
    div[data-testid="stTabs"] button[role="tab"]::before,
    div[data-testid="stTabs"] button[role="tab"]::after {{
        display: none !important;
        content: none !important;
        border: 0 !important;
        box-shadow: none !important;
        background: transparent !important;
        height: 0 !important;
        width: 0 !important;
        opacity: 0 !important;
    }}
    /* Tabs: remove default focus/underline and use subtle accent hover */
    div[data-testid="stTabs"] button[role="tab"] {{
        color: #5C6770;
        font-weight: 700;
        border-radius: 14px;
        transition: background-color 160ms ease, color 160ms ease, box-shadow 160ms ease, border-color 160ms ease, transform 160ms ease;
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-bottom: none !important;
        flex: 1;
        justify-content: center;
        padding: 0.82rem 1rem;
        white-space: nowrap;
        background: rgba(255, 255, 255, 0.78);
        box-shadow: none !important;
        text-decoration: none !important;
        outline: none !important;
        position: relative;
    }}
    
    @media (max-width: 768px) {{
        div[data-testid="stTabs"] button[role="tab"] {{
            flex: 1 0 auto !important;
            width: 150px;
        }}
    }}
    /* Remove any browser/Streamlit focus ring or underline */
    div[data-testid="stTabs"] button[role="tab"]:focus,
    div[data-testid="stTabs"] button[role="tab"]:focus-visible {{
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(31, 111, 139, 0.12) !important;
        border-bottom: none !important;
    }}
    /* Hover: subtle blue-teal hover effect */
    div[data-testid="stTabs"] button[role="tab"]:hover {{
        background: linear-gradient(180deg, rgba(15, 76, 129, 0.08) 0%, rgba(0, 128, 128, 0.06) 100%);
        color: {SDPS_PRIMARY};
        border-color: rgba(15, 76, 129, 0.25);
        box-shadow: 0 4px 12px rgba(15, 76, 129, 0.15) !important;
        transform: translateY(-1px);
    }}
    /* Selected tab: stronger teal emphasis with no underline */
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        /* Muted orange selected state */
        background: linear-gradient(180deg, {SDPS_SECONDARY} 0%, #B85A00 100%);
        color: #FFFFFF;
        border-color: rgba(184, 90, 0, 0.28);
        box-shadow: 0 10px 20px rgba(184, 90, 0, 0.18) !important;
        border-bottom: none !important;
    }}

    /* Orange underline under the tab list (full-width, subtle shadow) */
    div[data-testid="stTabs"] [data-baseweb="tab-list"]::after {{
        content: "";
        position: absolute;
        left: 10px;
        right: 10px;
        bottom: -6px;
        height: 4px;
        background: linear-gradient(90deg, {SDPS_SECONDARY} 0%, #DD6B20 100%);
        border-radius: 6px;
        box-shadow: 0 6px 14px rgba(230,126,0,0.14);
        display: block;
        z-index: 1;
    }}
    div[data-testid="stButton"] button {{
        font-size: 0.72rem;
        min-height: 1.8rem;
        padding: 0.18rem 0.55rem;
        border-radius: 8px;
        width: auto;
        line-height: 1;
    }}
    .stDownloadButton>button {{
        background: #6B3200;
        color: #ffffff;
        border: 1px solid #6B3200;
        border-radius: 12px;
        font-weight: 700;
    }}
    .stDownloadButton>button:hover {{
        background: #4f2400;
        border-color: #4f2400;
    }}
    
    <!-- Dark-mode CSS overrides -->
    
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div class="hero-panel">
        <div style="display:flex; flex-direction:column; justify-content:center; flex:1 1 520px; min-width: 320px;">
            <h1 class="main-header">Student Dropout Risk Prediction System</h1>
            <p class="subtitle">AI-assisted early warning dashboard for admission support</p>
            <p class="hero-copy">Single student assessment, intake triage, and model intelligence in one view.</p>
        </div>
        <div class="hero-meta">
            {SDPS_LOGO_HTML}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# SESSION STATE & MODEL LOADING
# ============================================================================
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = load_prediction_history()
if "batch_results" not in st.session_state:
    st.session_state.batch_results = None
if "clear_timestamp_confirm" not in st.session_state:
    st.session_state.clear_timestamp_confirm = False
if "history_notice" not in st.session_state:
    st.session_state.history_notice = None

@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "dropout_model.pkl")
    if not os.path.exists(model_path):
        st.error("Model file not found: dropout_model.pkl")
        st.stop()
    return joblib.load(model_path)

model = load_model()
db = get_database()

# ============================================================================
# FEATURE DEFINITIONS (UCI DATASET)
# ============================================================================
MARITAL_STATUS = {
    "Single": 1,
    "Married": 2,
    "Widower": 3,
    "Divorced": 4,
    "Facto Union": 5,
    "Legally Separated": 6
}

SPECIAL_NEEDS = {
    "No": 0,
    "Yes": 1
}

QUALIFICATION = {
    "UACE Certificate": 1,
    "Diploma": 42,
    "Bachelor's Degree": 2,
    "Degree": 3,
    "Master's Degree": 4,
    "Doctorate": 5,
    "Technical Certificate": 39
}

APPLICATION_MODE = {
    "Direct Entry (UACE)": 1,
    "Diploma Entry": 7,
    "International Student": 15,
    "Mature Age Entry": 39,
    "Transfer Student": 42,
    "Change of Course": 43,
    "Technical/Vocational Entry": 44,
    "Other Admission Route": 51
}

COURSE = {
    "Computer Science / IT": 9119,
    "Business & Management": 9147,
    "Tourism": 9254,
    "Nursing": 9500,
    "Journalism & Communication": 9773,
    "Education": 9853,
    "Agriculture": 9003,
    "Marketing": 9670
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_risk_category(prob):
    """Classify dropout risk"""
    if prob >= 0.7:
        return "HIGH RISK", "critical"
    elif prob >= 0.4:
        return "MODERATE RISK", "warning"
    else:
        return "LOW RISK", "success"

def validate_inputs(age):
    """Validate student inputs"""
    warnings_list = []
    if age < 18:
        warnings_list.append("Student is under 18 (early enrollment)")
    if age > 35:
        warnings_list.append("Mature student (age > 35)")
    return warnings_list

def generate_recommendations(prob, age, marital, special_needs):
    """Generate personalized intervention recommendations"""
    recs = []
    
    if prob >= 0.7:
        recs.extend([
            "Assign dedicated academic advisor for intensive monitoring",
            "Schedule mandatory counseling/mentoring session",
            "Review financial support eligibility",
            "Develop personalized success plan"
        ])
    elif prob >= 0.4:
        recs.extend([
            "Schedule bi-weekly check-ins with advisor",
            "Offer peer mentoring/study groups",
            "Monitor course attendance closely",
            "Provide access to tutoring services"
        ])
    else:
        recs.extend([
            "Continue standard academic support",
            "Encourage campus engagement",
            "Regular progress monitoring"
        ])
    
    if age >= 30:
        recs.append("Consider flexible scheduling options for balance")
    if marital in [2, 4, 5, 6]:
        recs.append("Assess work-life-study balance challenges")
    if special_needs == 1:
        recs.append("Verify all accessibility accommodations are active")
    
    return recs

# ============================================================================
# MAIN APPLICATION INTERFACE
# ============================================================================
def classify_priority(priority_score):
    if priority_score >= 80:
        return "P1 - Immediate"
    if priority_score >= 60:
        return "P2 - High"
    if priority_score >= 40:
        return "P3 - Medium"
    return "P4 - Routine"


def intervention_owner(priority):
    if priority == "P1 - Immediate":
        return "Retention Lead"
    if priority == "P2 - High":
        return "Academic Advisor"
    if priority == "P3 - Medium":
        return "Program Coordinator"
    return "Student Support Desk"


def compute_priority_score(prob, age, special_needs):
    score = prob * 100
    score += 10 if special_needs == 1 else 0
    score += 5 if (age < 18 or age >= 30) else 0
    return float(min(100, round(score, 2)))


moderate_threshold = 0.40
high_threshold = 0.70

# Admin Profile Section
db = get_database()
admin_profile = db.get_admin_profile(st.session_state.username)

st.sidebar.markdown("---")

# Load the profile image (image.png)
profile_image_path = os.path.join(os.path.dirname(__file__), "..", "assets", "image.png")
if os.path.exists(profile_image_path):
    with open(profile_image_path, "rb") as img_file:
        profile_img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
else:
    profile_img_base64 = load_logo_base64()  # Fallback to logo

# Professional Profile header with image.png
st.sidebar.markdown(f"""
    <div style="padding: 20px 16px; background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border-radius: 16px; margin-bottom: 20px; border: 1px solid rgba(15, 76, 129, 0.1); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
        <div style="text-align: center;">
            <img src="data:image/png;base64,{profile_img_base64}" alt="Profile" style="width: 70px; height: 70px; border-radius: 50%; border: 3px solid #0F4C81; box-shadow: 0 4px 12px rgba(15, 76, 129, 0.2); object-fit: cover;" />
        </div>
        <div style="text-align: center; margin-top: 12px;">
            <div style="font-size: 0.7em; color: #6B3200; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">Administrator</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.subheader("Student Assessment")

with st.sidebar.form("student_assessment_form", clear_on_submit=False):
    marital = st.selectbox("Marital Status", list(MARITAL_STATUS.keys()), index=None, placeholder="Select marital status", key="marital")
    application_mode = st.selectbox("Application Mode", list(APPLICATION_MODE.keys()), index=None, placeholder="Select application mode", key="application_mode")
    application_order = st.number_input("Application Order", min_value=0, max_value=9, value=None, step=1, placeholder="Enter application order")
    course = st.selectbox("Course", list(COURSE.keys()), index=None, placeholder="Select course", key="course")
    attendance = st.selectbox("Attendance", ["Daytime", "Evening"], index=None, placeholder="Select attendance", key="attendance")
    qualification = st.selectbox("Previous Qualification", list(QUALIFICATION.keys()), index=None, placeholder="Select previous qualification", key="qual")
    displaced = st.selectbox("Displaced", ["No", "Yes"], index=None, placeholder="Select displaced status", key="displaced")
    special = st.selectbox("Special Needs", list(SPECIAL_NEEDS.keys()), index=None, placeholder="Select special needs", key="special")
    gender = st.selectbox("Gender", ["Female", "Male"], index=None, placeholder="Select gender", key="gender")
    scholarship = st.selectbox("Scholarship Holder", ["No", "Yes"], index=None, placeholder="Select scholarship status", key="scholarship")
    international = st.selectbox("International", ["No", "Yes"], index=None, placeholder="Select international status", key="international")
    age_text = st.text_input("Age at Enrollment", placeholder="Enter age (18 or above)", key="age")

    predict_clicked = st.form_submit_button("Run Assessment", use_container_width=True, type="primary")

with st.sidebar.expander("Model Input Schema"):
    st.markdown("""
    **Required Features (in order):**
    1. Marital status
    2. Application mode
    3. Application order
    4. Course
    5. Attendance
    6. Previous qualification
    7. Displaced
    8. Special needs
    9. Gender
    10. Scholarship holder
    11. Age
    12. International
    """)

# Settings and Logout at the bottom of sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if st.sidebar.button("Settings", use_container_width=True, key="settings_btn"):
    st.session_state.show_settings = not st.session_state.get('show_settings', False)

if st.sidebar.button("Logout", use_container_width=True, type="secondary"):
    logout()

# Settings Panel (shown conditionally)
if st.session_state.get('show_settings', False):
    with st.sidebar.expander("Change Password", expanded=True):
        with st.form("change_password_form"):
            old_pass = st.text_input("Current Password", type="password", key="old_pass")
            new_pass = st.text_input("New Password", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass")
            
            if st.form_submit_button("Update Password", use_container_width=True):
                if new_pass != confirm_pass:
                    st.error("Passwords do not match")
                elif len(new_pass) < 8:
                    st.error("Password must be at least 8 characters")
                elif not any(c.isupper() for c in new_pass) or not any(c.isdigit() for c in new_pass):
                    st.error("Password must contain uppercase and numbers")
                else:
                    if db.change_password(st.session_state.username, old_pass, new_pass):
                        st.success("Password updated successfully")
                        st.session_state.show_settings = False
                    else:
                        st.error("Current password is incorrect")

st.markdown("## System Statistics")

# Get stats from database
stats = db.get_prediction_stats()
total_assessments = stats['total']
high_risk_cases = stats['high_risk']
low_risk_cases = stats['low_risk']

stat_col1, stat_col2, stat_col3 = st.columns(3)

with stat_col1:
    st.metric("Total Assessments", total_assessments)

with stat_col2:
    st.metric("High Risk Cases", high_risk_cases)

with stat_col3:
    st.metric("Low Risk Cases", low_risk_cases)

st.caption(
    f"History records loaded: {total_assessments}"
)


def map_risk(prob):
    if prob >= high_threshold:
        return "HIGH RISK", "critical"
    if prob >= moderate_threshold:
        return "MODERATE RISK", "warning"
    return "LOW RISK", "success"


tab1, tab2 = st.tabs(["Individual Assessment", "Cohort Triage (Admin)"])

with tab1:
    st.subheader("Individual Student Assessment")
    if predict_clicked:
        missing_fields = []

        if marital is None:
            missing_fields.append("Marital Status")
        if application_mode is None:
            missing_fields.append("Application Mode")
        if course is None:
            missing_fields.append("Course")
        if attendance is None:
            missing_fields.append("Attendance")
        if qualification is None:
            missing_fields.append("Previous Qualification")
        if displaced is None:
            missing_fields.append("Displaced")
        if special is None:
            missing_fields.append("Special Needs")
        if gender is None:
            missing_fields.append("Gender")
        if scholarship is None:
            missing_fields.append("Scholarship Holder")
        if international is None:
            missing_fields.append("International")

        if not age_text.strip():
            missing_fields.append("Age at Enrollment")
            age_value = None
        else:
            try:
                age_value = int(age_text)
            except ValueError:
                st.error("Age must be a whole number.")
                st.stop()

        # Removed grade validation

        if missing_fields:
            st.error(f"Please complete all required fields before running the assessment: {', '.join(missing_fields)}.")
            st.stop()

        if age_value < 18:
            st.error("Age must be 18 or above to run the assessment.")
            st.stop()

        application_mode_code = APPLICATION_MODE[application_mode]
        course_code = COURSE[course]
        attendance_code = 1 if attendance == "Daytime" else 0
        displaced_code = 1 if displaced == "Yes" else 0
        gender_code = 1 if gender == "Male" else 0
        scholarship_code = 1 if scholarship == "Yes" else 0
        international_code = 1 if international == "Yes" else 0

        input_data = pd.DataFrame({
            "Marital status": [MARITAL_STATUS[marital]],
            "Application mode": [application_mode_code],
            "Application order": [application_order],
            "Course": [course_code],
            "Daytime/evening attendance\t": [attendance_code],
            "Previous qualification": [QUALIFICATION[qualification]],
            "Displaced": [displaced_code],
            "Educational special needs": [SPECIAL_NEEDS[special]],
            "Gender": [gender_code],
            "Scholarship holder": [scholarship_code],
            "Age at enrollment": [age_value],
            "International": [international_code]
        })

        try:
            prob_dropout = float(model.predict_proba(input_data)[0][1])
            prob_graduate = 1 - prob_dropout
            risk_label, risk_type = map_risk(prob_dropout)

            priority_score = compute_priority_score(prob_dropout, age_value, SPECIAL_NEEDS[special])
            priority_band = classify_priority(priority_score)
            owner = intervention_owner(priority_band)

            # Save prediction to database
            prediction_id = db.save_prediction(
                age=age_value,
                marital_status=marital,
                course=course,
                application_mode=application_mode,
                attendance=attendance,
                qualification=qualification,
                gender=gender,
                displaced=displaced,
                special_needs=special,
                scholarship=scholarship,
                international=international,
                risk_probability=prob_dropout,
                risk_level=risk_label,
                priority_score=priority_score,
                priority_band=priority_band
            )
            
            # Refresh history from database
            st.session_state.prediction_history = db.get_all_predictions()

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Dropout Risk", f"{prob_dropout:.1%}")
            with k2:
                st.metric("Completion Probability", f"{prob_graduate:.1%}")
            with k3:
                st.metric("Risk Category", risk_label)
            with k4:
                st.metric("Priority Score", f"{priority_score:.1f}/100")

            if risk_type == "critical":
                st.markdown(f"<div class='risk-high'><strong>{risk_label}</strong><br>Immediate response required. Priority: {priority_band}</div>", unsafe_allow_html=True)
            elif risk_type == "warning":
                st.markdown(f"<div class='risk-moderate'><strong>{risk_label}</strong><br>Proactive intervention recommended. Priority: {priority_band}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='risk-low'><strong>{risk_label}</strong><br>Routine support pathway. Priority: {priority_band}</div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Student Context**")
                st.write(f"- Age: {age_value}")
                st.write(f"- Marital status: {marital}")
                st.write(f"- Course: {course}")
                st.write(f"- Special needs: {special}")
            with c2:
                st.markdown("**Intervention Routing**")
                st.write(f"- Priority band: {priority_band}")
                st.write(f"- Assigned owner: {owner}")
                st.write("- Suggested first action window: 24-72 hours" if priority_band in ["P1 - Immediate", "P2 - High"] else "- Suggested first action window: within 7 days")

            st.markdown("**Recommended Actions**")
            for idx, rec in enumerate(generate_recommendations(prob_dropout, age_value, MARITAL_STATUS[marital], SPECIAL_NEEDS[special]), 1):
                st.write(f"{idx}. {rec}")

        except Exception as e:
            st.error(f"Prediction error: {str(e)}")
    else:
        st.info("Use the left panel to enter student details, then click Run Assessment.")

    st.divider()
    st.subheader("Recent Assessments")
    
    if st.session_state.history_notice:
        st.markdown(
            f'''
            <div class="notice-success" role="status" aria-live="polite">
                <div class="notice-success-icon">✓</div>
                <div>
                    <p class="notice-success-title">{st.session_state.history_notice["title"]}</p>
                    <p class="notice-success-text">{st.session_state.history_notice["message"]}</p>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
        st.session_state.history_notice = None
    
    if st.session_state.prediction_history:
        hist_df = build_history_dataframe(st.session_state.prediction_history)
        history_view = hist_df.copy()
        if "_history_index" in history_view.columns:
            history_view = history_view.drop(columns=["_history_index"])
        if "timestamp" in history_view.columns:
            history_view["timestamp"] = history_view["timestamp"].fillna("")

        st.dataframe(history_view.head(10), width="stretch")

        button_col1, button_col2 = st.columns([1.5, 0.13])
        with button_col2:
            if not st.session_state.clear_timestamp_confirm:
                if st.button("Clear History", use_container_width=True):
                    st.session_state.clear_timestamp_confirm = True
                    st.rerun()
            else:
                st.caption("Are you sure you want to clear timestamp history?")
                confirm_col1, confirm_col2 = st.columns(2)
                with confirm_col1:
                    if st.button("Yes"):
                        db.clear_all_predictions()
                        st.session_state.prediction_history = []
                        st.session_state.clear_timestamp_confirm = False
                        st.session_state.history_notice = {
                            "title": "History cleared",
                            "message": "All recent assessment records have been removed.",
                        }
                        st.rerun()
                with confirm_col2:
                    if st.button("No"):
                        st.session_state.clear_timestamp_confirm = False
                        st.rerun()
    else:
        st.caption("No assessments yet.")


with tab2:
    st.subheader("Cohort Triage and Operations")
    uploaded = st.file_uploader(
        "Upload cohort CSV",
        type=["csv"],
        help="First 12 columns must follow model input order."
    )
    
    if uploaded:
        try:
            df_batch = pd.read_csv(uploaded)
            if len(df_batch.columns) < 12:
                st.error(f"Expected at least 12 columns, found {len(df_batch.columns)}")
            else:
                features = df_batch.iloc[:, :12].copy()
                probs = model.predict_proba(features.values)[:, 1]
    
                result_df = df_batch.copy()
                result_df["Dropout_Probability"] = probs
                result_df["Risk_Level"] = result_df["Dropout_Probability"].apply(lambda p: map_risk(float(p))[0])
                result_df["Priority_Score"] = result_df.apply(
                    lambda r: compute_priority_score(float(r["Dropout_Probability"]), float(r.iloc[10]), int(r.iloc[7])),
                    axis=1
                )
                result_df["Priority_Band"] = result_df["Priority_Score"].apply(classify_priority)
                result_df["Assigned_Owner"] = result_df["Priority_Band"].apply(intervention_owner)
    
                st.session_state.batch_results = result_df
    
                total = len(result_df)
                high_count = int((result_df["Dropout_Probability"] >= high_threshold).sum())
                mod_count = int(((result_df["Dropout_Probability"] >= moderate_threshold) & (result_df["Dropout_Probability"] < high_threshold)).sum())
                p1_count = int((result_df["Priority_Band"] == "P1 - Immediate").sum())
    
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Cohort Size", total)
                with k2:
                    st.metric("High Risk", f"{high_count} ({(high_count / total) * 100:.1f}%)")
                with k3:
                    st.metric("Moderate Risk", f"{mod_count} ({(mod_count / total) * 100:.1f}%)")
                with k4:
                    st.metric("Immediate Priority", p1_count)
    
                c1, c2 = st.columns(2)
                with c1:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.hist(result_df["Dropout_Probability"], bins=20, color=SDPS_PRIMARY, edgecolor=SDPS_BLACK)
                    ax.axvline(moderate_threshold, color=SDPS_SECONDARY, linestyle="--", label="Moderate threshold")
                    ax.axvline(high_threshold, color=SDPS_BLACK, linestyle="--", label="High threshold")
                    ax.set_facecolor(SDPS_SOFT_GRAY)
                    ax.set_title("Risk Probability Distribution")
                    ax.set_xlabel("Dropout Probability")
                    ax.set_ylabel("Students")
                    ax.legend()
                    st.pyplot(fig)
                with c2:
                    order = ["P1 - Immediate", "P2 - High", "P3 - Medium", "P4 - Routine"]
                    priority_counts = result_df["Priority_Band"].value_counts().reindex(order, fill_value=0)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.bar(priority_counts.index, priority_counts.values, color=[SDPS_PRIMARY, SDPS_SECONDARY, "#8d6e63", "#c7b299"])
                    ax.set_facecolor(SDPS_SOFT_GRAY)
                    ax.set_title("Operational Priority Queue")
                    ax.set_ylabel("Students")
                    ax.tick_params(axis="x", rotation=15)
                    st.pyplot(fig)
    
                st.markdown("**Triage Queue (highest priority first)**")
                triage = result_df.sort_values(by=["Priority_Score", "Dropout_Probability"], ascending=False)
                st.dataframe(triage.head(100), width="stretch", height=380)
    
                csv_data = triage.to_csv(index=False)
                triage_col1, triage_col2 = st.columns(2)
                with triage_col1:
                    st.download_button("Download Triage Plan", csv_data, "triage_plan.csv", "text/csv", use_container_width=True)
                with triage_col2:
                    if st.button("Clear Batch Results", use_container_width=True):
                        st.session_state.batch_results = None
                        st.success("Batch results cleared.")
                        st.rerun()
    
        except Exception as e:
            st.error(f"Batch processing error: {str(e)}")
    else:
        st.caption("Upload a cohort CSV to generate operational triage outputs.")
    
    
    
st.divider()
st.markdown("""
<div style='text-align:center; padding: 8px 0 18px 0; color: #6f6f6f; font-size: 0.95rem; line-height: 1.5;'>
<div style='font-weight: 700; color: #1f1f1f; margin-bottom: 4px;'>Student Dropout Risk Prediction System | SDPS</div>
Decision support for early intervention and retention strategy execution.
</div>
""", unsafe_allow_html=True)
