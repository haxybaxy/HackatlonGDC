import random
from Obstacle import Obstacle


def spawn_objects(world_boundaries, max_object_size, min_object_size, num_objects):
    """
    Spawn a number of objects with random sizes and positions
    :param world_boundaries: The boundaries of the world
    :param max_object_size: The maximum size of the object
    :param min_object_size: The minimum size of the object
    :param num_objects: The number of objects to spawn
    :return: A list of objects
    """
    objects = []
    for i in range(num_objects):
        # Random size
        size = (random.randint(min_object_size[0], max_object_size[0]), random.randint(min_object_size[1], max_object_size[1]))
        # Random position
        pos = (random.randint(world_boundaries[0], world_boundaries[2]), random.randint(world_boundaries[1], world_boundaries[3]))
        objects.append(Obstacle(pos, size))
    return objects
