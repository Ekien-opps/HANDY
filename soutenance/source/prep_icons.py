# Lucide icons -> PNG (white / bordeaux) + elephant watermark (white icon with a soft fade)
import os, cairosvg, numpy as np
from PIL import Image
S = '/tmp/claude-0/-home-user-HANDY/36455e3e-c271-5390-ad89-57cd94b34b42'
SRC = S + '/scratchpad/tools/node_modules/lucide-static/icons/'
A = S + '/scratchpad/build/assets/'
os.makedirs(A + 'icons', exist_ok=True)
ICONS = ['printer', 'clapperboard', 'monitor-smartphone', 'book-open-text', 'eye', 'messages-square',
         'trending-up', 'palette', 'layers', 'globe', 'leaf', 'users-round', 'cooking-pot']
for n in ICONS:
    svg = open(SRC + n + '.svg').read()
    for tag, col in (('w', '#FFFFFF'), ('b', '#7B1421')):
        s2 = svg.replace('stroke="currentColor"', f'stroke="{col}"').replace('stroke-width="2"', 'stroke-width="1.75"')
        cairosvg.svg2png(bytestring=s2.encode(), write_to=f'{A}icons/{n}_{tag}.png', output_width=512, output_height=512)
# watermark: white elephant icon, alpha fading from upper-left (strong) to lower-right (soft)
im = Image.open(S + '/images/7.png').convert('RGBA')
a = np.array(im).astype(float)
h, w = a.shape[:2]
yy, xx = np.mgrid[0:h, 0:w]
fade = 1.0 - 0.75 * ((xx / w) * 0.6 + (yy / h) * 0.4)
a[..., 3] = a[..., 3] * fade
a[..., :3] = 255
Image.fromarray(a.astype('uint8'), 'RGBA').save(A + 'watermark.png', optimize=True)
print(sorted(os.listdir(A + 'icons'))[:6], len(os.listdir(A + 'icons')))
