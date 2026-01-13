import os
from pathlib import Path
print('FIREBASE_CREDENTIALS_JSON set:', 'FIREBASE_CREDENTIALS_JSON' in os.environ and bool(os.environ.get('FIREBASE_CREDENTIALS_JSON')))
print('FIREBASE_CREDENTIALS_PATH set:', 'FIREBASE_CREDENTIALS_PATH' in os.environ and bool(os.environ.get('FIREBASE_CREDENTIALS_PATH')))
def check_file(p):
    p = Path(p)
    return p.exists(), (p.stat().st_size if p.exists() else None), (p.stat().st_mtime if p.exists() else None)
def check_default():
    default = Path(__file__).resolve().parent.parent / 'firebase-credentials.json'
    exists, size, mtime = check_file(default)
    print('default firebase-credentials.json exists:', exists, 'size:', size)
    if exists:
        try:
            import json
            j = json.loads(default.read_text())
            print('contains client_email:', 'client_email' in j)
            print('contains private_key (redacted):', 'private_key' in j)
            print('client_email sample:', j.get('client_email'))
        except Exception as e:
            print('failed to parse default json:', e)

if __name__ == '__main__':
    check_default()
