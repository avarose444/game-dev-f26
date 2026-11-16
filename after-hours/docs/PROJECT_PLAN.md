# After Hours — Initial Project Plan

**Version:** Initial (G1), November 15, 2026. This plan moves to Asana after the G1 decision; owners, acceptance criteria, dependencies and the full Risk Register follow at G2/G3.
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

By **Sat Nov 28**, an external player will have played one night in both agent and scripted modes, and I will know whether remembered callbacks change how players treat the NPCs.

The timeline is short: 12 days including Thanksgiving. So **scope decisions come early** (Nov 22), and Thanksgiving is used for the external playtest rather than as a break. Family or friends outside the course count as external players.

## Tasks through G2/G3

| # | Dates | Task | Role | Depends on | Acceptance criteria |
|---|---|---|---|---|---|
| 1 | Mon Nov 16–Tue 17 | Present at G1; read the decision and apply any conditions | Me | — | Conditions copied into this plan |
| 2 | Tue Nov 17 | Set up the project in my course repo; choose the provider and set `COURSE_MODEL`; **decide** the model | Tech Lead *(agent)*, me | 1 | Setup check passes, with one live call logged with latency; decision recorded |
| 3 | Wed Nov 18–Fri 20 | **Experiment 1:** one NPC (Mara) in the console, with persona card, memory list, schema, validator and timeout fallback | Tech Lead, Narrative *(agents)* | 2 | 20 scripted conversations run; p50/p95 latency and cost per turn logged; `test_validator.py` passes 15/15 |
| 4 | Thu Nov 19 | Write two Braintrust replies | Me | — | Posted |
| 5 | Fri Nov 20 | **Decide:** engine and UI stack (simplest option that runs in a browser) | Me | 3 | Recorded in the GDD |
| 6 | Fri Nov 20–Sat 21 | Adversarial suite: 20 cases (injection, unwitnessed facts, secret leak, persona break); Mara's scripted baseline tree | QA, Narrative *(agents)* | 3 | Suite runs with failures recorded; every relationship band has fallback lines |
| 7 | **Sun Nov 22** | **Cut checkpoint** (see triggers below) | Me | 3, 6 | Go / cut decision recorded |
| 8 | Sun Nov 22–Tue 24 | Night structure, character setup, Jun and Nico personas and baselines, mode toggle, Dawn ending, trace logging | Tech Lead, Narrative *(agents)* | 5, 7 | One full night plays through in both modes |
| 9 | Mon Nov 23–Tue 24 | Read G1 feedback; move the plan to Asana; full Risk Register | Producer *(agent)*, me | 1, feedback | Asana tasks have owners and acceptance criteria |
| 10 | Wed Nov 25 | Internal play-through, then an independent QA review | QA *(agent)*, me | 8 | No blocking findings open |
| 11 | Thu Nov 26–Fri 27 | **First external playtest** (at least one player, both modes), plus a BI summary of traces | Me, BI *(agent)* | 10 | Playtest log entry following reader Section 5.9; latency, cost and fallback rate reported |
| 12 | Fri Nov 27–Sat 28 | Update the GDD, Configuration Document and Risk Register; Initial Playtest Log; scope-lock plan; **record the first playable (Sat Nov 28)** | Me, Producer *(agent)* | 11 | All G2/G3 items linked in the post |
| 13 | Mon Nov 30 | G2/G3 review | Me | 12 | — |

After G2/G3, the scope-lock plan (G3) sets the Alpha / Beta / Gold work for the Dec 5 Gold recording.

## Cut triggers (fallbacks with a trigger and an action)

- If Experiment 1 shows **p95 above 4 s**, or the validator rejects **more than 10%** of live turns, by **Nov 22**: switch to suggested replies only, and reduce to **two NPCs**.
- If Mara's baseline tree is not done by **Nov 22**: drop Nico and use four time slots.
- If one full night doesn't play through in both modes by **Nov 25**: test with Mara alone in both modes on Thanksgiving, and keep the rest for G4.
- If spending reaches **$5** before the playtests: freeze live evaluation and rerun only failed cases.

## Risk Profile (summary; the full Register comes at G2/G3)

| Dimension | Rating | Evidence | Mitigation |
|---|---|---|---|
| IP / Concept | Medium | The pitch leans on big commercial IPs (GTA, Cyberpunk, Sims), and "complete freedom" was vague until rescoped | Original setting, names and art; attribution table in GDD Section 13; borrow mechanics and tone only |
| Business / Audience | Medium | Open-world fans may expect an open world; there are no playtests yet; classmates and family are reachable | Set expectations in the playtest intro ("one night, three people"); recruit players over Thanksgiving |
| **Technology** | **High** | LLM latency, memory consistency, secret leaks and injection resistance are all unmeasured | Experiment 1 by Nov 20; validator plus `legal_actions`; scripted fallback; 20-case adversarial suite |
| Team | Medium | Solo project; production agents are planned, not configured; review time is limited | Configure Tech Lead, QA and Narrative first; independent reviewer agent; I merge |
| Genre / Mechanics | Medium | The rescope removes open-world systems; the time-slot economy and meter thresholds are untested | Internal play-through Nov 25; balance goal in GDD Section 10 |
| **Timeline** | **High** | 12 days to a first playable, including Thanksgiving; every NPC is written twice (agent and baseline) | Baseline doubles as the fallback; cut checkpoint on Nov 22; two-NPC and Mara-only fallback scopes |

**Do the High ratings share a cause?** Yes. Both depend on the same unproven piece: the NPC agent loop. If it is slow or inconsistent, the technology fails, and the schedule slips while I fix it. Experiment 1 (task 3) tests that piece first, and the Nov 22 checkpoint turns the result into a scope decision. The deeper root cause, the original open-world ambition, is already addressed by the rescope.
