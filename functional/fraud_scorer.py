"""Z3 model for the Toeslagenaffaire risk scoring rules.

This script encodes the operational scoring logic that drove the
fraud-detection pipeline. The point is to show that the system can reach a
"high risk" classification (SAT) under its own rules before we layer ethical
constraints elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from z3 import Bool, If, Int, ModelRef, Solver, sat


FRAUD_THRESHOLD = 8
LOW_INCOME_LIMIT = 22_000
MAX_PAYMENT_ERRORS = 5


@dataclass(frozen=True)
class FraudVariables:
    """Typed handle to the Z3 symbols so other scripts can reuse them."""

    income: Int
    payment_errors: Int
    uses_intermediary: Bool
    is_dual_national: Bool
    on_fsv_blacklist: Bool
    risk_score: Int


def build_fraud_solver(name_prefix: str = "") -> Tuple[Solver, FraudVariables]:
    """Create the solver with all baseline constraints for reuse.

    Args:
        name_prefix: Optional prefix applied to every Z3 symbol. Ethical proofs
            can build multiple applicants within the same solver by supplying
            unique prefixes (e.g., "a_", "b_").
    """

    solver = Solver()

    def _name(base: str) -> str:
        return f"{name_prefix}{base}" if name_prefix else base

    income = Int(_name("income"))
    payment_errors = Int(_name("payment_errors"))
    uses_intermediary = Bool(_name("uses_intermediary"))
    is_dual_national = Bool(_name("is_dual_national"))
    on_fsv_blacklist = Bool(_name("on_fsv_blacklist"))
    risk_score = Int(_name("risk_score"))

    vars = FraudVariables(
        income=income,
        payment_errors=payment_errors,
        uses_intermediary=uses_intermediary,
        is_dual_national=is_dual_national,
        on_fsv_blacklist=on_fsv_blacklist,
        risk_score=risk_score,
    )

    # Domain bounds pulled from parliamentary inquiry testimony.
    solver.add(income >= 0, income <= 120_000)
    solver.add(payment_errors >= 0, payment_errors <= MAX_PAYMENT_ERRORS)
    solver.add(risk_score >= 0)

    # Risk score is a weighted sum of opaque heuristics.
    score_expression = (
        If(income < LOW_INCOME_LIMIT, 2, 0)
        + If(is_dual_national, 5, 0)
        + If(on_fsv_blacklist, 6, 0)
        + If(uses_intermediary, 2, 0)
        + payment_errors * 1
    )
    solver.add(risk_score == score_expression)

    # Operational rule: a demand review triggers once the score crosses the
    # fraud threshold. We assert existence of such a case (SAT baseline).
    solver.add(risk_score >= FRAUD_THRESHOLD)

    return solver, vars


def _model_to_dict(model: ModelRef, vars: FraudVariables) -> Dict[str, str]:
    """Return a printable snapshot of the solver model."""

    snapshot: Dict[str, str] = {}
    for field_name, symbol in vars.__dict__.items():
        snapshot[field_name] = str(model.evaluate(symbol, model_completion=True))
    return snapshot


def main() -> None:
    solver, variables = build_fraud_solver()
    result = solver.check()

    if result == sat:
        model = solver.model()
        print("SAT: system can reach a high-risk classification.")
        for name, value in _model_to_dict(model, variables).items():
            print(f"  {name:>18}: {value}")
    else:
        print("UNSAT: risk scoring constraints are inconsistent — unexpected.")


if __name__ == "__main__":
    main()
