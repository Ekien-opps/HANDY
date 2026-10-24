"""Ajoute les animations du deck, règle unique :
fondu + glissement de 20 px vers le haut, 0,5 s, ease-out (décélération 100 %).
- titres (espaces réservés titre/surtitre/numéro, objets nommés T_*) : automatiques au début de la diapositive ;
- contenu (objets nommés C<n>_*) : au clic, un clic par groupe n ;
- vidéo (objet nommé V<n>_*) : apparaît au clic n puis se lance automatiquement.
Compatible PowerPoint 2019 (effets Fondu + trajectoire personnalisée, schéma PresentationML 2010)."""
import re, sys, zipfile, shutil, subprocess
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
P = '{%s}' % NS['p']
DUR = 500
DY = 20 / 720          # 20 px sur une diapositive de 1280 x 720 px (13,333 x 7,5 in à 96 ppp)
VIDEO_MS = {'anim_logo_web': 12032, 'spot2d_web': 26069}


class Ids:
    def __init__(self):
        self.n = 0

    def __call__(self):
        self.n += 1
        return self.n


def fade(ids, spid, node):
    return (f'<p:par><p:cTn id="{ids()}" presetID="10" presetClass="entr" presetSubtype="0" accel="0" decel="100000" '
            f'fill="hold" grpId="0" nodeType="{node}"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="{ids()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{ids()}" dur="{DUR}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:animEffect>'
            f'</p:childTnLst></p:cTn></p:par>')


def rise(ids, spid):
    return (f'<p:par><p:cTn id="{ids()}" presetID="0" presetClass="path" presetSubtype="0" accel="0" decel="100000" '
            f'fill="hold" grpId="1" nodeType="withEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            f'<p:animMotion origin="layout" path="M 0 {DY:.5f} L 0 0 E" pathEditMode="relative" rAng="0" ptsTypes="AA">'
            f'<p:cBhvr><p:cTn id="{ids()}" dur="{DUR}" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr>'
            f'</p:animMotion></p:childTnLst></p:cTn></p:par>')


def play(ids, spid, ms):
    return (f'<p:par><p:cTn id="{ids()}" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" '
            f'nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            f'<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="{ids()}" dur="{ms}" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd></p:childTnLst></p:cTn></p:par>')


def group(ids, spids, first, auto=False, after=''):
    outer = ids()
    cond = ('<p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>'
            if auto else '<p:cond delay="indefinite"/>')
    inner = ids()
    effects = ''
    for k, spid in enumerate(spids):
        effects += fade(ids, spid, first if k == 0 else 'withEffect') + rise(ids, spid)
    xml = (f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst>{cond}</p:stCondLst><p:childTnLst>'
           f'<p:par><p:cTn id="{inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst>'
           f'<p:childTnLst>{effects}</p:childTnLst></p:cTn></p:par>')
    if after:
        xml += (f'<p:par><p:cTn id="{ids()}" fill="hold"><p:stCondLst><p:cond delay="{DUR}"/></p:stCondLst>'
                f'<p:childTnLst>{after}</p:childTnLst></p:cTn></p:par>')
    return xml + '</p:childTnLst></p:cTn></p:par>'


def process(xml, rels):
    root = etree.fromstring(xml)
    tree = root.find('p:cSld/p:spTree', NS)
    auto, clicks, texty, videos = [], {}, set(), {}
    for el in tree:
        tag = etree.QName(el).localname
        if tag not in ('sp', 'pic', 'cxnSp', 'graphicFrame'):
            continue
        c = el.find('.//p:cNvPr', NS)
        spid, name = c.get('id'), c.get('name') or ''
        ph = el.find('./*/p:nvPr/p:ph', NS)
        if tag == 'sp' and el.find('p:txBody', NS) is not None:
            texty.add(spid)
        if ph is not None:
            if ph.get('type') in ('sldNum', 'ftr', 'dt'):
                continue
            auto.append(spid)
        elif name.startswith('T_'):
            auto.append(spid)
        elif re.match(r'C\d+_', name):
            clicks.setdefault(int(name[1:name.index('_')]), []).append(spid)
        elif re.match(r'V\d+_', name):
            n = int(name[1:name.index('_')])
            clicks.setdefault(n, []).append(spid)
            vf = el.find('.//a:videoFile', NS)
            target = rels.get(vf.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link'), '')
            ms = next((v for k, v in VIDEO_MS.items() if k in target), None)
            videos[n] = (spid, ms or 30000)
    if not auto and not clicks:
        return xml
    ids = Ids()
    ids(); ids()                       # 1 = tmRoot, 2 = mainSeq
    seq = ''
    if auto:
        seq += group(ids, auto, 'withEffect', auto=True)
    for n in sorted(clicks):
        after = play(ids, *videos[n]) if n in videos else ''
        seq += group(ids, clicks[n], 'clickEffect', after=after)
    media = ''
    for n, (spid, _) in videos.items():
        media += (f'<p:video><p:cMediaNode vol="80000"><p:cTn id="{ids()}" fill="hold" display="0">'
                  f'<p:stCondLst><p:cond delay="indefinite"/></p:stCondLst></p:cTn>'
                  f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>')
    animated = auto + [s for n in sorted(clicks) for s in clicks[n]]
    bld = ''.join(f'<p:bldP spid="{s}" grpId="{g}" animBg="1"/>' for s in animated if s in texty for g in (0, 1))
    timing = (f'<p:timing xmlns:p="{NS["p"]}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">'
              f'<p:childTnLst><p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq">'
              f'<p:childTnLst>{seq}</p:childTnLst></p:cTn>'
              f'<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
              f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
              f'</p:seq>{media}</p:childTnLst></p:cTn></p:par></p:tnLst>'
              + (f'<p:bldLst>{bld}</p:bldLst>' if bld else '') + '</p:timing>')
    old = root.find('p:timing', NS)
    if old is not None:
        root.remove(old)
    node = etree.fromstring(timing)
    anchor = root.find('p:transition', NS)
    if anchor is None:
        anchor = root.find('p:clrMapOvr', NS)
    anchor.addnext(node)
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


zin = zipfile.ZipFile(SRC)
zout = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
stats = []
for item in zin.infolist():
    data = zin.read(item.filename)
    m = re.match(r'ppt/slides/slide(\d+)\.xml$', item.filename)
    if m:
        rels_xml = zin.read(f'ppt/slides/_rels/slide{m.group(1)}.xml.rels')
        rels = {r.get('Id'): r.get('Target') for r in etree.fromstring(rels_xml)}
        data = process(data, rels)
        stats.append((int(m.group(1)), data.count(b'clickEffect'), data.count(b'mediacall')))
    zout.writestr(item, data, compress_type=zipfile.ZIP_STORED if item.filename.endswith('.mp4') else zipfile.ZIP_DEFLATED)
zout.close()
print('clics par diapositive :', ' '.join(f'{n}:{c}{"+lecture" if v else ""}' for n, c, v in sorted(stats)))
