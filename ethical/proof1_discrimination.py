"""Formal proof that nationality-based scoring violates fairness.

We reuse the operational risk-scoring constraints and add a Kantian fairness
requirement: two identical applicants must receive the same score if
nationality is the only difference. Z3 reports UNSAT, proving the rule
breaks deontological ethics by design.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

from z3 import Solver, unsat

# Ensure the project root (one level up) is on sys.path so that running the
# script directly via ``python ethical/proof1_discrimination.py`` still allows
# absolute imports such as ``functional.fraud_scorer``.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from functional.fraud_scorer import FRAUD_THRESHOLD, FraudVariables, build_fraud_solver


def build_discrimination_solver() -> Tuple[Solver, FraudVariables, FraudVariables]:
    solver = Solver()

    solver_a, applicant_a = build_fraud_solver(name_prefix="a_")
    solver_b, applicant_b = build_fraud_solver(name_prefix="b_")

    solver.add(*solver_a.assertions())
    solver.add(*solver_b.assertions())

    # All features equal except nationality, mirroring parliamentary testimony.
    solver.add(applicant_a.income == applicant_b.income)
    solver.add(applicant_a.payment_errors == applicant_b.payment_errors)
    solver.add(applicant_a.uses_intermediary == applicant_b.uses_intermediary)
    solver.add(applicant_a.on_fsv_blacklist == applicant_b.on_fsv_blacklist)

    solver.add(applicant_a.is_dual_national == False)
    solver.add(applicant_b.is_dual_national == True)

    solver.add(applicant_a.risk_score >= FRAUD_THRESHOLD)
    solver.add(applicant_b.risk_score >= FRAUD_THRESHOLD)

    # Kantian fairness requirement: identical applicants must be treated equally.
    solver.add(applicant_a.risk_score == applicant_b.risk_score)

    return solver, applicant_a, applicant_b


def main() -> None:
    solver, applicant_a, applicant_b = build_discrimination_solver()
    result = solver.check()

    if result == unsat:
        print("UNSAT: system rules and fairness cannot co-exist.")
        print("Two identical applicants differing only by nationality cannot be treated equally.")
    else:
        print("SAT: Unexpectedly found a fair assignment, investigate constraints.")


if __name__ == "__main__":
    main()
