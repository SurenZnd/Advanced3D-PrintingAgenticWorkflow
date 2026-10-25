#!/usr/bin/env python3
"""Conservative non-mutating STL checks for Bambu Lab CAD-to-print workflows.

Checks basic topology, triangulation, connectivity, mm bounding box and optional
orientation-specific X/Y/Z fit. Does NOT check for self intersections, local wall
thickness, print supports, nozzle-feature resolution, correct mechanical fit, or
usable bed exclusions. An STL is unitless; explicit --units is mandatory.
"""

import argparse
import json
import math
import sys
from pathlib import Path


def check_positive_triplet(values, label):
    if values is None:
        return None
    if len(values) != 3 or not all(math.isfinite(x) and x > 0 for x in values):
        raise ValueError(f"{label} must be three finite positive values")
    return values


def audit_stl(args):
    try:
        import numpy as np
        import trimesh
    except ImportError as exc:
        return {"status": "ERROR", "errors": [f"Missing dependency: {exc}. Run pip install -r requirements.txt"]}, 2

    path = Path(args.file)
    if not path.is_file() or path.suffix.lower() != ".stl":
        return {"status": "ERROR", "errors": ["Input must be an existing .stl file"]}, 2

    report = {
        "file": str(path),
        "units_supplied": args.units,
        "units_interpreted_as": "mm" if args.units == "mm" else "inch (converted to mm)",
        "build_volume_mm": args.build_volume,
        "checks": {},
        "warnings": [
            "Basic mesh checks cannot prove minimum wall thickness, self-intersection freedom, "
            "supportability, correct dimensions, fit, or functional strength.",
            "Bed exclusion zones, edge clearances and part placement are not checked."
        ],
        "errors": [],
    }
    try:
        # STL loading as a mesh is deterministic for an STL file. Trimesh does
        # not repair the geometry simply by loading it.
        mesh = trimesh.load_mesh(str(path), process=False)
    except Exception as exc:
        report["errors"].append(f"Mesh could not be loaded: {type(exc).__name__}: {exc}")
        report["status"] = "FAIL"
        return report, 1
    if not isinstance(mesh, trimesh.Trimesh):
        report["errors"].append("File did not load as a single STL mesh")
        report["status"] = "FAIL"
        return report, 1

    if args.units == "inch":
        mesh.apply_scale(25.4)  # mm normalization solely in RAM for calculations

    # STL stores independent triangles: repeated coordinates do not share vertex IDs.
    # Canonicalize *identical* coordinates in memory for topology checks; this
    # does not change the user's STL or fill holes / change triangle positions.
    # Keep the original triangles for degeneration analysis.
    raw_face_areas = mesh.area_faces.copy()
    mesh.merge_vertices(digits_vertex=8)

    face_count = int(len(mesh.faces))
    vertex_count = int(len(mesh.vertices))
    if face_count == 0 or vertex_count == 0:
        report["errors"].append("Mesh has no faces or vertices")
        report["status"] = "FAIL"
        return report, 1

    points = np.asarray(mesh.vertices)
    finite = bool(np.all(np.isfinite(points)))
    report["checks"]["finite_coordinates"] = finite
    if not finite:
        report["errors"].append("Mesh contains non-finite coordinates")
        report["status"] = "FAIL"
        return report, 1

    dims = np.asarray(mesh.extents, dtype=float)
    volume = float(mesh.volume)
    bounds = np.asarray(mesh.bounds, dtype=float)
    areas = np.asarray(raw_face_areas, dtype=float)
    degenerate = int(np.count_nonzero(~np.isfinite(areas) | (areas <= 1e-12)))
    watertight = bool(mesh.is_watertight)
    winding = bool(mesh.is_winding_consistent)
    # is_volume rejects inverted solids and bad winding where trimesh detects them.
    is_volume = bool(mesh.is_volume)
    try:
        components = mesh.split(only_watertight=False)
        component_count = len(components)
    except Exception as exc:
        report["warnings"].append(f"Connected shell count unavailable: {exc}")
        component_count = None

    report["mesh"] = {
        "vertices": vertex_count,
        "triangles": face_count,
        "bounds_mm": bounds.round(6).tolist(),
        "dimensions_mm": dims.round(6).tolist(),
        "signed_volume_mm3": round(volume, 6),
        "surface_area_mm2": round(float(mesh.area), 6),
        "closed_components": component_count,
        "degenerate_triangles": degenerate,
    }
    report["checks"].update({
        "nondegenerate_triangles": degenerate == 0,
        "watertight": watertight,
        "consistent_winding": winding,
        "positive_enclosed_volume": bool(is_volume and volume > 0),
        "positive_extents": bool(np.all(dims > 0)),
    })
    for key, passed in report["checks"].items():
        if not passed:
            report["errors"].append(f"Failed: {key}")

    if component_count is not None:
        cc_ok = bool(component_count == 1 or args.allow_disconnected)
        report["checks"]["disconnected_components_accepted"] = cc_ok
        if not cc_ok:
            report["errors"].append(
                f"Detected {component_count} disconnected components; "
                "set --allow-disconnected only if those shells are intended"
            )
        if component_count > 1:
            report["warnings"].append(
                "Several disconnected shells detected. Each component's watertightness "
                "and intended multi-part arrangement need review."
            )

    if args.build_volume:
        limits = np.asarray(args.build_volume, dtype=float)
        fits = bool(np.all(dims <= limits + 1e-6))
        report["checks"]["fits_nominal_build_volume_in_current_orientation"] = fits
        if not fits:
            report["errors"].append(
                "Bounds exceed one or more nominal build-volume axes in current orientation; "
                "a different orientation may fit."
            )
        report["warnings"].append(
            "Nominal build-volume check uses bounding box only, not real machine exclusion areas."
        )
    else:
        report["warnings"].append("Build volume not supplied: machine fit is NOT_RUN.")

    if args.expected_dimensions:
        target = np.asarray(args.expected_dimensions, dtype=float)
        tolerance = args.dimension_tolerance_mm
        diff = np.abs(dims - target)
        dim_ok = bool(np.all(diff <= tolerance))
        report["checks"]["matches_expected_axis_dimensions"] = dim_ok
        report["mesh"]["dimension_differences_mm"] = diff.round(6).tolist()
        report["mesh"]["dimension_tolerance_mm"] = tolerance
        if not dim_ok:
            report["errors"].append(
                "Bounding box differs from axis-aligned expected dimensions "
                f"by more than {tolerance} mm; verify orientation and unit scale."
            )
    else:
        report["warnings"].append("No expected size supplied: cannot confirm intended CAD dimensions.")

    report["status"] = "PASS_GEOMETRY" if not report["errors"] else "FAIL"
    return report, (0 if not report["errors"] else 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="STL file to inspect, not modify")
    parser.add_argument("--units", choices=["mm", "inch"], required=True,
                        help="Units the STL author intended (STL itself has none)")
    parser.add_argument("--build-volume", type=float, nargs=3, metavar=("X", "Y", "Z"),
                        help="Nominal build volume in mm for the chosen printer")
    parser.add_argument("--expected-dimensions", type=float, nargs=3, metavar=("X", "Y", "Z"),
                        help="Expected axis-aligned bounding dimensions in mm")
    parser.add_argument("--dimension-tolerance-mm", type=float, default=0.2,
                        help="Allowed discrepancy from expected axis dimensions, default 0.2 mm")
    parser.add_argument("--allow-disconnected", action="store_true",
                        help="Accept intentional multiple independent shells (document why)")
    parser.add_argument("--json", metavar="FILE", help="Write machine-readable report")
    args = parser.parse_args()
    try:
        check_positive_triplet(args.build_volume, "--build-volume")
        check_positive_triplet(args.expected_dimensions, "--expected-dimensions")
        if not math.isfinite(args.dimension_tolerance_mm) or args.dimension_tolerance_mm < 0:
            raise ValueError("--dimension-tolerance-mm must be finite and nonnegative")
    except ValueError as exc:
        parser.error(str(exc))
    report, exit_code = audit_stl(args)
    payload = json.dumps(report, indent=2)
    print(payload)
    if args.json:
        try:
            Path(args.json).write_text(payload + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"Could not write JSON report: {exc}", file=sys.stderr)
            return 2
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
