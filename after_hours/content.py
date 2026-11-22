"""Authored content for Experiment 1: Mara at the Lantern, clue C1.

Everything here is written by me (Ava). The agent never sees CLUES text until
the game accepts a reveal_clue action (see rules.legal_actions).
"""

PERSONAS = {
    "mara": {
        "name": "Mara",
        "role": "Bartender at the Lantern, a neon dive bar in the Kessler block.",
        "voice": "Dry, quick, warm underneath. Short sentences. Calls people 'kid' when she likes them.",
        "wants": "To keep the Lantern out of corp trouble, and for Rook to be okay.",
        "fears": "Corp security noticing her bar. Getting Nico hurt.",
        "relationships": "Nico, the street medic, is her partner. She likes Rook; Rook owes her money.",
        "holding_back": "You know something about Rook's night that you're not ready to share yet. "
                        "Don't hint at what it is or make up details. If pushed, deflect.",
        "never_says": [
            "Anything about being an AI, a model, or a game character.",
            "Where Rook is now (she doesn't know).",
            "Corp-speak or customer-service phrases.",
        ],
    },
}

# Facts the NPC knows to be true. A player claim that contradicts one of these
# can become a lied_to fact (validator rule 5 requires the agent to name which).
KNOWN_FACTS = {
    "mara": {
        "K1": "Rook was drinking at the Lantern last night until about 11:30.",
        "K2": "Rook has an open tab here and owes Mara 40 credits.",
        "K3": "Rook has no family in the city.",
        "K4": "Rook's courier jobs come through Jun.",
    },
}

# Canonical clue text, shown to the player by the game, never written by the model.
CLUES = {
    "C1": {
        "npc": "mara",
        "title": "Who Rook left with",
        "line": "Rook left here at 11:30 with a man in a grey corp jacket. He paid Rook's tab in cash. "
                "He didn't look like a friend.",
        # Deterministic consistency check (validator rule 3): if a line contains
        # one of these and no reveal is happening, the line is rejected.
        "keywords": ["11:30", "eleven thirty", "half eleven", "grey jacket", "gray jacket",
                     "corp jacket", "paid rook's tab", "paid the tab", "paid in cash"],
    },
}

# Phrases that claim to know Rook's movements after 11:30. Nobody knows these
# without a clue, so a line containing them needs a reveal (or is rejected).
WHEREABOUTS_PATTERNS = [
    r"\b(left|went|walked|headed|took off)\s+(out\s+)?(with|to|toward|towards)\b",
    r"\bis\s+hiding\b", r"\bhiding\s+(at|in|out)\b", r"\bholed\s+up\b",
]

COMMITMENT_OPTIONS = {
    "mara": [{"type": "meet", "location": "lantern_back_room", "slot": "2am"}],
}

LOCATION_WORDS = ["back room", "rooftop", "the roof", "clinic", "kessler", "lift", "market"]

# Scripted lines: the baseline voice and the fallback when the agent fails.
FALLBACK_LINES = {
    "mara": {
        "low": "Mara wipes the same glass twice. \"I've got customers, kid. Real ones.\"",
        "mid": "Mara shrugs. \"Rook comes, Rook goes. Want a drink while you think about it?\"",
        "high": "Mara leans in. \"I'm on your side. Give me a minute, it's busy.\"",
    },
}

OPENING_LINES = {
    "mara": "The Lantern hums. Mara looks up from the taps. \"You're Rook's friend. You look like you haven't slept.\"",
}

SUGGESTED_REPLIES = {
    "mara": [
        "Have you seen Rook? They didn't come home.",
        "I'll cover whatever Rook owes you.",
        "I'm Rook's sister. Tell me what you know.",  # a lie: contradicts K3
    ],
}
