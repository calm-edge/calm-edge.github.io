---
{"slug": "atr-stop-loss-explained", "date": "2026-11-09", "minutes": 6,
 "title": "ATR stop loss explained: place stops outside the noise",
 "seo_title": "ATR stop loss: how to use Average True Range for stops",
 "description": "What the Average True Range measures, how to calculate it, how to place an ATR-based stop, and how to size the position so the dollar risk stays the same.",
 "faq": [
  ["What is a good ATR multiple for a stop loss?", "Common choices sit between 1 and 3 ATR, with 1.5 to 2 ATR a frequent starting point. There's no universal best value: it depends on your timeframe, your market and your strategy's targets, so test the multiple on your own trades."],
  ["Which ATR period should I use?", "14 periods is the classic default from J. Welles Wilder, who introduced the indicator. Shorter periods react faster to changes in volatility, longer ones are smoother. Pick one and keep it constant so your results stay comparable."],
  ["Does a wider ATR stop mean more risk?", "Not if you size from the stop. A wider stop with a proportionally smaller position risks the same number of dollars. What changes is how often ordinary noise stops you out."]
 ]}
---
Most stops don't get hit because the trade idea was wrong. They get hit because they were placed **inside the normal noise** of the market: the ordinary back-and-forth that happens on every chart, every day. The Average True Range (ATR) is a simple way to measure that noise and put your stop outside it.

## What ATR measures

ATR tells you **how far price typically moves in one bar** on the timeframe you're watching. It doesn't say anything about direction. A rising ATR means bars are getting bigger; a falling ATR means the market is quieter.

It starts from the **true range** of each bar, which is the largest of three distances:

<div class="formula">True range = max(high − low, |high − previous close|, |low − previous close|)</div>

The second and third terms matter when price gaps: a bar that opens far from the previous close has moved more than its own high-low shows. ATR is then an average of the true range, classically over **14 bars**.

## Why fixed stops fail

A 10-point stop can be generous on a quiet day and tiny on a busy one. The same distance means different things depending on volatility. That's why many traders get stopped out repeatedly in fast markets and then watch price go exactly where they expected.

Measuring the stop in ATR adapts it automatically: **on volatile days the stop widens, on quiet days it tightens**.

## How to place an ATR stop

1. **Read the ATR** at the moment of entry, on the timeframe you trade.
2. **Choose a multiple.** Common values sit between 1 and 3 ATR; 1.5 to 2 is a frequent starting point.
3. **Subtract it from the entry for a long** (add it for a short).

<div class="formula">Long stop = entry − (multiple × ATR)&nbsp;&nbsp;·&nbsp;&nbsp;Short stop = entry + (multiple × ATR)</div>

Example: you buy at 100.00 and the 14-period ATR is 0.80.

| Multiple | Stop distance | Stop price |
|---|---|---|
| 0.5 ATR | 0.40 | 99.60 |
| 1.0 ATR | 0.80 | 99.20 |
| 1.5 ATR | 1.20 | 98.80 |
| 2.0 ATR | 1.60 | 98.40 |

At half an ATR, an ordinary bar can reach the stop. At 1.5 ATR, price needs a move bigger than a typical bar to get there. That's a much stronger sign the trade is actually wrong.

Many traders combine ATR with structure: they place the stop beyond the last swing low and then check that it is at least 1 ATR away. If the swing is closer than that, the stop is probably sitting in the noise.

## Wider stop, smaller size

The obvious objection: a wider stop means a bigger loss. Only if you keep the same size. The rule is to **decide the dollar risk first and let the stop decide the size**:

<div class="formula">Position size = dollar risk ÷ (stop distance × value per point)</div>

With $200 of risk on the Micro E-mini S&P (MES), at $5 a point:

- **ATR 8 points, stop at 1.5 ATR = 12 points.** One contract risks $60, so 200 ÷ 60 = 3.3, round down to **3 contracts**.
- **ATR 16 points, stop at 1.5 ATR = 24 points.** One contract risks $120, so **1 contract**.

The dollar risk stays at or below $200 either way. On the volatile day you simply trade smaller. The [position size calculator](/tools/position-size-calculator/) does this division for you, and the [futures sizing guide](/learn/position-sizing-futures/) has more examples.

{{app}}

## ATR for targets and trailing stops

ATR works for exits too:

- **Targets:** if your stop is 1.5 ATR, a 2R target is 3 ATR away. Expressing both in ATR keeps the ratio constant as volatility changes.
- **Trailing stops:** a "chandelier" style stop trails at a fixed multiple of ATR below the highest price since entry. It gives the trend room in volatile phases and tightens when the market calms down.
- **Filters:** some traders skip setups when ATR is unusually high compared with its recent average, because stops get wide and positions get small.

## What can go wrong

- **ATR lags.** It's an average of past bars, so after a sudden volatility spike it takes a while to catch up.
- **Too wide is also a problem.** A 4 ATR stop rarely gets hit by noise, but the position becomes tiny and the target far away.
- **Changing the multiple trade by trade** defeats the purpose. Choose one and test it.
- **Gaps ignore stops.** A stop order limits the loss in normal conditions, but overnight gaps or fast news can fill it worse than planned.

## How to test your multiple

1. Pull your last 50 or more trades and note the ATR at each entry.
2. Measure how far each trade went against you before working (the maximum adverse excursion) in ATR units.
3. If most winners dipped 0.8 ATR before running, a 0.5 ATR stop was cutting good trades. Log the results in R so different stop sizes compare fairly; the [R-multiple guide](/learn/r-multiple-explained/) explains why.

A journal that records entry, stop and the ATR at the time turns this from guesswork into a quick check.

*Educational content, not financial advice.*
