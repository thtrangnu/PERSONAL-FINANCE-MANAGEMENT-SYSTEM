# Business Modules Specification

## 1. Purpose
This document divides the system into specific business modules to:
- facilitate task assignment,
- facilitate schema and API design,
- facilitate coding by Django app,
- clearly identify what to build first vs. what to extend later.

Confirmed modules:
- accounts
- income
- expenses
- categories
- bank_accounts
- budgets
- alerts
- debts
- sharing
- reports
- exports
- dashboard

---

## 2. Module Design Principles
Each module must clearly define:
1. **Module purpose**
2. **Main features**
3. **Data managed by the module**
4. **Dependencies on other modules**
5. **Whether it belongs to MVP or a later phase**

---

# 3. Detailed Module Descriptions

# 3.1. accounts

## Purpose
Manages users, authentication, and personal profiles.

## Main Features
- Registration.
- Login.
- Logout.
- View personal profile.
- Update profile.
- Change password.
- Manage account status.
- Extension: Google login.

## Primary Data
- Users
- UserProfile (if separated)
- Login logs (if implemented)

## Typical Inputs
- email/username
- password
- profile fields

## Typical Outputs
- session/token
- profile summary
- authentication status

## Dependencies
- Does not depend on other business modules.
- It is the foundation module for the entire system.

## Priority
**Required in version 1.**

---

# 3.2. income

## Purpose
Manages income transactions for users.

## Main Features
- Create an income record.
- Edit income.
- Delete income.
- View income list.
- Filter by date.
- Filter by category.
- Filter by bank account.

## Primary Data
- Incomes
- Categories
- Related to Users
- May relate to BankAccounts

## Key Income Attributes
- user_id
- category_id
- title
- amount
- income_date
- bank_account_id
- description
- note
- created_at
- updated_at

## Main Business Flow
1. User creates income.
2. System validates data.
3. Saves record to the incomes table.
4. If income is linked to a bank account, increase balance.
5. Transaction appears in dashboard/reports.

## Dependencies
- accounts
- bank_accounts (if account is linked)
- reports

## Priority
**Required in version 1.**

---

# 3.3. expenses

## Purpose
Manages expense transactions for users.

## Main Features
- Create an expense.
- Edit an expense.
- Delete an expense.
- View expense list.
- Filter by category.
- Filter by date.
- Filter by bank account.
- Track transaction history.

## Primary Data
- Expenses
- Users
- Categories
- BankAccounts

## Key Expense Attributes
- user_id
- category_id
- amount
- expense_date
- description
- bank_account_id
- payment_method
- note
- created_at
- updated_at

## Main Business Flow
1. User enters an expense.
2. System validates amount/category/user ownership.
3. If a bank account is linked, deduct balance.
4. System checks budget.
5. If threshold exceeded, generate alert.
6. Expense appears in dashboard/reports.

## Dependencies
- accounts
- categories
- bank_accounts
- budgets
- alerts
- reports

## Priority
**Required in version 1.**

---

# 3.4. categories

## Purpose
Manages categories used for both income and expenses.

## Main Features
- Create personal categories.
- Edit categories.
- Deactivate categories.
- View category list.
- Support for default system categories.
- Classify categories as income / expense / both.

## Primary Data
- Categories

## Key Attributes
- user_id (nullable for default/system categories)
- category_name
- category_type
- description
- color
- icon
- is_default
- is_active
- created_at
- updated_at

## Role in the System
- Standardizes classification of income and expenses.
- Input for reports.
- Foundation for category budgets.

## Dependencies
- accounts
- expenses
- budgets
- reports

## Priority
**Required in version 1.**

---

# 3.5. bank_accounts

## Purpose
Tracks where users hold their money: bank accounts, e-wallets, and cash wallets.

## Main Features
- Create a bank account.
- Edit a bank account.
- View balance.
- View related transactions.
- Activate/deactivate an account.

## Primary Data
- BankAccounts

## Key Attributes
- user_id
- account_name
- account_type
- provider_name
- account_number_masked
- currency
- opening_balance
- current_balance
- is_active
- created_at
- updated_at

## Main Business Flow
1. User creates an account.
2. Income/expense can reference this account.
3. Balance increases/decreases according to transactions.
4. Dashboard pulls total balance from this module.

## Dependencies
- accounts
- income
- expenses
- reports

## Priority
**Required in version 1.**

---

# 3.6. budgets

## Purpose
Manages spending plans and budget limits.

## Main Features
- Create an overall monthly budget.
- Create a category budget.
- Edit a budget.
- Close a budget.
- Track amount used / remaining / usage %.
- Trigger alert logic when threshold is exceeded.

## Primary Data
- Budgets

## Key Attributes
- user_id
- budget_name
- budget_scope (overall/category)
- category_id (nullable)
- period_month
- period_year
- spending_limit
- warning_percent
- status
- created_at
- updated_at

## Main Business Flow
1. User creates an overall monthly budget or a category budget.
2. Each new expense is compared against the relevant budget.
3. If usage >= warning threshold, generate a warning alert.
4. If usage > limit, generate a budget exceeded alert.

## Dependencies
- accounts
- expenses
- categories
- alerts
- reports

## Priority
**Required in version 1.**

---

# 3.7. alerts

## Purpose
Notifies users when attention-worthy events occur.

## Main Features
- Create alerts for budget exceeded.
- Create alerts for nearing the budget.
- Create debt overdue alerts (later phase).
- Mark as read.
- View alert list.

## Primary Data
- Alerts

## Key Attributes
- user_id
- alert_type
- title
- message
- related_budget_id
- related_expense_id
- related_debt_id
- is_read
- severity
- created_at

## Alert Sources
- budget checks when adding/editing expenses
- periodic jobs via Django management commands or Kubernetes CronJob
- debt overdue checker

## Dependencies
- accounts
- budgets
- expenses
- debts

## Priority
**Minimum required in version 1.**

---

# 3.8. debts

## Purpose
Manages debt records and payment history.

## Main Features
- Create a debt.
- Update a debt.
- Record a payment for a debt.
- Track due dates.
- Calculate remaining balance.
- Identify overdue status.

## Primary Data
- Debts
- DebtPayments

## Key Debt Attributes
- user_id
- debt_type
- counterparty_name
- original_amount
- remaining_amount
- due_date
- status
- description
- created_at
- updated_at

## Key Debt Payment Attributes
- debt_id
- payment_date
- amount
- bank_account_id
- note

## Dependencies
- accounts
- bank_accounts
- alerts
- reports

## Priority
**Build after the core is stable.**

---

# 3.9. sharing

## Purpose
Allows a group of users to share a portion of their financial data.

## Main Features
- Create a group.
- Invite members.
- Manage members.
- Attach shared transactions to the group.
- View shared transactions within the group.

## Primary Data
- Groups
- GroupMembers
- SharedTransactions

## Use Cases
Suitable for scenarios such as:
- housemates,
- travel groups,
- families tracking shared expenses,
- project teams managing a shared fund.

## Dependencies
- accounts
- expenses/income (if sharing is supported)
- reports

## Priority
**Build after the core version is complete.**

---

# 3.10. reports

## Purpose
Generates reports for tracking and analysis.

## Main Features
- Daily report.
- Monthly report.
- Yearly report.
- Report by category.
- Report by bank account.
- Table-based reports.
- Chart-based reports.

## Data Sourced From
- incomes
- expenses
- categories
- bank_accounts
- budgets
- debts (if extended)

## Typical Output
- total income
- total expenses
- net cash flow
- top spending categories
- spending trend over time

## Dependencies
- depends on nearly all core modules.

## Priority
**Required in version 1.**

---

# 3.11. exports

## Purpose
Exports data and reports to files for storage or sharing.

## Main Features
- Export to Excel.
- Export to PDF.
- Export monthly/yearly reports.
- Export transaction lists.

## Data Sourced From
- reports
- incomes
- expenses
- budgets

## Dependencies
- reports
- dashboard

## Priority
**Build after the core or minimally if time allows.**

---

# 3.12. dashboard

## Purpose
Provides the fastest high-level view of the current financial situation.

## Main Features
- Display total balance.
- Display this month's income.
- Display this month's expenses.
- Display recent transactions.
- Display budget progress.
- Display unread alerts.
- Display quick charts.

## Data Sourced From
- bank_accounts
- incomes
- expenses
- budgets
- alerts

## Role
- The screen users see most often after logging in.
- The visual hub connecting all modules.

## Priority
**Required in version 1.**

---

## 4. Module Dependency Graph

### Foundation Modules
- accounts
- categories
- bank_accounts

### Core Transaction Modules
- income
- expenses

### Financial Control Modules
- budgets
- alerts

### Display and Output Modules
- dashboard
- reports
- exports

### Extension Modules
- debts
- sharing

---

## 5. Version 1 Module Priorities
Modules required in the first version:
1. accounts / profile
2. income
3. expenses
4. categories
5. bank_accounts
6. budgets
7. reports
8. dashboard
9. alerts (at least basic)

### Why these modules for version 1
- Sufficient to demonstrate the main business logic.
- Sufficient to design the core schema.
- Sufficient to demo CRUD + dashboard + reports.
- Sufficient to generate strong use cases and ERD.

---

## 6. Deferred Modules
Modules for phase 2 or when time allows:
1. debts
2. sharing
3. advanced exports
4. Google login
5. advanced cloud sync

### Why deferred
- More complex in terms of rules and UI.
- Not required for the core system to function.
- Should be implemented after the schema and main flows are stable.

---

## 7. Module to Django App Mapping

| Business Module | Suggested Django App |
|---|---|
| accounts | accounts |
| income | incomes |
| expenses | expenses |
| categories | categories |
| bank_accounts | bank_accounts |
| budgets | budgets |
| alerts | alerts |
| debts | debts |
| sharing | sharing |
| reports | reports |
| exports | exports |
| dashboard | dashboard |
| admin/logging | core or adminpanel |

---

## 8. Conclusion
Dividing the system into modules as described above prevents confusion when starting development. Instead of viewing the problem as one large block, the team can build layer by layer:
- authentication layer,
- core data layer,
- control layer,
- display layer,
- extension layer.

This is an important step before writing business rules and the logical schema, because without clear module boundaries, the database easily becomes tangled or overlapping in responsibility.
