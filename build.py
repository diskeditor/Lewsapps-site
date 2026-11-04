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
TRANSMITTER_GLYPH = f'<svg viewBox="0 0 32 32" {S}><circle cx="16" cy="18" r="3" fill="#111"/><path d="M10 12a8.5 8.5 0 0 0 0 12M22 12a8.5 8.5 0 0 1 0 12M6 8a14 14 0 0 0 0 20M26 8a14 14 0 0 1 0 20"/></svg>'

e = html.escape


def icon(app, cls="icon", up=""):
    if (ROOT / "assets" / "icons" / f"{app['id']}.png").exists():
        return f'<img class="{cls} pic" style="--c:{app["color"]}" src="{up}assets/icons/{app["id"]}.png" alt="">'
    return f'<div class="{cls}" style="--c:{app["color"]}" aria-hidden="true">{GLYPHS.get(app["id"], e(app["name"][0]))}</div>'


def page(title, body, depth=0, desc="Pro Tools plug-ins and Mac apps for post production, from Parabolic."):
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
  <nav class="top">
    <a href="{up}index.html#apps">Apps</a>
    <a href="{up}index.html#support">Support</a>
    <a class="hide-sm" href="{up}index.html#privacy">Privacy</a>
  </nav>
</div></header>
{body}
<footer class="site"><div class="wrap">
  <span class="foot-p"><img class="parabolic" src="{up}assets/parabolic-logo.png" alt="Parabolic" width="600" height="146"> © {YEAR} Parabolic · New York</span>
  <nav><a href="{up}index.html#support">Support</a><a href="{up}index.html#privacy">Privacy</a><a href="mailto:{CONTACT}">Contact</a></nav>
</div></footer>
</body>
</html>
"""


def shot(a, up=""):
    return f"{up}assets/shots/{a['id']}.png" if (ROOT / "assets" / "shots" / f"{a['id']}.png").exists() else None


def app_card(a):
    sh = shot(a)
    thumb = f'<a class="thumb" href="apps/{a["id"]}.html"><img src="{sh}" alt="{e(a["name"])} screenshot" loading="lazy"></a>' if sh else ""
    return f"""<article class="card app" style="--c:{a['color']}" data-kind="{'plugin' if 'plug-in' in a['kind'].lower() else 'app'}">
  <div class="head">{icon(a)}<div><div class="kind">{e(a['kind'])}</div><h3>{e(a['name'])}</h3></div></div>
  {thumb}
  <p>{e(a['summary'])}</p>
  <div class="req">{REQ}</div>
  <div class="actions">
    <a class="btn primary sm" href="{e(a['download'])}">{e(a['download_label'])} <span class="ver">v{e(a['version'])}</span></a>
    <a class="btn sm" href="apps/{a['id']}.html">More info</a>
  </div>
</article>"""


def build_index():
    cards = "\n".join(app_card(a) for a in APPS)
    body = f"""<main class="wrap">
<section class="hero">
  <div class="eyebrow">Tools for post production</div>
</section>

<div class="tx-visit"><a class="btn" href="https://transmitter.info">Visit transmitter.info</a></div>

<section id="apps">
  <div class="toolbar"><div class="pill" role="tablist">
    <button class="on" data-f="all">All</button><button data-f="plugin">Pro Tools plug-ins</button><button data-f="app">Mac apps</button>
  </div></div>
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
    <div class="card"><p>DRAFT — Lewis to confirm: Lew's Apps don't collect personal data, use analytics or show ads. Apps that use the network talk only to your own computers and devices. This website doesn't use cookies or tracking.</p></div>
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
    (OUT / "index.html").write_text(page("Lew's Apps — Pro Tools plug-ins and Mac apps from Parabolic", body))


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
      <a class="btn primary" href="{e(a['download'])}">{e(a['download_label'])} <span class="ver">v{e(a['version'])}</span></a>
      <a class="btn" href="{e(a['support'])}">Support</a>
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
    print("built", len(APPS), "app pages into", OUT)
