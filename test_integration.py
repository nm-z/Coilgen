import unittest
import tkinter as tk
from Window import TkinterApp
import pygame
import time

class TestTkinterPygameIntegration(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = TkinterApp(self.root)
        time.sleep(0.1)  # Give some time for the window to initialize

    def tearDown(self):
        self.app.quit()
        self.root.update()  # Process any pending events
        self.root.destroy()

    def test_window_title(self):
        self.assertEqual(self.root.title(), "Tkinter and Pygame Integration")

    def test_pygame_initialization(self):
        self.assertTrue(pygame.get_init())
        self.assertEqual(self.app.screen.get_size(), (500, 500))

    def test_blue_circle_drawn(self):
        self.app.main_loop()  # Run one frame
        center_color = self.app.get_screen_color(250, 250)
        self.assertEqual(center_color[:3], (0, 0, 255))  # Blue (ignore alpha)

    def test_background_color(self):
        self.app.main_loop()  # Run one frame
        corner_color = self.app.get_screen_color(0, 0)
        self.assertEqual(corner_color[:3], (255, 255, 255))  # White (ignore alpha)

if __name__ == '__main__':
    unittest.main()