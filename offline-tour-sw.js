const CACHE='aria-guided-tour-offline-v1';
const ROOT=new URL('./',self.location.href).pathname;
const TOUR=ROOT+'fpa-copilot/employer-tour/';
const FILES=[ROOT,ROOT+'aria/',TOUR,...[0,1,2,3].map(i=>TOUR+'media/tour-v4.part'+i)];
self.addEventListener('install',event=>event.waitUntil((async()=>{const cache=await caches.open(CACHE);await cache.addAll(FILES);await self.skipWaiting()})()));
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('message',event=>{if(event.data==='OFFLINE_STATUS')event.source.postMessage({type:'ARIA_OFFLINE_READY'})});
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||url.origin!==self.location.origin||!FILES.includes(url.pathname))return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  try{const response=await fetch(event.request);if(response.ok)await cache.put(url.pathname,response.clone());return response}
  catch(error){const saved=await cache.match(url.pathname);if(saved)return saved;throw error}
 })());
});