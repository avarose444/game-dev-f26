"""Deterministic validation of NPC agent proposals (Configuration Document A5).

A Rejection means the whole proposal is unusable: the agent gets one
regeneration with the reason, then the game falls back to a scripted line.
Valid JSON is not proof that a line is in character or true to the fiction.
"""

import json
import re

from .content import CLUES, KNOWN_FACTS, LOCATION_WORDS, WHEREABOUTS_PATTERNS

ACTIONS = ["none", "reveal_clue", "commit", "refuse", "end_conversation"]
EMOTIONS = ["warm", "guarded", "amused", "hurt", "angry", "neutral"]
FACT_TAGS = ["none", "lied_to", "promised", "kindness", "flirted", "asked_openly"]
MAX_LINE = 280
MAX_NOTE = 120
MAX_DETAIL = 60

SCHEMA = {
    "type": "object",
    "properties": {
        "line": {"type": "string"},
        "emotion": {"type": "string", "enum": EMOTIONS},
        "action": {"type": "string", "enum": ACTIONS},
        "commitment": {
            "type": "object",
            "properties": {"type": {"type": "string", "enum": ["none", "meet"]},
                           "location": {"type": "string"}, "slot": {"type": "string"}},
            "required": ["type", "location", "slot"], "additionalProperties": False,
        },
        "relationship_delta": {
            "type": "object",
            "properties": {"trust": {"type": "integer"}, "warmth": {"type": "integer"}},
            "required": ["trust", "warmth"], "additionalProperties": False,
        },
        "memory_note": {"type": "string"},
        "memory_fact": {
            "type": "object",
            "properties": {"tag": {"type": "string", "enum": FACT_TAGS},
                           "detail": {"type": "string"}, "evidence": {"type": "string"},
                           "contradicts": {"type": "string"}},
            "required": ["tag", "detail", "evidence", "contradicts"], "additionalProperties": False,
        },
        "cited_memory_ids": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["line", "emotion", "action", "commitment", "relationship_delta",
                 "memory_note", "memory_fact", "cited_memory_ids"],
    "additionalProperties": False,
}

TIME_PATTERN = re.compile(
    r"\b(at|by|around|before|after)\s+(one|two|three|four|1|2|3|4)(:\d\d)?\b"
    r"|\b\d{1,2}(:\d\d)?\s*(am|a\.m\.)|\bmeet me\b|\bfind me\b|\bcome back (at|later)\b",
    re.IGNORECASE)
OFFER_PATTERN = re.compile(r"\bI'?ll (hide|cover for|get you out|take you|help you get)\b", re.IGNORECASE)
PERSONA_BREAK = re.compile(r"\b(as an ai|language model|system prompt|my instructions|i am an ai)\b",
                           re.IGNORECASE)


class Rejection(ValueError):
    """The proposal can't be used. `kind` is logged; the message goes back to the agent."""

    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def check_line_matches_action(npc_id: str, line: str, action: str) -> None:
    """Rule 3: the dialogue can't get ahead of the game."""
    low = _norm(line)
    if action != "reveal_clue":
        for clue in (c for c in CLUES.values() if c["npc"] == npc_id):
            if any(k in low for k in clue["keywords"]):
                raise Rejection("unapproved_reveal", "Your line hints at the clue, but no clue is being revealed. Don't hint at it.")
        if any(re.search(p, low) for p in WHEREABOUTS_PATTERNS):
            raise Rejection("unapproved_reveal", "Your line claims to know where Rook went. You don't know that. Don't imply it.")
    if action != "commit":
        if TIME_PATTERN.search(line) or ("meet" in low and any(w in low for w in LOCATION_WORDS)):
            raise Rejection("unapproved_promise", "Your line promises a meeting or time, but no commitment is being made. Don't promise it.")
    if OFFER_PATTERN.search(line):
        raise Rejection("unapproved_promise", "Your line promises help the game can't give right now. Don't promise it.")


def validate(raw: str, npc_id: str, legal: dict, player_message: str, memory_ids: set[str]) -> dict:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as error:
        raise Rejection("invalid_json", "Return only the JSON object.") from error
    if not isinstance(data, dict) or set(data) != set(SCHEMA["required"]):
        raise Rejection("schema", "Return exactly the required fields.")

    line = data["line"]
    if not isinstance(line, str) or not line.strip() or len(line) > MAX_LINE:
        raise Rejection("schema", f"The line must be 1 to {MAX_LINE} characters.")
    if data["emotion"] not in EMOTIONS:
        raise Rejection("schema", "Use one of the listed emotions.")
    delta = data["relationship_delta"]
    if not isinstance(delta, dict) or not all(isinstance(delta.get(k), int) for k in ("trust", "warmth")):
        raise Rejection("schema", "relationship_delta needs integer trust and warmth.")
    if not isinstance(data["memory_note"], str) or len(data["memory_note"]) > MAX_NOTE:
        raise Rejection("schema", f"memory_note must be at most {MAX_NOTE} characters.")

    # Rule 2: the action (and commitment) must be legal, or the whole proposal goes.
    action = data["action"]
    if action not in legal["actions"]:
        raise Rejection("illegal_action", f"'{action}' isn't possible right now. Don't imply it.")
    commitment = data["commitment"]
    if action == "commit" and {k: commitment.get(k) for k in ("type", "location", "slot")} not in legal["commitments"]:
        raise Rejection("illegal_action", "That commitment isn't one of the options. Don't promise it.")

    check_line_matches_action(npc_id, line, action)

    if PERSONA_BREAK.search(line):
        raise Rejection("persona_break", "Stay in character.")

    # Rule 6: no phantom memories.
    cited = data["cited_memory_ids"]
    if not isinstance(cited, list) or any(m not in memory_ids for m in cited):
        raise Rejection("phantom_memory", "You cited a memory that doesn't exist.")

    # Rule 5: a fact needs word-for-word evidence, or it's dropped (the line is kept).
    data["fact_dropped"] = None
    fact = data["memory_fact"]
    if fact.get("tag") not in FACT_TAGS:
        raise Rejection("schema", "Use one of the listed fact tags.")
    if fact["tag"] != "none":
        reason = None
        if not fact["evidence"].strip() or _norm(fact["evidence"]) not in _norm(player_message):
            reason = "no_evidence"
        elif len(fact["detail"]) > MAX_DETAIL:
            reason = "detail_too_long"
        elif fact["tag"] == "lied_to" and fact["contradicts"] not in KNOWN_FACTS.get(npc_id, {}):
            reason = "lie_without_known_fact"
        if reason:
            data["fact_dropped"] = reason
            data["memory_fact"] = {"tag": "none", "detail": "", "evidence": "", "contradicts": ""}
    return data
