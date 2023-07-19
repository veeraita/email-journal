import os
import base64
import json
import logging

logging.basicConfig(format='%(asctime)s - %(message)s',
                    level=logging.INFO)

from email.mime.text import MIMEText

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from utils.compile_prompt import create_message_text

### File path definitions ###
cwd = os.path.abspath(os.path.dirname(__file__))
# Gmail API credentials
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = os.path.abspath(os.path.join(os.path.dirname(cwd), 'oauth2_credentials.json'))
TOKEN_FILE = '/tmp/token.json'
# Email config
CONFIG_FILE = os.path.abspath(os.path.join(os.path.dirname(cwd), 'config.json'))
# Journaling prompts
PROMPT_FILE = os.path.abspath(os.path.join(os.path.dirname(cwd), 'journal_prompts.txt'))


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['subject'] = subject
    message = {
        'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8'),
        'payload': {
            'headers': {
                'From': sender,
                'To': to,
                'Subject': subject
            }
        }
    }
    return message


def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        logging.info(f'Message sent successfully! Message Id: {message["id"]}')
        return message
    except HttpError as error:
        logging.exception('An error occurred')


def connect_and_send():
    # Email configurations
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    sender = config['sender']
    receiver = config['receiver']
    subject = 'Daily Journal Reminder'
    body = create_message_text(PROMPT_FILE)

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Do the authentication
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    # Create Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Send the email
    message = create_message(sender, receiver, subject, body)
    send_message(service, 'me', message)


if __name__ == '__main__':
    connect_and_send()
