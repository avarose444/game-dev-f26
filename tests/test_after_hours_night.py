"""Deterministic tests for the full night: events, clue routes, finale and endings."""

import json
import unittest

from after_hours.night import Night
from after_hours.state import Fact


def scripted_night() -> Night:
    return Night("scripted")


def option(night: Night, tag_text: str) -> int:
    return next(i for i, o in enumerate(night.options()) if o.startswith(tag_text))


def skip_slot(night: Night, location: str = "clinic") -> None:
    night.visit(location)
    while night.phase == "event":
        night.choose_event(next(iter(night.current_event()["choices"])))
    if night.phase == "talk":
        night.leave()


class NightFlowTests(unittest.TestCase):
    def test_four_slots_then_dawn(self):
        night = scripted_night()
        for _ in range(4):
            skip_slot(night, "rooftop")
        self.assertEqual(night.phase, "dawn")
        self.assertEqual(night.ending, "last_call")

    def test_lift_needs_two_clues_at_three(self):
        night = scripted_night()
        for _ in range(3):
            skip_slot(night, "rooftop")
        self.assertEqual(night.state.slot, "3am")
        self.assertNotIn("lift", night.locations())
        night2 = scripted_night()
        night2.state.case_board = ["C1", "C3"]
        for _ in range(3):
            skip_slot(night2, "rooftop")
        self.assertIn("lift", night2.locations())

    def test_conversation_capped_at_six_exchanges(self):
        night = scripted_night()
        night.visit("rooftop")
        for _ in range(6):
            night.choose_option(1)
        self.assertEqual(night.state.slot, "1am")
        self.assertEqual(night.phase, "choose_location")


class EventTests(unittest.TestCase):
    def test_e1_cover_trades_for_c1(self):
        night = scripted_night()
        night.visit("lantern")
        night.choose_event("cover")
        self.assertEqual(night.state.credits, 15)
        night.choose_option(0)
        self.assertIn("C1", night.state.case_board)

    def test_e2_punch_closes_the_lantern_and_ends_visit(self):
        night = scripted_night()
        skip_slot(night, "rooftop")
        night.visit("lantern")
        night.choose_event("punch")
        self.assertEqual(night.state.slot, "2am")
        self.assertNotIn("lantern", night.locations())
        self.assertEqual(night.state.npcs["nico"].trust, 2)

    def test_flirting_in_front_of_nico_locks_c3(self):
        night = scripted_night()
        skip_slot(night, "rooftop")
        night.visit("lantern")
        night.choose_event("stay_out")
        night.choose_option(option(night, "Your eyes"))
        self.assertIn("nico_knows_flirt", night.state.flags)
        night.leave()
        night.state.npcs["nico"].trust = 5
        night.visit("clinic")
        night.choose_event("leave")       # E3 at 2am, didn't help
        night.choose_option(0)
        self.assertNotIn("C3", night.state.case_board)

    def test_e3_help_gives_c3_even_after_flirt_and_uses_the_hour(self):
        night = scripted_night()
        night.state.flags.add("nico_knows_flirt")
        skip_slot(night, "rooftop")
        skip_slot(night, "rooftop")
        night.visit("clinic")
        night.choose_event("help")
        self.assertIn("C3", night.state.case_board)
        self.assertEqual(night.state.slot, "3am")

    def test_e4_fires_after_asking_openly_twice(self):
        night = scripted_night()
        night.visit("rooftop")
        night.choose_option(option(night, "HEY"))
        night.leave()
        night.visit("clinic")
        night.choose_option(option(night, "ROOK!"))
        night.leave()
        night.visit("rooftop")            # 2am, Jun trust is low: no one hides you
        self.assertEqual(night.current_event()["id"], "E4")
        self.assertEqual(list(night.current_event()["choices"]), ["walk"])
        night.choose_event("walk")
        self.assertIn("tail_on_you", night.state.flags)

    def test_e4_hide_offered_when_trusted(self):
        night = scripted_night()
        night.state.npcs["mara"].facts.append(Fact("asked_openly", "", "x"))
        night.state.npcs["jun"].facts.append(Fact("asked_openly", "", "x"))
        night.state.npcs["mara"].trust = 2
        skip_slot(night, "rooftop")
        skip_slot(night, "rooftop")
        night.visit("lantern")
        self.assertEqual(list(night.current_event()["choices"]), ["hide"])

    def test_e5_needs_a_promise_to_jun(self):
        night = scripted_night()
        skip_slot(night, "clinic")
        night.visit("rooftop")
        self.assertIsNone(night.current_event())
        night.choose_option(option(night, "I'll get back"))
        night.leave()
        night.visit("rooftop")
        self.assertEqual(night.current_event()["id"], "E5")
        night.choose_event("watch")
        self.assertIn("C1", night.state.case_board)


class EndingTests(unittest.TestCase):
    def at_lift(self, **flags) -> Night:
        night = scripted_night()
        night.state.case_board = ["C1", "C2"]
        for flag in flags.get("flags", []):
            night.state.flags.add(flag)
        for npc, trust in flags.get("trust", {}).items():
            night.state.npcs[npc].trust = trust
        for npc, tag in flags.get("facts", []):
            night.state.npcs[npc].facts.append(Fact(tag, "", "x"))
        for _ in range(3):
            skip_slot(night, "rooftop")
        night.visit("lift")
        return night

    def test_keep_the_chip_is_paid_in_full(self):
        night = self.at_lift(facts=[("jun", "promised")])
        night.choose_finale("keep")
        self.assertEqual(night.ending, "paid_in_full")
        self.assertTrue(next(c for c in night.dawn_cards() if c["npc"] == "Jun")["promise_broken"])

    def test_return_with_jun_promise_is_out_by_dawn(self):
        night = self.at_lift(facts=[("jun", "promised")])
        night.choose_finale("return")
        self.assertEqual(night.ending, "out_by_dawn")

    def test_destroy_needs_an_ally(self):
        night = self.at_lift()
        night.choose_finale("destroy")
        self.assertEqual(night.ending, "last_call")
        night = self.at_lift(trust={"nico": 3})
        night.choose_finale("destroy")
        self.assertEqual(night.ending, "out_by_dawn")

    def test_tail_ruins_the_rescue(self):
        night = self.at_lift(trust={"mara": 5}, flags=["tail_on_you"])
        night.choose_finale("destroy")
        self.assertEqual(night.ending, "last_call")

    def test_not_found_after_flirt_is_morning_after(self):
        night = scripted_night()
        night.state.flags.add("nico_knows_flirt")
        for _ in range(4):
            skip_slot(night, "rooftop")
        self.assertEqual(night.ending, "morning_after")


class AgentModeTests(unittest.TestCase):
    def test_agent_mode_uses_the_validated_agent_and_falls_back(self):
        def timeout(system, user):
            raise TimeoutError

        night = Night("agent", model_fn=timeout)
        night.visit("rooftop")
        feed = night.say("What was Rook doing for you?")
        self.assertEqual(feed[-1]["kind"], "npc")
        self.assertEqual(night.state.log[-1]["fallback"], True)

    def test_snapshot_is_json_serializable(self):
        night = scripted_night()
        night.visit("lantern")
        json.dumps(night.snapshot())


if __name__ == "__main__":
    unittest.main()
