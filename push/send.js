// रोज़ सुबह सभी सब्सक्राइबर को सूचना भेजता है। गोपनीय मान GitHub Secrets से आते हैं।
const webpush = require('web-push');
const fs = require('fs');
const TIPS = ["आज एक ऐसा काम सबसे पहले निपटाएँ जिसे आप टालते आ रहे हैं; बाकी दिन हल्का हो जाएगा।", "अपने काम का रोज़ का छोटा हिसाब लिखें; सुधार वहीं से शुरू होता है।", "आज किसी एक नई चीज़ को सीखने में 20 मिनट लगाएँ।", "सहकर्मी या ग्राहक से बात करते समय पहले पूरा सुनें, फिर उत्तर दें।", "आज के तीन सबसे ज़रूरी काम सुबह ही लिख लें और उन्हें पहले करें।", "जो वादा करें, समय पर निभाएँ; साख इसी से बनती है।", "अपनी किसी पुरानी गलती से मिली सीख लिखें और उसे दोहराने से बचें।", "आज किसी अनुभवी व्यक्ति से अपने काम पर सलाह लें।", "काम के बीच हर घंटे दो मिनट उठकर टहलें; ध्यान बना रहता है।", "अपना बायोडाटा या प्रोफ़ाइल आज एक बार नए सिरे से देखकर सुधारें।", "मुश्किल काम को छोटे हिस्सों में बाँटें और पहला हिस्सा आज शुरू करें।", "आज किसी की बिना अपेक्षा मदद करें; अच्छे संबंध आगे काम आते हैं।", "संदेशों और ईमेल का जवाब आज ही दें; देरी से गलतफ़हमी बढ़ती है।", "अपने क्षेत्र की कोई एक नई जानकारी या ख़बर आज पढ़ें।", "आय या पद पर बात करने से पहले अपने काम के नतीजों की सूची तैयार रखें।", "गुस्से में आज कोई निर्णय या संदेश न भेजें; अगले दिन दोबारा पढ़कर भेजें।", "नया काम लेने से पहले देखें कि समय और क्षमता दोनों हैं; ज़रूरत हो तो विनम्रता से मना करें।", "अपने कौशल की एक कमी चुनें और इस सप्ताह उस पर थोड़ा-थोड़ा अभ्यास करें।", "आज सहयोगियों के अच्छे काम की खुलकर प्रशंसा करें।", "अपनी कार्य-जगह को व्यवस्थित करें; साफ़ जगह पर काम तेज़ होता है।", "आज किसी पुराने संपर्क को हालचाल का संदेश भेजें; संपर्क बने रहने से अवसर मिलते हैं।", "लक्ष्य को संख्या और तारीख़ के साथ लिखें; अस्पष्ट लक्ष्य अक्सर अधूरे रहते हैं।", "आज आय का एक छोटा हिस्सा बचत या आपातकालीन निधि में डालें।", "बैठक या कॉल से पहले अपने तीन मुख्य बिंदु तैयार रखें।", "काम में ईमानदारी रखें, चाहे कोई देख रहा हो या नहीं।", "जहाँ अटके हों, वहाँ मदद माँगने में संकोच न करें।", "आने वाले सप्ताह की योजना आज शाम 10 मिनट में बना लें।", "जो काम आपको सबसे अच्छा आता है, उसमें आज थोड़ी अतिरिक्त गुणवत्ता जोड़ें।", "आज कोई एक अधूरा काम पूरा करके बंद करें; अधूरे काम मन पर बोझ रखते हैं।", "रात को सोने से पहले दिन की एक अच्छी बात लिख लें; अगले दिन का उत्साह बनता है।"];
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
  const tip = TIPS[Math.floor(Date.UTC(ist.getUTCFullYear(), ist.getUTCMonth(), ist.getUTCDate()) / 86400000) % 30];
  const rashi = JSON.stringify({ title: '🔆 आज का राशिफल', body: 'आज की चंद्र-राशि व 12 राशियों का फल देखें\n💼 करियर टिप: ' + tip, tag: 'vj-daily', url: './?rf=1' });
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
