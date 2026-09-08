# Demo video script — The Living Cap Table

Target length: ~2 minutes. Every screen shown is real — the live deployed
contract, real GitHub data, a real wallet. Nothing in this script is staged
except the "Aurora" segment, which is labeled on screen as a walkthrough.

Record screen + voiceover together, or voiceover over a screen capture after
the fact — whichever is easier. Cursor movements should be slow and
deliberate; pause on numbers long enough for someone to actually read them.

---

## 0:00–0:15 — The problem

**[ON SCREEN: black slide, or a plain equity-split diagram — two names, a
percentage, a date]**

**VOICEOVER:**
"Every agent-built venture freezes ownership on day one. A split, agreed
before any real work exists.

Then reality happens — one contributor does most of the shipping, another
goes quiet, someone new carries the thing by week three. Nobody
renegotiates, because renegotiating equity is a fight nobody wants to
start. So the split just stays wrong."

---

## 0:15–0:35 — The idea

**[ON SCREEN: title card — "The Living Cap Table" / "Equity that's read, not
negotiated."]**

**VOICEOVER:**
"This is the Living Cap Table. A GenLayer contract that never lets that gap
open up. A founder writes the equity rubric in plain language. Contributors
register their GitHub handle. And from then on, the split isn't agreed —
it's read."

---

## 0:35–1:15 — Live: the real deployment

**[ON SCREEN: browser, `localhost:5173`, the actual running frontend]**

**VOICEOVER:**
"This isn't a mockup. This is deployed right now on GenLayer's Studio
Network."

**[Point at the contract address / Explorer link on screen]**

"That's the real contract address. And this—"

**[Scroll to the rubric card, then the cap table]**

"—is the real rubric, and the real cap table, read live off the chain."

**[Pause on the cap table entry — score, equity, and the reasoning text]**

"One contributor registered so far, so it's sitting at 100%. But look at
the reasoning next to it — that's not a rubber stamp. GenLayer's
validators actually pulled this account's real public GitHub activity and
judged it against the rubric. And they were skeptical."

**[Read the actual reasoning text on screen, e.g. "Created the repo, but
most activity is pushes to unrelated repos — no reviewed work on the target
repo visible."]**

---

## 1:15–1:45 — Live: triggering it for real

**[Click "Connect wallet." MetaMask prompts. Approve.]**

**VOICEOVER:**
"Anyone can connect a wallet here — not just the founder — and trigger a
recompute."

**[Click "Recompute equity." Status line shows the submitted tx hash,
pending.]**

"This just sent a real transaction. Right now, live, GenLayer's validators
— running genuinely different underlying models, Claude, GPT, Gemini,
several others — are independently pulling fresh GitHub activity and
judging it again."

**[Wait for it to resolve. Cap table updates with a new score / reasoning.]**

"And there it is. New score, new reasoning, updated automatically. Nobody
filed a claim. Nobody argued about it. The ledger just caught up."

---

## 1:45–2:05 — Why this is the rare pitch

**[ON SCREEN: split-screen or quick cut — "payment on deliverable" vs.
"continuous ownership," or just talking-head / voiceover over the repo]**

**VOICEOVER:**
"Every other tool in this space pays out a one-time bounty for a one-time
piece of work. That's a transaction primitive. This is an ownership
primitive — a standing, self-correcting stake that updates for the whole
life of a venture. And it's not another 'agents argue, GenLayer judges'
product either — there's no dispute to resolve here, because the mechanism
never lets a gap open up to argue about."

---

## 2:05–2:15 — Close

**[ON SCREEN: GitHub repo URL — github.com/angelraph/living-cap-table]**

**VOICEOVER:**
"The Living Cap Table. Full contract, tests, and this frontend are live in
the repo right now. Equity that's read, not negotiated."

---

## Optional extra beat (if you want to go past 2 minutes)

Cut in `demo/run_demo.py`'s output here, framed honestly:

**[ON SCREEN: terminal running `python demo/run_demo.py`]**

**VOICEOVER:**
"One thing the live deployment can't show yet with only one contributor:
what happens when a venture has several. So here's a quick walkthrough —
same contract, same math, a sample venture called Aurora with two agents."

**[Let period 1's output print — 55/45 split]**

"Two agents, both shipping. Even-ish split."

**[Let period 2's output print — 76/24]**

"Then one goes quiet, the other carries it alone. Nobody asks for anything.
The split just moves."

---

## Notes for recording

- Have the frontend already loaded and the wallet already unlocked before
  you hit record, so you're not fumbling through a MetaMask password on
  camera.
- The real recompute can take 20–40+ seconds to resolve (it's a genuine live
  GitHub fetch + multi-model consensus round, not an instant local call) —
  either let that breathing room play out with a beat of silence, or cut to
  the "Aurora" segment while it resolves and cut back.
- If the reasoning text angelraph gets scored on changes by the time you
  record, that's fine — read whatever the live text actually says. The
  point is that it's real and specific, not the exact wording above.
