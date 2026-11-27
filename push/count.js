// सब्सक्राइबर की संख्या (केवल गिनती; कोई पता/एंडपॉइंट नहीं छापता)।
const URL_ = process.env.CLOUD_URL, TOKEN = process.env.PUSH_TOKEN;
(async () => {
  const h = x => require('crypto').createHash('sha256').update(String(x)).digest('hex').slice(0,10);
  console.log('urlhash', h(URL_), 'applrl', h('https://script.google.com/macros/s/AKfycbwRBH_bPXcOMLTnPd3aTdWggZhrDUnb0Mh6BlJG9oAU0GxX90ssmFi3yb2cl6eNB-sQ1w/exec'));
  const subs = await (await fetch(URL_ + '?push=' + encodeURIComponent(TOKEN))).json();
  const n = Array.isArray(subs) ? subs.length : -1;
  const line = new Date(Date.now() + 5.5 * 3600e3).toISOString().slice(0, 16).replace('T', ' ') + ' IST — सूचना चालू: ' + n;
  console.log(line);
  if (process.env.GITHUB_STEP_SUMMARY) require('fs').appendFileSync(process.env.GITHUB_STEP_SUMMARY, '### ' + line + '\n');
})();
