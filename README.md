# Toeslagenaffaire — Formal Ethical Verification

This project uses the Z3 constraint solver to show that the Dutch childcare
benefit fraud detection system (Toeslagenaffaire, 2005–2021) was unethical by
design. Instead of simulating sample families, we encode the system's official
rules as satisfiability problems. Functional scripts prove the algorithm works
exactly as specified (SAT). Ethical proofs then add fairness, proportionality,
and due-process requirements; Z3 reports UNSAT, demonstrating these moral and
legal duties are mathematically incompatible with the deployed system.

## Repository Structure

```
toeslagenaffaire-ethics/
├── functional/
│   ├── fraud_scorer.py        # Risk scoring baseline (SAT)
│   └── recovery_demand.py     # All-or-nothing recovery baseline (SAT)
├── ethical/
│   ├── proof1_discrimination.py      # Kantian fairness proof (UNSAT)
│   ├── proof2_disproportionality.py  # Consequentialist proof (UNSAT)
│   └── proof3_due_process.py         # GDPR Article 22 proof (UNSAT)
├── validate_all.py            # Master runner for all scripts
├── evidence/                  # Place screenshots of solver output here
├── requirements.txt
└── README.md
```

## Logical Flow

1. `functional/fraud_scorer.py` encodes the risk scoring rules and proves the
   system can reach "high risk" classifications (SAT).
2. `functional/recovery_demand.py` encodes the all-or-nothing recovery policy
   and proves it can always demand the full annual benefit (SAT).
3. `ethical/proof1_discrimination.py` reuses the fraud constraints, adds a
   Kantian fairness rule (identical applicants differing only in nationality
   must score equally), and shows UNSAT.
4. `ethical/proof2_disproportionality.py` reuses the recovery constraints,
   adds a proportionality rule (demand ≤ irregularity), and shows UNSAT.
5. `ethical/proof3_due_process.py` encodes GDPR Article 22 duties alongside
   the actual automated rules, producing UNSAT.
6. `validate_all.py` runs every script sequentially, printing PASS/FAIL for
   screenshot-ready evidence.

| Script                               | Result | Proof                                     | Ethical School          |
| ------------------------------------ | ------ | ----------------------------------------- | ----------------------- |
| functional/fraud_scorer.py           | SAT    | Risk scoring baseline                     | —                       |
| functional/recovery_demand.py        | SAT    | Recovery baseline                         | —                       |
| ethical/proof1_discrimination.py     | UNSAT  | Fairness impossible with nationality bias | Kantian Deontology      |
| ethical/proof2_disproportionality.py | UNSAT  | Full recovery always exceeds irregularity | Consequentialism        |
| ethical/proof3_due_process.py        | UNSAT  | Automated system violates GDPR Art. 22    | Virtue Ethics / Kantian |

**SAT** (functional scripts) means "the system works as coded." **UNSAT**
(ethical scripts) means "system rules ∧ ethical requirement cannot be satisfied
simultaneously," proving the design itself is incompatible with moral/legal
constraints.

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Proof Suite

```powershell
python validate_all.py
```

The runner prints PASS/FAIL for each script and exits non-zero if any proof
regresses. Individual scripts can be run directly (e.g., `python
functional/fraud_scorer.py`) when you need a focused SAT/UNSAT explanation.

## Sources

- Dutch Parliamentary Inquiry (Kamerstuk 35510), 2023–2024
- Dutch Data Protection Authority FSV Investigation, April 2022
- Amnesty International "Xenophobic Machines," October 2021
- EU AI Act (2024), Article 5 — Prohibited Practices
- ECHR Articles 8 & 14 — SyRI ruling, District Court The Hague, 2020
