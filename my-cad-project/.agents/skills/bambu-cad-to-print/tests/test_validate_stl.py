"""Lightweight local smoke tests: python -m unittest discover -s tests -v"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'validate_stl.py'


class MeshValidatorTests(unittest.TestCase):
    def invoke(self, mesh, extra, units='mm'):
        with tempfile.TemporaryDirectory() as td:
            filepath = Path(td) / 'part.stl'
            mesh.export(str(filepath))
            p = subprocess.run(
                [sys.executable, str(SCRIPT), str(filepath), '--units', units] + extra,
                capture_output=True, text=True, check=False,
            )
            return p.returncode, json.loads(p.stdout)

    def test_box_passes(self):
        code, data = self.invoke(trimesh.creation.box(extents=[20, 10, 5]),
                                 ['--build-volume', '256', '256', '256',
                                  '--expected-dimensions', '20', '10', '5'])
        self.assertEqual(code, 0, data.get('errors'))
        self.assertEqual(data['status'], 'PASS_GEOMETRY')

    def test_open_surface_fails(self):
        mesh = trimesh.creation.box(extents=[20, 10, 5])
        mesh.update_faces([i for i in range(len(mesh.faces)) if i != 0])
        code, data = self.invoke(mesh, [])
        self.assertEqual(code, 1)
        self.assertFalse(data['checks']['watertight'])

    def test_build_volume_fails(self):
        code, data = self.invoke(trimesh.creation.box(extents=[300, 10, 5]),
                                 ['--build-volume', '256', '256', '256'])
        self.assertEqual(code, 1)
        self.assertFalse(data['checks']['fits_nominal_build_volume_in_current_orientation'])

    def test_units_inch_converted(self):
        code, data = self.invoke(trimesh.creation.box(extents=[1, 1, 1]),
                                 ['--build-volume', '30', '30', '30',
                                  '--expected-dimensions', '25.4', '25.4', '25.4'],
                                 units='inch')
        self.assertEqual(code, 0, data.get('errors'))
        self.assertEqual(data['mesh']['dimensions_mm'], [25.4, 25.4, 25.4])

    def test_disconnected_parts_need_explicit_approval(self):
        mesh = trimesh.util.concatenate([
            trimesh.creation.box(extents=[4, 4, 4]),
            trimesh.creation.box(extents=[4, 4, 4]).apply_translation([10, 0, 0]),
        ])
        code, data = self.invoke(mesh, [])
        self.assertEqual(code, 1)
        self.assertFalse(data['checks']['disconnected_components_accepted'])
        code, data = self.invoke(mesh, ['--allow-disconnected'])
        self.assertEqual(code, 0, data.get('errors'))


if __name__ == '__main__':
    unittest.main()
