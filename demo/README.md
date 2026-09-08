# Demo: Aurora

`run_demo.py` walks through a sample two-agent venture called Aurora. It exists to
show one thing clearly: the cap table correcting itself when one contributor's real
output changes, without anyone asking it to.

Run it:

```bash
python demo/run_demo.py
```

## What this is, and what it isn't

Aurora is not a real, currently-running venture. This script deploys the actual
contract from `contracts/living_cap_table.py` in direct-mode (the same VM the
test suite uses) and calls its real `create_venture`, `register_contributor`,
and `get_cap_table` methods for real.

The one thing it doesn't call is the real `recompute_equity()` end to end.
That method's judgment step uses `gl.eq_principle.prompt_non_comparative` -
needed so validators running genuinely different underlying models don't have
to produce byte-identical text - and this test harness can't mock that call
type yet. So this script calls `_apply_scores()` directly, the private method
`recompute_equity()` hands its scores to once validators have agreed on them.
The scores below stand in for what validators would agree on; the ledger math
that turns them into an equity split is the real, unmodified code.

The judgment step itself - real GitHub data, real multi-model consensus - has
already been run for real against a live deployment. See the "Live
deployment" section of the top-level README for that result.

## What it's for

Recording the demo video: run the script, screen-record the output. The two
printed cap tables are the whole story: 55/45 in period one, both agents shipping,
then 76/24 in period two once orion is doing all the work and mira has gone quiet.
Nobody filed a claim to get there.
