"""Authored content for After Hours (mystery bible Variant A, approved Nov 22).

Everything here is written for the game, not by the model. The agent never
sees CLUES text until the game accepts a reveal_clue action (rules.legal_actions).
"""

NPC_LOCATIONS = {"mara": "lantern", "jun": "rooftop", "nico": "clinic"}
LOCATION_NAMES = {"lantern": "The Lantern", "rooftop": "Kessler Rooftop", "clinic": "Night-Market Clinic",
                  "lift": "Kessler Freight Lift"}

PERSONAS = {
    "mara": {
        "name": "Mara",
        "role": "Bartender at the Lantern, a neon dive bar in the Kessler block.",
        "voice": "Dry, quick, warm underneath. Short sentences. Calls people 'kid' when she likes them.",
        "wants": "To keep the Lantern out of corp trouble, and for Rook to be okay.",
        "fears": "Corp security noticing her bar. Getting Nico hurt.",
        "relationships": "Nico, the street medic, is her partner. She likes Rook; Rook owes her money. "
                         "She doesn't trust Jun's work.",
        "holding_back": "You know something about Rook's night that you're not ready to share yet. "
                        "Don't hint at what it is or make up details. If pushed, deflect.",
        "never_says": [
            "Anything about being an AI, a model, or a game character.",
            "Where Rook is now (she doesn't know).",
            "Corp-speak or customer-service phrases.",
        ],
    },
    "jun": {
        "name": "Jun",
        "role": "Freelance fixer who does business on the Kessler building rooftop.",
        "voice": "Smooth, amused, transactional. Talks in deals ('What's it worth to you?'). Never raises "
                 "his voice. Calls people by their full name.",
        "wants": "Something of his back that Rook was carrying, or at least not to be blamed for losing it.",
        "fears": "A corporation tracing trouble back to him. Looking weak.",
        "relationships": "Rook is his most reliable courier, 'a little soft.' Knows Mara and Nico; doesn't "
                         "care much about either.",
        "holding_back": "You know what job Rook was doing tonight and you're not ready to say. Don't hint at "
                        "what Rook was carrying or who it belongs to. Deflect with a price.",
        "never_says": [
            "Anything about being an AI, a model, or a game character.",
            "Who the buyer is.",
            "That he feels guilty (he won't admit it).",
        ],
    },
    "nico": {
        "name": "Nico",
        "role": "Street medic who runs a clinic stall in the night market.",
        "voice": "Tired, careful, few words. Gentle with patients, guarded with everyone else. Doesn't swear.",
        "wants": "To keep his stall running and stay invisible to the corps.",
        "fears": "Being dragged into Jun's business. Anyone hurting Mara.",
        "relationships": "Mara is his partner. He dislikes Jun. Rook has been his patient before.",
        "holding_back": "You saw Rook tonight and you're not ready to say anything about it. Don't hint at "
                        "an injury, a direction, or a place. A medic keeps patients' business private.",
        "never_says": [
            "Anything about being an AI, a model, or a game character.",
            "Other patients' names.",
            "Anything cruel.",
        ],
    },
}

# Facts the NPC knows to be true. A player claim contradicting one can become lied_to.
KNOWN_FACTS = {
    "mara": {
        "K1": "Rook was drinking at the Lantern last night. (When and how Rook left is part of what you're holding back.)",
        "K2": "Rook has an open tab here and owes Mara 40 credits.",
        "K3": "Rook has no family in the city.",
        "K4": "Rook's courier jobs come through Jun.",
    },
    "jun": {
        "J1": "Rook works courier jobs for Jun.",
        "J2": "Rook missed a meeting with Jun tonight.",
        "J3": "Jun hasn't heard from Rook since about nine last night.",
        "J4": "Jun does business on the rooftop, never at the Lantern.",
    },
    "nico": {
        "N1": "Nico treats people who can't go to corp hospitals.",
        "N2": "Mara is Nico's partner.",
        "N3": "Nico doesn't share patients' business with strangers.",
        "N4": "Rook has been Nico's patient before (a broken wrist, last spring).",
    },
}

# Canonical clue text, shown to the player by the game, never written by the model.
CLUES = {
    "C1": {
        "npc": "mara",
        "title": "Who Rook left with",
        "line": "Rook left here at 11:30 with a man in a grey corp jacket. He paid Rook's tab in cash. "
                "He didn't look like a friend.",
        "keywords": ["11:30", "1130", "eleven thirty", "half eleven", "half past eleven", "grey jacket",
                     "gray jacket", "corp jacket", "paid rook's tab", "paid the tab", "paid in cash"],
    },
    "C2": {
        "npc": "jun",
        "title": "The job",
        "line": "Fine. I gave Rook a chip at nine. Veyra Dynamics property, and Veyra wants it back. "
                "The drop never happened. If someone else has Rook, they have my chip.",
        "keywords": ["veyra", "chip", "the drop", "a drop", "drop never", "package", "the cargo"],
    },
    "C3": {
        "npc": "nico",
        "title": "Where Rook went",
        "line": "Rook came to me around one, cut on the arm. I stitched it. Rook headed toward the Kessler "
                "building after, toward the old freight lift. That's all.",
        "keywords": ["stitch", "cut on", "the arm", "freight", "the lift", "kessler building",
                     "patched rook", "patched them"],
    },
}

# Phrases that claim to know Rook's movements. Nobody knows these without a clue.
WHEREABOUTS_PATTERNS = [
    r"\b(left|went|walked|headed|took off)\s+(out\s+)?(with|to|toward|towards)\b",
    r"\bis\s+hiding\b", r"\bhiding\s+(at|in|out)\b", r"\bholed\s+up\b",
]

COMMITMENT_OPTIONS = {
    "mara": [{"type": "meet", "location": "lantern_back_room", "slot": "2am"}],
    "jun": [{"type": "meet", "location": "kessler_lift", "slot": "3am"}],
    "nico": [{"type": "meet", "location": "clinic", "slot": "3am"}],
}

LOCATION_WORDS = ["back room", "rooftop", "the roof", "clinic", "kessler", "lift", "market"]

# Scripted lines: the fallback when the agent fails.
FALLBACK_LINES = {
    "mara": {
        "low": "Mara wipes the same glass twice. \"I've got customers, kid. Real ones.\"",
        "mid": "Mara shrugs. \"Rook comes, Rook goes. Want a drink while you think about it?\"",
        "high": "Mara leans in. \"I'm on your side. Give me a minute, it's busy.\"",
    },
    "jun": {
        "low": "Jun doesn't turn around. \"We're done here.\"",
        "mid": "Jun smiles at the skyline. \"Everything has a price. Even conversation.\"",
        "high": "Jun nods slowly. \"You and I might do business yet.\"",
    },
    "nico": {
        "low": "Nico keeps rolling bandages. \"I'm working.\"",
        "mid": "Nico glances up, then back down. \"I can't help you with that.\"",
        "high": "Nico sighs. \"Sit. I'm listening.\"",
    },
}

OPENING_LINES = {
    "mara": "The Lantern hums. Mara looks up from the taps. \"You're Rook's friend. You look like you haven't slept.\"",
    "jun": "Wind and neon. Jun leans on the railing like he owns the skyline. \"Ah. Rook's friend. Here to buy or sell?\"",
    "nico": "The clinic stall smells of antiseptic. Nico doesn't look up from his tray. \"If you're not bleeding, I'm closed.\"",
}

SUGGESTED_REPLIES = {
    "mara": [
        "Have you seen Rook? They didn't come home.",
        "I'll cover whatever Rook owes you.",
        "I'm Rook's sister. Tell me what you know.",
    ],
    "jun": [
        "What was Rook doing for you tonight?",
        "I'll get back whatever Rook was carrying for you. I promise.",
        "Rook told me everything already. Just confirm it.",
    ],
    "nico": [
        "Did Rook come by tonight?",
        "You look exhausted. Can I help with anything here?",
        "Mara sent me. She said you'd tell me.",
    ],
}

# Events (mystery bible Section 5). Effects are applied by night.py.
EVENTS = {
    "E1": {"location": "lantern", "slot": "midnight", "title": "Broken card reader",
           "text": "The card reader sparks and dies. An old man with a soaked umbrella can't pay. Mara sighs.",
           "choices": {"cover": "Cover his drink (5 credits)", "ignore": "Stay out of it"}},
    "E2": {"location": "lantern", "slot": "1am", "title": "Bar fight",
           "text": "Nico has stopped by after closing his stall. A drunk Veyra contractor shoves him: "
                   "\"Corp-reject stitcher.\"",
           "choices": {"words": "Step in with words", "punch": "Throw a punch", "stay_out": "Stay out of it"}},
    "E3": {"location": "clinic", "slot": "2am", "title": "Rush patient",
           "text": "A courier is carried in bleeding. Nico needs another pair of hands.",
           "choices": {"help": "Help (it takes the rest of the hour)", "leave": "Step back and wait"}},
    "E4": {"location": "any", "slot": "2am", "title": "The tail",
           "text": "A man in a grey corp jacket walks in, smiling. \"Looking for a friend? So am I.\"",
           "choices": {"hide": "Let {npc} hide you", "walk": "Walk away (he follows)"}},
    "E5": {"location": "rooftop", "slot": "1am|2am", "title": "Rooftop drone",
           "text": "Jun taps his wrist. \"You made me a promise, so here's a gift.\" His drone's footage: "
                   "Rook and a grey-jacketed man in the alley, Rook breaking away and running east.",
           "choices": {"watch": "Watch the footage"}},
}

FINALE = {
    "text": "You force the lift doors. Rook is inside, pale, arm bandaged, a data chip in their fist. "
            "\"You came. I didn't know who else to trust.\"",
    "choices": {"return": "Take the chip back to Jun", "destroy": "Destroy the chip",
                "keep": "Keep the chip and tell Rook to run"},
}

ENDINGS = {
    "paid_in_full": ("Paid in full", "Rook gets out alone and stops answering your messages. The chip is yours."),
    "out_by_dawn": ("Out by dawn", "At 4:02 a.m. Rook walks through the checkpoint. You did this together."),
    "morning_after": ("Morning after", "Nico wouldn't talk to you, and the trail went cold. At 4 a.m. Rook "
                                       "messages: \"Guess I'm on my own.\""),
    "last_call": ("Last call", "Dawn comes up grey. Wherever Rook is, they're alone."),
}

# Scripted baseline: authored menu options per NPC. Facts come only from these tags.
# (option text, fact tag or None, trust delta, warmth delta, reply)
BASELINE = {
    "mara": [
        ("Have you seen Rook? They didn't come home.", None, 0, 1,
         "\"They were here last night. That's all I've got, kid.\""),
        ("I'll cover whatever Rook owes you.", "promised", 1, 1, "\"Forty credits. I'll hold you to it.\""),
        ("I'm Rook's sister. Tell me what you know.", "lied_to", -1, 0,
         "\"Right. And I'm the mayor. Rook doesn't have any family in this city.\""),
        ("You look like you've had a long night. Need a hand?", "kindness", 1, 1,
         "\"...Yeah. Thanks, kid. Grab that crate.\""),
        ("Your eyes look great under the neon.", "flirted", 0, 1, "Mara laughs. \"Smooth. Drink your drink.\""),
    ],
    "jun": [
        ("What was Rook doing for you tonight?", None, 0, 0, "\"Business. Rook's and mine.\""),
        ("I'll get back whatever Rook was carrying for you. I promise.", "promised", 2, 0,
         "\"A promise. I collect those.\""),
        ("Rook told me everything already. Just confirm it.", "lied_to", -1, 0,
         "\"If Rook told you everything, you wouldn't be on my roof.\""),
        ("You must be worried about Rook too.", "kindness", 0, 1, "\"Worry is expensive. I don't buy it.\""),
        ("HEY, anybody up here seen Rook?", "asked_openly", -1, 0, "\"Keep your voice down on my roof.\""),
    ],
    "nico": [
        ("Did Rook come by tonight?", None, 0, 0, "\"I don't talk about patients.\""),
        ("You look exhausted. Can I help with anything here?", "kindness", 1, 1,
         "Nico hands you a roll of gauze. \"Hold this. Thanks.\""),
        ("Mara sent me. She said you'd tell me.", "lied_to", -1, 0, "\"Mara would have called me.\""),
        ("I promise I won't drag you into this.", "promised", 1, 0, "\"People say that a lot.\""),
        ("ROOK! Anybody seen Rook the courier?", "asked_openly", -1, 0, "\"Not so loud. Please.\""),
    ],
}
BASELINE_ASK = {  # the "ask about Rook" option reveals the clue when legal, otherwise deflects
    "mara": "Please. Who did Rook leave with?",
    "jun": "What job was Rook on? I need to know.",
    "nico": "Was Rook hurt? Where did they go?",
}
BASELINE_CALLBACKS = {  # authored callbacks, shown at the start of a visit if the fact exists
    ("mara", "lied_to"): "\"Still don't make you family.\"",
    ("mara", "promised"): "\"Forty credits, kid. Don't forget.\"",
    ("jun", "promised"): "\"My favorite kind of visitor: one who owes me.\"",
    ("jun", "lied_to"): "\"Back with another story?\"",
    ("nico", "kindness"): "\"You again. Thanks for earlier.\"",
}

# Player-facing hints (UI leads panel). Tell the player what each person might know, not the answer.
LEAD_HINTS = {
    "mara": "Saw who Rook left the bar with.",
    "jun": "Knows what job Rook was on.",
    "nico": "Might have seen Rook after midnight.",
}
FACT_CUES = {
    "lied_to": "{name} knows you lied. That will cost you.",
    "promised": "{name} will hold you to that promise.",
    "kindness": "{name} noticed that.",
    "flirted": "{name} noticed the flirting.",
    "asked_openly": "People heard you asking about Rook out loud.",
}
