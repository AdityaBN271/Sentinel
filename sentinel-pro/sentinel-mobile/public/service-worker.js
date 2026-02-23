self.addEventListener('install', (e) => {
    console.log('[Service Worker] Install');
});

self.addEventListener('fetch', (e) => {
    // Simple pass-through for now to enable PWA installation
    e.respondWith(fetch(e.request));
});
