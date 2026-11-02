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


orb_charts = {"a": export(ORB["c"]), "b": export(ORF["c"])}
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
gch = {"a": export(G["c"])}
gap_base = {"show": [], "levels": [{"price": G["prior"], "label": "Yesterday's close", "color": "gold"}], "zones": [],  # label on the left, above yesterday's candles
            "marks": [{"bar": G["pre"], "dir": "up", "text": "Gap up", "color": "mint"}]}
gap_trade = {**gap_base, "bars": G["fill"] + 3,
             "levels": gap_base["levels"] + [{"price": G["ib_lo"], "label": "First 15 min low", "color": "blue", "from": G["pre"], "below": True, "labelAt": 0.5}],
             "marks": [{"bar": G["trig"], "dir": "down", "text": "Close below", "color": "coral"}, {"bar": G["fill"], "dir": "up", "text": "Gap filled", "color": "gold"}]}
carousel("c302_car_gap_fill", gch, [
    {"type": "cover", "kicker": "Strategy breakdown", "title": "Gap fill: trading back to yesterday's close.", "chart": "a", "state": {**gap_base, "bars": G["pre"] + 4}},
    {"type": "points", "title": "What a gap is", "points": [
        {"b": "Today opens away from yesterday's close", "t": "News or overnight trading moved the price.", "color": "blue"},
        {"b": "\"Filling the gap\"", "t": "Price trades back to yesterday's close.", "color": "gold"},
        {"b": "Not every gap fills", "t": "Strong news gaps can run all day. You need a trigger.", "color": "coral"}]},
    {"type": "rows", "title": "One version of the rules", "head": ["", "", ""], "rows": [
        {"cells": ["Wait", "", "First 15 minutes"]}, {"cells": ["Entry", "", "Close below their low"], "good": True},
        {"cells": ["Stop", "", "Above the day's high"], "hl": True}, {"cells": ["Target", "", "Yesterday's close"], "good": True}]},
    {"type": "chart", "title": "The open fails, then the fill", "chart": "a", "chartH": 600, "state": gap_trade,
     "text": f"Gap of **{gap_pct:.1f}%**. Entry **{G['entry']:.2f}**, stop **{G['hod']:.2f}** (risk {G['risk']:.2f}), target **{G['prior']:.2f}** (reward {G['reward']:.2f})."},
    {"type": "points", "title": "When to skip it", "points": [
        {"b": "Big news behind the gap", "t": "Earnings or major data can keep the move going.", "color": "coral"},
        {"b": "The open keeps making highs", "t": "No failure, no trade.", "color": "gold"},
        {"b": "Reward smaller than risk", "t": "If the fill is closer than the stop, pass.", "color": "blue"}]},
    {"type": "end", "title": "Let the open fail first.", "text": "A gap is a reason to watch, not a reason to fade. Trade the failure, target the close."},
], post_car("Gap fill strategy explained", f"A gap fill means price trades back to yesterday's close. One way to trade it: wait for the first 15 minutes, enter on a close below their low, stop above the day's high, target yesterday's close. Example: a {gap_pct:.1f}% gap, entry {G['entry']:.2f}, stop {G['hod']:.2f}, target {G['prior']:.2f}. Big news gaps often don't fill, so you need the failure first.",
            ["#gapfill", "#daytradingstrategy", "#gaptrading"], "Gap fill trading strategy explained"))

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
ich = {"a": export(IB["c"], IS)}
IM, IT = IB["m"] - IS, IB["t_hit"] - IS
ib_lv = [{"price": IB["entry"], "label": "Buy stop", "color": "mint", "from": IM + 1, "labelPos": "right"},
         {"price": IB["stop"], "label": "Stop", "color": "coral", "from": IM + 1, "below": True, "labelPos": "right"}]
ib_marks = [{"bar": IM, "dir": "down", "text": "Mother bar", "color": "blue"}, {"bar": IM + 1, "dir": "up", "text": "Inside bar", "color": "gold"}]
carousel("c303_car_inside_bar", ich, [
    {"type": "cover", "kicker": "Strategy breakdown", "title": "The inside bar breakout.", "chart": "a", "state": {"bars": IM + 2, "show": [], "levels": [], "zones": [], "marks": ib_marks}},
    {"type": "points", "title": "What an inside bar is", "points": [
        {"b": "A candle inside the previous one", "t": "Lower high and higher low than the bar before it.", "color": "gold"},
        {"b": "The bar before is the \"mother bar\"", "t": "It sets the range the market is pausing in.", "color": "blue"},
        {"b": "A pause, often before a push", "t": "It shows indecision. Direction comes from the break.", "color": "mint"}]},
    {"type": "rows", "title": "One version of the rules", "head": ["", "", ""], "rows": [
        {"cells": ["Trend filter", "", "Trade with the trend"]}, {"cells": ["Entry", "", "Buy stop above inside bar"], "good": True},
        {"cells": ["Stop", "", "Below inside bar"], "hl": True}, {"cells": ["Target", "", "2R"], "good": True}]},
    {"type": "chart", "title": "Pause, then continuation", "chart": "a", "chartH": 600,
     "state": {"bars": IT + 1, "show": [], "zones": [], "marks": ib_marks, "levels": ib_lv + [{"price": IB["target"], "label": "Target 2R", "color": "mint", "from": IM + 1, "labelPos": "right"}]},
     "text": f"Entry **{IB['entry']:.2f}**, stop **{IB['stop']:.2f}**: risk **{IB['risk']:.2f}**, small because the inside bar is small. Target **{IB['target']:.2f}**."},
    {"type": "points", "title": "Why traders like it", "points": [
        {"b": "Tight, logical stop", "t": "If price breaks the other side, the idea is wrong.", "color": "mint"},
        {"b": "Works on any timeframe", "t": "Cleaner on daily and 4-hour charts.", "color": "blue"},
        {"b": "Easy to scan for", "t": "Two candles, one rule.", "color": "gold"}]},
    {"type": "points", "title": "Where it goes wrong", "points": [
        {"b": "Against the trend", "t": "Inside bars in a downtrend breaking up often fail.", "color": "coral"},
        {"b": "In a choppy range", "t": "Price can break one side, then the other.", "color": "coral"},
        {"b": "Huge mother bar", "t": "The pause can last for days. Be patient or skip it.", "color": "gold"}]},
    {"type": "end", "title": "Small bar, small risk, clear trigger.", "text": "Trade it with the trend, place the stop on the other side, and let the break decide."},
], post_car("Inside bar breakout strategy", f"An inside bar has a lower high and a higher low than the candle before it: a pause. One way to trade it: with the trend, a buy stop just above the inside bar, a stop just below it, target 2R. Example: entry {IB['entry']:.2f}, stop {IB['stop']:.2f}, target {IB['target']:.2f}.",
            ["#insidebar", "#priceaction", "#swingtrading"], "Inside bar breakout strategy explained"))

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
fch = {"a": export(FB["c"])}
fib_lv = [{"price": FB["lv"][0.5], "label": "50%", "color": "gold", "from": FB["b"], "labelPos": "right"},
          {"price": FB["lv"][0.618], "label": "61.8%", "color": "gold", "from": FB["b"], "below": True, "labelPos": "right"}]
fib_marks = [{"bar": FB["a"], "dir": "up", "text": "A (low)", "color": "blue"}, {"bar": FB["b"], "dir": "down", "text": "B (high)", "color": "blue"}]
fib_zone = [{"from": FB["b"], "to": len(FB["c"]) - 1, "lo": FB["lv"][0.618], "hi": FB["lv"][0.5], "color": "gold"}]
carousel("c304_car_fib_pullback", fch, [
    {"type": "cover", "kicker": "Strategy breakdown", "title": "Buying the pullback with Fibonacci levels.", "chart": "a",
     "state": {"bars": FB["low_bar"] + 2, "show": [], "levels": fib_lv, "zones": fib_zone, "marks": fib_marks}},
    {"type": "formula", "title": "How the levels are drawn", "formula": "Level = B − (B − A) × ratio",
     "small": f"Here: A = {FB['A']:.2f}, B = {FB['B']:.2f} → 50% = {FB['lv'][0.5]:.2f}, 61.8% = {FB['lv'][0.618]:.2f}",
     "text": "A is the start of the move, B its end. The common ratios **38.2%, 50% and 61.8%** mark how much of the move a pullback gives back."},
    {"type": "points", "title": "The idea", "points": [
        {"b": "Trends move in waves", "t": "A push, a pullback, another push.", "color": "mint"},
        {"b": "Many traders watch 50–61.8%", "t": "A deep but normal pullback in a healthy trend.", "color": "gold"},
        {"b": "The level is not the signal", "t": "Wait for price to react there.", "color": "coral"}]},
    {"type": "chart", "title": "Pullback into the zone, then a reaction", "chart": "a", "chartH": 600,
     "state": {"bars": FB["t_hit"] + 2, "show": [], "levels": fib_lv, "zones": fib_zone,
               "marks": [{"bar": FB["low_bar"], "dir": "up", "text": "Low in zone", "color": "gold"}, {"bar": FB["trig"], "dir": "down", "text": "Entry", "color": "mint"}]},
     "text": f"Low **{FB['low']:.2f}** inside the zone. Entry **{FB['entry']:.2f}** on the first close above the low bar's high, stop **{FB['stop']:.2f}**, first target the old high **{FB['B']:.2f}**."},
    {"type": "rows", "title": "This trade in numbers", "head": ["", "", ""], "rows": [
        {"cells": ["Risk", "", f"{FB['risk']:.2f}"]}, {"cells": ["Reward to B", "", f"{FB['reward']:.2f}"]},
        {"cells": ["Reward ÷ risk", "", f"{FB['reward'] / FB['risk']:.1f}R"], "good": True, "hl": True}]},
    {"type": "points", "title": "Common mistakes", "points": [
        {"b": "Picking A and B after the fact", "t": "Use clear swing points, the same way every time.", "color": "coral"},
        {"b": "Buying the level blindly", "t": "No reaction, no trade. Levels break.", "color": "gold"},
        {"b": "Using it against the trend", "t": "It's a tool for joining a trend, not for catching tops.", "color": "blue"}]},
    {"type": "end", "title": "Zone first, reaction second.", "text": "Fibonacci levels show where to look. The candle that reacts there tells you when."},
], post_car("Fibonacci pullback strategy", f"Fibonacci retracements measure how much of a move a pullback gives back: Level = B − (B − A) × ratio. Many traders watch 50–61.8% in a trend and wait for a reaction there. Example: low {FB['low']:.2f} inside the zone, entry {FB['entry']:.2f}, stop {FB['stop']:.2f}, first target {FB['B']:.2f} ({FB['reward'] / FB['risk']:.1f}R).",
            ["#fibonacci", "#pullback", "#daytradingstrategy"], "Fibonacci pullback trading strategy"))

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
rch = {"a": export(RG["c"])}
rlv = [{"price": 103.0, "label": "Range high", "color": "coral", "labelAt": 14.5}, {"price": 100.0, "label": "Range low", "color": "mint", "below": True, "labelAt": 19.5}]  # labels between the touches
r_touch = [{"bar": i, "dir": "down", "color": "coral"} for i in (4, 13, 23)] + [{"bar": i, "dir": "up", "color": "mint"} for i in (8, 18, 30)]
carousel("c305_car_range_trading", rch, [
    {"type": "cover", "kicker": "Strategy breakdown", "title": "How to trade a range (and when to stop).", "chart": "a", "state": {"bars": 31, "show": [], "levels": [{**rlv[0], "labelPos": "right"}, rlv[1]], "zones": [], "marks": r_touch}},  # nothing above the high at the right end yet
    {"type": "points", "title": "Is it really a range?", "points": [
        {"b": "At least two touches per side", "t": "Here: three at the high, three at the low.", "color": "blue"},
        {"b": "Flat highs and lows", "t": "Not higher lows or lower highs.", "color": "gold"},
        {"b": "Room inside", "t": "Enough distance for a reward bigger than the risk.", "color": "mint"}]},
    {"type": "rows", "title": "One version of the rules", "head": ["", "", ""], "rows": [
        {"cells": ["Buy", "", "Rejection near the low"], "good": True}, {"cells": ["Sell", "", "Rejection near the high"], "good": True},
        {"cells": ["Stop", "", "Just outside the range"], "hl": True}, {"cells": ["Target", "", "Middle or other side"]}]},
    {"type": "chart", "title": "Every range ends", "chart": "a", "chartH": 600,
     "state": {"bars": len(RG["c"]), "show": [], "levels": rlv, "zones": [], "marks": [{"bar": RG["brk"], "dir": "up", "text": "Close outside", "color": "mint"}]},
     "text": "After six touches, a candle **closes above** the high and price never comes back in. The stop just outside is what limits the damage."},
    {"type": "points", "title": "Rules that keep you safe", "points": [
        {"b": "The stop is not optional", "t": "A range trade without one turns into a breakout loss.", "color": "coral"},
        {"b": "Don't trade the middle", "t": "Entries in the middle have no edge and no clear stop.", "color": "gold"},
        {"b": "Switch modes on a close outside", "t": "Stop fading. Start watching the breakout and retest.", "color": "blue"}]},
    {"type": "end", "title": "Fade the edges, respect the break.", "text": "Ranges pay the patient trader until they don't. The close outside is your signal to stop."},
], post_car("How to trade a range", "A range needs at least two touches on each side and flat highs and lows. One way to trade it: buy rejections near the low, sell rejections near the high, stop just outside, target the middle or the other side. Every range ends: a close outside means stop fading and start watching the breakout.",
            ["#rangetrading", "#supportandresistance", "#priceaction"], "Range trading strategy explained"))

# ================================================================== 6-10. Market knowledge and routines (no chart)

# Futures contract math (CME specifications: ES $50 per point, MES $5, NQ $20, MNQ $2; tick 0.25 point)
SPEC = {"ES": 50, "MES": 5, "NQ": 20, "MNQ": 2}
TICK = 0.25
assert SPEC["ES"] * TICK == 12.5 and SPEC["MES"] * TICK == 1.25 and SPEC["NQ"] * TICK == 5 and SPEC["MNQ"] * TICK == 0.5
move = 10
carousel("c306_car_futures_math", {}, [
    {"type": "cover", "kicker": "Futures basics", "title": "What one point is worth on ES, NQ and the micros.",
     "text": "Know this **before** your first trade. It decides your position size."},
    {"type": "rows", "title": "Dollars per point", "head": ["Contract", "Per point", "Per tick (0.25)"], "rows": [
        {"cells": ["ES (S&P 500)", f"${SPEC['ES']}", f"${SPEC['ES'] * TICK:.2f}"]}, {"cells": ["MES (micro)", f"${SPEC['MES']}", f"${SPEC['MES'] * TICK:.2f}"], "good": True},
        {"cells": ["NQ (Nasdaq 100)", f"${SPEC['NQ']}", f"${SPEC['NQ'] * TICK:.2f}"]}, {"cells": ["MNQ (micro)", f"${SPEC['MNQ']}", f"${SPEC['MNQ'] * TICK:.2f}"], "good": True}]},
    {"type": "rows", "title": f"The same {move}-point move", "head": ["Contract", "", "1 contract"], "rows": [
        {"cells": ["ES", "", f"${SPEC['ES'] * move:,}"]}, {"cells": ["MES", "", f"${SPEC['MES'] * move:,}"], "good": True},
        {"cells": ["NQ", "", f"${SPEC['NQ'] * move:,}"]}, {"cells": ["MNQ", "", f"${SPEC['MNQ'] * move:,}"], "good": True}],
     "text": "Micros are **one tenth** of the full contract. Same chart, a tenth of the risk."},
    {"type": "formula", "title": "Risk per trade", "formula": "Risk = stop (points) × $ per point × contracts",
     "small": f"Example: 8-point stop on 3 MES = 8 × ${SPEC['MES']} × 3 = ${8 * SPEC['MES'] * 3}"},
    {"type": "points", "title": "Why it matters", "points": [
        {"b": "Size from the stop, not from a feeling", "t": "Decide the dollars you risk, then compute contracts.", "color": "mint"},
        {"b": "Start with micros", "t": "Learn with a tenth of the risk on the same market.", "color": "blue"},
        {"b": "NQ moves more points than ES", "t": "Same stop in points is not the same risk.", "color": "coral"}]},
    {"type": "end", "title": "Know the point value before you click.", "text": "Points × dollars per point × contracts = the money on the line."},
], post_car("Futures point values: ES, MES, NQ, MNQ", f"Dollars per point: ES ${SPEC['ES']}, MES ${SPEC['MES']}, NQ ${SPEC['NQ']}, MNQ ${SPEC['MNQ']}. A {move}-point move is ${SPEC['ES'] * move} on one ES and ${SPEC['MES'] * move} on one MES. Risk = stop in points × $ per point × contracts. Contract specs from CME Group.",
            ["#futurestrading", "#es", "#nq", "#microfutures"], "Futures point values explained: ES, MES, NQ, MNQ"))

carousel("c307_car_order_types", {}, [
    {"type": "cover", "kicker": "Trading basics", "title": "4 order types every trader must know.", "text": "Using the wrong one costs money on **every** trade."},
    {"type": "points", "title": "Market order", "points": [
        {"b": "Fills now, at the best available price", "t": "Speed is guaranteed. The price is not.", "color": "blue"},
        {"b": "Risk: slippage", "t": "In fast markets you can fill worse than the price you saw.", "color": "coral"}]},
    {"type": "points", "title": "Limit order", "points": [
        {"b": "Fills at your price or better", "t": "Buy limit below the market, sell limit above it.", "color": "mint"},
        {"b": "Risk: no fill", "t": "If price never reaches it, you're not in the trade.", "color": "gold"}]},
    {"type": "points", "title": "Stop order", "points": [
        {"b": "Becomes a market order at your price", "t": "Used for stop losses and breakout entries.", "color": "coral"},
        {"b": "Risk: slippage through the level", "t": "In a gap or a spike it fills beyond the stop.", "color": "gold"}]},
    {"type": "points", "title": "Stop-limit order", "points": [
        {"b": "Becomes a limit order at your price", "t": "You control the worst price.", "color": "blue"},
        {"b": "Risk: it can skip you", "t": "A stop-limit used as a stop loss may never fill.", "color": "coral"}]},
    {"type": "rows", "title": "Quick guide", "head": ["You want…", "", "Use"], "rows": [
        {"cells": ["In right now", "", "Market"]}, {"cells": ["A better price", "", "Limit"]},
        {"cells": ["Out if wrong, guaranteed", "", "Stop"], "good": True, "hl": True}, {"cells": ["A breakout entry, capped", "", "Stop-limit"]}]},
    {"type": "end", "title": "Your stop loss should be a stop order.", "text": "A stop-limit can be skipped in a fast move. That's exactly when you need to be out."},
], post_car("4 order types every trader must know", "Market: fills now, price not guaranteed. Limit: your price or better, fill not guaranteed. Stop: becomes a market order at your price, used for stop losses. Stop-limit: becomes a limit order, and can be skipped in a fast move, so don't use it as your protective stop.",
            ["#ordertypes", "#tradingbasics", "#stoploss"], "Market, limit, stop and stop-limit orders explained"))

carousel("c308_car_sessions", {}, [
    {"type": "cover", "kicker": "Market timing", "title": "When the market actually moves.", "text": "Futures trade almost 24 hours. **Volume doesn't.**"},
    {"type": "rows", "title": "Main sessions (New York time)", "head": ["Session", "", "Hours (ET)"], "rows": [
        {"cells": ["Asia (Tokyo)", "", "7 pm – 4 am"]}, {"cells": ["London", "", "3 am – 11:30 am"]},
        {"cells": ["New York stocks", "", "9:30 am – 4 pm"], "good": True, "hl": True}, {"cells": ["CME daily break", "", "5 pm – 6 pm"]}],
     "text": "Approximate, standard time. Shifts by an hour when daylight saving changes."},
    {"type": "points", "title": "The busiest windows", "points": [
        {"b": "The New York open", "t": "9:30–11:00 ET: the most volume and the biggest moves for US index futures.", "color": "mint"},
        {"b": "London / New York overlap", "t": "Both centers open: liquidity peaks for currencies.", "color": "blue"},
        {"b": "The close", "t": "15:00–16:00 ET: volume picks up again into the end of the day.", "color": "gold"}]},
    {"type": "points", "title": "The slow windows", "points": [
        {"b": "Midday (about 11:30–14:00 ET)", "t": "Lunch hours: thinner volume, more chop.", "color": "coral"},
        {"b": "Overnight for US indexes", "t": "Moves happen, but with a fraction of the day's volume.", "color": "coral"}]},
    {"type": "points", "title": "What to do with this", "points": [
        {"b": "Trade when your market is active", "t": "Breakout strategies need volume.", "color": "mint"},
        {"b": "Check the calendar", "t": "8:30 and 10:00 ET data releases move markets in seconds.", "color": "gold"},
        {"b": "Track your results by hour", "t": "Many traders find one window does most of their damage.", "color": "blue"}]},
    {"type": "end", "title": "Same market, different hours, different behaviour.", "text": "Pick the window that fits your strategy, and log which hours actually work for you."},
], post_car("Trading sessions: when the market actually moves", "Futures trade almost 24 hours, but volume doesn't. For US index futures the New York open (9:30–11:00 ET) is the busiest window, midday is often slow and choppy, and volume picks up again into the close. Check 8:30 and 10:00 ET data releases, and track your own results by hour.",
            ["#tradingsessions", "#daytrading", "#futurestrading"], "Trading sessions explained: when markets move"))

carousel("c309_car_premarket_routine", {}, [
    {"type": "cover", "kicker": "Trading routine", "title": "A 15-minute pre-market routine.", "text": "Most bad trades are decided **before** the open."},
    {"type": "points", "title": "1. The calendar (2 min)", "points": [
        {"b": "News times today", "t": "Data releases, central bank speakers, earnings.", "color": "gold"},
        {"b": "Decide in advance", "t": "Flat before big releases, or smaller size.", "color": "blue"}]},
    {"type": "points", "title": "2. The levels (5 min)", "points": [
        {"b": "Yesterday's high, low and close", "t": "The reference points most traders watch.", "color": "mint"},
        {"b": "Overnight high and low", "t": "Where the market went while you slept.", "color": "blue"}]},
    {"type": "points", "title": "3. The plan (5 min)", "points": [
        {"b": "Two scenarios", "t": "\"If price holds above X, I look for longs. If it loses Y, shorts.\"", "color": "mint"},
        {"b": "Which setups you'll take", "t": "Write them down. Everything else is a pass.", "color": "gold"}]},
    {"type": "points", "title": "4. The limits (3 min)", "points": [
        {"b": "Max loss for the day", "t": "Hit it and you're done. No exceptions.", "color": "coral"},
        {"b": "Max number of trades", "t": "Stops overtrading before it starts.", "color": "coral"},
        {"b": "Risk per trade", "t": "In dollars, decided now, not in the moment.", "color": "blue"}]},
    {"type": "end", "title": "Plan the trade before the market tempts you.", "text": "Calendar, levels, plan, limits. Fifteen minutes that save the rest of the day."},
], post_car("A 15-minute pre-market routine", "1. Calendar: news times today. 2. Levels: yesterday's high, low and close, overnight high and low. 3. Plan: two scenarios and the setups you'll take. 4. Limits: max daily loss, max number of trades, dollar risk per trade. Decided before the open, not in the moment.",
            ["#tradingroutine", "#tradingpsychology", "#daytrading"], "Pre-market routine checklist for day traders"))

carousel("c310_car_revenge_trading", {}, [
    {"type": "cover", "kicker": "Trading psychology", "title": "Revenge trading: how one loss becomes five.", "text": "It's not a strategy problem. It's a **rules** problem."},
    {"type": "points", "title": "What it looks like", "points": [
        {"b": "Re-entering right after a stop", "t": "Same direction, no new setup.", "color": "coral"},
        {"b": "Doubling the size", "t": "\"I just need to get it back.\"", "color": "coral"},
        {"b": "Moving or removing the stop", "t": "Because another loss feels unbearable.", "color": "coral"}]},
    {"type": "points", "title": "Why it happens", "points": [
        {"b": "Losses feel bigger than wins", "t": "A loss hurts more than an equal win feels good.", "color": "gold"},
        {"b": "The account becomes the goal", "t": "You stop trading setups and start trading your P&L.", "color": "gold"}]},
    {"type": "rows", "title": "Rules that stop it", "head": ["", "", ""], "rows": [
        {"cells": ["2 losses in a row", "", "10-minute break"], "hl": True}, {"cells": ["Daily loss limit hit", "", "Done for the day"], "good": True, "hl": True},
        {"cells": ["Size after a loss", "", "Same or smaller"]}, {"cells": ["New trade", "", "Only from your plan"]}]},
    {"type": "points", "title": "Make the rules automatic", "points": [
        {"b": "Set the limit in your platform", "t": "Many platforms and prop firms can lock you out at a loss.", "color": "blue"},
        {"b": "Write the reason before every entry", "t": "If you can't, it's probably revenge.", "color": "mint"},
        {"b": "Review the bad days", "t": "Count how much came after the first loss.", "color": "gold"}]},
    {"type": "end", "title": "The first loss is a cost. The next five are a choice.", "text": "Decide your stop-trading rules before the open, and make them hard to break."},
], post_car("Revenge trading: how one loss becomes five", "Re-entering right after a stop, doubling the size, moving the stop: that's revenge trading. Rules that stop it: a break after 2 losses in a row, a daily loss limit that ends the day, same or smaller size after a loss, and new trades only from your plan.",
            ["#tradingpsychology", "#revengetrading", "#riskmanagement"], "Revenge trading: rules to stop it"))


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
