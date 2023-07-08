import os
import datetime
import base64
import json
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

from email.mime.text import MIMEText

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


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


# Email configurations
config_file = 'config.json'
with open(config_file, 'r') as f:
    config = json.load(f)

sender = config['sender']
receiver = config['receiver']
subject = 'Daily Journal Reminder'
body = """
Was there something that made you happy today? Write it down so you'll remember it later!
"""

# Gmail API credentials
SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
    ]
credentials_file = 'credentials.json'
token_file = 'token.json'

creds = None
if os.path.exists(token_file):
    creds = credentials.Credentials.from_authorized_user_file(token_file, SCOPES)

# Do the authentication
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(token_file, 'w') as token:
        token.write(creds.to_json())

# Create Gmail API service
service = build('gmail', 'v1', credentials=creds)

# Send the email
message = create_message(sender, receiver, subject, body)
send_message(service, 'me', message)