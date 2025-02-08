import random
import time
import pygame
from Character import Character
from world_gen import spawn_objects
from bot import MyBot
#TODO: add controls for multiple players
#TODO: add dummy bots so that they can train models

screen = pygame.display.set_mode((500, 500))

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

class Env:
    def __init__(self, should_display=False, width=1280, height=700, n_of_obstacles=10):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.theme = GameTheme()

        self.background = self.create_background() #Create background surface once (below)

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

    def create_background(self):
        background = pygame.Surface((self.width, self.height))
        background.fill(self.theme.colors['background'])

        #Grass pattern
        for x in range(0, self.width, 10):
            for y in range(0, self.height, 10):
                if random.random() < 0.3: #30% chance for grass detail
                    size = random.randint(2,4)
                    color = random.choice(self.theme.colors['grass'])
                    pygame.draw.circle(background, color, (x,y), size)

        #Grid
        grid_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for x in range(0, self.width, self.theme.grid_size):
            pygame.draw.line(grid_surface, self.theme.colors['grid'], (x, 0), (x, self.height), self.theme.grid_line_width)
        for y in range(0, self.height, self.theme.grid_size):
            pygame.draw.line(grid_surface, self.theme.colors['grid'],
                             (0, y), (self.width, y), self.theme.grid_line_width)

        background.blit(grid_surface, (0, 0))
        return background

    def draw_obstacle(self, obstacle):
        #Shadow
        shadow_offset = 5
        shadow_rect = obstacle.rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        pygame.draw.rect(self.screen, (0,0,0,50), shadow_rect, border_radius=8)

        #Main obstacle
        pygame.draw.rect(self.screen, self.theme.colors['obstacle'], obstacle.rect, border_radius=8)

        #Highlight
        highlight = pygame.Surface((obstacle.rect.width, obstacle.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 255, 255, 30), highlight.get_rect(), border_radius=8)
        self.screen.blit(highlight, obstacle.rect)

    def set_players_bots_objects(self, players, bots, obstacles=None):
        self.OG_players = players
        self.OG_bots = bots
        self.OG_obstacles = obstacles

        self.reset()

    def get_world_bounds(self):
        return (0, 0, self.width, self.height)

    def reset(self, randomize_objects=False, randomize_players=False):
        self.running = True
        self.screen.blit(self.background, (0, 0))
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
            if hasattr(player, 'previous_positions'):
                player.previous_positions = []

    def step(self, debugging=False):
        #Background
        self.screen.blit(self.background, (0,0))

        players_info = {}
        alive_players = []

        #Player trials
        for player in self.players:
            if player.alive:
                if hasattr(player, 'previous_positions'):
                    for pos in player.previous_positions[-10:]:
                        pygame.draw.circle(self.screen, self.theme.colors['player_trail'], pos, player.rect.width // 2)


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

                #Store position for trial
                if not hasattr(player, 'previous_positions'):
                    player.previous_positions = []
                player.previous_positions.append(player.rect.center)
                if len(player.previous_positions) > 10:
                    player.previous_positions.pop(0)

            players_info[player.username] = player.get_info()

        # Check if game is over
        if len(alive_players) == 1:
            print("Game Over, winner is:", alive_players[0].username)
            winner_screen = self.background.copy()
            font = pygame.font.Font(None, 74)
            text = font.render(f"Winner: {alive_players[0].username}!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.width/2, self.height/2))
            winner_screen.blit(text, text_rect)
            self.screen.blit(winner_screen, (0, 0))
            pygame.display.flip()
            time.sleep(0.5) # remove this if not needed - I sure need it

            #self.running = False
            return True, players_info # Game is over

        for obstacle in self.obstacles:
            self.draw_obstacle(obstacle)

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


if __name__ == "__main__":
    # game space is 1280x720

    environment = Env(n_of_obstacles=25)
    screen = environment.screen

    world_bounds = environment.get_world_bounds()


    """SETTING UP CHARACTERS >>> UPDATE THIS"""
    players = [

    Character((world_bounds[2]-100, world_bounds[3]-100), screen, boundaries=world_bounds, username="Ninja"),

    Character((world_bounds[0], world_bounds[1]), screen, boundaries=world_bounds, username="Faze Jarvis")

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

        finished, info = environment.step()
        print(info)
        if finished:
            break
        else:
            environment.clock.tick(60)