---
name: bambu-cad-to-print
# Description is deliberately trigger-rich so an agent loads this for CAD, mesh and image-to-3D jobs.
description: Design, reconstruct, export, inspect, and validate printable mechanical or decorative 3D models for Bambu Lab FDM printers. Use for parametric CAD, STEP-to-STL/3MF conversion, OBJ/GLB/render-mesh repair, image/render-to-3D reconstruction, Bambu Studio preparation, fit and tolerances, and STL printability QA. Do not use for resin-specific workflows.
compatibility: Requires access to a CAD or mesh application for geometric edits; Python 3 with trimesh and numpy is optional for automated STL checking. Bambu Studio is required for final slicing verification.
metadata:
  version: "1.0.0"
  purpose: "DfAM and Bambu Studio readiness"
---

# Bambu CAD-to-Print — agent operating procedure

## Role and success criterion
Act as a CAD + Design-for-Additive-Manufacturing (DfAM) engineer. Aim for a dimensionally controlled part that is **likely to print and function**, not simply for an STL file that can be opened. Preserve an editable source when possible. Never claim a part is printable solely because an STL exists or a mesh checker passes.

## Ground rules
- Distinguish **measured**, **specified**, **estimated**, and **unverified** information. Never invent dimensions from a single render or claim to have inspected Bambu Studio without access.
- Do not promise an exact fit or load rating without design requirements, material properties, test prints, and appropriate engineering validation.
- Use millimeters in modeling and exports. STL is unitless: explicitly verify its interpreted units and bounding box on import.
- Make geometry changes upstream in source CAD or the master mesh whenever feasible; don't silently rely on slicer auto-repair to fix design defects.
- Treat approximate numbers in `references/design-rules.md` as **initial design targets**, not a printer guarantee. Actual line widths, filament, nozzle, profile, orientation and calibration control performance.
- Do not dispatch a printer job or overwrite files without user authorization. Do not mark a physical fit or print test as passed unless it was actually carried out.
- For safety-critical, high-load, heat-exposed, pressure-containing, or vehicle/aircraft parts, flag engineering verification as a separate mandatory activity. A consumer FDM print must not be automatically certified for such service.

## 0. Intake: collect/resolve the print contract
Read `assets/job-brief.template.yaml`. Extract from the request or supplied project:
1. Part purpose, major/critical dimensions, mating components, load direction and allowed tolerances.
2. Source type: CAD solid (native/STEP), surface CAD, triangulated mesh (STL/OBJ/3MF/FBX/GLB), 2D rendered image(s), scan, or mixed.
3. Target Bambu Lab printer **exact model**, nozzle diameter, build-volume and restrictions, filament/material, build plate, and intended Bambu Studio profile.
4. Required finish, text/embossed details, assembly style, support limitations and allowed print orientation.
5. Deliverable formats and verification capabilities (CAD, Python, Bambu Studio, test prints).

If a value is missing, choose reversible design defaults *only if low-risk*, mark them `ASSUMED`, and state consequences. Ask for genuinely essential dimensions and use explicit `BLOCKED` status where accurate design is impossible. Never assume every Bambu printer has the same print volume or material capability.

## 1. Route the input correctly
- **Native CAD / STEP / other solid B-rep:** inspect units, bounding box, body count, feature history where available, sketches and constraints; repair gaps / zero-thickness / surface bodies; save native CAD and optionally STEP; then triangulate to STL or 3MF.
- **Surface-only CAD:** close/stitch surfaces into a watertight, nonzero-volume solid; verify thickness. Export only after the solid is valid.
- **STL / OBJ / PLY / GLB / FBX / 3D render mesh:** verify intended scale, mesh normals, holes, manifold edges, intersections, disconnected shells, and real wall thickness. Repair or remodel; do not confuse texture-based bump details with printable geometry. CAD-like control may require reverse engineering/remodeling.
- **2D image / screenshot / rendered picture:** there is no inherent back surface, scale or wall thickness. Reconstruct 3D geometry using dimensions, orthographic references or explicit modeling assumptions, then follow the same CAD and mesh QA. Never describe an image-to-STL result as dimensionally accurate without measurements.
- **Multicolor/rendered appearance:** STL only contains triangulated geometry, not useful material/color assignments or image textures. Model physical relief, or deliver a suitable multibody/3MF Bambu Studio project if color/material assignment is needed. Check actual slicer behavior.

Refer to `references/source-to-mesh.md` for branching details.

## 2. Model for manufacturing, not for a screenshot
- Model at true 1:1 scale, fully dimension important geometry; use named parameters for wall, clearance, hole diameter, fillet, and interface dimensions.
- Prefer clean solid bodies. Eliminate accidental overlapping volumes, zero-thickness surfaces, self-intersections, microscopic slivers, loose floating details, inverted normals and non-manifold junctions.
- Design minimum walls and pins around **sliced extrusion line widths**. For an initial 0.4-mm-nozzle PLA/PETG design, target two lines (~0.8–0.9 mm) only for noncritical walls and 3–4+ lines (~1.2–1.8+ mm) for more robust walls; increase for loads. See reference notes; do not equate CAD wall width to nozzle diameter blindly.
- Use explicit per-side vs diametral clearances. Start with ~0.15–0.25 mm per side (~0.3–0.5 mm total) for a sliding/loose fit on a calibrated ordinary FDM machine; verify with a fit coupon. Snaps, press fits, bearings, threads, and moving hinges require application-specific coupons.
- Treat horizontal and vertical holes differently. FDM holes can print undersized; verify with a hole gauge, tune dimensions or plan drilling/reaming for tight fits.
- Design orientation from functional loads and exposed surfaces early. Layer interfaces tend to be weaker in the build (Z) direction; align important tensile load paths within layers where practical.
- Minimize unsupported undersides: slope/chamfer, bridge short distances where verified, add accessible supports, use teardrop horizontal holes, or split the part. A slope near 45 degrees above horizontal is a conservative orientation-dependent starting point, **not a universal cutoff**.
- Add fillets at stress-concentrating internal corners; chamfer interfaces/leading edges and print-bed edges when helpful. Avoid blind trapped support cavities, excessively thin tall pillars, and sharp internal corners that prevent hardware seating.
- For large flat areas or warp-prone polymers, consider ribs, corner radii, orientation and brim/adhesion strategy. Check available material / nozzle / enclosure compatibility for the exact printer.

## 3. CAD validation gate (before export)
Require:
- [ ] Key dimensions, coordinate axes and model units confirmed.
- [ ] Intended closed solid(s) with positive volume; no open/zero-thickness surfaces.
- [ ] Bodies and assembly fits intentional; no accidental intersects, duplicates or floating shells.
- [ ] Wall, embossed/debossed details, through-holes, fillets, gaps and support accessibility checked.
- [ ] Predicted print orientation and bounding box compatible with selected printer (including keep-out restrictions if applicable).
- [ ] For functional designs, load path and mating geometry reviewed and unresolved engineering assumptions noted.

## 4. Export geometry faithfully
- Preserve an editable master (`.FCStd`, `.f3d`, `.sldprt`, etc.) or source script when possible; use STEP for interoperable CAD solids.
- Export **only** intended solid body/bodies, with names preserved when the application allows. For a multi-part assembly, keep deliberate body/part separation.
- Export STL **binary** where supported; set refinement high enough that curved edges have no visible facets and no critical dimension is compromised. Start with chordal deviation ~0.05–0.10 mm for general prints, tighten to ~0.01–0.05 mm for small/precision curves if warranted; ensure angular refinement and triangle counts are sensible. These are workflow recommendations, not Bambu specifications.
- Do not add millions of microscopic triangles for details smaller than actual FDM resolution; verify small holes and rounds survived tessellation.
- Confirm unit convention, correct size after reimport, axis orientation and watertightness. STL does not store units, editable features, filaments or slicer settings.
- If available, also export a geometry-only 3MF; use a **Bambu Studio project 3MF** for printer profile, orientation, supports, plates and material mapping (verify those properties after reopening). A geometry 3MF and a Bambu project 3MF are not interchangeable promises.

## 5. Automated mesh QA gate
If Python and libraries are accessible, run:

```bash
python scripts/validate_stl.py path/to/model.stl --units mm --build-volume X Y Z --json qa-mesh.json
```

Read its status and warnings. `PASS_GEOMETRY` means only that the checked geometry and bounds meet the script's checks; it does **not** prove printability. Do not silently repair user geometry in this checker. For intentional disconnected parts, use `--allow-disconnected` and record why. See `references/validation-checklist.md`.

A mesh requires manual / CAD verification for local minimum wall thickness, self-intersections, fit tolerance, source accuracy, unsupported features, topological intentions and small text. An automated watertight result is not a substitute for those checks.

## 6. Bambu Studio slice-preview gate
When Bambu Studio is available:
1. Select the **exact printer/nozzle**, compatible material preset, build plate and desired quality settings. Confirm device profile isn't inferred from an unrelated machine.
2. Import STL/3MF (or supported STEP); inspect interpreted millimeter dimensions, body and shell count, orientation, bed fit and whether the slicer suggests repairs.
3. Orient for strength, appearance, surface contact, overhangs, supports and support removal. Inspect build-height and potential collisions/exclusion areas.
4. Slice. Inspect **layer-by-layer toolpaths**, especially first layer, thin walls, holes, slots, bridges, overhang undersides, small labels, top/bottom skins, seams, supports and roofs over internal cavities.
5. Verify that critical features weren't omitted or excessively thickened by wall generation, that supports can be removed, and that the material/extrusion profile is suitable. Adjust CAD first if necessary; re-export and re-slice.
6. Save the checked Bambu Studio project `.3mf` with chosen printer, nozzle, plate, filament, orientation, support settings and relevant slicing parameters. Reopen it if feasible to confirm reproducibility.

If no Bambu Studio integration or GUI access exists, label this gate `NOT_RUN`, give exact human review steps, and **do not say "slicer verified"**.

## 7. Functional physical verification
- Print a small **calibration coupon** containing the project's decisive hole/shaft/clip/sliding gap before long/high-value parts, where possible.
- Record printer model, nozzle, filament name, slicer profile/version, measured result, orientation, dimensional deviations, and failure observations.
- Iterate CAD named parameters and version outputs. Do not claim a successful physical print without measured evidence.

## 8. Required outputs and handoff
Give the user (where tool access makes these possible):
1. Editable CAD source + optionally STEP; or the mesh master / reconstruction method when no true CAD solid exists.
2. Final `.stl` and optional geometry `.3mf`; Bambu Studio project `.3mf` only if actually created/checked there.
3. A human-readable QA report using `assets/qa-report.template.md`, plus `qa-mesh.json` if script ran.
4. A short manifest with versions, dimensions (mm), source type, target printer/nozzle/material, assumptions, warnings, recommendations and **explicit gate statuses**.
5. Preview image or dimensional sketch if genuinely generated; never pretend an illustration validates geometry.

## Status vocabulary
Use `PASS`, `FAIL`, `NOT_RUN`, or `BLOCKED` for each gate. Report `READY_FOR_TEST_PRINT` only if CAD, mesh and Bambu Studio gates pass and high-risk functional requirements are not unresolved. Reserve `PHYSICALLY_VALIDATED` for a completed test print and measurements. End with the next precise user action, if any.
