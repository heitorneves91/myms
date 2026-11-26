# Independent heater and cup supports

Current implementation: the separate supplemental [mounting retrofit](MOUNTING_RETROFIT.md) uses four integrated printed supports, eight purchased PEEK spacers and stock fasteners while preserving the owner's completed prints. Geometric checks pass; procurement, physical fit, thermal and airflow validation remain outstanding. The pipe-clamp architecture below is an earlier proposal, not the current parts list.

2026-11-14: Owner confirmed that no heater/cup mounting hardware has been purchased. Thermal cutoff selection is deferred at the owner's request; this note covers mechanical mounting only.

## Redesign constraints — 2026-11-25

The owner reports successfully printing every part in `Printed_Assembly`. Those parts are now an installed-design constraint: preserve their geometry and existing interfaces. The owner cannot fabricate metal and has requested a mounting redesign. Custom sheet-metal cutting, drilling, bending or welding is not an acceptable owner task. Additional printable adapters and ready-made hardware are candidates; willingness to assemble purchased brackets/clamps/standoffs is being clarified before selecting them.

The owner initially reported foil around the cup, then asked to exclude foil and assume no existing metal supports. The implemented supplemental retrofit omits the custom partition/bands, independently retains the heater and reuses existing base holes. Cup contact geometry and commercial spacer dimensions are explicit, but actual procurement, clamping on real perforations and thermal behavior remain unverified. See the retrofit guide for CAD, assembly and the supplemental BOM. The earlier architecture below remains historical context.


## Earlier pipe-clamp architecture

Do not fasten the cup to the heater. Support both independently from the base. Keep the cup mouth aligned with the heater outlet, with a free gap between them. The current model has a 15.5 mm axial gap from the projecting outlet to the cup mouth; this is a layout starting point, not a validated thermal or airflow clearance.

For the cup, prefer two unlined metal pipe clamps with integral mounting bosses. The inspected cup barrel is 95 mm diameter. As a concrete size example, the [fischer FRSN 93–99 M8/M10](https://www.fischerfixingsusa.com/en-us/products/installation-systems/pipe-clamps/two-screw-pipe-clamps/pipe-clamp-frsn/50005-frsn-93-99-m8-m10) fits that diameter range and has no sound-insulation liner. This establishes an available hardware architecture, not local availability or thermal approval. Manufacturer dimensions for the complete clamp and boss are still needed before fitting it to this enclosure. Do not clamp the wider cup lip or tighten a perforated thin cup as though it were a rigid pipe.

A worm-drive hose clamp can also retain the cup, but it needs a separate load-bearing bracket. The previous CAD's welded-looking ring/foot references were conceptual: ordinary hose clamps do not come with those feet. Prefer the pipe-clamp arrangement to avoid custom welding or bending.

Each metal clamp connects to the floor through a low-conductivity, temperature-rated support. Prefer a standoff with separate upper and lower threaded attachments and a continuous insulating body between them. Verify the internal construction: opposing screws must not meet, and there must be no continuous metal insert from hot bracket to floor. Steatite threaded standoffs are an established component family; see [Abbatron ceramic standoffs](https://www.abbatron.com/products/75-ceramic-standoffs) and [CeramTec standoffs](https://www.ceramtec-group.com/fileadmin/user_upload/Corporate/11_Downloads/05_Ceramaseal/CeramTec_us_ceramaseal_accessories.pdf). Thread sizes, stiffness, temperature and thermal conductivity must match the selected hardware. An electrical insulation rating alone does not establish adequate thermal isolation.

The intended stack is:

```text
cup
unlined metal pipe clamp
short upper attachment
insulating standoff body
separate lower attachment
broad load-spreading washer / base reinforcement
ABS floor
```

Use the heater's existing tabs on separate metal angle supports, also isolated from the ABS base. Do not attach the hot cup to those tabs. Direct tab-to-ABS mounting may eventually prove workable if the heater manufacturer permits it and measured tab/wall temperatures remain acceptable; neither is established for this heater, so direct mounting is not the current recommendation.

## Correction to the original mounting study

The original assembly's generic ceramic spacer tubes have metal through-fastener paths. A ceramic tube around a screw does not interrupt heat conduction along that screw. Nor are all ceramics good thermal insulators. Treat those parts as envelope placeholders, not a finished thermal mounting detail.

Metal supports and clamps can become hot. Isolated fasteners address conduction, while air clearances and shielding address convection and radiation; both still require measurement. This note does not assign a safe gap or operating temperature.

## CAD consequences

Replace the proposed integral band/saddles with the selected pipe-clamp geometry, including bolt lugs and the threaded boss. Their bulk may require raising the cup and heater together. The existing 11.2 mm cup-foot spacers are not a fixed requirement, and mounting holes in the base remain provisional. Keep the return-air partition mechanically separate from the heater supports, so its fabrication does not determine how the heater is retained.

The full assembly is deliberately unchanged until support dimensions are available: fitting a real clamp and insulating support cannot be established from nominal pipe diameter alone. The existing shell, spool fit coupons, and axle can be reviewed independently of these mounting changes.
