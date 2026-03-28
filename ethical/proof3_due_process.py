"""Formal proof that the system violates GDPR Article 22 requirements."""

from __future__ import annotations

import sys
from pathlib import Path

from z3 import Bool, Solver, unsat, Implies

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.append(str(PROJECT_ROOT))


def build_due_process_solver() -> Solver:
	solver = Solver()

	explanation_provided = Bool("explanation_provided")
	human_review_before_action = Bool("human_review_before_action")
	appeal_pathway_communicated = Bool("appeal_pathway_communicated")

	system_fully_automated = Bool("system_fully_automated")
	explanation_suppressed = Bool("explanation_suppressed")
	appeal_blocked = Bool("appeal_blocked")

	# GDPR Article 22 requirements
	solver.add(Implies(system_fully_automated, explanation_provided == True))
	solver.add(Implies(system_fully_automated, human_review_before_action == True))
	solver.add(Implies(system_fully_automated, appeal_pathway_communicated == True))

	# System operational realities
	solver.add(system_fully_automated == True)
	solver.add(explanation_provided == False)
	solver.add(human_review_before_action == False)
	solver.add(appeal_pathway_communicated == False)

	solver.add(explanation_suppressed == (explanation_provided == False))
	solver.add(appeal_blocked == (appeal_pathway_communicated == False))

	return solver


def main() -> None:
	solver = build_due_process_solver()
	result = solver.check()

	if result == unsat:
		print("UNSAT: system rules contradict GDPR Article 22 due-process duties.")
	else:
		print("SAT: constraints need review—unexpected compatibility detected.")


if __name__ == "__main__":
	main()
