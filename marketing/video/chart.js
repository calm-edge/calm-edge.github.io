// Candlestick chart drawn as SVG in the style of TradingView's dark theme, shared by the video player, the
// carousels/pins (still.html) and the YouTube lessons.
// drawChart(svgHost, chart, box, state) draws one frame; everything is a pure function of `state`.
//   chart: { candles:[{o,h,l,c,v}], lines:[{id,label,color,values,dash}], bands:[{id,label,upper,lower,color}],
//            panel:{label,min,max,lines:[{id,color,values}],levels:[{y,label}],hist:{id,values}},
//            symbol: "EXAMPLE", tf: "5m", time: {start:"09:30", step:5} (intraday time axis, optional) }
//   box:   { x, y, w, h }  (frame pixels; the card extends 18px left and right of it)
//   state: { bars: float (how many candles are drawn), show: {id: 0..1 drawn fraction},
//            levels:[{price,label,color,from,to,alpha,below,labelPos,labelAt}], zones:[{from,to,lo,hi,color,label,alpha}],
//            marks:[{bar,price,dir,text,color,alpha,panel,value}], readout: bool, view: [first, last], volume: bool, header: bool }
// Returns a list of layout problems (labels outside the chart or overlapping each other).
(function () {
  // TradingView dark theme
  const TV = { bg: "#131722", grid: "#1E2330", border: "#2A2E39", text: "#B2B5BE", up: "#26A69A", down: "#EF5350", ink: "#D1D4DC" };
  const C = { mint: TV.up, coral: TV.down, gold: "#F5B941", blue: "#4C8DF6", ink: TV.ink, muted: "#787B86", line: TV.border, card: TV.bg, violet: "#B388FF", orange: "#FF9800" };
  const col = (c) => C[c] || c || C.gold;
  const NS = "http://www.w3.org/2000/svg";
  const fmt = (v) => v.toFixed(2);  // like TradingView: no thousands separator on the price scale

  // The "camera" frames what is visible now: the candles drawn so far (the forming one included, so the view moves
  // smoothly), the indicator values drawn so far, and this scene's levels and zones.
  function scaleFor(chart, state, upto, formed, v0) {
    let lo = Infinity, hi = -Infinity;
    const take = (v) => { if (v === null || v === undefined || isNaN(v)) return; lo = Math.min(lo, v); hi = Math.max(hi, v); };
    const a = Math.max(0, Math.floor(v0 || 0));
    for (let i = a; i < upto; i++) { const b = i === upto - 1 && formed ? formed : chart.candles[i]; take(b.h); take(b.l); }
    const show = state.show || {};
    (chart.lines || []).forEach((l) => { if (show[l.id]) l.values.slice(a, Math.floor(state.bars)).forEach(take); });
    (chart.bands || []).forEach((b) => { if (show[b.id]) { b.upper.slice(a, Math.floor(state.bars)).forEach(take); b.lower.slice(a, Math.floor(state.bars)).forEach(take); } });
    (state.levels || []).forEach((l) => take(l.price));
    (state.zones || []).forEach((z) => { take(z.lo); take(z.hi); });
    const span = Math.max(hi - lo, (hi + lo) / 2 * 0.004);
    const mid = (hi + lo) / 2;
    return [mid - span * 0.53, mid + span * 0.53];
  }

  function niceStep(raw) {
    const p = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / p;
    return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p;
  }

  const hhmm = (m) => `${String(Math.floor(m / 60) % 24).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;

  window.drawChart = function (host, chart, box, state) {
    const problems = [];
    const n = chart.candles.length, panel = chart.panel;
    const fs = Math.max(20, Math.min(28, box.w / 34));           // axis / header font size
    const timeH = chart.time ? Math.round(fs * 1.7) : 0;           // bottom time scale
    const innerH = box.h - timeH;
    const mainH = panel ? innerH * 0.66 : innerH, panelH = panel ? innerH - mainH : 0;
    const bars0 = Math.max(0, Math.min(n, state.bars)), full0 = Math.floor(bars0), frac0 = bars0 - full0;
    let formed = null;
    if (frac0 > 0 && full0 < n) { const b = chart.candles[full0], c = b.o + (b.c - b.o) * frac0;
      formed = { h: Math.max(b.o, c) + (b.h - Math.max(b.o, b.c)) * frac0, l: Math.min(b.o, c) - (Math.min(b.o, b.c) - b.l) * frac0 }; }
    const upto = Math.max(1, full0 + (formed ? 1 : 0));
    // Camera: state.view = [first, last] bar shown (fractions allowed, for smooth push-ins); default = everything so far.
    const v0 = state.view ? Math.max(0, state.view[0]) : 0;
    const [lo, hi] = scaleFor(chart, state, upto, formed, v0);
    const axisW = Math.round(fs * (0.6 * fmt(Math.max(...chart.candles.map((c) => c.h))).length + 1.4));  // right price scale, wide enough for the chart's longest price (constant: no jitter in videos)
    const plotR = box.x + box.w - axisW;                           // right edge of the drawing area
    const plotW = plotR - box.x;
    const slots = state.view ? Math.max(4, state.view[1] - v0) : Math.max(state.minBars || 16, bars0 + 1.5);
    const step = plotW / (state.view ? slots : Math.min(n + 0.5, slots)), bw = Math.max(4, step * 0.7);
    const X = (i) => box.x + step * (i - v0 + 0.5);
    const inView = (i) => X(i) > box.x - step && X(i) < plotR + step;
    const header = state.header !== false;
    const legendItems = [...(chart.lines || []), ...(chart.bands || [])].filter((ln) => (state.show || {})[ln.id] > 0 && ln.label);
    const headH = header ? fs * 1.9 + (legendItems.length ? fs * 1.5 : 0) : 0;
    const vol = state.volume !== false && chart.candles[0] && chart.candles[0].v !== undefined;
    const volH = vol ? mainH * 0.1 : 0;
    const markPad = chart._marked ? Math.min(112, mainH * 0.22) : 18; // room for arrows and their labels above the highs and below the lows
    const padT = Math.max(markPad, headH + 14), padB = markPad + volH * 0.45;
    const Y = (p) => box.y + padT + (mainH - padT - padB) * (1 - (p - lo) / (hi - lo));
    const P = (y) => lo + (1 - (y - box.y - padT) / (mainH - padT - padB)) * (hi - lo);
    const py0 = box.y + mainH;
    const PY = (v) => py0 + fs * 1.6 + (panelH - fs * 1.6 - 12) * (1 - (v - panel.min) / (panel.max - panel.min));
    const bars = Math.max(0, Math.min(n, state.bars));
    const full = Math.floor(bars), frac = bars - full;
    let s = "", axis = "";
    const ticks = [], tags = [];  // price-scale labels; a tick label is hidden where a level or last-price tag sits
    // card, grid, price scale
    s += `<rect x="${box.x - 18}" y="${box.y}" width="${box.w + 36}" height="${box.h}" rx="14" fill="${TV.bg}"/>`;
    const tick = niceStep((P(box.y) - P(box.y + mainH)) / Math.max(3, mainH / (fs * 4.2)));
    for (let p = Math.ceil(P(box.y + mainH) / tick) * tick; p <= P(box.y); p += tick) {
      const y = Y(p); if (y < box.y + 8 || y > box.y + mainH - 8) continue;
      s += `<line x1="${box.x - 18}" x2="${plotR}" y1="${y}" y2="${y}" stroke="${TV.grid}" stroke-width="2"/>`;
      if (y > box.y + fs && y < box.y + mainH - volH - fs * 0.8) ticks.push([y, p]);  // none over the volume: the bottom is where video captions sit
    }
    // time scale: vertical grid and labels at round times
    if (chart.time) {
      const [hh, mm] = chart.time.start.split(":").map(Number), t0 = hh * 60 + mm, st = chart.time.step || 5;
      const every = [15, 30, 60, 120, 240].find((m) => (m / st) * step >= fs * 4.2) || 240;
      for (let i = Math.max(0, Math.floor(v0)); i < n; i++) {
        const t = t0 + i * st; if (t % every !== 0 || !inView(i) || X(i) > plotR - fs * 1.5 || X(i) < box.x + fs * 1.5) continue;
        s += `<line x1="${X(i)}" x2="${X(i)}" y1="${box.y}" y2="${box.y + innerH}" stroke="${TV.grid}" stroke-width="2"/>`;
        axis += `<text x="${X(i)}" y="${box.y + innerH + timeH * 0.68}" text-anchor="middle" font-size="${fs}" fill="${TV.text}">${hhmm(t)}</text>`;
      }
    }
    // watermark, like the symbol watermark on TradingView
    s += `<text x="${box.x + plotW / 2}" y="${box.y + mainH / 2 + fs * 1.2}" text-anchor="middle" font-size="${Math.round(fs * 3.2)}" font-weight="700" fill="#FFFFFF" opacity="0.035" letter-spacing="6">CALM EDGE</text>`;
    // zones (behind everything)
    (state.zones || []).forEach((z) => {
      if (!z.alpha) return;
      const x0 = X(z.from) - step / 2, x1 = Math.min(plotR, X(Math.min(z.to, n - 1)) + step / 2);
      s += `<rect x="${x0}" y="${Y(z.hi)}" width="${x1 - x0}" height="${Y(z.lo) - Y(z.hi)}" fill="${col(z.color)}" opacity="${0.18 * z.alpha}" stroke="${col(z.color)}" stroke-opacity="${0.6 * z.alpha}" stroke-width="2"/>`;
    });
    // volume (bottom of the price pane)
    if (vol) {
      let vmax = 0; for (let i = Math.max(0, Math.floor(v0)); i < Math.min(n, full + 1); i++) if (inView(i)) vmax = Math.max(vmax, chart.candles[i].v || 0);
      for (let i = 0; i < Math.min(n, full + (frac > 0 ? 1 : 0)); i++) {
        if (!inView(i) || !vmax) continue;
        const b = chart.candles[i], k = i === full ? frac : 1, h = volH * (b.v / vmax) * k;
        s += `<rect x="${X(i) - bw / 2}" y="${py0 - h}" width="${bw}" height="${h}" fill="${b.c >= b.o ? TV.up : TV.down}" opacity="0.32"/>`;
      }
    }
    // bands
    (chart.bands || []).forEach((b) => {
      const k = (state.show || {})[b.id] || 0; if (!k) return;
      const upto = Math.min(full, Math.round(n * k));
      const up = [], dn = [];
      for (let i = 0; i < upto; i++) if (b.upper[i] !== null && inView(i)) { up.push(`${X(i)},${Y(b.upper[i])}`); dn.unshift(`${X(i)},${Y(b.lower[i])}`); }
      if (up.length > 1) {
        s += `<polygon points="${up.concat(dn).join(" ")}" fill="${col(b.color)}" opacity="0.08"/>`;
        s += `<polyline points="${up.join(" ")}" fill="none" stroke="${col(b.color)}" stroke-width="3" opacity="0.9"/>`;
        s += `<polyline points="${dn.join(" ")}" fill="none" stroke="${col(b.color)}" stroke-width="3" opacity="0.9"/>`;
      }
    });
    // levels: horizontal lines with a price tag on the scale
    (state.levels || []).forEach((l) => {
      if (!l.alpha) return;
      const x0 = X(l.from || 0) - step / 2, x1 = Math.min(plotR, X(l.to === undefined ? n - 1 : l.to) + step / 2), y = Y(l.price);
      s += `<line x1="${x0}" x2="${x1}" y1="${y}" y2="${y}" stroke="${col(l.color)}" stroke-width="3" ${l.solid ? "" : 'stroke-dasharray="10 7"'} opacity="${l.alpha}"/>`;
      if (y > box.y + 4 && y < box.y + mainH - 4 && l.alpha > 0.3) tags.push(y);
      if (y > box.y + 4 && y < box.y + mainH - 4)
        axis += `<g opacity="${l.alpha}"><rect x="${plotR + 2}" y="${y - fs * 0.72}" width="${axisW - 2}" height="${fs * 1.44}" rx="4" fill="${col(l.color)}"/>` +
          `<text x="${plotR + 12}" y="${y + fs * 0.35}" font-size="${fs}" font-weight="700" fill="#FFFFFF">${fmt(l.price)}</text></g>`;
    });
    // candles
    let last = null;
    for (let i = 0; i < Math.min(n, full + (frac > 0 ? 1 : 0)); i++) {
      const b = chart.candles[i];
      let o = b.o, c = b.c, h = b.h, l = b.l;
      if (i === full) { // the forming candle grows from its open
        const k = frac; c = o + (b.c - o) * k; h = Math.max(o, c) + (b.h - Math.max(b.o, b.c)) * k; l = Math.min(o, c) - (Math.min(b.o, b.c) - b.l) * k;
      }
      last = { o, h, l, c };
      if (!inView(i)) continue;
      const up = c >= o, color = up ? TV.up : TV.down;
      const y0 = Y(Math.max(o, c)), y1 = Y(Math.min(o, c));
      s += `<line x1="${X(i)}" x2="${X(i)}" y1="${Y(h)}" y2="${Y(l)}" stroke="${color}" stroke-width="2.5"/>`;
      s += `<rect x="${X(i) - bw / 2}" y="${y0}" width="${bw}" height="${Math.max(2.5, y1 - y0)}" fill="${color}"/>`;
    }
    // indicator lines on price
    (chart.lines || []).forEach((ln) => {
      const k = (state.show || {})[ln.id] || 0; if (!k) return;
      const upto = Math.min(full, Math.round(n * k)), pts = [];
      for (let i = 0; i < upto; i++) if (ln.values[i] !== null && inView(i)) pts.push(`${X(i)},${Y(ln.values[i])}`);
      if (pts.length > 1) s += `<polyline points="${pts.join(" ")}" fill="none" stroke="${col(ln.color)}" stroke-width="4" stroke-linejoin="round" ${ln.dash ? 'stroke-dasharray="12 8"' : ""}/>`;
    });
    // last price: dotted line and tag, like TradingView
    if (last && state.lastPrice !== false) {
      const y = Y(last.c), c = last.c >= last.o ? TV.up : TV.down;
      const clash = (state.levels || []).some((l) => l.alpha > 0.3 && Math.abs(Y(l.price) - y) < fs * 1.5);
      s += `<line x1="${box.x - 18}" x2="${plotR}" y1="${y}" y2="${y}" stroke="${c}" stroke-width="2" stroke-dasharray="3 5" opacity="0.9"/>`;
      if (!clash && y > box.y + 4 && y < box.y + mainH - 4) tags.push(y);
      if (!clash && y > box.y + 4 && y < box.y + mainH - 4)
        axis += `<rect x="${plotR + 2}" y="${y - fs * 0.72}" width="${axisW - 2}" height="${fs * 1.44}" rx="4" fill="${c}"/>` +
          `<text x="${plotR + 12}" y="${y + fs * 0.35}" font-size="${fs}" font-weight="700" fill="#FFFFFF">${fmt(last.c)}</text>`;
    }
    // lower panel
    let panelVal = null;
    if (panel) {
      s += `<line x1="${box.x - 18}" x2="${box.x + box.w + 18}" y1="${py0}" y2="${py0}" stroke="${TV.border}" stroke-width="3"/>`;
      const k = (state.show || {})[panel.id || "panel"];
      if (k) {
        (panel.levels || []).forEach((lv) => {
          s += `<line x1="${box.x - 18}" x2="${plotR}" y1="${PY(lv.y)}" y2="${PY(lv.y)}" stroke="${col(lv.color || "muted")}" stroke-width="2" stroke-dasharray="8 8" opacity="0.8"/>`;
          axis += `<text x="${plotR + 12}" y="${PY(lv.y) + fs * 0.35}" font-size="${fs}" fill="${col(lv.color || "muted")}">${lv.label || lv.y}</text>`;
        });
        const upto = Math.min(full, Math.round(n * k));
        if (panel.hist) for (let i = 0; i < upto; i++) { const v = panel.hist.values[i]; if (v === null || !inView(i)) continue;
          const y0 = PY(0), y1 = PY(v); s += `<rect x="${X(i) - bw / 2}" y="${Math.min(y0, y1)}" width="${bw}" height="${Math.abs(y1 - y0)}" fill="${v >= 0 ? TV.up : TV.down}" opacity="0.6"/>`; }
        (panel.lines || []).forEach((ln) => {
          const pts = []; for (let i = 0; i < upto; i++) if (ln.values[i] !== null && inView(i)) { pts.push(`${X(i)},${PY(ln.values[i])}`); }
          if (pts.length > 1) s += `<polyline points="${pts.join(" ")}" fill="none" stroke="${col(ln.color)}" stroke-width="4" stroke-linejoin="round"/>`;
        });
        const main = (panel.lines || [])[0];
        if (main) for (let i = upto - 1; i >= 0; i--) if (main.values[i] !== null) { panelVal = main.values[i]; break; }
        s += `<text x="${box.x}" y="${py0 + fs * 1.25}" font-size="${fs}" fill="${TV.text}">${panel.label}${panelVal !== null && state.readout !== false ? ` <tspan fill="${col((panel.lines[0] || {}).color)}">${panelVal.toFixed(1)}</tspan>` : ""}</text>`;
      }
    }
    ticks.forEach(([y, p]) => { if (!tags.some((t) => Math.abs(t - y) < fs * 1.5))
      axis += `<text x="${plotR + 12}" y="${y + fs * 0.35}" font-size="${fs}" fill="${TV.text}">${fmt(p)}</text>`; });
    if (timeH) s += `<line x1="${box.x - 18}" x2="${box.x + box.w + 18}" y1="${box.y + innerH}" y2="${box.y + innerH}" stroke="${TV.border}" stroke-width="2"/>`;
    s += `<line x1="${plotR}" x2="${plotR}" y1="${box.y}" y2="${box.y + innerH}" stroke="${TV.border}" stroke-width="2"/>`;
    const cid = "clip_" + (host.id || "c") + "_" + Math.round(box.x) + "_" + Math.round(box.y);  // unique per scene: an id shared with a hidden scene would not clip
    host.innerHTML = `<defs><clipPath id="${cid}"><rect x="${box.x - 18}" y="${box.y}" width="${plotR - box.x + 18}" height="${innerH}" rx="14"/></clipPath></defs>` +
      `<rect x="${box.x - 18}" y="${box.y}" width="${box.w + 36}" height="${box.h}" rx="14" fill="${TV.bg}" stroke="${TV.border}" stroke-width="2"/>` +
      `<g clip-path="url(#${cid})">${s}</g>${axis}`;
    // header (symbol, timeframe, OHLC) and indicator legend, like the top-left of a TradingView chart
    if (header) {
      const t = document.createElementNS(NS, "text");
      Object.entries({ x: box.x, y: box.y + fs * 1.35, "font-size": fs, fill: TV.ink }).forEach(([k, v]) => t.setAttribute(k, v));
      const c = last && last.c >= last.o ? TV.up : TV.down;
      t.innerHTML = `<tspan font-weight="700">${chart.symbol || "EXAMPLE"}${chart.tf ? " · " + chart.tf : ""}</tspan>` +
        (last && state.readout !== false ? ["O", "H", "L", "C"].map((k) => `<tspan fill="${TV.text}" dx="${k === "O" ? fs * 0.9 : fs * 0.5}">${k}</tspan><tspan fill="${c}" dx="4">${fmt(last[k.toLowerCase()])}</tspan>`).join("") : "");
      host.appendChild(t);
      if (t.getBBox().width > plotW - 10) {  // too long for a narrow chart: keep symbol and close only
        t.innerHTML = `<tspan font-weight="700">${chart.symbol || "EXAMPLE"}${chart.tf ? " · " + chart.tf : ""}</tspan>` + (last ? `<tspan fill="${TV.text}" dx="${fs * 0.9}">C</tspan><tspan fill="${c}" dx="4">${fmt(last.c)}</tspan>` : "");
      }
      let lx = box.x;
      legendItems.forEach((ln) => {
        const vals = ln.values || ln.upper, lastV = (() => { for (let i = Math.min(full, n) - 1; i >= 0; i--) if (vals[i] !== null) return vals[i]; return null; })();
        const u = document.createElementNS(NS, "text");
        Object.entries({ x: lx, y: box.y + fs * 2.85, "font-size": fs, fill: TV.text }).forEach(([k, v]) => u.setAttribute(k, v));
        u.innerHTML = `${ln.label}${lastV !== null && state.readout !== false ? ` <tspan fill="${col(ln.color)}">${fmt(lastV)}</tspan>` : ` <tspan fill="${col(ln.color)}">━</tspan>`}`;
        host.appendChild(u);
        lx += u.getBBox().width + fs * 1.2;
        if (lx > plotR + 10) problems.push("chart legend too wide");
      });
    }
    // labels (levels, zones, marks): text on a dark plate, measured to stay inside the drawing area
    const plates = [], arrows = [];
    const lfs = Math.round(Math.max(23, Math.min(30, fs * 1.08)));
    const label = (x, y, text, color, alpha, anchor) => {
      if (!text) return;  // a line without a label (e.g. already named in an earlier scene)
      const t = document.createElementNS(NS, "text");
      t.setAttribute("font-size", lfs); t.setAttribute("font-weight", "700"); t.setAttribute("fill", col(color)); t.textContent = text;
      host.appendChild(t);
      const w = t.getBBox().width, hgt = lfs * 1.3;
      y = Math.max(box.y + hgt / 2 + 10, Math.min(box.y + innerH - hgt / 2 - 10, y));  // a label never leaves the chart, even for one frame
      let x0 = anchor === "middle" ? x - w / 2 - 12 : anchor === "end" ? x - w - 24 : anchor === "end-left" ? x - 60 - w - 24 : anchor === "start-right" ? x + 52 : x;
      const minX = box.x - 6, maxX = plotR - 6 - w - 24;
      x0 = Math.max(minX, Math.min(maxX, x0));
      t.setAttribute("x", x0 + 12); t.setAttribute("y", y + lfs * 0.36);
      const r = document.createElementNS(NS, "rect");
      Object.entries({ x: x0, y: y - hgt / 2 - 3, width: w + 24, height: hgt + 6, rx: 6, fill: TV.bg, opacity: 0.92 * alpha, stroke: col(color), "stroke-width": 2 }).forEach(([k, v]) => r.setAttribute(k, v));
      host.insertBefore(r, t); t.setAttribute("opacity", alpha);
      if (alpha > 0.5) plates.push({ x0, x1: x0 + w + 24, y0: y - hgt / 2 - 3, y1: y + hgt / 2 + 3, text });
    };
    (state.levels || []).forEach((l) => { if (!l.alpha || !l.label) return;
      const right = l.labelPos === "right", xr = Math.min(plotR, X(l.to === undefined ? n - 1 : l.to) + step / 2);
      label(right ? xr + 18 : X(l.from || 0) - step / 2 + 6 + (l.labelAt || 0) * step, Y(l.price) - (l.below ? -lfs * 1.15 : lfs * 1.15), l.label, l.color, l.alpha, right ? "end" : "start"); });
    (state.zones || []).forEach((z) => { if (!z.alpha || !z.label) return;
      const above = Y(z.hi) - lfs * 1.15; label((X(z.from) + Math.min(plotR, X(Math.min(z.to, n - 1)))) / 2, above - lfs > box.y + headH ? above : Y(z.hi) + lfs * 1.15, z.label, z.color, z.alpha, "middle"); });
    (state.marks || []).forEach((m) => {
      if (!m.alpha || !inView(m.bar)) return;
      const x = X(m.bar), b = chart.candles[m.bar], c = col(m.color);
      // while the camera pushes in, a mark sliding off the left edge fades out before its label can leave the chart
      const a = m.alpha * Math.max(0, Math.min(1, (x - box.x - 40) / 110));
      if (a <= 0.02) return;
      if (m.panel) { // a dot on the indicator line, label beside it
        const y = PY(m.value);
        host.insertAdjacentHTML("beforeend", `<circle cx="${x}" cy="${y}" r="11" fill="${c}" stroke="${TV.bg}" stroke-width="4" opacity="${a}"/>`);
        if (m.text) label(x + 30, y, m.text, m.color, a, x > box.x + plotW * 0.6 ? "end-left" : "start");
        return;
      }
      const yv = Y(m.price !== undefined ? m.price : m.dir === "up" ? b.l : b.h);
      const up = m.dir === "up";
      const tip = up ? yv + 10 : yv - 10, tail = up ? tip + 62 : tip - 62;
      if (a > 0.5) arrows.push({ x0: x - 15, x1: x + 15, y0: Math.min(tip, tail), y1: Math.max(tip, tail), text: "arrow" });
      host.insertAdjacentHTML("beforeend", `<g opacity="${a}"><line x1="${x}" x2="${x}" y1="${tail}" y2="${tip + (up ? 16 : -16)}" stroke="${c}" stroke-width="6"/>` +
        `<polygon points="${x - 15},${tip + (up ? 24 : -24)} ${x + 15},${tip + (up ? 24 : -24)} ${x},${tip}" fill="${c}"/></g>`);
      if (!m.text) return;
      const ly = up ? tail + lfs * 1.0 : tail - lfs * 1.0, fits = ly - lfs > box.y + (up ? 0 : headH) && ly + lfs < box.y + mainH;
      if (fits) label(x, ly, m.text, m.color, a, "middle");
      else label(x - 26, tail + (up ? -8 : 8), m.text, m.color, a, x > box.x + plotW * 0.45 ? "end" : "start-right");
    });
    // checks
    const top = box.y, bottom = box.y + innerH;
    plates.forEach((p, i) => {
      if (p.x0 < box.x - 20 || p.x1 > plotR + 4 || p.y0 < top || p.y1 > bottom) problems.push("chart label outside the chart: " + p.text);
      arrows.forEach((q) => { if (p.x0 < q.x1 && q.x0 < p.x1 && p.y0 < q.y1 && q.y0 < p.y1) problems.push(`chart label covered by an arrow: ${p.text}`); });
      plates.slice(i + 1).forEach((q) => { if (p.x0 < q.x1 && q.x0 < p.x1 && p.y0 < q.y1 && q.y0 < p.y1) problems.push(`chart labels overlap: ${p.text} / ${q.text}`); });
    });
    return problems;
  };
})();
