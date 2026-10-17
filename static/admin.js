const token = location.pathname.split('/').pop();

async function api(path, opts = {}) {
  const r = await fetch(`/api/admin/queues/${token}${path}`, {
    headers: {'Content-Type': 'application/json'}, ...opts,
  });
  if (!r.ok) {
    const d = await r.json().catch(() => ({}));
    alert(d?.detail?.error?.message || 'Ошибка');
    throw new Error('api');
  }
  return r.json();
}

function render(state) {
  document.getElementById('queue-name').textContent = state.queue.name;
  const cur = state.current;
  document.getElementById('current').textContent = cur
    ? `№${cur.number} — ${cur.name}` : 'Никого';
  const ul = document.getElementById('waiting');
  ul.innerHTML = '';
  state.waiting.forEach(t => {
    const li = document.createElement('li');
    li.textContent = `№${t.number} — ${t.name}`;
    ul.appendChild(li);
  });
  document.getElementById('empty-waiting').hidden = state.waiting.length > 0;
  document.getElementById('served').textContent = state.stats.served_today;
  document.getElementById('current').dataset.ticket = cur?.ticket_id || '';
}

async function refresh() {
  try { render(await api('/state')); } catch {}
}

document.getElementById('next').onclick = async () => { await api('/next', {method: 'POST'}); refresh(); };
document.getElementById('serve').onclick = async () => {
  const id = document.getElementById('current').dataset.ticket;
  if (id) { await api(`/tickets/${id}/serve`, {method: 'POST'}); refresh(); }
};
document.getElementById('skip').onclick = async () => {
  const id = document.getElementById('current').dataset.ticket;
  if (id) { await api(`/tickets/${id}/skip`, {method: 'POST'}); refresh(); }
};
document.getElementById('add-form').onsubmit = async (e) => {
  e.preventDefault();
  const name = document.getElementById('add-name').value.trim();
  if (!name) return;
  await api('/tickets', {method: 'POST', body: JSON.stringify({name})});
  document.getElementById('add-name').value = '';
  refresh();
};

refresh();
setInterval(refresh, 5000);