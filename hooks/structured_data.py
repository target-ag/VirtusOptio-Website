"""Describe visible site and article facts as safely embedded JSON-LD.

Google references:
https://developers.google.com/search/docs/appearance/structured-data/organization
https://developers.google.com/search/docs/appearance/structured-data/article
https://developers.google.com/search/docs/appearance/site-names
"""

import json
from datetime import date, datetime
from urllib.parse import urljoin, urlsplit

from material.plugins.blog.structure import Post


AUTHOR_NAME = "Mark Deniel"
AUTHOR_URL = "https://www.linkedin.com/in/mark-d-819a57224/"
LOGO_PATH = "assets/brand/virtus-optio-logo-640.webp"


def _absolute_url(value, base):
    """Accept public HTTP(S) references, including site-relative asset paths."""
    if not isinstance(value, str) or not value.strip():
        return None
    result = urljoin(base, value.strip())
    parsed = urlsplit(result)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    return result


def _date_text(value):
    """Retain the supplied date precision rather than invent a publication time."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, str):
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return value
        except ValueError:
            pass
    return None


def _publisher(config, base):
    return {
        "@type": "Organization",
        "@id": base + "#organization",
        "name": config.site_name,
        "url": base,
        "logo": urljoin(base, LOGO_PATH),
    }


def _homepage(config, base):
    organization = _publisher(config, base)
    organization.update({
        "description": config.site_description,
        "email": "virtusoptio@gmail.com",
        "contactPoint": {
            "@type": "ContactPoint",
            "url": "https://wa.me/31616125169",
            "telephone": "+31616125169",
        },
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "KVK",
            "value": "95111492",
        },
    })
    return {
        "@context": "https://schema.org",
        "@graph": [
            organization,
            {
                "@type": "WebSite",
                "@id": base + "#website",
                "name": config.site_name,
                "url": base,
                "inLanguage": "en",
                "publisher": {"@id": base + "#organization"},
            },
        ],
    }


def _article(page, config, base):
    meta = page.meta
    canonical = _absolute_url(page.canonical_url or page.url, base)
    author_name = meta.get("author_name") or AUTHOR_NAME
    author = {"@type": "Person", "name": author_name}
    author_url = _absolute_url(meta.get("author_url"), base)
    if author_url or author_name == AUTHOR_NAME:
        author["url"] = author_url or AUTHOR_URL
    article = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "@id": canonical + "#article",
        "url": canonical,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "headline": page.title,
        "inLanguage": "en",
        "author": author,
        "publisher": _publisher(config, base),
    }
    if meta.get("description"):
        article["description"] = meta["description"]

    dates = meta.get("date")
    created = dates.get("created") if isinstance(dates, dict) else dates
    updated = dates.get("updated") if isinstance(dates, dict) else None
    for key, value in (("datePublished", created), ("dateModified", updated)):
        normalized = _date_text(value)
        if normalized:
            article[key] = normalized

    categories = [category.title for category in page.categories]
    if categories:
        article["articleSection"] = categories

    # Only an explicitly supplied article image is used; the logo or portrait
    # would misrepresent an article that has no relevant image of its own.
    cover = meta.get("cover")
    image = meta.get("image") or (cover.get("src") if isinstance(cover, dict) else None)
    references = image if isinstance(image, list) else [image]
    images = [url for item in references if (url := _absolute_url(item, base))]
    if images:
        article["image"] = images
    return article


def on_page_context(context, *, page, config, nav):
    """Keep JSON-LD local to each page; never mutate shared config per page."""
    context["structured_data"] = ""
    base = _absolute_url(config.site_url, config.site_url or "")
    if not base:
        return context
    base = base.rstrip("/") + "/"

    if page.file.src_uri == "index.md":
        data = _homepage(config, base)
    elif isinstance(page, Post) and not page.config.draft:
        data = _article(page, config, base)
    else:
        return context

    # Escaping '<' prevents metadata containing </script> from ending the data
    # block. JSON escapes preserve the decoded values and deterministic CSP hash.
    serialized = json.dumps(data, ensure_ascii=True, separators=(",", ":"))
    context["structured_data"] = serialized.replace("<", "\\u003c").replace(
        ">", "\\u003e"
    ).replace("&", "\\u0026")
    return context
