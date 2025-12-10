p='templates/attendance/dashboard.html'
s=open(p,'r',encoding='utf-8').read()
modal='''

<!-- New Unit Modal -->
<div id="newUnitModal" class="modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.5); align-items:center; justify-content:center; z-index:1000;">
  <div class="glass-card" style="max-width:520px; width:90%; padding:1.25rem;">
    <h3 style="margin-top:0;">Add New Unit</h3>
    <form id="new-unit-form">
      {% csrf_token %}
      <div class="form-group">
        <label for="unit_code">Unit Code</label>
        <input name="code" id="unit_code" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="unit_name">Unit Name</label>
        <input name="name" id="unit_name" class="form-input" required />
      </div>
      <div class="form-group">
        <label for="unit_description">Description</label>
        <textarea name="description" id="unit_description" class="form-input" rows="3"></textarea>
      </div>
      <div style="display:flex; gap:0.5rem; margin-top:1rem;">
        <button type="submit" class="btn btn-primary">Create</button>
        <button type="button" id="new-unit-cancel" class="btn btn-secondary">Cancel</button>
      </div>
      <div id="new-unit-errors" style="margin-top:0.75rem;color:var(--error);"></div>
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
  const cancel = document.getElementById('new-unit-cancel');
  const form = document.getElementById('new-unit-form');
  const errorsEl = document.getElementById('new-unit-errors');

  openBtn && openBtn.addEventListener('click', ()=>{
    modal.style.display = 'flex';
  });
  cancel && cancel.addEventListener('click', ()=>{ modal.style.display='none'; errorsEl.innerHTML=''; form.reset(); });

  form && form.addEventListener('submit', (e)=>{
    e.preventDefault();
    errorsEl.innerHTML='';
    const data = new FormData(form);
    fetch('{% url "create_unit_ajax" %}', {
      method: 'POST',
      body: data,
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken')
      }
    }).then(r=>r.json().then(j=>({ok:r.ok, status:r.status, json:j}))).then(res=>{
      if(res.ok && res.json.success){
        // add to units list
        const list = document.querySelector('.units-list');
        if(list){
          const span = document.createElement('span');
          span.className='unit-tag';
          span.textContent = res.json.unit.code + ' - ' + res.json.unit.name;
          list.prepend(span);
        }
        modal.style.display='none';
        form.reset();
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
# Append before the last {% endblock %}
if s.rfind('{% endblock %}')!=-1:
    idx = s.rfind('{% endblock %}')
    s = s[:idx] + modal + s[idx:]
    open(p,'w',encoding='utf-8').write(s)
    print('appended modal')
else:
    print('endblock not found')
