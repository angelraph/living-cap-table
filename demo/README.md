# Demo: Aurora

`run_demo.py` walks through a sample two-agent venture called Aurora. It exists to
show one thing clearly: the cap table correcting itself when one contributor's real
output changes, without anyone asking it to.

Run it:

```bash
python demo/run_demo.py
```

## What this is, and what it isn't

Aurora is not a real, currently-running venture. This script runs the actual
contract from `contracts/living_cap_table.py`, through the same direct-mode VM the
test suite uses, with GitHub and LLM calls mocked exactly the way the tests mock
them. Same contract code and the same consensus calls (`gl.eq_principle.strict_eq`
on real GitHub evidence, then again on the validators' scoring judgment), just no
live network access during the run, which is what makes it free to run and gives
identical output every time.

That means this script proves the mechanism works. It doesn't, on its own, prove
that a live deployment pulling real GitHub activity from a real GitHub account
would score things the same way an LLM would in production. That's what an
eventual Studio deployment against a real registered contributor is for, which
isn't set up yet (see the status list in the top-level README).

## What it's for

Recording the demo video: run the script, screen-record the output. The two
printed cap tables are the whole story: 55/45 in period one, both agents shipping,
then 76/24 in period two once orion is doing all the work and mira has gone quiet.
Nobody filed a claim to get there.
