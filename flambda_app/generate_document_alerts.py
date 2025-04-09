import pymysql
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_CONFIG = {
    'host': 'mysql',
    'user': 'root',
    'password': 'store',
    'database': 'store',
    'port': 3306,
    'cursorclass': pymysql.cursors.DictCursor
}

SMTP_CONFIG = {
    'host': 'sandbox.smtp.mailtrap.io',
    'port': 2525,
    'username': 'dc576eec74e766',
    'password': 'b3ba36d69cc7db',
    'from_email': 'Private Person <from@example.com>',
    'recipients': ['A Test User <to@example.com>']
}


def build_email_body(document_name, company_name, ended_at, link_download):
    return f"""
📢 Olá,

O documento 📑"{document_name}" da empresa 🏢"{company_name}" está com a data de expiração
prevista para {ended_at} ⏳.
Clique no link para relembrar do documento 📑"{document_name}": "{link_download}"

⚠️ Por favor, tome as providências necessárias para renovação ou atualização deste documento.

Atenciosamente,
Seu sistema automático 💻
"""


def run_alerts():
    conn = pymysql.connect(**DB_CONFIG)
    today = date.today()
    recipients = SMTP_CONFIG['recipients']
    sent_emails = ','.join(recipients)

    try:
        with conn.cursor() as cursor:
            # Buscar documentos que vencem em 30 dias
            query = """
                SELECT
                    d.id AS document_id,
                    d.name AS document_name,
                    d.url AS link_download,
                    d.ended_at,
                    c.name AS company_name
                FROM documents d
                JOIN company c ON c.id = d.company_id
                WHERE d.ended_at IS NOT NULL
                  AND d.deleted_at IS NULL
                  AND DATEDIFF(d.ended_at, CURRENT_DATE()) = 30
            """
            cursor.execute(query)
            documents = cursor.fetchall()

            for doc in documents:
                # Verificar se já existe alerta
                check_alert = """
                    SELECT 1 FROM alerts
                    WHERE document_id = %s AND alert_date = %s
                    LIMIT 1
                """
                cursor.execute(check_alert, (doc['document_id'], today))
                if cursor.fetchone():
                    print(f"⚠️  Alert already exists for document ID {doc['document_id']}")
                    continue

                # Enviar email
                subject = f"CD Control Document Expiration Alert: {doc['document_name']}"
                body = build_email_body(doc['document_name'],
                                        doc['company_name'],
                                        doc['ended_at'],
                                        doc['link_download'])

                msg = MIMEMultipart()
                msg['From'] = SMTP_CONFIG['from_email']
                msg['To'] = sent_emails
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
                    server.starttls()
                    server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
                    server.sendmail(
                        SMTP_CONFIG['from_email'],
                        recipients,
                        msg.as_string()
                    )
                    print(f"✅ Email sent for document ID {doc['document_id']}")

                # Salvar alerta
                insert_alert = """
                    INSERT INTO alerts (document_id, alert_date, sent_emails)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_alert, (doc['document_id'], today, sent_emails))

            conn.commit()
            print("🎉 Finished processing alerts.")

    finally:
        conn.close()


if __name__ == '__main__':
    run_alerts()
