import sys, io, re, zipfile, shutil
import pymupdf
from pdf2docx import Converter
src, out, tmp = sys.argv[1], sys.argv[2], sys.argv[3]
RASTER = [0, 2, 81, 100]      # couverture, page de titre, p. 70 (captures), 4e de couverture (0-based)
SHRINK = {34: 0.95, 51: 0.95}   # pages dont le pied de page déborde une fois converties
doc = pymupdf.open(src)
new = pymupdf.open()
for i, pg in enumerate(doc):
    if i in RASTER:
        pix = pg.get_pixmap(dpi=200)
        np_ = new.new_page(width=pg.rect.width, height=pg.rect.height)
        np_.insert_image(np_.rect, stream=pix.tobytes('jpeg', jpg_quality=88))
    elif i in SHRINK:
        f = SHRINK[i]
        np_ = new.new_page(width=pg.rect.width, height=pg.rect.height)
        r = pg.rect
        np_.show_pdf_page(pymupdf.Rect(r.width * (1 - f) / 2, 0, r.width * (1 + f) / 2, r.height * f), doc, i)
    else:
        new.insert_pdf(doc, from_page=i, to_page=i)
new.save(tmp + '/pre.pdf', garbage=3, deflate=True)
cv = Converter(tmp + '/pre.pdf')
cv.convert(tmp + '/raw.docx', multi_processing=False)
cv.close()
# noms de polices propres pour Word
FIX = {'Times New Roman,Bold': 'Times New Roman', 'Times New Roman,Italic': 'Times New Roman',
       'Times New Roman,BoldItalic': 'Times New Roman', 'Liberation Serif': 'Times New Roman',
       'Liberation Sans': 'Arial', 'Arial,Bold': 'Arial', 'Arial,BoldItalic': 'Arial',
       'Arial,Italic': 'Arial', 'Calibri,BoldItalic': 'Calibri', 'Calibri,Bold': 'Calibri'}
zin = zipfile.ZipFile(tmp + '/raw.docx')
zout = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
for item in zin.infolist():
    data = zin.read(item.filename)
    if item.filename.endswith('.xml'):
        s = data.decode('utf-8')
        s = re.sub(r'w:(ascii|hAnsi|cs|eastAsia)="([^"]+)"',
                   lambda m: 'w:%s="%s"' % (m.group(1), FIX.get(m.group(2), m.group(2).split(',')[0])), s)
        data = s.encode('utf-8')
    zout.writestr(item, data)
zout.close()
