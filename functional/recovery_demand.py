"""All-or-nothing recovery rule encoded in Z3.

The Dutch Tax Authority demanded full-year benefit repayment whenever the
system flagged any irregularity, regardless of the actual error magnitude.
This script captures those rules and demonstrates that the solver can find
such scenarios (SAT) before ethical proportionality constraints are added.
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


def build_recovery_solver() -> Tuple[Solver, RecoveryVariables]:
	"""Create solver preloaded with the all-or-nothing recovery rule."""

	solver = Solver()

	irregularity_type = Int("irregularity_type")
	irregularity_amount = Int("irregularity_amount")
	annual_benefit = Int("annual_benefit")
	demand_amount = Int("demand_amount")
	fsv_flagged = Bool("fsv_flagged")

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

	# All-or-nothing policy: if any irregularity exists (amount > 0), recover
	# the full annual benefit. When no irregularity, demand stays 0.
	solver.add(
		If(irregularity_amount > 0, demand_amount == annual_benefit, demand_amount == 0)
	)

	# Operational practice: FSV blacklist flag automatically set whenever a
	# recovery demand is issued, feeding other pipelines.
	solver.add(fsv_flagged == (demand_amount == annual_benefit))

	# Assert that at least one irregularity exists; ensures SAT baseline.
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
