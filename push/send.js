// रोज़ सुबह सभी सब्सक्राइबर को सूचना भेजता है। गोपनीय मान GitHub Secrets से आते हैं।
const webpush = require('web-push');
const URL_ = process.env.CLOUD_URL, TOKEN = process.env.PUSH_TOKEN;
webpush.setVapidDetails('mailto:vimalshubham3@gmail.com', process.env.VAPID_PUBLIC, process.env.VAPID_PRIVATE);
(async () => {
  const r = await fetch(URL_ + '?push=' + encodeURIComponent(TOKEN));
  const subs = await r.json();
  console.log('subscribers:', subs.length);
  const payload = JSON.stringify({ title: '🔆 आज का राशिफल', body: 'आज की चंद्र-राशि व 12 राशियों का फल देखें' });
  let ok = 0, dead = 0;
  for (const s of subs) {
    try { await webpush.sendNotification(s, payload, { TTL: 43200 }); ok++; }
    catch (e) {
      if (e.statusCode === 404 || e.statusCode === 410) {
        dead++;
        await fetch(URL_, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify({ type: 'pushdel', token: TOKEN, endpoint: s.endpoint }) }).catch(() => {});
      } else console.log('err', e.statusCode);
    }
  }
  console.log('sent', ok, 'removed', dead);
})();
