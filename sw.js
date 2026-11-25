// न्यूनतम service worker: केवल इंस्टॉल योग्य बनाने के लिए। कुछ कैश नहीं करता, इसलिए नया संस्करण हमेशा तुरंत मिलता है।
self.addEventListener('install',function(){self.skipWaiting();});
self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim());});
self.addEventListener('fetch',function(e){e.respondWith(fetch(e.request));});
