import pygame
from Character import Character
from Obstacle import Obstacle
from world_gen import spawn_objects


def run_game():

    """VARIABLES"""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    """SETTING UP OBJECTS"""
    obstacles = spawn_objects((0, 0, screen.get_width(), screen.get_height()), (100, 100), (50, 50), 10)


    """SETTING UP CHARACTERS >>> UPDATE THIS"""
    character = Character((screen.get_width()-100, screen.get_height()-100),  screen, boundaries=(0, 0, screen.get_width(), screen.get_height()), objects=obstacles)
    character2 = Character((0, 0),  screen, boundaries=(0, 0, screen.get_width(), screen.get_height()), objects=obstacles)

    players = [character, character2]

    # Here we setup player lists for each player once we created all players
    for player in players:
        temp = players.copy()
        temp.remove(player)
        player.players = temp

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        for player in players:
            player.reload() # Can be optimized but this should do the trick

        for player in players:
            player.reload()
            player.draw(screen)
            player.debug_draw(screen)

        for obstacle in obstacles:
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
        if keys[pygame.K_BACKSPACE]:
            character.add_rotate(-5)
        if keys[pygame.K_SPACE]:
            character.shoot()

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_game()