"""Build fingerprinted assets and authorize only the exact theme initializer."""
import base64
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLES = ("fonts.css", "home.css", "blog.css", "post.css", "theme.css", "navigation.css", "legal.css", "email-contact.css")
SCRIPTS = ("theme.js", "navigation.js", "cookie-settings.js", "email-contact.js")


def on_page_content(html, **kwargs):
    """Give content email links the same choices as the shared footer."""
    def mark_contact(match):
        anchor = match.group(0)
        if "data-email-contact" in anchor:
            return anchor
        return anchor.replace("<a ", "<a data-email-contact ", 1)

    return re.sub(r'<a\s[^>]*href="mailto:virtusoptio@gmail\.com"[^>]*>', mark_contact, html)


def on_config(config):
    css = "\n".join((ROOT / "docs/stylesheets" / name).read_text() for name in STYLES)
    fingerprint = hashlib.sha256(css.encode()).hexdigest()[:12]
    init = (ROOT / "docs/javascripts/theme-init.js").read_text().strip()
    config.extra["site_css"] = f"stylesheets/site-{fingerprint}.css"
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
    digest = base64.b64encode(hashlib.sha256(config.extra["theme_init"].encode()).digest()).decode()
    headers = site / "_headers"
    headers.write_text(headers.read_text().replace("THEME_INIT_HASH", digest))
