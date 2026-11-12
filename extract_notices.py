import re, html as H

html = open("/home/ubuntu/.hermes/cache/uhs_current.html", encoding="utf-8", errors="replace").read()

# Find each public-notice card (alert-danger box)
blocks = re.findall(r'<div class="card mb-3 mt-1 alert alert-danger">(.*?)</div>\s*(?=<div class="row">|<!-- |</body>)', html, re.S)

print("NUM NOTICE BLOCKS:", len(blocks))
for i, block in enumerate(blocks):
    title_m = re.search(r'<h3>(.*?)</h3>', block, re.S)
    title = H.unescape(re.sub(r'<[^>]+>', ' ', title_m.group(1))).strip() if title_m else ""
    title = re.sub(r'\s+', ' ', title)
    links = re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
    imgs = re.findall(r'<img[^>]*src="([^"]+)"', block)
    print(f"\n===== NOTICE {i} =====")
    print("TITLE:", title)
    for u, t in links:
        print(f"  LINK: {u}  ->  {H.unescape(t).strip()}")
    for u in imgs:
        print(f"  IMG: {u}")
