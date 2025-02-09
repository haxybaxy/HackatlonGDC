import time

from Environment import Env
from components.bot import MyBot
from components.character import Character


if __name__ == "__main__":
    # game space is 1280x1280

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
        for player in players:
            reward = environment.calculate_reward(info, player.username)
            print("Reward for", player.username, "is:", reward)

        print(info)
        if finished:
            break
        else:
            environment.clock.tick(60)