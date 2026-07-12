from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NAV_HTML = '''<div class="nav-links" id="navMenu"><a href="/#services">How It Works</a><a href="/results.html">Results</a><details class="nav-dropdown"><summary>Resources</summary><div class="nav-dropdown-menu"><a href="/blog.html">Blog</a><a href="/tools">Tools</a></div></details><a href="/#pricing">Pricing</a><a href="/#faq">FAQs</a><a class="btn btn-ghost" href="/#contact">Contact</a></div>'''

FOOTER_HTML = '''<footer class="footer"><div class="footer-main"><div class="container footer-grid"><div class="footer-brand"><div style="display:flex;align-items:center;gap:10px;margin-bottom:10px"><span class="brand-badge"><img src="/Blender%20Digital%20Full%20Logo.svg" alt="Blender Digital logo" /></span></div><p class="small">We grow restaurant sales across DoorDash, Uber Eats, Grubhub, and Toast.</p></div><div><h4>How It Works</h4><ul class="small"><li><a href="/#services">Access &amp; plan</a></li><li><a href="/#services">Launch campaigns</a></li><li><a href="/#services">Manage &amp; improve</a></li><li><a href="/#services">Report &amp; grow</a></li></ul></div><div><h4>Resources</h4><ul class="small"><li><a href="/blog.html">Blog</a></li><li><a href="/tools">Tools</a></li><li><a href="/faq.html">Frequently asked questions</a></li><li><a href="/blog/why-your-uber-eats-promotions-are-destroying-your-margins.html">Uber Eats promo margins</a></li><li><a href="/blog/restaurant-delivery-platform-image-size-requirements.html">Image size requirements</a></li></ul></div><div><h4>Company</h4><ul class="small"><li><a href="/results.html">Results</a></li><li><a href="/#pricing">Pricing</a></li><li><a href="/#contact">Contact</a></li><li><a href="#top">Back to top</a></li></ul></div></div></div><div class="footer-bottom"><div class="container" style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap"><div class="small" style="text-align:center;width:100%">© 2026 Blender Digital</div></div></div></footer>'''

SHELL_STYLE = '''<style id="shared-site-shell">
.nav-dropdown{position:relative}
.nav-dropdown summary{list-style:none;display:flex;align-items:center;gap:7px;padding:10px 12px;border-radius:12px;cursor:pointer;font:inherit;color:inherit}
.nav-dropdown summary::-webkit-details-marker{display:none}
.nav-dropdown summary::after{content:'';width:7px;height:7px;border-right:1.5px solid currentColor;border-bottom:1.5px solid currentColor;transform:rotate(45deg);margin:-3px 1px 0 2px;transition:transform .18s ease,margin .18s ease}
.nav-dropdown[open] summary::after{transform:rotate(225deg);margin:3px 1px 0 2px}
.nav-dropdown summary:hover,.nav-dropdown[open] summary{background:rgba(255,255,255,.7)}
.nav-dropdown-menu{position:absolute;z-index:30;top:calc(100% + 8px);left:0;min-width:170px;padding:8px;background:var(--white,#fff);border:1px solid rgba(43,43,43,.09);border-radius:14px;box-shadow:var(--shadow,0 10px 30px rgba(0,0,0,.08))}
.nav-dropdown-menu a{display:block;white-space:nowrap;padding:10px 12px}
@media(max-width:820px){
  .nav-links{align-items:stretch}
  .nav-dropdown{width:100%}
  .nav-dropdown summary{width:100%;justify-content:space-between;padding:12px}
  .nav-dropdown-menu{position:static;min-width:0;margin-top:4px;padding:4px 0 0;background:transparent;border:0;border-radius:0;box-shadow:none}
  .nav-dropdown-menu a{padding:10px 12px 10px 28px}
}
</style>'''

DROPDOWN_SCRIPT = '''<script id="shared-nav-dropdown-script">
(function(){
  const dropdowns=[...document.querySelectorAll('.nav-dropdown')];
  dropdowns.forEach(dropdown=>dropdown.addEventListener('toggle',()=>{
    if(dropdown.open) dropdowns.forEach(other=>{if(other!==dropdown) other.removeAttribute('open')});
  }));
  document.addEventListener('click',event=>{
    dropdowns.forEach(dropdown=>{if(!dropdown.contains(event.target)) dropdown.removeAttribute('open')});
  });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape') dropdowns.forEach(dropdown=>dropdown.removeAttribute('open'));
  });
  document.addEventListener('click',event=>{
    if(event.target && event.target.closest('.nav-dropdown-menu a')) dropdowns.forEach(dropdown=>dropdown.removeAttribute('open'));
  });
})();
</script>'''

FOOTER_RE = re.compile(r'<footer\b[^>]*>.*?</footer>', re.IGNORECASE | re.DOTALL)
STYLE_RE = re.compile(r'<style\s+id=["\']shared-site-shell["\']>.*?</style>', re.IGNORECASE | re.DOTALL)
SCRIPT_RE = re.compile(r'<script\s+id=["\']shared-nav-dropdown-script["\']>.*?</script>', re.IGNORECASE | re.DOTALL)
BRAND_RE = re.compile(r'(<a\b[^>]*class=["\'][^"\']*\bbrand\b[^"\']*["\'][^>]*href=)["\'][^"\']*["\']', re.IGNORECASE)
NAV_DIV_START_RE = re.compile(r'<div\b(?=[^>]*\bclass=["\'][^"\']*\bnav-links\b[^"\']*["\'])(?=[^>]*\bid=["\']navMenu["\'])[^>]*>', re.IGNORECASE)
NAV_TAG_RE = re.compile(r'<nav\b(?=[^>]*\bclass=["\'][^"\']*\bnav-links\b[^"\']*["\'])(?=[^>]*\bid=["\']navMenu["\'])[^>]*>.*?</nav\s*>', re.IGNORECASE | re.DOTALL)
DIV_TOKEN_RE = re.compile(r'<div\b[^>]*>|</div\s*>', re.IGNORECASE)


def replace_nav_block(html: str) -> tuple[str, bool]:
    match = NAV_DIV_START_RE.search(html)
    if match:
        depth = 0
        end = None
        for token in DIV_TOKEN_RE.finditer(html, match.start()):
            if token.group(0).lower().startswith('</div'):
                depth -= 1
                if depth == 0:
                    end = token.end()
                    break
            else:
                depth += 1

        if end is None:
            raise RuntimeError('Could not find closing div for #navMenu')

        return html[: match.start()] + NAV_HTML + html[end:], True

    if NAV_TAG_RE.search(html):
        return NAV_TAG_RE.sub(NAV_HTML, html, count=1), True

    return html, False


def upsert_before_closing(html: str, pattern: re.Pattern[str], replacement: str, closing_tag: str) -> str:
    if pattern.search(html):
        return pattern.sub(replacement, html, count=1)
    index = html.lower().rfind(closing_tag.lower())
    if index == -1:
        raise RuntimeError(f'Missing {closing_tag}')
    return html[:index] + replacement + '\n' + html[index:]


def update_page(path: Path) -> bool:
    original = path.read_text(encoding='utf-8')
    html = original

    html, nav_found = replace_nav_block(html)
    footer_found = bool(FOOTER_RE.search(html))

    if not nav_found and not footer_found:
        return False

    html = BRAND_RE.sub(r'\1"/"', html)

    if footer_found:
        html = FOOTER_RE.sub(FOOTER_HTML, html, count=1)

    html = upsert_before_closing(html, STYLE_RE, SHELL_STYLE, '</head>')
    html = upsert_before_closing(html, SCRIPT_RE, DROPDOWN_SCRIPT, '</body>')

    if html == original:
        return False

    path.write_text(html, encoding='utf-8')
    return True


def main() -> None:
    updated: list[str] = []
    for path in sorted(ROOT.rglob('*.html')):
        if any(part.startswith('.') for part in path.relative_to(ROOT).parts):
            continue
        if update_page(path):
            updated.append(str(path.relative_to(ROOT)))

    print(f'Updated {len(updated)} HTML files')
    for path in updated:
        print(path)


if __name__ == '__main__':
    main()
