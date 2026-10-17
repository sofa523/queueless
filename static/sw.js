self.addEventListener('push', (e) => {
  const data = e.data ? e.data.json() : {};
  e.waitUntil(self.registration.showNotification(data.title || 'QueueLess', {
    body: data.body || 'Ваша очередь приближается',
    icon: '/static/icon.png',
  }));
});