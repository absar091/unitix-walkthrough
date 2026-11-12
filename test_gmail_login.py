#!/usr/bin/env python3
"""Test Gmail IMAP login with the configured app password."""
import imaplib
import os

INBOX_EMAIL = "ahmadraoabsar@gmail.com"
APP_PASSWORD = "gpil fcat asct rpai"

print("Testing IMAP login...")
print(f"Email: {INBOX_EMAIL}")
print(f"Password (with spaces removed): {APP_PASSWORD.replace(' ', '')}")

try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=60)
    mail.login(INBOX_EMAIL, APP_PASSWORD.replace(" ", ""))
    print("LOGIN SUCCESS")
    # Get a count of messages
    status, messages = mail.search('UTF-8', 'ALL')
    if status == "OK":
        count = len(messages[0].split())
        print(f"Total messages in INBOX: {count}")
    mail.logout()
    print("LOGOFF SUCCESS")
except Exception as e:
    print(f"LOGIN ERROR: {type(e).__name__}: {e}")
