# Mechanical review and assembly guide

For the short current handover, read [PROJECT_STATE.md](PROJECT_STATE.md); for owner decisions and their rationales, read [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md). The final purchasing BOM is deferred.

## Decisions and reference audit

The owner confirmed on 2026-11-14 that the cup model's dimensions are correct and that the physical cup has approximately 6 mm side perforations and 3 mm bottom perforations. Those perforations are intentionally absent from the reference geometry; their pitch and total open area were not supplied. Do not use this solid reference as a flow simulation.

`cad/assembly/Hardware_References.FCStd` has two independent, valid, single-solid PartDesign bodies with editable feature histories:

| Body | Geometry, mm | Evidence |
| --- | --- | --- |
| MetalDiffuser | 95 cylindrical diameter, 127 height, modeled bounding diameter ~102.83 | Owner confirmed dimensions; lip fillet exceeds nominal 100 mm lip sketch |
| PTC | 60 × 60 × 39 body; 88 total tab span; outlet projects to -2.5 | Inspected native sketches and final BRep |
| Heater tabs | slot centers (38,24) and (-38,-24) in original XY plane; approximately 6 × 4 slots | Inspected native sketch; mounting face at Z=0 |
| Hot outlet | diameter 53 on original -Z face | `HotAirOut` feature and owner outlet identification |
| Fan inlet | original +Z face, diameter 58 surrounding central fan representation | `Fan` feature |

The heater is rotated so its outlet points along +X. Fan inlet is at X≈23, outlet at X≈64.5. Cup mouth is at X=80, cup base at X=207; centerline is Y=75, Z=65. There is no required cutting of the cup. Its mouth faces the heater, with the perforated base downstream.

## Dimensions and intended operation

- Chamber outside: 240 wide × 150 deep. The 10 mm wall panels leave a 220 × 130 mm interior before mounts. The floor runs from Z=-7 to 3, the walls end at Z=365, and the 10 mm lid ends at Z=375. Closed height including the feet and hinges is 391.5 mm.
- Spool axle at X=120, Z=250, parallel to Y. Front and rear walls carry the paired rails. The axle is 120 mm long including both journals.
- Envelope: 210 mm spool diameter, 75 mm width, approximately 55 mm hub bore. Owner's spool is approximately 200 mm diameter and 55 mm bore; **width remains an allowance, not a measurement**.
- 12 mm fixed axle, rectangular end journals, 12.6 mm bushing bore, 54.4 mm bushing outside diameter. The spool and bushings rotate around the fixed axle. Hub variation can require new bushings.
- The loaded axle lifts out through the open top. Two rear pin hinges retain the lid, and two front turnbuttons release by hand. Hinge leaves remain permanently bolted to the lid and rear wall; no screws need removing during spool changes. The front overhang has a finger grip. Open both turnbuttons, then lift the front of the lid. The hinges have 3.2 mm pin bores; use retained M3 pins/bolts, not printed snap pins.
- Each vent has a 20 × 5 mm opening (maximum 100 mm²) and a pivoting shutter. Loosen, rotate, and retighten. The pivots now sit on solid wall, 12 mm beside each opening, and the shutters clear the openings when rotated 90 degrees. This area is experimental; it was not calculated from fan pressure, exchange flow, or moisture release.
- The filament guide is on the lid at X=220, Y=75, toward the right-hand tangent of a 200 mm spool. A 2.8 mm side-release slot continues to the lid edge and through the locating lip. The removable guide has a matching side opening and rounded contact edges. Slip the filament out sideways before opening the lid if it is connected to the printer. Spool diameter and wound-filament diameter change the tangent angle; the rounded guide accommodates direction changes but still needs a physical pull-force check. The collar is a removable locating fit, not a claimed snap lock.
- A proposed heat-rated partition separates lower heater suction on the left from the cup on the right. Air from the cup can rise around the spool, return down the left, and enter the fan. The side/bottom partition gaps permit leakage; this is a proposed flow route, not a proven circulation rate.
- The small fresh-air inlet is at the lower front right, away from the fan suction. The exhaust is at the upper rear left.

## Print and fit sequence

1. Print the three `Track_Coupon` variants and axle first. Coupons have 14.3, 14.5, and 14.7 mm channels; the production rail uses 14.6 mm. Check ABS shrinkage and journal engagement. Print one bushing and check the physical spool bore and rotation.
2. Print a shutter and filament guide. Check pivot friction, guide bore, and collar fit. Clear stringing inside the guide; the filament should pull freely without scraping.
3. Print enclosure panels flat, printed ribs/lips facing up. Corner battens lie flat on their broad face. Axle STL lies horizontally; use support only where needed under journals. Bushings stand on their flanges. Electronics pod prints open side up; its carrier and lid print flat. STL orientation is already applied. Inspect support requirements under the hinge knuckles and the offset air-sensor cradle; these features are not claimed to print without supports.
4. Use the purchased ABS. Set sparse infill, wall loops, and top and bottom layers in Bambu Studio. The owner compared the 10 mm upper front plate at 5% sparse infill and reported roughly 25% more material for that plate. Check the sliced broad panels for top coverage, brim placement, P1S exclusion regions, holes, and warping.
5. Dry-assemble the shell and rails before printing all remaining panels. All M3 clearance and pivot bores are 3.2 mm, as requested. Insert receiving pockets are 4.0 mm diameter. Pocket depth is 5 mm by default and 4 mm in the short electronics-carrier bosses; both depths are parameters. Use inserts whose outside geometry and length suit those pockets. There are no 2.5 mm screw-forming pilots in this revision. Trial the actual insert installation in a spare piece before the large parts.

These are cold mechanical prototypes. Coupon success does not validate printed strength at drying temperature.

## Assembly order

See the [illustrated sensor and cable guide](SENSORS_AND_WIRING.md) for sensor body placement, tie routing and the current external wire loop into the electronics pod. The dedicated chamber opening and cover slots are not yet an aligned direct passage.

1. Fit suitable M3 heat-set inserts into the 4 mm diameter pockets before enclosing the supports. Use inserts in corner battens, seam bridges, electronics lid bosses, carrier bosses and latch brackets. Keep nuts and washers for through-bolted tracks, pod attachment, sensors and hinge leaves. Place the four lower corner battens inside the lower wall panels. Batten front/rear insert pockets align with wall screw heights 21 and 117 mm; side insert pockets with 31 and 107 mm. Fit the four feet under the base at X=16/224, Y=16/134, and run base screws through feet and base into batten ends.
2. Attach the upper panels, upper corner battens, and front/rear center seam bridges. Batten joints at Z=190 are staggered from the panel seam at Z=135. Bridges span Z=105–165. Their screws pass through the matching wall center holes at X=120, Z=117 and 153; the previous unused center holes at Z=21 and 347 have been removed. Insert pockets open toward the wall on both bridges. Use optional thin silicone sealing strips/tape on flat seams, keeping sealing material away from the hot zone.
3. Attach front and rear axle tracks through the matching wall holes at Z=260, 315, and 350, X=108 and 132. Use M3 through bolts, washers, and nuts. The channel faces inward. Check each rectangular journal rests in its pocket and cannot turn.
4. Slide bushings into the spool hub and put the axle through them. Lower the complete spool assembly into both tracks. Check rotation and filament feeding by hand with the lid closed.
5. Mount `Sensor_Mount_1` on the upper rear left. Place the sensor body in the recessed cradle at the end of the offset arm. Run a small tie down one body slot, underneath the raised cradle, and back up the other slot. Use the projecting base ear and its relieved tie slots for wire strain relief. The cradle holds the sensor away from the wall in chamber air. `Sensor_Mount_2` is a wall-contact clip: put the sensor body in its central window with the flat face against the target wall, retain it between the raised locators, and tie it through the paired slots. Route the rear of the body tie along the U-shaped groove around the contact window, leaving the flat sensor-to-wall interface unobstructed. Both mounts have lead-exit notches and a separate relieved cable-tie path. Insulate all leads individually; the tie grips the body, not bare leads. Current seats allow approximately 5.2 × 6.2 mm body envelopes and must be checked against the purchased sensors. Final sensing positions require thermal mapping.
6. Install vent shutters with M3 bolts, broad washers, and locking nuts. Hand-adjust the pivot friction. Fit the split filament guide into the lid with its release slot facing the right-hand lid edge.
7. Attach electronics pod ears through the rear lower wall using four printed 8 mm spacers and M3 through bolts at X=57/179, Z=37/89. Screw the removable carrier to its internal bosses. Cable-tie boards through carrier slots; dimensions and PCB holes are deliberately not guessed. Verify board/terminal clearance and tool access before wiring. Fit the lid using its four corner screws.
8. Route protected low-voltage wiring through the lower rear rectangular opening, using a suitable grommet/sleeve and mechanical strain relief. Lid slots allow wiring to enter the external pod. Keep the external power brick outside.
9. Bolt the rear hinge frame leaves to the rear wall and the moving leaves to the lid. Insert and retain their M3 pins. Bolt each front latch bracket to the wall from inside, and fit a turnbutton to its top insert. Set pivot friction so the turnbuttons move by hand. Swing each button outward 180 degrees to clear the lid; swing inward to retain it. There is 0.5 mm geometric clearance over the lid, so this is a retaining catch, not a gasket-compression latch. No lid screws need removing to open it.
10. Install and verify the separately selected metal/ceramic heater and cup support system **before** operating. These proposed reference parts are excluded from the ABS STL exports.

Final screw lengths and the purchasing BOM are deferred at the owner's request. Select lengths from the actual clamped stack, washers, nut height or insert engagement, and available blind-pocket depth. In particular, do not reuse the earlier 6–8 mm receiving engagement suggestion: the revised insert pockets are only 5 mm deep (4 mm for the carrier), and screws must not bottom out in them. Printed feet leave clearance for fastener heads underneath.

## Hardware and release blockers

Update: no mounting hardware has been bought. See [the revised independent mounting concept](MOUNTING_CONCEPT.md). The current ceramic tube/through-screw and integral band/foot references are placeholders and are superseded as a mounting recommendation. Thermal cutoff selection is deferred for this mechanical design step at the owner's request.

Already specified by the owner: PTC+fan, cup, external PSU, controller, MOSFET, buck, sensors, ABS. The following are mechanically necessary but **not confirmed in the purchased inventory**:

- M3 machine screws, compatible 4 mm-pocket heat-set inserts, washers and nuts; sealing material if dry storage is required.
- Heat-rated insulating spacers, heater tab fasteners, and an independently supported cup mounting system. The model includes proposed ceramic spacers, a metal partition with feet, and metal band/saddle envelopes. They are **design studies**, not fabrication drawings or off-the-shelf part specifications. Bands need a clamping mechanism and actual stock dimensions; solid ring references are not complete clamps.
- Protected wiring, grommets and mechanical strain relief, suitable DC fuse/holder and connector, and an independently rated overtemperature cutoff with a defined mounting arrangement.

The enclosure geometry is reviewable and the ABS STL files are exportable. A complete appliance manufacturing release is blocked on the actual heat-rated mounting hardware and protection devices. Avoid ordering/custom-fabricating the proposed metal references without resolving those details. Current floor mounting holes can be revised to match available mounts.

## Verification and physical test plan

`exports/prototype/validation.json` records solid validity, one connected solid per printed part, closed STL meshes, print bounding dimensions, printed-part intersections, and intersections between printed components and all reference solids. The build fails on these checks. Exact face contacts are allowed. The [CAD workflow](CAD_WORKFLOW.md#relevant-verification) lists the fastener, sampled motion, vent, filament path, and spool checks. Structural load, fastener head and nut clearances, insert retention, routing, friction, heat, airflow, and printed tolerances require physical verification.

Before power: verify the actual mount pattern, cup perforations, fan orientation, fan voltage, wiring polarity, connector/fuse ratings, independent fan wiring, and the independent thermal protection. Test heater and cup on a nonflammable setup first; map outlet, cup, mount, fastener, wall and spool temperatures. Confirm fan-failure and control-failure protection. Then test the assembled enclosure under supervision, starting below the intended setpoint. Determine operating temperature from measurements and the actual materials, not from ABS's name or the software setpoint.

Before feeding a print: check the loaded spool's pull force through the closed box, including travel and rubbing at the exit. Adjust bushings or use a bearing support if friction is excessive. Before relying on passive storage, test leakage at the seams, shutters, guide, and wire entry; this prototype does not claim an airtight seal.
