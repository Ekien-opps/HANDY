using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Validation;
using DocumentFormat.OpenXml;
using System.Text.RegularExpressions;
var v = new OpenXmlValidator(FileFormatVersions.Microsoft365);
if (args.Length > 1 && args[1] == "m3d") {
  // validate every am3d:model3d element against the typed Office 2019 schema
  using var doc = PresentationDocument.Open(args[0], false);
  int n = 0, errs = 0;
  string ns = "xmlns:am3d=\"http://schemas.microsoft.com/office/drawing/2017/model3d\" xmlns:a=\"http://schemas.openxmlformats.org/drawingml/2006/main\" xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\"";
  foreach (var sp in doc.PresentationPart.SlideParts) {
    string xml; using (var sr = new StreamReader(sp.GetStream())) xml = sr.ReadToEnd();
    foreach (Match m in Regex.Matches(xml, "<am3d:model3d .*?</am3d:model3d>", RegexOptions.Singleline)) {
      n++;
      var s = m.Value.Replace("<am3d:model3d ", "<am3d:model3d " + ns + " ");
      var el = new DocumentFormat.OpenXml.Office2019.Drawing.Model3D.Model3D(s);
      foreach (var e in v.Validate(el)) { errs++; if (errs < 20) Console.WriteLine($"{sp.Uri} | {e.Path?.XPath} | {e.Description}"); }
      // also check that every child was recognised (no unknown elements)
      foreach (var d in el.Descendants()) if (d is OpenXmlUnknownElement) { errs++; if (errs < 20) Console.WriteLine($"{sp.Uri} | UNKNOWN {d.LocalName}"); }
    }
  }
  Console.WriteLine($"MODEL3D elements: {n}, errors: {errs}");
  return;
}
using var pdoc = PresentationDocument.Open(args[0], false);
int c = 0;
foreach (var e in v.Validate(pdoc)) { c++; if (c <= 60) Console.WriteLine($"{e.ErrorType} | {e.Part?.Uri} | {e.Path?.XPath} | {e.Description}"); }
Console.WriteLine($"TOTAL ERRORS: {c}");
