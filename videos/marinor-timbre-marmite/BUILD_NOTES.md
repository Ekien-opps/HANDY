# BUILD_NOTES — index.html composition (timbre-marmite)

## Log
- [start] No previous BUILD_NOTES existed: composition work starts from scratch (index.html = blank scaffold).
- Loaded hyperframes-core skill. Root: standalone, data-composition-id=main, 1080x1350, duration 1, data-fps 60 (optional hint).

## Status: DONE (final render renders/check_png, 60 RGBA frames, ~50 s with 2 workers)
Rebuild: python3 tools/split_front.py && python3 tools/build_index.py ; render: npx hyperframes render . --fps 60
--format png-sequence -o ./renders/check_png ; QA: python3 tools/verify_render.py

## Final QA numbers (tools/verify_render.py)
- 60 frames 1080x1350 RGBA; alpha outside paper bbox+8: 0 on f0-f35 (fragments move beyond it from f36, by spec;
  canvas border alpha 0 on every frame).
- fire-coloured px in pot opening / lid area f28-f59: 0. Outside vignette f1-f32 vs f0: max diff 0.
- static vignette corners f0-f32 vs f0: 0 (no motion-blur stack drift).
- changed-pixel bbox f1-f32 (pot, lid, outline, flame, glow): x 160..904, y 209..1050 (safe zone 160.1..913.7 x
  184.6..1153.9); only f28 touches pixel column 160 (22 AA px of the outline at the spec's sX 101 % cap).
- f0 vs reference-full-render.png at reference scale over white: mean |dRGB| 0.659 (whole artboard), 1.61 inside
  the stamp bbox, p99 25 (edges: outline, glitter resampling, printed-flame overhang clipped per spec 4.1.3).
- lint 0/0, check 0 findings.

## Known deviations
- Fragment motion blur f37 (90 deg) / f38 (45 deg) not implemented: <= 2 px of blur, and the 1/k opacity stack is
  not an exact average over transparent gaps (fragments are not opaque copies).
- Lid foreshortening = scaleY 1-0.15*(open/36)^2 (0.85 at peak), physically derived for a hinged disc seen at
  ~29 deg elevation (spec suggested 70 %); lid pivot H, bounces about C.
- Float f15-f19 values designed (spec gives only +-1.5 deg/+-2 px around -32/-32): -31.6/-31.0, -30.7/-30.3,
  -31.2/-30.9, -32.6/-32.6, -33.4/-33.6. Knob follow-through table <= 3 deg (in assets/stamp-runtime.js).
- Right handle drawn behind the flame (split from pot_front), see above.

## Architecture (decided)
- index.html is GENERATED: `python3 tools/build_index.py` (template tools/index.template.html + tools/inline_tear.py
  compact tear data + flame.json frames + stamp-parts.svg defs). Never hand-edit index.html; edit the template.
- Seek-safety: GSAP 3.14 suppresses onUpdate when the runtime seeks with suppressEvents=true (verified in
  hyperframe.runtime: totalTime(t, true)). So the proxy uses an accessor property: tl.to(proxy,{f:60,duration:1,
  ease:'none'}) and proxy's setter calls render(f). render(f) is pure (snap to integer within 1e-4).
- SVG layers: intact stamp = paperGrey + <use #stampTop>; stampTop (defs) = paperWhite + PICTURE.
  PICTURE (clip #vignetteClip) = NMAX motion-blur copies (isolated groups, opacity 1/(j+1)); each copy =
  vignette, printed flames, outline (filter #olF = union of 32 offsets of SourceAlpha on a 30.5 px circle +
  white flood; measured original outline = 30.5 px exact round offset), pot_back(+heat/slit tints via
  filters), <use #flameG> (flame evaluated at t, never blurred), pot_front, lid group, printed glitter.
- Tear: fragments = <use #stampTop> clipped by tear polygons; grey copy = paperGreyPath clipped by the polygon
  shifted +6.156 (no greyCopyD inlined). Lips revealed f34-35 by a mask of thick polylines along the crack
  up to the front (instead of 900 chunks) - same visual result, much smaller file.

## Log (cont.)
- Built tools/inline_tear.py, tools/build_index.py, tools/index.template.html, tools/snap_frames.mjs
  (fast preview: node tools/snap_frames.mjs <outDir> <frames> [transparent|checker|#hex] [dpr] [debugJSON]).
- First renders look right (rest pose, f12 open + flame, f27 blur, f36 tear).
- Motion-blur stacking findings (Chromium software raster):
  * vignette rect AA edge broke the opaque-copy assumption -> each copy now draws the vignette gradient
    extended 4 px past #vignetteClip (exact at f0 with up to 15 identical copies).
  * 16 copies (opacity 1/16) breaks rendering (large diffs) -> NMAX = 15.
  * still a ~-4/255 drift in some 256 px tiles away from the pot when copies differ (f26/f27): investigating;
    candidate fix = clip copies j>=1 to the motion envelope.
- ROOT CAUSE of the blur drift: Chromium pushed the PICTURE clip-path down to every copy, so the 1/k stack was
  not composited in one surface (drift -4/255 away from the pot, AA edge thickening at the vignette border,
  and garbage at 16 copies). FIX: copies wrapped in <g filter="url(#stackF)"> (identity feOffset) -> one
  offscreen surface. Verified: 20 identical copies == 1 copy (max 1/255), no drift at f27. NMAX = 16.
- Right handle split out of pot_front (tools/split_front.py -> pot_front_body.png + pot_handle_r.png, exact
  recombination) so the flame passes in front of it (z: back < handle_R < flame < front_body < lid).
- Real renderer (hyperframes render, screenshot mode, swiftshader) == snap_frames preview (f0 max diff 0).
  Full 60-frame PNG render took ~1 min with 2 workers.
- Runtime JS moved to assets/stamp-runtime.js (source of truth, hand-editable); index.html keeps the inline
  data (window.__STAMP_DATA) and the inline timeline registration (lint requires it inline). <svg id="stage">
  is now the top-level clip (svg is an opaque tag for the nested-structure rule). index.html = 202 lines.
- Lid light-wrap (heatLid, lid-local radial mask at the free edge, 0.32*heat), slit glow mask near the back
  rim, underside slide 10 px, motion-blur samples NMAX 32 (n = ceil(disp/3 px)+1 per frame).
- lint: 0/0. check: 0 findings (layout overflow of #intact/#frags bounding boxes marked
  data-layout-allow-overflow: full-canvas rasters rotated with the lid; visible pixels verified in canvas).
- QA script: python3 tools/verify_render.py [renders/check_png] -> JSON + snapshots/contact-sheet.jpg +
  snapshots/f0_vs_reference.png.

## Review fixes (spec lens review, 2026-10-13)
- SPEC-1 (no paper bridge on branch A): F3 rest translate (+6.4,+4.8) -> (+6.4,+7.5), peak (+8.6,+6.5) -> (+8.6,+10.1)
  in tools/build_tear.py. Result: no sealed alpha-0 holes on f37-f40 and f43-f59; transient contact only at the
  spring undershoot frames f41/f42 (x0.88/x0.92), which reads as the pieces knocking back. f59 gap continuous.
- SPEC-2 (no fragment motion blur f37/f38), SPEC-3 (grey stress mark), SPEC-4 (no 30 fps version): accepted, documented.
- 2x master rendered with: node tools/snap_frames.mjs renders/<dir> 0-59 transparent 2 (matches the 1x render
  after a 2:1 box downscale: mean |d| 0.25-0.32/255).

## Deliverables (renders/, see renders/LISEZ-MOI.txt)
- PNG 1080x1350 and 2160x2700 (RGBA), ProRes 4444 (1080) / 4444 XQ (2160) with alpha, WebM VP9 alpha 1080 and 432.
- Verified: ffprobe 60 frames, 1.000 s each; decoded alpha vs PNG: MOV mean 0.004/255, WebM 0.05/255.
