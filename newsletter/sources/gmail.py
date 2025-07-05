import os
from typing import List
import logging

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

from ..models import NewsItem

logger = logging.getLogger(__name__)

class GmailSource:
    """Fetches important emails from Gmail"""
    
    def __init__(self, query: str = "from:newsletters OR subject:important", max_items: int = 5):
        self.query = query
        self.max_items = max_items
        self.gmail_service = None
        
        if GMAIL_AVAILABLE:
            self._setup_gmail()
    
    def _setup_gmail(self):
        """Setup Gmail API authentication"""
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        creds = None
        
        # Check if credentials file exists
        if not os.path.exists('credentials.json'):
            logger.warning("Gmail credentials.json not found. Skipping Gmail.")
            return
        
        # Load existing token
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing Gmail credentials: {e}")
                    return
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    logger.error(f"Error getting Gmail credentials: {e}")
                    return
            
            # Save credentials for next run
            try:
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                logger.error(f"Error saving Gmail token: {e}")
        
        try:
            self.gmail_service = build('gmail', 'v1', credentials=creds)
        except Exception as e:
            logger.error(f"Error building Gmail service: {e}")
    
    async def fetch(self) -> List[NewsItem]:
        """Fetch important emails from Gmail"""
        if not GMAIL_AVAILABLE:
            logger.warning("Google API libraries not installed. Skipping Gmail.")
            return []
        
        if not self.gmail_service:
            logger.warning("Gmail service not configured. Skipping Gmail.")
            return []
        
        try:
            logger.info("Fetching from Gmail...")
            
            results = self.gmail_service.users().messages().list(
                userId='me', q=self.query, maxResults=self.max_items
            ).execute()
            
            items = []
            messages = results.get('messages', [])
            
            for message in messages:
                try:
                    msg = self.gmail_service.users().messages().get(
                        userId='me', id=message['id']
                    ).execute()
                    
                    headers = msg['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                    
                    item = NewsItem(
                        title=f"Email: {subject}",
                        url=f"https://mail.google.com/mail/u/0/#inbox/{message['id']}",
                        summary=f"From: {sender}",
                        source='Gmail',
                        score=0
                    )
                    items.append(item)
                except Exception as e:
                    logger.error(f"Error processing Gmail message: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(items)} emails from Gmail")
            return items
            
        except Exception as e:
            logger.error(f"Error fetching Gmail: {e}")
            return []