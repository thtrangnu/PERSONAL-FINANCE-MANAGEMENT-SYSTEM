# Business Rules Specification

## 1. Purpose
This document defines the **business rules** that the system must follow. It serves as the bridge between:
- requirements,
- use cases,
- database schema,
- backend logic,
- triggers/procedures/functions.

Without establishing business rules upfront, the system is at risk of:
- drifting from the intended business logic,
- incorrect balance updates,
- incorrect reports,
- incorrect access control,
- data inconsistencies.

---

## 2. General Principles
1. Every piece of financial data must have a clearly identified owner.
2. Every transaction must have a valid value.
3. All money-related changes must be consistently reflected in balances, budgets, and reports.
4. Records that have already generated business events should not be hard-deleted if doing so risks corrupting history.
5. Shared data must be controlled by group membership.

---

# 3. Detailed Business Rules

# 3.1. User Ownership Rules

### BR-01 — Each income belongs to exactly one user
- An income record must have a `user_id`.
- No "ownerless" income may exist.
- Only the owning user may view, edit, or delete that income.

### BR-02 — Each expense belongs to exactly one user
- An expense record must have a `user_id`.
- Only the owning user may operate on that expense.

### BR-03 — Each budget belongs to exactly one user
- Budgets may not be shared between users in the core version.
- A user may not view another user's budget.

### BR-04 — Each bank account belongs to exactly one user
- A bank account or wallet is personal financial property.
- Only the owning user may view and edit it.

### BR-05 — Each alert must be linked to a specific recipient user
- Alerts always have a clearly identified recipient.
- No "orphan" alerts with an unknown owner.

---

# 3.2. Category Rules

### BR-06 — Each income/expense must belong to a valid category
- Both income and expense records must have a valid `category_id`.
- This ensures consistent aggregation in reports by category.

### BR-07 — A category may only be used if it is active
- If a category is deactivated, users may not use it for new income/expense records.
- Existing historical records remain unchanged.

### BR-08 — A category may be personal or system-level
- System categories can be shared across all users.
- Personal categories belong to a single user.
- Categories must also have a `category_type` matching the transaction:
  - income may only use categories of type `income` or `both`,
  - expense may only use categories of type `expense` or `both`.

### BR-09 — Do not hard-delete a category if it is referenced by income/expense/budget
- Use `is_active = false` instead of deletion.
- The goal is to preserve historical data integrity.

---

# 3.3. Income/Expense and Bank Account Rules

### BR-10 — Each income/expense may optionally be linked to a bank account
- A transaction may belong to a specific bank account, e-wallet, or cash wallet.
- If no bank account is linked, the transaction is still valid but does not affect any specific account balance.

### BR-11 — Adding income increases balance
- If income has a `bank_account_id`, the account's balance must increase by exactly `amount`.
- This rule must be applied consistently on creation.

### BR-12 — Adding expense decreases balance
- If expense has a `bank_account_id`, the account's balance must decrease by exactly `amount`.

### BR-13 — Editing income requires adjusting the balance difference
Example:
- old income = 1,000,000
- new income = 1,500,000
- balance must increase by 500,000

If the bank account is changed:
- the old account is reversed by the old amount,
- the new account receives the new amount.

### BR-14 — Editing expense requires adjusting the balance difference
Example:
- old expense = 300,000
- new expense = 250,000
- balance must be credited back 50,000

If the bank account is changed:
- rollback the old account,
- apply to the new account.

### BR-15 — Deleting income/expense linked to a bank account must roll back the balance
- Deleting income => subtract from balance.
- Deleting expense => add back to balance.

### BR-16 — Amount of income/expense must be greater than 0
- Zero or negative amounts are not allowed in standard records.
- If a negative adjustment is needed, use a separate transaction type — do not abuse normal income/expense records.

### BR-17 — Expense date and income date must not be null
- Every transaction must have a date.
- This is required data for daily/monthly/yearly aggregation.

---

# 3.4. Bank Account Rules

### BR-18 — Each bank account has an active/inactive status
- Inactive accounts retain their historical data.
- Inactive accounts should not accept new transactions.

### BR-19 — Account balance must reflect the current state according to system rules
Two common approaches:
1. Store `current_balance` and update via trigger/business logic.
2. Calculate dynamically from `opening_balance + transactions`.

In this project, the preferred approach is:
- store `opening_balance`,
- store `current_balance`,
- ensure `current_balance` is updated consistently by backend/trigger.

### BR-20 — Account number, if stored, should only be stored in masked form
- Do not store the full account number unless necessary.
- Example: `****1234`.

---

# 3.5. Budget Rules

### BR-21 — A budget may be an overall budget or a category budget
- `budget_scope = overall` means the spending limit applies to all expenses in the month.
- `budget_scope = category` means the limit applies only to a specific category.

### BR-22 — A budget must be tied to a clear time period
- At minimum, must have `period_month` and `period_year`.
- Budgets without a defined time period are not valid.

### BR-23 — A category budget must have a category_id
- If scope is `category` and `category_id` is missing, the budget is invalid.

### BR-24 — An overall budget does not require a category_id
- Because it manages the total monthly spending.

### BR-25 — Spending limit must be greater than 0
- Budgets with a zero or negative limit are not allowed.

### BR-26 — Warning percent must be within a valid range
Recommended:
- between 1 and 100.
- Common values: 70, 80, 90.

### BR-27 — Expenses counted toward a budget must fall within the budget period
- Only expenses with a date within the budget's month/year are counted toward usage.

### BR-28 — Budget usage must be updated when expenses change
Operations that affect usage:
- adding an expense,
- editing an expense,
- deleting an expense,
- changing the category,
- moving the date to a different month.

### BR-29 — A user should not have 2 active budgets with overlapping logic in the same period
Examples of what should not exist:
- two overall budgets both active for May 2026,
- or two category budgets for the same "dining" category both active for May 2026.

This can be enforced via a business-level uniqueness rule.

---

# 3.6. Alert Rules

### BR-30 — An alert must be created when spending exceeds a budget threshold
- If usage >= warning threshold, create a warning alert.
- If usage > limit, create an exceeded alert.

### BR-31 — Do not create infinite duplicate alerts for the same condition
Example:
- If a "100% budget exceeded" alert already exists for this month's budget, do not generate more duplicates on every refresh.

A deduplication mechanism is needed:
- keyed by `budget_id + alert_type + period + severity`.

### BR-32 — Alerts must be classified by severity
Suggested levels:
- info
- warning
- critical

### BR-33 — Alerts have read/unread status
- New alerts default to unread.
- Users can mark alerts as read.

### BR-33A — Each alert should reference only one related object
- Budget alerts should only use `related_budget_id`.
- Debt alerts should only use `related_debt_id`.
- A single alert should not reference multiple objects simultaneously.

---

# 3.7. Debt Rules

### BR-34 — A debt has one of: pending / partially_paid / paid / overdue
Core statuses:
- pending
- partially_paid
- paid
- overdue

### BR-35 — Debt original_amount must be > 0
- Every debt must have a valid principal amount.

### BR-36 — Remaining amount must not be negative
- After summing all payments, the remaining amount must not fall below 0.
- If a user overpays, the system must block or require adjustment.

### BR-37 — A debt payment must belong to a specific debt
- No standalone payments that are unlinked to a debt.

### BR-38 — If remaining_amount = 0, the debt transitions to paid
- The status update rule must be automatic or semi-automatic.

### BR-39 — If past due_date with remaining_amount > 0, the debt may become overdue
- This rule may be checked by a daily background job.

---

# 3.8. Sharing Group Rules

### BR-40 — Shared transactions are only visible to group members
- This is the most critical rule in the sharing module.

### BR-41 — Each shared transaction must belong to a specific group
- No "free-floating" shared transactions.

### BR-42 — Only valid members may view a group's transactions
- If a user is not in `GroupMembers`, access must be denied.

### BR-43 — Only the group owner/admin may manage members
- Adding/removing members requires explicit permission.

### BR-43A — Invited members must confirm before joining the group
- When an owner invites a user, the system creates a `pending` status.
- The invited user must accept or decline.
- Only members with `active` status may view and share transactions in the group.

### BR-44 — Personal transactions do not automatically become shared transactions
- The user must explicitly mark a transaction as shared or create a linking share record.

### BR-44A — A shared transaction may only reference one type of source transaction
- Only one of `expense_id` or `income_id` may have a value.
- Both may not be set simultaneously.
- Both may not be null simultaneously.

---

# 3.9. Deletion Rules

### BR-45 — Avoid hard-deleting important financial data
Soft delete recommended for:
- categories,
- bank accounts,
- budgets,
- alerts,
- debts.

### BR-46 — Hard-deleting income/expense must ensure business rollback
- Adjust balance.
- Adjust budget usage.
- Update report cache if applicable.

### BR-47 — Do not delete a user with financial data without a clear policy
- Lock the account instead of physically deleting it.

---

# 3.10. Reporting Rules

### BR-48 — Daily/Monthly/Yearly summary only counts data for the current user
- Do not aggregate data across multiple users.

### BR-49 — Reports must be based on valid, active transactions
- Do not include records marked as invalid/inactive if the system uses such statuses.

### BR-50 — Category reports only count expenses with a valid category
- If a category is deactivated later, historical records may still be included, depending on the agreed reporting rule.

### BR-51 — Dashboard data must be near real-time
- Dashboard must refresh when transactions change.

---

# 3.11. Security and Data Access Rules

### BR-52 — Users must not specify another user's `user_id` to operate on data
- The backend must extract the user from the session/token — not from client payload.

### BR-53 — All API/query operations must always filter by owner
- This is a mandatory technical rule derived from the business rule above.

### BR-54 — Exports may only include data the user is authorized to access
- Export files must not contain another user's data.

---

# 3.12. Audit/Logging Rules

### BR-55 — Important actions should be logged
Including:
- failed/successful logins,
- creating/editing/deleting transactions,
- budget changes,
- backup runs,
- recovery operations,
- critical system errors.

### BR-56 — Background tasks that generate alerts/backups should leave an execution trace
- Log the run time,
- success/failure result,
- error message if any.

---

## 4. Business Examples

### Example 1 — Adding an expense with bank account and budget
- User A has a bank account with balance = 5,000,000.
- User A has a dining budget for April of 2,000,000.
- Total dining expenses in April so far: 1,700,000.
- User A adds a dining expense of 400,000 on 2026-04-10.

**Expected result:**
- expense is saved,
- account balance becomes 4,600,000,
- budget usage becomes 2,100,000,
- system creates a "budget exceeded" alert.

### Example 2 — Editing an expense and changing the account
- Old expense = 300,000 linked to account A.
- User edits to 300,000 linked to account B.

**Expected result:**
- account A is credited back 300,000,
- account B is debited 300,000.

### Example 3 — Overdue debt
- Debt remaining amount = 2,000,000.
- Due date = 2026-04-01.
- Today = 2026-04-04.
- No new payment has been made.

**Expected result:**
- debt status may transition to overdue,
- system creates an overdue alert if this module is enabled.

---

## 5. Conclusion
Business rules are the anchor that ensures the database design and Django code stay aligned. In this project, the 4 most important rules to always remember are:

1. **Every piece of financial data must have a clearly identified owner.**
2. **Income increases balance; expense decreases balance.**
3. **Budget must be checked every time an expense changes.**
4. **Shared transactions are only visible to the correct group members.**

Once this document is finalized, the next steps are to draw use cases, create the ERD, and design the detailed logical schema.
