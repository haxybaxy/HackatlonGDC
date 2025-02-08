# Environment Readme

## Overview
The environment simulates a game space where players and bots interact. The primary objective is to allow bots to train and improve their decision-making based on observations of their surroundings. The game space consists of a defined width and height, obstacles, and multiple players controlled by either users or AI bots.

## Components
The environment consists of the following key elements:
- **Players:** Characters controlled by the bots.
- **Bots:** AI or Manually Tuned agents that make decisions based on observations.
- **Obstacles:** Objects in the game world that players must navigate around.
- **Game World:** A 2D grid with defined boundaries (1280x1280 by default, this value should not be changed). (Note that the window might be larger than your computer supports)

## Setting Up the Environment
To initialize the environment:
```python
environment = Env() # optionally you can change the number of obstacles with the parameter n_of_obstacles
screen = environment.screen
world_bounds = environment.get_world_bounds()
```

### Adding Players and Bots
Players and bots need to be added before running the environment.
- An example is already provided in the script:
```python
players = [
    Character((world_bounds[2]-100, world_bounds[3]-100), screen, boundaries=world_bounds, username="Ninja"),

    Character((world_bounds[0], world_bounds[1]), screen, boundaries=world_bounds, username="Faze Jarvis")
]

bots = [
    MyBot(),
    MyBot()
]

environment.set_players_bots_objects(players, bots)
```
- Ensure that the number of players and bots match

## Running the Game Loop
To run the environment:
```python
while True:
    finished, info = environment.step()
    if finished:
        # This means a game over condition has been reached
        break
    else:
        # Used to control the game speed, can be modified according to hardware capabilities
        environment.clock.tick(60)
```

## Understanding the Returned Dictionary
Each step of the environment returns a dictionary containing game state information for each player.

### Dictionary Structure
```python
{
    "general_info": {
        "total_players": int,  # Total number of players in the game
        "alive_players": int   # Number of players still alive
    },
    "players_info": {
        "player_username": {
            "location": [x, y],        # Player's current coordinates
            "rotation": angle,         # Player's rotation angle in degrees
            "rays": [ray1, ray2, ...], # List of rays (each ray represents a detected obstacle or enemy)
            "current_ammo": int,       # Amount of ammunition left
            "alive": bool,             # Whether the player is still alive
            "kills": int,              # Number of enemies the player has eliminated
            "damage_dealt": int,       # Total damage dealt to opponents
            "meters_moved": int,       # Distance moved since game start
            "total_rotation": int      # Total amount of rotation performed
        }
    }
}
```

### Example Output
```python
{
    "general_info": {
        "total_players": 2,
        "alive_players": 1
    },
    "players_info": {
        "Ninja": {
            "location": [100, 200],
            "rotation": 90,
            "rays": [[((1125, 625), (1114.53, 824.726)), None, 'none'], [((1125, 625), (1059.89, 814.104)), None, 'none'], [((1125, 625), (1010.28, 788.83)), None, 'none'], [((1125, 625), (969.571, 750.864)), None, 'none'], [((1125, 625), (940.899, 703.146)), None, 'none']], 
            "current_ammo": 15,
            "alive": True,
            "kills": 1,
            "damage_dealt": 100,
            "meters_moved": 50,
            "total_rotation": 180
        },
        "Faze Jarvis": {
            "location": [300, 400],
            "rotation": 45,
            "rays": [[((1125, 645), (929.370479853239, 603.4176618364475)), None, 'none'], [((1125, 645), (948.4104814282149, 551.1056874428214)), None, 'none'], [((1125, 645), (981.1320399322702, 506.06832590820005)), None, 'none'], [((1125, 645), (1094.4004357329502, 592.0)), 61.19912853410015, 'object'], [((1125, 645), (1111.7856158493116, 592.0)), 54.62252235554455, 'object']],
            "current_ammo": 10,
            "alive": False,
            "kills": 0,
            "damage_dealt": 0,
            "meters_moved": 20,
            "total_rotation": 90
        }
    }
}
```

### Explanation
- **`general_info`**: Provides an overview of the game state, including the total number of players and how many are still alive.
- **`players_info`**: Contains detailed data about each player's state.
  - **`location`**: Represents the current coordinates of the player.
  - **`rotation`**: The angle at which the player is facing.
  - **`rays`**: List of rays (5 total) used to detect objects and players. Each ray consists of:
    - **Start and end points**
    - **Distance**
    - **Hit type** ("object" or "player")
  - **`current_ammo`**: Remaining ammunition.
  - **`alive`**: Indicates whether the player is still in the game.
  - **`kills`**: The number of players this character has eliminated.
  - **`damage_dealt`**: Total damage done to opponents.
  - **`meters_moved`**: Distance moved in the game world.
  - **`total_rotation`**: Sum of all rotations performed.

## Modifying Bots
Bots can be modified by changing the `act` method of the `MyBot` class.
```python
class MyBot():
    def act(self, info):
        actions = {
            "forward": random.choice([True, False]),
            "right": random.choice([True, False]),
            "down": random.choice([True, False]),
            "left": random.choice([True, False]),
            "rotate": random.randint(-180, 180),
            "shoot": random.choice([True, False])
        }
        return actions
```
