import os
import base64
import re
from email import message_from_bytes
from bs4 import BeautifulSoup
from datetime import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    print("Initializing Gmail service...")
    creds = None
    if os.path.exists('token.pickle'):
        print("Found existing token.pickle, loading credentials.")
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        print("Credentials are missing or invalid.")
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("No valid credentials found. Launching OAuth flow...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
            print("Saved new credentials to token.pickle.")

    print("Gmail service initialized successfully.")
    return build('gmail', 'v1', credentials=creds)

def extract_morningbrew_content(html: str) -> list[dict]:
    print("🔍 Parsing HTML content...")
    soup = BeautifulSoup(html, 'html.parser')
    stories = soup.select('table.story-container')
    print(f"📦 Found {len(stories)} story sections in the email.")

    articles = []

    for idx, story in enumerate(stories):
        title_el = story.select_one('h1')
        if not title_el:
            continue

        title_text = title_el.get_text(strip=True)
        print(f"\n📰 Story {idx + 1}: {title_text}")
        content_blocks = []

        paragraphs = story.select('p')
        list_items = story.select('li')

        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                log = f"  - {text[:80]}... ({len(text)} chars)" if len(text) > 80 else f"  - {text}"
                print(log)
                content_blocks.append(text)

        for li in list_items:
            text = li.get_text(strip=True)
            if text:
                log = f"  • {text[:80]}... ({len(text)} chars)" if len(text) > 80 else f"  • {text}"
                print(log)
                content_blocks.append(f"- {text}")

        articles.append({
            "title": title_text,
            "published_at": datetime.now().isoformat(),  # You can extract this from the headers if needed
            "content": "\n\n".join(content_blocks)
        })

    return articles

def get_latest_morningbrew_news() -> list[dict]:
    service = get_gmail_service()
    print("📨 Fetching Morning Brew emails from crew@morningbrew.com...")

    try:
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q='from:crew@morningbrew.com',
            maxResults=1
        ).execute()
    except Exception as e:
        print(f"❌ Error fetching message list: {e}")
        return ""

    messages = results.get('messages', [])
    if not messages:
        print("❌ No Morning Brew emails found.")
        return ""

    msg_id = messages[0]['id']
    print(f"📬 Fetching full message content for ID: {msg_id}")

    try:
        msg_data = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    except Exception as e:
        print(f"❌ Failed to fetch message: {e}")
        return ""

    # Extract the HTML part of the message
    payload = msg_data.get('payload', {})
    parts = payload.get('parts', [])

    html_content = None
    for part in parts:
        if part.get('mimeType') == 'text/html':
            data = part['body'].get('data')
            if data:
                html_content = base64.urlsafe_b64decode(data).decode('utf-8')
                break

    if not html_content:
        print("❌ No HTML content found in the email.")
        return ""

    print("✅ HTML content retrieved. Extracting readable text...")
    return extract_morningbrew_content(html_content)
