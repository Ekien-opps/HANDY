import zipfile, re, posixpath, sys
from lxml import etree
z = zipfile.ZipFile(sys.argv[1]); problems = 0
def bad(*a):
    global problems; problems += 1; print(*a)
names = set(z.namelist())
if z.testzip(): bad('CRC error')
for n in names:
    if n.endswith('/'): bad('DIR ENTRY', n)
if z.infolist()[0].filename != '[Content_Types].xml': bad('Content_Types not first')
ct = etree.fromstring(z.read('[Content_Types].xml'))
defaults = {e.get('Extension').lower(): e.get('ContentType') for e in ct if e.tag.endswith('Default')}
over = {e.get('PartName'): e.get('ContentType') for e in ct if e.tag.endswith('Override')}
for n in names:
    if n.endswith('/'): continue
    if '/' + n not in over and n.rsplit('.', 1)[-1].lower() not in defaults: bad('NO CONTENT TYPE', n)
for p in over:
    if p[1:] not in names: bad('OVERRIDE MISSING PART', p)
for k, v in defaults.items():
    if v == 'image/jpg': bad('NONSTANDARD TYPE', k, v)
for n in sorted(names):
    if n.endswith('.rels'):
        base = posixpath.dirname(posixpath.dirname(n))
        for r in etree.fromstring(z.read(n)):
            if r.get('TargetMode') == 'External': continue
            t = r.get('Target'); t = t[1:] if t.startswith('/') else posixpath.normpath(posixpath.join(base, t))
            if t not in names: bad('BROKEN REL', n, r.get('Target'))
    if re.match(r'ppt/(slides|slideLayouts|slideMasters|notesSlides|notesMasters)/[^/]+\.xml$', n):
        x = z.read(n).decode()
        ids = re.findall(r'<p:cNvPr id="(\d+)"', x)
        d = sorted({i for i in ids if ids.count(i) > 1})
        if d: bad('DUP IDS', n, d)
        sp = set(re.findall(r'spTgt spid="(\d+)"', x))
        if sp - set(ids): bad('MISSING SPID', n, sp - set(ids))
        t = re.findall(r'<p:cTn id="(\d+)"', x)
        if len(t) != len(set(t)): bad('DUP CTN', n)
        b = re.findall(r'<p:bldP spid="(\d+)" grpId="(\d+)"', x)
        if len(b) != len(set(b)): bad('DUP BLDP', n)
print('problèmes :', problems)
