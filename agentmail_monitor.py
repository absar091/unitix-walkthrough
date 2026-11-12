#!/usr/bin/env python3
"""AgentMail inbox monitor - checks for new emails and outputs them as JSON.

Usage: python3 monitor_emails.py <inbox_email> <api_key>
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

from agentmail import AgentMail
from agentmail.inboxes import CreateInboxRequest


def get_env_var(name, required=True):
    """Get environment variable, fail if missing and required."""
    val = os.environ.get(name)
    if required and not val:
        print(f"ERROR: Missing required env var: {name}", file=sys.stderr)
        sys.exit(1)
    return val


def fetch_inbox_summary(inbox_id, api_key):
    """Fetch a summary of the inbox."""
    try:
        client = AgentMail(api_key=api_key)
        inbox = client.inboxes.get(inbox_id)
        return {
            "inbox_id": inbox.inbox_id,
            "display_name": inbox.display_name,
            "client_id": inbox.client_id,
            "created_at": inbox.created_at,
            "total_messages": len(inbox.messages) if hasattr(inbox, 'messages') else None
        }
    except Exception as e:
        print(f"ERROR: Failed to fetch inbox: {e}", file=sys.stderr)
        sys.exit(1)


def check_new_messages(inbox_id, api_key, since_timestamp=None):
    """Fetch new messages from the inbox.

    Args:
        inbox_id: The inbox ID
        api_key: The API key
        since_timestamp: Only return messages newer than this timestamp (ISO 8601)

    Returns:
        List of message dicts
    """
    try:
        client = AgentMail(api_key=api_key)
        result = client.inboxes.messages.search(inbox_id, limit=50)
        messages = []
        for msg in result.messages:
            msg_data = {
                "id": msg.id,
                "subject": msg.subject,
                "from": msg.from_,
                "to": msg.to,
                "cc": msg.cc,
                "date": msg.date,
                "text": msg.text,
                "html": msg.html,
                "labels": msg.labels,
            }
            messages.append(msg_data)

        # Filter by timestamp if provided
        if since_timestamp:
            cutoff = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
            messages = [m for m in messages if m["date"] > since_timestamp]

        return messages

    except Exception as e:
        print(f"ERROR: Failed to search messages: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    # Get credentials from environment
    inbox_email = get_env_var("AGENTMAIL_INBOX_EMAIL", required=True)
    api_key = get_env_var("AGENTMAIL_API_KEY", required=True)

    # Get optional since_timestamp from environment
    since_timestamp = get_env_var("AGENTMAIL_SINCE", required=False)

    # Inbox ID is the inbox email itself (agentmail.to uses the email as ID)
    inbox_id = inbox_email

    # Fetch summary
    summary = fetch_inbox_summary(inbox_id, api_key)
    print(json.dumps(summary, indent=2))

    # Fetch new messages
    if since_timestamp:
        new_messages = check_new_messages(inbox_id, api_key, since_timestamp)
    else:
        new_messages = check_new_messages(inbox_id, api_key)

    print(json.dumps({"messages": new_messages}, indent=2))

    if new_messages:
        print(f"NOTIFICATION: {len(new_messages)} new message(s) found", file=sys.stderr)
    else:
        print("NOTIFICATION: No new messages", file=sys.stderr)


if __name__ == "__main__":
    main()
