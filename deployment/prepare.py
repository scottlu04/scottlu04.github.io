"""Prepare the Jekyll build for Cloudflare Static Assets (standard library only)."""
from pathlib import Path
import base64
import hashlib
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, quote

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_cloudflare_site'
PRIVATE = ROOT / 'deployment' / '.private'
ORIGIN = 'https://scottlu.top'
GITHUB = 'https://scottlu04.github.io'

def prepare():
    assert (SITE / 'index.html').is_file(), 'Build Jekyll first'
    redirects = [f'/paper/dfcil.pdf {GITHUB}/paper/dfcil.pdf 302']
    for file in SITE.rglob('*'):
        if file.is_file() and file.stat().st_size > 25 * 1024 * 1024:
            path = '/' + file.relative_to(SITE).as_posix()
            # Only this existing public PDF is intentionally hosted by GitHub.
            if path != '/paper/dfcil.pdf':
                raise ValueError(f'Use media storage for oversized asset: {path}')
            file.unlink()
    # WAG is hosted independently; never claim a nonexistent local copy.
    redirects += ['/Wearable-As-Graph-WAG/ https://scottlu04.github.io/Wearable-As-Graph-WAG/ 301']
    (SITE / '_redirects').write_text('\n'.join(redirects) + '\n', encoding='utf-8')
    # Only canonical, present, public pages/documents belong in this sitemap.
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    source = ET.parse(SITE / 'sitemap.xml')
    urls = {ORIGIN + '/'}
    for loc in source.findall('.//{*}loc'):
        path = urlsplit(loc.text).path
        candidate = SITE / path.lstrip('/')
        if path == '/' or candidate.is_file() or (candidate / 'index.html').is_file():
            urls.add(ORIGIN + quote(path, safe='/:%'))
    root = ET.Element(f'{{{ns}}}urlset')
    for url in sorted(urls):
        ET.SubElement(ET.SubElement(root, f'{{{ns}}}url'), f'{{{ns}}}loc').text = url
    ET.ElementTree(root).write(SITE / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    # External project URLs remain covered by the GitHub site's project sitemap.
    (SITE / 'projects-sitemap.xml').unlink(missing_ok=True)
    (SITE / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {ORIGIN}/sitemap.xml\n', encoding='utf-8')
    manifest = {}
    for file in sorted(SITE.rglob('*')):
        if not file.is_file() or file.name in {'_headers', '_redirects'}:
            continue
        content = file.read_bytes()
        digest = hashlib.sha256(base64.b64encode(content) + file.suffix[1:].encode()).hexdigest()[:32]
        manifest['/' + file.relative_to(SITE).as_posix()] = {'hash': digest, 'size': len(content)}
    PRIVATE.mkdir(exist_ok=True)
    (PRIVATE / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    print(f'Prepared {len(manifest)} assets and {len(urls)} canonical sitemap URLs')

if __name__ == '__main__':
    prepare()
