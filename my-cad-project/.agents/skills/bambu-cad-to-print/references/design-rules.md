# FDM geometry design rules — starting values, not fixed guarantees

## Scope
All figures below are **starting points** for ordinary polymer FDM (PLA/PETG), a Bambu printer with a **0.4 mm nozzle**, and roughly 0.2 mm layers. Always adjust to material, actual Bambu Studio line widths, the printer/nozzle, cooling, part size, orientation, flow and measured calibration. Do not automatically apply the figures to a 0.2/0.6/0.8 mm nozzle.

| Design feature | Starting target / rule | Verification |
| --- | --- | --- |
| Single extrusion track | ~0.4–0.5 mm wide in typical 0.4 mm-nozzle profiles; may differ | Read wall-width settings and sliced path. Not a robust free-standing structural wall. |
| Thin non-load-bearing wall | >=2 actual extrusion line widths (~0.8–1.0 mm) | Inspect continuous paths; do not rely on a slicer invisibly expanding details. |
| Ordinary functional wall | 3–4+ extrusion paths (~1.2–1.8+ mm) or thicker with loading | Evaluate actual stress and layer bonding; print test as needed. |
| Loose/sliding two-part clearance | ~0.15–0.25 mm **per mating side** (0.30–0.50 mm diametral/total) | Fit coupon; surface finish and material shrinkage vary. |
| Tight / snap / press fit | **No universal number** | Print multi-step fit coupon with relevant material/orientation. |
| Holes for fasteners/shafts | Expect orientation-dependent dimensional deviation, often undersized | Print an undersize/oversize test grid; drill/ream for precision. |
| Unsupported overhang | Prefer undersides angled at least ~45° above the bed plane as an initial design heuristic | Validate in slicer and actual bridging/overhang test; not a sharp pass/fail threshold. |
| Short bridge | Can sometimes span without support; no universal bridge distance | Bridging depends on span, cooling, line direction, filament. |
| Z-direction tension | Usually weaker due to layer interfaces | Orient functional load in XY where possible; add material/fasteners. |
| Small embossing / text | Needs several resolvable extrusion paths and layer height for legibility | Inspect toolpaths, use larger font/relief or finer nozzle if necessary. |
| First-layer mating edge | Small chamfer may ease fit and mitigate elephant foot | Inspect real fit; bed compensation is profile-dependent. |
| STL curve resolution | General chordal deviation ~0.05–0.10 mm; precision ~0.01–0.05 mm where needed | Compare exported mesh to CAD and keep triangle count sensible. |

**Clarify units of fit:** Example: a cylindrical pin diameter of 10.00 mm with a chosen 0.20 mm radial clearance gets a hole modeled at **10.40 mm diameter**, before empirical correction. For two opposed flat faces, 0.20 mm clearance is the gap at each specified interface, not an overall feature diameter.

**Line width versus nozzle:** Prefer sizing to selected slicer's calculated/selected line width and wall generator. Arachne/variable-width paths can adapt, but are not a replacement for robust wall design. Bambu Studio's wall generator may make very small features printable by widening them — a geometric distortion that can break fit.

**Material:** PLA: prototyping/stiff and easy; PETG: tougher and less brittle but can string; ASA/ABS: more heat/UV potential but shrink/warp and require compatible ventilated/enclosed setup; TPU: flexible but needs flexible-specific design/slicer settings. Verify exact printer/hotend/plate/material compatibility and workplace ventilation rather than assuming one prescription works for all.

## Sources / provenance
- Bambu Lab, *Introduction to wall generator* — variable line widths and auto-enlargement of thin features: https://wiki.bambulab.com/en/software/bambu-studio/wall-generator
- Bambu Lab, *How to Print Overhangs*: https://wiki.bambulab.com/en/filament-acc/filament/print-quality/overhang
- Prusa Knowledge Base, *Modeling with 3D printing in mind* — line-width illustration, manifoldness, anisotropy, overhangs and fit-coupon emphasis: https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135
- Prusa Knowledge Base, *Layers and perimeters* — layer-height and perimeters: https://help.prusa3d.com/article/layers-and-perimeters_1748
- Autodesk Fusion, STL/3MF export: https://help.autodesk.com/view/fusion360/ENU/?caas=caas%2Fsfdcarticles%2Fsfdcarticles%2FHow-to-export-an-STL-file-from-Fusion-360.html

These resources are design guidance, not a substitute for machine and material datasheets or testing.
