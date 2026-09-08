"""Narrated walkthrough of the Living Cap Table contract.

This tells the story of a sample venture, "Aurora," run by two agents. It is
not a claim about any real, currently-running venture - it exists to show
the actual contract in contracts/living_cap_table.py doing the one thing
that matters: correcting an equity split on its own when one contributor's
real output changes, with nobody asking it to.

It runs through GenLayer's direct-mode VM (the same one tests/direct uses).
The real contract's judgment step (gl.eq_principle.prompt_non_comparative,
needed so validators running different underlying models don't have to
produce byte-identical text) isn't mockable in this test harness, so this
script calls _apply_scores() directly with the scores below standing in for
what validators would have agreed on - the exact same thing tests/direct
does, and the exact same deterministic ledger math the real contract runs.
The judgment step itself has been run for real, against a live GitHub
account, on a live deployment - see the README for that result.

Run with:
    python demo/run_demo.py
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from gltest.direct.vm import VMContext
from gltest.direct.loader import deploy_contract, create_address

CONTRACT_PATH = PROJECT_ROOT / "contracts" / "living_cap_table.py"


def _to_address(raw_address: bytes):
    """Imported lazily: the genlayer SDK only lands on sys.path after the
    first deploy_contract() call."""
    from genlayer.py.types import Address

    return Address("0x" + raw_address.hex())


def _section(title: str) -> None:
    print()
    print(f"--- {title} ---")


def main() -> None:
    vm = VMContext()
    founder = create_address("aurora_founder")
    orion = create_address("orion")  # the build agent
    mira = create_address("mira")  # the growth agent
    vm.sender = founder

    with vm.activate():
        contract = deploy_contract(CONTRACT_PATH, vm)

        _section("Sample venture: Aurora, run by two agents")
        rubric = (
            "Equity tracks shipped, reviewed code weighted by impact, and "
            "content that verifiably grew the user base. Padding activity "
            "with trivial commits does not count."
        )
        contract.create_venture(rubric)
        print(f"Rubric: {rubric}")

        contract.register_contributor("orion", "orion-agent-gh", _to_address(orion))
        contract.register_contributor("mira", "mira-agent-gh", _to_address(mira))
        print("Registered: orion (builds the product), mira (runs growth and content)")

        _section("Period 1: kickoff week, both agents ship real work")
        contract._apply_scores(
            ["orion", "mira"],
            {
                "orion": {"score": 55, "reason": "shipped the core checkout flow, reviewed"},
                "mira": {"score": 45, "reason": "wrote and shipped the launch content plan"},
            },
        )
        print(json.dumps(contract.get_cap_table(), indent=2))

        _section("Period 2: mira goes quiet, orion carries the venture alone")
        contract._apply_scores(
            ["orion", "mira"],
            {
                "orion": {"score": 90, "reason": "shipped billing, onboarding, and a mobile fix"},
                "mira": {"score": 0, "reason": "no verifiable public activity this period"},
            },
        )
        print(json.dumps(contract.get_cap_table(), indent=2))

        _section("Nobody filed a claim. The ledger just caught up.")


if __name__ == "__main__":
    main()
