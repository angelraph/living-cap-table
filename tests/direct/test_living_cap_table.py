"""Direct-mode tests for the Living Cap Table contract.

Run with: pytest tests/direct
These run fully in-memory against GenVM (no Studio needed) with web and LLM
calls mocked, so they execute in milliseconds and don't need network access.
"""

import pytest


CONTRACT_PATH = "contracts/living_cap_table.py"


def _to_address(raw_address: bytes):
    """Turn a raw 20-byte test address into the Address type register_contributor expects.

    str(raw_address) would return Python's bytes repr (e.g. "b'+\\xd8...'"),
    not a usable address, so go through hex explicitly. Imported lazily: the
    genlayer SDK only lands on sys.path after the first direct_deploy() call.
    """
    from genlayer.py.types import Address

    return Address("0x" + raw_address.hex())


def test_create_venture_sets_rubric_and_founder(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT_PATH)

    contract.create_venture("equity should track shipped, reviewed code")

    assert contract.get_rubric() == "equity should track shipped, reviewed code"


def test_create_venture_twice_fails(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT_PATH)

    contract.create_venture("first rubric")

    with direct_vm.expect_revert("venture already created"):
        contract.create_venture("second rubric")


def test_register_contributor_before_venture_created_fails(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT_PATH)

    with direct_vm.expect_revert("venture not created yet"):
        contract.register_contributor("agent-a", "agent-a-gh", _to_address(direct_alice))


def test_register_duplicate_handle_fails(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT_PATH)
    contract.create_venture("rubric")
    contract.register_contributor("agent-a", "agent-a-gh", _to_address(direct_alice))

    with direct_vm.expect_revert("handle already registered"):
        contract.register_contributor("agent-a", "agent-a-gh-2", _to_address(direct_alice))


def test_apply_scores_splits_equity_by_judged_score(direct_vm, direct_deploy, direct_alice, direct_bob):
    # recompute_equity()'s LLM-judgment step uses gl.eq_principle.prompt_non_comparative
    # so that validators running genuinely different models don't need byte-identical
    # answers - but this test harness (genlayer-test 0.29) can't mock that call type
    # yet, only gl.eq_principle.strict_eq / gl.nondet.exec_prompt. So this exercises
    # the deterministic half of recompute_equity() directly: _apply_scores() is the
    # part that takes validators' agreed scores and folds them into the ledger, with
    # no gl.eq_principle call in it at all. The judgment step itself is verified
    # against a live deployment instead (see README).
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT_PATH)
    contract.create_venture(
        "equity should track shipped, reviewed code weighted by quality and impact"
    )
    contract.register_contributor("agent-a", "agent-a-gh", _to_address(direct_alice))
    contract.register_contributor("agent-b", "agent-b-gh", _to_address(direct_bob))

    # Validators judge agent-a's work as three times more impactful this period.
    contract._apply_scores(
        ["agent-a", "agent-b"],
        {
            "agent-a": {"score": 75, "reason": "shipped the core feature, reviewed"},
            "agent-b": {"score": 25, "reason": "minor fixes only"},
        },
    )

    cap_table = contract.get_cap_table()
    assert cap_table["agent-a"]["equity_bps"] == 7500
    assert cap_table["agent-b"]["equity_bps"] == 2500
    assert cap_table["agent-a"]["score"] == 75
    assert "core feature" in cap_table["agent-a"]["last_scored_reason"]


def test_apply_scores_is_cumulative_across_periods(direct_vm, direct_deploy, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT_PATH)
    contract.create_venture("rubric")
    contract.register_contributor("agent-a", "agent-a-gh", _to_address(direct_alice))
    contract.register_contributor("agent-b", "agent-b-gh", _to_address(direct_bob))

    # Period 1: even split.
    contract._apply_scores(
        ["agent-a", "agent-b"],
        {
            "agent-a": {"score": 50, "reason": "period 1"},
            "agent-b": {"score": 50, "reason": "period 1"},
        },
    )
    assert contract.get_cap_table()["agent-a"]["equity_bps"] == 5000

    # Period 2: agent-a disappears, agent-b carries everything. The ledger should
    # self-correct without anyone filing a claim.
    contract._apply_scores(
        ["agent-a", "agent-b"],
        {
            "agent-a": {"score": 0, "reason": "no activity this period"},
            "agent-b": {"score": 100, "reason": "carried the venture alone"},
        },
    )

    cap_table = contract.get_cap_table()
    # cumulative: agent-a 50, agent-b 150 -> 25% / 75%
    assert cap_table["agent-a"]["equity_bps"] == 2500
    assert cap_table["agent-b"]["equity_bps"] == 7500


def test_recompute_equity_with_no_contributors_fails(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    contract = direct_deploy(CONTRACT_PATH)
    contract.create_venture("rubric")

    with direct_vm.expect_revert("no contributors registered"):
        contract.recompute_equity()
