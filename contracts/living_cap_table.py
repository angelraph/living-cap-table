# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from dataclasses import dataclass
from genlayer import *


@allow_storage
@dataclass
class Contributor:
    github_handle: str
    wallet: Address
    score: u256  # cumulative contribution score, arbitrary units, comparable only within this venture
    equity_bps: u256  # current equity share, in basis points (0-10000)
    last_scored_reason: str  # validators' most recent rationale for this contributor's last score


class LivingCapTable(gl.Contract):
    """Equity that's read, not negotiated.

    A venture's founder defines an equity rubric in plain language. Contributors
    register their public GitHub handle. Anyone can call recompute_equity(), which
    has GenLayer's validators pull each contributor's real public activity, judge it
    against the rubric for quality and impact (not raw event count), and reach
    consensus on a contribution score for the period. Equity is recomputed directly
    from that score. Nobody self-reports, nobody votes, and there is nothing to
    dispute because the ledger is never wrong long enough to need fixing.
    """

    founder: Address
    rubric: str
    created: bool
    handles: DynArray[str]
    contributors: TreeMap[str, Contributor]

    def __init__(self):
        self.created = False

    @gl.public.write
    def create_venture(self, rubric: str) -> None:
        if self.created:
            raise Exception("venture already created")
        self.founder = gl.message.sender_address
        self.rubric = rubric
        self.created = True

    @gl.public.write
    def register_contributor(self, handle: str, github_handle: str, wallet: str) -> None:
        if not self.created:
            raise Exception("venture not created yet")
        if handle in self.contributors:
            raise Exception("handle already registered")
        self.contributors[handle] = Contributor(
            github_handle=github_handle,
            wallet=Address(wallet),
            score=u256(0),
            equity_bps=u256(0),
            last_scored_reason="",
        )
        self.handles.append(handle)

    @gl.public.write
    def recompute_equity(self) -> None:
        if not self.created:
            raise Exception("venture not created yet")
        if len(self.handles) == 0:
            raise Exception("no contributors registered")

        handles = list(self.handles)
        github_by_handle = {h: self.contributors[h].github_handle for h in handles}
        rubric = self.rubric

        # Step 1: pull each contributor's real, public activity. This is a plain
        # fetch (not a subjective judgment), so validators reach consensus on the
        # exact bytes returned.
        def fetch_evidence() -> str:
            evidence = {}
            for handle, gh in github_by_handle.items():
                url = f"https://api.github.com/users/{gh}/events/public"
                web_data = gl.nondet.web.render(url, mode="text")
                evidence[handle] = web_data[:4000]
            return json.dumps(evidence, sort_keys=True)

        evidence_json = gl.eq_principle.strict_eq(fetch_evidence)

        content_payload = json.dumps(
            {"rubric": rubric, "evidence": json.loads(evidence_json)},
            sort_keys=True,
        )

        task = (
            "The content is JSON with a \"rubric\" (the plain-language equity rubric "
            "for this venture) and \"evidence\" (each contributor's recent public "
            "GitHub activity, keyed by internal handle).\n\n"
            "For every internal handle present in \"evidence\", assign an integer "
            "contribution score from 0 to 100 for this period, judging real shipped "
            "or reviewed quality and impact against the rubric - not raw event count. "
            "Padding activity with trivial or low-quality commits must not raise a "
            "score. Briefly justify each score in one short phrase."
        )
        criteria = (
            "The output must be valid JSON containing exactly the internal handles "
            "present in \"evidence\" as keys, each mapped to an object of the form "
            "{\"score\": int between 0 and 100, \"reason\": str}. Scores must reflect "
            "judged quality and impact rather than activity volume - two contributors "
            "with the same number of events should not receive the same score if one "
            "shipped substantive, reviewed work and the other did not."
        )

        # Step 2: this is the subjective call (was the work actually good?), so it
        # uses non-comparative consensus - validators judge the leader's answer
        # against the criteria instead of requiring byte-identical output.
        result_text = gl.eq_principle.prompt_non_comparative(
            lambda: content_payload,
            task=task,
            criteria=criteria,
        )

        scores = json.loads(result_text)

        total = 0
        for handle in handles:
            c = self.contributors[handle]
            entry = scores.get(handle, {"score": 0, "reason": ""})
            gained = int(entry.get("score", 0))
            c.score = u256(int(c.score) + gained)
            c.last_scored_reason = str(entry.get("reason", ""))
            total += int(c.score)

        if total == 0:
            return

        for handle in handles:
            c = self.contributors[handle]
            c.equity_bps = u256((int(c.score) * 10000) // total)

    @gl.public.view
    def get_cap_table(self) -> dict:
        return {
            handle: {
                "github_handle": self.contributors[handle].github_handle,
                "wallet": self.contributors[handle].wallet.as_hex,
                "score": int(self.contributors[handle].score),
                "equity_bps": int(self.contributors[handle].equity_bps),
                "equity_pct": round(int(self.contributors[handle].equity_bps) / 100, 2),
                "last_scored_reason": self.contributors[handle].last_scored_reason,
            }
            for handle in self.handles
        }

    @gl.public.view
    def get_rubric(self) -> str:
        return self.rubric
