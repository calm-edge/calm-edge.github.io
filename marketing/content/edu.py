"""Educational videos (series "trading, explained"): one concept per video, an animated chart from the first frame,
a follow call at the end. Every number said or shown is computed from the chart itself (see charts.py) and checked
here with assertions, so a chart that doesn't show what the script says fails the build instead of being published."""
from charts import path, closes, ema, rsi, vwap, atr, bollinger, macd, r2, stochastic

HANDLE = "@calmedgeofficial"
EDU_TAG = "Illustrative chart · education, not financial advice"
EDU_TAGS = ["#tradingeducation", "#technicalanalysis", "#daytrading", "#trading", "#learntotrade"]
SITE = "https://calm-edge.github.io"
FOLLOW = {"type": "follow", "text": "Follow for one trading concept a day.", "say": "Save this, and follow for one trading concept a day."}


def post_edu(title, body, tags, pin=None, site_path="/"):
    hashtags = " ".join(dict.fromkeys(tags + EDU_TAGS))
    tail = f"Save this for later and follow {HANDLE} for one trading concept a day."
    note = "Educational example on an illustrative chart. Not financial advice; trading involves risk of loss."
    return {
        "instagram": f"{body}\n\n{tail}\n\n{note}\n\n{hashtags}",
        "tiktok": f"{body} Follow for one trading concept a day. {' '.join(dict.fromkeys(tags + EDU_TAGS[:3]))}",
        "youtube": {"title": f"{title} #shorts", "description": f"{body}\n\nFree guides and calculators: {SITE}{site_path}\n\n{note}\n\n{hashtags} #shorts"},
        "facebook": f"{body}\n\n{tail}\n\nFree guides and calculators: {SITE}{site_path}",
        "pinterest": {"title": pin or title, "description": f"{body} Trading concepts explained simply, one a day.", "link": SITE + site_path},
    }


def export(c, start=0, lines=(), bands=(), panel=None):
    """Chart data for the player: candles and indicator series from `start` (indicators were warmed up on the full series)."""
    sl = lambda xs: r2(xs[start:])
    out = {"candles": c[start:], "lines": [{**l, "values": sl(l["values"])} for l in lines],
           "bands": [{**b, "upper": sl(b["upper"]), "lower": sl(b["lower"])} for b in bands]}
    if panel:
        out["panel"] = {**panel, "lines": [{**l, "values": sl(l["values"])} for l in panel["lines"]]}
    return out


def pick(build, ok, seeds=range(1, 60)):
    """First seed whose chart satisfies the lesson's conditions (deterministic)."""
    for s in seeds:
        r = build(s)
        if ok(r):
            return r
    raise AssertionError("no chart satisfies the lesson")


def words(n):
    """Small integers in words for the voice."""
    w = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
    t = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety"}
    if n < 20:
        return w[n]
    return t[n // 10 * 10] + ("" if n % 10 == 0 else "-" + w[n % 10])


V = []

# ------------------------------------------------------------------ 1. RSI above 70


def _rsi(seed):
    c = path([(0, 100), (10, 99.5), (18, 103.5), (21, 102.8), (29, 107.5), (32, 106.6), (39, 111), (42, 110.2), (49, 114.5), (52, 113.6), (59, 118)],
             seed=seed, noise=0.45, wick=0.4)
    r = rsi(closes(c))
    first = next(i for i, x in enumerate(r) if x is not None and x > 70)
    above = sum(1 for x in r[first:] if x > 70)
    return dict(c=c, r=r, first=first, above=above, n=len(c) - first)


R = pick(_rsi, lambda d: d["first"] >= 20 and d["above"] / d["n"] >= 0.85 and max(x for x in d["r"] if x) < 86)
S = 14
gain = (R["c"][-1]["c"] / R["c"][R["first"]]["c"] - 1) * 100
assert gain > 8
ch = export(R["c"], S, panel={"id": "rsi", "label": "RSI 14", "min": 0, "max": 100, "levels": [{"y": 70, "label": "70", "color": "coral"}, {"y": 30, "label": "30", "color": "mint"}],
                              "lines": [{"id": "rsi", "color": "violet", "values": R["r"]}]})
f = R["first"] - S
V.append({"id": "v201_edu_rsi_70", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "RSI above 70 doesn't mean sell.", "reveal": [10, f], "show": ["rsi"],
     "say": "RSI above seventy doesn't mean sell. Watch this."},
    {"type": "chart", "chart": "a", "headline": "RSI above 70 doesn't mean sell.", "reveal": [f, f + 8], "show": ["rsi"],
     "marks": [{"bar": f, "panel": True, "value": round(R["r"][R["first"]], 1), "dir": "up", "text": "Crosses 70", "color": "coral", "at": 0.15}],
     "say": "RSI compares recent up moves with recent down moves, from zero to one hundred. Above seventy is called overbought."},
    {"type": "chart", "chart": "a", "headline": "RSI above 70 doesn't mean sell.", "reveal": [f + 8, len(ch["candles"])], "show": ["rsi"],
     "marks": [{"bar": f, "dir": "down", "text": "Sell here?", "color": "coral", "at": 0.05},
               {"bar": len(ch["candles"]) - 1, "dir": "down", "text": f"+{gain:.0f}% later", "color": "mint", "at": 0.85}],
     "say": f"But in a strong trend it can stay there. Here RSI stayed above seventy on {words(R['above'])} of the next {words(R['n'])} bars, and price rose another {words(round(gain))} percent."},
    {"type": "rows", "title": "RSI above 70 usually means…", "head": ["", "", ""], "rows": [
        {"cells": ["Strong trend", "", "Strength"], "good": True, "hl": True}, {"cells": ["Sideways range", "", "Stretched"]}],
     "say": "So in a trend, read it as strength. In a sideways range, it can mean price is stretched."},
    FOLLOW],
    "post": post_edu("RSI above 70 doesn't mean sell", f"RSI above 70 is called overbought, but in a strong trend it can stay there for a long time. In this example RSI stayed above 70 on {R['above']} of the next {R['n']} bars while price rose another {gain:.0f}%. Read it as strength in a trend, as stretched in a range.",
                     ["#rsi", "#indicators"], "RSI above 70 doesn't mean sell (explained)")})

# ------------------------------------------------------------------ 2. 20 EMA trend filter


def _ema(seed):
    c = path([(0, 100), (9, 103.5), (13, 101.2), (21, 106), (25, 103.6), (33, 108.4), (37, 106), (45, 110.6), (49, 108.4), (53, 110.8), (57, 108.3), (61, 110.6),
              (65, 108.2), (69, 110.5), (73, 108.6), (76, 110)], seed=seed, noise=0.3, wick=0.3)
    e = ema(closes(c), 20)
    touch = [i for i in (25, 37) if c[i]["l"] <= e[i] + 0.1 and c[i]["c"] > e[i] - 0.05]
    trend_ok = all(c[i]["c"] > e[i] for i in range(19, 46))
    cross = [i for i in range(50, 77) if (c[i]["c"] - e[i]) * (c[i - 1]["c"] - e[i - 1]) < 0]
    return dict(c=c, e=e, touch=touch, ok=trend_ok, cross=cross)


E = pick(_ema, lambda d: d["ok"] and len(d["touch"]) == 2 and len(d["cross"]) >= 5)
S = 15
ch = export(E["c"], S, lines=[{"id": "ema", "label": "20 EMA", "color": "gold", "values": E["e"]}])
n = len(ch["candles"]); t1, t2 = (i - S for i in E["touch"]); rng0 = 50 - S
V.append({"id": "v202_edu_20ema", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "One line that shows you the trend.", "big": True, "reveal": [8, 16], "add": ["ema"], "addAt": 0.2,
     "say": "One line that shows you the trend: the twenty EMA."},
    {"type": "chart", "chart": "a", "headline": "Price above a rising 20 EMA: uptrend.", "reveal": [16, rng0 - 3], "show": ["ema"],
     "marks": [{"bar": t1, "dir": "up", "text": "Pullback", "color": "mint", "at": 0.35}, {"bar": t2, "dir": "up", "text": "Pullback", "color": "mint", "at": 0.7}],
     "say": "It's an average of recent closes that weighs the newest ones more. Above a rising EMA, the trend is up, and pullbacks often find buyers near it."},
    {"type": "chart", "chart": "a", "headline": "Flat EMA: no trend, no edge.", "reveal": [rng0 - 3, n], "show": ["ema"],
     "zones": [{"from": rng0, "to": n - 1, "lo": min(b["l"] for b in ch["candles"][rng0:]), "hi": max(b["h"] for b in ch["candles"][rng0:]), "color": "coral",
                "label": f"Crossed {len(E['cross'])} times", "at": 0.6}],
     "say": f"But it lags. When price goes sideways, the line goes flat, and price crossed it {words(len(E['cross']))} times in {words(77 - 50)} bars."},
    {"type": "rows", "title": "How to read the 20 EMA", "head": ["", "", ""], "rows": [
        {"cells": ["Rising, price above", "", "Uptrend"], "good": True, "hl": True}, {"cells": ["Falling, price below", "", "Downtrend"]},
        {"cells": ["Flat, crossed often", "", "No trend"], "hl": True}],
     "say": "Use it as a trend filter, not as a signal on its own."},
    FOLLOW],
    "post": post_edu("The 20 EMA trend filter in 30 seconds", f"The 20 EMA is an average of recent closes that weighs the newest ones more. Price above a rising EMA: uptrend, and pullbacks often find buyers near it. When it goes flat, it lags: here price crossed it {len(E['cross'])} times in 27 bars. Use it as a filter, not a signal.",
                     ["#ema", "#movingaverage", "#indicators"], "How to use the 20 EMA as a trend filter")})

# ------------------------------------------------------------------ 3. VWAP


def _vwap(seed):
    c = path([(0, 100), (4, 100.6), (12, 98.3), (19, 100.4), (22, 101.2), (26, 100.5), (34, 102.6), (40, 103.2)], seed=seed, noise=0.22, wick=0.22)
    v = vwap(c)
    below = [i for i in range(len(c)) if c[i]["c"] < v[i]]
    reclaim = next((i for i in range(12, 30) if c[i]["c"] > v[i] and c[i - 1]["c"] < v[i - 1]), None)
    test = [i for i in range(reclaim + 4, 32) if c[i]["l"] <= v[i] + 0.05 and c[i]["c"] > v[i]] if reclaim else []
    after = all(c[i]["c"] > v[i] for i in range(reclaim, len(c))) if reclaim else False
    return dict(c=c, v=v, reclaim=reclaim, test=test, after=after, below=below)


W = pick(_vwap, lambda d: d["reclaim"] and d["after"] and len(d["test"]) >= 1 and len(d["below"]) >= 8)
ch = export(W["c"], 0, lines=[{"id": "vwap", "label": "VWAP", "color": "blue", "values": W["v"]}])
n = len(ch["candles"]); rc, ts = W["reclaim"], W["test"][0]
V.append({"id": "v203_edu_vwap", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Why every day trader watches this line.", "big": True, "reveal": [7, rc - 2], "add": ["vwap"], "addAt": 0.1,
     "say": "Why every day trader watches this blue line."},
    {"type": "chart", "chart": "a", "headline": "VWAP: the average price paid today.", "reveal": [rc - 2, rc + 1], "show": ["vwap"],
     "marks": [{"bar": rc, "dir": "up", "text": "Reclaimed", "color": "mint", "at": 0.5}],
     "say": "VWAP is the average price everyone paid today, weighted by volume. Above it, today's average buyer is in profit."},
    {"type": "chart", "chart": "a", "headline": "Reclaim, retest, hold.", "reveal": [rc + 1, n], "show": ["vwap"],
     "marks": [{"bar": ts, "dir": "up", "text": "Retest holds", "color": "mint", "at": 0.35}],
     "say": "Here price reclaims VWAP, comes back to test it, and buyers defend it. Every close after that stays above."},
    {"type": "rows", "title": "Reading VWAP", "head": ["", "", ""], "rows": [
        {"cells": ["Above VWAP", "", "Buyers in control"], "good": True, "hl": True}, {"cells": ["Below VWAP", "", "Sellers in control"]},
        {"cells": ["Chopping around it", "", "No control"], "hl": True}],
     "say": "Above it, buyers have the upper hand. Below it, sellers do. Chopping around it, nobody does."},
    FOLLOW],
    "post": post_edu("VWAP explained in 30 seconds", "VWAP is the average price everyone paid today, weighted by volume. Above it, today's average buyer is in profit; below it, the average seller is. A reclaim followed by a retest that holds is one of the cleanest things to watch intraday.",
                     ["#vwap", "#daytradingtips"], "VWAP explained for day traders")})

# ------------------------------------------------------------------ 4. Support/resistance flip


def _flip(seed):
    wp = [(0, 101), (7, 104.4), (11, 102.2), (16, 104.5), (20, 102.6), (25, 104.4), (28, 103.6), (32, 106.3), (36, 107.6), (41, 105.6), (47, 108.4), (52, 109.6)]
    c = path(wp, seed=seed, noise=0.25, wick=0.25, force={7: {"h": 105.0}, 16: {"h": 104.98}, 25: {"h": 105.0}, 41: {"l": 105.06}})
    brk = next(i for i, b in enumerate(c) if b["c"] > 105)
    hits = [i for i in range(brk) if c[i]["h"] >= 104.95]
    ok = max(b["h"] for b in c[:brk]) <= 105.0 and min(b["l"] for b in c[brk + 2:]) >= 105.0 and brk >= 29
    return dict(c=c, brk=brk, hits=hits, ok=ok)


F = pick(_flip, lambda d: d["ok"] and len(d["hits"]) == 3)
ch = export(F["c"]); n = len(ch["candles"]); b = F["brk"]
V.append({"id": "v204_edu_sr_flip", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Old resistance becomes new support.", "big": True, "reveal": [8, 18],
     "levels": [{"price": 105, "to": b, "label": "Resistance", "color": "coral", "below": True, "at": 0.25}],
     "say": "Old resistance becomes new support. Here's how it looks."},
    {"type": "chart", "chart": "a", "headline": "Three tries. Sellers win each time.", "reveal": [18, b - 1],
     "levels": [{"price": 105, "to": b, "label": "Resistance", "color": "coral", "below": True}],
     "marks": [{"bar": h, "dir": "down", "color": "coral", "at": 0.1 + 0.25 * k} for k, h in enumerate(F["hits"])],
     "say": "Price hits the same level three times, and sellers push it back down every time."},
    {"type": "chart", "chart": "a", "headline": "Break, then retest from above.", "reveal": [b - 1, n],
     "levels": [{"price": 105, "label": "Now support", "color": "mint", "below": True}],
     "marks": [{"bar": b, "dir": "up", "text": "Break", "color": "mint", "at": 0.1}, {"bar": 41, "dir": "up", "text": "Retest", "color": "mint", "at": 0.55}],
     "say": "Then it breaks and closes above. When price comes back, the same level often holds as support, because buyers who missed the breakout are waiting there."},
    FOLLOW],
    "post": post_edu("Old resistance becomes new support", "A level that rejected price three times breaks, and on the retest it holds from above. Buyers who missed the breakout often wait at the old level. Wait for the close above, then watch the retest.",
                     ["#supportandresistance", "#priceaction"], "Support and resistance flip explained")})

# ------------------------------------------------------------------ 5. Failed breakout


def _fail(seed):
    wp = [(0, 102), (6, 104.5), (10, 103.2), (14, 104.5), (18, 103.6), (21, 104.7), (22, 104.45), (27, 102.8), (30, 103.3), (36, 100.8)]
    c = path(wp, seed=seed, noise=0.22, wick=0.22, force={6: {"h": 105.0}, 14: {"h": 104.99}, 22: {"o": 104.75, "h": 105.92, "l": 104.35, "c": 104.45}})
    ok = all(x["c"] < 105 for x in c) and all(x["h"] <= 105.0 for i, x in enumerate(c) if i != 22) and c[23]["c"] < 105
    return dict(c=c, ok=ok)


T = pick(_fail, lambda d: d["ok"])
ch = export(T["c"]); n = len(ch["candles"])
drop = 104.45 - T["c"][-1]["c"]
V.append({"id": "v205_edu_failed_breakout", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "This candle traps buyers every day.", "big": True, "reveal": [6, 21],
     "levels": [{"price": 105, "label": "Resistance", "color": "coral", "at": 0.2}],
     "say": "This candle traps buyers every single day."},
    {"type": "chart", "chart": "a", "headline": "A wick above is not a breakout.", "reveal": [21, 23],
     "levels": [{"price": 105, "label": "Resistance", "color": "coral"}],
     "marks": [{"bar": 22, "dir": "up", "text": "Closes back below", "color": "coral", "at": 0.55}],
     "say": "Price pokes above resistance, buyers jump in, and the candle closes back below the level. That's a failed breakout."},
    {"type": "chart", "chart": "a", "headline": "Trapped buyers become sellers.", "reveal": [23, n],
     "levels": [{"price": 105, "label": "Resistance", "color": "coral"}],
     "say": "Everyone who bought the poke is now losing, and their stops add fuel to the drop."},
    {"type": "rows", "title": "Before you buy a breakout", "head": ["", "", ""], "rows": [
        {"cells": ["Wick above the level", "", "Not yet"], "hl": True}, {"cells": ["Close above the level", "", "Breakout"], "good": True, "hl": True},
        {"cells": ["Close back below", "", "Failed"]}],
     "say": "So wait for a candle to close above the level, not just a wick."},
    FOLLOW],
    "post": post_edu("The candle that traps breakout buyers", "Price pokes above resistance, buyers jump in, and the candle closes back below: a failed breakout. Trapped buyers' stops add fuel to the drop. Wait for a close above the level, not just a wick.",
                     ["#breakout", "#priceaction"], "Failed breakout (bull trap) explained")})

# ------------------------------------------------------------------ 6. Double top


def _dt(seed):
    c = path([(0, 103), (12, 109.6), (19, 106.4), (26, 109.5), (31, 105.6), (34, 106.3), (42, 101.8)], seed=seed, noise=0.28, wick=0.25,
             force={12: {"h": 110.0}, 19: {"l": 106.0}, 26: {"h": 109.92}})
    hi1 = max(x["h"] for x in c[:20]); hi2 = max(x["h"] for x in c[20:30])
    neck = min(x["l"] for x in c[13:26])
    brk = next(i for i in range(27, len(c)) if c[i]["c"] < neck)
    target = round(neck - (hi1 - neck), 2)
    return dict(c=c, hi1=hi1, hi2=hi2, neck=neck, brk=brk, target=target, reached=min(x["l"] for x in c[brk:]) <= target)


D = pick(_dt, lambda d: d["hi1"] == 110.0 and d["hi2"] == 109.92 and d["neck"] == 106.0 and d["reached"])
ch = export(D["c"]); n = len(ch["candles"])
V.append({"id": "v206_edu_double_top", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "The double top, and when it's real.", "big": True, "reveal": [8, 20],
     "say": "The double top, and the moment it actually becomes real."},
    {"type": "chart", "chart": "a", "headline": "Two highs. One neckline.", "reveal": [20, 28],
     "marks": [{"bar": 12, "dir": "down", "text": "Top 1", "color": "coral", "at": 0.05}, {"bar": 26, "dir": "down", "text": "Top 2", "color": "coral", "at": 0.6}],
     "levels": [{"price": 106.0, "label": "Neckline", "color": "gold", "below": True, "at": 0.3}],
     "say": "Two highs at about the same price, with a low between them. That low is the neckline."},
    {"type": "chart", "chart": "a", "headline": "Confirmed only below the neckline.", "reveal": [28, n],
     "levels": [{"price": 106.0, "label": "Neckline", "color": "gold"}, {"price": D["target"], "label": "Classic target", "color": "blue", "below": True, "at": 0.3}],
     "marks": [{"bar": D["brk"], "dir": "down", "text": "Close below", "color": "coral", "at": 0.12}],
     "say": "It only counts when a candle closes below the neckline. The classic target is the pattern's height, measured down from the neckline. In this example price got there, but many double tops don't."},
    FOLLOW],
    "post": post_edu("Double top: when is it real?", "Two highs at about the same price and a low between them, the neckline. The pattern is only confirmed by a close below the neckline; the classic target is the pattern's height measured down from it. Many double tops fail, so wait for the close.",
                     ["#chartpatterns", "#doubletop"], "Double top pattern explained")})

# ------------------------------------------------------------------ 7. ATR stop


def _atr(seed):
    wp = [(0, 100), (8, 101.5), (12, 100.9), (20, 103.2), (25, 104.0), (29, 103.3), (33, 104.6), (44, 107.4)]
    c0 = path(wp, seed=seed, noise=0.3, wick=0.3)
    a = atr(c0)[25]; e = c0[25]["c"]
    c = path(wp, seed=seed, noise=0.3, wick=0.3, force={29: {"l": round(e - 1.0 * a, 2)}})
    a = atr(c)[25]; tight, wide = e - 0.5 * a, e - 1.5 * a
    lows = [x["l"] for x in c[26:]]
    hit_tight = next((i for i in range(26, len(c)) if c[i]["l"] <= tight), None)
    return dict(c=c, a=a, e=e, tight=round(tight, 2), wide=round(wide, 2), hit=hit_tight, ok=min(lows) >= wide + 0.25 * a and hit_tight is not None and c[-1]["c"] > e + 2)


A = pick(_atr, lambda d: d["ok"])
ch = export(A["c"]); n = len(ch["candles"])
V.append({"id": "v207_edu_atr_stop", "tag": EDU_TAG, "site_path": "/tools/position-size-calculator/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Why your stop keeps getting hit.", "big": True, "reveal": [6, 26],
     "levels": [{"price": A["e"], "from": 25, "label": "Entry", "color": "blue", "at": 0.6}],
     "say": "Why your stop keeps getting hit, right before price goes your way."},
    {"type": "chart", "chart": "a", "headline": "A stop inside normal noise.", "reveal": [26, A["hit"] + 6],
     "levels": [{"price": A["e"], "from": 25, "label": "Entry", "color": "blue"}, {"price": A["tight"], "from": 25, "label": "Tight stop", "color": "coral", "below": True, "labelPos": "right"}],
     "marks": [{"bar": A["hit"], "dir": "down", "text": "Stopped out", "color": "coral", "at": 0.45}],
     "say": "This stop sits half an ATR below entry. ATR is the average true range, how far price normally moves in one bar. An ordinary dip takes it out."},
    {"type": "chart", "chart": "a", "headline": "Stop at 1.5 ATR, smaller size.", "reveal": [A["hit"] + 6, n],
     "levels": [{"price": A["e"], "from": 25, "label": "Entry", "color": "blue"}, {"price": A["wide"], "from": 25, "label": "1.5 ATR stop", "color": "mint", "below": True}],
     "say": "At one and a half ATR, the same dip is just noise. Make the stop wider and the position smaller, so the dollar risk stays the same."},
    FOLLOW],
    "post": post_edu("Why your stop keeps getting hit", "ATR, the average true range, is how far price normally moves in one bar. A stop at half an ATR sits inside normal noise; at 1.5 ATR an ordinary dip doesn't reach it. Wider stop, smaller size, same dollar risk.",
                     ["#atr", "#stoploss", "#riskmanagement"], "ATR stop loss explained", "/tools/position-size-calculator/")})

# ------------------------------------------------------------------ 8. Bollinger squeeze


def _bb(seed):
    wp = [(0, 100), (5, 103), (9, 99), (14, 102.5), (19, 100.2), (23, 101.3), (27, 100.9), (31, 101.2), (35, 100.95), (39, 101.15), (42, 101.05), (47, 104.2), (53, 106.6)]
    c = path(wp, seed=seed, noise=0.18, wick=0.18)
    m, u, l = bollinger(closes(c))
    width = [None if x is None else (u[i] - l[i]) for i, x in enumerate(m)]
    lo_i = min(range(19, 43), key=lambda i: width[i])
    end = len(c) - 1
    return dict(c=c, m=m, u=u, l=l, width=width, lo_i=lo_i, ratio=width[end] / width[lo_i], early=width[19] / width[lo_i])


B = pick(_bb, lambda d: d["ratio"] >= 3 and d["early"] >= 2 and 32 <= d["lo_i"] <= 42)
S = 12
ch = export(B["c"], S, lines=[{"id": "mid", "color": "muted", "values": B["m"], "dash": True}], bands=[{"id": "bb", "label": "Bollinger Bands 20, 2", "color": "blue", "upper": B["u"], "lower": B["l"]}])
n = len(ch["candles"]); li = B["lo_i"] - S; ratio = int(B["ratio"])
V.append({"id": "v208_edu_bollinger_squeeze", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "When the bands pinch, get ready.", "big": True, "reveal": [8, 18], "add": ["bb", "mid"], "addAt": 0.15,
     "say": "When these bands pinch together, get ready."},
    {"type": "chart", "chart": "a", "headline": "Low volatility: the squeeze.", "reveal": [18, li + 2], "show": ["bb", "mid"],
     "marks": [{"bar": li, "dir": "down", "text": "Squeeze", "color": "gold", "at": 0.7}],
     "say": "Bollinger Bands sit two standard deviations around a twenty bar average. When price goes quiet, they squeeze together."},
    {"type": "chart", "chart": "a", "headline": "Quiet markets don't stay quiet.", "reveal": [li + 2, n], "show": ["bb", "mid"],
     "marks": [{"bar": n - 1, "dir": "down", "text": f"{ratio}x wider", "color": "mint", "at": 0.85}],
     "say": f"Low volatility tends to be followed by expansion. Here the bands ended up more than {words(ratio)} times wider. But the squeeze tells you a move may come, not which way."},
    FOLLOW],
    "post": post_edu("The Bollinger Band squeeze", f"Bollinger Bands sit two standard deviations around a 20-bar average. When price goes quiet they squeeze together, and low volatility tends to be followed by expansion: here the bands ended up more than {ratio}x wider. The squeeze doesn't tell you the direction.",
                     ["#bollingerbands", "#volatility", "#indicators"], "Bollinger Band squeeze explained")})

# ------------------------------------------------------------------ 9. Risk:reward and win rate


def _rr(seed):
    c = path([(0, 98.6), (8, 99.7), (12, 99.2), (18, 100.0), (22, 99.45), (27, 100.8), (30, 100.5), (36, 102.15)], seed=seed, noise=0.18, wick=0.16)
    hit_t = next((i for i in range(19, len(c)) if c[i]["h"] >= 102.0), None)
    ok = c[18]["c"] == 100.0 and min(x["l"] for x in c[19:]) > 99.0 and hit_t is not None
    return dict(c=c, hit=hit_t, ok=ok)


Q = pick(_rr, lambda d: d["ok"])
ch = export(Q["c"]); n = len(ch["candles"])
be = lambda r: 100 / (1 + r)
assert round(be(2), 1) == 33.3 and round(0.4 * 2 - 0.6 * 1, 2) == 0.2
V.append({"id": "v209_edu_risk_reward", "tag": EDU_TAG, "site_path": "/tools/r-multiple-calculator/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Wrong 60% of the time, still profitable.", "big": True, "reveal": [8, 19],
     "zones": [{"from": 18, "to": n - 1, "lo": 100.0, "hi": 102.0, "color": "mint", "label": "Reward 2R", "at": 0.45},
               {"from": 18, "to": n - 1, "lo": 99.0, "hi": 100.0, "color": "coral", "at": 0.45}],
     "say": "You can be wrong sixty percent of the time and still make money. Here's the math."},
    {"type": "chart", "chart": "a", "headline": "Risk 1 to make 2.", "reveal": [19, n],
     "zones": [{"from": 18, "to": n - 1, "lo": 100.0, "hi": 102.0, "color": "mint", "label": "Reward 2R"}, {"from": 18, "to": n - 1, "lo": 99.0, "hi": 100.0, "color": "coral"}],
     "levels": [{"price": 99.0, "from": 18, "label": "Stop: 1R", "color": "coral", "below": True}],
     "say": "Risk one unit to make two. That's a reward to risk of two to one."},
    {"type": "rows", "title": "Win rate you need to break even", "head": ["Reward : risk", "", "Break-even"], "rows": [
        {"cells": ["1 : 1", "", "50%"]}, {"cells": ["2 : 1", "", "33.3%"], "good": True, "hl": True}, {"cells": ["3 : 1", "", "25%"]}],
     "say": "At two to one you only need to win one trade in three to break even, before costs."},
    {"type": "rows", "title": "Win 40% at 2 : 1", "head": ["", "", ""], "rows": [
        {"cells": ["4 wins × 2R", "", "+8R"]}, {"cells": ["6 losses × 1R", "", "−6R"]}, {"cells": ["Per 10 trades", "", "+2R"], "good": True, "hl": True}],
     "say": "Win four out of ten: plus eight R, minus six R. Plus two R every ten trades."},
    FOLLOW],
    "post": post_edu("Wrong 60% of the time and still profitable", "With a 2:1 reward to risk you only need to win 1 trade in 3 to break even (33.3%, before costs). Win 4 out of 10: +8R − 6R = +2R every ten trades. Your win rate only means something next to your reward to risk.",
                     ["#riskreward", "#riskmanagement", "#tradingpsychology"], "Win rate vs risk reward explained", "/tools/r-multiple-calculator/")})

# ------------------------------------------------------------------ 10. Position size in futures


risk_usd = 50000 * 0.01; stop_pts = 4
mes = risk_usd / (stop_pts * 5); es = int(risk_usd // (stop_pts * 50))
assert mes == 25 and es == 2 and stop_pts * 50 * es <= risk_usd


def _ps(seed):
    c = path([(0, 5812), (8, 5818), (12, 5815), (20, 5821), (24, 5820), (34, 5829)], seed=seed, noise=0.9, wick=0.8)
    ok = c[20]["c"] == 5821 and min(x["l"] for x in c[21:]) > 5817.5
    return dict(c=c, ok=ok)


P = pick(_ps, lambda d: d["ok"])
ch = export(P["c"]); n = len(ch["candles"])
V.append({"id": "v210_edu_position_size", "tag": EDU_TAG, "site_path": "/tools/position-size-calculator/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "How many contracts? Three numbers.", "big": True, "reveal": [8, 21],
     "levels": [{"price": 5821, "from": 20, "label": "Entry", "color": "blue", "at": 0.5}, {"price": 5817, "from": 20, "label": "Stop: 4 points", "color": "coral", "below": True, "at": 0.65}],
     "say": "How many contracts should you trade? You only need three numbers."},
    {"type": "rows", "title": "1. How much you can lose", "head": ["", "", ""], "rows": [
        {"cells": ["Account", "", "$50,000"]}, {"cells": ["Risk per trade", "", "1%"]}, {"cells": ["Max loss", "", "$500"], "good": True, "hl": True}],
     "say": "One: how much you can lose. One percent of fifty thousand dollars is five hundred."},
    {"type": "rows", "title": "2. What one contract risks", "head": ["Contract", "$ per point", "4-point stop"], "rows": [
        {"cells": ["Micro (MES)", "$5", "$20"]}, {"cells": ["E-mini (ES)", "$50", "$200"]}],
     "say": "Two: what one contract loses at your stop. Four points is twenty dollars on the micro, two hundred on the E-mini."},
    {"type": "rows", "title": "3. Divide", "head": ["", "", "Contracts"], "rows": [
        {"cells": ["$500 ÷ $20", "", "25 micros"], "good": True, "hl": True}, {"cells": ["$500 ÷ $200 = 2.5", "", "2 E-minis"]}],
     "say": "Three: divide. Twenty-five micros, or two E-minis. Always round down."},
    FOLLOW],
    "post": post_edu("How many futures contracts should you trade?", "1) Max loss: 1% of $50,000 = $500. 2) Risk per contract: a 4-point stop is $20 on the Micro E-mini S&P ($5/point) and $200 on the E-mini ($50/point). 3) Divide and round down: 25 micros or 2 E-minis.",
                     ["#positionsizing", "#futurestrading", "#riskmanagement"], "Futures position size in 3 numbers", "/tools/position-size-calculator/")})

# ------------------------------------------------------------------ 11. Trend structure (higher highs, higher lows)


def _trend(seed):
    wp = [(0, 100), (6, 103), (10, 101.5), (16, 104.8), (20, 103.2), (26, 106.5), (30, 104.9), (35, 106.0), (40, 102.8), (44, 103.4)]
    c = path(wp, seed=seed, noise=0.22, wick=0.2, force={6: {"h": 103.3}, 10: {"l": 101.2}, 16: {"h": 105.1}, 20: {"l": 102.9}, 26: {"h": 106.8}, 30: {"l": 104.6}, 35: {"h": 106.3}})
    sh, sl = [6, 16, 26], [10, 20, 30]
    piv_h = all(c[i]["h"] == max(x["h"] for x in c[max(0, i - 4):i + 5]) for i in sh + [35])
    piv_l = all(c[i]["l"] == min(x["l"] for x in c[i - 4:i + 5]) for i in sl)
    hh = all(c[a]["h"] < c[b]["h"] for a, b in zip(sh, sh[1:])) and all(c[a]["l"] < c[b]["l"] for a, b in zip(sl, sl[1:]))
    lh = c[35]["h"] < c[26]["h"]
    brk = next((i for i in range(31, len(c)) if c[i]["c"] < c[30]["l"]), None)
    clean = brk is not None and brk > 35 and all(c[i]["l"] > c[30]["l"] for i in range(31, 36))
    return dict(c=c, ok=piv_h and piv_l and hh and lh and clean, brk=brk, sh=sh, sl=sl)


TS = pick(_trend, lambda d: d["ok"])
ch = export(TS["c"]); n = len(ch["candles"]); hl = TS["c"][30]["l"]
assert len(TS["sh"]) == 3
V.append({"id": "v211_edu_trend_structure", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "A trend is just two rules.", "big": True, "reveal": [6, 12],
     "say": "Forget indicators. A trend is just two simple rules."},
    {"type": "chart", "chart": "a", "headline": "Higher highs. Higher lows.", "reveal": [12, 32],
     "marks": [{"bar": 6, "dir": "down", "color": "mint", "at": 0.0}, {"bar": 10, "dir": "up", "color": "mint", "at": 0.05},
               {"bar": 16, "dir": "down", "text": "HH", "color": "mint", "at": 0.25}, {"bar": 20, "dir": "up", "text": "HL", "color": "mint", "at": 0.4},
               {"bar": 26, "dir": "down", "text": "HH", "color": "mint", "at": 0.6}, {"bar": 30, "dir": "up", "text": "HL", "color": "mint", "at": 0.8}],
     "say": "In an uptrend, each high is above the last one, and each pullback stops above the previous low."},
    {"type": "chart", "chart": "a", "headline": "Lower high, then a break.", "reveal": [32, n],
     "levels": [{"price": hl, "from": 30, "label": "Last higher low", "color": "gold", "below": True, "labelAt": -6, "at": 0.0}],
     "marks": [{"bar": 35, "dir": "down", "text": "Lower high", "color": "coral", "at": 0.2}, {"bar": TS["brk"], "dir": "down", "color": "coral", "at": 0.5}],
     "say": "When price makes a lower high and then closes below the last higher low, the structure is broken. That's often the first warning that the trend is changing."},
    FOLLOW],
    "post": post_edu("The two rules that define a trend", "An uptrend is higher highs and higher lows: each high above the last, each pullback stopping above the previous low. A lower high followed by a close below the last higher low breaks that structure, often the first warning that the trend is changing.",
                     ["#priceaction", "#marketstructure"], "Market structure: higher highs and higher lows explained")})

# ------------------------------------------------------------------ 12. MACD crossover lag


def _macd(seed):
    c = path([(0, 108), (18, 105.5), (24, 106.2), (44, 99.5), (72, 106.5)], seed=seed, noise=0.3, wick=0.28, force={44: {"l": 99.2}})
    m, s, h = macd(closes(c))
    low = min(range(36, 56), key=lambda i: c[i]["l"])
    crosses = [i for i in range(36, len(c)) if m[i - 1] is not None and s[i - 1] is not None and (m[i] - s[i]) * (m[i - 1] - s[i - 1]) < 0]
    return dict(c=c, m=m, s=s, h=h, low=low, crosses=crosses)


M = pick(_macd, lambda d: d["low"] == 44 and len(d["crosses"]) == 1 and d["m"][d["crosses"][0]] > d["s"][d["crosses"][0]] and 3 <= d["crosses"][0] - 44 <= 9
         and all(d["m"][i] > d["s"][i] for i in range(d["crosses"][0], len(d["c"]))))
S = 34
cx = M["crosses"][0]; lag = cx - M["low"]
rise = (M["c"][cx]["c"] / M["c"][M["low"]]["l"] - 1) * 100
assert 1 <= rise and lag >= 3
vals = [x for x in M["m"][S:] + M["s"][S:] + M["h"][S:] if x is not None]
lo_p, hi_p = min(vals), max(vals); span = hi_p - lo_p
ch = export(M["c"], S, panel={"id": "macd", "label": "MACD 12, 26, 9", "min": round(lo_p - 0.12 * span, 2), "max": round(hi_p + 0.12 * span, 2),
                              "levels": [{"y": 0, "label": "0", "color": "muted"}],
                              "lines": [{"id": "macd", "color": "blue", "values": M["m"]}, {"id": "signal", "color": "gold", "values": M["s"]}],
                              "hist": {"id": "hist", "values": M["h"]}})
ch["panel"]["hist"]["values"] = r2(M["h"][S:])
n = len(ch["candles"]); lw, cs = M["low"] - S, cx - S
V.append({"id": "v212_edu_macd_cross", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Why MACD crosses always feel late.", "big": True, "reveal": [6, lw - 2], "show": ["macd"],
     "say": "Why MACD crosses always feel late."},
    {"type": "chart", "chart": "a", "headline": "Built from moving averages.", "reveal": [lw - 2, cs - 1], "show": ["macd"],
     "marks": [{"bar": lw, "dir": "up", "text": "The low", "color": "mint", "at": 0.3}],
     "say": "MACD is the twelve EMA minus the twenty-six EMA, and the signal line is a nine EMA of MACD. Averages need time to turn."},
    {"type": "chart", "chart": "a", "headline": f"The cross came {lag} bars later.", "reveal": [cs - 1, n], "show": ["macd"],
     "marks": [{"bar": lw, "dir": "up", "text": "The low", "color": "mint", "at": 0.0}, {"bar": cs, "panel": True, "value": round(M["m"][cx], 3), "text": "Cross", "color": "gold", "at": 0.2}],
     "say": f"Here the bullish cross came {words(lag)} bars after the low, when price was already {words(round(rise))} percent off the bottom."},
    {"type": "rows", "title": "Reading a MACD cross", "head": ["", "", ""], "rows": [
        {"cells": ["In a trend", "", "Confirms momentum"], "good": True, "hl": True}, {"cells": ["In a range", "", "Often noise"]},
        {"cells": ["At the exact turn", "", "Almost never"], "hl": True}],
     "say": "So use it to confirm momentum, not to catch the exact turn."},
    FOLLOW],
    "post": post_edu("Why MACD crosses feel late", f"MACD is the 12 EMA minus the 26 EMA; the signal line is a 9 EMA of MACD. Built from averages, it lags: in this example the bullish cross came {lag} bars after the low, with price already {rise:.0f}% off the bottom. Use it to confirm momentum, not to catch the turn.",
                     ["#macd", "#indicators"], "MACD crossover explained: why it lags")})

# ------------------------------------------------------------------ 13. Bull flag


def _flag(seed):
    wp = [(0, 100.2), (5, 100), (13, 106), (16, 105.2), (18, 105.6), (21, 104.8), (23, 105.2), (26, 104.6), (29, 106.6), (40, 113.4)]
    c = path(wp, seed=seed, noise=0.22, wick=0.2)
    pole_lo = min(x["l"] for x in c[:6]); top = max(range(27), key=lambda i: c[i]["h"]); pole_hi = c[top]["h"]
    in_flag = 12 <= top <= 14 and all(c[i]["l"] >= 104.0 for i in range(top + 1, 27))
    brk = next((i for i in range(27, len(c)) if c[i]["c"] > pole_hi), None)
    target = round(pole_hi + (pole_hi - pole_lo), 2)
    hit = brk is not None and max(x["h"] for x in c[brk:]) >= target
    return dict(c=c, ok=in_flag and brk is not None and brk <= 30 and hit, lo=pole_lo, hi=pole_hi, top=top, brk=brk, target=target)


BF = pick(_flag, lambda d: d["ok"])
ch = export(BF["c"]); n = len(ch["candles"])
flag_lo = min(x["l"] for x in BF["c"][BF["top"] + 1:27])
V.append({"id": "v213_edu_bull_flag", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "This pattern is a pause, not a top.", "big": True, "reveal": [5, 15],
     "zones": [{"from": 5, "to": BF["top"], "lo": BF["lo"], "hi": BF["hi"], "color": "mint", "label": "Pole", "at": 0.35}],
     "say": "This pattern looks like a top, but it's often just a pause."},
    {"type": "chart", "chart": "a", "headline": "Strong pole. Slow, tight flag.", "reveal": [15, 27],
     "zones": [{"from": 5, "to": BF["top"], "lo": BF["lo"], "hi": BF["hi"], "color": "mint", "label": "Pole"}, {"from": BF["top"] + 1, "to": 26, "lo": flag_lo, "hi": BF["hi"], "color": "gold", "label": "Flag", "at": 0.3}],
     "say": "A bull flag is a sharp move up, then a slow, tight drift lower on smaller candles, as buyers take a breather."},
    {"type": "chart", "chart": "a", "headline": "Breakout, then the classic target.", "reveal": [27, n],
     "levels": [{"price": BF["hi"], "from": BF["top"], "label": "Flag high", "color": "gold", "below": True, "at": 0.0},
                {"price": BF["target"], "from": BF["top"], "label": "Classic target", "color": "blue", "at": 0.3}],
     "marks": [{"bar": BF["brk"], "dir": "up", "text": "Close above", "color": "mint", "at": 0.15}],
     "say": "It's confirmed by a close above the flag. The classic target adds the pole's height to the breakout. Here price got there, but plenty of flags fail."},
    FOLLOW],
    "post": post_edu("The bull flag: a pause, not a top", "A bull flag is a sharp move up (the pole) followed by a slow, tight drift lower on smaller candles. It's confirmed by a close above the flag; the classic target adds the pole's height to the breakout. Plenty of flags fail, so wait for the close.",
                     ["#chartpatterns", "#bullflag", "#priceaction"], "Bull flag pattern explained")})

# ------------------------------------------------------------------ 14. Bullish engulfing at support


def _eng(seed):
    wp = [(0, 103.5), (6, 100.4), (11, 102.6), (16, 101.6), (19, 101.0), (20, 100.6), (21, 101.5), (30, 104.2)]
    c = path(wp, seed=seed, noise=0.2, wick=0.18, force={6: {"l": 100.0}, 20: {"o": 101.15, "h": 101.25, "l": 100.05, "c": 100.45}, 21: {"o": 100.38, "h": 101.68, "l": 100.3, "c": 101.55}})
    a, b = c[20], c[21]
    eng = a["c"] < a["o"] and b["c"] > b["o"] and b["o"] <= a["c"] and b["c"] >= a["o"]
    sup = min(x["l"] for x in c[:20]) == 100.0 and all(x["l"] > 100.0 for x in c[7:20])
    after = all(x["l"] > a["l"] for x in c[22:]) and c[-1]["c"] > 103.5
    return dict(c=c, ok=eng and sup and after)


EG = pick(_eng, lambda d: d["ok"])
ch = export(EG["c"]); n = len(ch["candles"])
V.append({"id": "v214_edu_engulfing", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "One candle that swallows the last.", "big": True, "reveal": [6, 18],
     "levels": [{"price": 100.0, "label": "Support", "color": "gold", "below": True, "at": 0.3}],
     "say": "One candle that swallows the one before it."},
    {"type": "chart", "chart": "a", "headline": "The bullish engulfing candle.", "reveal": [18, 22],
     "levels": [{"price": 100.0, "label": "Support", "color": "gold", "below": True}],
     "marks": [{"bar": 21, "dir": "up", "text": "Engulfing", "color": "mint", "at": 0.6}],
     "say": "Its green body completely covers the previous red body. Sellers had control, and buyers took all of it back."},
    {"type": "chart", "chart": "a", "headline": "Location matters more than the candle.", "reveal": [22, n],
     "levels": [{"price": 100.0, "label": "Support", "color": "gold", "below": True}],
     "say": "It tends to mean more at support after a pullback, like here, than in the middle of a range."},
    {"type": "rows", "title": "A bullish engulfing candle…", "head": ["", "", ""], "rows": [
        {"cells": ["At support", "", "Worth noticing"], "good": True, "hl": True}, {"cells": ["Mid-range", "", "Often noise"]}],
     "say": "Read it with its location, never on its own."},
    FOLLOW],
    "post": post_edu("The bullish engulfing candle", "A bullish engulfing candle's green body completely covers the previous red body: sellers had control and buyers took all of it back. It tends to mean more at support after a pullback than in the middle of a range. Read it with its location, never on its own.",
                     ["#candlestickpatterns", "#priceaction"], "Bullish engulfing candle explained")})

# ------------------------------------------------------------------ 15. Drawdown math


def _dd(seed):
    c = path([(0, 100), (6, 92), (9, 95), (16, 78), (19, 82), (26, 50), (31, 60), (34, 57), (42, 75)], seed=seed, noise=1.1, wick=0.9)
    ok = c[0]["c"] == 100 and c[26]["c"] == 50 and c[-1]["c"] == 75 and max(x["h"] for x in c[1:]) < 101.5 and min(x["c"] for x in c) == 50
    return dict(c=c, ok=ok)


DD = pick(_dd, lambda d: d["ok"])
ch = export(DD["c"]); n = len(ch["candles"])
c0, cl, ce = DD["c"][0]["c"], DD["c"][26]["c"], DD["c"][-1]["c"]
down, up, net = (cl / c0 - 1) * 100, (ce / cl - 1) * 100, (ce / c0 - 1) * 100
assert (round(down), round(up), round(net)) == (-50, 50, -25)
need = lambda loss: loss / (1 - loss) * 100
assert (round(need(0.10), 1), round(need(0.25), 1), round(need(0.50))) == (11.1, 33.3, 100)
V.append({"id": "v215_edu_drawdown_math", "tag": EDU_TAG, "site_path": "/learn/max-drawdown-explained/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Down 50%, up 50%, still losing.", "big": True, "reveal": [6, 27],
     "levels": [{"price": c0, "label": "Start", "color": "muted", "below": True, "at": 0.1}],
     "marks": [{"bar": 26, "dir": "up", "text": f"−{abs(round(down))}%", "color": "coral", "at": 0.85}],
     "say": "Down fifty percent, then up fifty percent, and you're still losing."},
    {"type": "chart", "chart": "a", "headline": "Still 25% below the start.", "reveal": [27, n],
     "levels": [{"price": c0, "label": "Start", "color": "muted", "below": True}],
     "marks": [{"bar": 26, "dir": "up", "text": f"−{abs(round(down))}%", "color": "coral", "at": 0.0}, {"bar": n - 1, "dir": "down", "text": f"+{round(up)}%", "color": "mint", "at": 0.5}],
     "say": "A hundred falls to fifty. A fifty percent gain from fifty only gets back to seventy-five, still twenty-five percent below where it started."},
    {"type": "rows", "title": "Gain needed to get back", "head": ["Loss", "", "Gain needed"], "rows": [
        {"cells": ["−10%", "", "+11.1%"]}, {"cells": ["−25%", "", "+33.3%"]}, {"cells": ["−50%", "", "+100%"], "hl": True}],
     "say": "Losses and recoveries aren't symmetric. A fifty percent loss needs a one hundred percent gain just to get back to even."},
    FOLLOW],
    "post": post_edu("Down 50%, up 50%, still losing", "100 falls 50% to 50. A 50% gain from 50 is 75, still 25% below the start. The gain needed to recover is loss / (1 − loss): −10% needs +11.1%, −25% needs +33.3%, −50% needs +100%. That's why keeping drawdowns small matters.",
                     ["#drawdown", "#riskmanagement"], "Drawdown recovery math explained", "/learn/max-drawdown-explained/")})

# ------------------------------------------------------------------ 16. Stochastic at range support


def _sto(seed):
    wp = [(0, 101.6), (5, 102.85), (10, 100.2), (16, 102.8), (22, 100.25), (28, 102.85), (33, 101.4), (38, 100.15), (47, 102.75)]
    c = path(wp, seed=seed, noise=0.2, wick=0.18, force={10: {"l": 100.0}, 22: {"l": 100.02}, 38: {"l": 100.0}, 5: {"h": 103.0}, 16: {"h": 102.98}, 28: {"h": 103.0}})
    k, d = stochastic(c)
    cx = next((i for i in range(38, len(c)) if k[i] > d[i] and k[i - 1] <= d[i - 1]), None)
    rng = all(b["l"] >= 100.0 and b["h"] <= 103.0 for b in c)
    ok = (rng and k[38] < 20 and cx is not None and cx <= 40 and k[cx] < 30 and max(b["h"] for b in c[cx:]) >= 102.6
          and all(k[i] >= 20 for i in range(30, 37)) and max(k[cx:]) > 80)
    return dict(c=c, k=k, d=d, cx=cx, ok=ok)


ST = pick(_sto, lambda d: d["ok"], seeds=range(1, 300))
S = 15
ch = export(ST["c"], S, panel={"id": "sto", "label": "Stochastic 14, 3", "min": 0, "max": 100, "levels": [{"y": 80, "label": "80", "color": "coral"}, {"y": 20, "label": "20", "color": "mint"}],
                               "lines": [{"id": "k", "color": "blue", "values": ST["k"]}, {"id": "d", "color": "gold", "values": ST["d"]}]})
n = len(ch["candles"]); cs = ST["cx"] - S
assert min(b["l"] for b in ST["c"]) == 100.0 and max(b["h"] for b in ST["c"]) == 103.0 and ST["k"][ST["cx"]] < 20
ST_LO = {"price": 100.0, "label": "Range low", "color": "mint", "below": True}
ST_HI = {"price": 103.0, "label": "Range high", "color": "coral"}
V.append({"id": "v216_edu_stochastic", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Stochastic under 20 at support.", "big": True, "reveal": [6, 14], "show": ["sto"],
     "levels": [{**ST_LO, "at": 0.3}], "say": "Stochastic under twenty, right at support. Here's how to read it."},
    {"type": "chart", "chart": "a", "headline": "Where the close sits in its range.", "reveal": [14, cs + 1], "show": ["sto"],
     "levels": [ST_LO, {**ST_HI, "at": 0.2}],
     "marks": [{"bar": cs, "panel": True, "value": round(ST["k"][ST["cx"]], 1), "text": "Turns up", "color": "mint", "at": 0.6}],
     "say": "Stochastic shows where the close sits inside the last fourteen bars' range, from zero to one hundred. Below twenty, price is near the bottom of that range."},
    {"type": "chart", "chart": "a", "headline": "In a range, it often marks the bounce.", "reveal": [cs + 1, n], "show": ["sto"],
     "levels": [ST_LO, ST_HI],
     "marks": [{"bar": cs, "panel": True, "value": round(ST["k"][ST["cx"]], 1), "text": "Turns up", "color": "mint", "at": 0.0}],
     "say": "In a sideways market, a turn up from below twenty near support often comes before a move back toward the top of the range. In a strong downtrend, though, it can stay below twenty for a long time."},
    {"type": "rows", "title": "Stochastic below 20…", "head": ["", "", ""], "rows": [
        {"cells": ["In a range, at support", "", "Watch for the turn"], "good": True, "hl": True}, {"cells": ["In a strong downtrend", "", "Can stay low"]}],
     "say": "So read it with the market around it: useful in ranges, misleading in strong trends."},
    FOLLOW],
    "post": post_edu("Stochastic below 20 at support", "The stochastic oscillator shows where the close sits inside the range of the last 14 bars, from 0 to 100. Below 20, price is near the bottom of that range. In a sideways market, a turn up from below 20 near support often comes before a move back toward the top of the range; in a strong downtrend it can stay below 20 for a long time.",
                     ["#stochastic", "#indicators", "#rangetrading"], "Stochastic oscillator explained: below 20 at support")})

# ------------------------------------------------------------------ 17. RSI divergence


def _div(seed):
    wp = [(0, 100), (14, 103.2), (18, 102.3), (26, 106), (30, 104.4), (36, 106.8), (39, 106.1), (43, 107.8), (47, 106.3), (52, 103.8)]
    c = path(wp, seed=seed, noise=0.24, wick=0.2, force={26: {"h": 106.3}, 36: {"h": 107.1}, 43: {"h": 108.0}})
    r = rsi(closes(c))
    h1 = max(range(20, 30), key=lambda i: c[i]["h"]); h2 = max(range(31, 40), key=lambda i: c[i]["h"]); h3 = max(range(40, 48), key=lambda i: c[i]["h"])
    sw = min(range(h2, h3), key=lambda i: c[i]["l"])
    brk = next((i for i in range(h3, len(c)) if c[i]["c"] < c[sw]["l"]), None)
    ok = ((h1, h2, h3) == (26, 36, 43) and 66 <= r[h1] <= 86 and r[h2] < r[h1] - 5 and r[h3] < r[h1] - 5 and max(r[20:26]) < r[h1] + 3
          and brk is not None and max(b["h"] for b in c) == c[43]["h"])
    return dict(c=c, r=r, sw=sw, brk=brk, ok=ok)


DV = pick(_div, lambda d: d["ok"])
S = 14
assert min(x for x in DV["r"][S:] if x is not None) > 30
ch = export(DV["c"], S, panel={"id": "rsi", "label": "RSI 14", "min": 25, "max": 95, "levels": [{"y": 70, "label": "70", "color": "coral"}, {"y": 30, "label": "30", "color": "mint"}],
                               "lines": [{"id": "rsi", "color": "violet", "values": DV["r"]}]})
n = len(ch["candles"]); r1, r2_ = round(DV["r"][26]), round(DV["r"][36])
assert DV["c"][36]["h"] > DV["c"][26]["h"] and r2_ < r1 and DV["c"][43]["h"] > DV["c"][36]["h"]
later = 43 - 36
DV_MARKS = [{"bar": 26 - S, "dir": "down", "text": "High", "color": "muted"}, {"bar": 36 - S, "dir": "down", "text": "Higher high", "color": "coral"},
            {"bar": 26 - S, "panel": True, "value": round(DV["r"][26], 1), "text": str(r1), "color": "muted"}, {"bar": 36 - S, "panel": True, "value": round(DV["r"][36], 1), "text": str(r2_), "color": "coral"}]
DV_SW = {"price": DV["c"][DV["sw"]]["l"], "from": DV["sw"] - S, "label": "Last swing low", "color": "gold", "below": True, "labelPos": "right"}
V.append({"id": "v217_edu_rsi_divergence", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Price higher, RSI lower.", "big": True, "reveal": [6, 13], "show": ["rsi"],
     "say": "Price makes a higher high, but RSI makes a lower one."},
    {"type": "chart", "chart": "a", "headline": "Bearish divergence.", "reveal": [13, 23], "show": ["rsi"],
     "marks": [{**m, "at": 0.15 + 0.2 * k} for k, m in enumerate(DV_MARKS)],
     "say": f"That's bearish divergence: price went higher, but the momentum behind it got weaker. RSI peaked at {words(r1)}, then only {words(r2_)}."},
    {"type": "chart", "chart": "a", "headline": "A warning, not a trigger.", "reveal": [23, n], "show": ["rsi"],
     "levels": [{**DV_SW, "at": 0.35}],
     "marks": [{**m, "at": 0.0} for m in DV_MARKS[2:]] + [{"bar": 43 - S, "dir": "down", "text": "Another high", "color": "mint", "at": 0.2}, {"bar": DV["brk"] - S, "dir": "down", "color": "coral", "at": 0.7}],
     "say": f"But it's a warning, not a trigger. Here price made one more high {words(later)} bars later before it turned. Wait for price to confirm, like a close below the last swing low."},
    FOLLOW],
    "post": post_edu("RSI divergence: a warning, not a trigger", f"Bearish divergence: price makes a higher high while RSI makes a lower one (here {r1}, then {r2_}), so the momentum behind the move is fading. It's a warning, not a sell signal: in this example price made one more high {later} bars later before it turned. Wait for price to confirm, like a close below the last swing low.",
                     ["#rsi", "#divergence", "#indicators"], "RSI divergence explained")})

# ------------------------------------------------------------------ 18. Pin bar at support


def _pin(seed):
    wp = [(0, 104.5), (6, 101.8), (9, 102.9), (14, 100.3), (17, 101.6), (21, 100.9), (22, 100.6), (30, 103.6)]
    c = path(wp, seed=seed, noise=0.2, wick=0.16, force={14: {"l": 100.0}, 22: {"o": 100.65, "h": 100.95, "l": 99.55, "c": 100.88}})
    p = c[22]
    ok = (all(b["l"] > 100.0 for b in c[15:22]) and min(b["l"] for b in c[:22]) == 100.0 and all(b["l"] > p["l"] + 0.2 for b in c[23:])
          and c[-1]["c"] > 103 and c[21]["c"] < c[21]["o"])
    return dict(c=c, ok=ok)


PB = pick(_pin, lambda d: d["ok"])
ch = export(PB["c"]); n = len(ch["candles"]); pb = PB["c"][22]
body = pb["c"] - pb["o"]; tail = pb["o"] - pb["l"]; ratio = tail / body
assert body > 0 and 4.5 <= ratio <= 5.5 and pb["h"] - pb["c"] < body  # small body near the high, tail about 5x the body
PB_SUP = {"price": 100.0, "label": "Support", "color": "gold", "below": True}
V.append({"id": "v218_edu_pin_bar", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "The candle with a long tail.", "big": True, "reveal": [6, 18], "levels": [{**PB_SUP, "at": 0.3}],
     "say": "This candle with a long tail is called a pin bar."},
    {"type": "chart", "chart": "a", "headline": "Rejected below support.", "reveal": [18, 23], "levels": [PB_SUP],
     "marks": [{"bar": 22, "dir": "up", "text": "Pin bar", "color": "mint", "at": 0.6}],
     "say": f"Price dropped below support, and buyers pushed it all the way back to close near the high. The tail is about {words(round(ratio))} times the body."},
    {"type": "chart", "chart": "a", "headline": "Stop below the tail's tip.", "reveal": [23, n],
     "levels": [PB_SUP, {"price": pb["l"], "from": 22, "label": "Tail's tip", "color": "coral", "below": True, "labelPos": "right", "at": 0.3}],
     "say": "A pin bar tends to mean more at a level after a pullback, like here. Many traders put the stop just below the tip of the tail: if price goes back there, the rejection failed."},
    FOLLOW],
    "post": post_edu("The pin bar: buyers took it all back", f"A pin bar has a small body and a long tail. Here price dropped below support and buyers pushed it back to close near the high, with a tail about {round(ratio)}x the body. It tends to mean more at a level after a pullback; many traders put the stop just below the tip of the tail.",
                     ["#pinbar", "#candlestickpatterns", "#priceaction"], "Pin bar candlestick explained")})

# ------------------------------------------------------------------ 19. Breakout volume


def _vol(seed):
    wp = [(0, 102.6), (5, 104.7), (9, 103.3), (14, 104.75), (18, 103.5), (21, 104.8), (22, 105.25), (24, 104.6), (27, 103.7), (31, 104.6), (33, 104.9), (34, 105.6), (44, 108.2)]
    c = path(wp, seed=seed, noise=0.2, wick=0.18, force={5: {"h": 105.0}, 14: {"h": 104.98}, 22: {"o": 104.85, "h": 105.4, "c": 105.25, "v": 800},
                                                          34: {"o": 104.95, "c": 105.6, "h": 105.75, "v": 5200}})
    avg = lambda i: sum(b["v"] for b in c[i - 20:i]) / 20
    pre = all(b["c"] < 105 and b["h"] <= 105.0 for b in c[:22])
    back = next((i for i in range(23, 27) if c[i]["c"] < 105), None)
    between = all(b["c"] < 105 for b in c[23:34]) and all(b["h"] < 105.4 for b in c[23:34])
    after = all(b["l"] > 104.9 for b in c[36:]) and all(b["c"] > 105 for b in c[35:])
    return dict(c=c, r1=c[22]["v"] / avg(22), r2=c[34]["v"] / avg(34), ok=pre and back == 23 and between and after)


VO = pick(_vol, lambda d: d["ok"] and 0.28 <= d["r1"] < 0.4 and 2 <= d["r2"] < 3, seeds=range(1, 300))
ch = export(VO["c"]); n = len(ch["candles"])
VO_RES = {"price": 105.0, "label": "Resistance", "color": "coral", "below": True}
V.append({"id": "v219_edu_breakout_volume", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "Two breakouts. One held.", "big": True, "reveal": [6, 21], "levels": [{**VO_RES, "at": 0.3}],
     "say": "Two breakouts of the same level. Only one of them held. Watch the volume."},
    {"type": "chart", "chart": "a", "headline": "Breakout on thin volume.", "reveal": [21, 28], "levels": [VO_RES],
     "marks": [{"bar": 22, "dir": "up", "text": "Low volume", "color": "coral", "at": 0.3}],
     "say": "The first one closed above resistance on about a third of the average volume, then fell straight back into the range."},
    {"type": "chart", "chart": "a", "headline": "Breakout on heavy volume.", "reveal": [28, n], "levels": [VO_RES],
     "marks": [{"bar": 34, "dir": "up", "text": f"{VO['r2']:.1f}x volume", "color": "mint", "at": 0.3}],
     "say": "The second came on more than twice the average volume, and held. Volume guarantees nothing, but a breakout with real participation is generally considered more convincing."},
    FOLLOW],
    "post": post_edu("Breakout volume: why one held and one failed", f"Two breakouts of the same level. The first closed above resistance on about a third of the 20-bar average volume and fell straight back into the range. The second came on {VO['r2']:.1f}x the average volume and held. Volume guarantees nothing, but a breakout with real participation is generally considered more convincing.",
                     ["#volume", "#breakout", "#priceaction"], "Breakout volume explained")})

# ------------------------------------------------------------------ 20. Head and shoulders


def _hs(seed):
    wp = [(0, 101.5), (10, 106), (14, 103.45), (19, 108.5), (24, 103.4), (29, 105.9), (33, 102.4), (35, 103.0), (44, 97.3)]
    c = path(wp, seed=seed, noise=0.25, wick=0.22, force={10: {"h": 106.2}, 19: {"h": 108.7}, 29: {"h": 106.1}, 14: {"l": 102.9}, 24: {"l": 102.9}})
    neck, head = 102.9, c[19]["h"]
    piv = all(c[i]["h"] == max(b["h"] for b in c[i - 4:i + 5]) for i in (10, 19, 29)) and all(c[i]["l"] == min(b["l"] for b in c[i - 4:i + 5]) for i in (14, 24))
    brk = next((i for i in range(30, len(c)) if c[i]["c"] < neck), None)
    tgt = round(neck - (head - neck), 2)
    bounce = c[29]["c"] > c[25]["c"] + 1.2 and sum(c[i]["c"] > c[i]["o"] for i in range(26, 30)) >= 3
    ok = (piv and brk is not None and 31 <= brk <= 34 and all(b["c"] >= neck for b in c[10:brk]) and min(b["l"] for b in c[brk:]) <= tgt
          and bounce and max(b["h"] for b in c) == head)
    return dict(c=c, brk=brk, tgt=tgt, ok=ok)


HS = pick(_hs, lambda d: d["ok"], seeds=range(1, 300))
ch = export(HS["c"]); n = len(ch["candles"])
HS_NECK = {"price": 102.9, "label": "Neckline", "color": "gold", "below": True}
V.append({"id": "v220_edu_head_shoulders", "tag": EDU_TAG, "site_path": "/learn/", "charts": {"a": ch}, "scenes": [
    {"type": "chart", "chart": "a", "headline": "The pattern at many trend tops.", "big": True, "reveal": [6, 20],
     "say": "This pattern shows up at the end of many uptrends."},
    {"type": "chart", "chart": "a", "headline": "Shoulder, head, shoulder.", "reveal": [20, 31],
     "marks": [{"bar": 10, "dir": "down", "text": "Shoulder", "color": "coral", "at": 0.05}, {"bar": 19, "dir": "down", "text": "Head", "color": "coral", "at": 0.25},
               {"bar": 29, "dir": "down", "text": "Shoulder", "color": "coral", "at": 0.75}],
     "levels": [{**HS_NECK, "at": 0.45}],
     "say": "A high, a higher high, then a lower high: left shoulder, head, right shoulder. The lows between them form the neckline."},
    {"type": "chart", "chart": "a", "headline": "Confirmed below the neckline.", "reveal": [31, n],
     "levels": [HS_NECK, {"price": HS["tgt"], "label": "Classic target", "color": "blue", "below": True, "at": 0.4}],
     "marks": [{"bar": HS["brk"], "dir": "down", "text": "Close below", "color": "coral", "at": 0.15}],
     "say": "It's confirmed when a candle closes below the neckline. The classic target is the head's height, measured down from the neckline. Here price got there, but many don't."},
    FOLLOW],
    "post": post_edu("Head and shoulders: when it's confirmed", "A high, a higher high, then a lower high: left shoulder, head, right shoulder, with the lows between them forming the neckline. It's confirmed only by a close below the neckline; the classic target is the head's height measured down from it. Many don't reach it.",
                     ["#chartpatterns", "#headandshoulders", "#priceaction"], "Head and shoulders pattern explained")})
