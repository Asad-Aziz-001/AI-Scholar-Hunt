"""
Email Service Module
Handles sending emails and password reset logic
Mobile + Web responsive email template
"""

import smtplib
import time
import ssl
from email.mime.text import MIMEText
from flask_mail import Message


class EmailService:
    """Handles email sending with retries and direct SMTP fallback"""

    def __init__(self, app, mail):
        self.app = app
        self.mail = mail
        self.config = app.config

    def send_email(self, msg, max_retries=5):
        """Send email using Flask-Mail with retry logic"""
        for attempt in range(max_retries):
            try:
                self.mail.send(msg)
                print("✅ Email sent successfully using Flask-Mail")
                return True
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {str(e)}")
                time.sleep(3)

        print("All Flask-Mail attempts failed → trying direct SMTP")
        return self._send_direct_smtp(msg)

    def _send_direct_smtp(self, msg):
        """Fallback direct SMTP send"""
        try:
            mime_msg = MIMEText(msg.html or msg.body, 'html' if msg.html else 'plain')
            mime_msg['Subject'] = msg.subject
            mime_msg['From'] = self.config['MAIL_DEFAULT_SENDER']
            mime_msg['To'] = ', '.join(msg.recipients)

            for port in [465, 587]:
                try:
                    if port == 465:
                        context = ssl.create_default_context()
                        server = smtplib.SMTP_SSL(
                            self.config['MAIL_SERVER'], port, context=context, timeout=60
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
                    print(f"Port {port} failed: {str(e)}")
                    continue

            return False
        except Exception as e:
            print(f"❌ Direct SMTP failed: {str(e)}")
            return False

    def create_password_reset_email(self, user, reset_link):
        """
        Password reset email — mobile + web (Gmail/Outlook) compatible.
        Icon fix: display:block + line-height (no flexbox — Gmail strips it).
        Removed: fallback link box (as requested).
        """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Reset Your Password</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body, table, td, a {{
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}
        body {{
            background-color: #f0f9ff;
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            margin: 0; padding: 0; width: 100%;
        }}
        .wrapper {{
            background-color: #f0f9ff;
            padding: 40px 16px;
            width: 100%;
        }}
        .email-card {{
            background: #ffffff;
            border-radius: 20px;
            max-width: 560px;
            margin: 0 auto;
            overflow: hidden;
            box-shadow: 0 8px 40px rgba(14,165,233,0.12);
            border: 1px solid #bae6fd;
        }}

        /* Header */
        .email-header {{
            background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 60%, #38bdf8 100%);
            padding: 40px 32px 32px;
            text-align: center;
        }}

        /*
          ICON FIX — Gmail/Yahoo web strip display:flex from divs.
          Solution: display:block + line-height for vertical centering.
          This works across Gmail web, Outlook, Apple Mail, mobile.
        */
        .header-icon {{
            width: 72px;
            height: 72px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            border: 2px solid rgba(255,255,255,0.3);
            margin: 0 auto 16px;
            display: block;
            font-size: 48px;
            line-height: 68px;
            text-align: center;
        }}
        .header-brand {{
            color: rgba(255,255,255,0.85);
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }}
        .header-title {{
            color: #ffffff;
            font-size: 26px;
            font-weight: 800;
            line-height: 1.25;
            margin: 0;
        }}

        /* Body */
        .email-body {{
            padding: 36px 32px;
        }}
        .greeting {{
            font-size: 17px;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 12px;
        }}
        .message {{
            font-size: 15px;
            color: #475569;
            line-height: 1.7;
            margin-bottom: 28px;
        }}

        /* CTA Button */
        .btn-wrapper {{
            text-align: center;
            margin: 28px 0;
        }}
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #0369a1, #0ea5e9);
            color: #ffffff !important;
            text-decoration: none;
            font-size: 16px;
            font-weight: 700;
            padding: 16px 44px;
            border-radius: 50px;
            letter-spacing: 0.3px;
            box-shadow: 0 6px 20px rgba(14,165,233,0.35);
        }}

        /* Divider */
        .divider {{
            border: none;
            border-top: 1.5px solid #e0f2fe;
            margin: 28px 0;
        }}

        /* Warning box */
        .warning-box {{
            background: #fff7ed;
            border: 1.5px solid #fed7aa;
            border-left: 4px solid #f97316;
            border-radius: 10px;
            padding: 14px 16px;
            font-size: 13px;
            color: #92400e;
            line-height: 1.6;
        }}
        .warning-box strong {{ color: #78350f; }}

        /* Footer */
        .email-footer {{
            background: #f8faff;
            border-top: 1.5px solid #e0f2fe;
            padding: 24px 32px;
            text-align: center;
        }}
        .footer-logo {{
            font-size: 15px;
            font-weight: 800;
            color: #0369a1;
            margin-bottom: 8px;
        }}
        .footer-text {{
            font-size: 12px;
            color: #94a3b8;
            line-height: 1.7;
        }}
        .footer-text a {{
            color: #0ea5e9;
            text-decoration: none;
        }}

        /* Mobile */
        @media only screen and (max-width: 600px) {{
            .wrapper {{ padding: 20px 12px; }}
            .email-header {{ padding: 28px 20px 24px; }}
            .header-title {{ font-size: 22px; }}
            .email-body {{ padding: 24px 20px; }}
            .btn {{ padding: 14px 32px; font-size: 15px; }}
            .email-footer {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
<div class="wrapper">
    <div class="email-card">

        <!-- Header -->
        <div class="email-header">
            <div class="header-icon">&#127891;</div>
            <div class="header-brand">AI Scholar Hunt</div>
            <h1 class="header-title">Password Reset<br>Request 🔑</h1>
        </div>

        <!-- Body -->
        <div class="email-body">
            <p class="greeting">Hello, {user.name}! 👋</p>
            <p class="message">
                We received a request to reset the password for your
                <strong>AI Scholar Hunt</strong> account. Click the button below
                to set a new password. This link is valid for <strong>1 hour</strong>.
            </p>

            <!-- CTA Button -->
            <div class="btn-wrapper">
                <a href="{reset_link}" class="btn">🔐 &nbsp; Reset My Password</a>
            </div>

            <hr class="divider">

            <!-- Warning -->
            <div class="warning-box">
                ⚠️ &nbsp;<strong>Didn't request this?</strong> No worries — just ignore this email.
                Your account remains safe and no changes will be made.
            </div>
        </div>

        <!-- Footer -->
        <div class="email-footer">
            <div class="footer-logo">🎓 AI Scholar Hunt</div>
            <p class="footer-text">
                Helping students find scholarships worldwide.<br>
                Questions? <a href="mailto:aischolarhunt@gmail.com">aischolarhunt@gmail.com</a>
            </p>
        </div>

    </div>
    <p style="text-align:center; font-size:11px; color:#94a3b8; margin-top:20px;">
        © 2026 AI Scholar Hunt · You received this because a reset was requested for your account.
    </p>
</div>
</body>
</html>"""

        text = f"""
Password Reset — AI Scholar Hunt
==================================

Hello {user.name},

We received a request to reset your AI Scholar Hunt password.

Reset your password here:
{reset_link}

This link expires in 1 hour.

Didn't request this? Just ignore this email — your account is safe.

Best regards,
AI Scholar Hunt Team
aischolarhunt@gmail.com
        """

        msg = Message(
            subject="🔑 Reset Your AI Scholar Hunt Password",
            recipients=[user.email],
            body=text,
            html=html,
            sender=self.config['MAIL_DEFAULT_SENDER']
        )

        return msg