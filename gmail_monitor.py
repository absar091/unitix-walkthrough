#!/usr/bin/env python3
"""
Gmail Inbox Monitor - Checks a Gmail inbox for NEW emails and notifies.
Uses Gmail IMAP (app password) with SINCE filter to only check recent messages.

Run with: python3 gmail_monitor.py
Environment variables:
  AGENTMAIL_INBOX_EMAIL - Gmail address to monitor (e.g. ahmadraoabsar@gmail.com)
  AGENTMAIL_API_KEY     - Gmail app password (16-char app-specific password)
  AGENTMAIL_SINCE       - ISO timestamp to filter messages (optional, for incremental checks)
"""

import os
import json
import sys
import imaplib
import email
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

# Configure from env vars
INBOX_EMAIL = os.environ.get("AGENTMAIL_INBOX_EMAIL", "ahmadraoabsar@gmail.com")
APP_PASSWORD = os.environ.get("AGENTMAIL_API_KEY", "")
SINCE_TIMESTAMP = os.environ.get("AGENTMAIL_SINCE", "")

if not APP_PASSWORD:
    print("ERROR: AGENTMAIL_API_KEY not set", file=sys.stderr)
    sys.exit(1)

# Since timestamp for incremental checks (deduplication)
LAST_CHECKED_FILE = "/home/ubuntu/.hermes/cache/gmail_last_checked.txt"


def load_last_checked():
    """Load the last checked timestamp from file."""
    try:
        with open(LAST_CHECKED_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_checked(timestamp):
    """Save the last checked timestamp to file."""
    try:
        with open(LAST_CHECKED_FILE, "w") as f:
            f.write(timestamp)
    except Exception:
        pass


def get_since_param(since_timestamp=None):
    """Convert timestamp to IMAP SINCE parameter format."""
    if not since_timestamp:
        return None
    try:
        dt = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
        return dt.strftime("%d-%b-%Y %H:%M:%S +0000")
    except Exception:
        return since_timestamp


def fetch_new_messages(since_timestamp=None):
    """Fetch new messages from Gmail IMAP with SINCE filter."""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=60)
        mail.login(INBOX_EMAIL, APP_PASSWORD.replace(" ", ""))
        mail.select("INBOX")

        # First get all messages
        status, messages = mail.search('UTF-8', 'ALL')
        if status != "OK":
            mail.logout()
            return {"error": f"Search failed: {status}", "messages": []}

        msg_ids = messages[0].split()
        if not msg_ids:
            mail.logout()
            return {"count": 0, "messages": []}

        # Filter by timestamp in Python for SINCE support

        msg_ids = messages[0].split()
        if not msg_ids:
            mail.logout()
            return {"count": 0, "messages": []}

        # Process messages (limit to most recent 50 for performance)
        result = {"count": 0, "messages": []}
        for msg_id in msg_ids[-50:]:  # Last 50 messages (most recent)
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

            result["messages"].append({
                "id": msg_id.decode() if isinstance(msg_id, bytes) else msg_id,
                "subject": subject,
                "from": from_,
                "date": date_iso,
                "text": text[:300],
            })
            result["count"] += 1

        mail.logout()
        return result

    except Exception as e:
        return {"error": str(e), "messages": []}


def main():
    since = SINCE_TIMESTAMP if SINCE_TIMESTAMP else load_last_checked()

    if since:
        result = fetch_new_messages(since)
    else:
        # First run - check all recent messages
        result = fetch_new_messages()

    # Update last checked timestamp
    if result.get("count", 0) > 0:
        if result.get("messages"):
            newest = result["messages"][0].get("date", "")
            save_last_checked(newest)

    print(json.dumps(result, indent=2))

    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
    elif result.get("count", 0) > 0:
        print(f"NOTIFICATION: {result['count']} new message(s) found", file=sys.stderr)
    else:
        print("NOTIFICATION: No new messages", file=sys.stderr)


if __name__ == "__main__":
    main()
