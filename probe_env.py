import sys
print("python:", sys.executable)
print("version:", sys.version)
try:
    import agentmail
    print("agentmail module:", agentmail.__file__)
except Exception as e:
    print("agentmail import failed:", e)

import os
print("AGENTMAIL_INBOX_EMAIL set:", bool(os.environ.get("AGENTMAIL_INBOX_EMAIL")))
print("AGENTMAIL_API_KEY set:", bool(os.environ.get("AGENTMAIL_API_KEY")))
