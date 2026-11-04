"""Finds today's best posts by other creators to comment on (by hand): recent, popular, on our topics.
Writes marketing/engage/targets.json; the morning routine drafts a comment for each and puts them in Notion.

Sources (each optional, skipped if its credentials are missing or it fails):
- YouTube: search (API key YT_API_KEY), last 3 days, most viewed, English, comments enabled
- Instagram: top posts of a few hashtags (Graph API, IG_USER_ID + META_TOKEN)
- Reddit: newest questions in trading subreddits about journaling, rules, psychology, risk
"""
import datetime, json, os, pathlib, re, urllib.parse, urllib.request

OUT = pathlib.Path(__file__).parent / "targets.json"
NOW = datetime.datetime.now(datetime.timezone.utc)
YT_QUERIES = ["trading journal", "trading psychology", "day trading mistakes", "risk management trading", "futures day trading",
              "profit factor trading", "trading discipline", "trading with ChatGPT"]
IG_TAGS = ["tradingjournal", "tradingpsychology", "daytrader", "futurestrading", "riskmanagement"]
SUBS = ["Daytrading", "FuturesTrading", "algotrading", "Trading"]
SUB_WORDS = re.compile(r"journal|discipline|rules?\b|psycholog|revenge|fomo|risk|position siz|drawdown|win rate|expectancy|track|review|stats|edge", re.I)
UA = {"User-Agent": "CalmEdgeEngage/1.0 (by u/calmedge)"}


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def youtube():
    key = os.environ.get("YT_API_KEY")
    if not key:
        return [], "YT_API_KEY not set"
    after = (NOW - datetime.timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for q in YT_QUERIES:
        p = urllib.parse.urlencode({"part": "id", "q": q, "type": "video", "order": "viewCount", "publishedAfter": after,
                                    "relevanceLanguage": "en", "maxResults": 8, "key": key})
        ids += [i["id"]["videoId"] for i in get(f"https://www.googleapis.com/youtube/v3/search?{p}").get("items", [])]
    ids = list(dict.fromkeys(ids))[:50]
    if not ids:
        return [], None
    p = urllib.parse.urlencode({"part": "snippet,statistics", "id": ",".join(ids), "key": key})
    out, seen = [], set()
    for v in get(f"https://www.googleapis.com/youtube/v3/videos?{p}").get("items", []):
        s, st = v["snippet"], v.get("statistics", {})
        if s.get("liveBroadcastContent", "none") != "none" or re.search(r"\blive\b|stream", s["title"], re.I):
            continue  # live streams: comments get lost in the chat
        if "commentCount" not in st or s["channelId"] in seen or s.get("defaultAudioLanguage", "en")[:2] not in ("en", ""):
            continue
        seen.add(s["channelId"])
        out.append({"platform": "YouTube", "url": f"https://www.youtube.com/watch?v={v['id']}", "title": s["title"], "author": s["channelTitle"],
                    "views": int(st.get("viewCount", 0)), "comments": int(st.get("commentCount", 0)), "published": s["publishedAt"],
                    "text": s.get("description", "")[:600]})
    out.sort(key=lambda x: x["views"], reverse=True)
    return out[:6], None


def instagram():
    ig, tok = os.environ.get("IG_USER_ID"), os.environ.get("META_TOKEN")
    if not (ig and tok):
        return [], "IG_USER_ID / META_TOKEN not set"
    out, errs = [], []
    for tag in IG_TAGS:
        try:
            hid = get(f"https://graph.facebook.com/v21.0/ig_hashtag_search?user_id={ig}&q={tag}&access_token={tok}")["data"][0]["id"]
            media = get(f"https://graph.facebook.com/v21.0/{hid}/top_media?user_id={ig}&fields=permalink,caption,like_count,comments_count,timestamp"
                        f"&limit=10&access_token={tok}").get("data", [])
            for m in media:
                ts = datetime.datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00"))
                if NOW - ts > datetime.timedelta(days=4):
                    continue
                out.append({"platform": "Instagram", "url": m["permalink"], "title": (m.get("caption") or "")[:90].replace("\n", " "),
                            "author": "", "views": int(m.get("like_count") or 0), "comments": int(m.get("comments_count") or 0),
                            "published": m["timestamp"], "text": (m.get("caption") or "")[:600], "tag": tag})
        except Exception as e:  # hashtag search may need extra Meta access: skip quietly
            errs.append(f"{tag}: {str(e)[:120]}")
    out = list({o["url"]: o for o in out}.values())
    out.sort(key=lambda x: x["views"], reverse=True)
    return out[:6], ("; ".join(errs) if errs and not out else None)


def reddit():
    out, errs = [], []
    for sub in SUBS:
        try:
            for c in get(f"https://www.reddit.com/r/{sub}/new.json?limit=50").get("data", {}).get("children", []):
                d = c["data"]
                age = NOW - datetime.datetime.fromtimestamp(d["created_utc"], datetime.timezone.utc)
                text = f"{d['title']} {d.get('selftext', '')}"
                if age > datetime.timedelta(hours=36) or d.get("stickied") or not SUB_WORDS.search(text):
                    continue
                out.append({"platform": "Reddit", "url": "https://www.reddit.com" + d["permalink"], "title": d["title"], "author": f"r/{sub}",
                            "views": int(d.get("score", 0)), "comments": int(d.get("num_comments", 0)),
                            "published": datetime.datetime.fromtimestamp(d["created_utc"], datetime.timezone.utc).isoformat(),
                            "text": d.get("selftext", "")[:600]})
        except Exception as e:
            errs.append(f"{sub}: {str(e)[:120]}")
    # questions with some traction but not yet buried in answers
    out.sort(key=lambda x: (x["comments"] < 40, x["views"]), reverse=True)
    return out[:6], ("; ".join(errs) if errs and not out else None)


def main():
    result = {"generated_at": NOW.isoformat(timespec="minutes"), "targets": [], "notes": {}}
    # Reddit is not read automatically: its Responsible Builder Policy requires approved API access for any
    # automated reading. Reddit threads come from the daily routine's web search and are answered by hand.
    # Instagram hashtag search needs Meta's "Instagram Public Content Access" app review (refused with error #10
    # without it), so Instagram targets come from the "Creator da seguire" list in Notion instead.
    result["notes"]["instagram"] = "non usato: la ricerca hashtag richiede l'approvazione Meta (Instagram Public Content Access)"
    for name, fn in (("youtube", youtube),):
        try:
            items, note = fn()
        except Exception as e:
            items, note = [], str(e)[:200]
        result["targets"] += items
        if note:
            result["notes"][name] = note
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(json.dumps({"count": len(result["targets"]), "by": {p: sum(t["platform"] == p for t in result["targets"]) for p in ("YouTube", "Instagram", "Reddit")},
                      "notes": result["notes"]}, indent=1))


if __name__ == "__main__":
    main()
