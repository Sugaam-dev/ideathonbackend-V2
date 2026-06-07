

# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from app.config import settings
# def send_transactional_email(to_email: str, subject: str, html_content: str) -> None:
#     """Sends a transactional HTML email using configured SMTP parameters, with local fallbacks."""
#     message = MIMEMultipart("alternative")
#     message["Subject"] = subject
#     message["From"] = settings.SMTP_FROM_EMAIL
#     message["To"] = to_email
#     part = MIMEText(html_content, "html")
#     message.attach(part)
#     try:
#         # Connect and authenticate
#         server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
#         server.starttls()
#         server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
#         server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
#         server.quit()
#         print(f"[Email Dispatch] Successfully sent email to {to_email} with subject: '{subject}'")
#     except Exception as e:
#         # Print fallback to stdout for offline development ease
#         print(f"[Email Dispatch Error] Failed to send email via SMTP ({str(e)}). Logging to console instead:")
#         print("=================== EMAIL FALLBACK ===================")
#         print(f"Recipient: {to_email}")
#         print(f"Subject  : {subject}")
#         print("------------------- HTML Content --------------------")
#         print(html_content.strip())
#         print("======================================================")


import smtplib
import re
import queue
import threading
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
# Thread-safe in-memory email task queue
email_queue = queue.Queue()
def _email_worker():
    """
    Background worker thread that runs continuously, pulls emails from the 
    queue, and dispatches them sequentially with a rate limit.
    """
    while True:
        try:
            task = email_queue.get()
            if task is None:
                break
            
            to_email, subject, html_content = task
            _perform_smtp_send(to_email, subject, html_content)
            
            # Rate limit: Wait 1.5 seconds between emails to prevent SMTP server blocking
            time.sleep(1.5)
        except Exception as e:
            print(f"[Email Worker Error] Exception in task processing: {str(e)}")
            time.sleep(1)
        finally:
            email_queue.task_done()
# Automatically spawn and start the background daemon worker thread on boot
worker_thread = threading.Thread(target=_email_worker, daemon=True)
worker_thread.start()
def _perform_smtp_send(to_email: str, subject: str, html_content: str) -> None:
    """Establishes connection to SMTP and sends the multipart email."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        # Strip HTML to generate clean plain text fallback
        text_content = re.sub(r'<[^>]+>', '', html_content)
        text_content = re.sub(r'\n+', '\n', text_content).strip()
        # Attach alternative content types
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        # Connect and send
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(f"[Email Engine Error] SMTP send to {to_email} failed: {str(e)}")
def send_transactional_email(to_email: str, subject: str, html_content: str) -> None:
    """
    Core gateway to queue transaction alerts. Instead of sending emails instantly 
    and blocking the caller or overloading the SMTP server, it safely queues them.
    """
    email_queue.put((to_email, subject, html_content))
