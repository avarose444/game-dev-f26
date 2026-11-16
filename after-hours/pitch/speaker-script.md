# After Hours — G1 Speaker Script (plain-language version)

About 700 words, roughly 4 min 45 s at a normal speaking pace. Each **[Slide N]** cue matches the deck. Course terms are in **bold** the first time you say them, because the rubric checks for course vocabulary.

---

**[Slide 1]**
Hi, I'm Ava, and my game is called After Hours. Here's the one-sentence version, what the course calls **the X**: you play one night in a neon city. You make a character, pick where to spend each hour, and talk to three people who actually remember what you said and did. By morning, your relationships should feel like ones *you* made.

**[Slide 2]**
It's for people who play games like Cyberpunk or The Sims for the characters, not the fighting. How would I know it's working? In a **playtest** I'd watch for three things. Players go back to a character on their own. They type things like "sorry about earlier." And when I ask "tell me about Mara," they describe a moment between them, not just "she's nice."

**[Slide 3]**
This is the **core loop**, what you do over and over. You pick a place and say something. The character reacts, and maybe offers you a job or turns you down. You read how it went. Then you decide: keep going, fix it, or spend your next hour with someone else. Six hours, three people: you can't see everyone.

**[Slide 4]**
My three **pillars**, the rules I use to make design choices: they remember you; small city, deep people; and your night, your terms. My first idea was a huge open world, GTA plus Cyberpunk plus The Sims. That's way too big for this semester. My second was an AI that runs the whole city's events, but players couldn't tell what the AI did, so I couldn't test it. This version won because you can see the AI's effect right in the conversation.

**[Slide 5]**
Where the ideas come from. From The Sims, the relationship bars, except mine move based on what you say. From Cyberpunk, the scene where you first meet Evelyn Parker at a bar. She only tells you what she wants to, and you have to decide whether to trust her. That's exactly how Mara starts. Façade is the closest older game: you type to two characters in one apartment. The memory idea comes from a research paper called Generative Agents. I'm not using anyone's art, characters or code.

**[Slide 6]**
How it works. The game keeps the real facts: the time, the relationship scores, what everyone remembers. When you talk to Mara, the AI only gets what Mara should know. That's her **knowledge boundary**. The AI suggests a reply, and a **validator** checks it follows the rules: no actions she isn't allowed to take, no memories that never happened. If the reply breaks a rule or takes over six seconds, a pre-written line plays instead.

**[Slide 7]**
My **agent hypothesis**: characters who remember specific things you did make the relationship feel like yours. I compare that with a **scripted baseline**, the same characters with normal pre-written dialogue choices. People play one short night each way. I count how often they go back to someone and bring up earlier moments, and what they remember afterward. With the scripted version, you lose this: characters can't respond to your own words, and they only remember what I planned for.

**[Slide 8]**
In **scope**: making a character, three locations, three characters, relationship scores, memory, and a summary at dawn. Out: open world, driving, fighting, money, more than one night. If I run short on time, I cut the third character first, then the character art, then typing. Memory and the validator stay, because they're what I'm testing.

**[Slide 9]**
**Budgets**. I want a reply to start appearing in about a second and a half, and to be finished within three seconds. Those are targets; I haven't measured them yet. With a small, cheap model, one reply costs about three hundredths of a cent, so a whole session is about a penny and a half. I set a hard cap of five cents per session.

**[Slide 10]**
My **Risk Profile**. Two risks are High: technology and timeline. They share one cause: I haven't proven the AI characters work yet. So my first task is a test with one character by November 21, and on November 24 I decide whether to keep three characters or cut to two. The other four are Medium.

**[Slide 11]**
What I'm asking for: approval to build this one-night prototype. First the one-character test, then the full night in both versions, then a playtest with someone outside my project. If I get a **Hold**, it'd probably be to shrink the scope or prove the AI follows the rules, and I'd come back with my test results. To be clear, the X, the pillars and the hypothesis are my decisions. Shrinking the scope and the budget numbers were suggestions from my AI producer agent that I accepted. Thanks!
