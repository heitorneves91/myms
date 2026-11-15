> HISTORICAL SNAPSHOT — pre-CAD planning, superseded by [current project state](../PROJECT_STATE.md).
> Load only for historical detail; do not apply its unresolved questions or old dimensions as current instructions.
> The complete original root handover is retained verbatim below this banner. Later corrections and owner decisions are in [DESIGN_DECISIONS.md](../DESIGN_DECISIONS.md).
> Later relocation: the original hardware source called `myms.FCStd` in this snapshot is now [cad/assembly/Hardware_References.FCStd](../../cad/assembly/Hardware_References.FCStd). Historical text below is unchanged.

# MYMS — Complete Engineering Conversation Handover

**Project:** `myms` — affordable, custom, single-spool active filament dryer / feed box (inspired by AMS-style dryness management, **not** a multi-material automatic changer).

**Repository:** https://github.com/heitorneves91/myms

**Prepared:** 2026-11-14

**Language policy:** English for this document, all GitHub content, FreeCAD object names, code, and technical documentation. The original planning conversation was in Brazilian Portuguese.

**Important evidence boundary:** This is a carefully reconstructed **decision-oriented handover** from the conversation, **not a verbatim export** and **not a safety-certified or tested design**. Retain the original chat separately for full-fidelity context, images, prices, screenshots, and exact wording. Some prior assistant advice was tentative, inconsistent, or based on external specifications that have not been independently revalidated; this document marks those issues explicitly.

---

## 0. How to use this handover

- **CONFIRMED BY OWNER** = explicitly stated or purchased by the user.
- **DECIDED / LATEST PREFERENCE** = latest stated direction, subject to engineering feasibility.
- **PROPOSED** = concept or recommendation discussed, not fabricated or tested.
- **UNVERIFIED** = must be inspected, measured, or verified against manufacturer documentation.
- **SUPERSEDED** = historical suggestion; do not apply without a new decision.

This project is moving from high-level brainstorming to actual **FreeCAD CAD design**. Do not jump directly from a sketch to full printable STLs without verifying the existing hardware model and checking the physical layout.

### Highest priority facts, at a glance

| Subject | Latest information / status |
|---|---|
| Host operating system | Ubuntu 24.04 — owner-confirmed |
| CAD | FreeCAD 1.1.4 — owner-confirmed |
| Printer | Bambu Lab P1S — owner-confirmed |
| GitHub | `heitorneves91/myms`, public — owner-confirmed and publicly visible |
| Existing CAD | `myms.FCStd` is present in repo at handover; owner said the heater and stainless cup reference models have been drawn; **file contents not yet inspected by this handover** |
| Printed enclosure material | **ABS by Voolt3D, already purchased** — replaces early PETG enclosure plan |
| Heater | 24 V, **120 W PTC** (earlier drafts incorrectly referred to 100 W), integrated fan, **4 wires allowing separate fan control** |
| Heater nominal current | 120 W / 24 V = **5 A**, cold-start current unknown |
| PSU | Enclosed/external **24 V / 10 A** AC/DC adapter, purchased, **18 AWG** output lead with DC barrel/P4-style plug — actual continuous rating, barrel size, wire metallurgy, and surge capability unverified |
| Heater air output | Owner identified the circular grille of the PTC as the **hot-air outlet** |
| Heater orientation | **Horizontal/laid down**, toward the lower area, to avoid a tall box — later preference supersedes vertical concept drawings |
| Heater shielding | Perforated **stainless steel kitchen steamer cup/basket**, ~**95 mm diameter**, purchased; candidate shield/deflector, not insulating material |
| Controller | ESP32-C3 SuperMini USB-C, Wi-Fi and BLE; discussed/purchased as part of electronics shopping |
| Heater switch | D4184 / dual-MOSFET module advertised ~15 A / 400 W; hardware details to verify |
| DC/DC buck | LM2596 adjustable module, 24 V -> 5 V, may be a pack of five |
| Temperature sensors | **DS18B20** digital sensors, TO-92 style, purchased in multi-pack; planned two measurements |
| Spool support | **Removable center axle through spool hub, resting in tracks/slots on opposite box walls**, preferred over four rollers/bearings |
| Air circulation | **Primarily closed-loop recirculation** of chamber air through PTC; separate tiny remote fresh-air inlet and high humid-air exhaust, adjustable; do not aim fan suction at the outside-air vent |
| UI | **No display**. Wi-Fi web page served by ESP32, usable from a phone; jumpers/switches are acceptable fallback |
| Nominal drying setpoint | 55 °C initially, perhaps 60 °C; earlier limit of 60 °C was set for a PETG box, later enclosure changed to ABS. Higher operation needs physical validation, not merely a firmware setting |
| Filament problem that motivated project | Voolt3D PETG HF Premium white printed on P1S has poor finish/strength and ball-joint snap-fit failures relative to PLA; want to rule out moisture |

---

## 1. Origin and goals

The user was frustrated with switching from PLA to PETG: significantly worse surface quality and perceived lower mechanical strength. Previously robust **ball-joint snap-fit** features sometimes fractured in the PETG version, either by interlayer separation or across the material. The objective is to **rule out absorbed moisture as a cause**, while improving storage/print readiness.

The proposed appliance is a compact, DIY, active filament dryer for one standard **1 kg filament spool**, able to:

1. Heat and dry PETG and potentially other materials with material-appropriate temperatures/times.
2. Keep the spool enclosed and optionally feed filament directly to the Bambu P1S via a PTFE outlet.
3. Actively circulate hot air inside the box rather than continuously heating a large incoming outside-air stream.
4. Let moisture escape through small, preferably adjustable lower/upper external air exchange openings.
5. Run with safe temperature control via ESP32-C3 and independent hardware protection.
6. Optionally become a passive dry-storage box (vents closed and optional desiccant) when the heater is off.
7. Be mechanically printable in ABS on the Bambu P1S and easy to disassemble, maintain, adapt, and repair.
8. Avoid a commercial dryer purchase if possible; minimize cost and maximize learning, modularity, and functionality.

**Non-goal:** The term “mini AMS” is informal. No automatic filament switching, multi-spool mechanisms, motors, RFID, or motorized rewinding were specified. Do not assume AMS automatic loading or unloading is required.

---

## 2. Filament, existing printer, and original PETG problem

**Owner-confirmed filament and printer:**
- Bambu Lab **P1S**.
- Voolt3D **PETG HF Premium, white**, sold in Brazil. The assistant found a product labelled **PETG HF Premium White Dental**, but it was **not conclusively verified** that the owner bought that exact variant.
- Bambu Studio profile: **Generic PETG**, not necessarily the **Generic PETG HF** profile.
- User-stated print parameters: **240 °C nozzle**, **245 °C first layer**, **80 °C bed**, **16 mm³/s maximum volumetric flow**.
- Main failure case: snap-fits with ball joints, which worked acceptably in PLA but snapped or delaminated in PETG.

**Diagnoses discussed, all still hypotheses:**
- Absorbed water: bubbles, under-extrusion / intermittent flow, rough finish, weaker layer bonding.
- Excessive part cooling on small layers and/or auxiliary fan.
- Nozzle temperature, volumetric flow, and line speed interacting with bonding.
- Layer orientation, ball/socket interference, inadequate radii and high local snap-fit strain.
- PLA and PETG differing in stiffness, toughness, flexibility, and anisotropy; do not assume any one material is unconditionally stronger.

**Prior assistant claims worth re-checking before relying on them:**
- A Voolt3D white/dental HF page was paraphrased as 220–245 °C nozzle, 70 °C bed and up to 20 mm³/s; the exact material variant is not confirmed.
- Generic PETG cooling settings were previously described as 40–90%, while Generic PETG HF was described as up to 40%; **verify the installed Bambu Studio version and resolved filament profile** rather than trusting this statement.
- Suggested test profile: first 245 °C, other layers 240 °C, 80 °C bed, keep 16 mm³/s, part fan 20–40%, overhang cooling as needed (~60%), auxiliary fan 0%. These were experiments, not authoritative manufacturer settings.
- Suggested follow-up: reduce maximum volumetric flow from 16 to 8 mm³/s **only after** a controlled fan change if the failure remains; actual small-part flow may be below both caps.
- Print identical ball joints and compare failure behavior before/after drying, varying one factor at a time. Document fracture orientation and actual slicer speeds.

**Drying temperature history:** PETG drying was discussed around 55 °C for ~6 hours (some brands) or up to 65 °C for ~8 hours (some other brand profiles), but no verified single Voolt3D HF Premium white dryer specification was established. **Do not automatically set 65 °C as correct for this particular filament or spool.**

---

## 3. Important evolution of the project

This chronology prevents old sketches from overriding current decisions.

1. **Original concept:** one closed printable plastic box, 1 kg spool, heater (resistor/PTC), thermometer, tiny exhaust fan or slow humidity vent; maybe similar to a miniature AMS.
2. **Drying physics clarified:** heating alone inside a completely sealed, non-desiccated box is less effective because water vapour accumulates. Use airflow and controlled renewal; silica gel is optional for active drying and useful for storage.
3. **Heat source selected:** 24 V PTC with integrated fan; discussed 40/60/100/150 W initially. **Actual purchased unit is 120 W**, not 100 W.
4. **Controller selected:** ESP32-C3 SuperMini, DS18B20 sensors, MOSFET switching and LM2596 buck; no costly display; phone web UI planned.
5. **Power:** a 24 V / 10 A enclosed external AC/DC adapter purchased. A 150 W open-terminal supply was considered then not chosen; generic 10 A barrel-plug PSU was questioned. The final external PSU lead is marked **18 AWG**. The user owns bullet connectors and considered replacing the DC barrel, while a polarised XT60 was also discussed. **Connector replacement is not yet confirmed.**
6. **Enclosure material:** initially planned to 3D-print in PETG and cap operation around 55–60 °C, with worries about creep and local hot spots. Then **ABS Voolt3D was purchased** to print the enclosure, providing more thermal headroom. Original all-PETG box is **superseded**.
7. **Shielding and deflector:** initially drawn as a custom metal shield/heat duct. User does not want metalworking. Considered off-the-shelf metal items (perforated basket, utensils, aluminium box). Finally a **perforated stainless-steel steaming/kitchen cup, 95 mm diameter**, was found and purchased. It may be modified with a drill/Dremel *after* checking flow.
8. **PTC and deflector:** the user intends to leverage the PTC’s existing plastic mounting tabs, mount the PTC and potentially cup near ABS walls, and use the cup to redirect hot air. An assistant warned that metal can conduct heat through screws and advised independent or insulated mounting. Exact design remains **unresolved and must be validated**.
9. **PTC outlet direction:** user confirmed the **circular grille is the hot-air outlet**. An earlier drawing positioned a vertical PTC beneath an upside-down cup.
10. **Airflow critique:** user correctly observed a previous illustration lacked an obvious return-air path; a rising jet and tiny exhaust do **not** automatically create a well-defined recirculation loop. Later design should include a return path and avoid misleading arrows.
11. **Compactness:** user chose a **laid-down / horizontal PTC and cup** rather than stacking them vertically below the spool. **This is the latest preferred heater layout.**
12. **External air:** the heater should **pull primarily from inside the chamber**, with a small and separate exterior inlet located away from its suction. A small high exhaust lets out moist air; internal recirculation should dominate. **Do not put the fan directly against the outdoor-air intake.**
13. **Spool support change:** user proposed and preferred a **printed central cylinder/axle passing through spool center, supported by matching slides/tracks in the two side walls**. This **replaces** the earlier four rollers. Bearing-assisted axle is merely a future fallback if friction is high.
14. **CAD handoff:** user created actual reference CAD in FreeCAD and placed **`myms.FCStd`** in the public GitHub repository. Need inspect its actual contents. User requests all project materials in **English** from now on.

---

## 4. Physical hardware inventory and parameters

### 4.1 PTC heater and fan

- **CONFIRMED BY OWNER:** **24 V DC, 120 W nominal PTC** module, integrated fan, **4 separate wires**, allowing powering the fan independently of the element.
- **CONFIRMED:** circular grille is the **hot-air outlet**.
- **Approximate dimensions discussed from product images:** 60 × 60 × 42 mm body, ~87.5 mm including mounting tabs. **UNVERIFIED** until measuring the actual `.FCStd` geometry/part. Do not drill from an image.
- PTC cold-start current unknown. Nominal is **5 A**, but use the real module's datasheet or current measurements before choosing fuse/control device.
- Fan voltage and current **not independently confirmed**; confirm whether it is also 24 V, polarity, and min/max duty before wiring. User confirmed fan can run independently.
- Important: separate fan power means firmware can start fan first, switch element on/off, and keep fan on during cooldown. Hardware safety must not depend solely on Wi-Fi or firmware.
- Heater element may be dramatically hotter than target chamber air temperature. Keep airflow unobstructed; use rated independent thermal cutoff and robust barriers.

### 4.2 Stainless steel cup / cooking steamer

- **CONFIRMED:** purchased stainless-steel perforated cup/basket intended for cooking/steaming.
- **Approximate external diameter:** 95 mm (ask whether internal/external). Height, base geometry, wall thickness, hole layout, mounting options, and material grade have **not** been confirmed here.
- Its solid portions could deflect hot air, while perforations permit a portion of the flow. **It is a heat shield / deflector, not an insulator and not a thermal safety barrier.**
- Earlier concept: **upright heater** blowing into an **inverted cup** directly above it, air exits side perforations.
- **Latest preference:** **horizontal heater and horizontal or tilted cup**, lower in the enclosure to reduce height; use base/side of cup to redirect air upwards (needs actual CAD study). The user suggested cutting a slit/opening in the cup base and possibly covering some base perforations with aluminium, so the jet meets the end and turns upwards. **This is exploratory, not approved**: don't restrict the outlet, cover ventilation, or assume metal tape/foil is suitable without tests.
- The 95 mm diameter cup surrounding a nominal 60 × 60 mm square heater has only ~5 mm radial clearance at the four corners if concentric and coplanar (square diagonal ~84.9 mm). **This is not necessarily enough for airflow or thermally safe assembly.** A position above or adjacent to the heater may be preferable to enclosing its full square body.
- User is comfortable using a drill/Dremel to add holes if needed; drill after mapping required airflow and mounting, deburr all holes and protect cables.
- Do not let hot metal touch ABS; ensure thermal conduction through fasteners is considered. The original plastic PTC mounting tabs are **not automatically verified safe** merely because supplied on the product.

### 4.3 Power supply, connectors, wiring

- **CONFIRMED:** acquired **external enclosed AC/DC power brick 24 V, label 10 A (240 W)**. Previous assistant misread the photo as 15 A; user explicitly corrected it to **10 A**.
- PSU has a cylindrical DC barrel / "P4"-style plug; precise size (5.5 × 2.1 or 5.5 × 2.5 mm) unknown.
- Output cord marked **18 AWG** (~0.82 mm²), length not established; it may be stranded copper or copper-clad aluminium — verify if feasible.
- The owner has **bullet connectors** and considered cutting the original plug and soldering their own connector. **XT60** was also suggested as a mechanically polarised alternative. No final plug decision confirmed.
- Many generic barrel connectors are not rated for a sustained 5 A + startup margin; even if a PSU says 10 A, the cable/connector output path must be verified individually. Do not assume 10 A capacity from the PSU rating.
- For genuine copper AWG18 over 1 m one-way (2 m electrical loop), at 5 A DC the calculated voltage drop is roughly 0.21 V and heating loss ~1.05 W distributed along the pair. Actual safety depends on ambient temperature, insulation, bundling, current spike, crimp/solder, and fuse selection. Treat this as an estimate.
- The PSU nominal headroom is adequate for 120 W plus small electronics **if the manufacturer ratings and cold-start handling are real**. A better-quality 24 V / 8–10 A enclosed supply may be preferable if actual unit underperforms.
- Add a **DC-rated, properly sized fuse and protected wiring**; select size based on cold-start current and conductor ampacity, not a casual fixed guess. Keep mains cord and AC/DC adapter external and protected.
- **No uninsulated bullet contacts**, no reverse polarity, no unsafe solder-only strain relief. Verify polarity with a meter *before* cutting and *after* rewiring.

### 4.4 Electronics

| Part | Current plan | Notes |
|---|---|---|
| MCU | ESP32-C3 SuperMini, USB-C, preferably 4 MB flash | Wi-Fi and Bluetooth LE; no screen. Exact board pinout must be verified. |
| Heater switch | Dual D4184-type MOSFET board, marketed ~15 A / 400 W | Check true module continuous current, 3.3 V logic, gate drive, default-off state, thermal limits, board terminals, flyback implications for motor. Do **not** equate transistor peak rating with safe PCB rating. |
| Buck | LM2596 adjustable step down | Converts 24 V DC to regulated **5.0 V** for ESP32 board's 5V input. Set/measure with a multimeter before MCU hookup; check USB simultaneous-power behavior. |
| Temp sensors | 2 × DS18B20, TO-92 package | One measures representative chamber air, one measures a critical structural/hot-spot area; plan extra high-temperature safety sensor/cutoff as appropriate. |
| Sensor bus | 1-Wire | May share a GPIO using each sensor's unique address; typically requires 4.7 kΩ pull-up to 3.3 V. Preserve sensor address mapping across reboot. |
| Optional | Humidity sensor such as SHT31 | Only if temperature rating and location are appropriate. Relative humidity in warm air can be misleading. |
| Optional | Simple physical selector jumpers/buttons | Fallback for setpoint/mode; user considers this acceptable. |
| Required | Independent rated thermal cutoff/thermostat | Not controlled by MCU, appropriately coupled and DC-current-rated; choose trip value for actual validated hot-zone geometry. |

**Previous illustrative proposed GPIOs:** GPIO4 DS18B20, GPIO5 heater MOSFET, GPIO6 optional button. **Do not implement blind**: verify actual ESP32-C3 SuperMini pinout, boot-strapping behavior, USB/JTAG conflicts and output state during boot/reset. Fan control requires another appropriate driver and pin.

**ESP32 supply:** regulator/buck 24 -> 5 V -> board 5V pad; sensor VDD 3.3 V; share appropriate low-voltage ground as required for control circuit, subject to optocoupled-module wiring details. An "opto-isolated" module may not be truly isolated as wired. Keep all electronics outside the heated chamber.

**DS18B20:** digital temperature sensor, approximate accuracy ±0.5 °C from -10 to 85 °C, measure from -55 to 125 °C per common parts; check authenticity and datasheet. Wired three-terminal variant; wire colors are not evidence of pinout. Use appropriate insulated lead wires; consider silicone wire (~180–200 °C insulation) in heater vicinity, not generic PVC touching hot metal.

### 4.5 Filament transport and spool

- Standard 1 kg spool envelope was discussed at approximately **200 mm outer diameter** and **70–75 mm width**; measure actual Voolt3D spool and any intended alternatives.
- Spool center-bore is **not perfectly standardized**. Earlier rough examples: 49 mm and 51 mm Voolt3D variants; ~55 mm Bambu spool. Verify real targets before designing an interference-fit shaft.
- **LATEST DESIGN:** a **printed cylindrical removable axle through the spool center**, spanning the box width and resting in guide slots/tracks on **both side walls**. The owner imagines sliding axle+spool along a rail to a central seat/stop. This takes less dependence on spool outer diameter and frees the bottom for heater/airflow.
- Potential support: two matching U-tracks, end pockets, positive retention/detent or removable locking tabs so the axle cannot jump from pulling forces and vibration.
- Decide how relative rotation occurs: (A) shaft stays fixed at end pockets and spool slides on it; (B) shaft and spool rotate, with low-friction axle journals or 2 end bearings. The preferred **first experiment** is a simple printed shaft, then add bearings if friction is unacceptable.
- Track geometry must allow safe loading, prevent accidental escape, avoid hot jet, and minimize abrasion/flexing under 1 kg spool load and pull tension.
- Use a central shaft diameter smaller than the smallest known hub bore, or interchangeable adapters; don't demand an exact 50 mm hub diameter.
- Filament exit: PTFE bulkhead connector near top/upper side to feed directly to P1S, with gentle bend radii and spool-aligned path. Cable/filament routing must not foul track motion.
- Four bottom rollers / 608-bearing rollers were originally discussed, but were **superseded by the center-shaft approach**. Bearings remain optional if measurable friction/feeding issues occur.

---

## 5. Current physical layout — latest preferred architecture

**Primary objective:** compact, serviceable single-spool ABS enclosure for a horizontal 24 V 120 W PTC + stainless cup deflector and removable center-mounted spool axle. Use an external electronic compartment and separate mains brick.

### 5.1 Layout hierarchy (concept, not fixed dimensions)

1. Large **spool chamber**, above / near the heater but with adequate thermal separation and room to slide the center axle on parallel wall tracks.
2. **Horizontal PTC module** placed low (possibly low-side or low-rear), with its **fan inlet drawing mostly return air from within the spool chamber**.
3. The **hot outlet** of the PTC should face a suitable **stainless deflector** (the cup/basket laid down or tilted). Avoid a direct hot jet striking the ABS or spool; avoid blocking fan flow.
4. **Wide mixing/return passages** around and behind the spool, so the fan can drive a coherent internal flow path. The latest discussions explicitly rejected a mere upward jet with no return route.
5. **Small adjustable outside-air inlet** low and reasonably remote from PTC suction, and **small adjustable moist-air exhaust** high and preferably opposite, with low renewal relative to recirculation.
6. Separate **external electronics compartment** for ESP32, MOSFET, LM2596, wiring distribution, fuses; not in 60+ °C chamber.
7. External AC/DC PSU outside enclosure, with safe strain-relieved low-voltage entry.
8. Removable covers/access for spool, heater assembly, deflector, sensors and vent sliders. Be explicit about what can be removed without disturbing safety wiring.

### 5.2 Qualitative flow route

```
            [ SMALL HIGH EXHAUST ] ---> moisture to ambient
              .---------------------------------------.
              |          spool / hub                   |
              |      ^ warm mixed air                 |
              |      |                                |
              |      +-- around spool --+             |
              |                         |             |
              |   [mixing chamber]       v return     |
              |        ^ hot                         |
              |        |                             |
              |    [stainless deflector]   ---->      |
              |            ^                          |
              |    [PTC OUT]   [PTC FAN IN] <----------+
              |                       ^                |
              '---- small intake ------'--------------'

  (topology only; actual placement must reflect the horizontal heater)
```

**Physics caveat:** A fan moves air from its inlet toward its outlet; a closed chamber with low external renewal still allows forced internal recirculation **if the inlet has a return path**. Tiny fresh-air/exhaust vents control water vapour removal, not fan cooling. Do not make the fresh-air hole the only inlet to the PTC.

### 5.3 External vent sizes discussed

- Preliminary suggestion **2 × 5 mm diameter holes per side**, combined area ~39.3 mm² for intake and same for exhaust.
- Possible adjustable opening envelope **~80–100 mm²** each for testing.
- These are **experimental starting points**, **not calculations validated for the exact box, fan static pressure, water release rate, or climate**. Use replaceable vent plates/sliders with adjustable cross-sectional area.
- Lower intake on a side/front lower region; higher exhaust on the opposite upper region. Avoid an obvious shortcut from heater discharge directly out of the exhaust.
- External vents **must not** be relied on as over-temperature protection, and must not impede the PTC’s manufacturer-required airflow.

### 5.4 Enclosure dimensions and print segmentation

Several rough, **non-authoritative** dimensions appeared during brainstorming:
- Chamber about **230 × 230 × 110 mm** internal for a 200 mm spool with 70 mm width, before accommodating rails, heater, walls and thermal clearances.
- A concept illustration later labelled outer dimensions ~**220 × 130 × 240 mm**, **inconsistent** with some earlier assumptions and not a measured CAD design.
- Nominal P1S build volume **256 × 256 × 256 mm**; enclosure might need multiple printed ABS panels for margins, skirt/brim, warping, and assembly.

**Do not freeze dimensions from any of the above.** Build from verified spool + actual PTC/cup dimensions, mechanical mount, required airflow/thermal clearances, then fit to P1S printable panels. Keep wall thickness, ribs, corner radii, gasket land, screw bosses, and interfaces parameterized.

**ABS:** Voolt3D ABS filament purchased; an earlier manufacturer profile mentioned ~230–265 °C nozzle, ~100–120 °C bed, glass transition around 85–95 °C and max flow ~20 mm³/s (variant not confirmed). The P1S heated bed ceiling is approximately 100 °C, so printing large ABS panels may require brims, segmentation, warmed enclosure and care about warping. ABS printing produces significant ultrafine particulate and VOC emissions; ventilate/extract responsibly. Real heat-deflection and creep properties depend on print parameters, orientation and loads; ABS does **not** make contact with a hot PTC safe.

---

## 6. Thermal protection and materials (critical)

This is a powered heating appliance, 24 V DC heater drawing ~5 A, with mains in a separate PSU. The PTC itself can have surface/air temperatures far in excess of the 55–65 °C chamber setpoint. Plastic housing, filaments, wiring, glue, sensors, and fasteners can all become locally hotter than the controlled air measurement.

**Hard requirements before energizing inside printed enclosure:**

- Proper independent **normally-closed thermal cutoff / thermostat / one-time thermal fuse**, selected for measured hot-spot temperature, operating conditions and rated DC switching (AC-only current rating cannot be assumed equivalent for DC). Cut heater independently of the ESP32/MOSFET logic.
- Hardware handling of fan failure / disabled airflow. Separate fan supply is helpful, but firmware alone cannot guarantee operation if the motor fails.
- Avoid direct PTC-to-ABS contact. Use heat-rated support hardware and a properly isolated stainless barrier; **metal shields conduct and radiate heat** and do not replace clearance and measured heat mapping.
- Original **plastic mounting ears** on the PTC may be designed for mounting but are not independently proven suitable for bolting directly to printed ABS over long operation; validate with manufacturer/physical tests. Attaching the steel cup through shared fasteners can conduct heat into those mounting points.
- Provide thermally rated insulating sleeves/wire, mechanically supported exits, edge grommets and protections so wiring cannot touch rough or hot metal or jam the fan.
- Don't assume all sensor-to-board connections, silicone adhesives, ordinary heat-shrink sleeves, printed hinge pins, or glue gun adhesive withstand hot spots.
- Use a suitable **DC overcurrent fuse** and compatible connector/terminal ampacity; validate inrush of PTC and fan, not just nominal current.
- Ensure PSU remains externally ventilated, no exposed mains wiring near/inside the ABS box.
- Start testing at reduced target temperatures, ideally measure hot surfaces and wall/fastener temperatures with independent measurement, document behavior at steady state, after fan stop, after control failure, and during cooldown.
- **Never run unattended until the complete mechanical/electrical/thermal safety case has been demonstrated.** Even then do not imply an uncertified custom heater is safe for unattended household operation.

**Temperature strategy evolution:**
- PETG **enclosure** was initially capped around **55 °C default / 60 °C maximum** because of creep/deformation near glass transition. This is **superseded** by ABS enclosure purchase.
- With ABS enclosure, target drying air might be **55–60 °C initially** and perhaps higher **only after** manufacturer and safety validation. A screenshot conceptual sketch mentioned **65 °C**, but no engineering test showed that to be safe.
- Both DS18B20 readings are valuable for operating feedback, but a wall sensor may not detect a very local hot spot on stainless/fastener. Independent protection is mandatory.
- **Thermal cutoff 70–80 °C NC** appeared as a rough concept in an infographic, **not a proven chosen part or universal trip setpoint**. Choose cutoff after actual fault modelling and measurement, ensuring it cannot be bypassed by software and is rated for its voltage/current/load.

**PETG outgassing question discussed:** Significant thermal decomposition at 60 °C is very unlikely, but minor volatile emissions cannot be ruled out and literature discussing higher-temperature extrusion does not prove zero emissions at 60 °C. The main practical concern for the prior PETG box was thermal deformation and local overheating; the user subsequently switched to ABS.

---

## 7. Control and firmware plan

### 7.1 User experience

- No expensive physical display.
- The ESP32-C3 has **2.4 GHz Wi-Fi and BLE**; primary plan is an **on-device web UI** accessible via phone browser, not a mobile app.
- Proposed standalone access point: Wi-Fi SSID `MiniAMS`, then navigate to `192.168.4.1`. Alternate mode: connect to household Wi-Fi. Both are ideas; final provisioning/security design is open.
- UI controls: target temperature, drying duration, start/stop, live measured air temperature, optional wall temperature, fan and heater state, remaining time, alarms. User wanted a simple attractive interface and possibly saved settings in nonvolatile memory.
- Optional physical jumpers/selector are acceptable as a simpler fallback; no hardware display requirement.

### 7.2 Control algorithm, preliminary

- A simple **hysteresis** ON/OFF control was favored rather than fast PWM or PID for the heater. MOSFET input pin may be labelled `PWM` but can be driven as on/off **if** the selected board supports a 3.3 V logic high, known polarity and default-off state.
- Example setpoint **55 °C**, switch ON below about 53 °C and OFF above about 57 °C (old illustration). For a 65 °C setpoint another example used ON at 63 °C and OFF at 65 °C. **These example thresholds were not harmonized**; choose one documented control policy and tune for actual heater thermal inertia to avoid overshoot.
- If sensor read invalid, sensor disconnected, overtemperature detected, or MCU rebooting, **heater OFF** by design. Do not assume a MOSFET module powers up OFF without verifying actual board pull states.
- Fan may run continuously during dry cycle, starts before heater, continues after heater off until cooled. Fan independent power is available but supply voltage must be confirmed.
- On losing Wi-Fi, temperature controller should still operate safely under local settings; Wi-Fi is not a safety mechanism.
- Timeouts and dry cycles should persist appropriately; ensure reboot policy cannot silently re-enable heater following error.
- Optional humidity readout SHT31 may aid monitoring if rated for actual in-box location, but **relative humidity at 60 °C is not proof filament water content has dropped**.

### 7.3 Temperature/time profiles

- Default test for generic PETG: **55 °C / 6–8 h** was discussed; user’s exact PETG recommendation not verified.
- ABS, TPU and other materials may require their own manufacturer-verified profiles and safe spool compatibility; **do not hard-code a universal drying temperature**.
- Active drying: warmer air, controlled external vent exchange; passive storage: heater off, close vents and optionally include silica gel.
- The project need not include silica gel initially. It is useful for storage and may be added later.

---

## 8. Mechanical CAD requirements

### 8.1 Existing model

- User said: "I have already drawn the FreeCAD model(s) of the PTC+fan and stainless cup and created the public repository."
- At time of handover the repository contained a file named **`myms.FCStd`**. It is possible both reference objects are inside one `.FCStd`; **do not assume** their exact names or solid structure before inspection.
- Prior planning suggested separate `PTC_120W.FCStd` and `StainlessCup.FCStd`, but the actual repository currently exposes `myms.FCStd`. **Actual repo layout wins.**
- FreeCAD **1.1.4** on **Ubuntu 24.04** is the intended execution environment. Use macros (`.FCMacro`) or FreeCAD Python APIs to generate/edit, export STEP/STL, inspect shapes. Avoid importing `FreeCAD` from the host system Python if it is not installed in that environment; use the installed FreeCAD Python console/CLI as appropriate.
- Preserve existing reference geometry and make model variants or working copies. Native parametric feature trees are strongly preferred over triangulated-only final output.

### 8.2 Required assemblies/features

1. **Single-spool ABS enclosure**, segmented for the P1S, with ribs, appropriate printable orientations, cover, assembly fasteners and accessible service areas.
2. **Removable spool axle** and two **side-wall tracks** ending in captured support pockets; design for swapping a 1 kg spool without disassembling heater.
3. Heater area with **horizontal PTC**, real mounting tab pattern, protected wiring exits, independent fan feed, and no contact with ABS in hot zones.
4. **Stainless cup deflector mount** with removable hardware and experimentally adjustable orientation/clearance; minimal metalworking preferred. Modifications to the cup are optional experiments, not a manufacturing prerequisite.
5. Airflow passages providing an intentional **internal return path**, plus separate small adjustable lower air inlet and upper exhaust; don't make tight ducts that block fan operation.
6. PTFE feed-through connector/filament guide at a sensible top/upper-side position; avoid spool feed binding and tight bends.
7. **Sensors** with removable mounts, realistic placement not directly in hot jet, strain relief and cable channels.
8. **External electronics box** accessible without heating chamber disassembly: MCU, buck, MOSFET, wiring protection, optional buttons, low-voltage input connector, thermal cutout wiring.
9. Inspected, traceable **interference and tolerance check** between heater, cup, enclosure, spool, axle, connectors, and moving filament.
10. **Thermal assembly documentation** distinguishing manufacturing-ready ABS pieces from metal/electrical parts requiring review.

### 8.3 Printing/fit engineering

- Use printed ABS, not PLA, for the hot enclosure. No ABS plastic directly adjacent to hot PTC element without measured and validated isolation.
- Incorporate robust joining features (screws/inserts designed for ABS), printable fillets, wall thickness/nervures, and thermal expansion/creep consideration. Validate any brass heat-set insert installation and local heat source.
- Segment geometry to fit P1S's nominal 256 mm cubic envelope, allowing realistic brim/warping margins. No huge unprintable monolithic housing.
- Tolerances for all sliding and snap features are printer/ABS-specific; make CAD parameters and a small calibration coupon rather than assume a one-size number.
- Spool friction and feeder loading matter. P1S feeder must pull cleanly through PTFE without snap/skip. Test print while feeding from dryer before relying on passive center-axle friction design.

---

## 9. Geometry and airflow validation plan

**At this stage, no safe thermally validated final CAD exists.** A practical development sequence was discussed:

**Stage A — Reference audit**
- Open `myms.FCStd`; extract actual unit system, dimensions, heater outlet orientation, fan inlet face, tab dimensions and mounting holes, stainless cup hole pattern/geometry and space constraints.
- If STL/mesh imported, report lost editability and decide whether to keep reference volumes only.

**Stage B — Layout and parametric envelope**
- Measure target Voolt3D and optionally Bambu spools.
- Define min internal span for 1 kg spool and rail insertion/removal.
- Create simple bounding volumes for horizontal heater + stainless cup, return-air passage, spool/axle and external electronics.
- Compare multiple compact layouts for overall height and P1S segmentation. Prefer user's requested low height; do not blindly adopt the earlier vertical poster.

**Stage C — Mechanical prototypes**
- Print axle and rail pocket as cheap test coupon; verify sliding load, retention, ease of spool insertion and smooth rotation.
- Mount cold heater and cup mockup; confirm actual fasteners and clearance.
- Fabricate adjustable external vent prototypes.

**Stage D — Electrical + isolated safety tests (supervised)**
- Confirm PSU voltage/polarity, fan voltage/current and independent operation, heater cold current and fan startup.
- Verify MOSFET default-off and safe behavior on boot and fault, correctly sized fuse and thermal cutoff, wiring/connector ratings.
- Only on a suitable nonflammable test setup and with required independent thermal protection, test air path without ABS enclosure, track PTC and stainless temperatures.

**Stage E — Controlled box tests**
- At lower setpoints, measure average chamber air, hot jet, wall, cup, mounts, wires, return path, under spool, and near vents, including overshoot and fan failure behavior.
- Adjust deflector and airflow. The previously suggested two DS18B20 are not enough alone to characterize all hot spots; use additional temporary measurement instrumentation.
- Validate dry-cycle performance with controlled PETG print tests and check for air circulation and dimensional distortion.

**Stage F — Manufacturing release**
- Produce assembly `.FCStd`, per-part export, exploded views, dimensioned instruction drawings, detailed BOM, wiring schematic, firmware, assembly/inspection instructions and documented operating envelope.
- Only label operating modes safe after evidence and applicable testing, not by assumption.

---

## 10. Shopping and cost discussion (historical, not a live BOM)

The user reported an AliExpress total of **BRL 274 including taxes**, excluding printable filament. An earlier cart screenshot included some **multi-packs** and displayed individual item prices around:

| Item screenshot | Approx. price at that time (BRL) |
|---|---:|
| LM2596S, 5 units | 19.44 |
| ESP32-C3 SuperMini | 16.08 |
| MOSFET board, 5 units | 15.41 |
| Temperature sensors, 10 units | 17.02 |
| PTC 24 V / 120 W | 79.29 |
| Earlier PSU 24 V / 150 W | 94.21 |

These screenshot prices are **not authoritative present prices** or proof of actual quantities received. A 24 V / 10 A PSU was ultimately purchased instead of the earlier exposed 150 W PSU candidate. Later the user also bought **Voolt3D ABS** and the **95 mm stainless cup**. Unaccounted items may include hardware/fasteners, silicone gasket, PTFE bulkhead, wiring, fuse, thermal cutoff, and printed material.

**Do not use old price estimates to approve/replace safety-critical components.**

---

## 11. Historical conceptual illustrations and important caveats

Several visual concept drawings were created in the discussion:
- Initial isometric cutaway with vertical heater region, free-rolling spool and external electronics.
- Larger infographic of a **vertical PTC** below an **upside-down stainless cup** with orange flow arrows around the spool.
- Subsequent simple flow sketches showing recirculation, high exhaust, low outside inlet, and center shaft/tracks.

**These are conceptual only.** They sometimes overstate circulation and may contain internally inconsistent dimensions or component labels. They are **not mechanical drawings, mounting constraints, validated airflow CFD, wiring schematics, or verified measurements**. Their most recent design implications are:
- Horizontal PTC + horizontal/tilted stainless cup should be tested to reduce box height.
- Correct internal recirculation demands a path back to fan intake.
- Center axle/tracks replace rollers.
- External PSU is **24 V 10 A**, not any outdated image calling it 24 V 5 A.

If the owner supplies these images privately, preserve them as inspiration and compare against the current decision log rather than blindly replicating them.

---

## 12. Conflict and ambiguity register

| Issue | Older statement | Latest status / required resolution |
|---|---|---|
| PTC wattage | 100 W tentative | **120 W purchased** |
| Material | PETG box at 55–60 °C | **ABS purchased** |
| Heater orientation | Vertical under spool | **Horizontal to keep compact** |
| Deflector position | Inverted cup above upward outlet | **Horizontal/tilted cup concept; verify real geometry** |
| Spool support | 4 bottom rollers | **Central removable axle in dual side tracks** |
| Intake scheme | Fan potentially draws outside air | **Fan recirculates internal air; remote small outside inlet** |
| Vent size | 2 × 5 mm holes | Experimental only; make adjustable |
| Safety thermostat | 70–80 °C NC graphic | **Unspecified, must be independently rated/selected** |
| Source `.FCStd` | Two suggested files | Actual repo uses **`myms.FCStd`**; inspect |
| UI | Web or jumper | Web preferred, no display; fallback jumper possible |
| Power plug | P4, bullet, XT60 | Still undecided; verify ratings and polarity |
| Fan | May share heater supply | **Separate wires confirmed**; verify supply specs |
| Wall temp limit | Software setpoint 60 °C | Firmware is not a safety barrier; ABS still needs thermal validation |
| PETG print fault | Assumed moisture | **Unproven**; cooling/flow/orientation are alternatives |
| Spool bore | Treated as standard | Sizes vary; measure and accommodate |
| Enclosure dimensions | Several sketches | Unverified; build from actual CAD |

---

## 13. Questions requiring measured answers (not guesswork)

These should be answered by inspecting `myms.FCStd` and, if absent, by asking the user for targeted measurements:

1. How are heater and cup placed in the actual existing FCStd: independent solids, a single compound, origin coordinate systems, true shape topology?
2. Exact PTC body size, mounting tabs’ hole diameters and locations, rear fan inlet opening, **hot-air outlet direction** in the model, mounting ear material/rating, inlet/outlet clearances and cable exits.
3. Fan voltage/current/polarity and whether fan/blower housing is rated for its hot airstream.
4. Stainless cup height, inner vs outer diameter of the claimed **95 mm**, base wall curvature, hole density/locations, thickness and potential mounting points.
5. Real Voolt3D spool outside diameter, width, bore size and total 1 kg roll mass; what other brands to support?
6. Axle mode: fixed rod that spool rotates on, or captive rotating rod? Desired retention and loading method?
7. Container orientation and desired external footprint; top/side door and location relative to P1S and its feeder/PTFE entry?
8. Exact accessible connectors and cable lengths for the purchased PSU and the heater, and final DC connector choice.
9. Independent overtemperature cutoff hardware model and **DC rating**; fuse values after measuring cold-start behavior.
10. Whether the purchased ABS is the exact High Speed Premium formulation and its manufacturer drying/thermal guidance.
11. Desired operating maximum and target materials. Does drying **while printing** require a completely closed lid with feed-through at all times?
12. Where to place storage desiccant (optional) and whether vent sliders are manually adjusted or motorized (manual is sufficient for now).

---

## 14. Deliverables and repository organization

Possible repository structure (do **not** overwrite any existing work without inspecting it):

```
myms/
├── AGENTS.md
├── .gitignore
├── myms.FCStd                 # Owner's reference geometry — preserve
├── docs/
│   ├── PROJECT_HANDOVER.md     # This document
│   ├── FIRST_CODEX_PROMPT.md
│   ├── CAD_REFERENCE_INVENTORY.md  # Generate after inspecting FCStd
│   ├── DESIGN_DECISIONS.md         # Maintain during modeling
│   ├── TEST_PLAN.md                # Independent safety + function tests
│   └── BOM.md                      # Verified components + links/dimensions
├── cad/
│   ├── assembly/
│   ├── printable_parts/
│   └── reference/
├── scripts/
│   └── ...                    # Reproducible FreeCAD generators/checkers
├── exports/
│   └── ...                    # STL/STEP for finished versioned revisions
├── firmware/
│   └── ...                    # Optional later, ESP32-C3
└── private/                   # Local ONLY; gitignored chat export/screenshots
```

Development order: **(1) inspect actual reference CAD -> (2) measure and select layout -> (3) print/test axle/rails -> (4) build modular enclosure/heater fixture -> (5) validate thermal/electrical/airflow safety -> (6) complete assembly CAD and exports -> (7) firmware and docs -> (8) controlled PETG performance tests**. Firmware need not block CAD modeling, but cannot substitute independent hardware thermal safety.

### Principles for building a useful CAD tree

- Prefer FreeCAD `App::Part` assemblies and parametric `PartDesign::Body` components or equivalent supported primitives; keep references separate and identifiable.
- Semantic English labels like `PTC_Heater_Reference`, `Fan_Inlet`, `Heater_Outlet`, `Steel_Deflector_Reference`, `Spool_Axle`, `Axle_Track_Left`, `Axle_Track_Right`, `Lower_Intake`, `Upper_Exhaust`, `Electronics_Housing`.
- Parameter groups for spool, chamber clearance, wall thickness, slide track width, axle journals, heater mounts, cup, vent area, and tolerance offsets.
- Validate solids and boundary conditions, keep meaningful exports and manufacturing drawings tied to a versioned assembly.
- Explicitly tag thermal parts and fasteners as requiring separate safety review before build.

---

## 15. What "do not lose anything" really requires

**This document is extensive but cannot literally preserve every utterance, image, attachment and exact link from the original ChatGPT conversation.** For full fidelity, keep the original chat history separately.

1. Use ChatGPT's **Settings → Data controls → Export data** to obtain an account ZIP. Its contents can include unrelated conversations and personal information. **Never commit the raw account ZIP to this public repository.**
2. Extract the **specific project conversation**, preserving original chronology and attachments, to a **local private** copy (e.g. `private/original_chat.md`, `private/chat_assets/`) if desired. `private/` is gitignored by this bundle.
3. Treat the raw transcript as **historical source**, and this handover's latest-decision table as the current engineering priority, subject to actual measurements and later owner instructions.
4. When the user makes a new decision in Codex, update `docs/DESIGN_DECISIONS.md` and correct this handover where necessary to avoid long-term drift.
5. Keep legal rights/confidentiality in mind before public sharing. The original conversation was in Portuguese; repo content should remain in English.

---

## 16. Suggested first Codex task

**Do not immediately generate the final printable appliance.** First inspect `myms.FCStd` and report exactly which models already exist. Then propose a compact horizontal mechanical architecture using the real geometry, with a central removable axle in paired wall tracks and a sensible internal return-air duct. Create a stable parametric skeleton and a small test coupon for the slide/axle mechanism before expanding to the full housing. Surface all uncertain dimensions and thermal/electrical hazards instead of guessing.

The user wants Codex to **actually create and edit the FreeCAD project on their Ubuntu machine**, not merely write conceptual advice. Use FreeCAD's Python capability to inspect and build files locally, while preserving the original model and requesting approval before any public push.

---

## 17. Reference URLs and pointers

- Public repository: https://github.com/heitorneves91/myms
- OpenAI docs on ChatGPT data export: https://help.openai.com/en/articles/7260999-exporting-your-chatgpt-history-and-data
- OpenAI Codex project guidance (`AGENTS.md`): https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide
- Official FreeCAD project: https://www.freecad.org/

Earlier conversation referenced manufacturer and product pages for specific PETG/ABS properties, PTC boards and dryer designs. **Those claims and URLs are not reproduced as verified authoritative design specs here** because the exact products/variants still need part-specific validation. Prior assistant comments are leads for research, not a substitute for a datasheet or physical measurement.

**End of handover.**
