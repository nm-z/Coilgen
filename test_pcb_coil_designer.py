import unittest
from pcb_coil_designer import generate_coil

class TestPCB_CoilDesigner(unittest.TestCase):

    def test_generate_coil(self):
        coil = generate_coil(5, 1.0, 0.2)
        self.assertEqual(len(coil.xy[0]), 501)  # 5 turns with 100 points per turn + 1 initial point

    def test_invalid_generate_coil(self):
        with self.assertRaises(ValueError):
            generate_coil(-1, 1.0, 0.2)
        with self.assertRaises(ValueError):
            generate_coil(5, -1.0, 0.2)
        with self.assertRaises(ValueError):
            generate_coil(5, 1.0, -0.2)

if __name__ == '__main__':
    unittest.main()
