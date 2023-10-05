from settings import *


possible_backgrounds = {
    "banker": {
		"desc": "1. Be a banker from New York",
	},
    # "boss": {
	# 	"desc": "2. Be a boss from Ohio",
	# },
    "chef": {
		"desc": "3. Be a chef from France",
	},
    # "farmer": {
	# 	"desc": "4. Be a farmer from Missouri",
	# },
    # "man": {
	# 	"desc": "5. Be a man from Florida",
	# },
}

for bg_name in possible_backgrounds:
    img = pygame.transform.scale_by(pygame.image.load(os.path.join("assets", "characters", f"{bg_name}.png")), R)
    tex = Texture.from_surface(REN, img)
    rect = img.get_rect(midright=(WIDTH - 120, HEIGHT / 2))
    possible_backgrounds[bg_name]["img"] = img
    possible_backgrounds[bg_name]["tex"] = tex
    possible_backgrounds[bg_name]["rect"] = rect

bg_imgs = [v["tex"] for v in possible_backgrounds.values()]
bg_rects = [v["rect"] for v in possible_backgrounds.values()]

possible_food = {
<<<<<<< HEAD
    "Eggplants": 1,
    "Frikandelbroodje": 1,
    "Pickles": 1,
    "Stone baked garlic flat bread": 4,
    "Pineapple Pizza": 2,
    "Beef Jerky": 2,
    "Sour Patch Kids": 2,
    "CocoNutz": 1,
    "MrBeast Feastables": 1
=======
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
>>>>>>> db660e85218a1e2c7b6d36debd495c04cbbfc59a
}

food_img_list = {k: pygame.transform.scale_by(pygame.image.load(v[1]), R) for k, v in possible_food.items() if k in ["banker", "chef"]}

clothing = {
    "Kilt": 10,
    "Skinny jeans": 10,
    "Among Us hoodie": 69,
    "Minecraft t-shirt": 20,
    "$19 Fortnite card": 20,
}


class Character():
    def __init__(self):
        self.name = None
        self.hp = 5
        self.money = 25
        self.food = {
<<<<<<< HEAD
            "eggplants": 3,
            "frikandelbroodje": 1,
            "pickles": 3,
            "stone baked garlic flat bread": 1,
=======
            'Eggplant': 3,
            'Frikandelbroodje': 1,
            'Pickle': 3,
            'Stone baked garlic flat bread': 1,
>>>>>>> db660e85218a1e2c7b6d36debd495c04cbbfc59a
        }

    def setup(self, name, background):
        self.name = name
        self.background = background
