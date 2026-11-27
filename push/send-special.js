// विशेष अवसर की सूचना: शीर्षक/संदेश GitHub Actions के इनपुट से आते हैं (पर्यावरण-चर के रूप में)।
const webpush = require('web-push');
const URL_ = process.env.CLOUD_URL, TOKEN = process.env.PUSH_TOKEN;
const title = (process.env.SP_TITLE || '').trim(), body = (process.env.SP_BODY || '').trim();
let link = (process.env.SP_URL || './').trim();
if (!/^\.\/(\?[\w=&%.-]*)?$/.test(link)) link = './';
if (!title || !body) { console.log('शीर्षक और संदेश ज़रूरी हैं'); process.exit(1); }
webpush.setVapidDetails('mailto:vimalshubham3@gmail.com', process.env.VAPID_PUBLIC, process.env.VAPID_PRIVATE);
(async () => {
  const subs = await (await fetch(URL_ + '?push=' + encodeURIComponent(TOKEN))).json();
  console.log('subscribers:', subs.length);
  const msg = JSON.stringify({ title, body, tag: 'vj-special', url: link });
  let ok = 0, dead = 0;
  for (const s of subs) {
    try { await webpush.sendNotification(s, msg, { TTL: 43200 }); ok++; }
    catch (e) {
      if (e.statusCode === 404 || e.statusCode === 410 || (!e.statusCode && /subscription|p256dh|auth|endpoint/i.test(String(e.message)))) {
        dead++;
        await fetch(URL_, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify({ type: 'pushdel', token: TOKEN, endpoint: s.endpoint }) }).catch(() => {});
      } else console.log('err', e.statusCode);
    }
  }
  console.log('sent', ok, 'removed', dead);
})();
