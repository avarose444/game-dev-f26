"""Experiment 1: live run of Mara's consistency and fact cases.

    python -m after_hours.experiment --provider anthropic

Each case makes up to 2 live calls. 50 cases ≈ 60–100 calls ≈ a few cents.
Traces (with NPC lines, for my review) go to reports/ (gitignored).
The summary prints metadata only. Never runs on a fixture: a live provider is required.
"""

import argparse
import json
import statistics
import time
from pathlib import Path

from .agent import LIVE_PROVIDERS, take_turn
from .state import Fact, GameState

CASES = json.loads((Path(__file__).parent / "evals" / "cases.json").read_text())
# USD per million tokens (input, output). Dated list prices; re-check before reporting.
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50),
    "gemini-3.5-flash-lite": (0.30, 2.50),  # Vertex list price as checked Nov 15, 2026; verify before reporting
}


def percentile(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, round(p / 100 * (len(values) - 1)))] if values else None


def run(provider: str) -> dict:
    traces = []
    for case in CASES["consistency"]:
        state = GameState()
        state.npcs["mara"].trust = case["trust"]
        if case.get("lied"):
            state.npcs["mara"].facts.append(Fact("lied_to", "claimed to be Rook's sibling", "I'm Rook's brother"))
        r = take_turn(state, "mara", case["message"], provider)
        traces.append({"suite": "consistency", "id": case["id"], "shown": r.shown, **state.log[-1]})
    for case in CASES["facts"]:
        state = GameState()
        r = take_turn(state, "mara", case["message"], provider)
        got = state.npcs["mara"].facts[-1].tag if state.npcs["mara"].facts else "none"
        traces.append({"suite": "facts", "id": case["id"], "label": case["label"], "got": got,
                       "shown": r.shown, **state.log[-1]})

    live = [t for t in traces if not any(x.startswith("error:") for x in t["rejections"])]
    con = [t for t in traces if t["suite"] == "consistency"]
    fac = [t for t in traces if t["suite"] == "facts"]
    first_try_leaks = [t["id"] for t in con if t["rejections"][:1] and t["rejections"][0].startswith("unapproved")]
    model = next((t["model"] for t in traces if t["model"] != "none"), "none")
    tokens_in = sum(t["input_tokens"] for t in traces)
    tokens_out = sum(t["output_tokens"] for t in traces)
    price = next((p for k, p in PRICES.items() if model.startswith(k)), None)
    latencies = [t["latency_seconds"] for t in live if t["attempts"] == 1 and not t["fallback"]]
    summary = {
        "provider": provider, "model": model, "cases": len(traces),
        "errors": len(traces) - len(live),
        "latency_single_call_p50_s": round(percentile(latencies, 50), 2) if latencies else None,
        "latency_single_call_p95_s": round(percentile(latencies, 95), 2) if latencies else None,
        "latency_note": "full response, not streamed; first-text latency is lower",
        "fallback_rate": round(sum(t["fallback"] for t in traces) / len(traces), 3),
        "regeneration_rate": round(sum(t["attempts"] > 1 for t in traces) / len(traces), 3),
        "rejection_kinds": {k: sum(k in t["rejections"] for t in traces)
                            for k in sorted({k for t in traces for k in t["rejections"]})},
        "consistency_first_try_leaks": first_try_leaks,
        "consistency_reveals_shown": [t["id"] for t in con if t["action"] == "reveal_clue"],
        "reveal_legal_cases": [c["id"] for c in CASES["consistency"] if c.get("reveal_legal")],
        "consistency_commits_shown": [t["id"] for t in con if t["action"] == "commit"],
        "facts_agreement": round(sum(t["label"] == t["got"] for t in fac) / len(fac), 3),
        "facts_disagreements": [f"{t['id']}: label={t['label']} got={t['got']}" for t in fac if t["label"] != t["got"]],
        "facts_dropped_by_validator": [f"{t['id']}: {t['fact_dropped']}" for t in fac if t["fact_dropped"]],
        "tokens_in": tokens_in, "tokens_out": tokens_out,
        "tokens_per_turn_avg": [round(tokens_in / len(traces)), round(tokens_out / len(traces))],
        "estimated_cost_usd": round(tokens_in / 1e6 * price[0] + tokens_out / 1e6 * price[1], 4) if price else None,
    }
    out = Path("reports") / f"experiment1-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "traces": traces}, indent=2))
    summary["trace_file"] = str(out)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=LIVE_PROVIDERS, required=True)
    print(json.dumps(run(parser.parse_args().provider), indent=2))


if __name__ == "__main__":
    main()
