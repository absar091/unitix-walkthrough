import urllib.request
import re

url = "https://www.uhs.edu.pk/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
try:
    r = urllib.request.urlopen(req, timeout=20)
    data = r.read()
    print("STATUS", r.status)
    print("CT", r.headers.get("Content-Type"))
    txt = data.decode("utf-8", errors="replace")
    print("LEN", len(txt))
    open("/home/ubuntu/.hermes/cache/uhs_page.html", "w").write(txt)
    # extract title
    m = re.search(r"<title>(.*?)</title>", txt, re.S)
    print("TITLE", m.group(1).strip() if m else None)
    # extract visible text snippets
    body = re.search(r"<body.*?</body>", txt, re.S)
    if body:
        b = body.group(0)
        # strip scripts/styles
        b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
        b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
        # grab card/alerts
        cards = re.findall(r'alert alert-danger', b)
        print("CARDS(aler-danger)", len(cards))
        # find links
        links = re.findall(r'<a[^>]*>(.*?)</a>', b, re.S)
        seen = []
        for ln in links:
            t = re.sub(r"<[^>]+>", "", ln).strip()
            if t and len(t) < 120:
                seen.append(t)
        print("LINKS:", seen)
except Exception as e:
    print("ERR", repr(e))
