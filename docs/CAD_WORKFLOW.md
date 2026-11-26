# CAD sources, regeneration and verification

Read [PROJECT_STATE.md](PROJECT_STATE.md) first. This is the implementation guide, not a request to regenerate on every task.

## Files and ownership

| Path | Role |
| --- | --- |
| `cad/assembly/Hardware_References.FCStd` | Owner's original editable PartDesign heater/cup source; preserve |
| `cad/parameters.json` | Current generator inputs, mm |
| `scripts/build_model.py` | Generates the main native CAD and printable exports |
| `cad/assembly/MYMS_Prototype.FCStd` | Generated positioned mechanical prototype |
| `scripts/validate_mechanisms.py` | Alignment, sampled motion and functional geometric checks called by the build |
| `scripts/render_model.py` | Main closed/open/cutaway previews and initial visibility; saves the main file closed |
| `scripts/render_sensor_demo.py` | Separate sensor/tie/lead demonstration and reference-route checks |
| `cad/assembly/Sensor_Mounts_Demo.FCStd` | Illustrative hardware on copies of the actual mounts; not extra print parts |
| `exports/prototype/*.stl` | Optional individually oriented printable exports; 52 currently, including 3 fit coupons |
| `exports/prototype/MYMS_Printed_Assembly.step` | Printed bodies in assembly positions; no reference hardware |
| `exports/prototype/validation.json` | Last build's geometry and mechanism results; inspect/rebuild when relevant |
| `docs/sensor-demo-checks.txt` | Last demonstration's six body, tie and lead/cable checks |

The source reference contains two valid single-solid bodies: `Body` / `MetalDiffuser` and `Body001` / `PTC`. The generated hardware references are `PartDesign::Feature` shape snapshots. They include no source feature histories and are not live `App::Link` objects. The main file can open without the original, but the script requires it to regenerate.

## Modeling approach and limitations

- `Printed_Assembly`, `Hardware_References` and `Fit_Test_Coupons` are `App::Part` containers. The main printed group contains 49 bodies; 3 coupon bodies are in the separate hidden group. Each printed body has native sketches/pads/pockets, with fillets where used.
- The script places bodies by explicit `Placement`, not by Assembly Workbench joints. There is no solver, grounding hierarchy, automatic mating, or motion controller. Moving one body does not make neighbors follow. A container can move its children as a group.
- The names `Axle_Track_Left/Right` are historical names; the tracks actually mount to the front/rear walls with an axle parallel to Y.
- Sketch geometry is largely fixed with `Block` constraints. It is not a fully expression-driven dimensional constraint system. The generated `Parameters` spreadsheet is informational; editing it alone does not update shapes.
- JSON controls selected dimensions, but numerous mounting/layout coordinates, preview transforms and validation expectations are fixed to the present layout. Resizing shell/spool dimensions is an engineering change: inspect all affected coordinates and checks. Do not promise arbitrary resizing from one spreadsheet cell.
- Hardware occurrences were generated separately. Identical spacers/bands are repeated instances in a physical sense, but they are separate copied shapes in the tree. A later linked-component/joint refactor is an option, not an implemented feature or current mandate.
- Sensor demo references are approximate mechanical envelopes. Colored wires do not identify GPIOs or sensor pins. Main heater/cup hardware remains a mounting study.

## Commands and environment

For the **supplemental mounting retrofit**, use `bash scripts/build_mounting_retrofit.sh`. It reads/preserves the existing main CAD and creates only the new document, supplemental exports and previews. `bash scripts/build_mounting_retrofit.sh scripts/verify_mounting_retrofit.py` checks native reopening/recompute, saved GUI visibility and unchanged source hashes. See [MOUNTING_RETROFIT.md](MOUNTING_RETROFIT.md). Its four integrated bodies and 820 geometric/assembly checks are separate from the original 52 parts/86 mechanism checks below.

Owner environment: Ubuntu 24.04, FreeCAD 1.1.4 AppImage with bundled Python 3.11; host Python is different and may not import FreeCAD. Default image path is `/home/heits/tools/freecad`.

```bash
bash scripts/build.sh
bash scripts/build.sh --render
```

Override the image with `MYMS_FREECAD_APPIMAGE=/path/to/FreeCAD.AppImage`. The runner mounts it temporarily, uses its own `AppRun python` and library directory, and terminates its mount process on exit. Do not add a system FreeCAD package just to make host Python imports work.

The first command regenerates main CAD, STL/STEP and geometric validation without a GUI. `--render` also runs both render scripts, updates main previews and main opening visibility, and generates the sensor demonstration CAD/images/check report. Rendering requires a working display and can take noticeably longer than headless geometry; inspect outputs and process completion before reporting success.

Before regeneration, inspect `git status`, diffs and any user-edited CAD/source files. Generation creates a fresh document and replaces derived files; it does not preserve hand-edited features. Keep intentional manual work rather than blindly rebuilding over it. Do not launch scripts on every documentation-only change.

## Relevant verification

The last recorded build has **52 valid single-solid printable meshes**, no reported printed/printed or printed/reference volume intersections, and **86 mechanism-check entries**. The sensor demonstration adds **six checks** covering two sensor envelopes, body/wire tie paths and three lead/cable routes per sensor. These counts describe geometric checks.

Build checks include:

- BRep validity, one connected solid per exported part, closed mesh, and largest export dimension ≤246 mm. Actual current part bounds fit within 240 × 240 mm in their supplied orientation. Check bed exclusion zones/brims separately.
- Static solid intersections, allowing exact face contact and small numerical tolerances.
- Air-sensor arm/cradle profiles reach the original pad’s Y=16 bed edge, with the original open underside retained.
- Shell slab thickness, wall/batten and seam insert-axis alignment, and base/foot, track, hinge and latch fastener alignment.
- Turnbutton travel 0–180° every 15°, lid travel 0–110° every 5° plus 1–4° with turnbuttons open, and shutter swing 0–90° every 15°.
- Clear 100 mm² vent passages with shutters at 90° and solid wall around each pivot through the full wall depth.
- 2.4 mm axial and upward-release probes through the left-wall guide, 1.75 mm filament probes at ±15 degrees, a solid lid across the former port/slot, vertical spool loading clearance, axle journal engagement and original bushing volumes.

The demo script checks copied mount shapes against its illustrative sensor bodies, lead/wire paths and tie paths. For its geometry-only checks it supports `MYMS_DEMO_HEADLESS=1` inside FreeCAD's bundled Python. This does not render images or replace the main build checks.

After a CAD change, run the relevant generator/checks; inspect native reopening/recompute and visual previews where geometry/layout changed. Validate the final state rather than trusting a cached report. A failed run may have emitted some per-part files before the final assertions, so export presence alone is not success. Do not repeatedly broaden/re-run testing after successful checks without a new change or concern.

Checks do not establish continuous motion clearance, screw-head/nut clearance, installed insert retention, strength/creep, actual sensor fit, wire bending/anchoring, spool pull force, airtightness, airflow, heat distribution or safe operation. Native CAD and STL validity must not be described as appliance validation.

## Export workflow

Owner preference: open FreeCAD, select desired printed bodies, export them together as **one 3MF**, then orient/arrange/slice in Bambu Studio. Do not select hardware references or sensor-demo objects for printing. Fit coupons are optional.

Existing STL exports are convenience outputs, not a preferred format or a quality improvement over 3MF. `finish()` takes each body's local final shape, applies suggested rotations for selected parts, and translates its bounds to minimum X/Y/Z=0. Main FCStd and STEP keep assembly placements. A direct 3MF export of assembled bodies will therefore need arrangement/orientation; it does not automatically inherit STL rotations. Mesh quality depends on tessellation, not the extension. Current automatic mesh settings are 0.12 mm linear and 0.15 rad angular deflection, absolute.

The prototype generator does not produce 3MF files or configure printer, filament, or process profiles. A FreeCAD geometry export leaves those settings to Bambu Studio.

The regenerated enclosure uses a 10 mm slab for each chamber wall, the base, and the lid. The new upper front STL is 220 × 230 × 10 mm. Re-export selected bodies from the updated FreeCAD assembly when starting a new Bambu project.

## Display-state recovery

A headless `bash scripts/build.sh` save can omit `GuiDocument.xml`. On this FreeCAD version, reopening that document in the GUI restored containers, bodies and tips hidden despite valid BReps. The owner confirmed that showing them and fitting the view recovered the 10 mm model. Finish a generated revision with `--render`, which restores visibility and saves from the GUI, and verify GUI data exists in the final FCStd. Do not conclude that geometry is missing from a blank viewport or overwrite user edits just to restore visibility.
