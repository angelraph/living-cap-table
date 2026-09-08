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
| `register_contributor(handle, github_handle, wallet)` | write | Adds a contributor. `wallet` is an `Address`. |
| `recompute_equity()` | write | Validators score real GitHub activity against the rubric and update the ledger. |
| `get_cap_table()` | view | Current equity split (basis points) and the rationale behind each contributor's latest score. |
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

All 7 tests pass as of this writing (confirmed on Python 3.12, Linux).

On native Windows Python, `pytest tests/direct` currently fails with a
`PermissionError` while `genlayer-test` tries to delete a temp file it's
still holding open for stdin injection. Windows won't let you unlink a file
while a handle to it is still open; POSIX does. That's a bug in that
package's Windows support, not in this contract, so run tests from WSL,
Linux, or macOS until upstream fixes it.

Note on `genvm-lint`: its fast AST-based check flags `recompute_equity` with
"nested non-deterministic blocks are forbidden" for the two sequential
`gl.eq_principle` calls inside it. That's a false positive from the fast
heuristic, not a real constraint - the calls are sequential, not nested, and
this is confirmed two ways: `genvm-lint validate` (the deeper, SDK-based
check) passes clean, and the contract runs correctly on a live network (see
below).

## Live deployment

Deployed and exercised for real on GenLayer's hosted Studio Network
(`studionet`, chain id 61999):

- Contract: [`0x2B20c02d514478a1E1E687628e12c86e100A5Ca1`](https://genlayer-explorer.vercel.app)
- `create_venture(...)` and `register_contributor("angelraph", "angelraph", <wallet>)`
  both landed with `MAJORITY_AGREE` across 5 validators
- `recompute_equity()` made a real call to `api.github.com/users/angelraph/events/public`
  and a real judgment call across validators running different underlying
  models (Claude, GPT, Gemini, Qwen, DeepSeek, Mistral). Result, read back
  from the live contract:

  ```json
  {
    "angelraph": {
      "github_handle": "angelraph",
      "score": 12,
      "equity_bps": 10000,
      "last_scored_reason": "Active pushes, but evidence does not show substantive shipped or reviewed work on living-cap-table"
    }
  }
  ```

  That's not a rubber stamp - the validators looked at the real activity and
  scored it conservatively against the rubric, which is the entire point.

The wallet-connected flow in `frontend/` has since been clicked through for
real too: connect wallet, `recompute_equity()` from a real browser wallet,
transaction lands, cap table updates. A follow-up recompute (run again to
double-check the first wasn't a silently-swallowed no-op, the way
`register_contributor` was before it got fixed) moved the score from 12 to
50 cumulative, with a fresh, specific judgment: *"Created the
living-cap-table repo (directly relevant to rubric) but most activity is
pushes to unrelated repos (lucid, charter); no reviewed PRs or verifiable
quality work on the target repo visible."* Real evidence, re-evaluated,
genuinely different reasoning each time - not cached, not repeated.

Three real bugs turned up getting this far, all now fixed in the code:

1. `register_contributor` originally took `wallet: str` and converted it to
   `Address` inside the method. The live CLI's argument parser auto-detects
   any 40-hex-char `0x...` value as an address-typed argument regardless of
   the method's declared parameter type, so it handed the method an
   already-`Address` value, and converting an `Address` to an `Address`
   failed with `TypeError: cannot convert 'Address' object to bytes` -
   silently, since GenVM rolled back the whole call and the CLI still
   reported consensus success. Fixed by declaring `wallet: Address` directly.
2. `get_cap_table()` returned a computed `equity_pct` float. GenVM's calldata
   encoder can't serialize a raw Python float in a return value
   (`TypeError: not calldata encodable 0.0: float`). Removed it - `equity_bps`
   is the value that matters, percentage is a display concern for whatever
   reads it.
3. The scoring step originally used `gl.eq_principle.strict_eq`, which
   requires every validator's output to match byte-for-byte. That's fine
   when every validator calls the same mocked response (which is why it
   passed direct-mode tests), but on a live network different validators run
   genuinely different models, and their free-text justifications never
   match exactly - the transaction landed as `MAJORITY_DISAGREE` /
   `UNDETERMINED`. Fixed by switching to
   `gl.eq_principle.prompt_non_comparative`, which checks the leader's answer
   against stated criteria instead of requiring identical text. That call
   type isn't mockable in the installed `genlayer-test` version, so the
   deterministic ledger math it feeds into was pulled into its own method,
   `_apply_scores()`, which the test suite exercises directly - see the test
   file for details.

## Demo

[`demo/run_demo.py`](demo/run_demo.py) walks through a sample two-agent venture
and prints the cap table correcting itself across two periods:

```bash
python demo/run_demo.py
```

See [demo/README.md](demo/README.md) for what it does and doesn't prove.

## Frontend

[`frontend/`](frontend/) is a small Vite + TypeScript page that reads the
live contract above directly - rubric, cap table, and the reasoning behind
each contributor's score, no wallet required to view. A connected wallet can
also register as a contributor or trigger `recompute_equity()` for real.
See [frontend/README.md](frontend/README.md) for setup and what's been
verified so far.

```bash
cd frontend
npm install
npm run dev
```

## Status / next steps for the build window

- [x] Core Intelligent Contract: venture creation, contributor registration,
      consensus-based equity recomputation, public cap table view
- [x] Direct-mode test suite covering rubric setup, registration, scoring,
      and the self-correcting cumulative-score behavior across periods. All
      7 tests pass; `genvm-lint` is clean.
- [x] Narrated demo script showing the split correcting itself across two
      periods
- [x] Deployed and exercised live on GenLayer's Studio Network - real
      GitHub data, real multi-model validator consensus, real result read
      back from the chain (see Live deployment above)
- [x] Frontend ([`frontend/`](frontend/)) reading the live contract directly
      and driving it - both the read side (rubric, cap table) and the
      wallet-connected write side (register, recompute) confirmed working
      against real on-chain data with a real browser wallet
      (see [frontend/README.md](frontend/README.md))
- [ ] Demo video for submission - script ready: [demo/VIDEO-SCRIPT.md](demo/VIDEO-SCRIPT.md)

## Why this instead of another arbitration/marketplace pitch

See [PROJECT-APPLICATION.md](PROJECT-APPLICATION.md) for the full case: this is an
**ownership primitive** (a continuously-correct cap table), not another
payment-on-deliverable tool or another "agents dispute, GenLayer judges" product —
the two shapes almost every other GenLayer pitch takes.
