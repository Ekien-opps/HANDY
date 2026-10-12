# Frame packet: 02-doute

## Project inputs

- Project: /home/user/HANDY/videos/marinor-ivoire-pub-30s
- Design truth: /home/user/HANDY/videos/marinor-ivoire-pub-30s/frame.md
- RULES_DIR: /home/user/HANDY/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

## Frame 2 — Le doute (4,0–8,0 s, ~4,0 s)

- scene: Contenants industriels anonymes « Additifs », « Exhausteurs artificiels », « Conservateurs », rayés par le trait d'or et réduits en poussière dorée
- duration: 4s
- poster: 2.6s
- transition_in: cut (raccord A)
- status: outline
- src: compositions/02-doute.html
- voiceover: "Sans additifs ni substances douteuses pour votre santé ?"
- vo_cues_local: voix 0,35–3,38 · « Sans additifs » 0,35–1,14 · « substances douteuses » 1,27–2,40 · « votre santé » 2,60–3,26
- blueprint: compose
- rules: spring-pop-entrance, css-marker-patterns, particle-burst
- focal: le trio de contenants (centre-bas) ; secondaire : la question (haut)
- audio_cue: battement grave à 0,4 s ; pulsation d'alerte ; « swish » à 2,55 s ; effritement à 2,75 s

**Monde.** Un doute qui s'installe, nuit d'inquiétude — sans tomber dans la peur. Fond radial Bordeaux #7B1421 (centre) → #2a070d (bords), vignette, halo rouge #A40C21 qui pulse lentement derrière les contenants.

**Séquence (temps locaux) :**
- Scene 1 — entrée raccord A (0,00–0,35 s) : ÉTAT D'ENTRÉE plein cadre #2a070d (overlay opacity 1) qui s'efface (opacity 1→0, power1.out).
- Scene 2 (0,30–1,20 s) : trois contenants génériques SANS marque (un cube de bouillon emballé façon papier aluminium, un flacon en plastique, un pot à couvercle) **tombent** en rang au centre-bas (y −700→0, rebond back.out, stagger 0,12 s), chacun avec une étiquette blanche Montserrat 700 bordeaux : « Additifs », « Exhausteurs artificiels », « Conservateurs ». Taille contenants ≈ 260–320 px de haut, espacés de 420 px.
- Scene 3 (0,35–3,30 s) : texte en haut (y ≈ 200), Montserrat 700 blanc 64 px sur 2 lignes : « Sans additifs ni substances douteuses » / « pour votre santé ? » — révélé par groupes de mots sur la voix (« Sans additifs » 0,35 ; « ni substances douteuses » 1,27 ; « pour votre santé ? » 2,60), « votre santé » en Jaune Soleil #FBD021. Le halo d'alerte pulse 2× (0,9 s et 1,9 s).
- Scene 4 (2,50–2,95 s) : le **trait d'or** (pinceau doré épais 18 px, dégradé or) **raye d'un seul geste vers la gauche** les trois étiquettes (css-marker strike, power3.inOut 0,40 s).
- Scene 5 (2,75–3,45 s) : les contenants **s'effritent** en poussière (particle-burst déterministe, 40–60 particules par contenant, couleurs bordeaux/brun qui virent à l'or en retombant), les contenants scale→0 + opacity.
- Scene 6 — raccord B (3,45–4,00 s) : le trait d'or s'**épaissit** en bande diagonale (≈115°) qui balaie vers la gauche et **couvre tout le cadre à 3,95 s**, fond `linear-gradient(115deg,#F9A825,#FBD021)`. ÉTAT DE SORTIE : plein cadre or.

**Contrainte.** Aucune marque concurrente, pas de tête de mort. **Pourquoi.** Le problème santé ; prépare « 100 % naturel ».

## Selected motion rule: spring-pop-entrance

---
name: spring-pop-entrance
description: The canonical entrance pop — an element (or staggered group) arrives by scaling 0 → 1 on a smooth long-tail settle (power3 default); bouncy overshoot is a rare, explicitly-playful exception. fromTo so it's correct at t=0 under seek.
metadata:
  tags: spring, entrance, pop, scale, power3, settle, stagger, reveal, arrival
---

# Spring-Pop Entrance

> **Smooth beats bouncy.** This entrance defaults to a smooth long-tail settle — `power3.out` (or `expo.out` for a faster front) — that decelerates cleanly into the resting size with **no overshoot**. Bouncy `back.out` is the **#1 instant turn-off** in agent-made videos and is almost never executed well; it is a rare, explicitly-playful exception (consumer / fun brand), never the default. When unsure, settle smoothly.

THE entrance primitive: an element (or staggered group) arrives by springing from nothing — `scale: 0 → 1`, optional small `y` rise — and settles without bouncing. This is **arrival**, not reaction: distinct from [press-release-spring.md](press-release-spring.md) (a click/press → release feedback chain on an element that already rests on screen). Many blueprints used to borrow that rule to fake an entrance; reach for this instead.

## How It Works

One `fromTo` carries the whole arrival: from `{ scale: 0, opacity: 0 }` (explicit, so t=0 is correct under seek) to `{ scale: 1, opacity: 1, ease: "power3.out" }`. For a **group**, the same `fromTo` runs per element at `i * STAGGER`, capped so the group reads as one arriving beat. The `scale` grow is load-bearing; the `y` rise is garnish — drop everything else and it must still read as a clean entrance. Let the ease produce the settle: never hand-key a `scale: 1.1` mid-state (it double-bounces against the curve).

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="pop-hero" id="hero">{heroLabel}</div>

<div class="pop-grid">
  <div class="pop-item">{itemA}</div>
  <div class="pop-item">{itemB}</div>
  <div class="pop-item">{itemC}</div>
</div>
```

```css
.pop-hero,
.pop-item {
  transform-origin: 50% 50%; /* in-place pop; move to the source point for the anchored variation */
  will-change: transform;
}
.pop-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: GRID_GAP;
  place-items: center;
}
```

```js
// Single hero pop — smooth long-tail settle, no overshoot.
tl.fromTo(
  "#hero",
  { scale: 0, opacity: 0 },
  { scale: 1, opacity: 1, duration: POP_DUR, ease: "power3.out" },
  ENTRY_AT,
);

// Staggered group pop — one arriving beat.
gsap.utils.toArray(".pop-item").forEach((el, i) => {
  tl.fromTo(
    el,
    { scale: 0, opacity: 0, y: Y_RISE },
    { scale: 1, opacity: 1, y: 0, duration: POP_DUR, ease: "power3.out" },
    GROUP_ENTRY_AT + i * STAGGER,
  );
});
```

## Variations

- **Calm settle** (premium / enterprise): `power3.out`, no rotation, `Y_RISE` 0–12px — a weighted, confident landing for a hero wordmark or product shot.
- **Firm settle** (everyday default): `power3.out` or `expo.out` for a punchier front, `Y_RISE` ~24px — cards, icons, callouts.
- **Exact-physics settle**: when the settle IS the shot, swap the ease for `springEase({ response: 0.4 })` (critically damped) from `../adapters/gsap-easing-and-stagger.md` → Spring Eases; take `duration` from the helper.
- **Origin-anchored pop**: a callout growing out of a specific point (marker, pointer tip) sets `transform-origin` to that point (e.g. `0% 100%`) so `scale: 0 → 1` reads as "emerging from the source", not "inflating in place".
- **Pop into a held slot**: land the pop and hold still — no idle loop baked into the entrance. If the held frame genuinely needs life, hand off to [sine-wave-loop.md](sine-wave-loop.md) for subtle jitter on a separate later tween; prefer revealing the next element on its VO cue.
- **Bouncy pop (RARE — explicitly-playful only)**: swap the ease for `back.out(OVERSHOOT)` and optionally settle a small `rotation: ROT_FROM → 0` so elements look hand-placed. Only for a deliberately playful register — never product / enterprise / serious tone:

```js
tl.fromTo(
  el,
  { scale: 0, opacity: 0, rotation: ROT_FROM },
  { scale: 1, opacity: 1, rotation: 0, duration: POP_DUR, ease: `back.out(${OVERSHOOT})` },
  GROUP_ENTRY_AT + i * STAGGER,
);
```

Even here keep `OVERSHOOT ≤ ~2` — past that it reads as cartoon wobble. Better still: the baked spring at `dampingFraction: 0.6–0.7` (same adapters doc) gives ~5–10% overshoot that reads physical where `back.out` reads cartoon.

## Values

| token      | range                                     | notes                                                            |
| ---------- | ----------------------------------------- | ---------------------------------------------------------------- |
| EASE       | `power3.out` default; `expo.out` punchier | `back.out(OVERSHOOT)` only in the playful variant                |
| POP_DUR    | 0.4–0.7s                                  | shorter = tight snap; hero must be visible by **t ≤ 0.5s**       |
| STAGGER    | 0.04–0.08s                                | `min(0.06, 0.5 / ITEM_COUNT)` — self-caps the window             |
| ITEM_COUNT | 3–9                                       | >9 makes the stagger vanish — switch to a wipe/sweep reveal      |
| Y_RISE     | 0–32px                                    | small; never large enough to read as a slide-up                  |
| ROT_FROM   | −10°–+10°                                 | playful variant only; alternate sign by index (`i % 2 ? 6 : -6`) |
| ENTRY_AT   | 0–0.4s                                    | a beat of quiet, but keep the subject landing by t ≤ 0.5s        |

## Critical Constraints

- Default ease `power3.out` (no overshoot); `back.out` only in the explicitly-playful variant, and there `OVERSHOOT ≤ ~2`.
- `ITEM_COUNT × STAGGER ≤ ~0.5s` — the group must land inside one beat.
- Entrances state the collapsed from-state in `fromTo` — never rely on a CSS-hidden start (it renders visible before the tween claims it under seek).
- `transform-origin: 50% 50%` for an in-place pop; the source point only for the anchored variation.
- This is a finite arrival — idle motion on a held element is a separate, later `sine-wave-loop` tween.

## See also

`center-outward-expansion` (pop while radiating to slots) · `press-release-spring` (the click-feedback counterpart) · `sine-wave-loop` (post-arrival jitter, sparingly).

## Selected motion rule: css-marker-patterns

# CSS Patterns for Marker Highlighting

Pure CSS + GSAP implementations of all five MarkerHighlight.js drawing modes — no external library dependency, full timeline control. Snippets show mechanism DOM only, inside a standard scene clip (hyperframes-core); assume `tl` exists.

Shared scaffold for every mode: the wrap is `position: relative; display: inline`; the text copy is `position: relative` and z-indexed **above** the accent (below it for sketchout, where the lines cross the text).

## 1. Highlight Mode

Yellow marker sweep behind text — the most common mode.

```html
<span class="mh-highlight-wrap">
  <span class="mh-highlight-bar" id="hl-1"></span>
  <span class="mh-highlight-text">highlighted text</span>
</span>
```

```css
.mh-highlight-bar {
  position: absolute;
  inset: 0 -6px; /* bleed past the text edges */
  background: #fdd835;
  opacity: 0.35;
  transform: scaleX(0);
  transform-origin: left center;
  border-radius: 3px;
  z-index: 0;
}
```

```js
tl.to("#hl-1", { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.6);
// Optional hand-drawn skew: gsap.set("#hl-1", { skewX: -2 });
// Multi-line: tl.to(".mh-highlight-bar", { scaleX: 1, ..., stagger: 0.3 }, 0.6);
```

## 2. Circle Mode

Hand-drawn ellipse around text — `border-radius: 50%` plus a slight rotation for organic feel.

```html
<span class="mh-circle-wrap">
  <span class="mh-circle-text">IMPORTANT</span>
  <span class="mh-circle-ring" id="circle-1"></span>
</span>
```

```css
.mh-circle-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 130%; /* tight (short words): 150%; rounded-rect: 120% + border-radius: 30% */
  height: 160%;
  transform: translate(-50%, -50%) rotate(-3deg) scale(0);
  border: 3px solid #e53935;
  border-radius: 50%;
  z-index: 0;
}
```

```js
tl.to("#circle-1", { scale: 1, rotation: -3, duration: 0.6, ease: "back.out(1.7)" }, 0.7);
```

## 3. Burst Mode

Radiating lines from text center — each line a positioned span rotated to its angle. Use ~12 lines at 30° steps and **vary `--len` (40–80px)**; equal lengths look mechanical.

```html
<span class="mh-burst-wrap">
  <span class="mh-burst-text">WOW</span>
  <span class="mh-burst-container" id="burst-1">
    <span class="mh-burst-line" style="--angle: 0deg; --len: 70px;"></span>
    <span class="mh-burst-line" style="--angle: 30deg; --len: 55px;"></span>
    <!-- …one line per 30° step through 330deg, --len varied 40-80px -->
  </span>
</span>
```

```css
.mh-burst-container {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  z-index: 1; /* text copy at z-index: 2 */
}
.mh-burst-line {
  position: absolute;
  display: block;
  width: 3px;
  height: var(--len);
  background: #1e88e5;
  left: -1.5px;
  top: calc(-1 * var(--len));
  transform: rotate(var(--angle));
  transform-origin: bottom center;
  opacity: 0;
}
```

```js
tl.fromTo(
  "#burst-1 .mh-burst-line",
  { scaleY: 0, opacity: 0 },
  { scaleY: 1, opacity: 1, duration: 0.4, ease: "power2.out", stagger: 0.03 },
  0.7,
);
```

## 4. Scribble Mode

Wavy SVG underline that draws itself via `stroke-dashoffset`.

```html
<span class="mh-scribble-wrap">
  <span class="mh-scribble-text">underlined text</span>
  <svg class="mh-scribble-svg" viewBox="0 0 500 24" preserveAspectRatio="none">
    <path
      id="scribble-1"
      d="M0,12 Q31,0 62,12 Q93,24 125,12 Q156,0 187,12 Q218,24 250,12 Q281,0 312,12 Q343,24 375,12 Q406,0 437,12 Q468,24 500,12"
      fill="none"
      stroke="#FDD835"
      stroke-width="3"
      stroke-linecap="round"
    />
  </svg>
</span>
```

```css
.mh-scribble-svg {
  position: absolute;
  left: 0;
  bottom: -6px; /* strikethrough variant: top: 50%; transform: translateY(-50%) */
  width: 100%;
  height: 24px;
  z-index: 0;
}
```

```js
const path = document.querySelector("#scribble-1");
const len = path.getTotalLength();
gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
tl.to("#scribble-1", { strokeDashoffset: 0, duration: 0.8, ease: "power1.inOut" }, 0.7);
```

Path tuning: the `Q` control points alternate y between 0 and 24 for a natural wobble. Tighter waves = smaller x-increments (~25px per half-wave); looser = ~50px; subtler amplitude = y range 0–16.

## 5. Sketchout Mode

Cross-hatch over de-emphasized text — two angled lines create a "crossed out" effect.

```html
<span class="mh-sketchout-wrap">
  <span class="mh-sketchout-text">old price</span>
  <span class="mh-sketchout-lines" id="sketchout-1">
    <span class="mh-sketchout-line mh-sketchout-fwd"></span>
    <span class="mh-sketchout-line mh-sketchout-bwd"></span>
  </span>
</span>
```

```css
.mh-sketchout-lines {
  position: absolute;
  inset: 0 -4px;
  overflow: hidden;
  z-index: 1; /* text at z-index: 0 — the lines cross OVER it */
}
.mh-sketchout-line {
  position: absolute;
  display: block;
  top: 50%;
  left: 0;
  width: 100%;
  height: 2px;
  background: #e53935;
  transform-origin: left center;
}
.mh-sketchout-fwd {
  transform: scaleX(0) rotate(-12deg);
}
.mh-sketchout-bwd {
  transform: scaleX(0) rotate(12deg);
}
```

```js
// Forward slash first, backward follows
tl.to("#sketchout-1 .mh-sketchout-fwd", { scaleX: 1, duration: 0.3, ease: "power2.out" }, 1.0);
tl.to("#sketchout-1 .mh-sketchout-bwd", { scaleX: 1, duration: 0.3, ease: "power2.out" }, 1.15);
```

## Combining Modes in Captions

Cycle modes across caption groups for visual variety — every 2-3 groups for high energy, 3-4 for medium, 4-5 for low:

```js
const MODES = ["highlight", "circle", "burst", "scribble"];
GROUPS.forEach((group, gi) => {
  const mode = MODES[gi % MODES.length];
  group.emphasisWords.forEach((word) => applyMode(word.el, mode, tl, word.start));
});
```

## Selected motion rule: particle-burst

---
name: particle-burst
description: Deterministic particle / confetti events — a confetti pop that bursts up and drifts down (optionally instant-shrinking away), a dot burst from behind text, or a glyph dissolving to particles. Every particle's state is a pure ballistic function of timeline time from index-seeded values, so a scrub to any t shows the correct mid-flight frame.
metadata:
  tags: particles, confetti, burst, dissolve, celebration, ballistic, deterministic, punctuation
---

# Particle Burst

Discrete flying particles as a one-shot event: a **confetti pop** that erupts upward and drifts back down on gravity, a **dot burst** radiating from behind a landing word, or a **glyph dissolve** where text breaks into particles that scatter and die. Particles are ephemeral garnish — born from a beat, fly, gone; they never become layout.

Boundaries: [css-marker-patterns.md](css-marker-patterns.md)'s burst mode is radiating **drawn lines** — a static accent, no flight. [press-release-spring.md](press-release-spring.md)'s release burst is **one blurred radial layer** faking an explosion — enough when a single glow pop will do. [center-outward-expansion.md](center-outward-expansion.md) moves **real layout elements** to final resting slots; particles have no destination, only physics and a death.

## How It Works

The whole event is **one driver tween and one formula**:

1. **Seeded setup** — a fixed pool of `PARTICLE_COUNT` small divs is created once at composition setup (a deterministic loop — setup-time generation is fine; per-frame DOM creation is not). Each particle `i` derives everything from a pure hash:

   ```js
   // angle, speed, size, spin, color (palette[i % palette.length]) — all from prand(i * k)
   const prand = (n) => {
     const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
     return x - Math.floor(x); // 0..1, pure function of n
   };
   ```

2. **Ballistic formula** — a proxy tween advances `T: 0 → 1` over `FLIGHT_DUR` with `ease: "none"`; `onUpdate` positions every particle as a **pure function of T**:

   ```
   x(T) = vx · T·FLIGHT_DUR
   y(T) = vy · T·FLIGHT_DUR + ½ · G · (T·FLIGHT_DUR)²
   rot(T) = spin · T·FLIGHT_DUR
   ```

   Gravity `G` supplies the rise-decelerate-fall arc for free. Because position is computed from `T` (never accumulated per frame), a seek to any moment renders the exact mid-flight state — this is what makes DOM particles seek-safe. The driver's `ease: "none"` is load-bearing: the physics lives in the formula; an eased driver warps gravity and the arc stops reading as thrown objects.

3. **Death** — an opacity tail inside the same formula (fade over the last `FADE_FRAC` of flight), or the confetti signature: a separate **instant-shrink** tween scaling the pool to 0 in a blink at flight end. Either way the particles end invisible and stay invisible.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="burst-stage">
  <div class="particle-field" id="particle-field"></div>
  <div class="burst-hero" id="burst-hero">{heroWord}</div>
</div>
```

```css
/* .burst-stage: position: relative; display: grid; place-items: center.
   .burst-hero: z-index: 2 — particles fly BEHIND the word. */
.particle-field {
  position: absolute;
  z-index: 1;
  left: 50%;
  top: 50%; /* the launch origin — offset to taste (e.g. the word's baseline) */
  width: 0;
  height: 0;
}
.particle {
  position: absolute;
  left: 0;
  top: 0;
  border-radius: 2px; /* confetti chip; 50% for dots */
  opacity: 0; /* invisible until the event fires */
  will-change: transform, opacity;
}
```

```js
// Setup: deterministic pool, generated ONCE.
const field = document.getElementById("particle-field");
const palette = ["{accentA}", "{accentB}", "{accentC}"]; // 3-5 brand tokens
const parts = [];
for (let i = 0; i < PARTICLE_COUNT; i++) {
  const el = document.createElement("div");
  el.className = "particle";
  const size = SIZE_MIN + prand(i * 3 + 1) * (SIZE_MAX - SIZE_MIN);
  el.style.width = `${size}px`;
  el.style.height = `${size * 0.7}px`; // slightly oblong = confetti chip
  el.style.background = palette[i % palette.length];
  field.appendChild(el);
  // Index-seeded launch parameters — the particle's whole life, fixed here.
  const angle = -Math.PI / 2 + (prand(i * 5 + 2) * 2 - 1) * CONE; // upward cone
  const speed = SPEED_MIN + prand(i * 7 + 3) * (SPEED_MAX - SPEED_MIN);
  parts.push({
    el,
    vx: Math.cos(angle) * speed,
    vy: Math.sin(angle) * speed, // negative = up
    spin: (prand(i * 11 + 4) * 2 - 1) * SPIN_MAX,
  });
}

// Confetti pop — one driver, pure ballistic formula.
const drive = { T: 0 };
tl.fromTo(
  drive,
  { T: 0 },
  {
    T: 1,
    duration: FLIGHT_DUR,
    ease: "none", // physics lives in the formula, not the ease
    onUpdate: () => {
      const t = drive.T * FLIGHT_DUR; // seconds of flight — pure function of T
      const fade = Math.min(1, (1 - drive.T) / FADE_FRAC); // opacity tail
      parts.forEach((p) => {
        const x = p.vx * t;
        const y = p.vy * t + 0.5 * G * t * t; // rise, stall, drift down
        p.el.style.transform = `translate(${x}px, ${y}px) rotate(${p.spin * t}deg)`;
        p.el.style.opacity = String(drive.T === 0 ? 0 : fade); // T===0 guard covers seeks before the event
      });
    },
  },
  BURST_AT,
);
```

## Variations

- **Confetti pop, then instant-shrink** — the playful signature: full burst, gravity drift, then every chip scales to 0 in a blink: `FADE_FRAC` near 0, plus `tl.to(".particle", { scale: 0, duration: SHRINK_DUR, ease: "power2.in" }, BURST_AT + FLIGHT_DUR - SHRINK_DUR)` with `SHRINK_DUR` 0.15–0.25s. Keep the whole event tiny relative to the subject — a garnish measured in a few dozen pixels, not a screen-filling cannon.
- **Dot burst behind a landing word** — radial instead of a cone: `angle = prand(i) * Math.PI * 2`, `G` near 0, short flight (0.4–0.7s), round dots (`border-radius: 50%`), pool z-indexed behind the word. Fire at the word's settle frame.
- **Glyph dissolve** — seed each particle's **origin** across the glyph block's box (`ox = (prand(i*13) - 0.5) * BLOCK_W`, same for `oy`, added inside the transform), gentle outward drift with low `G`; text fades out over the first ~30% of flight while particles fade in from its silhouette. Color every particle `{textColor}` so the swarm reads as the text's own material. (True per-pixel dissolves are Canvas-2D territory — `techniques.md`; this DOM version sells it up to ~40 particles.)
- **Two-stage burst (pop + stragglers)** — split the pool: 70% on the main driver, 30% on a second driver ~0.12s later with lower speeds; the split is index-derived (`i % 10 < 3`). Same formula, two windows.

## Values

| token                 | range                                        | notes                                                                           |
| --------------------- | -------------------------------------------- | ------------------------------------------------------------------------------- | --- | ----------------------- |
| PARTICLE_COUNT        | 10–18 pop/dots; 24–40 dissolve               | **cap ~40** — per-frame style writes; past that, seek perf and register degrade |
| G                     | 900–1600 px/s² confetti; 0–200 dots/dissolve | natural fall vs drift                                                           |
| SPEED_MIN / SPEED_MAX | 250–700 px/s                                 | per-particle via `prand`, never uniform                                         |
| CONE                  | 0.35–0.8 rad (~20–45°)                       | wider = splash, narrower = fountain                                             |
| FLIGHT_DUR            | 0.7–1.4s                                     | arc should peak ~35–45% of flight: check `                                      | vy  | / G ≈ 0.4 × FLIGHT_DUR` |
| SIZE_MIN / SIZE_MAX   | 5–14px chips; 4–8px dots                     | on a 1080p frame                                                                |
| SPIN_MAX              | 180–720 deg/s confetti; 0 dots               | tumble                                                                          |
| FADE_FRAC             | 0.2–0.35                                     | near 0 when using instant-shrink                                                |
| BURST_AT              | on a cause                                   | the word's settle, a click, a lockup completing — an uncaused burst is noise    |

## Critical Constraints

- **Position is a pure function of time, driver ease `"none"`** — `x(T)`, `y(T)`, `rot(T)` computed from the driver value every frame, never accumulated (`+=`) per tick (accumulation breaks the moment the renderer seeks); gravity is the ease — an eased driver bends the parabola.
- **Fixed pool, no per-frame DOM** — all particles exist after setup with `opacity: 0`; the event only writes `transform` / `opacity`. **`PARTICLE_COUNT ≤ ~40`** — per-frame style writes scale linearly; keep the event cheap.
- **Particles start AND end at `opacity: 0`** — the `drive.T === 0` guard covers seeks to before the event; the tail/shrink covers after. A chip frozen mid-air at driver end is a bug every subsequent frame.
- **Particles are punctuation** — one event per beat, fired on a cause, small relative to the subject, dead before the next beat; z-ordered behind or around the word it celebrates, never over it. A persistent particle system is a background, and that's not this rule.

## See also

`spring-pop-entrance` (confetti fires on the hero's settle frame) · `kinetic-beat-slam` (one beat earns the confetti payoff) · `press-release-spring` (single-layer glow alternative, or compose both) · `css-marker-patterns` (drawn-line burst when the accent should feel hand-annotated) · `scale-swap-transition` (glyph dissolve covers the exit).
