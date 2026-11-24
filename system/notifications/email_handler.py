import smtplib
import imaplib
import email
import json
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import cv2


class PrinterAlertEmailHandler:
    def __init__(self):
        self.success = None

        config_path = Path(__file__).resolve().parent.parent / "configurations" / "email_config.json"
        with open(config_path) as f:
            data = json.load(f)
            emails = data["receiving_emails"]
            TO_EMAILS = []
            for email in emails:
                TO_EMAILS.append(email["email"])

            sender_emails = data["sender_email"][0]

            self.TO_EMAILS = TO_EMAILS
            self.EMAIL_ADDRESS = sender_emails["email_address"]
            self.EMAIL_PASSWORD = sender_emails["email_password"]
            self.SMTP_SERVER = sender_emails["smtp"]
            self.IMAP_SERVER = sender_emails["imap"]

    def send_email(self,msg):
        try:
            with smtplib.SMTP_SSL(self.SMTP_SERVER, 465) as server:
                server.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                server.send_message(msg)
                return
        except Exception as e:
            self.success = False

    def send_alert(self,image, printer_name) -> bool:
        self.success = True

        for email in self.TO_EMAILS:
            msg = MIMEMultipart()
            msg['From'] = self.EMAIL_ADDRESS
            msg['To'] = email
            msg['Subject'] = 'Aptikta Spausdintuvo klaida'

            # Email body
            body = f'Atsakykite į šį laišką "{printer_name}", kad išjungti spausdintuvą.'
            msg.attach(MIMEText(body, 'plain'))

            success, encoded_image = cv2.imencode('.jpg', image)
            if success:
                img_bytes = encoded_image.tobytes()
                image_attachment = MIMEImage(img_bytes, name='image.jpg')
                msg.attach(image_attachment)
            else:
                print("Failed to encode image")


            self.send_email(msg)
        return self.success




    '''
    def delete_all_emails_from_sender(self):
        try:
            with imaplib.IMAP4_SSL(self.IMAP_SERVER) as mail:
                mail.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                mail.select("inbox")

                # Search for all emails
                result, data = mail.search(None, "ALL")
                if result != "OK":
                    print("No messages found!")
                    return

                email_ids = data[0].split()
                for msg_id in email_ids:
                    mail.store(msg_id, '+FLAGS', '\\Deleted')

                # Permanently delete marked emails
                mail.expunge()
                print(f"Deleted {len(email_ids)} emails.")

        except Exception as e:
            print(f"Error deleting emails: {e}")
    '''

    def check_for_user_response(self,printer_name):
        try:
            with imaplib.IMAP4_SSL(self.IMAP_SERVER) as mail:
                mail.login(self.EMAIL_ADDRESS, self.EMAIL_PASSWORD)
                mail.select('inbox')

                # Mark all unread emails as read
                result, data = mail.search(None, 'UNSEEN')
                unread_ids = data[0].split()
                for msg_id in unread_ids:
                    mail.store(msg_id, '+FLAGS', '\\Seen')

                # Check messages from each sender
                for sender in self.TO_EMAILS:
                    result, data = mail.search(None, f'(FROM "{sender}")')

                    if result != "OK":
                        continue

                    mail_ids = data[0].split()
                    for num in reversed(mail_ids):
                        result, msg_data = mail.fetch(num, '(RFC822)')
                        raw_email = msg_data[0][1]
                        message = email.message_from_bytes(raw_email)
                        # Get plain text body
                        body = ""
                        if message.is_multipart():
                            for part in message.walk():
                                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                    break
                        else:
                            body = message.get_payload(decode=True).decode(errors='ignore')
                        print(body)
                        # Look for the keyword in the email body
                        if printer_name.upper() in body.upper():
                            return True

            return False

        except Exception as e:
            print(f"Error checking replies: {e}")
            return False



