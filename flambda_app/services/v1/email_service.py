import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 2525))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'Report <relatorios@madeiramadeira.com>')
    EMAIL_DOMAIN = "@madeiramadeira.com"

    @classmethod
    def validate_emails(cls, emails):
        standard = re.compile(rf"^[\w\.-]+{cls.EMAIL_DOMAIN}$")
        return [email for email in emails if standard.match(email)]

    @classmethod
    def build_message(cls, subject, body, recipient):
        msg = MIMEMultipart()
        msg['From'] = cls.FROM_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        return msg

    @classmethod
    def send(cls, subject, body, recipients):
        with smtplib.SMTP(cls.SMTP_HOST, cls.SMTP_PORT) as server:
            server.starttls()
            server.login(cls.SMTP_USERNAME, cls.SMTP_PASSWORD)

            for recipient in recipients:
                msg = cls.build_message(subject, body, recipient)
                server.sendmail(cls.FROM_EMAIL, recipient, msg.as_string())
                print(f"Email enviado para: {recipient}")
