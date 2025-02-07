import time
import pygame
from utils import find_hit_point_on_rectangle, distance_between_points


class Character:
    def __init__(self, starting_pos, screen, speed=5, boundaries=None, objects=None):
        self.rotation = 0
        self.max_boundaries = boundaries
        self.objects = objects if objects is not None else []
        self.rect = pygame.Rect(starting_pos, (40, 40))


        """CHARACTER STATS"""
        self.username = "player {}".format(id(self)) # add way to personalize
        self.collision_w_objects = True # turn off if you want to move through objects
        self.health = 100
        self.speed = speed
        self.distance_vision = 200
        self.damage = 20
        self.delay = 0.3 #(between shoots), a lot of time so it is longer but more intense
        self.max_ammo = 30
        self.current_ammo = self.max_ammo
        self.time_to_reload = 3
        self.alive = True

        """TIMERS"""
        self.start_reloading_time = None
        self.last_shoot_time = None

        self.screen = screen
        self.players = []

    "<<<<FOR USERS START>>>>"
    """GETTERS"""
    def get_location(self):
        # returns the position of the character in (x, y) format
        return self.get_center()

    def get_rotation(self):
        # returns the rotation of the character in degrees
        return self.rotation

    def get_rays(self):
        # returns a list of rays, each represented by a tuple of the form ((start_x, start_y), (end_x, end_y), distance, hit_type)
        # distance is None if no intersection, hit_type is "object" or "player" if intersection
        # to get the values:
        """
        for ray in character.get_rays():
            vector = ray[0]
            distance = ray[1]
            hit_type = ray[2]
        """
        return self.create_rays()

    """SETTERS"""
    def move_in_direction(self, direction):  # forward, right, down, left
        # This only moves the character if there is no collision with any object, improve it to be more cool
        original_pos = self.rect.topleft

        if direction == "forward":
            self.rect.y -= self.speed
        elif direction == "right":
            self.rect.x += self.speed
        elif direction == "down":
            self.rect.y += self.speed
        elif direction == "left":
            self.rect.x -= self.speed

        if self.collision_w_objects:
            # Check for collisions with objects
            for obj in self.objects:
                if self.rect.colliderect(obj.rect):                    # If collision occurred, revert to original position
                    self.rect.topleft = original_pos
                    return

        self.check_if_in_boundaries()

    def add_rotate(self, degrees):
        self.rotation += degrees

    def shoot(self):
        if self.current_ammo > 0:
            if self.last_shoot_time is not None and time.time() - self.last_shoot_time < self.delay:
                print("still on delay")
                return False

            rays = self.create_rays(num_rays=1, max_angle_view=1, distance=5000, damage=self.damage)
            for ray in rays:
                if ray[2] == "player":
                    print("hit player, did damage", self.damage)
                    color = "red"
                elif ray[2] == "object":
                    color = "yellow"
                else:
                    color = "gray"

                pygame.draw.line(self.screen, color, ray[0][0], ray[0][1], 5)
            self.last_shoot_time = time.time()

            self.current_ammo -= 1
            if self.current_ammo <= 0 and self.start_reloading_time is None:
                self.reload()
            else:
                print("is reloading (technically)")

        else:
            print("no ammo")

    "<<<<FOR USERS END>>>>"
    """UTILITIES"""
    def get_center(self):
        return self.rect.center

    def create_rays(self, num_rays=5, max_angle_view=80, distance=None, damage=0):
        # only works with odd numbers !!!!
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
            end_position = self.get_center() + direction_vector
            closest_end_position = end_position  # Store the closest intersection point

            # Check collision with each object
            for object in self.objects:
                point = find_hit_point_on_rectangle(self.get_center(), end_position, object.rect)
                if point is not None:
                    # Calculate distance to current intersection
                    current_distance = distance_between_points(self.get_center(), point)
                    # Calculate distance to current closest point
                    closest_distance = distance_between_points(self.get_center(), closest_end_position)

                    # Update closest point if this intersection is closer
                    if current_distance < closest_distance:
                        closest_end_position = point
                        hit_type = "object"
                        hit_distance = current_distance

            for player in self.players:
                point = find_hit_point_on_rectangle(self.get_center(), end_position, player.rect)
                if point is not None:
                    player.do_damage(damage, self)

                    # Calculate distance to current intersection
                    current_distance = distance_between_points(self.get_center(), point)
                    # Calculate distance to current closest point
                    closest_distance = distance_between_points(self.get_center(), closest_end_position)

                    # Update closest point if this intersection is closer
                    if current_distance < closest_distance:
                        closest_end_position = point
                        hit_type = "player"
                        hit_distance = current_distance

            # Add the ray with its closest intersection point (or original endpoint if no intersection)
            rays.append([(self.get_center(), closest_end_position), hit_distance, hit_type])

        return rays

    def reload(self):
        if self.start_reloading_time is None:
            self.start_reloading_time = time.time()
        else:
            if time.time() - self.start_reloading_time >= self.time_to_reload:
                self.current_ammo = self.max_ammo
                self.start_reloading_time = None

    """PYGAME"""
    def do_damage(self, damage, by_player=None):
        self.health -= damage
        if self.health <= 0:
            if self.alive:
                self.alive = False
                self.rect.x = -1000
                self.rect.y = -1000
                self.current_ammo = 0
                print("player died, killer was:", by_player.username)
            else:
                print("player is already dead (IGNORE THIS)")
        else:
            print("player took damage, current health:", self.health)

    def check_if_in_boundaries(self):
        if self.max_boundaries is not None:
            if self.rect.center[0] < self.max_boundaries[0]:
                self.rect.center = (self.max_boundaries[0], self.rect.center[1])
            if self.rect.center[0] > self.max_boundaries[2]:
                self.rect.center = (self.max_boundaries[2], self.rect.center[1])
            if self.rect.center[1] < self.max_boundaries[1]:
                self.rect.center = (self.rect.center[0], self.max_boundaries[1])
            if self.rect.center[1] > self.max_boundaries[3]:
                self.rect.center = (self.rect.center[0], self.max_boundaries[3])

    def draw(self, screen):
        # draws character body
        pygame.draw.rect(screen, "red", self.rect)

        # draws direction indicator
        direction_vector = pygame.Vector2(0, -40).rotate(self.rotation)
        end_position = self.get_center() + direction_vector
        pygame.draw.line(screen, "blue", self.get_center(), end_position, 5)

        # draws rays with different colors based on hit type
        rays = self.create_rays()
        for ray in rays:
            color = "yellow" if ray[1] == "object" else "green"
            pygame.draw.line(screen, color, ray[0][0], ray[0][1], 5)