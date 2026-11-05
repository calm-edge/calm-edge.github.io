"""Illustrative price charts for the educational videos.

A chart is drawn from waypoints (bar index -> price), so each one has exactly the shape the lesson needs,
plus deterministic noise (same seed, same chart, every render). Indicators are computed from the candles
with the standard formulas, so every number a video says about the chart is true for the chart it shows.
Tests: python3 marketing/content/test_charts.py"""
import math, random

# ---------------------------------------------------------------- price paths


def path(waypoints, seed=1, noise=0.25, wick=0.35, force=None, vol_base=1000):
    """waypoints: [(bar, price), ...] from bar 0 to the last bar. Returns candles [{o,h,l,c,v}].
    `noise` and `wick` are in price units; `force` = {bar: {"o":..,"h":..,"l":..,"c":..}} sets exact values."""
    rnd = random.Random(seed)
    n = waypoints[-1][0] + 1
    base = []
    for (i0, p0), (i1, p1) in zip(waypoints, waypoints[1:]):
        for i in range(i0, i1):
            base.append(p0 + (p1 - p0) * (i - i0) / (i1 - i0))
    base.append(waypoints[-1][1])
    out, prev, drift = [], base[0], 0.0
    for i in range(n):
        drift = 0.55 * drift + rnd.gauss(0, noise)
        c = base[i] + drift
        if i in (0, n - 1) or any(i == w[0] for w in waypoints):
            c = base[i]  # the shape's turning points land exactly on the waypoint
        o = prev + rnd.gauss(0, noise * 0.15)
        h = max(o, c) + abs(rnd.gauss(0, wick))
        l = min(o, c) - abs(rnd.gauss(0, wick))
        v = vol_base * (0.7 + 0.6 * rnd.random()) * (1 + 3 * abs(c - o) / max(noise, 1e-9) / 4)
        bar = {"o": o, "h": h, "l": l, "c": c, "v": v}
        if force and i in force:
            bar.update(force[i])
            bar["h"] = max(bar["h"], bar["o"], bar["c"]); bar["l"] = min(bar["l"], bar["o"], bar["c"])
        out.append(bar)
        prev = bar["c"]
    return [{k: round(x, 2) if k != "v" else round(x) for k, x in b.items()} for b in out]


# ---------------------------------------------------------------- indicators (None until warmed up)


def closes(c):
    return [b["c"] for b in c]


def sma(xs, n):
    return [None if i < n - 1 else sum(xs[i - n + 1:i + 1]) / n for i in range(len(xs))]


def ema(xs, n):
    """Seeded with the simple average of the first n values, then k = 2 / (n + 1)."""
    out, k, e = [], 2 / (n + 1), None
    for i, x in enumerate(xs):
        if x is None:
            out.append(None); continue
        if e is None:
            window = [v for v in xs[:i + 1] if v is not None]
            if len(window) < n:
                out.append(None); continue
            e = sum(window[-n:]) / n
        else:
            e = x * k + e * (1 - k)
        out.append(e)
    return out


def rsi(xs, n=14):
    """Wilder's RSI: first average = simple mean of n changes, then smoothed (avg * (n-1) + new) / n."""
    out = [None] * len(xs)
    if len(xs) <= n:
        return out
    ch = [xs[i] - xs[i - 1] for i in range(1, len(xs))]
    g = sum(max(c, 0) for c in ch[:n]) / n
    l = sum(max(-c, 0) for c in ch[:n]) / n
    val = lambda g, l: 100.0 if l == 0 else 100 - 100 / (1 + g / l)
    out[n] = val(g, l)
    for i in range(n, len(ch)):
        g = (g * (n - 1) + max(ch[i], 0)) / n
        l = (l * (n - 1) + max(-ch[i], 0)) / n
        out[i + 1] = val(g, l)
    return out


def bollinger(xs, n=20, k=2.0):
    """Middle = SMA(n); bands = middle +/- k * population standard deviation of the same n closes."""
    mid, up, lo = [], [], []
    for i in range(len(xs)):
        if i < n - 1:
            mid.append(None); up.append(None); lo.append(None); continue
        w = xs[i - n + 1:i + 1]; m = sum(w) / n
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / n)
        mid.append(m); up.append(m + k * sd); lo.append(m - k * sd)
    return mid, up, lo


def vwap(c):
    """Session VWAP from the first bar: cumulative (typical price x volume) / cumulative volume."""
    pv = vol = 0.0; out = []
    for b in c:
        tp = (b["h"] + b["l"] + b["c"]) / 3
        pv += tp * b["v"]; vol += b["v"]; out.append(pv / vol)
    return out


def atr(c, n=14):
    """Wilder's ATR: true range = max(h-l, |h-prev c|, |l-prev c|), first value = mean of n TRs."""
    tr = [c[0]["h"] - c[0]["l"]] + [max(b["h"] - b["l"], abs(b["h"] - p["c"]), abs(b["l"] - p["c"])) for p, b in zip(c, c[1:])]
    out = [None] * len(c)
    if len(c) < n:
        return out
    a = sum(tr[:n]) / n; out[n - 1] = a
    for i in range(n, len(c)):
        a = (a * (n - 1) + tr[i]) / n; out[i] = a
    return out


def macd(xs, fast=12, slow=26, signal=9):
    f, s = ema(xs, fast), ema(xs, slow)
    line = [None if a is None or b is None else a - b for a, b in zip(f, s)]
    sig = ema(line, signal)
    hist = [None if a is None or b is None else a - b for a, b in zip(line, sig)]
    return line, sig, hist


def stochastic(c, n=14, d=3):
    """Stochastic oscillator: %K = (close - lowest low of n bars) / (highest high - lowest low) x 100; %D = SMA(d) of %K."""
    k = [None] * len(c)
    for i in range(n - 1, len(c)):
        w = c[i - n + 1:i + 1]; lo, hi = min(b["l"] for b in w), max(b["h"] for b in w)
        k[i] = 50.0 if hi == lo else (c[i]["c"] - lo) / (hi - lo) * 100
    dl = [None if i < n + d - 2 else sum(k[i - d + 1:i + 1]) / d for i in range(len(c))]
    return k, dl


def r2(xs):
    return [None if x is None else round(x, 3) for x in xs]


# ---------------------------------------------------------------- helpers for writing true captions


def first(cond, start=0, end=None, xs=None):
    """First bar index >= start where cond(i) is true."""
    end = len(xs) if end is None and xs is not None else end
    for i in range(start, end):
        if cond(i):
            return i
    raise ValueError("condition never true: the lesson's claim does not hold on this chart")
