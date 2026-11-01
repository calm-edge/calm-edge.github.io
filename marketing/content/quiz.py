"""Reel format v2 ("decide before the reveal"), built to be watched to the end:
  1. hook: the chart is already moving and a question is on screen from frame one, with 2-3 answers;
  2. countdown 3-2-1 while the camera pushes in on the decision point (ticks);
  3. reveal: the chart plays out, the right answer lights up (pop), one or two sentences explain the concept;
  no static end card: the follow call is spoken over the last chart, and the video ends on the payoff.
Charts, marks and numbers are the lesson's own (edu.py), so every claim keeps its checks."""
import edu
from edu import words

L = {v["id"]: v for v in edu.V}
FOLLOW_SAY = " Follow for tomorrow's chart."


def chart_scenes(vid):
    return [s for s in L[vid]["scenes"] if s["type"] == "chart"]


def quiz(vid, question, options, answer, decide, hook, hook_say, steps, zoom=(22, 11)):
    """steps: [(scene dict overrides, say), ...] played after the reveal; the first one carries the answer."""
    les = L[vid]
    first = chart_scenes(vid)[0]
    show = first.get("show", []) + first.get("add", [])
    head = {"type": "chart", "chart": "a", "headline": question, "big": True, "options": options}
    scenes = [
        {**head, "reveal": [hook.get("from", 6), decide], "show": show, "grow": 0.95, **{k: v for k, v in hook.items() if k != "from"}, "say": hook_say},
        {**head, "reveal": [decide, decide], "show": show, "zoom": list(zoom), "countdown": 3, "duration": 3, "sfx": "countdown", "cont": True,
         **{k: v for k, v in hook.items() if k in ("levels", "zones", "marks")}},
    ]
    for k, (over, say) in enumerate(steps):
        sc = {**head, "show": show, "answer": answer, **over, "say": say + (FOLLOW_SAY if k == len(steps) - 1 else "")}
        if k == 0:
            sc["sfx"] = "reveal"
        if sc.get("type") == "chart":
            sc["cont"] = True
        scenes.append(sc)
    les["scenes"] = scenes
    les["tagFrom"] = 7  # the disclaimer tag appears after the hook
    les["format_v"] = 2


def at0(xs):
    return [{**x, "at": 0.0} for x in xs]


def lv(vid, i):
    s = chart_scenes(vid)[i]
    return {k: s[k] for k in ("levels", "marks", "zones") if s.get(k)}


# ---- failed breakout
quiz("v205_edu_failed_breakout", "Breakout! Buy it?", ["Buy", "Wait"], 1, 23,
     {"levels": at0(lv("v205_edu_failed_breakout", 1)["levels"])},
     "Price just broke above resistance. Do you buy it? Decide before the reveal.",
     [({"reveal": [23, 30], **lv("v205_edu_failed_breakout", 1)}, "Wait. The candle poked above resistance but closed back below it. That's a failed breakout, and it trapped everyone who bought the poke."),
      ({"reveal": [30, 37], **lv("v205_edu_failed_breakout", 2)}, "Their stops below the level add fuel to the drop. Wait for a close above, not a wick.")])

# ---- double top
quiz("v206_edu_double_top", "Two tops. Short it now?", ["Short now", "Wait"], 1, 28,
     {"marks": at0(lv("v206_edu_double_top", 1)["marks"]), "levels": at0(lv("v206_edu_double_top", 1)["levels"])},
     "Two tops at the same price. Do you short it now? Decide before the reveal.",
     [({"reveal": [28, 34], "levels": [lv("v206_edu_double_top", 2)["levels"][0]], "marks": lv("v206_edu_double_top", 2)["marks"]},
       "Wait. It's only a double top once a candle closes below the neckline, the low between the two tops."),
      ({"reveal": [34, 43], **lv("v206_edu_double_top", 2)}, "From there, the classic target is the pattern's height measured down. Here it got there, but many double tops don't.")])

# ---- ATR stop
A = edu.A
quiz("v207_edu_atr_stop", "Where does your stop go?", ["Tight", "1.5 ATR"], 1, 26,
     {"levels": [{"price": A["e"], "from": 25, "label": "Entry", "color": "blue", "at": 0.0}]},
     "You're long here. Tight stop, or one and a half ATR? Decide before the reveal.",
     [({"reveal": [26, 33], **lv("v207_edu_atr_stop", 1),  # entry already named in the question; its label would sit under the "Stopped out" arrow
        "levels": [{**l, "label": ""} if l.get("label") == "Entry" else l for l in lv("v207_edu_atr_stop", 1)["levels"]]}, "The tight stop, half an ATR below entry, got taken out by an ordinary dip."),
      ({"reveal": [33, 45], **lv("v207_edu_atr_stop", 2)}, "The wider one survived the noise. Wider stop, smaller size, same dollar risk.")])

# ---- Bollinger squeeze
B = edu.B
quiz("v208_edu_bollinger_squeeze", "Bands this tight. Which way next?", ["Up", "Down", "No idea"], 2, 32,
     {"from": 8},
     "The bands are this tight. Which way does it break? Decide before the reveal.",
     [({"reveal": [32, 42], **lv("v208_edu_bollinger_squeeze", 2)},
       f"Trick question. A squeeze tells you a big move may be coming, not its direction. Here the bands ended up more than {words(int(B['ratio']))} times wider.")])

# ---- risk:reward
rr_rows = [s for s in L["v209_edu_risk_reward"]["scenes"] if s["type"] == "rows"][1]
quiz("v209_edu_risk_reward", "You win only 40%. Profitable?", ["Yes", "No"], 0, 19,
     {"from": 8, "zones": at0(lv("v209_edu_risk_reward", 0)["zones"])},
     "You win only forty percent of your trades. Can you still make money? Decide before the reveal.",
     [({"reveal": [19, 37], **lv("v209_edu_risk_reward", 1)}, "Yes, if every win is twice the size of every loss."),
      ({**rr_rows, "type": "rows", "options": None, "headline": None}, "Four wins at two R is plus eight. Six losses cost six. That's plus two R every ten trades, before costs.")])

# ---- position size
ps_rows = [s for s in L["v210_edu_position_size"]["scenes"] if s["type"] == "rows"]
quiz("v210_edu_position_size", "4-point stop. How many micros?", ["5", "25", "50"], 1, 21,
     {"from": 8, "levels": at0(lv("v210_edu_position_size", 0)["levels"])},
     "Fifty thousand dollar account, one percent risk, four point stop. How many micro contracts? Decide before the reveal.",
     [({"reveal": [21, 35], **lv("v210_edu_position_size", 0)}, "Twenty-five. One percent of fifty thousand is five hundred dollars, and a four point stop on the micro risks twenty dollars per contract."),
      ({**ps_rows[2], "type": "rows", "options": None, "headline": None}, "Five hundred divided by twenty is twenty-five. On the E-mini it's two. Always round down.")])

# ---- trend structure
quiz("v211_edu_trend_structure", "Is this uptrend still alive?", ["Yes", "It's over"], 1, 36,
     {"marks": at0([m for m in lv("v211_edu_trend_structure", 1)["marks"] if m.get("text")])},
     "Higher highs, higher lows. Is this uptrend still alive? Decide before the reveal.",
     [({"reveal": [36, 45], **lv("v211_edu_trend_structure", 2)},
       "A lower high, then a close below the last higher low. The structure is broken, and that's often the first warning that the trend is changing.")])

# ---- MACD
mac = chart_scenes("v212_edu_macd_cross")[2]["say"]
quiz("v212_edu_macd_cross", "Did MACD catch this bottom?", ["Yes", "No, late"], 1, 12,
     {"marks": at0(lv("v212_edu_macd_cross", 1)["marks"])},
     "Here's the low. Did MACD catch it? Decide before the reveal.",
     [({"reveal": [12, 39], **lv("v212_edu_macd_cross", 2)},
       mac + " MACD is built from moving averages, so it confirms momentum. It doesn't catch the exact turn.")], zoom=(14, 9))

# ---- bull flag
quiz("v213_edu_bull_flag", "Top, or just a pause?", ["Top", "Pause"], 1, 27,
     {"from": 5, "zones": at0(lv("v213_edu_bull_flag", 1)["zones"])},
     "A sharp move up, then this slow drift lower. Is it the top, or just a pause? Decide before the reveal.",
     [({"reveal": [27, 41], **lv("v213_edu_bull_flag", 2)}, chart_scenes("v213_edu_bull_flag")[2]["say"])])

# ---- engulfing
quiz("v214_edu_engulfing", "Buy this candle?", ["Buy it", "Depends"], 1, 22,
     {"levels": at0(lv("v214_edu_engulfing", 1)["levels"]), "marks": at0(lv("v214_edu_engulfing", 1)["marks"])},
     "A big green candle swallows the red one. Do you buy it? Decide before the reveal.",
     [({"reveal": [22, 31], **lv("v214_edu_engulfing", 2)},
       "It depends where it is. A bullish engulfing candle tends to mean more at support after a pullback, like here, than in the middle of a range.")])

# ---- drawdown math
quiz("v215_edu_drawdown_math", "Down 50%, up 50%. Back to even?", ["Yes", "No"], 1, 27,
     {"levels": at0(lv("v215_edu_drawdown_math", 0)["levels"]), "marks": at0(lv("v215_edu_drawdown_math", 0)["marks"])},
     "Your account drops fifty percent, then gains fifty percent. Are you back to even? Decide before the reveal.",
     [({"reveal": [27, 43], **lv("v215_edu_drawdown_math", 1)}, chart_scenes("v215_edu_drawdown_math")[1]["say"])])
