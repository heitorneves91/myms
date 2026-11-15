# MYMS — Current Project State

**Updated:** 2026-11-14, through sensor illustrations, cable-routing questions and the FreeCAD/3MF discussion. This document replaces the former root `PROJECT_HANDOVER.md`. Repository: https://github.com/heitorneves91/myms. Documentation and CAD/code names are English.

## Read this first

MYMS is a DIY single-spool active filament dryer/feed box for a Bambu P1S, printed in purchased Voolt3D ABS. It now has an editable **mechanical review prototype**, not just reference hardware. It has not been physically or thermally validated. The owner wants practical CAD work, is learning FreeCAD, and appreciates explanations using real model illustrations.

Status meanings: **owner-confirmed** = explicitly stated; **implemented** = present in current files; **assumed** = layout allowance; **proposed** = discussed but not built/selected; **deferred** = explicitly left for later. A valid mesh is not a tested appliance.

| Need | Focused context |
| --- | --- |
| Why a choice was made; accepted versus proposed | [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) |
| Source files, model structure, rebuilding, checks, 3MF/STL | [CAD_WORKFLOW.md](CAD_WORKFLOW.md) |
| Printing, assembly, fit and current fastening scheme | [BUILD_GUIDE.md](BUILD_GUIDE.md) |
| Sensor illustrations and exact existing cable openings | [SENSORS_AND_WIRING.md](SENSORS_AND_WIRING.md) |
| Unfinished heater/cup supports and thermal-bridge correction | [MOUNTING_CONCEPT.md](MOUNTING_CONCEPT.md) |
| Inventory, electrical/control plans, material/thermal evidence | [HARDWARE_AND_CONTROL.md](HARDWARE_AND_CONTROL.md) |
| Full original planning history and old troubleshooting/costs | [history/INITIAL_PLANNING_HANDOVER.md](history/INITIAL_PLANNING_HANDOVER.md), only when needed |

Do not load every document by default. Current owner instructions and focused current documents supersede the historical snapshot. The initial snapshot was reconstructed from a Portuguese planning conversation, not a verbatim transcript; no raw account export or complete original chat is included.

## Current artifacts and verification

- [Main CAD](../cad/assembly/MYMS_Prototype.FCStd): separate native printed bodies in positioned Part containers. There are **no Assembly Workbench joints**, automatic mates or solver. Sketches use mostly fixed geometry, not a fully dimension-expression-driven model.
- [Original hardware CAD](../cad/assembly/Hardware_References.FCStd): preserve. Renamed and moved from root `myms.FCStd` at the owner’s request; its CAD contents are unchanged. It has the owner's editable heater/cup histories. Main-CAD references copy only final shapes; regeneration still reads the original.
- [Sensor demo CAD](../cad/assembly/Sensor_Mounts_Demo.FCStd): actual mount copies plus illustrative sensor bodies, ties, leads and screws. It is explanatory reference hardware, not extra printable bodies. The owner explicitly praised this form of demonstration.
- [Parameters](../cad/parameters.json), [generator](../scripts/build_model.py), [mechanism checks](../scripts/validate_mechanisms.py) and [runner](../scripts/build.sh) reproduce the model. The generated spreadsheet is informational only; changes there do not drive geometry.
- [Exports](../exports/prototype): **52 STL files = 49 assembly bodies + 3 fit coupons**, plus a printed-assembly STEP. Current [validation report](../exports/prototype/validation.json): all exported parts valid, single-solid and closed; no reported printed/printed or printed/reference intersections; **60 mechanism-check entries**. [Sensor report](sensor-demo-checks.txt): six additional envelope/tie/lead-route checks. No physical print, fit, heating or drying results have been reported.
- Views: [closed](assembly.png), [lid open](lid-open.png), [cutaway](cutaway.png), [sensor demo](sensor-mounts-demo.png). Main CAD saves closed. Sampled motion checks cover lid 0–110 degrees and catches 0–180 degrees, not continuous-motion proof or actual fastener hardware.

## Geometry and choices to preserve

| Topic | Current state and reason |
| --- | --- |
| Enclosure | 240 × 150 mm wall footprint, 3 mm walls, Z=365 wall height. Panels split at Z=135 for printing. Corner-batten joints stagger at Z=190. Keep printability/ABS warping and bed exclusion regions in mind. |
| Overall allowances | Closed hardware reaches about Z=371.5, feet Z=-6; rear pod Y=199, front catches about Y=-16.5. Leave opening clearance above/behind. The wall footprint is not the full appliance envelope. |
| Spool | Owner: Bambu standard, ~200 mm OD, ~55 mm bore. CAD: 210 mm OD and **assumed 75 mm width** to allow some variation. Width is not a measured owner dimension. |
| Axle/bushings | Fixed 12 mm axle, rectangular journals, front/rear tracks; 12.6 mm bushing bore, 54.4 mm hub OD (27.2 mm radius). Bushings/spool rotate around the axle. Owner explicitly said keep the current loose fit; different spool hubs can get replacement bushings. |
| Lid | Two permanently attached rear pin hinges, two front finger-operated turnbutton catches, finger grip and locating lips. No screws removed during spool changes. Catches retain with 0.5 mm gap; they are not gasket-compression latches. |
| Filament | Owner has no PTFE fitting. Rounded split guide on lid at X=220, Y=75, near a 200 mm spool's tangent. Matching 2.8 mm slot exits the right edge and clears the lip so filament can be freed sideways before opening. Previous rear-wall fitting is gone. |
| Fasteners | **3.2 mm M3 clearance and pivot bores** and **4.0 mm insert-pocket diameter** were explicitly requested. The generator assumes 5 mm pocket depth / 4 mm carrier depth; the owner did not specify those depths. Old 3.4 mm clearances and 2.5 mm pilot scheme are superseded. Inserts coexist with nuts/washers according to access. Final purchasing BOM is deferred. |
| Seams | Corrected wall/bridge centers at X=120, Z=117 and 153 on front and rear. Old unused middle holes at Z=21 and 347 were removed. |
| Vents | One 20 × 5 mm opening per intake/exhaust, **100 mm² each**, not an airflow calculation. Shutter pivots moved out of the openings onto solid wall 12 mm away; exhaust shifted to clear a batten. Both open at 90 degrees. |
| Sensors | `Sensor_Mount_1`: raised air-sensor cradle with body tie and cable tie ear. `Sensor_Mount_2`: flat-face wall-contact window with lead notch and rear U-shaped tie groove that avoids the contact face. Both have lead/tie clearances; individually insulate leads. Illustrative wire colors are not pin assignments. |

## Heater, cup and unfinished mounting

Owner's heater: **24 V, 120 W**, four wires with separate fan feed; circular grille is the hot outlet. The modeled body is 60 × 60 × 39 mm, tab span 88 mm, total Z extent 41.5 mm including outlet. Owner's cup: **95 mm barrel diameter, 127 mm length**, modeled lip bounds ~102.83 mm; owner confirmed dimensions and approximately **6 mm side / 3 mm bottom perforations**. Perforations are deliberately absent from the reference model; their pitch/count/open area are unknown.

Current layout: common centerline Y=75, Z=65. Heater outlet points +X at X~64.5; fan rear at X~23. Cup mouth at X=80, base at X=207. The ~15.5 mm outlet/mouth gap is geometry, not a verified safe clearance. A lower metal partition suggests an internal return path but leaks and has no measured flow/thermal result. Horizontal layout supersedes old vertical concepts; no cup modification is required in current CAD.

**No heater/cup mounting hardware has been bought.** The owner considered direct PTC-tab mounting to ABS. Recommendation is independent heater/cup supports, possibly unlined pipe clamps and suitable low-conductivity standoffs plus separate heater brackets. The CAD still contains **superseded mounting-study shapes**: two 10 mm heater spacers, four 9 mm partition feet, four 11.2 mm cup feet, two identical band/saddles and the metal partition. These are not selected commercial hardware, not ceramic cups, and not printable ABS fixtures. A ceramic tube does not stop heat flowing through a continuous metal screw. Replacement support geometry and actual dimensions remain open; see the mounting concept before changing them.

## Cable routing: existing versus proposed

Implemented: `Rear_Lower` has a **14 × 8 mm** opening at X=28–42, Z=38–46. `Electronics_Lid` has **two 18 × 8 mm** slots at X=104–122, Z=90–98 and 30–38. The pod's wall-facing base has no matching hole. The current route therefore loops outside the pod into its removable cover; an aligned direct passage, liner seat, cable anchors and sealing are **not implemented**.

Recommendation, not yet an approved routing change: align chamber/pod-base openings through the 8 mm stand-off gap, add appropriate edge protection and separate strain relief, and size from actual insulated bundle and connector dimensions. Do not use the air vents or rely on a tight raw ABS hole. No manual cutting was prescribed. Sensor illustrations only refined the sensor mounts; they did not fix the box-to-pod passage.

## Export preference and editing caution

Owner normally exports selected FreeCAD printable bodies together into **a single 3MF**, then arranges/slices in Bambu Studio. STL is not better and is optional. The generator's individual STLs have suggested print orientations and minimum Z=0; FCStd/STEP retain assembly placements. FreeCAD 3MF geometry is not a configured Bambu project. No automatic 3MF exporter or printer/filament/process profile exists here. Do not imply the owner must switch workflow or that removing STL outputs was requested.

Inspect for manual FreeCAD changes before regenerating: the script replaces the generated document rather than merging edits. Use FreeCAD's bundled Python via `bash scripts/build.sh`; `--render` also updates previews and the separate sensor demonstration. Do not regenerate CAD or exports for a documentation-only change. See the workflow file for limitations and exact check coverage.

## Explicit deferrals and next discussion points

- **Thermal cutoff:** not purchased; owner asked to ignore selection for the current mechanical work. Continue independent CAD work without repeatedly blocking on it. No powered/thermal approval follows from deferral.
- **Final fastener BOM:** owner deferred it. Earlier provisional counts/lengths are not a current shopping list, especially after hinge/latch additions and blind insert-pocket changes.
- **Open mechanical work:** select and dimension real heater/cup supports; discuss the aligned protected cable route and measure bundle/connectors; check physical sensor fit, lid/hinge/pivot fit, spool pull force and shell assembly when prototypes exist.
- **Optional organizational work:** component definitions/links and a real joint-based FreeCAD assembly were discussed as easier to maintain, not requested as an implemented refactor.
- **Later electrical/firmware/testing:** ESP32 phone web UI with no display, independent fan operation and cooldown, local fault handling, protected 24 V system and physical thermal/drying tests remain plans. Initial 55 °C, perhaps 60 °C, is discussion context, not a validated operating envelope.

When a new owner decision arrives, update its focused rationale and this summary if it changes the state. Keep the original planning archive for historical evidence rather than letting its old uncertainties override confirmed measurements.
