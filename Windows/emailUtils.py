import smtplib
import imaplib
import email
from emailConfigurations import TO_EMAIL, EMAIL_PASSWORD, EMAIL_ADDRESS, SMTP_SERVER, IMAP_SERVER
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import cv2


def send_email(image, printer_name):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['Subject'] = 'Aptikta Spausdintuvo klaida'

    # Email body
    body = f'Atsakykite į šį laišką "{printer_name}", kad išjungti spausdintuvą.'
    msg.attach(MIMEText(body, 'plain'))

    # Encode image as JPEG in memory
    success, encoded_image = cv2.imencode('.jpg', image)
    if success:
        img_bytes = encoded_image.tobytes()
        image_attachment = MIMEImage(img_bytes, name='image.jpg')
        msg.attach(image_attachment)
    else:
        print("Failed to encode image")

    # Send email
    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
    print("Email with image sent.")


def delete_all_emails_from_sender(sender_email):
    try:
        with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
            mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            mail.select("inbox")

            # Search for all messages from the sender
            result, data = mail.search(None, f'(FROM "{sender_email}")')
            email_ids = data[0].split()

            for msg_id in email_ids:
                mail.store(msg_id, '+FLAGS', '\\Deleted')

            # Permanently delete them
            mail.expunge()
    except Exception as e:
        print(f" Error deleting emails: {e}")




def check_for_yes_reply(printer_name):

    with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select('inbox')

        # Mark all unread emails as read
        result, data = mail.search(None, 'UNSEEN')
        unread_ids = data[0].split()
        for msg_id in unread_ids:
            mail.store(msg_id, '+FLAGS', '\\Seen')

        # Now check for replies (optional: you could re-check all or only recent)
        result, data = mail.search(None, f'(FROM "{TO_EMAIL}")')
        mail_ids = data[0].split()

        for num in reversed(mail_ids):
            result, msg_data = mail.fetch(num, '(RFC822)')
            raw_email = msg_data[0][1]
            message = email.message_from_bytes(raw_email)

            body = ""
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = message.get_payload(decode=True).decode()

            if printer_name.upper() in body.upper():
                print("Received YES reply!")
                return True
        return False