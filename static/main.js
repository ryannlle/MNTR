(function(){
  // Autosuggest for the main search input
  function debounce(fn, wait){
    let t;
    return function(){
      const args = arguments;
      clearTimeout(t);
      t = setTimeout(()=>fn.apply(this,args), wait);
    }
  }

  function createDropdown(){
    const d = document.createElement('ul');
    d.className = 'autosuggest list-group shadow-sm';
    d.setAttribute('role','listbox');
    d.style.position = 'absolute';
    d.style.zIndex = 1050;
    d.style.display = 'none';
    return d;
  }

  function attach(){
    const input = document.querySelector('input[name="q"]');
    if(!input) return;

    const wrapper = input.closest('.search-bar');
    if(!wrapper) return;

    wrapper.style.position = 'relative';

    const dropdown = createDropdown();
    wrapper.appendChild(dropdown);

    const showSuggestions = (items)=>{
      dropdown.innerHTML = '';
      if(!items || !items.length){ dropdown.style.display = 'none'; return; }
      items.forEach((it, idx)=>{
        const li = document.createElement('li');
        li.className = 'list-group-item list-group-item-action';
        li.textContent = it;
        li.setAttribute('role','option');
        li.dataset.value = it;
        li.addEventListener('click', ()=>{
          input.value = it;
          dropdown.style.display = 'none';
          input.focus();
        });
        dropdown.appendChild(li);
      });
      dropdown.style.display = 'block';
    };

    const fetchSuggestions = debounce(function(){
      const q = input.value.trim();
      if(!q){ showSuggestions([]); return; }
      fetch(`/accounts/api/autosuggest/?q=${encodeURIComponent(q)}`)
        .then(r=>r.json())
        .then(data=>{
          showSuggestions(data.suggestions || []);
        }).catch(()=>{ showSuggestions([]); });
    }, 240);

    input.addEventListener('input', fetchSuggestions);

    // keyboard navigation
    input.addEventListener('keydown', function(e){
      const items = dropdown.querySelectorAll('li');
      if(!items.length) return;
      const active = dropdown.querySelector('.active');
      let idx = Array.prototype.indexOf.call(items, active);
      if(e.key === 'ArrowDown'){
        e.preventDefault(); idx = Math.min(items.length-1, idx+1);
        if(active) active.classList.remove('active');
        items[idx].classList.add('active');
        items[idx].scrollIntoView({block:'nearest'});
      } else if(e.key === 'ArrowUp'){
        e.preventDefault(); idx = Math.max(0, idx-1);
        if(active) active.classList.remove('active');
        items[idx].classList.add('active');
        items[idx].scrollIntoView({block:'nearest'});
      } else if(e.key === 'Enter'){
        if(active){ e.preventDefault(); input.value = active.dataset.value; dropdown.style.display = 'none'; input.form && input.form.submit(); }
      } else if(e.key === 'Escape'){
        dropdown.style.display = 'none';
      }
    });

    document.addEventListener('click', function(e){
      if(!wrapper.contains(e.target)) dropdown.style.display = 'none';
    });
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', attach);
  else attach();
})();

// Sidebar toggle (persisted)
(function(){
  function applyState(collapsed){
    if(collapsed) document.documentElement.classList.add('sidebar-collapsed');
    else document.documentElement.classList.remove('sidebar-collapsed');
  }

  function init(){
    const btn = document.getElementById('sidebarToggle');
    if(!btn) return;
    const stored = localStorage.getItem('mntr_sidebar_collapsed');
    applyState(stored === '1');
    btn.addEventListener('click', function(){
      const collapsed = document.documentElement.classList.toggle('sidebar-collapsed');
      localStorage.setItem('mntr_sidebar_collapsed', collapsed ? '1' : '0');
    });
  }

  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
