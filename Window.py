import pygame
import tkinter as tk
from tkinter import Frame
import os
import sys

# Add the correct path to the Pygame library
pygame_path = "/path/to/your/venv/lib/python3.x/site-packages"
sys.path.insert(0, pygame_path)

class TkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter and Pygame Integration")
        self.embed_frame = Frame(root, width=500, height=500)
        self.embed_frame.pack()

        # Setting up pygame
        os.environ['SDL_WINDOWID'] = str(self.embed_frame.winfo_id())
        
        # Try different video drivers
        drivers = ['windib', 'x11']
        for driver in drivers:
            os.environ['SDL_VIDEODRIVER'] = driver
            try:
                pygame.init()
                self.screen = pygame.display.set_mode((500, 500))
                print(f"Successfully initialized Pygame with driver: {driver}")
                break
            except Exception as e:
                print(f"Error initializing Pygame with driver {driver}: {e}")
                pygame.quit()
        else:
            raise Exception("No suitable video driver found!")

        self.clock = pygame.time.Clock()

        # Start the Pygame loop
        self.running = True
        self.root.after(0, self.main_loop)  # Delay the start of the main loop

    def main_loop(self):
        if not self.running:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        self.screen.fill((255, 255, 255))  # White background
        pygame.draw.circle(self.screen, (0, 0, 255), (250, 250), 50)  # Draw a blue circle
        pygame.display.update()
        self.clock.tick(30)  # Limit to 30 FPS

        self.root.after(33, self.main_loop)  # Schedule the next update

    def quit(self):
        self.running = False
        pygame.quit()
        self.root.quit()
        self.root.destroy()

    def get_screen_color(self, x, y):
        return self.screen.get_at((x, y))