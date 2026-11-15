"""Geometric assembly checks, including sampled motion and fastener access."""
import math
import FreeCAD as A
import Part

V=A.Vector

def validate(doc,p):
    w,d,h,t=(p[k] for k in ('outer_width','outer_depth','wall_height','wall'))
    bodies=[b for b in doc.Printed_Assembly.Group if b.TypeId=='PartDesign::Body']
    checks=[]

    def clear(shape,targets,label):
        hits=[]
        for obj in targets:
            target=obj.Shape if hasattr(obj,'Shape') else obj
            if not shape.BoundBox.intersect(target.BoundBox): continue
            volume=shape.common(target).Volume
            if volume>0.05: hits.append((getattr(obj,'Name','shape'),round(volume,3)))
        assert not hits, (label,hits)

    def bore(label,center,axis,length,names):
        probe=Part.makeCylinder(p['m3_clearance']/2-0.05,length,V(*center),V(*axis))
        clear(probe,[doc.getObject(n) for n in names],label)
        checks.append(label)

    # Both sides of each seam must match the receiving insert pockets.
    for rear in (False,True):
        for z in (117,153):
            wall=('Rear' if rear else 'Front')+('_Lower' if z<135 else '_Upper')
            bore('Seam '+wall,(w/2,d+0.1 if rear else -0.1,z),(0,-1 if rear else 1,0),
                 t+p['insert_depth'],[wall,'Seam_Bridge_'+('Rear' if rear else 'Front')])
    # All wall-to-batten fasteners: clearance hole and insert entry align.
    for ix,x in enumerate((9,w-9)):
        for iy,rear in enumerate((False,True)):
            for z in (21,117,153,347):
                wall=('Rear' if rear else 'Front')+('_Lower' if z<135 else '_Upper')
                batten='Corner_%d%d_%d'%(ix,iy,int(z>=190))
                bore('Corner '+batten+' front '+str(z),(x,d+0.1 if rear else -0.1,z),
                     (0,-1 if rear else 1,0),t+p['insert_depth'],[wall,batten])
            for z in (31,107,163,337):
                wall=('Right' if ix else 'Left')+('_Lower' if z<135 else '_Upper')
                batten='Corner_%d%d_%d'%(ix,iy,int(z>=190))
                bore('Corner '+batten+' side '+str(z),(w+0.1 if ix else -0.1,d-9 if rear else 9,z),
                     (-1 if ix else 1,0,0),t+p['insert_depth'],[wall,batten])
    for x in (60,180):
        for dx in (4,14):
            bore('Lid hinge '+str(x+dx),(x+dx,138,h+6.1),(0,0,-1),6.2,
                 ['Top_Lid','Hinge_Lid_'+str(x)])
            for z in (345,355):
                bore('Frame hinge '+str(x+dx)+' '+str(z),(x+dx,d+4.1,z),(0,-1,0),7.2,
                     ['Rear_Upper','Hinge_Frame_'+str(x)])
        bore('Hinge pin '+str(x),(x-0.1,d+6,h+2),(1,0,0),18.2,
             ['Hinge_Frame_'+str(x),'Hinge_Lid_'+str(x)])
    for x in (50,190):
        for z in (352,360):
            bore('Latch bracket '+str(x)+' '+str(z),(x,3.1,z),(0,-1,0),t+p['insert_depth'],
                 ['Front_Upper','Latch_Bracket_'+str(x)])

    # Turnbuttons rotate in a plane above the lid; check the full 180-degree travel.
    open_latches=[]
    for x in (50,190):
        latch=doc.getObject('Lid_Latch_'+str(x))
        for angle in range(0,181,15):
            shape=latch.Shape.copy(); shape.rotate(V(x,-11.5,h+3.5),V(0,0,1),angle)
            clear(shape,[b for b in bodies if b!=latch],'Latch sweep '+str(x)+' '+str(angle))
        shape=latch.Shape.copy(); shape.rotate(V(x,-11.5,h+3.5),V(0,0,1),180)
        open_latches.append(shape)
    checks.append('Turnbuttons: 0–180 degrees, sampled every 15 degrees')

    # Swing lid, moving hinge leaves and guide together about their common pin axis.
    moving_names=('Top_Lid','Hinge_Lid_60','Hinge_Lid_180','Filament_Exit_Guide')
    moving=[doc.getObject(n) for n in moving_names]
    fixed=[b for b in bodies if b not in moving and not b.Name.startswith('Lid_Latch_')]+open_latches
    for angle in range(0,111,5):
        for b in moving:
            shape=b.Shape.copy(); shape.rotate(V(0,d+6,h+2),V(1,0,0),-angle)
            clear(shape,fixed,'Lid sweep '+b.Name+' '+str(angle))
    checks.append('Lid: 0–110 degrees, sampled every 5 degrees, latches open')

    for rear in (False,True):
        label='Exhaust' if rear else 'Intake'
        x=19 if rear else w-57
        z=h-25.5 if rear else 27.5
        wall=doc.getObject('Rear_Upper' if rear else 'Front_Lower')
        slot=Part.makeBox(20,3,5,V(31 if rear else w-45,d-3 if rear else 0,z-2.5))
        # The entire nominal opening is empty wall material.
        assert slot.common(wall.Shape).Volume<0.05
        # The pivot must lie in solid wall before the small drilled bore.
        ring=Part.makeCylinder(3.5,3,V(x,d if rear else 0,z),V(0,-1 if rear else 1,0))
        ring=ring.cut(Part.makeCylinder(p['m3_clearance']/2,3,V(x,d if rear else 0,z),V(0,-1 if rear else 1,0)))
        assert abs(ring.common(wall.Shape).Volume-ring.Volume)<0.05
        shutter=doc.getObject('Vent_Shutter_'+label)
        opened=shutter.Shape.copy(); opened.rotate(V(x,d if rear else 0,z),V(0,1,0),90 if rear else -90)
        opening_projection=Part.makeBox(20,6,5,V(31 if rear else w-45,d-1 if rear else -3,z-2.5))
        assert opened.common(opening_projection).Volume<0.05
        checks.append(label+': 100 mm2 opening, supported pivot, clear at 90 degrees')

    # Filament can leave the split eyelet sideways through the full lid thickness.
    probe=Part.makeCylinder(1.2,w-(w/2+100)+2,V(w/2+100,d/2,h+1),V(1,0,0))
    clear(probe,[doc.Top_Lid,doc.Filament_Exit_Guide],'Filament side-release route')
    checks.append('Filament side-release route: 2.4 mm probe')

    expected=math.pi*((31.5**2-6.3**2)*2+(27.2**2-6.3**2)*10)
    assert all(abs(doc.getObject('Spool_Bushing_'+str(i)).Shape.Volume-expected)<0.01 for i in (1,2))
    checks.append('Original 54.4 mm spool bushings unchanged')
    return checks
