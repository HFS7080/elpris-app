#!/usr/bin/env python3
"""
Notification module for Elpris App
"""

import json
import smtplib
from email.mime.text import MIMEText
import requests

class Notifier:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"notification": {"enabled": False, "method": "console"}}

    def send_notification(self, message, subject="Elpris - Billigste timer"):
        notification_config = self.config.get("notification", {})

        if not notification_config.get("enabled", False):
            self.send_console(message, subject)
            return

        method = notification_config.get("method", "console")

        if method == "telegram":
            self.send_telegram(message)
        elif method == "email":
            self.send_email(message, subject)
        else:
            self.send_console(message, subject)

    def send_console(self, message, subject=None):
        if subject:
            print(f"\n=== {subject} ===")
        print(message)
        if subject:
            print("=" * len(subject))

    def send_telegram(self, message):
        telegram_config = self.config.get("notification", {}).get("telegram", {})
        bot_token = telegram_config.get("bot_token", "")
        chat_id = telegram_config.get("chat_id", "")

        if not bot_token or not chat_id:
            print("Telegram konfiguration mangler")
            return

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        try:
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code != 200:
                print(f"Telegram fejl: {response.status_code}")
        except Exception as e:
            print(f"Fejl ved Telegram: {e}")

    def send_email(self, message, subject):
        email_config = self.config.get("notification", {}).get("email", {})

        if not email_config.get("enabled", False):
            print("Email er ikke aktiveret")
            return

        smtp_server = email_config.get("smtp_server", "")
        smtp_port = email_config.get("smtp_port", 587)
        username = email_config.get("username", "")
        password = email_config.get("password", "")
        from_email = email_config.get("from_email", "")
        to_email = email_config.get("to_email", "")

        if not all([smtp_server, username, password, from_email, to_email]):
            print("Email konfiguration mangler")
            return

        try:
            msg = MIMEText(message, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            print("Email sendt")
        except Exception as e:
            print(f"Fejl ved email: {e}")
