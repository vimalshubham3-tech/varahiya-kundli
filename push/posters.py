#!/usr/bin/env python3
"""रोज़ के पोस्टर अपने-आप बनाता है -> daily/<city>/*.png
ऐप की अपनी इंजन से पंचांग-चित्र, और राशिफल / जैन तिथि / आदत के पोस्टर।
चलाने का तरीका:  python3 push/posters.py [ऑउटपुट-फ़ोल्डर]
"""
import base64, datetime, html, json, os, re, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'daily')
APP = 'file://' + os.path.join(ROOT, 'index.html')
CITIES = {'gwalior': 'ग्वालियर', 'sumaoli': 'सुमावली'}
THEMES = ['saffron', 'royal', 'lotus', 'night']   # रोज़ बदलते रंग (ऐप के theme कुंजी)
FOOT = 'वरहिया हेल्प डेस्क · हर पल आपके साथ'
LINK = 'tinyurl.com/varahiya-jyotish-darshan'
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
today = datetime.datetime.now(IST).date()
WD = ['सोमवार', 'मंगलवार', 'बुधवार', 'गुरुवार', 'शुक्रवार', 'शनिवार', 'रविवार']
MON = ['जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून', 'जुलाई', 'अगस्त', 'सितम्बर', 'अक्टूबर', 'नवम्बर', 'दिसम्बर']
DATE_H = '%d %s %d · %s' % (today.day, MON[today.month - 1], today.year, WD[today.weekday()])

src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
LOGO = re.search(r"LOGO='(data:image/png;base64,[^']+)'", src).group(1)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{width:1080px;font-family:'Noto Sans Devanagari',sans-serif;color:#4a1020}
.p{width:1080px;min-height:1350px;background:#5d0d1c;padding:16px;position:relative}
.in{background:#fffaf0;border:3px solid #d4a84b;border-radius:28px;overflow:hidden;min-height:1318px;display:flex;flex-direction:column}
.hd{background:linear-gradient(#fff3cf,#f6dc9b);text-align:center;padding:26px 30px 18px;border-bottom:3px solid #d4a84b}
.hd small{font-size:26px;color:#7a1a2c;font-weight:600}
.hd h1{font-size:50px;line-height:1.25;color:#7a1a2c;font-weight:700;margin-top:4px}
.hd .sub{font-size:30px;color:#a0651b;font-weight:600;margin-top:6px}
.bd{padding:28px 34px;flex:1;display:flex;flex-direction:column}
.dt{background:#7a1a2c;color:#ffd978;border-radius:20px;padding:16px 26px;font-size:38px;font-weight:700;text-align:center;margin-bottom:22px}
.ft{background:#5d0d1c;color:#fff;text-align:center;padding:16px 10px 20px;font-size:28px;font-weight:600}
.ft span{display:block;color:#ffd978;font-size:25px;font-weight:500;margin-top:4px}
img.lg{width:110px;height:110px;object-fit:contain;position:absolute;left:44px;top:44px}
"""

def page(title, sub, body):
    return ('<html><head><meta charset="utf-8"><style>%s</style></head><body><div class="p"><div class="in">'
            '<div class="hd"><img class="lg" src="%s"><small>॥ श्री जिनाय नमः ॥</small>'
            '<h1>%s</h1><div class="sub">%s</div></div><div class="bd">%s</div>'
            '<div class="ft">%s<span>वरहिया जैन पंचांग एवं ज्योतिष वास्तु दर्शन · %s</span></div></div></div></body></html>'
            % (CSS, LOGO, title, sub, body, FOOT, LINK))

def esc(x):
    return html.escape(str(x))

def shot(ctx, htm, path):
    pg = ctx.new_page()
    pg.set_viewport_size({'width': 1080, 'height': 1350})
    pg.set_content(htm, wait_until='networkidle')
    pg.evaluate('document.fonts.ready')
    pg.wait_for_timeout(400)
    pg.locator('.p').screenshot(path=path)
    pg.close()

def save_canvas(pg, path):
    d = pg.evaluate("document.querySelector('.vjpc canvas').toDataURL('image/png')")
    with open(path, 'wb') as f:
        f.write(base64.b64decode(d.split(',')[1]))

def jain_poster():
    D = json.load(open(os.path.join(ROOT, 'push', 'daily.json'), encoding='utf-8'))
    k = today.isoformat()
    t = D.get(k)
    if not t:
        return None
    rows = ''
    if t.get('kal'):
        rows += '<div class="bx"><h3>🙏 आज के कल्याणक</h3>' + ''.join('<p>%s</p>' % esc(x) for x in t['kal']) + '</div>'
    if t.get('parv'):
        rows += '<div class="bx"><h3>🪔 आज का पर्व / व्रत</h3>' + ''.join('<p>%s</p>' % esc(x) for x in t['parv']) + '</div>'
    if not rows:
        rows = '<div class="bx"><h3>🙏 आज का दिन</h3><p>आज कोई कल्याणक या विशेष पर्व नहीं है। देव-शास्त्र-गुरु का स्मरण, णमोकार मंत्र का जाप व स्वाध्याय करें।</p></div>'
    up = []
    for i in range(1, 40):
        d2 = today + datetime.timedelta(days=i)
        e = D.get(d2.isoformat())
        if e and (e['kal'] or e['parv']):
            for x in (e['kal'] + e['parv']):
                up.append((d2, x))
        if len(up) >= 4:
            break
    nx = ''.join('<div class="up"><b>%d %s</b><span>%s</span></div>' % (a.day, MON[a.month - 1], esc(x)) for a, x in up[:4])
    css = ('<style>.bx{background:#fff3d6;border:2px solid #d4a84b;border-radius:20px;padding:22px 28px;margin-bottom:20px}'
           '.bx h3{font-size:34px;color:#7a1a2c;margin-bottom:8px}.bx p{font-size:40px;font-weight:600;line-height:1.5;color:#3b0c16}'
           '.tt{display:flex;justify-content:space-around;margin-bottom:22px}.tt div{background:#fff;border:2px solid #e3c987;border-radius:18px;padding:12px 24px;text-align:center;font-size:38px;font-weight:700;color:#7a1a2c}'
           '.tt small{display:block;font-size:24px;color:#a0651b;font-weight:500}'
           '.nx{font-size:34px;font-weight:700;color:#7a1a2c;margin:18px 0 10px}'
           '.up{display:flex;gap:18px;align-items:center;padding:10px 0;border-bottom:1px dashed #d4a84b;font-size:32px}.up b{min-width:230px;color:#a0651b}</style>')
    body = css + ('<div class="dt">%s</div><div class="tt"><div><small>तिथि</small>%s</div><div><small>मास</small>%s</div></div>%s<div class="nx">आगामी कल्याणक / पर्व</div>%s'
                  % (DATE_H, esc(t['tithi']), esc(t['mas']), rows, nx))
    return page('जैन तिथि व कल्याणक', 'आज का जैन पंचांग', body)

def rashi_posters(rs):
    out = []
    star = lambda n: '★' * n + '☆' * (5 - n)
    css = ('<style>.g{display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:1fr;gap:16px;flex:1}.c{background:#fff;border:2px solid #e3c987;border-radius:16px;padding:16px 20px}'
           '.c b{font-size:38px;color:#7a1a2c}.c i{font-style:normal;float:right;color:#c27a0e;font-size:28px;letter-spacing:1px}'
           '.c p{font-size:33px;line-height:1.45;margin-top:8px;color:#3b0c16;font-weight:500}</style>')
    for n, part in enumerate([rs[:6], rs[6:]]):
        cards = ''.join('<div class="c"><b>%s</b><i>%s</i><p>%s</p></div>' % (esc(r['n']), star(r['s']), esc(r['t'])) for r in part)
        sub = '%s राशियाँ · %s' % ('मेष से कन्या' if n == 0 else 'तुला से मीन', DATE_H)
        out.append(page('आज का राशिफल', sub, css + '<div class="g">%s</div>' % cards))
    return out

def tip_poster(habit, career, skill):
    css = ('<style>.bx{background:#fff3d6;border:2px solid #d4a84b;border-radius:22px;padding:34px 38px;margin-bottom:26px;flex:1;display:flex;flex-direction:column;justify-content:center}'
           '.bx h3{font-size:36px;color:#7a1a2c;margin-bottom:10px}.bx p{font-size:48px;font-weight:600;line-height:1.5;color:#3b0c16}'
           '.bx.s p{font-size:38px}</style>')
    body = css + '<div class="dt">%s</div><div class="bx"><h3>💡 आज की आदत</h3><p>%s</p></div>' % (DATE_H, esc(habit))
    if career:
        body += '<div class="bx s"><h3>💼 आज की करियर टिप</h3><p>%s</p></div>' % esc(career)
    if skill:
        body += '<div class="bx s"><h3>💻 आज की स्किल टिप</h3><p>%s</p></div>' % esc(skill)
    return page('आज की आदत', 'सुविचार व सीख', body)

def main():
    os.makedirs(OUT, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 800}, device_scale_factor=1, service_workers='block',
                            timezone_id='Asia/Kolkata', locale='hi-IN')
        ctx.add_init_script("localStorage.setItem('vj_reg_v1',JSON.stringify({name:'वरहिया हेल्प डेस्क',mobile:'9977004518',done:1}));"
                            "localStorage.setItem('vj_prof_v1',JSON.stringify({show:0,photo:0}));")
        theme = THEMES[today.toordinal() % len(THEMES)]
        info = {'date': today.isoformat(), 'theme': theme, 'files': {}}
        for key, hn in CITIES.items():
            d = os.path.join(OUT, key)
            os.makedirs(d, exist_ok=True)
            pg = ctx.new_page()
            pg.goto(APP)
            pg.wait_for_timeout(2500)
            pg.evaluate("""(n)=>{const s=document.getElementById('pn_place');const o=[...s.options].find(o=>o.textContent.trim()===n);
              s.value=o.value;s.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('pn_go').click();}""", hn)
            pg.wait_for_timeout(1500)
            pg.evaluate("""()=>{const x=document.createElement('button');x.setAttribute('data-vjp','open');document.body.appendChild(x);x.click();x.remove();}""")
            pg.wait_for_timeout(1200)
            pg.click('[data-vjp="t:%s"]' % theme)
            for fm, name in [('main', 'panchang'), ('status', 'panchang_status'), ('short', 'panchang_chhota'), ('chg', 'choghadiya')]:
                pg.click('[data-vjp="f:%s"]' % fm)
                pg.wait_for_timeout(1500)
                save_canvas(pg, os.path.join(d, name + '.png'))
                info['files'].setdefault(key, []).append(name + '.png')
            if key == 'gwalior':
                data = pg.evaluate("""()=>{
                  const r=[...document.getElementById('rf_r').children];
                  const tips=r[0].innerText;
                  const rs=r.slice(1).filter(e=>e.querySelector('b')&&e.querySelector('span')&&e.querySelector('div')).map(e=>{const s=e.querySelector('span').textContent;return {n:e.querySelector('b').textContent,s:(s.match(/★/g)||[]).length,t:e.querySelector('div').textContent}});
                  const car=(tips.match(/करियर टिप:\\s*([^\\n💻]+)/)||[])[1]||'', sk=(tips.match(/स्किल टिप:\\s*(.+)/)||[])[1]||'';
                  return {rs:rs,career:car.trim(),skill:sk.trim(),habit:(document.getElementById('pd_td')||{}).textContent||''};}""")
            pg.close()
        # शहर-निरपेक्ष पोस्टर (राशिफल, जैन तिथि, आदत) -> daily/common
        cm = os.path.join(OUT, 'common')
        os.makedirs(cm, exist_ok=True)
        files = []
        for i, htm in enumerate(rashi_posters(data['rs']), 1):
            n = 'rashifal_%d.png' % i
            shot(ctx, htm, os.path.join(cm, n)); files.append(n)
        j = jain_poster()
        if j:
            shot(ctx, j, os.path.join(cm, 'jain_tithi.png')); files.append('jain_tithi.png')
        shot(ctx, tip_poster(data['habit'], data['career'], data['skill']), os.path.join(cm, 'aaj_ki_aadat.png')); files.append('aaj_ki_aadat.png')
        info['files']['common'] = files
        json.dump(info, open(os.path.join(OUT, 'today.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        b.close()
    print('ठीक:', json.dumps(info, ensure_ascii=False))

if __name__ == '__main__':
    main()
