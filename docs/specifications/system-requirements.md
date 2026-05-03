# System Requirements — Personal Finance Management System

## 1. Purpose
This document describes the functional and non-functional requirements of the **NUFI** system in detail. The goal is to align the team on:
- what the system needs to do,
- the priority of each feature,
- the MVP scope vs. extension scope,
- acceptance and test criteria.

---

## 2. Requirements Scope
The system is a web application that helps individual users manage their personal finances daily, covering:
- personal profile management,
- recording income and expenses,
- managing income and expense categories,
- bank account tracking,
- budget planning,
- receiving alerts,
- viewing table/chart reports,
- extensions into debt tracking, sharing groups, file exports, and cloud sync.

---

## 3. Requirement Categories
This document divides requirements into 4 groups:
1. **Functional Requirements (FR)** — what the system must do.
2. **Non-functional Requirements (NFR)** — how the system must perform.
3. **Business Constraints / Assumptions** — constraints and assumptions.
4. **Acceptance Criteria** — criteria for sign-off.

---

## 4. Functional Requirements (FR)

# 4.1. Account and Authentication Requirements

### FR-01 — User Registration
The system must allow guests to register a new account.

**Input:**
- full_name
- email
- username (if used)
- password
- confirm_password

**Processing:**
- Check that email/username does not already exist.
- Validate email format.
- Validate minimum password requirements.
- Create a new user account.

**Output:**
- Success message or detailed error.

**Priority:** High.

---

### FR-02 — User Login
The system must allow users to log in with valid credentials.

**Input:**
- email or username
- password

**Processing:**
- Check that the account exists.
- Verify the password.
- Check that the account is active.

**Output:**
- Create a login session and redirect to dashboard.

**Priority:** High.

---

### FR-03 — User Logout
The system must allow users to log out safely.

**Priority:** High.

---

### FR-04 — Manage Profile
The system must allow users to view and update their personal profile.

**Editable fields:**
- full name
- phone number
- avatar
- gender (optional)
- date of birth (optional)
- timezone (optional)
- default currency (optional)

**Priority:** High.

---

### FR-05 — Change Password
Users must be able to change their password after verifying the old password.

**Priority:** Medium.

---

### FR-06 — Google Login (future extension)
The system may support Google login in an extension phase.

**Priority:** Low / later.

---

# 4.2. Income Management Requirements

### FR-07 — Create Income
Users must be able to create an income record.

**Minimum attributes:**
- user
- title / description
- amount
- income_date
- category
- bank_account (optional)
- note

**Processing:**
- Validate amount > 0.
- Validate category is valid for income (`income` or `both`).
- If a bank account is linked, increase balance accordingly.
- Log the transaction.

**Priority:** High.

---

### FR-08 — Update Income
Users must be able to edit their own income records.

**Processing:**
- If the amount or bank account changes, the balance must be adjusted correctly.

**Priority:** High.

---

### FR-09 — Delete Income
Users must be able to delete their own income records.

**Processing:**
- If the income has been added to a bank account balance, the balance must be rolled back.
- Soft delete is recommended to preserve history.

**Priority:** Medium.

---

### FR-10 — View Income List
Users must be able to view their own income list.

**Filters:**
- by date
- by month
- by year
- by category
- by bank account

**Sorting:**
- newest first
- oldest first
- ascending/descending amount

**Priority:** High.

---

# 4.3. Expense Management Requirements

### FR-11 — Create Expense
Users must be able to create an expense record.

**Minimum attributes:**
- user
- category
- amount
- expense_date
- description
- bank_account (optional)
- payment_method (cash/bank/e-wallet/other)
- note

**Processing:**
- Validate amount > 0.
- If a bank account is linked, decrease balance accordingly.
- Trigger budget check.
- Create an alert if threshold is exceeded.

**Priority:** High.

---

### FR-12 — Update Expense
Users must be able to edit their own expense records.

**Processing:**
- If amount, category, or bank account changes, the system must re-adjust balance and budget usage.

**Priority:** High.

---

### FR-13 — Delete Expense
Users must be able to delete their own expense records.

**Processing:**
- If this expense had been subtracted from a balance, it must be credited back.
- If this expense affected a budget, the budget usage must be updated.

**Priority:** Medium.

---

### FR-14 — View Expense List
Users must be able to view their own expense list.

**Filters:**
- by date/month/year
- by category
- by bank account
- by payment method
- by amount range

**Priority:** High.

---

# 4.4. Category Management Requirements

### FR-15 — Create Category
Users must be able to create categories for classifying income and expenses.

**Attributes:**
- category_name
- category_type (income / expense / both)
- color
- icon
- description
- is_default
- is_active

**Priority:** High.

---

### FR-16 — Update Category
Users must be able to edit their own categories or permitted categories.

**Priority:** High.

---

### FR-17 — Disable Category
Users/admins must be able to deactivate a category instead of hard-deleting it.

**Reason:**
- prevents corrupting old expense history.

**Priority:** Medium.

---

### FR-18 — View Categories
Users must be able to view the list of active categories within their permitted scope.

**Priority:** High.

---

# 4.5. Bank Account Management Requirements

### FR-19 — Create Bank Account
Users must be able to create a bank account, e-wallet, or cash wallet.

**Attributes:**
- account_name
- account_type
- provider_name
- account_number_masked (optional)
- current_balance
- currency
- note

**Priority:** High.

---

### FR-20 — Update Bank Account
Users must be able to edit their own bank account information.

**Note:**
- if opening balance or current balance is edited, a clear control mechanism is required.

**Priority:** High.

---

### FR-21 — View Bank Accounts
Users must be able to view their account list along with current balances.

**Priority:** High.

---

### FR-22 — View Account Transactions
Users must be able to view income/expense records linked to each bank account.

**Priority:** Medium.

---

# 4.6. Budget Management Requirements

### FR-23 — Create Overall Budget
Users must be able to create an overall budget for a specific month.

**Attributes:**
- budget_name
- period_month
- period_year
- spending_limit
- warning_percent

**Priority:** High.

---

### FR-24 — Create Category Budget
Users must be able to create a budget for a specific category within a month.

**Attributes:**
- category
- month/year
- spending_limit

**Priority:** High.

---

### FR-25 — Track Budget Usage
The system must automatically calculate total spending within a budget's scope.

**Output:**
- amount_used
- amount_remaining
- usage_percent
- over_limit_flag

**Priority:** High.

---

### FR-26 — Update Budget
Users must be able to edit budget limits and alert thresholds.

**Priority:** Medium.

---

### FR-27 — Disable Budget
Users must be able to close or deactivate old budgets.

**Priority:** Medium.

---

# 4.7. Alert Requirements

### FR-28 — Generate Spending Alert
The system must create an alert when:
- usage reaches the warning threshold (e.g., 80%).
- usage exceeds the budget limit (100%+).

**Alert types:**
- budget_warning
- budget_exceeded
- debt_overdue
- system_info

**Priority:** High.

---

### FR-29 — View Alerts
Users must be able to view their own alerts.

**Priority:** High.

---

### FR-30 — Mark Alert as Read
Users must be able to mark an alert as read.

**Priority:** Medium.

---

# 4.8. Reports and Dashboard Requirements

### FR-31 — Daily Summary
The system must provide a daily summary.

**Content:**
- total income for the day
- total expenses for the day
- net cash flow for the day

**Priority:** High.

---

### FR-32 — Monthly Summary
The system must provide a monthly summary.

**Content:**
- total income for the month
- total expenses for the month
- top spending category
- end-of-month balance (estimated or by account)

**Priority:** High.

---

### FR-33 — Yearly Summary
The system must provide a yearly summary.

**Priority:** Medium to High.

---

### FR-34 — Graphical Reports
The system must display chart-based reports such as:
- pie chart by category
- bar chart by month
- line chart of income/expense trends

**Priority:** High.

---

### FR-35 — Tabular Reports
The system must display table-based reports with filtering and sorting support.

**Priority:** High.

---

### FR-36 — Dashboard Overview
The dashboard must display at a glance:
- total balance across all accounts
- total income this month
- total expenses this month
- remaining budget
- recent transactions
- unread alerts

**Priority:** High.

---

# 4.9. Debt Management Requirements (Extension)

### FR-37 — Create Debt
Users must be able to record a debt.

**Classification:**
- money they owe someone else
- money someone else owes them

**Attributes:**
- debt_type
- counterparty_name
- original_amount
- due_date
- status
- note

**Priority:** Phase 2.

---

### FR-38 — Record Debt Payment
Users must be able to record debt payment history.

**Priority:** Phase 2.

---

### FR-39 — Debt Status Tracking
The system must determine status:
- pending
- partially_paid
- paid
- overdue

**Priority:** Phase 2.

---

# 4.10. Sharing Group Requirements (Extension)

### FR-40 — Create Group
Users must be able to create a financial sharing group.

**Priority:** Phase 2.

---

### FR-41 — Invite / Add Group Members
Group owners must be able to invite members. Invited users must confirm before becoming official members.

**Priority:** Phase 2.

---

### FR-42 — Share Transactions
Users must be able to mark selected transactions as shared within a group.

**Priority:** Phase 2.

---

### FR-43 — Restrict Group Visibility
Only group members may view shared transactions within that group.

**Priority:** Phase 2.

---

# 4.11. Export and Cloud Sync Requirements

### FR-44 — Export Excel
Users must be able to export reports to Excel.

**Priority:** Phase 2.

---

### FR-45 — Export PDF
Users must be able to export reports to PDF.

**Priority:** Phase 2.

---

### FR-46 — Scheduled Backup
The system must support periodic backups.

**Priority:** High for infrastructure; minimal demo implementation acceptable.

---

### FR-47 — Cloud Sync
The system may support syncing data/backup files to the cloud.

**Priority:** Phase 2.

---

# 4.12. Admin Requirements

### FR-48 — Admin Manage Users
Admin must be able to view user list, activate/deactivate accounts, and check status.

**Priority:** High.

---

### FR-49 — Admin Manage Default Categories
Admin must be able to manage the system's default categories.

**Priority:** Medium.

---

### FR-50 — Admin View Logs
Admin must be able to view system logs, login logs, error logs, and background task logs.

**Priority:** Medium.

---

## 5. Non-Functional Requirements (NFR)

### NFR-01 — Security
- Each user may only access their own data.
- All routes must enforce authentication/authorization.
- Passwords must be hashed.
- Sensitive IDs must not be exposed without access control.
- CSRF protection for web forms.
- Input validation on all entry points.

### NFR-02 — Performance
- Commonly used transaction list queries must respond well.
- Index frequently filtered columns: user_id, date, category_id, bank_account_id, status.
- Monthly/yearly reports must be optimized with aggregate queries or views.

### NFR-03 — Reliability
- The system must minimize data loss on failure.
- Balance changes must be consistent.
- Create/update/delete transaction operations should run within safe transactions.

### NFR-04 — Scalability
- New modules (debts, sharing, exports) can be added without breaking the existing schema.
- Services can be separated if needed in the future.

### NFR-05 — Maintainability
- Code is clearly organized by Django app module.
- Schema uses consistent naming conventions.
- Documentation covers tables, rules, APIs, and workflows.

### NFR-06 — Usability
- The interface must be easy to understand for general users.
- Input forms must clearly indicate required vs. optional fields.
- Dashboard and reports must be easy to read.

### NFR-07 — Backup & Recovery
- Periodic DB backups.
- Data recovery documentation.
- Backup files stored securely.

### NFR-08 — Auditability
- Important changes should be logged.
- Alerts and automated tasks must be traceable to their source.

---

## 6. Business Constraints / Assumptions
- The system serves individual users, not complex corporate accounting.
- Bank account data is initially entered manually by users.
- No live banking API integration in the first version.
- One expense belongs to exactly one primary category.
- One income/expense may be linked to one bank account or none.
- Current balance is data that the system can compute from transactions or update via a consistent rule.
- Budgets prioritize monthly cycles in the first version.
- Default currency is a single currency per user in the first version.

---

## 7. In-Scope / Out-of-Scope Summary

### 7.1. In-Scope
- user profile management
- income/expense entry
- bank account tracking
- daily/monthly/yearly summaries
- budget planning
- spending limit alerts
- graphical and tabular reports
- indexes/views/procedures/functions/triggers
- security, backup, recovery
- debt tracking (phase 2 if time permits)
- sharing groups (phase 2 if time permits)
- export Excel/PDF (phase 2 if time permits)
- cloud sync (phase 2)

### 7.2. Out-of-Scope
- live banking integration
- AI financial prediction
- OCR receipt scan
- real-time multi-currency exchange engine
- full native mobile app

---

## 8. Acceptance Criteria

### 8.1. MVP Acceptance Criteria
The project is considered to have reached MVP if:
1. Users can register, log in, and update their profile.
2. Users can CRUD income.
3. Users can CRUD expenses.
4. Users can CRUD categories.
5. Users can CRUD bank accounts.
6. Users can create and track a budget.
7. The system generates an alert when spending exceeds a threshold.
8. Dashboard displays overview information.
9. Daily/monthly/yearly reports work.
10. User data is correctly isolated from other users.

### 8.2. Database Acceptance Criteria
1. Clear relational schema.
2. Complete PK/FK definitions.
3. Indexes on main tables.
4. At least one view.
5. At least one procedure or function.
6. At least one trigger related to balance/alert/log.

### 8.3. Deployment Acceptance Criteria
1. Application runs with Docker.
2. MySQL connection is successful.
3. At least one CronJob / scheduled task is described or demonstrated.
4. Backup/recovery plan is in place.

---

## 9. Implementation Priority

### Priority 1 — Must Have
- auth
- profile
- categories
- income
- expenses
- bank accounts
- budgets
- alerts
- dashboard
- reports
- DB schema
- basic security

### Priority 2 — Should Have
- admin logs
- export Excel/PDF
- debt tracking
- complete views/procedures/functions/triggers
- backup automation

### Priority 3 — Nice to Have (if time allows)
- sharing groups
- advanced cloud sync
- Google login
- advanced reports

---

## 10. Conclusion
This requirements document is the basis for the team to proceed to:
- finalize actors and permissions,
- finalize modules,
- write business rules,
- draw use cases,
- draw ERD,
- design relational schema,
- then move to Django code and database implementation.

The more clearly requirements are defined early, the less drift there will be when implementing code, UI, and the database.
