"""Game rules: which actions are legal, and how a validated proposal changes state."""

from .content import CLUES, COMMITMENT_OPTIONS
from .state import (MAX_FACTS, MAX_MEMORIES, METER_MAX, METER_MIN, Fact, GameState,
                    clamp)

PER_TURN_DELTA = 2
PER_CONVERSATION_DELTA = 3


def clue_for(npc_id: str) -> str | None:
    return next((cid for cid, c in CLUES.items() if c["npc"] == npc_id), None)


def clue_threshold(state: GameState, npc_id: str) -> int:
    """Trust needed for the NPC to reveal their clue (GDD Section 8)."""
    npc = state.npcs[npc_id]
    if npc.has_fact("lied_to"):
        return 4
    if npc.has_fact("kindness"):
        return 2
    return 3


def legal_actions(state: GameState, npc_id: str) -> dict:
    """What the agent may propose this turn. Computed fresh every turn."""
    npc = state.npcs[npc_id]
    actions = ["none", "refuse", "end_conversation"]
    clue = clue_for(npc_id)
    traded = npc_id == "mara" and "covered_tab" in state.flags
    if clue and npc.revealed_clue is None and (npc.trust >= clue_threshold(state, npc_id) or traded):
        actions.append("reveal_clue")
    commitments = []
    if npc.trust >= 2 and not npc.has_fact("lied_to"):
        commitments = [c for c in COMMITMENT_OPTIONS.get(npc_id, []) if c not in npc.commitments]
    if commitments:
        actions.append("commit")
    return {"actions": actions, "commitments": commitments}


def apply(state: GameState, npc_id: str, proposal: dict) -> list[str]:
    """Apply an already-validated proposal. Returns the text shown to the player."""
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
    if fact.get("tag", "none") != "none" and len(npc.facts) < MAX_FACTS:
        npc.facts.append(Fact(fact["tag"], fact["detail"], fact["evidence"]))

    if proposal["action"] == "reveal_clue":
        clue_id = clue_for(npc_id)
        npc.revealed_clue = clue_id
        state.case_board.append(clue_id)
        shown.append(CLUES[clue_id]["line"])     # canonical text, never model-written
    elif proposal["action"] == "commit":
        npc.commitments.append(proposal["commitment"])

    return shown


def band(state: GameState, npc_id: str) -> str:
    trust = state.npcs[npc_id].trust
    return "low" if trust <= -2 else "high" if trust >= 2 else "mid"
