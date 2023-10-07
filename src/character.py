from .settings import *


possible_backgrounds = {
    "banker": {
		"desc": "Be a banker from New York",
        "catchphrase": f"Impressive,{ZWS * 10} very nice.",
	},

    # "boss": {
	# 	"desc": "2. Be a boss from Ohio",
	# },

    "chef": {
		"desc": "Be a chef from France",
        "catchphrase": "Anyone can cook."
	},

    "man": {
		"desc": "Be a man from Florida",
         "catchphrase": f"{ZWS * 5}W{'o' * 29}!{ZWS * 7} Yeah{ZWS * 10} baby!{ZWS * 10} That's what I've been waiting for, that's what it's all about! Woo!"
	},
}
for index, bg_name in enumerate(possible_backgrounds):
    img = pygame.transform.scale_by(pygame.image.load(os.path.join("assets", "characters", f"{bg_name}.png")), R)
    tex = Texture.from_surface(REN, img)
    rect = img.get_rect(center=(WIDTH - 220, HEIGHT / 2))
    possible_backgrounds[bg_name]["img"] = img
    possible_backgrounds[bg_name]["tex"] = tex
    possible_backgrounds[bg_name]["rect"] = rect
    possible_backgrounds[bg_name]["desc"] = f"{index + 1}. {possible_backgrounds[bg_name]['desc']}"
    if bg_name in ("banker", "chef", "man"):
        try:
            sound = pygame.mixer.Sound(os.path.join("assets", "sfx", f"{bg_name}.wav"))
        except FileNotFoundError:
            sound = pygame.mixer.Sound(os.path.join("assets", "sfx", f"{bg_name}.mp3"))
        possible_backgrounds[bg_name]["sound"] = sound
bg_imgs = [v["tex"] for v in possible_backgrounds.values()]
bg_rects = [v["rect"] for v in possible_backgrounds.values()]

possible_foods = {
    "Eggplant": {
        "price": 1
    },

    "Frikandelbroodje": {
        "price": 1,
    },

    "Pickle": {
        "price": 1,
    },

    "Stone baked garlic flat bread": {
        "price": 4,
    },

    # "Pineapple Pizza": {
    #     "price": 2,
    # },
    # "Beef Jerky": {
    #     "price": 2,
    # },
    "Sour Patch Kids": {
        "price": 2,
    },

    # "CocoNutz": {
    #     "price": 1,
    # },
    "MrBeast Feastables": {
        "price": 5,
    },

    "Pink-Sauce": {
        "price": 1,
    },
}
for bg_name in possible_foods:
    img = pygame.transform.scale_by(pygame.image.load(os.path.join("assets", "food", f"{bg_name.lower().replace(' ', '-')}.png")), R)
    tex = Texture.from_surface(REN, img)
    rect = img.get_rect(center=(WIDTH - 300, HEIGHT / 2))
    possible_foods[bg_name]["img"] = img
    possible_foods[bg_name]["tex"] = tex
    possible_foods[bg_name]["rect"] = rect
food_imgs = [v["tex"] for v in possible_foods.values()]
food_rects = [v["rect"] for v in possible_foods.values()]

clothing = {
    "Kilt": 10,
    "Skinny jeans": 10,
    "Among Us hoodie": 69,
    "Minecraft t-shirt": 20,
    "$19 Fortnite card": 20,
}


class Character:
    def __init__(self):
        self.name = None
        self.hp = 5
        self.money = 25
        self.show_money = False
        self.food = {
            "Eggplant": 3,
            "Frikandelbroodje": 1,
            "Pickle": 3,
            "Stone baked garlic flat bread": 1,
        }

    def update(self):
        if self.show_money:
            tex, rect = writ(f"${self.money}", (40, 350), 30)
            REN.blit(tex, rect)

    def setup(self, name, background):
        self.name = name
        self.background = background
