#!/usr/bin/env python3
"""Fixed gmail_monitor - uses date-only SINCE instead of datetime."""
import os
import sys
import json
import imaplib
import email
from email.header import decode_header, make_header
from datetime import datetime, timezone

INBOX_EMAIL = os.environ.get("AGENTMAIL_INBOX_EMAIL", "ahmadraoabsar@gmail.com")
APP_PASSWORD = os.environ.get("AGENTMAIL_API_KEY", "")
SINCE_TIMESTAMP = os.environ.get("AGENTMAIL_SINCE", "")

LAST_CHECKED_FILE = "/home/ubuntu/.hermes/cache/gmail_last_checked.txt"


def load_last_checked():
    try:
        with open(LAST_CHECKED_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_checked(timestamp):
    try:
        with open(LAST_CHECKED_FILE, "w") as f:
            f.write(timestamp)
    except Exception:
        pass


def get_since_param(since_timestamp=None):
    """Convert timestamp to IMAP SINCE parameter format.
    Gmail IMAP only accepts date-only SINCE; datetime with timezone fails.
    """
    if not since_timestamp:
        return None
    try:
        dt = datetime.fromisoformat(since_timestamp.replace("Z", "+00:00"))
        # Use date-only to avoid 'Could not parse command' error
        return dt.strftime("%d-%b-%Y")
    except Exception:
        return since_timestamp


def fetch_new_messages(since_timestamp=None):
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=60)
        mail.login(INBOX_EMAIL, APP_PASSWORD.replace(" ", ""))
        mail.select("INBOX")

        if since_timestamp:
            since_param = get_since_param(since_timestamp)
            status, messages = mail.search("UTF-8", "ALL SINCE " + since_param)
        else:
            status, messages = mail.search("UTF-8", "ALL")
        if status != "OK":
            mail.logout()
            return {"error": f"Search failed: {status}", "messages": []}

        msg_ids = messages[0].split()
        if not msg_ids:
            mail.logout()
            return {"count": 0, "messages": []}

        result = {"count": 0, "messages": []}
        for msg_id in msg_ids[-50:]:
            status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            msg_raw = msg_data[0][1]
            msg = email.message_from_bytes(msg_raw)

            subject = str(make_header(decode_header(msg.get("Subject", ""))))
            from_ = msg.get("From", "")
            date = msg.get("Date", "")
            try:
                date_parsed = parsedate_to_datetime(date)
                date_iso = date_parsed.isoformat()
            except Exception:
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

            result["messages"].append(
                {
                    "id": msg_id.decode()
                    if isinstance(msg_id, bytes)
                    else msg_id,
                    "subject": subject,
                    "from": from_,
                    "date": date_iso,
                    "text": text[:300],
                }
            )
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
        result = fetch_new_messages()

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
