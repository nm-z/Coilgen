# pygame_module.py

import pygame
import os

class PygameEmbed:
    def __init__(self, embed_frame_id, width, height):
        os.environ['SDL_WINDOWID'] = str(embed_frame_id)
        os.environ['SDL_VIDEODRIVER'] = 'windib'  # Use 'x11' for Linux

        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.running = True

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((255, 255, 255))  # White background
            pygame.draw.circle(self.screen, (0, 0, 255), (250, 250), 50)  # Draw a blue circle
            pygame.display.update()
            self.clock.tick(30)  # Limit to 30 FPS

        pygame.quit()
