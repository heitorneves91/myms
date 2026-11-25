# Hardware, control plan and operating evidence

Current consolidated inventory and planning context. This is not a finished electrical schematic, purchasing BOM or operating approval. The first software prototype is documented separately in [FIRMWARE.md](FIRMWARE.md). Read [PROJECT_STATE.md](PROJECT_STATE.md) for the current mechanical milestone and explicit deferrals. All original nuance and historical numerical examples remain in the [initial archive](history/INITIAL_PLANNING_HANDOVER.md).

## Confirmed hardware and measurements

| Item | Owner confirmation / inspected geometry | Still unknown |
| --- | --- | --- |
| Printer/software | Bambu P1S, FreeCAD 1.1.4, Ubuntu 24.04 | Installed slicer profile/version settings for future print recommendations |
| Enclosure filament | Voolt3D ABS, purchased | Exact formulation and verified thermal/print guidance |
| PTC + fan | 24 V, 120 W, four separate wires; circular grille is hot outlet | Fan voltage/current/polarity, cold-start current, mounting-tab ratings |
| PTC CAD | 60 × 60 × 39 mm body, 88 mm tab span; outlet projects 2.5 mm, complete bounds 88 × 60 × 41.5 mm | Physical tab/material temperatures under load |
| Cup | Owner confirmed model dimensions: 95 mm cylindrical body, 127 mm height; modeled lip bounds ~102.83 mm | Grade, complete perforation pattern/open area, actual mounting arrangement |
| Cup holes | Approximately 6 mm side holes and 3 mm bottom holes, owner-confirmed | Counts/pitch; holes are absent from CAD and must not be inferred from its solid surface |
| PSU | External enclosed 24 V / 10 A power brick; output lead marked 18 AWG, barrel/P4 plug | Sustained/surge capability, metallurgy/length, exact barrel size/rating, final connector choice |
| MCU | ESP32-C3 SuperMini USB-C, bought as part of electronics shopping | Exact board/pinout/power behavior |
| Switching | D4184/dual-MOSFET module, advertised ~15 A / 400 W | Actual PCB current/thermal rating, 3.3 V compatibility, default-off behavior, fan driver arrangement |
| Buck | LM2596 adjustable module | Actual board dimensions, verified 5.0 V setting, USB power interaction |
| Sensors | DS18B20 TO-92 package; two planned locations | Authenticity, actual dimensions/pinout, final thermal-map locations |
| Spool | Owner calls it Bambu standard, approximately 200 mm OD and 55 mm bore | Total width not measured; CAD allows 75 mm width and 210 mm OD |
| PTFE fitting | None purchased; owner intended a small hole | No purchased bulkhead is required by present design |
| Mounting hardware | Owner explicitly has not bought heater/cup mounts | Clamp, bracket and low-conductivity support selection/dimensions |
| Thermal cutoff | Not purchased; selection explicitly deferred for mechanical work | Device, location, trip behavior and suitable DC rating |

Heater tab slots are centered at original XY (38,24) and (-38,-24), approximately 6 × 4 mm. Fan inlet is original +Z; hot outlet is original -Z, diameter 53 mm. See [BUILD_GUIDE.md](BUILD_GUIDE.md) for coordinates and the native source audit.

## Electrical plan and unresolved selections

Nominal heater load is 120 W / 24 V = 5 A; cold-start current is not known. The 10 A PSU label provides nominal headroom but does not validate the complete cable/connector path. The owner has bullet connectors; replacing the barrel or using XT60 was discussed, not decided. Do not assign a barrel size, fuse value, connector purchase or fan supply rating by assumption.

Keep the AC/DC power brick and mains outside. Buck 24 V down to a measured 5.0 V for the MCU board's intended input; sensor bus supply/pull-up is planned around 3.3 V. Board USB simultaneous-power behavior, MOSFET grounding/isolation claims, boot states and wiring topology need inspection. No finished wiring diagram exists. A nominally isolated MOSFET board may not be isolated in the final wiring.

The two DS18B20s can share a 1-Wire bus by unique address; a 4.7 kΩ pull-up was discussed, not implemented. Preserve chamber/wall address assignment across reboot. The first firmware proposes configurable GPIO4 sensor, GPIO5 heater and GPIO6 **fan** inputs/outputs. These are **unverified wiring assumptions**; nothing is wired yet. The older GPIO6 button example is superseded. Verify straps, USB/JTAG, driver polarity and boot behavior before enabling the `dryer` build. Independent fan control needs its own appropriate switching arrangement. Wires in the demo are mechanically illustrative colors, not a pin assignment.

The chamber/cup may be far hotter locally than the air setpoint. Use suitable insulated leads, edge protection and mechanical strain relief, with fan/element wiring kept clear of sharp metal and moving fan parts. The [sensor/cable guide](SENSORS_AND_WIRING.md) documents the current external-loop route and the proposed direct passage; that passage is not implemented.

## Firmware and user interface: first implementation

Implemented 2026-11-24: [PlatformIO project](../firmware), [VS Code workspace](../myms.code-workspace), local authenticated phone/computer admin with live temperature chart, persistent DS18B20 role assignment, hysteresis heater control, fan pre-run/cooldown and latched sensor/overtemperature faults. No automatic cycle restart after reboot. Initial software targets are 25–55 °C (default 45 °C), with 65 °C air/wall trips; these settings have not been physically validated or tuned.

Owner confirmed nothing is wired. Default `monitor` reads sensors with physical output pins disabled; `simulation` supplies marked synthetic readings without driving outputs; `dryer` opts into the proposed configurable pins. All three compile. Computer controller/recorder tests and browser checks using mocked telemetry pass, but no firmware upload or board/thermal test has been performed.

Owner chose bounded on-device CSV sessions plus a computer-side recorder for longer tests. The admin can select sampling cadence and recording duration, download/delete sessions and provision home Wi-Fi. Device storage is not an archive; download CSVs into gitignored `measurements/` or another backed-up computer folder. See [FIRMWARE.md](FIRMWARE.md) for setup, password retrieval, limits, CSV schemas, API, assumptions and verification boundaries.

No display, BLE app, humidity sensor, fan tachometer, material profile library or complete electrical diagram was added. Software commands do not establish heater current, actual airflow or independent protection.

## Protection and temperature evidence

Owner explicitly asked to defer thermal cutoff selection and continue mechanical work. Respect that task scope. Independent overtemperature interruption, overcurrent protection, suitable connector/wire ratings and fan-failure handling remain unresolved prerequisites for powered validation; a firmware setpoint or PTC label does not establish them.

The old 70–80 °C NC thermostat suggestion was a conceptual graphic, not a selected device or universal safe trip value. Choose a device and mounting arrangement from actual temperatures/fault behavior and its DC switching suitability. The cup is a conducting/radiating deflector, not insulation. See [MOUNTING_CONCEPT.md](MOUNTING_CONCEPT.md) for the through-screw thermal-bridge correction.

Discussed initial chamber target: 55 °C, perhaps 60 °C after validation. The early PETG enclosure's 60 °C cap is superseded as a material assumption, not replaced by a measured higher ABS limit. No higher operating temperature has been validated. No physical prototype, dry-cycle result, temperature map, fault test or unattended-use evidence has been reported.

The pre-power test sequence remains: verify actual electrical ratings/polarity/default states, mount and independently protect the heater on a nonflammable setup, map cup/outlet/mount/fastener/wall/spool temperatures, test control/fan failure responses and cooldown, then supervise lower-temperature chamber tests. Two operational sensors alone do not characterize every hot spot. Printed material strength/creep and mounting conduction require measurements in the real assembly.

## Original filament problem and material limits

Owner's Voolt3D PETG HF Premium white produced worse finish and fragile ball-joint snap fits versus PLA on the P1S. Moisture is a hypothesis, alongside cooling, flow/temperature, layer orientation and fit/strain. Reported baseline: Generic PETG profile, 240 °C nozzle, 245 °C first layer, 80 °C bed, 16 mm³/s maximum flow. The exact White Dental variant was never confirmed.

Historical cooling changes and an 8 mm³/s follow-up were controlled experiments, not manufacturer instructions. Compare identical features before/after drying while changing one factor at a time. Original details, uncertain manufacturer/profile claims, historical BRL 274 cart and multipack prices remain in the archive; they are not a live BOM.

PETG drying around 55 °C for 6–8 h was discussed, along with other brands' 65 °C advice. No exact Voolt3D filament/spool drying specification was established; do not apply 65 °C universally. ABS, TPU and other materials need their own verified profiles and spool compatibility. Filament moisture, chamber RH and polymer strength are distinct observations.
