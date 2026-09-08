"""Narrated walkthrough of the Living Cap Table contract.

This tells the story of a sample venture, "Aurora," run by two agents. It is
not a claim about any real, currently-running venture - it exists to show
the actual contract in contracts/living_cap_table.py doing the one thing
that matters: correcting an equity split on its own when one contributor's
real output changes, with nobody asking it to.

It runs through GenLayer's direct-mode VM (the same one tests/direct uses),
with GitHub and LLM calls mocked exactly the way the test suite mocks them -
same contract code, same consensus calls, no live network access, so it's
free to run and gives the same output every time. That makes it a
reasonable thing to record for a demo video, and a reasonable thing for
anyone reviewing this submission to run themselves.

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


def _to_hex(raw_address: bytes) -> str:
    return "0x" + raw_address.hex()


def _section(title: str) -> None:
    print()
    print(f"--- {title} ---")


def _mock_period(vm: VMContext, scores: dict) -> None:
    """Point the next recompute_equity() call at one period's evidence.

    Clears the previous period's mocks first - mock_web/mock_llm match in
    registration order and never expire on their own, so without this the
    second call would still be scored with the first period's answer.
    """
    vm.clear_mocks()
    vm.mock_web(
        r".*api\.github\.com/users/.*/events/public.*",
        {"status": 200, "body": "[]"},
    )
    vm.mock_llm(r".*", json.dumps(scores))


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

        contract.register_contributor("orion", "orion-agent-gh", _to_hex(orion))
        contract.register_contributor("mira", "mira-agent-gh", _to_hex(mira))
        print("Registered: orion (builds the product), mira (runs growth and content)")

        _section("Period 1: kickoff week, both agents ship real work")
        _mock_period(
            vm,
            {
                "orion": {"score": 55, "reason": "shipped the core checkout flow, reviewed"},
                "mira": {"score": 45, "reason": "wrote and shipped the launch content plan"},
            },
        )
        contract.recompute_equity()
        print(json.dumps(contract.get_cap_table(), indent=2))

        _section("Period 2: mira goes quiet, orion carries the venture alone")
        _mock_period(
            vm,
            {
                "orion": {"score": 90, "reason": "shipped billing, onboarding, and a mobile fix"},
                "mira": {"score": 0, "reason": "no verifiable public activity this period"},
            },
        )
        contract.recompute_equity()
        print(json.dumps(contract.get_cap_table(), indent=2))

        _section("Nobody filed a claim. The ledger just caught up.")


if __name__ == "__main__":
    main()
