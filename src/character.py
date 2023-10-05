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
