"""Publishes today's approved content: reels (Instagram Reels, Facebook, YouTube Shorts), carousels (Instagram carousel,
Facebook multi-photo post) and long lessons (YouTube with chapters and thumbnail, Facebook video).

  python publish.py --schedule schedule.json --media-base https://<site>/media --log published.json [--dry-run] [--only instagram,youtube]

schedule.json: [{"id": "v003_emotions", "date": "2026-10-24", "time": "17:30", "channels": ["instagram", "facebook", "youtube", "pinterest"]}]
Each item is published once per channel: published.json remembers what went out (id, channel, url, time).
Credentials come from environment variables; a channel without credentials is skipped and reported.
Only standard library: runs anywhere."""
import argparse, datetime, json, os, pathlib, sys, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
TZ = ZoneInfo(os.environ.get("PUBLISH_TZ", "Europe/Rome"))
GRAPH = "https://graph.facebook.com/v21.0"


def http(method, url, data=None, headers=None, raw=None, timeout=120):
    body = raw
    hdrs = dict(headers or {})
    if data is not None and raw is None:
        if hdrs.get("Content-Type") == "application/json":
            body = json.dumps(data).encode()
        else:
            body = urllib.parse.urlencode(data).encode()
            hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            text = r.read().decode() or "{}"
            return r.status, (json.loads(text) if text.strip().startswith(("{", "[")) else text), dict(r.headers)
    except urllib.error.HTTPError as e:
        text = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {url.split('?')[0]} -> {e.code}: {text[:400]}")


def env(*names):
    vals = [os.environ.get(n, "").strip() for n in names]
    return vals if all(vals) else None


# ---------------- channels ----------------

def instagram(item, spec, video_url, cover_url):
    creds = env("IG_USER_ID", "META_TOKEN")
    if not creds:
        return None, "missing IG_USER_ID / META_TOKEN"
    ig, token = creds
    _, r, _ = http("POST", f"{GRAPH}/{ig}/media", {"media_type": "REELS", "video_url": video_url, "caption": spec["post"]["instagram"],
                                                    "share_to_feed": "true", "cover_url": cover_url, "access_token": token})
    cid = r["id"]
    for _ in range(60):  # Meta downloads and processes the video
        _, st, _ = http("GET", f"{GRAPH}/{cid}?fields=status_code,status&access_token={token}")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram processing error: {st.get('status')}")
        time.sleep(10)
    _, pub, _ = http("POST", f"{GRAPH}/{ig}/media_publish", {"creation_id": cid, "access_token": token})
    _, info, _ = http("GET", f"{GRAPH}/{pub['id']}?fields=permalink&access_token={token}")
    return info.get("permalink", pub["id"]), None


def facebook(item, spec, video_url, cover_url):
    creds = env("FB_PAGE_ID", "META_PAGE_TOKEN")
    if not creds:
        return None, "missing FB_PAGE_ID / META_PAGE_TOKEN"
    page, token = creds
    _, r, _ = http("POST", f"{GRAPH}/{page}/videos", {"file_url": video_url, "description": spec["post"]["facebook"], "access_token": token}, timeout=600)
    return f"https://www.facebook.com/{page}/videos/{r['id']}", None


def ig_carousel(item, spec, image_urls):
    creds = env("IG_USER_ID", "META_TOKEN")
    if not creds:
        return None, "missing IG_USER_ID / META_TOKEN"
    ig, token = creds
    children = []
    for u in image_urls:  # one container per slide, then the carousel container
        _, r, _ = http("POST", f"{GRAPH}/{ig}/media", {"image_url": u, "is_carousel_item": "true", "access_token": token})
        children.append(r["id"])
    _, r, _ = http("POST", f"{GRAPH}/{ig}/media", {"media_type": "CAROUSEL", "children": ",".join(children), "caption": spec["post"]["instagram"], "access_token": token})
    cid = r["id"]
    for _ in range(30):
        _, st, _ = http("GET", f"{GRAPH}/{cid}?fields=status_code,status&access_token={token}")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram carousel error: {st.get('status')}")
        time.sleep(5)
    _, pub, _ = http("POST", f"{GRAPH}/{ig}/media_publish", {"creation_id": cid, "access_token": token})
    _, info, _ = http("GET", f"{GRAPH}/{pub['id']}?fields=permalink&access_token={token}")
    return info.get("permalink", pub["id"]), None


def fb_photos(item, spec, image_urls):
    creds = env("FB_PAGE_ID", "META_PAGE_TOKEN")
    if not creds:
        return None, "missing FB_PAGE_ID / META_PAGE_TOKEN"
    page, token = creds
    ids = []
    for u in image_urls:  # unpublished photos, then one post with all of them
        _, r, _ = http("POST", f"{GRAPH}/{page}/photos", {"url": u, "published": "false", "access_token": token})
        ids.append(r["id"])
    data = {"message": spec["post"]["facebook"], "access_token": token}
    data.update({f"attached_media[{k}]": json.dumps({"media_fbid": i}) for k, i in enumerate(ids)})
    _, r, _ = http("POST", f"{GRAPH}/{page}/feed", data)
    return f"https://www.facebook.com/{r['id']}", None


def chapters_text(chapters):
    fmt = lambda t: f"{int(t // 60)}:{int(t % 60):02d}"
    return "\n".join(f"{fmt(c['t'])} {c['title']}" for c in chapters)


def youtube(item, spec, video_path, cover_url):
    creds = env("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")
    if not creds:
        return None, "missing YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN"
    cid, secret, refresh = creds
    _, tok, _ = http("POST", "https://oauth2.googleapis.com/token", {"client_id": cid, "client_secret": secret, "refresh_token": refresh, "grant_type": "refresh_token"})
    auth = {"Authorization": f"Bearer {tok['access_token']}"}
    y = spec["post"]["youtube"]
    long = spec.get("kind") == "long"
    desc = y["description"]
    if "{chapters}" in desc:  # real timestamps of this render, from the site's media index
        base = cover_url.rsplit("/", 1)[0]
        _, idx, _ = http("GET", f"{base}/index.json")
        ch = (idx.get(item["id"]) or {}).get("chapters") or []
        desc = desc.replace("{chapters}", ("Chapters\n" + chapters_text(ch)) if len(ch) >= 3 else "")
    meta = {"snippet": {"title": y["title"][:100], "description": desc[:4900], "categoryId": "27",
                        "tags": y.get("tags") or ["trading journal", "day trading", "trading psychology", "risk management", "AI"]},
            "status": {"privacyStatus": os.environ.get("YT_PRIVACY", "public"), "selfDeclaredMadeForKids": False}}
    data = pathlib.Path(video_path).read_bytes()
    _, _, h = http("POST", "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                   raw=json.dumps(meta).encode(), headers={**auth, "Content-Type": "application/json; charset=UTF-8",
                                                           "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(len(data))})
    loc = h.get("Location") or h.get("location")
    _, v, _ = http("PUT", loc, raw=data, headers={**auth, "Content-Type": "video/mp4"}, timeout=900)
    if not long:
        return f"https://youtube.com/shorts/{v['id']}", None
    try:  # custom thumbnails need a verified channel; the video stays up either way
        thumb = urllib.request.urlopen(cover_url.replace("_cover.jpg", "_thumb.jpg"), timeout=60).read()
        http("POST", f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={v['id']}", raw=thumb, headers={**auth, "Content-Type": "image/jpeg"})
    except Exception as e:
        print("thumbnail not set:", str(e)[:200])
    return f"https://www.youtube.com/watch?v={v['id']}", None


def pinterest(item, spec, video_url, cover_url):
    creds = env("PINTEREST_TOKEN", "PINTEREST_BOARD_ID")
    if not creds:
        return None, "missing PINTEREST_TOKEN / PINTEREST_BOARD_ID"
    token, board = creds
    p = spec["post"]["pinterest"]
    pin_img = cover_url.replace("_cover.jpg", "_pin.jpg")
    _, r, _ = http("POST", "https://api.pinterest.com/v5/pins", {"board_id": board, "title": p["title"][:100], "description": p["description"][:500],
                                                                  "link": p["link"], "media_source": {"source_type": "image_url", "url": pin_img}},
                   headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    return f"https://www.pinterest.com/pin/{r['id']}/", None


CHANNELS = {"instagram": instagram, "facebook": facebook, "youtube": youtube, "pinterest": pinterest}
def ig_story(media_url, video):
    """Instagram story pointing people to the new post: the reel itself, or the carousel cover at 9:16."""
    creds = env("IG_USER_ID", "META_TOKEN")
    if not creds:
        return None, "missing IG_USER_ID / META_TOKEN"
    ig, token = creds
    _, r, _ = http("POST", f"{GRAPH}/{ig}/media", {"media_type": "STORIES", ("video_url" if video else "image_url"): media_url, "access_token": token})
    cid = r["id"]
    for _ in range(60):
        _, st, _ = http("GET", f"{GRAPH}/{cid}?fields=status_code,status&access_token={token}")
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram story error: {st.get('status')}")
        time.sleep(5)
    _, pub, _ = http("POST", f"{GRAPH}/{ig}/media_publish", {"creation_id": cid, "access_token": token})
    return f"story:{pub['id']}", None


CAROUSEL_CHANNELS = {"instagram": ig_carousel, "facebook": fb_photos}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schedule", required=True); ap.add_argument("--log", required=True)
    ap.add_argument("--media-base", required=True); ap.add_argument("--media-dir", required=True)
    ap.add_argument("--dry-run", action="store_true"); ap.add_argument("--only", default="")
    ap.add_argument("--now", default=None, help="ISO datetime, for tests")
    a = ap.parse_args()
    now = datetime.datetime.fromisoformat(a.now).replace(tzinfo=TZ) if a.now else datetime.datetime.now(TZ)
    schedule = json.loads(pathlib.Path(a.schedule).read_text())
    logp = pathlib.Path(a.log)
    log = json.loads(logp.read_text()) if logp.exists() else []
    done = {(e["id"], e["channel"]) for e in log if e.get("url")}
    only = set(filter(None, a.only.split(",")))
    report = []
    for item in schedule:
        when = datetime.datetime.fromisoformat(f"{item['date']}T{item.get('time', '17:30')}").replace(tzinfo=TZ)
        if when > now or (now - when).days > 2:  # not yet, or too old to post late
            continue
        spec = json.loads((ROOT / "content" / "videos" / f"{item['id']}.json").read_text())
        video_url = f"{a.media_base.rstrip('/')}/{item['id']}.mp4"
        cover_url = f"{a.media_base.rstrip('/')}/{item['id']}_cover.jpg"
        carousel = spec.get("kind") == "carousel"
        images = [f"{a.media_base.rstrip('/')}/{item['id']}_{k + 1}.jpg" for k in range(len(spec.get("slides", [])))]
        for ch in item.get("channels", []):
            table = CAROUSEL_CHANNELS if carousel else CHANNELS
            if ch not in table or (only and ch not in only) or (item["id"], ch) in done:
                continue
            if a.dry_run:
                report.append({"id": item["id"], "channel": ch, "dry_run": True, **({"images": images} if carousel else {})}); continue
            try:
                if carousel:
                    url, skipped = table[ch](item, spec, images)
                else:
                    src = str(pathlib.Path(a.media_dir) / f"{item['id']}.mp4") if ch == "youtube" else video_url
                    url, skipped = table[ch](item, spec, src, cover_url)
                entry = {"id": item["id"], "channel": ch, "time": now.isoformat(timespec="minutes")}
                entry.update({"url": url} if url else {"skipped": skipped})
            except Exception as e:  # keep going with the other channels
                entry = {"id": item["id"], "channel": ch, "time": now.isoformat(timespec="minutes"), "error": str(e)[:500]}
            log.append(entry); report.append(entry)
            logp.write_text(json.dumps(log, indent=1))
        # after the Instagram post, the same content goes to the story, so profile visitors and followers see it twice
        posted_ig = any(e["id"] == item["id"] and e["channel"] == "instagram" and e.get("url") for e in log)
        if posted_ig and (item["id"], "instagram_story") not in done and not a.dry_run and (not only or "instagram" in only):
            try:
                media = f"{a.media_base.rstrip('/')}/{item['id']}_story.jpg" if carousel else video_url
                url, skipped = ig_story(media, not carousel)
                entry = {"id": item["id"], "channel": "instagram_story", "time": now.isoformat(timespec="minutes")}
                entry.update({"url": url} if url else {"skipped": skipped})
            except Exception as e:
                entry = {"id": item["id"], "channel": "instagram_story", "time": now.isoformat(timespec="minutes"), "error": str(e)[:500]}
            log.append(entry); report.append(entry)
            logp.write_text(json.dumps(log, indent=1))
    print(json.dumps(report, indent=1))
    if any("error" in r for r in report):
        sys.exit(1)


if __name__ == "__main__":
    main()
