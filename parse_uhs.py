import re, html as h

with open("/home/ubuntu/.hermes/cache/uhs_current.html", "r", encoding="utf-8") as f:
    content = f.read()

# Split content into segments: notice cards and non-card content
# Each notice card: <div class="card mb-3 mt-1 alert alert-danger"> ... </div>
# Find all card blocks
card_pattern = re.compile(r'<div class="card mb-3 mt-1 alert alert-danger">(.*?)</div>(?:\s*</div>)?', re.DOTALL)
matches = card_pattern.findall(content)
print("Number of card blocks found:", len(matches))

def extract_text(s):
    s = re.sub(r'<script.*?</script>', ' ', s, flags=re.DOTALL)
    s = re.sub(r'<style.*?</style>', ' ', s, flags=re.DOTALL)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = re.sub(r'&amp;', '&', s)
    s = re.sub(r'&lt;', '<', s)
    s = re.sub(r'&gt;', '>', s)
    s = re.sub(r'&nbsp;', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

for idx, card in enumerate(matches, 1):
    print(f"\n=== NOTICE {idx} ===")
    # Title: h3
    h3 = re.search(r'<h3>(.*?)</h3>', card, re.DOTALL)
    if h3:
        print("TITLE:", extract_text(h3.group(1)))
    # Links
    links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', card, re.DOTALL)
    for href, text in links:
        print(f"  LINK: {href}")
        print(f"  TEXT: {extract_text(text)[:200]}")
