# The Living Cap Table

**Equity that's read, not negotiated.**

A GenLayer Intelligent Contract for GenLayer's Agent Tank hackathon (Future of Work
track). Full pitch, problem statement, and rationale: [PROJECT-APPLICATION.md](PROJECT-APPLICATION.md).

## What it does

Agent-built ventures fix an ownership split on day one, before any real work exists,
and then reality never matches it. `LivingCapTable` fixes that by never fixing a
split in the first place:

1. A founder deploys the contract with a plain-language **rubric** for how equity
   should be earned.
2. Contributors **register** with their public GitHub handle and wallet.
3. Anyone can call `recompute_equity()`. GenLayer's validators pull each
   contributor's real public GitHub activity, judge it against the rubric for
   quality and impact (not raw event count), and reach consensus on a
   contribution score for the period. Equity updates directly from that score.
4. `get_cap_table()` is a public view — the current split plus the reasoning
   behind it. Nobody files a claim; there's never a gap between what's owed and
   what's recorded large enough to need one.

## Contract

[`contracts/living_cap_table.py`](contracts/living_cap_table.py)

| Method | Type | Description |
|---|---|---|
| `create_venture(rubric)` | write | Deploys the venture with its equity rubric. Once. |
| `register_contributor(handle, github_handle, wallet)` | write | Adds a contributor. |
| `recompute_equity()` | write | Validators score real GitHub activity against the rubric and update the ledger. |
| `get_cap_table()` | view | Current equity split (basis points + %) and the rationale behind each contributor's latest score. |
| `get_rubric()` | view | The venture's equity rubric. |

## Running it

Needs Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then run the test suite, which deploys the contract in-memory and mocks the
web/LLM calls, so it needs no running Studio and no network access:

```bash
pytest tests/direct
```

All 7 tests pass as of this writing (confirmed on Python 3.12, Linux). The
GenLayer linter is also clean:

```bash
genvm-lint contracts/living_cap_table.py
```

On native Windows Python, `pytest tests/direct` currently fails with a
`PermissionError` while `genlayer-test` tries to delete a temp file it's
still holding open for stdin injection. Windows won't let you unlink a file
while a handle to it is still open; POSIX does. That's a bug in that
package's Windows support, not in this contract, so run tests from WSL,
Linux, or macOS until upstream fixes it.

Deploying to an actual network, or writing integration tests that run
against a live [GenLayer Studio](https://studio.genlayer.com/) instance,
needs the GenLayer CLI as well. Not set up yet, see the status list below.

## Status / next steps for the build window

- [x] Core Intelligent Contract: venture creation, contributor registration,
      consensus-based equity recomputation, public cap table view
- [x] Direct-mode test suite covering rubric setup, registration, scoring,
      and the self-correcting cumulative-score behavior across periods. All
      7 tests pass; `genvm-lint` is clean.
- [ ] Integration tests against a live GenLayer Studio instance
- [ ] Seeded demo GitHub repo with staged, uneven contributor activity
- [ ] Minimal frontend showing a live demo venture's cap table updating in
      real time as `recompute_equity()` runs
- [ ] Demo video for submission

## Why this instead of another arbitration/marketplace pitch

See [PROJECT-APPLICATION.md](PROJECT-APPLICATION.md) for the full case: this is an
**ownership primitive** (a continuously-correct cap table), not another
payment-on-deliverable tool or another "agents dispute, GenLayer judges" product —
the two shapes almost every other GenLayer pitch takes.
