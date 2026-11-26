// सब्सक्राइबर की संख्या (केवल गिनती; कोई पता/एंडपॉइंट नहीं छापता)।
const URL_ = process.env.CLOUD_URL, TOKEN = process.env.PUSH_TOKEN;
(async () => {
  const subs = await (await fetch(URL_ + '?push=' + encodeURIComponent(TOKEN))).json();
  const n = Array.isArray(subs) ? subs.length : -1;
  const line = new Date(Date.now() + 5.5 * 3600e3).toISOString().slice(0, 16).replace('T', ' ') + ' IST — सूचना चालू: ' + n;
  console.log(line);
  if (process.env.GITHUB_STEP_SUMMARY) require('fs').appendFileSync(process.env.GITHUB_STEP_SUMMARY, '### ' + line + '\n');
})();
