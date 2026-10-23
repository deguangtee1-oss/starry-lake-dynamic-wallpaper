import unittest
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.create_v11 import P0, P1, star_position, overlay_point_star

class V11StarTests(unittest.TestCase):
    def test_motion_is_monotone_down_left(self):
        a = star_position(0.6)
        b = star_position(7.4)
        self.assertIsNotNone(a)
        self.assertIsNotNone(b)
        self.assertLess(b[0], a[0])
        self.assertGreater(b[1], a[1])
        self.assertLess(P1[0], P0[0])
        self.assertGreater(P1[1], P0[1])

    def test_absent_at_loop_seam(self):
        self.assertIsNone(star_position(0.0))
        self.assertIsNone(star_position(7.99))

    def test_overlay_is_local_and_point_sized(self):
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        before = frame.copy()
        overlay_point_star(frame, 4.0)
        ys, xs = np.where(np.any(frame != before, axis=2))
        self.assertGreater(len(xs), 0)
        self.assertLessEqual(xs.max() - xs.min(), 8)
        self.assertLessEqual(ys.max() - ys.min(), 8)
        self.assertGreater(xs.min(), 650)
        self.assertLess(xs.max(), 750)

if __name__ == "__main__":
    unittest.main()
