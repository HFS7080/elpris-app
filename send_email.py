#!/usr/bin/env python3
import smtplib
import glob
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

def send_email(smtp_server, smtp_port, email_user, email_password, email_to):
    # Find den nyeste result-fil
    result_files = glob.glob('result_*.txt')
    if not result_files:
        result = 'Kunne ikke finde resultater. Prøv igen senere.'
    else:
        result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        with open(result_files[0], 'r') as f:
            result = f.read()

    # Opret email
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_to
    msg['Subject'] = 'Elpris - Billigste timer i morgen'
    msg.attach(MIMEText(result, 'plain', 'utf-8'))

    # Send email
    try:
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(email_user, email_password)
            server.send_message(msg)
        print('✅ Email sendt succesfuldt!')
        return True
    except Exception as e:
        print(f'❌ Fejl ved email: {e}')
        with open('email_error.txt', 'w') as f:
            f.write(f'Fejl ved email: {e}')
        return False

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Brug: python send_email.py SMTP_SERVER SMTP_PORT EMAIL_USER EMAIL_PASSWORD EMAIL_TO")
        sys.exit(1)

    success = send_email(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    sys.exit(0 if success else 1)
