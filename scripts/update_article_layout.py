from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "blog"

STYLE_MARKER = "/* Wider editorial shell and standalone related resources */"
STYLE_BLOCK = r'''
    /* Wider editorial shell and standalone related resources */
    .blog-shell{max-width:1040px!important}
    .hero .blog-shell .lead{max-width:860px}
    .blog-body{padding:clamp(28px,4vw,50px)}
    .blog-body>.intro{max-width:780px}
    .blog-body>.section-block>p,
    .blog-body>.section-block>ul,
    .blog-body>.section-block>ol{max-width:780px}
    .related-resources-card{
      margin-top:48px;
      padding:clamp(26px,3.5vw,42px);
      background:var(--white,#fff);
      border:1px solid rgba(43,43,43,.08);
      border-radius:var(--radius,18px);
      box-shadow:var(--shadow,0 10px 30px rgba(0,0,0,.08));
    }
    .related-resources-card .section-block{margin:0;padding:0;border:0}
    .related-resources-card .section-head{margin-bottom:12px}
    .related-resources-card>p,
    .related-resources-card .section-block>p{max-width:760px;margin-bottom:20px}
    .related-resources-card .related-carousel-wrap{margin-top:18px}
    @media(max-width:560px){
      .blog-body{padding:22px}
      .related-resources-card{margin-top:30px;padding:22px}
    }
'''


def find_balanced_block(text: str, start: int, tag: str) -> tuple[int, int] | None:
    token_re = re.compile(rf'<{tag}\b|</{tag}>', re.I)
    depth = 0
    for match in token_re.finditer(text, start):
        token = match.group(0).lower()
        if token.startswith(f'<{tag}'):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return start, match.end()
    return None


def inject_styles(html: str) -> str:
    if STYLE_MARKER in html:
        start = html.find(STYLE_MARKER)
        style_end = html.find('</style>', start)
        if style_end != -1:
            block_start = html.rfind('\n', 0, start) + 1
            return html[:block_start] + STYLE_BLOCK + html[style_end:]
        return html

    style_close = html.rfind("</style>")
    if style_close == -1:
        return html
    return html[:style_close] + STYLE_BLOCK + html[style_close:]


def move_related_resources(html: str) -> str:
    article_match = re.search(r'<article\b[^>]*class=["\'][^"\']*\bblog-body\b[^"\']*["\'][^>]*>', html, re.I)
    if not article_match:
        return html

    article_bounds = find_balanced_block(html, article_match.start(), "article")
    if not article_bounds:
        return html
    article_start, article_end = article_bounds
    article_html = html[article_start:article_end]

    heading_match = re.search(r'<h2\b[^>]*>\s*More Resources\s*</h2>', article_html, re.I)
    if not heading_match:
        return html

    opening_re = re.compile(
        r'<(?P<tag>section|div)\b[^>]*class=["\'][^"\']*\bsection-block\b[^"\']*["\'][^>]*>',
        re.I,
    )
    candidates = list(opening_re.finditer(article_html[:heading_match.start()]))
    if not candidates:
        return html

    opening = candidates[-1]
    tag = opening.group('tag').lower()
    block_bounds = find_balanced_block(article_html, opening.start(), tag)
    if not block_bounds:
        return html
    rel_start, rel_end = block_bounds

    related_html = article_html[rel_start:rel_end]
    related_html = re.sub(
        r'<h2\b([^>]*)>\s*More Resources\s*</h2>',
        r'<h2 id="more-resources-heading"\1>More Resources</h2>',
        related_html,
        count=1,
        flags=re.I,
    )

    article_without_related = article_html[:rel_start] + article_html[rel_end:]
    standalone = (
        '\n      <section class="related-resources-card" aria-labelledby="more-resources-heading">\n'
        + related_html
        + '\n      </section>'
    )

    return html[:article_start] + article_without_related + standalone + html[article_end:]


def update(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    if "blog-body" not in html:
        return False
    original = html
    html = inject_styles(html)
    html = move_related_resources(html)
    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


changed = []
for path in BLOG_DIR.rglob("*.html"):
    if path.name in {"index.html", "blog.html"}:
        continue
    if update(path):
        changed.append(str(path.relative_to(ROOT)))

print(f"Updated {len(changed)} article files")
for item in changed:
    print(item)
