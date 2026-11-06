"""Reels v3 ("scroll-stoppers"), from 6 Nov 2026: built to stop the scroll and get a comment.
- The hook is a stake (money, a loss, a mistake) in at most 7 words, on screen and spoken from frame one, with a flash.
- No presenter, chart as big as possible, 3-word captions, the disclaimer tag only on the last scene (it stays in the caption).
- A pattern interrupt every 2-3 seconds: a new element on the chart or a big number popping in ("pops").
- 12-20 seconds; the last line runs back into the hook, so the video loops.
- It ends on a comment CTA: a keyword to get a free resource by DM, or a yes/no question.
Every number is computed from the chart and asserted here, as in edu.py."""
from charts import path
from edu import EDU_TAG, HANDLE, SITE, export, pick, post_edu
import strategy_carousels as SC

V = []
TD_GUIDE = "/learn/prop-firm-trailing-drawdown-explained/"

# ------------------------------------------------------------------ 1. Intraday trailing drawdown: break-even day, $1,400 of room gone

START, DD = 50000, 2000


def _eq(seed):
    wp = [(4, 50000), (8, 50620), (11, 50430), (16, 51400), (19, 50980), (22, 51120), (27, 50180), (30, 50000)]
    c = path([(0, 50000)] + wp, seed=seed, noise=45, wick=40, force={16: {"h": 51400}})
    for i in list(range(0, 4)) + [31, 32]:
        if i < len(c):
            c[i] = {"o": 50000.0, "h": 50000.0, "l": 50000.0, "c": 50000.0}
    while len(c) < 33:
        c.append({"o": 50000.0, "h": 50000.0, "l": 50000.0, "c": 50000.0})
    for b in c:
        b.pop("v", None)  # an account balance has no volume
    c[4]["o"] = 50000.0
    ok = max(b["h"] for b in c) == 51400 and c[30]["c"] == 50000 and min(b["l"] for b in c) > 49800 and all(c[i]["h"] < 51400 for i in range(16))
    return dict(c=c, ok=ok)


EQ = pick(_eq, lambda d: d["ok"], seeds=range(1, 300))
eq = EQ["c"]
peak = [max(b["h"] for b in eq[:i + 1]) for i in range(len(eq))]
floor = [round(p - DD) for p in peak]
room_end = round(eq[-1]["c"] - floor[-1]); gone = DD - room_end; open_max = peak[-1] - START
assert (open_max, floor[-1], room_end, gone) == (1400, 49400, 600, 1400) and eq[-1]["c"] == START
ch1 = {"candles": eq, "lines": [{"id": "floor", "label": "Loss limit", "color": "coral", "values": floor}], "bands": [], "symbol": "50K ACCOUNT", "tf": "5m"}
V.append({"id": "v221_edu_trailing_drawdown", "style": "v3", "tag": EDU_TAG, "site_path": TD_GUIDE, "charts": {"a": ch1}, "hook": "stake", "scenes": [
    {"type": "chart", "chart": "a", "headline": "Break-even day. Still lost $1,400.", "big": True, "reveal": [9, 13], "grow": 0.95, "punch": True,
     "say": "Break-even day. And you still lost fourteen hundred dollars."},
    {"type": "chart", "chart": "a", "headline": "The limit chases your high.", "big": True, "reveal": [13, 17], "add": ["floor"], "addAt": 0.0, "cont": True,
     "marks": [{"bar": 16, "dir": "down", "text": "Peak", "color": "mint", "at": 0.6}],
     "pops": [{"text": f"+${open_max:,} open", "color": "mint", "at": 0.55, "y": 0.6}],
     "say": "With an intraday trailing limit, it follows your highest balance, open profit included."},
    {"type": "chart", "chart": "a", "headline": "Then it never comes down.", "big": True, "reveal": [17, 33], "show": ["floor"], "cont": True,
     "levels": [{"price": floor[-1], "from": 16, "label": f"Limit {floor[-1]:,}", "color": "coral", "below": True, "labelPos": "right", "at": 0.3}],
     "pops": [{"text": f"Room: ${room_end:,}", "color": "coral", "at": 0.7, "y": 0.9}],
     "say": "The trade goes back to zero. The limit doesn't. Two thousand of room is now six hundred."},
    {"type": "comment", "title": "Want the guide to every limit type?", "keyword": "RULES", "sub": "Comment it. I'll DM you the free guide.",
     "say": "Comment rules, and I'll send you my free guide to every limit type."},
], "post": post_edu("Break-even day, still lost $1,400", f"On an intraday trailing drawdown the loss limit follows your highest balance, open profit included. A 50K account with a $2,000 limit runs to +${open_max:,} open: the limit rises to ${floor[-1]:,}. The trade comes back to break-even and the limit stays there: ${room_end:,} of room left instead of $2,000. Some firms trail end-of-day instead, and most limits lock at some point: check your firm's rules. Comment RULES for the free guide.",
                    ["#propfirm", "#futurestrading", "#trailingdrawdown", "#fundedtrader"], "Intraday trailing drawdown explained", TD_GUIDE)})

# ------------------------------------------------------------------ 2. Slippage through a stop on 08:30 data (same computed chart as c318)

SL = SC.SL
s_entry, s_stop, s_fill = SL["c"][14]["c"], 5000.0, SL["c"][17]["o"]
assert (s_entry - s_stop, s_stop - s_fill, s_entry - s_fill) == (4, 3, 7) and all(b["l"] > s_stop for b in SL["c"][15:17])
ch2 = {**export(SL["c"]), "tf": "5m", "time": {"start": "07:05", "step": 5}}
L_long = {"price": s_entry, "from": 14, "label": "Long", "color": "blue", "labelPos": "right"}
L_stop = {"price": s_stop, "from": 6, "label": "Stop", "color": "coral", "below": True}
L_fill = {"price": s_fill, "from": 17, "label": "Filled here", "color": "orange", "below": True, "labelPos": "right"}
V.append({"id": "v222_edu_news_slippage", "style": "v3", "tag": EDU_TAG, "site_path": "/tools/position-size-calculator/", "charts": {"a": ch2}, "hook": "stake", "scenes": [
    {"type": "chart", "chart": "a", "headline": "Stop: 4 points. Loss: 7.", "big": True, "reveal": [10, 15], "grow": 0.95, "punch": True,
     "levels": [{**L_long, "at": 0.0}, {**L_stop, "at": 0.0}],
     "say": "Your stop was four points away. You lost seven."},
    {"type": "chart", "chart": "a", "headline": "08:30. The data hits.", "big": True, "reveal": [15, 18], "cont": True, "levels": [L_long, L_stop],
     "marks": [{"bar": 17, "dir": "down", "text": "08:30", "color": "coral", "at": 0.5}],
     "pops": [{"text": f"{s_entry:,.0f} → {s_fill:,.0f}", "color": "coral", "at": 0.55, "y": 0.74}],
     "say": "Eight thirty data. Price jumps straight past your stop."},
    {"type": "chart", "chart": "a", "headline": "Your stop fills here.", "big": True, "reveal": [18, 18], "cont": True, "levels": [L_long, L_stop, {**L_fill, "at": 0.1}],
     "marks": [{"bar": 17, "dir": "down", "text": "08:30", "color": "coral"}],
     "pops": [{"text": f"−{s_stop - s_fill:.0f} pts slippage", "color": "gold", "at": 0.3, "y": 0.74}],
     "say": "A triggered stop is a market order. It fills at the next price."},
    {"type": "comment", "title": "Would you hold through 8:30?", "options": ["YES", "NO"], "sub": "Comment below. Send it to the friend who does.",
     "say": "Would you hold through eight thirty? Yes or no, comment below."},
], "post": post_edu("Stop 4 points away, lost 7", f"Long at {s_entry:,.2f}, stop at {s_stop:,.2f}: 4 points of planned risk. At 08:30 economic data came out and the next trade printed at {s_fill:,.2f}. A stop becomes a market order when triggered, so it filled there: 3 points of slippage, 7 points lost. Would you hold a trade through 8:30 data? Yes or no in the comments.",
                    ["#slippage", "#futurestrading", "#stoploss", "#daytrading"], "Slippage on a stop loss explained", "/tools/position-size-calculator/")})
