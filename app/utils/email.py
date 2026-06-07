# # app/utils/email.py
# from app.config import settings
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# def send_transactional_email(to_email: str, subject: str, html_content: str) -> None:
#     try:
#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = subject
#         msg["From"] = settings.SMTP_FROM_EMAIL
#         msg["To"] = to_email
#         msg.attach(MIMEText(html_content, "html"))

#         with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#             server.starttls()
#             server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
#             server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
#     except Exception as e:
#         print(f"[Email Engine Error] {str(e)}")

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
def send_transactional_email(to_email: str, subject: str, html_content: str) -> None:
    """Sends a transactional HTML email using configured SMTP parameters, with local fallbacks."""
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    part = MIMEText(html_content, "html")
    message.attach(part)
    try:
        # Connect and authenticate
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
        server.quit()
        print(f"[Email Dispatch] Successfully sent email to {to_email} with subject: '{subject}'")
    except Exception as e:
        # Print fallback to stdout for offline development ease
        print(f"[Email Dispatch Error] Failed to send email via SMTP ({str(e)}). Logging to console instead:")
        print("=================== EMAIL FALLBACK ===================")
        print(f"Recipient: {to_email}")
        print(f"Subject  : {subject}")
        print("------------------- HTML Content --------------------")
        print(html_content.strip())
        print("======================================================")
