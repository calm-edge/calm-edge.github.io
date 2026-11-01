"""Instagram highlight covers and highlight stories (1080x1920 JPEG), uploaded by hand: Instagram's API can't create highlights.
  python marketing/stories/highlights.py out_dir      (renders with video/still.py; fails if any text overflows)
Platform links are added by hand as link stickers when uploading (stickers can't be drawn into an image)."""
import json, pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).parent
STILL = HERE.parent / "video" / "still.py"
HANDLE = "@calmedgeofficial"
TAG = "Education, not financial advice"

COVERS = [("start", "mint"), ("lessons", "blue"), ("strategies", "gold"), ("risk", "coral"), ("tools", "violet"), ("links", "mint")]

H = {
    "hl_start": [
        {"type": "cover", "kicker": "Welcome to Calm Edge", "title": "Trading, explained. One concept a day.",
         "text": "Clear charts, real numbers, **no hype**. Everything is education, not financial advice.", "button": ""},
        {"type": "rows", "title": "What we post", "head": ["", "", ""], "rows": [
            {"cells": ["09:30", "", "Strategy carousel"]}, {"cells": ["17:30", "", "20-second chart quiz"], "good": True, "hl": True},
            {"cells": ["Sunday", "", "Full lesson on YouTube"]}],
         "text": "Times are Central European. **Turn on notifications** so you don't miss the quiz."},
        {"type": "points", "title": "Get the most out of it", "points": [
            {"b": "Answer the quiz before the reveal", "t": "Then check yourself. That's how it sticks.", "color": "mint"},
            {"b": "Save the carousels", "t": "They're built to be reread before you trade.", "color": "gold"},
            {"b": "Ask in the comments", "t": "Questions become future lessons.", "color": "blue"}]},
    ],
    "hl_lessons": [
        {"type": "cover", "kicker": "Lessons", "title": "Indicators, patterns and price action.", "text": "Short lessons on the concepts traders use every day.", "button": ""},
        {"type": "rows", "title": "Covered so far", "head": ["", "", ""], "rows": [
            {"cells": ["RSI, 20 EMA, VWAP, MACD", "", "Indicators"]}, {"cells": ["Bollinger squeeze, ATR", "", "Volatility"]},
            {"cells": ["Double top, bull flag", "", "Patterns"]}, {"cells": ["Breakouts, S/R flip, engulfing", "", "Price action"]}],
         "text": "Find them in the **Reels** tab of the profile."},
    ],
    "hl_strategies": [
        {"type": "cover", "kicker": "Strategies", "title": "Complete strategies, with the rules.", "text": "Entry, stop, target, and **the day it fails**.", "button": ""},
        {"type": "rows", "title": "Strategy breakdowns", "head": ["", "", ""], "rows": [
            {"cells": ["Opening range breakout", "", "Intraday"]}, {"cells": ["Gap fill", "", "Intraday"]},
            {"cells": ["Inside bar breakout", "", "Swing"]}, {"cells": ["Fibonacci pullback", "", "Trend"]}, {"cells": ["Range trading", "", "Range"]}],
         "text": "Test any strategy on your own data **before** risking money."},
    ],
    "hl_risk": [
        {"type": "cover", "kicker": "Risk", "title": "The part that keeps you in the game.", "button": ""},
        {"type": "rows", "title": "Five rules worth knowing", "head": ["", "", ""], "rows": [
            {"cells": ["Size from the stop", "", "Not from a feeling"]}, {"cells": ["Stops outside noise", "", "Use ATR"]},
            {"cells": ["2R target", "", "33% to break even"], "good": True, "hl": True}, {"cells": ["Daily loss limit", "", "Then stop"]},
            {"cells": ["After a loss", "", "Same size or smaller"]}]},
        {"type": "formula", "title": "Position size", "formula": "Contracts = $ risk ÷ (stop × $ per point)",
         "small": "$200 ÷ (8 points × $5 on MES) = 5 contracts"},
    ],
    "hl_tools": [
        {"type": "cover", "kicker": "Tools", "title": "Free calculators and our apps.", "text": "Position size, risk of ruin and more, **free on our site**. Link in bio.", "button": ""},
        {"type": "points", "title": "Our apps", "points": [
            {"b": "Trading Journal AI", "t": "Log trades, see your real numbers, review them with your AI.", "color": "mint"},
            {"b": "Prop Firm Manager", "t": "Drawdown, payouts and rules for every prop account in one screen.", "color": "gold"},
            {"b": "Both, as a bundle", "t": "Desktop apps, your data stays on your computer. Link in bio.", "color": "blue"}]},
    ],
    "hl_links": [
        {"type": "cover", "kicker": "Find us everywhere", "title": "Calm Edge on every platform.", "text": "Same name everywhere: **Calm Edge**.", "button": ""},
        {"type": "rows", "title": "Where to find what", "head": ["", "", ""], "rows": [
            {"cells": ["YouTube", "", "Full weekly lessons"], "good": True, "hl": True}, {"cells": ["TikTok", "", "Daily chart quiz"]},
            {"cells": ["Pinterest", "", "Cheat sheets"]}, {"cells": ["Facebook", "", "Everything, in one feed"]}, {"cells": ["Website", "", "Guides and calculators"]}],
         "text": "Tap the links on this story."},
    ],
}


def main():
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    specs = [{"id": "hl_covers", "kind": "stories", "handle": HANDLE, "slides": [{"type": "hlcover", "icon": i, "color": c} for i, c in COVERS]}]
    specs += [{"id": k, "kind": "stories", "handle": HANDLE, "tag": TAG, "slides": v} for k, v in H.items()]
    bad = 0
    for sp in specs:
        f = pathlib.Path(tempfile.mkdtemp()) / f"{sp['id']}.json"; f.write_text(json.dumps(sp))
        r = subprocess.run([sys.executable, str(STILL), str(f), str(out)], capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr[-800:]); bad += r.returncode != 0
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
