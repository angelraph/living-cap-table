# The Living Cap Table

Equity that's read, not negotiated.

Track: Future of Work. That track is defined as "work verified by consensus, paid on outcome, with portable reputation," and that's exactly what this is.

## The one-liner

A GenLayer Intelligent Contract that keeps ownership in an agent-built venture continuously correct, instead of frozen at a day-one guess. Validators judge real GitHub and on-chain evidence for quality, not just activity, and recompute equity as they go. Nobody self-reports. Nobody votes. Nobody files a claim, because the ledger is never wrong long enough to need one.

## The problem

Every agent-built venture — a product, a trading desk, a content operation run by a few autonomous agents plus a human founder — still splits equity the old way: a percentage agreed on day one, before any real work exists.

Reality never matches that split. One contributor does most of the shipping. Another disappears after the kickoff call. A third joins in week three and rebuilds the core of the thing. Nobody renegotiates, because renegotiating equity is a political, adversarial act, and an autonomous agent can't sit in that negotiation the way a human cofounder can. So the cap table has been wrong since day two, and it stays wrong for the life of the venture, because there's no mechanism to correct it short of a conversation nobody wants to start.

The tools that exist for this today (Coordinape-style peer voting, SourceCred-style contribution scoring, manual vesting schedules) break the same way for an agentic team. They need either self-reporting, which a careless or adversarial agent can game trivially, or a human-style political process, which an agent can't meaningfully take part in. None of them actually check whether claimed work was real and good, only whether it was logged.

## How it works

A venture's founder writes the equity rubric in plain language when the contract is deployed — something like "equity should track shipped, reviewed code; deals sourced weighted by contract value; content weighted by engagement it verifiably drove." That's the whole spec. There's no rigid point system to game.

Each contributing agent registers its public work surface: GitHub handle, wallet, whatever else the rubric cares about.

On a cadence, or whenever anyone calls it, GenLayer's validators pull the real evidence — merged pull requests, on-chain settlements, campaign numbers — straight from the open web, and judge it against the rubric. That judgment is the hard part: was this pull request meaningful or padding? Did this deal actually close on good terms? That's a subjective call, and it's exactly the kind of question GenLayer's Optimistic Democracy was built to settle by validator consensus rather than a plain oracle lookup.

Whatever the validators agree on updates a running equity ledger. Vesting driven by verified output instead of the calendar.

The cap table itself is just a public view. Anyone — a counterparty, an investor, someone doing diligence before an acquisition — can see the current split and the evidence behind every basis point of it. There's no dispute process to build, because the mechanism doesn't let a gap open up between what's owed and what's recorded in the first place.

## Why this needs GenLayer and not just an oracle

It needs three things at once: judgment over ambiguous, real-world evidence (not "did X happen" but "was X good"), live access to the web from inside contract execution, and consensus over that judgment so no single party, including the founder, can quietly move the needle. Drop any one of those and it degrades back into a gameable point system that a Discord bot could run.

## Why this is the rare pitch here

Everything else that could plausibly sit in this track is a payment-on-deliverable tool. Rally, Apolo, GHBounty, and MergeProof, all already live in Future of Work, settle a one-time bounty against a one-time piece of verified work. That's a transaction primitive. The Living Cap Table is an ownership primitive: it doesn't pay out and close a ticket, it maintains a standing, self-correcting stake for every contributor across the life of a venture, and nothing live in the ecosystem does that yet.

It's also deliberately not another arbitration product. That shape of pitch (agents disagree, GenLayer rules on it) is already the most common one on this platform, and it's occupied here by Internet Court in the Onchain Justice track. There's no ruling to hand down in this system at all, because there's never a rupture to rule on.

## Why a founder would actually want this

The most common way a small agent-plus-human venture dies isn't a bad product. It's an equity fight, or the quieter version of that: everyone privately thinks the split is wrong and nobody says so until it's too late to fix without a blowup. This removes the fight by removing the ambiguity — the record updates itself, in public, from evidence anyone can check.

It also fixes a second problem founders already have: diligence. When it's time to raise, sell, or wind a venture down, "who actually built this" usually gets reconstructed from memory and old Slack messages. Here it's just a query.

## What's built for the hackathon window

The contract (`contracts/living_cap_table.py`) is done and deployed for real on GenLayer's hosted Studio Network: venture creation, contributor registration, a `recompute_equity()` method that fetches real GitHub activity and has validators score it against the rubric, and a `get_cap_table()` view that shows the current split plus the reasoning behind it. It's been run end to end against a real GitHub account, not mocked data — validators pulled the real activity, judged it conservatively against the rubric, and the result is readable from the live contract right now. Full details, including three real bugs that only showed up on the live network and how they were fixed, are in the README.

There's also a direct-mode test suite covering the registration rules and the case that matters most — two contributors judged unevenly across two periods, with the cap table correcting itself and no one asking it to.

Still to do before submission: a frontend that shows a venture's cap table and lets someone trigger `recompute_equity()` against the live contract, and a short demo video.
