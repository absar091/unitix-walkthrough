#!/usr/bin/env python3
"""
Email Sender - Send emails on command via trigger file
Usage: 
  1. User says "email name@example.com about Your message" in chat
  2. Cron job (every 1m) checks for trigger file
  3. Script sends the email and clears the trigger
"""

import json
import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime

# Gmail config (from user-confirmed app password)
SENDER_EMAIL = os.environ.get("AGENTMAIL_INBOX_EMAIL", "ahmadraoabsar@gmail.com")
SENDER_PASSWORD = os.environ.get("AGENTMAIL_API_KEY", "")

# Trigger file location
TRIGGER_FILE = "/home/ubuntu/.hermes/cache/email_trigger.txt"
OUTPUT_FILE = "/home/ubuntu/.hermes/cache/email_result.json"

def send_email(recipient, body):
    """Send an email via Gmail SMTP."""
    try:
        # Derive subject from body
        subject = body[:50] if len(body) > 50 else body
        
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient
        msg["Subject"] = subject
        msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
        msg["X-Sent-At"] = datetime.now().isoformat()
        
        msg.attach(MIMEText(body, "plain", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()

        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "to": recipient,
            "subject": subject,
        }
        print(f"Email sent to {recipient}")
        return True
    except Exception as e:
        result = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }
        print(f"ERROR: {e}")
        return False

def read_trigger():
    """Read the trigger file and return recipient and body."""
    try:
        with open(TRIGGER_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return None
            # Format: "recipient|body" or "recipient body..."
            lines = content.split("\n", 1)
            recipient = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            return recipient, body
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Trigger read error: {e}")
        return None

def write_result(result):
    """Write the result to a file."""
    with open(OUTPUT_FILE, "w") as f:
        json.dump(result, f, indent=2)

def main():
    import json
    
    # Check for trigger file
    trigger = read_trigger()
    if not trigger:
        # No trigger, exit
        print("No trigger found, exiting.")
        return

    recipient, body = trigger
    if not recipient or not body:
        print("Invalid trigger format.")
        # Clear invalid trigger
        try:
            os.remove(TRIGGER_FILE)
        except:
            pass
        return

    print(f"Sending email to {recipient}...")
    success = send_email(recipient, body)
    
    # Clear trigger after processing
    try:
        os.remove(TRIGGER_FILE)
    except:
        pass

    # Write result
    result = {
        "status": "success" if success else "error",
        "timestamp": datetime.now().isoformat(),
        "recipient": recipient,
    }
    write_result(result)
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email.")

if __name__ == "__main__":
    main()
