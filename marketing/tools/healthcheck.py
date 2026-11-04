"""End-to-end health check of the Calm Edge engine, with real requests (nothing is mocked or posted).

Checks the live site, the old-address bridge, the Gumroad pages, the media every scheduled post needs,
the Pinterest feed, every recent post on Instagram / Facebook / YouTube through their APIs, the
permissions of the Meta token, and the sources of marketing/engage. Prints one line per check
(OK / FAIL / WARN) and writes the same to the GitHub job summary. Exit code 1 if any check FAILs.
"""
import datetime as dt, json, os, pathlib, sys, urllib.error, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = "https://calm-edge.github.io"
OLD = "https://amirkallas2cs-gif.github.io"
GRAPH = "https://graph.facebook.com/v21.0"
ROME = ZoneInfo("Europe/Rome")
NOW = dt.datetime.now(ROME)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) CalmEdgeHealth/1.0"}
rows = []


def rec(status, name, detail=""):
    rows.append((status, name, str(detail)[:400]))
    print(f"{status:4} {name}  {str(detail)[:400]}", flush=True)


def fetch(url, method="GET", data=None, headers=None, timeout=40):
    req = urllib.request.Request(url, data=data, method=method, headers={**UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers or {})
    except Exception as e:
        return 0, str(e).encode(), {}


def jget(url, headers=None):
    s, b, _ = fetch(url, headers=headers)
    try:
        return s, json.loads(b)
    except Exception:
        return s, {"raw": b[:300].decode("utf-8", "replace")}


# ---------- site ----------
def site():
    for path, must in [("/", "Calm Edge"), ("/trading-journal-ai/", "Trading Journal"), ("/prop-firm-manager/", "Prop Firm Manager"), ("/learn/", ""),
                       ("/prop/rules.json", ""), ("/media/index.json", ""), ("/pins.xml", "<rss")]:
        s, b, h = fetch(SITE + path)
        ok = s == 200 and (must.encode() in b if must else True)
        rec("OK" if ok else "FAIL", f"sito {path}", f"HTTP {s}, {len(b)} byte")
    s, b, _ = fetch(SITE + "/prop/rules.json")
    try:
        r = json.loads(b); rec("OK", "rules.json valido", f"{len(r.get('firms', r)) if isinstance(r, dict) else len(r)} voci")
    except Exception as e:
        rec("FAIL", "rules.json valido", e)
    # old address: must send people (and app 1.0.1) to the new site. Old sub-pages are answered by the
    # bridge's 404 page, which forwards to the same path on the new site (GitHub Pages can't send a 301).
    for path, what in [("/", b"calm-edge.github.io"), ("/prop-firm-manager/", b'location.replace("https://calm-edge.github.io" + location.pathname'), ("/prop/rules.json", None)]:
        s, b, _ = fetch(OLD + path)
        ok = s in (200, 404) and what in b if what else s == 200 and b.strip().startswith((b"{", b"["))
        rec("OK" if ok else "FAIL", f"vecchio indirizzo {path}", f"HTTP {s}" + ("" if ok else f" {b[:120]!r}"))


def gumroad():
    for name, url in [("Trading Journal AI", "https://kallas8.gumroad.com/l/axltbh"),
                      ("Prop Firm Manager", "https://kallas8.gumroad.com/l/prop-firm-manager"),
                      ("Bundle", "https://kallas8.gumroad.com/l/znfvjd")]:
        s, b, _ = fetch(url)
        rec("OK" if s == 200 else "FAIL", f"Gumroad {name}", f"HTTP {s}, {len(b)} byte")


# ---------- media for every scheduled post ----------
def media():
    sched = json.loads((ROOT / "marketing/schedule.json").read_text())
    idx = jget(SITE + "/media/index.json")[1]
    missing = []
    for it in sched:
        when = dt.datetime.fromisoformat(f"{it['date']}T{it.get('time', '17:30')}").replace(tzinfo=ROME)
        if when < NOW - dt.timedelta(hours=2):
            continue
        i = it["id"]
        if "_car_" in i:
            spec = json.loads((ROOT / f"marketing/content/videos/{i}.json").read_text())
            n = len(spec.get("slides", []))
            need = [f"{i}_{k}.jpg" for k in range(1, n + 1)] + [f"{i}_story.jpg", f"{i}_pin.jpg"]
        else:
            need = [f"{i}.mp4", f"{i}_cover.jpg", f"{i}_pin.jpg"]
        for f in need:
            s, b, h = fetch(f"{SITE}/media/{f}", method="HEAD")
            if s != 200:
                missing.append(f"{f} HTTP {s}")
        ent = idx.get(i) if isinstance(idx, dict) else None
        if ent and ent.get("problems"):
            missing.append(f"{i} problems={ent['problems']}")
        rec("OK" if not missing else "FAIL", f"media {it['date']} {it.get('time')} {i}", "; ".join(missing) or f"{len(need)} file presenti")
        missing = []


def pins():
    s, b, _ = fetch(SITE + "/pins.xml")
    try:
        root = ET.fromstring(b)
        items = root.findall(".//item")
        imgs = [e.attrib.get("url") for e in root.iter() if e.tag.endswith("content") or e.tag == "enclosure"]
        bad = []
        for u in [u for u in imgs if u][:5]:
            st, _, _ = fetch(u, method="HEAD")
            if st != 200:
                bad.append(f"{u} HTTP {st}")
        rec("OK" if items and not bad else "FAIL", "feed Pinterest pins.xml", f"{len(items)} pin; ultimi titoli: " +
            " | ".join((x.findtext('title') or '')[:40] for x in items[:3]) + (f"; immagini rotte: {bad}" if bad else ""))
    except Exception as e:
        rec("FAIL", "feed Pinterest pins.xml", e)


# ---------- social APIs ----------
def recent_posts(days=8):
    pub = json.loads((ROOT / "marketing/published.json").read_text())
    lim = NOW - dt.timedelta(days=days)
    return [e for e in pub if "url" in e and dt.datetime.fromisoformat(e["time"]) >= lim]


def meta():
    ig, tok, page, ptok = (os.environ.get(k, "") for k in ("IG_USER_ID", "META_TOKEN", "FB_PAGE_ID", "META_PAGE_TOKEN"))
    if not (ig and tok and page and ptok):
        rec("FAIL", "credenziali Meta", "mancano IG_USER_ID / META_TOKEN / FB_PAGE_ID / META_PAGE_TOKEN"); return
    s, dbg = jget(f"{GRAPH}/debug_token?input_token={tok}&access_token={tok}")
    d = dbg.get("data", {})
    granted = sorted(d.get("scopes", []))
    rec("OK" if granted else "FAIL", "token Meta: permessi concessi", f"tipo {d.get('type')}: " + (", ".join(granted) or str(dbg)))
    for need, why in [("instagram_content_publish", "pubblicare su Instagram"), ("instagram_manage_insights", "leggere visualizzazioni e tempo di visione"),
                      ("pages_manage_posts", "pubblicare su Facebook"), ("pages_read_engagement", "leggere la pagina Facebook")]:
        if granted:
            rec("OK" if need in granted else "WARN", f"permesso {need}", why + ("" if need in granted else ": NON concesso"))
    if d:
        when = "mai" if not d.get("expires_at") else dt.datetime.fromtimestamp(d["expires_at"], ROME).strftime("%d/%m/%Y")
        dae = d.get("data_access_expires_at")
        dae = dt.datetime.fromtimestamp(dae, ROME).strftime("%d/%m/%Y") if dae else "n/d"
        soon = d.get("expires_at") and dt.datetime.fromtimestamp(d["expires_at"], ROME) - NOW < dt.timedelta(days=14)
        rec("WARN" if soon or not d.get("is_valid") else "OK", "token Meta: validità", f"valido={d.get('is_valid')}, scade={when}, accesso dati fino al {dae}")
    # every recent Instagram post must exist on the account
    s, med = jget(f"{GRAPH}/{ig}/media?fields=id,permalink,timestamp,media_product_type&limit=50&access_token={tok}")
    codes = {m["permalink"].rstrip("/").split("/")[-1] for m in med.get("data", [])}
    rec("OK" if s == 200 else "FAIL", "Instagram: lettura post dell'account", f"{len(codes)} post" if s == 200 else med)
    for e in recent_posts():
        if e["channel"] == "instagram":
            code = e["url"].rstrip("/").split("/")[-1]
            rec("OK" if code in codes else "FAIL", f"Instagram {e['id']}", e["url"])
        elif e["channel"] == "facebook":
            obj = e["url"].rstrip("/").split("/")[-1]
            s, r = jget(f"{GRAPH}/{obj}?fields=id,created_time&access_token={ptok}")
            rec("OK" if s == 200 and r.get("id") else "FAIL", f"Facebook {e['id']}", e["url"] if s == 200 else r)
    # stories: list what's live now
    s, st = jget(f"{GRAPH}/{ig}/stories?fields=id,timestamp&access_token={tok}")
    rec("OK" if s == 200 else "WARN", "Instagram storie attive ora", f"{len(st.get('data', []))} storie" if s == 200 else st)
    # insights (needed to learn what keeps people watching)
    first = (med.get("data") or [{}])[0].get("id")
    if first:
        s, r = jget(f"{GRAPH}/{first}/insights?metric=reach,saved&access_token={tok}")
        rec("OK" if s == 200 else "WARN", "Instagram insights (copertura, salvataggi)", "funziona" if s == 200 else r.get("error", {}).get("message", r))


def youtube():
    cid, sec, ref = (os.environ.get(k, "") for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"))
    if not (cid and sec and ref):
        rec("FAIL", "credenziali YouTube", "mancano YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN"); return
    s, b, _ = fetch("https://oauth2.googleapis.com/token", "POST",
                    urllib.parse.urlencode({"client_id": cid, "client_secret": sec, "refresh_token": ref, "grant_type": "refresh_token"}).encode(),
                    {"Content-Type": "application/x-www-form-urlencoded"})
    tok = json.loads(b).get("access_token") if s == 200 else None
    rec("OK" if tok else "FAIL", "YouTube: rinnovo accesso", "ok" if tok else b[:300])
    if not tok:
        return
    auth = {"Authorization": f"Bearer {tok}"}
    s, ch = jget("https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true", auth)
    c = (ch.get("items") or [None])[0]
    if c:
        rec("OK", "YouTube: canale (OAuth)", f"{c['snippet']['title']}, iscritti {c['statistics'].get('subscriberCount')}, video {c['statistics'].get('videoCount')}")
    else:
        rec("WARN", "YouTube: canale (OAuth)", f"HTTP {s}: {str(ch.get('error', ch))[:250]}")
    ids = {}
    for e in recent_posts():
        if e["channel"] == "youtube":
            ids[e["url"].rstrip("/").split("/")[-1].split("v=")[-1]] = e["id"]
    key = os.environ.get("YT_API_KEY", "")
    if ids and key:  # public view: is each video online and public for everyone?
        s, r = jget("https://www.googleapis.com/youtube/v3/videos?part=status,statistics,snippet&id=" + ",".join(ids) + f"&key={key}")
        if s != 200:
            rec("FAIL", "YouTube: lettura video pubblici", str(r)[:300]); return
        found = {v["id"]: v for v in r.get("items", [])}
        for vid, name in ids.items():
            v = found.get(vid)
            if not v:
                rec("FAIL", f"YouTube {name}", f"{vid} non esiste o non è pubblico"); continue
            st = v["status"]
            ok = st.get("privacyStatus") == "public" and st.get("uploadStatus") == "processed"
            rec("OK" if ok else "FAIL", f"YouTube {name}", f"{st.get('privacyStatus')}/{st.get('uploadStatus')}, canale {v['snippet'].get('channelTitle')}, views {v.get('statistics', {}).get('viewCount')}")


def engage_sources():
    key = os.environ.get("YT_API_KEY", "")
    if key:
        s, r = jget(f"https://www.googleapis.com/youtube/v3/search?part=snippet&q=day+trading&type=video&maxResults=1&key={key}")
        rec("OK" if s == 200 else "FAIL", "YouTube API key (engage)", "funziona" if s == 200 else r)
    else:
        rec("FAIL", "YouTube API key (engage)", "YT_API_KEY mancante")


for fn in (site, gumroad, media, pins, meta, youtube, engage_sources):
    try:
        fn()
    except Exception as e:
        rec("FAIL", f"controllo {fn.__name__} interrotto", repr(e))

fails = [r for r in rows if r[0] == "FAIL"]
warns = [r for r in rows if r[0] == "WARN"]
summary = f"{len(rows) - len(fails) - len(warns)} OK, {len(warns)} WARN, {len(fails)} FAIL"
print("\nRISULTATO:", summary)
if os.environ.get("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
        f.write(f"## Controllo motore Calm Edge: {summary}\n\n| Esito | Controllo | Dettaglio |\n|---|---|---|\n")
        for s, n, d in rows:
            f.write(f"| {s} | {n} | {d.replace('|', '/')} |\n")
(ROOT / "marketing/health.json").write_text(json.dumps({"checked_at": NOW.isoformat(timespec="minutes"), "summary": summary,
    "checks": [{"status": s, "check": n, "detail": d} for s, n, d in rows]}, indent=1, ensure_ascii=False))
for s, n, d in fails + warns:
    print(f"::{'error' if s == 'FAIL' else 'warning'} title={n}::{d}")
print(f"::notice title=health::{summary}")
sys.exit(1 if fails else 0)
