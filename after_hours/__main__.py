"""Console conversation with Mara (Experiment 1).

    python -m after_hours                        # scripted mode: no model, no cost
    python -m after_hours --provider anthropic   # live: needs ANTHROPIC_API_KEY and COURSE_MODEL
"""

import argparse

from .agent import LIVE_PROVIDERS, take_turn
from .content import CLUES, OPENING_LINES, SUGGESTED_REPLIES
from .state import GameState

LIVE_CALL_LIMIT = 60  # per session (agent-config.json limits)


def scripted_model(system, user):
    """Scripted mode: always fails over to the authored fallback line. No model call."""
    raise RuntimeError("scripted mode")


def main() -> None:
    parser = argparse.ArgumentParser(description="After Hours: talk to Mara at the Lantern")
    parser.add_argument("--provider", choices=["scripted", *LIVE_PROVIDERS], default="scripted")
    parser.add_argument("--debug", action="store_true", help="Show meters, facts and validator results")
    args = parser.parse_args()

    state, calls = GameState(), 0
    print("AFTER HOURS — The Lantern, midnight. Rook is missing.")
    print("Type to talk, 1-3 for a suggested reply, 'quit' to leave.\n")
    print(OPENING_LINES["mara"])
    while True:
        for i, reply in enumerate(SUGGESTED_REPLIES["mara"], 1):
            print(f"  {i}. {reply}")
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() == "quit":
            break
        if text in ("1", "2", "3"):
            text = SUGGESTED_REPLIES["mara"][int(text) - 1]
        if not text:
            continue
        model_fn = scripted_model if args.provider == "scripted" or calls >= LIVE_CALL_LIMIT else None
        calls += model_fn is None
        print("  Mara is typing…")
        before = (state.npcs["mara"].next_memory_id, len(state.npcs["mara"].facts))
        result = take_turn(state, "mara", text, args.provider, model_fn=model_fn)
        for line in result.shown:
            print(line)
        if result.action == "reveal_clue":
            print(f"  [Case board: {CLUES[state.npcs['mara'].revealed_clue]['title']}]")
        npc = state.npcs["mara"]
        if len(npc.facts) > before[1]:
            print(f"  [Mara will hold you to that: {npc.facts[-1].tag}]")
        elif npc.next_memory_id > before[0]:
            print("  [Mara will remember that.]")
        if args.debug:
            print(f"  [debug] trust={npc.trust} warmth={npc.warmth} facts={[f.tag for f in npc.facts]} "
                  f"action={result.action} fallback={result.fallback} rejections={result.rejections} "
                  f"fact_dropped={result.fact_dropped} {result.latency_seconds:.2f}s "
                  f"tokens={result.input_tokens}/{result.output_tokens} model={result.model}")
        if result.action == "end_conversation":
            break
    print("\nYou step back out into the neon.")


if __name__ == "__main__":
    main()
