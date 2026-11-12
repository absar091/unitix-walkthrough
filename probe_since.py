#!/usr/bin/env python3
import os, sys, imaplib

INBOX_EMAIL = os.environ.get("AGENTMAIL_INBOX_EMAIL", "ahmadraoabsar@gmail.com")
APP_PASSWORD = os.environ.get("AGENTMAIL_API_KEY", "")

mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=60)
try:
    mail.login(INBOX_EMAIL, APP_PASSWORD.replace(" ", ""))
    mail.select("INBOX")
    tests = [
        "ALL SINCE 07-Nov-2026 05:55:27 +0000",
        "ALL SINCE 07-Nov-2026 05:55:27 +00:00",
        "SINCE 07-Nov-2026 05:55:27 +0000",
        "SINCE 07-Nov-2026",
        "SINCE 07-Nov-2026 05:55:27",
        "SINCE 08-Nov-2026",
    ]
    for t in tests:
        status, messages = mail.search("UTF-8", t)
        print(f"TEST: {t!r}")
        print(f"  STATUS: {status}")
        print(f"  RESPONSE: {messages[0] if messages else 'None'}")
        print()
    mail.logout()
except Exception as e:
    print("ERROR:", e)
    try:
        mail.logout()
    except Exception:
        pass
