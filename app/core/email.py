import smtplib
import re
import threading
import time
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

from app.config import settings
from app.database import SessionLocal
from app.features.auth.models import EmailLog
from app.core.celery_app import celery_app

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
        print(f"[Email Logger Error] Failed to write log to DB: {str(db_err)}")
    finally:
        db.close()

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
        print(f"[Email Engine Error] SMTP send failed using account {username}: {error_msg}")
        return False, error_msg

@celery_app.task(name="send_email_task", max_retries=3)
def send_transactional_email_task(to_email: str, subject: str, html_content: str) -> bool:
    """
    Asynchronous Celery task that sends emails with account rotation, health checks, and database logging.
    """
    sent_successfully = False
    max_attempts = min(3, len(email_accounts))
    attempts = 0
    
    last_error = None
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
            last_error = error_msg
            attempts += 1
            time.sleep(0.5)  # Brief backoff delay
            
    # Sequential delay between task dispatches to prevent SMTP rate-blocking
    time.sleep(1.5)
    
    if not sent_successfully:
        # Let Celery know the task failed
        raise RuntimeError(f"Failed to send email to {to_email} after {max_attempts} attempts. Last error: {last_error}")
        
    return sent_successfully

def send_transactional_email(to_email: str, subject: str, html_content: str) -> None:
    """
    Interface proxy helper function. Automatically pushes email tasks onto the Celery/Redis queue.
    This preserves absolute compatibility with existing services.py modules without changing import links.
    """
    send_transactional_email_task.delay(to_email, subject, html_content)
