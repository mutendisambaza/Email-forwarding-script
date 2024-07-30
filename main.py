from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import imaplib
import smtplib
import email
import os
from pathlib import Path
from dotenv import load_dotenv
 
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
env_vars = current_dir / ".env"
load_dotenv(env_vars)

#Config
IMAP_SERVER = os.getenv('IMAP_SERVER')
IMAP_PORT = int(os.getenv('IMAP_PORT'))
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
FORWARD_TO_EMAIL = os.getenv('FORWARD_TO_EMAIL')
SEARCH_FROM = os.getenv('SEARCH_FROM')
SEARCH_SUBJECT = os.getenv('SEARCH_SUBJECT')


def check_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select('inbox')

    result, data = mail.search(None, f'(FROM "{SEARCH_FROM}" SUBJECT "{SEARCH_SUBJECT}")')

    if result == 'OK':
            for num in data[0].split():
                result, msg_data = mail.fetch(num, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = message_from_bytes(raw_email)

                # Forward the email
                forward_email(msg)

                # Mark the email as seen (optional)
                mail.store(num, '+FLAGS', '\\Seen')

    mail.logout()


def forward_email(msg):
    # Set up the SMTP server
    smtp_server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    smtp_server.starttls()  # Use STARTTLS
    smtp_server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)

    # Create a new email message
    forwarded_msg = MIMEMultipart()
    forwarded_msg['From'] = EMAIL_ACCOUNT
    forwarded_msg['To'] = FORWARD_TO_EMAIL
    forwarded_msg['Subject'] = f"Fwd: {msg['Subject']}"

    # Attach the original email content
    forwarded_msg.attach(MIMEText(msg.get_payload(decode=True), 'plain'))

    # Send the email
    smtp_server.send_message(forwarded_msg)
    smtp_server.quit()



