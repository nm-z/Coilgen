import unittest
import os
from pcb_coil_designer import generate_coil, export_coil_to_file

class TestPCB_CoilDesigner(unittest.TestCase):

    def test_generate_coil(self):
        coil = generate_coil(5, 1.0, 0.2)
        self.assertEqual(len(coil.xy[0]), 500)  # 5 turns with 100 points per turn

    def test_invalid_generate_coil(self):
        with self.assertRaises(ValueError):
            generate_coil(-1, 1.0, 0.2)
        with self.assertRaises(ValueError):
            generate_coil(5, -1.0, 0.2)
        with self.assertRaises(ValueError):
            generate_coil(5, 1.0, -0.2)

    def test_export_coil_gerber(self):
        file_path = "test_coil.gbr"
        export_coil_to_file(file_path, 'Gerber Files', 5, 1.0, 0.2)
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_export_coil_dxf(self):
        file_path = "test_coil.dxf"
        export_coil_to_file(file_path, 'DXF Files', 5, 1.0, 0.2)
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_export_coil_svg(self):
        file_path = "test_coil.svg"
        export_coil_to_file(file_path, 'SVG Files', 5, 1.0, 0.2)
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_export_coil_drill(self):
        file_path = "test_coil.txt"
        export_coil_to_file(file_path, 'Drill Files', 5, 1.0, 0.2)
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

if __name__ == '__main__':
    unittest.main()
