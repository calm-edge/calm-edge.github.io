"""Renders every video (and its Pinterest pin) that is new or changed. Unchanged ones are kept from the cache.
  python marketing/render_all.py <media-dir> [--jobs 3]
A video is re-rendered when its spec, the player, the renderer, the voice settings or the app screenshots change."""
import argparse, hashlib, json, pathlib, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).parent
SPECS = sorted((ROOT / "content" / "videos").glob("*.json"))
ENGINE = [ROOT / "video" / f for f in ("player.html", "chart.js", "render.py", "tts.py", "pin.py", "still.py", "still.html")]
SHOTS = sorted(p for p in (ROOT / "shots").rglob("*") if p.is_file())  # files only (shots/presenter/ is a folder)


def digest(spec):
    h = hashlib.sha256()
    for f in [spec, *ENGINE, *SHOTS]:
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()[:16]


def outputs(spec, media):
    """Files a spec must produce: reels -> mp4 + pin; carousels -> slides + pin; long lessons -> mp4 + thumbnail + pin."""
    d = json.loads(spec.read_text()); vid = spec.stem; kind = d.get("kind", "reel")
    if kind == "carousel":
        return kind, [media / f"{vid}_{i + 1}.jpg" for i in range(len(d["slides"]))] + [media / f"{vid}_pin.jpg", media / f"{vid}_story.jpg"]
    files = [media / f"{vid}.mp4", media / f"{vid}_pin.jpg"]
    return kind, files + ([media / f"{vid}_thumb.jpg"] if kind == "long" else [])


def one(spec, media):
    vid = spec.stem
    want = digest(spec)
    stamp = media / f"{vid}.hash"
    kind, files = outputs(spec, media)
    if stamp.exists() and stamp.read_text() == want and all(f.exists() for f in files) and (media / f"{vid}.json").exists():
        return vid, "cached", None
    py = sys.executable; shots = str(ROOT / "shots")
    steps = []
    if kind in ("reel", "long"):
        steps.append([py, str(ROOT / "video" / "render.py"), str(spec), str(media), "--shots", shots])
    if kind in ("carousel", "long"):
        steps.append([py, str(ROOT / "video" / "still.py"), str(spec), str(media)])
    if kind in ("reel", "long"):
        steps.append([py, str(ROOT / "video" / "pin.py"), str(spec), str(media), "--shots", shots])
    logs, failed = "", False
    for cmd in steps:
        r = subprocess.run(cmd, capture_output=True, text=True)
        logs += r.stdout + r.stderr
        failed |= bool(r.returncode)
    if kind == "carousel" and not failed:  # still.py prints the metadata line; keep it like render.py does
        line = [l for l in logs.splitlines() if l.startswith("{")][-1]
        (media / f"{vid}.json").write_text(json.dumps({**json.loads(line), "seconds": 0, "engines": []}, indent=2))
    if failed:  # never publish media that failed its checks; it's retried next run
        for f in media.glob(f"{vid}*"):
            f.unlink()
        return vid, "failed", logs[-1500:]
    stamp.write_text(want)
    return vid, "rendered", None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("media"); ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    media = pathlib.Path(a.media); media.mkdir(parents=True, exist_ok=True)
    keep = {s.stem for s in SPECS}
    for f in media.iterdir():  # drop media of videos that no longer exist
        if f.is_file() and not any(f.name.startswith(k) for k in keep) and f.name != "failed.json":
            f.unlink()
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda s: one(s, media), SPECS))
    failed = [r for r in results if r[1] == "failed"]
    for vid, status, err in results:
        print(f"{vid}: {status}")
        if err:
            print(err)
    index = {v: {**json.loads((media / f"{v}.json").read_text()), "status": s} for v, s, _ in results if s != "failed"}
    (media / "index.json").write_text(json.dumps(index, indent=1))
    (media / "failed.json").write_text(json.dumps([{"id": v, "error": e} for v, _, e in failed], indent=1))
    print(f"{len(failed)} failed: they'll be retried on the next run")


if __name__ == "__main__":
    main()
