"""Renders one vertical video (1080x1920, 30 fps, H.264 + AAC) from a spec JSON.

  python render.py spec.json out_dir --shots <dir with app screenshots> [--voice warm|calm] [--engine kokoro|edge|silence]

Each scene lasts as long as its narration (+ a short pause). Frames are drawn by player.html as a pure
function of time and captured one by one, so the result is identical on every run.
Fails if any text leaves the frame or overlaps the caption area."""
import argparse, json, os, pathlib, shutil, subprocess, sys, tempfile, wave
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import tts

HERE = pathlib.Path(__file__).parent
FONTS = HERE.parents[1] / "site" / "static" / "fonts"
FPS, LEAD, TAIL = 30, 0.12, 0.38

CHECK = """() => {
  const bad = [], cap = document.querySelector('.caption .box'), cr = cap && cap.offsetParent ? cap.getBoundingClientRect() : null;
  const W = document.body.clientWidth, H = document.body.clientHeight, land = W > H;
  const L = 60, R = land ? W - 60 : W - 120, T = land ? 15 : 200, B = land ? H - 30 : H - 420;
  document.querySelectorAll('.layer').forEach(l => {
    if (l.style.display === 'none' || +l.style.opacity < 0.98) return;
    l.querySelectorAll('.big, .mid, .label, .statv, .bubble, .cta, .kicker, .rows .r > div, .rows .hd > div, .tag, .chip, .opt, .ovl, .stamp').forEach(e => {
      const r = e.getBoundingClientRect();
      if (+getComputedStyle(e).opacity < 0.05) return;  // not shown yet (e.g. a stamp before it lands)
      if (r.left < L || r.right > R || r.top < T || r.bottom > B) bad.push('outside safe area: ' + e.textContent.trim().slice(0, 40));
      if (e.scrollWidth > e.clientWidth + 1) bad.push('text overflow: ' + e.textContent.trim().slice(0, 40));
      if (cr && r.bottom > cr.top + 2 && r.top < cr.bottom && r.right > cr.left && r.left < cr.right) bad.push('under captions: ' + e.textContent.trim().slice(0, 40));
    });
    l.querySelectorAll('.shot').forEach(e => { const r = e.getBoundingClientRect();
      if (cr && r.bottom > cr.top + 2 && r.top < cr.bottom) bad.push('screenshot under captions'); });
  });
  if (cr && (cr.left < L || cr.right > R)) bad.push('captions too wide');
  (window.__problems || []).forEach(p => bad.push(p)); window.__problems = [];
  document.querySelectorAll('.layer').forEach(l => { if (l.style.display === 'none' || +l.style.opacity < 0.98) return;
    l.querySelectorAll('svg.chart text').forEach(e => { const r = e.getBoundingClientRect();
      if (cr && r.width && r.bottom > cr.top + 2 && r.top < cr.bottom && r.right > cr.left && r.left < cr.right) bad.push('chart under captions'); }); });
  // Nothing may overlap the demo-data tag.
  const tg = document.querySelector('.tag');
  if (tg) { const t = tg.getBoundingClientRect();
    document.querySelectorAll('.layer').forEach(l => { if (l.style.display === 'none' || +l.style.opacity < 0.5) return;
      l.querySelectorAll('.mid, .big, .kicker, .shot, .label, .bubble').forEach(e => { const r = e.getBoundingClientRect();
        if (r.bottom > t.top && r.top < t.bottom && r.right > t.left && r.left < t.right) bad.push('overlaps tag: ' + e.textContent.trim().slice(0, 30)); }); }); }
  return bad;
}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("out")
    ap.add_argument("--shots", required=True); ap.add_argument("--voice", default=None)
    ap.add_argument("--engine", default=None); ap.add_argument("--speed", type=float, default=None)
    ap.add_argument("--suffix", default="")
    a = ap.parse_args()
    spec = json.loads(pathlib.Path(a.spec).read_text())
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    vid = spec["id"] + a.suffix; voice = a.voice or os.environ.get("VIDEO_VOICE") or spec.get("voice", "andrew_up"); speed = a.speed or spec.get("speed")

    work = pathlib.Path(tempfile.mkdtemp(prefix=f"vid-{vid}-"))
    shutil.copy(HERE / "player.html", work / "player.html")
    shutil.copy(HERE / "chart.js", work / "chart.js")
    shutil.copytree(FONTS, work / "fonts")
    shutil.copytree(a.shots, work / "shots")

    # 1. Voice, one line per scene; scene length follows the voice.
    marks = json.loads((pathlib.Path(a.shots) / "marks.json").read_text())
    engines = set()
    for i, s in enumerate(spec["scenes"]):
        if s.get("type") == "shot":
            s["img"] = f"shots/{s['img']}.png"
            for k in ("ring", "focus"):  # named highlight areas measured on the real app
                if isinstance(s.get(k), str):
                    s[k] = marks[s[k]]
        if s.get("say"):
            w = work / f"line{i}.wav"
            engines.add(tts.speak(s["say"], w, voice, speed, a.engine))
            s["speech"] = tts.duration(w)
            s["duration"] = round(LEAD + s["speech"] + TAIL + s.get("hold", 0), 3)
        else:
            s["duration"] = s.get("duration", 1.6)
        s["lead"] = LEAD
    total = sum(s["duration"] for s in spec["scenes"])

    # 2. Audio track: each line placed at the start of its scene (+ lead), silence elsewhere.
    track = work / "voice.wav"
    with wave.open(str(track), "wb") as W:
        W.setnchannels(1); W.setsampwidth(2); W.setframerate(tts.RATE)
        for i, s in enumerate(spec["scenes"]):
            n = int(round(s["duration"] * tts.RATE)); data = b""
            if s.get("say"):
                with wave.open(str(work / f"line{i}.wav")) as r:
                    data = b"\0\0" * int(LEAD * tts.RATE) + r.readframes(r.getnframes())
            data = data[: n * 2]; W.writeframes(data + b"\0\0" * (n - len(data) // 2))

    # 2b. Sound effects: a tick each second of a countdown, a soft "pop" on a reveal (synthesised, no files needed).
    import array, math
    fx = [(sum(x["duration"] for x in spec["scenes"][:i]) + s.get("sfx_at", 0) * s["duration"], s["sfx"]) for i, s in enumerate(spec["scenes"]) if s.get("sfx")]
    if fx:
        with wave.open(str(track)) as r:
            pcm = array.array("h", r.readframes(r.getnframes()))
        def tone(at, freq, dur, vol, decay):
            start = int(at * tts.RATE)
            for k in range(int(dur * tts.RATE)):
                if start + k >= len(pcm):
                    break
                v = vol * math.exp(-k / (decay * tts.RATE)) * math.sin(2 * math.pi * freq * k / tts.RATE)
                pcm[start + k] = max(-32768, min(32767, pcm[start + k] + int(v * 32767)))
        for at, kind in fx:
            if kind == "countdown":
                for sec in range(3):
                    tone(at + sec, 1320, 0.09, 0.22, 0.03)
            elif kind == "reveal":
                tone(at, 660, 0.25, 0.20, 0.08); tone(at + 0.06, 990, 0.25, 0.16, 0.08)
            elif kind == "stamp":  # a low thud with a click on top, when a stamp slams onto the screen
                tone(at, 110, 0.35, 0.35, 0.09); tone(at, 2200, 0.03, 0.10, 0.01)
            elif kind == "riser":  # rising sweep while the camera zooms out or the chart waits
                start, dur = int(at * tts.RATE), 1.4
                phase = 0.0
                for k in range(int(dur * tts.RATE)):
                    if start + k >= len(pcm):
                        break
                    x = k / (dur * tts.RATE); phase += 2 * math.pi * (260 + 700 * x * x) / tts.RATE
                    v = 0.13 * math.sin(math.pi * x) * math.sin(phase)
                    pcm[start + k] = max(-32768, min(32767, pcm[start + k] + int(v * 32767)))
        with wave.open(str(track), "wb") as W:
            W.setnchannels(1); W.setsampwidth(2); W.setframerate(tts.RATE); W.writeframes(pcm.tobytes())

    # 3. Frames -> ffmpeg.
    frames = int(round(total * FPS))
    mp4 = out / f"{vid}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-i", str(track), "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-af", "highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2,equalizer=f=3000:t=q:w=1.2:g=3,loudnorm=I=-14:TP=-1:LRA=7", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                           "-movflags", "+faststart", "-shortest", str(mp4)], stdin=subprocess.PIPE)
    problems = set()
    with sync_playwright() as p:
        exe = os.environ.get("CHROME_PATH") or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
        b = p.chromium.launch(executable_path=exe if os.path.exists(exe) else None, args=["--allow-file-access-from-files"])
        land = spec.get("format") == "landscape"
        pg = b.new_page(viewport={"width": 1920, "height": 1080} if land else {"width": 1080, "height": 1920})
        pg.goto((work / "player.html").as_uri())
        pg.evaluate("() => Promise.all(['400', '600', '700'].map((w) => document.fonts.load(w + ' 30px Inter')))")  # load every weight before measuring text
        pg.evaluate("spec => window.load(spec)", spec)
        for f in range(frames):
            t = f / FPS
            pg.evaluate("t => window.render(t)", t)
            if f % 10 == 0:
                problems.update(pg.evaluate(CHECK))
            ff.stdin.write(pg.screenshot(type="jpeg", quality=94))
            if f == int(min(1.4, spec["scenes"][0]["duration"] - 0.1) * FPS):
                pg.screenshot(path=str(out / f"{vid}_cover.jpg"), type="jpeg", quality=92)
        b.close()
    ff.stdin.close(); ff.wait()
    shutil.rmtree(work, ignore_errors=True)
    if len(engines - {"silence"}) > 1:
        problems.add("mixed voices: " + ", ".join(sorted(engines)))
    import datetime
    chapters, t0 = [], 0.0
    for s in spec["scenes"]:  # YouTube chapters: m:ss at the start of each scene that opens a chapter
        if s.get("chapter"):
            chapters.append({"t": round(t0, 2), "title": s["chapter"]})
        t0 += s["duration"]
    meta = {"chapters": chapters, "kind": spec.get("kind", "reel"), "id": vid, "rendered_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z", "seconds": round(total, 2), "voice": voice, "engines": sorted(engines), "problems": sorted(problems)}
    (out / f"{vid}.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))
    if ff.returncode or problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
