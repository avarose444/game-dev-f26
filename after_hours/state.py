"""Game state. The game engine is the only thing that changes these objects."""

from dataclasses import dataclass, field

METER_MIN, METER_MAX = -5, 5
MAX_MEMORIES = 12
MAX_FACTS = 8
SLOTS = ["midnight", "1am", "2am", "3am"]


@dataclass
class Fact:
    tag: str          # lied_to | promised | kindness | flirted | asked_openly
    detail: str
    evidence: str     # exact quote from the player's message


@dataclass
class NPCState:
    trust: int = 0
    warmth: int = 0
    memories: list[dict] = field(default_factory=list)   # {"id": "m1", "slot": ..., "note": ...}
    facts: list[Fact] = field(default_factory=list)
    revealed_clue: str | None = None
    commitments: list[dict] = field(default_factory=list)
    conversation_delta: dict = field(default_factory=lambda: {"trust": 0, "warmth": 0})
    next_memory_id: int = 1

    def has_fact(self, tag: str) -> bool:
        return any(f.tag == tag for f in self.facts)


@dataclass
class GameState:
    player: dict = field(default_factory=lambda: {
        "name": "Sam", "pronouns": "they/them", "background": "Courier", "trait": "Honest"})
    slot: str = "midnight"
    location: str = "lantern"
    npcs: dict[str, NPCState] = field(default_factory=lambda: {"mara": NPCState()})
    conversation: list[dict] = field(default_factory=list)   # {"speaker": ..., "text": ...}
    case_board: list[str] = field(default_factory=list)
    flags: set[str] = field(default_factory=set)              # e.g. "covered_tab" from event E1
    log: list[dict] = field(default_factory=list)             # per-turn metadata


def clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))
