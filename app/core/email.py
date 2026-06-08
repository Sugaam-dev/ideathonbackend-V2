

# # import smtplib
# # from email.mime.text import MIMEText
# # from email.mime.multipart import MIMEMultipart
# # from app.config import settings
# # def send_transactional_email(to_email: str, subject: str, html_content: str) -> None:
# #     """Sends a transactional HTML email using configured SMTP parameters, with local fallbacks."""
# #     message = MIMEMultipart("alternative")
# #     message["Subject"] = subject
# #     message["From"] = settings.SMTP_FROM_EMAIL
# #     message["To"] = to_email
# #     part = MIMEText(html_content, "html")
# #     message.attach(part)
# #     try:
# #         # Connect and authenticate
# #         server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
# #         server.starttls()
# #         server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
# #         server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
# #         server.quit()
# #         print(f"[Email Dispatch] Successfully sent email to {to_email} with subject: '{subject}'")
# #     except Exception as e:
# #         # Print fallback to stdout for offline development ease
# #         print(f"[Email Dispatch Error] Failed to send email via SMTP ({str(e)}). Logging to console instead:")
# #         print("=================== EMAIL FALLBACK ===================")
# #         print(f"Recipient: {to_email}")
# #         print(f"Subject  : {subject}")
# #         print("------------------- HTML Content --------------------")
# #         print(html_content.strip())
# #         print("======================================================")


# import smtplib
# import re
# import queue
# import threading
# import time
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from app.config import settings
# # Thread-safe in-memory email task queue
# email_queue = queue.Queue()
# def _email_worker():
#     """
#     Background worker thread that runs continuously, pulls emails from the 
#     queue, and dispatches them sequentially with a rate limit.
#     """
#     while True:
#         try:
#             task = email_queue.get()
#             if task is None:
#                 break
            
#             to_email, subject, html_content = task
#             _perform_smtp_send(to_email, subject, html_content)
            
#             # Rate limit: Wait 1.5 seconds between emails to prevent SMTP server blocking
#             time.sleep(1.5)
#         except Exception as e:
#             print(f"[Email Worker Error] Exception in task processing: {str(e)}")
#             time.sleep(1)
#         finally:
#             email_queue.task_done()
# # Automatically spawn and start the background daemon worker thread on boot
# worker_thread = threading.Thread(target=_email_worker, daemon=True)
# worker_thread.start()
# def _perform_smtp_send(to_email: str, subject: str, html_content: str) -> None:
#     """Establishes connection to SMTP and sends the multipart email."""
#     try:
#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = subject
#         msg["From"] = settings.SMTP_FROM_EMAIL
#         msg["To"] = to_email
#         # Strip HTML to generate clean plain text fallback
#         text_content = re.sub(r'<[^>]+>', '', html_content)
#         text_content = re.sub(r'\n+', '\n', text_content).strip()
#         # Attach alternative content types
#         msg.attach(MIMEText(text_content, "plain"))
#         msg.attach(MIMEText(html_content, "html"))
#         # Connect and send
#         with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
#             server.starttls()
#             server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
#             server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
#     except Exception as e:
#         print(f"[Email Engine Error] SMTP send to {to_email} failed: {str(e)}")
# def send_transactional_email(to_email: str, subject: str, html_content: str) -> None:
#     """
#     Core gateway to queue transaction alerts. Instead of sending emails instantly 
#     and blocking the caller or overloading the SMTP server, it safely queues them.
#     """
#     email_queue.put((to_email, subject, html_content))




import smtplib
import re
import queue
import threading
import time
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from app.config import settings
from app.database import SessionLocal
from app.features.auth.models import EmailLog
# Thread-safe in-memory email task queue
email_queue = queue.Queue()
# Parse the comma-separated email accounts from configurations
smtp_usernames = [u.strip() for u in settings.SMTP_USERNAMES.split(",") if u.strip()]
smtp_passwords = [p.strip() for p in settings.SMTP_PASSWORDS.split(",") if p.strip()]
# Combine usernames and passwords into a list of account tuples: (username, password)
email_accounts = list(zip(smtp_usernames, smtp_passwords))
current_account_index = 0
account_lock = threading.Lock()  # Ensure index increments are thread-safe
# Track consecutive failures per email account to determine health
smtp_consecutive_failures = {}
health_lock = threading.Lock()
MAX_CONSECUTIVE_FAILURES = 3
def mark_smtp_success(username: str):
    with health_lock:
        smtp_consecutive_failures[username] = 0
def mark_smtp_failure(username: str) -> bool:
    """Increments failure count and returns True if marked unhealthy."""
    with health_lock:
        count = smtp_consecutive_failures.get(username, 0) + 1
        smtp_consecutive_failures[username] = count
        return count >= MAX_CONSECUTIVE_FAILURES
def get_healthy_accounts():
    """Returns list of SMTP accounts that have not hit the failure threshold.
    If all accounts are flagged unhealthy, returns all accounts as a fallback.
    """
    with health_lock:
        healthy = [
            acc for acc in email_accounts 
            if smtp_consecutive_failures.get(acc[0], 0) < MAX_CONSECUTIVE_FAILURES
        ]
        if not healthy:
            # Fallback: if all accounts are unhealthy, try all of them
            return email_accounts
        return healthy
def get_next_email_account():
    """Gets the next email account in round-robin fashion, prioritizing healthy ones."""
    global current_account_index
    if not email_accounts:
        raise ValueError("No SMTP accounts configured in SMTP_USERNAMES and SMTP_PASSWORDS.")
    
    with account_lock:
        healthy = get_healthy_accounts()
        # Find next healthy account starting from current pointer
        for i in range(len(email_accounts)):
            idx = (current_account_index + i) % len(email_accounts)
            candidate = email_accounts[idx]
            if candidate in healthy:
                current_account_index = (idx + 1) % len(email_accounts)
                return candidate
        
        # Fallback to standard round-robin
        account = email_accounts[current_account_index]
        current_account_index = (current_account_index + 1) % len(email_accounts)
        return account
def _log_smtp_transaction(recipient_email: str, subject: str, smtp_account_used: str, status: str, error_message: Optional[str] = None):
    """Saves SMTP dispatch attempt metadata into the database email_logs table."""
    db = SessionLocal()
    try:
        log_entry = EmailLog(
            recipient_email=recipient_email,
            subject=subject,
            smtp_account_used=smtp_account_used,
            status=status,
            error_message=error_message
        )
        db.add(log_entry)
        db.commit()
    except Exception as db_err:
        # Never crash the email worker due to database logger failures.
        print(f"[Email Logger Error] Failed to write log to DB: {str(db_err)}")
    finally:
        db.close()
def _email_worker():
    """
    Background worker thread that runs continuously, pulls emails from the 
    queue, and dispatches them sequentially with a rate limit and retries.
    """
    while True:
        try:
            task = email_queue.get()
            if task is None:
                break
            
            to_email, subject, html_content = task
            
            # Retry mechanism: Try sending using rotating accounts
            sent_successfully = False
            max_attempts = min(3, len(email_accounts))  # Max 3 attempts per email or total accounts count
            attempts = 0
            
            while attempts < max_attempts:
                username, password = get_next_email_account()
                
                success, error_msg = _perform_smtp_send(to_email, subject, html_content, username, password)
                
                if success:
                    mark_smtp_success(username)
                    _log_smtp_transaction(to_email, subject, username, "SUCCESS")
                    sent_successfully = True
                    break
                else:
                    mark_smtp_failure(username)
                    _log_smtp_transaction(to_email, subject, username, "FAILED", error_msg)
                    attempts += 1
                    time.sleep(0.5)  # Backoff brief delay
            
            # Rate limit: Wait 1.5 seconds between emails to prevent SMTP server blocking
            time.sleep(1.5)
        except Exception as e:
            # Quietly log unexpected worker loop errors without exposing credentials
            print(f"[Email Worker Error] Exception in loop: {str(e)}")
            time.sleep(1)
        except SystemExit:
            break
        finally:
            email_queue.task_done()
# Automatically spawn and start the background daemon worker thread on boot
worker_thread = threading.Thread(target=_email_worker, daemon=True)
worker_thread.start()
def _perform_smtp_send(to_email: str, subject: str, html_content: str, username: str, password: str) -> tuple[bool, Optional[str]]:
    """Establishes connection to SMTP and sends the multipart email using specific credentials."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = username  # Must match the authenticated username for Gmail to send successfully
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
            server.login(username, password)
            server.sendmail(username, to_email, msg.as_string())
            return True, None
    except Exception as e:
        error_msg = str(e)
        # Quiet error log: only prints connection failures without exposing subject line/body
        print(f"[Email Engine Error] SMTP send failed using account {username}: {error_msg}")
        return False, error_msg
def send_transactional_email(to_email: str, subject: str, html_content: str) -> None:
    """
    Core gateway to queue transaction alerts. Instead of sending emails instantly 
    and blocking the caller or overloading the SMTP server, it safely queues them.
    """
    email_queue.put((to_email, subject, html_content))
