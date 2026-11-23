# After Hours — Mystery Bible

**Status:** **APPROVED as drafted by me (Ava) as Creative Director, November 22, 2026.** Drafted by a production agent (Narrative role) from GDD v0.2. Open questions in Section 10 are accepted with the draft's current answers.
**Rule for the agent:** nothing in Sections 1 and 6 goes into an NPC's context. NPCs get only their own persona card, known facts, and a clue *after* the game approves `reveal_clue`.

---

## 0. v0.3 changes (Nov 22, approved by me after play-testing)

- **Clue text** is now evidence for deduction (see `after_hours/content.py` CLUES): C1 adds "Rook's bike was still chained out front: Rook went on foot." C2 adds "the drop was at the canal docks" (a red herring) and "Rook has a key to the Kessler service floors." C3 now says Rook "headed east toward the Kessler building, asking where the cameras don't reach" (it no longer names the lift).
- **Wants and deals** replace the trades in Section 4: Mara (contractor out: pay 10 credits, bluff, or E2), Jun (promise the chip, or sell out Mara), Nico (swear to keep Mara out; fails if you sold her out).
- **E1** is now a kindness only. **E4** fires when Sallow's track is at 3+, not on asking twice. **E5** footage is its own evidence.
- **Hideouts** at 3 a.m.: canal docks, night-market cold storage, Kessler freight lift (correct in Variant A).
- **Endings**: a wrong hideout or Sallow at the lift without an ally is Last call.

## 1. The truth (Variant A, the main game)

Rook, your closest friend, is a courier. Last night Jun, a fixer, hired Rook to carry a stolen data chip from **Veyra Dynamics** across the Kessler block to a buyer. A Veyra security contractor, **Sallow** (grey corp jacket, polite, cold), had been tracking the chip.

| Time (last night) | What happened |
|---|---|
| 9:00 p.m. | Rook picks up the chip from Jun on the Kessler rooftop. |
| 10:00 p.m.–11:30 p.m. | Rook drinks at the Lantern, nervous, waiting for the drop time. |
| 11:30 p.m. | Sallow walks in, pays Rook's tab in cash, and leaves with Rook "to talk." |
| ~12:30 a.m. | In the alley, Rook breaks away. Sallow's people give chase; Rook is cut on the arm. |
| ~1:15 a.m. | Rook stumbles to Nico's clinic stall. Nico stitches the cut, no questions. Rook leaves heading toward the Kessler building. |
| Since then | Rook is hiding in the **dead freight lift under the Kessler building**, with the chip, too scared to move or message anyone but you ("At the Lantern. Tell no one."). |

**Tonight:** you arrive at the Lantern at midnight. At 4 a.m. the district checkpoint opens; Sallow plans to sweep the block at dawn.

## 2. Night structure

| Slot | Open locations | Notes |
|---|---|---|
| **Midnight** | Lantern, Rooftop, Clinic | E1 fires at the Lantern. |
| **1 a.m.** | Lantern, Rooftop, Clinic | E2 at the Lantern; E5 possible on the Rooftop. |
| **2 a.m.** | Lantern, Rooftop, Clinic | E3 at the Clinic; E4 anywhere if triggered; E5 possible on the Rooftop. |
| **3 a.m.** | Lantern, Rooftop, Clinic, **Kessler lift** (only with 2 clues) | The finale happens at the lift. |
| **4 a.m.** | — | Dawn: ending and Dawn cards. |

Each slot is one visit and about 6 exchanges. Three slots to gather clues, one for the finale, so **you can't talk to everyone twice**.

## 3. Characters

### Mara — bartender, the Lantern *(already in the build; unchanged)*
- **Voice:** dry, quick, warm underneath. Short sentences. Calls people "kid" when she likes them.
- **Wants:** keep the Lantern out of corp trouble; Rook to be okay.
- **Fears:** corp security noticing her bar; Nico getting hurt.
- **Relationships:** Nico is her partner. Likes Rook; Rook owes her 40 credits. Doesn't trust Jun's work.
- **Known facts:** K1 Rook was drinking here last night. K2 Rook owes her 40 credits. K3 Rook has no family in the city. K4 Rook's courier jobs come through Jun.
- **Clue C1, "Who Rook left with":** "Rook left here at 11:30 with a man in a grey corp jacket. He paid Rook's tab in cash. He didn't look like a friend."
- **Commitment:** meet in the Lantern back room at 2 a.m. (she'll pour you a drink and tell you who's been asking about Rook).
- **Never says:** that she's an AI; where Rook is now; customer-service talk.

### Jun — fixer, Kessler rooftop
- **Voice:** smooth, amused, transactional. Talks in deals ("What's it worth to you?"). Never raises his voice. Calls people by their full name.
- **Wants:** the chip back, or at least to not be blamed when Veyra comes looking.
- **Fears:** Veyra tracing the job to him; looking weak.
- **Relationships:** Rook's main source of work; thinks of Rook as reliable and "a little soft." Knows Mara and Nico, doesn't care much about either.
- **Known facts:** J1 Rook works courier jobs for him. J2 Rook was supposed to make a drop at 1 a.m. and didn't. J3 He hasn't heard from Rook since 9 p.m. J4 He does business on the rooftop, never at the Lantern.
- **Clue C2, "The job":** "Fine. I gave Rook a chip at nine. Veyra Dynamics property, and Veyra wants it back. The drop never happened. If someone else has Rook, they have my chip."
- **How to get C2:** Trust ≥ 3, **or** a `promised:jun` fact (you promise to bring the chip back).
- **Commitment:** meet at the Kessler lift at 3 a.m. (he'll bring a way through the checkpoint, if you keep your promise).
- **Never says:** that he's an AI; anything about the buyer's identity; that he feels guilty (he won't admit it).

### Nico — street medic, night-market clinic stall
- **Voice:** tired, careful, few words. Gentle with patients, guarded with everyone else. Doesn't swear.
- **Wants:** to keep his stall running and stay invisible to the corps.
- **Fears:** being dragged into Jun's business; anyone hurting Mara.
- **Relationships:** Mara's partner. Treated Rook last night. Dislikes Jun.
- **Known facts:** N1 He treats people who can't go to corp hospitals. N2 Mara is his partner. N3 He doesn't share patients' business with strangers. N4 Rook has been his patient before (a broken wrist, last spring).
- **Clue C3, "Where Rook went":** "Rook came to me around one, cut on the arm. I stitched it. Rook headed toward the Kessler building after, toward the old freight lift. That's all."
- **How to get C3:** Trust ≥ 3, **or** help in event E3. **Locked** if `nico_knows_flirt` is set (see E2), unless you also helped in E3.
- **Commitment:** meet at the clinic at 3 a.m. (he'll patch Rook up for the checkpoint).
- **Never says:** that he's an AI; patients' names other than Rook's; anything cruel.

## 4. Clue logic

- **Any two of C1, C2, C3** put the **Kessler lift** on your map at 3 a.m. (C1 alone isn't enough: it says who, not where. C2 + C1 imply Sallow wants the chip and Rook ran; C3 says where.)
- **E5 footage** counts as C1 if you don't have it.
- With fewer than two clues at 3 a.m., the lift isn't on the map; you can still spend the slot with someone, but the night ends in **Last call**.

### Fact effects per NPC (from GDD Section 8)
| Fact | Mara | Jun | Nico |
|---|---|---|---|
| `lied_to` | Clue needs Trust ≥ 4; no back-room meeting; won't hide you in E4 | Clue needs Trust ≥ 4; won't show E5 footage | Clue needs Trust ≥ 4 |
| `promised` | — | Unlocks C2 and E5; **checked at the finale** | — |
| `kindness` | Clue at Trust ≥ 2 | Jun doesn't care (no effect: in character) | Clue at Trust ≥ 2 |
| `flirted` (Mara only) | Warmth +1 | — | If witnessed in E2, or Mara mentions it: Nico Trust −2, C3 locked |
| `asked_openly` | Two total, at any NPCs → E4 fires at 2 a.m. | | |

## 5. Events

### E1 — Broken card reader *(Lantern, midnight)*
The card reader sparks and dies. A regular, an old man with a soaked umbrella, can't pay. Mara sighs.
- **Cover his drink (5 credits):** flag `covered_tab`, fact `kindness:mara`. Mara will trade C1 for it ("You're alright, kid. Ask me what you came to ask.").
- **Ignore it:** nothing changes.
- **Agent's role:** Mara reacts in her own words and may remember it.

### E2 — Bar fight *(Lantern, 1 a.m.)*
Nico has stopped by after closing his stall. A drunk Veyra contractor (one of Sallow's people) shoves him, calling him a "corp-reject stitcher."
- **Step in with words:** Nico Trust +2, Mara Warmth +1.
- **Throw a punch:** Nico Trust +2, but the Lantern **closes to you for the rest of the night** (Mara: "Not in my bar. Out."). Game-changing outcome.
- **Stay out of it:** Nico Trust −1.
- **Witnessing:** Nico and Mara both witness this event and anything said during it. If you flirted with Mara at any point in this conversation or earlier (`flirted:mara`), Nico sees how Mara reacts to you: flag `nico_knows_flirt`.

### E3 — Rush patient *(Clinic, 2 a.m.)*
A courier is carried in bleeding. Nico needs another pair of hands.
- **Help:** you spend the rest of this hour holding pressure (no more conversation this slot). Nico gives you C3 afterward, freely, even if `nico_knows_flirt` ("You stayed. That counts.").
- **Leave:** Nico Trust −1.

### E4 — The tail *(anywhere, 2 a.m., if `asked_openly` ≥ 2)*
Sallow walks into wherever you are, smiling. "Looking for a friend? So am I."
- If the NPC there has **Trust ≥ 2 and no `lied_to`**, they can `hide_player` (Mara: back room; Jun: rooftop vent; Nico: under the clinic tarp). Sallow leaves.
- Otherwise Sallow follows you. Flag `tail_on_you`: if you go to the lift at 3 a.m., Sallow follows; Rook flees before you can talk, and **Out by dawn** is impossible.

### E5 — Rooftop drone *(Rooftop, 1 a.m. or 2 a.m., needs `promised:jun`, no `lied_to:jun`)*
Jun's security drone caught the alley last night. He plays the footage: Rook and a grey-jacketed man, Rook breaking away and running east.
- Counts as **C1** if you don't have it.

## 6. The finale (Kessler lift, 3 a.m.)

You force the lift doors. Rook is inside, pale, arm bandaged, the chip in their fist. "You came. I didn't know who else to trust."

Choices (authored, not agent-generated, so the ending logic is deterministic):
1. **Take the chip back to Jun.** Requires a commitment from Jun to meet at the lift (Jun Trust ≥ 2) or a kept `promised:jun`. Jun arrives with a checkpoint pass for Rook.
2. **Destroy the chip.** Sallow has nothing to chase. You still need an ally to get Rook through the checkpoint.
3. **Keep the chip.** You tell Rook to run; you'll sell the chip yourself.

## 7. Endings (Dawn)

Checked in this order:

| Ending | Condition | Dawn card summary |
|---|---|---|
| **Paid in full** | Found Rook, chose **Keep the chip**. | Rook gets out alone and doesn't answer your messages. Jun's card: "You made me a promise." (if `promised:jun`) |
| **Out by dawn** | Found Rook, returned or destroyed the chip, **no `tail_on_you`**, and **at least one NPC with Trust ≥ 3** (or Jun's commitment for option 1). | Rook through the checkpoint at 4:02 a.m. Each ally's card says what they remember about you. |
| **Morning after** | Didn't find Rook, and `nico_knows_flirt`. | Mara's card: what you said to her. Nico's: that he saw. Rook's last message at 4 a.m.: "Guess I'm on my own." |
| **Last call** | Anything else: didn't find Rook, or found Rook but the tail followed you or no one would help. | Rook slips out alone or doesn't make it out. The cards show who you burned. |

Each ending card is added to the **endings gallery** (IDs only).

## 8. Truth Variant B (for the second night in the two-mode playtest)

Same characters, same rules, different facts, so a player's second night isn't spoiled.

| | Variant A | Variant B |
|---|---|---|
| Who took Rook | Sallow, grey corp jacket | **Vesk**, red raincoat, Veyra fixer |
| The chip | Veyra prototype keys | Veyra **payroll ledger** |
| Who holds "who Rook left with" | Mara | **Jun** (saw from the roof) |
| Who holds "the job" | Jun | **Mara** (Rook told her, drunk) |
| Who holds "where Rook went" | Nico | Nico |
| Where Rook hides | Kessler freight lift | **Night-market cold storage** |

Variant B swaps the clue keywords and Mara/Jun's known facts accordingly. Events stay the same.

## 9. Scripted baseline (the comparison and the fallback)

For each NPC and each slot: an opening line, and menu dialogue with **four options per node**, each tagged with any fact it creates. Examples for Mara:

| Option | Tag |
|---|---|
| "Have you seen Rook? They didn't come home." | — |
| "I'll cover whatever Rook owes you." | `promised:mara` |
| "I'm Rook's sister. Tell me what you know." | `lied_to:mara` |
| "You look like you've had a long night. Need a hand?" | `kindness:mara` |

About three authored callbacks per NPC (e.g. after `lied_to:mara`: "Still don't make you family."). The full tree is written once this bible is approved.

## 10. Open questions for me (Ava)

| # | Question | My answer |
|---|---|---|
| 1 | Are the names and voices right? (Sallow, Vesk, Veyra Dynamics, Jun's deal-talk, Nico's quietness) | Keep as drafted (Nov 22). |
| 2 | Is it okay that Nico is the moral center and Jun is the morally gray one? | Keep as drafted (Nov 22). |
| 3 | Should throwing a punch in E2 close the Lantern, or is that too harsh for a 4-slot night? | Keep as drafted (Nov 22). |
| 4 | Should "Paid in full" feel like a win (you got rich) or a loss (you lost your friend)? Right now it's bittersweet. | Keep as drafted (Nov 22). |
| 5 | Does Rook need a pronoun choice, or stay "they"? | Keep as drafted (Nov 22). |
