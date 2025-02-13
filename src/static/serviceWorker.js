
const cacheName = "MyCache_1";
const precachedResources = ["/", "/index.css", "snow.JPEG"];

async function precache() {
    const cache = await caches.open(cacheName);
    return cache.addAll(precachedResources);
}

self.addEventListener('install', function(event) {
    console.log('[Service Worker] Installing Service Worker ...', event);
    event.waitUntil(precache());
});
self.addEventListener('activate', function(event) {
    console.log('[Service Worker] Activating Service Worker ...', event);
});
self.addEventListener('fetch', function(event) {
    console.log('[Service Worker] Fetching something ...', event);
});
