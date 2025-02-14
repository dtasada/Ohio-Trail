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

towards Cleveland, Ohio.{ZWS * 20}

You are on a {trip_type} trip.{ZWS * 20}

With you on the plane are another 200 people."""

    # plane crashing animation and
    anim_plane = Animation("intro-hook", (0, 100), 5, 0.35, should_stay=True)
    active_widgets.append(anim_plane)
    #
    info_intro = RetroEntry(
        text_intro, (0, 0), intro_crash, reverse_data=(12, "4 people.")
    )
    # info_intro must be last thing appended!
    active_widgets.append(info_intro)


@pause1
def intro_crash():
    active_widgets.pop()
    text_intro_crash = f"""Oh no!{ZWS * 20} The plane has crashed!{ZWS * 20}

You are one of only 5 survivors.{ZWS * 20}

You and 4 NPCs are now stranded on an island.{ZWS *20}

Objective: survive for as long as possible.
"""
    info_intro_crash = RetroEntry(text_intro_crash, (0, 0), select_planewreck)
    active_widgets.append(info_intro_crash)


def select_planewreck():
    active_widgets.clear()

    crash_opts = RetroSelection(
        [Action.LOOT_CORPSES, Action.EXPLORE_PLANEWRECK, Action.GO_TO_FOREST], (0, 60)
    )

    crash_info = RetroEntry(
        "You are now at the planewreck", (0, 0), selection=crash_opts
    )
    active_widgets.append(crash_info)


def info_loot_corpses():
    print("you found moneh")


def info_explore_planewreck():
    print("you found bodies")


def info_go_to_forest():
    print("you went fshing in the forest")


class Action(Enum):
    LOOT_CORPSES = member(partial(info_loot_corpses))
    EXPLORE_PLANEWRECK = member(partial(info_explore_planewreck))
    GO_TO_FOREST = member(partial(info_go_to_forest))
