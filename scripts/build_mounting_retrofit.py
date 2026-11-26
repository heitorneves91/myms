"""Build supplemental native CAD without regenerating any already printed part.

Run with bash scripts/build_mounting_retrofit.sh (FreeCAD AppImage + GUI).
All dimensions mm. This is a fit prototype, not a thermally validated assembly.
"""
import hashlib
import itertools
import json
import math
from pathlib import Path

import FreeCAD as A
import FreeCADGui as G
import MeshPart
import Part
import Sketcher

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'cad/mounting_retrofit.json').read_text())
# Profiles below deliberately match this particular printed shell and stock
# spacer stack. Reject unsupported edits instead of silently ignoring a value.
for key, expected in {
    'floor_z': 3, 'adapter_base_thickness': 6, 'heater_plate_x': 82,
    'heater_plate_thickness': 6, 'heater_spacer_length': 20,
    'cup_center_y': 75, 'cup_center_z': 65, 'cup_spacer_length': 20,
    'cup_contact_head_height': 2, 'cup_contact_washer_thickness': .8,
    'cup_contact_washer_od': 9, 'cup_contact_head_od': 6, 'cup_cap_thickness': 4,
    'heater_base_width': 26,
}.items():
    assert P[key] == expected, f'{key}: update the layout/profile code and checks for a different hardware stack'
OUT = ROOT / 'exports/mounting-retrofit'
OUT.mkdir(parents=True, exist_ok=True)
V = A.Vector
YZ = A.Rotation(V(1, 1, 1), 120)  # sketch X/Y -> world Y/Z; extrusion -> world X
CR = P['clearance_diameter'] / 2
IR = P['insert_diameter'] / 2
SOURCE = ROOT / P['source']
ORIGINAL = ROOT / 'cad/assembly/Hardware_References.FCStd'
before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE, ORIGINAL)}
G.showMainWindow()
source = A.openDocument(str(SOURCE))
doc = A.newDocument('MYMS_Mounting_Retrofit')
old = doc.addObject('App::Part', 'Existing_Printed_Assembly')
old.Label = 'EXISTING PRINTS - unchanged reference copies'
new = doc.addObject('App::Part', 'Retrofit_Printed_Parts')
hardware = doc.addObject('App::Part', 'Purchased_Hardware_References')
refs = doc.addObject('App::Part', 'Existing_Heater_And_Deflector')
printed, pads, fasteners, snapshots = [], [], [], []
checks = []


def reference(group, name, shape, color, note=''):
    obj = doc.addObject('PartDesign::Feature', name)
    group.addObject(obj)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    obj.addProperty('App::PropertyString', 'Status').Status = note
    return obj


for body in source.Printed_Assembly.Group:
    if body.TypeId != 'PartDesign::Body':
        continue
    shape = body.Shape.copy()
    shape.Placement = body.getGlobalPlacement()
    obj = reference(old, body.Name + '_Existing', shape, (.77, .79, .80), 'Already printed; do not reprint')
    snapshots.append((body, obj))
for name in ('PTC_Heater_Reference', 'Steel_Deflector_Reference', 'Spool_Envelope_UNMEASURED'):
    body = source.getObject(name)
    shape = body.Shape.copy()
    shape.Placement = body.getGlobalPlacement()
    if name == 'Steel_Deflector_Reference':
        shape.translate(V(P['cup_shift_x'], 0, 0))
    obj = reference(refs, name, shape, (.24, .26, .28) if name.startswith('PTC') else (.62, .65, .68),
                    'Purchased hardware' if name != 'Spool_Envelope_UNMEASURED' else 'Existing assumed spool envelope')
    if name == 'Spool_Envelope_UNMEASURED':
        obj.ViewObject.ShapeColor = (.85, .48, .22)
        obj.ViewObject.Transparency = 65


params = doc.addObject('Spreadsheet::Sheet', 'Retrofit_Parameters')
for row, (key, value) in enumerate(P.items(), 1):
    params.set('A' + str(row), key)
    params.set('B' + str(row), str(value))
params.addProperty('App::PropertyString', 'Note').Note = 'Informational; regenerate from cad/mounting_retrofit.json'


def polygon(points):
    return [Part.LineSegment(V(*a, 0), V(*b, 0)) for a, b in zip(points, points[1:] + points[:1])]


def rectangle(x, y, w, h):
    return polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def circles(points, r):
    return [Part.Circle(V(x, y, 0), V(0, 0, 1), r) for x, y in points]


def body(name):
    obj = doc.addObject('PartDesign::Body', name)
    new.addObject(obj)
    obj.addProperty('App::PropertyString', 'ReleaseStatus').ReleaseStatus = P['status']
    printed.append(obj)
    return obj


def sketch(obj, name, geoms, placement):
    sk = doc.addObject('Sketcher::SketchObject', obj.Name + '_' + name + '_Profile')
    obj.addObject(sk)
    sk.Placement = placement
    for geom in geoms:
        index = sk.addGeometry(geom, False)
        sk.addConstraint(Sketcher.Constraint('Block', index))
    return sk


def feature(obj, name, geoms, placement, length, pocket=False):
    sk = sketch(obj, name, geoms, placement)
    f = obj.newObject('PartDesign::Pocket' if pocket else 'PartDesign::Pad', obj.Name + '_' + name)
    f.Profile = sk
    f.Length = length
    doc.recompute()
    for child in obj.Group:
        child.Visibility = child == f
    assert not f.Shape.isNull(), (obj.Name, name, 'Empty feature')
    return f


def xy(z):
    return A.Placement(V(0, 0, z), A.Rotation())


def yz(x):
    return A.Placement(V(x, 0, 0), YZ)


def drill(obj, name, point, direction, length, radius=CR):
    # Pocket cuts opposite the sketch normal.
    rotation = A.Rotation(V(0, 0, 1), -V(*direction))
    return feature(obj, name, circles([(0, 0)], radius), A.Placement(V(*point), rotation), length, True)


def countersink(obj, name, x, y, top, radius=3.2):
    first = sketch(obj, name + '_Top', circles([(x, y)], radius), xy(top))
    second = sketch(obj, name + '_Bottom', circles([(x, y)], CR), xy(top - (radius - CR)))
    f = obj.newObject('PartDesign::SubtractiveLoft', obj.Name + '_' + name)
    f.Profile = first
    f.Sections = [second]
    f.Ruled = True
    doc.recompute()
    for child in obj.Group:
        child.Visibility = child == f


def fixture(name, shape, note='Illustrative fastener envelope; confirm purchased dimensions'):
    obj = reference(hardware, name, shape, (.46, .49, .52), note)
    fasteners.append(obj)
    return obj


def spacer(name, start, axis, length=20):
    start, axis = V(*start), V(*axis)
    af = P['spacer_hex_across_flats']
    radius = af / math.sqrt(3)
    points = [V(radius * math.cos(i * math.pi / 3), radius * math.sin(i * math.pi / 3), 0) for i in range(6)]
    shape = Part.Face(Part.makePolygon(points + [points[0]])).extrude(V(0, 0, length))
    shape = shape.cut(Part.makeCylinder(1.25, length, V(), V(0, 0, 1)))
    shape.Placement = A.Placement(start, A.Rotation(V(0, 0, 1), axis))
    return reference(hardware, name, shape, (.66, .46, .28),
                     'BUY PEEK M3 female/female, 20 mm long, 6 mm AF; not printable ABS; thermal verification pending')


def screw(name, point, axis, length, head_r=3, head_h=3, countersunk=False):
    p, n = V(*point), V(*axis)
    shape = Part.makeCylinder(1.5, length, p, n)
    head = (Part.makeCone(head_r, 1.5, head_h, p, n) if countersunk else
            Part.makeCylinder(head_r, head_h, p - n * head_h, n))
    return fixture(name, shape.fuse(head))


def washer(name, point, axis, outer=3.5, thick=.5):
    p, n = V(*point), V(*axis)
    return fixture(name, Part.makeCylinder(outer, thick, p, n).cut(Part.makeCylinder(1.6, thick, p, n)))


def locknut(name, point, axis):
    radius = 5.5 / math.sqrt(3)
    vertices = [V(radius * math.cos(i * math.pi / 3), radius * math.sin(i * math.pi / 3), 0) for i in range(6)]
    shape = Part.Face(Part.makePolygon(vertices + [vertices[0]])).extrude(V(0, 0, 4))
    shape = shape.cut(Part.makeCylinder(1.6, 4))
    shape.Placement = A.Placement(V(*point), A.Rotation(V(0, 0, 1), V(*axis)))
    return fixture(name, shape, 'Illustrative M3 locknut: 5.5 AF, 4 mm high; verify actual hardware')


# One-piece heater supports: broad outer X=88 face is continuous with the
# mast, so both the heel and upright print from that same bed face.
# Existing tab front faces X=62; PEEK X=62..82. Cup moves +15 mm.
for label, base_y, y0, profile in (
    ('Lower', 21, 12, [(35, 9), (47, 9), (47, 21), (57, 21), (57, 33), (35, 33)]),
    ('Upper', 129, 104, [(107, 9), (119, 9), (119, 109), (93, 109), (93, 97), (107, 97)]),
):
    hole_y, hole_z = (51, 27) if label == 'Lower' else (99, 103)
    support = body('PTC_' + label + '_Support')
    feature(support, 'Integrated_Base', rectangle(62, y0, P['heater_base_width'],
            38 if label == 'Lower' else 34), xy(3), 6)
    feature(support, 'Integrated_Mast', polygon(profile), yz(P['heater_plate_x']), P['heater_plate_thickness'])
    feature(support, 'Existing_Base_Holes', circles([(68, base_y), (78, base_y)], CR), xy(9), 6, True)
    drill(support, 'PEEK_Cold_Attachment', (82, hole_y, hole_z), (1, 0, 0), 6)
    spacer('Heater_' + label + '_PEEK_20', (62, hole_y, hole_z), (1, 0, 0))
    washer('Heater_' + label + '_Cold_Washer', (88, hole_y, hole_z), (1, 0, 0))
    screw('Heater_' + label + '_Cold_M3x10', (88.5, hole_y, hole_z), (-1, 0, 0), 10)
    washer('Heater_' + label + '_Hot_Washer', (57, hole_y, hole_z), (1, 0, 0))
    screw('Heater_' + label + '_Hot_M3x10', (57, hole_y, hole_z), (1, 0, 0), 10)

# Cup: two three-point PEEK cradles. Hot-end screws/large washers are small stock
# contact pads; no fabricated band and no long screw bridging PEEK to ABS.
R = P['cup_body_radius']
contact_stack = P['cup_contact_head_height'] + P['cup_contact_washer_thickness']
mount_r = R + P['cup_spacer_length'] + contact_stack
cap_z = P['cup_center_z'] + mount_r
for x in P['cup_stations_x']:
    name = 'Cup_' + str(int(x))
    frame = body(name + '_Cradle')
    frame_x = x - P['cup_frame_thickness'] / 2
    feature(frame, 'Open_Frame', polygon([(18, 3), (132, 3), (132, cap_z), (126, cap_z),
                                         (126, 9), (24, 9), (24, cap_z), (18, cap_z)]),
            yz(frame_x), P['cup_frame_thickness'])
    for sign, side in ((-1, 'Front'), (1, 'Rear')):
        u = V(0, -sign / math.sqrt(2), 1 / math.sqrt(2))  # toward cup center
        outward = -u
        b = V(x, 75, 65) + outward * mount_r
        tangent = V(0, u.z, -u.y)
        points = []
        for p in (b + tangent * 8, b - tangent * 8, b - tangent * 8 - u * 8, b + tangent * 8 - u * 8):
            points.append((p.y, p.z))
        feature(frame, side + '_Pad_Seat', polygon(points), yz(frame_x), P['cup_frame_thickness'])
        drill(frame, side + '_Cold_Clearance', tuple(b + u * .1), tuple(-u), 20)
        # Relieve the upright beside the angled PEEK end and expose the cold
        # washer/head below the diagonal seat. Without these pockets the union
        # of base and upright obstructs insertion and tool access.
        drill(frame, side + '_PEEK_End_Relief', tuple(b + u * 5), tuple(-u), 5, 3.7)
        drill(frame, side + '_Cold_Head_Access', tuple(b - u * 8), tuple(-u), 20, 3.7)
        rod = spacer(name + '_' + side + '_PEEK_20', tuple(b), tuple(u))
        end = b + u * 20
        washer(name + '_' + side + '_Contact_Washer', tuple(end), tuple(u), 4.5, .8)
        screw(name + '_' + side + '_Contact_M3x6', tuple(end + u * .8), tuple(-u), 6, 3, 2)
        washer(name + '_' + side + '_Cold_Washer', tuple(b - u * 8.5), tuple(u))
        screw(name + '_' + side + '_Cold_M3x12', tuple(b - u * 8.5), tuple(u), 12)
        pads.append((b, u))
    feature(frame, 'Existing_Base_Holes', circles([(x, 61), (x, 89)], CR), xy(9), 6, True)
    feature(frame, 'Integrated_Bridge', rectangle(frame_x, 18, P['cup_frame_thickness'], 114), xy(cap_z), P['cup_cap_thickness'])
    feature(frame, 'Top_Cold_Clearance', circles([(x, 75)], CR), xy(cap_z + 4), 4, True)
    countersink(frame, 'Cold_Screw_Countersink', x, 75, cap_z + 4)
    top = V(x, 75, cap_z)
    spacer(name + '_Top_PEEK_20', tuple(top), (0, 0, -1))
    end = top + V(0, 0, -20)
    washer(name + '_Top_Contact_Washer', tuple(end), (0, 0, -1), 4.5, .8)
    screw(name + '_Top_Contact_M3x6', tuple(end + V(0, 0, -.8)), (0, 0, 1), 6, 3, 2)
    screw(name + '_Top_Cold_M3x8_CS', (x, 75, cap_z + 4), (0, 0, -1), 8, 3, 1.5, True)


# Existing base attachment fasteners, to expose their clearance in the review.
base_points = [(68,21), (78,21), (68,129), (78,129), (113,61), (113,89), (183,61), (183,89)]
for i, (x, y) in enumerate(base_points):
    screw('Base_M3x25_' + str(i), (x, y, -7.5), (0, 0, 1), 25)
    washer('Base_Lower_Washer_' + str(i), (x, y, -7.5), (0, 0, 1))
    washer('Base_Upper_Washer_' + str(i), (x, y, 9), (0, 0, 1))
    locknut('Base_Locknut_' + str(i), (x, y, 9.5), (0, 0, 1))


def check(name, condition, **data):
    checks.append(dict(name=name, passed=bool(condition), **data))


def intersection(a, b):
    # Cheap bounding box rejection before BRep operations.
    if not a.BoundBox.intersect(b.BoundBox):
        return 0
    return a.common(b).Volume


doc.recompute()
for original, copy in snapshots:
    check('Preserved_' + original.Name, abs(original.Shape.Volume - copy.Shape.Volume) < 1e-6,
          source_volume=original.Shape.Volume, snapshot_volume=copy.Shape.Volume)
for obj in printed:
    shape = obj.Shape
    check('Valid_' + obj.Name, shape.isValid() and len(shape.Solids) == 1,
          solids=len(shape.Solids), volume=shape.Volume)
    for child in obj.Group:
        child.Visibility = child == obj.Tip
    obj.ViewObject.ShapeColor = (.25, .60, .67)
    obj.Tip.ViewObject.ShapeColor = (.25, .60, .67)
    for original, copy in snapshots:
        vol = intersection(shape, copy.Shape)
        check('Existing_clear_' + obj.Name + '_' + original.Name, vol < 1e-5, overlap_mm3=vol)
    for existing in refs.Group:
        vol = intersection(shape, existing.Shape)
        check('Hardware_clear_' + obj.Name + '_' + existing.Name, vol < 1e-5, overlap_mm3=vol,
              separation_mm=shape.distToShape(existing.Shape)[0])
for a, b in itertools.combinations(printed, 2):
    vol = intersection(a.Shape, b.Shape)
    check('New_parts_clear_' + a.Name + '_' + b.Name, vol < 1e-5, overlap_mm3=vol)
for item in hardware.Group:
    for obj in printed:
        vol = intersection(item.Shape, obj.Shape)
        check('Stock_clear_' + item.Name + '_' + obj.Name, vol < 1e-5, overlap_mm3=vol)
    for existing in refs.Group:
        vol = intersection(item.Shape, existing.Shape)
        check('Stock_hardware_clear_' + item.Name + '_' + existing.Name, vol < 1e-5,
              overlap_mm3=vol, separation_mm=item.Shape.distToShape(existing.Shape)[0])
# Each existing floor hole and its adapter share a void for the M3 shank.
for x, y in base_points:
    probe = Part.makeCylinder(CR - .05, 16, V(x, y, -7), V(0,0,1))
    for obj in [doc.Base_Existing] + printed:
        check('Base_axis_' + str(x) + '_' + str(y) + '_' + obj.Name,
              intersection(probe, obj.Shape) < 1e-5)
check('Heater_screw_metal_gap', 20 - (10 - 6.5) - (10 - 5) > 0, gap_mm=11.5)
check('Cup_bottom_screw_metal_gap', 20 - (12 - 8.5) - (6 - .8) > 0, gap_mm=11.3)
check('Cup_top_screw_metal_gap', 20 - (8 - 4) - (6 - .8) > 0, gap_mm=10.8)
check('No_partition_or_fabricated_bands', not any('Partition' in o.Name or 'Band' in o.Name for o in doc.Objects))
check('Four_integrated_prints', len(printed) == 4, count=len(printed))
for obj in printed:
    if obj.Name.startswith('PTC_'):
        check('Flush_print_face_' + obj.Name,
              abs(obj.Shape.BoundBox.XMax - (P['heater_plate_x'] + P['heater_plate_thickness'])) < 1e-6,
              outer_x=obj.Shape.BoundBox.XMax)

# Closed cradles cannot be dropped over the cup. Verify a bench assembly path:
# lower pads installed, cup held 1 mm above its seats, frames slid from the cup
# base end (never over the wider mouth lip), then lowered into contact.
cup = doc.Steel_Deflector_Reference.Shape
raised_cup = cup.copy()
raised_cup.translate(V(0, 0, 1))
cradles = [obj for obj in printed if obj.Name.startswith('Cup_')]
for frame in cradles:
    prefix = frame.Name.removesuffix('_Cradle')
    moving = [frame] + [obj for obj in hardware.Group if
                       obj.Name.startswith(prefix + '_Front_') or obj.Name.startswith(prefix + '_Rear_')]
    station = frame.Shape.BoundBox.Center.x
    start = cup.BoundBox.XMax + 12 - station
    steps = math.ceil(start / 5)
    worst = 0
    for i in range(steps + 1):
        dx = start * (1 - i / steps)
        for obj in moving:
            shape = obj.Shape.copy()
            shape.translate(V(dx, 0, 0))
            worst = max(worst, intersection(shape, raised_cup))
    check('Cup_base_end_loading_' + frame.Name, worst < 1e-5,
          sampled_positions=steps + 1, held_above_seats_mm=1, maximum_overlap_mm3=worst)
    for lift in (1, .5, 0):
        shape = cup.copy()
        shape.translate(V(0, 0, lift))
        worst = max(intersection(shape, obj.Shape) for obj in moving)
        check('Cup_lower_into_seats_' + prefix + '_' + str(lift), worst < 1e-5,
              maximum_overlap_mm3=worst)
    # With the cup seated, slide the top contact assembly into the fixed bridge
    # from its +X side, then install the countersunk cold screw from above.
    moving_top = [doc.getObject(prefix + suffix) for suffix in
                  ('_Top_PEEK_20', '_Top_Contact_Washer', '_Top_Contact_M3x6')]
    worst = 0
    for dx in range(12, -1, -1):
        for obj in moving_top:
            shape = obj.Shape.copy()
            shape.translate(V(dx, 0, 0))
            for fixed in [cup] + [c.Shape for c in cradles]:
                worst = max(worst, intersection(shape, fixed))
    check('Top_contact_axial_installation_' + prefix, worst < 1e-5,
          sampled_positions=13, maximum_overlap_mm3=worst)

# Export only the new parts. A single combined 3MF can be selected/exported by the owner.
exports = []
for obj in printed:
    shape = obj.Shape.copy()
    # Heater outer X face and cradle flat X face both lie on the bed.
    shape.rotate(V(), V(0, 1, 0), 90)
    bb = shape.BoundBox
    shape.translate(V(-bb.XMin, -bb.YMin, -bb.ZMin))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=.12, AngularDeflection=.15, Relative=False)
    check('Printable_' + obj.Name, mesh.isSolid() and max(bb.XLength, bb.YLength, bb.ZLength) <= 240)
    mesh.write(str(OUT / (obj.Name + '.stl')))
    exports.append(dict(name=obj.Name, size_mm=[bb.XLength, bb.YLength, bb.ZLength], closed=mesh.isSolid(),
                        print_face='Maximum X face on bed; +90 deg around Y'))

old.Visibility = True
new.Visibility = True
hardware.Visibility = True
refs.Visibility = True
params.Visibility = False
# Local module view with the complete enclosure available in the tree.
hidden = ('Front_Upper', 'Front_Lower', 'Left_Upper', 'Left_Lower', 'Right_Upper', 'Right_Lower',
          'Rear_Upper', 'Top_Lid')
for name in hidden:
    obj = doc.getObject(name + '_Existing')
    if obj:
        obj.Visibility = False
for obj in old.Group:
    if not obj.Name.startswith('Base_'):
        obj.Visibility = False
# Preserve spool envelope in the view to make top clearance visible.
view = G.activeDocument().activeView()
view.viewAxonometric()
view.fitAll()
G.updateGui()
view.saveImage(str(ROOT / 'docs/mounting-retrofit.png'), 1500, 1200, 'White')
# Detail view: temporarily hide the inherited base and spool, without deleting either.
doc.Base_Existing.Visibility = False
doc.Spool_Envelope_UNMEASURED.Visibility = False
view.fitAll()
G.updateGui()
view.saveImage(str(ROOT / 'docs/mounting-retrofit-detail.png'), 1500, 1100, 'White')
doc.Base_Existing.Visibility = True
doc.Spool_Envelope_UNMEASURED.Visibility = True
view.fitAll()
doc.recompute()
# Only the new document is saved. Neither source file is saved or regenerated.
path = ROOT / 'cad/assembly/MYMS_Mounting_Retrofit.FCStd'
doc.saveAs(str(path))
for filename, digest in before.items():
    check('Source_file_unchanged_' + filename, hashlib.sha256((ROOT / filename).read_bytes()).hexdigest() == digest)
report = dict(status=P['status'], source_sha256=before, prints=exports, checks=checks,
              passed=all(c['passed'] for c in checks),
              limitations=['No thermal or airflow simulation/validation', 'Real cup perforations absent from reference',
                           'Actual stock hardware dimensions, PEEK ratings, clamp grip and source availability require verification'])
(OUT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
failures = [c for c in checks if not c['passed']]
print(json.dumps(dict(file=str(path), prints=len(printed), checks=len(checks), failures=failures), indent=2))
assert not failures, 'Retrofit geometric checks failed; inspect validation.json'

# Remove only the six known obsolete generated components, leaving owner files alone.
for name in ('Heater_Lower_Base_Adapter', 'Heater_Upper_Base_Adapter',
             'Heater_Lower_Mast', 'Heater_Upper_Mast',
             'Cup_113_Removable_Cap', 'Cup_183_Removable_Cap'):
    stale = OUT / (name + '.stl')
    if stale.exists():
        stale.unlink()
