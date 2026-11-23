---
{"slug": "rsi-divergence-explained", "date": "2026-11-23", "minutes": 6,
 "title": "RSI divergence explained: when price and momentum disagree",
 "seo_title": "RSI divergence explained: bullish, bearish and hidden divergence",
 "description": "What RSI divergence is, how to spot regular and hidden divergence step by step, why it is a warning rather than an entry signal, and how traders add confirmation and a stop.",
 "faq": [
  ["Is RSI divergence a reliable signal?", "It is a useful warning, not a reliable trigger on its own. In strong trends divergence can appear several times in a row while price keeps going. Most traders wait for a confirmation such as a break of structure before acting on it."],
  ["What is the difference between regular and hidden divergence?", "Regular divergence hints that a trend may be losing strength and is often read as a possible reversal warning. Hidden divergence appears during pullbacks inside a trend and is often read as a sign the trend may continue."],
  ["Which RSI setting is best for divergence?", "The classic setting is 14 periods, introduced by J. Welles Wilder. Shorter settings produce more divergences and more false ones; longer settings produce fewer. Keep one setting so your results stay comparable."]
 ]}
---
Price makes a new high. Everyone watching the chart feels the trend is strong. But the momentum underneath it is getting weaker, and the RSI shows it with a **lower high**. That disagreement between price and the indicator is called **divergence**, and it's one of the most discussed ideas in technical analysis. It's also one of the most misused.

## A quick reminder: what RSI measures

The Relative Strength Index compares the size of recent up moves with the size of recent down moves and scales the result between 0 and 100. The classic setting looks back **14 bars**.

<div class="formula">RSI = 100 − 100 ÷ (1 + average gain ÷ average loss)</div>

When up moves dominate, RSI rises; when down moves dominate, it falls. So RSI is a measure of **momentum**: not where price is, but how forcefully it has been moving.

## What divergence means

Normally price and momentum move together. A new high in price comes with a new high in RSI, because the latest push up was strong. Divergence is when the two **stop agreeing**:

- Price makes a **higher high**, RSI makes a **lower high**: the second push was weaker than the first.
- Price makes a **lower low**, RSI makes a **higher low**: the second drop had less force than the first.

Divergence doesn't say price will turn. It says the move is **losing steam**, which is information worth having before you add to a position or chase a breakout.

## The four types

| Type | Price | RSI | Common reading |
|---|---|---|---|
| Regular bearish | Higher high | Lower high | Uptrend may be weakening |
| Regular bullish | Lower low | Higher low | Downtrend may be weakening |
| Hidden bearish | Lower high | Higher high | Downtrend may continue |
| Hidden bullish | Higher low | Lower low | Uptrend may continue |

Regular divergence is the one most people mean. Hidden divergence shows up during **pullbacks inside a trend**: price holds a higher low while RSI dips lower, which many traders read as the pullback being shallow compared with the momentum it burned.

## How to spot it step by step

1. **Find two clear swing points** in price, like two obvious highs a few bars apart. Small wiggles don't count.
2. **Draw a line connecting them** on the price chart.
3. **Look at RSI at the same two bars** and connect those peaks too.
4. **Compare the slopes.** If one line points up and the other points down, you have divergence.

The most common mistake is comparing RSI peaks that don't line up with the price swings. Always compare the indicator **at the same bars** as the price highs or lows.

## Why divergence alone isn't an entry

In a strong trend, RSI can diverge two or three times while price keeps grinding higher. Each divergence looked like a top; none of them was. Momentum can fade without the trend reversing, because a market can rise slowly as well as quickly.

That's why many traders treat divergence as a **warning light**, then wait for price itself to confirm:

- **A break of structure:** for a bearish divergence, price closes below the last higher low.
- **A trendline break** on the price chart.
- **A failed retest** of the high that formed the divergence.

Until one of those happens, the trend is still the trend.

{{app}}

## Where the stop goes

If you do act on a confirmed bearish divergence, the swing high that formed it gives you a natural invalidation point. A common approach is to place the stop **just beyond that high**, then size the position from the stop distance so the dollar risk is fixed in advance. The [position size calculator](/tools/position-size-calculator/) does the arithmetic, and the [R-multiple guide](/learn/r-multiple-explained/) explains why measuring results in R makes different stop distances comparable.

For targets, many traders look at the last swing low or a nearby support level, and check that the reward is at least as large as the risk before taking the trade.

## What can go wrong

- **Trend strength overrides it.** The stronger the trend, the more divergences it can absorb.
- **Timeframe mismatch.** A divergence on a 1-minute chart means little against a strong trend on the daily chart.
- **Hindsight.** Divergence looks obvious on old charts because you already know which one worked. In real time you only know a swing is complete after price moves away from it.
- **Too many signals.** On short RSI settings, divergences appear constantly. More signals doesn't mean more edge.

## How to test it on your own trades

Before relying on divergence, check whether it actually helps your strategy:

1. Mark the last 30 to 50 divergences on the market and timeframe you trade, in real-time order.
2. Note which ones were followed by a confirmation, and what happened next.
3. Record each hypothetical trade in R: entry after confirmation, stop beyond the swing, a fixed target.

If the results only look good with hand-picked examples, divergence isn't adding much. If confirmed divergences show a positive [expectancy](/learn/trading-expectancy-explained/) over a decent sample, you've found something worth logging and tracking trade by trade.

*Educational content, not financial advice.*
