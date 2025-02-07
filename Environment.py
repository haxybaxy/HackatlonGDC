import random
import time
import pygame
from Character import Character
from world_gen import spawn_objects
from bot import MyBot
#TODO: add controls for multiple players
#TODO: add dummy bots so that they can train models


class Env:
    def __init__(self, should_display=False, width=1280, height=720):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.running = True

        self.display = should_display # If you want to display the game or not

        # INIT SOME VARIABLES
        self.OG_bots = None
        self.OG_players = None
        self.OG_obstacles = None

        self.bots = None
        self.players = None
        self.obstacles = None

    def set_players_bots_objects(self, players, bots, obstacles=None):
        self.OG_players = players
        self.OG_bots = bots
        self.OG_obstacles = obstacles

        self.reset()

    def get_world_bounds(self):
        return (0, 0, self.width, self.height)

    def reset(self, randomize_objects=False, randomize_players=False):
        self.running = True
        self.screen.fill("green")
        pygame.display.flip()
        time.sleep(1)

        # TODO: add variables for parameters
        if randomize_objects:
            self.obstacles = spawn_objects((0, 0, self.width, self.height), (100, 100), (50, 50), 10)
        else:
            if self.OG_obstacles is None:
                self.OG_obstacles = spawn_objects((0, 0, self.width, self.height), (100, 100),
                                          (50, 50), 10)

            self.obstacles = self.OG_obstacles

        self.players = self.OG_players.copy()
        self.bots = self.OG_bots
        if randomize_players:
            self.bots = self.bots.shuffle()
            for index in range(len(self.players)):
                self.players[index].related_bot = self.bots[index] # ensuring bots change location

        else:
            for index in range(len(self.players)):
                self.players[index].related_bot = self.bots[index]

        # Here we setup player lists for each player once we created all players
        for player in self.players:
            player.reset()
            temp = self.players.copy()
            temp.remove(player)
            player.players = temp # Setting up players for each player
            player.objects = self.obstacles # Setting up obstacles for each player

    def step(self):
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("purple")

        alive_players = []
        for player in self.players:
            if player.alive:
                alive_players.append(player)
                player.reload()
                player.draw(screen)
                actions = player.related_bot.act(player.get_info())
                print("Bot would like to do:", actions)
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
            self.screen.fill("green")  # "Victory Screen" improve this
            pygame.display.flip()
            time.sleep(0.5) # remove this if not needed

            #self.running = False
            return False # Game is over

        for obstacle in self.obstacles:
            obstacle.draw(screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

        return True


if __name__ == "__main__":
    # game space is 1280x720

    environment = Env()
    screen = environment.screen

    world_bounds = environment.get_world_bounds()


    """SETTING UP CHARACTERS >>> UPDATE THIS"""
    players = [

    Character((1280 - 100, 720 - 100), screen, boundaries=world_bounds),

    Character((0, 0), screen, boundaries=world_bounds)

    ]

    """ENSURE THERE ARE AS MANY BOTS AS PLAYERS"""
    bots = [

        MyBot(),
        MyBot()

    ]

    environment.set_players_bots_objects(players, bots) # Environment should be ready
    st = time.time()
    while True:
        if st + 15 < time.time():
            environment.reset()
            st = time.time()
        if not environment.step():
            break
        else:
            environment.clock.tick(60)