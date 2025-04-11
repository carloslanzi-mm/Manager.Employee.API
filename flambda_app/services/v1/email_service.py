import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List


class EmailService:
    """
    Serviço de envio de e-mails via SMTP.
    """
    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 2525))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'Report <relatorios@madeiramadeira.com>')
    EMAIL_DOMAIN = "@madeiramadeira.com"

    @classmethod
    def validate_emails(cls, emails: List[str]) -> List[str]:
        """
        Filtra e retorna apenas e-mails válidos do domínio madeiramadeira.com.

        Args:
            emails (List[str]): Lista de e-mails a validar.

        Returns:
            List[str]: Lista de e-mails válidos com domínio permitido.
        """
        standard = re.compile(rf"^[\w\.-]+{cls.EMAIL_DOMAIN}$")
        return [email for email in emails if standard.match(email)]

    @classmethod
    def build_message(cls, subject: str, body: str, recipient: str) -> MIMEMultipart:
        """
        Monta a mensagem de e-mail.

        Args:
            subject (str): Assunto do e-mail.
            body (str): Corpo do e-mail.
            recipient (str): Destinatário.

        Returns:
            MIMEMultipart: Objeto da mensagem pronta para envio.
        """
        msg = MIMEMultipart()
        msg['From'] = cls.FROM_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        return msg

    @classmethod
    def send(cls, subject: str, body: str, recipients: List[str]) -> None:
        """
        Envia e-mail para uma lista de destinatários.

        Args:
            subject (str): Assunto do e-mail.
            body (str): Corpo da mensagem.
            recipients (List[str]): Lista de e-mails de destino.
        """
        with smtplib.SMTP(cls.SMTP_HOST, cls.SMTP_PORT) as server:
            server.starttls()
            server.login(cls.SMTP_USERNAME, cls.SMTP_PASSWORD)

            for recipient in recipients:
                msg = cls.build_message(subject, body, recipient)
                server.sendmail(cls.FROM_EMAIL, recipient, msg.as_string())
                print(f"Email enviado para: {recipient}")
