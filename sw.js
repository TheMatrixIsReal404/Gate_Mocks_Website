// ─────────────────────────────────────────────────────────────────────────────
// GATE CSE PRACTICE PLATFORM — Service Worker (PWA Offline Support v8.4)
// ─────────────────────────────────────────────────────────────────────────────

const CACHE_NAME = 'gate-cse-v8.9';
const STATIC_ASSETS = [
  './',
  './index.html',
  './style.css',
  './app.js',
  './firebase.js',
  './manifest.json',
  './data/sample_questions.json',
  './data/gate_30_hard_mocks.json',
  './data/gate_30_easy_mocks.json',
  './data/gate_30_easy1_mocks.json',
  './data/gate_30_medium_mocks.json',
  './data/gate_20_full_mocks.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[SW] Pre-caching static assets (v8.8)');
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('[SW] Cache addAll warning:', err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.map(key => {
          if (key !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Ignore firestore or auth API calls — let firebase SDK handle its own offline persistence
  if (url.origin.includes('firestore.googleapis.com') ||
      url.origin.includes('identitytoolkit.googleapis.com') ||
      url.origin.includes('securetoken.googleapis.com') ||
      url.origin.includes('firebaseapp.com')) {
    return;
  }

  // Network first with cache fallback for local files
  event.respondWith(
    fetch(event.request)
      .then(response => {
        if (response && response.status === 200 && response.type === 'basic') {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then(cached => {
          if (cached) return cached;
          if (event.request.headers.get('accept')?.includes('text/html')) {
            return caches.match('./index.html');
          }
        });
      })
  );
});
