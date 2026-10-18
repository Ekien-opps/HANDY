import sys, subprocess
from PIL import Image
sys.path.insert(0, '.')
import lower_thirds as L
series = [(L.LowerThird(t, s, d), deb) for (_, t, s, deb, d, _) in L.SERIE]
L.rendre_piste(series, sys.argv[1])
# aperçu H.264 sur des images du film
fonds = {k: Image.open('../../images/%s.webp' % v).convert('RGBA') for k, v in
         {"10": "10", "9": "9", "11": "11"}.items()}
choix = ["11", "11", "10", "10", "9", "11", "10", "10", "9", "10", "9", "11"]
p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1920x1080",
                      "-r", "24", "-i", "-", "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
                      "-movflags", "+faststart", sys.argv[2]], stdin=subprocess.PIPE)
for (lt, _), k in zip(series, choix):
    for i in range(int(round((lt.duree + 0.4) * 24))):
        im = fonds[k].copy()
        t = i / 24
        if t < lt.duree:
            im.alpha_composite(lt.image(t))
        p.stdin.write(im.convert("RGB").tobytes())
p.stdin.close(); p.wait()
