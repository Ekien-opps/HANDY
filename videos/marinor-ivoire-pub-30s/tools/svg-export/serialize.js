/* In-page DOM → layered SVG serializer for a HyperFrames scene frozen at one time.
 * Usage (in page): await window.__hfToSVG({ title, stripPrefix })  → { svg, stats }
 * Everything is emitted in absolute 1920×1080 screen space: leaves carry their own
 * screen matrix; groups mirror the DOM hierarchy for naming/organisation only.
 */
(function () {
  const SVGNS = "http://www.w3.org/2000/svg";
  const W = 1920, H = 1080;

  window.__hfToSVG = async function (opts = {}) {
    const stripPrefix = opts.stripPrefix || "";
    const stageEl = document.getElementById("stage");
    const sceneRoot = stageEl.querySelector("[data-composition-id]");
    const defs = [];
    const stats = { boxes: 0, svgs: 0, images: 0, texts: 0, skippedMasks: 0, boxShadows: 0, filters: 0 };
    let uid = 0;
    const nid = (p) => `${p}_${++uid}`;
    const usedIds = new Set();
    const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    const f = (n) => { const v = Math.round(n * 1000) / 1000; return Object.is(v, -0) ? 0 : v; };
    const mstr = (m) => `matrix(${f(m.a)} ${f(m.b)} ${f(m.c)} ${f(m.d)} ${f(m.e)} ${f(m.f)})`;
    const isIdentity = (m) => Math.abs(m.a - 1) < 1e-4 && Math.abs(m.b) < 1e-4 && Math.abs(m.c) < 1e-4 && Math.abs(m.d - 1) < 1e-4 && Math.abs(m.e) < 1e-3 && Math.abs(m.f) < 1e-3;

    function niceName(el) {
      let base = el.id || (typeof el.className === "string" ? el.className.split(/\s+/).filter(c => c && c !== "clip")[0] : "") || el.tagName.toLowerCase();
      if (stripPrefix && base.startsWith(stripPrefix)) base = base.slice(stripPrefix.length);
      base = base.replace(/^f0\d-[a-z-]*?-(?=[a-z])/, "");
      base = base.replace(/[^A-Za-z0-9_\-]/g, "_").replace(/^[^A-Za-z]+/, "") || "groupe";
      let name = base, i = 2;
      while (usedIds.has(name)) name = `${base}_${i++}`;
      usedIds.add(name);
      return name;
    }

    // ---------- colours ----------
    function parseColor(c) {
      if (!c) return null;
      const m = c.match(/rgba?\(([^)]+)\)/);
      if (!m) return c === "transparent" ? null : { css: c, a: 1 };
      const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number);
      const a = p.length > 3 ? p[3] : 1;
      if (a <= 0.001) return null;
      const hex = "#" + p.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, "0")).join("");
      return { css: hex, a };
    }

    // ---------- element → screen matrix ----------
    function markerMatrix(el) {
      const cs = getComputedStyle(el);
      let restore = null;
      if (cs.position === "static" && cs.transform === "none" && cs.display !== "inline") { restore = el.style.position; el.style.position = "relative"; }
      const cl = el.clientLeft || 0, ct = el.clientTop || 0;
      const pts = [[0, 0], [100, 0], [0, 100]].map(([x, y]) => {
        const m = document.createElement("div");
        m.style.cssText = `position:absolute;left:${x - cl}px;top:${y - ct}px;width:0;height:0;margin:0;padding:0;border:0;transform:none;display:block;`;
        el.appendChild(m);
        const r = m.getBoundingClientRect();
        m.remove();
        return [r.left, r.top];
      });
      if (restore !== null) el.style.position = restore;
      const [p0, p1, p2] = pts;
      return new DOMMatrix([(p1[0] - p0[0]) / 100, (p1[1] - p0[1]) / 100, (p2[0] - p0[0]) / 100, (p2[1] - p0[1]) / 100, p0[0], p0[1]]);
    }
    function replacedMatrix(el) {
      // swap the replaced element for a same-sized div carrying the same id/class/style, measure, swap back
      const d = document.createElement("div");
      if (el.id) d.id = el.id;
      d.setAttribute("class", el.getAttribute("class") || "");
      d.setAttribute("style", el.getAttribute("style") || "");
      const cs = getComputedStyle(el);
      const w = el.offsetWidth !== undefined ? el.offsetWidth : el.getBoundingClientRect().width;
      const h = el.offsetHeight !== undefined ? el.offsetHeight : el.getBoundingClientRect().height;
      const bw = el.width && el.width.baseVal ? el.width.baseVal.value : w;
      const bh = el.height && el.height.baseVal ? el.height.baseVal.value : h;
      d.style.width = (w || bw) + "px";
      d.style.height = (h || bh) + "px";
      d.style.display = cs.display === "inline" ? "inline-block" : cs.display;
      d.style.verticalAlign = cs.verticalAlign;
      d.style.boxSizing = "border-box";
      el.replaceWith(d);
      const M = markerMatrix(d);
      const size = [d.offsetWidth, d.offsetHeight];
      d.replaceWith(el);
      return { M, w: size[0], h: size[1] };
    }

    // ---------- CSS gradients → SVG ----------
    function splitTop(s) {
      const out = []; let depth = 0, cur = "";
      for (const ch of s) {
        if (ch === "(") depth++;
        if (ch === ")") depth--;
        if (ch === "," && depth === 0) { out.push(cur.trim()); cur = ""; } else cur += ch;
      }
      if (cur.trim()) out.push(cur.trim());
      return out;
    }
    function lenToPx(v, ref) {
      if (v == null) return null;
      v = v.trim();
      if (v.endsWith("%")) return parseFloat(v) / 100 * ref;
      if (v.endsWith("px")) return parseFloat(v);
      if (v === "0") return 0;
      return parseFloat(v);
    }
    function parseStops(parts, lengthRef) {
      const stops = [];
      for (const p of parts) {
        const m = p.match(/^(rgba?\([^)]*\)|#[0-9a-fA-F]+|[a-z]+)\s*(.*)$/);
        if (!m) continue;
        const col = parseColor(m[1]) || { css: "#000000", a: 0 };
        const poss = m[2].trim() ? m[2].trim().split(/\s+/) : [];
        if (!poss.length) stops.push({ col, pos: null });
        else for (const ps of poss) stops.push({ col, pos: lenToPx(ps, lengthRef) / lengthRef });
      }
      if (!stops.length) return stops;
      if (stops[0].pos == null) stops[0].pos = 0;
      if (stops[stops.length - 1].pos == null) stops[stops.length - 1].pos = 1;
      for (let i = 1; i < stops.length; i++) {
        if (stops[i].pos == null) {
          let j = i; while (stops[j].pos == null) j++;
          const a = stops[i - 1].pos, b = stops[j].pos;
          for (let k = i; k < j; k++) stops[k].pos = a + (b - a) * (k - i + 1) / (j - i + 1);
        }
        if (stops[i].pos < stops[i - 1].pos) stops[i].pos = stops[i - 1].pos;
      }
      return stops;
    }
    const stopsXml = (stops) => stops.map(s => `<stop offset="${f(Math.max(0, Math.min(1, s.pos)))}" stop-color="${s.col.css}"${s.col.a < 1 ? ` stop-opacity="${f(s.col.a)}"` : ""}/>`).join("");
    function gradientDef(css, w, h, place) {
      // returns id of an SVG gradient in the element's local box space (or, with place.M, in screen space), or null
      const pre = place ? `${place.M ? mstr(place.M) + " " : ""}translate(${f(place.ox || 0)} ${f(place.oy || 0)}) ` : "";
      if (place && place.tw) { w = place.tw; h = place.th; }
      const lin = css.match(/^(repeating-)?linear-gradient\((.*)\)$/s);
      const rad = css.match(/^(repeating-)?radial-gradient\((.*)\)$/s);
      if (lin) {
        const parts = splitTop(lin[2]);
        let angle = 180;
        if (/^-?[\d.]+deg$/.test(parts[0])) { angle = parseFloat(parts.shift()); }
        else if (/^-?[\d.]+turn$/.test(parts[0])) { angle = parseFloat(parts.shift()) * 360; }
        else if (/^to /.test(parts[0])) {
          const t = parts.shift();
          const map = { "to top": 0, "to right": 90, "to bottom": 180, "to left": 270 };
          if (map[t] != null) angle = map[t];
          else {
            const right = /right/.test(t), bottom = /bottom/.test(t);
            const a = Math.atan2(w, h) * 180 / Math.PI; // corner angle
            angle = bottom ? (right ? 180 - a : 180 + a) : (right ? a : 360 - a);
          }
        }
        const rad_ = angle * Math.PI / 180;
        const sx = Math.sin(rad_), sy = -Math.cos(rad_);
        const L = Math.abs(w * sx) + Math.abs(h * sy);
        const cx = w / 2, cy = h / 2;
        const x1 = cx - sx * L / 2, y1 = cy - sy * L / 2, x2 = cx + sx * L / 2, y2 = cy + sy * L / 2;
        const stops = parseStops(parts, L);
        const id = nid("lg");
        defs.push(`<linearGradient id="${id}" gradientUnits="userSpaceOnUse" x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}"${pre ? ` gradientTransform="${pre.trim()}"` : ""}>${stopsXml(stops)}</linearGradient>`);
        return id;
      }
      if (rad) {
        const parts = splitTop(rad[2]);
        let shapeDesc = "";
        if (!/^(rgba?\(|#|transparent)/.test(parts[0])) shapeDesc = parts.shift();
        let cx = w / 2, cy = h / 2, rx, ry;
        const atM = shapeDesc.match(/at\s+(\S+)\s+(\S+)/);
        if (atM) {
          const kw = { left: "0%", center: "50%", right: "100%", top: "0%", bottom: "100%" };
          cx = lenToPx(kw[atM[1]] || atM[1], w); cy = lenToPx(kw[atM[2]] || atM[2], h);
        }
        const shapePart = shapeDesc.replace(/at\s+.*$/, "").trim();
        const isCircle = /circle/.test(shapePart);
        const dims = shapePart.replace(/circle|ellipse/g, "").trim().split(/\s+/).filter(Boolean);
        const dx = Math.max(cx, w - cx), dy = Math.max(cy, h - cy);
        const nx = Math.min(cx, w - cx), ny = Math.min(cy, h - cy);
        if (dims.length && !/side|corner/.test(dims[0])) {
          rx = lenToPx(dims[0], w); ry = dims[1] ? lenToPx(dims[1], h) : rx;
        } else {
          const kw = dims[0] || "farthest-corner";
          if (kw === "closest-side") { rx = nx; ry = ny; if (isCircle) rx = ry = Math.min(nx, ny); }
          else if (kw === "farthest-side") { rx = dx; ry = dy; if (isCircle) rx = ry = Math.max(dx, dy); }
          else if (kw === "closest-corner") { if (isCircle) rx = ry = Math.hypot(nx, ny); else { rx = nx * Math.SQRT2; ry = ny * Math.SQRT2; } }
          else { if (isCircle) rx = ry = Math.hypot(dx, dy); else { rx = dx * Math.SQRT2; ry = dy * Math.SQRT2; } }
        }
        rx = Math.max(rx, 0.01); ry = Math.max(ry, 0.01);
        const stops = parseStops(parts, rx);
        const id = nid("rg");
        defs.push(`<radialGradient id="${id}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" gradientTransform="${pre}translate(${f(cx)} ${f(cy)}) scale(${f(rx)} ${f(ry)})">${stopsXml(stops)}</radialGradient>`);
        return id;
      }
      return null;
    }

    function bgPlacement(cs, w, h, layerIndexFromTop) {
      const pick = (v) => { const a = splitTop(v); return a[Math.min(layerIndexFromTop, a.length - 1)] || a[0]; };
      const size = pick(cs.backgroundSize || "auto"), pos = pick(cs.backgroundPosition || "0% 0%");
      let tw = w, th = h;
      if (size && size !== "auto" && size !== "auto auto" && size !== "cover" && size !== "contain") {
        const [sx, sy] = size.split(/\s+/);
        tw = sx === "auto" ? w : lenToPx(sx, w); th = !sy || sy === "auto" ? h : lenToPx(sy, h);
      }
      const [px, py] = (pos || "0% 0%").split(/\s+/);
      const off = (v, box, tile) => (v || "0%").trim().endsWith("%") ? (box - tile) * parseFloat(v) / 100 : lenToPx(v, box);
      return { tw, th, ox: off(px, w, tw), oy: off(py, h, th) };
    }

    // ---------- shapes ----------
    function radii(cs, w, h) {
      const r = (v, ref) => { const p = v.split(" "); return [lenToPx(p[0], ref), lenToPx(p[1] || p[0], ref === w ? h : w)]; };
      return {
        tl: r(cs.borderTopLeftRadius, w), tr: r(cs.borderTopRightRadius, w),
        br: r(cs.borderBottomRightRadius, w), bl: r(cs.borderBottomLeftRadius, w),
      };
    }
    function boxShape(cs, w, h, inset = 0) {
      const R = radii(cs, w, h);
      const x = inset, y = inset, W_ = w - 2 * inset, H_ = h - 2 * inset;
      // CSS: if adjacent radii overflow a side, scale ALL radii by the same factor
      const fct = Math.min(1,
        w / Math.max(1e-6, R.tl[0] + R.tr[0]), w / Math.max(1e-6, R.bl[0] + R.br[0]),
        h / Math.max(1e-6, R.tl[1] + R.bl[1]), h / Math.max(1e-6, R.tr[1] + R.br[1]));
      const adj = (v) => Math.max(0, v * fct - inset);
      const [tlx, tly] = [adj(R.tl[0]), adj(R.tl[1])];
      const [trx, try_] = [adj(R.tr[0]), adj(R.tr[1])];
      const [brx, bry] = [adj(R.br[0]), adj(R.br[1])];
      const [blx, bly] = [adj(R.bl[0]), adj(R.bl[1])];
      const same = Math.abs(tlx - trx) < 0.01 && Math.abs(trx - brx) < 0.01 && Math.abs(brx - blx) < 0.01 && Math.abs(tly - try_) < 0.01 && Math.abs(try_ - bry) < 0.01 && Math.abs(bry - bly) < 0.01;
      if (same && tlx >= W_ / 2 - 0.01 && tly >= H_ / 2 - 0.01) return { tag: "ellipse", attrs: `cx="${f(x + W_ / 2)}" cy="${f(y + H_ / 2)}" rx="${f(W_ / 2)}" ry="${f(H_ / 2)}"` };
      if (same) return { tag: "rect", attrs: `x="${f(x)}" y="${f(y)}" width="${f(W_)}" height="${f(H_)}"${tlx > 0 ? ` rx="${f(tlx)}" ry="${f(tly)}"` : ""}` };
      const d = `M${f(x + tlx)} ${f(y)}H${f(x + W_ - trx)}A${f(trx)} ${f(try_)} 0 0 1 ${f(x + W_)} ${f(y + try_)}V${f(y + H_ - bry)}A${f(brx)} ${f(bry)} 0 0 1 ${f(x + W_ - brx)} ${f(y + H_)}H${f(x + blx)}A${f(blx)} ${f(bly)} 0 0 1 ${f(x)} ${f(y + H_ - bly)}V${f(y + tly)}A${f(tlx)} ${f(tly)} 0 0 1 ${f(x + tlx)} ${f(y)}Z`;
      return { tag: "path", attrs: `d="${d}"` };
    }
    // box-shadow → outer shadows (blurred shape copies under the box) + inset shadows (clipped inner strokes)
    function boxShadows(cs, w, h, M, scale) {
      const bs = cs.boxShadow;
      if (!bs || bs === "none") return { under: "", over: "" };
      let under = "", over = "";
      const list = splitTop(bs);
      for (const sh of list.reverse()) {
        const inset = /\binset\b/.test(sh);
        const col = (sh.match(/rgba?\([^)]*\)|#[0-9a-f]{3,8}/i) || ["rgb(0,0,0)"])[0];
        const c = parseColor(col); if (!c) continue;
        const nums = sh.replace(col, "").replace("inset", "").trim().split(/\s+/).map(parseFloat).filter(n => !isNaN(n));
        const [dx = 0, dy = 0, blur = 0, spread = 0] = nums;
        const T = ` transform="${mstr(M)}"`;
        const fid = blur > 0 ? nid("flou") : null;
        if (fid) defs.push(`<filter id="${fid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="${f(blur / 2 * scale)}"/></filter>`);
        const fa = fid ? ` filter="url(#${fid})"` : "";
        const op = c.a < 1 ? ` fill-opacity="${f(c.a)}"` : "";
        if (!inset) {
          const sp = boxShape(cs, w + 2 * spread, h + 2 * spread);
          const Ms = M.translate(dx - spread, dy - spread);
          under += `<g${fa}><${sp.tag} transform="${mstr(Ms)}" ${sp.attrs} fill="${c.css}"${op}/></g>`;
        } else {
          const shape = boxShape(cs, w, h);
          const cid = nid("clip");
          defs.push(`<clipPath id="${cid}" clipPathUnits="userSpaceOnUse"><${shape.tag}${T} ${shape.attrs}/></clipPath>`);
          const sw = 2 * (spread + blur * 0.5) + 0.01;
          const ring = boxShape(cs, w, h);
          const Mo = M.translate(dx, dy);
          over += `<g clip-path="url(#${cid})"><g${fa}><${ring.tag} transform="${mstr(Mo)}" ${ring.attrs} fill="none" stroke="${c.css}" stroke-width="${f(sw)}"${c.a < 1 ? ` stroke-opacity="${f(c.a)}"` : ""}/></g></g>`;
        }
      }
      return { under, over };
    }
    function clipPathFromCss(cp, w, h, M) {
      if (!cp || cp === "none") return null;
      let shape = null;
      let m;
      if ((m = cp.match(/^inset\((.*)\)$/))) {
        const v = m[1].split(/\s+round\s+/)[0].trim().split(/\s+/);
        const t = lenToPx(v[0], h), r = lenToPx(v[1] ?? v[0], w), b = lenToPx(v[2] ?? v[0], h), l = lenToPx(v[3] ?? v[1] ?? v[0], w);
        shape = `<rect x="${f(l)}" y="${f(t)}" width="${f(Math.max(0, w - l - r))}" height="${f(Math.max(0, h - t - b))}"/>`;
      } else if ((m = cp.match(/^circle\((.*)\)$/))) {
        const [rr, at] = m[1].split(/\s+at\s+/);
        const r = lenToPx(rr || "50%", Math.hypot(w, h) / Math.SQRT2);
        const [ax, ay] = (at || "50% 50%").split(/\s+/);
        shape = `<circle cx="${f(lenToPx(ax, w))}" cy="${f(lenToPx(ay, h))}" r="${f(r)}"/>`;
      } else if ((m = cp.match(/^ellipse\((.*)\)$/))) {
        const [rr, at] = m[1].split(/\s+at\s+/);
        const [rx, ry] = (rr || "50% 50%").split(/\s+/);
        const [ax, ay] = (at || "50% 50%").split(/\s+/);
        shape = `<ellipse cx="${f(lenToPx(ax, w))}" cy="${f(lenToPx(ay, h))}" rx="${f(lenToPx(rx, w))}" ry="${f(lenToPx(ry, h))}"/>`;
      } else if ((m = cp.match(/^polygon\((.*)\)$/))) {
        const pts = splitTop(m[1].replace(/^(nonzero|evenodd),/, "")).map(p => { const [x, y] = p.trim().split(/\s+/); return `${f(lenToPx(x, w))},${f(lenToPx(y, h))}`; });
        shape = `<polygon points="${pts.join(" ")}"/>`;
      }
      if (!shape) return null;
      const id = nid("clip");
      defs.push(`<clipPath id="${id}" clipPathUnits="userSpaceOnUse">${shape.replace(/^<(\w+)/, `<$1 transform="${mstr(M)}"`)}</clipPath>`);
      return id;
    }
    function parseFilter(filter, scale) {
      if (!filter || filter === "none") return null;
      const prims = [];
      let m; const re = /(blur|drop-shadow|brightness|saturate|contrast|opacity|grayscale|sepia|hue-rotate)\(([^()]*(?:\([^()]*\)[^()]*)*)\)/g;
      let src = "SourceGraphic", n = 0;
      while ((m = re.exec(filter))) {
        const out = `f${n++}`;
        if (m[1] === "blur") prims.push(`<feGaussianBlur in="${src}" stdDeviation="${f(parseFloat(m[2]) * scale)}" result="${out}"/>`);
        else if (m[1] === "drop-shadow") {
          const col = (m[2].match(/rgba?\([^)]*\)|#[0-9a-f]+/i) || ["rgba(0,0,0,0.5)"])[0];
          const nums = m[2].replace(col, "").trim().split(/\s+/).map(parseFloat);
          const c = parseColor(col) || { css: "#000", a: 0 };
          prims.push(`<feDropShadow in="${src}" dx="${f((nums[0] || 0) * scale)}" dy="${f((nums[1] || 0) * scale)}" stdDeviation="${f((nums[2] || 0) / 2 * scale)}" flood-color="${c.css}" flood-opacity="${f(c.a)}" result="${out}"/>`);
        } else if (m[1] === "brightness") {
          const v = parseFloat(m[2]); prims.push(`<feComponentTransfer in="${src}" result="${out}"><feFuncR type="linear" slope="${v}"/><feFuncG type="linear" slope="${v}"/><feFuncB type="linear" slope="${v}"/></feComponentTransfer>`);
        } else if (m[1] === "saturate") {
          prims.push(`<feColorMatrix in="${src}" type="saturate" values="${parseFloat(m[2])}" result="${out}"/>`);
        } else if (m[1] === "opacity") {
          prims.push(`<feComponentTransfer in="${src}" result="${out}"><feFuncA type="linear" slope="${parseFloat(m[2])}"/></feComponentTransfer>`);
        } else continue;
        src = out;
      }
      if (!prims.length) return null;
      const id = nid("filtre");
      defs.push(`<filter id="${id}" x="-50%" y="-50%" width="200%" height="200%" color-interpolation-filters="sRGB">${prims.join("")}</filter>`);
      stats.filters++;
      return id;
    }
    function maskFromCss(cs, w, h, M) {
      const mi = cs.webkitMaskImage || cs.maskImage;
      if (!mi || mi === "none") return { ok: true, id: null };
      if (/url\(/.test(mi)) return { ok: false };
      const layers = splitTop(mi);
      const rects = [];
      for (const L of layers) {
        // convert alpha-based CSS mask gradient into a luminance mask (white = visible)
        const lumCss = L.replace(/rgba?\(([^)]*)\)/g, (_, inner) => {
          const p = inner.split(/[ ,\/]+/).filter(Boolean).map(Number); const a = p.length > 3 ? p[3] : 1;
          const g = Math.round(a * 255); return `rgb(${g}, ${g}, ${g})`;
        });
        const gid = gradientDef(lumCss, w, h);
        if (!gid) return { ok: false };
        rects.push(`<rect x="0" y="0" width="${f(w)}" height="${f(h)}" fill="url(#${gid})"/>`);
      }
      const id = nid("masque");
      defs.push(`<mask id="${id}" maskUnits="userSpaceOnUse" x="-4000" y="-4000" width="9920" height="9080"><g transform="${mstr(M)}">${rects.join("")}</g></mask>`);
      return { ok: true, id };
    }

    // ---------- images ----------
    const dataCache = new Map();
    async function dataUri(src) {
      if (dataCache.has(src)) return dataCache.get(src);
      const blob = await (await fetch(src)).blob();
      const uri = await new Promise(r => { const fr = new FileReader(); fr.onload = () => r(fr.result); fr.readAsDataURL(blob); });
      dataCache.set(src, uri);
      return uri;
    }

    // ---------- inline SVG cloning ----------
    const SVG_PROPS = ["fill", "fill-opacity", "fill-rule", "stroke", "stroke-width", "stroke-opacity", "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "stroke-dashoffset", "stroke-miterlimit", "opacity", "stop-color", "stop-opacity", "font-family", "font-size", "font-weight", "font-style", "letter-spacing", "text-anchor", "dominant-baseline", "clip-path", "mask", "filter", "paint-order", "visibility", "flood-color", "flood-opacity", "lighting-color", "mix-blend-mode"];
    const DEFAULTS = { "fill-opacity": "1", "stroke-opacity": "1", "opacity": "1", "stroke-dasharray": "none", "stroke-dashoffset": "0px", "stroke-miterlimit": "4", "fill-rule": "nonzero", "stroke-linecap": "butt", "stroke-linejoin": "miter", "clip-path": "none", "mask": "none", "filter": "none", "paint-order": "normal", "visibility": "visible", "mix-blend-mode": "normal", "stop-opacity": "1", "font-style": "normal", "letter-spacing": "normal", "text-anchor": "start", "dominant-baseline": "auto", "flood-opacity": "1", "stroke": "none" };
    const NON_RENDER = new Set(["defs", "symbol", "linearGradient", "radialGradient", "pattern", "clipPath", "mask", "filter", "marker", "style", "script", "title", "desc", "metadata"]);
    function cleanUrl(v) { return v.replace(/url\("?#([^")]+)"?\)/g, "url(#$1)").replace(/url\("?[^")]*#([^")]+)"?\)/g, "url(#$1)"); }
    function inlineSvgStyles(orig, clone) {
      if (orig.nodeType !== 1) return;
      const tag = orig.localName;
      if (tag === "style" || tag === "script") { clone.remove(); return; }
      const cs = getComputedStyle(orig);
      const inDefs = !!orig.closest("defs,symbol,linearGradient,radialGradient,pattern,clipPath,mask,filter,marker");
      if (!inDefs && (cs.display === "none")) { clone.remove(); return; }
      const par = orig.parentElement;
      const pcs = par && !(par instanceof SVGSVGElement && !par.parentElement.closest("svg")) && par.namespaceURI === SVGNS ? getComputedStyle(par) : null;
      const INHERITED = /^(fill|fill-opacity|fill-rule|stroke|stroke-width|stroke-opacity|stroke-linecap|stroke-linejoin|stroke-dasharray|stroke-dashoffset|stroke-miterlimit|font-family|font-size|font-weight|font-style|letter-spacing|text-anchor|dominant-baseline|paint-order|visibility)$/;
      for (const p of SVG_PROPS) {
        let v = cs.getPropertyValue(p);
        if (!v) continue;
        // keep inheritance intact (crucial inside <symbol>, whose content inherits from the <use>)
        if (INHERITED.test(p) && !orig.hasAttribute(p) && (pcs ? pcs.getPropertyValue(p) === v : (inDefs || DEFAULTS[p] === v || (p === "fill" && v === "rgb(0, 0, 0)")))) continue;
        if (p === "stop-color" || p === "stop-opacity") { if (tag !== "stop") continue; }
        if (p === "flood-color" || p === "flood-opacity" || p === "lighting-color") { if (!/^fe/.test(tag)) continue; }
        if ((p === "stop-color" || p === "flood-color") && /rgba?\(/.test(v)) { const c = parseColor(v); if (c) { clone.setAttribute(p, c.css); if (c.a < 1) clone.setAttribute(p === "stop-color" ? "stop-opacity" : "flood-opacity", f(c.a)); } continue; }
        if (DEFAULTS[p] !== undefined && v === DEFAULTS[p] && !orig.hasAttribute(p)) continue;
        if (p.startsWith("font") || p === "letter-spacing" || p === "text-anchor" || p === "dominant-baseline") { if (!/^(text|tspan|textPath)$/.test(tag)) continue; }
        if (p === "mix-blend-mode") { if (v !== "normal") clone.setAttribute("style", `mix-blend-mode:${v}`); continue; }
        if ((p === "fill" || p === "stroke") && /rgba?\(/.test(v)) {
          const c = parseColor(v);
          if (!c) { clone.setAttribute(p, "none"); continue; }
          clone.setAttribute(p, c.css);
          if (c.a < 1) clone.setAttribute(p + "-opacity", f(c.a * parseFloat(cs.getPropertyValue(p + "-opacity") || 1)));
          continue;
        }
        if (/url\(/.test(v)) v = cleanUrl(v);
        if (p === "stroke-dasharray" && v !== "none") v = v.replace(/px/g, "");
        if (p === "stroke-dashoffset" || p === "stroke-width" || p === "font-size" || p === "letter-spacing") v = v.replace(/px/g, "");
        clone.setAttribute(p, v);
      }
      // CSS transform on SVG element (wins over the attribute)
      if (!inDefs && orig instanceof SVGGraphicsElement && !(orig instanceof SVGSVGElement)) {
        const t = cs.transform;
        if (t && t !== "none") {
          const M = new DOMMatrix(t);
          let [ox, oy] = cs.transformOrigin.split(" ").map(parseFloat);
          if (cs.transformBox === "fill-box") { try { const bb = orig.getBBox(); ox += bb.x; oy += bb.y; } catch (e) {} }
          const T = new DOMMatrix().translate(ox, oy).multiply(M).translate(-ox, -oy);
          clone.setAttribute("transform", mstr(T));
        }
      }
      if (!inDefs && parseFloat(cs.opacity) === 0 && !NON_RENDER.has(tag)) { clone.remove(); return; }
      if (!inDefs && cs.visibility === "hidden" && !orig.querySelector("*")) { clone.remove(); return; }
      clone.removeAttribute("class");
      if (clone.getAttribute("style") && !/mix-blend-mode/.test(clone.getAttribute("style"))) clone.removeAttribute("style");
      [...clone.attributes].forEach(a => { if (a.name.startsWith("data-")) clone.removeAttribute(a.name); });
      const oc = [...orig.children], cc = [...clone.children];
      for (let i = 0; i < oc.length; i++) if (cc[i]) inlineSvgStyles(oc[i], cc[i]);
    }
    function svgUserMatrix(svg) {
      const cs = getComputedStyle(svg);
      const bw = parseFloat(cs.width) || 0, bh = parseFloat(cs.height) || 0;
      // box → screen via markers on a same-sized stand-in (follows 3D/perspective projection)
      const d = document.createElement("div");
      if (svg.id) d.id = svg.id;
      d.setAttribute("class", svg.getAttribute("class") || "");
      d.setAttribute("style", svg.getAttribute("style") || "");
      d.style.width = bw + "px"; d.style.height = bh + "px";
      d.style.display = cs.display === "inline" ? "inline-block" : cs.display;
      d.style.verticalAlign = cs.verticalAlign; d.style.boxSizing = "content-box"; d.style.padding = "0"; d.style.border = "0";
      svg.replaceWith(d);
      const Mbox = markerMatrix(d);
      d.replaceWith(svg);
      // user space → box (viewBox + preserveAspectRatio)
      const vb = svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width ? svg.viewBox.baseVal : null;
      if (!vb) return Mbox;
      const par = (svg.getAttribute("preserveAspectRatio") || "xMidYMid meet").trim();
      let sx = bw / vb.width, sy = bh / vb.height, tx = 0, ty = 0;
      if (!/^none/.test(par)) {
        const sc = /slice/.test(par) ? Math.max(sx, sy) : Math.min(sx, sy);
        const al = par.split(/\s+/)[0];
        const ax = /xMin/.test(al) ? 0 : /xMax/.test(al) ? 1 : 0.5, ay = /YMin/.test(al) ? 0 : /YMax/.test(al) ? 1 : 0.5;
        tx = (bw - vb.width * sc) * ax; ty = (bh - vb.height * sc) * ay; sx = sy = sc;
      }
      return Mbox.multiply(new DOMMatrix([sx, 0, 0, sy, tx - vb.x * sx, ty - vb.y * sy]));
    }
    const globalDefs = [];
    const hoisted = new Set();
    function emitSvgRoot(svg, groupAttrs) {
      stats.svgs++;
      const M = svgUserMatrix(svg);
      const clone = svg.cloneNode(true);
      inlineSvgStyles(svg, clone);
      // hoist defs / symbols / gradients so <use> across svgs keeps working
      clone.querySelectorAll("defs, symbol").forEach(d => {
        if (d.parentNode && d.parentNode.closest && d.parentNode.closest("defs,symbol") && d.parentNode !== clone) return;
        globalDefs.push(d.localName === "defs" ? d.innerHTML : d.outerHTML);
        d.remove();
      });
      // viewport clip (inline svg default overflow:hidden)
      let clipAttr = "";
      const ov = getComputedStyle(svg).overflow;
      if (ov !== "visible") {
        const vb = svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width ? svg.viewBox.baseVal : null;
        const vx = vb ? vb.x : 0, vy = vb ? vb.y : 0;
        const vw = vb ? vb.width : svg.width.baseVal.value, vh = vb ? vb.height : svg.height.baseVal.value;
        const id = nid("clip");
        // preserveAspectRatio may letterbox; clip to the visible viewport rectangle in user space
        const inv = M.inverse();
        const r = svg.getBoundingClientRect();
        const pts = [[r.left, r.top], [r.right, r.top], [r.right, r.bottom], [r.left, r.bottom]].map(([x, y]) => { const p = inv.transformPoint(new DOMPoint(x, y)); return `${f(p.x)},${f(p.y)}`; });
        const useViewBox = Math.abs(M.b) < 1e-4 && Math.abs(M.c) < 1e-4; // axis-aligned → exact viewBox rect
        defs.push(`<clipPath id="${id}" clipPathUnits="userSpaceOnUse">${useViewBox ? `<rect x="${f(vx)}" y="${f(vy)}" width="${f(vw)}" height="${f(vh)}"/>` : `<polygon points="${pts.join(" ")}"/>`}</clipPath>`);
        clipAttr = ` clip-path="url(#${id})"`;
      }
      return `<g ${groupAttrs}><g transform="${mstr(M)}"${clipAttr}>${clone.innerHTML}</g></g>`;
    }

    // ---------- text ----------
    function textFillAndStroke(cs, scale) {
      let a = "";
      const c = parseColor(cs.webkitTextFillColor && cs.webkitTextFillColor !== cs.color ? cs.webkitTextFillColor : cs.color);
      a += c ? ` fill="${c.css}"${c.a < 1 ? ` fill-opacity="${f(c.a)}"` : ""}` : ` fill="none"`;
      const sw = parseFloat(cs.webkitTextStrokeWidth || 0);
      if (sw > 0) {
        const sc = parseColor(cs.webkitTextStrokeColor);
        if (sc) a += ` stroke="${sc.css}" stroke-width="${f(sw * scale)}" stroke-linejoin="round"${sc.a < 1 ? ` stroke-opacity="${f(sc.a)}"` : ""}`;
        if (/stroke/.test(cs.paintOrder || "") && (cs.paintOrder || "").indexOf("stroke") < (cs.paintOrder || "fill").indexOf("fill") + 100) a += ` paint-order="stroke fill"`;
      }
      return a;
    }
    function textShadowFilter(ts, scale) {
      if (!ts || ts === "none") return "";
      const shadows = splitTop(ts);
      const prims = []; const merges = [];
      shadows.slice(0, 3).forEach((s, i) => {
        const col = (s.match(/rgba?\([^)]*\)|#[0-9a-f]+/i) || ["rgb(0,0,0)"])[0];
        const nums = s.replace(col, "").trim().split(/\s+/).map(parseFloat);
        const c = parseColor(col) || { css: "#000", a: 0 };
        prims.push(`<feDropShadow in="SourceGraphic" dx="${f((nums[0] || 0) * scale)}" dy="${f((nums[1] || 0) * scale)}" stdDeviation="${f((nums[2] || 0) / 2 * scale)}" flood-color="${c.css}" flood-opacity="${f(c.a)}" result="s${i}"/>`);
        merges.push(`<feMergeNode in="s${i}"/>`);
      });
      const id = nid("ombre_texte");
      // drop shadows include the source; merge in reverse so the first shadow paints on top
      defs.push(`<filter id="${id}" x="-20%" y="-50%" width="140%" height="200%" color-interpolation-filters="sRGB">${prims.join("")}<feMerge>${merges.reverse().join("")}</feMerge></filter>`);
      return ` filter="url(#${id})"`;
    }
    const textFillStack = [];
    function emitText(node, parentEl) {
      const raw = node.textContent;
      if (!raw.trim()) return "";
      const cs = getComputedStyle(parentEl);
      if (cs.visibility === "hidden") return "";
      const M = markerMatrix(parentEl);
      const scale = Math.hypot(M.a, M.b);
      const rot = Math.atan2(M.b, M.a) * 180 / Math.PI;
      // baseline from font metrics: a text Range's rect spans fontAscent+fontDescent (scaled)
      const mctx = (window.__hfCtx ||= document.createElement("canvas").getContext("2d"));
      mctx.font = `${cs.fontStyle} ${cs.fontWeight} ${parseFloat(cs.fontSize)}px ${cs.fontFamily}`;
      const mm = mctx.measureText("Hg");
      const asc = mm.fontBoundingBoxAscent, desc = mm.fontBoundingBoxDescent;
      const words = [];
      const re = /\S+/g; let m;
      while ((m = re.exec(raw))) {
        const r = document.createRange(); r.setStart(node, m.index); r.setEnd(node, m.index + m[0].length);
        const rects = r.getClientRects();
        if (!rects.length) continue;
        words.push({ s: m.index, e: m.index + m[0].length, rect: rects[0] });
      }
      if (!words.length) return "";
      // group into lines (same visual line → similar top)
      const lines = [];
      for (const w of words) {
        const L = lines[lines.length - 1];
        if (L && Math.abs(L.top - w.rect.top) < w.rect.height * 0.5) { L.words.push(w); }
        else lines.push({ top: w.rect.top, words: [w] });
      }
      const baseOffOf = (rect) => rect.height * (asc / Math.max(1e-6, asc + desc));
      let tt = cs.textTransform;
      const family = cs.fontFamily.split(",")[0].replace(/["']/g, "").trim();
      const fs = parseFloat(cs.fontSize) * scale;
      const ls = cs.letterSpacing === "normal" ? 0 : parseFloat(cs.letterSpacing) * scale;
      let paint = textFillAndStroke(cs, scale);
      if (/fill="none"/.test(paint) && textFillStack.length) paint = paint.replace(/fill="none"/, `fill="url(#${textFillStack[textFillStack.length - 1]})"`);
      const shadow = textShadowFilter(cs.textShadow, scale);
      let out = "";
      for (const L of lines) {
        let txt = raw.slice(L.words[0].s, L.words[L.words.length - 1].e).replace(/\s+/g, " ");
        if (tt === "uppercase") txt = txt.toUpperCase(); else if (tt === "lowercase") txt = txt.toLowerCase();
        const x = Math.abs(rot) > 0.5 ? null : L.words[0].rect.left;
        const y = L.top + baseOffOf(L.words[0].rect);
        const tf = Math.abs(rot) > 0.5 ? ` transform="translate(${f(L.words[0].rect.left)} ${f(y)}) rotate(${f(rot)})"` : "";
        const pos = tf ? ` x="0" y="0"` : ` x="${f(x)}" y="${f(y)}"`;
        out += `<text${pos}${tf} font-family="${esc(family)}" font-size="${f(fs)}" font-weight="${cs.fontWeight}"${cs.fontStyle !== "normal" ? ` font-style="${cs.fontStyle}"` : ""}${ls ? ` letter-spacing="${f(ls)}"` : ""}${paint}${shadow} xml:space="preserve">${esc(txt)}</text>`;
        stats.texts++;
      }
      return out;
    }

    // ---------- HTML box painting ----------
    async function paintEl(el) {
      if (el.nodeType !== 1) return "";
      const tag = el.localName;
      if (tag === "script" || tag === "style" || tag === "template") return "";
      const cs = getComputedStyle(el);
      if (cs.display === "none") return "";
      const op = parseFloat(cs.opacity);
      if (op <= 0.001) return "";
      const name = niceName(el);
      const blend = cs.mixBlendMode !== "normal" ? ` style="mix-blend-mode:${cs.mixBlendMode}"` : "";
      let gAttrs = `id="${name}"`;
      if (op < 0.999) gAttrs += ` opacity="${f(op)}"`;
      gAttrs += blend;

      if (tag === "svg") {
        const fl = parseFilter(cs.filter, 1);
        if (fl) gAttrs += ` filter="url(#${fl})"`;
        if (cs.visibility === "hidden") return "";
        return emitSvgRoot(el, gAttrs);
      }

      let M, w, h;
      if (tag === "img" || tag === "video" || tag === "canvas") { ({ M, w, h } = replacedMatrix(el)); }
      else { M = markerMatrix(el); w = el.offsetWidth; h = el.offsetHeight; }
      const scale = Math.hypot(M.a, M.b) || 1;
      const fl = parseFilter(cs.filter, scale);
      if (fl) gAttrs += ` filter="url(#${fl})"`;
      const cpid = clipPathFromCss(cs.clipPath, w, h, M);
      if (cpid) gAttrs += ` clip-path="url(#${cpid})"`;
      const mk = maskFromCss(cs, w, h, M);
      if (!mk.ok) { stats.skippedMasks++; return ""; }
      if (mk.id) gAttrs += ` mask="url(#${mk.id})"`;

      let own = "";
      const visible = cs.visibility !== "hidden";
      if (visible && w > 0 && h > 0) {
        const T = ` transform="${mstr(M)}"`;
        if (tag === "img") {
          const uri = await dataUri(el.currentSrc || el.src);
          const fit = cs.objectFit;
          const par = fit === "contain" ? "xMidYMid meet" : fit === "cover" ? "xMidYMid slice" : "none";
          own += `<image${T} x="0" y="0" width="${f(w)}" height="${f(h)}" preserveAspectRatio="${par}" href="${uri}"/>`;
          stats.images++;
        } else {
          const shape = boxShape(cs, w, h);
          const bg = parseColor(cs.backgroundColor);
          if (bg) { own += `<${shape.tag}${T} ${shape.attrs} fill="${bg.css}"${bg.a < 1 ? ` fill-opacity="${f(bg.a)}"` : ""}/>`; }
          const clipText = /text/.test((cs.webkitBackgroundClip || "") + (cs.backgroundClip || ""));
          if (cs.backgroundImage && cs.backgroundImage !== "none" && !clipText) {
            const all = splitTop(cs.backgroundImage);
            const layers = all.map((L, i) => ({ L, i })).reverse(); // CSS paints last layer at the bottom
            for (const { L, i } of layers) {
              if (/^url\(/.test(L)) {
                const u = L.match(/url\("?([^")]+)"?\)/)[1];
                const uri = await dataUri(u);
                own += `<image${T} x="0" y="0" width="${f(w)}" height="${f(h)}" preserveAspectRatio="${cs.backgroundSize === "contain" ? "xMidYMid meet" : cs.backgroundSize === "cover" ? "xMidYMid slice" : "none"}" href="${uri}"/>`;
                continue;
              }
              const gid = gradientDef(L, w, h, bgPlacement(cs, w, h, i));
              if (gid) own += `<${shape.tag}${T} ${shape.attrs} fill="url(#${gid})"/>`;
            }
          }
          const bw = parseFloat(cs.borderTopWidth);
          if (bw > 0 && cs.borderTopStyle !== "none") {
            const bc = parseColor(cs.borderTopColor);
            if (bc) { const s2 = boxShape(cs, w, h, bw / 2); own += `<${s2.tag}${T} ${s2.attrs} fill="none" stroke="${bc.css}" stroke-width="${f(bw)}"${bc.a < 1 ? ` stroke-opacity="${f(bc.a)}"` : ""}${cs.borderTopStyle === "dashed" ? ` stroke-dasharray="${f(bw * 3)} ${f(bw * 2)}"` : cs.borderTopStyle === "dotted" ? ` stroke-dasharray="0 ${f(bw * 2)}" stroke-linecap="round"` : ""}/>`; }
          }
          if (cs.boxShadow && cs.boxShadow !== "none") {
            stats.boxShadows++;
            const sh = boxShadows(cs, w, h, M, scale);
            own = sh.under + own + sh.over;
          }
          if (own) stats.boxes++;
        }
      }
      // background-clip:text → the background becomes the fill of the text below
      let pushedFill = false;
      if (/text/.test((cs.webkitBackgroundClip || "") + (cs.backgroundClip || "")) && cs.backgroundImage !== "none") {
        const L = splitTop(cs.backgroundImage)[0];
        const gid = gradientDef(L, w, h, { M, ...bgPlacement(cs, w, h, 0) });
        if (gid) { textFillStack.push(gid); pushedFill = true; }
      }
      // children: text nodes + elements, painted in z-order
      let kids = "";
      const children = [...el.childNodes];
      const elems = children.map((n, i) => ({ n, i, z: n.nodeType === 1 ? (() => { const c = getComputedStyle(n); return c.position !== "static" && c.zIndex !== "auto" ? parseInt(c.zIndex, 10) : 0; })() : 0 }));
      elems.sort((a, b) => a.z - b.z || a.i - b.i);
      for (const { n } of elems) {
        if (n.nodeType === 3) { if (visible || true) kids += emitText(n, el); }
        else if (n.nodeType === 1) kids += await paintEl(n);
      }
      if (pushedFill) textFillStack.pop();
      if (kids && tag !== "img" && /(hidden|clip)/.test(cs.overflow + cs.overflowX + cs.overflowY)) {
        const s3 = boxShape(cs, w, h);
        const id = nid("clip");
        defs.push(`<clipPath id="${id}" clipPathUnits="userSpaceOnUse"><${s3.tag} transform="${mstr(M)}" ${s3.attrs}/></clipPath>`);
        kids = `<g clip-path="url(#${id})">${kids}</g>`;
      }
      if (!own && !kids) return "";
      return `<g ${gAttrs}>${own}${kids}</g>`;
    }

    const body = await paintEl(sceneRoot);
    const title = esc(opts.title || sceneRoot.getAttribute("data-composition-id"));
    const svg = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">\n<title>${title}</title>\n<defs>${globalDefs.join("")}${defs.join("")}</defs>\n${body}\n</svg>\n`;
    return { svg, stats };
  };
})();
