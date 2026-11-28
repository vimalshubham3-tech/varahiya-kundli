# English posters: daily/<city>/en/*.png and daily/common/en/*.png  (run after posters.py)
import os, sys, re, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import posters as P
from playwright.sync_api import sync_playwright

today = P.today
WD = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MON = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
DATE_E = '%d %s %d · %s' % (today.day, MON[today.month - 1], today.year, WD[today.weekday()])
CITIES = {'gwalior': ('ग्वालियर', 'Gwalior'), 'sumaoli': ('सुमावली', 'Sumaoli')}
esc = P.esc
CSS = P.CSS.replace("@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');",
                    "@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&display=swap');"
                    ).replace("font-family:'Noto Sans Devanagari',sans-serif", "font-family:'Noto Sans','Noto Sans Devanagari',sans-serif")
FOOT = 'Varahiya Help Desk · with you every moment'

def page(title, sub, body):
    return ('<html><head><meta charset="utf-8"><style>%s</style></head><body><div class="p"><div class="in">'
            '<div class="hd"><img class="lg" src="%s"><small>|| Shri Jinaya Namah ||</small>'
            '<h1>%s</h1><div class="sub">%s</div></div><div class="bd">%s</div>'
            '<div class="ft">%s<span>Varahiya Jain Panchang &amp; Jyotish Vastu Darshan · %s</span></div></div></div></body></html>'
            % (CSS, P.LOGO, title, sub, body, FOOT, P.LINK))

JS_EN = """()=>{
 const res=document.getElementById('pn_res');const R=[];
 res.querySelectorAll('.tw>table>tbody>tr').forEach(tr=>{if(tr.cells.length>1)R.push([tr.cells[0].textContent.replace(/\\s+/g,' ').trim(),tr.cells[1].innerText.split('\\n').map(s=>s.trim()).filter(Boolean)]);});
 const row=k=>{for(const r of R){if(r[0].indexOf(k)===0)return r[1];}return [];};
 const one=k=>row(k).join(' ');
 const first=k=>{const a=row(k);return a.length?a[0].split(' — ')[0].replace(/\\s*\\(.*?\\)\\s*/g,'').trim():'';};
 const seg=k=>row(k).join('').split(/(?<=[\\d)])(?=[A-Z])/).map(s=>{const m=s.match(/^(.*?) — (.*)$/);if(!m)return [s,''];const t=m[2].match(/(\\d\\d:\\d\\d(?: \\(\\+1\\))?)\\s*$/);return [m[1].replace(/\\s*\\(.*?\\)\\s*/g,'').trim(),t?'till '+t[1]:m[2]];});
 const iv=s=>{const m=(s||'').match(/(\\d\\d:\\d\\d)\\s*[–-]\\s*(\\d\\d:\\d\\d)/);return m?m[1]+'–'+m[2]:'';};
 const lst=a=>{const o=[];a.forEach(x=>{const t=iv(one(x[1]));if(t)o.push([x[0],t]);});return o;};
 return {tithi:first('Tithi ('),nak:first('Nakshatra ('),wd:one('Day'),sr:one('Sunrise / Sunset').split('/')[0].trim(),
  segs:{tithi:seg('Tithi ('),nak:seg('Nakshatra ('),yoga:seg('Yoga ('),karan:seg('Karan ('),moon:seg('Moon sign (')},
  sun:one('Sun sign'),ss:one('Sunrise / Sunset'),mr:one('Moonrise'),
  shubh:lst([['Amrit Kaal','Amrit Kaal'],['Abhijit','Abhijit'],['Vijay','Vijay'],['Godhuli','Godhuli'],['Brahma Muhurta','Brahma']]),
  ashubh:lst([['Rahu Kaal','Rahu Kaal'],['Gulika','Gulika'],['Yamaganda','Yamaganda'],['Bhadra','Bhadra (inauspicious)'],['Durmuhurta','Durmuhurta']]),
  chd:one('Choghadiya — Day'),chn:one('Choghadiya — Night')};}"""

def tr(pg, s):
    return pg.evaluate("(s)=>window.__vjTr?window.__vjTr(s):s", s)

def panchang_poster(city, x):
    def seg(a):
        return ''.join('<div class="sg"><b>%s</b><span>%s</span></div>' % (esc(n), esc(t)) for n, t in a[:3])
    css = ('<style>.g{display:grid;grid-template-columns:1fr 1fr;gap:14px}.c{background:#fff;border:2px solid #e3c987;border-radius:16px;padding:14px 18px}'
           '.c h4{font-size:26px;color:#a0651b;font-weight:600;margin-bottom:4px}.sg{display:flex;justify-content:space-between;gap:10px;font-size:29px;color:#3b0c16;padding:2px 0}'
           '.sg b{font-weight:700;color:#7a1a2c}.sg span{font-size:24px;color:#5a2a35;text-align:right}'
           '.t{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px}.t div{border-radius:16px;padding:12px 18px;font-size:30px;font-weight:600;display:flex;justify-content:space-between}'
           '.t .a{background:#fff3d6;border:2px solid #d4a84b;color:#3b0c16}.t .b{background:#7a1a2c;color:#fff}.t b{font-weight:700}</style>')
    s = x['segs']
    cards = ''.join('<div class="c"><h4>%s</h4>%s</div>' % (h, seg(s[k])) for h, k in [('Tithi', 'tithi'), ('Nakshatra', 'nak'), ('Yoga', 'yoga'), ('Karan', 'karan')])
    cards += '<div class="c"><h4>Moon sign</h4>%s</div><div class="c"><h4>Sun sign</h4><div class="sg"><b>%s</b></div><h4 style="margin-top:8px">Sunrise / Sunset</h4><div class="sg"><b>%s</b></div></div>' % (seg(s['moon']), esc(x['sun']), esc(x['ss']))
    tm = ''.join('<div class="a"><span>%s</span><b>%s</b></div>' % (esc(a), esc(b)) for a, b in x['shubh'][:3])
    tm += ''.join('<div class="b"><span>%s</span><b>%s</b></div>' % (esc(a), esc(b)) for a, b in x['ashubh'][:3])
    body = '<style>.dtx{}</style>' + css + '<div class="dt">%s</div><div class="g">%s</div><div class="t">%s</div>' % (DATE_E, cards, tm)
    return page('Daily Panchang', city, body)

def chog_poster(city, x):
    def parse(t):
        out = []
        for m in re.finditer(r'(\d\d:\d\d)[–-](\d\d:\d\d)\s*([A-Za-z ]+?)\s*(✓)?(?=\s*\d\d:\d\d[–-]|\s*$)', t):
            nm = m.group(3).strip()
            if nm.lower() == 'auspicious':
                nm = 'Shubh'
            out.append((m.group(1) + '–' + m.group(2), nm, bool(m.group(4))))
        return out
    css = ('<style>.cl{display:flex;gap:18px}.cl>div{flex:1}.cl h3{font-size:34px;color:#7a1a2c;margin-bottom:10px;text-align:center}'
           '.i{display:flex;justify-content:space-between;background:#fff;border:2px solid #e3c987;border-radius:14px;padding:10px 16px;margin-bottom:9px;font-size:27px;font-weight:600;color:#3b0c16}'
           '.i.ok{background:#e9f7e1;border-color:#7bbf5a}.i.bad{background:#fff0ea;border-color:#e0907a}.i b{font-weight:700}</style>')
    good = {'Amrit', 'Shubh', 'Labh', 'Char'}
    def col(title, t):
        rows = ''.join('<div class="i %s"><span>%s</span><b>%s</b></div>' % ('ok' if n in good else 'bad', a, n) for a, n, ok in parse(t))
        return '<div><h3>%s</h3>%s</div>' % (title, rows)
    body = css + '<div class="dt">%s</div><div class="cl">%s%s</div><div style="text-align:center;font-size:25px;color:#5a2a35;margin-top:8px">Green = favourable · Red = avoid new work</div>' % (DATE_E, col('Day', x['chd']), col('Night', x['chn']))
    return page('Choghadiya', city, body)

def week_poster(city, days):
    css = ('<style>.r{display:flex;align-items:center;gap:16px;background:#fff;border:2px solid #e3c987;border-radius:18px;padding:16px 22px;margin-bottom:14px}'
           '.r.now{background:#fff0c2;border-color:#d4a84b}.r .d{min-width:230px}.r .d b{display:block;font-size:44px;color:#7a1a2c;line-height:1.1}'
           '.r .d small{font-size:26px;color:#a0651b;font-weight:600}.r .t{flex:1;font-size:32px;font-weight:700;color:#3b0c16;line-height:1.35}'
           '.r .t small{display:block;font-size:26px;font-weight:500;color:#5a2a35}</style>')
    rows = ''
    for i, x in enumerate(days):
        rows += ('<div class="r%s"><div class="d"><b>%s</b><small>%s %s</small></div><div class="t">%s<small>Nakshatra: %s · Sunrise %s</small></div></div>'
                 % (' now' if i == 0 else '', esc(x['day']), esc(x['mon']), esc(x['wd']), esc(x['tithi']), esc(x['nak']), esc(x['sr'])))
    return page('Next 7 Days Panchang', 'Tithi & Nakshatra · ' + city, css + rows)

def shubh_poster(city, d):
    def blk(title, items, cls):
        r = ''.join('<div class="i"><span>%s</span><b>%s</b></div>' % (esc(a), esc(b)) for a, b in items) or '<div class="i"><span>—</span></div>'
        return '<div class="bk %s"><h3>%s</h3>%s</div>' % (cls, title, r)
    css = ('<style>.bk{border-radius:22px;padding:22px 30px;margin-bottom:20px}.bk h3{font-size:38px;margin-bottom:10px}'
           '.bk.g{background:#fff3d6;border:2px solid #d4a84b;color:#3b0c16}.bk.g h3{color:#7a1a2c}.bk.b{background:#7a1a2c;color:#fff}.bk.b h3{color:#ffd978}'
           '.i{display:flex;justify-content:space-between;font-size:38px;padding:9px 0;border-bottom:1px solid #ffffff33}.bk.g .i{border-color:#d4a84b66}.i b{font-weight:700}'
           '.nt{font-size:27px;color:#5a2a35;text-align:center;margin-top:6px}</style>')
    body = (css + '<div class="dt">%s</div>' % DATE_E + blk('✅ Auspicious times (new work, shopping, travel)', d['shubh'], 'g')
            + blk('⚠️ Inauspicious times (avoid auspicious work)', d['ashubh'], 'b') + '<div class="nt">Times as per sunrise at %s</div>' % esc(city))
    return page("Today's Shubh Muhurta", city, body)

def rashi_posters(rs):
    out = []
    star = lambda n: '★' * n + '☆' * (5 - n)
    css = ('<style>.g{display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:1fr;gap:16px;flex:1}.c{background:#fff;border:2px solid #e3c987;border-radius:16px;padding:16px 20px}'
           '.c b{font-size:38px;color:#7a1a2c}.c i{font-style:normal;float:right;color:#c27a0e;font-size:28px;letter-spacing:1px}'
           '.c p{font-size:30px;line-height:1.4;margin-top:8px;color:#3b0c16;font-weight:500}</style>')
    for n, part in enumerate([rs[:6], rs[6:]]):
        cards = ''.join('<div class="c"><b>%s</b><i>%s</i><p>%s</p></div>' % (esc(r['n']), star(r['s']), esc(r['t'])) for r in part)
        sub = '%s · %s' % ('Aries to Virgo' if n == 0 else 'Libra to Pisces', DATE_E)
        out.append(page("Today's Horoscope", sub, css + '<div class="g">%s</div>' % cards))
    return out

def tip_poster(habit, career, skill):
    css = ('<style>.bx{background:#fff3d6;border:2px solid #d4a84b;border-radius:22px;padding:34px 38px;margin-bottom:26px;flex:1;display:flex;flex-direction:column;justify-content:center}'
           '.bx h3{font-size:36px;color:#7a1a2c;margin-bottom:10px}.bx p{font-size:48px;font-weight:600;line-height:1.45;color:#3b0c16}'
           '.bx.s p{font-size:38px}</style>')
    body = css + '<div class="dt">%s</div><div class="bx"><h3>💡 Today\'s Habit</h3><p>%s</p></div>' % (DATE_E, esc(habit))
    if career:
        body += '<div class="bx s"><h3>💼 Career tip of the day</h3><p>%s</p></div>' % esc(career)
    if skill:
        body += '<div class="bx s"><h3>💻 Skill tip of the day</h3><p>%s</p></div>' % esc(skill)
    return page("Today's Habit", 'A thought & a lesson', body)

SUTRA_EN = [
 ('Tattvartha Sutra', 'Right faith, right knowledge and right conduct together form the path to liberation.'),
 ('Tattvartha Sutra', 'Sincere faith in the fundamental realities, such as the soul, is right faith.'),
 ('Tattvartha Sutra', 'Knowing and perceiving (upayoga) is the defining mark of the soul.'),
 ('Tattvartha Sutra', 'The function of souls is to support one another.'),
 ('Tattvartha Sutra', 'That which arises, passes away and yet remains permanent in essence is "sat" (real).'),
 ('Tattvartha Sutra', 'Abstaining from violence, falsehood, theft, unchastity and possessiveness is the vow.'),
 ('Tattvartha Sutra', "Harming another's life through carelessness or passion is violence."),
 ('Tattvartha Sutra', 'Speaking harmful or untrue words is falsehood.'),
 ('Tattvartha Sutra', 'Taking what has not been given is theft.'),
 ('Tattvartha Sutra', 'Attachment to things is possessiveness.'),
 ('Tattvartha Sutra', 'Austerity sheds old karmas.'),
 ('Tattvartha Sutra', 'The activity of body, speech and mind is called yoga.'),
 ('Namokar Mantra', 'Salutation to the Arihants, who conquered attachment and aversion and attained Kevalgyan.'),
 ('Namokar Mantra', 'Salutation to the Siddhas, who are free of all karmas.'),
 ('Namokar Mantra', 'Salutation to the Acharyas, who practise conduct themselves and guide the sangh.'),
 ('Namokar Mantra', 'Salutation to the Upadhyayas, who teach the scriptures and impart knowledge.'),
 ('Namokar Mantra', 'Salutation to all the sadhus of the world.'),
 ('Jain principle', 'Non-violence is the highest dharma — causing no pain to any being.'),
 ('Kshama-path', 'I have friendship with all beings; I have enmity with none.'),
]

def sutra_poster():
    i = today.toordinal() % len(P.SUTRA)
    t = P.SUTRA[i]
    src, mean = SUTRA_EN[i]
    css = ('<style>.bx{background:#fff3d6;border:2px solid #d4a84b;border-radius:24px;padding:40px 40px;margin-bottom:22px;text-align:center}'
           '.bx small{display:block;font-size:30px;color:#a0651b;font-weight:600;margin-bottom:14px}'
           '.bx .s{font-size:60px;line-height:1.4;color:#7a1a2c;font-weight:700}'
           '.bx .m{font-size:38px;line-height:1.5;color:#3b0c16;font-weight:500;margin-top:20px}'
           '.nm{background:#7a1a2c;color:#ffd978;border-radius:20px;padding:22px;text-align:center;font-size:36px;font-weight:600;line-height:1.6}'
           '.nm small{display:block;color:#fff;font-size:26px;font-weight:500;margin-bottom:6px}</style>')
    body = (css + '<div class="dt">%s</div><div class="bx"><small>%s</small><div class="s">%s</div><div class="m">Meaning: %s</div></div>'
            '<div class="nm"><small>Namokar Mantra</small>%s</div>' % (DATE_E, esc(src), esc(t[0]), esc(mean), P.NAMOKAR))
    return page("Today's Jain Sutra", 'One sutra a day, with a simple meaning', body)

def main():
    D = json.load(open(os.path.join(P.ROOT, 'push', 'daily.json'), encoding='utf-8'))
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width': 390, 'height': 800}, device_scale_factor=1, service_workers='block',
                            timezone_id='Asia/Kolkata', locale='en-IN')
        ctx.add_init_script("localStorage.setItem('vj_reg_v1',JSON.stringify({name:'Varahiya Help Desk',mobile:'9977004518',done:1}));"
                            "localStorage.setItem('vj_prof_v1',JSON.stringify({show:0,photo:0}));")
        info = {}
        data = None
        pgt = None
        for key, (hn, en) in CITIES.items():
            d = os.path.join(P.OUT, key, 'en')
            os.makedirs(d, exist_ok=True)
            pg = ctx.new_page()
            pg.goto(P.APP)
            pg.wait_for_timeout(2500)
            pg.evaluate("document.documentElement.lang!=='en'&&document.getElementById('lang').click()")
            pg.wait_for_timeout(1200)
            pg.evaluate("""(n)=>{const s=document.getElementById('pn_place');const o=[...s.options].find(o=>n.indexOf(o.textContent.trim())>=0);
              s.value=o.value;s.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('pn_go').click();}""", [hn, en])
            pg.wait_for_timeout(1500)
            days, today_x = [], None
            for i in range(7):
                dt = today + datetime.timedelta(days=i)
                pg.evaluate("(v)=>{const e=document.getElementById('pn_date');e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('pn_go').click();}", dt.isoformat())
                pg.wait_for_timeout(900)
                x = pg.evaluate(JS_EN)
                x['day'] = str(dt.day); x['mon'] = MON[dt.month - 1]; x['wd'] = WD[dt.weekday()]
                days.append(x)
                if i == 0:
                    today_x = x
            P.shot(ctx, panchang_poster(en, today_x), os.path.join(d, 'panchang.png'))
            P.shot(ctx, chog_poster(en, today_x), os.path.join(d, 'choghadiya.png'))
            P.shot(ctx, week_poster(en, days), os.path.join(d, 'saptah_panchang.png'))
            P.shot(ctx, shubh_poster(en, today_x), os.path.join(d, 'shubh_muhurat.png'))
            info[key] = ['panchang.png', 'choghadiya.png', 'saptah_panchang.png', 'shubh_muhurat.png']
            pg.evaluate("(v)=>{const e=document.getElementById('pn_date');e.value=v;e.dispatchEvent(new Event('change',{bubbles:true}));document.getElementById('pn_go').click();}", today.isoformat())
            pg.wait_for_timeout(900)
            if key == 'gwalior':
                data = pg.evaluate("""()=>{
                  const r=[...document.getElementById('rf_r').children];
                  const tips=r[0].innerText;
                  const rs=r.slice(1).filter(e=>e.querySelector('b')&&e.querySelector('span')&&e.querySelector('div')).map(e=>{const s=e.querySelector('span').textContent;return {n:e.querySelector('b').textContent,s:(s.match(/★/g)||[]).length,t:e.querySelector('div').textContent}});
                  const car=(tips.match(/career tip:\\s*([^\\n💻]+)/i)||[])[1]||'', sk=(tips.match(/skill tip:\\s*(.+)/i)||[])[1]||'';
                  return {rs:rs,career:car.trim(),skill:sk.trim(),habit:(document.getElementById('pd_td')||{}).textContent||''};}""")
                pgt = pg
            else:
                pg.close()
        # Jain tithi + upcoming kalyanak (translate daily.json strings through the app's translator)
        cm = os.path.join(P.OUT, 'common', 'en')
        os.makedirs(cm, exist_ok=True)
        files = []
        for i, htm in enumerate(rashi_posters(data['rs']), 1):
            n = 'rashifal_%d.png' % i
            P.shot(ctx, htm, os.path.join(cm, n)); files.append(n)
        t = D.get(today.isoformat())
        if t:
            T = lambda s: tr(pgt, s)
            rows = ''
            if t.get('kal'):
                rows += '<div class="bx"><h3>🙏 Today\'s Kalyanak</h3>' + ''.join('<p>%s</p>' % esc(T(x)) for x in t['kal']) + '</div>'
            if t.get('parv'):
                rows += '<div class="bx"><h3>🪔 Today\'s Parv / Vrat</h3>' + ''.join('<p>%s</p>' % esc(T(x)) for x in t['parv']) + '</div>'
            if not rows:
                rows = '<div class="bx"><h3>🙏 Today</h3><p>No kalyanak or special parv today. Remember Dev-Shastra-Guru, recite the Namokar Mantra and do swadhyay.</p></div>'
            up = []
            for i in range(1, 40):
                d2 = today + datetime.timedelta(days=i)
                e = D.get(d2.isoformat())
                if e and (e['kal'] or e['parv']):
                    for x in (e['kal'] + e['parv']):
                        up.append((d2, T(x)))
                if len(up) >= 4:
                    break
            nx = ''.join('<div class="up"><b>%d %s</b><span>%s</span></div>' % (a.day, MON[a.month - 1][:3], esc(x)) for a, x in up[:4])
            css = ('<style>.bx{background:#fff3d6;border:2px solid #d4a84b;border-radius:20px;padding:22px 28px;margin-bottom:20px}'
                   '.bx h3{font-size:34px;color:#7a1a2c;margin-bottom:8px}.bx p{font-size:38px;font-weight:600;line-height:1.45;color:#3b0c16}'
                   '.tt{display:flex;justify-content:space-around;margin-bottom:22px}.tt div{background:#fff;border:2px solid #e3c987;border-radius:18px;padding:12px 24px;text-align:center;font-size:38px;font-weight:700;color:#7a1a2c}'
                   '.tt small{display:block;font-size:24px;color:#a0651b;font-weight:500}'
                   '.nx{font-size:34px;font-weight:700;color:#7a1a2c;margin:18px 0 10px}'
                   '.up{display:flex;gap:18px;align-items:center;padding:10px 0;border-bottom:1px dashed #d4a84b;font-size:30px}.up b{min-width:170px;color:#a0651b}</style>')
            body = css + ('<div class="dt">%s</div><div class="tt"><div><small>Tithi</small>%s</div><div><small>Month</small>%s</div></div>%s<div class="nx">Upcoming kalyanak / parv</div>%s'
                          % (DATE_E, esc(T(t['tithi'])), esc(T(t['mas'])), rows, nx))
            P.shot(ctx, page('Jain Tithi & Kalyanak', "Today's Jain Panchang", body), os.path.join(cm, 'jain_tithi.png')); files.append('jain_tithi.png')
            # upcoming list poster
            rows, n = '', 0
            for i in range(0, 45):
                dt = today + datetime.timedelta(days=i)
                e = D.get(dt.isoformat())
                if not e or not (e['kal'] or e['parv']):
                    continue
                rows += '<div class="r%s"><b>%d %s<small>%s</small></b><em>%s</em><span>%s</span></div>' % (
                    ' now' if i == 0 else '', dt.day, MON[dt.month - 1][:3], WD[dt.weekday()], esc(T(e['tithi'])), esc(' · '.join(T(z) for z in e['kal'] + e['parv'])))
                n += 1
                if n >= 9:
                    break
            if not rows:
                rows = '<div class="r"><span>No kalyanak/parv recorded in the next 45 days</span></div>'
            css = ('<style>.r{display:flex;gap:16px;align-items:center;background:#fff;border:2px solid #e3c987;border-radius:16px;padding:14px 18px;margin-bottom:12px;font-size:27px}'
                   '.r b{min-width:170px;color:#7a1a2c;font-size:34px;line-height:1.15}.r b small{display:block;font-size:23px;color:#a0651b;font-weight:600}'
                   '.r em{font-style:normal;min-width:190px;color:#a0651b;font-weight:600;font-size:25px}.r span{flex:1;font-weight:600;line-height:1.3}'
                   '.r.now{background:#fff0c2;border-color:#d4a84b}</style>')
            P.shot(ctx, page('Upcoming Kalyanak & Parv', 'Next few weeks · ' + DATE_E, css + '<div>%s</div>' % rows), os.path.join(cm, 'vrat_calendar.png')); files.append('vrat_calendar.png')
        P.shot(ctx, sutra_poster(), os.path.join(cm, 'jain_sutra.png')); files.append('jain_sutra.png')
        P.shot(ctx, tip_poster(data['habit'], data['career'], data['skill']), os.path.join(cm, 'aaj_ki_aadat.png')); files.append('aaj_ki_aadat.png')
        info['common'] = files
        if pgt:
            pgt.close()
        b.close()
    print('OK:', json.dumps(info))

if __name__ == '__main__':
    main()
