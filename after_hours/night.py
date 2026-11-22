"""One night of After Hours: locations, events, conversations, the finale and Dawn.

The UI (console or browser) calls these methods; every state change happens here
or in rules.py. In agent mode NPC replies come from agent.take_turn; in scripted
mode (the playtest baseline) they come from the authored menu in content.BASELINE.
"""

from . import rules
from .agent import take_turn
from .content import (BASELINE, BASELINE_ASK, BASELINE_CALLBACKS, CLUES, ENDINGS, EVENTS, FALLBACK_LINES,
                      FINALE, LOCATION_NAMES, NPC_LOCATIONS, OPENING_LINES, PERSONAS, SUGGESTED_REPLIES)
from .state import SLOTS, Fact, GameState

EXCHANGES_PER_VISIT = 6
LIVE_CALL_LIMIT = 60
NPC_AT = {loc: npc for npc, loc in NPC_LOCATIONS.items()}


class Night:
    def __init__(self, mode: str = "scripted", provider: str = "vertex", model_fn=None):
        if mode not in ("agent", "scripted"):
            raise ValueError("mode must be agent or scripted")
        self.mode, self.provider, self.model_fn = mode, provider, model_fn
        self.state = GameState()
        self.phase = "choose_location"          # choose_location | event | talk | finale | dawn
        self.npc: str | None = None
        self.events: list[str] = []
        self.done_events: set[str] = set()
        self.exchanges = 0
        self.live_calls = 0
        self.ending: str | None = None
        self.feed: list[dict] = []              # messages produced by the last action

    # ---------- helpers ----------
    def _say(self, kind: str, text: str, speaker: str | None = None) -> None:
        self.feed.append({"kind": kind, "speaker": speaker, "text": text})

    @property
    def slot_index(self) -> int:
        return SLOTS.index(self.state.slot)

    def clue_count(self) -> int:
        return len(self.state.case_board)

    def locations(self) -> list[str]:
        if self.phase != "choose_location":
            return []
        locs = [loc for loc in ("lantern", "rooftop", "clinic")
                if not (loc == "lantern" and "lantern_closed" in self.state.flags)]
        if self.state.slot == "3am" and self.clue_count() >= 2:
            locs.append("lift")
        return locs

    # ---------- moving through the night ----------
    def visit(self, location: str) -> list[dict]:
        self.feed = []
        if location not in self.locations():
            raise ValueError("You can't go there right now.")
        self.state.location = location
        if location == "lift":
            self.phase = "finale"
            self._say("narration", FINALE["text"])
            return self.feed
        self.npc = NPC_AT[location]
        self.exchanges = 0
        self.state.conversation = []
        self.state.npcs[self.npc].conversation_delta = {"trust": 0, "warmth": 0}
        self.state.flags.discard("nico_present")
        self._say("narration", f"{self.state.slot.upper()} · {LOCATION_NAMES[location]}")
        self._say("npc", OPENING_LINES[self.npc], self.npc)
        if self.mode == "scripted":
            for (npc_id, tag), line in BASELINE_CALLBACKS.items():
                if npc_id == self.npc and self.state.npcs[npc_id].has_fact(tag):
                    self._say("npc", line, self.npc)
        self.events = self._events_here()
        self._next_event_or_talk()
        return self.feed

    def _events_here(self) -> list[str]:
        s, loc, found = self.state, self.state.location, []
        if s.slot == "2am" and loc == "clinic" and "E3" not in self.done_events:
            found.append("E3")
        if s.slot == "2am" and rules.asked_openly_count(s) >= 2 and "E4" not in self.done_events:
            found.append("E4")
        if s.slot == "midnight" and loc == "lantern" and "E1" not in self.done_events:
            found.append("E1")
        if s.slot == "1am" and loc == "lantern" and "E2" not in self.done_events:
            found.append("E2")
        jun = s.npcs["jun"]
        if (loc == "rooftop" and s.slot in ("1am", "2am") and "E5" not in self.done_events
                and jun.has_fact("promised") and not jun.has_fact("lied_to")):
            found.append("E5")
        return found

    def _next_event_or_talk(self) -> None:
        if self.events:
            self.phase = "event"
            event = EVENTS[self.events[0]]
            self._say("event", f"{event['title']}: {event['text']}")
        else:
            self.phase = "talk"

    def current_event(self) -> dict | None:
        if self.phase != "event":
            return None
        event_id = self.events[0]
        choices = dict(EVENTS[event_id]["choices"])
        if event_id == "E4":
            npc = self.state.npcs[self.npc]
            if npc.trust >= 2 and not npc.has_fact("lied_to"):
                choices["hide"] = choices["hide"].format(npc=PERSONAS[self.npc]["name"])
                del choices["walk"]
            else:
                del choices["hide"]
        if event_id == "E1" and self.state.credits < 5:
            del choices["cover"]
        return {"id": event_id, "title": EVENTS[event_id]["title"], "choices": choices}

    def choose_event(self, choice: str) -> list[dict]:
        self.feed = []
        event = self.current_event()
        if not event or choice not in event["choices"]:
            raise ValueError("That isn't a choice right now.")
        event_id = self.events.pop(0)
        self.done_events.add(event_id)
        s, ends_visit = self.state, False
        self._say("player", event["choices"][choice])
        if event_id == "E1" and choice == "cover":
            s.credits -= 5
            s.flags.add("covered_tab")
            rules.add_fact(s, "mara", Fact("kindness", "covered a regular's drink", "Cover his drink"))
            self._say("npc", "Mara raises an eyebrow. \"You're alright, kid. Ask me what you came to ask.\"", "mara")
        elif event_id == "E2":
            s.flags.add("nico_present")
            if choice in ("words", "punch"):
                rules.change_meters(s, "nico", trust=2)
            if choice == "words":
                rules.change_meters(s, "mara", warmth=1)
                self._say("npc", "The contractor backs off. Nico gives you a short nod.", "nico")
            elif choice == "punch":
                s.flags.add("lantern_closed")
                self._say("npc", "Mara slams the bar. \"Not in my bar. Out. Don't come back tonight.\"", "mara")
                ends_visit = True
            else:
                rules.change_meters(s, "nico", trust=-1)
                self._say("narration", "Nico takes the shove and says nothing. He noticed you didn't move.")
            self._check_flirt_witnessed()
        elif event_id == "E3":
            if choice == "help":
                s.flags.add("helped_e3")
                self._say("narration", "You hold pressure for most of an hour. The courier makes it.")
                self._say("npc", "Nico wipes his hands. \"You stayed. That counts.\"", "nico")
                if s.npcs["nico"].revealed_clue is None:
                    self._say("clue", rules.reveal(s, "nico"))
                ends_visit = True
            else:
                rules.change_meters(s, "nico", trust=-1)
                self._say("narration", "Nico works alone. It takes him a long time.")
        elif event_id == "E4":
            if choice == "hide":
                s.flags.add("hidden_from_tail")
                self._say("narration", f"{PERSONAS[self.npc]['name']} hides you. The grey jacket leaves.")
            else:
                s.flags.add("tail_on_you")
                self._say("narration", "You walk out. Footsteps follow you all the way down the block.")
        elif event_id == "E5":
            s.flags.add("e5_seen")
            if "C1" not in s.case_board:
                s.case_board.append("C1")
                self._say("clue", "Drone footage: " + CLUES["C1"]["line"])
        if ends_visit:
            self._end_visit()
        else:
            self._next_event_or_talk()
        return self.feed

    def _check_flirt_witnessed(self) -> None:
        if "nico_present" in self.state.flags and self.state.npcs["mara"].has_fact("flirted"):
            self.state.flags.add("nico_knows_flirt")

    # ---------- conversation ----------
    def options(self) -> list[str]:
        """Suggested replies (agent mode) or the full authored menu (scripted mode)."""
        if self.phase != "talk":
            return []
        if self.mode == "agent":
            return SUGGESTED_REPLIES[self.npc]
        return [BASELINE_ASK[self.npc]] + [o[0] for o in BASELINE[self.npc]]

    def say(self, text: str) -> list[dict]:
        """Agent mode: free text or a suggested reply."""
        self.feed = []
        if self.phase != "talk" or self.mode != "agent":
            raise ValueError("You can't talk right now.")
        model_fn = self.model_fn
        over_budget = self.live_calls >= LIVE_CALL_LIMIT
        if over_budget:  # session budget spent: scripted fallback lines from here on
            def model_fn(system, user):
                raise RuntimeError("live call limit reached")
        self._say("player", text.strip()[:300])
        before = (self.state.npcs[self.npc].next_memory_id, len(self.state.npcs[self.npc].facts))
        result = take_turn(self.state, self.npc, text, self.provider, model_fn=model_fn)
        if not over_budget:
            self.live_calls += result.attempts
        self._say("npc", result.shown[0], self.npc)
        for extra in result.shown[1:]:
            self._say("clue", extra)
        self._after_turn(before)
        if result.action == "end_conversation":
            self._say("narration", f"{PERSONAS[self.npc]['name']} turns away. The conversation's over.")
            self._end_visit()
        return self.feed

    def choose_option(self, index: int) -> list[dict]:
        """Scripted mode: pick from the authored menu. Facts come only from option tags."""
        self.feed = []
        if self.phase != "talk" or self.mode != "scripted":
            raise ValueError("You can't do that right now.")
        options = self.options()
        if not 0 <= index < len(options):
            raise ValueError("No such option.")
        s, npc_id = self.state, self.npc
        before = (s.npcs[npc_id].next_memory_id, len(s.npcs[npc_id].facts))
        self._say("player", options[index])
        if index == 0:  # ask about Rook
            if "reveal_clue" in rules.legal_actions(s, npc_id)["actions"]:
                self._say("npc", "A long pause. \"...Alright.\"", npc_id)
                self._say("clue", rules.reveal(s, npc_id))
            else:
                self._say("npc", FALLBACK_LINES[npc_id][rules.band(s, npc_id)], npc_id)
        else:
            text, tag, trust, warmth, reply = BASELINE[npc_id][index - 1]
            if tag and not s.npcs[npc_id].has_fact(tag):
                rules.add_fact(s, npc_id, Fact(tag, text[:60], text))
            rules.change_meters(s, npc_id, trust, warmth)
            self._say("npc", reply, npc_id)
        self._after_turn(before)
        return self.feed

    def _after_turn(self, before: tuple[int, int]) -> None:
        npc = self.state.npcs[self.npc]
        name = PERSONAS[self.npc]["name"]
        if len(npc.facts) > before[1]:
            self._say("system", f"{name} will hold you to that.")
        elif npc.next_memory_id > before[0]:
            self._say("system", f"{name} will remember that.")
        self._check_flirt_witnessed()
        self.exchanges += 1
        if self.exchanges >= EXCHANGES_PER_VISIT and self.phase == "talk":
            self._say("narration", "The hour's nearly up.")
            self._end_visit()

    def leave(self) -> list[dict]:
        self.feed = []
        if self.phase not in ("talk", "event"):
            raise ValueError("Nothing to leave.")
        self._say("narration", "You step back out into the neon.")
        self._end_visit()
        return self.feed

    def _end_visit(self) -> None:
        self.npc, self.events = None, []
        self.state.flags.discard("nico_present")
        if self.slot_index + 1 >= len(SLOTS):
            self._dawn(found_rook=False)
        else:
            self.state.slot = SLOTS[self.slot_index + 1]
            self.phase = "choose_location"
            if self.state.slot == "3am" and self.clue_count() >= 2:
                self._say("system", "You've pieced it together: the old Kessler freight lift.")

    # ---------- finale and Dawn ----------
    def choose_finale(self, choice: str) -> list[dict]:
        self.feed = []
        if self.phase != "finale" or choice not in FINALE["choices"]:
            raise ValueError("That isn't a choice right now.")
        self._say("player", FINALE["choices"][choice])
        self._dawn(found_rook=True, choice=choice)
        return self.feed

    def _dawn(self, found_rook: bool, choice: str | None = None) -> None:
        s = self.state
        if found_rook and choice == "keep":
            ending = "paid_in_full"
        elif found_rook:
            jun = s.npcs["jun"]
            jun_helps = choice == "return" and (jun.has_fact("promised") or any(
                c["location"] == "kessler_lift" for c in jun.commitments))
            ally = any(npc.trust >= 3 for npc in s.npcs.values())
            ending = "out_by_dawn" if "tail_on_you" not in s.flags and (jun_helps or ally) else "last_call"
        else:
            ending = "morning_after" if "nico_knows_flirt" in s.flags else "last_call"
        self.ending, self.phase = ending, "dawn"
        title, text = ENDINGS[ending]
        self._say("ending", f"{title}. {text}")

    def dawn_cards(self) -> list[dict]:
        cards = []
        for npc_id, npc in self.state.npcs.items():
            cards.append({
                "npc": PERSONAS[npc_id]["name"], "trust": npc.trust, "warmth": npc.warmth,
                "remembers": [m["note"] for m in npc.memories[:3]],
                "facts": [f.tag for f in npc.facts],
                "promise_broken": npc_id == "jun" and self.ending == "paid_in_full" and npc.has_fact("promised"),
            })
        return cards

    def snapshot(self) -> dict:
        """Everything a UI needs to draw the current screen."""
        s = self.state
        return {
            "mode": self.mode, "phase": self.phase, "slot": s.slot, "location": s.location,
            "npc": self.npc, "npc_name": PERSONAS[self.npc]["name"] if self.npc else None,
            "locations": [{"id": loc, "name": LOCATION_NAMES[loc]} for loc in self.locations()],
            "event": self.current_event(), "options": self.options(),
            "finale_choices": FINALE["choices"] if self.phase == "finale" else {},
            "case_board": [{"id": c, "title": CLUES[c]["title"], "text": CLUES[c]["line"]} for c in s.case_board],
            "credits": s.credits, "exchanges_left": EXCHANGES_PER_VISIT - self.exchanges,
            "meters": {n: {"trust": v.trust, "warmth": v.warmth} for n, v in s.npcs.items()},
            "ending": {"id": self.ending, "title": ENDINGS[self.ending][0]} if self.ending else None,
            "dawn_cards": self.dawn_cards() if self.phase == "dawn" else [],
            "feed": self.feed,
        }
