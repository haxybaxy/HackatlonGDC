import time

from Environment import Env
from components.clean_bot import MyBot
from components.character import Character


if __name__ == "__main__":
    # game space is 1280x1280

    environment = Env(display_width=800, display_height=800, n_of_obstacles=25)
    screen = environment.screen

    world_bounds = environment.get_world_bounds()


    """SETTING UP CHARACTERS >>> UPDATE THIS"""
    players = [

    Character((world_bounds[2]-100, world_bounds[3]-100), screen, boundaries=world_bounds, username="Ninja"),

    Character((world_bounds[0], world_bounds[1]), screen, boundaries=world_bounds, username="Faze Jarvis")

    ]

    """ENSURE THERE ARE AS MANY BOTS AS PLAYERS >>> UPDATE THIS"""
    bots = [

        MyBot(),
        MyBot()

    ]

    environment.set_players_bots_objects(players, bots) # Environment should be ready

    time_limit = 120 # Time limit to force a match to end
    epochs = 100

    # THIS WILL PERFORM A SINGLE GAME
    for epochs in range(epochs):
        start_time = time.time()
        while True:
            if start_time + time_limit < time.time():
                print("Game Over, time limit reached")
                break

            finished, info = environment.step()
            for player in players:
                reward = environment.calculate_reward(info, player.username)
                print("Reward for", player.username, "is:", reward)

            print(info)
            if finished:
                break
            else:
                environment.clock.tick(120) # 120 FPS