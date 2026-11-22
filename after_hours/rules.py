"""Game rules: which actions are legal, and how a validated proposal changes state."""

from .content import CLUES, COMMITMENT_OPTIONS
from .state import (MAX_FACTS, MAX_MEMORIES, METER_MAX, METER_MIN, Fact, GameState,
                    clamp)

PER_TURN_DELTA = 2
PER_CONVERSATION_DELTA = 3


def clue_for(npc_id: str) -> str | None:
    return next((cid for cid, c in CLUES.items() if c["npc"] == npc_id), None)


def clue_threshold(state: GameState, npc_id: str) -> int:
    """Trust needed for the NPC to reveal their clue (mystery bible Section 4)."""
    npc = state.npcs[npc_id]
    if npc.has_fact("lied_to"):
        return 4
    if npc.has_fact("kindness") and npc_id != "jun":  # Jun doesn't care about kindness
        return 2
    return 3


def traded_for_clue(state: GameState, npc_id: str) -> bool:
    """The non-trust routes to a clue: covering the tab (Mara) or a promise (Jun)."""
    if npc_id == "mara":
        return "covered_tab" in state.flags
    if npc_id == "jun":
        return state.npcs["jun"].has_fact("promised")
    return False


def clue_locked(state: GameState, npc_id: str) -> bool:
    """Nico won't share if he saw you flirt with Mara, unless you helped him in E3."""
    return npc_id == "nico" and "nico_knows_flirt" in state.flags and "helped_e3" not in state.flags


def legal_actions(state: GameState, npc_id: str) -> dict:
    """What the agent may propose this turn. Computed fresh every turn."""
    npc = state.npcs[npc_id]
    actions = ["none", "refuse", "end_conversation"]
    clue = clue_for(npc_id)
    earned = npc.trust >= clue_threshold(state, npc_id) or traded_for_clue(state, npc_id)
    if clue and npc.revealed_clue is None and earned and not clue_locked(state, npc_id):
        actions.append("reveal_clue")
    commitments = []
    if npc.trust >= 2 and not npc.has_fact("lied_to"):
        commitments = [c for c in COMMITMENT_OPTIONS.get(npc_id, []) if c not in npc.commitments]
    if commitments:
        actions.append("commit")
    return {"actions": actions, "commitments": commitments}


def reveal(state: GameState, npc_id: str) -> str:
    """Mark the NPC's clue as shared and add it to the case board. Returns the canonical text."""
    clue_id = clue_for(npc_id)
    state.npcs[npc_id].revealed_clue = clue_id
    if clue_id not in state.case_board:
        state.case_board.append(clue_id)
    return CLUES[clue_id]["line"]


def change_meters(state: GameState, npc_id: str, trust: int = 0, warmth: int = 0) -> None:
    """Event and baseline changes: clamped to the meter range only."""
    npc = state.npcs[npc_id]
    npc.trust = clamp(npc.trust + trust, METER_MIN, METER_MAX)
    npc.warmth = clamp(npc.warmth + warmth, METER_MIN, METER_MAX)


def add_fact(state: GameState, npc_id: str, fact: Fact) -> None:
    npc = state.npcs[npc_id]
    if len(npc.facts) < MAX_FACTS:
        npc.facts.append(fact)


def apply(state: GameState, npc_id: str, proposal: dict) -> list[str]:
    """Apply an already-validated agent proposal. Returns the text shown to the player."""
    npc = state.npcs[npc_id]
    shown = [proposal["line"]]

    for meter in ("trust", "warmth"):
        delta = clamp(proposal["relationship_delta"][meter], -PER_TURN_DELTA, PER_TURN_DELTA)
        used = npc.conversation_delta[meter]
        delta = clamp(used + delta, -PER_CONVERSATION_DELTA, PER_CONVERSATION_DELTA) - used
        npc.conversation_delta[meter] += delta
        setattr(npc, meter, clamp(getattr(npc, meter) + delta, METER_MIN, METER_MAX))

    note = proposal["memory_note"].strip()
    if note:
        npc.memories.insert(0, {"id": f"m{npc.next_memory_id}", "slot": state.slot, "note": note})
        npc.next_memory_id += 1
        del npc.memories[MAX_MEMORIES:]

    fact = proposal.get("memory_fact") or {}
    if fact.get("tag", "none") != "none":
        add_fact(state, npc_id, Fact(fact["tag"], fact["detail"], fact["evidence"]))

    if proposal["action"] == "reveal_clue":
        shown.append(reveal(state, npc_id))     # canonical text, never model-written
    elif proposal["action"] == "commit":
        npc.commitments.append(proposal["commitment"])

    return shown


def band(state: GameState, npc_id: str) -> str:
    trust = state.npcs[npc_id].trust
    return "low" if trust <= -2 else "high" if trust >= 2 else "mid"


def asked_openly_count(state: GameState) -> int:
    return sum(f.tag == "asked_openly" for npc in state.npcs.values() for f in npc.facts)
