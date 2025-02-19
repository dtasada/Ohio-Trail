from .character import *
from .game import game
from .widgets import *
from enum import member
from functools import partial


def ask_background(name):
    player.name = name
    active_widgets.append(
        RetroEntry(
            f"And {name}, what may your background be?",
            pos=(0, 60),
            command=ask_bg_selection,
        )
    )


def ask_bg_selection():
    active_widgets.append(
        RetroSelection(
            actions=[i.desc for i in possible_backgrounds],
            pos=(0, 80),
            command=set_character_bg,
            images=[i.tex for i in possible_backgrounds],
            image_rects=[i.rect for i in possible_backgrounds],
        )
    )


def set_character_bg(bg):
    background = [i for i in possible_backgrounds if i.desc == bg][0]
    player.background = background.name
    speed = 0.7 if background.name == "man" else 0.4
    voiceline_entry = RetroEntry(
        background.catchphrase,
        pos=(150, 420),
        command=intro,
        accepts_input=False,
        wrap=game.window.size[0] - 300,
        speed=speed,
        typewriter=False,
    )
    active_widgets.append(voiceline_entry)
    for i in possible_backgrounds:
        if i.desc == bg:
            i.sound.play()


@pause1
def intro():
    active_widgets.clear()
    trip_type = {"banker": "business", "chef": "culinary"}.get(
        player.background, "pleasure"
    )
    text_intro = f"""Your name is {player.name}. You have boarded a plane headed

towards {random.choice(ohio_cities)}, Ohio.{ZWS * 20}

You are on a {trip_type} trip.{ZWS * 20}

With you on the plane are another 200 people."""

    anim_plane = Animation("intro-hook", (0, 100), 5, 0.35, should_stay=True)
    active_widgets.append(anim_plane)

    info_intro = RetroEntry(
        text_intro, command=intro_wreck, reverse_data=(12, "4 people.")
    )
    # info_intro must be last thing appended!
    active_widgets.append(info_intro)


@pause1
def intro_wreck():
    active_widgets.pop()
    text = f"""Oh no!{ZWS * 20} The plane has crashed!{ZWS * 20}

You are one of only 5 survivors.{ZWS * 20}

You and 4 NPCs are now stranded on an island.{ZWS *20}

Objective: survive for as long as possible.
"""
    active_widgets.append(RetroEntry(text, command=select_planewreck, delay=2000))


def select_planewreck():
    player.location = Location.PLANEWRECK
    active_widgets.clear()

    Action.update_last_action(select_planewreck)
    selection = [Action.EXPLORE_PLANEWRECK, Action.WALK_TO_FOREST, Action.TALK_TO_NPCS]
    if Completed.LOOTED_CORPSES not in player.completed:
        selection.insert(0, Action.LOOT_CORPSES)

    active_widgets.append(RetroEntry("You are at the planewreck.", selection=selection))


def info_loot_corpses():
    active_widgets.clear()

    if Completed.LOOTED_CORPSES in player.completed:
        active_widgets.append(
            RetroEntry(
                "You already found everything!",
                selection=[Action.OK],
            )
        )
    else:
        money_found = gauss(10, 3, 0)
        player.money += money_found

        goofy = random.choice(
            [
                "smackaroons",
                "doubloons",
                "clams",
                "bucks",
                "dollars",
                "george washingtons",
            ]
        )

        active_widgets.append(
            RetroEntry(
                f"You find {money_found} {goofy[:-1] if money_found == 1 else goofy}",
                selection=[Action.OK],
            )
        )

    player.complete(Completed.LOOTED_CORPSES)


def explore_planewreck():
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            f"""You look through the wreckage.{ZWS * 20}
There's really nothing left to find but some corpses.{ZWS * 20}
You should probably leave them alone.{ZWS * 20}

There's a forest in the distance.""",
            selection=[Action.OK],
            choice_pos=(0, 80),
        )
    )


def select_forest():
    player.location = Location.FOREST
    active_widgets.clear()

    Action.update_last_action(select_forest)
    selection = [Action.WALK_TO_PLANEWRECK]
    if Completed.EXPLORED_FOREST in player.completed:
        selection.append(Action.WALK_TO_LAKE)
        selection.append(Action.WALK_TO_MOUNTAIN)

        if Completed.SET_UP_CAMP in player.completed:
            selection.append(Action.WALK_TO_CAMP)
        else:
            selection.append(Action.SET_UP_CAMP)
    else:
        selection.append(Action.EXPLORE_FOREST)

    active_widgets.append(
        RetroEntry(
            "You are in the forest.",
            selection=selection,
        )
    )


def talk_to_npcs():
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You just talk to yourself.",
            selection=[Action.OK],
        )
    )


def explore_forest():
    # TODO
    active_widgets.clear()

    if Completed.EXPLORED_FOREST in player.completed:
        active_widgets.append(
            RetroEntry(
                "There's nothing left to explore.",
                selection=[Action.OK],
            )
        )
    else:
        active_widgets.append(
            RetroEntry(
                f"There appears to be a mountain in the distance... {ZWS * 20}\nOh, and also a lake. ",
                selection=[Action.OK],
            )
        )

        player.complete(Completed.EXPLORED_FOREST)


def select_lake():
    player.location = Location.LAKE
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You enjoy the quiet.",
            selection=[Action.OK],
        )
    )


def select_mountain():
    player.location = Location.MOUNTAIN
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You hear some eerie sounds coming from inside.",
            selection=[Action.OK],
        )
    )


def set_up_camp():
    # TODO
    active_widgets.clear()
    Action.update_last_action(select_camp)
    active_widgets.append(
        RetroEntry(
            "You and the NPCs have all set up a camp!",
            selection=[Action.OK],
        )
    )

    player.complete(Completed.SET_UP_CAMP)


def select_camp():
    player.location = Location.CAMP
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You are at the camp.",
            selection=[
                Action.WALK_TO_MY_TENT,
                Action.WALK_TO_CAMPFIRE,
                Action.WALK_TO_FOREST,
            ],
        )
    )


def select_my_tent():
    player.location = Location.MY_TENT
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You are at your tent.",
            selection=[Action.SLEEP, Action.LEAVE_TENT],
        )
    )


def select_campfire():
    # TODO
    player.location = Location.CAMPFIRE
    Action.update_last_action(select_campfire)
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You are sitting at the campfire.",
            selection=[Action.ENJOY_WARMTH, Action.COOK_FOOD, Action.LEAVE_CAMPFIRE],
        )
    )


def enjoy_warmth():
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            random.choice(["Ahhhh...", "Warm and toasty.", "Cozy.", "Mmmmm..."]),
            selection=[Action.OK],
        )
    )


def cook_food():
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            random.choice(["Jesse... we need to cook.", "Cooking time!", "Yum!"]),
            selection=[Action.OK],
        )
    )


def character_sleep():
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            random.choice(
                [
                    "You sleep soundly.",
                    "Zzzzz...",
                    "Goodnight.",
                    "*yawwwwn*",
                    "Sleepy time.",
                ]
            ),
            selection=[Action.OK],
        )
    )


class Action(Enum):
    COOK_FOOD = member(partial(cook_food))
    ENJOY_WARMTH = member(partial(enjoy_warmth))
    EXPLORE_FOREST = member(partial(explore_forest))
    EXPLORE_PLANEWRECK = member(partial(explore_planewreck))
    LEAVE_CAMPFIRE = member(partial(select_camp))
    LEAVE_TENT = member(partial(select_camp))
    LOOT_CORPSES = member(partial(info_loot_corpses))
    SET_UP_CAMP = member(partial(set_up_camp))
    SLEEP = member(partial(character_sleep))
    TALK_TO_NPCS = member(partial(talk_to_npcs))
    WALK_TO_CAMP = member(partial(select_camp))
    WALK_TO_CAMPFIRE = member(partial(select_campfire))
    WALK_TO_FOREST = member(partial(select_forest))
    WALK_TO_LAKE = member(partial(select_lake))
    WALK_TO_MOUNTAIN = member(partial(select_mountain))
    WALK_TO_MY_TENT = member(partial(select_my_tent))
    WALK_TO_PLANEWRECK = member(partial(select_planewreck))
    OK = member(lambda: Action.last_action())

    last_action: Callable = ask_background

    @classmethod
    def update_last_action(cls, action):
        cls.last_action = action
