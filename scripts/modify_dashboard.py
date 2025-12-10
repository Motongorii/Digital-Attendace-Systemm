import io,sys
p='templates/attendance/dashboard.html'
s=open(p,'r',encoding='utf-8').read()
old_open = "<a href=\"{% url 'create_unit' %}\" class=\"btn btn-secondary btn-view\">"
if old_open in s:
    s=s.replace(old_open, '<button id="open-new-unit" class="btn btn-secondary btn-view">')
# replace the specific closing tag after 'New Unit'
s=s.replace('New Unit\n            </a>','New Unit\n            </button>')
open(p,'w',encoding='utf-8').write(s)
print('done')
