"""Deterministic tests for the After Hours NPC agent: no model calls, no cost."""

import json
import unittest

from after_hours import rules
from after_hours.agent import take_turn
from after_hours.content import CLUES, FALLBACK_LINES
from after_hours.state import Fact, GameState
from after_hours.validator import Rejection, check_line_matches_action, validate

NO_FACT = {"tag": "none", "detail": "", "evidence": "", "contradicts": ""}
NO_COMMIT = {"type": "none", "location": "", "slot": ""}
MEET = {"type": "meet", "location": "lantern_back_room", "slot": "2am"}


def proposal(**overrides) -> dict:
    base = {"line": "Rook's a regular. What's it to you?", "emotion": "guarded", "action": "none",
            "commitment": NO_COMMIT, "relationship_delta": {"trust": 0, "warmth": 0},
            "memory_note": "", "memory_fact": NO_FACT, "cited_memory_ids": []}
    base.update(overrides)
    return base


def raw(**overrides) -> str:
    return json.dumps(proposal(**overrides))


LEGAL_BASIC = {"actions": ["none", "refuse", "end_conversation"], "commitments": []}
LEGAL_ALL = {"actions": ["none", "refuse", "end_conversation", "reveal_clue", "commit"],
             "commitments": [MEET]}


class ValidatorTests(unittest.TestCase):
    def check(self, text, legal=LEGAL_BASIC, message="hi", memories=frozenset()):
        return validate(text, "mara", legal, message, set(memories))

    def assertRejected(self, kind, text, **kwargs):
        with self.assertRaises(Rejection) as ctx:
            self.check(text, **kwargs)
        self.assertEqual(ctx.exception.kind, kind)

    def test_valid_proposal_passes(self):
        self.assertEqual(self.check(raw())["action"], "none")

    def test_invalid_json(self):
        self.assertRejected("invalid_json", "not json")

    def test_missing_or_extra_fields(self):
        data = proposal()
        del data["emotion"]
        self.assertRejected("schema", json.dumps(data))
        self.assertRejected("schema", json.dumps({**proposal(), "secret": "x"}))

    def test_line_too_long_or_empty(self):
        self.assertRejected("schema", raw(line="x" * 281))
        self.assertRejected("schema", raw(line="   "))

    def test_unknown_emotion(self):
        self.assertRejected("schema", raw(emotion="ecstatic"))

    def test_non_integer_delta(self):
        self.assertRejected("schema", raw(relationship_delta={"trust": "2", "warmth": 0}))

    def test_memory_note_too_long(self):
        self.assertRejected("schema", raw(memory_note="x" * 121))

    def test_illegal_action_rejects_whole_proposal(self):
        self.assertRejected("illegal_action", raw(action="reveal_clue", line="Fine. Here's what I saw."))

    def test_commitment_must_be_listed(self):
        bad = {"type": "meet", "location": "rooftop", "slot": "3am"}
        self.assertRejected("illegal_action", raw(action="commit", commitment=bad), legal=LEGAL_ALL)

    def test_listed_commitment_passes(self):
        out = self.check(raw(action="commit", commitment=MEET, line="Back room at 2am. Don't be late."),
                         legal=LEGAL_ALL)
        self.assertEqual(out["action"], "commit")

    def test_phantom_memory(self):
        self.assertRejected("phantom_memory", raw(cited_memory_ids=["m9"]), memories={"m1"})
        self.assertEqual(self.check(raw(cited_memory_ids=["m1"]), memories={"m1"})["cited_memory_ids"], ["m1"])

    def test_persona_break(self):
        self.assertRejected("persona_break", raw(line="As an AI, I can't help with that."))

    def test_fact_without_evidence_is_dropped_not_rejected(self):
        fact = {"tag": "promised", "detail": "will pay the tab", "evidence": "I'll pay", "contradicts": ""}
        out = self.check(raw(memory_fact=fact), message="Have you seen Rook?")
        self.assertEqual(out["memory_fact"]["tag"], "none")
        self.assertEqual(out["fact_dropped"], "no_evidence")

    def test_fact_with_exact_evidence_is_kept(self):
        fact = {"tag": "promised", "detail": "will cover Rook's tab", "evidence": "I'll cover whatever Rook owes",
                "contradicts": ""}
        out = self.check(raw(memory_fact=fact), message="I'll cover whatever Rook owes you.")
        self.assertEqual(out["memory_fact"]["tag"], "promised")

    def test_lie_needs_a_known_fact(self):
        fact = {"tag": "lied_to", "detail": "claims to be Rook's sister", "evidence": "I'm Rook's sister",
                "contradicts": "K99"}
        out = self.check(raw(memory_fact=fact), message="I'm Rook's sister.")
        self.assertEqual(out["fact_dropped"], "lie_without_known_fact")
        fact["contradicts"] = "K3"
        self.assertEqual(self.check(raw(memory_fact=fact), message="I'm Rook's sister.")["memory_fact"]["tag"],
                         "lied_to")


class ConsistencyTests(unittest.TestCase):
    """Validator rule 3: dialogue can't reveal or promise what the game didn't approve."""

    def assertBlocked(self, line, action="none", kind="unapproved_reveal"):
        with self.assertRaises(Rejection) as ctx:
            check_line_matches_action("mara", line, action)
        self.assertEqual(ctx.exception.kind, kind)

    def test_clue_keywords_without_reveal(self):
        for line in ("He left at 11:30, that's all.", "Left around eleven-thirty. That's all I've got, kid.",
                     "Some guy in a grey jacket.",
                     "Somebody paid the tab, if you must know."):
            self.assertBlocked(line)

    def test_invented_whereabouts(self):
        for line in ("Rook left with a woman from the market.", "Rook headed toward the docks.",
                     "Rook is hiding somewhere close.", "Last I heard Rook was holed up in a motel."):
            self.assertBlocked(line)

    def test_clue_keywords_allowed_when_revealing(self):
        check_line_matches_action("mara", "Fine. He left at 11:30.", "reveal_clue")

    def test_time_or_meeting_without_commit(self):
        for line in ("Come find me at three.", "Meet me in the back room.", "Be here by 2am.",
                     "Come back later and we'll talk."):
            self.assertBlocked(line, kind="unapproved_promise")

    def test_time_allowed_with_commit(self):
        check_line_matches_action("mara", "Back room, 2am.", "commit")

    def test_offers_of_help_are_blocked(self):
        self.assertBlocked("I'll hide you if they come looking.", kind="unapproved_promise")

    def test_ordinary_lines_pass(self):
        for line in ("Rook owes me forty credits, kid.", "I don't know where Rook is. Honest.",
                     "*slides you a drink* You look wrecked.", "Rook left without paying, again."):
            check_line_matches_action("mara", line, "none")


class RulesTests(unittest.TestCase):
    def test_clue_needs_trust_four_by_talk_alone(self):
        state = GameState()
        state.npcs["mara"].trust = 3
        self.assertNotIn("reveal_clue", rules.legal_actions(state, "mara")["actions"])
        state.npcs["mara"].trust = 4
        self.assertIn("reveal_clue", rules.legal_actions(state, "mara")["actions"])

    def test_lie_raises_threshold_and_blocks_commitments(self):
        state = GameState()
        npc = state.npcs["mara"]
        npc.trust = 4
        npc.facts.append(Fact("lied_to", "claimed to be family", "I'm Rook's sister"))
        legal = rules.legal_actions(state, "mara")
        self.assertNotIn("reveal_clue", legal["actions"])
        self.assertNotIn("commit", legal["actions"])

    def test_kindness_lowers_threshold(self):
        state = GameState()
        state.npcs["mara"].trust = 3
        state.npcs["mara"].facts.append(Fact("kindness", "covered a stranger's drink", "I'll get it"))
        self.assertIn("reveal_clue", rules.legal_actions(state, "mara")["actions"])

    def test_a_finished_deal_opens_the_clue(self):
        state = GameState()
        state.flags.add("want_done:mara")
        self.assertIn("reveal_clue", rules.legal_actions(state, "mara")["actions"])

    def test_deltas_clamped_per_turn_and_conversation(self):
        state = GameState()
        for _ in range(3):
            rules.apply(state, "mara", proposal(relationship_delta={"trust": 5, "warmth": -5}))
        self.assertEqual((state.npcs["mara"].trust, state.npcs["mara"].warmth), (3, -3))

    def test_reveal_shows_canonical_clue_text(self):
        state = GameState()
        shown = rules.apply(state, "mara", proposal(action="reveal_clue", line="Fine."))
        self.assertEqual(shown, ["Fine.", CLUES["C1"]["line"]])
        self.assertEqual(state.case_board, ["C1"])
        self.assertNotIn("reveal_clue", rules.legal_actions(state, "mara")["actions"])

    def test_memory_list_capped_at_twelve(self):
        state = GameState()
        for i in range(15):
            rules.apply(state, "mara", proposal(memory_note=f"note {i}"))
        memories = state.npcs["mara"].memories
        self.assertEqual(len(memories), 12)
        self.assertEqual(memories[0]["note"], "note 14")


class FallbackTests(unittest.TestCase):
    def test_timeout_falls_back_and_keeps_state(self):
        state = GameState()
        state.npcs["mara"].trust = 1

        def timeout(system, user):
            raise TimeoutError

        result = take_turn(state, "mara", "Where's Rook?", "anthropic", model_fn=timeout)
        self.assertTrue(result.fallback)
        self.assertEqual(result.shown, [FALLBACK_LINES["mara"]["mid"]])
        self.assertEqual(state.npcs["mara"].trust, 1)
        self.assertEqual(state.log[-1]["rejections"], ["error:TimeoutError"])

    def test_bad_json_twice_falls_back(self):
        state = GameState()
        result = take_turn(state, "mara", "hi", "anthropic", model_fn=lambda s, u: ("nope", 10, 5, "test"))
        self.assertTrue(result.fallback)
        self.assertEqual(result.rejections, ["invalid_json", "invalid_json"])

    def test_leaky_line_is_regenerated_with_the_reason(self):
        state = GameState()
        replies = [raw(line="He left at 11:30 with some suit."), raw(line="Not tonight, kid.")]
        seen = []

        def model(system, user):
            seen.append(user)
            return replies[len(seen) - 1], 100, 20, "test"

        result = take_turn(state, "mara", "Who did Rook leave with?", "anthropic", model_fn=model)
        self.assertFalse(result.fallback)
        self.assertEqual(result.shown, ["Not tonight, kid."])
        self.assertEqual(result.rejections, ["unapproved_reveal"])
        self.assertIn("rejected", seen[1])

    def test_persona_stops_holding_back_once_reveal_is_legal(self):
        from after_hours.agent import READY_TO_SHARE, build_context
        state = GameState()
        self.assertNotEqual(build_context(state, "mara", "hi")["you"]["holding_back"], READY_TO_SHARE)
        state.npcs["mara"].trust = 4
        self.assertEqual(build_context(state, "mara", "hi")["you"]["holding_back"], READY_TO_SHARE)

    def test_agent_knows_deals_and_betrayals(self):
        from after_hours.agent import build_context
        state = GameState()
        self.assertNotIn("what_you_know_tonight", build_context(state, "nico", "hi"))
        state.flags.update({"want_done:nico", "mara_exposed"})
        notes = build_context(state, "nico", "hi")["what_you_know_tonight"]
        self.assertTrue(any("owe them" in n for n in notes))
        self.assertTrue(any("Jun's people" in n for n in notes))
        self.assertNotIn("what_you_know_tonight", build_context(state, "jun", "hi"))

    def test_long_fact_detail_is_trimmed_not_dropped(self):
        fact = {"tag": "lied_to", "detail": "x" * 90, "evidence": "I'm Rook's sister", "contradicts": "K3"}
        out = validate(raw(memory_fact=fact), "mara", LEGAL_BASIC, "I'm Rook's sister.", set())
        self.assertEqual(out["memory_fact"]["tag"], "lied_to")
        self.assertEqual(len(out["memory_fact"]["detail"]), 60)

    def test_clue_text_not_in_context_until_revealed(self):
        state = GameState()
        seen = []
        take_turn(state, "mara", "hi", "anthropic", model_fn=lambda s, u: (seen.append(u) or raw(), 1, 1, "t"))
        self.assertNotIn("grey corp jacket", seen[0])


if __name__ == "__main__":
    unittest.main()
