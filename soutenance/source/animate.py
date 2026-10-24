"""Applique la règle d'animation unique à tout le deck.

Effet : apparition en fondu + glissement de 20 px vers le haut, 0,5 s, ease-out
(décélération 100 %), construit sur l'effet d'entrée natif « Élever » (Ascend,
presetID 42) — lisible et modifiable dans PowerPoint 2019.

Déclenchement :
  - titre (placeholder title/ctrTitle) et objets nommés "t_*" : automatique à l'ouverture de la diapositive ;
  - objets nommés "cN_*" : au clic N (tous les objets d'un même N apparaissent ensemble) ;
  - autres objets : statiques.

Usage : python animate.py entree.pptx sortie.pptx
"""
import re
import sys
import zipfile
from collections import OrderedDict

from lxml import etree

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}
SLIDE_H_PX = 720  # 7,5 po à 96 ppp
DY = f"{20 / SLIDE_H_PX:.4f}".rstrip("0")  # 20 px -> fraction de la hauteur de diapositive
DUR = 500


class Ids:
    def __init__(self):
        self.n = 2

    def next(self):
        self.n += 1
        return self.n


def effect(ids, spid, node_type):
    tgt = f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
    return (
        f'<p:par><p:cTn id="{ids.next()}" presetID="42" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="{node_type}">'
        '<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        f'<p:set><p:cBhvr><p:cTn id="{ids.next()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>{tgt}'
        '<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
        f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{ids.next()}" dur="{DUR}"/>{tgt}</p:cBhvr></p:animEffect>'
        f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{ids.next()}" dur="{DUR}" decel="100000" fill="hold"/>{tgt}'
        '<p:attrNameLst><p:attrName>ppt_x</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
        '<p:tav tm="0"><p:val><p:strVal val="#ppt_x"/></p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="#ppt_x"/></p:val></p:tav>'
        '</p:tavLst></p:anim>'
        f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{ids.next()}" dur="{DUR}" decel="100000" fill="hold"/>{tgt}'
        '<p:attrNameLst><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
        f'<p:tav tm="0"><p:val><p:strVal val="#ppt_y+{DY}"/></p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="#ppt_y"/></p:val></p:tav>'
        '</p:tavLst></p:anim>'
        '</p:childTnLst></p:cTn></p:par>'
    )


def group(ids, spids, first_type, auto):
    if auto:
        cond = '<p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>'
    else:
        cond = '<p:cond delay="indefinite"/>'
    outer, inner = ids.next(), ids.next()
    effects = "".join(effect(ids, sp, first_type if i == 0 else "withEffect") for i, sp in enumerate(spids))
    return (
        f'<p:par><p:cTn id="{outer}" fill="hold"><p:stCondLst>{cond}</p:stCondLst><p:childTnLst>'
        f'<p:par><p:cTn id="{inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
        f"{effects}</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>"
    )


def build_timing(xml):
    root = etree.fromstring(xml)
    tree = root.find("p:cSld/p:spTree", NS)
    auto, clicks, bld = [], {}, []
    for el in tree:
        tag = etree.QName(el).localname
        if tag not in ("sp", "pic", "graphicFrame", "grpSp", "cxnSp"):
            continue
        c = el.find(".//p:cNvPr", NS)
        spid, name = c.get("id"), c.get("name") or ""
        ph = el.find(".//p:nvPr/p:ph", NS)
        is_title = ph is not None and ph.get("type") in ("title", "ctrTitle")
        if is_title or name.startswith("t_") or (ph is not None and ph.get("type") == "body"):
            auto.append(spid)
        else:
            m = re.match(r"c(\d+)_", name)
            if not m:
                continue
            clicks.setdefault(int(m.group(1)), []).append(spid)
        if tag == "sp":
            has_text = bool("".join(el.itertext()).strip())
            bld.append(f'<p:bldP spid="{spid}" grpId="0"/>' if has_text else f'<p:bldP spid="{spid}" grpId="0" animBg="1"/>')
        elif tag == "graphicFrame":
            bld.append(f'<p:bldGraphic spid="{spid}" grpId="0"><p:bldAsOne/></p:bldGraphic>')
    if not auto and not clicks:
        return None, 0, 0
    ids = Ids()
    seq = ""
    if auto:
        seq += group(ids, auto, "afterEffect", True)
    for k in sorted(clicks):
        seq += group(ids, clicks[k], "clickEffect", False)
    timing = (
        '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
        '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
        f"{seq}</p:childTnLst></p:cTn>"
        '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
        '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst>'
        "</p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>"
        f'{"<p:bldLst>" + "".join(bld) + "</p:bldLst>" if bld else ""}</p:timing>'
    )
    return timing, len(auto), len(clicks)


def main(src, dst):
    zin = zipfile.ZipFile(src)
    out = OrderedDict()
    report = []
    for info in zin.infolist():
        data = zin.read(info.filename)
        m = re.match(r"ppt/slides/slide(\d+)\.xml$", info.filename)
        if m:
            xml = data.decode("utf-8")
            assert "<p:timing" not in xml, info.filename
            timing, na, nc = build_timing(data)
            if timing:
                if "</p:clrMapOvr>" in xml:
                    xml = xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + timing, 1)
                else:
                    xml = xml.replace("</p:cSld>", "</p:cSld>" + timing, 1)
                data = xml.encode("utf-8")
            report.append((int(m.group(1)), na, nc))
        out[info] = data
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in out.items():
            zout.writestr(info, data)
    for n, na, nc in sorted(report):
        print(f"diapo {n:2d} : {na} objet(s) auto, {nc} clic(s)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
