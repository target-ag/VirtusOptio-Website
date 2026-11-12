"""Render Dutch static pages from a reviewed, source-keyed translation catalog.

English is canonical at the root. No browser translation service, cookies or
redirects are used. Missing translations stop the build instead of silently
publishing mixed-language pages. Source text remains the lookup key so edits
cannot accidentally retain a stale translation.
"""
import gzip
import hashlib
import json
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
import xml.etree.ElementTree as ET

from mkdocs.plugins import event_priority

ROOT = Path(__file__).resolve().parent.parent
TRANSLATED_ATTRIBUTES = {'alt', 'aria-label', 'title', 'placeholder'}
TRANSLATED_META = {'description', 'og:title', 'og:description', 'og:image:alt',
                   'twitter:title', 'twitter:description', 'twitter:image:alt'}


class DutchPage(HTMLParser):
    def __init__(self, catalog, page_url, page_paths, script_path):
        super().__init__(convert_charrefs=True)
        self.catalog, self.page_url, self.page_paths = catalog, page_url, page_paths
        self.script_path = script_path
        self.parts, self.missing = [], set()
        self.raw_tag = None
        self.json_ld = False
        self.raw_text = ''
        self.svg_depth = 0

    def translate(self, value):
        key = value.strip()
        if not key or not re.search('[A-Za-z]', key):
            return value
        if key not in self.catalog:
            # Public contact values are configuration, not translatable prose.
            if re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', key):
                return value
            self.missing.add(key)
            return value
        return value[:len(value)-len(value.lstrip())] + self.catalog[key] + value[len(value.rstrip()):]

    def local_url(self, value, *, resource=False):
        if value.startswith('#'):
            return value
        absolute = urljoin(self.page_url, value)
        parsed = urlsplit(absolute)
        if parsed.scheme not in {'http', 'https'} or parsed.netloc != urlsplit(self.page_url).netloc:
            return value
        path = parsed.path
        if path.startswith("/assets/blog/three-ways-grow-business-") and "-nl-" not in path:
            path = path.replace("three-ways-grow-business-", "three-ways-grow-business-nl-")
        if not resource and path in self.page_paths:
            path = '/nl' + path
        return urlunsplit(('', '', path, parsed.query, parsed.fragment))

    def structured(self, value, key=None):
        if isinstance(value, list):
            return [self.structured(item, key) for item in value]
        if isinstance(value, dict):
            return {k:self.structured(v,k) for k,v in value.items()}
        if not isinstance(value, str): return value
        if key == 'inLanguage': return 'nl'
        if key in {'description', 'headline', 'articleSection'}: return self.translate(value)
        if key in {'url', '@id', 'image'} and urlsplit(value).netloc == urlsplit(self.page_url).netloc:
            # Keep shared entity IDs stable; localize page and article references.
            if key == '@id' and urlsplit(value).fragment in {'organization','person','website'}:return value
            return urljoin(self.page_url,self.local_url(value))
        return value

    def handle_starttag(self, tag, attrs):
        if tag == 'svg' or self.svg_depth:
            if tag == 'svg':self.svg_depth += 1
            self.parts.append(self.get_starttag_text());return
        attributes=dict(attrs)
        if tag in {'script','style'}:
            self.raw_tag=tag
            self.raw_text=''
            self.json_ld=tag=='script' and attributes.get('type')=='application/ld+json'
        rewritten=[]
        is_language_link=attributes.get('hreflang') in {'en','nl'} and tag=='a'
        for name,value in attrs:
            if value is None:rewritten.append(name);continue
            if tag=='html' and name=='lang':value='nl'
            elif name in TRANSLATED_ATTRIBUTES:value=self.translate(value)
            elif tag=='meta' and name=='content':
                kind=attributes.get('name') or attributes.get('property')
                if kind in TRANSLATED_META:value=self.translate(value)
                elif kind=='og:locale':value='nl_NL'
                elif kind=='og:url':value=urljoin(self.page_url,self.local_url(value))
                elif kind in {'og:image','twitter:image'}:
                    parsed=urlsplit(value)
                    filename=Path(parsed.path).name
                    candidate='assets/social/nl-'+filename
                    if not (ROOT/'docs'/candidate).exists():candidate='assets/social/nl-default.jpg'
                    value=urljoin(self.page_url,'/'+candidate)
            elif name=='href':
                if is_language_link:
                    if attributes['hreflang']=='en':value=urlsplit(self.page_url).path
                    else:value='/nl'+urlsplit(self.page_url).path
                elif tag=='link' and attributes.get('rel')=='alternate':pass
                elif tag=='link' and attributes.get('rel')=='canonical':value=urljoin(self.page_url,self.local_url(value))
                else:value=self.local_url(value,resource=tag=='link')
            elif name=='src':
                value='/'+self.script_path if tag=='script' else self.local_url(value,resource=True)
            elif name=='srcset':
                value=', '.join(' '.join([self.local_url(part.strip().split()[0],resource=True)]+part.strip().split()[1:]) for part in value.split(','))
            elif name=='aria-current' and is_language_link:
                continue
            rewritten.append(f'{name}="{escape(value,quote=True)}"')
        if is_language_link and attributes['hreflang']=='nl':rewritten.append('aria-current="page"')
        self.parts.append('<'+tag+(' '+' '.join(rewritten) if rewritten else '')+'>')

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        self.parts[-1]=self.parts[-1][:-1]+' />'

    def handle_endtag(self,tag):
        if self.svg_depth:
            self.parts.append('</'+tag+'>')
            if tag=='svg':self.svg_depth-=1
            return
        if self.raw_tag==tag:
            text=self.raw_text
            if self.json_ld:
                text=json.dumps(self.structured(json.loads(text)),ensure_ascii=True,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
            self.parts.append(text)
            self.raw_tag=None
        self.parts.append('</'+tag+'>')

    def handle_data(self,text):
        if self.raw_tag:self.raw_text+=text
        elif self.svg_depth:self.parts.append(text)
        else:self.parts.append(escape(self.translate(text),quote=False))

    def handle_comment(self,text):self.parts.append('<!--'+text+'-->')
    def handle_decl(self,text):self.parts.append('<!'+text+'>')


@event_priority(-150)
def on_post_build(config):
    site=Path(config.site_dir)
    catalog=json.loads((ROOT/'translations/nl.json').read_text())
    ui=json.loads((ROOT/'translations/nl-ui.json').read_text())
    js=config.extra['site_script_source']
    for en,nl in ui.items():
        # Only replace complete quoted UI literals, never selectors or keys.
        js=js.replace(json.dumps(en),json.dumps(nl,ensure_ascii=True))
    fingerprint=hashlib.sha256(js.encode()).hexdigest()[:12]
    script_path=f'javascripts/site-nl-{fingerprint}.js'
    (site/script_path).write_text(js)
    pages=sorted(p for p in site.rglob('*.html') if 'nl' not in p.relative_to(site).parts)
    paths={'/'+p.relative_to(site).as_posix().removesuffix('index.html') for p in pages}
    missing=set()
    for page in pages:
        relative=page.relative_to(site)
        path='/'+relative.as_posix().removesuffix('index.html')
        en_url=urljoin(config.site_url,path)
        nl_url=urljoin(config.site_url,'/nl'+path)
        source=page.read_text()
        alternate=(f'<link rel="alternate" hreflang="en" href="{escape(en_url)}">\n'
                   f'<link rel="alternate" hreflang="nl" href="{escape(nl_url)}">\n'
                   f'<link rel="alternate" hreflang="x-default" href="{escape(en_url)}">\n')
        source=source.replace('</head>',alternate+'</head>')
        switch=(f'<nav class="language-switch" aria-label="Language">'
                f'<a href="{path}" hreflang="en" lang="en" aria-current="page" title="View this page in English">EN</a>'
                f'<span aria-hidden="true">/</span>'
                f'<a href="/nl{path}" hreflang="nl" lang="nl" title="View this page in Dutch">NL</a></nav>')
        source=source.replace('<!--LANGUAGE_SWITCH-->',switch)
        page.write_text(source)
        parser=DutchPage(catalog,en_url,paths,script_path)
        parser.feed(source)
        parser.close()
        missing.update(parser.missing)
        target=site/'nl'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(''.join(parser.parts))
    if missing:
        (ROOT/'.cache/missing-translations.json').write_text(json.dumps(sorted(missing),ensure_ascii=False,indent=2))
        raise ValueError(f'{len(missing)} Dutch translations are missing; see .cache/missing-translations.json')
    # Every indexed English URL gets an indexed Dutch counterpart. Non-indexed
    # category/archive pages keep their noindex metadata and stay out of both.
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    tree=ET.parse(site/'sitemap.xml')
    for item in list(tree.getroot()):
        copied=ET.fromstring(ET.tostring(item))
        loc=copied.find('s:loc',ns)
        loc.text=urljoin(config.site_url,'/nl'+urlsplit(loc.text).path)
        tree.getroot().append(copied)
    tree.write(site/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    (site/'sitemap.xml.gz').write_bytes(gzip.compress((site/'sitemap.xml').read_bytes(),mtime=0))
    manifest=ROOT/'.cache/social-cards.json'
    cards=json.loads(manifest.read_text())
    cards.extend([{'key':'nl-'+c['key'],'title':catalog[c['title']],'lang':'nl'} for c in list(cards)])
    manifest.write_text(json.dumps(cards,ensure_ascii=False))
