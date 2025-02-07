import time
import pygame
from Character import Character
from world_gen import spawn_objects
from bot import MyBot
#TODO: add controls for multiple players
#TODO: add dummy bots so that they can train models

def run_game():

    """VARIABLES"""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    bots = []

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

        alive_players = []
        for player in players:
            if player.alive:
                alive_players.append(player)
                player.reload()
                player.draw(screen)
                actions = player.related_bot.act(player.get_info())
                print("Bot would like to do:", actions)
                actions = {
                    "forward": True,
                    "right": False,
                    "down": False,
                    "left": False,
                    "rotate": 0,
                    "shoot": False
                }
                if actions["forward"]:
                    player.move_in_direction("forward")
                if actions["right"]:
                    player.move_in_direction("right")
                if actions["down"]:
                    player.move_in_direction("down")
                if actions["left"]:
                    player.move_in_direction("left")
                if actions["rotate"]:
                    player.add_rotate(actions["rotate"])
                if actions["shoot"]:
                    player.shoot()

        # Check if game is over
        if len(alive_players) == 1:
            print("Game Over, winner is:", alive_players[0].username)
            screen.fill("green") # "Victory Screen" improve this
            pygame.display.flip()
            time.sleep(2)
            running = False

        for obstacle in obstacles:
            obstacle.draw(screen)

        #Use for manual override
        """
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
            character.shoot()"""

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_game()