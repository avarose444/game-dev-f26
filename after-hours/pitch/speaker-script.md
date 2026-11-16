# After Hours — G1 Speaker Script

About 680 words, roughly 4 min 40 s at a comfortable pace (~145 wpm). Each **[Slide N]** cue matches the deck. If you run long, trim the bracketed *(optional)* lines first.

---

**[Slide 1: Title and the X]**
Hi, I'm Ava, and this is *After Hours*. My X: After Hours is a one-night life sim in a neon city district. You create a character, choose where to spend each hour, and talk with three residents who remember what you said and did, so the relationships you end the night with feel like ones you actually made.

**[Slide 2: Player and motivation]**
It's for players who love open-world and life-sim games for their characters more than their combat. The motivation is self-expression and connection. In a playtest, if it works, I'd see players return to an NPC unprompted to follow up on something, type replies that refer back to earlier moments, and, when I ask "tell me about Mara," describe something specific that happened between them.

**[Slide 3: Core loop]**
The loop: you act, by picking a location for the hour and talking or offering something. The NPC responds in character and may take a validated action, like offering a job or refusing a favor. You interpret the reaction, the meter change and the "Mara will remember that" cue. Then you choose your next action: push, repair, or spend your next hour with someone else. Six hours, three people: you can't see everyone.

**[Slide 4: Pillars and concepts considered]**
Three pillars. They remember you. Small city, deep people. Your night, your terms. I considered two other concepts. My original was a full open-world sim mixing GTA, Cyberpunk and The Sims; it can't reach a testable playable by G2/G3. Then an AI "city director" running world events, but players can't tell a generated event from a scripted one. This concept won because the agent's effect is visible in conversation, and it has a clean scripted baseline.

**[Slide 5: References]**
From The Sims I borrow visible relationship meters, but they move from what you say, not from repeating a chat action. From Cyberpunk 2077, the neon tone; there's no combat. From GTA, only the sense that the city lives without you. *Façade* is my closest precedent: free-text conversation in one place over twenty minutes. The memory list simplifies the *Generative Agents* paper. The validation pattern comes from the course starter. Everything is inspiration only: no assets, names or code.

**[Slide 6: Systems diagram]**
The game engine owns the world state: time, meters, flags, every NPC's memories. Each turn it builds a bounded context packet: this NPC's persona, its own memories and meters, the public player profile, recent lines, and the legal actions. Player text is untrusted. The model returns JSON. A deterministic validator checks the action is legal, clamps the meter change, and rejects memories that don't exist. If anything fails, or the call takes more than six seconds, the scripted line plays instead. The NPC never sees other NPCs' memories or events it didn't witness.

**[Slide 7: Agent hypothesis]**
My hypothesis: an NPC agent that recalls specific things you said or did, and acts only through validated actions, will make players feel their relationships are their own, compared with an authored branching-dialogue version of the same three NPCs. Playtest question: when an NPC brings up something you did earlier, do you treat it as part of the relationship? Players play one short night in each mode, order alternated, and I count return visits, callback replies and specific moments recalled. With the scripted baseline, the player loses responses to their own words and callbacks to anything I didn't pre-flag.

**[Slide 8: Scope]**
Included: character setup, one block with three locations, three NPCs in both modes, meters, memory, and a dawn summary. Excluded: open world, driving, combat, economy, needs, multiple nights, NPC gossip. I'd cut first the third NPC, then portraits, then free text. Memory and validation stay.

**[Slide 9: Budgets]**
Latency targets, not yet measured: first streamed text under 1.5 seconds median, the full line under 3 seconds at p95, and a 6-second hard timeout. Cost: on Claude Haiku 5.5, about two thousand input and a hundred fifty output tokens per turn comes to about $0.0003. Forty turns plus summaries is about a cent and a half per session, with a hard ceiling of five cents.

**[Slide 10: Risk Profile]**
Technology and Timeline are High, and they share a cause: the unproven NPC agent loop. My first experiment, one NPC in the console by November 21, measures latency and validator failures, and on November 24 I either continue or cut to two NPCs. IP, Audience, Team and Mechanics are Medium. *(optional: The rescope already removed the biggest mechanics risk.)*

**[Slide 11: Decision requested]**
I'm asking for approval to prototype the one-night, three-NPC slice: Experiment 1, then a playable night in both modes, and an external playtest before G2/G3. A Hold would most likely need me to reduce scope further or show the agent can be validated, and I'd return with Experiment 1's measurements. To be clear about who decided what: the narrowed scope and the budgets were recommendations from my Producer agent. The X, the pillars and the hypothesis are my decisions. Thanks.
