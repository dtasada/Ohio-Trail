from settings import *

possible_background = [
    '1. Be a banker from New York',
    '2. Be a boss from Ohio',
    '3. Be a chef from France',
    '4. Be a farmer from Missouri',
    '5. Be a man from Florida',
]

possible_food = [
    'Eggplants',
    'Frikandelbroodje',
    'Pickles',
    'Stone baked garlic flat bread',
    'Pineapple Pizza',
    'Beef Jerky',
    'Sour Patch Kids'
    'CocoNutz',
]

clothing = {
    'Kilt': 10,
    'Skinny jeans': 10,
    'Among Us hoodie': 69,
    'Minecraft t-shirt': 20,
    '$19 Fortnite card': 20,
}

class Character():
    def __init__(self):
        self.name = None
        self.hp = 5
        self.food = {
            'eggplants': 3,
            'frikandelbroodje': 1,
            'pickles': 3,
            'stone baked garlic flat bread': 1,
        }

    def setup(self, name, background):
        self.name = name
        self.background = background
