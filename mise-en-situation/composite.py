import sys
import numpy as np
import cv2
from PIL import Image

scene_path, poster_path, out_path = sys.argv[1:4]
SS = 4  # supersampling factor for clean anti-aliased edges

scene = np.array(Image.open(scene_path).convert("RGB")).astype(np.float32) / 255.0
H, W = scene.shape[:2]

# Poster: keep only the opaque framed board (drop the mockup's grey side shadow)
p = np.array(Image.open(poster_path).convert("RGBA"))
x0, x1 = 102, 1639
poster = p[:, x0:x1, :3].astype(np.float32) / 255.0
ph, pw = poster.shape[:2]

# --- Tone match to the sunlit scene ---------------------------------------
# lift blacks slightly (daylight haze / reflection), open whites, warm tint
lo, hi = 0.0, 0.925
poster = np.clip((poster - lo) / (hi - lo), 0, 1)
poster = 0.035 + poster * (0.985 - 0.035)
poster = poster ** 1.04
# warm cast of the scene light
poster *= np.array([1.02, 1.0, 0.965], dtype=np.float32)
# very slight desaturation (print on vinyl, viewed from distance)
gray = poster.mean(axis=2, keepdims=True)
poster = gray + (poster - gray) * 0.94
# sunlight falloff: brighter top-left, a touch darker bottom-right
yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
grad = 1.035 - 0.07 * (0.55 * xx / pw + 0.45 * yy / ph)
poster *= grad[..., None]
# soft specular sheen band from the top-left (glossy vinyl)
d = (xx / pw * 0.8 + yy / ph * 0.6)
sheen = np.exp(-((d - 0.35) ** 2) / (2 * 0.12 ** 2)) * 0.035
poster = poster + sheen[..., None] * (1 - poster)
poster = np.clip(poster, 0, 1)

# --- Destination corners (outer edge of existing billboard face) ----------
dst = np.array([
    [501.5, 216.8],  # TL
    [915.3, 217.0],  # TR
    [914.3, 510.9],  # BR
    [501.5, 512.0],  # BL
], dtype=np.float32)
src = np.array([[0, 0], [pw, 0], [pw, ph], [0, ph]], dtype=np.float32)

M = cv2.getPerspectiveTransform(src, dst * SS)
big = (W * SS, H * SS)
warped = cv2.warpPerspective(poster, M, big, flags=cv2.INTER_CUBIC,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=0)
mask = cv2.warpPerspective(np.ones((ph, pw), np.float32), M, big,
                           flags=cv2.INTER_LINEAR, borderValue=0)
# premultiplied downsample -> anti-aliased edges
warped = cv2.resize(warped * mask[..., None], (W, H), interpolation=cv2.INTER_AREA)
mask = cv2.resize(mask, (W, H), interpolation=cv2.INTER_AREA)
color = np.where(mask[..., None] > 1e-4, warped / np.maximum(mask[..., None], 1e-4), 0)

# match scene softness: tiny blur, then a gentle unsharp like the photo
color = cv2.GaussianBlur(color, (0, 0), 0.45)
blur = cv2.GaussianBlur(color, (0, 0), 1.2)
color = np.clip(color + 0.25 * (color - blur), 0, 1)

# grain matching the photo
rng = np.random.default_rng(7)
noise = rng.normal(0, 0.008, (H, W, 1)).astype(np.float32)
color = np.clip(color + noise, 0, 1)

# subtle ambient occlusion just inside the frame edge
inner = cv2.erode((mask > 0.99).astype(np.float32), np.ones((3, 3), np.uint8), iterations=2)
ao = 1 - 0.06 * (1 - cv2.GaussianBlur(inner, (0, 0), 1.5))
color *= ao[..., None]

out = scene * (1 - mask[..., None]) + color * mask[..., None]
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(out_path)
print("saved", out_path)
