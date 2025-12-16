import requests

BASE = 'http://127.0.0.1:8000'  # Use local dev server by default
USERNAME = 'Motog'
PASSWORD = '123456'

s = requests.Session()
print('GET /login/')
resp = s.get(BASE + '/login/')
print('GET status', resp.status_code)
print('GET response headers:')
for k,v in resp.headers.items():
    if k.lower().startswith('set-cookie'):
        print('  ', k, v)
print('cookies after GET:', s.cookies.get_dict())

# extract csrf token from cookies or form
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
print('POST response headers:')
for k,v in post.headers.items():
    if k.lower().startswith('set-cookie') or k.lower()=='location':
        print('  ', k, v)
print('cookies after POST:', s.cookies.get_dict())

if post.status_code in (301,302,303,307):
    loc = post.headers.get('Location')
    print('Redirect to', loc)
    r2 = s.get(BASE + loc)
    print('Follow status', r2.status_code)
    print('cookies after follow:', s.cookies.get_dict())
    print('Final URL', r2.url)
    print('Final response contains login form?', 'Enter your username' in r2.text[:1000])
else:
    print('No redirect; response len', len(post.text))
    print(post.text[:1000])
