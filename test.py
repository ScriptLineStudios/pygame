import pygame
display=pygame.display.set_mode((600,600))
surf = pygame.image.load("test.png")

while True:
    display.blit(pygame.transform.blur(surf, 2), (0, 0))
    pygame.display.update()