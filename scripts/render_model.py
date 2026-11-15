"""Run in FreeCAD GUI Python; renders and saves sensible initial visibility."""
import FreeCAD as A, FreeCADGui as G
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
G.showMainWindow()
doc=A.openDocument(str(ROOT/'cad/assembly/MYMS_Prototype.FCStd'))
for obj in doc.Objects:
    if obj.TypeId=='PartDesign::Body':
        for child in obj.Group:
            if child.ViewObject: child.Visibility=False
        obj.Visibility=True
        obj.Tip.Visibility=True
        obj.Tip.ViewObject.ShapeColor=(0.73,0.79,0.80)
    elif obj.TypeId=='Sketcher::SketchObject': obj.Visibility=False
doc.Printed_Assembly.Visibility=True
doc.Hardware_References.Visibility=True
doc.Fit_Test_Coupons.Visibility=False
for obj in doc.Hardware_References.Group:
    obj.Visibility=True
    obj.ViewObject.ShapeColor=(0.94,0.91,0.80) if obj.Name.startswith('Ceramic') else (0.55,0.57,0.61)
doc.Spool_Envelope_UNMEASURED.ViewObject.ShapeColor=(0.87,0.55,0.22)
doc.Spool_Envelope_UNMEASURED.ViewObject.Transparency=55
doc.PTC_Heater_Reference.ViewObject.ShapeColor=(0.16,0.18,0.19)
doc.recompute()
view=G.activeDocument().activeView()
view.viewAxonometric(); view.fitAll()
G.updateGui()
view.saveImage(str(ROOT/'docs/assembly.png'),1600,1300,'White')
moving=('Top_Lid','Hinge_Lid_60','Hinge_Lid_180','Filament_Exit_Guide')
saved={name:A.Placement(doc.getObject(name).Placement) for name in moving+('Lid_Latch_50','Lid_Latch_190')}
def rotate_object(name,point,axis,angle):
    turn=A.Placement(); turn.rotate(A.Vector(*point),A.Vector(*axis),angle)
    doc.getObject(name).Placement=turn.multiply(saved[name])
for x in (50,190):
    rotate_object('Lid_Latch_'+str(x),(x,-11.5,368.5),(0,0,1),180)
for name in moving: rotate_object(name,(0,156,367),(1,0,0),-105)
doc.recompute(); view.fitAll(); G.updateGui()
view.saveImage(str(ROOT/'docs/lid-open.png'),1600,1500,'White')
for name,placement in saved.items(): doc.getObject(name).Placement=placement
doc.recompute()
for name in ('Front_Upper','Front_Lower','Top_Lid','Corner_00_0','Corner_00_1','Corner_10_0','Corner_10_1','Seam_Bridge_Front'):
    doc.getObject(name).Visibility=False
view.fitAll(); G.updateGui()
view.saveImage(str(ROOT/'docs/cutaway.png'),1600,1300,'White')
# Save complete assembly as opening view; cutaway is a separate image.
for name in ('Front_Upper','Front_Lower','Top_Lid','Corner_00_0','Corner_00_1','Corner_10_0','Corner_10_1','Seam_Bridge_Front'):
    doc.getObject(name).Visibility=True
doc.save()
print('Saved assembly, open-lid and cutaway previews')
