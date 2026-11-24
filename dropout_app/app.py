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

    try:
        from PIL import Image

        with Image.open(LOGO_PATH) as img:
            rgba = img.convert("RGBA")
            bbox = rgba.getbbox()
            if bbox:
                cropped = rgba.crop(bbox)
                side = max(cropped.size)
                square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
                offset = ((side - cropped.width) // 2, (side - cropped.height) // 2)
                square.paste(cropped, offset)
                buf = BytesIO()
                square.save(buf, format="PNG")
                return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        pass

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
        min-height: 88vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px;
        background-image:
            radial-gradient(circle at 20% 20%, rgba(0, 128, 128, 0.16), transparent 34%),
            radial-gradient(circle at 80% 30%, rgba(15, 76, 129, 0.18), transparent 36%);
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
        opacity: 0.14;
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
        border: 1px solid rgba(128, 128, 128, 0.25);
        border-radius: 32px;
        background: rgba(128, 128, 128, 0.08);
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18);
        backdrop-filter: blur(18px);
        color: inherit;
        animation: sdpsFloat 5s ease-in-out infinite;
    }}
    .sdps-splash-logo {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 140px;
        height: 140px;
        padding: 0;
        overflow: hidden;
        margin-bottom: 18px;
        border-radius: 50%;
        border: 3px solid rgba(15, 76, 129, 0.28);
        background: #ffffff;
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.20);
        box-sizing: border-box;
    }}
    .sdps-splash-logo img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
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
        color: inherit;
        font-size: clamp(2.1rem, 7vw, 4.4rem);
        font-weight: 900;
        letter-spacing: -0.06em;
        line-height: 0.95;
    }}
    .sdps-splash-subtitle {{
        margin: 14px auto 0;
        max-width: 420px;
        color: inherit;
        opacity: 0.82;
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
        background: rgba(128, 128, 128, 0.22);
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
                {SDPS_LOGO_HTML or '<div style="font-size:2.4rem;font-weight:900;color:#0F4C81;">SDPS</div>'}
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
        background-image:
            radial-gradient(circle at 15% 15%, rgba(0, 128, 128, 0.14), transparent 28%),
            radial-gradient(circle at 85% 20%, rgba(245, 158, 11, 0.08), transparent 30%);
    }}
    [data-testid="block-container"] {{
        width: min(420px, 100%) !important;
        max-width: 420px !important;
        padding-top: 8vh !important;
        padding-bottom: 5vh !important;
    }}
    [data-testid="stTextInput"] label p {{
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }}
    .auth-brand {{
        text-align: center;
        margin-bottom: 22px;
    }}
    .auth-logo {{
        width: 98px;
        height: 98px;
        padding: 0;
        margin: 0 auto 14px;
        border-radius: 50%;
        border: 3px solid rgba(15, 76, 129, 0.28);
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.16);
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        box-sizing: border-box;
    }}
    .auth-logo img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }}
    .auth-title {{
        margin: 0;
        color: inherit;
        font-size: 1.5rem;
        font-weight: 900;
        letter-spacing: -0.04em;
    }}
    .auth-subtitle {{
        margin: 8px 0 0;
        color: inherit;
        opacity: 0.80;
        font-size: 0.85rem;
        line-height: 1.45;
    }}
    .auth-note {{
        margin: 18px 0 0;
        color: inherit;
        opacity: 0.78;
        font-size: 0.88rem;
        line-height: 1.5;
        text-align: center;
    }}
    .auth-note strong {{
        color: inherit;
        opacity: 1;
    }}
    [data-testid="stForm"] {{
        background: rgba(128, 128, 128, 0.08) !important;
        border: 1px solid rgba(128, 128, 128, 0.24) !important;
        border-radius: 24px !important;
        padding: 40px 30px 30px !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.14) !important;
        backdrop-filter: blur(16px) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    brand_html = f"""
    <div class="auth-brand">
        <div class="auth-logo">
            {SDPS_LOGO_HTML or '<div style="font-size:2rem;font-weight:900;color:#0F4C81;">SDPS</div>'}
        </div>
        <h1 class="auth-title">Welcome</h1>
        <p class="auth-subtitle">Sign in to access the Student Dropout Risk Prediction System dashboard.</p>
    </div>
    """

    brand_html_create = f"""
    <div class="auth-brand">
        <div class="auth-logo">
            {SDPS_LOGO_HTML or '<div style="font-size:2rem;font-weight:900;color:#0F4C81;">SDPS</div>'}
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
    """Inject theme-adaptive CSS that keeps text legible in both light and dark themes."""
    st.markdown(f"""
    <style>
    * {{
        scrollbar-color: {SDPS_SECONDARY} rgba(128, 128, 128, 0.18);
        scrollbar-width: thin;
    }}
    *::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    *::-webkit-scrollbar-track {{
        background: rgba(128, 128, 128, 0.14);
        border-radius: 999px;
    }}
    *::-webkit-scrollbar-thumb {{
        background: {SDPS_SECONDARY};
        border-radius: 999px;
    }}
    [data-testid="stHeader"] {{
        background-color: transparent !important;
    }}
    .stApp {{
        background-image:
            radial-gradient(circle at 10% 10%, rgba(0, 128, 128, 0.10), transparent 28%),
            radial-gradient(circle at 90% 0%, rgba(245, 158, 11, 0.06), transparent 30%);
    }}
    .block-container {{
        padding-top: 0.75rem !important;
        padding-bottom: 1.25rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: 0 !important;
    }}
    [data-testid="stSidebar"] {{
        border-right: 1px solid rgba(128, 128, 128, 0.22) !important;
    }}
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"] {{
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    [data-testid="stSidebarCollapseButton"] button,
    button[data-testid="stExpandSidebarButton"],
    [data-testid="stExpandSidebarButton"] button {{
        visibility: visible !important;
        opacity: 1 !important;
        color: inherit !important;
        background: rgba(128, 128, 128, 0.16) !important;
        border: 1px solid rgba(128, 128, 128, 0.32) !important;
        border-radius: 10px !important;
        min-width: 2.25rem !important;
        min-height: 2.25rem !important;
        padding: 0.25rem !important;
        transition: background-color 150ms ease, border-color 150ms ease !important;
    }}
    [data-testid="stSidebarCollapseButton"] *,
    button[data-testid="stExpandSidebarButton"] *,
    [data-testid="stExpandSidebarButton"] * {{
        visibility: visible !important;
        opacity: 1 !important;
        color: inherit !important;
    }}
    [data-testid="stSidebarCollapseButton"] svg,
    button[data-testid="stExpandSidebarButton"] svg,
    [data-testid="stExpandSidebarButton"] svg {{
        fill: currentColor !important;
    }}
    [data-testid="stSidebarCollapseButton"] button:hover,
    button[data-testid="stExpandSidebarButton"]:hover,
    [data-testid="stExpandSidebarButton"] button:hover {{
        background: rgba(15, 76, 129, 0.24) !important;
        border-color: rgba(15, 76, 129, 0.48) !important;
    }}
    [data-testid="stSidebar"] .stMarkdown h2 {{
        font-size: 1.2em;
        font-weight: 600;
        margin-top: 0;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(128, 128, 128, 0.22);
    }}
    [data-testid="stSidebar"] .profile-card,
    [data-testid="stSidebar"] .schema-card {{
        background: rgba(128, 128, 128, 0.10) !important;
        border: 1px solid rgba(128, 128, 128, 0.24) !important;
        border-radius: 16px;
        color: inherit !important;
    }}
    [data-testid="stExpander"] {{
        border: 1px solid rgba(128, 128, 128, 0.24) !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] summary p {{
        font-weight: 600 !important;
    }}
    div[data-testid="stDataFrame"] {{
        border: 1px solid rgba(128, 128, 128, 0.24) !important;
        border-radius: 16px !important;
        overflow: hidden;
        margin-top: 8px !important;
    }}
    div[data-testid="stMetric"] {{
        background: rgba(128, 128, 128, 0.08) !important;
        border: 1px solid rgba(128, 128, 128, 0.24) !important;
        border-radius: 16px !important;
        padding: 12px 14px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
        color: inherit !important;
        min-height: 96px !important;
        text-align: center !important;
    }}
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {{
        color: inherit !important;
        opacity: 0.78;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }}
    div[data-testid="stMetric"] div[data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: inherit !important;
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
        background: rgba(128, 128, 128, 0.08) !important;
        padding: 7px;
        margin-bottom: 12px;
        border-radius: 16px;
        border: 1px solid rgba(128, 128, 128, 0.22) !important;
        border-bottom: none !important;
        position: relative;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
    }}
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
    div[data-testid="stTabs"] button[role="tab"] {{
        color: inherit !important;
        opacity: 0.80;
        font-weight: 700;
        border-radius: 12px;
        background: transparent !important;
        border: 1px solid transparent !important;
        flex: 1;
        justify-content: center;
        padding: 0.72rem 0.9rem;
        white-space: nowrap;
        box-shadow: none !important;
        text-decoration: none !important;
        outline: none !important;
        transition: background-color 160ms ease, color 160ms ease, box-shadow 160ms ease, border-color 160ms ease, transform 160ms ease;
    }}
    div[data-testid="stTabs"] button[role="tab"] * {{
        color: inherit !important;
    }}
    div[data-testid="stTabs"] button[role="tab"]:hover {{
        color: inherit !important;
        opacity: 1;
        background: rgba(15, 76, 129, 0.16) !important;
        border-color: rgba(15, 76, 129, 0.30) !important;
    }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        color: #ffffff !important;
        opacity: 1;
        background: linear-gradient(135deg, {SDPS_SECONDARY} 0%, {SDPS_PRIMARY} 100%) !important;
        border-color: rgba(255, 255, 255, 0.18) !important;
        box-shadow: 0 10px 24px rgba(0, 128, 128, 0.22) !important;
    }}
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] * {{
        color: #ffffff !important;
    }}
    div[data-testid="stTabs"] [data-baseweb="tab-panel"] {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 6px 10px 0 10px;
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
    button[kind="primary"],
    button[kind="primaryFormSubmit"],
    button[data-testid^="stBaseButton-primary"],
    div[data-testid="stFormSubmitButton"] > button,
    .stDownloadButton > button,
    .stFileUploader button {{
        background: linear-gradient(135deg, {SDPS_SECONDARY} 0%, {SDPS_PRIMARY} 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 8px 20px rgba(0, 128, 128, 0.18) !important;
    }}
    button[kind="primary"] *,
    button[kind="primaryFormSubmit"] *,
    button[data-testid^="stBaseButton-primary"] *,
    div[data-testid="stFormSubmitButton"] > button *,
    .stDownloadButton > button *,
    .stFileUploader button * {{
        color: #ffffff !important;
    }}
    button[kind="primary"]:hover,
    button[kind="primaryFormSubmit"]:hover,
    button[data-testid^="stBaseButton-primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    .stDownloadButton > button:hover,
    .stFileUploader button:hover {{
        background: linear-gradient(135deg, #006666 0%, #0a3b66 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 12px 28px rgba(0, 128, 128, 0.28) !important;
        transform: translateY(-1px) !important;
    }}
    button[kind="secondary"],
    button[kind="tertiary"],
    button[data-testid^="stBaseButton-secondary"],
    button[data-testid^="stBaseButton-tertiary"] {{
        background: rgba(128, 128, 128, 0.12) !important;
        color: inherit !important;
        border: 1px solid rgba(128, 128, 128, 0.28) !important;
        box-shadow: none !important;
    }}
    button[kind="secondary"] *,
    button[kind="tertiary"] *,
    button[data-testid^="stBaseButton-secondary"] *,
    button[data-testid^="stBaseButton-tertiary"] * {{
        color: inherit !important;
    }}
    button[kind="secondary"]:hover,
    button[kind="tertiary"]:hover,
    button[data-testid^="stBaseButton-secondary"]:hover,
    button[data-testid^="stBaseButton-tertiary"]:hover {{
        background: rgba(15, 76, 129, 0.18) !important;
        color: inherit !important;
        border-color: rgba(15, 76, 129, 0.42) !important;
        transform: translateY(-1px) !important;
    }}
    .hero-panel,
    .stat-card,
    .profile-card,
    .schema-card,
    .insight-box,
    .notice-success {{
        background: rgba(128, 128, 128, 0.08) !important;
        border: 1px solid rgba(128, 128, 128, 0.24) !important;
        color: inherit !important;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
    }}
    .hero-panel {{
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 6px;
        padding: 16px 24px;
        margin: 0 0 14px 0;
        width: 100%;
        border-radius: 22px !important;
        background: linear-gradient(135deg, rgba(15, 76, 129, 0.14), rgba(0, 128, 128, 0.10)) !important;
        box-sizing: border-box;
    }}
    .main-header {{
        font-size: 2.35em;
        font-weight: 900;
        margin: 0;
        letter-spacing: -0.04em;
        line-height: 1.08;
        color: inherit !important;
    }}
    .subtitle,
    .hero-copy,
    .centered-caption,
    .form-instruction,
    .stat-label,
    .stat-note {{
        color: inherit !important;
        opacity: 0.80;
    }}
    .subtitle {{
        font-size: 1.04em;
        margin: 0;
    }}
    .hero-copy {{
        max-width: 760px;
        line-height: 1.35;
        text-align: center;
        margin: 0 auto;
    }}
    .centered-caption {{
        text-align: center;
        font-size: 0.85rem;
    }}
    .form-instruction {{
        text-align: center;
        font-size: 0.95rem;
        margin-bottom: 10px;
    }}
    .subsection-header {{
        font-size: 1.35em;
        font-weight: 700;
        color: inherit !important;
        text-align: center;
        margin: 0 0 11px 0;
    }}
    .stat-value {{
        color: inherit !important;
    }}
    .hero-chip {{
        background: linear-gradient(135deg, {SDPS_SECONDARY}, {SDPS_PRIMARY}) !important;
        color: #ffffff !important;
    }}
    .risk-high {{
        background: rgba(239, 68, 68, 0.14) !important;
        border: 1px solid rgba(239, 68, 68, 0.30) !important;
        border-left: 5px solid #ef4444 !important;
        padding: 12px 14px;
        border-radius: 10px;
        margin: 7px 0;
        color: inherit !important;
    }}
    .risk-moderate {{
        background: rgba(245, 158, 11, 0.14) !important;
        border: 1px solid rgba(245, 158, 11, 0.30) !important;
        border-left: 5px solid #f59e0b !important;
        padding: 12px 14px;
        border-radius: 10px;
        margin: 7px 0;
        color: inherit !important;
    }}
    .risk-low {{
        background: rgba(16, 185, 129, 0.14) !important;
        border: 1px solid rgba(16, 185, 129, 0.30) !important;
        border-left: 5px solid #10b981 !important;
        padding: 12px 14px;
        border-radius: 10px;
        margin: 7px 0;
        color: inherit !important;
    }}
    .notice-success {{
        background: rgba(16, 185, 129, 0.12) !important;
        border-left: 6px solid #10b981 !important;
        padding: 11px 13px;
        color: inherit !important;
    }}
    .notice-success-icon {{
        background: #10b981 !important;
        color: #ffffff !important;
    }}
    .notice-success-title,
    .notice-success-text {{
        color: inherit !important;
    }}
    div[data-testid="stFileUploader"] {{
        border: 1px dashed rgba(128, 128, 128, 0.38) !important;
        border-radius: 18px !important;
        margin-bottom: 10px !important;
    }}
    div[data-testid="stDivider"] {{
        margin: 10px 0 !important;
    }}
    .tab-content-wrapper {{
        max-width: 1200px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
    }}
    .tab-content-wrapper .stForm {{
        text-align: left;
    }}
    .stAlert {{
        border-radius: 14px !important;
    }}
    .hero-logo {{
        display: flex;
        justify-content: center;
        align-items: center;
        width: 128px;
        height: 128px;
        padding: 0;
        overflow: hidden;
        border-radius: 50%;
        border: 3px solid rgba(15, 76, 129, 0.28);
        background: #ffffff;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.14);
        margin: 0;
        box-sizing: border-box;
        flex-shrink: 0;
    }}
    .hero-logo img {{
        height: 100%;
        width: 100%;
        max-width: 100%;
        object-fit: cover;
        display: block;
        flex-shrink: 0;
        border: 0;
    }}
    @media (max-width: 768px) {{
        .block-container {{
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }}
        .hero-panel {{
            padding: 12px 16px;
        }}
        .hero-logo {{
            width: 108px;
            height: 108px;
        }}
        .main-header {{
            font-size: 1.95rem;
        }}
        .stats-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
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
        }}
    }}
    @media (max-width: 480px) {{
        .hero-logo {{
            width: 92px;
            height: 92px;
        }}
        .main-header {{
            font-size: 1.65rem;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)


def style_plot(fig, ax):
    """Style chart with an explicit light card palette so labels stay readable in all themes."""
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FAFAFA')
    ax.tick_params(colors='#1F2937', labelsize=9)
    ax.title.set_color('#1F2937')
    ax.title.set_fontweight('bold')
    ax.title.set_fontsize(12)
    ax.xaxis.label.set_color('#1F2937')
    ax.yaxis.label.set_color('#1F2937')
    for spine in ax.spines.values():
        spine.set_color('#CBD5E1')
    ax.grid(True, axis='y', alpha=0.35, color='#CBD5E1', linestyle='--')
    ax.set_axisbelow(True)
    legend = ax.get_legend()
    if legend is not None:
        legend.get_frame().set_facecolor('#FFFFFF')
        legend.get_frame().set_edgecolor('#CBD5E1')
        for text in legend.get_texts():
            text.set_color('#1F2937')


SDPS_LOGO_BASE64 = load_logo_base64()
SDPS_LOGO_HTML = (
    f'<img src="data:image/png;base64,{SDPS_LOGO_BASE64}" alt="SDPS logo" '
    'style="height:100%; width:100%; object-fit:contain; display:block;" />'
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
if "show_assessments_page" not in st.session_state:
    st.session_state.show_assessments_page = False
if "show_about_page" not in st.session_state:
    st.session_state.show_about_page = False

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
    """Generate advisory support suggestions (not assumptions about individual students)."""
    recs = []

    if prob >= 0.7:
        recs.extend([
            "Conduct a confidential student check-in with an academic advisor",
            "Review academic progress and attendance records together",
            "Assess possible financial or personal challenges",
            "Refer the student to appropriate counseling, mentoring, or financial support services",
            "Follow up regularly on the student's progress"
        ])
    elif prob >= 0.4:
        recs.extend([
            "Conduct a proactive confidential student check-in",
            "Review academic progress and course attendance",
            "Assess possible financial, scheduling, or personal challenges",
            "Refer the student to peer mentoring, tutoring, or support services if helpful",
            "Follow up on the student's progress during the semester"
        ])
    else:
        recs.extend([
            "Continue standard academic advising and campus engagement",
            "Review academic progress and attendance during routine check-ins",
            "Keep support services accessible if needs arise"
        ])

    if age >= 30:
        recs.append("Explore flexible scheduling options to support work-life-study balance")
    if marital in [2, 4, 5, 6]:
        recs.append("Discuss whether family or work commitments require additional flexibility")

    return recs


def render_about_sdps_content():
    """Render shared overview, technology stack, support actions, and responsible-use content."""
    st.markdown("""
**1. System Overview & Problem Addressed**
- **What SDPS does:** The Student Dropout Risk Prediction System (SDPS) provides early-warning risk estimates for individual students or uploaded intake cohorts to help staff prioritize timely academic and pastoral support.
- **Problem addressed:** Many students disengage before challenges are noticed. Early risk screening helps institutions spot potential risk factors at admission or enrollment and offer proactive support.
- **Intended users:** Academic advisors, admissions teams, program coordinators, and student support staff.
- **How it works:** Staff enter 10 enrollment and demographic attributes (or upload a CSV/Excel cohort sheet). The model outputs an estimated dropout probability, a risk band (`LOW`, `MODERATE`, or `HIGH`), and a composite priority score to help organize follow-up outreach.

**2. Model & Technology Stack**
- **Model:** **Decision Tree classification** — a transparent, rule-based machine learning model that learns step-by-step decision rules from historical student enrollment patterns to estimate dropout risk.
- **Technology stack:** **Python**, **Decision Tree classification**, **Scikit-learn**, **Pandas**, **NumPy**, **Streamlit**, **Render**, and **Supabase**.

**3. Possible Student Support Actions (Advisory)**
- Conduct a confidential student check-in.
- Review academic progress and attendance.
- Assess possible financial or personal challenges.
- Refer the student to appropriate support services.
- Follow up on the student's progress.

**4. Privacy & Responsible Use Notice**
- **Confidentiality:** Student records and prediction results must remain strictly confidential and accessible only to authorized staff.
- **Decision support only:** Predictions are probabilistic indicators, not final verdicts about any student's ability or future.
- **Fairness:** Students must never be judged, penalized, or denied admission or academic opportunities based solely on a model prediction.
- **Human oversight:** Qualified staff must always apply human judgment and contextual review before initiating any intervention.
""")

# ============================================================================
# MAIN APPLICATION INTERFACE
# ============================================================================
def compute_priority_score(prob, age, scholarship="No", attendance="Daytime"):
    """
    Calculate a composite priority score (0-100) based on multiple risk factors.
    
    Base score: dropout probability Ã— 60 (max 60 points from probability)
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
    <div class="profile-card" style="padding: 20px 16px; background: rgba(128, 128, 128, 0.10); border-radius: 16px; margin-bottom: 20px; border: 1px solid rgba(128, 128, 128, 0.24); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);">
        <div style="text-align: center;">
            <img src="data:image/png;base64,{profile_img_base64}" alt="Profile" style="width: 84px; height: 84px; border-radius: 50%; border: 3px solid #0F4C81; box-shadow: 0 4px 12px rgba(15, 76, 129, 0.2); object-fit: cover;" />
        </div>
        <div style="text-align: center; margin-top: 12px;">
            <div style="font-size: 0.72em; color: inherit; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">{account_type.title()}</div>
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
    st.session_state.show_assessments_page = False
    st.session_state.show_about_page = False
    st.rerun()

# Back button (shown only on schema page)
if st.session_state.get('show_schema_page', False):
    st.sidebar.markdown("---")
    if st.sidebar.button("← Back to Dashboard", use_container_width=True, key="back_to_dashboard_btn"):
        st.session_state.show_schema_page = False
        st.session_state.show_assessments_page = False
        st.session_state.show_about_page = False
        st.rerun()

if st.sidebar.button("Recent Assessments", use_container_width=True, key="assessments_page_btn"):
    st.session_state.show_assessments_page = True
    st.session_state.show_schema_page = False
    st.session_state.show_about_page = False
    st.rerun()

# Back button (shown only on assessments page)
if st.session_state.get('show_assessments_page', False):
    st.sidebar.markdown("---")
    if st.sidebar.button("← Back to Dashboard", use_container_width=True, key="back_to_dashboard_btn_2"):
        st.session_state.show_assessments_page = False
        st.session_state.show_schema_page = False
        st.session_state.show_about_page = False
        st.rerun()

if st.sidebar.button("About SDPS", use_container_width=True, key="about_page_btn"):
    st.session_state.show_about_page = True
    st.session_state.show_schema_page = False
    st.session_state.show_assessments_page = False
    st.rerun()

# Back button (shown only on About SDPS page)
if st.session_state.get('show_about_page', False):
    st.sidebar.markdown("---")
    if st.sidebar.button("← Back to Dashboard", use_container_width=True, key="back_to_dashboard_btn_3"):
        st.session_state.show_about_page = False
        st.session_state.show_schema_page = False
        st.session_state.show_assessments_page = False
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

# Show About SDPS page
if st.session_state.get('show_about_page', False):
    st.markdown('<div class="tab-content-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="subsection-header">About SDPS — System Overview, Model & Responsible Use</p>', unsafe_allow_html=True)
    render_about_sdps_content()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Show schema page or continue to main dashboard
if st.session_state.get('show_schema_page', False):
    st.markdown('<div class="tab-content-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="subsection-header">Model Input Schema</p>', unsafe_allow_html=True)
    st.info("Ensure uploaded files contain these features and use the expected values.")
    st.dataframe(schema_df, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    # Don't show the rest of the dashboard when on schema page
    st.stop()

# Show assessments page
if st.session_state.get('show_assessments_page', False):
    st.markdown('<div class="tab-content-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="subsection-header">Recent Assessments</p>', unsafe_allow_html=True)
    
    if st.session_state.prediction_history:
        hist_df = build_history_dataframe(st.session_state.prediction_history)
        history_view = hist_df.copy()
        if "_history_index" in history_view.columns:
            history_view = history_view.drop(columns=["_history_index"])
        if "timestamp" in history_view.columns:
            history_view["timestamp"] = history_view["timestamp"].fillna("")
        st.dataframe(history_view, use_container_width=True)
    else:
        st.caption("No assessments yet.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download buttons for assessments
    st.markdown('<div class="tab-content-wrapper">', unsafe_allow_html=True)
    st.markdown('<p class="subsection-header">Download Assessments</p>', unsafe_allow_html=True)
    
    if st.session_state.prediction_history:
        hist_df_full = build_history_dataframe(st.session_state.prediction_history)
        if "_history_index" in hist_df_full.columns:
            hist_df_full = hist_df_full.drop(columns=["_history_index"])
        if "timestamp" in hist_df_full.columns:
            hist_df_full["timestamp"] = hist_df_full["timestamp"].fillna("")
        
        csv = hist_df_full.to_csv(index=False).encode('utf-8')
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            hist_df_full.to_excel(writer, index=False, sheet_name='Assessments')
        excel_data = buffer.getvalue()
        
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f'recent_assessments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv',
                use_container_width=True
            )
        with dl_col2:
            st.download_button(
                label="Download as Excel",
                data=excel_data,
                file_name=f'recent_assessments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )
    st.markdown('</div>', unsafe_allow_html=True)
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

        age_value = None
        age_valid = True
        if not age_text.strip():
            missing_fields.append("Age at Enrollment")
        else:
            try:
                age_value = int(age_text)
            except ValueError:
                age_valid = False
                st.error("Age must be a whole number.")

        if missing_fields:
            st.error(f"Please complete all required fields before running the assessment: {', '.join(missing_fields)}.")
        elif age_valid and age_value < 18:
            st.error("Age must be 18 or above to run the assessment.")
        elif age_valid:
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
            st.markdown(
                f"<div class='risk-high'><strong>{data['risk_label']}</strong> (Priority: {data['priority_band']})<br>"
                "Higher estimated dropout risk — early advisor outreach is suggested to explore student support options. "
                "This is an early-warning indicator to guide support, not a final judgment on the student.</div>",
                unsafe_allow_html=True,
            )
        elif data["risk_type"] == "warning":
            st.markdown(
                f"<div class='risk-moderate'><strong>{data['risk_label']}</strong> (Priority: {data['priority_band']})<br>"
                "Moderate estimated dropout risk — a proactive check-in and progress review may be helpful. "
                "This indicator supports early outreach rather than a final assessment.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='risk-low'><strong>{data['risk_label']}</strong> (Priority: {data['priority_band']})<br>"
                "Lower estimated dropout risk — continue routine academic support and standard progress monitoring.</div>",
                unsafe_allow_html=True,
            )

        st.caption("Decision-support indicator only: human assessment by advisors or academic staff is required before taking any action.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Student Context**")
            st.write(f"- Age: {data['age_value']}")
            st.write(f"- Marital status: {data['marital']}")
            st.write(f"- Course: {data['course']}")
        with c2:
            st.markdown("**Intervention Routing**")
            st.write(f"- Priority band: {data['priority_band']}")
            st.write(f"- Suggested support contact: {data['owner']}")
            st.write("- Suggested follow-up window: 24-72 hours" if data["priority_band"] in ["P1 - Immediate", "P2 - High"] else "- Suggested follow-up window: within 7 days")

        st.markdown("**Suggested Support Actions (Advisory Only)**")
        st.caption("Possible next steps for human review — not assumptions about an individual student:")
        for idx, rec in enumerate(generate_recommendations(data["prob_dropout"], data["age_value"], MARITAL_STATUS[data["marital"]]), 1):
            st.write(f"{idx}. {rec}")

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

                # â”€â”€ VALIDATE: catch unmapped values â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
                # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
                
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
                st.caption("Cohort predictions are early-warning decision-support indicators; human review is required before taking any action.")
    
                 # --- Display Charts ---
                n_students = len(result_df)

                # â”€â”€ Chart 1: Risk Probability Distribution â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

                ax.set_title("Risk Probability Distribution", fontsize=13, fontweight='bold', pad=10)
                ax.set_xlabel("Dropout Probability", fontsize=10)
                ax.set_ylabel("Students", fontsize=10)
                ax.legend(fontsize=8, loc='upper right')
                style_plot(fig, ax)
                fig.tight_layout()
                st.pyplot(fig)

                # â”€â”€ Chart 2: Operational Priority Queue â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

                ax.set_title(f"Operational Priority Queue (Top {top_n})", fontsize=13, fontweight='bold', pad=10)
                ax.set_xlabel("Priority Score", fontsize=10)
                ax.set_xlim(0, 105)
                ax.legend(fontsize=8, loc='lower right')
                style_plot(fig, ax)
                fig.tight_layout()
                st.pyplot(fig)

                # â”€â”€ Chart 3: Average Dropout Risk by Course â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

                    ax.set_title("Average Dropout Risk by Course", fontsize=13, fontweight='bold', pad=10)
                    ax.set_xlabel("Average Dropout Probability", fontsize=10)
                    ax.legend(fontsize=8)
                    style_plot(fig, ax)
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
                    ax.set_title("Age vs Dropout Risk", fontsize=13, fontweight='bold', pad=10)
                    ax.set_xlabel("Age at Enrollment", fontsize=10)
                    ax.set_ylabel("Dropout Probability", fontsize=10)
                    style_plot(fig, ax)
                    fig.tight_layout()
                    st.pyplot(fig)

                # â”€â”€ Chart 4: Risk Category Composition (Centered) â”€â”€â”€
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
                ax.set_title("Risk Category Composition", fontsize=13, fontweight='bold', pad=10, color='#1F2937')
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
<div style='text-align:center; padding: 8px 0 18px 0; color: inherit; opacity: 0.78; font-size: 0.95rem; line-height: 1.5;'>
<div style='font-weight: 700; color: inherit; opacity: 1; margin-bottom: 4px;'>Student Dropout Risk Prediction System | SDPS</div>
Decision support for early student intervention • Student data is confidential and human review is required.
</div>
""", unsafe_allow_html=True)
