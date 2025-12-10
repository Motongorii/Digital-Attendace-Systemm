f = 'templates/attendance/dashboard.html'
c = open(f, 'r', encoding='utf-8').read()

# Find the description label in the modal and make it more visible
old_desc = '<label for="unit_description">Description</label>'
new_desc = '<label for="unit_description" style="color:#00ffe6; font-weight:700;">Description (Optional - Clear Notes)</label>'

if old_desc in c:
    c = c.replace(old_desc, new_desc)
    print('updated description label in modal')
else:
    print('description label not found')

open(f, 'w', encoding='utf-8').write(c)
