// नेटवर्क पहले; न मिले तो कैश से (ऑफ़लाइन चले)
var C='kn-v1';
self.addEventListener('install',function(){self.skipWaiting();});
self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim());});
self.addEventListener('fetch',function(e){
  if(e.request.method!=='GET')return;
  e.respondWith(fetch(e.request).then(function(r){var c=r.clone();caches.open(C).then(function(k){k.put(e.request,c);});return r;}).catch(function(){return caches.match(e.request);}));
});
