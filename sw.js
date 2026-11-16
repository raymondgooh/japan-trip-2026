// Keeps the app shell available offline. Trip data itself is cached by the page (localStorage).
const CACHE = 'jp26-shell-v1';
self.addEventListener('install', e => { self.skipWaiting(); e.waitUntil(caches.open(CACHE).then(c => c.addAll(['./']).catch(() => {}))); });
self.addEventListener('activate', e => e.waitUntil(
  caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET') return;
  if (/supabase\.co$|open-meteo\.com$/.test(url.hostname)) return;           // live data: never cached here
  const put = res => { if (res && (res.ok || res.type === 'opaque')) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return res; };
  if (url.origin === location.origin) {
    // newest version when online, saved copy when offline or the network stalls
    const net = fetch(req).then(put);
    const slow = new Promise(r => setTimeout(r, 4000)).then(() => caches.match(req, {ignoreSearch: req.mode === 'navigate'}));
    e.respondWith(Promise.race([net.catch(() => null), slow]).then(r => r || caches.match(req, {ignoreSearch: req.mode === 'navigate'})).then(r => r || caches.match('./')).then(r => r || net));
    return;
  }
  // fonts and the Supabase library: saved copy first
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(put)));
});
