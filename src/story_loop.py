from .widgets import *
import sys


"""
The storyline functions that drive the game forward.
"""


def slide_2():
    active_widgets.clear()
    active_widgets.append(RetroEntry(f"WAZAAAAAAAA", command=lambda: sys.exit(0)))
