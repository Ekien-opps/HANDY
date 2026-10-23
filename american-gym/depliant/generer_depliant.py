"""Dépliant 3 volets American's Gym (A4 à l'italienne, pli roulé).

Produit, pour l'extérieur et l'intérieur :
  - un SVG vectoriel pour Illustrator (textes modifiables, formes vectorielles,
    images incorporées, un groupe nommé par volet / élément) ;
  - une variante « impression » (fond perdu 3 mm, sans repères de pliage) qui
    sert à générer le PDF.

Volets (pli roulé : le volet replié vers l'intérieur fait 97 mm) :
  extérieur : [rabat 97 mm | dos 100 mm | couverture 100 mm]
  intérieur : [100 mm      | 100 mm     | volet replié 97 mm]

Usage : python3 generer_depliant.py   (depuis le dossier depliant/)
"""
import base64
import io
from pathlib import Path

from PIL import Image, ImageFont

HERE = Path(__file__).parent
FONTS = HERE.parent / "fonts"
IMAGES = HERE / "images"


def mm(v):
    return v * 72 / 25.4


W, H = mm(297), mm(210)
BLEED = mm(3)
M = mm(8)                       # marge de sécurité dans chaque volet

RED = "#EC1827"
RED_DARK = "#B5101E"
DARK = "#121519"
DARK2 = "#1A1E24"
WHITE = "#FFFFFF"
LIGHT = "#F3F4F6"
INK = "#1E2329"
GREY = "#5A616B"
GREY_ON_DARK = "#B9BEC6"

WEIGHTS = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
_font_cache = {}


def pil_font(weight, size):
    key = (weight, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONTS / f"Montserrat-{WEIGHTS[weight]}.ttf"), int(size * 20))
    return _font_cache[key]


def text_width(s, weight, size):
    return pil_font(weight, size).getlength(s) / 20


def wrap(s, weight, size, width):
    lines, cur = [], ""
    for word in s.split():
        test = f"{cur} {word}".strip()
        if text_width(test, weight, size) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Svg:
    def __init__(self, print_version):
        self.print_version = print_version
        self.defs = []
        self.body = []
        self.n = 0

    def uid(self, prefix):
        self.n += 1
        return f"{prefix}{self.n}"

    # --- primitives -------------------------------------------------------
    def rect(self, x, y, w, h, fill, rx=0, extra=""):
        r = f' rx="{f(rx)}"' if rx else ""
        return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r} fill="{fill}"{extra}/>'

    def poly(self, pts, fill, extra=""):
        p = " ".join(f"{f(x)},{f(y)}" for x, y in pts)
        return f'<polygon points="{p}" fill="{fill}"{extra}/>'

    def text(self, lines, x, y, size, weight, fill, leading=None, spacing=0, anchor="start"):
        """Texte (une ou plusieurs lignes). x, y : ligne de base de la 1re ligne."""
        if isinstance(lines, str):
            lines = [lines]
        leading = leading or size * 1.25
        ls = f' letter-spacing="{f(spacing)}"' if spacing else ""
        fam = f"Montserrat-{WEIGHTS[weight]}, Montserrat"
        out = [f'<text font-family="{fam}" font-weight="{weight}" font-size="{f(size)}" fill="{fill}"{ls}>']
        for i, line in enumerate(lines):
            lx = x
            if anchor == "end":
                lx = x - text_width(line, weight, size) - spacing * len(line)
            elif anchor == "middle":
                lx = x - (text_width(line, weight, size) + spacing * len(line)) / 2
            out.append(f'<tspan x="{f(lx)}" y="{f(y + i * leading)}">{esc(line)}</tspan>')
        out.append("</text>")
        return "".join(out)

    def para(self, s, x, y, width, size=8.2, weight=400, fill=INK, leading=None):
        leading = leading or size * 1.55
        lines = wrap(s, weight, size, width)
        return self.text(lines, x, y, size, weight, fill, leading), y + leading * len(lines)

    def image(self, name, x, y, w, h, clip_pts=None, focus=(0.5, 0.5)):
        """Image incorporée, recadrée au format exact du cadre (pas de déformation)."""
        im = Image.open(IMAGES / name).convert("RGB")
        target = w / h
        iw, ih = im.size
        if iw / ih > target:
            cw = round(ih * target)
            x0 = round((iw - cw) * focus[0])
            im = im.crop((x0, 0, x0 + cw, ih))
        else:
            ch = round(iw / target)
            y0 = round((ih - ch) * focus[1])
            im = im.crop((0, y0, iw, y0 + ch))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=92)
        data = base64.b64encode(buf.getvalue()).decode()
        img = (f'<image x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" '
               f'xlink:href="data:image/jpeg;base64,{data}"/>')
        if clip_pts:
            cid = self.uid("clip")
            p = " ".join(f"{f(a)},{f(b)}" for a, b in clip_pts)
            self.defs.append(f'<clipPath id="{cid}"><polygon points="{p}"/></clipPath>')
            return f'<g clip-path="url(#{cid})">{img}</g>'
        return img

    def logo(self, x, y, w):
        im = Image.open(IMAGES / "logo_american_gym.png")
        h = w * im.height / im.width
        buf = io.BytesIO()
        im.save(buf, "PNG")
        data = base64.b64encode(buf.getvalue()).decode()
        return (f'<image x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" '
                f'xlink:href="data:image/png;base64,{data}"/>'), h

    def vgrad(self, stops):
        gid = self.uid("grad")
        st = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
        self.defs.append(f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">{st}</linearGradient>')
        return f"url(#{gid})"

    def group(self, gid, *items):
        return f'<g id="{gid}">' + "".join(items) + "</g>"

    def render(self, title):
        if self.print_version:
            vb = f"{f(-BLEED)} {f(-BLEED)} {f(W + 2 * BLEED)} {f(H + 2 * BLEED)}"
            size = f'width="{f(297 + 6)}mm" height="{f(210 + 6)}mm"'
        else:
            vb = f"0 0 {f(W)} {f(H)}"
            size = 'width="297mm" height="210mm"'
        return ('<?xml version="1.0" encoding="UTF-8"?>\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'version="1.1" {size} viewBox="{vb}">\n<title>{esc(title)}</title>\n'
                "<defs>" + "".join(self.defs) + "</defs>\n" + "\n".join(self.body) + "\n</svg>\n")


# --- pictogrammes vectoriels (dessinés sur une grille de 24) ---------------------
ICONS = {
    "phone": '<path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z" fill="{c}"/>',
    "pin": '<path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z" fill="{c}"/>',
    "facebook": '<path d="M13.4 21v-7.6h2.6l.4-3h-3V8.5c0-.86.25-1.45 1.49-1.45h1.6V4.4c-.28-.04-1.22-.12-2.32-.12-2.3 0-3.87 1.4-3.87 3.97v2.15H7.7v3h2.6V21z" fill="{c}"/>',
    "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5" fill="none" stroke="{c}" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="{c}" stroke-width="2"/><circle cx="17.2" cy="6.8" r="1.2" fill="{c}"/>',
    "tiktok": '<path d="M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 0 1-2.59 2.5c-1.42 0-2.6-1.16-2.6-2.6 0-1.72 1.66-3.01 3.37-2.48V9.66c-3.45-.46-6.47 2.22-6.47 5.64 0 3.33 2.76 5.7 5.69 5.7 3.14 0 5.69-2.55 5.69-5.7V9.01a7.35 7.35 0 0 0 4.3 1.38V7.3s-1.88.09-3.24-1.48z" fill="{c}"/>',
    "clock": '<circle cx="12" cy="12" r="8.5" fill="none" stroke="{c}" stroke-width="2"/><path d="M12 7v5.4l3.6 2.2" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>',
    "dumbbell": '<rect x="1.5" y="9" width="2.4" height="6" rx=".8" fill="{c}"/><rect x="4.4" y="6.5" width="3.2" height="11" rx="1" fill="{c}"/><rect x="7.6" y="10.8" width="8.8" height="2.4" fill="{c}"/><rect x="16.4" y="6.5" width="3.2" height="11" rx="1" fill="{c}"/><rect x="20.1" y="9" width="2.4" height="6" rx=".8" fill="{c}"/>',
    "heart": '<path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" fill="{c}"/><path d="M4 11h4.2l1.5-3 2.4 6.2 1.8-3.2H20" fill="none" stroke="{bg}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>',
    "lotus": '<path d="M1.5 8.5C5.5 8.7 9 11 10.4 15c.6 1.8.8 3.7.6 5.5C5.6 20 1.8 15.5 1.5 8.5z" fill="{c}"/><path d="M22.5 8.5C18.5 8.7 15 11 13.6 15c-.6 1.8-.8 3.7-.6 5.5 5.4-.5 9.2-5 9.5-12z" fill="{c}"/><path d="M12 2.5c3 3 3.8 6.5 3.8 9.5 0 3.6-1.8 6.4-3.8 8.5-2-2.1-3.8-4.9-3.8-8.5 0-3 .8-6.5 3.8-9.5z" fill="{c}" stroke="{bg}" stroke-width="1.3"/>',
    "stopwatch": '<circle cx="12" cy="13.5" r="7.5" fill="none" stroke="{c}" stroke-width="2"/><rect x="9.5" y="2.5" width="5" height="2.2" rx=".8" fill="{c}"/><path d="M12 9.5v4.3l2.6 1.6M18.4 6.6l1.4-1.4" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"/>',
    "group": '<circle cx="12" cy="7" r="3.2" fill="{c}"/><path d="M6.2 19c0-3.4 2.6-6 5.8-6s5.8 2.6 5.8 6z" fill="{c}"/><circle cx="4.6" cy="9.4" r="2.3" fill="{c}"/><path d="M.6 18.4c0-2.6 1.8-4.6 4-4.6 1 0 1.9.4 2.6 1-.9 1-1.5 2.3-1.7 3.6z" fill="{c}"/><circle cx="19.4" cy="9.4" r="2.3" fill="{c}"/><path d="M23.4 18.4c0-2.6-1.8-4.6-4-4.6-1 0-1.9.4-2.6 1 .9 1 1.5 2.3 1.7 3.6z" fill="{c}"/>',
    "flame": '<path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67zM11.71 19c-1.78 0-3.22-1.4-3.22-3.14 0-1.62 1.05-2.76 2.81-3.12 1.77-.36 3.6-1.21 4.62-2.58.39 1.29.59 2.65.59 4.04 0 2.65-2.15 4.8-4.8 4.8z" fill="{c}"/>',
    "check": '<path d="M5 12.5l4.2 4.2L19 7" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>',
}


def icon(name, cx, cy, size, color=WHITE, bg=RED, circle=None, ring=False):
    """Pictogramme centré en (cx, cy). circle : rayon du disque de fond (ou None)."""
    s = size / 24
    out = []
    if circle:
        if ring:
            out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(circle)}" fill="none" stroke="{color}" stroke-width="1.4"/>')
        else:
            out.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(circle)}" fill="{bg}"/>')
    out.append(f'<g transform="translate({f(cx - size / 2)} {f(cy - size / 2)}) scale({f(s)})">'
               + ICONS[name].replace("{c}", color).replace("{bg}", bg) + "</g>")
    return "".join(out)


def band_along(svg, x0, x1, p, q, offset, thick, fill):
    """Bande parallèle au bord en biais passant par p et q, décalée de offset (vers le haut si < 0)."""
    def y(x):
        return p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0]) + offset
    return svg.poly([(x0, y(x0)), (x1, y(x1)), (x1, y(x1) + thick), (x0, y(x0) + thick)], fill)


# --- contenus ------------------------------------------------------------------
PHONE = "+225 07 88 48 18 72"
ADDRESS = ("Abobo, Abidjan", "Côte d’Ivoire")


def exterieur(print_version=False):
    s = Svg(print_version)
    b = BLEED
    xa, wa = 0, mm(97)                 # rabat
    xb, wb = mm(97), mm(100)           # dos
    xc, wc = mm(197), mm(100)          # couverture

    s.body.append(s.group("Fond", s.rect(-b, -b, W + 2 * b, H + 2 * b, DARK),
                          s.rect(xb, -b, wb, H + 2 * b, DARK2)))

    # ---------------- volet A : rabat ----------------
    ya = mm(102)
    photo = s.image("photo_sportive.jpg", -b, -b, wa + b, ya + mm(10) + b,
                    clip_pts=[(-b, -b), (wa, -b), (wa, ya - mm(14)), (-b, ya + mm(6))], focus=(0.5, 0.2))
    fade = s.poly([(-b, ya - mm(30)), (wa, ya - mm(48)), (wa, ya - mm(14)), (-b, ya + mm(6))],
                  s.vgrad([(0, DARK, 0), (1, DARK, 0.85)]))
    stripes = (s.poly([(-b, ya + mm(6)), (wa * 0.62, ya - mm(4.4)), (wa * 0.62, ya - mm(1.2)), (-b, ya + mm(9.2))], RED)
               + s.poly([(wa * 0.66, ya - mm(6.6)), (wa, ya - mm(14)), (wa, ya - mm(10.8)), (wa * 0.66, ya - mm(3.4))], RED))
    q_lines = ["Là où la santé,", "la force et le", "bien-être se", "rencontrent."]
    qy = ya + mm(18)
    quote = (s.text("“", M - 2, qy + 4, 46, 900, RED)
             + s.text(q_lines, M + mm(10), qy, 15, 800, WHITE, leading=18.5)
             + s.text("— American’s Gym", M + mm(10), qy + 18.5 * 4 + 2, 8.5, 600, RED))
    ly = qy + 18.5 * 4 + mm(13)
    reasons = ["Équipements modernes et entretenus", "Coachs à votre écoute",
               "Programmes adaptés à tous les niveaux", "Ambiance conviviale et motivante"]
    lst = [s.text("POURQUOI NOUS CHOISIR ?", M, ly, 9.5, 800, RED, spacing=0.3)]
    for i, r in enumerate(reasons):
        yy = ly + mm(7) + i * mm(6.6)
        lst.append(icon("check", M + 5, yy - 3, 8, WHITE, circle=6))
        lst.append(s.text(r, M + 16, yy, 7.8, 500, WHITE))
    corner = s.poly([(wa * 0.55, H + b), (wa, H - mm(16)), (wa, H + b)], RED)
    s.body.append(s.group("Volet_A_rabat",
                          s.group("A_photo", photo, fade, stripes),
                          s.group("A_citation", quote),
                          s.group("A_pourquoi_nous", *lst),
                          s.group("A_forme_rouge", corner)))

    # ---------------- volet B : dos ----------------
    lw = mm(52)
    logo, lh = s.logo(xb + (wb - lw) / 2 + mm(1), mm(17), lw - mm(2))
    card = s.rect(xb + (wb - lw - mm(12)) / 2, mm(11), lw + mm(12), lh + mm(12), WHITE, rx=mm(4))
    cy0 = mm(17) + lh + mm(20)
    contact = [s.text("CONTACTEZ-NOUS", xb + M, cy0, 14, 800, WHITE),
               s.rect(xb + M, cy0 + 6, mm(12), 2.4, RED)]
    rows = [("phone", "Téléphone / WhatsApp", PHONE), ("facebook", "Facebook", "American’s Gym"),
            ("instagram", "Instagram", "American’s Gym"), ("tiktok", "TikTok", "American’s.Gym.dok"),
            ("pin", "Adresse", f"{ADDRESS[0]} — {ADDRESS[1]}")]
    for i, (ic, label, val) in enumerate(rows):
        ry = cy0 + mm(12) + i * mm(10.5)
        contact.append(icon(ic, xb + M + 9, ry + 1, 10, WHITE, circle=9))
        contact.append(s.text(label, xb + M + 24, ry - 2.5, 6.5, 500, GREY_ON_DARK))
        contact.append(s.text(val, xb + M + 24, ry + 7.5, 8.6, 700, WHITE))
    hy = cy0 + mm(12) + 5 * mm(10.5) + mm(4)
    hours = [icon("clock", xb + M + 7, hy - 4, 13, RED),
             s.text("HORAIRES D’OUVERTURE", xb + M + 18, hy, 9.5, 800, WHITE, spacing=0.3)]
    for i, (d, t) in enumerate([("Lundi – Vendredi", "__h__ – __h__"), ("Samedi", "__h__ – __h__"),
                                ("Dimanche", "__h__ – __h__")]):
        yy = hy + mm(6.5) + i * mm(5)
        hours.append(s.text(d, xb + M + 18, yy, 7.8, 500, GREY_ON_DARK))
        hours.append(s.text(t, xb + wb - M, yy, 7.8, 700, WHITE, anchor="end"))
    band = s.poly([(xb, H - mm(26)), (xb + wb, H - mm(36)), (xb + wb, H + b), (xb, H + b)], RED)
    band2 = s.poly([(xb, H - mm(29)), (xb + wb * 0.45, H - mm(33.5)), (xb + wb * 0.45, H - mm(31.3)), (xb, H - mm(26.8))], WHITE)
    slogan = s.text(["Plus qu’une salle,", "un mode de vie !"], xb + M, H - mm(17), 13, 800, WHITE, leading=16)
    s.body.append(s.group("Volet_B_dos",
                          s.group("B_logo", card, logo),
                          s.group("B_contact", *contact),
                          s.group("B_horaires", *hours),
                          s.group("B_bandeau_slogan", band, band2, slogan)))

    # ---------------- volet C : couverture ----------------
    yc = mm(128)
    photo = s.image("photo_athlete.jpg", xc, -b, wc + b, yc + b,
                    clip_pts=[(xc, -b), (xc + wc + b, -b), (xc + wc + b, yc - mm(22)), (xc, yc)], focus=(0.62, 0.5))
    fade = s.rect(xc, yc - mm(60), wc + b, mm(60), s.vgrad([(0, DARK, 0), (1, DARK, 0.9)]))
    title = s.text("AMERICAN’S GYM", xc + M, yc - mm(27), 22, 800, WHITE)
    red_block = s.poly([(xc, yc - mm(4)), (xc + wc + b, yc - mm(26)), (xc + wc + b, H + b), (xc, H + b)], RED)
    p, q = (xc, yc - mm(4)), (xc + wc + b, yc - mm(26))
    dark_cut = (band_along(s, xc, xc + wc * 0.42, p, q, -mm(4.2), mm(1.6), WHITE)
                + s.poly([(xc + wc * 0.78, H + b), (xc + wc + b, H - mm(20)), (xc + wc + b, H + b)], RED_DARK))
    acc = (s.text(["PLUS FORT", "CHAQUE JOUR,"], xc + M, yc + mm(14), 21, 900, WHITE, leading=24)
           + s.text(["MIEUX DANS", "VOTRE PEAU !"], xc + M, yc + mm(14) + 52, 21, 900, DARK, leading=24))
    pic = []
    py = H - mm(13)
    for i, (ic, lab) in enumerate([("dumbbell", "SPORT"), ("heart", "SANTÉ"), ("lotus", "BIEN-ÊTRE")]):
        px = xc + M + mm(8) + i * mm(24)
        pic.append(icon(ic, px, py - mm(4), 15, WHITE, bg=RED, circle=12, ring=True))
        pic.append(s.text(lab, px, py + mm(5), 6.4, 800, WHITE, anchor="middle", spacing=0.3))
    lcard = s.group("C_cartouche_logo",
                    f'<path d="M{f(xc)} {f(-b)}H{f(xc + mm(48))}V{f(mm(28))}'
                    f'A{f(mm(14))} {f(mm(14))} 0 0 1 {f(xc + mm(34))} {f(mm(42))}H{f(xc)}Z" fill="{WHITE}"/>')
    lg, _ = s.logo(xc + mm(4), mm(4), mm(36))
    s.body.append(s.group("Volet_C_couverture",
                          s.group("C_photo", photo, fade),
                          lcard, s.group("C_logo", lg),
                          s.group("C_titre", title),
                          s.group("C_formes_rouges", red_block, dark_cut),
                          s.group("C_accroche", acc),
                          s.group("C_pictos", *pic)))
    if not print_version:
        s.body.append(guides([mm(97), mm(197)]))
    return s.render("American's Gym — dépliant, extérieur")


def interieur(print_version=False):
    s = Svg(print_version)
    b = BLEED
    xd, wd = 0, mm(100)
    xe, we = mm(100), mm(100)
    xf, wf = mm(200), mm(97)
    s.body.append(s.group("Fond", s.rect(-b, -b, wd + b, H + 2 * b, WHITE),
                          s.rect(xe, -b, we, H + 2 * b, DARK),
                          s.rect(xf, -b, wf + b, H + 2 * b, LIGHT)))

    # ---------------- volet D : à propos ----------------
    yd = mm(70)
    photo = s.image("photo_facade.jpg", -b, -b, wd + b, yd + mm(8) + b,
                    clip_pts=[(-b, -b), (wd, -b), (wd, yd - mm(12)), (-b, yd + mm(6))], focus=(0.3, 0.5))
    stripe = (s.poly([(-b, yd + mm(6)), (wd, yd - mm(12)), (wd, yd - mm(8.6)), (-b, yd + mm(9.4))], RED)
              + band_along(s, wd * 0.48, wd, (-b, yd + mm(6)), (wd, yd - mm(12)), mm(5.4), mm(1.6), DARK))
    ty = yd + mm(24)
    about = [s.text("À PROPOS", M, ty, 18, 900, INK), s.rect(M, ty + 6, mm(12), 2.4, RED)]
    p1 = ("American’s Gym est bien plus qu’une salle de sport : c’est un lieu de vie dédié à votre "
          "santé, à votre forme et à votre bien-être, au cœur d’Abobo.")
    p2 = ("Que vous débutiez ou que vous soyez confirmé, notre équipe vous accompagne pas à pas "
          "vers vos objectifs, dans une ambiance conviviale et motivante.")
    t, y = s.para(p1, M, ty + mm(11), wd - 2 * M, fill=GREY)
    about.append(t)
    t, y = s.para(p2, M, y + mm(2), wd - 2 * M, fill=GREY)
    about.append(t)
    my = y + mm(7)
    mission = [s.text("NOTRE MISSION", M, my, 11, 800, RED, spacing=0.3)]
    t, y = s.para("Vous aider à devenir plus fort chaque jour et à vous sentir mieux dans votre peau, "
                  "grâce à un accompagnement sérieux et bienveillant.", M, my + mm(6), wd - 2 * M, fill=GREY)
    mission.append(t)
    sig = [s.rect(M, H - mm(19), 2.4, mm(9), RED),
           s.text(["L’excellence du fitness au cœur", "de votre bien-être."], M + 9, H - mm(15), 8.4, 700, INK, leading=11)]
    s.body.append(s.group("Volet_D_a_propos",
                          s.group("D_photo_facade", photo, stripe),
                          s.group("D_a_propos", *about),
                          s.group("D_mission", *mission),
                          s.group("D_signature", *sig)))

    # ---------------- volet E : services ----------------
    deco = (s.poly([(xe + we * 0.62, -b), (xe + we, -b), (xe + we, mm(16))], RED)
            + s.poly([(xe, H - mm(10)), (xe + we * 0.3, H - mm(16)), (xe + we * 0.3, H + b), (xe, H + b)], RED))
    ey = mm(24)
    head = [s.text("NOS SERVICES", xe + M, ey, 18, 900, WHITE),
            s.rect(xe + M, ey + 6, mm(12), 2.4, RED),
            s.text("Tout pour atteindre vos objectifs", xe + M, ey + mm(9), 8.4, 600, GREY_ON_DARK)]
    services = [
        ("dumbbell", "Musculation", "Plateau complet, charges libres et machines guidées pour gagner en force."),
        ("heart", "Cardio-training", "Tapis, vélos et rameurs pour votre endurance et votre santé cardiaque."),
        ("stopwatch", "Coaching personnalisé", "Un programme sur mesure et un suivi régulier de vos progrès."),
        ("group", "Cours collectifs", "L’énergie du groupe pour se dépasser dans la bonne humeur."),
        ("flame", "Perte de poids & remise en forme", "Des séances ciblées pour affiner la silhouette durablement."),
        ("lotus", "Bien-être & récupération", "Étirements et conseils pour récupérer et prendre soin de vous."),
    ]
    items = []
    for i, (ic, name, desc) in enumerate(services):
        yy = ey + mm(20) + i * mm(22)
        items.append(icon(ic, xe + M + 11, yy + 5, 13, WHITE, circle=12))
        items.append(s.text(name, xe + M + 30, yy, 9.6, 700, WHITE))
        t, _ = s.para(desc, xe + M + 30, yy + 12, we - 2 * M - 30, size=7.6, fill=GREY_ON_DARK, leading=11)
        items.append(t)
    s.body.append(s.group("Volet_E_services", s.group("E_formes", deco), s.group("E_titre", *head),
                          s.group("E_liste_services", *items)))

    # ---------------- volet F : formules + appel à l'action ----------------
    fy = mm(24)
    head = [s.text("NOS FORMULES", xf + M, fy, 18, 900, INK),
            s.rect(xf + M, fy + 6, mm(12), 2.4, RED),
            s.text("Choisissez votre rythme", xf + M, fy + mm(9), 8.4, 600, GREY)]
    cards = []
    offers = [("Séance unique", "Accès à la salle pour une séance"),
              ("Mensuel", "Accès illimité pendant 1 mois"),
              ("Trimestriel", "Accès illimité pendant 3 mois"),
              ("Annuel", "Le meilleur rapport qualité-prix")]
    cw = wf - 2 * M
    for i, (name, desc) in enumerate(offers):
        yy = fy + mm(17) + i * mm(19.5)
        cards.append(s.rect(xf + M, yy, cw, mm(15.5), WHITE, rx=mm(1.6)))
        cards.append(s.rect(xf + M, yy, mm(1.4), mm(15.5), RED))
        cards.append(s.text(name, xf + M + mm(4), yy + mm(6.6), 9.2, 800, INK))
        cards.append(s.text(desc, xf + M + mm(4), yy + mm(11.4), 6.6, 500, GREY))
        cards.append(s.text("____ FCFA", xf + M + cw - mm(3), yy + mm(9), 9.5, 800, RED, anchor="end"))
    cta_top = H - mm(62)
    cta = [s.poly([(xf, cta_top + mm(14)), (xf + wf + b, cta_top), (xf + wf + b, H + b), (xf, H + b)], RED),
           s.poly([(xf, cta_top + mm(14)), (xf + wf * 0.4, cta_top + mm(8.2)), (xf + wf * 0.4, cta_top + mm(11.4)), (xf, cta_top + mm(17.2))], DARK),
           s.text(["REJOIGNEZ-", "NOUS !"], xf + M, H - mm(16) - 11.5 - mm(7) - 23, 20, 900, WHITE, leading=23),
           s.text(["Votre transformation", "commence aujourd’hui."], xf + M, H - mm(16) - 11.5, 8.6, 600, WHITE, leading=11.5),
           icon("phone", xf + M + 8, H - mm(8.5) - 3, 10, RED, bg=WHITE, circle=8),
           s.text(PHONE, xf + M + 21, H - mm(8.5), 9.2, 800, WHITE)]
    s.body.append(s.group("Volet_F_formules", s.group("F_titre", *head), s.group("F_formules", *cards),
                          s.group("F_appel_action", *cta)))
    if not print_version:
        s.body.append(guides([mm(100), mm(200)]))
    return s.render("American's Gym — dépliant, intérieur")


def guides(xs):
    lines = "".join(f'<line x1="{f(x)}" y1="0" x2="{f(x)}" y2="{f(H)}" stroke="#00B7EB" stroke-width="0.5" '
                    f'stroke-dasharray="4 3"/>' for x in xs)
    return f'<g id="REPERES_pliage_a_masquer">{lines}</g>'


if __name__ == "__main__":
    out = HERE
    (out / "american_gym_depliant_exterieur.svg").write_text(exterieur(), encoding="utf-8")
    (out / "american_gym_depliant_interieur.svg").write_text(interieur(), encoding="utf-8")
    pr = out / "_impression"
    pr.mkdir(exist_ok=True)
    (pr / "exterieur.svg").write_text(exterieur(True), encoding="utf-8")
    (pr / "interieur.svg").write_text(interieur(True), encoding="utf-8")
    print("SVG écrits")
