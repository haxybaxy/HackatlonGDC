import math
import time
import pygame
from components.character import Character
from components.world_gen import spawn_objects
from components.my_bot import MyBot
#TODO: add controls for multiple players
#TODO: add dummy bots so that they can train models

# TODO: Check if this is needed to be run
#screen = pygame.display.set_mode((100, 100))

class Env:
    def __init__(self, should_display=False, world_width=1280, world_height=1280, display_width=640, display_height=640, n_of_obstacles=10):
        pygame.init()

        self.screen = pygame.display.set_mode((display_width, display_height))

        # ONLY FOR DISPLAY
        # Create display window with desired display dimensions
        self.display_width = display_width
        self.display_height = display_height
        self.screen = pygame.display.set_mode((display_width, display_height))

        # REAL WORLD DIMENSIONS
        # Create an off-screen surface for the game world
        self.world_width = world_width
        self.world_height = world_height
        self.world_surface = pygame.Surface((world_width, world_height))

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

        """REWARD VARIABLES"""
        self.last_positions = {}
        self.last_damage = {}
        self.last_kills = {}
        self.last_health = {}
        self.visited_areas = {}


    def set_players_bots_objects(self, players, bots, obstacles=None):
        self.OG_players = players
        self.OG_bots = bots
        self.OG_obstacles = obstacles

        self.reset()

    def get_world_bounds(self):
        return (0, 0, self.world_width, self.world_height)

    def reset(self, randomize_objects=False, randomize_players=False):
        self.running = True
        self.screen.fill("green")
        pygame.display.flip()
        time.sleep(1)

        self.last_positions = {}
        self.last_damage = {}
        self.last_kills = {}
        self.last_health = {}
        self.visited_areas = {}

        # TODO: add variables for parameters
        if randomize_objects:
            self.OG_obstacles = spawn_objects((0, 0, self.world_width, self.world_height), self.max_obstacle_size, self.min_obstacle_size, self.n_of_obstacles)
        else:
            if self.OG_obstacles is None:
                if self.OG_obstacles is None:
                    self.OG_obstacles = spawn_objects((0, 0, self.world_width, self.world_height), self.max_obstacle_size,
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
        self.world_surface.fill("purple")

        players_info = {}
        alive_players = []
        for player in self.players:
            if player.alive:
                alive_players.append(player)
                player.reload()
                player.draw(self.world_surface)
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

        new_dic = {
            "general_info": {
                "total_players": len(self.players),
                "alive_players": len(alive_players)
            },
            "players_info": players_info
        }

        # Check if game is over
        if len(alive_players) == 1:
            print("Game Over, winner is:", alive_players[0].username)
            self.world_surface.fill("green")  # "Victory Screen" improve this
            pygame.display.flip()
            time.sleep(0.5) # remove this if not needed

            #self.running = False
            return True, new_dic # Game is over

        for obstacle in self.obstacles:
            obstacle.draw(self.world_surface)

        # flip() the display to put your work on screen
        # Scale the off-screen world surface to the display window size
        scaled_surface = pygame.transform.scale(self.world_surface, (self.display_width, self.display_height))
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

        return False, new_dic

    """TO MODIFY"""
    def calculate_reward_empty(self, info_dictionary, bot_username):
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
        health = bot_info.get("health", 0)

        # Calculate reward:
        reward = 0
        # Add your reward calculation here

        return reward

    def calculate_reward(self, info_dictionary, bot_username):
        """
        Reward function for training bots.

        Reward components (one-time per step):
          1. Walking: if the bot moves, +1 (only if it moved this step).
          2. Exploring: if the bot enters a new grid cell (e.g., 100x100), +5.
          3. Damage: reward the difference in damage inflicted this frame.
          4. Kill: reward massively for new kills (+20 per kill).
          5. Missing: if a shot was fired and no damage was dealt, -1.
          6. Getting hit: if health decreases compared to last step, negative penalty.
          7. Staying near borders: if within 50 pixels of any border, -1.
        """
        players_info = info_dictionary.get("players_info", {})
        bot_info = players_info.get(bot_username)
        if bot_info is None:
            print(f"Bot {bot_username} not found in info dictionary.")
            return 0

        # Extract current values
        current_position = bot_info.get("location", [0, 0])
        damage_dealt = bot_info.get("damage_dealt", 0)
        kills = bot_info.get("kills", 0)
        alive = bot_info.get("alive", False)
        health = bot_info.get("health", 100)
        # Expect a flag indicating if a shot was fired this frame
        shot_fired = bot_info.get("shot_fired", False)

        # Initialize tracking dictionaries if necessary
        if bot_username not in self.last_positions:
            self.last_positions[bot_username] = current_position
        if bot_username not in self.last_damage:
            self.last_damage[bot_username] = damage_dealt
        if bot_username not in self.last_kills:
            self.last_kills[bot_username] = kills
        if bot_username not in self.last_health:
            self.last_health[bot_username] = health
        if bot_username not in self.visited_areas:
            self.visited_areas[bot_username] = set()

        reward = 0

        # 1. Walking reward (one-time): if moved at all, +1
        distance_moved = math.dist(current_position, self.last_positions[bot_username])
        if distance_moved > 0:
            reward += 1

        # 2. Exploration reward (one-time): if entering a new grid cell, +5
        grid_size = 100  # You can adjust the grid size as needed.
        cell = (int(current_position[0] // grid_size), int(current_position[1] // grid_size))
        if cell not in self.visited_areas[bot_username]:
            reward += 5
            self.visited_areas[bot_username].add(cell)

        # 3. Damage reward: reward the damage inflicted this frame.
        delta_damage = damage_dealt - self.last_damage[bot_username]
        if delta_damage > 0:
            reward += delta_damage  # 1 point per damage unit

        # 4. Kill reward: massive reward for new kills.
        delta_kills = kills - self.last_kills[bot_username]
        if delta_kills > 0:
            reward += delta_kills * 20  # 20 points per kill

        # 5. Negative reward for missing: if a shot was fired and no damage occurred.
        if shot_fired and delta_damage <= 0:
            reward -= 1

        # 6. Negative reward if hit by enemy: if health decreased.
        delta_health = self.last_health[bot_username] - health
        if delta_health > 0:
            reward -= delta_health * 0.2  # adjust penalty factor as needed

        # 7. Negative reward for staying near the borders.
        border_threshold = 50
        near_border = (
                current_position[0] < border_threshold or
                current_position[0] > self.world_width - border_threshold or
                current_position[1] < border_threshold or
                current_position[1] > self.world_height - border_threshold
        )
        if near_border:
            reward -= 1

        # Update tracking values for next step.
        self.last_positions[bot_username] = current_position
        self.last_damage[bot_username] = damage_dealt
        self.last_kills[bot_username] = kills
        self.last_health[bot_username] = health

        return reward

