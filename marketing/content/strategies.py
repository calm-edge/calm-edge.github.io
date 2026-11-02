"""Strategy and market-knowledge content for carousels and long lessons, on topics the daily reels don't cover
(the reels teach single concepts; these teach complete strategies with rules, market mechanics and routines).
Every chart is computed (charts.py) and every number on a slide is checked here with assertions.
Ids: c3NN_car_<topic> (carousels), y3NN_long_<topic> (YouTube lessons)."""
import math
from charts import path, closes, ema
from edu import EDU_TAG, HANDLE, SITE, export, pick, words
from carousels import post_car
from longform import post_long, FOLLOW_LONG

C, Y = [], []


def carousel(cid, charts, slides, post):
    if not charts:  # no chart in this one: the caption's disclaimer must not mention one
        post["instagram"] = post["instagram"].replace("Educational example on an illustrative chart.", "Educational content.")
    C.append({"id": cid, "kind": "carousel", "lesson": None, "tag": EDU_TAG if charts else "Education, not financial advice", "handle": HANDLE, "site_path": post["pinterest"]["link"].replace(SITE, ""),
              "charts": charts, "slides": slides, "post": post})


def first_after(c, start, cond):
    return next((i for i in range(start, len(c)) if cond(c[i])), None)


# ================================================================== 1. Opening range breakout (ORB)
OR_BARS = 6  # 6 five-minute bars = the first 30 minutes


def _orb(seed, wp, force, win):
    c = path(wp, seed=seed, noise=0.13, wick=0.12, force=force)
    hi, lo = max(b["h"] for b in c[:OR_BARS]), min(b["l"] for b in c[:OR_BARS])
    mid = round((hi + lo) / 2, 2)
    brk = first_after(c, OR_BARS, lambda b: b["c"] > hi)
    if brk is None:
        return dict(ok=False)
    entry = c[brk]["c"]; risk = round(entry - mid, 2); target = round(entry + 2 * risk, 2)
    t_hit = first_after(c, brk + 1, lambda b: b["h"] >= target)
    s_hit = first_after(c, brk + 1, lambda b: b["l"] <= mid)
    quiet = all(lo <= b["l"] and b["h"] <= hi for b in c[OR_BARS:brk])  # nothing left the range before the breakout bar
    ok = quiet and 7 <= brk <= 10 and (t_hit is not None and (s_hit is None or s_hit > t_hit) if win else s_hit is not None and (t_hit is None or t_hit > s_hit))
    return dict(c=c, hi=hi, lo=lo, mid=mid, brk=brk, entry=entry, risk=risk, target=target, t_hit=t_hit, s_hit=s_hit, ok=ok)


OR_FORCE = {1: {"h": 101.2}, 4: {"l": 100.0}}
ORB = pick(lambda s: _orb(s, [(0, 100.5), (1, 101.05), (3, 100.4), (4, 100.15), (5, 100.7), (7, 101.0), (9, 101.5), (13, 101.85), (16, 101.55), (22, 102.6), (25, 102.35), (32, 103.7)],
                          OR_FORCE, True), lambda d: d["ok"])
ORF = pick(lambda s: _orb(s, [(0, 100.5), (1, 101.05), (3, 100.4), (4, 100.15), (5, 100.7), (7, 101.0), (9, 101.4), (11, 100.95), (15, 100.3), (20, 99.7), (26, 99.95)],
                          OR_FORCE, False), lambda d: d["ok"])
for d in (ORB, ORF):
    assert d["hi"] == 101.2 and d["lo"] == 100.0 and d["mid"] == 100.6
assert ORB["t_hit"] - ORB["brk"] >= 8  # the target takes a while: the lesson says so


def orb_state(d, bars, target=True, stop=True):
    lv = [{"price": d["hi"], "label": "Range high", "color": "mint", "from": 0, "labelPos": "right"},
          {"price": d["lo"], "label": "Range low", "color": "coral", "from": 0, "below": True, "labelPos": "right"}]
    if stop:
        lv.append({"price": d["mid"], "label": "Stop: midpoint", "color": "coral", "from": d["brk"], "below": True, "labelPos": "right"})
    if target:
        lv.append({"price": d["target"], "label": "Target 2R", "color": "mint", "from": d["brk"], "labelPos": "right"})
    return {"bars": bars, "show": [], "levels": lv, "zones": [{"from": 0, "to": OR_BARS - 1, "lo": d["lo"], "hi": d["hi"], "color": "blue", "label": "First 30 min"}],
            "marks": [{"bar": d["brk"], "dir": "up", "text": "Close above", "color": "mint"}]}


orb_charts = {"a": {**export(ORB["c"]), "tf": "5m", "time": {"start": "09:30", "step": 5}}, "b": {**export(ORF["c"]), "tf": "5m", "time": {"start": "09:30", "step": 5}}}
win_state = orb_state(ORB, ORB["t_hit"] + 3)
fail_state = orb_state(ORF, len(ORF["c"]), target=False)
fail_state["marks"].append({"bar": ORF["s_hit"], "dir": "down", "text": "Stopped", "color": "coral"})
carousel("c301_car_orb", orb_charts, [
    {"type": "cover", "kicker": "Strategy breakdown", "title": "The opening range breakout, step by step.", "chart": "a", "state": orb_state(ORB, ORB["brk"] + 4, target=False, stop=False)},
    {"type": "points", "title": "The idea", "points": [
        {"b": "Mark the first 30 minutes", "t": "Their high and low are the opening range.", "color": "blue"},
        {"b": "Wait for a close outside it", "t": "A close above the high: long. Below the low: short.", "color": "mint"},
        {"b": "Risk is defined by the range", "t": "The stop goes back inside it, where the idea is wrong.", "color": "coral"}]},
    {"type": "rows", "title": "One version of the rules", "head": ["", "", ""], "rows": [
        {"cells": ["Entry", "", "Close above range high"], "good": True}, {"cells": ["Stop", "", "Range midpoint"], "hl": True},
        {"cells": ["Target", "", "2× the risk (2R)"], "good": True}, {"cells": ["Time limit", "", "Flat by midday"]}]},
    {"type": "chart", "title": "When it works", "chart": "a", "chartH": 600, "state": win_state,
     "text": f"Range **{ORB['lo']:.2f}–{ORB['hi']:.2f}**, entry **{ORB['entry']:.2f}**, stop **{ORB['mid']:.2f}**: risk **{ORB['risk']:.2f}**. Target {ORB['target']:.2f} hit **{ORB['t_hit'] - ORB['brk']} bars** later."},
    {"type": "chart", "title": "When it doesn't", "chart": "b", "chartH": 600, "state": fail_state,
     "text": "Same setup, different day: the breakout fails, price falls back into the range and **the stop takes a 1R loss**."},
    {"type": "points", "title": "Filters traders add", "points": [
        {"b": "Skip huge ranges", "t": "A very wide range means a very wide stop.", "color": "gold"},
        {"b": "Trade with the bigger trend", "t": "Long breakouts above VWAP and a rising average.", "color": "mint"},
        {"b": "Mind the news", "t": "A data release at 10:00 can whip both sides of the range.", "color": "coral"}]},
    {"type": "end", "title": "Defined risk, not a sure thing.", "text": "Breakouts fail often. The edge, if any, comes from **small losses and 2R wins**. Test it on your own data first."},
], post_car("Opening range breakout: the full strategy", f"The opening range breakout in 7 slides. Mark the high and low of the first 30 minutes, wait for a candle to close outside the range, put the stop back inside it (here the midpoint) and aim for 2× the risk. Example: entry {ORB['entry']:.2f}, stop {ORB['mid']:.2f}, target {ORB['target']:.2f}. And the day it fails: a 1R loss. Test any strategy on your own data before trading it.",
            ["#openingrangebreakout", "#daytradingstrategy", "#orb"], "Opening range breakout strategy explained"))

# ================================================================== 2. Gap fill


def _gap(seed):
    pre = 12  # yesterday's last hour
    wp = [(0, 99.2), (5, 99.75), (8, 99.5), (11, 100.0), (12, 101.25), (14, 101.6), (17, 101.15), (19, 101.4), (23, 100.6), (27, 100.05), (29, 100.3), (36, 99.9)]
    c = path(wp, seed=seed, noise=0.11, wick=0.12, force={12: {"o": 101.1, "l": 101.0}})
    prior = c[pre - 1]["c"]
    day = range(pre, len(c))
    hod_bar = max(day, key=lambda i: c[i]["h"])
    ib_lo = min(c[i]["l"] for i in range(pre, pre + 3))  # low of the first 15 minutes
    trig = first_after(c, pre + 3, lambda b: b["c"] < ib_lo)
    if trig is None:
        return dict(ok=False)
    hod = max(c[i]["h"] for i in range(pre, trig + 1))
    entry = c[trig]["c"]; risk = round(hod - entry, 2); reward = round(entry - prior, 2)
    fill = first_after(c, trig + 1, lambda b: b["l"] <= prior)
    stop_hit = first_after(c, trig + 1, lambda b: b["h"] >= hod)
    ok = (c[pre]["o"] - prior >= 1.0 and hod_bar < trig and fill is not None and (stop_hit is None or stop_hit > fill)
          and reward / risk >= 1.2 and all(c[i]["c"] >= ib_lo for i in range(pre, pre + 3)) and trig >= pre + 6)
    return dict(c=c, pre=pre, prior=prior, ib_lo=ib_lo, trig=trig, hod=hod, entry=entry, risk=risk, reward=reward, fill=fill, ok=ok)


G = pick(_gap, lambda d: d["ok"])
gap_pct = (G["c"][G["pre"]]["o"] / G["prior"] - 1) * 100
gch = {"a": {**export(G["c"]), "tf": "5m"}}
gap_base = {"show": [], "levels": [{"price": G["prior"], "label": "Yesterday's close", "color": "gold"}], "zones": [],  # label on the left, above yesterday's candles
            "marks": [{"bar": G["pre"], "dir": "up", "text": "Gap up", "color": "mint"}]}
gap_trade = {**gap_base, "bars": G["fill"] + 3,
             "levels": gap_base["levels"] + [{"price": G["ib_lo"], "label": "First 15 min low", "color": "blue", "from": G["pre"], "below": True, "labelAt": 0.5}],
             "marks": [{"bar": G["trig"], "dir": "down", "text": "Close below", "color": "coral"}, {"bar": G["fill"], "dir": "up", "text": "Gap filled", "color": "gold"}]}
# c302 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py

# ================================================================== 3. Inside bar breakout (daily chart)


def _inside(seed):
    m = 21  # mother bar
    wp = [(0, 100), (8, 104.5), (12, 103.0), (18, 106.0), (20, 105.4), (21, 107.0), (22, 106.5), (24, 107.8), (28, 109.3), (31, 108.7), (36, 111.2)]
    c = path(wp, seed=seed, noise=0.35, wick=0.3, force={m: {"o": 105.2, "h": 107.4, "l": 104.9, "c": 107.0}, m + 1: {"o": 106.9, "h": 107.2, "l": 106.1, "c": 106.5}})
    mo, ib = c[m], c[m + 1]
    inside = ib["h"] < mo["h"] and ib["l"] > mo["l"]
    trig = first_after(c, m + 2, lambda b: b["h"] > ib["h"])
    if trig is None:
        return dict(ok=False)
    entry = round(ib["h"] + 0.05, 2); stop = round(ib["l"] - 0.05, 2); risk = round(entry - stop, 2); target = round(entry + 2 * risk, 2)
    t_hit = first_after(c, trig, lambda b: b["h"] >= target)
    s_hit = first_after(c, trig, lambda b: b["l"] <= stop)
    ok = inside and trig == m + 2 and t_hit is not None and (s_hit is None or s_hit > t_hit) and mo["h"] - mo["l"] > 2.5 * (ib["h"] - ib["l"]) / 1.2
    return dict(c=c, m=m, mo=mo, ib=ib, trig=trig, entry=entry, stop=stop, risk=risk, target=target, t_hit=t_hit, ok=ok)


IB = pick(_inside, lambda d: d["ok"])
IS = 12  # the chart starts at bar 12: the pattern gets more room
ich = {"a": {**export(IB["c"], IS), "tf": "1D"}}
IM, IT = IB["m"] - IS, IB["t_hit"] - IS
ib_lv = [{"price": IB["entry"], "label": "Buy stop", "color": "mint", "from": IM + 1, "labelPos": "right"},
         {"price": IB["stop"], "label": "Stop", "color": "coral", "from": IM + 1, "below": True, "labelPos": "right"}]
ib_marks = [{"bar": IM, "dir": "down", "text": "Mother bar", "color": "blue"}, {"bar": IM + 1, "dir": "up", "text": "Inside bar", "color": "gold"}]
# c303 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py

# ================================================================== 4. Fibonacci pullback


def _fib(seed):
    a, b = 4, 16
    wp = [(0, 101), (a, 100.0), (8, 102.6), (10, 102.0), (b, 106.0), (19, 104.6), (21, 105.1), (24, 102.6), (27, 104.0), (30, 103.6), (38, 107.4)]
    c = path(wp, seed=seed, noise=0.22, wick=0.2)
    a = min(range(0, 10), key=lambda i: c[i]["l"]); b = max(range(a, 30), key=lambda i: c[i]["h"])  # the swing points, as found on the chart
    A, B = c[a]["l"], c[b]["h"]
    if not 13 <= b <= 18:
        return dict(ok=False)
    lv = {k: round(B - (B - A) * k, 2) for k in (0.382, 0.5, 0.618)}
    low_bar = min(range(b + 1, 30), key=lambda i: c[i]["l"]); low = c[low_bar]["l"]
    trig = first_after(c, low_bar + 1, lambda x: x["c"] > c[low_bar]["h"])
    if trig is None:
        return dict(ok=False)
    entry = c[trig]["c"]; stop = round(low - 0.2, 2); risk = round(entry - stop, 2); reward = round(B - entry, 2)
    s_hit = first_after(c, trig + 1, lambda x: x["l"] <= stop); t_hit = first_after(c, trig + 1, lambda x: x["h"] >= B)
    ok = (lv[0.618] <= low <= lv[0.5] and trig <= low_bar + 3
          and t_hit is not None and (s_hit is None or s_hit > t_hit) and reward / risk >= 1.5)
    return dict(c=c, a=a, b=b, A=A, B=B, lv=lv, low_bar=low_bar, low=low, trig=trig, entry=entry, stop=stop, risk=risk, reward=reward, t_hit=t_hit, ok=ok)


FB = pick(_fib, lambda d: d["ok"])
fch = {"a": {**export(FB["c"]), "tf": "15m"}}
fib_lv = [{"price": FB["lv"][0.5], "label": "50%", "color": "gold", "from": FB["b"], "labelPos": "right"},
          {"price": FB["lv"][0.618], "label": "61.8%", "color": "gold", "from": FB["b"], "below": True, "labelPos": "right"}]
fib_marks = [{"bar": FB["a"], "dir": "up", "text": "A (low)", "color": "blue"}, {"bar": FB["b"], "dir": "down", "text": "B (high)", "color": "blue"}]
fib_zone = [{"from": FB["b"], "to": len(FB["c"]) - 1, "lo": FB["lv"][0.618], "hi": FB["lv"][0.5], "color": "gold"}]
# c304 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py

# ================================================================== 5. Range trading


def _range(seed):
    wp = [(0, 101.5), (4, 102.95), (8, 100.1), (13, 102.9), (18, 100.05), (23, 102.95), (27, 101.0), (30, 100.2), (33, 101.6), (36, 103.6), (40, 104.3)]
    c = path(wp, seed=seed, noise=0.18, wick=0.14, force={4: {"h": 103.0}, 8: {"l": 100.0}, 13: {"h": 103.0}, 18: {"l": 100.0}, 23: {"h": 103.0}, 30: {"l": 100.0}})
    for b in c[:34]:  # the range is the lesson: its edges are exact (the touches above are forced onto them)
        for k in "ohlc":
            b[k] = min(103.0, max(100.0, b[k]))
    inside = all(100.0 <= b["l"] and b["h"] <= 103.0 for b in c[:34]) and all(b["l"] <= min(b["o"], b["c"]) and b["h"] >= max(b["o"], b["c"]) for b in c)
    brk = first_after(c, 30, lambda b: b["c"] > 103.0)
    ok = inside and brk is not None and brk >= 34 and all(b["c"] > 103.0 for b in c[brk:])
    return dict(c=c, brk=brk, ok=ok)


RG = pick(_range, lambda d: d["ok"])
rch = {"a": {**export(RG["c"]), "tf": "5m"}}
rlv = [{"price": 103.0, "label": "Range high", "color": "coral", "labelAt": 14.5}, {"price": 100.0, "label": "Range low", "color": "mint", "below": True, "labelAt": 19.5}]  # labels between the touches
r_touch = [{"bar": i, "dir": "down", "color": "coral"} for i in (4, 13, 23)] + [{"bar": i, "dir": "up", "color": "mint"} for i in (8, 18, 30)]
# c305 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py

# ================================================================== 6-10. Market knowledge and routines (no chart)

# Futures contract math (CME specifications: ES $50 per point, MES $5, NQ $20, MNQ $2; tick 0.25 point)
SPEC = {"ES": 50, "MES": 5, "NQ": 20, "MNQ": 2}
TICK = 0.25
assert SPEC["ES"] * TICK == 12.5 and SPEC["MES"] * TICK == 1.25 and SPEC["NQ"] * TICK == 5 and SPEC["MNQ"] * TICK == 0.5
move = 10
# c306 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py

# c307 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py

# c308 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py

# c309 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py

# c310 retired (2 Nov 2026): replaced by the clearer step-by-step carousels in strategy_carousels.py


# ================================================================== YouTube: Opening range breakout, the complete strategy
n_a, n_b = len(ORB["c"]), len(ORF["c"])
RISK_USD, STOP_PTS = 200, 8
per_contract = STOP_PTS * SPEC["MES"]; contracts = RISK_USD // per_contract
assert per_contract == 40 and contracts == 5
be = 1 / (1 + 2)  # break-even win rate at 2R, before costs
assert round(be * 100) == 33


def lvl(d, *names, at=0.0):
    keep = {"hi": 0, "lo": 1, "stop": 2, "target": 3}
    full = orb_state(d, 0)["levels"]
    return [{**full[keep[k]], "at": at} for k in names if keep[k] < len(full)]


orb_zone = lambda d, at=0.0: [{**orb_state(d, 0)["zones"][0], "at": at}]
brk_mark = lambda d, at=0.3: [{"bar": d["brk"], "dir": "up", "text": "Close above", "color": "mint", "at": at}]
Y.append({"id": "y302_long_orb", "kind": "long", "format": "landscape", "tag": EDU_TAG, "charts": orb_charts,
          "thumb": {"type": "thumb", "kicker": "Full strategy", "title": "Opening range breakout, step by step", "chart": "a", "state": orb_state(ORB, ORB["t_hit"] + 3, stop=False)},  # no stop line: on the short 16:9 chart its label collides with "Range low"
          "scenes": [
    {"type": "chart", "chart": "a", "chapter": "Intro", "headline": "The opening range breakout", "big": True, "reveal": [3, n_a], "levels": lvl(ORB, "hi", "lo"), "zones": orb_zone(ORB),
     "say": "The opening range breakout is one of the oldest day trading strategies there is. It's simple, the rules fit on one card, and the risk is defined before you enter. In this lesson we'll build it step by step: what the opening range is, the exact rules, a day when it works, a day when it doesn't, the filters traders add, and how to size it."},
    {"type": "hook", "kicker": "Before we start", "text": "Education on illustrative charts. Not financial advice.",
     "say": "Everything here is education, on illustrative charts. No strategy works every day, and you should test any idea on your own data before risking money on it."},
    {"type": "chart", "chart": "a", "chapter": "What the opening range is", "headline": "The first 30 minutes", "reveal": [1, OR_BARS], "zones": orb_zone(ORB, 0.5),
     "say": "Start with the idea. The first minutes after the open are when the most orders hit the market: overnight news, orders waiting from the day before, funds rebalancing. That burst of activity sets a high and a low."},
    {"type": "chart", "chart": "a", "headline": "High and low of the range", "reveal": [OR_BARS, OR_BARS], "zones": orb_zone(ORB), "levels": lvl(ORB, "hi", "lo", at=0.2),
     "say": f"Here we use the first thirty minutes, six five-minute candles. Their highest high is the range high, {ORB['hi']:.2f}. Their lowest low is the range low, {ORB['lo']:.2f}. Some traders use five or fifteen minutes instead. What matters is choosing one and always using the same one."},
    {"type": "hook", "kicker": "The logic", "text": "A close outside the range shows who won the open.",
     "say": "The logic is this. While price stays inside the range, buyers and sellers are still fighting over the open. When a candle closes outside it, one side has won that first battle, and the move often continues in that direction. Often, not always."},
    {"type": "rows", "chapter": "The rules", "title": "One version of the rules", "head": ["", "", ""], "rows": [
        {"cells": ["Entry", "", "Close above range high"], "good": True}, {"cells": ["Stop", "", "Range midpoint"], "hl": True},
        {"cells": ["Target", "", "2× the risk (2R)"], "good": True}, {"cells": ["Time limit", "", "Flat by midday"]}],
     "say": "Here's one version of the rules. Entry: a five-minute candle closes above the range high, and we buy at that close. For shorts, it's the mirror image below the range low. Stop: the middle of the range. If price falls back to the midpoint, the breakout has failed. Target: two times what we risk. And a time limit: if neither the stop nor the target is hit by midday, we close the trade."},
    {"type": "hook", "kicker": "Why the midpoint", "text": "Back in the middle of the range, the breakout has failed.",
     "say": "Why the midpoint and not the range low? Because a stop at the range low can be very far away, and a wide stop means a small position. The midpoint is a compromise: far enough to survive a normal retest of the breakout, close enough to keep the risk reasonable."},
    {"type": "chart", "chart": "a", "chapter": "A day when it works", "headline": "The breakout", "reveal": [OR_BARS, ORB["brk"] + 1], "zones": orb_zone(ORB), "levels": lvl(ORB, "hi", "lo"), "marks": brk_mark(ORB, 0.6),
     "say": f"Let's see it on a chart. Price spends two more candles inside the range. Then this candle closes above the range high, at {ORB['entry']:.2f}. That's our entry."},
    {"type": "chart", "chart": "a", "headline": "Stop and target", "reveal": [ORB["brk"] + 1, ORB["brk"] + 1], "zones": orb_zone(ORB), "levels": lvl(ORB, "hi", "lo", "stop", "target", at=0.25), "marks": brk_mark(ORB, 0.0),
     "say": f"The stop goes at the midpoint, {ORB['mid']:.2f}. So the risk is {ORB['risk']:.2f} points. Two times that, added to the entry, gives the target: {ORB['target']:.2f}. All of this is decided before the trade, not during it."},
    {"type": "chart", "chart": "a", "headline": "Patience", "pin": True, "reveal": [ORB["brk"] + 1, n_a], "zones": orb_zone(ORB), "levels": lvl(ORB, "hi", "lo", "stop", "target"), "marks": brk_mark(ORB, 0.0),
     "say": f"Now the hard part: doing nothing. Price pulls back, but never reaches the midpoint. It takes {words(ORB['t_hit'] - ORB['brk'])} candles, about {words(round((ORB['t_hit'] - ORB['brk']) * 5 / 60))} hours, to reach the target. Plenty of traders would have taken a small profit long before, and that habit quietly destroys the math of a two R strategy."},
    {"type": "chart", "chart": "b", "chapter": "A day when it doesn't", "headline": "Same setup, different day", "reveal": [OR_BARS, ORF["brk"] + 1], "zones": orb_zone(ORF), "levels": lvl(ORF, "hi", "lo"), "marks": brk_mark(ORF, 0.6),
     "say": "Now another day. The same range, the same kind of candle closing above the high. Same entry rules, same stop, same target."},
    {"type": "chart", "chart": "b", "headline": "The breakout fails", "reveal": [ORF["brk"] + 1, n_b], "zones": orb_zone(ORF), "levels": lvl(ORF, "hi", "lo", "stop"),
     "marks": brk_mark(ORF, 0.0) + [{"bar": ORF["s_hit"], "dir": "down", "text": "Stopped", "color": "coral", "at": 0.4}],
     "say": f"This time, buyers can't hold it. Price falls back into the range, and {words(ORF['s_hit'] - ORF['brk'])} candles later it hits the midpoint. We lose one R. And notice what happens next: price keeps falling. Without the stop, a normal loss would have become a big one."},
    {"type": "hook", "kicker": "Break-even win rate at 2R", "text": "1 ÷ (1 + 2) ≈ 33%, before costs.",
     "say": "This is the point of the whole structure. With a target twice the size of the stop, you break even, before costs, if one trade in three reaches the target. You can be wrong most of the time and still not lose money. But only if the losses really stay at one R, and the winners really get to two."},
    {"type": "rows", "chapter": "Filters traders add", "title": "Common filters", "head": ["", "", ""], "rows": [
        {"cells": ["Range too wide", "", "Skip: stop too far"]}, {"cells": ["Against the trend", "", "Skip or smaller"]},
        {"cells": ["News inside the window", "", "Wait for it"]}, {"cells": ["After midday", "", "No new entries"], "hl": True}],
     "say": "Most traders add filters, and these are the common ones. First, range size. If today's opening range is much wider than usual, the stop is far and the position tiny, so many skip the day. Second, direction. Taking long breakouts only when price is above VWAP and the moving averages point up. Third, news. A big data release at ten o'clock can whip price through both sides of the range, so some wait for it. And fourth, time. Breakouts late in the morning tend to have less volume behind them."},
    {"type": "hook", "kicker": "One rule about filters", "text": "Add them before you test, not after.",
     "say": "One warning about filters. It's easy to look at past charts and add a filter for every losing day until the results look perfect. That's called curve fitting, and it usually stops working the moment you go live. Choose a few filters that make sense, then test them."},
    {"type": "hook", "chapter": "Sizing and risk", "kicker": "Contracts = $ risk ÷ $ risk per contract", "text": f"${RISK_USD} ÷ ({STOP_PTS} pts × ${SPEC['MES']}) = {contracts} MES",
     "say": f"Now, sizing. Decide the dollars you risk per trade first. Say {words(RISK_USD // 100)} hundred dollars. If the stop is {words(STOP_PTS)} points away and you trade the micro E-mini, at five dollars a point, one contract risks forty dollars. Two hundred divided by forty is {words(contracts)} contracts. On a wider day, with a stop twice as far, you'd trade half as many. The dollar risk stays the same."},
    {"type": "rows", "title": "Daily limits", "head": ["", "", ""], "rows": [
        {"cells": ["Trades per day", "", "1, maybe 2"]}, {"cells": ["After a loss", "", "Same size, no revenge"], "hl": True}, {"cells": ["Daily max loss", "", "Decided before the open"], "good": True}],
     "say": "And limit the day. The opening range breakout is usually one trade, maybe two if the first one stops out and the other side breaks. Never re-enter bigger to win it back, and decide your maximum daily loss before the open."},
    {"type": "rows", "chapter": "Test it yourself", "title": "How to test it", "head": ["", "", ""], "rows": [
        {"cells": ["1. Write the rules", "", "Before looking"]}, {"cells": ["2. Go back 50+ days", "", "Same rules, every day"]},
        {"cells": ["3. Log every trade", "", "Entry, stop, result in R"], "good": True}, {"cells": ["4. Then trade small", "", "Micros, real fills"]}],
     "say": "Before trading it, test it. Write the rules down first. Then go back at least fifty trading days on your market and apply them to every single day, including the ugly ones. Log each trade in R: plus two, minus one, or the time exit. Then trade it small, with micros, to see real fills and your own discipline."},
    {"type": "hook", "kicker": "What you're measuring", "text": "Win rate, average R, and how you feel on losing streaks.",
     "say": "What you're looking for is simple: the win rate, the average result in R, and the longest losing streak. If the numbers work and you can follow the rules through five losses in a row, then you have something."},
    {"type": "rows", "chapter": "Summary", "title": "The opening range breakout", "head": ["", "", ""], "rows": [
        {"cells": ["Range", "", "First 30 minutes"]}, {"cells": ["Entry", "", "Close outside the range"], "good": True},
        {"cells": ["Stop", "", "Back inside: midpoint"], "hl": True}, {"cells": ["Target", "", "2R, flat by midday"], "good": True}],
     "say": "To sum up. Mark the high and low of the first thirty minutes. Enter on a close outside the range. Stop at the midpoint, target two R, and be flat by midday. Size from the stop, and test it before you trust it. It won't work every day, and it doesn't need to."},
    FOLLOW_LONG],
          "post": post_long("Opening Range Breakout Strategy: complete rules, examples and risk management",
                            "The opening range breakout explained step by step: how to mark the opening range, entry, stop and target rules, a day when it works and a day when it fails, the filters traders add, position sizing from the stop, and how to test it on your own data before trading it.",
                            ["#openingrangebreakout", "#daytradingstrategy", "#futurestrading"])})
