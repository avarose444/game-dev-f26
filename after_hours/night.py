"""One night of After Hours: locations, events, conversations, deals, the hunt and Dawn.

v0.3 loop (Nov 22 redesign): each person wants something; deals for those wants
open their clue (some deals are gambles, some betray someone else). Sallow hunts
Rook too and gets closer every hour. At 3 a.m. you decide where Rook is hiding.

The UI calls these methods; every state change happens here or in rules.py.
Agent mode: NPC replies from agent.take_turn. Scripted mode (the playtest
baseline): replies from the authored menu in content.BASELINE.
"""

from . import rules
from .agent import take_turn
from .content import (BASELINE, BASELINE_ASK, BASELINE_CALLBACKS, CLUES, DEALS, ENDINGS, EVENTS,
                      EXTRA_EVIDENCE, FACT_CUES, FALLBACK_LINES, FINALE, HIDEOUTS, LEAD_HINTS, LOCATION_NAMES,
                      NPC_LOCATIONS, OPENING_LINES, PERSONAS, ROOK_IS_AT, SALLOW_MAX, SALLOW_STEPS,
                      SUGGESTED_REPLIES, WANT_ASK, WANTS)
from .state import SLOTS, Fact

EXCHANGES_PER_VISIT = 6
LIVE_CALL_LIMIT = 60
NPC_AT = {loc: npc for npc, loc in NPC_LOCATIONS.items()}
EVIDENCE = {**{cid: {"title": c["title"], "line": c["line"]} for cid, c in CLUES.items()}, **EXTRA_EVIDENCE}


class Night:
    def __init__(self, mode: str = "scripted", provider: str = "vertex", model_fn=None):
        if mode not in ("agent", "scripted"):
            raise ValueError("mode must be agent or scripted")
        from .state import GameState
        self.mode, self.provider, self.model_fn = mode, provider, model_fn
        self.state = GameState()
        self.phase = "choose_location"          # choose_location | event | talk | finale | dawn
        self.npc: str | None = None
        self.events: list[str] = []
        self.done_events: set[str] = set()
        self.exchanges = 0
        self.live_calls = 0
        self.heat = 0                           # Sallow's progress, 0..SALLOW_MAX
        self.ending: str | None = None
        self.feed: list[dict] = []              # messages produced by the last action
        self.history: list[dict] = []           # every message this night (to redraw the page)
        self.met: set[str] = set()
        self.want_known: set[str] = set()
        self.used_suggestions: set[str] = set()
        self.nudged: set[str] = set()
        self.memory_cue_shown = False

    # ---------- helpers ----------
    def _say(self, kind: str, text: str, speaker: str | None = None) -> None:
        message = {"kind": kind, "speaker": speaker, "text": text}
        self.feed.append(message)
        self.history.append(message)

    @property
    def slot_index(self) -> int:
        return SLOTS.index(self.state.slot)

    def clue_count(self) -> int:
        return len(self.state.case_board)

    def _heat(self, amount: int, why: str) -> None:
        before = self.heat
        self.heat = max(0, min(SALLOW_MAX, self.heat + amount))
        if self.heat != before:
            arrow = "closer" if self.heat > before else "further off"
            self._say("hunt", f"Sallow is {arrow}: {why}")

    def want_done(self, npc_id: str) -> bool:
        return f"want_done:{npc_id}" in self.state.flags

    def allies(self) -> list[str]:
        """People who'll help you get Rook out: a deal kept with them, or real trust."""
        return [n for n, npc in self.state.npcs.items() if self.want_done(n) or npc.trust >= 3]

    def locations(self) -> list[str]:
        if self.phase != "choose_location":
            return []
        return [loc for loc in ("lantern", "rooftop", "clinic")
                if not (loc == "lantern" and "lantern_closed" in self.state.flags)]

    def hideouts(self) -> list[str]:
        return list(HIDEOUTS) if self.phase == "choose_location" and self.state.slot == "3am" else []

    # ---------- moving through the night ----------
    def visit(self, location: str) -> list[dict]:
        self.feed = []
        if location in self.hideouts():
            return self._search(location)
        if location not in self.locations():
            raise ValueError("You can't go there right now.")
        self.state.location = location
        self.npc = NPC_AT[location]
        self.met.add(self.npc)
        self.memory_cue_shown = False
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
        if s.slot == "2am" and self.heat >= 3 and "E4" not in self.done_events:
            found.append("E4")
        if s.slot == "midnight" and loc == "lantern" and "E1" not in self.done_events:
            found.append("E1")
        if s.slot == "1am" and loc == "lantern" and "E2" not in self.done_events and not self.want_done("mara"):
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
            self._nudge_if_ready()

    def current_event(self) -> dict | None:
        if self.phase != "event":
            return None
        event_id = self.events[0]
        choices = dict(EVENTS[event_id]["choices"])
        if event_id == "E4":
            npc = self.state.npcs[self.npc]
            if npc.trust >= 2 or self.want_done(self.npc):
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
            rules.add_fact(s, "mara", Fact("kindness", "covered a regular's drink", "Cover his drink"))
            rules.change_meters(s, "mara", trust=1, warmth=1)
            self._say("npc", "Mara raises an eyebrow. \"You're alright, kid.\"", "mara")
            self._say("system", "Mara noticed that. Mara: trust +1 · warmth +1")
        elif event_id == "E2":
            s.flags.add("nico_present")
            if choice in ("words", "punch"):
                rules.change_meters(s, "nico", trust=2)
                self._complete_want("mara", "The contractor stumbles out into the rain. Mara watches him go.")
            if choice == "words":
                rules.change_meters(s, "mara", warmth=1)
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
                self._say("narration", f"{PERSONAS[self.npc]['name']} hides you. The grey jacket leaves empty-handed.")
                self._heat(-1, "he lost your trail.")
            else:
                self._say("narration", "You walk out. Footsteps follow you all the way down the block.")
                self._heat(2, "he's following you now.")
        elif event_id == "E5":
            if "E5" not in s.case_board:
                s.case_board.append("E5")
                self._say("clue", "Drone footage: " + EXTRA_EVIDENCE["E5"]["line"])
        if ends_visit:
            self._end_visit()
        else:
            self._next_event_or_talk()
        return self.feed

    def _check_flirt_witnessed(self) -> None:
        if "nico_present" in self.state.flags and self.state.npcs["mara"].has_fact("flirted"):
            self.state.flags.add("nico_knows_flirt")

    # ---------- wants and deals ----------
    def _learn_want(self) -> None:
        if self.npc not in self.want_known:
            self.want_known.add(self.npc)
            self._say("system", f"New lead: {WANTS[self.npc]['hint']} Offer a deal below.")

    def deals(self) -> list[dict]:
        if self.phase != "talk" or self.npc not in self.want_known or self.want_done(self.npc):
            return []
        s, out = self.state, []
        for deal_id, deal in DEALS.items():
            if deal["npc"] != self.npc or deal_id in s.flags:
                continue
            if deal_id == "mara_pay" and s.credits < 10:
                continue
            if deal_id == "jun_sell" and "C1" not in s.case_board:
                continue
            out.append({"id": deal_id, "label": deal["label"], "risky": deal["risky"]})
        return out

    def make_deal(self, deal_id: str) -> list[dict]:
        self.feed = []
        if deal_id not in {d["id"] for d in self.deals()}:
            raise ValueError("That deal isn't on the table.")
        s = self.state
        s.flags.add(deal_id)
        self._say("player", DEALS[deal_id]["label"])
        if deal_id == "mara_pay":
            s.credits -= 10
            self._complete_want("mara", "The contractor pockets the credits and leaves. Mara exhales.")
        elif deal_id == "mara_bluff":
            if self.heat <= 2:
                self._complete_want("mara", "He goes pale, checks his phone, and hurries out. The bluff worked.")
            else:
                self._say("narration", "He laughs and makes a call. \"Funny. Sallow says nobody's recalling anyone.\"")
                rules.change_meters(s, "mara", trust=-1)
                self._say("system", "The bluff failed. Mara: trust -1")
                self._heat(2, "the contractor called him about you.")
        elif deal_id == "jun_promise":
            rules.add_fact(s, "jun", Fact("promised", "will bring the chip back", "Promise to bring the chip back"))
            self._complete_want("jun", "Jun offers his hand. \"I collect on promises.\"")
        elif deal_id == "jun_sell":
            s.flags.add("mara_exposed")
            rules.change_meters(s, "mara", trust=-2)
            self._complete_want("jun", "Jun's smile sharpens. \"Mara saw it, did she? Useful.\" He sends a message.")
            self._say("system", "You sold Mara out. Nico will hear about it.")
        elif deal_id == "nico_swear":
            if "mara_exposed" in s.flags:
                rules.change_meters(s, "nico", trust=-2)
                self._say("npc", "\"Jun's people were at the Lantern asking about her an hour ago. Because of you.\" "
                                 "Nico turns away.", "nico")
                self._say("system", "Nico knows you sold Mara out. Nico: trust -2")
            else:
                rules.add_fact(s, "nico", Fact("promised", "will keep Mara out of it", "Swear you'll keep Mara out of it"))
                self._complete_want("nico", "Nico studies you for a long moment, then nods.")
        self._nudge_if_ready()
        return self.feed

    def _complete_want(self, npc_id: str, narration: str) -> None:
        s = self.state
        s.flags.add(f"want_done:{npc_id}")
        self._say("narration", narration)
        if npc_id == "mara":
            self._heat(-1, "his eyes in the Lantern are gone.")
        if self.npc == npc_id and s.npcs[npc_id].revealed_clue is None and not rules.clue_locked(s, npc_id):
            self._say("npc", "\"A deal's a deal.\"", npc_id)
            self._say("clue", rules.reveal(s, npc_id))

    # ---------- conversation ----------
    def options(self) -> list[str]:
        """Suggested replies (agent mode) or the full authored menu (scripted mode)."""
        if self.phase != "talk":
            return []
        npc = self.state.npcs[self.npc]
        fixed = [] if npc.revealed_clue else [BASELINE_ASK[self.npc]]
        if self.npc not in self.want_known and not self.want_done(self.npc):
            fixed.append(WANT_ASK)
        if self.mode == "agent":
            pool = SUGGESTED_REPLIES[self.npc] + [o[0] for o in BASELINE[self.npc]]
            fresh = [t for t in dict.fromkeys(pool) if t not in self.used_suggestions and t not in fixed]
            return fixed + fresh[:3]
        return fixed + [o[0] for o in BASELINE[self.npc] if o[0] not in self.used_suggestions]

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
        text = text.strip()[:300]
        self._say("player", text)
        self.used_suggestions.add(text)
        before = self._before()
        result = take_turn(self.state, self.npc, text, self.provider, model_fn=model_fn)
        if not over_budget:
            self.live_calls += result.attempts
        self._say("npc", result.shown[0], self.npc)
        for extra in result.shown[1:]:
            self._say("clue", extra)
        if text == WANT_ASK or self.exchanges >= 1:  # by the second exchange you've heard what they want
            self._learn_want()
        self._after_turn(before)
        if result.action == "end_conversation" and self.phase == "talk":
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
        s, npc_id, text = self.state, self.npc, options[index]
        before = self._before()
        self._say("player", text)
        self.used_suggestions.add(text)
        if text == BASELINE_ASK[npc_id]:
            if "reveal_clue" in rules.legal_actions(s, npc_id)["actions"]:
                self._say("npc", "A long pause. \"...Alright.\"", npc_id)
                self._say("clue", rules.reveal(s, npc_id))
            else:
                self._say("npc", FALLBACK_LINES[npc_id][rules.band(s, npc_id)], npc_id)
        elif text == WANT_ASK:
            self._say("npc", WANTS[npc_id]["line"], npc_id)
            self._learn_want()
        else:
            _, tag, trust, warmth, reply = next(o for o in BASELINE[npc_id] if o[0] == text)
            if tag and not s.npcs[npc_id].has_fact(tag):
                rules.add_fact(s, npc_id, Fact(tag, text[:60], text))
            rules.change_meters(s, npc_id, trust, warmth)
            self._say("npc", reply, npc_id)
        self._after_turn(before)
        return self.feed

    def _before(self) -> tuple[int, int, int, int]:
        npc = self.state.npcs[self.npc]
        return npc.next_memory_id, len(npc.facts), npc.trust, npc.warmth

    def _after_turn(self, before: tuple[int, int, int, int]) -> None:
        """Show what changed: trust and warmth ticks, new facts, the hunt, and (once a visit) a memory cue."""
        npc = self.state.npcs[self.npc]
        name = PERSONAS[self.npc]["name"]
        ticks = []
        for label, delta in (("trust", npc.trust - before[2]), ("warmth", npc.warmth - before[3])):
            if delta:
                ticks.append(f"{label} {'+' if delta > 0 else ''}{delta}")
        if ticks:
            self._say("system", f"{name}: " + " · ".join(ticks))
        if len(npc.facts) > before[1]:
            tag = npc.facts[-1].tag
            self._say("system", FACT_CUES[tag].format(name=name))
            if tag == "asked_openly":
                self._heat(1, "people heard you asking about Rook.")
            elif tag == "lied_to":
                self._heat(1, f"{name} caught your lie, and word travels.")
        elif npc.next_memory_id > before[0] and not self.memory_cue_shown:
            self.memory_cue_shown = True
            self._say("system", f"{name} will remember that.")
        self._check_flirt_witnessed()
        self._nudge_if_ready()
        self.exchanges += 1
        if self.exchanges >= EXCHANGES_PER_VISIT and self.phase == "talk":
            self._say("narration", "The hour's nearly up.")
            self._end_visit()

    def _nudge_if_ready(self) -> None:
        """Tell the player once when an NPC would share their clue if asked."""
        npc_id = self.npc
        if (npc_id and npc_id not in self.nudged and self.state.npcs[npc_id].revealed_clue is None
                and "reveal_clue" in rules.legal_actions(self.state, npc_id)["actions"]):
            self.nudged.add(npc_id)
            self._say("system", f"{PERSONAS[npc_id]['name']} seems ready to talk. Ask about Rook.")

    def leads(self) -> list[dict]:
        out = []
        for npc_id, npc in self.state.npcs.items():
            if npc.revealed_clue:
                status = "shared"
            elif rules.clue_locked(self.state, npc_id):
                status = "closed"
            elif "reveal_clue" in rules.legal_actions(self.state, npc_id)["actions"]:
                status = "ready"
            elif npc_id in self.want_known:
                status = "want"
            else:
                status = "met" if npc_id in self.met else "new"
            out.append({"npc": npc_id, "name": PERSONAS[npc_id]["name"],
                        "where": LOCATION_NAMES[NPC_LOCATIONS[npc_id]], "hint": LEAD_HINTS[npc_id],
                        "want": WANTS[npc_id]["hint"] if npc_id in self.want_known else None,
                        "trust": npc.trust, "warmth": npc.warmth,
                        "needed": rules.clue_threshold(self.state, npc_id), "status": status})
        return out

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
            self._dawn(found_rook=False, reason="Dawn comes and you never went looking for Rook.")
            return
        self.state.slot = SLOTS[self.slot_index + 1]
        self.phase = "choose_location"
        self._heat(1, "another hour gone.")
        self._say("hunt", SALLOW_STEPS[self.heat])
        if self.state.slot == "3am":
            self._say("system", "3 a.m. Last hour. Where is Rook hiding? Check your case board, then choose. "
                                "(Or spend the hour talking, and hope.)")

    # ---------- the search, the finale, Dawn ----------
    def _search(self, hideout: str) -> list[dict]:
        self.state.location = hideout
        self._say("player", f"Search the {HIDEOUTS[hideout]['name']}.")
        if hideout != ROOK_IS_AT:
            self._dawn(found_rook=False, reason=HIDEOUTS[hideout]["wrong"])
            return self.feed
        if self.heat >= SALLOW_MAX:
            helpers = self.allies()
            if not helpers:
                self._dawn(found_rook=False, reason="You find the lift, and Sallow standing in front of it. "
                                                    "Nobody's coming to help you.")
                return self.feed
            name = PERSONAS[helpers[0]]["name"]
            self._say("narration", f"Sallow is already at the lift. Then {name} steps out of the dark behind him, "
                                   "and he decides it isn't worth it.")
        self.phase = "finale"
        self._say("narration", FINALE["text"])
        return self.feed

    def choose_finale(self, choice: str) -> list[dict]:
        self.feed = []
        if self.phase != "finale" or choice not in FINALE["choices"]:
            raise ValueError("That isn't a choice right now.")
        self._say("player", FINALE["choices"][choice])
        self._dawn(found_rook=True, choice=choice)
        return self.feed

    def _dawn(self, found_rook: bool, choice: str | None = None, reason: str = "") -> None:
        s = self.state
        if reason:
            self._say("narration", reason)
        if found_rook and choice == "keep":
            ending = "paid_in_full"
        elif found_rook:
            jun_helps = choice == "return" and self.want_done("jun")
            ending = "out_by_dawn" if jun_helps or self.allies() else "last_call"
            if ending == "last_call":
                self._say("narration", "You have Rook, but nobody will help you past the checkpoint.")
        else:
            ending = "morning_after" if "nico_knows_flirt" in s.flags else "last_call"
        self.ending, self.phase, self.npc = ending, "dawn", None
        title, text = ENDINGS[ending]
        self._say("ending", f"{title}. {text}")

    def dawn_cards(self) -> list[dict]:
        cards = []
        for npc_id, npc in self.state.npcs.items():
            cards.append({
                "npc": PERSONAS[npc_id]["name"], "trust": npc.trust, "warmth": npc.warmth,
                "remembers": [m["note"] for m in npc.memories[:3]],
                "facts": [f.tag for f in npc.facts],
                "deal": self.want_done(npc_id),
                "promise_broken": npc_id == "jun" and self.ending == "paid_in_full" and self.want_done("jun"),
                "betrayed": npc_id == "mara" and "mara_exposed" in self.state.flags,
            })
        return cards

    def snapshot(self) -> dict:
        """Everything a UI needs to draw the current screen."""
        s = self.state
        return {
            "mode": self.mode, "phase": self.phase, "slot": s.slot, "location": s.location,
            "location_name": LOCATION_NAMES.get(s.location) or HIDEOUTS.get(s.location, {}).get("name", s.location),
            "npc": self.npc, "npc_name": PERSONAS[self.npc]["name"] if self.npc else None,
            "locations": [{"id": loc, "name": LOCATION_NAMES[loc]} for loc in self.locations()],
            "hideouts": [{"id": h, "name": HIDEOUTS[h]["name"], "about": HIDEOUTS[h]["about"]} for h in self.hideouts()],
            "event": self.current_event(), "options": self.options(), "deals": self.deals(),
            "finale_choices": FINALE["choices"] if self.phase == "finale" else {},
            "case_board": [{"id": c, "title": EVIDENCE[c]["title"], "text": EVIDENCE[c]["line"]} for c in s.case_board],
            "credits": s.credits, "exchanges_left": EXCHANGES_PER_VISIT - self.exchanges,
            "sallow": {"heat": self.heat, "max": SALLOW_MAX, "where": SALLOW_STEPS[self.heat]},
            "leads": self.leads(), "clues_needed": 2,
            "ending": {"id": self.ending, "title": ENDINGS[self.ending][0]} if self.ending else None,
            "dawn_cards": self.dawn_cards() if self.phase == "dawn" else [],
            "feed": self.feed,
        }
