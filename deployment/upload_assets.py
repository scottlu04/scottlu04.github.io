"""Upload only assets authorized by a short-lived Cloudflare upload session."""
from pathlib import Path
import base64
import json
import mimetypes
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'deployment' / '.private'
SITE = ROOT / '_cloudflare_site'
ACCOUNT = 'ec55ec5f6cd1127695b562e7fc3e20d3'

def upload(session=None):
    standalone = session is None
    if standalone:
        session = json.loads((PRIVATE / 'upload-session.json').read_text())
    manifest = json.loads((PRIVATE / 'manifest.json').read_text())
    by_hash = {value['hash']: key for key, value in manifest.items()}
    completion = session['jwt'] if not session.get('buckets') else None
    for bucket in session.get('buckets', []):
        boundary = 'cfassets' + uuid.uuid4().hex
        parts = []
        for digest in bucket:
            path = SITE / by_hash[digest].lstrip('/')
            mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
            if path.suffix == '.xml':
                mime = 'application/xml'
            parts += [f'--{boundary}\r\nContent-Disposition: form-data; name="{digest}"; filename="{digest}"\r\nContent-Type: {mime}\r\n\r\n'.encode(), base64.b64encode(path.read_bytes()), b'\r\n']
        parts.append(f'--{boundary}--\r\n'.encode())
        request = urllib.request.Request(
            f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/workers/assets/upload?base64=true',
            data=b''.join(parts), method='POST', headers={
                'Authorization': 'Bearer ' + session['jwt'],
                'Content-Type': 'multipart/form-data; boundary=' + boundary,
            })
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
        if not result.get('success'):
            raise RuntimeError('Cloudflare asset upload failed')
        completion = result.get('result', {}).get('jwt') or completion
        print(f'Uploaded {len(bucket)} assets')
    if not completion:
        raise RuntimeError('Missing upload completion token')
    if standalone:
        (PRIVATE / 'completion.json').write_text(json.dumps({'jwt': completion}))
        (PRIVATE / 'upload-session.json').unlink()
    return completion

if __name__ == '__main__':
    upload()
