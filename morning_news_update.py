#!/usr/bin/env python3
"""
Morning News Update - Runs every day at 8 AM
- Checks Gmail inbox for new emails
- Fetches major news and international news
- Sends organized update to user
"""

import os
import imaplib
import email
import json
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

# Gmail config
INBOX_EMAIL = os.environ.get("AGENTMAIL_INBOX_EMAIL", "ahmadraoabsar@gmail.com")
APP_PASSWORD = os.environ.get("AGENTMAIL_API_KEY", "")

# Output file
OUTPUT_FILE = "/home/ubuntu/.hermes/cache/morning_update_result.json"

def fetch_gmail_updates():
    """Fetch new Gmail messages."""
    updates = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=60)
        mail.login(INBOX_EMAIL, APP_PASSWORD.replace(" ", ""))
        mail.select("INBOX")
        
        status, messages = mail.search('UTF-8', 'ALL')
        if status == "OK":
            msg_ids = messages[0].split()
            # Get most recent 20
            for msg_id in msg_ids[-20:]:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue
                msg_raw = msg_data[0][1]
                msg = email.message_from_bytes(msg_raw)
                
                subject = ""
                if msg.is_multipart():
                    subject = str(make_header(decode_header(msg.get("Subject", ""))))
                else:
                    subject = str(make_header(decode_header(msg.get("Subject", ""))))
                
                from_ = msg.get("From", "")
                date = msg.get("Date", "")
                try:
                    date_parsed = parsedate_to_datetime(date)
                    date_iso = date_parsed.isoformat()
                except:
                    date_iso = date
                
                text = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                text = payload.decode("utf-8", errors="replace")
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        text = payload.decode("utf-8", errors="replace")
                
                updates.append({
                    "subject": subject[:100],
                    "from": from_[:50],
                    "date": date_iso,
                    "preview": text[:200]
                })
        mail.logout()
    except Exception as e:
        print(f"Email fetch error: {e}")
    
    return updates

def fetch_news(query, limit=5):
    """Fetch news using web_search."""
    news = []
    try:
        results = web_search(query, limit=limit)
        for r in results:
            news.append({
                "title": r.get("title", ""),
                "description": r.get("description", ""),
                "url": r.get("url", "")
            })
    except Exception as e:
        print(f"News fetch error: {e}")
    
    return news

def main():
    print("Starting morning news update...")

    # 1. Fetch Gmail updates
    print("Fetching Gmail updates...")
    gmail_updates = fetch_gmail_updates()

    # 2. Fetch major news and international news
    print("Fetching major news...")
    major_news = fetch_news("world top headlines", 3)
    
    print("Fetching international news...")
    international_news = fetch_news("international news", 3)

    # 3. Compile the update
    update = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gmail_updates": gmail_updates,
        "major_news": major_news,
        "international_news": international_news,
        "summary": {
            "emails": len(gmail_updates),
            "major_news": len(major_news),
            "international_news": len(international_news)
        }
    }

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(update, f, indent=2)

    print(f"Morning update saved: {update['summary']}")
    print("Morning update complete.")

    return update

if __name__ == "__main__":
    main()
