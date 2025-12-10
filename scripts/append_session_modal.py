p='templates/attendance/dashboard.html'
s=open(p,'r',encoding='utf-8').read()
modal='''
<!-- New Session Modal -->
<div id="newSessionModal" class="modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); align-items:center; justify-content:center; z-index:1000;">
  <div class="glass-card" style="max-width:520px; width:90%; padding:1.25rem;">
    <h3 style="margin-top:0;">Create New Session</h3>
    <form id="new-session-form">
      {% csrf_token %}
      <div class="form-group">
        <label for="session_unit">Unit</label>
        <select name="unit" id="session_unit" class="form-input" required>
          {% for unit in units %}<option value="{{ unit.id }}">{{ unit.code }} - {{ unit.name }}</option>{% endfor %}
        </select>
      </div>
      <div class="form-group">
        <label for="session_semester">Semester</label>
        <input name="semester" id="session_semester" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="session_date">Date</label>
        <input type="date" name="date" id="session_date" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="session_start_time">Start Time</label>
        <input type="time" name="start_time" id="session_start_time" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="session_end_time">End Time</label>
        <input type="time" name="end_time" id="session_end_time" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="session_venue">Venue</label>
        <input name="venue" id="session_venue" class="form-input" required />
      </div>
      <div style="display:flex; gap:0.5rem; margin-top:1rem;">
        <button type="submit" class="btn btn-primary">Create</button>
        <button type="button" id="new-session-cancel" class="btn btn-secondary">Cancel</button>
      </div>
      <div id="new-session-errors" style="margin-top:0.75rem;color:var(--error);"></div>
    </form>
  </div>
</div>

<script>
(function(){
  const openBtn = document.querySelector('.btn-primary.btn-view');
  const modal = document.getElementById('newSessionModal');
  const cancel = document.getElementById('new-session-cancel');
  const form = document.getElementById('new-session-form');
  const errorsEl = document.getElementById('new-session-errors');

  openBtn && openBtn.addEventListener('click', (e)=>{
    if(openBtn.textContent.includes('Create Session')){
      e.preventDefault();
      modal.style.display = 'flex';
    }
  });
  cancel && cancel.addEventListener('click', ()=>{ modal.style.display='none'; errorsEl.innerHTML=''; form.reset(); });

  form && form.addEventListener('submit', (e)=>{
    e.preventDefault();
    errorsEl.innerHTML='';
    const data = new FormData(form);
    fetch('/session/create/', {
      method: 'POST',
      body: data,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)')?.pop() || ''
      }
    }).then(r=>r.json().then(j=>({ok:r.ok, status:r.status, json:j}))).then(res=>{
      if(res.ok && res.json.success){
        modal.style.display='none';
        form.reset();
        // Optionally, reload or update session list
        location.reload();
      } else {
        if(res.json && res.json.errors){
          let html='';
          for(const k in res.json.errors){ html += `<div><strong>${k}:</strong> ${res.json.errors[k].join(', ')}</div>` }
          errorsEl.innerHTML = html;
        } else if(res.json && res.json.error){
          errorsEl.textContent = res.json.error;
        } else {
          errorsEl.textContent = 'An error occurred';
        }
      }
    }).catch(err=>{ errorsEl.textContent='Network error'; });
  });
})();
</script>
'''
if s.rfind('{% endblock %}')!=-1:
    idx = s.rfind('{% endblock %}')
    s = s[:idx] + modal + s[idx:]
    open(p,'w',encoding='utf-8').write(s)
    print('appended session modal')
else:
    print('endblock not found')
