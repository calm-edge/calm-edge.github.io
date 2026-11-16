---
{"slug": "vwap-explained", "date": "2026-11-16", "minutes": 6,
 "title": "VWAP explained: the intraday line that weighs every trade by volume",
 "seo_title": "VWAP explained: how it's calculated and how day traders use it",
 "description": "What the volume-weighted average price is, how to calculate it bar by bar, why it resets every session, and the three common ways day traders use it, with the limits to know.",
 "faq": [
  ["What is the difference between VWAP and a moving average?", "A moving average gives every bar the same weight and looks back a fixed number of bars. VWAP weights each price by the volume traded there and starts from the open of the session, so it grows to include every bar of the day and resets the next morning."],
  ["Does VWAP work on daily or weekly charts?", "Standard VWAP is an intraday tool because it resets each session. On higher timeframes traders use an anchored VWAP instead, which starts from a point they choose, such as an earnings day or a major swing low."],
  ["Is price above VWAP a buy signal?", "No. Above VWAP only says the average participant today paid less than the current price. Many traders use it as a filter or a reference level, not as a trigger on its own."]
 ]}
---
Moving averages treat a bar where ten contracts traded the same as a bar where ten thousand did. The **volume-weighted average price (VWAP)** fixes that: it is the average price of the session, with each price counted as many times as it actually traded. That's why many day traders keep it on every intraday chart.

## What VWAP measures

VWAP answers a simple question: **what has the average participant paid today?** If price sits above VWAP, buyers who entered during the session are, on average, in profit; below it, they are on average underwater.

Large funds often use VWAP as an execution benchmark: a buy order filled below the day's VWAP is usually considered a good fill. Because so many participants watch the same line, price often reacts around it.

## How VWAP is calculated

Each bar contributes its **typical price** multiplied by its volume:

<div class="formula">Typical price = (high + low + close) ÷ 3</div>

<div class="formula">VWAP = Σ (typical price × volume) ÷ Σ volume, from the session open</div>

Both sums are **cumulative**: they start at the first bar of the session and keep growing until the close. Here are the first four 5-minute bars of a made-up session:

| Bar | High | Low | Close | Volume | Typical price | Running VWAP |
|---|---|---|---|---|---|---|
| 1 | 101.00 | 99.00 | 100.50 | 1,200 | 100.17 | 100.17 |
| 2 | 101.50 | 100.20 | 101.20 | 800 | 100.97 | 100.49 |
| 3 | 101.30 | 100.40 | 100.60 | 1,000 | 100.77 | 100.58 |
| 4 | 100.90 | 99.80 | 100.00 | 1,500 | 100.23 | 100.46 |

Notice bar 4: its typical price is close to bar 1's, but it carried the most volume, so it pulls VWAP down more than bar 2 pushed it up. That's the volume weighting at work.

## Why it resets every session

VWAP starts fresh at each session open. In the first minutes it moves a lot, because only a few bars are in the average. By the afternoon thousands of bars and a large cumulative volume are behind it, so **late in the day VWAP barely moves**. For 24-hour markets like crypto, charting platforms typically reset it at a fixed time such as midnight UTC; check what your platform uses.

If you want the same idea over several days, use an **anchored VWAP**: the same formula, but started from a bar you choose, like a breakout day or an earnings gap.

## Three common ways traders use VWAP

1. **Trend filter.** Some traders only look for longs while price holds above VWAP and only shorts below it. It doesn't predict anything; it just keeps them on the side the session's average participant is profitable on.
2. **Pullback level in a trend.** On trending days price often pulls back toward VWAP before continuing. Traders who use this wait for price to reach the line and show a reaction (a rejection candle, a higher low) before entering, with the stop beyond the line.
3. **Mean reversion with bands.** Many platforms draw standard-deviation bands around VWAP. On quiet, range-bound days, stretches to the outer bands tend to snap back toward VWAP. On trending days the same stretch can keep going, so this approach needs a way to tell the two days apart.

Whatever the approach, the stop and the size still come first: decide the dollar risk, place the stop where the idea is wrong, and let the [position size calculator](/tools/position-size-calculator/) turn that into a number of contracts or shares.

{{app}}

## What can go wrong

- **VWAP lags late in the session.** By the afternoon it reflects the whole day, so it reacts slowly to a fresh move.
- **Trend days ignore it.** On strong trend days price can stay far from VWAP for hours; fading every stretch can mean several losses in a row.
- **Thin volume distorts it.** Pre-market or holiday sessions with little volume make the early VWAP jumpy and less meaningful.
- **Different settings, different lines.** Whether your chart includes extended hours changes the value. Make sure you compare like with like.

## How to test whether VWAP helps you

1. Tag each trade in your journal with where price was relative to VWAP at entry: above, below, or at the line.
2. After 30 to 50 trades, compare the average result in R for each group. The [R-multiple guide](/learn/r-multiple-explained/) explains why R makes the groups comparable.
3. If trades against VWAP lose consistently, a simple filter may help. If there's no difference, VWAP isn't adding anything to your setup, and that's useful to know too. The [expectancy guide](/learn/trading-expectancy-explained/) shows how to judge whether a change actually improved your numbers.

*Educational content, not financial advice.*
