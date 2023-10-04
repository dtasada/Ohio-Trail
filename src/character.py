from settings import *


possible_backgrounds = {
    'banker': [
		'1. Be a banker from New York',
        path('assets', 'banker.png')
	],
    'boss': [
		'2. Be a boss from Ohio',
        path('assets', 'boss.png')
	],
    'chef': [
		'3. Be a chef from France',
        path('assets', 'chef.png')
	] ,
    'farmer': [
		'4. Be a farmer from Missouri',
        path('assets', 'farmer.png')
	],
    'man': [
		'5. Be a man from Florida',
        path('assets', 'man')
	],
}

possible_food = {
    'Eggplants': 1,
    'Frikandelbroodje': 1,
    'Pickles': 1,
    'Stone baked garlic flat bread': 4,
    'Pineapple Pizza': 2,
    'Beef Jerky': 2,
    'Sour Patch Kids': 2,
    'CocoNutz': 1,
    'MrBeast Feastables': 1
}

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
        self.money = 25
        self.food = {
            'eggplants': 3,
            'frikandelbroodje': 1,
            'pickles': 3,
            'stone baked garlic flat bread': 1,
        }

    def setup(self, name, background):
        self.name = name
        self.background = background
