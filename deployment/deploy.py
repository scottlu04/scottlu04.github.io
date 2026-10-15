"""Publish the prepared site using Cloudflare's documented direct-upload API.

Credentials are read only from the environment and are never logged or saved.
DNS/domain bindings are deliberately outside the routine deployment operation.
"""
import json
import os
import sys
import urllib.request
from upload_assets import upload, ROOT, PRIVATE, ACCOUNT

WORKER = 'scottlu-home'
API = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/workers'

def main():
    manifest = json.loads((PRIVATE / 'manifest.json').read_text())
    metadata = json.loads((ROOT / 'deployment/metadata.json').read_text())
    script = (ROOT / 'deployment/worker.mjs').read_text()
    if '--dry-run' in sys.argv:
        print(f'Deploy target: {WORKER}; {len(manifest)} assets; no API calls made')
        return
    token = os.environ.get('CLOUDFLARE_API_TOKEN')
    if not token:
        raise SystemExit('Set CLOUDFLARE_API_TOKEN with Workers Scripts Edit permission for the intended account.')

    def api(path, body, content_type='application/json', method='POST'):
        request = urllib.request.Request(API + path, data=body, method=method, headers={
            'Authorization': 'Bearer ' + token, 'Content-Type': content_type,
        })
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
        if not result.get('success'):
            raise RuntimeError('Cloudflare deployment request failed')
        return result['result']

    session = api(f'/scripts/{WORKER}/assets-upload-session', json.dumps({'manifest':manifest}).encode())
    metadata['assets']['jwt'] = upload(session)
    boundary = 'scottlu-home-deploy'
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="metadata"\r\nContent-Type: application/json\r\n\r\n'
        + json.dumps(metadata)
        + f'\r\n--{boundary}\r\nContent-Disposition: form-data; name="worker.mjs"; filename="worker.mjs"\r\nContent-Type: application/javascript+module\r\n\r\n'
        + script + f'\r\n--{boundary}--\r\n'
    ).encode()
    result = api(f'/scripts/{WORKER}', body, f'multipart/form-data; boundary={boundary}', 'PUT')
    print(f"Published {WORKER}, deployment {result.get('deployment_id', 'complete')}")

if __name__ == '__main__':
    main()
