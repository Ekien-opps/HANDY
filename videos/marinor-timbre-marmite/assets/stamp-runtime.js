// Marin'Or Ivoire - timbre "marmite chaude" runtime (HyperFrames composition "main").
// Source of truth for the animation logic. Data (flame frames, tear geometry, rig points) is inlined by
// tools/build_index.py into index.html as window.__STAMP_DATA. render(f) is a pure function of the frame.
(() => {
  const D = window.__STAMP_DATA; // inlined by tools/build_index.py in index.html
  const [Hx, Hy] = D.H, [Cx, Cy] = D.C, [Kx, Ky] = D.KB, [Bx, By] = D.B, [Ex, Ey] = D.E;
  const LAST = 59;
  const FIRE_OUT_FRAME = 28; // hold key: 0 until f27, 1 from f28
  const FORESHORTEN = 0.15; // lid scaleY = 1 - FORESHORTEN * (open/36)^2  -> 85 % at the -36 deg peak
  const SLIDE = 10; // lid underside slide (lid-local px) at full open (crescent of the heated underside)
  const NMAX = D.nmax;

  // ---------------- frame tables (spec section 5), integer frames ----------------
  // lid [rot deg (negative = open), dY px, dX px], relative to the squashed lip.
  // Pivot H up to f28, C for the bounces (f28 -> f32). f15-f19 float: +-1.5 deg / +-2 px around -32 / -32.
  const LID = [
    [0, 0, 0], [0, 0, 1.5], [0, 0, -1], [0, 0, 1.5], [0, 0, -1.5], [0, 0, 1], [0, 0, 0], [0, 2, 0],
    [-17.6, -15.4, 0], [-28.2, -25.9, 0], [-33.7, -31.3, 0], [-35.7, -33.3, 0], [-36, -33.6, 0],
    [-35, -33.2, 0], [-33, -32.4, 0],
    [-31.6, -31.0, 0], [-30.7, -30.3, 0], [-31.2, -30.9, 0], [-32.6, -32.6, 0], [-33.4, -33.6, 0],
    [-34, -34.4, 0], [-35, -35.2, 0],
    [-34.3, -34.5, 0], [-32.1, -32.3, 0], [-28.6, -28.7, 0], [-23.6, -23.7, 0], [-17.1, -17.3, 0], [-9.3, -9.3, 0],
    [0, 0, 0], [1.8, -6, 0], [0.6, -2.4, 0], [0, 0, 0], [-0.5, -1.6, 0],
  ];
  // knob secondary rotation (deg, about the knob base, lid-local), |x| <= 3, follow-through of the lid
  const KNOB = { 7: -0.5, 8: 2.5, 9: 3, 10: 1.8, 11: 0.6, 12: -0.4, 13: -0.8, 14: -0.4, 15: 0.2, 16: 0.4, 17: 0.2,
    18: -0.2, 19: -0.3, 20: 0.3, 21: 0.5, 22: 0, 23: -0.8, 24: -1.6, 25: -2.2, 26: -2.6, 27: -3, 28: 2.6,
    29: 1, 30: -1.2, 31: 0.6, 32: -0.2 };
  // CTRL_SQUASH sX/sY (%), about B
  const SQ = { 7: [100.5, 98.5], 8: [99.5, 102], 9: [99.8, 101], 28: [101, 96.5], 29: [100.5, 98.8],
    30: [99.6, 100.8], 31: [100.2, 99.6] };
  // shutter (deg) per frame, spec section 7
  const SHUT = (f) => (f <= 7 ? 0 : f <= 10 ? 180 : f <= 23 ? 90 : f <= 25 ? 180 : f <= 27 ? 270 :
    f === 28 ? 0 : f <= 31 ? 45 : f <= 36 ? 0 : f === 37 ? 90 : f === 38 ? 45 : 0);
  // fire lights
  const SLIT = { 8: 0.4, 9: 0.15 }; // slit glow #FFECD1 at 40 % on the pop frame

  const lidT = [], knobT = [], sqT = [], shutT = [], slitT = [];
  for (let f = 0; f <= LAST; f++) {
    lidT.push(LID[f] || [0, 0, 0]);
    knobT.push([KNOB[f] || 0]);
    const s = SQ[f] || [100, 100];
    sqT.push([s[0] / 100, s[1] / 100]);
    shutT.push(SHUT(f));
    slitT.push([SLIT[f] || 0]);
  }
  const clampF = (f) => Math.min(LAST, Math.max(0, f));
  function sample(T, f) {
    f = clampF(f);
    const i = Math.floor(f), u = f - i;
    if (u < 1e-6 || i >= LAST) return T[i];
    const a = T[i], b = T[i + 1];
    return a.map((v, j) => v + (b[j] - v) * u);
  }
  const fx = (v, n = 4) => (Math.abs(v) < 1e-9 ? "0" : (+v.toFixed(n)).toString());

  // ---------------- affine helpers (SVG matrix [a b c d e f]) ----------------
  const mul = (m, n) => [m[0] * n[0] + m[2] * n[1], m[1] * n[0] + m[3] * n[1], m[0] * n[2] + m[2] * n[3],
    m[1] * n[2] + m[3] * n[3], m[0] * n[4] + m[2] * n[5] + m[4], m[1] * n[4] + m[3] * n[5] + m[5]];
  const rotM = (deg, cx, cy) => { const r = (deg * Math.PI) / 180, c = Math.cos(r), s = Math.sin(r);
    return [c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy]; };
  const trM = (x, y) => [1, 0, 0, 1, x, y];
  const scM = (sx, sy, cx, cy) => [sx, 0, 0, sy, cx * (1 - sx), cy * (1 - sy)];
  const ap = (m, p) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];
  const mstr = (m) => `matrix(${m.map((v) => fx(v, 6)).join(" ")})`;

  // ---------------- pot rig at (fractional) frame t ----------------
  function rig(t) {
    t = clampF(t);
    const [rot, dy, dx] = sample(lidT, t);
    const [kr] = sample(knobT, t);
    const [sx, sy] = sample(sqT, t);
    const open = Math.min(1, Math.max(0, -rot / 36));
    const syL = 1 - FORESHORTEN * open * open;
    const piv = t > 28 ? [Cx, Cy] : [Hx, Hy];
    const lidRT = mul(trM(dx, dy), rotM(rot, piv[0], piv[1])); // rotation + translation (no foreshortening)
    const lid = mul(lidRT, scM(1, syL, Hx, Hy));
    const sq = scM(sx, sy, Bx, By);
    return { rot, open, sq, lid, lidRT, slide: SLIDE * open, knob: rotM(kr, Kx, Ky) };
  }

  // motion-blur sample count per integer frame: from the exposure-interval displacement of probe points
  const LID_PROBES = [[D.lidFree, Hy], [539, 441], [300, 560], [700, 520]];
  const BODY_PROBES = [[194, 1000], [871, 600], [538, 760], [275, 636]];
  const NCOPIES = [];
  for (let f = 0; f <= LAST; f++) {
    const sh = shutT[f] / 360;
    if (!sh) { NCOPIES.push(1); continue; }
    const a = rig(f - sh / 2), b = rig(f + sh / 2);
    let d = 0;
    for (const p of LID_PROBES) {
      const pa = ap(mul(a.sq, a.lid), p), pb = ap(mul(b.sq, b.lid), p);
      d = Math.max(d, Math.hypot(pa[0] - pb[0], pa[1] - pb[1]));
    }
    for (const p of BODY_PROBES) {
      const pa = ap(a.sq, p), pb = ap(b.sq, p);
      d = Math.max(d, Math.hypot(pa[0] - pb[0], pa[1] - pb[1]));
    }
    NCOPIES.push(Math.max(2, Math.min(NMAX, Math.ceil(d / 3.0) + 1)));
  }

  // ---------------- DOM handles ----------------
  const $ = (id) => document.getElementById(id);
  const copies = [];
  for (let j = 0; j < NMAX; j++) {
    const root = $("pic" + j);
    copies.push({
      root, vis: j === 0,
      sq: [...root.querySelectorAll(".sq")], lid: [...root.querySelectorAll(".lid")],
      lus: [...root.querySelectorAll(".lus")], knob: [...root.querySelectorAll(".knob")],
      heatBack: root.querySelector(".heatBack"), slitBack: root.querySelector(".slitBack"),
      heatUnder: root.querySelector(".heatUnder"), slitUnder: root.querySelector(".slitUnder"),
      heatLid: root.querySelector(".heatLid"),
    });
  }
  const flSq = $("flSq"), flBody = $("flBody"), flGlow = $("flGlow");
  const flOut = $("flOut"), flMid = $("flMid"), flCore = $("flCore"), flGlit = $("flGlit");
  const slitPoly = $("slitPoly");
  const intact = $("intact"), frags = $("frags"), reveal = $("reveal"), stress = $("stress");
  const fragEl = { F1: $("fF1"), F2: $("fF2"), F3: $("fF3") };
  const setAttr = (el, k, v) => { if (el.getAttribute(k) !== v) el.setAttribute(k, v); };
  const show = (el, on) => { const v = on ? "" : "none"; if (el.style.display !== v) el.style.display = v; };

  // ---------------- flame (flame.json frames f9..f27; FIRE_OUT from f28) ----------------
  const FL = D.flame;
  const pts = (a) => { let s = ""; for (let i = 0; i < a.length; i += 2) s += (i ? " " : "") + fx(a[i], 2) + "," + fx(a[i + 1], 2); return s; };
  function flameAt(f) {
    if (f < 9 || f >= FIRE_OUT_FRAME) return null;
    const i = Math.floor(f), u = f - i;
    const A = FL[i], B = u > 1e-6 && FL[i + 1] ? FL[i + 1] : null;
    const lay = {};
    for (const n of ["out", "mid", "core"]) lay[n] = B ? A[n].map((v, j) => v + (B[n][j] - v) * u) : A[n];
    let sx, sy;
    if (f >= 22) {
      // section 6.3: slaved to the lid angle, base 100 % keyed at f21
      const a = Math.abs(sample(lidT, f)[0]);
      const k = Math.pow(Math.min(1, Math.max(0, a / 35)), 0.75);
      sx = 100 * (0.7 + 0.3 * k);
      sy = 100 * k;
    } else {
      sx = B ? A.sx + (B.sx - A.sx) * u : A.sx;
      sy = B ? A.sy + (B.sy - A.sy) * u : A.sy;
    }
    return { lay, sx, sy };
  }
  function heatAt(f, fl) {
    if (!fl) return 0;
    return Math.min(1, Math.pow(fl.sy / 112, 0.85));
  }

  // ---------------- tear ----------------
  const T = D.tear;
  const fN = T.front.start + T.crack.trunk.L / T.front.speed;
  function frontS(f) {
    const sT = Math.min(T.crack.trunk.L, Math.max(0, T.front.speed * (f - T.front.start)));
    const u = Math.min(1, Math.max(0, (f - fN) / (T.front.end - fN)));
    return { trunk: sT, branchA: u * T.crack.branchA.L, branchB: u * T.crack.branchB.L };
  }
  function crackPts(b, s) {
    const c = T.crack[b], p = c.p, S = c.s;
    if (s <= 0) return "0,0";
    let out = "";
    for (let i = 0; i < S.length; i++) {
      if (S[i] <= s) { out += (i ? " " : "") + p[2 * i] + "," + p[2 * i + 1]; continue; }
      const u = (s - S[i - 1]) / (S[i] - S[i - 1]);
      out += " " + fx(p[2 * i - 2] + u * (p[2 * i] - p[2 * i - 2]), 2) + "," + fx(p[2 * i - 1] + u * (p[2 * i + 1] - p[2 * i - 1]), 2);
      break;
    }
    return out;
  }
  // per-integer-frame fragment state [rot, tx, ty, lum]: multiplier x rest, the peak table at f38
  const FT = {};
  for (const k of ["F1", "F2", "F3"]) {
    const fr = T.frag[k];
    FT[k] = [];
    for (let f = 0; f <= LAST; f++) {
      if (f < 36) { FT[k].push([0, 0, 0, 0]); continue; }
      if (f === 38) { FT[k].push(fr.peak.slice()); continue; }
      const m = f >= 47 ? 1 : T.mult[f];
      FT[k].push(fr.rest.map((v) => v * m));
    }
  }

  // ---------------- render(f): pure function of the frame ----------------
  function render(fr) {
    let f = clampF(fr);
    const r = Math.round(f);
    if (Math.abs(f - r) < 1e-4) f = r;
    const fi = Math.round(f);
    const fire = f < FIRE_OUT_FRAME ? 1 : 0;

    // flame + fire lights (frame centre)
    const fl = fire && !(window.__hfDebug || {}).noFlame ? flameAt(f) : null;
    const heat = fire ? heatAt(f, fl) : 0;
    const slit = fire ? sample(slitT, f)[0] : 0;
    const c = rig(f);
    setAttr(flSq.parentNode, "transform", mstr(c.sq));
    if (fl) {
      show(flSq, true);
      const xf = `translate(${Ex} ${Ey}) rotate(14) scale(${fx(fl.sx / 100, 5)} ${fx(fl.sy / 100, 5)})`;
      setAttr(flBody, "transform", xf);
      setAttr(flGlow, "transform", xf);
      const o = pts(fl.lay.out), co = pts(fl.lay.core);
      setAttr(flOut, "points", o);
      setAttr(flGlow, "points", o);
      setAttr(flMid, "points", pts(fl.lay.mid));
      setAttr(flCore, "points", co);
      setAttr(flGlit, "points", co);
      // slit matte, SQ space: below the lid underside line, or beyond the lid's free edge
      const L = D.lidFree - 4;
      const loc = [[Hx - 600, Hy], [L, Hy], [L, Hy - 3000], [Hx + 3000, Hy - 3000], [Hx + 3000, Hy + 3000], [Hx - 600, Hy + 3000]];
      setAttr(slitPoly, "points", loc.map((p) => { const q = ap(c.lidRT, p); return fx(q[0], 2) + "," + fx(q[1], 2); }).join(" "));
    } else {
      show(flSq, false);
    }

    // PICTURE: n motion-blur copies at sub-frame times over the shutter interval (1, 1/2, 1/3 ... opacities)
    const DBG = window.__hfDebug || {};
    const sh = shutT[fi] / 360;
    const n = DBG.n ? Math.min(NMAX, DBG.n) : sh > 0 ? NCOPIES[fi] : 1;
    for (let j = 0; j < NMAX; j++) {
      const cp = copies[j];
      if (j >= n) { if (cp.vis) { show(cp.root, false); cp.vis = false; } continue; }
      if (!cp.vis) { show(cp.root, true); cp.vis = true; }
      setAttr(cp.root, "opacity", j ? fx(1 / (j + 1), 6) : "1");
      const t = n > 1 && !DBG.same ? f + ((j + 0.5) / n - 0.5) * sh : f;
      const g = n > 1 ? rig(t) : c;
      const sqs = mstr(g.sq), lids = mstr(g.lid), luss = `translate(0 ${fx(g.slide, 3)})`, kn = mstr(g.knob);
      for (const e of cp.sq) setAttr(e, "transform", sqs);
      for (const e of cp.lid) setAttr(e, "transform", lids);
      for (const e of cp.lus) setAttr(e, "transform", luss);
      for (const e of cp.knob) setAttr(e, "transform", kn);
      setAttr(cp.heatBack, "opacity", fx(0.75 * heat, 4));
      setAttr(cp.heatUnder, "opacity", fx(0.85 * heat, 4));
      setAttr(cp.slitBack, "opacity", fx(slit, 4));
      setAttr(cp.slitUnder, "opacity", fx(slit, 4));
      setAttr(cp.heatLid, "opacity", fx(0.32 * heat, 4));
    }

    // tear
    show(stress, f >= T.stressFrame && f < T.stressFrame + 1);
    const torn = f >= 36;
    show(intact, !torn);
    show(frags, torn);
    const rev = !torn && f > T.front.start;
    show(reveal, rev);
    if (rev) {
      const s = frontS(f);
      const a = crackPts("trunk", s.trunk), b = crackPts("branchA", s.branchA), d = crackPts("branchB", s.branchB);
      setAttr($("mT"), "points", a); setAttr($("hT"), "points", a);
      setAttr($("mA"), "points", b); setAttr($("hA"), "points", b);
      setAttr($("mB"), "points", d); setAttr($("hB"), "points", d);
    }
    if (torn) {
      for (const k of ["F1", "F2", "F3"]) {
        const [rot, tx, ty, lum] = sample(FT[k], f);
        const pv = T.frag[k].pivot;
        setAttr(fragEl[k], "transform", `translate(${fx(tx)} ${fx(ty)}) rotate(${fx(rot)} ${pv[0]} ${pv[1]})`);
        const fl2 = `brightness(${fx(1 + lum, 5)})`;
        if (fragEl[k].style.filter !== fl2) fragEl[k].style.filter = fl2;
      }
    }
  }

  // the paused GSAP timeline that drives render() is built and registered inline in index.html
  window.__stampRender = render;
  window.__renderFrame = render; // debug hook (tools/snap_frames.mjs)
  render(0);
})();
