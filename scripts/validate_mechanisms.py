"""Geometric assembly checks, including sampled motion and fastener access."""
import math
import FreeCAD as A
import Part

V=A.Vector

def validate(doc,p):
    w,d,h,t=(p[k] for k in ('outer_width','outer_depth','wall_height','wall'))
    split=p['panel_split_height']
    floor_top=doc.Base.Shape.BoundBox.ZMax
    floor_bottom=doc.Base.Shape.BoundBox.ZMin
    lid_top=h+t
    corner_center=t+6
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

    # The enclosure slabs have the requested thickness on their normal axes.
    for side,axis in (('Front','Y'),('Rear','Y'),('Left','X'),('Right','X')):
        for level in ('Lower','Upper'):
            bounds=doc.getObject(side+'_'+level).Shape.BoundBox
            assert abs(getattr(bounds,axis+'Length')-t)<1e-6
    assert abs(floor_top-floor_bottom-t)<1e-6
    assert abs(doc.Top_Lid_Plate.Length.Value-t)<1e-6
    checks.append('All eight wall panels, base and lid slabs match the shell thickness')

    # Both sides of each seam must match the receiving insert pockets.
    for rear in (False,True):
        for z in (117,153):
            wall=('Rear' if rear else 'Front')+('_Lower' if z<split else '_Upper')
            bore('Seam '+wall,(w/2,d+0.1 if rear else -0.1,z),(0,-1 if rear else 1,0),
                 t+p['insert_depth'],[wall,'Seam_Bridge_'+('Rear' if rear else 'Front')])
    # All wall-to-batten fasteners: clearance hole and insert entry align.
    for ix,x in enumerate((corner_center,w-corner_center)):
        for iy,rear in enumerate((False,True)):
            y=d-corner_center if rear else corner_center
            batten='Corner_%d%d_0'%(ix,iy)
            bore('Foot and base '+batten,(x,y,floor_bottom-6.1),(0,0,1),t+6+p['insert_depth'],
                 [f'Foot_{x:g}_{y:g}','Base',batten])
            for z in (21,117,153,347):
                wall=('Rear' if rear else 'Front')+('_Lower' if z<split else '_Upper')
                batten='Corner_%d%d_%d'%(ix,iy,int(z>=190))
                bore('Corner '+batten+' front '+str(z),(x,d+0.1 if rear else -0.1,z),
                     (0,-1 if rear else 1,0),t+p['insert_depth'],[wall,batten])
            for z in (31,107,163,337):
                wall=('Right' if ix else 'Left')+('_Lower' if z<split else '_Upper')
                batten='Corner_%d%d_%d'%(ix,iy,int(z>=190))
                bore('Corner '+batten+' side '+str(z),(w+0.1 if ix else -0.1,y,z),
                     (-1 if ix else 1,0,0),t+p['insert_depth'],[wall,batten])
    for x in (60,180):
        for dx in (4,14):
            bore('Lid hinge '+str(x+dx),(x+dx,d-12,lid_top+3.1),(0,0,-1),t+3.2,
                 ['Top_Lid','Hinge_Lid_'+str(x)])
            for z in (345,355):
                bore('Frame hinge '+str(x+dx)+' '+str(z),(x+dx,d+4.1,z),(0,-1,0),t+4.2,
                     ['Rear_Upper','Hinge_Frame_'+str(x)])
        bore('Hinge pin '+str(x),(x-0.1,d+6,lid_top-1),(1,0,0),18.2,
             ['Hinge_Frame_'+str(x),'Hinge_Lid_'+str(x)])
    for x in (50,190):
        for z in (352,360):
            bore('Latch bracket '+str(x)+' '+str(z),(x,t+0.1,z),(0,-1,0),t+p['insert_depth'],
                 ['Front_Upper','Latch_Bracket_'+str(x)])

    # Turnbuttons rotate in a plane above the lid; check the full 180-degree travel.
    open_latches=[]
    for x in (50,190):
        latch=doc.getObject('Lid_Latch_'+str(x))
        for angle in range(0,181,15):
            shape=latch.Shape.copy(); shape.rotate(V(x,-11.5,lid_top+0.5),V(0,0,1),angle)
            clear(shape,[b for b in bodies if b!=latch],'Latch sweep '+str(x)+' '+str(angle))
        shape=latch.Shape.copy(); shape.rotate(V(x,-11.5,lid_top+0.5),V(0,0,1),180)
        open_latches.append(shape)
    checks.append('Turnbuttons: 0–180 degrees, sampled every 15 degrees')

    # Swing lid, moving hinge leaves and guide together about their common pin axis.
    moving_names=('Top_Lid','Hinge_Lid_60','Hinge_Lid_180','Filament_Exit_Guide')
    moving=[doc.getObject(n) for n in moving_names]
    fixed_bodies=[b for b in bodies if b not in moving and not b.Name.startswith('Lid_Latch_')]
    fixed=fixed_bodies+open_latches
    for angle in (*range(5),*range(5,111,5)):
        for b in moving:
            shape=b.Shape.copy(); shape.rotate(V(0,d+6,lid_top-1),V(1,0,0),-angle)
            clear(shape,fixed,'Lid sweep '+b.Name+' '+str(angle))
    checks.append('Lid: 0–110 degrees, sampled every 5 degrees plus 1–4 degrees, latches open')

    for rear in (False,True):
        label='Exhaust' if rear else 'Intake'
        slot_x=t+28 if rear else w-45
        x=slot_x-12
        z=h-35 if rear else 27.5
        wall=doc.getObject('Rear_Upper' if rear else 'Front_Lower')
        slot=Part.makeBox(20,t+3,5,V(slot_x,d-t-3 if rear else 0,z-2.5))
        shutter=doc.getObject('Vent_Shutter_'+label)
        clear(slot,[b for b in bodies if b!=shutter],label+' opening through wall and past backers')
        # The pivot must lie in solid wall before the small drilled bore.
        pivot_point=V(x,d if rear else 0,z)
        inward=V(0,-1 if rear else 1,0)
        ring=Part.makeCylinder(3.5,t,pivot_point,inward)
        ring=ring.cut(Part.makeCylinder(p['m3_clearance']/2,t,pivot_point,inward))
        assert abs(ring.common(wall.Shape).Volume-ring.Volume)<0.05
        for angle in range(0,91,15):
            opened=shutter.Shape.copy()
            opened.rotate(pivot_point,V(0,1,0),angle if rear else -angle)
            clear(opened,[b for b in bodies if b!=shutter],label+' shutter sweep '+str(angle))
        opening_projection=Part.makeBox(20,6,5,V(slot_x,d-1 if rear else -3,z-2.5))
        assert opened.common(opening_projection).Volume<0.05
        checks.append(label+': 100 mm2 opening, supported pivot, clear at 90 degrees and through sampled swing')

    # Filament can leave the split eyelet sideways through the full lid thickness.
    guide=doc.Filament_Exit_Guide
    guide_center=guide.Placement.Base
    probe=Part.makeBox(w-guide_center.x+2,2.4,t+6,V(guide_center.x,guide_center.y-1.2,h-4))
    clear(probe,[doc.Top_Lid,doc.Filament_Exit_Guide],'Filament side-release route')
    checks.append('Filament side-release route: 2.4 mm probe')

    # A full-size spool has a clear vertical loading corridor between the rails.
    spool_width=p['spool_width']
    spool_diameter=p['spool_diameter']
    spool_bottom=p['axle_height']-spool_diameter/2
    loading_path=Part.makeBox(spool_diameter,spool_width,lid_top-spool_bottom+1,
                             V((w-spool_diameter)/2,(d-spool_width)/2,spool_bottom))
    loading_parts=('Spool_Axle','Spool_Bushing_1','Spool_Bushing_2')
    clear(loading_path,[b for b in fixed_bodies if b.Name not in loading_parts]+open_latches,
          'Spool loading corridor')
    checks.append('Modeled spool clears the enclosure during vertical loading')

    for rear in (False,True):
        panel='Rear_Upper' if rear else 'Front_Upper'
        track=doc.Axle_Track_Right if rear else doc.Axle_Track_Left
        for x in (w/2-12,w/2+12):
            for z in (260,315,350):
                bore('Axle track '+panel+' '+str(x)+' '+str(z),
                     (x,d+0.1 if rear else -0.1,z),(0,-1 if rear else 1,0),t+8.2,
                     [panel,track.Name])
        # Each journal occupies 3 mm of the track depth at the support shoulder.
        axle=doc.Spool_Axle.Shape
        rail=track.Shape.BoundBox
        seated_y=rail.YMin if rear else rail.YMax-3
        journal=Part.makeBox(14,3,8,V(w/2-7,seated_y,p['axle_height']-4))
        assert abs(axle.common(journal).Volume-journal.Volume)<0.05
    checks.append('Both axle journals engage 3 mm of their tracks')

    expected=math.pi*((31.5**2-6.3**2)*2+(27.2**2-6.3**2)*10)
    assert all(abs(doc.getObject('Spool_Bushing_'+str(i)).Shape.Volume-expected)<0.01 for i in (1,2))
    checks.append('Original 54.4 mm spool bushings unchanged')
    return checks
