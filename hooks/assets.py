"""Build assets and authorize only the exact inline styles and scripts."""
import base64
import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
STYLES = ("fonts.css", "home.css", "blog.css", "post.css", "theme.css", "navigation.css", "legal.css", "email-contact.css")
SCRIPTS = ("theme.js", "navigation.js", "cookie-settings.js", "email-contact.js")


def on_page_content(html, **kwargs):
    """Give content email links the same choices as the shared footer."""
    def mark_contact(match):
        anchor = match.group(0)
        if "data-email-contact" not in anchor:
            anchor = anchor.replace("<a ", "<a data-email-contact ", 1)
        # This is the public business contact; its own dialog needs no decoder.
        return "<!--email_off-->" + anchor + "<!--/email_off-->"

    return re.sub(r'<a\s[^>]*href="mailto:virtusoptio@gmail\.com"[^>]*>.*?</a>', mark_contact, html, flags=re.S)


def sha256(value):
    return base64.b64encode(hashlib.sha256(value.encode()).digest()).decode()


class StructuredDataHashes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.block = None
        self.hashes = set()

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type") == "application/ld+json":
            self.block = ""

    def handle_data(self, data):
        if self.block is not None:
            self.block += data

    def handle_endtag(self, tag):
        if tag == "script" and self.block is not None:
            self.hashes.add(sha256(self.block))
            self.block = None


def on_config(config):
    css = "\n".join((ROOT / "docs/stylesheets" / name).read_text() for name in STYLES)
    fingerprint = hashlib.sha256(css.encode()).hexdigest()[:12]
    init = (ROOT / "docs/javascripts/theme-init.js").read_text().strip()
    config.extra["site_css"] = f"stylesheets/site-{fingerprint}.css"
    # Inline the small bundle to avoid a render-blocking network round trip.
    # CSS URLs now resolve from each HTML page, rather than /stylesheets/.
    base_path = urlsplit(config.site_url).path.rstrip("/")
    config.extra["site_styles"] = css.replace("../assets/", f"{base_path}/assets/").strip()
    js = "\n".join((ROOT / "docs/javascripts" / name).read_text() for name in SCRIPTS)
    js_fingerprint = hashlib.sha256(js.encode()).hexdigest()[:12]
    config.extra["site_js"] = f"javascripts/site-{js_fingerprint}.js"
    config.extra["theme_init"] = init
    return config


def on_post_build(config):
    site = Path(config.site_dir)
    css = "\n".join((ROOT / "docs/stylesheets" / name).read_text() for name in STYLES)
    (site / config.extra["site_css"]).write_text(css)
    js = "\n".join((ROOT / "docs/javascripts" / name).read_text() for name in SCRIPTS)
    (site / config.extra["site_js"]).write_text(js)
    structured = StructuredDataHashes()
    for page in site.rglob("*.html"):
        structured.feed(page.read_text())
    headers = site / "_headers"
    headers.write_text(headers.read_text()
                      .replace("THEME_INIT_HASH", sha256(config.extra["theme_init"]))
                      .replace("SITE_STYLE_HASH", sha256(config.extra["site_styles"]))
                      .replace("STRUCTURED_DATA_HASHES", " ".join(f"'sha256-{digest}'" for digest in sorted(structured.hashes))))
