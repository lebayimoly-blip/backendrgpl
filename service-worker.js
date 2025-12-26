const CACHE_NAME = "rgpl-cache-v1";
const urlsToCache = [
  "/",
  "/index.html",
  "/login.html",
  "/offline.html",
  "/page-famille-edit.html",
  "/stats.html",
  "/static/style.css",
  "/static/js/login.js",
  "/static/data/stats.json",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    fetch(event.request).catch(() =>
      caches.match(event.request).then(response => response || caches.match("/offline.html"))
    )
  );
});
