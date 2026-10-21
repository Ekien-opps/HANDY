import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import count_lines
log = json.load(open('out/textlog.json'))
per = {}
for sn, name, paras, w, row in log:
    if sn is None or row == 'chrome':
        continue
    n = count_lines(paras, w)
    key = row or name
    d = per.setdefault(sn, {})
    d[key] = max(d.get(key, 0), n)
bad = 0
for sn in sorted(per):
    tot = sum(per[sn].values())
    flag = '  <-- TROP' if tot > 6 else ''
    bad += tot > 6
    if flag or '-v' in sys.argv:
        print(sn, tot, per[sn], flag)
print('slides > 6 lignes :', bad, '| max :', max(sum(v.values()) for v in per.values()))
