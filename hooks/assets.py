"""Build shared, fingerprinted CSS and authorize only the exact theme initializer."""
import base64
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLES = ("fonts.css", "home.css", "blog.css", "post.css", "theme.css", "navigation.css", "legal.css", "email-contact.css")


def on_config(config):
    css = "\n".join((ROOT / "docs/stylesheets" / name).read_text() for name in STYLES)
    fingerprint = hashlib.sha256(css.encode()).hexdigest()[:12]
    init = (ROOT / "docs/javascripts/theme-init.js").read_text().strip()
    config.extra["site_css"] = f"stylesheets/site-{fingerprint}.css"
    config.extra["theme_init"] = init
    return config


def on_post_build(config):
    site = Path(config.site_dir)
    css = "\n".join((ROOT / "docs/stylesheets" / name).read_text() for name in STYLES)
    (site / config.extra["site_css"]).write_text(css)
    digest = base64.b64encode(hashlib.sha256(config.extra["theme_init"].encode()).digest()).decode()
    headers = site / "_headers"
    headers.write_text(headers.read_text().replace("THEME_INIT_HASH", digest))
