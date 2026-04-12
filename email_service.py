"""
email_service.py — Email Service
==================================
Handles sending password reset emails using:
  1. Flask-Mail (primary)
  2. Direct SMTP (fallback if Flask-Mail fails)

Usage:
  from email_service import EmailService
  email_service = EmailService(app, mail)
  msg = email_service.create_password_reset_email(user, reset_link)
  email_service.send_email(msg)
"""

import smtplib
import ssl
import time
from email.mime.text import MIMEText
from flask_mail import Message


class EmailService:
    """Handles all email sending with retry logic and SMTP fallback."""

    def __init__(self, app, mail):
        """
        Initialize with Flask app and Mail instance.

        Args:
            app:  Flask application instance.
            mail: Flask-Mail instance.
        """
        self.app    = app
        self.mail   = mail
        self.config = app.config

    # ==============================================================
    #   Send Email (with retries)
    # ==============================================================

    def send_email(self, msg, max_retries: int = 5) -> bool:
        """
        Send an email using Flask-Mail.
        Falls back to direct SMTP if all retries fail.

        Args:
            msg:         Flask-Mail Message object.
            max_retries: Number of retry attempts before fallback.

        Returns:
            True if email was sent successfully, False otherwise.
        """
        for attempt in range(max_retries):
            try:
                self.mail.send(msg)
                print(f"✅ Email sent (attempt {attempt + 1})")
                return True
            except Exception as e:
                print(f"⚠️  Flask-Mail attempt {attempt + 1} failed: {e}")
                time.sleep(3)

        print("❌ All Flask-Mail attempts failed → trying direct SMTP...")
        return self._send_direct_smtp(msg)

    # ==============================================================
    #   Direct SMTP Fallback
    # ==============================================================

    def _send_direct_smtp(self, msg) -> bool:
        """
        Fallback: send email via raw SMTP (tries ports 465 and 587).

        Args:
            msg: Flask-Mail Message object.

        Returns:
            True if sent successfully, False on failure.
        """
        try:
            # Build MIME message from Flask-Mail message
            mime_msg = MIMEText(msg.html or msg.body, 'html' if msg.html else 'plain')
            mime_msg['Subject'] = msg.subject
            mime_msg['From']    = self.config['MAIL_DEFAULT_SENDER']
            mime_msg['To']      = ', '.join(msg.recipients)

            # Try ports 465 (SSL) and 587 (STARTTLS)
            for port in [465, 587]:
                try:
                    if port == 465:
                        context = ssl.create_default_context()
                        server  = smtplib.SMTP_SSL(
                            self.config['MAIL_SERVER'], port,
                            context=context, timeout=60
                        )
                    else:
                        server = smtplib.SMTP(self.config['MAIL_SERVER'], port, timeout=60)
                        server.starttls()

                    server.login(self.config['MAIL_USERNAME'], self.config['MAIL_PASSWORD'])
                    server.send_message(mime_msg)
                    server.quit()
                    print(f"✅ Direct SMTP success on port {port}")
                    return True

                except Exception as e:
                    print(f"❌ SMTP port {port} failed: {e}")
                    continue

            return False

        except Exception as e:
            print(f"❌ Direct SMTP failed entirely: {e}")
            return False

    # ==============================================================
    #   Email Templates
    # ==============================================================

    def create_password_reset_email(self, user, reset_link: str) -> Message:
        """
        Create a styled HTML password reset email.

        Args:
            user:       User model instance (must have .name and .email).
            reset_link: Full URL for the password reset page.

        Returns:
            Flask-Mail Message object (call send_email() to send it).
        """
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            background:#f0f9ff;
            font-family:'Segoe UI',Tahoma,Arial,sans-serif;
        }}
        .wrapper {{ padding:40px 16px; }}
        .card {{
            background:#fff;
            border-radius:20px;
            max-width:560px;
            margin:0 auto;
            overflow:hidden;
            box-shadow:0 8px 40px rgba(14,165,233,0.12);
            border:1px solid #bae6fd;
        }}
        /* Header */
        .header {{
            background:linear-gradient(135deg,#0369a1,#0ea5e9,#38bdf8);
            padding:40px 32px 32px;
            text-align:center;
        }}
        .icon {{
            width:72px; height:72px;
            background:rgba(255,255,255,0.2);
            border-radius:20px;
            border:2px solid rgba(255,255,255,0.3);
            margin:0 auto 16px;
            display:block;
            font-size:48px;
            line-height:68px;
            text-align:center;
        }}
        .brand {{ color:rgba(255,255,255,0.85); font-size:12px; font-weight:600; letter-spacing:2.5px; text-transform:uppercase; margin-bottom:10px; }}
        .title {{ color:#fff; font-size:26px; font-weight:800; }}
        /* Body */
        .body {{ padding:36px 32px; }}
        .greeting {{ font-size:17px; font-weight:700; color:#0f172a; margin-bottom:12px; }}
        .message {{ font-size:15px; color:#475569; line-height:1.7; margin-bottom:28px; }}
        .btn-wrap {{ text-align:center; margin:28px 0; }}
        .btn {{
            display:inline-block;
            background:linear-gradient(135deg,#0369a1,#0ea5e9);
            color:#fff !important;
            text-decoration:none;
            font-size:16px; font-weight:700;
            padding:16px 44px;
            border-radius:50px;
        }}
        hr {{ border:none; border-top:1.5px solid #e0f2fe; margin:28px 0; }}
        .warning {{
            background:#fff7ed;
            border:1.5px solid #fed7aa;
            border-left:4px solid #f97316;
            border-radius:10px;
            padding:14px 16px;
            font-size:13px;
            color:#92400e;
        }}
        /* Footer */
        .footer {{
            background:#f8faff;
            border-top:1.5px solid #e0f2fe;
            padding:24px 32px;
            text-align:center;
        }}
        .footer-logo {{ font-size:15px; font-weight:800; color:#0369a1; margin-bottom:8px; }}
        .footer-text {{ font-size:12px; color:#94a3b8; }}
        .footer-text a {{ color:#0ea5e9; text-decoration:none; }}
        @media (max-width:600px) {{
            .body, .header {{ padding:24px 20px; }}
            .btn {{ padding:14px 32px; }}
        }}
    </style>
</head>
<body>
<div class="wrapper">
    <div class="card">
        <div class="header">
            <div class="icon">&#127891;</div>
            <div class="brand">AI Scholar Hunt</div>
            <h1 class="title">Password Reset Request 🔑</h1>
        </div>
        <div class="body">
            <p class="greeting">Hello, {user.name}! 👋</p>
            <p class="message">
                We received a request to reset your <strong>AI Scholar Hunt</strong> password.
                Click the button below to set a new password.
                This link is valid for <strong>1 hour</strong>.
            </p>
            <div class="btn-wrap">
                <a href="{reset_link}" class="btn">🔐 &nbsp; Reset My Password</a>
            </div>
            <hr>
            <div class="warning">
                ⚠️ &nbsp;<strong>Didn't request this?</strong>
                Just ignore this email — your account remains safe.
            </div>
        </div>
        <div class="footer">
            <div class="footer-logo">🎓 AI Scholar Hunt</div>
            <p class="footer-text">
                Helping students find scholarships worldwide.<br>
                Questions? <a href="mailto:aischolarhunt@gmail.com">aischolarhunt@gmail.com</a>
            </p>
        </div>
    </div>
    <p style="text-align:center;font-size:11px;color:#94a3b8;margin-top:20px;">
        © 2026 AI Scholar Hunt · Reset requested for your account.
    </p>
</div>
</body>
</html>"""

        plain_text = f"""
Password Reset — AI Scholar Hunt
=====================================
Hello {user.name},

We received a request to reset your AI Scholar Hunt password.

Reset link:
{reset_link}

This link expires in 1 hour.
Didn't request this? Just ignore this email — your account is safe.

AI Scholar Hunt Team
aischolarhunt@gmail.com
        """

        return Message(
            subject="🔑 Reset Your AI Scholar Hunt Password",
            recipients=[user.email],
            body=plain_text,
            html=html,
            sender=self.config['MAIL_DEFAULT_SENDER']
        )
