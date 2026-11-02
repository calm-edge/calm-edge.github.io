---
{"slug": "opening-range-breakout-strategy", "date": "2026-11-02", "minutes": 7,
 "title": "Opening range breakout: the complete rules, with a winning and a losing day",
 "seo_title": "Opening range breakout strategy: rules, stop, target and sizing",
 "description": "How the opening range breakout works: how to mark the range, entry, stop and target rules, the filters traders add, how to size it from the stop, and how to test it before trading it.",
 "faq": [
  ["What is the opening range in trading?", "It's the high and low of the first minutes after the market opens. Many day traders use the first 30 minutes; others use 5 or 15. What matters is picking one window and always using the same one."],
  ["Where do you put the stop on an opening range breakout?", "Back inside the range, where the breakout idea is wrong. Common choices are the opposite side of the range or its midpoint. The midpoint keeps the stop closer, so the position can be larger for the same dollar risk."],
  ["What win rate does a 2R opening range breakout need?", "With a target twice the size of the stop, you break even before costs at a win rate of about 33%: 1 ÷ (1 + 2). Fees, slippage and time exits push that number up a little, so measure it on your own trades."]
 ]}
---
The **opening range breakout** (ORB) is one of the oldest day trading strategies there is. The rules fit on an index card, the risk is defined before you enter, and you know within a few hours whether you were right. It's also a strategy that fails often, which is exactly why the way you manage risk matters more than the entry.

This guide walks through one complete version of the rules, a day when it works, a day when it doesn't, and how to test it before you trade it. Education only, not financial advice.

## What the opening range is

The first minutes after the open are usually the busiest of the day. That burst of activity sets a **high** and a **low**: the opening range.

Traders measure it over a fixed window. Here we use the **first 30 minutes**, or six five-minute candles. Some use 5 or 15 minutes. There's no magic number; what matters is choosing one and always using the same one, so your results are comparable.

## The logic behind the breakout

While price stays inside the range, buyers and sellers are still fighting over the open. When a candle **closes** outside it, one side has won that first battle, and the move often continues in that direction. Often, not always. The strategy doesn't need every breakout to work; it needs the losers to stay small and the winners to run.

## One version of the rules

| Rule | Long version |
|---|---|
| Range | High and low of the first 30 minutes |
| Entry | A five-minute candle closes above the range high |
| Stop | The midpoint of the range |
| Target | 2× the risk (2R) |
| Time limit | Flat by midday if neither is hit |

Shorts are the mirror image: a close below the range low, the same midpoint stop, the same 2R target.

**Why the midpoint and not the range low?** A stop at the far side of the range can be very wide, and a wide stop means a tiny position. The midpoint is a compromise: far enough to survive a normal retest of the breakout, close enough to keep the risk reasonable. If price gets back to the middle of the range, the breakout has clearly failed.

**Why a close and not a touch?** Price pokes through the range high all the time and comes straight back. Waiting for a close filters out some of those pokes.

## A day when it works

Picture a range from 100.00 to 101.20, so the midpoint is 100.60. Price spends a few more candles inside the range, then a candle closes above the high at, say, 101.40. That's the entry.

- **Risk** = 101.40 − 100.60 = 0.80 points
- **Target** = 101.40 + 2 × 0.80 = 103.00

Then comes the hard part: doing nothing. Price pulls back toward the range high but never reaches the midpoint, and it takes a couple of hours to reach the target. Plenty of traders would have taken a small profit long before, and that habit quietly destroys the math of a 2R strategy.

## A day when it doesn't

Same range, same kind of candle closing above the high, same entry, stop and target. This time buyers can't hold it. Price falls back into the range and hits the midpoint a few candles later: **−1R**. And often price keeps falling after that. Without the stop, a normal loss becomes a big one.

That's the whole structure. You will have days like this one, sometimes several in a row. The question is whether your losses really stay at 1R.

## The math that makes it work

With a target twice the size of the stop, the break-even win rate before costs is:

<div class="formula">1 ÷ (1 + 2) ≈ 33%</div>

You can be wrong on most trades and still not lose money, but only if two things are true: the losses really stay at −1R, and the winners really get to +2R. Moving the stop "just this once" or grabbing a quick +0.5R breaks the math. If you want to see how win rate and average win/loss combine, the article on [trading expectancy](/learn/trading-expectancy-explained/) works through it.

{{app}}

## Filters traders add

Most traders add a few filters on top of the basic rules:

- **Range too wide:** if today's range is much wider than usual, the stop is far and the position small. Many skip the day.
- **Direction:** take long breakouts only when price is above VWAP and the moving averages point up, and shorts only in the opposite case.
- **News:** a big data release inside the window can whip price through both sides of the range, so some traders wait for it.
- **Time:** breakouts late in the morning tend to have less volume behind them. No new entries after midday.

One warning: it's tempting to look at past charts and add a filter for every losing day until the results look perfect. That's curve fitting, and it usually stops working the moment you go live. Choose a few filters that make sense, then test them.

## Sizing from the stop

Decide the dollars you risk per trade first, then let the stop decide the size:

<div class="formula">Contracts = dollar risk ÷ (stop in points × point value)</div>

With $200 of risk and an 8-point stop on the Micro E-mini S&P (MES), at $5 a point, one contract risks $40, so you trade **5 contracts**. On a wider day, with a 16-point stop, you'd trade half as many. The dollar risk stays the same. The [position sizing guide for futures](/learn/position-sizing-futures/) has more examples.

Limit the day too: one trade, maybe two if the first stops out and the other side breaks. Never re-enter bigger to win it back, and decide your maximum daily loss before the open.

## How to test it yourself

1. **Write the rules down** before looking at any chart.
2. **Go back at least 50 trading days** on your market and apply them to every day, including the ugly ones.
3. **Log every trade in R**: +2, −1, or the time exit. The article on [R multiples](/learn/r-multiple-explained/) explains why R beats dollars here.
4. **Then trade it small**, with micros, to see real fills and your own discipline.

What you're measuring is simple: the win rate, the average result in R, and the longest losing streak. If the numbers hold up and you can follow the rules through five losses in a row, you have something worth trading. If not, you've learned that cheaply.
