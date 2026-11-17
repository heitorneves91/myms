"""Render real mount geometry with illustrative sensor, ties and insulated leads.

Reference parts show assembly intent, not a sensor pinout or exact hardware BOM.
No modifications are made to the main document by this illustration script.
"""
from pathlib import Path
import os,sys
import FreeCAD as A, FreeCADGui as G, Part

ROOT=Path(__file__).resolve().parents[1]
V=A.Vector
HEADLESS=bool(os.getenv('MYMS_DEMO_HEADLESS'))
if HEADLESS: G.setupWithoutGUI()
elif not A.GuiUp: G.showMainWindow()
source=A.openDocument(str(ROOT/'cad/assembly/MYMS_Prototype.FCStd'))
doc=A.newDocument('Sensor_Mounts_Demonstration')
groups=[]
evidence=[]

def item(group,name,shape,color,note='Illustrative hardware, not a manufacturing model'):
    obj=doc.addObject('PartDesign::Feature',name)
    group.addObject(obj); obj.Shape=shape
    if obj.ViewObject: obj.ViewObject.ShapeColor=color
    obj.addProperty('App::PropertyString','Purpose').Purpose=note
    return obj

def tube(points,r):
    shapes=[]
    for start,end in zip(points,points[1:]):
        v=V(*end)-V(*start)
        shapes.append(Part.makeCylinder(r,v.Length,V(*start),v.normalize()))
    for point in points[1:-1]: shapes.append(Part.makeSphere(r,V(*point)))
    return shapes[0].multiFuse(shapes[1:]) if len(shapes)>1 else shapes[0]

def strap(x1,x2,y,zlow,zhigh):
    width=1.6; thick=0.6
    return Part.makeCompound([
        Part.makeBox(x2-x1+thick,width,thick,V(x1,y,zlow)),
        Part.makeBox(x2-x1+thick,width,thick,V(x1,y,zhigh)),
        Part.makeBox(thick,width,zhigh-zlow,V(x1,y,zlow)),
        Part.makeBox(thick,width,zhigh-zlow,V(x2,y,zlow)),
        Part.makeBox(1.8,2.4,1.1,V(x2-0.6,y-0.4,zhigh)),
    ])

for n in (1,2):
    group=doc.addObject('App::Part','Air_Sensor' if n==1 else 'Wall_Contact_Sensor')
    groups.append(group)
    mount=source.getObject('Sensor_Mount_'+str(n)).Tip.Shape.copy()
    printed=item(group,'Printed_Mount_'+str(n),mount,(0.67,0.78,0.82),'Copy of actual exported mount geometry')
    cx=22.6 if n==1 else 16.6
    floor=15.7 if n==1 else 0
    center=floor+1.8
    sensor=Part.makeCylinder(2.5,5.8,V(cx,5.2,center),V(0,1,0))
    sensor=sensor.common(Part.makeBox(6,6,4.4,V(cx-3,5.1,floor)))
    item(group,'Sensor_Body_'+str(n),sensor,(0.12,0.13,0.14),'TO-92-style envelope; verify actual sensor dimensions')
    overlap=mount.common(sensor).Volume
    assert overlap<0.02,('Sensor intersects mount',n,overlap)
    evidence.append('Sensor body '+str(n)+': seated without intersection')
    if n==1:
        bodytie=strap(17.7,27.7,7.4,14.0,20.05)
        wiretie=strap(7.7,15.7,-2.3,0.15,4.4)
    else:
        bodytie=Part.makeCompound([
            Part.makeBox(12.6,1.6,0.6,V(9.7,7.4,4.35)),
            Part.makeBox(0.6,1.6,4.2,V(9.7,7.4,0.15)),
            Part.makeBox(0.6,1.6,4.2,V(21.7,7.4,0.15)),
            Part.makeBox(0.6,6.0,0.6,V(9.7,7.4,0.15)),
            Part.makeBox(0.6,6.0,0.6,V(21.7,7.4,0.15)),
            Part.makeBox(12.6,1.4,0.6,V(9.7,12.0,0.15)),
            Part.makeBox(1.8,2.4,1.1,V(21.1,7.0,4.35)),
        ])
        wiretie=strap(10.7,22.7,1.5,0.15,3.05)
    assert mount.common(bodytie).Volume<0.02,('Blocked body tie route',n)
    assert sensor.common(bodytie).Volume<0.02,('Tie crosses sensor body',n)
    assert mount.common(wiretie).Volume<0.02,('Blocked wire tie route',n)
    evidence.append('Sensor '+str(n)+': body and wire tie routes clear')
    item(group,'Body_Retaining_Tie_'+str(n),bodytie,(0.95,0.64,0.10),'Yellow: body retention; lightly snug, not crushing the package')
    item(group,'Wire_Strain_Relief_Tie_'+str(n),wiretie,(0.95,0.64,0.10),'Yellow: grips insulated cable, not exposed leads')
    # Colored wires are mechanical route indicators; colors do not assign sensor pins.
    for i,color in enumerate(((0.82,0.18,0.16),(0.18,0.35,0.78),(0.20,0.61,0.30))):
        x=cx+(i-1)*1.27
        leads=tube([(x,5.2,center),(x,2.2,center)],0.22)
        if n==1:
            path=[(x,2.2,center),(x,0.5,center),(12+(i-1)*1.1,-1.5,3.8),(12+(i-1)*1.1,-12,3.8)]
        else:
            path=[(x,2.2,center),(x,-12,center)]
        wire=tube(path,0.45)
        # The demo must not disguise a blocked lead or cable route.
        assert mount.common(leads).Volume<0.02,('Blocked lead route',n,i)
        assert mount.common(wire).Volume<0.02,('Blocked wire route',n,i)
        item(group,'Insulated_Lead_'+str(n)+'_'+str(i),leads,(0.7,0.7,0.72),'Lead/joint representation; insulate each lead separately')
        item(group,'Wire_'+str(n)+'_'+str(i),wire,color,'Illustrative insulation color; not a pin assignment')
    evidence.append('Sensor '+str(n)+': all three lead/cable paths clear')
    # A representative fastener shows which hole fixes the bracket to the wall.
    bolt=Part.makeCylinder(1.5,6,V(4,8,-3))
    bolt=bolt.fuse(Part.makeCylinder(2.8,2,V(4,8,3)))
    item(group,'Mounting_Screw_'+str(n),bolt,(0.58,0.60,0.64),'M3 mounting fastener; washer/nut omitted for clarity')
    if n==2:
        wall=Part.makeBox(32,23,1.5,V(-2,-4,-1.5))
        obj=item(group,'Wall_Contact_Surface',wall,(0.8,0.81,0.82),'Transparent target wall; flat sensor face rests on this plane')
        if obj.ViewObject: obj.ViewObject.Transparency=80
    group.addProperty('App::PropertyString','AssemblyNotes').AssemblyNotes='References are schematic. Use the correct sensor pinout; insulate each joint. Ties need physical tightening.'
    group.Placement.Base.x=0 if n==1 else 50

print_group=doc.addObject('App::Part','Air_Sensor_Print_Orientation')
print_shape=source.Sensor_Mount_1.Tip.Shape.copy()
print_shape.rotate(V(),V(1,0,0),-90)
bb=print_shape.BoundBox
print_shape.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
item(print_group,'Air_Mount_Edge_Down',print_shape,(0.83,0.87,0.88),
     'Print on original pad edge Y=16; same orientation as Sensor_Mount_1.stl')
item(print_group,'Print_Bed_Reference',Part.makeBox(40,26,0.5,V(-4,-4,-0.5)),(0.36,0.38,0.40),
     'Reference plane only; do not print')
print_group.Visibility=False
A.closeDocument(source.Name)
doc.recompute()
(ROOT/'docs/sensor-demo-checks.txt').write_text('\n'.join(evidence)+'\n')
if HEADLESS:
    print('Sensor reference and lead/tie route checks passed',flush=True)
    sys.exit(0)
view=G.activeDocument().activeView(); view.viewAxonometric()
for i,g in enumerate(groups,1):
    for other in groups: other.Visibility=(other==g)
    view.fitAll(); G.updateGui()
    view.saveImage(str(ROOT/('docs/sensor-mount-'+str(i)+'.png')),1400,1100,'White')
for g in groups: g.Visibility=True
view.fitAll(); G.updateGui()
view.saveImage(str(ROOT/'docs/sensor-mounts-demo.png'),1800,1100,'White')
for g in groups: g.Visibility=False
print_group.Visibility=True
view.fitAll(); G.updateGui()
view.saveImage(str(ROOT/'docs/sensor-mount-1-print.png'),1400,1100,'White')
print_group.Visibility=False
for g in groups: g.Visibility=True
view.fitAll()
doc.saveAs(str(ROOT/'cad/assembly/Sensor_Mounts_Demo.FCStd'))
(ROOT/'docs/sensor-demo-checks.txt').write_text('\n'.join(evidence)+'\n')
print('Saved sensor demonstration CAD and three images; body and wire paths checked')
