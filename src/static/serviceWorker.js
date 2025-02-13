
const cacheName = "MyCache_1";
const precachedResources = ["/", "/index.css", "snow.JPEG"];

async function precache() {
    const cache = await caches.open(cacheName);
    return cache.addAll(precachedResources);
}

async function cacheFirst(request) {
    console.log(`caching: ${request}`)
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open("MyCache_1");
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        return Response.error();
    }
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
    if (precachedResources.includes(url.pathname)) {
        event.respondWith(cacheFirst(event.request));
    }
});
