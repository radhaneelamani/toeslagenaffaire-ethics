"""All-or-nothing recovery rule encoded in Z3.

This script captures how the Tax Authority demanded full-year benefit
repayment whenever any irregularity was detected, regardless of the actual
error magnitude. Ethical proofs import this baseline to show proportionality
is impossible under the policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from z3 import Bool, If, Int, ModelRef, Solver, sat


ANNUAL_BENEFIT_MIN = 6_000
ANNUAL_BENEFIT_MAX = 30_000
IRREGULARITY_MAX = 5_000


@dataclass(frozen=True)
class RecoveryVariables:
    """Typed wrapper for reuse in ethical proofs."""

    irregularity_type: Int
    irregularity_amount: Int
    annual_benefit: Int
    demand_amount: Int
    fsv_flagged: Bool


def build_recovery_solver(name_prefix: str = "") -> Tuple[Solver, RecoveryVariables]:
    """Create solver preloaded with the all-or-nothing recovery rule.

    Args:
        name_prefix: Optional symbol prefix so ethical proofs can compose
            multiple recovery scenarios inside a single solver.
    """

    solver = Solver()

    def _name(base: str) -> str:
        return f"{name_prefix}{base}" if name_prefix else base

    irregularity_type = Int(_name("irregularity_type"))
    irregularity_amount = Int(_name("irregularity_amount"))
    annual_benefit = Int(_name("annual_benefit"))
    demand_amount = Int(_name("demand_amount"))
    fsv_flagged = Bool(_name("fsv_flagged"))

    vars = RecoveryVariables(
        irregularity_type=irregularity_type,
        irregularity_amount=irregularity_amount,
        annual_benefit=annual_benefit,
        demand_amount=demand_amount,
        fsv_flagged=fsv_flagged,
    )

    solver.add(irregularity_type >= 0, irregularity_type <= 3)
    solver.add(irregularity_amount >= 1, irregularity_amount <= IRREGULARITY_MAX)
    solver.add(annual_benefit >= ANNUAL_BENEFIT_MIN, annual_benefit <= ANNUAL_BENEFIT_MAX)
    solver.add(demand_amount >= 0)

    # All-or-nothing policy: if any irregularity exists, recover the entire annual benefit.
    solver.add(
        If(irregularity_amount > 0, demand_amount == annual_benefit, demand_amount == 0)
    )

    # Operational practice: recovery automatically flags the applicant in the FSV list.
    solver.add(fsv_flagged == (demand_amount == annual_benefit))

    # Baseline assumes at least one irregularity exists so the solver returns SAT.
    solver.add(irregularity_amount >= 1)

    return solver, vars


def _model_to_dict(model: ModelRef, vars: RecoveryVariables) -> Dict[str, str]:
    snapshot: Dict[str, str] = {}
    for field_name, symbol in vars.__dict__.items():
        snapshot[field_name] = str(model.evaluate(symbol, model_completion=True))
    return snapshot


def main() -> None:
    solver, variables = build_recovery_solver()
    result = solver.check()

    if result == sat:
        model = solver.model()
        print("SAT: all-or-nothing recovery produces a demand assignment.")
        for name, value in _model_to_dict(model, variables).items():
            print(f"  {name:>20}: {value}")
    else:
        print("UNSAT: recovery rule is inconsistent — unexpected.")


if __name__ == "__main__":
    main()
