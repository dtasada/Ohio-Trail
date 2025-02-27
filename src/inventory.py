from .story_loop import *
from .game import *
from .settings import *
from .widgets import *

from typing import List, Optional


class InventoryItem:
    def __init__(self, img_dir, name, value: Optional[int] = None) -> None:
        self.name: str = name
        self.value: Optional[int] = value
        self.img: pygame.Surface = pygame.transform.scale_by(
            pygame.image.load(
                Path("assets", img_dir, f"{name.lower().replace(' ', '-')}.png")
            ),
            SCALING,
        )
        self.tex: Texture = Texture.from_surface(game.renderer, self.img)
        self.rect: pygame.Rect = self.img.get_rect()

    def select(self) -> None: ...


class Food(InventoryItem):
    @classmethod
    def setup(cls):
        cls.EGGPLANT = cls("food", "Eggplant", 1)
        cls.FRIKANDELBROODJE = cls("food", "Frikandelbroodje", 1)
        cls.PICKLE = cls("food", "Pickle", 1)
        cls.STONE_BAKED_GARLIC_FLATBREAD = cls(
            "food", "Stone baked garlic flatbread", 4
        )
        cls.SOUR_PATCH_KIDS = cls("food", "Sour Patch Kids", 2)
        cls.MRBEAST_FEASTABLES = cls("food", "MrBeast Feastables", 5)
        cls.PINK_SAUCE = cls("food", "Pink Sauce", 1)

    def select(self) -> None:
        active_widgets.clear()
        active_widgets.append(
            RetroEntry(
                random.choice(["Nom nom nom...", "mmmmmgh...", "*chomp chomp*"]),
                selection=[Action.OK],
            )
        )


Food.setup()


class Inventory:
    def __init__(self) -> None:
        self.items: List[InventoryItem] = [
            Food.PICKLE,
            Food.FRIKANDELBROODJE,
            Food.EGGPLANT,
            Food.STONE_BAKED_GARLIC_FLATBREAD,
            Food.SOUR_PATCH_KIDS,
            Food.PINK_SAUCE,
            InventoryItem("items", "doubloons", 50),
        ]
        self.index = 0
        self.should_draw = True

    def update(self) -> None:
        if not self.should_draw:
            return

        cell_size = 64
        cell_count = 8
        grid_border_size = 3

        top_left = (
            game.window.size[0] / 2 - cell_size * cell_count / 2,
            game.window.size[1] - cell_size * 1.5,
        )
        top_right = (top_left[0] + cell_count * cell_size, top_left[1])
        bottom_left = [top_left[0], top_left[1] + cell_size]

        grid_size = [cell_size * cell_count, cell_size]

        fill_rect(
            game.renderer,
            Color.WHITE,
            pygame.Rect(
                (top_left[0] - grid_border_size, top_left[1]),
                (grid_border_size, grid_size[1]),
            ),
        )
        fill_rect(
            game.renderer,
            Color.WHITE,
            pygame.Rect(top_right, (grid_border_size, grid_size[1])),
        )
        fill_rect(
            game.renderer,
            Color.WHITE,
            pygame.Rect(
                (top_left[0], top_left[1] - grid_border_size),
                (grid_size[0], grid_border_size),
            ),
        )
        fill_rect(
            game.renderer,
            Color.WHITE,
            pygame.Rect(bottom_left, (grid_size[0], grid_border_size)),
        )

        for i in range(cell_count + 1):
            fill_rect(
                game.renderer,
                Color.WHITE,
                pygame.Rect(
                    (top_left[0] + i * cell_size, top_left[1]),
                    (2, cell_size),
                ),
            )

        for i, item in enumerate(self.items):
            game.renderer.blit(
                item.tex,
                pygame.Rect(top_left[0] + i * cell_size, top_left[1], 64, 64),
            )

        game.renderer.blit(
            *write(
                "^",
                (
                    bottom_left[0] + self.index * cell_size + cell_size / 2,
                    bottom_left[1] + 24,
                ),
                size=28,
                anchor="center",
            )
        )

        desc_tex, desc_rect = write(
            enum_to_str(self.items[self.index].name),
            (
                top_left[0] + grid_size[0] / 2,
                top_left[1] - 8,
            ),
            anchor="midbottom",
        )
        game.renderer.blit(desc_tex, desc_rect)

    def process_event(self, event) -> None:
        if not self.should_draw:
            return

        """if event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_LEFT:
                    Sound.BEEP.play()
                    self.index = (
                        self.index - 1 if self.index > 0 else len(self.items) - 1
                    )
                case pygame.K_RIGHT:
                    Sound.BEEP.play()
                    self.index = (
                        self.index + 1 if self.index < len(self.items) - 1 else 0
                    )
                case pygame.K_RETURN:
                    self.items[self.index].select()"""


inventory: Inventory = Inventory()
