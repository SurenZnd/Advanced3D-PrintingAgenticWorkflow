# Routing CAD, 3D render geometry and rendered pictures to printable meshes

## Four paths

**A — True CAD solid** (FreeCAD, Fusion, Onshape, SolidWorks, STEP): verify units/solids, fully dimension functional features, close surface bodies, export high-quality mesh. Preserve native/STEP source.

**B — CAD surface/render-body file** (NURBS surfaces, meshes exported by CAD-to-render pipeline): determine what is inside the file, not what its filename implies. For surfaces stitch/thicken/close into solid; for triangulated render mesh weld intentional seams, remove only known irrelevant internal geometry, fix outward normals, repair non-manifold regions, check thickness. Preserve the original and the edited master.

**C — Game/render mesh** (OBJ, FBX, GLB/GLTF, Blender geometry): units and coordinate conventions may be arbitrary; rescale using an explicitly known dimension. Textures, shaders, displacement maps, alpha cutouts and normal maps typically do **not** become physical 3D geometry in STL. Apply/convert geometry-affecting modifiers only as appropriate, close and thicken surfaces, eliminate self-intersections, verify volume, then export mesh. Separate nonprinting objects. An aesthetically excellent rendered mesh can be structurally unsuitable for FDM.

**D — 2D rendered still/video frame:** image pixels do not contain enough information to uniquely recover depth, back surfaces, hidden features, exact curvature or scale. Request dimensioned drawings, at least one known dimension, multiple orthographic views or calibrated scan data for functional accuracy. Build parametric solids from these references; for decorative objects, model approximate geometry and clearly state accuracy limitations. Do not label generated depth inference 'measured CAD'.

## Non-negotiable mesh checks
- Correct scale and units: confirm size after import; STL itself has no unit metadata.
- Positive volume, intentional closed surfaces, consistently directed winding/normals.
- No open boundaries, unintended loose shells, degenerate faces, self-intersections, zero-thickness wall junctions, intersecting nested bodies without intended union.
- Features survive voxel/boolean/triangulation resolution and slicer toolpath generation.
- Texture/material/color information handled separately: STL geometry alone does not encode meaningful color or image texture; consider 3MF multi-part Bambu Studio workflow.

## Filenames / representations
- `part_source.[cad format]` — editable reference.
- `part_step.step` — solid interchange where feasible.
- `part_mesh_master.[blend|obj|...]` — editable render mesh if source wasn't CAD.
- `part_print.stl` — geometry-only, units must be communicated.
- `part_bambu_project.3mf` — Bambu Studio plate, printer and print profile if actually saved there.

If an STL is automatically repaired, compare its form, holes, body connectivity and dimensional envelope with the source. Auto-repair can fill intentional holes or join/discard elements.

**Parametric script sources:** For OpenSCAD, CadQuery, FreeCAD Python scripts or Blender geometry-node scripts, preserve the generating script and all dimensional parameters. Execute deterministic regeneration, check boolean outcomes, then export the resulting closed mesh. A pretty CAD viewport or rendered picture is not evidence of watertight generated geometry.
