"""Content bank: video specs + post texts for every channel. Run to (re)write content/videos/*.json.
Numbers come from the demo journal shown in the app (verified against the spreadsheet edition).
Every video that shows numbers carries the "Example journal · demo data" tag."""
import json, pathlib

OUT = pathlib.Path(__file__).parent / "videos"
TAG = "Example journal · demo data"
LINK = "https://kallas8.gumroad.com/l/axltbh"
BASE_TAGS = ["#tradingjournal", "#daytrading", "#trading", "#tradingpsychology", "#futurestrading"]

CTA = lambda text="A calm, honest record of every trade.": {
    "type": "cta", "title": "Trading Journal AI", "sub": "Desktop app · Windows & Mac", "text": text, "button": "Link in bio",
    "say": "Trading Journal AI. Link in bio."}
ONECLICK = {"type": "shot", "img": "oneclick", "title": "One click. Your AI reviews your week.", "ring": "btn_claude",
            "chips": [{"text": "Claude", "color": "mint"}, {"text": "ChatGPT", "color": "blue"}, {"text": "Gemini", "color": "gold"}],
            "say": "Then one click, and your own AI reviews your week."}


def post(title, body, tags, pin=None):
    """Texts for each channel. `title` is also the YouTube title; `pin` the Pinterest title."""
    hashtags = " ".join(dict.fromkeys(tags + BASE_TAGS))
    return {
        "instagram": f"{body}\n\nTrading Journal AI: desktop app for Windows & Mac, with a one-click AI review. Link in bio.\n\n{hashtags}",
        "tiktok": f"{body} {' '.join(dict.fromkeys(tags + BASE_TAGS[:3]))}",
        "youtube": {"title": f"{title} #shorts", "description": f"{body}\n\nTrading Journal AI (Windows & Mac): {LINK}\n\nExample journal with demo data. Not financial advice.\n\n{hashtags} #shorts"},
        "facebook": f"{body}\n\nTrading Journal AI: {LINK}",
        "pinterest": {"title": pin or title, "description": f"{body} Trading journal app for Windows & Mac with AI weekly review.", "link": LINK},
    }


V = []

V.append({"id": "v001_rule_breaks", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "Trading journal", "text": "Breaking your own rules has a price. Do you know yours?",
     "say": "Breaking your own rules has a price. Do you know yours?"},
    {"type": "shot", "img": "add_trade", "title": "Ten fields per trade. The rest is automatic.",
     "chips": [{"html": "R <b>+2.00R</b>"}, {"html": "P&amp;L <b>+$77.52</b>"}, {"html": "<b>Win</b>"}],
     "say": "Log every trade in ten fields. Risk, R and P and L calculate themselves."},
    {"type": "rows", "title": "Did you follow your plan?", "head": ["My plan", "Trades", "Net P&L"],
     "rows": [{"cells": ["Followed", "73", "+$2,033"], "good": True}, {"cells": ["Broke a rule", "16", "−$555"], "hl": True}],
     "say": "Mark whether you followed your plan. In this example, sixteen rule breaks cost five hundred and fifty five dollars."},
    {"type": "rows", "title": "Your costliest mistakes", "head": ["Mistake", "Times", "Net P&L"],
     "rows": [{"cells": ["FOMO entry", "5", "−$609"], "hl": True}, {"cells": ["No setup", "3", "−$122"]}, {"cells": ["Chased price", "1", "−$65"]}],
     "say": "And you see which mistake costs the most. Here, it's FOMO entries."},
    ONECLICK,
    {"type": "chat", "me": "Weekly review, last 14 days.",
     "ai": ["Net P&amp;L <span class='m'>+385.28</span> · win rate <b>67%</b> · profit factor <b>3.80</b>",
            "Your best hours: <b>10:00–12:00</b>, 7 wins out of 8. One rule for next week: <b>no trades before 10:00.</b>"],
     "say": "Claude, ChatGPT or Gemini, working from your real numbers."},
    CTA()],
    "post": post("What breaking your trading rules really costs", "Breaking your own rules has a price. In this example journal, 16 rule breaks cost $555, and FOMO entries were the costliest mistake.",
                 ["#riskmanagement", "#tradingrules"], "How much do broken trading rules cost you?")})

V.append({"id": "v002_best_setup", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "Your edge", "text": "Your favourite setup might be the one losing you money.",
     "say": "Your favourite setup might be the one losing you money."},
    {"type": "rows", "title": "Average R by setup", "head": ["Setup", "Trades", "Avg R"],
     "rows": [{"cells": ["Trend pullback", "16", "+0.89R"], "good": True, "hl": True}, {"cells": ["Opening range", "29", "+0.63R"]},
              {"cells": ["VWAP reclaim", "24", "+0.11R"]}, {"cells": ["Failed breakout", "20", "−0.41R"], "hl": True}],
     "say": "In this example journal, trend pullbacks earn almost one R per trade. Failed breakouts lose almost half an R, every time."},
    {"type": "stat", "label": "Failed breakouts, 20 trades", "value": -713, "prefix": "$", "color": "coral", "sub": "20% win rate",
     "say": "Twenty trades, seven hundred and thirteen dollars gone."},
    {"type": "shot", "img": "by_setup", "title": "Every setup, with its sample size.", "ring": "setup_worst",
     "say": "The journal ranks every setup for you, so you know what's real and what's noise."},
    ONECLICK, CTA("Know your edge, setup by setup.")],
    "post": post("Your favourite trading setup might be losing you money", "Rank your setups by average R, not by feel. In this example journal, one setup made +0.89R per trade and another lost -0.41R.",
                 ["#tradingstrategy", "#edge"], "Find your best trading setup by average R")})

V.append({"id": "v003_emotions", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "Trading psychology", "text": "Six frustrated trades. $674 gone.",
     "say": "Six frustrated trades. Six hundred and seventy four dollars, gone."},
    {"type": "rows", "title": "Net P&L by emotion", "head": ["Emotion", "Trades", "Net P&L"],
     "rows": [{"cells": ["Calm", "55", "+$1,994"], "good": True, "hl": True}, {"cells": ["Confident", "18", "+$39"]},
              {"cells": ["Anxious", "5", "−$114"]}, {"cells": ["Frustrated", "6", "−$674"], "hl": True}],
     "say": "In this example journal, calm trades made almost two thousand dollars. Six frustrated ones lost six hundred and seventy four."},
    {"type": "stat", "label": "Win rate when frustrated", "value": 0, "suffix": "%", "color": "coral", "sub": "0 wins out of 6",
     "say": "Zero wins out of six. Your mood leaves a trace in your numbers."},
    ONECLICK, CTA("See what your emotions cost you.")],
    "post": post("Your emotions are in your trading numbers", "Tag each trade with how you felt. In this example journal, 55 calm trades made +$1,994 and 6 frustrated trades lost -$674.",
                 ["#mindset", "#tradingmindset"], "How emotions affect trading results")})

V.append({"id": "v004_profit_factor", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "Trading maths", "text": "A 51% win rate tells you almost nothing.",
     "say": "A fifty one percent win rate tells you almost nothing."},
    {"type": "stat", "label": "Profit factor", "value": 1.43, "decimals": 2, "color": "mint", "sub": "gross profit ÷ gross loss",
     "say": "Profit factor does. It's everything you won, divided by everything you lost."},
    {"type": "rows", "title": "How to read it", "head": ["Profit factor", "", "Meaning"],
     "rows": [{"cells": ["Below 1", "", "Losing"], "hl": True}, {"cells": ["1 to 1.5", "", "Thin edge"]}, {"cells": ["Above 1.5", "", "Solid edge"], "good": True, "hl": True}],
     "say": "Below one, you're losing money. Above one and a half, you have a solid edge."},
    {"type": "shot", "img": "kpis", "title": "Calculated for you, for any period.", "ring": "kpi_pf",
     "say": "Your journal calculates it for any period, with win rate, R and drawdown."},
    CTA("Your real numbers, not your feelings.")],
    "post": post("Profit factor explained in 30 seconds", "Win rate alone tells you almost nothing. Profit factor = gross profit / gross loss. Below 1 you're losing, above 1.5 you have a solid edge.",
                 ["#tradingeducation", "#profitfactor"], "Profit factor explained for traders")})

V.append({"id": "v005_r_multiple", "scenes": [
    {"type": "hook", "kicker": "Trading maths", "text": "Stop counting dollars. Count R.",
     "say": "Stop counting dollars. Count R."},
    {"type": "rows", "title": "One trade, in R", "head": ["", "", "Value"],
     "rows": [{"cells": ["Risk (entry to stop)", "", "$40"]}, {"cells": ["Result", "", "+$80"], "good": True}, {"cells": ["R multiple", "", "+2.00R"], "good": True, "hl": True}],
     "say": "R is what a trade made, divided by what you risked. Risk forty, make eighty: that's plus two R."},
    {"type": "hook", "text": "R lets you compare every trade, whatever the size.",
     "say": "R lets you compare every trade, whatever the size, the market or the account."},
    {"type": "shot", "img": "add_trade", "title": "Your journal does the maths.",
     "chips": [{"html": "Risk <b>$40</b>"}, {"html": "R <b>+2.00R</b>"}],
     "say": "Type entry, stop and exit. The R appears as you type."},
    CTA("Every trade in R, automatically.")],
    "post": post("R multiple explained: the number pro traders track", "R = what a trade made / what you risked. Risk $40, make $80: +2R. It lets you compare every trade, whatever the size.",
                 ["#tradingeducation", "#riskmanagement"], "R multiple explained for day traders")})

V.append({"id": "v006_time_of_day", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "Your edge", "text": "When do you actually make money?",
     "say": "When do you actually make money? Most traders guess."},
    {"type": "rows", "title": "Net P&L by time of day", "head": ["Hours", "Trades", "Net P&L"],
     "rows": [{"cells": ["09–10 h", "26", "+$471"]}, {"cells": ["10–12 h", "39", "+$315"]}, {"cells": ["12–14 h", "11", "+$145"]},
              {"cells": ["14–17 h", "13", "+$548"], "good": True, "hl": True}],
     "say": "In this example journal, the afternoon made the most with the fewest trades. Thirteen trades, five hundred and forty eight dollars."},
    {"type": "shot", "img": "by_hour", "title": "By hour and by weekday.", "ring": "hour_best",
     "say": "Your journal splits every result by hour and by weekday."},
    ONECLICK, CTA("Trade your best hours.")],
    "post": post("When do you actually make money trading?", "Split your results by hour. In this example journal, 13 afternoon trades made more than 39 trades in the late morning.",
                 ["#daytrader", "#tradingtips"], "Best time of day to trade? Check your journal")})

V.append({"id": "v007_drawdown", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "Risk", "text": "The number that decides if you survive.",
     "say": "There's one number that decides if you survive as a trader."},
    {"type": "stat", "label": "Max drawdown", "value": -612, "prefix": "$", "color": "coral", "sub": "on a $10,000 account · 6.1%",
     "say": "Max drawdown: the biggest drop from a peak. In this example, six hundred and twelve dollars."},
    {"type": "shot", "img": "equity", "title": "Your equity curve, trade by trade.",
     "say": "Your equity curve shows every peak and every dip."},
    {"type": "stat", "label": "Longest losing streak", "value": 4, "suffix": " trades", "color": "gold",
     "say": "Know your longest losing streak before it surprises you."},
    CTA("Know your risk before the market tells you.")],
    "post": post("Max drawdown: the number that decides if you survive", "Max drawdown is the biggest drop from a peak in your account. Track it, together with your longest losing streak.",
                 ["#riskmanagement", "#drawdown"], "Max drawdown explained for traders")})

V.append({"id": "v008_ai_review", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "AI for traders", "text": "Your AI can review your trading week. In one click.",
     "say": "Your AI can review your trading week. In one click."},
    {"type": "shot", "img": "oneclick", "title": "Pick a period. Pick your AI.", "ring": "btn_claude",
     "chips": [{"text": "Claude", "color": "mint"}, {"text": "ChatGPT", "color": "blue"}, {"text": "Gemini", "color": "gold"}],
     "say": "Pick a period and your AI. It opens with your numbers already in the chat."},
    {"type": "chat", "me": "Weekly review, last 14 days.",
     "ai": ["Net P&amp;L <span class='m'>+385.28</span> · win rate <b>67%</b> · profit factor <b>3.80</b>",
            "Calm trades: <span class='m'>+395</span>. One FOMO entry: <span class='c'>−2.48</span>. It's the habit, not the amount."],
     "say": "No uploads, no prompts. It uses the same numbers you see in the journal."},
    {"type": "hook", "text": "No signals. No predictions. Just what you actually did.",
     "say": "No signals, no predictions. Just an honest look at what you actually did."},
    CTA("Uses the AI you already have.")],
    "post": post("Let your AI review your trading week in one click", "Pick a period, click Claude, ChatGPT or Gemini, and your AI reviews your week from your real numbers. No uploads, no prompts.",
                 ["#ai", "#chatgpt", "#claude"], "AI trading journal review in one click")})

V.append({"id": "v009_calendar", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "P&L calendar", "text": "Your month, one glance.",
     "say": "Your trading month, in one glance."},
    {"type": "shot", "img": "calendar", "title": "Green days. Red days. Weekly totals.",
     "say": "Green days, red days, and the total for every week."},
    {"type": "stat", "label": "October, 18 trades", "value": 598, "prefix": "+$", "color": "mint",
     "say": "In this example, October closed up five hundred and ninety eight dollars."},
    CTA("See your month at a glance.")],
    "post": post("A P&L calendar for your trading month", "Green days, red days and weekly totals, built from your trades automatically.",
                 ["#pnl", "#tradingcalendar"], "Trading P&L calendar")})

V.append({"id": "v010_position_size", "scenes": [
    {"type": "hook", "kicker": "Risk management", "text": "Position size in three numbers.",
     "say": "Position size, in three numbers."},
    {"type": "rows", "title": "Example: MES futures", "head": ["", "", "Value"],
     "rows": [{"cells": ["Risk per trade", "", "$100"]}, {"cells": ["Stop distance", "", "4 points"]}, {"cells": ["Point value", "", "$5"]}],
     "say": "How much you'll risk, how far your stop is, and what one point is worth."},
    {"type": "stat", "label": "Contracts = 100 ÷ (4 × 5)", "value": 5, "suffix": " contracts", "color": "mint",
     "say": "Risk divided by stop times point value. Here, five contracts."},
    {"type": "hook", "text": "Same risk on every trade. That's what makes R honest.",
     "say": "Same risk on every trade. That's what makes your results comparable."},
    CTA("Point values for futures, stocks, forex and crypto.")],
    "post": post("Position size in 3 numbers (futures example)", "Contracts = risk / (stop distance x point value). $100 risk, 4-point stop on MES ($5/point) = 5 contracts.",
                 ["#positionsizing", "#riskmanagement", "#futures"], "How to calculate position size for futures")})

V.append({"id": "v011_weekday", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "Your edge", "text": "Is there a day you should just not trade?",
     "say": "Is there a day of the week you should just not trade?"},
    {"type": "rows", "title": "Net P&L by weekday", "head": ["Day", "Trades", "Net P&L"],
     "rows": [{"cells": ["Monday", "22", "+$841"], "good": True, "hl": True}, {"cells": ["Tuesday", "16", "+$320"]}, {"cells": ["Wednesday", "19", "+$267"]},
              {"cells": ["Thursday", "17", "−$30"], "hl": True}, {"cells": ["Friday", "15", "+$80"]}],
     "say": "In this example journal, Mondays made the most. Thursdays lost money over seventeen trades."},
    {"type": "hook", "text": "Small samples lie. Your journal shows the count.",
     "say": "Careful with small samples. Your journal always shows how many trades are behind each number."},
    ONECLICK, CTA()],
    "post": post("Is there a day you should not trade?", "Split your results by weekday, and always check the sample size. In this example journal, Thursdays lost money over 17 trades.",
                 ["#daytrader", "#tradingtips"], "Best day of the week to trade? Check your data")})

V.append({"id": "v012_privacy", "scenes": [
    {"type": "hook", "kicker": "Trading journal", "text": "Your trades are nobody's business.",
     "say": "Your trades are nobody's business."},
    {"type": "rows", "title": "Trading Journal AI", "head": ["", "", ""],
     "rows": [{"cells": ["Stored on your computer", "", "✓"], "good": True}, {"cells": ["No account, no cloud", "", "✓"], "good": True},
              {"cells": ["Daily backups", "", "✓"], "good": True}, {"cells": ["Export to CSV", "", "✓"], "good": True}],
     "say": "Your journal lives on your computer. No account, no cloud, daily backups, and you can export everything."},
    {"type": "shot", "img": "kpis", "title": "A desktop app for Windows and Mac.",
     "say": "A fast desktop app for Windows and Mac."},
    CTA("Private by design.")],
    "post": post("A private trading journal: your data stays on your computer", "No account, no cloud. Your trading journal lives on your computer, with daily backups and CSV export.",
                 ["#privacy", "#tradingtools"], "Private trading journal app for Windows and Mac")})

V.append({"id": "v013_long_short", "tag": TAG, "scenes": [
    {"type": "hook", "kicker": "Your edge", "text": "Long or short: where's your edge?",
     "say": "Long or short. Where's your edge, really?"},
    {"type": "rows", "title": "By side", "head": ["Side", "Trades", "Net P&L"],
     "rows": [{"cells": ["Long", "58", "+$1,119"]}, {"cells": ["Short", "31", "+$360"]}],
     "say": "In this example journal, longs made more in total, but there were almost twice as many of them."},
    {"type": "hook", "text": "Compare per trade, not just in total.",
     "say": "Compare per trade, not just in total. That's what average R is for."},
    ONECLICK, CTA()],
    "post": post("Long vs short: where is your trading edge?", "Compare long and short trades per trade, not just in total. Average R tells you where your edge really is.",
                 ["#tradingstrategy"], "Long vs short trading edge")})

V.append({"id": "v014_habit", "scenes": [
    {"type": "hook", "kicker": "Trading habit", "text": "A trading journal you'll actually keep.",
     "say": "A trading journal you'll actually keep."},
    {"type": "shot", "img": "add_trade", "title": "Ten fields. Thirty seconds.",
     "chips": [{"html": "<b>Date</b>"}, {"html": "<b>Entry</b>"}, {"html": "<b>Stop</b>"}, {"html": "<b>Exit</b>"}],
     "say": "Ten fields per trade. About thirty seconds after you close it."},
    {"type": "shot", "img": "kpis", "title": "Everything else fills in.",
     "say": "Dashboard, calendar, setups and mistakes fill in by themselves."},
    ONECLICK, CTA()],
    "post": post("A trading journal you'll actually keep", "Ten fields per trade, about 30 seconds. Dashboard, calendar, setups and mistakes fill in by themselves.",
                 ["#tradinghabits"], "Simple trading journal app")})

# ---------------------------------------------------------------- Prop Firm Manager ($29)
# Numbers: the app's example accounts (same as the product previews) or worked examples of the published rules.
PFM_LINK = "https://kallas8.gumroad.com/l/prop-firm-manager"
PFM_PAGE = "/prop-firm-manager/"
PFM_TAG = "Example accounts · demo data"
PFM_RULE_TAG = "Worked example · check your firm's current rules"
BUNDLE_LINK = "https://kallas8.gumroad.com/l/znfvjd"
PFM_TAGS = ["#propfirm", "#fundedtrader", "#futurestrading", "#daytrading", "#trading"]

CTA_PFM = lambda text="Every prop account, one calm screen.": {
    "type": "cta", "title": "Prop Firm Manager", "sub": "Desktop app · Windows & Mac", "text": text, "button": "Link in bio",
    "say": "Prop Firm Manager. Link in bio."}


def post_pfm(title, body, tags, pin=None):
    hashtags = " ".join(dict.fromkeys(tags + PFM_TAGS))
    tail = "Prop Firm Manager: desktop app for Windows & Mac. Loss limits, payouts, consistency and fees for Topstep, Apex, MFFU, Lucid, Tradeify and Take Profit Trader."
    return {
        "instagram": f"{body}\n\n{tail} Link in bio.\n\n{hashtags}",
        "tiktok": f"{body} {' '.join(dict.fromkeys(tags + PFM_TAGS[:3]))}",
        "youtube": {"title": f"{title} #shorts", "description": f"{body}\n\n{tail}\n{PFM_LINK}\n\nProp Trader Bundle (Prop Firm Manager + Trading Journal AI, $55): {BUNDLE_LINK}\n\nExample numbers. Not affiliated with any prop firm. Always check your firm's current rules. Not financial advice.\n\n{hashtags} #shorts"},
        "facebook": f"{body}\n\nProp Firm Manager (Windows & Mac): {PFM_LINK}\nBundle with Trading Journal AI, $55: {BUNDLE_LINK}",
        "pinterest": {"title": pin or title, "description": f"{body} Prop firm tracker app for Windows & Mac.", "link": PFM_LINK},
    }


V.append({"id": "v101_pfm_one_screen", "tag": PFM_TAG, "site_path": PFM_PAGE, "scenes": [
    {"type": "hook", "kicker": "Prop firm traders", "text": "Three accounts. Three loss limits. Do you know all of them right now?",
     "say": "Three prop accounts. Three loss limits. Do you know all of them, right now?"},
    {"type": "shot", "img": "pfm_card_apex", "title": "Your real loss limit, after every day.", "ring": "pfm_apex_room",
     "chips": [{"html": "Room <b>$2,760</b>", "color": "mint"}, {"html": "<b>Locked</b> at $50,100", "color": "blue"}],
     "say": "Log each day's result, and every account shows its real loss limit and how much room is left."},
    {"type": "shot", "img": "pfm_card_topstep", "title": "Targets, size and today's max.", "ring": "pfm_ts_facts",
     "say": "Evaluations show the target, the size you're allowed, and the most you can make today."},
    {"type": "shot", "img": "pfm_today", "title": "What matters today, first.", "ring": "pfm_today_first",
     "say": "And the most important thing for today is always at the top."},
    CTA_PFM()],
    "post": post_pfm("Every prop firm account on one screen", "Three prop accounts, three different loss limits. Log each day's result and see every account's real loss limit, room left and today's max.",
                     ["#topstep", "#apextraderfunding"], "Track all your prop firm accounts in one app")})

V.append({"id": "v102_pfm_eod_trailing", "tag": PFM_RULE_TAG, "site_path": "/learn/prop-firm-trailing-drawdown-explained/", "scenes": [
    {"type": "hook", "kicker": "Trailing drawdown", "text": "Your loss limit moves up. It never moves back down.",
     "say": "On a prop account, your loss limit moves up with you. It never moves back down."},
    {"type": "rows", "title": "50K account, $2,000 end-of-day trailing", "head": ["Day", "Close", "Loss limit"],
     "rows": [{"cells": ["Start", "$50,000", "$48,000"]}, {"cells": ["Day 1", "$50,800", "$48,800"], "good": True},
              {"cells": ["Day 2", "$50,300", "$48,800"], "hl": True}, {"cells": ["Day 3", "$52,100", "$50,100"], "good": True}],
     "say": "Close at fifty thousand eight hundred, and the limit climbs to forty eight thousand eight hundred. Lose five hundred the next day, and it stays there."},
    {"type": "hook", "kicker": "Then it locks", "text": "At $50,100: the starting balance + $100.",
     "say": "On many accounts it stops trailing at the starting balance plus one hundred dollars. From there, it's locked."},
    {"type": "shot", "img": "pfm_chart", "title": "Balance vs loss limit, day by day.",
     "say": "Prop Firm Manager replays every day with your firm's rules, so you always see the real number."},
    CTA_PFM("Know your real loss limit, every day.")],
    "post": post_pfm("Trailing drawdown explained in 30 seconds", "On a 50K account with a $2,000 end-of-day trailing drawdown, the loss limit follows your best close and never moves back down. On many accounts it locks at the starting balance + $100.",
                     ["#drawdown", "#riskmanagement"], "Prop firm trailing drawdown explained")})

V.append({"id": "v103_pfm_intraday", "tag": PFM_RULE_TAG, "site_path": "/learn/prop-firm-trailing-drawdown-explained/", "scenes": [
    {"type": "hook", "kicker": "Intraday drawdown", "text": "You closed green. Your loss limit still went up.",
     "say": "You closed the day green. And your loss limit still went up more than you think."},
    {"type": "rows", "title": "50K account, $2,000 intraday trailing", "head": ["Moment", "Balance", "Loss limit"],
     "rows": [{"cells": ["Open", "$50,000", "$48,000"]}, {"cells": ["Day's high", "$50,900", "$48,900"], "hl": True},
              {"cells": ["Close", "$50,200", "$48,900"]}],
     "say": "Intraday accounts trail your highest balance, open profit included. A high of fifty thousand nine hundred pulls the limit to forty eight thousand nine hundred."},
    {"type": "stat", "label": "Room left at the close", "value": 1300, "prefix": "$", "color": "gold", "sub": "not $2,200",
     "say": "So at the close you have thirteen hundred dollars of room. Not twenty two hundred."},
    {"type": "hook", "text": "Log your close and the day's high. The app does the rest.",
     "say": "Type your close and the day's high. Prop Firm Manager does the rest."},
    CTA_PFM()],
    "post": post_pfm("Intraday trailing drawdown: the trap", "On intraday accounts the loss limit trails your highest balance, open profit included. A high of $50,900 moves the limit to $48,900, even if you close at $50,200.",
                     ["#drawdown", "#riskmanagement"], "Intraday trailing drawdown explained")})

V.append({"id": "v104_pfm_consistency", "tag": PFM_RULE_TAG, "site_path": PFM_PAGE, "scenes": [
    {"type": "hook", "kicker": "Consistency rule", "text": "A great day can push your target further away.",
     "say": "A great day can push your profit target further away."},
    {"type": "rows", "title": "50K evaluation, $3,000 target, 55% rule", "head": ["Best day", "Of target", "Target"],
     "rows": [{"cells": ["$1,500", "50%", "$3,000"], "good": True}, {"cells": ["$1,650", "55%", "$3,000"], "good": True},
              {"cells": ["$1,800", "60%", "$3,273"], "hl": True}],
     "say": "If your best day is more than fifty five percent of the target, the target rises to best day divided by point fifty five. Eighteen hundred dollars makes it three thousand two hundred and seventy three."},
    {"type": "shot", "img": "pfm_today", "title": "Today's max, before you trade.", "ring": "pfm_today_first",
     "say": "Prop Firm Manager tells you today's max before you start. Here, sixteen hundred and fifty dollars."},
    CTA_PFM("Know today's max before you trade.")],
    "post": post_pfm("The consistency rule that moves your target", "With a 55% consistency rule on a $3,000 target, a $1,800 best day raises the target to $3,273. Know today's max before you trade.",
                     ["#topstep", "#consistency"], "Prop firm consistency rule explained")})

V.append({"id": "v105_pfm_payout", "tag": PFM_TAG, "site_path": PFM_PAGE, "scenes": [
    {"type": "hook", "kicker": "Payouts", "text": "Can you request a payout today? How much?",
     "say": "Can you request a payout today? And how much?"},
    {"type": "shot", "img": "pfm_payout", "title": "Every payout condition, checked.", "ring": "pfm_gate_days",
     "chips": [{"html": "Days <b>4 / 5</b>", "color": "gold"}, {"html": "Now <b>$760</b>", "color": "mint"}],
     "say": "Every condition is checked for you. Here, four qualifying days out of five, and seven hundred and sixty dollars above the safety net."},
    {"type": "shot", "img": "pfm_log_apex", "title": "Type today's result. See what changes.", "ring": "pfm_pv_apex",
     "say": "Type today's result before you save it. Three hundred dollars more, and the payout is ready: up to one thousand and sixty."},
    {"type": "stat", "label": "Payout ready", "value": 1060, "prefix": "$", "color": "mint", "sub": "5 / 5 qualifying days",
     "say": "No spreadsheets, no guessing."},
    CTA_PFM("Know when, and how much, to withdraw.")],
    "post": post_pfm("Prop firm payout: when and how much", "Qualifying days, buffer, consistency and payout caps, checked for you. In this example, one more $300 day makes the payout ready: up to $1,060.",
                     ["#payout", "#apextraderfunding"], "Prop firm payout checklist app")})

V.append({"id": "v106_pfm_is_it_paying", "tag": PFM_TAG, "site_path": PFM_PAGE, "scenes": [
    {"type": "hook", "kicker": "The honest number", "text": "Are prop firms paying you, or are you paying them?",
     "say": "Are prop firms paying you? Or are you paying them?"},
    {"type": "shot", "img": "pfm_money_kpis", "title": "Fees in, payouts out.", "ring": "pfm_money_net",
     "say": "Every evaluation, reset and activation fee, against every payout you actually received."},
    {"type": "stat", "label": "Return on fees", "value": 186.4, "decimals": 1, "suffix": "%", "color": "mint", "sub": "$660 spent · $1,890 received",
     "say": "In this example, six hundred and sixty dollars spent, eighteen hundred and ninety received."},
    {"type": "shot", "img": "pfm_money_firms", "title": "Firm by firm.",
     "say": "Firm by firm, so you know where your money really goes."},
    CTA_PFM("The honest number on your prop trading.")],
    "post": post_pfm("Are prop firms paying you, or are you paying them?", "Track every evaluation, reset and activation fee against the payouts you actually received. In this example: $660 spent, $1,890 received, ROI on fees 186.4%.",
                     ["#fundedtrader"], "Track prop firm fees and payouts")})

V.append({"id": "v107_pfm_alerts_ai", "site_path": PFM_PAGE, "scenes": [
    {"type": "hook", "kicker": "Never miss a deadline", "text": "Evaluation expiring. Subscription renewing. Payout ready.",
     "say": "Evaluation about to expire. Subscription about to renew. Payout ready."},
    {"type": "shot", "img": "pfm_alerts", "title": "Desktop notifications. Each one optional.",
     "say": "Prop Firm Manager sends a desktop notification for each one. Turn off what you don't need."},
    {"type": "shot", "img": "pfm_ai", "title": "Ask your own AI, with your numbers.", "ring": "pfm_ai_btn",
     "chips": [{"text": "Claude", "color": "mint"}, {"text": "ChatGPT", "color": "blue"}, {"text": "Gemini", "color": "gold"}],
     "say": "And one click opens your own AI with the account and its rules already written in."},
    CTA_PFM("Rules, deadlines and payouts, handled.")],
    "post": post_pfm("Never miss a prop firm deadline again", "Desktop notifications before an evaluation expires, before a subscription renews, when a payout is ready and when you're close to the loss limit. Each one optional.",
                     ["#tradingtools"], "Prop firm deadline reminders app")})

V.append({"id": "v108_pfm_rules", "site_path": PFM_PAGE, "scenes": [
    {"type": "hook", "kicker": "Prop firm rules", "text": "89 account types. 6 firms. Rules checked at the source.",
     "say": "Eighty nine account types, from six prop firms, checked against their official help centers."},
    {"type": "shot", "img": "pfm_rule_card", "title": "Every rule, in plain English.",
     "chips": [{"text": "Topstep", "color": "mint"}, {"text": "Apex", "color": "blue"}, {"text": "MFFU", "color": "gold"}],
     "say": "Drawdown, size, consistency, payouts and inactivity, in plain English."},
    {"type": "hook", "text": "Rules change? The app checks for updated cards.",
     "say": "When a firm changes its rules, the app checks for updated cards. Or edit any card yourself."},
    CTA_PFM("Topstep · Apex · MFFU · Lucid · Tradeify · TPT")],
    "post": post_pfm("Prop firm rules in plain English", "89 account types from Topstep, Apex, MyFundedFutures, Lucid, Tradeify and Take Profit Trader, checked against their official help centers. Edit any card yourself.",
                     ["#topstep", "#apextraderfunding", "#myfundedfutures"], "Prop firm rules compared")})


# ---------------------------------------------------------------- educational series (content/edu.py)
import sys as _sys
_sys.path.insert(0, str(pathlib.Path(__file__).parent))
import edu as _edu
V.extend(_edu.V)
import carousels as _car  # first carousels mirrored the reels: retired, only the published one stays online
V.extend(c for c in _car.C if c["id"] in ("c202_car_20ema",))
import longform as _long  # y301 (same topics as the reels) retired; long lessons now live in strategies.py
import strategies as _strat  # strategies, market mechanics and routines: topics the reels don't cover
V.extend(_strat.C)
V.extend(_strat.Y)
import strategy_carousels as _scar  # carousels v2: step by step on TradingView-style charts
V.extend(_scar.C)
import quiz as _quiz  # after carousels/longform, which read the original lesson scenes

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for v in V:
        v.setdefault("voice", "andrew_up")
        (OUT / f"{v['id']}.json").write_text(json.dumps(v, indent=1, ensure_ascii=False))
    print(len(V), "videos written")
