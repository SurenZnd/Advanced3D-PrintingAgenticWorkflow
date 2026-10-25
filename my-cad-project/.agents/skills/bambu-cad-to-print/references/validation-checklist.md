# Evidence and acceptance checklist

## Geometry — CAN partly automate
- Nonempty mesh / triangles / positive volume.
- Each intended solid watertight, consistent normals/winding.
- Expected connected solid count.
- Bounding dimensions after explicit mm interpretation match source.
- Build volume fit for current orientation; additionally account for actual Bambu printer exclusion zones/usable height in the slicer.
- No obvious tiny/degenerate triangles; multiple surfaces and duplicate shells checked.

## Geometry — requires CAD/mesh-engineering review
- Local wall thickness and pin/emboss detail strength.
- No self-intersections or zero-thickness contacts; not automatically proven by watertightness.
- Critical nominal dimensions and manufacturing allowances remain correct after meshing.
- Unsupported undersides, unreachable supports, chamfers/radii, assembly / load paths.
- For render-derived content, provenance of dimensions and whether texture relief became physical geometry.

## Bambu Studio — GUI/slicer access required
- Correct exact machine, nozzle and printable material/plate preset.
- STL interpreted as intended size; bodies visible; support strategy feasible.
- First layer, wall/toolpath preview, thin walls and engraved text visible.
- Support, bridges, top surfaces, cavities, seams and Z/XY strength orientation acceptable.
- Reopened project 3MF uses the intended profile; remember project files may contain machine-specific settings.

## Physical — test print required
- Critical fit coupon physically measured.
- Surface finish, tolerances, orientation and dimensional repeatability evaluated.
- Load-bearing structural applications tested against engineering acceptance criteria; functional certification not inferred.

## Gate status semantics
- `PASS`: check actually completed and passed with evidence.
- `FAIL`: check completed and failed (include observed issue).
- `NOT_RUN`: capability not available or not attempted.
- `BLOCKED`: essential inputs missing (include what exactly is needed).
- `READY_FOR_TEST_PRINT`: may be assigned only when geometry and slicer QA both passed with no unresolved high-risk design issue. Not equivalent to physically validated.
