const slug = location.pathname.split('/').pop();
let ticketId = localStorage.getItem(`queueless.ticket.${slug}`);

async function api(path, opts = {}) {
  const r = await fetch(`/api/queue/${slug}${path}`, {
    headers: {'Content-Type': 'application/json'}, ...opts,
  });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw d;
  return d;
}

function render(s) {
  document.getElementById('join-block').hidden = true;
  document.getElementById('status-block').hidden = false;
  document.getElementById('number').textContent = `№${s.number}`;
  document.getElementById('position').textContent = Math.max(s.position, 0);
  document.getElementById('eta').textContent = s.eta_minutes;
  document.getElementById('current').textContent = s.current_number ?? '—';
  const txt = document.getElementById('state-text');
  if (s.status === 'called') txt.textContent = 'Ваша очередь! Подойдите к стойке';
  else if (s.status === 'served') txt.textContent = 'Обслужен';
  else if (s.status === 'skipped') txt.textContent = 'Пропущен';
  else txt.textContent = 'Ожидаете';
}

async function refresh() {
  try { render(await api(`/ticket/${ticketId}`)); } catch { /* noop */ }
}

async function bootstrap() {
  try {
    const q = await api('/../..'.replace('..','')); // заглушка, чтобы не падать
  } catch {}
  // Просто загружаем название очереди через join (или отдельный endpoint при желании)
  if (ticketId) {
    document.getElementById('join-block').hidden = true;
    document.getElementById('status-block').hidden = false;
    refresh();
    setInterval(refresh, 5000);
  } else {
    document.getElementById('join-block').hidden = false;
  }
}

document.getElementById('join-form').onsubmit = async (e) => {
  e.preventDefault();
  const name = document.getElementById('name').value.trim();
  if (!name) return;
  const d = await api('/join', {method: 'POST', body: JSON.stringify({name})});
  ticketId = d.ticket_id;
  localStorage.setItem(`queueless.ticket.${slug}`, ticketId);
  render(d);
  setInterval(refresh, 5000);
};

document.getElementById('enable-push').onclick = async () => {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    alert('Ваш браузер не поддерживает push-уведомления');
    return;
  }
  const reg = await navigator.serviceWorker.register('/sw.js');
  const perm = await Notification.requestPermission();
  if (perm !== 'granted') { alert('Уведомления отключены'); return; }
  const sub = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(window.VAPID_PUBLIC_KEY || ''),
  });
  await api(`/ticket/${ticketId}/subscribe`, {
    method: 'POST',
    body: JSON.stringify({
      type: 'webpush',
      endpoint: sub.endpoint,
      keys: {
        p256dh: btoa(String.fromCharCode(...new Uint8Array(sub.getKey('p256dh')))),
        auth: btoa(String.fromCharCode(...new Uint8Array(sub.getKey('auth')))),
      },
    }),
  });
  alert('Уведомления включены');
};

function urlBase64ToUint8Array(base64) {
  const padding = '='.repeat((4 - base64.length % 4) % 4);
  const raw = atob((base64 + padding).replace(/-/g, '+').replace(/_/g, '/'));
  return Uint8Array.from([...raw].map(c => c.charCodeAt(0)));
}

bootstrap();