import random
import time

import pygame


class GameTheme:
    def __init__(self):
        self.colors = {
            'background': (34, 39, 46), #DArk Blue
            'grass': [(34, 139, 34), (46, 154, 46)], #Two shades of Green
            'obstacle': (75, 83, 88), #Grey
            'grid': (50, 50, 50, 30), #Semi-transparent Grid
            'player_trail': (255, 255, 255, 30), #Semi-transparent White
        }
        self.grid_size = 50
        self.grid_line_width = 1


class game_UI:
    def __init__(self, screen, world_width, world_height):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.world_width = world_width
        self.world_height = world_height

        self.bots = []
        self.obstacles = []
        self.players = []
        self.alive_players = []


        self.theme = GameTheme()
        self.background = self.create_background() #Create background surface once (below)

    def create_background(self):
        background = pygame.Surface((self.world_width, self.world_height))
        background.fill(self.theme.colors['background'])

        #Grass pattern
        for x in range(0, self.world_width, 10):
            for y in range(0, self.world_height, 10):
                if random.random() < 0.3: #30% chance for grass detail
                    size = random.randint(2,4)
                    color = random.choice(self.theme.colors['grass'])
                    pygame.draw.circle(background, color, (x,y), size)

        #Grid
        grid_surface = pygame.Surface((self.world_width, self.world_height), pygame.SRCALPHA)
        for x in range(0, self.world_width, self.theme.grid_size):
            pygame.draw.line(grid_surface, self.theme.colors['grid'], (x, 0), (x, self.world_height), self.theme.grid_line_width)
        for y in range(0, self.world_height, self.theme.grid_size):
            pygame.draw.line(grid_surface, self.theme.colors['grid'],
                             (0, y), (self.world_width, y), self.theme.grid_line_width)

        background.blit(grid_surface, (0, 0))
        return background

    def display_background(self, time_delay=1):
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        time.sleep(time_delay)

    def display_winner_screen(self, alive_players):
        winner_screen = self.background.copy()
        font = pygame.font.Font(None, 74)
        text = font.render(f"Winner: {alive_players[0].username}!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.world_width / 2, self.world_height / 2))
        winner_screen.blit(text, text_rect)
        self.screen.blit(winner_screen, (0, 0))

        pygame.display.flip()
        time.sleep(0.5)  # remove this if not needed - I sure need it

    def draw_everything(self, dictionary, players, obstacles):
        # here use self.screen and draw what you want, characters ecc ecc

        # retrieve the players' information from the dictionary
        players_info = dictionary.get("players_info", {})

        for bot_info in players_info:

            print(bot_info)

            bot_info = players_info.get(bot_info)

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


        #NOT SURE IF THIS WORKS
