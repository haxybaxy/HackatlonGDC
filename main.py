import pygame
from Character import Character
from Obstacle import Obstacle

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
obstacle = Obstacle((100, 100), (50, 50))
character = Character((screen.get_width() / 2, screen.get_height() / 2), boundaries=(0, 0, screen.get_width(), screen.get_height()), objects=[obstacle])

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    #pygame.draw.circle(screen, "red", player_pos, 40)

    character.draw(screen)
    character.debug_draw(screen)
    obstacle.draw(screen)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        character.move_in_direction("forward")
    if keys[pygame.K_s]:
        character.move_in_direction("down")
    if keys[pygame.K_a]:
        character.move_in_direction("left")
    if keys[pygame.K_d]:
        character.move_in_direction("right")
    if keys[pygame.K_RETURN]:
        character.add_rotate(5)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()