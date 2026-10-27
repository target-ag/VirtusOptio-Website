"""Check every generated HTML page against the site's script restrictions.

Run after a production or draft-preview build: python scripts/check_security.py site
This catches future posts/templates that would fail under the deployed CSP.
"""

from html.parser import HTMLParser
import base64
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit


class PageCheck(HTMLParser):
    def __init__(self, path, root, headers):
        super().__init__()
        self.path, self.root = path, root
        self.errors = []
        self.headers = headers
        self.inline_script = None
        self.inline_style = None
        self.script_type = None
        policy = next((line.split(":", 1)[1] for line in headers.splitlines()
                       if line.strip().startswith("Content-Security-Policy:")), "")
        self.directives = {parts[0]: parts[1:] for directive in policy.split(";")
                           if (parts := directive.split())}

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        for name, value in attributes:
            if name.startswith("on") or name == "style":
                self.errors.append(f"inline attribute {name} is blocked by CSP")
            if name in {"href", "src", "action"} and value:
                scheme = urlsplit(value.strip()).scheme.lower()
                if scheme in {"javascript", "vbscript"}:
                    self.errors.append(f"unsafe URL scheme in {name}")
        if tag == "script":
            src = attrs.get("src", "")
            if not src:
                self.inline_script = ""
                self.script_type = attrs.get("type", "")
            elif urlsplit(src).scheme or urlsplit(src).netloc:
                self.errors.append("script must be an external file on this site")
            else:
                script = (self.root / src.lstrip("/") if src.startswith("/")
                          else self.path.parent / src).resolve()
                if not script.is_relative_to(self.root.resolve()) or not script.is_file():
                    self.errors.append(f"script file is missing: {src}")
        if tag == "style":
            self.inline_style = ""
        if tag in {"iframe", "object", "embed", "form", "base"}:
            self.errors.append(f"{tag} requires an explicit security policy review")

    def handle_data(self, data):
        if self.inline_script is not None:
            self.inline_script += data
        if self.inline_style is not None:
            self.inline_style += data

    def handle_endtag(self, tag):
        if tag == "script" and self.inline_script is not None:
            digest = base64.b64encode(hashlib.sha256(self.inline_script.encode()).digest()).decode()
            if f"'sha256-{digest}'" not in self.directives.get("script-src", []):
                self.errors.append("inline script is not authorized by its exact CSP hash")
            if self.script_type == "application/ld+json":
                try:
                    json.loads(self.inline_script)
                except json.JSONDecodeError:
                    self.errors.append("structured data must be valid JSON")
            self.inline_script = None
        if tag == "style" and self.inline_style is not None:
            digest = base64.b64encode(hashlib.sha256(self.inline_style.encode()).digest()).decode()
            if f"'sha256-{digest}'" not in self.directives.get("style-src", []):
                self.errors.append("inline style is not authorized by its exact CSP hash")
            self.inline_style = None


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    headers = (root / "_headers").read_text()
    for required in ("script-src 'self'", "frame-ancestors 'none'",
                     "style-src-attr 'none'", "script-src-attr 'none'",
                     "X-Frame-Options: DENY", "X-Content-Type-Options: nosniff"):
        if required not in headers:
            raise SystemExit(f"Missing required protection: {required}")
    if "'unsafe-inline'" in headers or "'unsafe-eval'" in headers:
        raise SystemExit("CSP must not allow unrestricted inline code or eval")
    pages = list(root.rglob("*.html"))
    if not pages:
        raise SystemExit("No built HTML pages found")
    errors = []
    for path in pages:
        parser = PageCheck(path, root, headers)
        parser.feed(path.read_text())
        errors.extend(f"{path}: {error}" for error in parser.errors)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Security compatibility passed for {len(pages)} HTML pages.")


if __name__ == "__main__":
    main()
