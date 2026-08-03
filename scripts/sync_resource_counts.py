from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BLOG_COUNT = 22
TOOL_COUNT = 3

BLOG_PATTERN = re.compile(
    r'(<a\b[^>]*href=["\'](?:https://blenderdigital\.co)?/?blog(?:\.html)?["\'][^>]*>)(?:Blog|Blogs(?:\s*\(\d+\))?)(</a>)',
    re.I,
)
TOOL_PATTERN = re.compile(
    r'(<a\b[^>]*href=["\'](?:https://blenderdigital\.co)?/?tools/?["\'][^>]*>)(?:Tools(?:\s*\(\d+\))?)(</a>)',
    re.I,
)

changed = []
for path in ROOT.rglob("*.html"):
    if ".git" in path.parts:
        continue

    html = path.read_text(encoding="utf-8")
    original = html

    html = BLOG_PATTERN.sub(rf"\1Blogs ({BLOG_COUNT})\2", html)
    html = TOOL_PATTERN.sub(rf"\1Tools ({TOOL_COUNT})\2", html)

    if html != original:
        path.write_text(html, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

print(f"Updated {len(changed)} HTML files")
for item in changed:
    print(item)
