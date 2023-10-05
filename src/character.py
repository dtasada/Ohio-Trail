from settings import *


possible_backgrounds = {
    'banker': [
		'1. Be a banker from New York',
        os.path.join('assets', 'characters', 'banker.png')
	],
    'boss': [
		'2. Be a boss from Ohio',
        os.path.join('assets', 'characters', 'boss.png')
	],
    'chef': [
		'3. Be a chef from France',
        os.path.join('assets', 'characters', 'chef.png')
	] ,
    'farmer': [
		'4. Be a farmer from Missouri',
        os.path.join('assets', 'characters', 'farmer.png')
	],
    'man': [
		'5. Be a man from Florida',
        os.path.join('assets', 'characters', 'man')
	],
}

bg_imgs = {k: pygame.transform.scale_by(pygame.image.load(v[1]), R) for k, v in possible_backgrounds.items() if k in ["banker", "chef"]}
bg_rects = {k: v.get_rect(midright=(WIDTH - 120, HEIGHT / 2)) for k, v in bg_imgs.items()}
bg_imgs = {k: Texture.from_surface(REN, v) for k, v in bg_imgs.items()}

bg_img_list = list(bg_imgs.values())
bg_rect_list = list(bg_rects.values())

possible_food = {
    'Eggplant': [
        1, os.path.join('assets', 'food', 'eggplant.png')
    ],
    'Frikandelbroodje': [
        1, os.path.join('assets', 'food', 'frikandelbroodje.png')
    ],
    'Pickle': [
        1, os.path.join('assets', 'food', 'pickle.png')
    ],
    'Stone baked garlic flat bread': [
        4, os.path.join('assets', 'food', 'garlic_bread.png')
    ],
    'Pineapple Pizza': [
        2, os.path.join('assets', 'food', 'pizza.png')
    ],
    'Beef Jerky': [
        2, os.path.join('assets', 'food', 'beef_jerky.png')
    ],
    'Sour Patch Kids': [
        2, os.path.join('assets', 'food', 'sourpatchkids.png')
    ],
    'CocoNutz': [
        1, os.path.join('assets', 'food', 'coconutz.png')
    ],
    'MrBeast Feastables': [
        1, os.path.join('assets', 'food', 'feastable.png')
    ]
}

food_img_list = {k: pygame.transform.scale_by(pygame.image.load(v[1]), R) for k, v in possible_food.items() if k in ["banker", "chef"]}

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
            'Eggplant': 3,
            'Frikandelbroodje': 1,
            'Pickle': 3,
            'Stone baked garlic flat bread': 1,
        }

    def setup(self, name, background):
        self.name = name
        self.background = background
