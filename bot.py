

class MyBot():
    def __init__(self):
        self.name = "MyBot"

    # IMPLEMENT YOUR METHODS HERE

    # Modify but don't rename this method
    def act(self, info):
        # Receives info dictionary from the game (for the proper player)
        """
        info = {
            "location": self.get_location(),
            "rotation": self.get_rotation(),
            "rays": self.get_rays(),
            "current_ammo": self.current_ammo
        }
        """


        # Should return a dictionary of moves, for example:
        actions = {
            "forward": 0,
            "right": 0,
            "down": 0,
            "left": 0,
            "rotate": 0,
            "shoot": False
            }
        # Include even non used variables

        return actions