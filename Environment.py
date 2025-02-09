import time
import pygame
from components.character import Character
from components.world_gen import spawn_objects
from components.bot import MyBot
#TODO: add controls for multiple players
#TODO: add dummy bots so that they can train models

# TODO: Check if this is needed to be run
#screen = pygame.display.set_mode((100, 100))

class Env:
    def __init__(self, should_display=False, width=1280, height=1280, n_of_obstacles=10):
        pygame.init()
        screen = pygame.display.set_mode((width, height))

        self.width = width
        self.height = height
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.display = should_display # If you want to display the game or not

        self.n_of_obstacles = n_of_obstacles
        self.min_obstacle_size = (50, 50)
        self.max_obstacle_size = (100, 100)

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
            self.OG_obstacles = spawn_objects((0, 0, self.width, self.height), self.max_obstacle_size, self.min_obstacle_size, self.n_of_obstacles)
        else:
            if self.OG_obstacles is None:
                if self.OG_obstacles is None:
                    self.OG_obstacles = spawn_objects((0, 0, self.width, self.height), self.max_obstacle_size,
                                                      self.min_obstacle_size, self.n_of_obstacles)

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

    def step(self, debugging=False):
        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("purple")

        players_info = {}
        alive_players = []
        for player in self.players:
            if player.alive:
                alive_players.append(player)
                player.reload()
                player.draw(self.screen)
                actions = player.related_bot.act(player.get_info())
                if debugging:
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

            players_info[player.username] = player.get_info()

        # Check if game is over
        if len(alive_players) == 1:
            print("Game Over, winner is:", alive_players[0].username)
            self.screen.fill("green")  # "Victory Screen" improve this
            pygame.display.flip()
            time.sleep(0.5) # remove this if not needed

            #self.running = False
            return True, players_info # Game is over

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

        new_dic = {
            "general_info" : {
                "total_players": len(self.players),
                "alive_players": len(alive_players)
            },
            "players_info": players_info
        }

        return False, players_info

    """TO MODIFY"""
    def calculate_reward(self, info_dictionary, bot_username):
        """THIS FUNCTION IS USED TO CALCULATE THE REWARD FOR A BOT"""
        """NEEDS TO BE WRITTEN BY YOU TO FINE TUNE YOURS"""

        # retrieve the players' information from the dictionary
        players_info = info_dictionary.get("players_info", {})
        bot_info = players_info.get(bot_username)

        # if the bot is not found, return a default reward of 0
        if bot_info is None:
            print("Bot not found in the dictionary")
            return 0

        # Extract variables from the bot's info
        location = bot_info.get("location", [0, 0])
        rotation = bot_info.get("rotation", 0)
        rays = bot_info.get("rays", [])
        current_ammo = bot_info.get("current_ammo", 0)
        alive = bot_info.get("alive", False)
        kills = bot_info.get("kills", 0)
        damage_dealt = bot_info.get("damage_dealt", 0)
        meters_moved = bot_info.get("meters_moved", 0)
        total_rotation = bot_info.get("total_rotation", 0)

        # Calculate reward:
        reward = 0
        # Add your reward calculation here

        return reward


