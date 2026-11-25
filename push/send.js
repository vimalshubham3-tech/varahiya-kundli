// रोज़ सुबह सभी सब्सक्राइबर को सूचना भेजता है। गोपनीय मान GitHub Secrets से आते हैं।
const webpush = require('web-push');
const fs = require('fs');
const URL_ = process.env.CLOUD_URL, TOKEN = process.env.PUSH_TOKEN;
webpush.setVapidDetails('mailto:vimalshubham3@gmail.com', process.env.VAPID_PUBLIC, process.env.VAPID_PRIVATE);
(async () => {
  const r = await fetch(URL_ + '?push=' + encodeURIComponent(TOKEN));
  const subs = await r.json();
  console.log('subscribers:', subs.length);
  // आज/कल की जैन तिथि (push/daily.json — हर वर्ष नया बनाना होगा)
  const D = JSON.parse(fs.readFileSync(__dirname + '/daily.json', 'utf8'));
  const ist = new Date(Date.now() + 5.5 * 3600 * 1000), key = d => d.toISOString().slice(0, 10);
  const td = D[key(ist)], tm = D[key(new Date(ist.getTime() + 86400000))];
  const parts = [];
  if (td) {
    parts.push('तिथि: ' + td.tithi + ' (' + td.mas + ')' + (td.vrat ? ' — पर्व-तिथि' : ''));
    if (td.kal.length) parts.push('कल्याणक: ' + td.kal.join('; '));
    if (td.parv.length) parts.push('पर्व/व्रत: ' + td.parv.join('; '));
    if (tm && (tm.kal.length || tm.parv.length)) parts.push('कल: ' + tm.kal.concat(tm.parv).join('; '));
  }
  const jain = JSON.stringify({ title: '🙏 आज की जैन तिथि', body: parts.length ? parts.join('\n') : 'आज की जैन तिथि, कल्याणक व पर्व देखें', tag: 'vj-jain', url: './?jt=1' });
  const rashi = JSON.stringify({ title: '🔆 आज का राशिफल', body: 'आज की चंद्र-राशि व 12 राशियों का फल देखें', tag: 'vj-daily', url: './?rf=1' });
  let ok = 0, dead = 0;
  for (const s of subs) {
    try { await webpush.sendNotification(s, jain, { TTL: 43200 }); await webpush.sendNotification(s, rashi, { TTL: 43200 }); ok++; }
    catch (e) {
      if (e.statusCode === 404 || e.statusCode === 410) {
        dead++;
        await fetch(URL_, { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: JSON.stringify({ type: 'pushdel', token: TOKEN, endpoint: s.endpoint }) }).catch(() => {});
      } else console.log('err', e.statusCode);
    }
  }
  console.log('sent', ok, 'removed', dead);
})();
