importScripts("./version.js");

const CACHE_NAME = `tecmap-shell-${self.TECMAP_VERSION || "dev"}`; 
const APP_SHELL = [
  "./",
  "./tecmap.html",
  "./config.js",
  "./version.js",
  "./manifest.webmanifest",
  "./leaflet-tilelayer-colorfilter-global.min.js",
  "./data/stops_with_coords.js",
  "./data/routes.js",
  "./icon-192.png",
  "./icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL))
  );
});

self.addEventListener("message", event => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const request = event.request;

  if (request.method !== "GET") return;

  const requestUrl = new URL(request.url);
  if (requestUrl.origin !== self.location.origin) return;

  // Always fetch version.js from network so update detection always gets the latest value
  if (requestUrl.pathname.endsWith("/version.js")) {
    event.respondWith(fetch(request));
    return;
  }

  // Fast launch: serve cached HTML first, refresh in background.
  const isNavigation = request.mode === "navigate";
  const isHtmlRequest = request.headers.get("accept")?.includes("text/html");
  if (isNavigation || isHtmlRequest) {
    const backgroundUpdate = fetch(request)
      .then(networkResponse => {
        if (!networkResponse || networkResponse.status !== 200) return;
        const responseCopy = networkResponse.clone();
        return caches.open(CACHE_NAME).then(cache => cache.put(request, responseCopy));
      })
      .catch(() => {});

    event.respondWith(
      caches.match(request)
        .then(cached => cached || caches.match("./tecmap.html"))
        .then(cachedOrFallback => {
          if (cachedOrFallback) return cachedOrFallback;
          return fetch(request);
        })
    );
    event.waitUntil(backgroundUpdate);
    return;
  }

  event.respondWith(
    caches.match(request).then(cachedResponse => {
      if (cachedResponse) {
        // Background refresh for next visit.
        fetch(request)
          .then(networkResponse => {
            if (networkResponse && networkResponse.status === 200) {
              const responseCopy = networkResponse.clone();
              caches.open(CACHE_NAME).then(cache => cache.put(request, responseCopy));
            }
          })
          .catch(() => {});
        return cachedResponse;
      }

      return fetch(request).then(networkResponse => {
        if (!networkResponse || networkResponse.status !== 200) {
          return networkResponse;
        }

        const responseCopy = networkResponse.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, responseCopy));
        return networkResponse;
      });
    })
  );
});
