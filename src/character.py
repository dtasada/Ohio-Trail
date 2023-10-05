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
    "Eggplants": 1,
    "Frikandelbroodje": 1,
    "Pickles": 1,
    "Stone baked garlic flat bread": 4,
    "Pineapple Pizza": 2,
    "Beef Jerky": 2,
    "Sour Patch Kids": 2,
    "CocoNutz": 1,
    "MrBeast Feastables": 1
}

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
            "eggplants": 3,
            "frikandelbroodje": 1,
            "pickles": 3,
            "stone baked garlic flat bread": 1,
        }

    def setup(self, name, background):
        self.name = name
        self.background = background
