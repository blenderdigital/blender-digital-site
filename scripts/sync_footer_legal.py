from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

LEGAL_LIST_PATTERNS = [
    r'\s*<li><a href="/?terms-of-service">Terms of Service</a></li>',
    r'\s*<li><a href="/?privacy-policy">Privacy Policy</a></li>',
    r'\s*<li><a href="/?privacy-policy\?tab=fulfillment">Fulfillment Policy</a></li>',
]

FOOTER_BOTTOM = '''<div class="footer-bottom"><div class="container footer-bottom-inner"><div class="small footer-copyright">© 2026 Blender Digital</div><nav class="footer-legal-links" aria-label="Legal"><a href="/terms-of-service">Terms of Service</a><a href="/privacy-policy">Privacy Policy</a></nav></div></div>'''

FOOTER_CSS = '''
    /* Shared legal footer row */
    .footer-bottom-inner{display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:nowrap}
    .footer-copyright{width:auto!important;flex:0 0 auto;text-align:left!important}
    .footer-legal-links{display:flex;align-items:center;justify-content:flex-end;gap:22px;margin-left:auto;font-size:.82rem;font-weight:500}
    .footer-legal-links a{padding:0;text-decoration:none}
    .footer-legal-links a:hover{text-decoration:underline;text-underline-offset:4px}
    @media (max-width:680px){.footer-bottom-inner{flex-direction:column;align-items:flex-start;gap:12px}.footer-legal-links{justify-content:flex-start;flex-wrap:wrap;gap:10px 18px;margin-left:0}}
'''


def replace_balanced_div(html: str, marker: str, replacement: str) -> tuple[str, bool]:
    start = html.find(marker)
    if start == -1:
        return html, False

    token_re = re.compile(r'<div\b|</div>', re.I)
    depth = 0
    for match in token_re.finditer(html, start):
        token = match.group(0).lower()
        if token.startswith('<div'):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = match.end()
                return html[:start] + replacement + html[end:], True
    return html, False


def remove_balanced_div(html: str, marker: str) -> tuple[str, bool]:
    return replace_balanced_div(html, marker, '')


def update_file(path: Path) -> bool:
    html = path.read_text(encoding='utf-8')
    if '<footer' not in html or 'footer-bottom' not in html:
        return False

    original = html

    for pattern in LEGAL_LIST_PATTERNS:
        html = re.sub(pattern, '', html, flags=re.I)

    # Remove the older standalone legal strip so there is only one legal row.
    while 'id="sitewide-legal-links"' in html:
        start = html.find('<div id="sitewide-legal-links"')
        marker_end = html.find('>', start)
        marker = html[start:marker_end + 1]
        html, removed = remove_balanced_div(html, marker)
        if not removed:
            break

    html, replaced = replace_balanced_div(html, '<div class="footer-bottom">', FOOTER_BOTTOM)
    if not replaced:
        html, replaced = replace_balanced_div(html, "<div class='footer-bottom'>", FOOTER_BOTTOM)

    if '/* Shared legal footer row */' not in html:
        style_close = html.rfind('</style>')
        if style_close != -1:
            html = html[:style_close] + FOOTER_CSS + html[style_close:]

    if html != original:
        path.write_text(html, encoding='utf-8')
        return True
    return False


changed = []
for path in ROOT.rglob('*.html'):
    if '.git' in path.parts:
        continue
    if update_file(path):
        changed.append(str(path.relative_to(ROOT)))

print(f'Updated {len(changed)} HTML files')
for item in changed:
    print(item)
