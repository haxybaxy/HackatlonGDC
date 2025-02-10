import pygame
import random
import time
import math
from components.crystal_obstacle import CrystalObstacle

class GameTheme:
    def __init__(self):
        self.colors = {
            'background': (25, 10, 40),  # Deep purple space
            'terrain': [
                (147, 112, 219, 100),  # Light purple
                (138, 43, 226, 100),  # Blue violet
                (75, 0, 130, 100)  # Indigo
            ],
            'obstacle': (173, 216, 230, 180),  # Crystal blue
            'grid': (148, 0, 211, 15),  # Very faint purple grid
            'player_trail': (255, 255, 255, 40),  # Glowing white trail
        }
        self.grid_size = 40
        self.grid_line_width = 1


class game_UI:
    def __init__(self, screen, world_width, world_height):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.world_width = world_width
        self.world_height = world_height
        self.theme = GameTheme()

        # Defining obstacle parameters internally
        self.n_of_obstacles = 20
        self.min_obstacle_size = (50, 50)
        self.max_obstacle_size = (100, 100)

        self.obstacles = self.create_obstacles()
        self.background = self.create_background()

    def create_obstacles(self):
        obstacles = []
        for _ in range(self.n_of_obstacles):
            width = random.randint(self.min_obstacle_size[0], self.max_obstacle_size[0])
            height = random.randint(self.min_obstacle_size[1], self.max_obstacle_size[1])
            obstacle_size = (width, height)
            x = random.randint(0, self.world_width - obstacle_size[0])
            y = random.randint(0, self.world_height - obstacle_size[1])
            obstacle = CrystalObstacle((x, y), obstacle_size)
            obstacles.append(obstacle)
        return obstacles

    def create_background(self):
        background = pygame.Surface((self.world_width, self.world_height))
        background.fill(self.theme.colors['background'])

        # Create separate surface for terrain features
        terrain_surface = pygame.Surface((self.world_width, self.world_height), pygame.SRCALPHA)

        # Add alien terrain features (crystalline formations)
        for _ in range(300):  # More details for richer appearance
            x = random.randint(0, self.world_width)
            y = random.randint(0, self.world_height)
            size = random.randint(2, 8)
            color = random.choice(self.theme.colors['terrain'])

            # Randomly choose between different alien terrain features
            feature_type = random.choice(['crystal', 'spore', 'star'])

            if feature_type == 'crystal':
                points = [
                    (x, y - size),
                    (x + size // 2, y + size // 2),
                    (x - size // 2, y + size // 2)
                ]
                pygame.draw.polygon(terrain_surface, color, points)

            elif feature_type == 'spore':
                pygame.draw.circle(terrain_surface, color, (x, y), size)
                smaller_color = list(color)
                smaller_color[3] = 150  # More transparent
                pygame.draw.circle(terrain_surface, tuple(smaller_color), (x, y), size // 2)

            else:  # star
                star_color = (255, 255, 255, random.randint(30, 100))
                pygame.draw.circle(terrain_surface, star_color, (x, y), 1)

        # Add ethereal fog effect
        for _ in range(20):
            x = random.randint(0, self.world_width)
            y = random.randint(0, self.world_height)
            size = random.randint(50, 200)
            fog_color = (147, 112, 219, 5)  # Very transparent purple
            pygame.draw.circle(terrain_surface, fog_color, (x, y), size)

        # Grid
        grid_surface = pygame.Surface((self.world_width, self.world_height), pygame.SRCALPHA)
        for x in range(0, self.world_width, self.theme.grid_size):
            pygame.draw.line(grid_surface, self.theme.colors['grid'],
                             (x, 0), (x, self.world_height), self.theme.grid_line_width)
        for y in range(0, self.world_height, self.theme.grid_size):
            pygame.draw.line(grid_surface, self.theme.colors['grid'],
                             (0, y), (self.world_width, y), self.theme.grid_line_width)

        # Combine all layers
        background.blit(terrain_surface, (0, 0))
        background.blit(grid_surface, (0, 0))
        return background

    def display_background(self, time_delay=1):
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        time.sleep(time_delay)

    def display_opening_screen(self):
        screen = pygame.display.get_surface()
        screen_width, screen_height = screen.get_size()
        start_time = pygame.time.get_ticks()

        bg_color = (25, 10, 40)  # Deep space purple
        title_color = (255, 255, 255)  # Bright white
        subtitle_color = (200, 200, 255)  # Soft light blue
        star_colors = [(255, 255, 255), (200, 200, 255), (150, 150, 255)]

        while True:
            screen.fill(bg_color)

            # Draw starry background
            for _ in range(200):
                x = random.randint(0, screen_width)
                y = random.randint(0, screen_height)
                color = random.choice(star_colors)
                size = random.randint(1, 3)
                pygame.draw.circle(screen, color, (x, y), size)

            # Title with shadow effect
            title_font = pygame.font.Font(None, 86)
            title_text = title_font.render("COSMIC BATTLE", True, title_color)
            shadow_text = title_font.render("COSMIC BATTLE", True, (50, 50, 100))

            title_rect = title_text.get_rect(center=(screen_width / 2, screen_height / 3))
            shadow_rect = shadow_text.get_rect(center=(screen_width / 2, screen_height / 3 + 3))

            screen.blit(shadow_text, shadow_rect)
            screen.blit(title_text, title_rect)

            # Subtitle with subtle animation
            subtitle_font = pygame.font.Font(None, 44)
            subtitle_text = subtitle_font.render("Press Any Key to Start", True, subtitle_color)
            subtitle_rect = subtitle_text.get_rect(center=(screen_width / 2, screen_height / 2 + 100))

            # Blinking effect
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                screen.blit(subtitle_text, subtitle_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    return

            pygame.time.delay(40)

    def display_winner_screen(self, alive_players):
        winner_screen = self.background.copy()
        font = pygame.font.Font(None, 74)
        text = font.render(f"Winner: {alive_players[0].username}!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.world_width / 2, self.world_height / 2))
        winner_screen.blit(text, text_rect)
        self.screen.blit(winner_screen, (0, 0))
        pygame.display.flip()
        time.sleep(0.5)

    def draw_everything(self, dictionary, players, obstacles):
        self.screen.blit(self.background, (0, 0))

        # Draw obstacles
        for obstacle in obstacles:
            obstacle.draw(self.screen)

        # Draw players
        for player in players:
            if player.alive:
                player.draw(self.screen)

        pygame.display.flip()

        # Retrieve players' information
        players_info = dictionary.get("players_info", {})

        for bot_info in players_info:
            print(bot_info)

            bot_info = players_info.get(bot_info)

            # if the bot is not found, return a default reward of 0
            if bot_info is None:
                print("Bot not found in the dictionary")
                return 0

            # Extract variables from bot's info
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