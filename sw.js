// न्यूनतम service worker + सूचना (push)। कुछ कैश नहीं करता, इसलिए नया संस्करण तुरंत मिलता है।
self.addEventListener('install',function(){self.skipWaiting();});
self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim());});
self.addEventListener('fetch',function(e){e.respondWith(fetch(e.request));});
self.addEventListener('push',function(e){
  var d={};try{d=e.data?e.data.json():{};}catch(x){}
  e.waitUntil(self.registration.showNotification(d.title||'🔆 आज का राशिफल',{body:d.body||'आज की चंद्र-राशि व 12 राशियों का फल देखें',icon:'icon-192.png',badge:'icon-192.png',tag:'vj-daily',data:{url:'./?rf=1'}}));
});
self.addEventListener('notificationclick',function(e){
  e.notification.close();var u=(e.notification.data&&e.notification.data.url)||'./';
  e.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(function(l){
    for(var i=0;i<l.length;i++){if('focus' in l[i]){l[i].navigate(u);return l[i].focus();}}
    return self.clients.openWindow(u);}));
});
