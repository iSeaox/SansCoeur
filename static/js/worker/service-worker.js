const CACHE_NAME = 'sanscoeur-v0.0.2';
const CACHE_URLS = [
  '/static/js/worker/service-worker.js',
  '/static/img/sco_logo_500.png',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(CACHE_URLS);
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

self.addEventListener('push', function(event) {
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/static/img/sco_logo_500.png',
  }
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});