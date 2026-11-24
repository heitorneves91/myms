# MYMS: agent entry point

Read [docs/PROJECT_STATE.md](docs/PROJECT_STATE.md) first. It is the current handover, replacing the former root `PROJECT_HANDOVER.md`.

Load only the context needed for the task:

| Task | Read next |
| --- | --- |
| Understand an owner choice or avoid reverting a decision | [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md) |
| Edit/regenerate CAD, export, render, or inspect validation | [docs/CAD_WORKFLOW.md](docs/CAD_WORKFLOW.md) |
| Assemble, print, fit, or review fasteners | [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) |
| Sensor mounts or chamber-to-electronics wiring route | [docs/SENSORS_AND_WIRING.md](docs/SENSORS_AND_WIRING.md) |
| Heater/cup mounting | [docs/MOUNTING_CONCEPT.md](docs/MOUNTING_CONCEPT.md) |
| Inventory, electronics, firmware, materials, thermal testing | [docs/HARDWARE_AND_CONTROL.md](docs/HARDWARE_AND_CONTROL.md) |
| Old prices, original PETG troubleshooting, or full initial planning detail | [docs/history/INITIAL_PLANNING_HANDOVER.md](docs/history/INITIAL_PLANNING_HANDOVER.md), only when needed |

Working rules:

- Keep code, CAD names, repository documentation and GitHub content in English.
- Distinguish owner-confirmed facts, implemented geometry, assumptions, assistant proposals and physically tested results. Current CAD is a mechanical review prototype; no physical build/thermal results have been reported.
- Preserve `cad/assembly/Hardware_References.FCStd`: it contains the owner's original editable heater/cup models and is a generator input. Assembly references are shape snapshots, not full copies of their feature histories.
- Inspect the working tree and applicable source files before editing or regeneration. The owner works in FreeCAD; regeneration replaces the generated document and can discard manual CAD edits.
- Use [cad/parameters.json](cad/parameters.json) and the generator for reproducible geometry changes. Some layout coordinates and checks are fixed to the current design; the spreadsheet does not drive regeneration.
- Honor the owner's 3.2 mm M3 clearance holes and 4 mm heat-set insert pockets. Keep current spool bushings unless asked otherwise. The owner prefers exporting selected FreeCAD parts together as a single 3MF; existing STL exports are optional conveniences.
- Thermal cutoff selection is explicitly deferred. The owner reopened the printed-assembly fastener BOM on 2026-11-22; see BUILD_GUIDE.md for its sizing assumptions and hinge-clearance finding. Heater/cup fasteners remain unselected. Continue independent mechanical work without repeatedly asking to resolve deferred protection topics; deferral is not thermal validation or permission to energize an unprotected appliance.
- When the owner asks for planning/questions only, do not edit artifacts during that discussion. Otherwise carry authorized work through implementation and relevant verification.
- Update the appropriate focused document when a decision or implementation changes, and keep the brief state summary accurate. Historical text does not override newer owner instructions or the current handover.

This file is a navigation and project-conventions layer, not a requirement to load every document into context.
