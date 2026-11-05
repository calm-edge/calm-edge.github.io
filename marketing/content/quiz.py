"""Reel hooks, built to be watched to the end. Five formats, rotated so two days in a row never look the same:
  quiz      - a question with 2-3 answers from frame one, 3-2-1 countdown, the right answer lights up;
  next      - an open loop: the chart stops on the key moment, "What happens next?" pulses over it, then the payoff;
  spot      - "Find the mistake in this trade": the viewer hunts for it during a countdown, then a MISTAKE stamp;
  myth      - MYTH: a belief most traders hold, stamped FALSE, then TRUTH with the chart that proves it;
  zoomout   - zoomed in on a few candles that look like one thing ("Looks bearish, right?"), then the camera pulls back.
Quiz format, in detail:
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
    les["hook"] = "quiz"


def at0(xs):
    return [{**x, "at": 0.0} for x in xs]


def lv(vid, i):
    s = chart_scenes(vid)[i]
    return {k: s[k] for k in ("levels", "marks", "zones") if s.get(k)}



def _finish(vid, scenes, fmt):
    last = [k for k, sc in enumerate(scenes) if sc.get("say")][-1]
    scenes[last] = {**scenes[last], "say": scenes[last]["say"] + FOLLOW_SAY}
    L[vid]["scenes"] = scenes
    L[vid]["tagFrom"] = 7
    L[vid]["format_v"] = 2
    L[vid]["hook"] = fmt


def next_up(vid, headline, decide, hook, hook_say, steps, overlay="What happens next?", zoom=(22, 13)):
    """Open loop: the chart plays up to the key moment and freezes under a pulsing question, then the payoff."""
    show = _show(vid)
    head = {"type": "chart", "chart": "a", "headline": headline, "big": True}
    scenes = [{**head, "reveal": [hook.get("from", 6), decide], "show": show, "grow": 0.95, **{k: v for k, v in hook.items() if k != "from"}, "say": hook_say},
              {**head, "reveal": [decide, decide], "show": show, "zoom": list(zoom), "overlay": overlay, "duration": 2.4, "sfx": "riser", "cont": True,
               **{k: v for k, v in hook.items() if k in ("levels", "zones", "marks")}}]
    for k, (over, say) in enumerate(steps):
        sc = {**head, "show": show, **over, "say": say}
        if sc.get("type") == "chart":
            sc["cont"] = True
        if k == 0:
            sc["sfx"] = "reveal"
        scenes.append(sc)
    _finish(vid, scenes, "next")


def spot(vid, headline, decide, hook, hook_say, steps, stamp="MISTAKE", zoom=(22, 12)):
    """'Find the mistake': the trade is on screen, the viewer looks for the error during a countdown, then the stamp."""
    show = _show(vid)
    head = {"type": "chart", "chart": "a", "headline": headline, "big": True}
    scenes = [{**head, "reveal": [hook.get("from", 6), decide], "show": show, "grow": 0.95, **{k: v for k, v in hook.items() if k != "from"}, "say": hook_say},
              {**head, "reveal": [decide, decide], "show": show, "zoom": list(zoom), "countdown": 3, "duration": 3, "sfx": "countdown", "cont": True,
               **{k: v for k, v in hook.items() if k in ("levels", "zones", "marks")}}]
    for k, (over, say) in enumerate(steps):
        sc = {**head, "show": show, **over, "say": say}
        if sc.get("type") == "chart":
            sc["cont"] = True
        if k == 0:
            sc.update({"stamp": {"text": stamp, "at": 0.04}, "sfx": "stamp", "sfx_at": 0.04})
        scenes.append(sc)
    _finish(vid, scenes, "spot")


def myth(vid, myth_text, truth_text, hook, hook_say, steps, stamp="FALSE"):
    """MYTH on screen from frame one, stamped FALSE while the chart plays, then TRUTH and the proof."""
    show = _show(vid)
    scenes = [{"type": "chart", "chart": "a", "kicker": "Myth", "kickerColor": "coral", "headline": myth_text, "big": True, "show": show, "grow": 0.95,
               "reveal": [hook.get("from", 6), hook["to"]], **{k: v for k, v in hook.items() if k not in ("from", "to")},
               "stamp": {"text": stamp, "at": 0.62}, "sfx": "stamp", "sfx_at": 0.62, "hold": 0.4, "say": hook_say}]
    for k, (over, say) in enumerate(steps):
        sc = {"type": "chart", "chart": "a", "kicker": "Truth", "kickerColor": "mint", "headline": truth_text, "big": True, "show": show, **over, "say": say}
        if sc.get("type") == "chart" and k > 0:
            sc["cont"] = True
        scenes.append(sc)
    _finish(vid, scenes, "myth")


def zoomout(vid, headline, at_bar, window, hook_say, reveal_headline, steps, zones=None):
    """Zoomed in on the last few candles (they look like one thing), then the camera pulls back to show the whole picture."""
    show = _show(vid)
    scenes = [{"type": "chart", "chart": "a", "headline": headline, "big": True, "show": show, "reveal": [at_bar - 4, at_bar], "zoom": [window, window - 1],
               "minBars": 4, "say": hook_say},
              {"type": "chart", "chart": "a", "headline": reveal_headline, "big": True, "show": show, "reveal": [at_bar, at_bar], "zoom": [window, at_bar + 1.5],
               "zones": [{**z, "at": 0.55} for z in (zones or [])], "sfx": "riser", "cont": True, "duration": 2.6}]
    for k, (over, say) in enumerate(steps):
        sc = {"type": "chart", "chart": "a", "headline": reveal_headline, "big": True, "show": show, **over, "say": say}
        if sc.get("type") == "chart":
            sc["cont"] = True
        if k == 0:
            sc["sfx"] = "reveal"
        scenes.append(sc)
    _finish(vid, scenes, "zoomout")


def _show(vid):
    first = chart_scenes(vid)[0]
    return first.get("show", []) + first.get("add", [])


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

# ---- ATR stop: spot the mistake
A = edu.A
_tight = [l for l in lv("v207_edu_atr_stop", 1)["levels"] if l.get("label") == "Tight stop"]
spot("v207_edu_atr_stop", "Find the mistake in this trade.", 26,
     {"levels": [{"price": A["e"], "from": 25, "label": "Entry", "color": "blue", "at": 0.0}] + at0(_tight)},
     "Long here, with the stop right below. Find the mistake before the countdown ends.",
     [({"reveal": [26, 33], **lv("v207_edu_atr_stop", 1),  # entry already named in the hook; its label would sit under the "Stopped out" arrow
        "levels": [{**l, "label": ""} if l.get("label") == "Entry" else l for l in lv("v207_edu_atr_stop", 1)["levels"]]},
       "The stop. Half an ATR below entry is inside normal noise, and an ordinary dip takes it out."),
      ({"reveal": [33, 45], **lv("v207_edu_atr_stop", 2)},
       "ATR is how far price normally moves in one bar. At one and a half ATR, the same dip is just noise. Wider stop, smaller size, same dollar risk.")])
# ---- Bollinger squeeze: what happens next
B = edu.B
next_up("v208_edu_bollinger_squeeze", "The bands are pinching.", 32, {"from": 8},
        "When Bollinger Bands pinch this tight, price has gone quiet. Watch what happens next.",
        [({"reveal": [32, 42], **lv("v208_edu_bollinger_squeeze", 2), "headline": "Quiet markets don't stay quiet."},
          f"The bands ended up more than {words(int(B['ratio']))} times wider. But notice: the squeeze told you a move might come, not which way.")],
        overlay="Wait for it…")
# ---- risk:reward: myth
rr_rows = [s for s in L["v209_edu_risk_reward"]["scenes"] if s["type"] == "rows"][1]
myth("v209_edu_risk_reward", "You must win most trades.", "Win 40%, still profitable.",
     {"from": 8, "to": 19, "zones": at0(lv("v209_edu_risk_reward", 0)["zones"])},
     "Myth: to make money, you need to win most of your trades.",
     [({"reveal": [19, 37], **lv("v209_edu_risk_reward", 1)},
       "Not true. Risk one unit to make two, and you break even winning just one trade in three, before costs."),
      ({**rr_rows, "type": "rows"}, "Win four out of ten: four wins at two R is plus eight, six losses cost six. Plus two R every ten trades.")])
# ---- position size
ps_rows = [s for s in L["v210_edu_position_size"]["scenes"] if s["type"] == "rows"]
quiz("v210_edu_position_size", "4-point stop. How many micros?", ["5", "25", "50"], 1, 21,
     {"from": 8, "levels": at0(lv("v210_edu_position_size", 0)["levels"])},
     "Fifty thousand dollar account, one percent risk, four point stop. How many micro contracts? Decide before the reveal.",
     [({"reveal": [21, 35], **lv("v210_edu_position_size", 0)}, "Twenty-five. One percent of fifty thousand is five hundred dollars, and a four point stop on the micro risks twenty dollars per contract."),
      ({**ps_rows[2], "type": "rows", "options": None, "headline": None}, "Five hundred divided by twenty is twenty-five. On the E-mini it's two. Always round down.")])

# ---- trend structure: what happens next
next_up("v211_edu_trend_structure", "Higher highs. Higher lows.", 32,
        {"marks": at0([m for m in lv("v211_edu_trend_structure", 1)["marks"] if m.get("text")])},
        "Higher highs, higher lows: a clean uptrend. Watch what happens next.",
        [({"reveal": [32, 45], **lv("v211_edu_trend_structure", 2), "headline": "Lower high, then a break."},
          "A lower high, then a close below the last higher low. The structure is broken, and that's often the first warning that the trend is changing.")])
# ---- MACD
mac = chart_scenes("v212_edu_macd_cross")[2]["say"]
quiz("v212_edu_macd_cross", "Did MACD catch this bottom?", ["Yes", "No, late"], 1, 12,
     {"marks": at0(lv("v212_edu_macd_cross", 1)["marks"])},
     "Here's the low. Did MACD catch it? Decide before the reveal.",
     [({"reveal": [12, 39], **lv("v212_edu_macd_cross", 2)},
       mac + " MACD is built from moving averages, so it confirms momentum. It doesn't catch the exact turn.")], zoom=(14, 9))

# ---- bull flag: zoom out
zoomout("v213_edu_bull_flag", "Looks bearish, right?", 26, 9,
        "Price drifting lower, candle after candle. Looks bearish, right?", "Now zoom out.",
        [({"reveal": [26, 27], "zones": at0(lv("v213_edu_bull_flag", 1)["zones"]), "headline": "It's a bull flag."},
          "It's a bull flag: a sharp move up, then a slow, tight drift lower on smaller candles, as buyers take a breather."),
         ({"reveal": [27, 41], **lv("v213_edu_bull_flag", 2), "headline": "Pause, then breakout."}, chart_scenes("v213_edu_bull_flag")[2]["say"])],
        zones=lv("v213_edu_bull_flag", 1)["zones"])
# ---- engulfing: myth
myth("v214_edu_engulfing", "Engulfing = buy signal.", "Location matters more.",
     {"from": 6, "to": 22, "levels": at0(lv("v214_edu_engulfing", 1)["levels"]), "marks": at0(lv("v214_edu_engulfing", 1)["marks"])},
     "Myth: a bullish engulfing candle is a buy signal.",
     [({"reveal": [22, 31], **lv("v214_edu_engulfing", 2)},
       "Its green body swallows the previous red one, so buyers took control for a bar. But it tends to mean more at support after a pullback, like here, than in the middle of a range.")])
# ---- drawdown math
quiz("v215_edu_drawdown_math", "Down 50%, up 50%. Back to even?", ["Yes", "No"], 1, 27,
     {"levels": at0(lv("v215_edu_drawdown_math", 0)["levels"]), "marks": at0(lv("v215_edu_drawdown_math", 0)["marks"])},
     "Your account drops fifty percent, then gains fifty percent. Are you back to even? Decide before the reveal.",
     [({"reveal": [27, 43], **lv("v215_edu_drawdown_math", 1)}, chart_scenes("v215_edu_drawdown_math")[1]["say"])])

# ---- stochastic: what happens next
_cs = edu.ST["cx"] - 15
next_up("v216_edu_stochastic", "Stochastic under 20 at support.", _cs + 1,
        {"levels": at0(lv("v216_edu_stochastic", 1)["levels"])},
        "Stochastic just turned up from below twenty, right at the bottom of the range. Watch what happens next.",
        [({"reveal": [_cs + 1, 33], **lv("v216_edu_stochastic", 2), "headline": "Back to the top of the range."},
          "Stochastic shows where the close sits inside the last fourteen bars' range. In a sideways market, a turn up from below twenty near support often comes before a move back toward the top. In a strong downtrend, it can stay low for a long time.")])
# ---- RSI divergence: myth
myth("v217_edu_rsi_divergence", "Divergence = sell now.", "A warning, not a trigger.",
     {"from": 6, "to": 23, "marks": at0(lv("v217_edu_rsi_divergence", 1)["marks"])},
     "Myth: when RSI diverges from price, the top is in.",
     [({"reveal": [23, 39], **lv("v217_edu_rsi_divergence", 2)},
       f"Price made a higher high while RSI made a lower one: momentum was fading. But price made one more high {words(edu.later)} bars later before it turned. Wait for price to confirm, like a close below the last swing low.")])
# ---- pin bar: quiz
quiz("v218_edu_pin_bar", "Long tail at support. Who won?", ["Sellers", "Buyers"], 1, 23,
     {"levels": at0(lv("v218_edu_pin_bar", 1)["levels"])},
     "Price dropped below support and left a long tail. Who won this candle? Decide before the reveal.",
     [({"reveal": [23, 25], **lv("v218_edu_pin_bar", 1)}, chart_scenes("v218_edu_pin_bar")[1]["say"].replace("Price dropped", "Buyers. Price dropped")),
      ({"reveal": [25, 31], **lv("v218_edu_pin_bar", 2)}, chart_scenes("v218_edu_pin_bar")[2]["say"])], zoom=(16, 9))
# ---- breakout volume: spot the mistake
spot("v219_edu_breakout_volume", "Find the mistake in this trade.", 23,
     {"levels": [{"price": edu.VO["c"][22]["c"], "from": 22, "label": "Long", "color": "blue", "labelPos": "right", "at": 0.0}] + at0(lv("v219_edu_breakout_volume", 0)["levels"])},
     "Long on the close above resistance. Find the mistake before the countdown ends.",
     [({"reveal": [23, 28], **lv("v219_edu_breakout_volume", 1)},
       "The volume. This breakout came on about a third of the average volume, and price fell straight back into the range."),
      ({"reveal": [28, 45], **lv("v219_edu_breakout_volume", 2)},
       chart_scenes("v219_edu_breakout_volume")[2]["say"])])
# ---- head and shoulders: zoom out
zoomout("v220_edu_head_shoulders", "Bouncing off support, right?", 29, 6,
        "Price bounces off support, green candle after green candle. Looks bullish, right?", "Now zoom out.",
        [({"reveal": [29, 31], **lv("v220_edu_head_shoulders", 1), "marks": at0(lv("v220_edu_head_shoulders", 1)["marks"]), "headline": "It's the right shoulder."},
          chart_scenes("v220_edu_head_shoulders")[1]["say"]),
         ({"reveal": [31, 45], **lv("v220_edu_head_shoulders", 2), "headline": "Then the neckline breaks."}, chart_scenes("v220_edu_head_shoulders")[2]["say"])])
