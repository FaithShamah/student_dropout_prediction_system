import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import re
import base64
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from dotenv import load_dotenv
from database import Database
from io import BytesIO
from utils.email_service import EmailService

email_service = EmailService()

warnings.filterwarnings("ignore")
load_dotenv()

SDPS_PRIMARY = "#0F4C81"   # Deep Indigo/Blue
SDPS_SECONDARY = "#008080" # Teal
SDPS_BLACK = "#1F2937"
SDPS_WHITE = "#FFFFFF"
SDPS_LIGHT = "#F3F4F6"
SDPS_SOFT_BLUE = "#E0E7FF"
SDPS_SOFT_TEAL = "#CCFBF1"
SDPS_SOFT_GRAY = "#F9FAFB"
SDPS_ACCENT = "#F59E0B"    # Amber/Gold accent
SDPS_DARK_BG = "#0B1120"
SDPS_DARK_SURFACE = "#111827"
SDPS_DARK_SURFACE_2 = "#1F2937"
SDPS_DARK_TEXT = "#E5E7EB"
SDPS_DARK_MUTED = "#94A3B8"
SDPS_DARK_BORDER = "#334155"

LOGO_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "logo__2_-removebg-preview.png")

moderate_threshold = 0.40
high_threshold = 0.70


def load_logo_base64():
    if not os.path.exists(LOGO_PATH):
        return ""

    with open(LOGO_PATH, "rb") as logo_file:
        return base64.b64encode(logo_file.read()).decode("utf-8")


def render_splash_screen():
    st.markdown(f"""
    <style>
    @keyframes sdpsFloat {{
        0%, 100% {{ transform: translateY(0) scale(1); }}
        50% {{ transform: translateY(-10px) scale(1.02); }}
    }}
    @keyframes sdpsPulse {{
        0%, 100% {{ opacity: 0.35; transform: scale(0.96); }}
        50% {{ opacity: 0.9; transform: scale(1); }}
    }}
    @keyframes sdpsProgress {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(100%); }}
    }}
    .sdps-splash {{
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px;
        background:
            radial-gradient(circle at 20% 20%, rgba(0, 128, 128, 0.28), transparent 30%),
            radial-gradient(circle at 80% 30%, rgba(15, 76, 129, 0.34), transparent 34%),
            linear-gradient(135deg, #07111f 0%, #0f172a 48%, #102f45 100%);
        overflow: hidden;
        position: relative;
    }}
    .sdps-splash::before,
    .sdps-splash::after {{
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        border-radius: 50%;
        filter: blur(2px);
        opacity: 0.18;
        animation: sdpsPulse 4s ease-in-out infinite;
    }}
    .sdps-splash::before {{
        left: -90px;
        bottom: -110px;
        background: {SDPS_ACCENT};
    }}
    .sdps-splash::after {{
        right: -120px;
        top: -100px;
        background: {SDPS_SECONDARY};
        animation-delay: 1s;
    }}
    .sdps-splash-card {{
        position: relative;
        z-index: 1;
        width: min(560px, 100%);
        text-align: center;
        padding: 44px 34px 34px;
        border: 1px solid rgba(255, 255, 255, 0.16);
        border-radius: 32px;
        background: rgba(15, 23, 42, 0.78);
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(18px);
        animation: sdpsFloat 5s ease-in-out infinite;
    }}
    .sdps-splash-logo {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 132px;
        height: 132px;
        margin-bottom: 18px;
        border-radius: 50%;
        border: 4px solid rgba(255, 255, 255, 0.82);
        background: #ffffff;
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.35);
    }}
    .sdps-splash-logo img {{
        width: 92px;
        height: 92px;
        object-fit: contain;
    }}
    .sdps-splash-kicker {{
        margin: 0 0 8px;
        color: {SDPS_ACCENT};
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }}
    .sdps-splash-title {{
        margin: 0;
        color: #ffffff;
        font-size: clamp(2.1rem, 7vw, 4.4rem);
        font-weight: 900;
        letter-spacing: -0.06em;
        line-height: 0.95;
    }}
    .sdps-splash-subtitle {{
        margin: 14px auto 0;
        max-width: 420px;
        color: #cbd5e1;
        font-size: 1.02rem;
        line-height: 1.55;
    }}
    .sdps-splash-loader {{
        position: relative;
        width: min(320px, 70%);
        height: 8px;
        margin: 28px auto 0;
        overflow: hidden;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.12);
    }}
    .sdps-splash-loader span {{
        position: absolute;
        inset: 0;
        border-radius: inherit;
        background: linear-gradient(90deg, {SDPS_SECONDARY}, {SDPS_ACCENT});
        animation: sdpsProgress 1.45s ease-in-out infinite;
    }}
    </style>
    <div class="sdps-splash">
        <div class="sdps-splash-card">
            <div class="sdps-splash-logo">
                {SDPS_LOGO_HTML or '<div style="font-size:2.4rem;font-weight:900;color:#fff;">SDPS</div>'}
            </div>
            <p class="sdps-splash-kicker">Student Dropout Prediction System</p>
            <p class="sdps-splash-subtitle">AI-assisted early warning dashboard for student retention and admission support.</p>
            <div class="sdps-splash-loader"><span></span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_auth_page(db):
    if not st.session_state.get("splash_done", False):
        st.session_state.splash_done = True
        render_splash_screen()
        time.sleep(3)
        st.rerun()

    SDPS_LOGO_HTML = f'<img src="data:image/png;base64,{load_logo_base64()}">' if load_logo_base64() else ""
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown(f"""
    <style>
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    .stApp {{
        background:
            radial-gradient(circle at 15% 15%, rgba(0, 128, 128, 0.22), transparent 28%),
            radial-gradient(circle at 85% 20%, rgba(245, 158, 11, 0.14), transparent 30%),
            linear-gradient(135deg, #07111f 0%, #0f172a 52%, #102f45 100%) !important;
    }}
    [data-testid="block-container"] {{
        width: min(420px, 100%) !important;
        max-width: 420px !important;
        padding-top: 8vh !important;
        padding-bottom: 5vh !important;
    }}
    [data-testid="stTextInput"] label p {{
        color: #e5e7eb !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }}
    .auth-brand {{
        text-align: center;
        margin-bottom: 22px;
    }}
    .auth-logo {{
        width: 80px;
        height: 80px;
        margin: 0 auto 14px;
        border-radius: 50%;
        border: 4px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28);
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #ffffff;
    }}
    .auth-logo img {{
        width: 60px;
        height: 60px;
        object-fit: contain;
    }}
    .auth-title {{
        margin: 0;
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 900;
        letter-spacing: -0.04em;
    }}
    .auth-subtitle {{
        margin: 8px 0 0;
        color: #cbd5e1;
        font-size: 0.85rem;
        line-height: 1.45;
    }}
    .auth-note {{
        margin: 18px 0 0;
        color: #94a3b8;
        font-size: 0.88rem;
        line-height: 1.5;
        text-align: center;
    }}
    .auth-note strong {{
        color: #e5e7eb;
    }}
    [data-testid="stForm"] {{
        background: rgba(22, 33, 51, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 24px !important;
        padding: 40px 30px 30px !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.5) !important;
        backdrop-filter: blur(16px) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    brand_html = f"""
    <div class="auth-brand">
        <div class="auth-logo">
            {SDPS_LOGO_HTML or '<div style="font-size:2rem;font-weight:900;color:#fff;">SDPS</div>'}
        </div>
        <h1 class="auth-title">Welcome</h1>
        <p class="auth-subtitle">Sign in to access the Student Dropout Risk Prediction System dashboard.</p>
    </div>
    """

    brand_html_create = f"""
    <div class="auth-brand">
        <div class="auth-logo">
            {SDPS_LOGO_HTML or '<div style="font-size:2rem;font-weight:900;color:#fff;">SDPS</div>'}
        </div>
        <h1 class="auth-title">Create an Account</h1>
        <p class="auth-subtitle">Join SDPS to start predicting student dropout risks.</p>
    </div>
    """

    if st.session_state.get("creation_success"):
        st.success("Account created successfully! Please sign in with your new credentials.")
        st.session_state.creation_success = False

    if st.session_state.auth_mode == "login":
        with st.form("user_login_form", clear_on_submit=False):
            st.markdown(brand_html, unsafe_allow_html=True)
            identifier = st.text_input("Username or Email", placeholder="Enter your username or email", key="login_identifier")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            if st.form_submit_button("Sign In", type="primary", use_container_width=True):
                verified, username, account_type, message = db.verify_user_or_admin(identifier.strip(), password)
                if verified:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.account_type = account_type
                    st.query_params["authenticated"] = username
                    st.query_params["account_type"] = account_type
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
                    
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create an Account", use_container_width=True, type="secondary"):
                st.session_state.auth_mode = "create"
                st.rerun()
        with col2:
            if st.button("Forgot Password?", use_container_width=True, type="secondary"):
                st.session_state.auth_mode = "forgot_password"
                st.rerun()
            
    elif st.session_state.auth_mode == "create":
        with st.form("user_create_form", clear_on_submit=False):
            st.markdown(brand_html_create, unsafe_allow_html=True)
            full_name = st.text_input("Full Name", placeholder="e.g., Jane Nakato", key="create_full_name")
            username = st.text_input("Username", placeholder="Choose a username", key="create_username")
            email = st.text_input("Email", placeholder="name@example.com", key="create_email")
            new_password = st.text_input("Password", type="password", placeholder="At least 8 characters", key="create_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="create_confirm_password")
            if st.form_submit_button("Create Account", type="primary", use_container_width=True):
                full_name = full_name.strip()
                username = username.strip()
                email = email.strip()

                if not full_name or not username or not email or not new_password or not confirm_password:
                    st.error("Please complete all fields.")
                elif len(username) < 3:
                    st.error("Username must be at least 3 characters.")
                elif not re.fullmatch(r"[A-Za-z0-9_.-]+", username):
                    st.error("Username can only contain letters, numbers, dots, underscores, and hyphens.")
                elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
                    st.error("Enter a valid email address.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif not any(char.isupper() for char in new_password) or not any(char.isdigit() for char in new_password):
                    st.error("Password must contain at least one uppercase letter and one number.")
                else:
                    created, create_message = db.create_user(username, email, new_password, full_name=full_name)
                    if created:
                        otp = email_service.generate_otp()
                        db.set_verification_code(email, otp)
                        email_service.send_verification_email(email, otp)
                        
                        st.session_state.creation_success = True
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(create_message)
                        
        st.write("")
        if st.button("Already have an account? Sign In", use_container_width=True, type="secondary"):
            st.session_state.auth_mode = "login"
            st.rerun()

    elif st.session_state.auth_mode == "verify_email":
        with st.form("verify_email_form", clear_on_submit=False):
            st.markdown(brand_html, unsafe_allow_html=True)
            st.info(f"Please enter the 6-digit verification code sent to your email.")
            otp_input = st.text_input("Verification Code", key="verify_otp")
            if st.form_submit_button("Verify Email", type="primary", use_container_width=True):
                if db.verify_email_code(st.session_state.verify_email_username, otp_input.strip()):
                    st.success("Email verified successfully! You can now log in.")
                    st.session_state.auth_mode = "login"
                    st.rerun()
                else:
                    st.error("Invalid verification code.")
        
        st.write("")
        if st.button("Back to Login", use_container_width=True, type="secondary"):
            st.session_state.auth_mode = "login"
            st.rerun()

    elif st.session_state.auth_mode == "forgot_password":
        with st.form("forgot_password_form", clear_on_submit=False):
            st.markdown(brand_html, unsafe_allow_html=True)
            st.info("Enter your email address to receive a password reset code.")
            reset_email = st.text_input("Email Address", key="reset_email_input")
            if st.form_submit_button("Send Reset Code", type="primary", use_container_width=True):
                user_data = db.get_user_by_email(reset_email.strip())
                if user_data:
                    otp = email_service.generate_otp()
                    db.set_verification_code(reset_email.strip(), otp)
                    email_sent = email_service.send_password_reset_email(reset_email.strip(), otp)
                    
                    if not email_sent:
                        st.error("Failed to send reset email. Please try again or contact support.")
                        st.stop()
                    
                    st.session_state.reset_email_target = reset_email.strip()
                    st.session_state.auth_mode = "reset_password"
                    st.rerun()
                else:
                    st.error("Email not found.")
        
        st.write("")
        if st.button("Back to Login", use_container_width=True, type="secondary"):
            st.session_state.auth_mode = "login"
            st.rerun()

    elif st.session_state.auth_mode == "reset_password":
        with st.form("reset_password_form", clear_on_submit=False):
            st.markdown(brand_html, unsafe_allow_html=True)
            st.info(f"Enter the code sent to {st.session_state.reset_email_target} and your new password.")
            reset_otp = st.text_input("Reset Code", key="reset_otp_input")
            new_pass = st.text_input("New Password", type="password", key="new_pass_input")
            if st.form_submit_button("Reset Password", type="primary", use_container_width=True):
                if len(new_pass) < 8 or not any(c.isupper() for c in new_pass) or not any(c.isdigit() for c in new_pass):
                    st.error("Password must be at least 8 chars, 1 uppercase, 1 number.")
                else:
                    success, msg = db.reset_password_with_code(st.session_state.reset_email_target, reset_otp.strip(), new_pass)
                    if success:
                        st.success("Password reset successfully! Please log in.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(msg)
                        
        st.write("")
        if st.button("Cancel", use_container_width=True, type="secondary"):
            st.session_state.auth_mode = "login"
            st.rerun()

    st.markdown(f"""
    <p class="auth-note">
        <strong>Admin Portal:</strong> Use your designated admin credentials to sign in.<br>
        <strong>New user:</strong> Create an account above, then sign in to access the dashboard.
    </p>
    """, unsafe_allow_html=True)


def render_ui_css(dark_mode: bool = True):
    if dark_mode:
        css_vars = f"""
        :root {{
            --sdps-bg: {SDPS_DARK_BG};
            --sdps-bg-2: #0f172a;
            --sdps-surface: {SDPS_DARK_SURFACE};
            --sdps-surface-2: {SDPS_DARK_SURFACE_2};
            --sdps-text: {SDPS_DARK_TEXT};
            --sdps-muted: {SDPS_DARK_MUTED};
            --sdps-border: {SDPS_DARK_BORDER};
            --sdps-input: #0f172a;
            --sdps-primary: {SDPS_PRIMARY};
            --sdps-secondary: {SDPS_SECONDARY};
            --sdps-accent: {SDPS_ACCENT};
            --sdps-danger: #ef4444;
            --sdps-warning: #f59e0b;
            --sdps-success: #10b981;
            --sdps-card-shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
        }}
        """
    else:
        css_vars = """
        :root {
            --sdps-bg: #f8fafc;
            --sdps-bg-2: #ffffff;
            --sdps-surface: #ffffff;
            --sdps-surface-2: #f1f5f9;
            --sdps-text: #111827;
            --sdps-muted: #64748b;
            --sdps-border: #dbe3ef;
            --sdps-input: #ffffff;
            --sdps-primary: #0F4C81;
            --sdps-secondary: #008080;
            --sdps-accent: #F59E0B;
            --sdps-danger: #dc2626;
            --sdps-warning: #d97706;
            --sdps-success: #059669;
            --sdps-card-shadow: 0 18px 50px rgba(15, 23, 42, 0.08);
        }
        """

    st.markdown(f"""
    <style>
    {css_vars}
    * {{
        scrollbar-color: var(--sdps-secondary) var(--sdps-surface-2);
        scrollbar-width: thin;
    }}
    *::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    *::-webkit-scrollbar-track {{
        background: var(--sdps-surface-2);
        border-radius: 999px;
    }}
    *::-webkit-scrollbar-thumb {{
        background: var(--sdps-secondary);
        border-radius: 999px;
    }}
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    .stApp {{
        background:
            radial-gradient(circle at 10% 10%, rgba(0, 128, 128, 0.13), transparent 28%),
            radial-gradient(circle at 90% 0%, rgba(245, 158, 11, 0.08), transparent 30%),
            linear-gradient(180deg, var(--sdps-bg) 0%, var(--sdps-bg-2) 100%) !important;
        color: var(--sdps-text) !important;
    }}
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 1.25rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: 0 !important;
    }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #07111f 0%, #0f2740 55%, #0b1120 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 12px 0 30px rgba(0, 0, 0, 0.22) !important;
    }}
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {{
        color: #e5e7eb !important;
    }}
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {{
        color: #94a3b8 !important;
        opacity: 0.8;
        -webkit-text-fill-color: #94a3b8 !important;
    }}
    [data-testid="stSidebar"] [data-baseweb="menu"] {{
        background-color: #111827 !important;
        color: #e5e7eb !important;
    }}
    [data-testid="stSidebar"] [role="option"] {{
        color: #e5e7eb !important;
        background-color: #111827 !important;
    }}
    [data-testid="stSidebar"] [role="option"]:hover {{
        color: #ffffff !important;
        background-color: rgba(15, 76, 129, 0.55) !important;
    }}
    .stTextInput > div > input,
    .stNumberInput > div > input,
    .stTextArea textarea,
    .stSelectbox [data-baseweb="select"] > div,
    .stMultiselect [data-baseweb="select"] > div {{
        background-color: var(--sdps-input) !important;
        color: var(--sdps-text) !important;
        -webkit-text-fill-color: var(--sdps-text) !important;
        caret-color: var(--sdps-text) !important;
        border: 1px solid var(--sdps-border) !important;
        box-shadow: none !important;
    }}
    .stTextInput > div > input::placeholder,
    .stNumberInput > div > input::placeholder {{
        color: var(--sdps-muted) !important;
        opacity: 0.82;
    }}
    .stMarkdown,
    .stMarkdown *,
    .stCaption,
    .stMetric *,
    .stDataFrame *,
    .stDataFrame table,
    .stDataFrame thead,
    .stDataFrame tbody {{
        color: var(--sdps-text) !important;
    }}
    [data-testid="stExpander"] {{
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] summary {{
        background: rgba(255, 255, 255, 0.05) !important;
        color: #e5e7eb !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        background: rgba(15, 76, 129, 0.4) !important;
        color: #ffffff !important;
    }}
    [data-testid="stExpander"] summary svg {{
        fill: #e5e7eb !important;
    }}
    [data-testid="stExpander"] summary p {{
        font-weight: 600 !important;
    }}
    .stDataFrame table,
    div[data-testid="stDataFrame"] {{
        background-color: rgba(17, 24, 39, 0.72) !important;
        border: 1px solid var(--sdps-border) !important;
        border-radius: 16px !important;
        overflow: hidden;
    }}
    div[data-testid="stDataFrame"] thead tr,
    div[data-testid="stDataFrame"] thead th {{
        background-color: var(--sdps-surface-2) !important;
        color: var(--sdps-muted) !important;
    }}
    div[data-testid="stDataFrame"] tbody tr:nth-child(even) {{
        background-color: rgba(255, 255, 255, 0.035) !important;
    }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(180deg, var(--sdps-surface) 0%, rgba(17, 24, 39, 0.86) 100%) !important;
        border: 1px solid var(--sdps-border) !important;
        border-radius: 18px !important;
        box-shadow: var(--sdps-card-shadow) !important;
        color: var(--sdps-text) !important;
        min-height: 96px !important;
    }}
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
        color: var(--sdps-muted) !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: #ffffff !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.06) 0%, rgba(255, 255, 255, 0.035) 100%) !important;
        border: 1px solid var(--sdps-border) !important;
        box-shadow: var(--sdps-card-shadow) !important;
    }}
    div[data-testid="stTabs"] button[role="tab"] {{
        color: var(--sdps-muted) !important;
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid transparent !important;
    }}
    div[data-testid="stTabs"] button[role="tab"]:hover {{
        color: #ffffff !important;
        background: rgba(15, 76, 129, 0.38) !important;
        border-color: rgba(255, 255, 255, 0.16) !important;
    }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        color: #ffffff !important;
        background: linear-gradient(135deg, {SDPS_SECONDARY} 0%, {SDPS_PRIMARY} 100%) !important;
        border-color: rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 10px 24px rgba(0, 128, 128, 0.22) !important;
    }}
    .stButton > button,
    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button,
    button[kind="primary"],
    button[kind="secondary"],
    button[kind="tertiary"] {{
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        min-height: 2.25rem !important;
        padding: 0.45rem 0.85rem !important;
        transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease, color 160ms ease !important;
    }}
    .stButton > button,
    div[data-testid="stButton"] > button,
    div[data-testid="stFormSubmitButton"] > button,
    button[kind="primary"] {{
        background: linear-gradient(135deg, {SDPS_SECONDARY} 0%, {SDPS_PRIMARY} 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 8px 20px rgba(0, 128, 128, 0.18) !important;
    }}
    .stButton > button:hover,
    div[data-testid="stButton"] > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #006666 0%, #0a3b66 100%) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.22) !important;
        box-shadow: 0 12px 28px rgba(0, 128, 128, 0.28) !important;
        transform: translateY(-1px) !important;
    }}
    button[kind="secondary"],
    button[kind="tertiary"] {{
        background: rgba(255, 255, 255, 0.08) !important;
        color: #e5e7eb !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        box-shadow: none !important;
    }}
    button[kind="secondary"]:hover,
    button[kind="tertiary"]:hover {{
        background: rgba(15, 76, 129, 0.38) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.22) !important;
        transform: translateY(-1px) !important;
    }}
    .stDownloadButton > button,
    .stFileUploader button {{
        background: linear-gradient(135deg, {SDPS_PRIMARY} 0%, {SDPS_SECONDARY} 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }}
    .stDownloadButton > button:hover,
    .stFileUploader button:hover {{
        background: linear-gradient(135deg, #0a3b66 0%, #006666 100%) !important;
        color: #ffffff !important;
    }}
    .hero-panel,
    .stat-card,
    .profile-card,
    .schema-card,
    .tab-content-wrapper,
    .risk-high,
    .risk-moderate,
    .risk-low,
    .insight-box,
    .notice-success {{
        background: linear-gradient(180deg, rgba(17, 24, 39, 0.9) 0%, rgba(15, 23, 42, 0.82) 100%) !important;
        border: 1px solid var(--sdps-border) !important;
        color: var(--sdps-text) !important;
        box-shadow: var(--sdps-card-shadow) !important;
    }}
    .hero-panel {{
        background: linear-gradient(135deg, rgba(15, 76, 129, 0.28), rgba(0, 128, 128, 0.18)) !important;
        margin-top: -1.5rem !important;
        padding-top: 20px !important;
        padding-bottom: 20px !important;
    }}
    .main-header {{
        color: #ffffff !important;
        text-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
    }}
    .subtitle,
    .hero-copy,
    .centered-caption,
    .form-instruction,
    .stat-label,
    .stat-note,
    .subsection-header {{
        color: var(--sdps-muted) !important;
    }}
    .subsection-header {{
        color: #ffffff !important;
    }}
    .stat-value {{
        color: #ffffff !important;
    }}
    .hero-chip {{
        background: linear-gradient(135deg, {SDPS_SECONDARY}, {SDPS_PRIMARY}) !important;
        color: #ffffff !important;
    }}
    .risk-high {{
        background: rgba(245, 158, 11, 0.14) !important;
        border-left: 5px solid {SDPS_ACCENT} !important;
        color: #fed7aa !important;
    }}
    .risk-moderate {{
        background: rgba(245, 158, 11, 0.10) !important;
        border-left: 5px solid #fbbf24 !important;
        color: #fde68a !important;
    }}
    .risk-low {{
        background: rgba(16, 185, 129, 0.10) !important;
        border-left: 5px solid #10b981 !important;
        color: #bbf7d0 !important;
    }}
    .notice-success {{
        background: rgba(16, 185, 129, 0.12) !important;
        border-left: 6px solid #10b981 !important;
        color: #d1fae5 !important;
    }}
    .notice-success-icon {{
        background: #10b981 !important;
        color: #ffffff !important;
    }}
    .notice-success-title,
    .notice-success-text {{
        color: #d1fae5 !important;
    }}
    div[data-testid="stFileUploader"] {{
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px dashed var(--sdps-border) !important;
        border-radius: 18px !important;
    }}
    div[data-testid="stFileUploaderDropzone"] {{
        background-color: transparent !important;
    }}
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] > div > span {{
        color: var(--sdps-text) !important;
    }}
    div[data-testid="stFileUploaderDropzone"] div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] small {{
        color: #1f2937 !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button span {{
        color: #ffffff !important;
    }}
    div[data-testid="stFileUploaderDropzone"] svg {{
        fill: #1f2937 !important;
    }}
    .stCheckbox label,
    .stCheckbox span {{
        color: var(--sdps-text) !important;
    }}
    .stAlert {{
        border-radius: 14px !important;
    }}
    .hero-logo {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 112px;
        height: 112px;
        overflow: hidden;
        border-radius: 50%;
        border: 4px solid #ffffff;
        background: #ffffff;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        margin: 0;
        box-sizing: border-box;
        flex-shrink: 0;
    }}
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }}
        .stats-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        }}
        div[data-testid="stTabs"] button[role="tab"] {{
            flex: 1 0 auto !important;
            width: 150px !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def style_plot(fig, ax):
    """Style chart to match the light dashboard theme."""
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')
    ax.tick_params(colors='#4A4A4A', labelsize=9)
    ax.title.set_color('#1F2937')
    ax.title.set_fontweight('bold')
    ax.title.set_fontsize(12)
    ax.xaxis.label.set_color('#4A4A4A')
    ax.yaxis.label.set_color('#4A4A4A')
    for spine in ax.spines.values():
        spine.set_color('#E5E7EB')
    ax.grid(True, axis='y', alpha=0.3, color='#E5E7EB', linestyle='--')
    ax.set_axisbelow(True)


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
    """Display splash, login, and account creation pages."""
    render_auth_page(get_database())

def logout():
    """Handle logout"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.account_type = "admin"
    st.session_state.splash_done = False
    for key in ["authenticated", "account_type"]:
        if key in st.query_params:
            del st.query_params[key]
    st.rerun()

# Fix 1: Use query parameters for persistent login across browser refreshes
auth_token = st.query_params.get("authenticated", None)
auth_account_type = st.query_params.get("account_type", "admin")
if auth_token:
    st.session_state.logged_in = True
    if "username" not in st.session_state:
        st.session_state.username = auth_token
    if "account_type" not in st.session_state:
        st.session_state.account_type = auth_account_type

# Check authentication status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "account_type" not in st.session_state:
    st.session_state.account_type = "admin"
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# Show login page if not authenticated
if not st.session_state.logged_in:
    st.set_page_config(
        page_title="SDPS Login",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    render_ui_css(True)
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
render_ui_css(st.session_state.get("dark_mode", True))

if "login_message" in st.session_state and st.session_state.login_message:
    st.toast(st.session_state.login_message, icon="✅")
    st.session_state.login_message = None

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, #E6F3FF 0%, #B8D9FF 100%);
        color: #1a2935;
    }}
    .block-container {{
        padding-top: 0.65rem;
        padding-bottom: 1rem;
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
        background-color: #E0E7FF !important;
        color: {SDPS_PRIMARY} !important;
    }}
    [data-testid="stSidebar"] .profile-card,
    [data-testid="stSidebar"] .schema-card {{
        background: rgba(255, 255, 255, 0.1) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
        transition: background-color 0.2s ease, transform 0.2s ease;
    }}
    [data-testid="stSidebar"] .profile-card:hover,
    [data-testid="stSidebar"] .schema-card:hover {{
        background: rgba(255, 255, 255, 0.16) !important;
        transform: translateY(-1px);
    }}
    [data-testid="stSidebar"] .schema-card table,
    [data-testid="stSidebar"] .schema-card th,
    [data-testid="stSidebar"] .schema-card td {{
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.22) !important;
    }}
    [data-testid="stSidebar"] .schema-card thead {{
        background: rgba(255, 255, 255, 0.18) !important;
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
    div[data-testid="stForm"] .stButton>button[kind="primary"],
    div[data-testid="stForm"] .stButton button,
    div[data-testid="stForm"] .stButton > button,
    div[data-testid="stForm"] button,
    div[data-testid="stForm"] button[data-baseweb="button"],
    .stButton>button[kind="primary"] {{
        background: linear-gradient(135deg, {SDPS_SECONDARY} 0%, {SDPS_PRIMARY} 100%) !important;
        background-color: {SDPS_SECONDARY} !important;
        color: #ffffff !important;
        border: 1px solid {SDPS_SECONDARY} !important;
        transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }}
    div[data-testid="stForm"] .stButton>button[kind="primary"]:hover,
    div[data-testid="stForm"] .stButton button:hover,
    div[data-testid="stForm"] .stButton > button:hover,
    div[data-testid="stForm"] button:hover,
    div[data-testid="stForm"] button[data-baseweb="button"]:hover,
    .stButton>button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #006666 0%, {SDPS_PRIMARY} 100%) !important;
        background-color: #006666 !important;
        border-color: {SDPS_PRIMARY} !important;
        box-shadow: 0 8px 18px rgba(0, 128, 128, 0.32) !important;
        transform: translateY(-1px);
    }}
    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div[role="slider"] {{
        background: {SDPS_SECONDARY};
    }}
    .hero-panel {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 6px;
        padding: 10px 24px;
        margin: 0 -0.5rem 12px -0.5rem;
        width: calc(100% + 1rem);
        max-width: none;
        background: linear-gradient(135deg, #ffffff 0%, #fff6ee 100%);
        border: 1px solid #eadbcc;
        border-radius: 22px;
        box-shadow: 0 14px 40px rgba(107, 50, 0, 0.08);
        flex-wrap: wrap;
        box-sizing: border-box;
    }}
    .hero-logo {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 112px;
        height: 112px;
        overflow: hidden;
        border-radius: 50%;
        border: 4px solid #ffffff;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        margin: 0;
        box-sizing: border-box;
        flex-shrink: 0;
    }}
    .hero-logo img {{
        height: 100%;
        width: 100%;
        max-width: 100%;
        object-fit: contain;
        flex-shrink: 0;
        border: 0;
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
        font-size: 2.65em;
        color: {SDPS_ACCENT};
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.04em;
        line-height: 1.04;
    }}
    .subtitle {{
        font-size: 1.06em;
        color: #7a5a43;
        margin-top: -1px;
        margin-bottom: 1px;
    }}
.hero-copy {{
        max-width: 760px;
        color: #5f5f5f;
        line-height: 1.25;
        text-align: center;
        margin: 0 auto;
    }}
    .hero-meta {{
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
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
        margin: 0 0 6px 0;
    }}
    .stats-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 0 0 12px 0;
    }}
    .stat-card {{
        background: #ffffff;
        border: 1px solid #eadbcc;
        border-radius: 16px;
        padding: 12px 14px;
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
        text-align: center;
    }}
    .stat-value {{
        color: #1f1f1f;
        font-size: 1.15rem;
        font-weight: 800;
        text-align: center;
    }}
    .stat-note {{
        display: block;
        color: #5f5f5f;
        font-size: 0.92rem;
        margin-top: 6px;
        line-height: 1.4;
        text-align: center;
    }}
    .risk-high {{ 
        background-color: #fff1e1; 
        border-left: 5px solid #E67E00;
        padding: 12px; 
        border-radius: 10px; 
        margin: 7px 0;
    }}
    .risk-moderate {{ 
        background-color: #f4e7db; 
        border-left: 5px solid #6B3200;
        padding: 12px; 
        border-radius: 10px; 
        margin: 7px 0;
    }}
    .risk-low {{ 
        background-color: #fafafa; 
        border-left: 5px solid #6B3200;
        padding: 12px; 
        border-radius: 10px; 
        margin: 7px 0;
    }}
    .insight-box {{
        background-color: #f2f2f2;
        border-left: 4px solid #E67E00;
        padding: 10px;
        border-radius: 10px;
        margin: 7px 0;
    }}
    .notice-success {{
        display: flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, #f4e7db 0%, #fff8ef 100%);
        border: 1px solid rgba(107, 50, 0, 0.18);
        border-left: 6px solid {SDPS_SECONDARY};
        color: #4f2400;
        border-radius: 14px;
        padding: 11px 13px;
        margin: 7px 0 10px 0;
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
        padding: 11px 12px;
        box-shadow: 0 6px 18px rgba(107, 50, 0, 0.06);
        min-height: 94px;
        text-align: center !important;
    }}
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
        color: #6B3200;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        margin: 0 auto !important;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        width: 100% !important;
    }}
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {{
        display: flex;
        justify-content: space-between;
        gap: 12px;
        width: 100%;
        background: linear-gradient(180deg, rgba(255, 252, 248, 0.98) 0%, rgba(246, 240, 233, 0.96) 100%);
        padding: 7px;
        margin-bottom: 12px;
        border-radius: 16px;
        border: 1px solid rgba(31, 111, 139, 0.12);
        position: relative;
        border-bottom: none !important;
        box-shadow: 0 10px 24px rgba(52, 72, 84, 0.08);
    }}
    
    /* Responsive design for mobile */
    @media (max-width: 768px) {{
        .hero-panel {{
            padding: 9px 18px;
            gap: 5px;
            margin: 0 -0.5rem 10px -0.5rem;
            width: calc(100% + 1rem);
            max-width: none;
            border-radius: 18px;
            text-align: center;
            justify-content: center;
        }}
        .hero-panel > div {{
            text-align: center;
        }}
        .hero-logo {{
            width: 96px;
            height: 96px;
        }}
        .hero-logo img {{
            width: 100% !important;
            height: 100% !important;
            object-fit: contain !important;
        }}
        .main-header {{
            font-size: 2.1rem;
            line-height: 1.08;
        }}
        .subtitle {{
            font-size: 0.98rem;
            margin-top: -3px;
            margin-bottom: 2px;
        }}
        .hero-copy {{
            font-size: 0.94rem;
            line-height: 1.25;
            text-align: center;
        }}
        .hero-meta {{
            flex: 0 0 auto;
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
            padding: 8px 14px;
            gap: 4px;
            margin: 0 -0.75rem 8px -0.75rem;
            width: calc(100% + 1.5rem);
            max-width: none;
        }}
        .hero-logo {{
            width: 84px;
            height: 84px;
        }}
        .hero-logo img {{
            width: 100% !important;
            height: 100% !important;
            object-fit: contain !important;
        }}
        .main-header {{
            font-size: 1.72rem;
            line-height: 1.08;
        }}
        .subtitle {{
            font-size: 0.9rem;
            margin-bottom: 1px;
        }}
        .hero-copy {{
            font-size: 0.88rem;
            line-height: 1.25;
            text-align: center;
        }}
        .hero-meta {{
            flex: 0 0 auto;
        }}
        .hero-meta img {{
            width: 82px !important;
            height: 82px !important;
        }}
        div[data-testid="stMetric"] {{
            min-height: 88px;
            padding: 9px 10px;
        }}
        div[data-testid="stMetric"] label {{
            font-size: 0.8rem !important;
        }}
        div[data-testid="stMetric"] div[aria-describedby] {{
            font-size: 0.92rem !important;
        }}
        div[data-testid="stMetric"] {{
            text-align: center !important;
        }}
        .stat-card {{
            padding: 12px 14px;
        }}
        [data-testid="stSidebar"] .schema-card {{
            padding: 10px;
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
        padding: 0.72rem 0.9rem;
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
    .centered-caption {{
        text-align: center;
        color: #6f6f6f;
        font-size: 0.85rem;
    }}
    .subsection-header {{
        font-size: 1.35em;
        font-weight: 700;
        color: #1f1f1f;
        text-align: center;
        margin: 0 0 11px 0;
    }}
    .form-instruction {{
        text-align: center;
        color: #5f5f5f;
        font-size: 0.95rem;
        margin-bottom: 10px;
        font-weight: normal;
    }}
    .stat-card {{
        background: #ffffff;
        border: 1px solid #eadbcc;
        border-radius: 16px;
        padding: 12px 14px;
        box-shadow: 0 8px 20px rgba(31, 111, 139, 0.05);
        text-align: center;
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
    
    /* Tab content container - centered and constrained */
    div[data-testid="stTabs"] [data-baseweb="tab-panel"] {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 6px 10px 0 10px;
    }}
    .stMarkdown p {{
        margin: 0 0 8px 0;
    }}
    .stMarkdown p:last-child {{
        margin-bottom: 0;
    }}
    div[data-testid="stDivider"] {{
        margin: 10px 0 !important;
    }}
    div[data-testid="stFileUploader"] {{
        margin-bottom: 10px !important;
    }}
    div[data-testid="stDataFrame"] {{
        margin-top: 8px !important;
    }}
    .tab-content-wrapper {{
        max-width: 1200px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
    }}
    .tab-content-wrapper .stSubheader,
    .tab-content-wrapper .stMarkdown,
    .tab-content-wrapper .stMetric,
    .tab-content-wrapper .stDataFrame {{
        text-align: center;
    }}
    .tab-content-wrapper .stForm {{
        text-align: left;
    }}
    /* Ensure text wraps properly on mobile */
    .tab-content-wrapper, .stDataFrame, .stDataFrame * {{
        word-wrap: break-word;
        word-break: break-word;
        white-space: normal;
        overflow-wrap: break-word;
    }}
    /* Mobile text containment */
    @media (max-width: 768px) {{
        div[data-testid="stTabs"] [data-baseweb="tab-panel"] {{
            padding: 0 8px;
        }}
        .stDataFrame, .stDataFrame * {{
            font-size: 0.85rem !important;
        }}
        .stMetric {{
            min-height: 90px !important;
        }}
        .stMetric label {{
            font-size: 0.8rem !important;
        }}
        .stMetric div[aria-describedby] {{
            font-size: 0.95rem !important;
        }}
    }}
    @media (max-width: 480px) {{
        div[data-testid="stTabs"] [data-baseweb="tab-panel"] {{
            padding: 0 6px;
        }}
        .stMarkdown p, .stCaption {{
            font-size: 0.9rem !important;
            line-height: 1.45;
        }}
        .stDataFrame {{
            font-size: 0.8rem !important;
        }}
    }}
    
    <!-- Dark-mode CSS overrides -->
    
    </style>
    """, unsafe_allow_html=True)

render_ui_css(st.session_state.get("dark_mode", True))

st.markdown(f"""
    <div class="hero-panel">
        <div class="hero-logo">
            {SDPS_LOGO_HTML}
        </div>
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; flex:0 1 auto; max-width: 760px; text-align: center; gap: 6px;">
            <h1 class="main-header">Student Dropout Risk Prediction System</h1>
            <p class="subtitle">AI-assisted early warning dashboard for admission support</p>
            <p class="hero-copy">Single student assessment, intake triage, and model intelligence in one view.</p>
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
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None
if "show_change_password" not in st.session_state:
    st.session_state.show_change_password = False
if "show_schema_page" not in st.session_state:
    st.session_state.show_schema_page = False

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

QUALIFICATION = {
    "UACE Certificate": 1,
    "Diploma": 42,
    "Bachelor's Degree": 2,
    "Master's Degree": 4,
    "Doctorate": 5,
    "Technical Certificate": 39
}

APPLICATION_MODE = {
    "Direct Entry (UACE)": 1,
    "Diploma Entry": 7,
    "Mature Age Entry": 39,
    "Transfer Student": 42,
    "Change of Course": 43,
    "Technical/Vocational Entry": 44,
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

def generate_recommendations(prob, age, marital):
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
    
    return recs

# ============================================================================
# MAIN APPLICATION INTERFACE
# ============================================================================
def compute_priority_score(prob, age, scholarship="No", attendance="Daytime"):
    """
    Calculate a composite priority score (0-100) based on multiple risk factors.
    
    Base score: dropout probability × 60 (max 60 points from probability)
    Age risk:   +10 if age < 18 or age >= 30 (non-traditional age)
    Scholarship: +10 if no scholarship holder
    Attendance: +10 if evening/nighttime attendance
    High risk:  +10 if probability already >= 0.70
    """
    base = prob * 60
    age_bonus = 10 if (age < 18 or age >= 30) else 0
    scholarship_bonus = 10 if scholarship == "No" else 0
    attendance_bonus = 10 if attendance in ["evening", "nighttime", "Evening", "Nighttime"] else 0
    high_risk_bonus = 10 if prob >= 0.70 else 0
    
    score = base + age_bonus + scholarship_bonus + attendance_bonus + high_risk_bonus
    return float(min(100, round(score, 2)))


def classify_priority(priority_score, risk_level):
    """
    Classify priority band ALIGNED with risk level to avoid contradictions.
    """
    if risk_level == "HIGH RISK":
        if priority_score >= 70:
            return "P1 - Immediate"
        return "P2 - High"
    elif risk_level == "MODERATE RISK":
        if priority_score >= 55:
            return "P2 - High"
        return "P3 - Medium"
    else:  # LOW RISK
        if priority_score >= 30:
            return "P3 - Medium"
        return "P4 - Routine"


def intervention_owner(priority_band):
    if priority_band == "P1 - Immediate":
        return "Retention Lead"
    if priority_band == "P2 - High":
        return "Academic Advisor"
    if priority_band == "P3 - Medium":
        return "Program Coordinator"
    return "Student Support Desk"

moderate_threshold = 0.40
high_threshold = 0.70

# ============================================================================
# SIDEBAR CONTENT
# ============================================================================

db = get_database()

# Check account type to load correct profile
account_type = st.session_state.get('account_type', 'admin')

# Load Profile
if account_type == 'user':
    user_profile = db.get_user_profile(st.session_state.username)
    profile_image_path = os.path.join(os.path.dirname(__file__), "..", "assets", "image.png")
else:
    user_profile = db.get_admin_profile(st.session_state.username)
    profile_image_path = os.path.join(os.path.dirname(__file__), "..", "assets", "image.png")

# Fallback logo
if os.path.exists(profile_image_path):
    with open(profile_image_path, "rb") as img_file:
        profile_img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
else:
    profile_img_base64 = load_logo_base64()  # Fallback to logo

# Professional Profile header
st.sidebar.markdown(f"""
    <div class="profile-card" style="padding: 20px 16px; background: rgba(255, 255, 255, 0.1); border-radius: 16px; margin-bottom: 20px; border: 1px solid rgba(255, 255, 255, 0.18); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
        <div style="text-align: center;">
            <img src="data:image/png;base64,{profile_img_base64}" alt="Profile" style="width: 70px; height: 70px; border-radius: 50%; border: 3px solid #0F4C81; box-shadow: 0 4px 12px rgba(15, 76, 129, 0.2); object-fit: cover;" />
        </div>
        <div style="text-align: center; margin-top: 12px;">
            <div style="font-size: 0.7em; color: #ffffff; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">{account_type.title()}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Settings and Logout at the bottom of sidebar
st.sidebar.markdown("<br>", unsafe_allow_html=True)

if st.sidebar.button("Settings", use_container_width=True, key="settings_btn"):
    st.session_state.show_settings = not st.session_state.get('show_settings', False)

# Settings Panel
if st.session_state.get('show_settings', False):
    with st.sidebar.expander("Change Password", expanded=True):
        with st.form("change_password_form"):
            old_pass = st.text_input("Current Password", type="password", placeholder="Current password", key="old_pass")
            new_pass = st.text_input("New Password", type="password", placeholder="New password", key="new_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm new password", key="confirm_pass")
            
            if st.form_submit_button("Update Password", use_container_width=True):
                if new_pass != confirm_pass:
                    st.error("Passwords do not match")
                elif len(new_pass) < 8:
                    st.error("Password must be at least 8 characters")
                elif not any(c.isupper() for c in new_pass) or not any(c.isdigit() for c in new_pass):
                    st.error("Password must contain uppercase and numbers")
                else:
                    # Call the correct method based on account type
                    if account_type == 'user':
                        success, msg = db.change_user_password(st.session_state.username, old_pass, new_pass)
                        if success:
                            st.success("Password updated successfully")
                        else:
                            st.error(msg)
                    else:
                        if db.change_password(st.session_state.username, old_pass, new_pass):
                            st.success("Password updated successfully")
                        else:
                            st.error("Current password is incorrect")

        st.sidebar.markdown("---")
        
        # Only admins see the Danger Zone
        if account_type == 'admin':
            st.sidebar.caption("Danger Zone")
            
            st.sidebar.markdown("**Manage Users**")
            all_users = db.get_all_users()
            if all_users:
                user_names = [u['username'] for u in all_users]
                selected_user = st.sidebar.selectbox("Select user to delete", ["-- Select User --"] + user_names)
                if selected_user != "-- Select User --":
                    if st.sidebar.button(f"Delete '{selected_user}'", type="primary", use_container_width=True):
                        if db.delete_user(selected_user):
                            st.sidebar.success(f"User '{selected_user}' deleted.")
                            st.rerun()
                        else:
                            st.sidebar.error("Could not delete user.")
            else:
                st.sidebar.caption("No regular users found.")
            
            st.sidebar.markdown("---")
            if not st.session_state.get("delete_history_confirm_sb"):
                if st.sidebar.button("Delete Prediction History", use_container_width=True, key="delete_history_btn_sb", type="secondary"):
                    st.session_state.delete_history_confirm_sb = True
                    st.rerun()
            else:
                st.sidebar.caption("Are you sure you want to delete all prediction history? This cannot be undone.")
                del_col1, del_col2 = st.sidebar.columns(2)
                with del_col1:
                    if st.sidebar.button("Yes, Delete", use_container_width=True, key="confirm_delete_yes_sb"):
                        db.clear_all_predictions()
                        st.session_state.prediction_history = []
                        st.session_state.delete_history_confirm_sb = False
                        st.session_state.history_notice = {
                            "title": "History deleted",
                            "message": "All prediction records have been permanently removed.",
                        }
                        st.rerun()
                with del_col2:
                    if st.sidebar.button("Cancel", use_container_width=True, key="confirm_delete_no_sb"):
                        st.session_state.delete_history_confirm_sb = False
                        st.rerun()



# Model Input Schema page navigation (button before Logout)
if st.sidebar.button("Model Input Schema", use_container_width=True, key="schema_page_btn"):
    st.session_state.show_schema_page = True
    st.rerun()

# Back button (shown only on schema page)
if st.session_state.get('show_schema_page', False):
    st.sidebar.markdown("---")
    if st.sidebar.button("← Back to Dashboard", use_container_width=True, key="back_to_dashboard_btn"):
        st.session_state.show_schema_page = False
        st.rerun()

if st.sidebar.button("Logout", use_container_width=True, type="secondary"):
    logout()

# Schema DataFrame definition (used for both sidebar and main page)
schema_df = pd.DataFrame({
    "Feature": [
        "Marital Status", "Application Mode", "Application Order", "Course", "Attendance",
        "Previous Qualification", "Gender", "Scholarship Holder", "Age at Enrollment", "International"
    ],
    "Description": [
        "Student's marital status at enrollment.",
        "Admission route through which the student entered the institution.",
        "First choice(0) to last choice(9) in the application preferences of the student.",
        "Academic program selected by the student.",
        "Study schedule of the student chosen on application.",
        "Highest qualification obtained before admission.",
        "Student's gender.",
        "Whether the student receives scholarship funding.",
        "Student's age when admitted.",
        "Whether the student is an international student."
    ],
    "Expected Values": [
        "Single, Married, Widower, Divorced, Facto Union, Legally Separated",
        "Direct Entry(UACE), Diploma Entry, Change of Course, Mature Age Entry, Transfer Student",
        "Integer (0-9)",
        "Computer Science/IT, Business & Management, Tourism, Nursing,Journalism & Communication,Agriculture, Marketing, Education, Business & Management",
        "Daytime, Evening",
        "UACE, Diploma,Technical certificate, Bachelor's Degree, Master's Degree, Doctorate",
        "Male, Female",
        "Yes, No",
        "Positive Integer",
        "Yes, No"
    ],
    "Example": [
        "Single", "Direct Entry", "1", "Computer Science", "Daytime", "Diploma", "Female", "No", "20", "No"
    ]
})

# Show schema page or continue to main dashboard
if st.session_state.get('show_schema_page', False):
    st.markdown('<div class="tab-content-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="subsection-header">Model Input Schema</p>', unsafe_allow_html=True)
    st.info("Ensure uploaded files contain these features and use the expected values.")
    st.dataframe(schema_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    # Don't show the rest of the dashboard when on schema page
    st.stop()

st.markdown('<p class="subsection-header">System Statistics</p>', unsafe_allow_html=True)

if st.session_state.get("refresh_stats"):
    stats = db.get_prediction_stats()
    st.session_state["refresh_stats"] = False
else:
    stats = db.get_prediction_stats()

total_assessments = stats['total']
high_risk_cases = stats['high_risk']
moderate_risk_cases = stats['moderate_risk']
low_risk_cases = stats['low_risk']

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.metric("Total Assessments", total_assessments)

with stat_col2:
    st.metric("High Risk Cases", high_risk_cases)

with stat_col3:
    st.metric("Moderate Risk Cases", moderate_risk_cases)

with stat_col4:
    st.metric("Low Risk Cases", low_risk_cases)

st.markdown(f'<p class="centered-caption">History records loaded: {total_assessments}</p>', unsafe_allow_html=True)


def map_risk(prob):
    if prob >= high_threshold:
        return "HIGH RISK", "critical"
    if prob >= moderate_threshold:
        return "MODERATE RISK", "warning"
    return "LOW RISK", "success"


tab1, tab2 = st.tabs(["Individual Assessment", "Cohort Triage"])

with tab1:
    st.markdown('<div class="tab-content-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="subsection-header">Individual Student Assessment</p>', unsafe_allow_html=True)

    st.markdown('<p class="form-instruction">Input student details to make predictions</p>', unsafe_allow_html=True)
    with st.form("student_assessment_form", clear_on_submit=True):
        marital = st.selectbox("Marital Status", list(MARITAL_STATUS.keys()), index=None, placeholder="Select marital status", key="marital")
        application_mode = st.selectbox("Application Mode", list(APPLICATION_MODE.keys()), index=None, placeholder="Select admission route", key="application_mode")
        application_order = st.number_input("Application Order", min_value=0, max_value=9, value=None, step=1, placeholder="e.g., 1")
        course = st.selectbox("Course", list(COURSE.keys()), index=None, placeholder="Select course", key="course")
        attendance = st.selectbox("Attendance", ["Daytime", "Evening"], index=None, placeholder="Select class schedule", key="attendance")
        qualification = st.selectbox("Previous Qualification", list(QUALIFICATION.keys()), index=None, placeholder="Select previous qualification", key="qual")
        gender = st.selectbox("Gender", ["Female", "Male"], index=None, placeholder="Select gender", key="gender")
        scholarship = st.selectbox("Scholarship Holder", ["No", "Yes"], index=None, placeholder="Select scholarship status", key="scholarship")
        international = st.selectbox("International", ["No", "Yes"], index=None, placeholder="Select international status", key="international")
        age_text = st.text_input("Age at Enrollment", placeholder="e.g., 18", key="age")

        predict_clicked = st.form_submit_button("Run Assessment", use_container_width=True, type="primary")

    if predict_clicked:
        missing_fields = []

        if marital is None:
            missing_fields.append("Marital Status")
        if application_mode is None:
            missing_fields.append("Application Mode")
        if application_order is None:
            missing_fields.append("Application Order")
        if course is None:
            missing_fields.append("Course")
        if attendance is None:
            missing_fields.append("Attendance")
        if qualification is None:
            missing_fields.append("Previous Qualification")
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
            "Gender": [gender_code],
            "Scholarship holder": [scholarship_code],
            "Age at enrollment": [age_value],
            "International": [international_code]
        })

        try:
            prob_dropout = float(model.predict_proba(input_data)[0][1])
            prob_graduate = 1 - prob_dropout
            risk_label, risk_type = map_risk(prob_dropout)

            priority_score = compute_priority_score(prob_dropout, age_value, scholarship=scholarship, attendance=attendance)
            priority_band = classify_priority(priority_score, risk_label)
            owner = intervention_owner(priority_band)

            st.session_state.last_prediction = {
                "prob_dropout": prob_dropout,
                "prob_graduate": prob_graduate,
                "risk_label": risk_label,
                "risk_type": risk_type,
                "priority_score": priority_score,
                "priority_band": priority_band,
                "owner": owner,
                "age_value": age_value,
                "marital": marital,
                "course": course,
            }
            result = db.save_prediction(
                age=age_value,
                marital_status=marital,
                course=course,
                application_mode=application_mode,
                application_order=application_order,
                attendance=attendance,
                qualification=qualification,
                gender=gender,
                scholarship=scholarship,
                international=international,
                risk_probability=prob_dropout,
                risk_level=risk_label,
                priority_score=priority_score,
                priority_band=priority_band,
            )
            if isinstance(result, tuple):
                saved, save_err = result
                if not saved:
                    st.warning(f"Prediction saved to session, but database save failed: {save_err}")
            else:
                if result == 0:
                    st.warning("Prediction saved to session, but database returned no ID.")
            st.session_state.prediction_history = load_prediction_history()
            st.session_state["refresh_stats"] = True
            st.rerun()

        except Exception as e:
            st.error(f"Prediction error: {str(e)}")

    if st.session_state.get("last_prediction"):
        data = st.session_state["last_prediction"]
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Dropout Risk", f"{data['prob_dropout']:.1%}")
        with k2:
            st.metric("Completion Probability", f"{data['prob_graduate']:.1%}")
        with k3:
            st.metric("Risk Category", data["risk_label"])
        with k4:
            st.metric("Priority Score", f"{data['priority_score']:.1f}/100")

        if data["risk_type"] == "critical":
            st.markdown(f"<div class='risk-high'><strong>{data['risk_label']}</strong><br>Immediate response required. Priority: {data['priority_band']}</div>", unsafe_allow_html=True)
        elif data["risk_type"] == "warning":
            st.markdown(f"<div class='risk-moderate'><strong>{data['risk_label']}</strong><br>Proactive intervention recommended. Priority: {data['priority_band']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='risk-low'><strong>{data['risk_label']}</strong><br>Routine support pathway. Priority: {data['priority_band']}</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Student Context**")
            st.write(f"- Age: {data['age_value']}")
            st.write(f"- Marital status: {data['marital']}")
            st.write(f"- Course: {data['course']}")
        with c2:
            st.markdown("**Intervention Routing**")
            st.write(f"- Priority band: {data['priority_band']}")
            st.write(f"- Assigned owner: {data['owner']}")
            st.write("- Suggested first action window: 24-72 hours" if data["priority_band"] in ["P1 - Immediate", "P2 - High"] else "- Suggested first action window: within 7 days")

        st.markdown("**Recommended Actions**")
        for idx, rec in enumerate(generate_recommendations(data["prob_dropout"], data["age_value"], MARITAL_STATUS[data["marital"]]), 1):
            st.write(f"{idx}. {rec}")

    st.divider()
    st.markdown('<p class="subsection-header">Recent Assessments</p>', unsafe_allow_html=True)
    
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
    else:
        st.caption("No assessments yet.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-content-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="subsection-header">Cohort Triage and Operations</p>', unsafe_allow_html=True)
    
    # UPDATED: Added "xlsx" to the accepted file types
    uploaded = st.file_uploader(
        "Upload cohort CSV or Excel",
        type=["csv", "xlsx"],
        help="Upload a CSV or Excel file with columns like 'age', 'gender', 'marital', 'course', etc."
    )
    
    if uploaded:
        try:
            # UPDATED: Logic to handle both CSV and Excel files
            if uploaded.name.endswith('.xlsx'):
                df_batch = pd.read_excel(uploaded)
            else:
                df_batch = pd.read_csv(uploaded)

            
            # ---------------------------------------------------------
            # AUTO-RENAME COLUMNS
            # ---------------------------------------------------------
            rename_map = {
                'age': 'Age at enrollment',
                'marital': 'Marital status',
                'application_mode': 'Application mode',
                'application_order': 'Application order',
                'course': 'Course',
                'attendance': 'Daytime/evening attendance',
                'qualification': 'Previous qualification',
                'gender': 'Gender',
                'scholarship': 'Scholarship holder',
                'international': 'International'
            }
            
            # Apply renaming (handling case and whitespace)
            df_batch.columns = [rename_map.get(str(col).strip().lower(), col) for col in df_batch.columns]
            
            # 1. Clean column names again just in case
            df_batch.columns = df_batch.columns.str.strip()

            # 2. Define the EXACT columns the model needs
            required_columns = [
                "Marital status",
                "Application mode",
                "Application order",
                "Course",
                "Daytime/evening attendance",
                "Previous qualification",
                "Gender",
                "Scholarship holder",
                "Age at enrollment",
                "International"
            ]

            # 3. Check if the CSV (now renamed) has all the required columns
            missing_cols = [col for col in required_columns if col not in df_batch.columns]
            if missing_cols:
                st.error(f"❌ Your file is missing these columns: {', '.join(missing_cols)}")
                st.info("ℹ️ Ensure your file has headers: age, gender, marital, course, etc.")
            else:
                # 4. Select only the columns we need
                features = df_batch[required_columns].copy()

                # ---------------------------------------------------------
                # MAP TEXT TO NUMBERS
                # ---------------------------------------------------------
                
                # 1. Marital Status
                features["Marital status"] = features["Marital status"].map(MARITAL_STATUS)

                # 2. Application Mode
                features["Application mode"] = features["Application mode"].map(APPLICATION_MODE)

                # 3. Application Order
                features["Application order"] = pd.to_numeric(features["Application order"], errors='coerce')

                # 4. Course
                features["Course"] = features["Course"].map(COURSE)

                # 5. Attendance
                attendance_map = {"Daytime": 1, "Evening": 0}
                features["Daytime/evening attendance"] = features["Daytime/evening attendance"].map(attendance_map)
    
               # 6. Qualification
                features["Previous qualification"] = features["Previous qualification"].map(QUALIFICATION)

                # 7. Gender
                gender_map = {"Male": 1, "Female": 0}
                features["Gender"] = features["Gender"].map(gender_map)

                # 8. Scholarship
                scholarship_map = {"Yes": 1, "No": 0}
                features["Scholarship holder"] = features["Scholarship holder"].map(scholarship_map)

                # 9. Age
                features["Age at enrollment"] = pd.to_numeric(features["Age at enrollment"], errors='coerce')

                # 10. International
                international_map = {"Yes": 1, "No": 0}
                features["International"] = features["International"].map(international_map)

                # Convert everything to float
                features = features.astype(float)

                # ── VALIDATE: catch unmapped values ──────────────────
                if features.isnull().any().any():
                    nan_cols = features.columns[features.isnull().any()].tolist()
                    bad_rows = features[features.isnull().any(axis=1)]
                    st.error(
                        f"❌ Some values could not be mapped to numbers. "
                        f"Problem columns: **{', '.join(nan_cols)}**"
                    )
                    st.info(
                        "ℹ️ Make sure your CSV uses the exact values shown in the "
                        "Model Input Schema (e.g., 'Daytime'/'Evening', 'Male'/'Female', "
                        "'Yes'/'No')."
                    )
                    with st.expander("Show rows with unmapped values"):
                        st.dataframe(bad_rows)
                    st.stop()
                # ─────────────────────────────────────────────────────
                
                # ---------------------------------------------------------
                # RUN PREDICTIONS
                # ---------------------------------------------------------
                
                probs = model.predict_proba(features.values)[:, 1]
    
                # Add results to the dataframe
                result_df = df_batch.copy()
                result_df["Dropout_Probability"] = probs
                result_df["Risk_Level"] = result_df["Dropout_Probability"].apply(lambda p: map_risk(float(p))[0])
                
                # Calculate Priority Score
                result_df["Priority_Score"] = result_df.apply(
                    lambda r: compute_priority_score(
                        float(r["Dropout_Probability"]), 
                        float(r["Age at enrollment"]),
                        scholarship=str(r.get("Scholarship holder", "No")),
                        attendance=str(r.get("Daytime/evening attendance", "Daytime"))
                    ),
                    axis=1
                )
                result_df["Priority_Band"] = result_df.apply(
                    lambda r: classify_priority(r["Priority_Score"], r["Risk_Level"]),
                    axis=1
                )
                result_df["Assigned_Owner"] = result_df["Priority_Band"].apply(intervention_owner)
    
                st.session_state.batch_results = result_df
    
                # --- Display Cohort Metrics ---
                total = len(result_df)
                high_count = int((result_df["Dropout_Probability"] >= high_threshold).sum())
                mod_count = int(((result_df["Dropout_Probability"] >= moderate_threshold) & (result_df["Dropout_Probability"] < high_threshold)).sum())
                low_count = int((result_df["Dropout_Probability"] < moderate_threshold).sum())
    
                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Cohort Size", total)
                with k2:
                    st.metric("High Risk", f"{high_count} ({(high_count / total) * 100:.1f}%)")
                with k3:
                    st.metric("Moderate Risk", f"{mod_count} ({(mod_count / total) * 100:.1f}%)")
                with k4:
                    st.metric("Low Risk", f"{low_count} ({(low_count / total) * 100:.1f}%)")
    
                 # --- Display Charts ---
                n_students = len(result_df)

                # ── Chart 1: Risk Probability Distribution ──────────
                fig, ax = plt.subplots(figsize=(10, 4))

                # Adaptive bin count: scale with data size
                n_bins = max(5, min(25, n_students // 3))

                # Colored risk zones behind the histogram
                ax.axvspan(0, moderate_threshold, alpha=0.08,
                           color='#10b981', label='Low Risk Zone')
                ax.axvspan(moderate_threshold, high_threshold, alpha=0.08,
                           color='#f59e0b', label='Moderate Risk Zone')
                ax.axvspan(high_threshold, 1.0, alpha=0.08,
                           color='#ef4444', label='High Risk Zone')

                ax.hist(
                    result_df["Dropout_Probability"],
                    bins=n_bins,
                    color=SDPS_PRIMARY,
                    edgecolor='white',
                    alpha=0.85,
                    zorder=3,
                )
                ax.axvline(moderate_threshold, color='#f59e0b',
                           linestyle='--', linewidth=1.5,
                           label=f'Moderate threshold ({moderate_threshold})')
                ax.axvline(high_threshold, color='#ef4444',
                           linestyle='--', linewidth=1.5,
                           label=f'High threshold ({high_threshold})')

                style_plot(fig, ax)
                ax.set_title("Risk Probability Distribution", fontsize=13, fontweight='bold', pad=10)
                ax.set_xlabel("Dropout Probability", fontsize=10)
                ax.set_ylabel("Students", fontsize=10)
                ax.legend(fontsize=8, loc='upper right')
                fig.tight_layout()
                st.pyplot(fig)

                # ── Chart 2: Operational Priority Queue ─────────────
                top_n = min(15, n_students)
                top_df = result_df.nlargest(top_n, "Priority_Score") \
                                  .sort_values("Priority_Score")

                labels = [f"Student {i+1}" for i in range(len(top_df))]

                bar_colors = []
                for _, row in top_df.iterrows():
                    if row["Risk_Level"] == "HIGH RISK":
                        bar_colors.append("#ef4444")
                    elif row["Risk_Level"] == "MODERATE RISK":
                        bar_colors.append("#f59e0b")
                    else:
                        bar_colors.append("#10b981")

                fig_height = max(4, top_n * 0.4)
                fig, ax = plt.subplots(figsize=(10, fig_height))
                bars = ax.barh(
                    labels,
                    top_df["Priority_Score"],
                    color=bar_colors,
                    edgecolor='white',
                    height=0.6,
                )

                # Score labels on the bars
                for bar, score in zip(bars, top_df["Priority_Score"]):
                    ax.text(
                        bar.get_width() + 1,
                        bar.get_y() + bar.get_height() / 2,
                        f'{score:.0f}',
                        va='center', fontsize=9,
                        fontweight='bold', color='#1F2937',
                    )

                ax.axvline(70, color='#ef4444', linestyle=':',
                           alpha=0.5, label='P1 threshold')
                ax.axvline(55, color="#2e0bf5", linestyle=':',
                           alpha=0.5, label='P2 threshold')

                style_plot(fig, ax)
                ax.set_title(f"Operational Priority Queue (Top {top_n})", fontsize=13, fontweight='bold', pad=10)
                ax.set_xlabel("Priority Score", fontsize=10)
                ax.set_xlim(0, 105)
                ax.legend(fontsize=8, loc='lower right')
                fig.tight_layout()
                st.pyplot(fig)

                # ── Chart 3: Average Dropout Risk by Course ─────────
                if "Course" in result_df.columns:
                    course_risk = (
                        result_df.groupby("Course")["Dropout_Probability"]
                        .mean()
                        .sort_values(ascending=True)
                    )

                    fig_height = max(4, len(course_risk) * 0.5)
                    fig, ax = plt.subplots(figsize=(10, fig_height))
                    course_colors = [
                        '#ef4444' if v >= high_threshold
                        else '#f59e0b' if v >= moderate_threshold
                        else '#10b981'
                        for v in course_risk.values
                    ]
                    ax.barh(
                        course_risk.index,
                        course_risk.values,
                        color=course_colors,
                        edgecolor='white',
                        height=0.6,
                    )
                    ax.axvline(moderate_threshold, color='#f59e0b',
                               linestyle='--', linewidth=1.5,
                               label='Moderate threshold')
                    ax.axvline(high_threshold, color='#ef4444',
                               linestyle='--', linewidth=1.5,
                               label='High threshold')

                    style_plot(fig, ax)
                    ax.set_title("Average Dropout Risk by Course", fontsize=13, fontweight='bold', pad=10)
                    ax.set_xlabel("Average Dropout Probability", fontsize=10)
                    ax.legend(fontsize=8)
                    fig.tight_layout()
                    st.pyplot(fig)
                else:
                    # Fallback: Age vs Risk scatter
                    fig, ax = plt.subplots(figsize=(10, 5))
                    scatter_colors = result_df["Risk_Level"].map(
                        {"HIGH RISK": "#ef4444",
                         "MODERATE RISK": "#f59e0b",
                         "LOW RISK": "#10b981"}
                    )
                    ax.scatter(
                        result_df["Age at enrollment"],
                        result_df["Dropout_Probability"],
                        c=scatter_colors, alpha=0.7,
                        edgecolors='white', s=80, zorder=3,
                    )
                    ax.axhline(moderate_threshold, color="#2b0e94",
                               linestyle='--', linewidth=1)
                    ax.axhline(high_threshold, color="#d11d1d",
                               linestyle='--', linewidth=1)
                    style_plot(fig, ax)
                    ax.set_title("Age vs Dropout Risk", fontsize=13, fontweight='bold', pad=10)
                    ax.set_xlabel("Age at Enrollment", fontsize=10)
                    ax.set_ylabel("Dropout Probability", fontsize=10)
                    fig.tight_layout()
                    st.pyplot(fig)

                # ── Chart 4: Risk Category Composition (Centered) ───
                risk_counts = result_df["Risk_Level"].value_counts()
                labels = risk_counts.index.tolist()
                sizes = risk_counts.values.tolist()
                colors_map = {
                    "HIGH RISK": "#ef4444",
                    "MODERATE RISK": "#f59e0b",
                    "LOW RISK": "#10b981",
                }
                chart_colors = [colors_map.get(l, "#94a3b8") for l in labels]

                # Use a square aspect ratio for the donut
                fig, ax = plt.subplots(figsize=(5, 5))
                wedges, texts, autotexts = ax.pie(
                    sizes,
                    labels=labels,
                    colors=chart_colors,
                    autopct='%1.1f%%',
                    startangle=90,
                    pctdistance=0.75,
                    wedgeprops=dict(width=0.4, edgecolor='white'),
                )
                for t in autotexts:
                    t.set_fontsize(10)
                    t.set_fontweight('bold')
                    t.set_color('#1F2937')
                for t in texts:
                    t.set_fontsize(10)
                    t.set_color('#4A4A4A')
                ax.set_title("Risk Category Composition", fontsize=13, fontweight='bold', pad=10)
                fig.patch.set_facecolor('#FFFFFF')
                fig.tight_layout()
                
                # Center the donut chart so it doesn't stretch across the whole page
                left, center, right = st.columns([1, 2, 1])
                with center:
                    st.pyplot(fig)
                    
                # --- Display Detailed Table ---
                st.markdown('<p class="subsection-header">Detailed Results</p>', unsafe_allow_html=True)
                st.dataframe(
                    result_df, 
                    use_container_width=True,
                    height=400
                )

                                # --- Save to Database Option ---
                st.markdown("---")
                save_to_db = st.checkbox("Save cohort results to database history", value=False)

                if save_to_db:
                    with st.spinner("Saving predictions to database..."):
                        saved_count = 0
                        for index, row in result_df.iterrows():
                            # Save each row using the existing database function
                            # We use 'result_df' because it still holds the original text values (e.g., "Male", "Married")
                            db.save_prediction(
                                age=int(row['Age at enrollment']),
                                marital_status=row['Marital status'],
                                course=row['Course'],
                                application_mode=row['Application mode'],
                                application_order=int(row['Application order']),
                                attendance=row['Daytime/evening attendance'], # This is currently text "Daytime" or "Evening" in result_df
                                qualification=row['Previous qualification'],
                                gender=row['Gender'],
                                scholarship=row['Scholarship holder'],
                                international=row['International'],
                                risk_probability=row['Dropout_Probability'],
                                risk_level=row['Risk_Level'],
                                priority_score=row['Priority_Score'],
                                priority_band=row['Priority_Band']
                            )
                            saved_count += 1
                        
                        st.success(f"Successfully saved {saved_count} records to the database.")
                        # Refresh the stats on the main dashboard
                        st.session_state["refresh_stats"] = True

                # --- Download Buttons ---
                
                # 1. Prepare CSV Data
                csv = result_df.to_csv(index=False).encode('utf-8')
                
                # 2. Prepare Excel Data
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    result_df.to_excel(writer, index=False, sheet_name='Cohort Results')
                excel_data = buffer.getvalue()

                # 3. Display Buttons Side-by-Side
                dl_col1, dl_col2 = st.columns(2)

                with dl_col1:
                    st.download_button(
                        label="Download as CSV",
                        data=csv,
                        file_name=f'cohort_triage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                        mime='text/csv',
                        use_container_width=True
                    )

                with dl_col2:
                    st.download_button(
                        label="Download as Excel",
                        data=excel_data,
                        file_name=f'cohort_triage_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        use_container_width=True
                    )

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown("""
<div style='text-align:center; padding: 8px 0 18px 0; color: #6f6f6f; font-size: 0.95rem; line-height: 1.5;'>
<div style='font-weight: 700; color: #1f1f1f; margin-bottom: 4px;'>Student Dropout Risk Prediction System | SDPS</div>
Decision support for early intervention and retention strategy execution.
</div>
""", unsafe_allow_html=True)
