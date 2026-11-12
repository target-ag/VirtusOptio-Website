"""Page metadata and crawl hygiene for the custom MkDocs templates."""
import gzip
import json
import hashlib
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

from mkdocs.plugins import event_priority
from material.plugins.blog.structure import Post

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_URLS = set()
PUBLISHED_CATEGORIES = set()
SOCIAL_CARDS = []


def on_config(config):
    EXCLUDED_URLS.clear()
    SOCIAL_CARDS.clear()
    PUBLISHED_CATEGORIES.clear()
    return config


@event_priority(-100)
def on_nav(nav, *, config, files):
    for file in files:
        page = file.page
        if isinstance(page, Post) and not page.config.draft:
            PUBLISHED_CATEGORIES.update(page.meta.get('categories', []))
    return nav


@event_priority(-100)
def on_page_context(context, *, page, config, nav):
    meta = page.meta
    title = meta.get('seo_title') or f'{meta.get("title") or page.title} — {config.site_name}'
    if page.file.src_uri == 'index.md':
        title = f'{config.site_name} — Ethical Selling & Sales Systems'
    description = meta.get('description') or config.site_description
    is_archive = page.url.startswith('blog/archive/')
    category = meta.get('category')
    is_empty_category = category and category not in PUBLISHED_CATEGORIES
    if is_archive:
        description = f'Browse {getattr(page, "name", "") or "past"} articles from Virtus Optio on business growth, ethical selling and practical sales systems.'
    if is_empty_category:
        description = f'Explore the {category} topic and find related practical guidance in the Virtus Optio business blog.'
    noindex = bool(meta.get('noindex') or is_archive or is_empty_category)
    if noindex:
        EXCLUDED_URLS.add(page.canonical_url)
    image_key = hashlib.sha256(page.file.src_uri.encode()).hexdigest()[:12]
    SOCIAL_CARDS.append({"key": image_key, "title": title})
    image_path = f'assets/social/{image_key}.jpg'
    if not (ROOT / 'docs' / image_path).exists():
        image_path = 'assets/social/default.jpg'
    context['seo'] = {
        'title': title,
        'description': description,
        'url': page.canonical_url,
        'image': urljoin(config.site_url, image_path),
        'image_key': image_key,
        'type': 'article' if isinstance(page, Post) else 'website',
        'noindex': noindex,
    }
    context['published_categories'] = PUBLISHED_CATEGORIES
    return context


def on_env(env, *, config, files):
    env.globals['seo'] = {
        'title': 'Page not found — Virtus Optio',
        'description': 'Find your way back to Virtus Optio: ethical selling and practical sales systems.',
        'url': urljoin(config.site_url, '404.html'),
        'image': urljoin(config.site_url, 'assets/social/default.jpg'),
        'type': 'website',
        'noindex': True,
    }
    return env


@event_priority(-100)
def on_post_build(config):
    site = Path(config.site_dir)
    (ROOT / '.cache').mkdir(exist_ok=True)
    (ROOT / '.cache/social-cards.json').write_text(json.dumps(SOCIAL_CARDS))
    sitemap = site / 'sitemap.xml'
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    ET.register_namespace('', ns['s'])
    tree = ET.parse(sitemap)
    for item in list(tree.getroot()):
        loc = item.find('s:loc', ns)
        if loc is not None and loc.text in EXCLUDED_URLS:
            tree.getroot().remove(item)
    tree.write(sitemap, encoding='utf-8', xml_declaration=True)
    (site / 'sitemap.xml.gz').write_bytes(gzip.compress(sitemap.read_bytes(), mtime=0))
    for page in site.rglob('*.html'):
        text = page.read_text()
        page.write_text(re.sub(r'<!--\s*more\s*-->', '', text))
    target = site / '.well-known/security.txt'
    target.parent.mkdir(exist_ok=True)
    target.write_text((ROOT / 'docs/.well-known/security.txt').read_text().replace('virtusoptio@gmail.com', config.extra['contact_email']))
