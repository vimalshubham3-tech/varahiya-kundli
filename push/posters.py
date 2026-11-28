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


JS_DAY = """()=>{
 const res=document.getElementById('pn_res');const R=[];
 res.querySelectorAll('.tw>table>tbody>tr').forEach(tr=>{if(tr.cells.length>1)R.push([tr.cells[0].textContent.replace(/\\s+/g,' ').trim(),tr.cells[1].textContent.replace(/\\s+/g,' ').trim()]);});
 const find=(k,st)=>{for(const r of R){if(st?r[0].indexOf(k)===0:r[0].indexOf(k)>-1)return r[1];}return '';};
 const ang=k=>{const t=find(k,true).split(' | ')[0];return t.split(' — ')[0].replace(/\\s*\\(.*?\\)\\s*/g,'').trim();};
 const iv=s=>{const m=(s||'').match(/(\\d\\d:\\d\\d)\\s*[–-]\\s*(\\d\\d:\\d\\d)/);return m?m[1]+'–'+m[2]:'';};
 const lst=a=>{const o=[];a.forEach(x=>{const t=iv(find(x[1]));if(t)o.push([x[0],t]);});return o;};
 const sr=find('सूर्योदय / सूर्यास्त').split('/')[0].trim();
 return {tithi:ang('तिथि ('),nak:ang('नक्षत्र ('),wd:find('वार',true),sr:sr,
  shubh:lst([['अमृत काल','अमृत काल'],['अभिजित','अभिजित'],['विजय','विजय'],['गोधूलि','गोधूलि'],['ब्रह्म मुहूर्त','ब्रह्म']]),
  ashubh:lst([['राहुकाल','राहुकाल'],['गुलिक','गुलिक'],['यमगंड','यमगंड'],['भद्रा','भद्रा (अशुभ)'],['दुर्मुहूर्त','दुर्मुहूर्त']])};}"""

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


SUTRA = [
 ('सम्यग्दर्शनज्ञानचारित्राणि मोक्षमार्गः', 'तत्त्वार्थ सूत्र', 'सही श्रद्धा, सही ज्ञान और सही आचरण — इन तीनों का मेल ही मोक्ष का मार्ग है।'),
 ('तत्त्वार्थश्रद्धानं सम्यग्दर्शनम्', 'तत्त्वार्थ सूत्र', 'जीवादि तत्त्वों पर सच्ची श्रद्धा रखना ही सम्यग्दर्शन है।'),
 ('उपयोगो लक्षणम्', 'तत्त्वार्थ सूत्र', 'जानना-देखना (उपयोग) ही जीव की पहचान है।'),
 ('परस्परोपग्रहो जीवानाम्', 'तत्त्वार्थ सूत्र', 'जीवों का काम एक-दूसरे का सहयोग करना है।'),
 ('उत्पादव्ययध्रौव्ययुक्तं सत्', 'तत्त्वार्थ सूत्र', 'जो नया रूप लेता है, पुराना छोड़ता है और फिर भी मूल रूप में बना रहता है, वही सत् है।'),
 ('हिंसानृतस्तेयाब्रह्मपरिग्रहेभ्यो विरतिर्व्रतम्', 'तत्त्वार्थ सूत्र', 'हिंसा, झूठ, चोरी, अब्रह्म और परिग्रह से दूर रहना ही व्रत है।'),
 ('प्रमत्तयोगात्प्राणव्यपरोपणं हिंसा', 'तत्त्वार्थ सूत्र', 'असावधानी या कषाय से किसी के प्राणों को कष्ट पहुँचाना हिंसा है।'),
 ('असदभिधानमनृतम्', 'तत्त्वार्थ सूत्र', 'अप्रिय या हानिकारक असत्य बोलना झूठ है।'),
 ('अदत्तादानं स्तेयम्', 'तत्त्वार्थ सूत्र', 'बिना दी हुई वस्तु ले लेना चोरी है।'),
 ('मूर्छा परिग्रहः', 'तत्त्वार्थ सूत्र', 'वस्तुओं में ममत्व (मोह) रखना ही परिग्रह है।'),
 ('तपसा निर्जरा च', 'तत्त्वार्थ सूत्र', 'तप से पुराने कर्म झड़ते हैं।'),
 ('कायवाङ्मनःकर्म योगः', 'तत्त्वार्थ सूत्र', 'शरीर, वाणी और मन की क्रिया को योग कहा गया है।'),
 ('णमो अरिहंताणं', 'णमोकार मंत्र', 'अरिहंत भगवान को नमस्कार, जिन्होंने राग-द्वेष जीतकर केवलज्ञान पाया।'),
 ('णमो सिद्धाणं', 'णमोकार मंत्र', 'सिद्ध भगवान को नमस्कार, जो सब कर्मों से मुक्त हो चुके हैं।'),
 ('णमो आयरियाणं', 'णमोकार मंत्र', 'आचार्य परमेष्ठी को नमस्कार, जो स्वयं आचरण करते और संघ का मार्गदर्शन करते हैं।'),
 ('णमो उवज्झायाणं', 'णमोकार मंत्र', 'उपाध्याय परमेष्ठी को नमस्कार, जो शास्त्र पढ़ाते और ज्ञान देते हैं।'),
 ('णमो लोए सव्वसाहूणं', 'णमोकार मंत्र', 'लोक के सभी साधुओं को नमस्कार।'),
 ('अहिंसा परमो धर्मः', 'जैन सिद्धांत', 'किसी भी जीव को कष्ट न देना सबसे बड़ा धर्म है।'),
 ('मित्ती मे सव्वभूदेसु', 'क्षमा-पाठ', 'सब प्राणियों से मेरी मैत्री है; किसी से मेरा बैर नहीं।'),
]
NAMOKAR = 'णमो अरिहंताणं · णमो सिद्धाणं · णमो आयरियाणं<br>णमो उवज्झायाणं · णमो लोए सव्वसाहूणं'

def sutra_poster():
    t = SUTRA[today.toordinal() % len(SUTRA)]
    css = ('<style>.bx{background:#fff3d6;border:2px solid #d4a84b;border-radius:24px;padding:40px 40px;margin-bottom:22px;text-align:center}'
           '.bx small{display:block;font-size:30px;color:#a0651b;font-weight:600;margin-bottom:14px}'
           '.bx .s{font-size:64px;line-height:1.4;color:#7a1a2c;font-weight:700}'
           '.bx .m{font-size:38px;line-height:1.55;color:#3b0c16;font-weight:500;margin-top:20px}'
           '.nm{background:#7a1a2c;color:#ffd978;border-radius:20px;padding:22px;text-align:center;font-size:36px;font-weight:600;line-height:1.6}'
           '.nm small{display:block;color:#fff;font-size:26px;font-weight:500;margin-bottom:6px}</style>')
    body = (css + '<div class="dt">%s</div><div class="bx"><small>%s</small><div class="s">%s</div><div class="m">अर्थ: %s</div></div>'
            '<div class="nm"><small>णमोकार मंत्र</small>%s</div>' % (DATE_H, esc(t[1]), esc(t[0]), esc(t[2]), NAMOKAR))
    return page('आज का जैन सूत्र', 'रोज़ एक सूत्र, सरल अर्थ के साथ', body)

def vrat_poster():
    D = json.load(open(os.path.join(ROOT, 'push', 'daily.json'), encoding='utf-8'))
    rows, n = '', 0
    for i in range(0, 45):
        dt = today + datetime.timedelta(days=i)
        e = D.get(dt.isoformat())
        if not e or not (e['kal'] or e['parv']):
            continue
        rows += '<div class="r%s"><b>%d %s<small>%s</small></b><em>%s</em><span>%s</span></div>' % (
            ' now' if i == 0 else '', dt.day, MON[dt.month - 1], WD[dt.weekday()], esc(e['tithi']), esc(' · '.join(e['kal'] + e['parv'])))
        n += 1
        if n >= 9:
            break
    if not rows:
        rows = '<div class="r"><span>अगले 45 दिन में कोई कल्याणक/पर्व दर्ज नहीं</span></div>'
    css = ('<style>.r{display:flex;gap:16px;align-items:center;background:#fff;border:2px solid #e3c987;border-radius:16px;padding:14px 18px;margin-bottom:12px;font-size:28px}'
           '.r b{min-width:190px;color:#7a1a2c;font-size:34px;line-height:1.15}.r b small{display:block;font-size:23px;color:#a0651b;font-weight:600}'
           '.r em{font-style:normal;min-width:170px;color:#a0651b;font-weight:600;font-size:26px}.r span{flex:1;font-weight:600;line-height:1.35}'
           '.r.now{background:#fff0c2;border-color:#d4a84b}</style>')
    return page('आगामी कल्याणक व पर्व', 'अगले कुछ सप्ताह · ' + DATE_H, css + '<div>%s</div>' % rows)

def week_poster(city_hn, days):
    css = ('<style>.r{display:flex;align-items:center;gap:16px;background:#fff;border:2px solid #e3c987;border-radius:18px;padding:16px 22px;margin-bottom:14px}'
           '.r.now{background:#fff0c2;border-color:#d4a84b}.r .d{min-width:210px}.r .d b{display:block;font-size:44px;color:#7a1a2c;line-height:1.1}'
           '.r .d small{font-size:26px;color:#a0651b;font-weight:600}.r .t{flex:1;font-size:32px;font-weight:700;color:#3b0c16;line-height:1.35}'
           '.r .t small{display:block;font-size:26px;font-weight:500;color:#5a2a35}</style>')
    rows = ''
    for i, x in enumerate(days):
        rows += ('<div class="r%s"><div class="d"><b>%s</b><small>%s %s</small></div><div class="t">%s<small>नक्षत्र: %s · सूर्योदय %s</small></div></div>'
                 % (' now' if i == 0 else '', esc(x['day']), esc(x['mon']), esc(x['wd']), esc(x['tithi']), esc(x['nak']), esc(x['sr'])))
    return page('अगले 7 दिन का पंचांग', 'तिथि व नक्षत्र · ' + city_hn, css + rows)

def shubh_poster(city_hn, d):
    def blk(title, items, cls):
        r = ''.join('<div class="i"><span>%s</span><b>%s</b></div>' % (esc(a), esc(b)) for a, b in items) or '<div class="i"><span>—</span></div>'
        return '<div class="bk %s"><h3>%s</h3>%s</div>' % (cls, title, r)
    css = ('<style>.bk{border-radius:22px;padding:22px 30px;margin-bottom:20px}.bk h3{font-size:38px;margin-bottom:10px}'
           '.bk.g{background:#fff3d6;border:2px solid #d4a84b;color:#3b0c16}.bk.g h3{color:#7a1a2c}.bk.b{background:#7a1a2c;color:#fff}.bk.b h3{color:#ffd978}'
           '.i{display:flex;justify-content:space-between;font-size:38px;padding:9px 0;border-bottom:1px solid #ffffff33}.bk.g .i{border-color:#d4a84b66}.i b{font-weight:700}'
           '.nt{font-size:27px;color:#5a2a35;text-align:center;margin-top:6px}</style>')
    body = (css + '<div class="dt">%s</div>' % DATE_H + blk('✅ शुभ समय (नए काम, खरीदारी, यात्रा)', d['shubh'], 'g')
            + blk('⚠️ अशुभ समय (इनमें शुभ कार्य टालें)', d['ashubh'], 'b') + '<div class="nt">समय %s के सूर्योदय के अनुसार</div>' % esc(city_hn))
    return page('आज का शुभ मुहूर्त', city_hn, body)

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
            # 7 दिन का पंचांग + आज के शुभ/अशुभ समय
            days = []
            for i in range(7):
                dt = today + datetime.timedelta(days=i)
                pg.evaluate("(v)=>{const e=document.getElementById('pn_date');e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('pn_go').click();}", dt.isoformat())
                pg.wait_for_timeout(700)
                x = pg.evaluate(JS_DAY)
                x['day'] = str(dt.day); x['mon'] = MON[dt.month - 1]; x['wd'] = WD[dt.weekday()]
                days.append(x)
                if i == 0:
                    today_x = x
            shot(ctx, week_poster(hn, days), os.path.join(d, 'saptah_panchang.png'))
            shot(ctx, shubh_poster(hn, today_x), os.path.join(d, 'shubh_muhurat.png'))
            info['files'][key] += ['saptah_panchang.png', 'shubh_muhurat.png']
            pg.evaluate("(v)=>{const e=document.getElementById('pn_date');e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('pn_go').click();}", today.isoformat())
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
        shot(ctx, vrat_poster(), os.path.join(cm, 'vrat_calendar.png')); files.append('vrat_calendar.png')
        shot(ctx, sutra_poster(), os.path.join(cm, 'jain_sutra.png')); files.append('jain_sutra.png')
        shot(ctx, tip_poster(data['habit'], data['career'], data['skill']), os.path.join(cm, 'aaj_ki_aadat.png')); files.append('aaj_ki_aadat.png')
        info['files']['common'] = files
        json.dump(info, open(os.path.join(OUT, 'today.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        b.close()
    print('ठीक:', json.dumps(info, ensure_ascii=False))

if __name__ == '__main__':
    main()
