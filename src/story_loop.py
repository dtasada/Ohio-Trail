from .character import *
from .game import game
from .widgets import *
from enum import member
from functools import partial


def ask_background(name):
    player.name = name
    ent_bg = RetroEntry(
        f"And {name}, what may your background be?", (0, 60), ask_bg_selection
    )
    active_widgets.append(ent_bg)


def ask_bg_selection():
    bg_list = [i.desc for i in possible_backgrounds]
    sel_bg = RetroSelection(
        bg_list,
        (0, 80),
        set_character_bg,
        [i.tex for i in possible_backgrounds],
        [i.rect for i in possible_backgrounds],
    )
    active_widgets.append(sel_bg)


def set_character_bg(bg):
    background = [i for i in possible_backgrounds if i.desc == bg][0]
    player.background = background.name
    speed = 0.7 if background.name == "man" else 0.4
    voiceline_entry = RetroEntry(
        background.catchphrase,
        (150, 420),
        intro,
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
        text_intro, (0, 0), intro_wreck, reverse_data=(12, "4 people.")
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
    active_widgets.append(RetroEntry(text, (0, 0), select_planewreck, delay=2000))


def select_planewreck():
    player.location = Location.PLANEWRECK
    active_widgets.clear()

    Action.update_last_action(select_planewreck)
    active_widgets.append(
        RetroEntry(
            "You are at the planewreck.",
            (0, 0),
            selection=RetroSelection(
                [
                    Action.LOOT_CORPSES,
                    Action.EXPLORE_PLANEWRECK,
                    Action.WALK_TO_FOREST,
                    Action.TALK_TO_NPCS,
                ],
                (0, 60),
            ),
        )
    )


def info_loot_corpses():
    active_widgets.clear()

    if Completed.LOOTED_CORPSES in player.completed:
        active_widgets.append(
            RetroEntry(
                "You already found everything!",
                (0, 0),
                selection=RetroSelection([Action.OK], (0, 30)),
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
                (0, 0),
                selection=RetroSelection([Action.OK], (0, 30)),
            )
        )

    player.complete(Completed.LOOTED_CORPSES)


def explore_planewreck():
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You gaze into the distance...",
            (0, 0),
            selection=RetroSelection([Action.OK], (0, 30)),
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
            (0, 0),
            selection=RetroSelection(selection, (0, 30)),
        )
    )


def talk_to_npcs():
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You just talk to yourself.",
            (0, 0),
            selection=RetroSelection([Action.OK], (0, 30)),
        )
    )


def explore_forest():
    # TODO
    active_widgets.clear()

    if Completed.EXPLORED_FOREST in player.completed:
        active_widgets.append(
            RetroEntry(
                "There's nothing left to explore.",
                (0, 0),
                selection=RetroSelection([Action.OK], (0, 30)),
            )
        )
    else:
        active_widgets.append(
            RetroEntry(
                f"There appears to be a mountain in the distance... {ZWS * 20} Oh, and also a lake.",
                (0, 0),
                selection=RetroSelection([Action.OK], (0, 30)),
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
            (0, 0),
            selection=RetroSelection([Action.OK], (0, 30)),
        )
    )


def select_mountain():
    player.location = Location.MOUNTAIN
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You hear some eerie sounds coming from inside.",
            (0, 0),
            selection=RetroSelection([Action.OK], (0, 30)),
        )
    )


def set_up_camp():
    # TODO
    active_widgets.clear()
    Action.update_last_action(select_camp)
    active_widgets.append(
        RetroEntry(
            "You and the NPCs have all set up a camp!",
            (0, 0),
            selection=RetroSelection([Action.OK], (0, 30)),
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
            (0, 0),
            selection=RetroSelection(
                [
                    Action.WALK_TO_MY_TENT,
                    Action.WALK_TO_CAMPFIRE,
                    Action.WALK_TO_FOREST,
                ],
                (0, 30),
            ),
        )
    )


def select_my_tent():
    player.location = Location.MY_TENT
    # TODO
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            "You are at your tent.",
            (0, 0),
            selection=RetroSelection([Action.OK], (0, 30)),
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
            (0, 0),
            selection=RetroSelection(
                [Action.ENJOY_WARMTH, Action.COOK_FOOD, Action.LEAVE_CAMPFIRE], (0, 30)
            ),
        )
    )


def enjoy_warmth():
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            random.choice(["Ahhhh...", "Warm and toasty.", "Cozy.", "Mmmmm..."]),
            (0, 0),
            selection=RetroSelection([Action.OK], (0, 30)),
        )
    )


def cook_food():
    active_widgets.clear()
    active_widgets.append(
        RetroEntry(
            random.choice(["Jesse... we need to cook.", "Cooking time!", "Yum!"]),
            (0, 0),
            selection=RetroSelection([Action.OK], (0, 30)),
        )
    )


class Action(Enum):
    COOK_FOOD = member(partial(cook_food))
    ENJOY_WARMTH = member(partial(enjoy_warmth))
    EXPLORE_FOREST = member(partial(explore_forest))
    EXPLORE_PLANEWRECK = member(partial(explore_planewreck))
    LEAVE_CAMPFIRE = member(partial(select_camp))
    LOOT_CORPSES = member(partial(info_loot_corpses))
    SET_UP_CAMP = member(partial(set_up_camp))
    SLEEP = member(partial(select_camp))
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
