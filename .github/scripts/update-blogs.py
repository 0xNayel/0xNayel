#!/usr/bin/env python3
"""Scrape the 5 most-viewed posts from 0xnayel.com and splice them into README.md."""

import html
import pathlib
import re
import sys
import urllib.request

URL = "https://0xnayel.com/?sort=views"
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TOP_N = 5
START = "<!-- BLOG-LIST:START -->"
END = "<!-- BLOG-LIST:END -->"
README = pathlib.Path("README.md")

req = urllib.request.Request(URL, headers={"User-Agent": UA})
with urllib.request.urlopen(req, timeout=30) as resp:
    page = resp.read().decode("utf-8", errors="replace")

card_re = re.compile(
    r'<article class="blog-card".*?'
    r'<span class="blog-views"><i[^>]*></i>\s*(\d+)\s*</span>.*?'
    r'<h2 class="blog-card-title"><a href="(/publications/[^"]+)">([^<]+)</a>',
    re.DOTALL,
)
matches = card_re.findall(page)[:TOP_N]
if not matches:
    sys.exit("No posts parsed — the site layout may have changed.")

lines = [
    f"- [{html.unescape(title).strip()}](https://0xnayel.com{href}) · {views} views"
    for views, href, title in matches
]
block = START + "\n" + "\n".join(lines) + "\n" + END

text = README.read_text(encoding="utf-8")
new = re.sub(
    re.escape(START) + r".*?" + re.escape(END),
    lambda _: block,
    text,
    flags=re.DOTALL,
)

if new == text:
    print("No changes.")
else:
    README.write_text(new, encoding="utf-8")
    print(f"README updated with {len(matches)} posts.")
