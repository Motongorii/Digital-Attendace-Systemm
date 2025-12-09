import requests

BASE = 'https://digital-attendance-system.fly.dev'
USERNAME = 'Motog'
PASSWORD = '123456'

s = requests.Session()
print('GET /login/')
resp = s.get(BASE + '/login/')
print('GET status', resp.status_code)
print('GET set-cookie headers:')
for k,v in resp.headers.items():
    if k.lower().startswith('set-cookie'):
        print('  ', k, v)
print('cookies after GET:', s.cookies.get_dict())

csrftoken = s.cookies.get('csrftoken') or ''
print('csrf cookie:', csrftoken)

payload = {
    'username': USERNAME,
    'password': PASSWORD,
    'csrfmiddlewaretoken': csrftoken,
}
headers = {'Referer': BASE + '/login/'}
print('\nPOST /login/')
post = s.post(BASE + '/login/', data=payload, headers=headers, allow_redirects=False)
print('POST status', post.status_code)
print('POST headers:')
for k,v in post.headers.items():
    if k.lower().startswith('set-cookie') or k.lower()=='location':
        print('  ', k, v)
print('cookies after POST:', s.cookies.get_dict())

if post.status_code in (301,302,303,307):
    loc = post.headers.get('Location')
    print('\nGET', loc)
    r = s.get(BASE + loc, allow_redirects=True)
    print('Final status', r.status_code)
    print('Response URL', r.url)
    print('\nHistory:')
    for i,h in enumerate(r.history):
        print(i, h.status_code, h.headers.get('Location'))
        for k,v in h.headers.items():
            if k.lower().startswith('set-cookie'):
                print('    set-cookie:', v)
    print('\nFinal response headers:')
    for k,v in r.headers.items():
        if k.lower().startswith('set-cookie'):
            print('   ', k, v)
    print('\nCookies at end:', s.cookies.get_dict())
    print('\nResponse snippet:')
    print(r.text[:1200])
else:
    print('No redirect; response len', len(post.text))
    print(post.text[:1000])
