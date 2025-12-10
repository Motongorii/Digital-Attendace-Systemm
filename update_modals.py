#!/usr/bin/env python3
"""
Update dashboard.html with modern, responsive modals.
"""
import re

# Read current file
with open('templates/attendance/dashboard.html', 'r') as f:
    content = f.read()

# Find the start of the new Unit modal section
start_marker = '<!-- New Unit Modal -->'
end_marker = '})();\n</script>\n\n<!-- New Session Modal -->'

if start_marker in content and end_marker in content:
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker) + len('})();\n</script>')
    
    new_unit_section = '''<!-- New Unit Modal: Modern, Responsive Design -->
<div id="newUnitModal" class="modal-backdrop" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center; z-index:1050; padding:1rem; overflow-y:auto;">
  <div class="modal-content glass-card" style="max-width:550px; width:100%; padding:2rem; border:2px solid var(--primary-cyan); box-shadow:0 0 30px rgba(0,255,242,0.25), inset 0 0 20px rgba(0,255,242,0.1); border-radius:20px; margin:auto;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
      <h2 style="color:#00ffe6; font-size:1.8rem; margin:0; font-family:'Orbitron',monospace; font-weight:800; text-shadow:0 0 8px #00ffe6;">Add New Unit</h2>
      <button type="button" id="unit-modal-close" style="background:none; border:none; color:#00ffe6; font-size:2rem; cursor:pointer; padding:0; width:40px; height:40px; display:flex; align-items:center; justify-content:center; transition:color 0.2s;">×</button>
    </div>
    <form id="new-unit-form">
      {% csrf_token %}
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label for="unit_code" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">Unit Code</label>
        <input name="code" id="unit_code" class="form-input" placeholder="e.g., CS101" style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px;" required />
      </div>
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label for="unit_name" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">Unit Name</label>
        <input name="name" id="unit_name" class="form-input" placeholder="e.g., Introduction to Programming" style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px;" required />
      </div>
      <div class="form-group" style="margin-bottom:1.5rem;">
        <label for="unit_description" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">Description (Optional)</label>
        <textarea name="description" id="unit_description" placeholder="Add any notes or details about this unit..." style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px; min-height:100px; font-family:inherit; resize:vertical;" rows="3"></textarea>
      </div>
      <div id="new-unit-errors" style="margin-bottom:1rem; color:#ff3366; font-weight:700; font-size:1.1rem; display:none;"></div>
      <div style="display:flex; gap:0.75rem; margin-top:1.5rem;">
        <button type="submit" class="btn btn-primary" style="flex:1; padding:1rem; font-size:1.1rem; font-weight:700;">Create Unit</button>
        <button type="button" id="new-unit-cancel" class="btn btn-secondary" style="flex:1; padding:1rem; font-size:1.1rem; font-weight:700;">Cancel</button>
      </div>
    </form>
  </div>
</div>

<script>
(function(){
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const openBtn = document.getElementById('open-new-unit');
  const modal = document.getElementById('newUnitModal');
  const closeBtn = document.getElementById('unit-modal-close');
  const cancel = document.getElementById('new-unit-cancel');
  const form = document.getElementById('new-unit-form');
  const errorsEl = document.getElementById('new-unit-errors');
  const codeInput = document.getElementById('unit_code');

  if(openBtn) {
    openBtn.addEventListener('click', (e) => {
      e.preventDefault();
      modal.style.display = 'flex';
      setTimeout(() => codeInput && codeInput.focus(), 100);
    });
  }

  const closeModal = () => {
    modal.style.display = 'none';
    errorsEl.style.display = 'none';
    errorsEl.innerHTML = '';
    form.reset();
  };

  if(closeBtn) closeBtn.addEventListener('click', closeModal);
  if(cancel) cancel.addEventListener('click', closeModal);

  if(modal) {
    modal.addEventListener('click', (e) => {
      if(e.target === modal) closeModal();
    });
  }

  if(form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      errorsEl.innerHTML = '';
      errorsEl.style.display = 'none';

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
          modal.style.display = 'none';
          form.reset();
          setTimeout(() => location.reload(), 500);
        } else {
          let html = '';
          if(json.error === 'not_a_lecturer') {
            html = 'You are not registered as a lecturer. Please contact admin.';
          } else if(json.errors) {
            for(const key in json.errors) {
              const msgs = json.errors[key];
              if(Array.isArray(msgs)) {
                html += '<div><strong>' + key + ':</strong> ' + msgs.join(', ') + '</div>';
              } else {
                html += '<div><strong>' + key + ':</strong> ' + msgs + '</div>';
              }
            }
          } else if(json.error) {
            html = json.error;
          } else {
            html = 'An error occurred. Please try again.';
          }
          errorsEl.innerHTML = html;
          errorsEl.style.display = 'block';
        }
      } catch(err) {
        console.error('Network error:', err);
        errorsEl.innerHTML = 'Network error. Please check your connection.';
        errorsEl.style.display = 'block';
      }
    });
  }
})();
</script>
'''
    
    # Update content
    content = content[:start_idx] + new_unit_section + content[end_idx:]
    print("✓ Updated New Unit modal")
else:
    print("✗ Could not find unit modal markers")

# Now update the session modal
start_marker2 = '<!-- New Session Modal -->'
end_marker2 = '})();\n</script>\n{% endblock %}'

if start_marker2 in content and end_marker2 in content:
    start_idx2 = content.find(start_marker2)
    end_idx2 = content.find(end_marker2) + len('})();\n</script>')
    
    new_session_section = '''<!-- New Session Modal: Modern, Responsive Design -->
<div id="newSessionModal" class="modal-backdrop" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.7); align-items:center; justify-content:center; z-index:1050; padding:1rem; overflow-y:auto;">
  <div class="modal-content glass-card" style="max-width:600px; width:100%; padding:2rem; border:2px solid var(--primary-magenta); box-shadow:0 0 30px rgba(255,0,128,0.2), inset 0 0 20px rgba(255,0,128,0.08); border-radius:20px; margin:auto;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
      <h2 style="color:#ff0080; font-size:1.8rem; margin:0; font-family:'Orbitron',monospace; font-weight:800; text-shadow:0 0 8px #ff0080;">Create Session</h2>
      <button type="button" id="session-modal-close" style="background:none; border:none; color:#ff0080; font-size:2rem; cursor:pointer; padding:0; width:40px; height:40px; display:flex; align-items:center; justify-content:center; transition:color 0.2s;">×</button>
    </div>
    <form id="new-session-form">
      {% csrf_token %}
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label for="session_unit" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">Unit</label>
        <select name="unit" id="session_unit" class="form-input" style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px;" required>
          <option value="">-- Select Unit --</option>
          {% for unit in units %}<option value="{{ unit.id }}">{{ unit.code }} - {{ unit.name }}</option>{% endfor %}
        </select>
      </div>
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label for="session_semester" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">Semester</label>
        <select name="semester" id="session_semester" class="form-input" style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px;" required>
          <option value="">-- Select Semester --</option>
          <option value="1">Semester 1</option>
          <option value="2">Semester 2</option>
        </select>
      </div>
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label for="session_date" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">Date</label>
        <input type="date" name="date" id="session_date" class="form-input" style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px;" required />
      </div>
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label for="session_start_time" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">Start Time</label>
        <input type="time" name="start_time" id="session_start_time" class="form-input" style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px;" required />
      </div>
      <div class="form-group" style="margin-bottom:1.25rem;">
        <label for="session_end_time" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">End Time</label>
        <input type="time" name="end_time" id="session_end_time" class="form-input" style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px;" required />
      </div>
      <div class="form-group" style="margin-bottom:1.5rem;">
        <label for="session_venue" style="color:#00ffe6; font-weight:700; font-size:1.05rem; display:block; margin-bottom:0.5rem;">Venue (Room/Location)</label>
        <input name="venue" id="session_venue" class="form-input" placeholder="e.g., Room 101" style="width:100%; padding:0.9rem; font-size:1.05rem; background:rgba(0,0,0,0.3); border:2px solid var(--primary-cyan); color:#fff; border-radius:8px;" required />
      </div>
      <div id="new-session-errors" style="margin-bottom:1rem; color:#ff3366; font-weight:700; font-size:1.1rem; display:none;"></div>
      <div style="display:flex; gap:0.75rem; margin-top:1.5rem;">
        <button type="submit" class="btn btn-primary" style="flex:1; padding:1rem; font-size:1.1rem; font-weight:700;">Create Session</button>
        <button type="button" id="new-session-cancel" class="btn btn-secondary" style="flex:1; padding:1rem; font-size:1.1rem; font-weight:700;">Cancel</button>
      </div>
    </form>
  </div>
</div>

<script>
(function(){
  const openBtn = document.querySelector('.btn-primary.btn-view');
  const modal = document.getElementById('newSessionModal');
  const closeBtn = document.getElementById('session-modal-close');
  const cancel = document.getElementById('new-session-cancel');
  const form = document.getElementById('new-session-form');
  const errorsEl = document.getElementById('new-session-errors');

  if(openBtn) {
    openBtn.addEventListener('click', (e) => {
      if(openBtn.textContent.includes('Create Session')) {
        e.preventDefault();
        modal.style.display = 'flex';
      }
    });
  }

  const closeModal = () => {
    modal.style.display = 'none';
    errorsEl.style.display = 'none';
    errorsEl.innerHTML = '';
    form.reset();
  };

  if(closeBtn) closeBtn.addEventListener('click', closeModal);
  if(cancel) cancel.addEventListener('click', closeModal);

  if(modal) {
    modal.addEventListener('click', (e) => {
      if(e.target === modal) closeModal();
    });
  }

  if(form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      errorsEl.innerHTML = '';
      errorsEl.style.display = 'none';

      const data = new FormData(form);
      fetch('/session/create/', {
        method: 'POST',
        body: data,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)')?.pop() || ''
        }
      }).then(r => r.json().then(j => ({ ok: r.ok, status: r.status, json: j }))).then(res => {
        if(res.ok && res.json.success) {
          modal.style.display = 'none';
          form.reset();
          location.reload();
        } else {
          let html = '';
          if(res.json && res.json.errors) {
            for(const k in res.json.errors) {
              html += '<div><strong>' + k + ':</strong> ' + (Array.isArray(res.json.errors[k]) ? res.json.errors[k].join(', ') : res.json.errors[k]) + '</div>';
            }
          } else if(res.json && res.json.error) {
            html = res.json.error;
          } else {
            html = 'An error occurred';
          }
          errorsEl.innerHTML = html;
          errorsEl.style.display = 'block';
        }
      }).catch(err => {
        errorsEl.innerHTML = 'Network error';
        errorsEl.style.display = 'block';
      });
    });
  }
})();
</script>
'''
    
    content = content[:start_idx2] + new_session_section + content[end_idx2:]
    print("✓ Updated New Session modal")
else:
    print("✗ Could not find session modal markers")

# Write the file back
with open('templates/attendance/dashboard.html', 'w') as f:
    f.write(content)

print("\n✓ Dashboard updated successfully with modern, responsive modals!")
