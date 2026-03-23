"""Master runner that executes all functional and ethical proofs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent


def _run(command: List[str]) -> Tuple[int, str]:
	result = subprocess.run(command, capture_output=True, text=True)
	return result.returncode, result.stdout + result.stderr


TASKS = [
	("functional/fraud_scorer.py", "SAT"),
	("functional/recovery_demand.py", "SAT"),
	("ethical/proof1_discrimination.py", "UNSAT"),
	("ethical/proof2_disproportionality.py", "UNSAT"),
	("ethical/proof3_due_process.py", "UNSAT"),
]


def main() -> int:
	failures = []

	for script, expected in TASKS:
		command = [sys.executable, str(PROJECT_ROOT / script)]
		code, output = _run(command)

		if code == 0 and expected in output:
			status = "PASS"
		else:
			status = "FAIL"
			failures.append((script, output))

		print(f"{status:>4}  {script}")

	if failures:
		print("\nFailures detected:")
		for script, output in failures:
			print(f"--- {script} ---")
			print(output.rstrip())
		return 1

	return 0


if __name__ == "__main__":
	raise SystemExit(main())
