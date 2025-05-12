import smtplib
import os
import time
from email.message import EmailMessage
from services.config_loader import load_mail_config
from services.logger_service import log_and_print

def send_mail_with_attachment(receiver_email, subject, body, attachment_path):
    """
    Sends an email with an attachment using SMTP settings from config.json.
    
    Args:
        receiver_email (str): Recipient email address.
        subject (str): Email subject.
        body (str): Email content.
        attachment_path (str): Path to attachment file.

    Raises:
        Exception: If email sending fails.
    """
    config = load_mail_config()
    sender_email = config["sender_email"]
    sender_password = config["sender_password"]
    smtp_server = config["smtp_server"]
    smtp_port = config["smtp_port"]

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        raise Exception(f"Failed to send email: {e}")
    
def check_for_confirmation(subject_keyword: str, wait_minutes: int = 5, check_interval: int = 30) -> bool:
    """
    Checks for a confirmation email with a specific subject keyword within a time window.
    
    Args:
        subject_keyword (str): Subject keyword to search for in the email.
        wait_minutes (int): Total wait time in minutes.
        check_interval (int): Interval between checks in seconds.
    
    Returns:
        bool: True if confirmation email found, False otherwise.
    """
    config = load_mail_config()
    email_user = config["sender_email"]
    email_pass = config["sender_password"]

    end_time = time.time() + wait_minutes * 60

    while time.time() < end_time:
        try:
            log_and_print("📧 Checking inbox for confirmation email...")
            with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
                mail.login(email_user, email_pass)
                mail.select("inbox")

                result, data = mail.search(None, f'(SUBJECT "{subject_keyword}")')

                if result == "OK":
                    mail_ids = data[0].split()
                    if mail_ids:
                        log_and_print("📧 Confirmation email found!")
                        return True

            time.sleep(check_interval)
        except Exception as e:
            log_and_print(f"❌ Failed to check confirmation email: {e}", level="error")
            time.sleep(check_interval)

    log_and_print("⏰ Confirmation email not received in the given time.")
    return False