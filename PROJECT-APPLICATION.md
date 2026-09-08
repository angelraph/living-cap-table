# The Living Cap Table

**Equity that's read, not negotiated.**

**Track: Future of Work** — "Work verified by consensus, paid on outcome, with portable reputation."

---

## The one-liner

A GenLayer Intelligent Contract that continuously recomputes ownership in an agent-built venture from validators' real-time judgment of verified contribution — so nobody ever files for their fair cut, because the ledger was never wrong long enough to need fixing.

## The problem

Every agent-built venture — a product, a trading desk, a content operation run by a handful of autonomous agents plus a human founder — still freezes equity the old way: a percentage split negotiated on day one, before any real work exists.

Reality never matches that split. One contributor does 80% of the shipping. Another disappears after the kickoff call. A third joins in week three and rebuilds the core of the thing. Nobody renegotiates, because renegotiating equity is a political, adversarial act — and an autonomous agent can't sit in that negotiation the way a cofounder can. The cap table has been wrong since day two, and it silently stays wrong for the life of the venture.

The tools that exist for this (Coordinape-style peer voting, SourceCred-style contribution scoring, manual vesting schedules) all break the same way for an agentic team: they need either self-reporting (trivially gamed by a careless or adversarial agent) or a human-style political process (agents can't meaningfully participate in "vibes"-based peer allocation). Nothing verifies that claimed work was *real and good*, not just *logged*.

## The mechanism

1. **Rubric, not formula.** A venture's founder defines the equity rubric in plain language at deploy time — e.g. *"equity should track shipped, reviewed code; deals sourced weighted by contract value; content weighted by engagement it verifiably drove."* No rigid point system to game.
2. **Registration.** Each contributing agent registers its public work surface — GitHub handle, wallet, content accounts.
3. **Continuous, non-deterministic evaluation.** On a cadence, GenLayer's validators independently pull live evidence — merged PRs, on-chain settlements, campaign data — straight from the open web, and reason over the rubric against that evidence. This is a genuinely subjective call (was this PR meaningful or padding? did this deal actually close on good terms?) — exactly the class of question Optimistic Democracy exists to settle by LLM-validator consensus, not a simple oracle lookup.
4. **Consensus updates the ledger.** The validators' agreed contribution scores update a running equity ledger — vesting driven by verified output instead of the calendar.
5. **The cap table is a public view, not a claim.** Anyone — a counterparty, an investor, an acquirer — can query the current split and the full evidence trail behind every basis point. There is no dispute process because there is no gap between what's owed and what's recorded large enough to need one.

## Why this needs GenLayer specifically

It needs all three things only GenLayer's Intelligent Contracts offer together: LLM-grade judgment over ambiguous real-world evidence (not "did X happen" but "was X good"), live web access from inside contract execution, and trust-minimized consensus over that judgment so no single party — including the founder — can quietly move the needle. Take away any one of those and the product degrades back into a gameable point system.

## Why this is the rare pitch, not the obvious one

Every other track-fit angle in this space is a **payment-on-deliverable** tool — Rally, Apolo, GHBounty, and MergeProof (all already live in this exact track) settle a one-time bounty against a one-time piece of verified work. That's a transaction primitive. The Living Cap Table is an **ownership primitive**: it doesn't pay out and close a ticket, it maintains a standing, ever-correcting stake for every contributor across the entire life of a venture. Nothing live in the ecosystem does this. It's also deliberately *not* another arbitration/dispute product (the single most crowded shape of GenLayer pitch, occupied here by Internet Court and the whole Onchain Justice track) — there is no complaint to file and no ruling to hand down, because the mechanism never lets a gap open up in the first place.

## Why a founder would actually want this

The single most common way a small agent-plus-human venture quietly dies isn't a bad product — it's an equity fight, or the resentment that builds up when everyone privately believes the split is wrong and nobody says so. This removes the fight by removing the ambiguity: the record updates itself, in public, from evidence everyone can check. It also solves a second real problem founders have today — diligence. When it's time to raise, sell, or wind down, "who actually built this" is usually reconstructed from memory and Slack scrollback. Here it's just a query.

## MVP scope for the build window (Sep 3–17)

- One GenVM Intelligent Contract (Python) exposing:
  - `create_venture(rubric: str)`
  - `register_contributor(handle, github, wallet)`
  - `recompute_equity()` — the non-deterministic method: fetches GitHub activity for each registered contributor, has validators reason over it against the rubric, reaches consensus via GenLayer's equivalence principle, updates the ledger
  - `get_cap_table()` — public view: current split + evidence trail
- A single-page frontend showing a live demo venture's cap table updating as real commits land in a seeded public GitHub repo
- README + a short demo video: three agents contribute unevenly to the seeded repo, the cap table visibly self-corrects, nobody asks for anything

## Still needed for submission

- GitHub repository (public) implementing the above
- Full project application in the portal, plus a short demo video/GIF
- Team info / links

---

*Superseded drafts: "Court of Intent" (dispute-over-agreement adjudication — already live as Internet Court) and "Agent Probate" (succession-on-disappearance — same reactive-judgment shape as Court of Intent, just later in an agent's life). Living Cap Table was chosen because it's structurally proactive/continuous rather than reactive, and it doesn't compete in the crowded "agents in conflict, GenLayer judges" category at all.*
