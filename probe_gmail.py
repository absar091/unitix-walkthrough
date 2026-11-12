#!/usr/bin/env python3
import os, sys, imaplib, email
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime

INBOX_EMAIL = os.environ.get("AGENTMAIL_INBOX_EMAIL", "ahmadraoabsar@gmail.com")
APP_PASSWORD = os.environ.get("AGENTMAIL_API_KEY", "")

mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, timeout=60)
try:
    mail.login(INBOX_EMAIL, APP_PASSWORD.replace(" ", ""))
    mail.select("INBOX")
    status, messages = mail.search("UTF-8", "ALL")
    print("STATUS:", status)
    parts = messages[0].split() if messages and messages[0] else []
    print("MSG_COUNT:", len(parts))
    if parts:
        print("LAST_10:", parts[-10:])
    for mid in parts[-1:]:
        status, msg_data = mail.fetch(mid, "(RFC822)")
        if status == "OK":
            raw = msg_data[0][1]
            msg = email.message_from_bytes(raw)
            subj = str(make_header(decode_header(msg.get("Subject", ""))))
            frm = msg.get("From", "")
            date = msg.get("Date", "")
            print("SUBJ:", repr(subj))
            print("FROM:", repr(frm))
            print("DATE:", repr(date))
    mail.logout()
except Exception as e:
    print("ERROR:", e)
    try:
        mail.logout()
    except Exception:
        pass
