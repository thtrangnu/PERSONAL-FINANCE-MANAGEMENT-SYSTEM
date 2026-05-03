# Relational Schema Design

## 1. Purpose
This document describes the logical relational schema for the **NUFI** system, including:
- list of tables,
- purpose of each table,
- columns and data types,
- primary keys (PK), foreign keys (FK), and constraints,
- system fields,
- proposed indexes,
- relationships between tables.

The goal is to establish a clear foundation before writing:
- Django models,
- migrations,
- SQL DDL,
- views/procedures/functions/triggers.

---

## 2. General Design Conventions

### 2.1. Table Naming
- Use plural nouns in `snake_case` for SQL implementation.
- Confirmed main tables:
  - `users`
  - `categories`
  - `bank_accounts`
  - `incomes`
  - `expenses`
  - `budgets`
  - `alerts`
  - `debts`
  - `debt_payments`
  - `groups`
  - `group_members`
  - `shared_transactions`

### 2.2. Primary Key Convention
- Each table uses `BIGINT UNSIGNED AUTO_INCREMENT` as primary key.
- PK column names follow the entity:
  - `user_id`
  - `category_id`
  - `income_id`
  - `expense_id`
  - ...

### 2.3. System Timestamp Convention
Main business tables should include:
- `created_at`
- `updated_at`

Some tables also have business-specific date fields:
- `income_date`
- `expense_date`
- `payment_date`
- `due_date`
- `joined_at`

### 2.4. Status Field Convention
- Use `is_active` for simple on/off status.
- Use `status` for multi-branch business statuses.

### 2.5. Currency Type
- Use `DECIMAL(18,2)` for all monetary values to avoid floating-point errors.

### 2.6. Security Convention
- Do not store plaintext passwords.
- Do not store full account numbers unless necessary.
- Store only `account_number_masked` when appropriate for demo/academic purposes.

### 2.7. Business Constraint Convention
- Simple constraints such as `amount > 0` and `period_month BETWEEN 1 AND 12` can be set via `CHECK`.
- Cross-column rules or record-type-dependent rules should be documented and enforced via:
  - backend,
  - stored procedure,
  - trigger.

Examples:
- `categories.is_default` paired with `user_id`,
- `budgets.budget_scope` paired with `category_id`,
- `shared_transactions.expense_id` / `income_id`,
- `alerts` should reference only one related object at a time.

---

## 3. Confirmed Table List
Main tables:
1. `users`
2. `categories`
3. `bank_accounts`
4. `incomes`
5. `expenses`
6. `budgets`
7. `alerts`
8. `debts`
9. `debt_payments`
10. `groups`
11. `group_members`
12. `shared_transactions`

---

# 4. Table Details

# 4.1. `users`

## Purpose
Stores user account information.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| user_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| username | VARCHAR(50) | No | UNIQUE | Login username |
| email | VARCHAR(150) | No | UNIQUE | User email |
| password_hash | VARCHAR(255) | No | | Hashed password |
| full_name | VARCHAR(120) | No | | Full name |
| phone_number | VARCHAR(20) | Yes | | Phone number |
| avatar_url | VARCHAR(255) | Yes | | Profile picture URL |
| default_currency | VARCHAR(10) | Yes | | e.g. `VND`, `USD` |
| timezone | VARCHAR(50) | Yes | | User timezone |
| role | ENUM('user','admin') | No | | Role |
| is_active | BOOLEAN | No | | Account status |
| last_login_at | DATETIME | Yes | | Last login time |
| created_at | DATETIME | No | | Creation time |
| updated_at | DATETIME | No | | Last update time |

## Proposed Indexes
- unique `username`
- unique `email`
- index `role`
- index `is_active`

---

# 4.2. `categories`

## Purpose
Stores categories used for:
- income,
- expenses,
- or both.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| category_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| user_id | BIGINT UNSIGNED | Yes | FK | Null for system categories |
| category_name | VARCHAR(100) | No | | Category name |
| category_type | ENUM('income','expense','both') | No | | Category type |
| description | VARCHAR(255) | Yes | | Description |
| color_code | VARCHAR(20) | Yes | | UI color code |
| icon_name | VARCHAR(50) | Yes | | Icon name |
| is_default | BOOLEAN | No | | System category flag |
| is_active | BOOLEAN | No | | Active status |
| created_at | DATETIME | No | | Creation time |
| updated_at | DATETIME | No | | Last update time |

## Foreign Keys
- `user_id` → `users.user_id`

## Proposed Business Constraints
- If `is_default = true`, `user_id` should be `NULL`.
- If it is a personal category, `user_id` must have a value.
- For `incomes`, the category should have `category_type = 'income'` or `'both'`.
- For `expenses` or `budgets`, the category should have `category_type = 'expense'` or `'both'`.

## Suggested Unique Constraints
- unique `(user_id, category_name)` for personal categories.
- System categories should be seeded and controlled by admin/backend.

## Proposed Indexes
- index `user_id`
- index `category_type`
- index `is_default`
- index `is_active`

---

# 4.3. `bank_accounts`

## Purpose
Stores bank accounts, e-wallets, and cash wallets belonging to users.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| bank_account_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| user_id | BIGINT UNSIGNED | No | FK | Owner |
| account_name | VARCHAR(100) | No | | Account name |
| account_type | ENUM('bank','cash','e_wallet','other') | No | | Account type |
| provider_name | VARCHAR(100) | Yes | | Bank or wallet name |
| account_number_masked | VARCHAR(30) | Yes | | Masked account number |
| currency | VARCHAR(10) | No | | Currency type |
| opening_balance | DECIMAL(18,2) | No | | Initial balance |
| current_balance | DECIMAL(18,2) | No | | Current balance |
| note | VARCHAR(255) | Yes | | Notes |
| is_active | BOOLEAN | No | | Still in use |
| created_at | DATETIME | No | | Creation time |
| updated_at | DATETIME | No | | Last update time |

## Foreign Keys
- `user_id` → `users.user_id`

## Proposed Indexes
- index `user_id`
- index `account_type`
- index `is_active`

---

# 4.4. `incomes`

## Purpose
Stores income transactions for users.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| income_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| user_id | BIGINT UNSIGNED | No | FK | Owner |
| category_id | BIGINT UNSIGNED | No | FK | Income category |
| bank_account_id | BIGINT UNSIGNED | Yes | FK | Receiving account |
| title | VARCHAR(150) | No | | Transaction title |
| amount | DECIMAL(18,2) | No | | Amount |
| income_date | DATE | No | | Transaction date |
| description | VARCHAR(255) | Yes | | Description |
| note | TEXT | Yes | | Notes |
| status | ENUM('active','deleted') | No | | Status |
| created_at | DATETIME | No | | Creation time |
| updated_at | DATETIME | No | | Last update time |

## Foreign Keys
- `user_id` → `users.user_id`
- `category_id` → `categories.category_id`
- `bank_account_id` → `bank_accounts.bank_account_id`

## Proposed Constraints
- `amount > 0`
- `income_date` is required

## Proposed Indexes
- index `user_id`
- index `category_id`
- index `income_date`
- index `bank_account_id`
- composite index `(user_id, income_date)`

---

# 4.5. `expenses`

## Purpose
Stores expense transactions for users.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| expense_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| user_id | BIGINT UNSIGNED | No | FK | Owner |
| category_id | BIGINT UNSIGNED | No | FK | Expense category |
| bank_account_id | BIGINT UNSIGNED | Yes | FK | Payment account |
| amount | DECIMAL(18,2) | No | | Amount |
| expense_date | DATE | No | | Transaction date |
| payment_method | ENUM('cash','bank','e_wallet','credit_card','other') | Yes | | Payment method |
| description | VARCHAR(255) | Yes | | Description |
| note | TEXT | Yes | | Notes |
| status | ENUM('active','deleted') | No | | Status |
| created_at | DATETIME | No | | Creation time |
| updated_at | DATETIME | No | | Last update time |

## Foreign Keys
- `user_id` → `users.user_id`
- `category_id` → `categories.category_id`
- `bank_account_id` → `bank_accounts.bank_account_id`

## Proposed Constraints
- `amount > 0`
- `expense_date` is required

## Proposed Indexes
- index `user_id`
- index `category_id`
- index `bank_account_id`
- index `expense_date`
- composite index `(user_id, expense_date)`
- composite index `(user_id, category_id, expense_date)`

---

# 4.6. `budgets`

## Purpose
Stores monthly budget information in two forms:
- overall monthly budget,
- category-based budget.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| budget_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| user_id | BIGINT UNSIGNED | No | FK | Owner |
| budget_name | VARCHAR(120) | No | | Budget name |
| budget_scope | ENUM('overall','category') | No | | Budget scope |
| category_id | BIGINT UNSIGNED | Yes | FK | Only used when scope=`category` |
| period_month | TINYINT UNSIGNED | No | | 1..12 |
| period_year | SMALLINT UNSIGNED | No | | e.g. 2026 |
| spending_limit | DECIMAL(18,2) | No | | Spending limit |
| warning_percent | DECIMAL(5,2) | No | | e.g. 80.00 |
| status | ENUM('active','inactive','closed') | No | | Status |
| created_at | DATETIME | No | | Creation time |
| updated_at | DATETIME | No | | Last update time |

## Foreign Keys
- `user_id` → `users.user_id`
- `category_id` → `categories.category_id`

## Proposed Constraints
- `period_month BETWEEN 1 AND 12`
- `spending_limit > 0`
- `warning_percent > 0 AND warning_percent <= 100`
- if `budget_scope = 'category'` then `category_id` must not be null
- if `budget_scope = 'overall'` then `category_id` should be null

## Suggested Business Uniqueness
- Avoid having 2 `active` budgets with overlapping logic for the same:
  - user,
  - scope,
  - category,
  - month,
  - year.

## Proposed Indexes
- index `user_id`
- index `category_id`
- index `(period_year, period_month)`
- composite index `(user_id, period_year, period_month)`

---

# 4.7. `alerts`

## Purpose
Stores alerts sent to users.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| alert_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| user_id | BIGINT UNSIGNED | No | FK | Alert recipient |
| alert_type | ENUM('budget_warning','budget_exceeded','debt_overdue','system_info','other') | No | | Alert type |
| severity | ENUM('info','warning','critical') | No | | Severity level |
| title | VARCHAR(150) | No | | Title |
| message | TEXT | No | | Message body |
| related_budget_id | BIGINT UNSIGNED | Yes | FK | Related budget |
| related_expense_id | BIGINT UNSIGNED | Yes | FK | Related expense |
| related_debt_id | BIGINT UNSIGNED | Yes | FK | Related debt |
| is_read | BOOLEAN | No | | Read status |
| created_at | DATETIME | No | | Creation time |

## Foreign Keys
- `user_id` → `users.user_id`
- `related_budget_id` → `budgets.budget_id`
- `related_expense_id` → `expenses.expense_id`
- `related_debt_id` → `debts.debt_id`

## Business Conventions
- budget alerts should only use `related_budget_id`
- debt alerts should only use `related_debt_id`
- a single alert should not reference multiple related objects simultaneously

## Proposed Indexes
- index `user_id`
- index `alert_type`
- index `is_read`
- index `created_at`
- composite index `(user_id, is_read, created_at)`

---

# 4.8. `debts`

## Purpose
Stores debt records for users.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| debt_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| user_id | BIGINT UNSIGNED | No | FK | Owner |
| debt_type | ENUM('i_owe','owed_to_me') | No | | Direction of the debt |
| counterparty_name | VARCHAR(150) | No | | Other party involved |
| original_amount | DECIMAL(18,2) | No | | Original amount |
| remaining_amount | DECIMAL(18,2) | No | | Remaining balance |
| due_date | DATE | Yes | | Due date |
| status | ENUM('pending','partially_paid','paid','overdue') | No | | Status |
| description | VARCHAR(255) | Yes | | Description |
| note | TEXT | Yes | | Notes |
| created_at | DATETIME | No | | Creation time |
| updated_at | DATETIME | No | | Last update time |
| is_active | BOOLEAN | No | | Still being tracked |

## Foreign Keys
- `user_id` → `users.user_id`

## Proposed Constraints
- `original_amount > 0`
- `remaining_amount >= 0`
- `remaining_amount <= original_amount`

## Proposed Indexes
- index `user_id`
- index `status`
- index `due_date`
- composite index `(user_id, status, due_date)`

---

# 4.9. `debt_payments`

## Purpose
Stores payment history for each debt.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| debt_payment_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| debt_id | BIGINT UNSIGNED | No | FK | Related debt |
| bank_account_id | BIGINT UNSIGNED | Yes | FK | Account used for payment |
| payment_date | DATE | No | | Payment date |
| amount | DECIMAL(18,2) | No | | Amount paid |
| note | TEXT | Yes | | Notes |
| created_at | DATETIME | No | | Creation time |

## Foreign Keys
- `debt_id` → `debts.debt_id`
- `bank_account_id` → `bank_accounts.bank_account_id`

## Proposed Constraints
- `amount > 0`

## Proposed Indexes
- index `debt_id`
- index `payment_date`
- index `bank_account_id`

---

# 4.10. `groups`

## Purpose
Stores financial sharing groups.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| group_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| owner_user_id | BIGINT UNSIGNED | No | FK | Group creator |
| group_name | VARCHAR(120) | No | | Group name |
| description | VARCHAR(255) | Yes | | Description |
| status | ENUM('active','inactive','archived') | No | | Status |
| created_at | DATETIME | No | | Creation time |
| updated_at | DATETIME | No | | Last update time |

## Foreign Keys
- `owner_user_id` → `users.user_id`

## Proposed Indexes
- index `owner_user_id`
- index `status`

---

# 4.11. `group_members`

## Purpose
Stores members of each group.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| group_member_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| group_id | BIGINT UNSIGNED | No | FK | Group |
| user_id | BIGINT UNSIGNED | No | FK | Member |
| member_role | ENUM('owner','member') | No | | Role in the group |
| joined_at | DATETIME | No | | Join date |
| status | ENUM('pending','active','left','removed') | No | | Membership status |

## Foreign Keys
- `group_id` → `groups.group_id`
- `user_id` → `users.user_id`

## Suggested Unique Constraint
- unique `(group_id, user_id)`

## Proposed Indexes
- index `group_id`
- index `user_id`
- index `status`

---

# 4.12. `shared_transactions`

## Purpose
Links personal transactions to a sharing group.

## Design Note
The simplest approach in this project is to allow a `shared_transactions` record to reference **one existing expense or one existing income**.

## Proposed Structure
| Column | Data Type | Null | Key | Description |
|---|---|---:|---|---|
| shared_transaction_id | BIGINT UNSIGNED AUTO_INCREMENT | No | PK | Primary key |
| group_id | BIGINT UNSIGNED | No | FK | Target group |
| shared_by_user_id | BIGINT UNSIGNED | No | FK | User who shared the transaction |
| expense_id | BIGINT UNSIGNED | Yes | FK | Shared expense transaction |
| income_id | BIGINT UNSIGNED | Yes | FK | Shared income transaction |
| visibility_status | ENUM('visible','hidden') | No | | Visibility status |
| note | VARCHAR(255) | Yes | | Notes |
| created_at | DATETIME | No | | Creation time |

## Foreign Keys
- `group_id` → `groups.group_id`
- `shared_by_user_id` → `users.user_id`
- `(group_id, shared_by_user_id)` → `group_members(group_id, user_id)`
- `expense_id` → `expenses.expense_id`
- `income_id` → `incomes.income_id`

## Business Constraints
- Only one of `expense_id` or `income_id` may have a value.
- Both may not be null simultaneously.
- Only group members may create records here.

## Proposed Indexes
- index `group_id`
- index `shared_by_user_id`
- index `expense_id`
- index `income_id`

---

## 5. Key Relationships Between Tables

### 5.1. User and Personal Data
- `users` 1 — N `categories`
- `users` 1 — N `bank_accounts`
- `users` 1 — N `incomes`
- `users` 1 — N `expenses`
- `users` 1 — N `budgets`
- `users` 1 — N `alerts`
- `users` 1 — N `debts`
- `users` 1 — N `groups` (as owner)
- `users` 1 — N `group_members`

### 5.2. Category and Transactions
- `categories` 1 — N `incomes`
- `categories` 1 — N `expenses`
- `categories` 1 — N `budgets` (for category budgets)

### 5.3. BankAccount and Transactions
- `bank_accounts` 1 — N `incomes`
- `bank_accounts` 1 — N `expenses`
- `bank_accounts` 1 — N `debt_payments`

### 5.4. Budget and Alerts
- `budgets` 1 — N `alerts`

### 5.5. Debt and DebtPayments
- `debts` 1 — N `debt_payments`
- `debts` 1 — N `alerts`

### 5.6. Groups and Sharing
- `groups` 1 — N `group_members`
- `groups` 1 — N `shared_transactions`

---

## 6. Confirmed System Fields
Key system fields that should appear on main tables:
- `created_at`
- `updated_at`
- `is_active`
- `status`

### Application Guide
- `created_at`, `updated_at`: almost all main tables.
- `is_active`: `users`, `categories`, `bank_accounts`, `debts`.
- `status`: `incomes`, `expenses`, `budgets`, `debts`, `groups`, `group_members`.

---

## 7. Proposed Index Strategy
Since the course requires **indexes**, they must be designed to match actual query patterns.

### 7.1. Required Indexes
- `users(email)`
- `users(username)`
- `categories(user_id)`
- `categories(category_type)`
- `incomes(user_id, income_date)`
- `expenses(user_id, expense_date)`
- `expenses(user_id, category_id, expense_date)`
- `bank_accounts(user_id)`
- `budgets(user_id, period_year, period_month)`
- `alerts(user_id, is_read, created_at)`
- `debts(user_id, status, due_date)`
- `group_members(group_id, user_id)`

### 7.2. Benefits
- Speeds up user-filtered queries.
- Speeds up dashboard and report queries.
- Speeds up monthly budget queries.
- Speeds up unread alert queries.
- Speeds up membership checks in sharing.

---

## 8. Suggested Views / Procedures / Functions / Triggers

### 8.1. Suggested Views
**View 1 — `vw_monthly_expense_summary`**
- Aggregates expenses by user, month, year, and category.

**View 2 — `vw_budget_usage`**
- Displays budget limit, amount used, remaining, and usage percent.

**View 3 — `vw_dashboard_snapshot`**
- Quick data aggregation for each user's dashboard.

### 8.2. Suggested Stored Procedures
**Procedure 1 — `sp_create_expense`**
- adds expense,
- updates balance,
- checks budget,
- creates alert if needed.

**Procedure 2 — `sp_create_income`**
- adds income,
- updates balance.

**Procedure 3 — `sp_monthly_summary`**
- returns summary by user/month/year.

### 8.3. Suggested Functions
**Function 1 — `fn_budget_usage_percent(budget_id)`**
- Returns the percentage of budget used.

**Function 2 — `fn_remaining_budget(budget_id)`**
- Returns remaining budget amount.

**Function 3 — `fn_debt_remaining(debt_id)`**
- Returns remaining debt amount.

### 8.4. Suggested Triggers
**Trigger 1 — `before insert/update on categories`**
- validates the relationship between `is_default`, `user_id`, and `category_type`.

**Trigger 2 — `after insert on incomes`**
- increases `current_balance` in `bank_accounts`.

**Trigger 3 — `after insert on expenses`**
- decreases `current_balance` in `bank_accounts`.

**Trigger 4 — `before insert/update on budgets`**
- validates `budget_scope` and `category_id` logic.

**Trigger 5 — `before insert/update on shared_transactions`**
- validates that exactly one of `expense_id` or `income_id` is set.

**Trigger 6 — `after insert/update on debt_payments`**
- updates `remaining_amount` and `status` in `debts`.

---

## 9. Django Implementation Notes

### 9.1. For the `users` table
Practical recommendation when coding Django:
- use a custom user model or Django's default auth,
- then map the logic from this document to the model implementation.

### 9.2. For soft delete
Options:
- `status = 'deleted'`
- or `is_active = false`

### 9.3. For `categories`
- System categories can be pre-seeded.
- `category_type` validation can be done in the serializer/service layer before writing to DB.

### 9.4. For `shared_transactions`
- In the initial phase, if simplicity is preferred, only expense sharing may be supported.
- `income_id` can be left for a later extension phase.

---

## 10. Conclusion
This relational schema adequately meets the project objectives by covering:
- users,
- income transactions,
- expense transactions,
- shared categories for income/expenses,
- bank accounts,
- budgets,
- alerts,
- debts,
- sharing groups.

The schema is also suitable for academic requirements as it can be extended to implement:
- PK/FK,
- indexes,
- views,
- procedures,
- functions,
- triggers,
- security,
- backup and recovery.
