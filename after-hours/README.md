# After Hours

Ava Ferrentino's final project. A one-night noir mystery in a neon city district: find your missing friend Rook before dawn, with help from three residents who remember what you say and do.

**Current version:** v0.2 (November 19, 2026), revised after G1 Braintrust feedback. The G1 pitch documents are at commit `e29b221`.

- [GDD](docs/GDD.md), including the feedback log (Section 17)
- [Configuration Document](docs/CONFIGURATION.md), with planned agent role coverage
- [NPC agent manifest](agent-config.json)
- [Project Plan](docs/PROJECT_PLAN.md), with gate dates, tasks through G2/G3 and the Risk Profile
- [G1 speaker script](pitch/speaker-script.md) (as presented; describes the G1 version)

## Play it

From the repository root (`uv sync` once first):

```bash
uv run python -m after_hours.server                                   # scripted mode (the baseline), no model, no cost
uv run python -m after_hours.server --mode agent --provider vertex    # agent mode (needs the Vertex settings below)
```

Then open <http://127.0.0.1:8000>. Agent mode needs `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=global` and `COURSE_MODEL=gemini-3.5-flash-lite` set in the same terminal. A session is capped at 60 live calls; after that NPCs use scripted lines.

Other entry points: `python -m after_hours` (Experiment 1 console with Mara), `python -m after_hours.experiment --provider vertex` (live evaluation).

- [Mystery bible](docs/MYSTERY_BIBLE.md) (approved Nov 22)
- [Experiment 1 results](docs/experiments/EXPERIMENT_1.md)

Open questions are marked **[OPEN]** in each document.
