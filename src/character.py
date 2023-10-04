from settings import *

class Character():
    def __init__(self):
        self.name = None
        self.hp = 5
        self.food = {
            'pickles': 3,
            'eggplants': 3,
            'frikandelbroodje': 1,
            'stone baked garlic flat bread': 1,
        }

    def setup(self, name):
        self.name = name
