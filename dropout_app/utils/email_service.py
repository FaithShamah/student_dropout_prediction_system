import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        self.is_configured = bool(self.smtp_server and self.smtp_user and self.smtp_password)

    def generate_otp(self, length=6):
        """Generate a random numeric OTP"""
        return ''.join(random.choices(string.digits, k=length))

    def send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Sends an email using SMTP or prints to console if not configured."""
        if not self.is_configured:
            print("\n" + "="*50)
            print("DEVELOPMENT MODE: MOCK EMAIL SENT")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print("-" * 50)
            print(html_body)
            print("="*50 + "\n")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to_email

            part = MIMEText(html_body, "html")
            msg.attach(part)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_user, to_email, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

    def send_verification_email(self, to_email: str, otp: str) -> bool:
        subject = "SDPS - Verify Your Email Address"
        body = f"""
        <html>
            <body>
                <h2>Welcome to SDPS</h2>
                <p>Please use the following 6-digit code to verify your email address:</p>
                <h3 style="color: #0F4C81; font-size: 24px; padding: 10px; background: #f3f4f6; display: inline-block; border-radius: 5px;">{otp}</h3>
                <p>If you didn't create an account, you can safely ignore this email.</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, body)

    def send_password_reset_email(self, to_email: str, otp: str) -> bool:
        subject = "SDPS - Password Reset Request"
        body = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>We received a request to reset your password. Use the following code to proceed:</p>
                <h3 style="color: #F59E0B; font-size: 24px; padding: 10px; background: #f3f4f6; display: inline-block; border-radius: 5px;">{otp}</h3>
                <p>If you did not request a password reset, please secure your account immediately.</p>
            </body>
        </html>
        """
        return self.send_email(to_email, subject, body)
