#!/usr/bin/env bash
# Export every key frame listed in keyframes.tsv (scene, local time, file stem, title) with QA.
cd "$(dirname "$0")/../.."
ONLY="${1:-}"
while IFS=$'\t' read -r sc t name title; do
  [ -n "$ONLY" ] && [[ "$name" != *"$ONLY"* ]] && continue
  node tools/svg-export/export.mjs --scene "$sc" --time "$t" --out "exports/svg/$name.svg" --title "$title" --qa < /dev/null 2>&1 | python3 -c "
import sys,json
for l in sys.stdin:
  try: o=json.loads(l)
  except: print('  !', l.strip()[:300]); continue
  if 'qa' in o: print('   QA diff', o['qa']['meanAbsDiff'], '| pixels off', o['qa']['pctPixelsOff'],'%')
  else: print('$name', o['kb'],'KB', o['stats'], 'PAGE-ERR '+str(o['pageErrors']) if o['pageErrors'] else '')
"
done < tools/svg-export/keyframes.tsv
