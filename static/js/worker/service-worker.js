self.addEventListener('install', event => {
  // Installation réussie, rien à faire
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  // Activation réussie, rien à faire
  self.clients.claim();
});