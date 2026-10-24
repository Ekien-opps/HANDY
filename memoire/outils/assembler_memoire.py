import io, sys, copy
import pdfplumber
from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.colors import Color, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

Z = sys.argv[1]          # dossier des PDF extraits
OUT = sys.argv[2]
W, H = 595.32, 841.92
LIB = '/usr/share/fonts/truetype/liberation/'
for n, f in [('TNR', 'LiberationSerif-Regular'), ('TNR-B', 'LiberationSerif-Bold'),
             ('TNR-I', 'LiberationSerif-Italic'), ('TNR-BI', 'LiberationSerif-BoldItalic'),
             ('ARB', 'LiberationSans-Bold')]:
    pdfmetrics.registerFont(TTFont(n, LIB + f + '.ttf'))
RED = Color(0.753, 0, 0)
GREY = Color(0.45, 0.45, 0.45)
L, R = 70.8, 525.0      # marges utilisées par les pages existantes

def src(name):
    return Z + '/' + name + '.pdf'

def badge_poly(path, idx):
    p = pdfplumber.open(path).pages[idx]
    for c in p.curves:
        col = c.get('non_stroking_color')
        if c['top'] > 780 and col and len(col) == 3 and abs(col[0] - 0.753) < 0.01:
            return [(x, y) for x, y in c['pts']]
    raise RuntimeError('badge introuvable: %s p%d' % (path, idx))

def draw_badge(c, poly, label):
    """Redessine le badge rouge (masque l'ancien numéro) et écrit le nouveau."""
    c.saveState()
    pth = c.beginPath()
    pth.moveTo(poly[0][0], H - poly[0][1])
    for x, y in poly[1:]:
        pth.lineTo(x, H - y)
    pth.close()
    c.setFillColor(RED); c.setStrokeColor(black); c.setLineWidth(2.25)
    c.drawPath(pth, fill=1, stroke=1)
    x0 = min(x for x, _ in poly)
    cx, cy = x0 + 20.0, H - 814.2
    size = 12.0
    while pdfmetrics.stringWidth(label, 'ARB', size) > 15 and size > 7:
        size -= 0.5
    c.setFillColor(black); c.setStrokeColor(black); c.setLineWidth(0.9)
    t = c.beginText()
    t.setTextRenderMode(2)
    t.setFont('ARB', size)
    t.setTextOrigin(cx - pdfmetrics.stringWidth(label, 'ARB', size) / 2, cy - size * 0.36)
    t.textOut(label)
    c.drawText(t)
    c.restoreState()

def overlay(draw):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(W, H))
    draw(c)
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]

def page_of(path, idx):
    return PdfReader(path).pages[idx]

def stamped(path, idx, draw):
    pg = page_of(path, idx)
    pg.merge_page(overlay(draw))
    return pg

MEM = src('Memoire correcte')
TPL_POLY = badge_poly(MEM, 84)          # page 85 vierge = gabarit en-tête/pied/badge

def new_page(label, draw_body):
    def d(c):
        draw_badge(c, TPL_POLY, label)
        draw_body(c)
    return stamped(MEM, 84, d)

def rebadge(path, idx, label):
    poly = badge_poly(path, idx)
    return stamped(path, idx, lambda c: draw_badge(c, poly, label))

def title(c, txt, size=16):
    c.setFillColor(black); c.setFont('TNR-B', size)
    c.drawString(L, H - 73 - size * 0.8, txt)

def leader_line(c, y, x, parts, num, numfont='TNR', size=12):
    """parts = [(texte, police)], points de conduite jusqu'au numéro aligné à droite."""
    xx = x
    for t, f in parts:
        c.setFont(f, size); c.drawString(xx, y, t)
        xx += pdfmetrics.stringWidth(t, f, size)
    nw = pdfmetrics.stringWidth(num, numfont, size)
    c.setFont(numfont, size); c.drawString(R - nw, y, num)
    dot = pdfmetrics.stringWidth('.', 'TNR', size)
    x1, x2 = xx + 3, R - nw - 3
    n = int((x2 - x1) / dot)
    if n > 0:
        c.setFont('TNR', size); c.drawString(x2 - n * dot, y, '.' * n)

def wrap(text, font, size, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if pdfmetrics.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def justified(c, lines, x, y, width, font, size, lead):
    for i, ln in enumerate(lines):
        words = ln.split()
        last = i == len(lines) - 1
        c.setFont(font, size)
        if last or len(words) == 1:
            c.drawString(x, y, ln)
        else:
            tw = sum(pdfmetrics.stringWidth(w, font, size) for w in words)
            gap = (width - tw) / (len(words) - 1)
            xx = x
            for w in words:
                c.drawString(xx, y, w); xx += pdfmetrics.stringWidth(w, font, size) + gap
        y -= lead
    return y

# ---------------------------------------------------------------- pages créées
def blank_page():
    return overlay(lambda c: c.setFillColor(white))

def dedicace(c):
    c.setFillColor(black)
    c.setFont('TNR-BI', 18)
    c.drawCentredString(W / 2, H / 2 + 8, 'À Ma Mère !')
    c.drawCentredString(W / 2, H / 2 - 26, 'Mes Enfants !')

SIGLES = [
    ('2D / 3D', 'Deux dimensions / Trois dimensions'),
    ('CAMES', 'Conseil Africain et Malgache pour l’Enseignement Supérieur'),
    ('CMJN', 'Cyan, Magenta, Jaune, Noir'),
    ('CMS', 'Content Management System (Système de Gestion de Contenu)'),
    ('CSS', 'Cascading Style Sheets (feuilles de style en cascade)'),
    ('DD', 'Dictionnaire de Données'),
    ('FCFA', 'Franc de la Communauté Financière Africaine'),
    ('HTML', 'HyperText Markup Language'),
    ('ICANN', 'Internet Corporation for Assigned Names and Numbers'),
    ('ISTC', 'Institut des Sciences et Techniques de la Communication'),
    ('LMD', 'Licence – Master – Doctorat'),
    ('MCD', 'Modèle Conceptuel de Données'),
    ('MERISE', 'Méthode d’Étude et de Réalisation Informatique pour les'),
    ('', 'Systèmes d’Entreprise'),
    ('MLD', 'Modèle Logique de Données'),
    ('OQLF', 'Office Québécois de la Langue Française'),
    ('PDG', 'Président-Directeur Général'),
    ('RVB', 'Rouge, Vert, Bleu'),
    ('SEO', 'Search Engine Optimization (référencement naturel)'),
    ('SFX', 'Sound Effects (effets sonores)'),
    ('SGBD', 'Système de Gestion de Bases de Données'),
    ('UI', 'User Interface (interface utilisateur)'),
    ('URL', 'Uniform Resource Locator'),
    ('USA', 'United States of America (États-Unis d’Amérique)'),
    ('UX', 'User Experience (expérience utilisateur)'),
    ('VFX', 'Visual Effects (effets visuels)'),
]

def sigles(c):
    title(c, 'LISTE DES SIGLES ET ABRÉVIATIONS')
    y = H - 120
    for s, d in SIGLES:
        if s:
            y -= 6
            c.setFont('TNR-B', 12); c.drawString(L, y, s)
            c.setFont('TNR', 12); c.drawString(L + 62, y, ':')
        c.setFont('TNR', 12); c.drawString(L + 72, y, d)
        y -= 18

FIGS = [
    (52, 'Mise en situation du dépliant', 63),
    (53, 'Ouverture du logiciel Adobe Photoshop 1990 - 2024', 63),
    (54, 'Positionnement du background et insertion du texte', 64),
    (55, 'Positionnement du background et insertion de texte', 64),
    (56, 'Kakemono final', 65),
    (57, 'Mise en situation du kakemono', 65),
    (58, 'Ouverture du logiciel Adobe Photoshop', 66),
    (59, 'Création du background', 66),
    (60, 'Affiche réseaux sociaux', 67),
    (61, 'Lancement du logiciel Adobe After Effects 1992-2024', 68),
    (62, 'Animation du Logo', 69),
    (63, 'Rendu final de l’animation du Logo', 69),
    (64, 'Lancement du logiciel Adobe After Effects 1992-2024', 70),
    (65, 'Animation des Images et des textes', 70),
    (66, 'Rendu final de la vidéo 2D', 71),
    (67, 'Ouverture du logiciel Blender', 72),
    (68, 'Outils techniques', 72),
    (69, 'Modélisation du bâtiment d’American’s Gym', 73),
    (70, 'Page « Accueil » American’s Gym', 74),
    (71, 'Page « À Propos »', 74),
    (72, 'Page « Nos équipements »', 75),
    (73, 'Page « Boutique »', 75),
    (74, 'Page « Tarifs »', 76),
    (75, 'Page « Contacts »', 76),
]

def figs_suite(c):
    c.setFillColor(black)
    y = H - 108 - 10
    for n, cap, p in FIGS:
        leader_line(c, y, L, [('Figure %d' % n, 'TNR-BI'), (' : ' + cap, 'TNR-I')], str(p))
        y -= 25.5

def tableaux(c):
    title(c, 'LISTE DES TABLEAUX')
    y = H - 118
    for n, cap, p in [(1, 'Dictionnaire de données', 48),
                      (2, 'Tableau du délai d’exécution', 53),
                      (3, 'Tableau du coût de réalisation', 54)]:
        leader_line(c, y, L, [('Tableau %d' % n, 'TNR-BI'), (' : ' + cap, 'TNR-I')], str(p))
        y -= 25.5

# (niveau, texte, page) — niveau 0 = rubriques/parties, 1 = chapitres, 2 = I., 3 = I.1.
TOC = [
    (0, 'REMERCIEMENTS', 'V'), (0, 'SOMMAIRE', 'VI'),
    (0, 'LISTE DES SIGLES ET ABRÉVIATIONS', 'VII'), (0, 'LISTE DES ILLUSTRATIONS', 'VIII'),
    (0, 'LISTE DES TABLEAUX', 'XI'), (0, 'AVANT-PROPOS', 'XII'),
    (0, 'INTRODUCTION', 1), (0, 'PROBLÉMATIQUE', 2),
    (0, 'PREMIÈRE PARTIE : CADRE D’ÉTUDE', 3),
    (1, 'CHAPITRE 1 : APPROCHE THÉORIQUE', 4),
    (2, 'I. JUSTIFICATION DU CHOIX DU SUJET', 4),
    (3, 'I.1. Motivation personnelle', 4), (3, 'I.2. Intérêt scientifique', 4),
    (3, 'I.3. Intérêt social', 4), (3, 'I.4. Intérêt économique', 5),
    (2, 'II. APPROCHE DÉFINITIONNELLE', 5),
    (3, 'II.1. Conception', 5), (3, 'II.2. Réalisation', 6), (3, 'II.3. Communication', 6),
    (3, 'II.4. Supports de communication', 7), (3, 'II.5. Promotion', 7),
    (3, 'II.6. Salle de sport', 8), (3, 'II.7. American’s Gym', 8),
    (1, 'CHAPITRE 2 : ÉTUDE DE L’EXISTANT', 9),
    (2, 'I. PRÉSENTATION DE L’EXISTANT', 9),
    (3, 'I.1. Services et activités proposés', 9), (3, 'I.2. Organisation de l’équipe', 9),
    (3, 'I.3. Présentation des canaux digitaux actuels', 10),
    (2, 'II. CRITIQUE DE L’EXISTANT', 10),
    (3, 'II.1. L’identité visuelle', 10), (3, 'II.2. Aperçu des pages Facebook et TikTok', 11),
    (2, 'III. CONSÉQUENCES', 12),
    (2, 'IV. PROPOSITION DE SOLUTION', 12),
    (3, 'IV.1. Supports imprimés', 12), (3, 'IV.2. Supports digitaux', 13),
    (1, 'CHAPITRE 3 : PRÉSENTATION DE LA STRUCTURE « AMERICAN’S GYM »', 14),
    (2, 'I. PRÉSENTATION DE LA STRUCTURE', 14), (2, 'II. ORGANISATION DE LA STRUCTURE', 15),
    (2, 'III. MISSIONS DE LA STRUCTURE', 16), (2, 'IV. VISION', 16), (2, 'V. VALEURS', 16),
    (2, 'VI. LES DIFFÉRENTS SERVICES', 17), (2, 'VII. IDENTITÉ DE LA MARQUE', 17),
    (0, 'DEUXIÈME PARTIE : ÉTUDE TECHNIQUE', 18),
    (1, 'CHAPITRE 1 : CAHIER DE CHARGES', 19),
    (2, 'I. OBJECTIF', 19), (2, 'II. CIBLES', 19), (2, 'III. PERSPECTIVES', 20),
    (2, 'IV. RESSOURCES HUMAINES', 20), (2, 'V. RESSOURCES MATÉRIELLES ET LOGICIELLES', 21),
    (2, 'VI. SPÉCIFICATIONS TECHNIQUES DE CRÉATION', 21),
    (1, 'CHAPITRE 2 : IDENTITÉ VISUELLE', 22),
    (2, 'I. LOGO', 22), (2, 'II. CHARTE GRAPHIQUE', 23),
    (3, 'II.1. Description du logo', 23), (3, 'II.2. Typographie', 24),
    (3, 'II.3. Aspect iconographique', 26), (3, 'II.4. Aspect chromatique', 27),
    (3, 'II.5. Principe d’utilisation et interdits', 28),
    (1, 'CHAPITRE 3 : CONCEPTION DES SUPPORTS', 32),
    (2, 'I. SUPPORTS IMPRIMÉS', 32),
    (3, 'I.1. Affiches', 32), (3, 'I.2. Flyer', 34), (3, 'I.3. Dépliant', 35), (3, 'I.4. Kakemono', 37),
    (2, 'II. CONCEPTION DES SUPPORTS DIGITAUX', 38),
    (2, 'III. SPOT ANIMATIQUE 2D', 38),
    (3, 'III.1. Fiche technique', 38), (3, 'III.2. Synopsis', 39), (3, 'III.3. Durée', 39),
    (3, 'III.4. Scénario', 39),
    (2, 'IV. SPOT ANIMATIQUE 3D', 40),
    (3, 'IV.1. Fiche technique', 40), (3, 'IV.2. Synopsis', 40), (3, 'IV.3. Durée', 40),
    (3, 'IV.4. Scénario', 40),
    (2, 'V. CONCEPTION DU SITE WEB', 41),
    (3, 'V.1. Conception du site web', 41), (3, 'V.2. Arborescence du site', 41),
    (3, 'V.3. Maquette des différentes pages du site web', 42),
    (3, 'V.3. Phase de préparation du site web', 45),
    (2, 'VI. CHOIX DES LANGAGES', 46),
    (3, 'VI.1. HTML', 46), (3, 'VI.2. CSS', 46), (3, 'VI.3. JavaScript', 47),
    (2, 'VII. CONCEPTION DE BASE DE DONNÉES', 47),
    (3, 'VII.1. Le Système de Gestion des Bases de Données (SGBD)', 47),
    (3, 'VII.2. La méthode d’analyse', 47), (3, 'VII.3. Le Modèle Conceptuel de Données', 48),
    (2, 'VIII. CHOIX DES LOGICIELS', 50),
    (3, 'VIII.1. Illustrator', 50), (3, 'VIII.2. Adobe Photoshop', 51),
    (3, 'VIII.3. Adobe After Effects', 51), (3, 'VIII.4. Premiere Pro', 52),
    (3, 'VIII.5. Adobe Dreamweaver', 52),
    (2, 'IX. DÉLAI ET COÛT DU PROJET', 53),
    (3, 'IX.1. Planning d’exécution (Délais)', 53),
    (3, 'IX.2. Estimation budgétaire (Coûts de la réalisation)', 54),
    (0, 'TROISIÈME PARTIE : RÉALISATION DES SUPPORTS', 55),
    (1, 'CHAPITRE 1 : SUPPORTS IMPRIMÉS / PRINTS', 56),
    (2, 'I. RÉALISATION DES AFFICHES', 56),
    (3, 'I.1. Première affiche', 56), (3, 'I.2. Deuxième affiche', 58),
    (3, 'I.3. Réalisation du flyer', 59),
    (2, 'II. RÉALISATION DU DÉPLIANT', 61), (2, 'III. RÉALISATION DU KAKÉMONO', 63),
    (2, 'IV. RÉALISATION DE SUPPORTS DIGITAUX', 66),
    (1, 'CHAPITRE 2 : VIDÉOS 2D ET 3D', 68),
    (2, 'I. RÉALISATION DU SPOT ANIMATIQUE 2D', 68), (2, 'II. RÉALISATION DU SPOT VIDÉO 2D', 70),
    (2, 'III. LES ÉTAPES DE LA RÉALISATION DU SPOT 3D', 72),
    (1, 'CHAPITRE 3 : SITE WEB', 74),
    (2, 'I. PRÉSENTATION DES PAGES', 74), (2, 'II. HÉBERGEMENT', 77), (2, 'III. RÉFÉRENCEMENT', 77),
    (0, 'CONCLUSION', 78), (0, 'BIBLIOGRAPHIE', 80), (0, 'WEBOGRAPHIE', 81), (0, 'GLOSSAIRE', 82),
]
TOC_START = 85
INDENT = {0: 0, 1: 14, 2: 30, 3: 48}
FONT = {0: 'TNR-B', 1: 'TNR-B', 2: 'TNR', 3: 'TNR'}
LEAD = 17.2
TOP_FIRST, TOP_NEXT, BOTTOM = H - 118, H - 82, 78

def toc_pages():
    # répartition en pages
    pages, cur, y = [], [], TOP_FIRST
    entries = TOC + [(0, 'TABLE DES MATIÈRES', TOC_START)]
    for e in entries:
        extra = 6 if e[0] == 0 else (3 if e[0] == 1 else 0)
        if y - extra < BOTTOM:
            pages.append(cur); cur, y = [], TOP_NEXT
        y -= extra
        cur.append((e, y)); y -= LEAD
    pages.append(cur)
    out = []
    for i, pe in enumerate(pages):
        def body(c, pe=pe, first=(i == 0)):
            c.setFillColor(black)
            if first:
                title(c, 'TABLE DES MATIÈRES')
            for (lvl, txt, num), y in pe:
                leader_line(c, y, L + INDENT[lvl], [(txt, FONT[lvl])], str(num),
                            numfont=FONT[lvl], size=12)
        out.append(new_page(str(TOC_START + i), body))
    return out

RESUME = ("Le présent mémoire porte sur la conception et la réalisation de supports de "
          "communication pour la promotion d’American’s Gym, structure de fitness, de musculation et "
          "de sports de combat située à Abobo-Dokui (Abidjan). Malgré la qualité de ses équipements et "
          "la diversité de ses activités, la structure souffre d’une visibilité limitée, liée à une "
          "identité visuelle appliquée de manière incohérente, à une ligne éditoriale confuse sur les "
          "réseaux sociaux et à l’absence d’un site web propre. À partir d’une analyse de l’existant et "
          "d’un cahier des charges, l’étude propose un dispositif de communication cohérent : identité "
          "visuelle et charte graphique, supports imprimés (affiches, flyer, dépliant, kakémono), "
          "visuels pour les réseaux sociaux, spots animés 2D et 3D réalisés avec Adobe After Effects et "
          "Blender, ainsi qu’un site web vitrine développé en HTML, CSS et JavaScript, appuyé sur une "
          "base de données modélisée selon la méthode MERISE. Le coût global du projet est estimé à "
          "4 800 000 FCFA. Ces réalisations visent à renforcer l’image de marque d’American’s Gym, à "
          "attirer de nouveaux adhérents et à fidéliser sa clientèle ; leur efficacité devra être "
          "mesurée après leur diffusion.")
MOTS = ("Mots-clés : communication visuelle, identité visuelle, supports de communication, "
        "salle de sport, motion design, site web.")
ABSTRACT = ("This thesis deals with the design and production of communication materials to promote "
            "American’s Gym, a fitness, bodybuilding and combat sports facility located in Abobo-Dokui "
            "(Abidjan). Despite the quality of its equipment and the variety of its activities, the gym "
            "suffers from limited visibility, due to an inconsistently applied visual identity, a "
            "confusing editorial line on social media and the lack of a dedicated website. Based on an "
            "analysis of the existing situation and a set of specifications, the study proposes a "
            "consistent communication system: a visual identity and graphic charter, printed materials "
            "(posters, flyer, leaflet, roll-up banner), social media visuals, 2D and 3D animated "
            "commercials produced with Adobe After Effects and Blender, and a showcase website developed "
            "in HTML, CSS and JavaScript, supported by a database designed with the MERISE method. The "
            "overall cost of the project is estimated at 4,800,000 FCFA. These productions aim to "
            "strengthen American’s Gym’s brand image, attract new members and retain its customers; "
            "their effectiveness will have to be measured after their release.")
KEYS = ("Keywords: visual communication, visual identity, communication materials, gym, "
        "motion design, website.")

def quatrieme(c):
    c.setFillColor(RED)
    p = c.beginPath(); p.moveTo(0, 0); p.lineTo(46, 0); p.lineTo(22, H); p.lineTo(0, H); p.close()
    c.drawPath(p, fill=1, stroke=0)
    x, width = 85, W - 85 - 70.8
    y = H - 80
    c.setFillColor(black)
    for head, txt, kw in [('RÉSUMÉ', RESUME, MOTS), ('ABSTRACT', ABSTRACT, KEYS)]:
        c.setFont('TNR-B', 14); c.drawCentredString(x + width / 2, y, head); y -= 26
        y = justified(c, wrap(txt, 'TNR', 11.5, width), x, y, width, 'TNR', 11.5, 16)
        y -= 4
        y = justified(c, wrap(kw, 'TNR-BI', 11.5, width), x, y, width, 'TNR-BI', 11.5, 16)
        y -= 34

# ---------------------------------------------------------------- assemblage
w = PdfWriter()
add = w.add_page
add(page_of(src('PAGE DE GARDE Correcte'), 0))                 # I   couverture (non numérotée)
add(blank_page())                                                # II  page de garde vierge
add(page_of(src('PAGE 3 THEME'), 0))                            # III page de titre
add(new_page('IV', dedicace))                                    # IV  dédicace (à compléter)
add(page_of(src('REMERCIEMENTS'), 0))                           # V
add(page_of(src('SOMMAIRE'), 0))                                # VI
add(new_page('VII', sigles))                                     # VII
add(rebadge(src('LISTE DES ILLUSTRATIONS'), 0, 'VIII'))         # VIII fig. 1-27
add(rebadge(src('LISTE DES ILLUSTRATIONS SUITE ET FIN'), 0, 'IX'))  # IX fig. 28-51
add(stamped(src('LISTE DES ILLUSTRATIONS'), 1,                   # X  fig. 52-75 (page vide réutilisée)
            lambda c: (draw_badge(c, badge_poly(src('LISTE DES ILLUSTRATIONS'), 1), 'X'), figs_suite(c))))
add(new_page('XI', tableaux))                                    # XI
add(rebadge(src('AVANT PROPOS'), 0, 'XII'))                     # XII
mem = PdfReader(MEM)
for i in range(84):                                              # 1-84 corps → glossaire
    add(mem.pages[i])
for pg in toc_pages():                                           # 85+ table des matières
    add(pg)
add(overlay(quatrieme))                                          # 4e de couverture (non numérotée)
w.add_metadata({'/Title': 'Conception et réalisation de supports de communication pour la '
                          'promotion de la structure de sport « American’s Gym »',
                '/Author': 'CAMARA BINTOU ÉPSE HOZAN'})
with open(OUT, 'wb') as f:
    w.write(f)
print('pages:', len(w.pages))
