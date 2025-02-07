import pygame
import math

from utils import find_hit_point_on_rectangle, distance_between_points


class Character:
    def __init__(self, starting_pos, screen, speed=5, boundaries=None, objects=None):
        self.pos = pygame.Vector2(starting_pos)
        self.speed = speed
        self.rotation = 0
        self.max_boundaries = boundaries
        self.distance_vision = 200
        self.objects = objects if objects is not None else []

        self.screen = screen
        self.players = []
    "<<<<FOR USERS START>>>>"
    """GETTERS"""
    def get_location(self):
        # returns the position of the character in (x, y) format
        return self.pos

    def get_rotation(self):
        # returns the rotation of the character in degrees
        return self.rotation

    def get_rays(self):
        # returns a list of rays, each represented by a tuple of the form ((start_x, start_y), (end_x, end_y), distance, hit_type)
        # distance is None if no intersection, hit_type is "object" or "player" if intersection
        return self.create_rays()

    """SETTERS"""
    def move_in_direction(self, direction):  # forward, right, down, left
        if direction == "forward":
            self.pos.y -= self.speed
        elif direction == "right":
            self.pos.x += self.speed
        elif direction == "down":
            self.pos.y += self.speed
        elif direction == "left":
            self.pos.x -= self.speed

        self.check_if_in_boundaries()

    def add_rotate(self, degrees):
        self.rotation += degrees

    def shoot(self):
        rays = self.create_rays(num_rays=1, max_angle_view=1, distance=5000)
        for ray in rays:
            color = "yellow" if ray[1] == "object" else "green"
            pygame.draw.line(self.screen, color, ray[0][0], ray[0][1], 5)

    "<<<<FOR USERS END>>>>"
    """UTILITIES"""
    def create_rays(self, num_rays=5, max_angle_view=80, distance=None):
        # only works with odd numbers
        if distance is None:
            distance = self.distance_vision

        hit_distance = None
        rays = []
        for i in range(0, max_angle_view, max_angle_view//num_rays):
            # Reset hit_type for each ray
            hit_type = "none"

            # Middle point is 80/5 * (5-1)//2 --> max_angle_view/num_rays * (num_rays-1)//2
            # Calculate ray endpoint
            direction_vector = pygame.Vector2(0, -distance).rotate(i - max_angle_view/num_rays * (num_rays-1)//2).rotate(self.rotation)
            end_position = self.pos + direction_vector
            closest_end_position = end_position  # Store the closest intersection point

            # Check collision with each object
            for object in self.objects:
                point = find_hit_point_on_rectangle(self.pos, end_position, object.rect)
                if point is not None:
                    # Calculate distance to current intersection
                    current_distance = distance_between_points(self.pos, point)
                    # Calculate distance to current closest point
                    closest_distance = distance_between_points(self.pos, closest_end_position)

                    # Update closest point if this intersection is closer
                    if current_distance < closest_distance:
                        closest_end_position = point
                        hit_type = "object"
                        hit_distance = current_distance

            for player in self.players:
                point = find_hit_point_on_rectangle(self.pos, end_position, player.rect)
                if point is not None:
                    # Calculate distance to current intersection
                    current_distance = distance_between_points(self.pos, point)
                    # Calculate distance to current closest point
                    closest_distance = distance_between_points(self.pos, closest_end_position)

                    # Update closest point if this intersection is closer
                    if current_distance < closest_distance:
                        closest_end_position = point
                        hit_type = "player"
                        hit_distance = current_distance

            # Add the ray with its closest intersection point (or original endpoint if no intersection)
            rays.append([(self.pos, closest_end_position), hit_distance, hit_type])

        return rays

    """PYGAME"""
    def check_if_in_boundaries(self):
        if self.max_boundaries is not None:
            if self.pos.x < self.max_boundaries[0]:
                self.pos.x = self.max_boundaries[0]
            if self.pos.x > self.max_boundaries[2]:
                self.pos.x = self.max_boundaries[2]
            if self.pos.y < self.max_boundaries[1]:
                self.pos.y = self.max_boundaries[1]
            if self.pos.y > self.max_boundaries[3]:
                self.pos.y = self.max_boundaries[3]

    def draw(self, screen):
        # Draw character body
        pygame.draw.circle(screen, "red", self.pos, 40)

        # Draw direction indicator
        direction_vector = pygame.Vector2(0, -40).rotate(self.rotation)
        end_position = self.pos + direction_vector
        pygame.draw.line(screen, "blue", self.pos, end_position, 5)

        # Draw rays with different colors based on hit type
        rays = self.create_rays()
        for ray in rays:
            color = "yellow" if ray[1] == "object" else "green"
            pygame.draw.line(screen, color, ray[0][0], ray[0][1], 5)

    # For debugging purposes, add this method to the Character class
    def debug_draw(self, screen):
        # Draw character and rays normally
        self.draw(screen)

        # Draw rectangle corners and edges for debugging
        for obj in self.objects:
            rect = obj.rect
            # Draw corners
            corners = [
                (rect.left, rect.top),
                (rect.right, rect.top),
                (rect.right, rect.bottom),
                (rect.left, rect.bottom)
            ]
            for corner in corners:
                pygame.draw.circle(screen, "red", corner, 3)

            # Draw edges
            pygame.draw.rect(screen, "blue", rect, 1)  # Draw rect outline