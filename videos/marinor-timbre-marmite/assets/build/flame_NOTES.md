# flame_NOTES (running log) - FLAME, timbre-marmite, option B / HyperFrames

## Status: DONE (v2). Re-run: `python3 tools/build_flame.py` (~15 s, deterministic; `--no-previews` for JSON only)

## Outputs
- assets/build/flame.json : meta (placement, colours, gradient, vertex order), poses P0 P1 SMEAR P2 P3 A B C,
  framePlan f9..f28, frames{} = baked per-frame layers (use these), checks (extremes per frame).
- assets/build/flame_poses.png (all poses, all layers, dark + #F6E8EA rows; guide lines at y=0 and y=-H_fl)
- assets/build/flame_inplace_f12.png (left: real z-order pot_back < flame(+glow 35 % screen, +glitter 70 % screen on core) < pot_front < lid at -36/-33.6; right: unoccluded, hidden skirt ghosted) + safe-zone guide, E and target crosshairs.
- assets/build/flame_frames_strip.png (f9..f27 in place with spec lid angles, context only).

## Design
- Straight edges only; tips 26-30 deg (P2: 29/28/27/28/29); 5 tongues leaning outward (fan); heights
  OL .35, FL .62, C 1.00, FR .70, OR .40 (right side taller: it is the side left visible by the lid).
- Base 240 at local y=0; outer edges continue straight through the base corners down to y=+90 (fan from the
  pot), then vertical skirt to skirtY (hidden under pot_front).
- OUT gradient userSpaceOnUse in flame-local px: (-70,30) #FF6B31 -> (95,-385) #FFA53A (light at the tips,
  along the lean, like the printed flames). MID #F9A825 inset 18, CORE #FBD021 inset 37.
- Inner layers = exact mitre inset (own wavefront offset, checked vs shapely buffer(-d, mitre): symdiff 0 px2),
  then spikes with neck < 21.6 px dropped by `drop_spike` (result is a subset, every edge parallel to an OUT
  edge, no chord cuts). Vanished tongues = zero-area spikes (vertices merged). 15 vertices per layer, every pose.
- SMEAR = (P1+P2)/2 with central tip at -1.30*H_fl (f10: 0.8*1.3 = 104 % H_fl, tip y 267.8).
- P0 = P1 x 0.08 (germ, OUT only; MID/CORE collapsed to a zero-area spine), not used by framePlan.
- framePlan on twos: f14 A | f15-16 B | f17-18 A | f19-20 C | f21-22 A | f23-24 B | f25-26 C | f27 A; f11 = 85 % P2 + 15 % SMEAR.

## Skirt (important for the composition)
- Inner front lip at x~627 is y~750, ~100 px BELOW E: a 30 px base extension would leave the base edge
  floating inside the pot. Skirt default y=+200 local; per-frame skirtY (framePlan + frames) is the smallest depth
  that puts every layer's bottom edge under opaque pot_front (alpha >= 0.995, also 4 px above): f9 390, f25 205,
  f26 245, f27 365, else 200. Bottom y of layer = skirtY - inset; x unchanged.
- The flame must sit between pot_back and pot_front. If FL_GLOW is drawn above pot_front, clip it to above the
  lip or it will show the skirt.

## Checks: canvas extremes per frame (OUT incl. skirt; ok = +-24 px glow inside x 160.1..913.7, y >= 184.6, height <= 1.2 H_fl)
| f | sY/sX | skirtY | minX | maxX | minY (top) | central tip | H ratio | ok (+24 glow) |
|---|---|---|---|---|---|---|---|---|
| 9 | 35/60 | 390 | 539.9 | 740.0 | 519.6 | (660.0;519.6) | 0.350 | True |
| 10 | 80/75 | 200 | 514.6 | 797.7 | 267.8 | (722.3;267.8) | 1.040 | True |
| 11 | 108/88 | 200 | 486.1 | 850.8 | 235.3 | (729.8;235.3) | 1.129 | True |
| 12 | 116/95 | 200 | 472.2 | 872.0 | 223.8 | (732.5;223.8) | 1.160 | True |
| 13 | 108/102 | 200 | 465.4 | 874.1 | 251.3 | (718.3;251.3) | 1.080 | True |
| 14 | 100/100 | 200 | 462.8 | 871.0 | 281.4 | (715.1;281.4) | 1.000 | True |
| 15 | 103/99.5 | 200 | 457.9 | 862.5 | 265.9 | (731.3;265.9) | 1.051 | True |
| 16 | 103/99.5 | 200 | 457.9 | 862.5 | 265.9 | (731.3;265.9) | 1.051 | True |
| 17 | 97/101.5 | 200 | 458.9 | 873.1 | 292.4 | (712.3;292.4) | 0.970 | True |
| 18 | 97/101.5 | 200 | 458.9 | 873.1 | 292.4 | (712.3;292.4) | 0.970 | True |
| 19 | 101/100 | 200 | 467.1 | 881.0 | 279.8 | (708.3;279.8) | 1.000 | True |
| 20 | 104/100 | 200 | 468.0 | 882.1 | 269.0 | (711.0;269.0) | 1.030 | True |
| 21 | 100/100 | 200 | 462.8 | 871.0 | 281.4 | (715.1;281.4) | 1.000 | True |
| 22 | 98.5/99.55 | 200 | 463.2 | 869.5 | 286.9 | (713.7;286.9) | 0.985 | True |
| 23 | 93.7/98.11 | 200 | 457.6 | 856.5 | 300.5 | (722.5;300.5) | 0.956 | True |
| 24 | 86/95.8 | 200 | 459.7 | 849.3 | 329.1 | (715.2;329.1) | 0.877 | True |
| 25 | 74/92.2 | 205 | 473.9 | 853.9 | 377.5 | (684.7;377.5) | 0.733 | True |
| 26 | 58.5/87.55 | 245 | 478.1 | 837.9 | 433.6 | (671.2;433.6) | 0.579 | True |
| 27 | 37/81.1 | 365 | 479.8 | 808.9 | 511.4 | (658.3;511.4) | 0.370 | True |
| 28 | 0 | - | - | - | - | - | 0 | not rendered |
- f12 central tip (732.52; 223.80) vs target (732; 224): glow top 199.8 (spec: >= 200 -> 0.2 px, fine). Worst right: f20 maxX 882.1 (+24 = 906.1 < 913.7).

## Caveats / notes for the composition
- Rendered tip angles change with the non-uniform frame scales (measured, central tongue: f9 43 deg, f10 17 deg (smear), f12 22 deg, f14-21 27 deg, f27 55 deg under the lid): this is the spec squash/stretch, pose geometry itself is 26-30 deg.
- The open lid hides most of OL/FL at f9-f27 (expected: flame licks the lid's free edge); the visible read is C right half + FR + OR.
- glitter-rgb.png is white outside its mask: sample the texture inside the mask (preview uses the largest in-mask rectangle tile, x1.8).
- No text anywhere in outputs; guides only in previews.
