dialogue = {
    "The Sailor": {
        0: {
            "text": "You're awake. Took a hell of a knock, didn't ya.",
            "responses": [
                "What the hell happened?",
                "Where are we?",
                "Is everyone alright?",
                "Goodbye",
            ],
        },
        1: {
            "text": "Plane crashed, kid.\nYou were knocked out cold, but you're lucky to be breathin'.",
            "checkpoint": 0,
        },
        2: {
            "text": "We're on some godforsaken island...\ndon't know where, though.",
            "checkpoint": 0,
        },
        3: {
            "text": "Look around, kid.\nYou think everyone's alright?\nYou're lucky to be alive, lots of folks didn't make it.",
            "checkpoint": 0,
        },
        4: {
            "text": "See you around, kid.",
            "checkpoint": "exit",
        },
        5: {
            "text": "They say there's something here…\nsomething that moves in the shadows.\nYe never see it, not clearly, anyway, but ye feel it.\nYou hear it, at night,\nwhen the wind's still and the island's quiet.\nA rustling, a whispering in the trees,\nlike the earth itself is breathin'.",
            "responses": ["Ok..."],
        },
        6: {
            "text": "Mark my words,\nye'll feel it long before ye ever see it.\nAnd if it wants ye… well, there's no escaping it",
            "checkpoint": "exit",
        },
    },
    "exit": None,
}


class Dialogue:
    """
    Dialogue class for communication with npc's
    self.id is used to keep track of what dialogue to use
    """

    def __init__(self):
        self.cur = None
        self.id = 0
        self.checkpoint = 0


dia = Dialogue()
