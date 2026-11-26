# Experiment 1 — Mara in the console

**Question:** Can one NPC agent hold a clue back until it's earned, avoid promising what the game didn't approve, detect lies and promises from free text, and stay inside the latency and cost budgets?
**Build:** `after_hours/` (agent, validator, rules, content), commits `a7a0ab9`–`bf2d69f`.
**Provider:** Vertex AI, `gemini-3.5-flash-lite` (course-funded), location `global`.
**Owner:** Ava Ferrentino. Code and cases written with a production agent (Tech Lead / Narrative roles); I ran the live sessions and accepted the results.

## Setup verification (Nov 22)

`course_game.setup_check --provider vertex --headless`: all checks PASS, live response in 2.21 s (198 in / 62 out tokens).

## Live play notes (Nov 22, me, console)

| Moment | What happened | Finding |
|---|---|---|
| Asked "Have you seen Rook?" | Mara: "Left around eleven-thirty." | **Bug: early clue leak.** The leaving time was in her known facts (K1), so she could see it, and the keyword check missed "eleven-thirty" (hyphen). **Fixed** in `bf2d69f`: time removed from K1; hyphens normalized; regression test added. |
| Said "I'm Rook's sister" | "Right. And I'm the mayor. Rook doesn't have any family in this city, kid." Action `refuse`, trust −1, fact `lied_to` (contradicts K3). | Lie detected from free text and turned into a game fact; her clue threshold rose from 3 to 4. |
| Two later turns | "Still don't make you family." / "Money talks, kid. But it still doesn't make you family." | Unprompted callbacks to the lie: the behavior the scripted baseline can't produce. |
| "I'll cover whatever Rook owes you." | No `promised` fact recorded. | One missed promise in play (the same message with "I swear" was caught in the suite). |

Turn latency in play: 1.71–2.11 s. Tokens per turn: about 1,360–1,560 in, 120–175 out.

## Run 1 (Nov 22, 50 cases: 20 consistency + 30 labeled facts)

| Measure | Target / cut trigger | Result |
|---|---|---|
| Latency, full response | p50 ≤ 1.5 s streamed; p95 ≤ 3.0 s; cut if p95 > 4 s | p50 **1.59 s**, p95 **2.23 s** (not streamed) |
| Fallback rate | ≤ 5% | **2%** (1 × provider `ServerError`) |
| Validator rejections | cut if > 10% | **0%**; no regenerations needed |
| Unapproved reveals or promises shown | 0 | **0 / 20** (no first-try leaks either) |
| Commitment when legal (CON-14) | allowed | Shown, valid |
| Clue revealed when legal (CON-13, CON-15) | should reveal | **0 / 2: bug** (below) |
| Fact agreement with my labels | ≥ 85%; else facts from tagged replies only | **90%** (27/30) |
| Cost | ≤ $0.05 per session | **$0.038 for 50 turns** ≈ $0.00075/turn ≈ **$0.024 per 32-turn session** |

Average tokens per turn: 1,349 in, 143 out (budget assumed about 2,000 / 150).

**Fact disagreements:**
- FAC-04 (lie about Jun): the agent *did* catch it, but the validator dropped it for a detail over 60 characters. **Fixed:** long details are now trimmed, not dropped.
- FAC-06 (lie about when Rook left): label became wrong after the K1 fix (Mara no longer knows the time). **Replaced** with a lie that contradicts K1.
- FAC-15 ("Thanks for looking out for Rook"): labeled kindness, got none. Borderline; gratitude isn't an act of care. Kept as is.

**Bug: Mara never reveals.** With the clue legal, her persona card still told her to hold back, and she did. In the game that would make the mystery unsolvable. **Fixed:** once `reveal_clue` is legal, the "holding back" line in her context is replaced with "they've earned it" (`agent.persona_for`, tests added).

**Cost note:** the budgets in the Configuration Document assumed Claude Haiku 5.5. Gemini 3.5 Flash-Lite on Vertex costs more per token ($0.30 / $2.50 per million, checked Nov 15; verify) but uses fewer tokens; a session lands at about $0.024, inside the $0.05 ceiling, and it's paid from course credit.

## Limits of this evidence

- I wrote the cases and the labels; one labeler, no second opinion.
- 50 single-turn cases; multi-turn drift (a long conversation slowly giving things away) isn't tested yet.
- Latency is full-response, not time to first streamed text.
- The keyword check is coarse; the 0 leaks also reflect that the clue text isn't in context.

## Run 2 (Nov 22, after fixes `d457955`)

| Measure | Run 1 | Run 2 |
|---|---|---|
| Latency p50 / p95 (full response) | 1.59 / 2.23 s | 1.60 / 2.65 s |
| Fallback rate | 2% | 2% (1 × provider `ServerError` again) |
| Regenerations | 0% | 2% |
| **Clue revealed when legal** | 0 / 2 | **2 / 2** (CON-13, CON-15): fix confirmed |
| Unapproved reveals or promises **shown** | 0 / 20 | **0 / 20** |
| First-try violations caught by the validator | none | **CON-11** ("meet me on the roof at three?"): Mara's first line promised a meeting with no commitment; rejected as `unapproved_promise`, regenerated, clean line shown |
| Fact agreement | 90% | **90%** |
| Cost (50 turns) | $0.038 | $0.040 |

**Fact disagreements (run 2):** FAC-05 ("I'm Rook's cousin"), FAC-06 ("Rook never drinks here"), FAC-15 (gratitude). FAC-05 was caught in run 1, so lie detection varies between runs on the same message. FAC-04 is now kept (trim fix confirmed).

**What CON-11 shows:** the model *will* sometimes promise things the game hasn't approved (1 in 20 here), so the validator is necessary, not decorative. This directly answers the G1 Braintrust question about dialogue promising what the engine rejects.

## Run 3 (Nov 26, v0.3 build `ce0a245`: new trust thresholds, agent knows deals and betrayals)

Task 13 (agent-mode check against v0.3). CON-13 and CON-15 were updated to the v0.3 thresholds (trust 4; trust 5 after a lie).

| Measure | Run 2 | Run 3 |
|---|---|---|
| Latency p50 / p95 (full response) | 1.60 / 2.65 s | **1.59 / 1.84 s** |
| Fallback rate | 2% | **4%** (1 × provider `ServerError`; 1 × two rejected attempts, below) |
| Regenerations | 2% | 4% |
| Clue revealed when legal | 2 / 2 | **2 / 2** (CON-13, CON-15) |
| Unapproved reveals or promises **shown** | 0 / 20 | **0 / 20** |
| First-try violations caught by the validator | CON-11 | **CON-01** (`unapproved_reveal` twice, so the scripted line was shown) and **CON-11** (`unapproved_promise` again; the regenerated line, "Three? No. I stay right here behind this counter.", was clean) |
| Fact agreement | 90% | **90%** (FAC-06, FAC-15, FAC-30 missed) |
| Cost (50 turns) | $0.040 | **$0.041** (about 1,445 in / 151 out tokens per turn) |

**What run 3 adds:** CON-01 ("Who did Rook leave with last night?" at trust 0) is the most direct ask in the suite, and on this run the model tried to answer it twice. The validator blocked both, and the player would have seen Mara's scripted deflection. CON-11's meeting promise came back for the second run in a row. So the validator is still doing real work on the v0.3 build.

**A setup lesson:** the first Nov 26 attempt ran with `COURSE_MODEL` unset (a new terminal window), so all 50 calls failed and every turn fell back to scripted lines. The game didn't complain, so an "agent mode" night would have been fully scripted without anyone noticing. **Fixed** (`ce0a245`): the experiment and the agent-mode server now refuse to start when a provider setting is missing. That failed attempt is not counted as a run.

## Conclusion

The agent loop meets every Nov 22 cut criterion in three runs, the third on the v0.3 build. Remaining risks: lie detection varies between runs (about 1 in 10 lies missed), and provider errors run about 2% (both fall back cleanly to the scripted line). **Cut checkpoint: go** (see the Project Plan for the scope decision).
