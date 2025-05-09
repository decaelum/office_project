import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from tkinter import simpledialog, Tk
from services.automation.config_loader import load_mail_config

def send_mail_with_attachment(receiver_email, subject, body, attachment_path):
    """
    Belirtilen e-posta adresine rapor gönderir.
    """
    config = load_mail_config()
    smtp_server = config["smtp_server"]
    smtp_port = config["smtp_port"]
    sender_email = config["sender_email"]
    sender_password = config["sender_password"]

    print(f"Yüklenen Config: {config}")

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
            msg.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print("📧 E-posta başarıyla gönderildi.")
        return True

    except Exception as e:
        print(f"❌ E-posta gönderim hatası: {e}")
        return False
    
    