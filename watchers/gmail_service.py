import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

class GmailService:
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send', 
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    def __init__(self, credentials_path, token_path):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.service = None
        self.logger = logging.getLogger("GmailService")
        
        # Suppress noisy google logs immediately
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
        logging.getLogger('googleapiclient.discovery').setLevel(logging.ERROR)
        
        self._authenticate()

    def _authenticate(self):
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Error refreshing token: {e}")
                    self.creds = None
            
            if not self.creds:
                # This should ideally be handled by refresh_gmail_token.py
                self.logger.warning("No valid credentials found. Please run refresh_gmail_token.py")
                return

            with open(self.token_path, 'w', encoding='utf-8') as token:
                token.write(self.creds.to_json())
        
        if self.creds:
            self.service = build('gmail', 'v1', credentials=self.creds)

    def list_unread_messages(self, query='is:unread'):
        if not self.service:
            return []
        try:
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            return [m['id'] for m in messages]
        except Exception as e:
            self.logger.error(f"Error listing messages: {e}")
            return []

    def get_message_content(self, msg_id):
        if not self.service:
            return None
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            result = {
                'id': msg_id,
                'from': '',
                'subject': '',
                'body': '',
                'snippet': message.get('snippet', '')
            }
            
            for header in headers:
                if header['name'] == 'From':
                    result['from'] = header['value']
                if header['name'] == 'Subject':
                    result['subject'] = header['value']
            
            # Extract body
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            result['body'] = base64.urlsafe_b64decode(data).decode()
            else:
                data = payload.get('body', {}).get('data')
                if data:
                    result['body'] = base64.urlsafe_b64decode(data).decode()
            
            return result
        except Exception as e:
            self.logger.error(f"Error getting message {msg_id}: {e}")
            return None

    def mark_as_read(self, msg_id):
        if not self.service:
            return False
        try:
            self.service.users().messages().batchModify(
                userId='me',
                body={'ids': [msg_id], 'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error marking message {msg_id} as read: {e}")
            return False

    def send_message(self, to, subject, body):
        if not self.service:
            self.logger.error("Cannot send email: No valid service.")
            return None

        try:
            message = EmailMessage()
            message.set_content(body)
            message['To'] = to
            message['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}

            send_message = (self.service.users().messages().send(userId="me", body=create_message).execute())
            self.logger.info(f'Sent message to {to}. Message Id: {send_message["id"]}')
            return send_message
        except HttpError as error:
            self.logger.error(f'An error occurred: {error}')
            return None
