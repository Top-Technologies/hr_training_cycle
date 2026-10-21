# HR Training Cycle: Module Documentation

**Platform:** Odoo 18 (Community and Enterprise)
**Module name:** `hr_training_cycle`
**Depends on:** `hr`, `mail`
**Location in Odoo:** Employees app → **Training** menu

---

## 1. Purpose

The module moves three paper HR forms into Odoo and links them into one training cycle, from the first need to the six-month result:
- **HR-OF-009:** Training Need Assessment (`hr.training.need` with `hr.training.need.line`)
- **HR-OF-010:** Training Attendance (`hr.training.session` with days and attendees)
- **HR-OF-011:** Employee Post Training Evaluation (`hr.training.evaluation` with Part A and Part B)

---

## 2. Process Workflow

1. **Need Assessment (HR-OF-009):** Department head creates training need assessment and submits.
2. **Approve / Refuse:** HR Training Manager reviews and approves or refuses.
3. **Session Planning (HR-OF-010):** HR creates session, adds training dates, links approved need lines.
4. **Attendees & Attendance:** Load attendees directly from linked needs, confirm session, record daily attendance. Print attendance sheet report.
5. **Close Training:** Closing session automatically generates evaluations for attended trainees with direct manager set as evaluator, and creates a to-do for Part A due in 7 days.
6. **Part A (Trainee):** Trainee completes self-evaluation on knowledge gained and application.
7. **Part B (Direct Manager, 6-Month Follow-Up):** Automated daily scheduled action flags 6-month deadline and assigns Part B to direct manager. Manager rates 10 performance criteria (1–4) and logs goal achievement and results. Average score is computed automatically.
8. **HR Review & Employee File:** Smart button and Training tab on the employee form summarize all completed sessions and evaluations.
