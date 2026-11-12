"""Check built-page SEO, local links, published assets and crawl exclusions."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
import gzip
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent / 'site'
BASE = 'https://virtusoptio.com/'

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.meta, self.links, self.h1, self.canonical = path, {}, [], 0, None
    def handle_starttag(self, tag, pairs):
        a = dict(pairs)
        if tag == 'meta': self.meta[a.get('property') or a.get('name')] = a.get('content')
        if tag == 'h1': self.h1 += 1
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical = a.get('href')
        if tag in {'a', 'img', 'script', 'link'}:
            value = a.get('src') or a.get('href')
            if value: self.links.append(value)

errors=[]
pages=[]
for path in ROOT.rglob('*.html'):
    p=Page(path);p.feed(path.read_text());pages.append(p)
    relative=path.relative_to(ROOT).as_posix()
    url=urljoin(BASE,relative.removesuffix('index.html'))
    if p.h1 != 1: errors.append(f'{relative}: expected one H1, got {p.h1}')
    for key in ('description','og:title','og:description','og:image','og:url','twitter:card','twitter:image'):
        if not p.meta.get(key):errors.append(f'{relative}: missing {key}')
    image=urlsplit(p.meta.get('og:image',''))
    if image.netloc != 'virtusoptio.com' or not (ROOT/image.path.lstrip('/')).is_file():
        errors.append(f'{relative}: social image is missing or not absolute')
    if relative != '404.html' and p.canonical != url:
        errors.append(f'{relative}: unexpected canonical {p.canonical}')
    if 'cookie-notice"' in path.read_text(): errors.append(f'{relative}: obsolete cookie banner')
    if '<!-- more -->' in path.read_text():errors.append(f'{relative}: excerpt marker published')
    for value in p.links:
        parsed=urlsplit(urljoin(url,value))
        if parsed.scheme not in {'http','https'} or parsed.netloc != 'virtusoptio.com': continue
        target=ROOT/unquote(parsed.path).lstrip('/')
        if target.is_dir(): target=target/'index.html'
        if not target.is_file():errors.append(f'{relative}: broken local URL {value}')
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
sitemap=ROOT/'sitemap.xml'
urls={e.text for e in ET.parse(sitemap).findall('s:url/s:loc',ns)}
for p in pages:
    if 'noindex' in p.meta.get('robots','') and p.canonical in urls:
        errors.append(f'{p.path}: noindex URL is in sitemap')
for path in ('assets/brand/virtus-optio-logo.png','assets/fonts/SOURCES.txt','stylesheets/fonts.css','social-cards.json'):
    if (ROOT/path).exists():errors.append(f'Build-only asset published: {path}')
if gzip.decompress((ROOT/'sitemap.xml.gz').read_bytes()) != sitemap.read_bytes():
    errors.append('Compressed sitemap differs')
if not (ROOT/'.well-known/security.txt').is_file(): errors.append('security.txt missing')
if errors:raise SystemExit('\n'.join(errors))
print(f'Site checks passed: {len(pages)} pages, {len(urls)} indexed URLs, valid local links and social images.')
