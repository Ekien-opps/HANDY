# Positions of the 15 3D products on the "Présentation des produits" slides (13 to 18).
# Each instance: key, base point on slide (EMU, bottom-centre of the product), scale k (EMU per real cm), rotations (deg)
import math

W, H = 12192000, 6858000
EPICES = ['epice_poulet', 'epice_poisson', 'paprika', 'piment', 'akpi',
          'djoumble', 'crevette', 'poudre_poisson', 'ail', 'bouillon']
MARINADES = ['marinade_poulet', 'marinade_poisson', 'marinade_mixte']
ESSENTIELS = ['arachide', 'huile']
ALL = EPICES + MARINADES + ESSENTIELS

NAMES = {'marinade_poulet': 'Marinade poulet', 'marinade_poisson': 'Marinade poisson', 'marinade_mixte': 'Marinade mixte',
         'epice_poulet': 'Épice spéciale poulet', 'epice_poisson': 'Épice spéciale poisson', 'paprika': 'Paprika',
         'piment': 'Piment en poudre', 'akpi': "Graines d'akpi", 'djoumble': 'Poudre de djoumblé',
         'crevette': 'Poudre de crevettes séchées', 'poudre_poisson': 'Poudre de poisson sec', 'ail': "Purée d'ail",
         'bouillon': 'Bouillon bio de poulet', 'arachide': "Pâte d'arachide", 'huile': 'Huile rouge'}
# real widths in cm (front view) used for spacing
WID = {k: 13.99 for k in EPICES}
WID.update({k: 8.66 for k in MARINADES}); WID.update({'arachide': 12.0, 'huile': 6.6})
HEI = {k: 20.51 for k in EPICES}
HEI.update({k: 15.89 for k in MARINADES}); HEI.update({'arachide': 11.75, 'huile': 18.3})


def inst(key, x, y, k, ax=0, ay=0, az=0, shadow=True):
    return dict(key=key, x=int(x), y=int(y), k=k, ax=ax, ay=ay, az=az, shadow=shadow)


def row(keys, cx, base_y, k, gap_cm, ax=4, ay_list=None):
    total = sum(WID[q] for q in keys) + gap_cm * (len(keys) - 1)
    x = cx - total * k / 2
    out = []
    for i, q in enumerate(keys):
        w = WID[q] * k
        out.append(inst(q, x + w / 2, base_y, k, ax, (ay_list[i] if ay_list else 0)))
        x += w + gap_cm * k
    return out


def camera(insts, F, Fp, Z):
    """Zoom about focus F on the previous composition, F lands on Fp (a camera dolly)."""
    out = []
    for i in insts:
        j = dict(i)
        j['x'] = int(Fp[0] + Z * (i['x'] - F[0])); j['y'] = int(Fp[1] + Z * (i['y'] - F[1])); j['k'] = i['k'] * Z
        out.append(j)
    return out


L = {}
# --- 14: line-up on the table (Bob's Red Mill), back row = 10 épices, front row = marinades + essentiels
back = row(EPICES, W / 2, 3.18e6, 60000, 1.4, ax=4, ay_list=[0] * 10)
front = row(['huile', 'marinade_poulet', 'marinade_poisson', 'marinade_mixte', 'arachide'], W / 2, 6.18e6, 86000, 3.2,
            ax=5, ay_list=[-8, -4, 0, 4, 10])
L[14] = back + front

# --- 13: products float in an orbit around the section title (they "appear together" and will land on 14)
orb = []
n = len(ALL)
rng_ay = [28, -34, 18, -22, 40, -16, 30, -38, 12, -26, 35, -12, 24, -30, 20]
rng_az = [8, -6, 10, -9, 5, -11, 7, -5, 9, -8, 6, -10, 4, -7, 9]
order = ['arachide', 'paprika', 'marinade_poulet', 'piment', 'akpi', 'huile', 'djoumble', 'crevette',
         'marinade_poisson', 'poudre_poisson', 'ail', 'epice_poulet', 'marinade_mixte', 'bouillon', 'epice_poisson']
for i, q in enumerate(order):
    a = -math.pi / 2 + 2 * math.pi * i / n + 0.21
    depth = (math.sin(a) + 1) / 2              # 0 = top (far) .. 1 = bottom (near)
    k = (38000 + 30000 * depth) * (1.25 if q in MARINADES + ESSENTIELS else 1.0)
    x = W / 2 + 5.15e6 * math.cos(a)
    yc = H / 2 + 0.15e6 + 2.55e6 * math.sin(a)
    orb.append(inst(q, x, yc + HEI[q] * k / 2, k, 12, rng_ay[i], rng_az[i], shadow=False))
L[13] = orb

# --- 15: camera dolly onto the marinades (zoom x2.15), the spice row exits upward, essentiels exit right
mar14 = [i for i in L[14] if i['key'] == 'marinade_poisson'][0]
F = (mar14['x'], mar14['y'] - HEI['marinade_poisson'] * mar14['k'] / 2)
L[15] = camera(L[14], F, (8.75e6, 3.75e6), 2.15)
for i in L[15]:
    if i['key'] in MARINADES:
        i['ay'] = {'marinade_poulet': -14, 'marinade_poisson': 0, 'marinade_mixte': 14}[i['key']]
    if i['key'] == 'huile':
        i['x'] = -1.6e6                         # leaves frame left, behind the text column
    if i['key'] == 'arachide':
        i['x'] = W + 2.2e6

# --- 16: the 10 épices re-arrange into a 5 x 2 grid (Jacquet), marinades sink out bottom-left, essentiels off right
g = []
k16 = 90000
pitch_x, cx0 = 1.42e6, 5.55e6
for r in range(2):
    for c in range(5):
        q = EPICES[r * 5 + c]
        g.append(inst(q, cx0 + c * pitch_x, (3.22e6 if r == 0 else 5.98e6), k16, 4, [-10, -5, 0, 5, 10][c]))
L[16] = g + [inst('marinade_poulet', -1.2e6, H + 3.7e6, 190000, 5, -14), inst('marinade_poisson', 0.6e6, H + 4.0e6, 205000, 5, 0),
             inst('marinade_mixte', 2.4e6, H + 3.7e6, 190000, 5, 14),
             inst('arachide', W + 2.0e6, 6.2e6, 160000, 8, 20), inst('huile', W + 1.0e6, 6.0e6, 160000, 5, -10)]

# --- 17: essentiels, close-up; épices drift up and out (camera tilts down)
L[17] = [dict(i, y=int(i['y'] - 7.2e6)) for i in g] + [
    inst('marinade_poulet', -2.2e6, 6.6e6, 150000, 5, -14), inst('marinade_poisson', -1.0e6, 6.9e6, 160000, 5, 0),
    inst('marinade_mixte', -3.4e6, 6.6e6, 150000, 5, 14),
    inst('huile', 9.75e6, 6.12e6, 205000, 5, -16), inst('arachide', 7.35e6, 6.42e6, 210000, 9, 24)]

# --- 18: appetite display: three-tier podium (pyramid), all 15 products together
t1 = row(['paprika', 'epice_poulet', 'piment'], W / 2, 3.06e6, 56000, 1.2, ax=6, ay_list=[-8, 0, 8])
t2 = row(['akpi', 'djoumble', 'epice_poisson', 'crevette', 'poudre_poisson'], W / 2, 4.38e6, 66000, 1.2, ax=6,
         ay_list=[-12, -6, 0, 6, 12])
t3 = row(['bouillon', 'huile', 'marinade_poulet', 'marinade_poisson', 'marinade_mixte', 'arachide', 'ail'], W / 2, 6.22e6,
         84000, 2.2, ax=7, ay_list=[-14, -10, -5, 0, 5, 12, 14])
L[18] = t1 + t2 + t3
TIERS = [(3.06e6, 56000, t1), (4.38e6, 66000, t2), (6.22e6, 84000, t3)]

# z-order: farther (higher base y = nearer) drawn last
for s in L:
    L[s].sort(key=lambda i: i['y'])
    assert sorted(i['key'] for i in L[s]) == sorted(ALL), s
