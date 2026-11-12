import os, re

roots = ["/home/ubuntu/.hermes/hermes-agent"]
hits = []
for root in roots:
    for dirpath, dirnames, filenames in os.walk(root):
        if "node_modules" in dirpath or ".git" in dirpath:
            continue
        for f in filenames:
            if f.endswith(".py"):
                p = os.path.join(dirpath, f)
                try:
                    sz = os.path.getsize(p)
                except Exception:
                    continue
                if sz > 200000:
                    continue
                try:
                    txt = open(p, encoding="utf-8", errors="ignore").read()
                except Exception:
                    continue
                if re.search(r"AGENTMAIL_INBOX|env.*job|job.*env|injections", txt, re.I):
                    hits.append((p, txt))

for p, txt in hits:
    print("=====", p)
    # print lines mentioning env/job
    for i, line in enumerate(txt.splitlines(), 1):
        if re.search(r"env|AGENTMAIL_INBOX|job_config|injection", line, re.I):
            print(f"{i}: {line[:140]}")
