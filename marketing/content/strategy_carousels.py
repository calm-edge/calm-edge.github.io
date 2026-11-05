"""Carousels v2 (from 2 Nov 2026): one idea per slide, step by step on a TradingView-style chart.
Slide pattern: a hook cover with the chart, then "Step 1..4" slides where each slide adds ONE new element to the same
chart (a level, a zone, an arrow) with a title of a few words and one short caption, then what can go wrong, then the
takeaway. Every number comes from the computed charts in strategies.py (asserted there) or is computed here.
Ids: c3NN_car_<topic> (c311 onwards)."""
from charts import path, sma, closes, atr
from edu import EDU_TAG, HANDLE, SITE, export, pick
from carousels import post_car
import strategies as S

C = []
TALL = 700  # chart height on step slides


def carousel(cid, charts, slides, post):
    if not charts:
        post["instagram"] = post["instagram"].replace("Educational example on an illustrative chart.", "Educational content.")
    C.append({"id": cid, "kind": "carousel", "lesson": None, "tag": EDU_TAG if charts else "Education, not financial advice", "handle": HANDLE,
              "site_path": post["pinterest"]["link"].replace(SITE, ""), "charts": charts, "slides": slides, "post": post})


def st(bars, levels=(), zones=(), marks=(), **kw):
    # no last-price line on teaching slides: only the elements the slide talks about
    return {"bars": bars, "show": [], "levels": list(levels), "zones": list(zones), "marks": list(marks), "lastPrice": False, **kw}


def step(n, of, title, state, text, chart="a", h=TALL):
    return {"type": "chart", "kicker": f"Step {n} of {of}", "title": title, "chart": chart, "chartH": h, "state": state, "text": text}


# ================================================================== Gap fill
G = S.G; pre = G["pre"]
first15_hi = max(b["h"] for b in G["c"][pre:pre + 3])
L_prior = {"price": G["prior"], "label": "Yesterday's close", "color": "gold"}
L_low15 = {"price": G["ib_lo"], "label": "First 15 min low", "color": "blue", "from": pre, "below": True, "labelAt": 3}
L_stop = {"price": G["hod"], "label": "Stop: day's high", "color": "coral", "from": G["trig"], "labelPos": "right"}
Z_15 = {"from": pre, "to": pre + 2, "lo": G["ib_lo"], "hi": first15_hi, "color": "blue"}
M_gap = {"bar": pre, "dir": "up", "text": "Gap up", "color": "mint"}
M_trig = {"bar": G["trig"], "dir": "up", "text": "Close below", "color": "coral"}  # arrow under the candle: the stop label sits above
M_fill = {"bar": G["fill"], "dir": "up", "text": "Gap filled", "color": "gold"}
gap_pct = (G["c"][pre]["o"] / G["prior"] - 1) * 100
carousel("c311_car_gap_fill", S.gch, [
    {"type": "cover", "kicker": "Strategy · 4 steps", "title": "Gap up at the open. Fade it or follow it?", "chart": "a", "chartH": 640,
     "state": st(pre + 4, [L_prior], marks=[M_gap])},
    step(1, 4, "Mark yesterday's close", st(pre + 1, [L_prior], marks=[M_gap]),
         f"Today opened **{gap_pct:.1f}% higher**. Yesterday's close is where the gap would **fill**."),
    step(2, 4, "Let 15 minutes trade", st(pre + 3, [L_prior, L_low15], [Z_15]),
         "Don't trade the open. Mark the **low** of the first three 5-minute candles."),
    step(3, 4, "Enter on a close below it", st(G["trig"] + 1, [L_prior, {**L_low15, "label": ""}, L_stop], marks=[M_trig]),
         f"The open failed. Entry **{G['entry']:.2f}**, stop above the day's high **{G['hod']:.2f}**."),
    step(4, 4, "Target: yesterday's close", st(G["fill"] + 2, [L_prior, L_stop], marks=[M_trig, M_fill]),
         f"Risk **{G['risk']:.2f}** to make **{G['reward']:.2f}**. Here the gap filled."),
    {"type": "points", "title": "Skip it when…", "points": [
        {"b": "Big news caused the gap", "t": "Earnings or major data can keep the move going all day.", "color": "coral"},
        {"b": "The open keeps making highs", "t": "No failure, no trade.", "color": "gold"},
        {"b": "The fill is closer than the stop", "t": "Reward smaller than risk: pass.", "color": "blue"}]},
    {"type": "end", "title": "Let the open fail first.", "text": "A gap is a reason to watch, not a reason to fade. **Trade the failure, target the close.**"},
], post_car("Gap fill strategy in 4 steps", f"Gap fill in 4 steps: 1) mark yesterday's close, 2) let the first 15 minutes trade, 3) enter on a close below their low with a stop above the day's high, 4) target yesterday's close. Example: {gap_pct:.1f}% gap, entry {G['entry']:.2f}, stop {G['hod']:.2f}, target {G['prior']:.2f}. Skip it when big news caused the gap.",
            ["#gapfill", "#daytradingstrategy", "#gaptrading"], "Gap fill trading strategy in 4 steps"))

# ================================================================== Inside bar
IB, IM, IT = S.IB, S.IM, S.IT
mo, ib = IB["mo"], IB["ib"]
Z_mother = {"from": IM, "to": IM, "lo": mo["l"], "hi": mo["h"], "color": "blue"}
Z_inside = {"from": IM + 1, "to": IM + 1, "lo": ib["l"], "hi": ib["h"], "color": "gold"}
M_mo = {"bar": IM, "dir": "down", "text": "Mother bar", "color": "blue"}
M_ib = {"bar": IM + 1, "dir": "up", "text": "Inside bar", "color": "gold"}
L_buy = {"price": IB["entry"], "label": "Buy stop", "color": "mint", "from": IM + 1, "labelPos": "right"}
L_ibstop = {"price": IB["stop"], "label": "Stop", "color": "coral", "from": IM + 1, "below": True, "labelPos": "right"}
L_tgt = {"price": IB["target"], "label": "Target 2R", "color": "mint", "from": IM + 1, "labelPos": "right"}
zoom = [IM - 9, IM + 4]
carousel("c312_car_inside_bar", S.ich, [
    {"type": "cover", "kicker": "Strategy · 4 steps", "title": "The candle with the tightest stop.", "chart": "a", "chartH": 620,
     "state": st(IM + 2, marks=[M_mo, M_ib], view=zoom)},
    step(1, 4, "Spot the inside bar", st(IM + 2, zones=[Z_mother, Z_inside], marks=[M_mo, M_ib], view=zoom),
         "**Lower high and higher low** than the bar before it. The market is pausing."),
    step(2, 4, "Buy stop just above it", st(IM + 2, [L_buy], marks=[M_ib], view=zoom),
         f"You only get in if price breaks out: **{IB['entry']:.2f}**. No breakout, no trade."),
    step(3, 4, "Stop just below it", st(IM + 2, [L_buy, L_ibstop], marks=[M_ib], view=zoom),
         f"Risk: **{IB['risk']:.2f}** points. A small bar means a small risk."),
    step(4, 4, "Target: 2× the risk", st(IT + 1, [L_buy, L_ibstop, L_tgt], marks=[M_ib]),
         f"Target **{IB['target']:.2f}**. Here the break went up and the target was hit."),
    {"type": "points", "title": "Where it goes wrong", "points": [
        {"b": "Against the trend", "t": "Inside bars breaking against the trend fail more often.", "color": "coral"},
        {"b": "In a choppy range", "t": "Price breaks one side, then the other.", "color": "coral"},
        {"b": "A huge mother bar", "t": "The pause can last for days.", "color": "gold"}]},
    {"type": "end", "title": "Small bar. Small risk. Clear trigger.", "text": "Trade it **with the trend**, stop on the other side, and let the break decide."},
], post_car("Inside bar breakout in 4 steps", f"Inside bar breakout in 4 steps: 1) find a candle with a lower high and a higher low than the one before, 2) buy stop just above it, 3) stop just below it, 4) target 2× the risk. Example: entry {IB['entry']:.2f}, stop {IB['stop']:.2f}, target {IB['target']:.2f}. Best with the trend.",
            ["#insidebar", "#priceaction", "#swingtrading"], "Inside bar breakout strategy in 4 steps"))

# ================================================================== Fibonacci pullback
FB = S.FB
F50 = {"price": FB["lv"][0.5], "label": "50%", "color": "gold", "from": FB["b"], "labelAt": 1}
F62 = {"price": FB["lv"][0.618], "label": "61.8%", "color": "gold", "from": FB["b"], "below": True, "labelAt": 1}
FZ = {"from": FB["b"], "to": len(FB["c"]) - 1, "lo": FB["lv"][0.618], "hi": FB["lv"][0.5], "color": "gold"}
MA = {"bar": FB["a"], "dir": "up", "text": "A", "color": "blue"}
MB = {"bar": FB["b"], "dir": "down", "text": "B", "color": "blue"}
F_stop = {"price": FB["stop"], "label": "Stop", "color": "coral", "from": FB["trig"], "below": True, "labelPos": "right"}
F_tgt = {"price": FB["B"], "label": "Target: B", "color": "mint", "from": FB["trig"], "labelPos": "right"}
carousel("c313_car_fib_pullback", S.fch, [
    {"type": "cover", "kicker": "Strategy · 4 steps", "title": "Where do pullbacks usually stop?", "chart": "a", "chartH": 640,
     "state": st(FB["low_bar"] + 2, [F50, F62], [FZ])},
    step(1, 4, "Find the move: A to B", st(FB["b"] + 1, marks=[MA, MB]),
         f"A = where the move started (**{FB['A']:.2f}**). B = where it ended (**{FB['B']:.2f}**)."),
    step(2, 4, "Draw 50% and 61.8%", st(FB["b"] + 3, [F50, F62], [FZ], [MA, MB]),
         f"How much of the move a pullback gives back: **{FB['lv'][0.5]:.2f}** and **{FB['lv'][0.618]:.2f}**."),
    step(3, 4, "Wait for a reaction there", st(FB["trig"] + 1, [F50, F62], [FZ], [{"bar": FB["low_bar"], "dir": "up", "text": "Low in zone", "color": "gold"}, {"bar": FB["trig"], "dir": "down", "text": "Entry", "color": "mint"}]),
         f"The level is not the signal. Entry **{FB['entry']:.2f}** on the first strong close."),
    step(4, 4, "Stop below, target the old high", st(FB["t_hit"] + 2, [F_stop, F_tgt], [FZ]),
         f"Risk **{FB['risk']:.2f}**, reward to B **{FB['reward']:.2f}**: about **{FB['reward'] / FB['risk']:.1f}R**."),
    {"type": "points", "title": "Common mistakes", "points": [
        {"b": "Choosing A and B after the fact", "t": "Use clear swing points, the same way every time.", "color": "coral"},
        {"b": "Buying the line blindly", "t": "No reaction, no trade. Levels break.", "color": "gold"},
        {"b": "Using it against the trend", "t": "It's for joining a trend, not catching tops.", "color": "blue"}]},
    {"type": "end", "title": "Zone first. Reaction second.", "text": "Fibonacci shows **where** to look. The candle that reacts there tells you **when**."},
], post_car("Fibonacci pullback in 4 steps", f"Fibonacci pullback in 4 steps: 1) find the move from A to B, 2) draw 50% and 61.8% of it, 3) wait for a reaction in that zone, 4) stop below the low, target the old high. Example: entry {FB['entry']:.2f}, stop {FB['stop']:.2f}, target {FB['B']:.2f} (about {FB['reward'] / FB['risk']:.1f}R).",
            ["#fibonacci", "#pullback", "#daytradingstrategy"], "Fibonacci pullback strategy in 4 steps"))

# ================================================================== Range trading
RG = S.RG
assert all(abs(RG["c"][i]["h"] - 103.0) < 1e-9 for i in (4, 13, 23)) and all(abs(RG["c"][i]["l"] - 100.0) < 1e-9 for i in (8, 18, 30))
R_hi = {"price": 103.0, "label": "Range high", "color": "coral", "labelPos": "right"}
R_lo = {"price": 100.0, "label": "Range low", "color": "mint", "below": True, "labelAt": 19.5}
touch = [{"bar": i, "dir": "down", "color": "coral"} for i in (4, 13, 23)] + [{"bar": i, "dir": "up", "color": "mint"} for i in (8, 18, 30)]
Z_buy = {"from": 0, "to": 30, "lo": 100.0, "hi": 100.45, "color": "mint", "label": "Buy zone"}
Z_sell = {"from": 0, "to": 30, "lo": 102.55, "hi": 103.0, "color": "coral", "label": "Sell zone"}
carousel("c314_car_range_trading", S.rch, [
    {"type": "cover", "kicker": "Strategy · 4 steps", "title": "Price bounced here 6 times. Here's the plan.", "chart": "a", "chartH": 640,
     "state": st(31, [{**R_hi, "label": ""}, {**R_lo, "label": ""}], marks=touch)},  # narrow cover chart: lines only
    step(1, 4, "Confirm it's a range", st(31, [R_hi, R_lo], marks=touch),
         "At least **2 touches per side** and flat highs and lows. Here: **3 and 3**."),
    step(2, 4, "Trade only the edges", st(31, zones=[Z_sell, Z_buy]),
         "Buy rejections near the low, sell rejections near the high. **The middle has no edge.**"),
    step(3, 4, "Stop just outside", st(31, [{**R_hi, "label": "Short stop above"}, {**R_lo, "label": "Long stop below"}]),
         "If price **closes outside** the range, the idea is wrong. Get out."),
    step(4, 4, "Every range ends", st(len(RG["c"]), [R_hi, R_lo], marks=[{"bar": RG["brk"], "dir": "up", "text": "Close outside", "color": "mint"}]),
         "After 6 touches, a close above the high and price never comes back. **The stop saves you.**"),
    {"type": "points", "title": "3 rules", "points": [
        {"b": "No stop, no range trade", "t": "Without one, a breakout becomes a big loss.", "color": "coral"},
        {"b": "Skip the middle", "t": "No edge and no clear stop there.", "color": "gold"},
        {"b": "A close outside? Switch", "t": "Stop fading. Watch the breakout and the retest.", "color": "blue"}]},
    {"type": "end", "title": "Fade the edges. Respect the break.", "text": "Ranges pay the patient trader **until they don't**."},
], post_car("How to trade a range in 4 steps", "Range trading in 4 steps: 1) confirm it's a range (2+ touches per side, flat highs and lows), 2) trade only the edges, 3) stop just outside, 4) when a candle closes outside, the range is over. The stop is what saves you when it breaks.",
            ["#rangetrading", "#supportandresistance", "#priceaction"], "Range trading strategy in 4 steps"))

# ================================================================== Order types (on a chart)


def _orders(seed):
    c = path([(0, 100.4), (6, 100.1), (10, 100.25), (14, 99.55), (17, 99.75), (21, 100.2), (25, 100.8), (30, 101.1)], seed=seed, noise=0.07, wick=0.07)
    now = 9
    lim = next((i for i in range(now + 1, len(c)) if c[i]["l"] <= 99.5), None)
    stp = next((i for i in range(now + 1, len(c)) if c[i]["h"] >= 100.5), None)
    ok = (lim is not None and stp is not None and lim < stp and all(99.5 < b["l"] and b["h"] < 100.5 for b in c[1:now + 1])
          and c[0]["h"] < 100.5 and 99.9 <= c[now]["c"] <= 100.25 and min(b["l"] for b in c) > 99.3)
    return dict(c=c, now=now, lim=lim, stp=stp, ok=ok)


OT = pick(_orders, lambda d: d["ok"], seeds=range(1, 400))
och = {"a": {**export(OT["c"]), "tf": "5m"}}
now = OT["now"]; px = OT["c"][now]["c"]
L_lim = {"price": 99.5, "label": "Buy limit 99.50", "color": "blue", "from": now, "below": True, "labelPos": "right"}
L_stp = {"price": 100.5, "label": "Buy stop 100.50", "color": "orange", "from": now, "labelPos": "right"}
carousel("c315_car_order_types", och, [
    {"type": "cover", "kicker": "Trading basics", "title": "3 buy orders. Where does each one fill?", "chart": "a", "chartH": 640,
     "state": st(now + 1, [L_lim, L_stp], marks=[{"bar": now, "dir": "up", "text": "Price now", "color": "ink"}])},
    {"type": "chart", "kicker": "Order 1", "title": "Market order: fills now", "chart": "a", "chartH": TALL,
     "state": st(now + 1, marks=[{"bar": now, "dir": "up", "text": f"Filled ~{px:.2f}", "color": "ink"}]),
     "text": "Fills **immediately** at the best price available. Fast, but the price is **not guaranteed**."},
    {"type": "chart", "kicker": "Order 2", "title": "Buy limit: below the price", "chart": "a", "chartH": TALL,
     "state": st(OT["lim"] + 1, [L_lim], marks=[{"bar": OT["lim"], "dir": "down", "text": "Filled 99.50", "color": "blue"}]),
     "text": "You wait for a **better price**. Here it came. If it never comes, **no fill**."},
    {"type": "chart", "kicker": "Order 3", "title": "Buy stop: above the price", "chart": "a", "chartH": TALL,
     "state": st(OT["stp"] + 1, [L_stp], marks=[{"bar": OT["stp"], "dir": "up", "text": "Triggered 100.50", "color": "orange"}]),
     "text": "Used for **breakouts** and **stop losses**. It becomes a market order, so it can **slip**."},
    {"type": "points", "title": "And the stop-limit?", "points": [
        {"b": "A stop that becomes a limit order", "t": "You cap the worst price you accept.", "color": "blue"},
        {"b": "In a fast move it can be skipped", "t": "Price jumps past your limit: no fill.", "color": "coral"},
        {"b": "So don't use it as a stop loss", "t": "That's exactly when you need to be out.", "color": "gold"}]},
    {"type": "rows", "title": "Quick guide", "head": ["You want…", "", "Use"], "rows": [
        {"cells": ["In right now", "", "Market"]}, {"cells": ["A better price", "", "Limit"]},
        {"cells": ["Out if wrong", "", "Stop"], "good": True, "hl": True}, {"cells": ["A capped breakout entry", "", "Stop-limit"]}]},
    {"type": "end", "title": "Your stop loss should be a stop order.", "text": "Limit to get a better price. Stop to get **out, no matter what**."},
], post_car("Market, limit and stop orders on one chart", "Market order: fills now, price not guaranteed. Buy limit: below the price, fills only if price comes to you. Buy stop: above the price, for breakouts and stop losses, can slip. Stop-limit: can be skipped in a fast move, so don't use it as your protective stop.",
            ["#ordertypes", "#tradingbasics", "#stoploss"], "Market, limit, stop and stop-limit orders explained on a chart"))

# ================================================================== Futures point value (on a chart)
SPEC, TICK = S.SPEC, S.TICK


def _move(seed):
    c = path([(0, 5000.0), (5, 5003.0), (8, 5001.5), (14, 5007.5), (17, 5006.0), (22, 5010.0)], seed=seed, noise=0.6, wick=0.6)
    ok = c[0]["c"] == 5000.0 and c[-1]["c"] == 5010.0 and min(b["l"] for b in c) > 4998.5 and max(b["h"] for b in c) < 5011.5
    return dict(c=c, ok=ok)


MV = pick(_move, lambda d: d["ok"])
mch = {"a": {**export(MV["c"]), "tf": "5m"}}
move = MV["c"][-1]["c"] - MV["c"][0]["c"]
assert move == 10
mv_state = st(len(MV["c"]), [{"price": 5000.0, "label": "Start 5,000", "color": "blue", "below": True, "labelAt": 6},
                             {"price": 5010.0, "label": "+10 points", "color": "mint", "labelAt": 4}])
carousel("c316_car_futures_math", mch, [
    {"type": "cover", "kicker": "Futures basics", "title": "10 points on this chart: $500 or $50?", "chart": "a", "chartH": 640, "state": mv_state},
    {"type": "rows", "title": f"The same {move:.0f}-point move", "head": ["Contract", "", "1 contract"], "rows": [
        {"cells": ["ES (S&P 500)", "", f"${SPEC['ES'] * move:,.0f}"]}, {"cells": ["MES (micro)", "", f"${SPEC['MES'] * move:,.0f}"], "good": True, "hl": True},
        {"cells": ["NQ (Nasdaq 100)", "", f"${SPEC['NQ'] * move:,.0f}"]}, {"cells": ["MNQ (micro)", "", f"${SPEC['MNQ'] * move:,.0f}"], "good": True, "hl": True}],
     "text": "Same chart, same move. **The contract decides the money.**"},
    {"type": "rows", "title": "Dollars per point", "head": ["Contract", "Per point", "Per tick"], "rows": [
        {"cells": ["ES", f"${SPEC['ES']}", f"${SPEC['ES'] * TICK:.2f}"]}, {"cells": ["MES", f"${SPEC['MES']}", f"${SPEC['MES'] * TICK:.2f}"], "good": True},
        {"cells": ["NQ", f"${SPEC['NQ']}", f"${SPEC['NQ'] * TICK:.2f}"]}, {"cells": ["MNQ", f"${SPEC['MNQ']}", f"${SPEC['MNQ'] * TICK:.2f}"], "good": True}],
     "text": "One tick = **0.25** points. Micros are **one tenth** of the full contract."},
    {"type": "formula", "title": "Your risk, in dollars", "formula": "Stop × $ per point × contracts",
     "small": f"8-point stop on 3 MES = 8 × ${SPEC['MES']} × 3 = ${8 * SPEC['MES'] * 3}"},
    {"type": "points", "title": "Why it matters", "points": [
        {"b": "Size from the stop", "t": "Decide the dollars first, then the contracts.", "color": "mint"},
        {"b": "Start with micros", "t": "Same market, a tenth of the risk.", "color": "blue"},
        {"b": "NQ moves more points than ES", "t": "The same stop in points is not the same risk.", "color": "coral"}]},
    {"type": "end", "title": "Know the point value before you click.", "text": "Points × $ per point × contracts = **the money on the line**."},
], post_car("Futures point values: ES, MES, NQ, MNQ", f"The same {move:.0f}-point move is ${SPEC['ES'] * move:,.0f} on one ES, ${SPEC['MES'] * move:,.0f} on one MES, ${SPEC['NQ'] * move:,.0f} on one NQ and ${SPEC['MNQ'] * move:,.0f} on one MNQ. Risk = stop in points × $ per point × contracts. Contract specs from CME Group.",
            ["#futurestrading", "#es", "#nq", "#microfutures"], "Futures point values explained: ES, MES, NQ, MNQ"))

# ================================================================== 20-day breakout (trend following)


def _don(seed):
    wp = [(0, 100), (6, 103), (10, 100.8), (16, 103.4), (21, 101.2), (26, 103.2), (29, 102.6), (31, 104.4), (37, 108), (40, 106.8), (47, 111.5), (50, 110.3), (54, 113.4), (58, 110.5), (61, 109)]
    c = path(wp, seed=seed, noise=0.45, wick=0.4)
    hi20 = lambda i: max(b["h"] for b in c[i - 20:i]); lo10 = lambda i: min(b["l"] for b in c[i - 10:i])
    brk = next((i for i in range(25, len(c)) if c[i]["c"] > hi20(i)), None)
    if brk is None:
        return dict(ok=False)
    stop = lo10(brk); ex = next((i for i in range(brk + 1, len(c)) if c[i]["c"] < lo10(i)), None)
    if ex is None:
        return dict(ok=False)
    stopped = any(b["l"] <= stop for b in c[brk + 1:ex])
    R = (c[ex]["c"] - c[brk]["c"]) / (c[brk]["c"] - stop)
    return dict(c=c, brk=brk, ex=ex, hi=hi20(brk), stop=stop, trail=lo10(ex), entry=c[brk]["c"], exit=c[ex]["c"], R=R,
                ok=29 <= brk <= 32 and 55 <= ex <= 61 and not stopped and R >= 1.8 and all(c[i]["c"] <= hi20(i) for i in range(25, brk)))


DN = pick(_don, lambda d: d["ok"], seeds=range(1, 400))
dk, dx = DN["brk"], DN["ex"]; d_risk = DN["entry"] - DN["stop"]
assert DN["entry"] > DN["hi"] and DN["exit"] < DN["trail"] and abs(DN["R"] - (DN["exit"] - DN["entry"]) / d_risk) < 1e-9
dch = {"a": {**export(DN["c"]), "tf": "1D"}}
D_hi = {"price": DN["hi"], "from": dk - 20, "to": dk, "label": "20-day high", "color": "blue", "labelAt": 1}
D_stop = {"price": DN["stop"], "from": dk - 10, "label": "Stop: 10-day low", "color": "coral", "below": True, "labelPos": "right"}
D_trail = {"price": DN["trail"], "from": dx - 10, "to": dx, "label": "10-day low", "color": "gold", "below": True, "labelAt": 1}
M_dbrk = {"bar": dk, "dir": "up", "text": "Close above", "color": "mint"}
M_dex = {"bar": dx, "dir": "down", "text": "Exit", "color": "gold"}
carousel("c317_car_20day_breakout", dch, [
    {"type": "cover", "kicker": "Strategy · 4 steps", "title": "Buy new 20-day highs? A trend system.", "chart": "a", "chartH": 640,
     "state": st(dk + 4, [{**D_hi, "label": ""}], marks=[M_dbrk])},
    step(1, 4, "Mark the 20-day high", st(dk, [D_hi]),
         f"The highest high of the last **20 days**: **{DN['hi']:.2f}**."),
    step(2, 4, "Buy a close above it", st(dk + 1, [D_hi], marks=[M_dbrk]),
         f"Entry on the close: **{DN['entry']:.2f}**. New highs are what trends are made of."),
    step(3, 4, "Stop at the 10-day low", st(dk + 1, [D_hi, D_stop], marks=[M_dbrk]),
         f"The lowest low of the last 10 days: **{DN['stop']:.2f}**. Risk: **{d_risk:.2f}**."),
    step(4, 4, "Exit below the 10-day low", st(dx + 1, [D_stop, D_trail], marks=[M_dbrk, M_dex]),
         f"The exit follows the trend up. Out at **{DN['exit']:.2f}**: about **{DN['R']:.1f}R**."),
    {"type": "points", "title": "Where it goes wrong", "points": [
        {"b": "Sideways markets", "t": "Breakouts fail again and again: many small losses.", "color": "coral"},
        {"b": "Giving profit back", "t": "The 10-day exit waits for the turn, so it gives some back.", "color": "gold"},
        {"b": "A few trades pay for many", "t": "Most of the profit tends to come from a handful of big trends.", "color": "blue"}]},
    {"type": "end", "title": "Lose small. Let the trend pay.", "text": "A breakout system lives on **a few big trends**. Skipping trades after a losing streak is how most people break it."},
], post_car("20-day breakout system in 4 steps", f"A simple trend-following system in 4 steps: 1) mark the 20-day high, 2) buy a close above it, 3) stop at the 10-day low, 4) exit on a close below the 10-day low. Example: entry {DN['entry']:.2f}, stop {DN['stop']:.2f}, exit {DN['exit']:.2f}, about {DN['R']:.1f}R. It loses often in sideways markets; a few big trends tend to pay for the rest.",
            ["#trendfollowing", "#breakouttrading", "#swingtrading"], "20-day breakout trend following system in 4 steps"))

# ================================================================== Slippage on a stop (on a chart)


def _slip(seed):
    wp = [(0, 5001), (6, 5003.5), (10, 5002), (14, 5004.5), (16, 5004.0), (17, 4997.0), (19, 4995.5), (24, 4996.5)]
    c = path(wp, seed=seed, noise=0.6, wick=0.5, force={14: {"c": 5004.0}, 17: {"o": 4997.0, "h": 4997.75, "c": 4995.25, "l": 4994.5}})
    ok = c[14]["c"] == 5004.0 and all(b["l"] > 5000.75 for b in c[1:17]) and c[16]["c"] > 5001 and c[17]["o"] == 4997.0
    return dict(c=c, ok=ok)


SL = pick(_slip, lambda d: d["ok"])
sch = {"a": {**export(SL["c"]), "tf": "5m", "time": {"start": "07:05", "step": 5}}}
s_entry, s_stop, s_fill = SL["c"][14]["c"], 5000.0, SL["c"][17]["o"]
s_plan, s_slip = s_entry - s_stop, s_stop - s_fill; s_lost = s_entry - s_fill; s_n = 5
assert (s_plan, s_slip, s_lost) == (4, 3, 7) and SL["c"][16]["l"] > s_stop and 7 * 60 + 5 + 17 * 5 == 8 * 60 + 30  # the gap bar is the 08:30 bar
usd_plan, usd_lost = round(s_plan * SPEC["MES"] * s_n), round(s_lost * SPEC["MES"] * s_n)
assert (usd_plan, usd_lost) == (100, 175)
S_entry = {"price": s_entry, "from": 14, "label": "Long", "color": "blue", "labelPos": "right"}
S_stop = {"price": s_stop, "from": 6, "label": "Stop", "color": "coral", "below": True}
S_fill = {"price": s_fill, "from": 17, "label": "Filled here", "color": "orange", "below": True, "labelPos": "right"}
M_news = {"bar": 17, "dir": "down", "text": "08:30 data", "color": "coral"}
carousel("c318_car_slippage", sch, [
    {"type": "cover", "kicker": "Market mechanics", "title": "Stop 4 points away. Lost 7. Why?", "chart": "a", "chartH": 640,
     "state": st(18, [{**S_entry, "label": ""}, {**S_stop, "label": ""}], marks=[M_news])},
    step(1, 4, "Long, stop 4 points below", st(15, [S_entry, S_stop]),
         f"Entry **{s_entry:,.2f}**, stop **{s_stop:,.2f}**. Planned risk: **{s_plan:.0f} points**."),
    step(2, 4, "08:30: a data release", st(18, [S_entry, S_stop], marks=[M_news]),
         f"The first trade after the news is **{s_fill:,.2f}**. Price jumped straight past the stop."),
    step(3, 4, "The stop fills at the next price", st(18, [S_entry, S_stop, S_fill], marks=[M_news]),
         f"A stop becomes a **market order** when it triggers. Fill: **{s_fill:,.2f}**, **{s_slip:.0f} points** of slippage."),
    step(4, 4, f"Planned {s_plan:.0f} points, lost {s_lost:.0f}", st(len(SL["c"]), [S_entry, S_stop, S_fill], marks=[M_news]),
         f"On {s_n} MES (${SPEC['MES']} a point): **${usd_plan}** planned, **${usd_lost}** lost."),
    {"type": "points", "title": "How to limit it", "points": [
        {"b": "Know the calendar", "t": "Scheduled data like CPI or payrolls can jump the price.", "color": "coral"},
        {"b": "Trade liquid hours", "t": "Thin markets skip more prices.", "color": "gold"},
        {"b": "Size for a bad fill", "t": "Assume a stop can cost more than planned.", "color": "blue"}]},
    {"type": "end", "title": "A stop limits the loss. It can't fix the price.", "text": "Slippage is part of the cost of trading. **Plan for it before the news, not after.**"},
], post_car("Slippage: stop 4 points away, lost 7", f"Long at {s_entry:,.2f} with a stop at {s_stop:,.2f}: 4 points of planned risk. At 08:30 a data release made price jump to {s_fill:,.2f}. A stop becomes a market order when triggered, so it filled there: 3 points of slippage. On {s_n} MES that's ${usd_plan} planned and ${usd_lost} lost. Know the calendar, trade liquid hours and size for a bad fill.",
            ["#slippage", "#futurestrading", "#stoploss"], "Slippage on a stop loss explained on a chart"))

# ================================================================== FOMO: chasing a move (on a chart)


def _fomo(seed):
    wp = [(0, 100.5), (4, 100.9), (8, 100.1), (12, 100.85), (16, 100.2), (18, 100.7), (19, 101.3), (24, 104.2), (28, 102.2), (30, 102.6), (36, 105.4)]
    c = path(wp, seed=seed, noise=0.18, wick=0.16, force={4: {"h": 101.0}, 12: {"h": 100.98}, 8: {"l": 100.0}, 16: {"l": 100.02}})
    base_hi = max(b["h"] for b in c[:19]); base_lo = min(b["l"] for b in c[:19])
    brk = next((i for i in range(17, len(c)) if c[i]["c"] > base_hi), None)
    green = sum(c[i]["c"] > c[i]["o"] for i in range(20, 25))
    pb = min(range(25, 31), key=lambda i: c[i]["l"])
    ok = (base_hi == 101.0 and base_lo == 100.0 and brk == 19 and green >= 4 and base_hi < c[pb]["l"] < 102.6
          and max(b["h"] for b in c[:25]) == max(b["h"] for b in c[20:25]) and c[pb + 1]["c"] > c[pb + 1]["o"])
    return dict(c=c, ok=ok, brk=brk, pb=pb)


FO = pick(_fomo, lambda d: d["ok"], seeds=range(1, 400))
fch = {"a": {**export(FO["c"]), "tf": "15m"}}
f_brk, f_chase, f_pb = FO["c"][19]["c"], FO["c"][24]["c"], FO["pb"]
f_stop = 100.0; r_brk, r_chase = f_brk - f_stop, f_chase - f_stop; mult = r_chase / r_brk
f_re = FO["c"][f_pb + 1]["c"]; r_re = f_re - f_stop; f_dd = f_chase - FO["c"][f_pb]["l"]
assert mult > 3 and r_re < r_chase and 1 / mult < 1 / 3
Z_base = {"from": 0, "to": 18, "lo": 100.0, "hi": 101.0, "color": "blue", "label": "Base"}
F_stop = {"price": f_stop, "label": "Stop: below the base", "color": "coral", "below": True, "labelPos": "right"}
M_fbrk = {"bar": 19, "dir": "up", "text": "Breakout", "color": "mint"}
M_chase = {"bar": 24, "dir": "down", "text": "You buy here?", "color": "coral"}
M_pb = {"bar": f_pb, "dir": "up", "text": "Pullback", "color": "gold"}
carousel("c319_car_fomo_chase", fch, [
    {"type": "cover", "kicker": "Trading psychology", "title": "Price ran without you. Chase it?", "chart": "a", "chartH": 640,
     "state": st(25, zones=[{**Z_base, "label": ""}], marks=[M_chase])},
    step(1, 4, "The breakout you missed", st(20, zones=[Z_base], marks=[M_fbrk]),
         f"A close above the base at **{f_brk:.2f}**. With a stop below the base, risk was **{r_brk:.2f}**."),
    step(2, 4, "Five candles later", st(25, zones=[Z_base], marks=[M_fbrk, M_chase]),
         f"Now it's **{f_chase:.2f}**. It feels like the train is leaving."),
    step(3, 4, f"Same stop, {mult:.1f}× the risk", st(25, [F_stop], [Z_base], [M_chase]),
         f"Risk from here: **{r_chase:.2f}** vs **{r_brk:.2f}**. Same dollars at risk means **less than a third** of the size."),
    step(4, 4, "Here, a pullback came", st(f_pb + 2, [F_stop], [Z_base], [M_chase, M_pb]),
         f"A chaser sat through a **{f_dd:.2f}** drop. Entry after it: risk **{r_re:.2f}**. Not every move gives one."),
    {"type": "points", "title": "Before you chase, ask", "points": [
        {"b": "Where is my stop?", "t": "If it's far away, the trade got worse, not better.", "color": "coral"},
        {"b": "Is my size smaller?", "t": "Same dollars at risk means fewer contracts.", "color": "gold"},
        {"b": "Would I take it fresh?", "t": "If not, it's FOMO, not a setup.", "color": "blue"}]},
    {"type": "end", "title": "Missing a move costs nothing.", "text": "Chasing turns a good idea into **a bad price**. Another setup always comes."},
], post_car("FOMO: should you chase a move you missed?", f"The breakout closed at {f_brk:.2f} with a stop below the base at {f_stop:.2f}: risk {r_brk:.2f}. Five candles later price was {f_chase:.2f}: the same stop now means {r_chase:.2f} of risk, {mult:.1f}x more, so less than a third of the size for the same dollars. Before you chase, ask: where is my stop, is my size smaller, would I take this trade fresh?",
            ["#fomo", "#tradingpsychology", "#riskmanagement"], "FOMO in trading: chasing a move explained on a chart"))

# ================================================================== Three down days in an uptrend


def _tdd(seed):
    wp = [(0, 95), (15, 99), (20, 98), (35, 103), (40, 102), (52, 106), (55, 104.8), (58, 106.3), (62, 107.2), (66, 106.6), (70, 108.4)]
    c = path(wp, seed=seed, noise=0.35, wick=0.3); cl = closes(c); m = sma(cl, 50); a = atr(c)
    d3 = [i for i in range(52, 62) if cl[i] < cl[i - 1] < cl[i - 2] < cl[i - 3]]
    if not d3:
        return dict(ok=False)
    e = d3[0]; stop = round(min(b["l"] for b in c[e - 2:e + 1]) - a[e], 2)
    ex = next((i for i in range(e + 1, len(c)) if cl[i] > c[i - 1]["h"]), None)
    ok = all(cl[i] > m[i] for i in range(49, e + 1)) and ex is not None and 2 <= ex - e <= 5 and all(b["l"] > stop for b in c[e + 1:ex + 1]) and cl[ex] > cl[e]
    return dict(c=c, m=m, a=a[e], e=e, stop=stop, ex=ex, ok=ok)


TD = pick(_tdd, lambda d: d["ok"])
S0 = 45
tch = {"a": {**export(TD["c"], S0, lines=[{"id": "sma50", "label": "SMA 50", "color": "gold", "values": TD["m"]}]), "tf": "1D"}}
te, tx = TD["e"] - S0, TD["ex"] - S0
t_entry, t_exit = TD["c"][TD["e"]]["c"], TD["c"][TD["ex"]]["c"]; t_risk = t_entry - TD["stop"]; t_R = (t_exit - t_entry) / t_risk
assert t_risk > 0 and t_R > 1 and all(TD["c"][i]["c"] < TD["c"][i - 1]["c"] for i in range(TD["e"] - 2, TD["e"] + 1))
T_stop = {"price": TD["stop"], "from": te, "label": "Stop", "color": "coral", "below": True, "labelPos": "right"}
M_d3 = [{"bar": te - k, "dir": "down", "text": "" if k else "Entry", "color": "coral"} for k in (2, 1, 0)]
M_tx = {"bar": tx, "dir": "up", "text": "Exit", "color": "mint"}
SH = ["sma50"]
carousel("c320_car_three_down_days", tch, [
    {"type": "cover", "kicker": "Strategy · 4 steps", "title": "3 red days in an uptrend. Buy the dip?", "chart": "a", "chartH": 640,
     "state": st(te + 1, show=SH)},
    step(1, 4, "Trend filter: 50-day SMA", st(te - 2, show=SH),
         "Trade it only when price is above the **50-day SMA**: the trend is up."),
    step(2, 4, "Wait for 3 lower closes", st(te + 1, marks=[{**m, "text": ""} for m in M_d3], show=SH),
         f"Three closes in a row, each lower than the last. Entry on the third close: **{t_entry:.2f}**."),
    step(3, 4, "Stop: 1 ATR below the low", st(te + 1, [T_stop], marks=[M_d3[2]], show=SH),
         f"The pullback's low minus one ATR: **{TD['stop']:.2f}**. Risk: **{t_risk:.2f}**."),
    step(4, 4, "Exit on the first strong close", st(tx + 1, [T_stop], marks=[M_d3[2], M_tx], show=SH),
         f"A close above the previous day's high: **{t_exit:.2f}**, about **{t_R:.1f}R**."),
    {"type": "points", "title": "Skip it when…", "points": [
        {"b": "Price is below the 50-day", "t": "Then a dip is often just the trend going down.", "color": "coral"},
        {"b": "News caused the drop", "t": "That can be a real repricing, not a pullback.", "color": "gold"},
        {"b": "Three days turn into ten", "t": "That's exactly what the stop is for.", "color": "blue"}]},
    {"type": "end", "title": "Buy weakness only inside strength.", "text": "The trend filter does the heavy lifting. **No uptrend, no trade.**"},
], post_car("3 down days in an uptrend: a pullback strategy", f"A pullback strategy in 4 steps: 1) only when price is above the 50-day SMA, 2) wait for three lower closes in a row and enter on the third, 3) stop at the pullback's low minus one ATR, 4) exit on the first close above the previous day's high. Example: entry {t_entry:.2f}, stop {TD['stop']:.2f}, exit {t_exit:.2f}, about {t_R:.1f}R.",
            ["#pullback", "#swingtrading", "#meanreversion"], "Three down days pullback strategy in 4 steps"))
