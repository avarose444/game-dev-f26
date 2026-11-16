# After Hours — Initial Project Plan

**Version:** Initial (G1), November 15, 2026. This plan moves to Asana after the G1 decision; owners, acceptance criteria, dependencies and the full Risk Register follow at G2/G3.
**Owner:** Ava Ferrentino, Producer role. Rows marked *(agent)* are delegated execution; I review and accept them.

## Gate dates

| Gate / event | Date |
|---|---|
| G1 pitch post due | Sun Nov 15, 11:59 p.m. |
| G1 gate review (in class) | Mon Nov 16 |
| G1 decision posted (Approve / Hold) | by Tue Nov 17 |
| Two Braintrust replies due | Thu Nov 19, 11:59 p.m. |
| G1 graded feedback returned | by Mon Nov 23 |
| **G2/G3 combined review** | **[fill in from syllabus]** |
| G4 Final / Pre-Launch | [fill in from syllabus] |
| G5 Retrospective | [fill in from syllabus] |

## Goal for the next work cycle

By the G2/G3 review, an external player will be able to play one night with three NPCs, in both agent and scripted modes, and we will know whether remembered callbacks change how players treat the NPCs.

## First tasks through G2

| # | Dates | Task | Role | Depends on | Acceptance criteria |
|---|---|---|---|---|---|
| 1 | Nov 16–17 | Present at G1; read the decision and apply any conditions | Me | — | Conditions copied into this plan |
| 2 | Nov 17–18 | Create the repository from the course starter; choose the provider and set `COURSE_MODEL` | Tech Lead *(agent)*, me | 1 | Setup check passes, with one live call logged with latency |
| 3 | Nov 18 | **Decide:** model | Me | 2 | Decision recorded in the Configuration Document |
| 4 | Nov 18–21 | **Experiment 1:** one NPC (Mara) in the console, with persona card, memory list, schema, validator and timeout fallback | Tech Lead, Narrative *(agents)* | 2 | 20 scripted conversations run; p50/p95 latency and cost per turn logged; `test_validator.py` passes 15/15 |
| 5 | Nov 19 | Write two Braintrust replies | Me | — | Posted |
| 6 | Nov 20 | **Decide:** engine and UI stack | Me | 4 | Recorded in the GDD |
| 7 | Nov 20–22 | Adversarial suite: 20 cases (injection, unwitnessed facts, secret leak, persona break) | QA *(agent)* | 4 | Suite runs; failures recorded rather than hidden |
| 8 | Nov 21–24 | Scripted baseline tree for Mara (also the fallback) | Narrative *(agent)*, me | 4 | Every relationship band has fallback lines |
| 9 | Nov 23–24 | Revise the GDD and Configuration Document from feedback; move the plan to Asana; full Risk Register | Producer *(agent)*, me | 1, feedback | Asana tasks have owners and acceptance criteria |
| 10 | **Nov 24** | **Cut checkpoint** (see triggers below) | Me | 4, 7 | Go / cut decision recorded |
| — | Nov 25–29 | Thanksgiving: low capacity, buffer only | — | — | — |
| 11 | Nov 30–Dec 2 | Night structure (6 slots, 3 locations), character setup, Jun and Nico personas and baselines | Tech Lead, Narrative *(agents)* | 6, 8 | One full night plays through in both modes |
| 12 | Dec 2–3 | Dawn ending, mode toggle, trace logging, BI summary script | Tech Lead, BI *(agents)* | 11 | Summary shows latency, cost and fallback rate per session |
| 13 | Dec 3 | Internal play-through, then an independent QA review | QA *(agent)*, me | 12 | No blocking findings open |
| 14 | by Dec 5 | **First external playtest** (at least one player, both modes) | Me, BI | 13 | Playtest log entry following reader Section 5.9 |
| 15 | before G2/G3 | Update the GDD, Configuration Document, Risk Register, Playtest Log and plan; record the walkthrough | Me | 14 | Linked in the post |

## Cut triggers (fallbacks with a trigger and an action)

- If Experiment 1 shows **p95 above 4 s**, or the validator rejects **more than 10%** of live turns, by Nov 24: switch to suggested replies only, and reduce to **two NPCs**.
- If Mara's baseline tree is not done by Nov 24: drop Nico and use four time slots.
- If spending reaches **$5** before the playtests: freeze live evaluation and rerun only failed cases.

## Risk Profile (summary; the full Register comes at G2/G3)

| Dimension | Rating | Evidence | Mitigation |
|---|---|---|---|
| IP / Concept | Medium | The pitch leans on big commercial IPs (GTA, Cyberpunk, Sims), and "complete freedom" was vague until rescoped | Original setting, names and art; attribution table in GDD Section 13; borrow mechanics and tone only |
| Business / Audience | Medium | Open-world fans may expect an open world; there are no playtests yet; classmates are reachable | Set expectations in the playtest intro ("one night, three people"); recruit 4–6 external players |
| **Technology** | **High** | LLM latency, memory consistency, secret leaks and injection resistance are all unmeasured | Experiment 1 in week 1; validator plus `legal_actions`; scripted fallback; 20-case adversarial suite |
| Team | Medium | Solo project; production agents are planned, not configured; review time is limited | Configure Tech Lead, QA and Narrative first; independent reviewer agent; I merge |
| Genre / Mechanics | Medium | The rescope removes open-world systems; the time-slot economy and meter thresholds are untested | Internal play-throughs from Nov 30; balance goal in GDD Section 10 |
| **Timeline** | **High** | Two versions of every NPC to write (agent and baseline), Thanksgiving week, and the G2/G3 date still to confirm | Baseline doubles as the fallback; cut checkpoint on Nov 24; two-NPC fallback scope |

**Do the High ratings share a cause?** Yes. Both depend on the same unproven piece: the NPC agent loop. If it is slow or inconsistent, the technology fails, and the schedule slips while I fix it. Experiment 1 (task 4) tests that piece first, and the Nov 24 checkpoint turns the result into a scope decision. The deeper root cause, the original open-world ambition, is already addressed by the rescope.
