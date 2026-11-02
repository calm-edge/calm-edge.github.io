"""Still images from a spec: carousel slides (1080x1350 JPEG, Instagram/Facebook), the Pinterest pin
(1000x1500, the cover slide) and YouTube thumbnails (1280x720). Fails if any text overflows.
  python still.py spec.json out_dir"""
import json, os, pathlib, shutil, sys, tempfile
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).parent
FONTS = HERE.parents[1] / "site" / "static" / "fonts"


def main():
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())
    out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    work = pathlib.Path(tempfile.mkdtemp())
    for f in ("still.html", "chart.js"):
        shutil.copy(HERE / f, work / f)
    shutil.copytree(FONTS, work / "fonts")
    jobs = []  # (slide spec, slide index, W, H, file)
    if spec.get("slides"):
        n = len(spec["slides"])
        jobs += [(spec, i, 1080, 1350, f"{spec['id']}_{i + 1}.jpg") for i in range(n)]
        jobs.append((spec, 0, 1000, 1500, f"{spec['id']}_pin.jpg"))
        jobs.append((spec, 0, 1080, 1920, f"{spec['id']}_story.jpg"))  # Instagram story announcing the post
    if spec.get("kind") == "stories":  # story frames (1080x1920): highlight covers and highlight content
        jobs = [(spec, i, 1080, 1920, f"{spec['id']}_{i + 1}.jpg") for i in range(len(spec["slides"]))]
    if spec.get("thumb"):
        jobs.append(({**spec, "slides": [spec["thumb"]]}, 0, 1280, 720, f"{spec['id']}_thumb.jpg"))
    problems = []
    with sync_playwright() as p:
        exe = os.environ.get("CHROME_PATH") or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
        b = p.chromium.launch(executable_path=exe if os.path.exists(exe) else None, args=["--allow-file-access-from-files"])
        for sp, i, W, H, name in jobs:
            pg = b.new_page(viewport={"width": W, "height": H})
            pg.goto((work / "still.html").as_uri()); pg.evaluate("() => Promise.all(['400', '600', '700'].map((w) => document.fonts.load(w + ' 30px Inter')))")  # load every weight before measuring text
            probs = pg.evaluate("([s, i, W, H]) => renderSlide(s, i, W, H)", [sp, i, W, H])
            problems += [f"{name}: {x}" for x in probs]
            pg.screenshot(path=str(out / name), type="jpeg", quality=92)
            pg.close()
        b.close()
    shutil.rmtree(work, ignore_errors=True)
    meta = {"id": spec["id"], "kind": spec.get("kind", "reel"), "slides": len(spec.get("slides", [])), "problems": problems}
    print(json.dumps(meta))
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main()
