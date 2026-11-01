// Candlestick chart drawn as SVG, shared by the video player and the Pinterest pin.
// drawChart(svgHost, chart, box, state) draws one frame; everything is a pure function of `state`.
//   chart: { candles:[{o,h,l,c}], lines:[{id,label,color,values,dash}], bands:[{id,upper,lower,color}],
//            panel:{label,min,max,lines:[{id,color,values}],levels:[{y,label}],hist:{id,values}} }
//   box:   { x, y, w, h }  (frame pixels)
//   state: { bars: float (how many candles are drawn), show: {id: 0..1 drawn fraction},
//            levels:[{price,label,color,from,to,alpha}], zones:[{from,to,lo,hi,color,label,alpha}],
//            marks:[{bar,price,dir,text,color,alpha,panel,value}], readout: bool }
// Returns a list of layout problems (labels outside the chart or overlapping each other).
(function () {
  const C = { mint: "#5FD3A0", coral: "#F2848A", gold: "#F2C14E", blue: "#6CA8FF", ink: "#E8EDF3", muted: "#93A3B5", line: "#2A3A4C", card: "#16212D", violet: "#B48CFF" };
  const col = (c) => C[c] || c || C.gold;
  const NS = "http://www.w3.org/2000/svg";
  const fmt = (v) => (Math.abs(v) >= 1000 ? v.toLocaleString("en-US", { maximumFractionDigits: 0 }) : v.toFixed(2));

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
    return [mid - span * 0.56, mid + span * 0.56];
  }

  window.drawChart = function (host, chart, box, state) {
    const problems = [];
    const n = chart.candles.length, panel = chart.panel;
    const mainH = panel ? box.h * 0.64 : box.h, gap = panel ? 26 : 0, panelH = panel ? box.h - mainH - gap : 0;
    const bars0 = Math.max(0, Math.min(n, state.bars)), full0 = Math.floor(bars0), frac0 = bars0 - full0;
    let formed = null;
    if (frac0 > 0 && full0 < n) { const b = chart.candles[full0], c = b.o + (b.c - b.o) * frac0;
      formed = { h: Math.max(b.o, c) + (b.h - Math.max(b.o, b.c)) * frac0, l: Math.min(b.o, c) - (Math.min(b.o, b.c) - b.l) * frac0 }; }
    const upto = Math.max(1, full0 + (formed ? 1 : 0));
    // Camera: state.view = [first, last] bar shown (fractions allowed, for smooth push-ins); default = everything so far.
    const v0 = state.view ? Math.max(0, state.view[0]) : 0;
    const [lo, hi] = scaleFor(chart, state, upto, formed, v0);
    const slots = state.view ? Math.max(4, state.view[1] - v0) : Math.max(state.minBars || 16, bars0 + 1.5);
    const step = box.w / (state.view ? slots : Math.min(n + 0.5, slots)), bw = Math.max(4, step * 0.62);
    const X = (i) => box.x + step * (i - v0 + 0.5);
    const inView = (i) => X(i) > box.x - step && X(i) < box.x + box.w + step;
    const pad = chart._marked ? Math.min(112, mainH * 0.24) : 30; // room for arrows and their labels above the highs and below the lows
    const Y = (p) => box.y + pad + (mainH - 2 * pad) * (1 - (p - lo) / (hi - lo));
    const py0 = box.y + mainH + gap;
    const PY = (v) => py0 + 14 + (panelH - 28) * (1 - (v - panel.min) / (panel.max - panel.min));
    const bars = Math.max(0, Math.min(n, state.bars));
    const full = Math.floor(bars), frac = bars - full;
    let s = "";
    // frames
    s += `<rect x="${box.x - 18}" y="${box.y}" width="${box.w + 36}" height="${mainH}" rx="26" fill="${C.card}" stroke="${C.line}" stroke-width="3"/>`;
    if (panel) s += `<rect x="${box.x - 18}" y="${py0}" width="${box.w + 36}" height="${panelH}" rx="26" fill="${C.card}" stroke="${C.line}" stroke-width="3"/>`;
    // zones (behind everything)
    (state.zones || []).forEach((z) => {
      if (!z.alpha) return;
      const x0 = X(z.from) - step / 2, x1 = Math.min(box.x + box.w, X(Math.min(z.to, n - 1)) + step / 2);
      s += `<rect x="${x0}" y="${Y(z.hi)}" width="${x1 - x0}" height="${Y(z.lo) - Y(z.hi)}" fill="${col(z.color)}" opacity="${0.16 * z.alpha}" rx="8"/>`;
    });
    // bands
    (chart.bands || []).forEach((b) => {
      const k = (state.show || {})[b.id] || 0; if (!k) return;
      const upto = Math.min(full, Math.round(n * k));
      const up = [], dn = [];
      for (let i = 0; i < upto; i++) if (b.upper[i] !== null && inView(i)) { up.push(`${X(i)},${Y(b.upper[i])}`); dn.unshift(`${X(i)},${Y(b.lower[i])}`); }
      if (up.length > 1) {
        s += `<polygon points="${up.concat(dn).join(" ")}" fill="${col(b.color)}" opacity="0.10"/>`;
        s += `<polyline points="${up.join(" ")}" fill="none" stroke="${col(b.color)}" stroke-width="4" opacity="0.85"/>`;
        s += `<polyline points="${dn.join(" ")}" fill="none" stroke="${col(b.color)}" stroke-width="4" opacity="0.85"/>`;
      }
    });
    // levels
    (state.levels || []).forEach((l) => {
      if (!l.alpha) return;
      const x0 = X(l.from || 0) - step / 2, x1 = Math.min(box.x + box.w, X(l.to === undefined ? n - 1 : l.to) + step / 2), y = Y(l.price);
      s += `<line x1="${x0}" x2="${x1}" y1="${y}" y2="${y}" stroke="${col(l.color)}" stroke-width="5" stroke-dasharray="16 12" opacity="${l.alpha}"/>`;
    });
    // candles
    for (let i = 0; i < Math.min(n, full + (frac > 0 ? 1 : 0)); i++) {
      if (!inView(i)) continue;
      const b = chart.candles[i];
      let o = b.o, c = b.c, h = b.h, l = b.l;
      if (i === full) { // the forming candle grows from its open
        const k = frac; c = o + (b.c - o) * k; h = Math.max(o, c) + (b.h - Math.max(b.o, b.c)) * k; l = Math.min(o, c) - (Math.min(b.o, b.c) - b.l) * k;
      }
      const up = c >= o, color = up ? C.mint : C.coral;
      const y0 = Y(Math.max(o, c)), y1 = Y(Math.min(o, c));
      s += `<line x1="${X(i)}" x2="${X(i)}" y1="${Y(h)}" y2="${Y(l)}" stroke="${color}" stroke-width="3"/>`;
      s += `<rect x="${X(i) - bw / 2}" y="${y0}" width="${bw}" height="${Math.max(3, y1 - y0)}" fill="${color}" rx="2"/>`;
    }
    // indicator lines on price
    (chart.lines || []).forEach((ln) => {
      const k = (state.show || {})[ln.id] || 0; if (!k) return;
      const upto = Math.min(full, Math.round(n * k)), pts = [];
      for (let i = 0; i < upto; i++) if (ln.values[i] !== null && inView(i)) pts.push(`${X(i)},${Y(ln.values[i])}`);
      if (pts.length > 1) s += `<polyline points="${pts.join(" ")}" fill="none" stroke="${col(ln.color)}" stroke-width="6" stroke-linejoin="round" ${ln.dash ? 'stroke-dasharray="14 10"' : ""}/>`;
    });
    // lower panel
    let panelVal = null;
    if (panel) {
      const k = (state.show || {})[panel.id || "panel"];
      if (k) {
        (panel.levels || []).forEach((lv) => {
          s += `<line x1="${box.x}" x2="${box.x + box.w}" y1="${PY(lv.y)}" y2="${PY(lv.y)}" stroke="${col(lv.color || "muted")}" stroke-width="3" stroke-dasharray="10 10" opacity="0.8"/>`;
          s += `<rect x="${box.x + box.w - 46}" y="${PY(lv.y) - 17}" width="50" height="34" rx="8" fill="#0F1720" stroke="${col(lv.color || "muted")}" stroke-width="2"/>` +
            `<text x="${box.x + box.w - 21}" y="${PY(lv.y) + 9}" text-anchor="middle" font-size="24" font-weight="700" fill="${col(lv.color || "muted")}">${lv.label || lv.y}</text>`;
        });
        const upto = Math.min(full, Math.round(n * k));
        if (panel.hist) for (let i = 0; i < upto; i++) { const v = panel.hist.values[i]; if (v === null || !inView(i)) continue;
          const y0 = PY(0), y1 = PY(v); s += `<rect x="${X(i) - bw / 2}" y="${Math.min(y0, y1)}" width="${bw}" height="${Math.abs(y1 - y0)}" fill="${v >= 0 ? C.mint : C.coral}" opacity="0.55"/>`; }
        (panel.lines || []).forEach((ln) => {
          const pts = []; for (let i = 0; i < upto; i++) if (ln.values[i] !== null && inView(i)) { pts.push(`${X(i)},${PY(ln.values[i])}`); }
          if (pts.length > 1) s += `<polyline points="${pts.join(" ")}" fill="none" stroke="${col(ln.color)}" stroke-width="5" stroke-linejoin="round"/>`;
        });
        const main = (panel.lines || [])[0];
        if (main) for (let i = upto - 1; i >= 0; i--) if (main.values[i] !== null) { panelVal = main.values[i]; break; }
        s += `<text x="${box.x}" y="${py0 + 40}" font-size="28" font-weight="700" fill="${C.muted}">${panel.label}${panelVal !== null && state.readout !== false ? ` <tspan fill="${col((panel.lines[0] || {}).color)}">${panelVal.toFixed(1)}</tspan>` : ""}</text>`;
      }
    }
    const cid = "clip_" + (host.id || "c") + "_" + Math.round(box.x) + "_" + Math.round(box.y);  // unique per scene: an id shared with a hidden scene would not clip
    host.innerHTML = `<defs><clipPath id="${cid}"><rect x="${box.x - 18}" y="${box.y}" width="${box.w + 36}" height="${box.h}" rx="26"/></clipPath></defs><g clip-path="url(#${cid})">${s}</g>`;
    // legend for visible price lines, measured so items never collide
    let lx = box.x + 6;
    [...(chart.lines || []), ...(chart.bands || [])].forEach((ln) => {
      if (!((state.show || {})[ln.id] > 0) || !ln.label) return;
      host.insertAdjacentHTML("beforeend", `<line x1="${lx}" x2="${lx + 34}" y1="${box.y + 42}" y2="${box.y + 42}" stroke="${col(ln.color)}" stroke-width="6"/>`);
      const t = document.createElementNS(NS, "text");
      Object.entries({ x: lx + 46, y: box.y + 52, "font-size": 30, "font-weight": 700, fill: C.ink }).forEach(([k, v]) => t.setAttribute(k, v));
      t.textContent = ln.label; host.appendChild(t);
      lx += 46 + t.getBBox().width + 34;
      if (lx > box.x + box.w + 10) problems.push("chart legend too wide");
    });
    // labels (levels, zones, marks): text with a dark plate, measured to stay inside the chart
    const plates = [], arrows = [];
    const label = (x, y, text, color, alpha, anchor) => {
      if (!text) return;  // a line without a label (e.g. already named in an earlier scene)
      const t = document.createElementNS(NS, "text");
      t.setAttribute("font-size", "34"); t.setAttribute("font-weight", "700"); t.setAttribute("fill", col(color)); t.textContent = text;
      host.appendChild(t);
      const w = t.getBBox().width, hgt = 44;
      y = Math.max(box.y + hgt / 2 + 10, Math.min(box.y + box.h - hgt / 2 - 10, y));  // a label never leaves the card, even for one frame
      let x0 = anchor === "middle" ? x - w / 2 : anchor === "end" ? x - w - 24 : anchor === "end-left" ? x - 60 - w - 24 : anchor === "start-right" ? x + 52 : x;
      const minX = box.x - 6, maxX = box.x + box.w + 6 - w - 24;
      x0 = Math.max(minX + 12, Math.min(maxX, x0));
      t.setAttribute("x", x0 + 12); t.setAttribute("y", y + 12);
      const r = document.createElementNS(NS, "rect");
      Object.entries({ x: x0, y: y - hgt / 2 - 4, width: w + 24, height: hgt + 8, rx: 12, fill: "#0F1720", opacity: 0.88 * alpha, stroke: col(color), "stroke-width": 2 }).forEach(([k, v]) => r.setAttribute(k, v));
      host.insertBefore(r, t); t.setAttribute("opacity", alpha);
      if (alpha > 0.5) plates.push({ x0, x1: x0 + w + 24, y0: y - hgt / 2 - 4, y1: y + hgt / 2 + 4, text });
    };
    (state.levels || []).forEach((l) => { if (!l.alpha || !l.label) return;
      const right = l.labelPos === "right", xr = Math.min(box.x + box.w, X(l.to === undefined ? n - 1 : l.to) + step / 2);
      label(right ? xr + 24 : X(l.from || 0) + (l.labelAt || 0) * step, Y(l.price) - (l.below ? -40 : 40), l.label, l.color, l.alpha, right ? "end" : "start"); });
    (state.zones || []).forEach((z) => { if (!z.alpha || !z.label) return;
      const above = Y(z.hi) - 40; label((X(z.from) + Math.min(box.x + box.w, X(Math.min(z.to, n - 1)))) / 2, above - 30 > box.y ? above : Y(z.hi) + 40, z.label, z.color, z.alpha, "middle"); });
    (state.marks || []).forEach((m) => {
      if (!m.alpha || !inView(m.bar)) return;
      const x = X(m.bar), b = chart.candles[m.bar], c = col(m.color);
      // while the camera pushes in, a mark sliding off the left edge fades out before its label can leave the chart
      const a = m.alpha * Math.max(0, Math.min(1, (x - box.x - 40) / 110));
      if (a <= 0.02) return;
      if (m.panel) { // a dot on the indicator line, label beside it
        const y = PY(m.value);
        host.insertAdjacentHTML("beforeend", `<circle cx="${x}" cy="${y}" r="13" fill="${c}" stroke="#0F1720" stroke-width="4" opacity="${a}"/>`);
        if (m.text) label(x + 30, y, m.text, m.color, a, x > box.x + box.w * 0.6 ? "end-left" : "start");
        return;
      }
      const yv = Y(m.price !== undefined ? m.price : m.dir === "up" ? b.l : b.h);
      const up = m.dir === "up";
      const tip = up ? yv + 14 : yv - 14, tail = up ? tip + 70 : tip - 70;
      if (a > 0.5) arrows.push({ x0: x - 16, x1: x + 16, y0: Math.min(tip, tail), y1: Math.max(tip, tail), text: "arrow" });
      host.insertAdjacentHTML("beforeend", `<g opacity="${a}"><line x1="${x}" x2="${x}" y1="${tail}" y2="${tip + (up ? 18 : -18)}" stroke="${c}" stroke-width="7"/>` +
        `<polygon points="${x - 16},${tip + (up ? 26 : -26)} ${x + 16},${tip + (up ? 26 : -26)} ${x},${tip}" fill="${c}"/></g>`);
      if (!m.text) return;
      const ly = up ? tail + 34 : tail - 34, fits = ly - 30 > box.y && ly + 30 < box.y + mainH;
      if (fits) label(x, ly, m.text, m.color, a, "middle");
      else label(x - 26, tail + (up ? -8 : 8), m.text, m.color, a, x > box.x + box.w * 0.45 ? "end" : "start-right");
    });
    // checks
    const top = box.y, bottom = box.y + box.h;
    plates.forEach((p, i) => {
      if (p.x0 < box.x - 20 || p.x1 > box.x + box.w + 20 || p.y0 < top || p.y1 > bottom) problems.push("chart label outside the chart: " + p.text);
      arrows.forEach((q) => { if (p.x0 < q.x1 && q.x0 < p.x1 && p.y0 < q.y1 && q.y0 < p.y1) problems.push(`chart label covered by an arrow: ${p.text}`); });
      plates.slice(i + 1).forEach((q) => { if (p.x0 < q.x1 && q.x0 < p.x1 && p.y0 < q.y1 && q.y0 < p.y1) problems.push(`chart labels overlap: ${p.text} / ${q.text}`); });
    });
    return problems;
  };
})();
