# After Hours — Project Plan

**Version:** v0.2, November 19, 2026, revised after G1 Braintrust feedback (the game is now a one-night mystery; see GDD Section 17). Initial (G1) version at commit `e29b221`. This plan moves to Asana after the G1 decision; owners, acceptance criteria, dependencies and the full Risk Register follow at G2/G3.
**Owner:** Ava Ferrentino, Producer role. Rows marked *(agent)* are delegated execution; I review and accept them.

## Gate dates (from the syllabus)

| Gate / event | Date | What it needs |
|---|---|---|
| G1 pitch post due | Sun Nov 15, 11:59 p.m. | Recording, deck, Initial GDD and Configuration Document, this plan |
| G1 gate review (in class) | Mon Nov 16 | — |
| G1 decision posted (Approve / Hold) | by Tue Nov 17 | — |
| Two Braintrust replies due | Thu Nov 19, 11:59 p.m. | — |
| G1 graded feedback returned | by Mon Nov 23 | — |
| **G2/G3 recording due** | **Sat Nov 28** | First playable; Initial Playtest Log; scope-lock plan; Update GDD and Configuration Document; updated Risk Register |
| **G2 Prototype + G3 Production (combined review)** | **Mon Nov 30** [the syllabus row's date was cut off where I copied it; confirm] | Braintrust notes |
| G4 Gold recording due | Sat Dec 5 | Gold build |
| **G4 Final / Pre-Launch Review** | **Mon Dec 7** | Final GDD and Configuration Document; harness; Update Playtest Log |
| **G5 Retrospective / Closure; showcase** | **Mon Dec 14** | Final game and AAR; Playtest Log |
| Capstone presentations | Dec 17–23 | Engineering & Design Retrospective, recorded walkthrough, live presentation |

## Goal for the next work cycle

By **Sat Nov 28**, an external player will have played the mystery in both agent and scripted modes, and I will know whether players connect how their night ended to things they said.

The timeline is short: 12 days including Thanksgiving. So **scope decisions come early** (Nov 22), and Thanksgiving is used for the external playtest rather than as a break. Family or friends outside the course count as external players.

## Tasks through G2/G3

| # | Dates | Task | Role | Depends on | Acceptance criteria |
|---|---|---|---|---|---|
| 1 | Mon Nov 16–Tue 17 | Present at G1; read the decision and apply any conditions | Me | — | Conditions copied into this plan |
| 2 | Tue Nov 17 | Set up the project in my course repo; choose the provider and set `COURSE_MODEL`; **decide** the model | Tech Lead *(agent)*, me | 1 | Setup check passes, with one live call logged with latency; decision recorded |
| 3 | Thu Nov 19–Sat 21 | **Experiment 1:** Mara in the console, with persona card, clue C1 withheld until legal, memory notes and facts, schema, validator, line/action consistency check and timeout fallback | Tech Lead, Narrative *(agents)* | 2 | p50/p95 latency and cost per turn logged; `test_validator.py` and `test_consistency.py` pass; `evals/consistency/` 20 cases with 0 unapproved reveals or promises shown; `evals/facts/` 30 labeled messages with ≥ 85% agreement |
| 4 | Thu Nov 19 | Write two Braintrust replies; revise GDD and Configuration Document from my Braintrust feedback | Me, Producer *(agent)* | — | Posted; v0.2 docs pushed |
| 5 | Fri Nov 20 | **Decide:** engine and UI stack (simplest option that runs in a browser) | Me | 3 | Recorded in the GDD |
| 6 | Fri Nov 20–Sat 21 | **Mystery bible:** truth, clues C1–C3 with keyword lists, events E1–E5, endings, plus a second truth variant for the two-mode playtest. Adversarial suite (20 cases); Mara's scripted baseline tree | Narrative, QA *(agents)*, me | 3 | I approve the bible; every relationship band has fallback lines; suite runs with failures recorded |
| 7 | **Sun Nov 22** | **Cut checkpoint** (see triggers below) | Me | 3, 6 | **Done.** Decision recorded below |
| 8 | Sun Nov 22 | **Done Nov 22.** Four-slot night, character setup, case board, events E1–E3 (E4–E5 if on schedule), Jun and Nico personas and baselines, facts and clue gating, mode toggle, four endings and Dawn cards, trace logging | Tech Lead, Narrative *(agents)* | 5, 6, 7 | One full night plays through in both modes and each ending is reachable |
| 9 | Mon Nov 23–Tue 24 | Read G1 feedback; move the plan to Asana; full Risk Register | Producer *(agent)*, me | 1, feedback | Asana tasks have owners and acceptance criteria |
| 10 | Wed Nov 25 | Internal play-through, then an independent QA review | QA *(agent)*, me | 8 | No blocking findings open |
| 11 | Thu Nov 26–Fri 27 | **First external playtest** (at least one player, both modes), plus a BI summary of traces | Me, BI *(agent)* | 10 | Playtest log entry following reader Section 5.9; latency, cost and fallback rate reported |
| 12 | Fri Nov 27–Sat 28 | Update the GDD, Configuration Document and Risk Register; Initial Playtest Log; scope-lock plan; **record the first playable (Sat Nov 28)** | Me, Producer *(agent)* | 11 | All G2/G3 items linked in the post |
| 13 | Mon Nov 30 | G2/G3 review | Me | 12 | — |

After G2/G3, the scope-lock plan (G3) sets the Alpha / Beta / Gold work for the Dec 5 Gold recording.

## Cut triggers (fallbacks with a trigger and an action)

- If Experiment 1 shows **p95 above 4 s**, or the validator rejects **more than 10%** of live turns, by **Nov 22**: switch to suggested replies only, and reduce to **two NPCs**.
- If Mara's baseline tree or the mystery bible is not done by **Nov 22**: drop events E4–E5. *(Fired Nov 22; overridden, see result below. Backstop: Nov 24.)*
- If `evals/facts/` agreement is below **85%** by Nov 22: create facts only from tagged suggested replies in both modes, and test agent mode on dialogue and callbacks only (this weakens the hypothesis; record it).
- If two NPCs aren't playable by **Nov 24**: drop Nico; Jun holds C3.
- If one full night doesn't play through in both modes by **Nov 25**: test with Mara alone in both modes on Thanksgiving, and keep the rest for G4.
- If spending reaches **$5** before the playtests: freeze live evaluation and rerun only failed cases.

## Cut checkpoint result (Nov 22)

**Evidence:** Experiment 1 run 1 ([write-up](experiments/EXPERIMENT_1.md)): p95 2.23 s, fallback 2%, 0 rejections, 0 unapproved reveals or promises, 90% fact agreement, about $0.024 per session. No technical trigger fired.

**Schedule trigger fired:** the mystery bible and Mara's baseline tree were not done by Nov 22 (Experiment 1 itself ran 2 days late), which under the rule above means dropping E4–E5.

**[DECISION, Nov 22, Creative Director]: keep everything** (three NPCs and events E1–E5), overriding the schedule trigger. The Producer role recommended cutting E4–E5; I chose to keep them because the experiment showed the agent loop works, which was the main risk.

**Backstop:** if E4–E5 aren't playable in the full night by **Tue Nov 24**, they're cut then, with no further review, so the Nov 25 play-through and Thanksgiving playtest stay on schedule.

## Scope lock (Nov 23) and the last five days

**What happened Nov 22:** the full night was built, then redesigned after my own play-through found it not fun (v0.3: wants and deals, deduction, Sallow's hunt; GDD Section 6A), then given its final look (neon-deco UI, ambient sound, Rook's phone). That was the right call for the hypothesis and the playtest, but it is the last design change before G2/G3.

**Slip (Nov 26):** tasks 13–14 ran three days late (nothing was committed Nov 23–25). Task 15 moves to Fri Nov 27 alongside the playtest log; task 16 (internal play-through) is folded into today's agent-mode night.

**[DECISION, Nov 23]: feature freeze.** From Nov 23 only bug fixes, Variant B, agent-mode fixes, docs and the playtest. No new mechanics, events, characters or UI features until after the G2/G3 review.

| # | Dates | Task | Acceptance criteria |
|---|---|---|---|
| 13 | Mon Nov 23 → **done Nov 26** | **Agent-mode check against v0.3** (agent context knows deals and the Mara betrayal; Experiment 1 rerun with updated thresholds; one full night in agent mode with Vertex) | Experiment rerun passes Nov 22 criteria; no blocking bugs in a full agent-mode night. **Result:** run 3 passes every criterion (EXPERIMENT_1.md); found and fixed a silent all-fallback mode when settings are missing |
| 14 | Mon Nov 23–Tue 24 → **done Nov 26** | **Truth Variant B** (different hideout and clue holders) for the second night of the two-mode playtest | Both variants play through to every ending in tests. **Result:** done (`--truth B`); clue holders and villain name kept, deviation logged in MYSTERY_BIBLE 8a |
| 15 | Tue Nov 24 | Configuration Document and Risk Register updated for v0.3; plan moved to Asana | Docs match the build |
| 16 | Wed Nov 25 | Internal play-through, both modes; bug fixes only | No blocking bugs |
| 17 | Thu Nov 26–Fri 27 | **External playtest** (1+ players outside the course, one night per mode, order alternated) and Initial Playtest Log | Log entry per reader Section 5.9 |
| 18 | Sat Nov 28 | Record the G2/G3 walkthrough | Posted with all links |

**Post-G3 ideas (parked, not cut):** NPC expressions from the agent's emotion field; more events; a second night; player-made characters; desktop-pet rewards (Braintrust #4); more sound design.

## Risk Profile (summary; the full Register comes at G2/G3)

| Dimension | Rating | Evidence | Mitigation |
|---|---|---|---|
| IP / Concept | Medium | The pitch leans on big commercial IPs (GTA, Cyberpunk, Sims), and "complete freedom" was vague until rescoped | Original setting, names and art; attribution table in GDD Section 13; borrow mechanics and tone only |
| Business / Audience | Medium | Open-world fans may expect an open world; there are no playtests yet; classmates and family are reachable | Set expectations in the playtest intro ("one night, three people"); recruit players over Thanksgiving |
| **Technology** | **High** | LLM latency, memory consistency, secret leaks and injection resistance are all unmeasured | Experiment 1 by Nov 20; validator plus `legal_actions`; scripted fallback; 20-case adversarial suite |
| Team | Medium | Solo project; production agents are planned, not configured; review time is limited | Configure Tech Lead, QA and Narrative first; independent reviewer agent; I merge |
| Genre / Mechanics | Medium | v0.2 adds a goal, events and endings (fixing the G1 "no objective" concern) but clue thresholds and pacing over four slots are untested | Internal play-through Nov 25; balance goals in GDD Section 11 |
| **Timeline** | **High** | 9 days to a first playable, including Thanksgiving; v0.2 adds writing (mystery bible, five events, four endings, a second truth variant); every NPC is written twice | Baseline doubles as the fallback; cut checkpoint on Nov 22; two-NPC and Mara-only fallback scopes |

**Do the High ratings share a cause?** Yes. Both depend on the same unproven piece: the NPC agent loop. If it is slow or inconsistent, the technology fails, and the schedule slips while I fix it. Experiment 1 (task 3) tests that piece first, and the Nov 22 checkpoint turns the result into a scope decision. The deeper root cause, the original open-world ambition, is already addressed by the rescope.
