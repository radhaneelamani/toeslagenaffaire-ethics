"""Proportionality proof: recovery demands always exceed irregularities.

We reuse the operational recovery solver and add a consequentialist
proportionality constraint: recovery demand must not exceed the actual
irregularity amount. Z3 returns UNSAT, proving disproportional harm is baked
into the rule.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple

from z3 import Solver, unsat

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))

from functional.recovery_demand import RecoveryVariables, build_recovery_solver


def build_proportionality_solver() -> Tuple[Solver, RecoveryVariables]:
	solver, vars = build_recovery_solver(name_prefix="rule_")

	# Proportionality requirement: state cannot demand more than the proven
	# irregularity amount.
	solver.add(vars.demand_amount <= vars.irregularity_amount)

	return solver, vars


def main() -> None:
	solver, vars = build_proportionality_solver()
	result = solver.check()

	if result == unsat:
		print("UNSAT: proportionality is impossible under the all-or-nothing rule.")
		print("Demanding the full annual benefit always exceeds the irregularity amount.")
	else:
		print("SAT: unexpected proportional case found — constraints need investigation.")


if __name__ == "__main__":
	main()
