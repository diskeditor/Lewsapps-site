#!/usr/bin/env python3
"""Builds the static lewsapps.com site from apps.json into ./docs (served by GitHub Pages).

To release a new version of an app: edit its "version" and "download" in apps.json, run
  python3 build.py
and commit.
"""
import html, json, os, pathlib

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "docs"
APPS = json.loads((ROOT / "apps.json").read_text())
FREE_IRS = json.loads((ROOT / "free-irs.json").read_text())
FREE_IRS_COLOR = "#5fd1bd"
REQ = "macOS 13 Ventura or later · Apple silicon or Intel"
CONTACT = "lew@parabolicny.com"
YEAR = 2026

S = 'fill="none" stroke="#111" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"'
GLYPHS = {
    "cone": f'<svg viewBox="0 0 32 32" {S}><circle cx="16" cy="16" r="12"/><circle cx="16" cy="16" r="7"/><circle cx="16" cy="16" r="2.4" fill="#111"/></svg>',
    "paddle": f'<svg viewBox="0 0 32 32" {S}><rect x="4" y="10" width="24" height="12" rx="6"/><circle cx="22" cy="16" r="3.6" fill="#111"/><path d="M9 16h4"/></svg>',
    "conduit": f'<svg viewBox="0 0 32 32" {S}><path d="M4 11h18M17 6l5 5-5 5"/><path d="M28 21H10M15 16l-5 5 5 5"/></svg>',
    "silencer": f'<svg viewBox="0 0 32 32" {S}><path d="M5 12h5l7-6v20l-7-6H5z"/><path d="M21 12l7 8M28 12l-7 8"/></svg>',
    "transmitter-network": f'<svg viewBox="0 0 32 32" {S}><circle cx="7" cy="16" r="3.5"/><circle cx="25" cy="8" r="3.5"/><circle cx="25" cy="24" r="3.5"/><path d="M10.2 14.4l11.6-5M10.2 17.6l11.6 5"/></svg>',
    "channel": f'<svg viewBox="0 0 32 32" {S}><path d="M8 5v22M16 5v22M24 5v22"/><rect x="5" y="17" width="6" height="4" rx="1.2" fill="#111"/><rect x="13" y="9" width="6" height="4" rx="1.2" fill="#111"/><rect x="21" y="14" width="6" height="4" rx="1.2" fill="#111"/></svg>',
    "gauge": f'<svg viewBox="0 0 32 32" {S}><path d="M5 22a11 11 0 0 1 22 0"/><path d="M16 22l6-8"/><circle cx="16" cy="22" r="2" fill="#111"/><path d="M8.5 13.5l1.6 1.4M16 9v2M23.5 13.5l-1.6 1.4"/></svg>',
}
GLYPHS["free-irs"] = f'<svg viewBox="0 0 32 32" {S}><path d="M4 16h3l2-9 3 18 3-14 2 8 2-5 2 4 2-2h5"/></svg>'
TRANSMITTER_GLYPH = f'<svg viewBox="0 0 32 32" {S}><circle cx="16" cy="18" r="3" fill="#111"/><path d="M10 12a8.5 8.5 0 0 0 0 12M22 12a8.5 8.5 0 0 1 0 12M6 8a14 14 0 0 0 0 20M26 8a14 14 0 0 1 0 20"/></svg>'

e = html.escape


def icon(app, cls="icon", up=""):
    if (ROOT / "assets" / "icons" / f"{app['id']}.png").exists():
        return f'<img class="{cls} pic" style="--c:{app["color"]}" src="{up}assets/icons/{app["id"]}.png" alt="">'
    return f'<div class="{cls}" style="--c:{app["color"]}" aria-hidden="true">{GLYPHS.get(app["id"], e(app["name"][0]))}</div>'


def page(title, body, depth=0, desc="Pro Tools plug-ins and Mac apps for post production, from Parabolic.", mid=""):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta name="theme-color" content="#14161a">
<link rel="stylesheet" href="{up}assets/style.css">
<link rel="icon" type="image/png" href="{up}assets/favicon.png">
<link rel="apple-touch-icon" href="{up}assets/icon-180.png">
</head>
<body>
<header class="site"><div class="wrap">
  <a class="brand" href="{up}index.html"><img src="{up}assets/logo.webp" alt="Lew's Apps" height="34"> <small class="from-p">from <img class="parabolic" src="{up}assets/parabolic-logo.png" alt="Parabolic" width="600" height="146"></small></a>
  {mid}
  <nav class="top">
    <a href="{up}index.html#support">Support</a>
    <a href="{up}index.html#disclaimer">Disclaimer</a>
    <a class="hide-sm" href="{up}index.html#privacy">Privacy</a>
  </nav>
</div></header>
{body}
<footer class="site"><div class="wrap">
  <span class="foot-p"><img class="parabolic" src="{up}assets/parabolic-logo.png" alt="Parabolic" width="600" height="146"> © {YEAR} Parabolic · New York</span>
  <nav><a href="{up}index.html#support">Support</a><a href="{up}index.html#privacy">Privacy</a><a href="{up}index.html#disclaimer">Disclaimer</a><a href="mailto:{CONTACT}">Contact</a></nav>
</div></footer>
</body>
</html>
"""


def shot(a, up=""):
    return f"{up}assets/shots/{a['id']}.png" if (ROOT / "assets" / "shots" / f"{a['id']}.png").exists() else None


def app_card(a):
    sh = shot(a)
    thumb = f'<a class="thumb" href="apps/{a["id"]}.html"><img src="{sh}" alt="{e(a["name"])} screenshot" loading="lazy"></a>' if sh else ""
    support_btn = f'\n    <a class="btn sm" href="{a["support"][3:]}">Support</a>' if a["support"].startswith("../") else ""
    return f"""<article class="card app" style="--c:{a['color']}" data-kind="{'plugin' if 'plug-in' in a['kind'].lower() else 'app'}">
  <div class="head">{icon(a)}<div><div class="kind">{e(a['kind'])}</div><h3>{e(a['name'])}</h3></div></div>
  {thumb}
  <p>{e(a['summary'])}</p>
  <div class="req">{REQ}</div>
  <div class="actions">
    {download_buttons(a, 'btn primary sm')}
    <a class="btn sm" href="apps/{a['id']}.html">More info</a>{support_btn}
  </div>
</article>"""


def download_buttons(a, cls):
    """One Download button, or one per installer when an app has several ("downloads": [{"label", "url"}, …],
    e.g. Transmitter Network's plug-ins and its Receiver app)."""
    items = a.get("downloads") or [{"label": a["download_label"], "url": a["download"]}]
    return "\n    ".join(
        f'<a class="{cls}" href="{e(d["url"])}">{e(d["label"])} <span class="ver">v{e(a["version"])}</span></a>'
        for d in items)


def free_irs_card():
    """A card (not an app) pointing to free impulse-response libraries for Chamber, next to Chamber's card."""
    fake = {"id": "free-irs", "color": FREE_IRS_COLOR, "name": "IRs"}
    return f"""<article class="card app" style="--c:{FREE_IRS_COLOR}" data-kind="plugin">
  <div class="head">{icon(fake)}<div><div class="kind">For Chamber</div><h3>IRs</h3></div></div>
  <p>Impulse-response libraries of real rooms, halls and historic spaces, in stereo, surround and 3D, to load into Chamber.</p>
  <div class="req">Links to each publisher's own site</div>
  <div class="actions">
    <a class="btn primary sm" href="free-irs.html">See the libraries</a>
    <a class="btn sm" href="apps/chamber.html">Chamber</a>
  </div>
</article>"""


def build_free_irs():
    libs = []
    for l in FREE_IRS:
        libs.append(f"""<div class="card lib">
      <h3>{e(l['name'])}</h3>
      <div class="by">{e(l['by'])}</div>
      <p>{e(l['what'])}</p>
      <dl class="meta"><dt>Formats</dt><dd>{e(l['formats'])}</dd><dt>Good for</dt><dd>{e(l['best'])}</dd><dt>Licence</dt><dd>{e(l['licence'])}</dd></dl>
      <div class="actions"><a class="btn primary sm" href="{e(l['url'])}" target="_blank" rel="noopener">Go to {e(l['name'].split(' (')[0])} &#8599;</a></div>
    </div>""")
    body = f"""<main class="wrap" style="--c:{FREE_IRS_COLOR}">
<div class="crumb"><a href="index.html#apps">&#8592; All apps</a> &nbsp;&middot;&nbsp; <a href="apps/chamber.html">Chamber</a></div>
<div class="card main free-head">
  <div class="head">{icon({"id": "free-irs", "color": FREE_IRS_COLOR, "name": "IRs"}, 'icon lg')}<div><div class="kind">For Chamber</div><h1>IRs</h1>
  <p class="tag">Real rooms, halls and historic spaces, from the people who recorded them.</p></div></div>
</div>

<section class="block">
  <div class="eyebrow">Libraries</div>
  <div class="cols libs">
    {''.join(libs)}<div class="card lib">
      <h3>Impulse Record</h3>
      <div class="actions"><a class="btn primary sm" href="https://impulserecord.onfastspring.com" target="_blank" rel="noopener">Go to Impulse Record &#8599;</a></div>
    </div>
  </div>
</section>

<section class="block">
  <div class="eyebrow">Using them in Chamber</div>
  <div class="cols">
    <div class="card"><h3>Import</h3><ol>
      <li>Download a library from its site and unzip it.</li>
      <li>In Chamber, click Convolution, then Browse... and Import..., and pick the library's folder.</li>
      <li>Chamber copies it into its IR Library, groups the files into rooms and finds any photos.</li>
    </ol></div>
    <div class="card"><h3>Surround and 3D</h3><p>Chamber maps every IR channel to your track's speakers, from mono to 7.1.4. Front, rear and height files of one room become one surround room, and B-format files are decoded to your speakers. If a library names its files its own way, use Build room... to set it up once.</p></div>
    <div class="card"><h3>Licences</h3><p>Each library's licence is set by its publisher. Some ask for credit (for example "University of Huddersfield, CC-BY 4.0"). Read the terms on its site before using it in your work.</p></div>
  </div>
</section>

<p class="fine">These links go to each publisher's own website. Lew's Apps doesn't host, sell or distribute these files and isn't affiliated with these publishers. Library names belong to their owners.</p>
</main>"""
    (OUT / "free-irs.html").write_text(page("IRs for Chamber — Lew's Apps", body,
        desc="Impulse-response libraries of real rooms and spaces, in stereo, surround and 3D, to use with Chamber."))


def build_index():
    cards = "\n".join(app_card(a) + ("\n" + free_irs_card() if a["id"] == "chamber" else "") for a in APPS)
    body = f"""<main class="wrap">
<section id="apps">
  <div class="grid">
{cards}
  </div>
</section>

<section class="block" id="support">
  <div class="eyebrow">Setup / Support</div>
  <h2>Getting set up</h2>
  <div class="cols">
    <div class="card"><h3>Install</h3><ol><li>Download the installer for your app.</li><li>Open the .pkg and follow the steps.</li><li>For plug-ins, restart Pro Tools and find them in the insert menu.</li></ol></div>
    <div class="card"><h3>Requirements</h3><p>All apps and plug-ins run on macOS 13 Ventura or later, on Apple silicon or Intel Macs. Plug-ins are AAX for Pro Tools.</p></div>
    <div class="card"><h3>Need help?</h3><p>Each app has its own support page — use the Support button on its page. Or email <a href="mailto:{CONTACT}">{CONTACT}</a> with your macOS version, the app version and what happened.</p></div>
  </div>
</section>

<section class="block" id="privacy">
  <div class="eyebrow">Privacy</div>
  <h2>Privacy</h2>
  <div class="cols">
    <div class="card"><p>Lew's Apps don't collect personal data, use analytics or show ads. Apps that use the network talk only to your own computers and devices. This website doesn't use cookies or tracking.</p></div>
  </div>
</section>

<section class="block" id="disclaimer">
  <div class="eyebrow">Disclaimer</div>
  <h2>Beta software</h2>
  <div class="cols">
    <div class="card"><p>All apps and plug-ins are heavily tested but are still in beta. They are provided as is, and no guarantees or warranties are expressed or implied.</p></div>
  </div>
</section>
</main>
<script>
document.querySelectorAll('.pill button').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('.pill button').forEach(x => x.classList.toggle('on', x === b));
  const f = b.dataset.f;
  document.querySelectorAll('.app').forEach(c => c.style.display = (f === 'all' || c.dataset.kind === f) ? '' : 'none');
}}));
</script>"""
    (OUT / "index.html").write_text(page("Lew's Apps — Pro Tools plug-ins and Mac apps from Parabolic", body, mid='<div class="bar-title">Tools for post production</div>'))


def build_app(a):
    feats = "".join(f"<li>{e(f)}</li>" for f in a["features"])
    others = "".join(
        f'<a class="chip" style="--c:{o["color"]}" href="{o["id"]}.html">{icon(o, up="../")}{e(o["name"])}</a>'
        for o in APPS if o["id"] != a["id"])
    sh = shot(a, "../")
    wide = ""
    if sh:
        import struct
        with open(ROOT / "assets" / "shots" / f"{a['id']}.png", "rb") as fh:
            w, h = struct.unpack(">II", fh.read(24)[16:24])
        wide = " wide" if w / h > 2.2 else ""
    shot_html = f'<figure class="card shot{wide}"><a href="{sh}"><img src="{sh}" alt="{e(a["name"])} screenshot"></a></figure>' if sh else ""
    body = f"""<main class="wrap" style="--c:{a['color']}">
<div class="crumb"><a href="../index.html#apps">← All apps</a></div>
<div class="detail">
  <div class="card main">
    <div class="head">{icon(a, 'icon lg', '../')}<div><div class="kind">{e(a['kind'])}</div><h1>{e(a['name'])}</h1><p class="tag">{e(a['tagline'])}</p></div></div>
    <p class="summary">{e(a['summary'])}</p>
    <div class="actions">
      {download_buttons(a, 'btn primary')}
      <a class="btn" href="{e(a['support'])}">Support</a>{'<a class="btn" href="../free-irs.html">IRs</a>' if a['id'] == 'chamber' else ''}
    </div>
  </div>
  <div class="card side">
    <h3>Features</h3>
    <ul class="feat">{feats}</ul>
    <h3>Details</h3>
    <dl class="meta"><dt>Version</dt><dd>{e(a['version'])}</dd><dt>Requires</dt><dd>macOS 13 Ventura or later</dd><dt>Runs on</dt><dd>Apple silicon or Intel</dd><dt>Type</dt><dd>{e(a['kind'])}</dd></dl>
  </div>
</div>
{shot_html}
<section class="others"><div class="eyebrow" style="margin-bottom:12px">More apps</div><div class="row">{others}</div></section>
</main>"""
    (OUT / "apps" / f"{a['id']}.html").write_text(
        page(f"{a['name']} — Lew's Apps", body, depth=1, desc=f"{a['name']}: {a['summary']}"))


def build_support():
    """Each support/<id>.html body fragment becomes docs/<id>-support.html."""
    for f in sorted((ROOT / "support").glob("*.html")):
        a = next((x for x in APPS if x["id"] == f.stem), None)
        name = a["name"] if a else f.stem.title()
        body = '<main class="wrap support-wrap" style="--c:#9b6dff">\n<div class="crumb"><a href="apps/' + f.stem + '.html">← ' + e(name) + '</a></div>\n' + f.read_text().replace("{up}", "") + "\n</main>"
        (OUT / f"{f.stem}-support.html").write_text(page(f"{name} Support — Lew's Apps", body, desc=f"Support for {name}: setup, troubleshooting and contact."))


if __name__ == "__main__":
    (OUT / "apps").mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    import shutil
    for f in (ROOT / "assets").iterdir():
        if f.is_dir():
            shutil.copytree(f, OUT / "assets" / f.name, dirs_exist_ok=True)
        else:
            shutil.copy(f, OUT / "assets" / f.name)
    (OUT / "CNAME").write_text("lewsapps.com\n")
    build_index()
    for a in APPS:
        build_app(a)
    build_support()
    build_free_irs()
    print("built", len(APPS), "app pages into", OUT)
