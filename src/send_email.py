import os
import json
import logging
import smtplib
import ssl

from email.mime.text import MIMEText

from utils.compile_prompt import create_message_text

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)

### File path definitions ###
# Current directory
cwd = os.path.abspath(os.path.dirname(__file__))
# Email config
CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(cwd), "config.json"))
# Journaling prompts
PROMPT_FILE = os.path.abspath(os.path.join(os.path.dirname(cwd), "journal_prompts.txt"))


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message["to"] = to
    message["subject"] = subject

    return message


def send_message(sender_email, receiver_email, password, message):
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        logging.info("Successfully sent email")
    except:
        logging.exception("An error occurred")


def main():
    # Email configurations
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    sender = config["sender"]
    receiver = config["receiver"]
    password = config["password"]
    subject = "Daily Journal Reminder"
    body = create_message_text(PROMPT_FILE)

    # Send the email
    message = create_message(sender, receiver, subject, body)
    send_message(sender, receiver, password, message)


if __name__ == "__main__":
    main()
