# MYMS — Current Project State

**Updated:** 2026-11-26, through firmware 0.4.0 bounded sensor-free heater testing and the module-level electrical schematic. The original main CAD remains unchanged; the separate retrofit adds four integrated printed supports around purchased PEEK spacers. This document replaces the former root `PROJECT_HANDOVER.md`. Repository: https://github.com/heitorneves91/myms. Documentation and CAD/code names are English.

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
| Wiring diagram, required resistors/capacitors, LM2596 and MOSFET interface | [ELECTRICAL_SCHEMATIC.md](ELECTRICAL_SCHEMATIC.md) |
| PlatformIO setup, firmware/admin, sensor roles and temperature recordings | [FIRMWARE.md](FIRMWARE.md) |
| Full original planning history and old troubleshooting/costs | [history/INITIAL_PLANNING_HANDOVER.md](history/INITIAL_PLANNING_HANDOVER.md), only when needed |

Do not load every document by default. Current owner instructions and focused current documents supersede the historical snapshot. The initial snapshot was reconstructed from a Portuguese planning conversation, not a verbatim transcript; no raw account export or complete original chat is included.

## Current artifacts and verification

- **Owner-reported physical progress (2026-11-25):** all parts in `Printed_Assembly` have been printed successfully. Preserve these parts and their existing interfaces when redesigning the unfinished heater/cup mounting. No measured thermal or drying performance was reported. The owner cannot fabricate metal and authorized a redesign preserving existing prints, excluding foil and assuming no existing metal supports.
- **Supplemental mounting retrofit:** [MYMS_Mounting_Retrofit.FCStd](../cad/assembly/MYMS_Mounting_Retrofit.FCStd), [guide/BOM](MOUNTING_RETROFIT.md), [parameters](../cad/mounting_retrofit.json) and [generator](../scripts/build_mounting_retrofit.py). Four integrated native printed bodies reuse existing base holes; eight purchased PEEK M3 female/female 20 mm spacers separate hot/cold attachments. No fabricated bands/partition. Heater stays fixed; cup shifts +15 mm in X. Both source CAD hashes are unchanged. All 820 geometric/assembly checks and native GUI reopening/recompute pass. Procurement, actual hardware dimensions, contact on real cup perforations, friction-based cup retention, ABS/PEEK temperatures and changed airflow remain unverified. Cold-fit prototype only.
- **Manual firmware controls (0.4.0, 2026-11-26):** owner requested fan-only and fan-plus-heater starts from the admin. Implemented untimed manual modes with explicit Stop; fan-only works without sensors, while continuous heat uses the target field and both fresh assigned sensors. At the owner's subsequent request, missing sensors enable a separately labeled 20-second heater output test after 10 s fan pre-run, followed by at least 2 min fan cooling and continued manual fan operation. Repeated requests cannot extend the test; it is not temperature-controlled drying. Regulated heating still faults on sensor loss. Manual operation continues with the page closed; it never resumes after reboot. Mode transitions pass controller/browser tests, and all three PlatformIO environments compile. Physical outputs remain disabled in `monitor`/`simulation`; hardware validation is still outstanding. See FIRMWARE.md for behavior and `/api/manual`.
- **Electrical proposal (2026-11-26):** [two-sheet schematic, connection list and passive BOM](ELECTRICAL_SCHEMATIC.md). Owner confirms a 24 V fan and one TRIG/PWM plus GND per MOSFET board. Two modules provide independent channels. The purchased LM2596 supplies measured 5.0 V; shared DS18B20 pull-up is 4.7 kΩ, sensor supply decoupling 100 nF each. A proposed TC4427A buffer covers unverified direct-gate 3.3 V drive; actual module input/terminal circuit, fan current, fuse sizes and startup behavior remain unresolved. USB external-power link and deferred thermal-cutoff position are shown. No firmware or CAD regeneration for this work.
- **Access:** owner removed the admin/API login in firmware 0.4.0. Open the page directly; the computer recorder no longer prompts for credentials. The AP still uses `myms1234` (constant `AP_PASSWORD`). Old admin NVS keys are ignored without clearing settings/recordings. The lightweight mutation header remains, but anyone who can reach the device on its local network can control it.
- [Firmware](../firmware), [VS Code workspace](../myms.code-workspace) and [firmware guide](FIRMWARE.md): first ESP32-C3 software prototype with local admin without login, live chart, persistent sensor roles, hysteresis/fan/fault controller, bounded downloadable CSV sessions and [computer recorder](../scripts/record_temperatures.py). At initial delivery the owner confirmed nothing was wired and selected device CSV plus computer recording; later they reported a sensor attempt without its pull-up and NaN serial logs. Default `monitor` and optional `simulation` builds do not drive power outputs; `dryer` explicitly enables configurable proposed GPIOs. All three compile and computer-side tests pass; no agent-performed board upload or physical/thermal validation; the owner has not confirmed successful sensor readings or heater operation. Raw measurements default to gitignored `measurements/`. No CAD regeneration for this work.
- [Main CAD](../cad/assembly/MYMS_Prototype.FCStd): separate native printed bodies in positioned Part containers. There are **no Assembly Workbench joints**, automatic mates or solver. Sketches use mostly fixed geometry, not a fully dimension-expression-driven model.
- [Original hardware CAD](../cad/assembly/Hardware_References.FCStd): preserve. Renamed and moved from root `myms.FCStd` at the owner’s request; its CAD contents are unchanged. It has the owner's editable heater/cup histories. Main-CAD references copy only final shapes; regeneration still reads the original.
- [Sensor demo CAD](../cad/assembly/Sensor_Mounts_Demo.FCStd): actual mount copies plus illustrative sensor bodies, ties, leads and screws. It is explanatory reference hardware, not extra printable bodies. The owner explicitly praised this form of demonstration.
- [Parameters](../cad/parameters.json), [generator](../scripts/build_model.py), [mechanism checks](../scripts/validate_mechanisms.py) and [runner](../scripts/build.sh) reproduce the model. The generated spreadsheet is informational only; changes there do not drive geometry.
- [Exports](../exports/prototype): **52 STL files = 49 assembly bodies + 3 fit coupons**, plus a printed-assembly STEP. Current [validation report](../exports/prototype/validation.json): all exported parts valid, single-solid and closed, with no printed/printed or printed/reference intersections and **86 mechanism-check entries**. [Sensor report](sensor-demo-checks.txt): six additional envelope/tie/lead-route checks. The owner now reports all Printed_Assembly parts printed successfully; no quantified fit, heating or drying results have been reported.
- Views: [closed](assembly.png), [lid open](lid-open.png), [cutaway](cutaway.png), [sensor demo](sensor-mounts-demo.png). Main CAD saves closed. Sampled motion checks cover lid 0–110 degrees and catches 0–180 degrees, not continuous-motion proof or actual fastener hardware.

## Geometry and choices to preserve

| Topic | Current state and reason |
| --- | --- |
| Enclosure | 10 mm chamber walls, base and lid. The 240 × 150 mm footprint leaves 220 × 130 mm inside before mounts. The floor top is Z=3, walls end at Z=365, and lid top is Z=375. Panel seams are at Z=135 and batten joints at Z=190. Wall loops and infill are slicer settings. The owner reported roughly 25% more filament for the upper front plate trial at 5% sparse infill. |
| Overall allowances | Closed hardware reaches Z=378.5, feet Z=-13; rear pod Y=199, front catches about Y=-16.5. Leave opening clearance above and behind. |
| Spool | Owner: Bambu standard, ~200 mm OD, ~55 mm bore. CAD: 210 mm OD and **assumed 75 mm width** to allow some variation. Width is not a measured owner dimension. |
| Axle/bushings | Fixed Ø12 mm × 120 mm axle with rectangular journals and front/rear tracks; 12.6 mm bushing bore, 54.4 mm hub OD (27.2 mm radius). Bushings/spool rotate around the axle. Owner explicitly said keep the current loose fit; different spool hubs can get replacement bushings. |
| Lid | Two permanently attached rear pin hinges, two front finger-operated turnbutton catches, finger grip and locating lips. No screws removed during spool changes. Catches retain with 0.5 mm gap; they are not gasket-compression latches. |
| Filament | Owner has no PTFE fitting. Rounded, flared split guide fixed to `Left_Upper` at X=0, Y=75, Z=355, near a top tangent of the 200–210 mm spool envelope. A 2.8 mm upward release slot reaches the wall top; open the lid to free filament upward. The lid has no filament hole or release slot. The guide stays fixed during lid motion and is retained by two M3 screws into 4 mm wall insert pockets. |
| Fasteners | **3.2 mm M3 clearance and pivot bores** and **4.0 mm insert-pocket diameter** were explicitly requested. The generator assumes 5 mm pocket depth / 4 mm carrier depth; the owner did not specify those depths. Old 3.4 mm clearances and 2.5 mm pilot scheme are superseded. Inserts coexist with nuts/washers according to access. A dimensioned printed-assembly fastener BOM is now in BUILD_GUIDE.md; actual hardware selection and heater/cup fasteners remain open. |
| Seams | Corrected wall/bridge centers at X=120, Z=117 and 153 on front and rear. Old unused middle holes at Z=21 and 347 were removed. |
| Vents | One 20 × 5 mm opening per intake/exhaust, **100 mm² each**. Pivots sit on solid wall 12 mm from each slot. The exhaust is at X=38–58, Z=327.5–332.5 to clear its batten and hinge. Both shutters open at 90 degrees. |
| Sensors | `Sensor_Mount_1`: original open arm/cradle layout. Arm and cradle extend from local Y=2 to Y=16, flush with the first pad's long edge, for the owner's edge-down printing orientation. The STL applies that rotation. The earlier filled, base-down pedestal was a misunderstanding and is removed. Sensor seat, mounting hole and tie/wire routes are retained. `Sensor_Mount_2` is unchanged. |

## Heater, cup and unfinished mounting

Owner's heater: **24 V, 120 W**, four wires with separate fan feed; circular grille is the hot outlet. The modeled body is 60 × 60 × 39 mm, tab span 88 mm, total Z extent 41.5 mm including outlet. Owner's cup: **95 mm barrel diameter, 127 mm length**, modeled lip bounds ~102.83 mm; owner confirmed dimensions and approximately **6 mm side / 3 mm bottom perforations**. Perforations are deliberately absent from the reference model; their pitch/count/open area are unknown.

Original-main layout: centerline Y=75, Z=65; heater outlet X~64.5, fan rear X~23, cup X=80..207. **Supplemental retrofit:** heater unchanged, cup X=95..222, giving a 30.5 mm outlet/mouth gap and 8 mm cup-base/right-wall gap. The custom partition is omitted for a free-return baseline. No gap, circulation rate or temperature has been physically validated.

No new mounting hardware has been reported purchased. The original main CAD still contains superseded ceramic-foot/band/partition studies; do not print or shop for exact equivalents. The separate retrofit uses four integrated printed supports, eight commercially specified PEEK spacers and stock fasteners. PEEK is a purchased interface, not an ABS print instruction or thermal approval. See [MOUNTING_RETROFIT.md](MOUNTING_RETROFIT.md) for the source files, supplemental BOM and physical checks before ordering/printing.


## Cable routing: existing versus proposed

Implemented: `Rear_Lower` has a **14 × 8 mm** opening at X=28–42, Z=38–46. `Electronics_Lid` has **two 18 × 8 mm** slots at X=104–122, Z=90–98 and 30–38. The pod's wall-facing base has no matching hole. The current route therefore loops outside the pod into its removable cover; an aligned direct passage, liner seat, cable anchors and sealing are **not implemented**.

Recommendation, not yet an approved routing change: align chamber/pod-base openings through the 8 mm stand-off gap, add appropriate edge protection and separate strain relief, and size from actual insulated bundle and connector dimensions. Do not use the air vents or rely on a tight raw ABS hole. No manual cutting was prescribed. Sensor illustrations only refined the sensor mounts; they did not fix the box-to-pod passage.

## Export preference and editing caution

Owner normally exports selected FreeCAD printable bodies together into **a single 3MF**, then arranges/slices in Bambu Studio. STL is not better and is optional. The generator's individual STLs have suggested print orientations and minimum Z=0; FCStd/STEP retain assembly placements. FreeCAD 3MF geometry is not a configured Bambu project. No automatic 3MF exporter or printer/filament/process profile exists here. Do not imply the owner must switch workflow or that removing STL outputs was requested.

Inspect for manual FreeCAD changes before regenerating: the script replaces the generated document rather than merging edits. Use FreeCAD's bundled Python via `bash scripts/build.sh`; `--render` also updates previews and the separate sensor demonstration. Do not regenerate CAD or exports for a documentation-only change. See the workflow file for limitations and exact check coverage.

## Explicit deferrals and next discussion points

- **Thermal cutoff:** not purchased; owner asked to ignore selection for the current mechanical work. Continue independent CAD work without repeatedly blocking on it. No powered/thermal approval follows from deferral.
- **Fastener BOM:** owner requested the current list on 2026-11-22, superseding the earlier printed-assembly BOM deferral. BUILD_GUIDE.md records 90 screws, 34 locknuts, 126 washers and 56 inserts, with explicit sizing assumptions. Four under-lid hinge connections need rear-wall clearance relief; no CAD change has been made for that finding. Heater/cup fasteners and exact insert products remain unselected.
- **Open mechanical work:** procure/measure retrofit hardware, cold-fit the new supports and verify perforation contact, friction-based axial cup retention and thermal/flow behavior; discuss the aligned protected cable route and measure bundle/connectors; check physical sensor fit, lid/hinge/pivot fit, spool pull force and shell assembly when prototypes exist.
- **Optional organizational work:** component definitions/links and a real joint-based FreeCAD assembly were discussed as easier to maintain, not requested as an implemented refactor.
- **Electrical/firmware/testing:** the first firmware/admin/recording implementation now exists; GPIO4/5/6 are proposed configurable sensor/heater/fan pins, not verified wiring. Next: USB-only upload and sensor tests, independent fan-driver/electrical selection and actual default-off verification, then protected supervised thermal tests. Sensor wiring has been attempted without a pull-up and yielded NaN logs; no successful temperature or heater-switching test is confirmed. Initial 55 °C, perhaps 60 °C, remains discussion context, not a validated operating envelope; software currently offers 25–55 °C targets with initial 65 °C air/wall trips.

When a new owner decision arrives, update its focused rationale and this summary if it changes the state. Keep the original planning archive for historical evidence rather than letting its old uncertainties override confirmed measurements.

The earlier blank-view diagnosis was display-only: the headless-saved FCStd lacked `GuiDocument.xml`, and FreeCAD restored its objects hidden. Showing containers, bodies and tips restored the model without geometry changes. The owner confirmed the recovery worked. Finish generated revisions with a GUI/render save; a later headless build can overwrite that display state again.
