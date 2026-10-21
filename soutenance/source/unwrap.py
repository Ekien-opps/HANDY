# Copy of a pptx where every mc:AlternateContent is replaced by its mc:Choice children, so the validator sees them
import zipfile, sys, re
from lxml import etree
MC='http://schemas.openxmlformats.org/markup-compatibility/2006'
src, dst, inject = sys.argv[1], sys.argv[2], len(sys.argv) > 3
zi = zipfile.ZipFile(src); zo = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for it in zi.infolist():
    b = zi.read(it.filename)
    if re.match(r'ppt/slides/slide\d+\.xml$', it.filename):
        t = etree.fromstring(b)
        for ac in t.iter(f'{{{MC}}}AlternateContent'):
            pass
        for ac in list(t.iter(f'{{{MC}}}AlternateContent')):
            ch = ac.find(f'{{{MC}}}Choice'); par = ac.getparent(); idx = par.index(ac)
            for k, c in enumerate(list(ch)):
                par.insert(idx + k, c)
            par.remove(ac)
        b = etree.tostring(t, xml_declaration=True, encoding='UTF-8', standalone=True)
        if inject and it.filename.endswith('slide14.xml'):
            b = b.replace(b'<am3d:objViewport', b'<am3d:bogus/><am3d:objViewport', 1).replace(b'option="byObject"', b'option="byNothing"')
    zo.writestr(it, b)
zo.close()
