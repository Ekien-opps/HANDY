#!/usr/bin/env bash
# Usage: tools/preview-scene.sh <frame_id> <duration_s> <comma-separated local times> [outdir]
# Mounts ONE scene alone in an isolated harness (black ground, like the final index) and snapshots it.
set -euo pipefail
PROJ="$(cd "$(dirname "$0")/.." && pwd)"
ID="$1"; DUR="$2"; AT="$3"
H="${TMPDIR:-/tmp}/hf-harness-$ID"
OUT="${4:-$PROJ/.hyperframes/previews/$ID}"
rm -rf "$H"; mkdir -p "$H/compositions" "$OUT"
ln -s "$PROJ/assets" "$H/assets"
cp "$PROJ/compositions/$ID.html" "$H/compositions/$ID.html"
cp "$PROJ/hyperframes.json" "$H/hyperframes.json"
cat > "$H/index.html" <<HTML
<!doctype html>
<html lang="fr"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="assets/vendor/gsap.min.js"></script>
<style>*{margin:0;padding:0;box-sizing:border-box}html,body{width:1920px;height:1080px;overflow:hidden;background:#000}#root{width:100%;height:100%;position:relative;overflow:hidden}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="$DUR" data-width="1920" data-height="1080">
<div id="slot-$ID" data-composition-id="$ID" data-composition-src="compositions/$ID.html" data-start="0" data-duration="$DUR" data-track-index="1" data-width="1920" data-height="1080"></div>
</div><script>const tl=gsap.timeline({paused:true});window.__timelines["main"]=tl;</script></body></html>
HTML
cd "$H"
echo "== lint (scene mounted alone) =="
npx hyperframes lint 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | tail -25 || true
echo "== snapshot =="
rm -rf "$OUT"/*
npx hyperframes snapshot --at "$AT" --no-end -o "$OUT" 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -vE "describe|GEMINI" | tail -4
python3 - "$OUT" <<'PY'
import sys,glob,os
from PIL import Image,ImageDraw
out=sys.argv[1]; fs=sorted(glob.glob(os.path.join(out,'frame-*.png')))
if fs:
    w,h=640,360; cols=3; rows=(len(fs)+cols-1)//cols
    sheet=Image.new('RGB',(cols*w,rows*(h+28)),(20,20,20)); d=ImageDraw.Draw(sheet)
    for i,f in enumerate(fs):
        im=Image.open(f).convert('RGB').resize((w,h)); x=(i%cols)*w; y=(i//cols)*(h+28)
        sheet.paste(im,(x,y+28)); d.text((x+8,y+6),os.path.basename(f),fill=(255,255,255))
    sheet.save(os.path.join(out,'sheet.jpg'),quality=82); print('SHEET:',os.path.join(out,'sheet.jpg'))
PY
