"""Reopen and recompute the supplemental native CAD without saving source files."""
import hashlib
import json
from pathlib import Path
import zipfile
import FreeCAD as A
import FreeCADGui as G

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / 'exports/mounting-retrofit/validation.json').read_text())
assert report['passed'], 'Resolve geometry validation failures first'
path = ROOT / 'cad/assembly/MYMS_Mounting_Retrofit.FCStd'
with zipfile.ZipFile(path) as archive:
    assert 'GuiDocument.xml' in archive.namelist(), 'Missing FreeCAD view data'
G.showMainWindow()
doc = A.openDocument(str(path))
doc.recompute()
assert len(doc.Retrofit_Printed_Parts.Group) == 4
assert {obj.Name for obj in doc.Retrofit_Printed_Parts.Group} == {p['name'] for p in report['prints']}
assert {p.stem for p in (ROOT / 'exports/mounting-retrofit').glob('*.stl')} == {p['name'] for p in report['prints']}
for obj in doc.Retrofit_Printed_Parts.Group:
    assert obj.TypeId == 'PartDesign::Body' and obj.Tip is not None
    assert obj.Tip.Shape.isValid() and len(obj.Tip.Shape.Solids) == 1, obj.Name
assert doc.Retrofit_Printed_Parts.Visibility
assert doc.Base_Existing.Visibility
assert doc.PTC_Heater_Reference.Visibility and doc.Steel_Deflector_Reference.Visibility
for filename, digest in report['source_sha256'].items():
    assert hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == digest, filename
print('Native reopen/recompute, GUI opening visibility, 4 single-solid bodies and source preservation passed')
