"""Renders the Experiencing Agency app screens (375x812 @2x) into ../images with headless Chromium.
Run from this folder: python3 render.py ../images   (needs Python Playwright with Chromium, plus Inter and Lora installed).
This folder is not published; the build only copies images/ and files/.
"""
import sys, pathlib
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(sys.argv[1])
HERE = pathlib.Path(__file__).parent

CSS = """
@font-face { font-family: Lora; src: url(file:///usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf); font-weight: 400 700; }
:root {
  --linden: #2E5B3F; --linden-deep: #234832; --leaf: #E3EDDF; --leaf-2: #C9DCC3;
  --ink: #18201B; --muted: #5C6760; --line: #E1E5E0; --paper: #FBFBF9; --white: #fff;
  --zahra: #F2D3C2; --jan: #CFDCEB; --agatha: #E8DDB5;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 375px; height: 812px; overflow: hidden; }
body { font-family: Inter, sans-serif; color: var(--ink); background: var(--paper);
  -webkit-font-smoothing: antialiased; font-feature-settings: "cv11", "ss03"; }
.screen { position: relative; width: 375px; height: 812px; display: flex; flex-direction: column; }

/* Group header: the group's colour and symbol on every screen */
.group { background: var(--linden); color: var(--white); padding: 0 20px 16px; }
.status { height: 47px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 10px 0 14px; font: 600 16px/1 Inter; letter-spacing: -0.2px; }
.status svg { display: block; }
.status .right { display: flex; gap: 6px; align-items: center; }
.ident { display: flex; gap: 12px; align-items: center; margin-top: 6px; }
.mark { width: 42px; height: 42px; border-radius: 50%; background: var(--leaf); flex: none;
  display: grid; place-items: center; }
.ident h1 { font: 600 20px/1.15 Lora, serif; letter-spacing: -0.1px; }
.ident p { font: italic 400 14px/1.3 Lora, serif; opacity: .85; margin-top: 2px; }

.body { flex: 1; padding: 22px 20px 0; overflow: hidden; }
.title { font: 600 26px/1.15 Lora, serif; letter-spacing: -0.3px; }
.sub { font-size: 15px; line-height: 1.45; color: var(--muted); margin-top: 6px; }

/* Tab bar: meetings now live in the main menu */
.tabs { height: 84px; border-top: 1px solid var(--line); background: var(--white);
  display: grid; grid-template-columns: repeat(4, 1fr); padding-top: 9px; }
.tab { display: flex; flex-direction: column; align-items: center; gap: 4px;
  font-size: 10.5px; font-weight: 500; color: #7D867F; }
.tab.on { color: var(--linden); }
.tab .badge { position: absolute; margin-left: 18px; margin-top: -2px; width: 8px; height: 8px;
  border-radius: 50%; background: #C8553D; border: 1.5px solid var(--white); }
.tab .ic { position: relative; }
.home-ind { position: absolute; bottom: 8px; left: 50%; transform: translateX(-50%);
  width: 134px; height: 5px; border-radius: 3px; background: var(--ink); }

/* Welcome summary rows, each a way in */
.rows { margin-top: 18px; background: var(--white); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
.row { display: flex; align-items: center; gap: 14px; padding: 15px 14px 15px 16px; }
.row + .row { border-top: 1px solid var(--line); }
.row .n { width: 34px; height: 34px; border-radius: 10px; background: var(--leaf); color: var(--linden-deep);
  display: grid; place-items: center; font: 600 16px/1 Inter; flex: none; }
.row .t { flex: 1; font-size: 15px; line-height: 1.35; }
.row .t small { display: block; font-size: 13px; color: var(--muted); margin-top: 2px; }
.chev { flex: none; }

.next { margin-top: 18px; background: var(--leaf); border-radius: 14px; padding: 16px; display: flex; gap: 14px; }
.next .lbl { font-size: 13px; color: var(--linden-deep); font-weight: 500; }
.next h3 { font: 600 18px/1.25 Lora, serif; margin-top: 3px; }
.next p { font-size: 14px; color: var(--muted); margin-top: 3px; }
.next .ill { flex: none; align-self: center; }

.pulse { margin-top: 18px; display: flex; gap: 12px; align-items: center; font-size: 14px; color: var(--muted); line-height: 1.4; padding: 0 2px; }

/* Meetings */
.chips { display: flex; gap: 8px; margin-top: 16px; }
.chip { height: 34px; padding: 0 13px; border-radius: 17px; border: 1px solid #CDD3CD; background: var(--white);
  display: flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 500; }
.chip.on { background: var(--linden); border-color: var(--linden); color: var(--white); }
.day { font-size: 13px; font-weight: 600; color: var(--muted); margin: 20px 0 8px; }
.meet { background: var(--white); border: 1px solid var(--line); border-radius: 14px; padding: 14px 14px 14px 16px;
  display: flex; gap: 12px; align-items: center; }
.meet + .meet { margin-top: 10px; }
.meet .ico { width: 48px; height: 48px; border-radius: 12px; background: var(--leaf); display: grid; place-items: center; flex: none; }
.meet .info { flex: 1; min-width: 0; }
.meet h3 { font-size: 16px; font-weight: 600; line-height: 1.3; }
.meet .when { font-size: 13.5px; color: var(--muted); margin-top: 2px; }
.who { white-space: nowrap; display: flex; align-items: center; gap: 8px; margin-top: 9px; font-size: 13px; color: var(--ink); }
.stack { display: flex; }
.stack .av { width: 22px; height: 22px; font-size: 9.5px; border: 2px solid var(--white); margin-left: -6px; }
.stack .av:first-child { margin-left: 0; }
.meet.open { border-style: dashed; border-color: #AFC3A8; background: #F6F9F4; }
.meet.open .ico { background: var(--white); }
.tag { display: inline-block; font-size: 12px; font-weight: 600; color: var(--linden-deep); background: var(--leaf);
  border-radius: 6px; padding: 3px 7px; margin-top: 8px; }

/* Avatars */
.av { width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center; flex: none;
  font: 600 13px/1 Inter; color: var(--ink); }
.av.z { background: var(--zahra); } .av.j { background: var(--jan); } .av.a { background: var(--agatha); }
.av.m { background: #D9D4EA; } .av.you { background: var(--linden); color: var(--white); }

/* Discussion */
.back { display: flex; align-items: center; gap: 4px; font-size: 15px; color: var(--linden); font-weight: 500; margin: -4px 0 12px -4px; }
.meta { display: flex; gap: 14px; margin-top: 10px; font-size: 13.5px; color: var(--muted); }
.meta span { display: flex; gap: 5px; align-items: center; }
.hr { height: 1px; background: var(--line); margin: 18px 0 16px; }
.h2 { font-size: 15px; font-weight: 600; display: flex; justify-content: space-between; }
.h2 span { font-weight: 400; color: var(--muted); font-size: 13.5px; }
.c { display: flex; gap: 11px; margin-top: 16px; }
.c .bub { flex: 1; }
.c .nm { font-size: 14px; font-weight: 600; display: flex; gap: 8px; align-items: baseline; }
.c .nm time { font-weight: 400; font-size: 12.5px; color: var(--muted); }
.c p { font-size: 15px; line-height: 1.45; margin-top: 3px; }
.c.mine .bub { background: var(--leaf); border-radius: 4px 14px 14px 14px; padding: 10px 12px 12px; margin-top: -2px; }
.flag { display: inline-flex; gap: 5px; align-items: center; font-size: 12px; font-weight: 600; color: var(--white);
  background: var(--linden); border-radius: 10px; padding: 3px 8px 3px 6px; }
.compose { position: absolute; left: 0; right: 0; bottom: 84px; padding: 10px 16px; background: var(--paper);
  border-top: 1px solid var(--line); display: flex; gap: 10px; align-items: center; }
.field { flex: 1; height: 42px; border-radius: 21px; border: 1px solid #CDD3CD; background: var(--white);
  display: flex; align-items: center; padding: 0 16px; font-size: 15px; color: #848C86; }
.send { width: 42px; height: 42px; border-radius: 50%; background: var(--linden); display: grid; place-items: center; }
.send.idle { background: #C7CFC8; }
.posted { margin: 10px 0 0 47px; font-size: 13.5px; color: var(--linden-deep); display: flex; gap: 6px; align-items: center; }
.toast { position: absolute; left: 16px; right: 16px; bottom: 150px; background: var(--ink); color: var(--white);
  border-radius: 12px; padding: 12px 14px; font-size: 14px; line-height: 1.4; display: flex; gap: 10px; align-items: center;
  box-shadow: 0 8px 24px rgba(24,32,27,.18); }

/* Thank-you */
.thanks { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 64px 12px 0; }
.thanks .big { width: 112px; height: 112px; border-radius: 50%; background: var(--leaf); display: grid; place-items: center; }
.thanks h2 { font: 600 27px/1.2 Lora, serif; margin-top: 26px; letter-spacing: -0.3px; }
.thanks p { font-size: 16px; line-height: 1.5; color: var(--muted); margin-top: 12px; max-width: 300px; }
.quote { margin-top: 22px; background: var(--white); border: 1px solid var(--line); border-radius: 14px;
  padding: 14px 16px; text-align: left; width: 100%; }
.quote small { font-size: 12.5px; color: var(--muted); font-weight: 500; }
.quote div { font: 500 16px/1.4 Inter; margin-top: 4px; }
.btn { margin-top: 26px; width: 100%; height: 50px; border-radius: 25px; background: var(--linden); color: var(--white);
  display: grid; place-items: center; font-size: 16px; font-weight: 600; }
.link { margin-top: 14px; font-size: 15px; font-weight: 500; color: var(--linden); }
"""

# --- icons -------------------------------------------------------------
def sprout(size=24, stem="#2E5B3F", leaf="#2E5B3F", fill=True):
    f = leaf if fill else "none"
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{stem}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
<path d="M12 21v-9"/><path d="M12 12c0-4 3-6.5 7.5-6.5 0 4.2-3 6.5-7.5 6.5z" fill="{f}"/><path d="M12 14.5C12 11 9.6 9 6 9c0 3.4 2.4 5.5 6 5.5z" fill="{f}"/><path d="M7.5 21h9"/></svg>'''

def pot(size=26):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="#234832" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
<path d="M12 13V8"/><path d="M12 9c0-3 2.2-4.8 5.5-4.8 0 3.1-2.2 4.8-5.5 4.8z" fill="#2E5B3F"/><path d="M12 10.5C12 8 10.2 6.5 7.5 6.5c0 2.5 1.8 4 4.5 4z" fill="#2E5B3F"/><path d="M6.5 13h11l-1.4 7.2a1 1 0 0 1-1 .8H8.9a1 1 0 0 1-1-.8z" fill="#fff"/></svg>'''

def hall(size=26):  # town hall, for the meeting with the mayor
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="#234832" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
<path d="M3.5 9 12 4l8.5 5z" fill="#fff"/><path d="M5.5 9.5v8M9.8 9.5v8M14.2 9.5v8M18.5 9.5v8"/><path d="M3.5 20h17"/></svg>'''

def bulb(size=26):
    return f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="#2E5B3F" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
<path d="M9 17.5h6M10 20.5h4"/><path d="M12 3.5a6 6 0 0 0-3.6 10.8c.4.3.6.8.6 1.3v.4h6v-.4c0-.5.2-1 .6-1.3A6 6 0 0 0 12 3.5z"/></svg>'''

ICON = {
 'home': '<path d="M4 10.5 12 4l8 6.5V19a1 1 0 0 1-1 1h-4.5v-5.5h-5V20H5a1 1 0 0 1-1-1z"/>',
 'cal': '<rect x="4" y="5.5" width="16" height="14.5" rx="2.5"/><path d="M4 10h16M8.5 3.5v4M15.5 3.5v4"/>',
 'mega': '<path d="M4 10v4a1 1 0 0 0 1 1h2l8 4.5v-15L7 9H5a1 1 0 0 0-1 1z"/><path d="M18.5 9.5a3.5 3.5 0 0 1 0 5"/>',
 'group': '<circle cx="9" cy="8.5" r="3.2"/><path d="M3.5 19.5c.4-3.2 2.6-5 5.5-5s5.1 1.8 5.5 5"/><circle cx="16.8" cy="9.5" r="2.5"/><path d="M15.8 14.6c2.6-.3 4.5 1.3 4.9 4.4"/>',
}
def icon(name, color, size=25, fill=False):
    fl = color if fill else 'none'
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fl}" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>'

CHEV = '<svg class="chev" width="9" height="15" viewBox="0 0 9 15" fill="none" stroke="#9AA39C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1.5 1.5 7.5 7.5l-6 6"/></svg>'
BACK = '<svg width="11" height="18" viewBox="0 0 11 18" fill="none" stroke="#2E5B3F" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2 2 9l7 7"/></svg>'
SEND = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5.5 11.5 12 5l6.5 6.5"/></svg>'
CLOCK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#5C6760" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>'
PIN = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#5C6760" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/></svg>'
CHECK2 = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2E5B3F" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>'
CHECK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C9DCC3" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12.5 4.5 4.5L19 7.5"/></svg>'
NEWC = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>'
FILTER = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 7h16M7 12h10M10 17h4"/></svg>'

STATUS = '''<div class="status"><span>9:41</span><span class="right">
<svg width="18" height="12" viewBox="0 0 18 12" fill="#fff"><rect x="0" y="8" width="3" height="4" rx="1"/><rect x="5" y="5.5" width="3" height="6.5" rx="1"/><rect x="10" y="3" width="3" height="9" rx="1"/><rect x="15" y="0" width="3" height="12" rx="1"/></svg>
<svg width="16" height="12" viewBox="0 0 16 12" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round"><path d="M1.5 4.3a9.5 9.5 0 0 1 13 0"/><path d="M4 7a5.8 5.8 0 0 1 8 0"/><circle cx="8" cy="10" r="1.1" fill="#fff" stroke="none"/></svg>
<svg width="27" height="13" viewBox="0 0 27 13" fill="none"><rect x=".5" y=".5" width="23" height="12" rx="3.5" stroke="#fff" opacity=".45"/><rect x="2.5" y="2.5" width="19" height="8" rx="2" fill="#fff"/><path d="M25 4.5v4" stroke="#fff" stroke-width="1.5" stroke-linecap="round" opacity=".5"/></svg>
</span></div>'''

def header():
    return f'''<header class="group">{STATUS}<div class="ident"><div class="mark">{sprout(26)}</div>
<div><h1>ClimAction Wrangelkiez</h1><p>Together for a greener tomorrow</p></div></div></header>'''

def tabs(active, badge=None):
    items = [('home', 'Home'), ('cal', 'Meetings'), ('mega', 'Announcements'), ('group', 'Group')]
    out = []
    for key, label in items:
        on = key == active
        col = '#2E5B3F' if on else '#7D867F'
        b = '<span class="badge"></span>' if badge == key else ''
        out.append(f'<div class="tab{" on" if on else ""}"><span class="ic">{icon(key, col)}{b}</span>{label}</div>')
    return f'<nav class="tabs">{"".join(out)}</nav><div class="home-ind"></div>'

def page(inner):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="screen">{inner}</div></body></html>'

# --- screens -----------------------------------------------------------
welcome = page(f'''{header()}
<main class="body">
  <h2 class="title">Welcome back</h2>
  <p class="sub">Here's what's happened since Thursday.</p>
  <div class="rows">
    <div class="row"><span class="n">2</span><span class="t">replies to your comments<small>From Zahra and Jan</small></span>{CHEV}</div>
    <div class="row"><span class="n">1</span><span class="t">new meeting<small>Local impact: daycares, Tue 6 May</small></span>{CHEV}</div>
    <div class="row"><span class="n">2</span><span class="t">announcements<small>Tree watering rota, plant swap</small></span>{CHEV}</div>
  </div>
  <div class="next"><div style="flex:1"><div class="lbl">Next meeting</div><h3>Meeting with Mayor Wegner</h3><p>Friday 25 April, 18:00</p></div><div class="ill">{hall(40)}</div></div>
  <div class="pulse">{sprout(30, fill=False)}<span>The group is growing: 3 new members joined this month.</span></div>
</main>
{tabs('home')}''')

meetings = page(f'''{header()}
<main class="body">
  <h2 class="title">Meetings</h2>
  <div class="chips"><span class="chip">{FILTER} Topic</span><span class="chip on">{FILTER} Next two weeks</span></div>
  <div class="day">Today</div>
  <div class="meet open"><div class="ico">{bulb()}</div><div class="info"><h3>Topic still open</h3><div class="when">Weekly check-in, 19:00</div><span class="tag">Suggest a topic</span></div>{CHEV}</div>
  <div class="day">Friday 25 April</div>
  <div class="meet"><div class="ico">{hall()}</div><div class="info"><h3>Meeting with Mayor Wegner</h3><div class="when">18:00, Rotes Rathaus</div>
    <div class="who"><span class="stack"><span class="av j">JP</span><span class="av a">AK</span></span>Jan and 8 others discussing</div></div>{CHEV}</div>
  <div class="day">Tuesday 6 May</div>
  <div class="meet"><div class="ico">{pot()}</div><div class="info"><h3>Local impact: daycares</h3><div class="when">19:00, Nachbarschaftshaus</div>
    <div class="who"><span class="stack"><span class="av z">ZM</span><span class="av j">JP</span></span>Zahra and 3 others discussing</div></div>{CHEV}</div>
</main>
{tabs('cal')}''')

def discussion_head():
    return f'''<div class="back">{BACK} Meetings</div>
  <h2 class="title">Local impact: daycares</h2>
  <div class="meta"><span>{CLOCK} Tue 6 May, 19:00</span><span>{PIN} Nachbarschaftshaus</span></div>
  <div class="hr"></div>'''

ZAHRA = '''<div class="c"><span class="av z">ZM</span><div class="bub"><div class="nm">Zahra M <time>2 days ago</time></div>
  <p>I totally agree with rallying the local daycares! Although we should be careful to involve the one on Oppelner Str. again.</p></div></div>'''
JAN = '''<div class="c"><span class="av j">JP</span><div class="bub"><div class="nm">Jan P <time>Yesterday</time></div>
  <p>Yeah I remember last time we approached them... I'm also unsure about the one on the far end of Görlitzer Str.</p></div></div>'''

discussion = page(f'''{header()}
<main class="body">
  {discussion_head()}
  <div class="h2">Discussion <span>4 people</span></div>
  {ZAHRA}{JAN}
</main>
<div class="compose"><div class="field">Add a comment</div><div class="send idle">{SEND}</div></div>
{tabs('cal')}''')

new_comment = page(f'''{header()}
<main class="body">
  <div class="back">{BACK} Local impact: daycares</div>
  <div class="h2">Discussion <span>4 people</span></div>
  {ZAHRA}{JAN}
  <div class="c mine"><span class="av you">You</span><div class="bub"><div class="nm"><span class="flag">{NEWC} New comment</span> <time>Just now</time></div>
  <p>It seems you might not remember, but Agatha and I spoke to them 5 weeks ago and they're willing to collaborate again. I'll send over their contact details.</p></div></div>
  <div class="posted">{CHECK2} Posted. Zahra and Jan will see it on their next visit.</div>
</main>
<div class="compose"><div class="field">Add a comment</div><div class="send idle">{SEND}</div></div>
{tabs('cal')}''')

thanks = page(f'''{header()}
<main class="body">
  <div class="thanks">
    <div class="big">{sprout(58)}</div>
    <h2>Thanks for starting the conversation</h2>
    <p>Your topic is on the agenda for tonight's check-in. Others can add to it before 19:00.</p>
    <div class="quote"><small>Your topic</small><div>Watering the new street trees on Wrangelstraße over the summer</div></div>
    <div class="btn">See tonight's agenda</div>
    <div class="link">Back to meetings</div>
  </div>
</main>
{tabs('cal')}''')

SCREENS = {'welcome': welcome, 'meetings': meetings, 'discussion': discussion,
           'new-comment': new_comment, 'topic-thanks': thanks}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 375, 'height': 812}, device_scale_factor=2)
    for name, html in SCREENS.items():
        f = HERE / f'{name}.html'; f.write_text(html)
        pg.goto(f.as_uri()); pg.wait_for_timeout(250)
        pg.screenshot(path=str(OUT / f'{name}.jpg'), type='jpeg', quality=88)
        print('rendered', name)
    b.close()
