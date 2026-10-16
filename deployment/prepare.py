"""Build the approved static homepage and its Cloudflare asset manifest."""
from pathlib import Path
from html.parser import HTMLParser
import base64
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, quote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'homepage'
SITE = ROOT / '_cloudflare_site'
PRIVATE = ROOT / 'deployment' / '.private'
ORIGIN = 'https://scottlu.top'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.noindex = False
        self.references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name', '').lower() == 'robots':
            self.noindex = 'noindex' in attrs.get('content', '').lower()
        for key in ('src', 'href'):
            if attrs.get(key):
                self.references.append(attrs[key])

def prepare():
    assert (SOURCE / 'index.html').is_file(), 'Missing approved homepage source'
    # Clear only the known generated directory, so retired assets cannot leak into a release.
    assert SITE.resolve() == ROOT.resolve() / '_cloudflare_site'
    assert not SITE.is_symlink()
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    for file in SOURCE.rglob('*'):
        if file.is_symlink():
            raise ValueError(f'Symlink not allowed: {file}')
        if file.is_file():
            if file.suffix.lower() not in {'.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.ico', '.pdf'}:
                raise ValueError(f'Unexpected public file: {file}')
            if file.stat().st_size > 25 * 1024 * 1024:
                raise ValueError(f'Asset exceeds static size limit: {file}')
            destination = SITE / file.relative_to(SOURCE)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, destination)

    urls = set()
    for file in SITE.rglob('*.html'):
        page = Page()
        page.feed(file.read_text(encoding='utf-8-sig'))
        for reference in page.references:
            link = urlsplit(reference)
            if link.scheme or link.netloc or not link.path:
                continue
            target = SITE / link.path.lstrip('/') if link.path.startswith('/') else file.parent / link.path
            assert target.resolve().is_relative_to(SITE.resolve()), f'Outside public directory: {reference}'
            assert target.is_file(), f'Broken local reference in {file.name}: {reference}'
        if not page.noindex:
            relative = file.relative_to(SITE).as_posix()
            path = '/' if relative == 'index.html' else '/' + relative.removesuffix('.html')
            urls.add(ORIGIN + quote(path, safe='/'))
    assert ORIGIN + '/' in urls, 'Homepage must remain indexable'
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    sitemap = ET.Element(f'{{{ns}}}urlset')
    for url in sorted(urls):
        ET.SubElement(ET.SubElement(sitemap, f'{{{ns}}}url'), f'{{{ns}}}loc').text = url
    ET.ElementTree(sitemap).write(SITE / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (SITE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n', encoding='utf-8')
    metadata = json.loads((ROOT / 'deployment/metadata.json').read_text())
    (SITE / '_redirects').write_text(metadata['assets']['config']['_redirects'], encoding='utf-8')
    manifest = {}
    for file in sorted(SITE.rglob('*')):
        if not file.is_file() or file.name in {'_headers', '_redirects'}:
            continue
        content = file.read_bytes()
        digest = hashlib.sha256(base64.b64encode(content) + file.suffix[1:].encode()).hexdigest()[:32]
        manifest['/' + file.relative_to(SITE).as_posix()] = {'hash': digest, 'size': len(content)}
    PRIVATE.mkdir(exist_ok=True)
    (PRIVATE / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    print(f'Prepared {len(manifest)} assets and {len(urls)} canonical sitemap URLs; local links validated')

if __name__ == '__main__':
    prepare()
