"""Deterministic tests for the full night (v0.3): deals, the hunt, deduction, endings."""

import json
import unittest

from after_hours.content import WANT_ASK
from after_hours.night import Night
from after_hours.state import Fact


def scripted_night() -> Night:
    return Night("scripted")


def option(night: Night, start: str) -> int:
    return next(i for i, o in enumerate(night.options()) if o.startswith(start))


def skip_slot(night: Night, location: str = "clinic") -> None:
    night.visit(location)
    while night.phase == "event":
        night.choose_event(next(iter(night.current_event()["choices"])))
    if night.phase == "talk":
        night.leave()


def learn_want(night: Night) -> None:
    night.choose_option(night.options().index(WANT_ASK))


class NightFlowTests(unittest.TestCase):
    def test_four_slots_then_dawn(self):
        night = scripted_night()
        for _ in range(4):
            skip_slot(night, "rooftop")
        self.assertEqual(night.phase, "dawn")
        self.assertEqual(night.ending, "last_call")

    def test_hideouts_only_at_three(self):
        night = scripted_night()
        self.assertEqual(night.hideouts(), [])
        for _ in range(3):
            skip_slot(night, "rooftop")
        self.assertEqual(night.state.slot, "3am")
        self.assertEqual(set(night.hideouts()), {"docks", "cold_storage", "lift"})

    def test_conversation_capped_at_six_exchanges(self):
        night = scripted_night()
        night.visit("rooftop")
        for _ in range(6):
            night.choose_option(0)          # asking about Rook can be repeated
        self.assertEqual(night.state.slot, "1am")

    def test_sallow_gets_closer_every_hour(self):
        night = scripted_night()
        for _ in range(3):
            skip_slot(night, "rooftop")
        self.assertEqual(night.heat, 3)


class DealTests(unittest.TestCase):
    def test_asking_what_it_takes_reveals_the_want_and_deals(self):
        night = scripted_night()
        night.visit("rooftop")
        self.assertEqual(night.deals(), [])
        learn_want(night)
        self.assertIn("jun_promise", [d["id"] for d in night.deals()])

    def test_deal_gives_the_clue_right_away(self):
        night = scripted_night()
        night.visit("rooftop")
        learn_want(night)
        night.make_deal("jun_promise")
        self.assertIn("C2", night.state.case_board)
        self.assertTrue(night.state.npcs["jun"].has_fact("promised"))

    def test_paying_off_the_contractor_slows_sallow(self):
        night = scripted_night()
        night.visit("lantern")
        night.choose_event("ignore")
        learn_want(night)
        night.make_deal("mara_pay")
        self.assertEqual(night.state.credits, 10)
        self.assertIn("C1", night.state.case_board)
        self.assertEqual(night.heat, 0)   # can't go below 0

    def test_bluff_works_early_and_fails_late(self):
        early = scripted_night()
        early.visit("lantern")
        early.choose_event("ignore")
        learn_want(early)
        early.make_deal("mara_bluff")
        self.assertIn("C1", early.state.case_board)

        late = scripted_night()
        late.heat = 3
        late.visit("lantern")
        late.choose_event("ignore")
        learn_want(late)
        late.make_deal("mara_bluff")
        self.assertNotIn("C1", late.state.case_board)
        self.assertEqual(late.heat, 5)

    def test_selling_mara_out_closes_nico(self):
        night = scripted_night()
        night.state.case_board.append("C1")
        night.visit("rooftop")
        learn_want(night)
        night.make_deal("jun_sell")
        self.assertIn("C2", night.state.case_board)
        night.leave()
        night.visit("clinic")
        learn_want(night)
        night.make_deal("nico_swear")
        self.assertNotIn("C3", night.state.case_board)
        self.assertEqual(next(l for l in night.leads() if l["npc"] == "nico")["status"], "closed")

    def test_jun_sell_needs_maras_clue(self):
        night = scripted_night()
        night.visit("rooftop")
        learn_want(night)
        self.assertNotIn("jun_sell", [d["id"] for d in night.deals()])


class EventTests(unittest.TestCase):
    def test_e1_cover_is_kindness(self):
        night = scripted_night()
        night.visit("lantern")
        night.choose_event("cover")
        self.assertEqual(night.state.credits, 15)
        self.assertTrue(night.state.npcs["mara"].has_fact("kindness"))

    def test_e2_words_gets_the_contractor_out(self):
        night = scripted_night()
        skip_slot(night, "rooftop")
        night.visit("lantern")
        night.choose_event("words")
        self.assertTrue(night.want_done("mara"))
        self.assertIn("C1", night.state.case_board)

    def test_e2_punch_closes_the_lantern(self):
        night = scripted_night()
        skip_slot(night, "rooftop")
        night.visit("lantern")
        night.choose_event("punch")
        self.assertEqual(night.state.slot, "2am")
        self.assertNotIn("lantern", night.locations())

    def test_flirting_in_front_of_nico_locks_c3(self):
        night = scripted_night()
        skip_slot(night, "rooftop")
        night.visit("lantern")
        night.choose_event("stay_out")
        night.choose_option(option(night, "Your eyes"))
        self.assertIn("nico_knows_flirt", night.state.flags)

    def test_e3_help_gives_c3_even_when_burned(self):
        night = scripted_night()
        night.state.flags.add("mara_exposed")
        skip_slot(night, "rooftop")
        skip_slot(night, "rooftop")
        night.visit("clinic")
        night.choose_event("help")
        self.assertIn("C3", night.state.case_board)

    def test_e4_fires_when_sallow_is_close(self):
        night = scripted_night()
        night.visit("rooftop")
        night.choose_option(option(night, "HEY"))      # asked openly: heat +1
        night.leave()                                   # +1
        skip_slot(night, "rooftop")                     # +1 -> 3
        night.visit("rooftop")
        self.assertEqual(night.current_event()["id"], "E4")
        night.choose_event("walk")
        self.assertEqual(night.heat, 5)

    def test_e5_needs_a_promise_to_jun(self):
        night = scripted_night()
        night.visit("rooftop")
        learn_want(night)
        night.make_deal("jun_promise")
        night.leave()
        night.visit("rooftop")
        self.assertEqual(night.current_event()["id"], "E5")
        night.choose_event("watch")
        self.assertIn("E5", night.state.case_board)


class EndingTests(unittest.TestCase):
    def at_three(self, heat=None, flags=(), trust=None) -> Night:
        night = scripted_night()
        for _ in range(3):
            skip_slot(night, "rooftop")
        if heat is not None:
            night.heat = heat
        night.state.flags.update(flags)
        for npc, value in (trust or {}).items():
            night.state.npcs[npc].trust = value
        return night

    def test_wrong_hideout_is_last_call(self):
        night = self.at_three()
        night.visit("docks")
        self.assertEqual(night.ending, "last_call")

    def test_keep_the_chip_is_paid_in_full(self):
        night = self.at_three(flags={"want_done:jun"})
        night.visit("lift")
        night.choose_finale("keep")
        self.assertEqual(night.ending, "paid_in_full")
        self.assertTrue(next(c for c in night.dawn_cards() if c["npc"] == "Jun")["promise_broken"])

    def test_return_with_jun_deal_is_out_by_dawn(self):
        night = self.at_three(flags={"want_done:jun"})
        night.visit("lift")
        night.choose_finale("return")
        self.assertEqual(night.ending, "out_by_dawn")

    def test_destroy_needs_an_ally(self):
        night = self.at_three()
        night.visit("lift")
        night.choose_finale("destroy")
        self.assertEqual(night.ending, "last_call")
        night = self.at_three(trust={"nico": 3})
        night.visit("lift")
        night.choose_finale("destroy")
        self.assertEqual(night.ending, "out_by_dawn")

    def test_sallow_at_the_lift_without_allies(self):
        night = self.at_three(heat=5)
        night.visit("lift")
        self.assertEqual(night.ending, "last_call")

    def test_sallow_at_the_lift_with_an_ally(self):
        night = self.at_three(heat=5, flags={"want_done:mara"})
        night.visit("lift")
        self.assertEqual(night.phase, "finale")

    def test_not_found_after_flirt_is_morning_after(self):
        night = scripted_night()
        night.state.flags.add("nico_knows_flirt")
        for _ in range(4):
            skip_slot(night, "rooftop")
        self.assertEqual(night.ending, "morning_after")


class GuidanceTests(unittest.TestCase):
    def test_used_menu_options_disappear(self):
        night = scripted_night()
        night.visit("rooftop")
        night.choose_option(option(night, "I'll get back"))
        self.assertFalse(any(o.startswith("I'll get back") for o in night.options()))

    def test_trust_ticks_and_fact_cue_are_shown(self):
        night = scripted_night()
        night.visit("rooftop")
        feed = night.choose_option(option(night, "I'll get back"))
        texts = [m["text"] for m in feed if m["kind"] == "system"]
        self.assertIn("Jun: trust +2", texts)
        self.assertIn("Jun will hold you to that promise.", texts)

    def test_agent_suggestions_rotate_and_want_is_learned(self):
        def timeout(system, user):
            raise TimeoutError
        night = Night("agent", model_fn=timeout)
        night.visit("rooftop")
        first = night.options()
        night.say(first[-1])
        self.assertNotIn(first[-1], night.options())
        night.say(WANT_ASK)
        self.assertIn("jun", night.want_known)


class AgentModeTests(unittest.TestCase):
    def test_agent_mode_uses_the_validated_agent_and_falls_back(self):
        def timeout(system, user):
            raise TimeoutError
        night = Night("agent", model_fn=timeout)
        night.visit("rooftop")
        feed = night.say("What was Rook doing for you?")
        self.assertTrue(any(m["kind"] == "npc" for m in feed))
        self.assertTrue(night.state.log[-1]["fallback"])

    def test_snapshot_is_json_serializable(self):
        night = scripted_night()
        night.visit("lantern")
        json.dumps(night.snapshot())


if __name__ == "__main__":
    unittest.main()
