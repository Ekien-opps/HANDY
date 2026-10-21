# Render every 3D pose with three.js, then compute PowerPoint frame geometry + fallback PNGs
import json, subprocess, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from layout3d import L
B = os.path.dirname(os.path.abspath(__file__)); T = B + '/../tools'
VFOV = 1.5588457   # 2*d*tan(22.5deg) with d = 67740115 EMU = 1.8817 m : scene height seen by the viewport
jobs = {}
for s, insts in L.items():
    for i in insts:
        jid = f"{i['key']}_{i['ax']}_{i['ay']}_{i['az']}".replace('-', 'm')
        i['jid'] = jid
        jobs[jid] = dict(id=jid, key=i['key'], ax=i['ax'], ay=i['ay'], az=i['az'])
json.dump(list(jobs.values()), open(B + '/jobs.json', 'w'))
if not os.path.exists(B + '/renders/meta.json') or '--force' in sys.argv:
    subprocess.run(['node', 'render3d.mjs', B + '/jobs.json', B + '/renders'], cwd=T, check=True)
meta = json.load(open(B + '/renders/meta.json'))
os.makedirs(B + '/fallback', exist_ok=True)
out = {}
for s, insts in L.items():
    for n, i in enumerate(insts):
        m = meta[i['jid']]; N = m['N']; c = N / 2
        x0, y0, x1, y1 = m['bbox']
        hw = max(c - x0, x1 - c) + 6; hh = max(c - y0, y1 - c) + 6
        V = VFOV * i['k'] * m['L']                      # objViewport size (EMU)
        px = V / N                                      # EMU per canvas pixel
        cx, cy = i['x'] - (m['base'][0] - c) * px, i['y'] - (m['base'][1] - c) * px
        fw, fh = 2 * hw * px, 2 * hh * px
        # fallback image cropped to the frame, ~150 dpi of its on-slide size
        fid = f"s{s}_{i['key']}"
        im = Image.open(f"{B}/renders/{i['jid']}.png").crop((int(c - hw), int(c - hh), int(c + hw), int(c + hh)))
        tw = max(60, int(fw / 914400 * 150)); im = im.resize((tw, max(1, int(tw * im.size[1] / im.size[0]))), Image.LANCZOS)
        im.save(f"{B}/fallback/{fid}.png", optimize=True)
        sx = i['k'] * m['L']                            # model size on slide (EMU) for shadows
        out.setdefault(s, []).append(dict(i, V=int(V), off=(int(cx - fw / 2), int(cy - fh / 2)), ext=(int(fw), int(fh)),
                                          L=m['L'], center=m['center'], png=f"{B}/fallback/{fid}.png",
                                          foot=(int(i['x']), int(i['y'])), size=int(sx)))
json.dump(out, open(B + '/instances.json', 'w'), indent=1)
print({s: len(v) for s, v in out.items()}, len(jobs), 'renders')
