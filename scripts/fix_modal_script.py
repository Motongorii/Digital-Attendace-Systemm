import re

f = 'templates/attendance/dashboard.html'
c = open(f, 'r', encoding='utf-8').read()

# Find and replace the new unit modal script section with improved version
old_script = r'''<script>
\(function\(\)\{
  function getCookie\(name\) \{
    const v = document\.cookie\.match\('\(^|;\)\\s\*' \+ name \+ '\\s\*=\\s\*\(\[^;]+\)'\);
    return v \? v\.pop\(\) : '';
  \}'''

new_script = '''<script>
(function(){
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }'''

# Simpler approach: replace the entire script block
start = c.find('(function(){')
end = c.find('})();', start) + 5

if start != -1 and end > start:
    new_modal_script = '''(function(){
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const openBtn = document.getElementById('open-new-unit');
  const modal = document.getElementById('newUnitModal');
  const cancel = document.getElementById('new-unit-cancel');
  const form = document.getElementById('new-unit-form');
  const errorsEl = document.getElementById('new-unit-errors');
  const codeInput = document.getElementById('unit_code');
  const nameInput = document.getElementById('unit_name');
  const descInput = document.getElementById('unit_description');

  // Open modal on button click
  if(openBtn) {
    openBtn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.style.display = 'flex';
      // Focus first field
      setTimeout(() => codeInput && codeInput.focus(), 100);
    });
  }

  // Close modal
  if(cancel) {
    cancel.addEventListener('click', () => {
      modal.style.display = 'none';
      errorsEl.innerHTML = '';
      form.reset();
    });
  }

  // Close modal on outside click
  if(modal) {
    modal.addEventListener('click', (e) => {
      if(e.target === modal) {
        modal.style.display = 'none';
        errorsEl.innerHTML = '';
      }
    });
  }

  // Form submission
  if(form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorsEl.innerHTML = '';

      const formData = new FormData(form);
      const csrfToken = getCookie('csrftoken');

      try {
        const resp = await fetch('/unit/create-ajax/', {
          method: 'POST',
          body: formData,
          headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
          },
          credentials: 'same-origin'
        });

        const json = await resp.json();

        if(json.success) {
          // Add unit to list
          const unitsList = document.querySelector('.units-list');
          if(unitsList) {
            const tag = document.createElement('span');
            tag.className = 'unit-tag';
            tag.textContent = json.unit.code + ' - ' + json.unit.name;
            unitsList.prepend(tag);
          }
          // Close modal and reset form
          modal.style.display = 'none';
          form.reset();
          // Show success via toast or alert
          if(window.showNotification) {
            showNotification('Unit created successfully!', 'success');
          }
        } else {
          if(json.errors) {
            let html = '';
            for(const key in json.errors) {
              const msgs = json.errors[key];
              if(Array.isArray(msgs)) {
                html += '<div><strong>' + key + ':</strong> ' + msgs.join(', ') + '</div>';
              } else {
                html += '<div><strong>' + key + ':</strong> ' + msgs + '</div>';
              }
            }
            errorsEl.innerHTML = html;
          } else if(json.error) {
            errorsEl.textContent = 'Error: ' + json.error;
          } else {
            errorsEl.textContent = 'An error occurred. Please try again.';
          }
        }
      } catch(err) {
        console.error('Network error:', err);
        errorsEl.textContent = 'Network error. Please check your connection.';
      }
    });
  }
})();'''
    
    c = c[:start] + new_modal_script + c[end:]
    open(f, 'w', encoding='utf-8').write(c)
    print('updated modal script')
else:
    print('modal script not found')
