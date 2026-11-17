"""Run with FreeCAD's bundled Python; see scripts/build.sh. Millimetres.

Editable native sketch/pad/pocket parts. Hardware remains reference geometry.
Rebuild after changing parameters.json; generated files are review prototypes.
"""
import FreeCAD as A
import Part, Sketcher, MeshPart
import json, math, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = json.loads((ROOT / 'cad/parameters.json').read_text())
OUT = ROOT / 'exports/prototype'
OUT.mkdir(parents=True, exist_ok=True)
doc = A.newDocument('MYMS_Prototype')
V = A.Vector
parts = []
assembly = doc.addObject('App::Part', 'Printed_Assembly')
refs = doc.addObject('App::Part', 'Hardware_References')
params = doc.addObject('Spreadsheet::Sheet', 'Parameters')
for row, (key, val) in enumerate(P.items(), 1):
    params.set('A'+str(row), key)
    params.set('B'+str(row), str(val))

def rect(x,y,w,h):
    pts = [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
    return [Part.LineSegment(V(*pts[i],0),V(*pts[(i+1)%4],0)) for i in range(4)]

def circle(x,y,r):
    return [Part.Circle(V(x,y,0),V(0,0,1),r)]

def feature(body, name, geoms, z, length, pocket=False, plane=None):
    sk = doc.addObject('Sketcher::SketchObject',body.Name+'_'+name+'_Profile')
    body.addObject(sk)
    sk.Placement.Base.z = z
    if plane is not None: sk.Placement=plane
    for g in geoms:
        idx=sk.addGeometry(g,False)
        sk.addConstraint(Sketcher.Constraint('Block',idx))
    f=body.newObject('PartDesign::Pocket' if pocket else 'PartDesign::Pad',body.Name+'_'+name)
    f.Profile=sk
    f.Length=length
    doc.recompute()
    sk.Visibility=False
    for old in body.Group:
        if old != f: old.Visibility=False
    return f

def drill(body,name,center,normal,radius,depth):
    return feature(body,name,circle(0,0,radius),0,depth,True,
                   A.Placement(V(*center),A.Rotation(V(0,0,1),V(*normal))))

def tube(body,name,center,axis,outer,inner,length):
    return feature(body,name,circle(0,0,outer)+circle(0,0,inner),0,length,False,
                   A.Placement(V(*center),A.Rotation(V(0,0,1),V(*axis))))

def new(name):
    b=doc.addObject('PartDesign::Body',name)
    assembly.addObject(b)
    b.addProperty('App::PropertyString','ReleaseStatus').ReleaseStatus='PROTOTYPE — measurements and thermal validation pending'
    return b

def funnel(body,name,z0,r0,z1,r1):
    profiles=[]
    for i,(z,r) in enumerate(((z0,r0),(z1,r1))):
        sk=doc.addObject('Sketcher::SketchObject',body.Name+'_'+name+'_Profile'+str(i))
        body.addObject(sk); sk.Placement.Base.z=z
        sk.addGeometry(circle(0,0,r)[0],False)
        sk.addConstraint(Sketcher.Constraint('Block',0)); profiles.append(sk)
    loft=body.newObject('PartDesign::SubtractiveLoft',body.Name+'_'+name)
    loft.Profile=profiles[0]; loft.Sections=[profiles[1]]; loft.Ruled=True
    doc.recompute()
    for obj in body.Group:
        if obj!=loft: obj.Visibility=False
    return loft

def plate(name,w,h,t,holes=(),slots=()):
    b=new(name)
    feature(b,'Plate',rect(0,0,w,h),0,t)
    gs=[]
    for x,y,r in holes: gs+=circle(x,y,r)
    for x,y,sw,sh in slots: gs+=rect(x,y,sw,sh)
    if gs: feature(b,'Openings',gs,t,t,True)
    return b

def place(b,base,rot=None):
    b.Placement=A.Placement(V(*base),rot or A.Rotation())

def finish(b,rot=None):
    doc.recompute()
    shape=b.Tip.Shape.copy()
    # Tip.Shape is in the body's local coordinate system.
    if rot: shape.Placement=A.Placement(V(),rot).multiply(shape.Placement)
    bb=shape.BoundBox
    shape.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.12,AngularDeflection=0.15,Relative=False)
    mesh.write(str(OUT/(b.Name+'.stl')))
    parts.append({'name':b.Name,'size_mm':[round(v,3) for v in (bb.XLength,bb.YLength,bb.ZLength)],
                  'volume_mm3':round(shape.Volume,2),'solid_count':len(shape.Solids),
                  'valid':shape.isValid(),'mesh_closed':mesh.isSolid()})
    if b.Tip.ViewObject: b.Tip.ViewObject.ShapeColor=(0.72,0.77,0.80)

CR=P['m3_clearance']/2; IR=P['insert_diameter']/2
W=P['outer_width']; D=P['outer_depth']; H=P['wall_height']; T=P['wall']; S=P['panel_split_height']
FLOOR_Z=3  # Preserve the chamber floor and heater/cup mounting datum.
LID_Z=H+T
CORNER_SIZE=12
CORNER_CENTER=T+CORNER_SIZE/2
EXHAUST_X=T+28
EXHAUST_Z=H-35  # Leave room for the entire shutter below the rear hinge leaf.
EXIT_Z=P['filament_exit_height']
Rfront=A.Rotation(V(1,0,0),90) # local x=x, y=z, extrusion=-y
Rside=A.Rotation(V(1,1,1),120) # local x=y, y=z, extrusion=x

# Screw-fastened panels; corner battens carry the load and seal the seams.
for upper,z0,ph in [(False,FLOOR_Z,S-FLOOR_Z),(True,S,H-S)]:
    for rear in (False,True):
        holes=[(x-T,z,CR) for x in (CORNER_CENTER,W-CORNER_CENTER) for z in (18,ph-18)]
        holes += [(W/2-T,(S+18 if upper else S-18)-z0,CR)]
        if upper:
            holes += [(x-T,z-S,CR) for x in (W/2-12,W/2+12) for z in (260,315,350)]
        if rear and not upper:
            holes += [(x-T,z-z0,CR) for x in (57,179) for z in (37,89)]
            holes += [(W-56-T,128-z0,CR)]
        if rear and upper: holes += [(34-T,258-S,CR)]
        slots=[]
        if not upper and not rear: slots=[(W-45-T,22,20,5)]
        if upper and rear: slots=[(EXHAUST_X-T,EXHAUST_Z-z0-2.5,20,5)]
        if upper and not rear:
            holes += [(x-T,z-S,CR) for x in (50,190) for z in (352,360)]
        if upper and rear:
            holes += [(x-T,z-S,CR) for x in (64,74,184,194) for z in (345,355)]
        if not upper and rear: slots += [(28-T,38-z0,14,8)] # protected low voltage loom exit
        b=plate(('Rear' if rear else 'Front')+('_Upper' if upper else '_Lower'),W-2*T,ph,T,holes,slots)
        place(b,(T,D if rear else T,z0),Rfront); finish(b)
    for right in (False,True):
        holes=[(y,z,CR) for y in (CORNER_CENTER,D-CORNER_CENTER) for z in (28,ph-28)]
        b=plate(('Right' if right else 'Left')+('_Upper' if upper else '_Lower'),D,ph,T,holes)
        if upper and not right:
            feature(b,'Guide_Seat',circle(D/2,EXIT_Z-z0,3),T,T,True)
            feature(b,'Guide_Release_Slot',rect(D/2-1.4,EXIT_Z-z0,2.8,H-EXIT_Z+1),T,T,True)
            for offset in (-9,9):
                drill(b,'Guide_Insert_'+str(offset),(D/2+offset,EXIT_Z-z0,0),(0,0,-1),IR,P['insert_depth'])
        place(b,(W-T if right else 0,0,z0),Rside); finish(b)

floor_holes=[(x,y,CR) for x in (CORNER_CENTER,W-CORNER_CENTER) for y in (CORNER_CENTER,D-CORNER_CENTER)]
b=plate('Base',W,D,T,floor_holes)
place(b,(0,0,FLOOR_Z-T))
lid=plate('Top_Lid',W,D+6,T,[(x,D-138,CR) for x in (64,74,184,194)])
feature(lid,'Finger_Grip',rect(W/2-20,D+4,40,8),0,T)
# Underside locating lip, deliberately relieved at the four screw battens.
lip_start=T+17
lip_near=T+0.4
lip_far=T+2.4
lips=[(lip_start,D-lip_far,100-lip_start,2),(140,D-lip_far,W-lip_start-140,2)]
# Interrupt the rear lip around the hinge mounting washers and nuts.
for start,end in ((lip_start,59),(79,100),(140,179),(199,W-lip_start)):
    lips.append((start,lip_near,end-start,2))
lips += [(x,lip_start,2,D-2*lip_start) for x in (lip_near,W-lip_far)]
for i,(x,y,w,h) in enumerate(lips):
    feature(lid,'Lip'+str(i),rect(x,y,w,h),T,4)
# Print outside face down, flip in assembly so the lip enters the chamber.
place(lid,(0,D,LID_Z),A.Rotation(V(1,0,0),180)); finish(lid)

# Four full height battens, split with staggered joints relative to panels.
# Clearance holes match separate, outward-facing 4 mm insert pockets.
for ix,x in enumerate((T,W-T-CORNER_SIZE)):
    for iy,y in enumerate((T,D-T-CORNER_SIZE)):
        for iz,(z0,z1) in enumerate(((FLOOR_Z,190),(190,H))):
            b=plate('Corner_%d%d_%d'%(ix,iy,iz),12,z1-z0,12)
            # local XY=vertical broad face, local Z=toward chamber depth
            # Machine holes with native cylinders/cuts below using reusable pockets.
            # transform a horizontal-hole sketch onto the body planes.
            # local x corresponds global x; local y global z; local z=-global y.
            # This batten is placed with the same orientation as front plates.
            # front/back face screws enter the local Z faces.
            panelzs=(21,S-18,S+18,H-18)
            for j,z in enumerate(panelzs):
                if z0+4<z<z1-4:
                    drill(b,'Front_Insert'+str(j),(6,z-z0,0 if iy else 12),(0,0,-1 if iy else 1),IR,P['insert_depth'])
            for j,z in enumerate((31,S-28,S+28,H-28)):
                if z0+4<z<z1-4:
                    drill(b,'Side_Insert'+str(j),(12 if ix else 0,z-z0,6),(1 if ix else -1,0,0),IR,P['insert_depth'])
            if iz==0: drill(b,'Floor_Insert',(6,0,6),(0,-1,0),IR,P['insert_depth'])
            place(b,(x,y+12,z0),Rfront); finish(b)

# Printed feet provide clearance for base and heater support screw heads.
for x,y,_ in floor_holes:
    b=new(f'Foot_{x:g}_{y:g}')
    feature(b,'Ring',circle(0,0,8)+circle(0,0,CR),0,6)
    place(b,(x,y,FLOOR_Z-T-6)); finish(b)

# Front/rear middle seam bridges, one shared backer spans the split.
for rear in (False,True):
    b=plate('Seam_Bridge_'+('Rear' if rear else 'Front'),24,60,8)
    for i,h in enumerate((12,48)):
        drill(b,'Wall_Insert'+str(i),(12,h,0 if rear else 8),(0,0,-1 if rear else 1),IR,P['insert_depth'])
    place(b,(W/2-12,D-T if rear else T+8,S-30),Rfront); finish(b)

# Top-loading axle rails, slot bottom is the journal support shoulder.
AZ=P['axle_height']; railbottom=AZ-7
for right in (False,True):
    holes=[(x,z-railbottom,CR) for x in (6,30) for z in (260,315,350)]
    b=plate('Axle_Track_'+('Right' if right else 'Left'),36,H-railbottom,8,holes)
    feature(b,'Journal_Channel',rect(18-P['journal_width']/2,3,P['journal_width'],H-railbottom),8,5,True)
    # local x=global x, local y=global z, local z=-global y
    place(b,(W/2-18,D-T,railbottom),Rfront)
    if not right:
        # reverse front-back orientation around vertical: slot opens into chamber
        place(b,(W/2+18,T,railbottom),A.Rotation(V(0,0,1),180).multiply(Rfront))
    finish(b)

b=new('Spool_Axle')
axle_shoulder=T+9
shaft_length=D-2*axle_shoulder
feature(b,'Shaft',circle(0,0,6),0,shaft_length)
feature(b,'Lower_Journal',rect(-7,-4,14,8),-4,4)
feature(b,'Upper_Journal',rect(-7,-4,14,8),shaft_length,4)
place(b,(W/2,axle_shoulder,AZ),A.Rotation(V(1,0,0),-90)); finish(b,A.Rotation(V(1,0,0),90))
# Loose rotating bushings. The bore and flange dimensions must match measured spool.
for i in range(2):
    b=new('Spool_Bushing_'+str(i+1))
    feature(b,'Flange',circle(0,0,P['spool_bore']/2+4)+circle(0,0,6.3),0,2)
    feature(b,'Hub',circle(0,0,(P['spool_bore']-0.6)/2)+circle(0,0,6.3),2,10)
    y=(D-P['spool_width'])/2-2 if i==0 else (D+P['spool_width'])/2+2
    place(b,(W/2,y,AZ),A.Rotation(V(1,0,0),-90 if i==0 else 90)); finish(b)

# Pivot is on solid wall, 12 mm to the left of each 20 x 5 mm opening.
for rear in (False,True):
    slotx=EXHAUST_X if rear else W-45
    z=EXHAUST_Z if rear else 27.5
    pivotx=slotx-12
    b=plate('Vent_Shutter_'+('Exhaust' if rear else 'Intake'),40,15,2,[(4,7.5,CR)])
    place(b,(pivotx-4,D+2 if rear else 0,z-7.5),Rfront); finish(b)
    wall=doc.getObject('Rear_Upper' if rear else 'Front_Lower')
    feature(wall,'Vent_Pivot',circle(pivotx-T,z-(S if rear else FLOOR_Z),CR),T,T,True)
    parts[:]=[p for p in parts if p['name']!=wall.Name]; finish(wall)

# Fixed left-wall guide: split opens upward, independently of the hinged lid.
b=new('Filament_Exit_Guide')
feature(b,'Flange',circle(0,0,5)+circle(0,0,P['filament_exit_hole']/2),0,2)
feature(b,'Retaining_Ears',rect(-3,3,6,9)+rect(-3,-12,6,9),0,2)
feature(b,'Mounting_Holes',circle(0,-9,CR)+circle(0,9,CR),2,2,True)
feature(b,'Collar',circle(0,0,2.8)+circle(0,0,P['filament_exit_hole']/2),-T,T)
funnel(b,'Outer_Funnel',2,3.0,-T/2+0.5,P['filament_exit_hole']/2)
funnel(b,'Inner_Funnel',-T,2.3,-T/2-0.5,P['filament_exit_hole']/2)
old=b.Tip
assert old.Shape.isValid(), 'Invalid guide funnel geometry'
edges=[]
for i,e in enumerate(old.Shape.Edges,1):
    if hasattr(e.Curve,'Radius'):
        if (abs(e.Curve.Radius-3)<0.01 and abs(e.CenterOfMass.z-2)<0.01) or (abs(e.Curve.Radius-2.3)<0.01 and abs(e.CenterOfMass.z+T)<0.01): edges.append('Edge'+str(i))
f=b.newObject('PartDesign::Fillet','Filament_Guide_Rounds'); f.Base=(old,edges); f.Radius=0.2
doc.recompute(); old.Visibility=False
feature(b,'Side_Release',rect(0,-1.4,6,2.8),2,T+2,True)
place(b,(0,D/2,EXIT_Z),A.Rotation(V(0,1,0),-90))
finish(b,A.Rotation(V(1,0,0),180))

# Hinges: two outside rear leaves and interleaved knuckles, permanently pinned.
for x in (60,180):
    pin_height=24+T  # Local height above the frame leaf's origin.
    b=plate('Hinge_Frame_'+str(x),18,20,4,[(4,5,CR),(14,5,CR),(4,15,CR),(14,15,CR)])
    feature(b,'Neck',rect(0,17,5.7,pin_height-17)+rect(12.3,17,5.7,pin_height-17),0,4)
    tube(b,'Outer_Knuckle_A',(0,pin_height,-2),(1,0,0),4.5,CR,5.7)
    tube(b,'Outer_Knuckle_B',(12.3,pin_height,-2),(1,0,0),4.5,CR,5.7)
    drill(b,'Pin_Clearance',(0,pin_height,-2),(-1,0,0),CR,18)
    place(b,(x,D+4,H-25),Rfront); finish(b)
    b=plate('Hinge_Lid_'+str(x),18,18,3,[(4,6,CR),(14,6,CR)])
    feature(b,'Neck',rect(6.3,18,5.4,6),-1,4)
    tube(b,'Inner_Knuckle',(6.3,24,-1),(1,0,0),4.5,CR,5.4)
    drill(b,'Pin_Clearance',(0,24,-1),(-1,0,0),CR,18)
    place(b,(x,D-18,LID_Z)); finish(b,A.Rotation(V(0,1,0),90))

# Horizontal turnbuttons swing above the lid, so they do not bind on its edge.
for x in (50,190):
    b=plate('Latch_Bracket_'+str(x),18,18,16)
    # Local x=x, local y=z, local z=-y (front-facing bracket).
    feature(b,'Pivot_Stand',rect(0,18,18,T+1.5),7,9)
    for i,z in enumerate((6,14)):
        drill(b,'Wall_Insert'+str(i),(9,z,0),(0,0,-1),IR,P['insert_depth'])
    drill(b,'Pivot_Insert',(9,19.5+T,11.5),(0,1,0),IR,P['insert_depth'])
    place(b,(x-9,0,H-19),Rfront); finish(b)
    b=plate('Lid_Latch_'+str(x),12,30,3,[(6,5,CR)])
    feature(b,'Finger_Tab',rect(12,17,6,10),0,3)
    place(b,(x-6,-16.5,LID_Z+0.5)); finish(b)

# External electronics pod. Plain removable carrier avoids guessed PCB hole patterns.
pod=plate('Electronics_Pod',112,94,3)
feature(pod,'Walls',rect(0,0,112,94)+rect(3,3,106,88),3,35)
for i,(x,y) in enumerate(((3,3),(101,3),(3,83),(101,83))):
    feature(pod,'Boss'+str(i),rect(x,y,8,8),3,35)
feature(pod,'Lid_Insert_Pockets',sum((circle(x,y,IR) for x,y in ((7,7),(105,7),(7,87),(105,87))),[]),38,P['insert_depth'],True)
for i,(x,y) in enumerate(((-10,12),(-10,64),(112,12),(112,64))):
    feature(pod,'Mount_Ear'+str(i),rect(x,y,10,18),0,3)
feature(pod,'Mount_Holes',sum((circle(x,y,CR) for x in (-5,117) for y in (21,73)),[]),3,3,True)
for i,(x,y) in enumerate(((15,21),(97,21),(15,73),(97,73))):
    feature(pod,'Carrier_Boss'+str(i),circle(x,y,4),3,5)
feature(pod,'Carrier_Insert_Pockets',sum((circle(x,y,IR) for x,y in ((15,21),(97,21),(15,73),(97,73))),[]),8,P['carrier_insert_depth'],True)
# Wiring enters through replaceable lid, not an unmeasured connector cutout.
place(pod,(62,D+8,110),A.Rotation(V(1,0,0),-90)); finish(pod)
b=plate('Electronics_Lid',112,94,3,[(x,y,CR) for x,y in ((7,7),(105,7),(7,87),(105,87))],[(42,12,18,8),(42,72,18,8)])
place(b,(62,D+46,110),A.Rotation(V(1,0,0),-90)); finish(b)
b=plate('Electronics_Carrier',98,68,2,[(8,8,CR),(90,8,CR),(8,60,CR),(90,60,CR)],[(12,20,3,28),(30,20,3,28),(48,20,3,28),(66,20,3,28),(84,20,3,28)])
place(b,(69,D+16,97),A.Rotation(V(1,0,0),-90)); finish(b)

for x in (57,179):
    for z in (37,89):
        b=new('Pod_Spacer_'+str(x)+'_'+str(z))
        feature(b,'Ring',circle(0,0,4)+circle(0,0,CR),0,8)
        place(b,(x,D,z),A.Rotation(V(1,0,0),-90)); finish(b)

# Edge-down printing: all three pads reach the first pad's Y=16 bed edge.
b=plate('Sensor_Mount_1',24,16,3,[(4,8,CR)])
feature(b,'Standoff_Arm',rect(8,2,8,14),3,12)
feature(b,'Cradle',rect(14,2,18,14),15,3)
feature(b,'Sensor_Seat',rect(20,5,5.2,6.2),18,2.3,True)
feature(b,'Lead_Exit_Notch',rect(20,2,5.2,3.1),18,2.3,True)
feature(b,'Body_Tie_Slots',rect(17,5,2,6)+rect(27,5,2,6),18,3,True)
feature(b,'Wire_Tie_Ear',rect(6,-4,12,5),0,3)
feature(b,'Wire_Tie_Slots',rect(7,-3,2,3)+rect(15,-3,2,3),3,3,True)
feature(b,'Wire_Tie_Rear_Relief',rect(7,0,10,3),0,1,True,
        A.Placement(V(0,-0.5,0),A.Rotation(V(1,0,0),180)))
place(b,(30,D-T,AZ),Rfront); finish(b,A.Rotation(V(1,0,0),-90))
# Wall-contact sensor: window exposes the sensor face to the target wall.
b=plate('Sensor_Mount_2',28,16,3,[(4,8,CR)],[(14,5,5.2,6.2),(9,5,2,6),(21,5,2,6),(10,0.8,2,3),(22,0.8,2,3)])
feature(b,'Sensor_Locators',rect(12,4,2,8)+rect(19.2,4,1.8,8),3,1.0)
feature(b,'Lead_Exit_Notch',rect(14,0,5.2,5.1),3,3,True)
tie_route=[(9,7),(11,7),(11,12),(21,12),(21,7),(23,7),(23,14),(9,14)]
tie_profile=[Part.LineSegment(V(x,16-y,0),V(tie_route[(i+1)%8][0],16-tie_route[(i+1)%8][1],0)) for i,(x,y) in enumerate(tie_route)]
feature(b,'Rear_Tie_Relief',tie_profile,0,1,True,
        A.Placement(V(0,16,0),A.Rotation(V(1,0,0),180)))
feature(b,'Wire_Tie_Rear_Relief',rect(10,12.7,14,2),0,1,True,
        A.Placement(V(0,16,0),A.Rotation(V(1,0,0),180)))
doc.recompute()
place(b,(W-60,D-T,120),Rfront); finish(b)

# Small physical fit coupons, outside assembled product and hidden by default.
coupons=doc.addObject('App::Part','Fit_Test_Coupons')
for gap in (0.3,0.5,0.7):
    b=plate('Track_Coupon_'+str(int(gap*100)),32,28,8)
    feature(b,'Slot',rect(16-(14+gap)/2,5,14+gap,24),8,5,True)
    assembly.removeObject(b); coupons.addObject(b); finish(b); b.Visibility=False
coupons.Visibility=False

# Heat-rated support bolt locations: no ABS heater/cup cradles.
# These holes accept isolated mounting hardware; exact hardware is not selected.
floor=doc.getObject('Base')
thermalholes=[(x,y,CR) for x in (68,78) for y in (21,129)]
thermalholes += [(x,y,CR) for x in (113,183) for y in (61,89)]
feature(floor,'Isolated_Support_Holes',sum((circle(x,y,r) for x,y,r in thermalholes),[]),T,T,True)
finish(floor)

# Preserve original parametric source file; reference copies are positioned only here.
source=A.openDocument(str(ROOT/'cad/assembly/Hardware_References.FCStd'))
audit=[]
for obj in (source.getObject('Body'),source.getObject('Body001')):
    bb=obj.Shape.BoundBox
    audit.append({'name':obj.Name,'label':obj.Label,'size_mm':[bb.XLength,bb.YLength,bb.ZLength], 'valid':obj.Shape.isValid(),'solids':len(obj.Shape.Solids)})
    r=doc.addObject('PartDesign::Feature', 'Steel_Deflector_Reference' if obj.Name=='Body' else 'PTC_Heater_Reference')
    refs.addObject(r); r.Shape=obj.Shape.copy()
    if obj.Name=='Body': place(r,(207,75,65),A.Rotation(V(0,1,0),-90))
    else: place(r,(62,75,65),A.Rotation(V(0,1,0),-90))
    if r.ViewObject: r.ViewObject.ShapeColor=(0.65,0.65,0.68) if obj.Name=='Body' else (0.22,0.23,0.24)
    r.addProperty('App::PropertyString','Evidence').Evidence='Owner reference; cup perforations and physical fit unverified'
A.closeDocument(source.Name)

def reference(name,shape,color):
    r=doc.addObject('PartDesign::Feature',name); refs.addObject(r); r.Shape=shape
    if r.ViewObject: r.ViewObject.ShapeColor=color
    return r

spool=Part.makeCylinder(P['spool_diameter']/2,P['spool_width'],V(W/2,(D-P['spool_width'])/2,AZ),V(0,1,0))
spool=spool.cut(Part.makeCylinder(P['spool_bore']/2,P['spool_width'],V(W/2,(D-P['spool_width'])/2,AZ),V(0,1,0)))
r=reference('Spool_Envelope_UNMEASURED',spool,(0.85,0.53,0.22))
if r.ViewObject: r.ViewObject.Transparency=65
# This is a proposed heat-rated metal/ceramic assembly, excluded from ABS STLs.
divider=Part.makeBox(1,118,105,V(72,16,14)).cut(Part.makeCylinder(36,3,V(71,75,65),V(1,0,0)))
for y,z in ((51,27),(99,103)):
    divider=divider.cut(Part.makeCylinder(CR,3,V(71,y,z),V(1,0,0)))
    spacer=Part.makeCylinder(3.5,10,V(62,y,z),V(1,0,0)).cut(Part.makeCylinder(CR,10,V(62,y,z),V(1,0,0)))
    reference('Ceramic_Heater_Spacer_'+str(y)+'_PROPOSED',spacer,(0.94,0.91,0.80))
for y in (16,124):
    foot=Part.makeBox(18,10,2,V(64,y,12))
    for x in (68,78):
        foot=foot.cut(Part.makeCylinder(CR,2,V(x,y+5,12)))
        spacer=Part.makeCylinder(3.5,9,V(x,y+5,3)).cut(Part.makeCylinder(CR,9,V(x,y+5,3)))
        reference('Ceramic_Partition_Foot_'+str(x)+'_'+str(y)+'_PROPOSED',spacer,(0.94,0.91,0.80))
    divider=divider.fuse(foot)
r=reference('Metal_Return_Partition_PROPOSED',divider,(0.65,0.67,0.70))
r.addProperty('App::PropertyString','Status').Status='Heat-rated material; requires confirmed fabrication and isolated mounts'
for x in (110,180):
    band=Part.makeCylinder(49,6,V(x,75,65),V(1,0,0)).cut(Part.makeCylinder(47.8,6,V(x,75,65),V(1,0,0)))
    foot=Part.makeBox(6,36,2,V(x,57,14.2))
    # A narrow vertical web joins saddle foot to the lower band.
    foot=foot.fuse(Part.makeBox(6,4,3,V(x,73,16)))
    for y in (61,89):
        foot=foot.cut(Part.makeCylinder(CR,2,V(x+3,y,14.2)))
        spacer=Part.makeCylinder(3.5,11.2,V(x+3,y,3)).cut(Part.makeCylinder(CR,11.2,V(x+3,y,3)))
        reference('Ceramic_Cup_Foot_'+str(x)+'_'+str(y)+'_PROPOSED',spacer,(0.94,0.91,0.80))
    band=band.fuse(foot)
    reference('Metal_Cup_Band_'+str(x)+'_PROPOSED',band,(0.7,0.7,0.72))

doc.recompute()
# Real solid intersections, excluding intentionally connected printable parts.
collisions=[]
for hardware in refs.Group:
    for b in assembly.Group:
        if b.TypeId!='PartDesign::Body': continue
        common=hardware.Shape.common(b.Shape)
        if common.Volume>0.1: collisions.append([hardware.Name,b.Name,round(common.Volume,3)])
print_overlaps=[]
bs=[b for b in assembly.Group if b.TypeId=='PartDesign::Body']
for i,b in enumerate(bs):
    for other in bs[i+1:]:
        if not b.Shape.BoundBox.intersect(other.Shape.BoundBox): continue
        vol=b.Shape.common(other.Shape).Volume
        if vol>0.1: print_overlaps.append([b.Name,other.Name,round(vol,3)])
import importlib.util
spec=importlib.util.spec_from_file_location('myms_mechanisms',ROOT/'scripts/validate_mechanisms.py')
mechanisms=importlib.util.module_from_spec(spec); spec.loader.exec_module(mechanisms)
mechanism_checks=mechanisms.validate(doc,P)
report={'mechanism_checks':mechanism_checks,'printed_part_intersections':print_overlaps,'status':'MECHANICAL REVIEW PROTOTYPE — NOT THERMALLY VALIDATED', 'parts':parts,'reference_inventory':audit,'hardware_print_intersections':collisions}
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
assert all(p['valid'] and p['solid_count']==1 and p['mesh_closed'] for p in parts), 'Invalid part, inspect validation.json'
assert all(max(p['size_mm'])<=246 for p in parts), 'Print envelope exceeds 246 mm'
assert not print_overlaps, 'Printed parts overlap, inspect validation.json'
assert not collisions, 'Hardware interference, inspect validation.json'
doc.recompute()
doc.saveAs(str(ROOT/'cad/assembly/MYMS_Prototype.FCStd'))
Part.export([b for b in assembly.Group if b.TypeId=='PartDesign::Body'],str(OUT/'MYMS_Printed_Assembly.step'))
print('Built',len(parts),'parts; all single-solid, closed, valid; no hardware/print collisions.')
