import random
from components.obstacle import Obstacle
import math

def spawn_objects(world_boundaries, max_object_size, min_object_size, num_objects, corner_radius=100):
    """
    Spawn a number of objects with random sizes and positions, keeping corners empty
    :param world_boundaries: The boundaries of the world
    :param max_object_size: The maximum size of the object
    :param min_object_size: The minimum size of the object
    :param num_objects: The number of objects to spawn
    :param corner_radius: The radius of empty space in corners
    :return: A list of objects
    """
    objects = []
    corners = [
        (world_boundaries[0], world_boundaries[1]),  # Top-left
        (world_boundaries[2], world_boundaries[1]),  # Top-right
        (world_boundaries[0], world_boundaries[3]),  # Bottom-left
        (world_boundaries[2], world_boundaries[3])   # Bottom-right
    ]

    def is_in_corner(x, y, size):
        # Check if any part of the object would be within corner_radius of any corner
        for corner_x, corner_y in corners:
            # Check all corners of the object
            object_corners = [
                (x, y),  # Top-left
                (x + size[0], y),  # Top-right
                (x, y + size[1]),  # Bottom-left
                (x + size[0], y + size[1])  # Bottom-right
            ]
            for obj_x, obj_y in object_corners:
                distance = math.sqrt((obj_x - corner_x)**2 + (obj_y - corner_y)**2)
                if distance < corner_radius:
                    return True
        return False

    attempts = 0
    max_attempts = num_objects * 100  # Prevent infinite loop

    while len(objects) < num_objects and attempts < max_attempts:
        # Random size
        size = (
            random.randint(min_object_size[0], max_object_size[0]),
            random.randint(min_object_size[1], max_object_size[1])
        )
        # Random position
        pos = (
            random.randint(world_boundaries[0], world_boundaries[2] - size[0]),
            random.randint(world_boundaries[1], world_boundaries[3] - size[1])
        )

        if not is_in_corner(pos[0], pos[1], size):
            objects.append(Obstacle(pos, size))

        attempts += 1

    return objects