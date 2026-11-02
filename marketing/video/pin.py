"""Pinterest pin (1000x1500) for a video spec: the hook as headline, one app visual, the brand.
  python pin.py spec.json out_dir --shots <dir>"""
import argparse, json, os, pathlib, shutil, sys, tempfile, html
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
FONTS = HERE.parents[1] / "site" / "static" / "fonts"
LOGO = '<svg width="64" height="64" viewBox="0 0 1024 1024"><circle cx="512" cy="512" r="470" fill="#16212D" stroke="#2A3A4C" stroke-width="24"/><path d="M236 640 C 330 640, 360 560, 430 575 S 520 650, 590 540 S 700 420, 790 380" fill="none" stroke="#5FD3A0" stroke-width="64" stroke-linecap="round"/></svg>'


def rows_html(s):
    s = json.loads(json.dumps(s))
    two = len(s["head"]) == 3 and s["head"][1] == "" and all(r["cells"][1] == "" for r in s["rows"])
    if two:
        s["head"].pop(1); [r["cells"].pop(1) for r in s["rows"]]
    out = "".join(f'<div class="r {"hl" if r.get("hl") else ""} {"good" if r.get("good") else ""}">' +
                  "".join(f'<div class="{("neg" if str(c)[:1] in "−-" else "pos" if str(c)[:1] == "+" else "") if j == len(r["cells"]) - 1 else ""}">{html.escape(str(c))}</div>'
                          for j, c in enumerate(r["cells"])) + "</div>" for r in s["rows"])
    hd = "" if all(h == "" for h in s["head"]) else f'<div class="hd">{"".join(f"<div>{html.escape(h)}</div>" for h in s["head"])}</div>'
    return f'<div class="rows {"two" if two else ""}">{hd}{out}</div>'


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("out"); ap.add_argument("--shots", required=True)
    a = ap.parse_args()
    spec = json.loads(pathlib.Path(a.spec).read_text())
    hook = next((s for s in spec["scenes"] if s["type"] == "hook"), None)
    charts = [s for s in spec["scenes"] if s["type"] == "chart"]
    if hook is None:  # chart lessons: the first headline is the pin's title
        hook = {"text": charts[0]["headline"], "kicker": "Trading, explained"}
    visual = next((s for t in ("rows", "stat", "shot") for s in spec["scenes"] if s["type"] == t), None)
    chart_state = None
    if charts:
        sc = next((s for s in charts if s.get("pin")), charts[-1])
        n = len(spec["charts"][sc["chart"]]["candles"])
        chart_state = {"chart": sc["chart"], "state": {"bars": (sc.get("reveal") or [n, n])[1], "show": {k: 1 for k in sc.get("show", []) + sc.get("add", [])},
                       "levels": [{**l, "alpha": 1} for l in sc.get("levels", [])], "zones": [{**z, "alpha": 1} for z in sc.get("zones", [])],
                       "marks": [{**m, "alpha": 1} for m in sc.get("marks", [])]}}
        vis = '<svg id="pc" width="860" height="560" style="overflow:visible"></svg>'
    elif visual and visual["type"] == "rows":
        vis = f'<div class="vt">{html.escape(visual.get("title", ""))}</div>{rows_html(visual)}'
    elif visual and visual["type"] == "stat":
        v = visual["value"]; d = visual.get("decimals", 0)
        num = f'{"−" if v < 0 else ""}{visual.get("prefix", "")}{abs(v):,.{d}f}{visual.get("suffix", "")}'
        vis = f'<div class="vt">{html.escape(visual["label"])}</div><div class="stat" style="color:var(--{visual.get("color", "mint")})">{num}</div>'
    else:
        vis = f'<div class="shot"><img src="shots/{visual["img"]}.png"></div>' if visual else ""
    brand = (("Calm Edge", "Trading, explained · one concept a day") if "_edu_" in spec["id"] else
             ("Prop Firm Manager", "Desktop app · every prop account, one screen") if "_pfm_" in spec["id"] else
             ("Trading Journal AI", "Desktop app · one-click AI review"))
    page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face {{ font-family: Inter; font-weight: 400; src: url(fonts/Inter-Regular.woff) }}
@font-face {{ font-family: Inter; font-weight: 700; src: url(fonts/Inter-Bold.woff) }}
:root {{ --mint:#5FD3A0; --coral:#F2848A; --gold:#F2C14E; --blue:#6CA8FF; --line:#2A3A4C; --muted:#93A3B5 }}
* {{ margin:0; padding:0; box-sizing:border-box }}
body {{ width:1000px; height:1500px; background:#0F1720; color:#E8EDF3; font-family:Inter; position:relative; overflow:hidden }}
.g {{ position:absolute; border-radius:50%; filter:blur(120px); opacity:.32 }}
.safe {{ position:absolute; inset:80px 70px; display:flex; flex-direction:column; gap:44px }}
.k {{ font-size:28px; letter-spacing:5px; text-transform:uppercase; font-weight:700; color:var(--mint) }}
h1 {{ font-size:84px; line-height:1.05; letter-spacing:-2px; font-weight:700; text-wrap:balance }}
.vt {{ font-size:40px; font-weight:700; color:var(--muted) }}
.rows {{ background:#16212D; border:3px solid var(--line); border-radius:28px; overflow:hidden }}
.rows .hd, .rows .r {{ display:grid; grid-template-columns:1.6fr 1fr 1.2fr; align-items:center; padding:0 30px }}
.rows .hd {{ background:#1B2836; color:var(--muted); font-size:28px; font-weight:700; height:76px }}
.rows.two .hd, .rows.two .r {{ grid-template-columns:3fr 1.2fr }}
.rows .r:first-child {{ border-top:0 }}
.rows .r {{ height:100px; font-size:40px; border-top:2px solid var(--line) }}
.rows .r > :not(:first-child), .rows .hd > :not(:first-child) {{ text-align:right }}
.rows .r.hl {{ background:rgba(242,132,138,.10); box-shadow:inset 8px 0 0 var(--coral) }}
.rows .r.good.hl {{ background:rgba(95,211,160,.10); box-shadow:inset 8px 0 0 var(--mint) }}
.pos {{ color:var(--mint); font-weight:700 }} .neg {{ color:var(--coral); font-weight:700 }}
.stat {{ font-size:200px; font-weight:700; letter-spacing:-6px; line-height:1 }}
.shot {{ border-radius:24px; overflow:hidden; border:3px solid var(--line) }} .shot img {{ width:100%; display:block }}
.brand {{ margin-top:auto; display:flex; align-items:center; gap:22px }}
.brand b {{ font-size:44px }} .brand span {{ display:block; font-size:28px; color:var(--muted) }}
.tag {{ font-size:22px; color:var(--muted) }}
</style></head><body>
<div class="g" style="width:900px;height:900px;left:-350px;top:-400px;background:#5FD3A0"></div>
<div class="g" style="width:800px;height:800px;right:-350px;bottom:-350px;background:#6CA8FF"></div>
<div class="safe"><div class="k">{html.escape(hook.get("kicker", "Trading journal"))}</div><h1>{html.escape(hook["text"])}</h1>{vis}
<div class="brand">{LOGO}<div><b>{brand[0]}</b><span>{brand[1]}</span></div></div>
{f'<div class="tag">{html.escape(spec["tag"])}</div>' if spec.get("tag") else ""}</div>
<script src="chart.js"></script></body></html>"""
    work = pathlib.Path(tempfile.mkdtemp())
    shutil.copytree(FONTS, work / "fonts"); shutil.copytree(a.shots, work / "shots"); shutil.copy(HERE / "chart.js", work / "chart.js")
    (work / "pin.html").write_text(page, encoding="utf-8")
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        exe = os.environ.get("CHROME_PATH") or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
        b = p.chromium.launch(executable_path=exe if os.path.exists(exe) else None)
        pg = b.new_page(viewport={"width": 1000, "height": 1500}); pg.goto((work / "pin.html").as_uri()); pg.evaluate("() => Promise.all(['400', '600', '700'].map((w) => document.fonts.load(w + ' 30px Inter')))")
        chart_bad = []
        if chart_state:
            chart_bad = pg.evaluate("""([ch, st]) => { const svg = document.getElementById('pc'); const r = svg.getBoundingClientRect();
              const slack = document.querySelector('.brand').getBoundingClientRect().top - r.bottom - 50;
              const h = Math.min(780, 560 + Math.max(0, slack)); svg.setAttribute('height', h);
              ch._extra = []; ch._marked = st.marks.some(m => !m.panel); st.levels.forEach(l => ch._extra.push(l.price)); st.zones.forEach(z => ch._extra.push(z.lo, z.hi));
              const g = document.createElementNS('http://www.w3.org/2000/svg', 'g'); g.setAttribute('transform', `translate(${-r.left} ${-r.top})`); svg.appendChild(g);
              return drawChart(g, ch, {x: r.left + 18, y: r.top, w: 824, h: h}, st); }""", [spec["charts"][chart_state["chart"]], chart_state["state"]])
        bad = pg.evaluate("""() => { const s = document.querySelector('.safe').getBoundingClientRect(), out = [];
          document.querySelectorAll('.safe > *').forEach(e => { const r = e.getBoundingClientRect(); if (r.bottom > s.bottom + 1 || r.right > s.right + 1) out.push(e.className || e.tagName); });
          return out; }""")
        pg.screenshot(path=str(out / f"{spec['id']}_pin.jpg"), type="jpeg", quality=90)
        b.close()
    shutil.rmtree(work, ignore_errors=True)
    bad += chart_bad
    print(spec["id"], "pin", "overflow: " + ",".join(bad) if bad else "ok")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
