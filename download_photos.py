#!/usr/bin/env python3
"""Saves every photo used by the website into an "images" folder and points all five pages at them.

How to use (on a computer):
  1. Put this file in the same folder as index.html, about.html, gallery.html, reviews.html, warranty.html
  2. Run:  python download_photos.py      (on Mac/Linux: python3 download_photos.py)
  3. Open index.html. Upload the whole folder (pages + images folder) to your host.
Backups of your pages are saved in a folder called "backup_pages"."""
import re, os, sys, shutil, urllib.request, urllib.parse

H = "https://white-hare-927448.hostingersite.com/wp-content/uploads/"
V = "https://vccustomhomes.com/wp-content/uploads/2025/05/"
PAGES = ["index.html", "about.html", "gallery.html", "reviews.html", "warranty.html"]
PAGES = [p for p in PAGES if os.path.exists(p)]
if not PAGES:
    sys.exit("Put this script in the same folder as the website pages, then run it again.")

os.makedirs("backup_pages", exist_ok=True)
for p in PAGES:
    if not os.path.exists(os.path.join("backup_pages", p)):
        shutil.copy(p, os.path.join("backup_pages", p))

pat = re.compile(r'https://(?:white-hare-927448\.hostingersite\.com|vccustomhomes\.com)/wp-content/uploads/[^"\'\s)<>]+?\.(?:webp|jpe?g|png)', re.I)
pages = {}
for p in PAGES:
    t = open(p, encoding="utf-8").read()
    t = re.sub(r'H\+"([^"]+)"', lambda m: '"' + H + m.group(1) + '"', t)
    t = re.sub(r'V\+"([^"]+)"', lambda m: '"' + V + m.group(1) + '"', t)
    pages[p] = t
urls = sorted({u for t in pages.values() for u in pat.findall(t)})
print(f"Found {len(urls)} photos.")
if "--list" in sys.argv:
    print("\n".join(urls)); sys.exit()

os.makedirs("images", exist_ok=True)
def fetch(url):
    req = urllib.request.Request(url.replace(" ", "%20"), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

saved = {}
for u in urls:
    name = urllib.parse.unquote(u.rsplit("/", 1)[1]).replace(" ", "-")
    other = u.replace("white-hare-927448.hostingersite.com", "vccustomhomes.com") if "hostingersite" in u else u.replace("vccustomhomes.com", "white-hare-927448.hostingersite.com")
    data = None
    for t in (u, other):
        try:
            data = fetch(t); break
        except Exception:
            pass
    if data:
        open(os.path.join("images", name), "wb").write(data)
        saved[u] = "images/" + urllib.parse.quote(name)
        print("saved", name)
    else:
        print("FAILED (left as a web link):", u)

for p, t in pages.items():
    for u, local in saved.items():
        t = t.replace(u, local)
    open(p, "w", encoding="utf-8").write(t)
print(f"\nDone: {len(saved)} of {len(urls)} photos saved to the images folder. Open index.html to check.")
