# Roles and Permissions Specification

## 1. Purpose
This document defines:
- which actors exist in the system,
- what each actor is allowed to do,
- what each actor is not allowed to do,
- access control principles and data security policies.

This is an extremely important document because the project deals directly with **personal financial data**. Incorrect permission design leads to serious failures in both business logic and security.

---

## 2. List of Main Actors
The system has 3 confirmed actors:
1. **Guest**
2. **User**
3. **Admin**

---

## 3. Actor Descriptions

### 3.1. Guest
A guest is a user who has not logged in.

**Characteristics:**
- No authenticated session.
- Has no personal financial data in the system, or has not yet accessed it.

**Usage goals:**
- Learn about the system.
- Register a new account.
- Log in if an account already exists.

---

### 3.2. User
A user is someone who has successfully logged in and uses the system to manage personal finances.

**Characteristics:**
- Has a valid account.
- May only operate on their own data.
- Can use core modules: income, expense, category, bank account, budget, reports.

**Usage goals:**
- Track personal finances.
- View spending reports.
- Control budgets.
- Receive alerts.

---

### 3.3. Admin
An admin is a system administrator.

**Characteristics:**
- Has higher permissions than a regular user.
- Can manage users, default categories, logs, and system status.
- Must not use administrative privileges to arbitrarily view users' private financial data unless the system policy permits it.

**Usage goals:**
- Manage system operations.
- Check user accounts.
- Check errors and logs.
- Monitor backup/recovery.

---

## 4. General Access Control Principles

### 4.1. Principle of Least Privilege
Each actor is granted **only the permissions necessary** to complete their tasks.

### 4.2. Ownership-Based Access Control
For personal financial data, access must be based on **data ownership**:
- income records belong to a user — only that user may view/edit/delete them,
- expense records belong to a user — only that user may view/edit/delete them,
- budgets belong to a user — only that user may view/edit/delete them,
- bank accounts belong to a user — only that user may view/edit them.

### 4.3. Authentication Before Authorization
To check permissions, a user must first be authenticated.

### 4.4. Default Deny
If a permission has not been explicitly granted, the system must deny access by default.

---

## 5. Permission Matrix by Actor

| Feature | Guest | User | Admin |
|---|---|---|---|
| View landing page | Yes | Yes | Yes |
| Register | Yes | Not needed | Can create users manually if supported |
| Login | Yes | Yes | Yes |
| Logout | No | Yes | Yes |
| View/edit personal profile | No | Yes (own only) | Yes (admin's own profile) |
| Manage income | No | Yes (own only) | Not by default |
| Manage expenses | No | Yes (own only) | Not by default |
| Manage personal categories | No | Yes (own only) | Can manage system categories |
| Manage bank accounts | No | Yes (own only) | Not by default |
| Manage budgets | No | Yes (own only) | Not by default |
| View alerts | No | Yes (own only) | Can view system alerts |
| View dashboard | No | Yes (own only) | Has admin dashboard |
| View reports | No | Yes (own only) | Admin reports only if available |
| Track debts | No | Yes (own only) | Not by default |
| Join sharing groups | No | Yes | Not by default |
| Export Excel/PDF | No | Yes (own data only) | Can export admin reports |
| Manage users | No | No | Yes |
| Manage logs | No | No | Yes |
| Backup/Recovery operations | No | No | Yes |

---

## 6. Detailed Permissions by Actor

# 6.1. Guest Permissions

### Guest is allowed to
- Access the landing page.
- View system introduction content.
- Access the registration page.
- Access the login page.

### Guest is not allowed to
- View the dashboard.
- View reports.
- View or create income/expense.
- View any financial data.
- Call APIs that require authentication.

### System behavior when a guest attempts unauthorized access
- Redirect to the login page.
- Or return HTTP 401/403 depending on the architecture.

---

# 6.2. User Permissions

## 6.2.1. Personal Profile
Users are allowed to:
- view their profile,
- edit their profile,
- change their password,
- modify certain personal settings.

Users are not allowed to:
- edit another user's profile,
- view another user's detailed profile.

---

## 6.2.2. Income
Users are allowed to:
- create income,
- view their own income list,
- view details of their own income,
- edit their own income,
- delete their own income.

Users are not allowed to:
- view another user's income,
- edit/delete another user's income,
- pass arbitrary `user_id` to take ownership of records.

---

## 6.2.3. Expenses
Users are allowed to:
- create expenses,
- view their own expenses,
- edit their own expenses,
- delete their own expenses,
- filter expenses by category/date/account.

Users are not allowed to:
- access another user's expenses,
- view another user's category usage.

---

## 6.2.4. Categories
Users are allowed to:
- create personal categories,
- edit their own categories,
- deactivate their own categories,
- use default system categories if provided.

Users are not allowed to:
- edit system categories (admin only),
- edit another user's personal categories.

---

## 6.2.5. Bank Accounts
Users are allowed to:
- create bank accounts,
- edit account information,
- view balance,
- view related transactions.

Users are not allowed to:
- view or modify another user's bank accounts,
- deduct from another user's balance.

---

## 6.2.6. Budgets
Users are allowed to:
- create budgets,
- edit budgets,
- close budgets,
- view budget usage,
- view alerts generated by budgets.

Users are not allowed to:
- access another user's budgets.

---

## 6.2.7. Alerts
Users are allowed to:
- view their own alerts,
- mark alerts as read,
- filter by alert type.

Users are not allowed to:
- view another user's alerts.

---

## 6.2.8. Reports and Dashboard
Users are allowed to:
- view their personal dashboard,
- view their own daily/monthly/yearly reports,
- view their own charts and data tables,
- export their own data.

Users are not allowed to:
- view another user's aggregate reports,
- export another user's data.

---

## 6.2.9. Debts
Users are allowed to:
- create debt records,
- update status,
- record payments,
- view their own debts.

Users are not allowed to:
- view another user's debts unless a valid sharing model exists.

---

## 6.2.10. Sharing Groups
Users are allowed to:
- create a group if the system permits,
- join a group,
- view shared transactions of groups they are a member of,
- add shared transactions if they have permission in the group.

Users are not allowed to:
- view transactions of groups they are not a member of,
- add members without authorization if not the owner/admin of the group,
- view private transactions that have not been shared.

---

# 6.3. Admin Permissions

## 6.3.1. User Management
Admin is allowed to:
- view user list,
- activate / deactivate users,
- search users,
- view account status.

Admin should exercise caution with:
- editing individual users' personal financial data,
- accessing private data outside of policy.

---

## 6.3.2. System Category Management
Admin is allowed to:
- create default categories,
- edit shared categories,
- deactivate system categories.

---

## 6.3.3. Logs and Operations
Admin is allowed to:
- view authentication logs,
- view error logs,
- view scheduled job logs,
- monitor backup/recovery,
- check system tasks.

---

## 6.3.4. Backup/Recovery
Admin is allowed to:
- run manual backups,
- restore data following procedure,
- check backup file status,
- verify basic integrity.

---

## 6.3.5. Admin Limitations
By default, admins should not have access to all individual transaction details unless:
- the course/project policy explicitly permits it,
- it is needed for controlled debugging,
- the data is demo data only.

Better practice:
- admins manage users and the system,
- users' detailed financial data should still be protected.

---

## 7. Core Security Rules

### 7.1. Each user may only view their own financial data
This is the most important rule in the system.

Applies to:
- income,
- expenses,
- personal categories,
- bank accounts,
- budgets,
- alerts,
- reports,
- debts.

### 7.2. Income/expense must never be exposed to other users
This applies at all levels:
- UI,
- API,
- exports,
- reports,
- DB queries.

### 7.3. Never trust client-side data
Even if the client sends a `user_id`, the backend must extract the user from the current session/token and verify ownership.

### 7.4. Log important actions
Actions that should be logged:
- successful/failed logins,
- password changes,
- locking/unlocking users,
- backup/recovery,
- system errors,
- background job runs.

---

## 8. Confirmed Login Methods

### Phase 1
- **Standard login** with email/username + password.

### Phase 2
- **Google Login** can be added later.

### Rationale
- Standard login is straightforward and stable for MVP.
- Google login is a good extension but should not be implemented before the core schema and features are complete.

---

## 9. Backend Permission Enforcement in Django
In Django, access control must be enforced at the following levels:

### 9.1. Route-Level Protection
- Pages requiring login must have `login_required` or equivalent.
- APIs must block unauthenticated access.

### 9.2. Object-Level Permissions
Not only checking if the user is logged in, but also verifying:
- whether this object belongs to the current user.

Example:
- `/expenses/15/edit/` is only valid if expense id=15 belongs to the currently logged-in user.

### 9.3. Admin Panel Separation
- The admin panel is accessible to admins only.
- Regular users must not access admin features.

---

## 10. Detailed Permission Matrix by Module

| Module | Guest | User | Admin |
|---|---|---|---|
| Accounts | register/login | profile/update/logout | manage users |
| Income | none | CRUD own | not by default |
| Expenses | none | CRUD own | not by default |
| Categories | none | CRUD own categories | manage default categories |
| Bank Accounts | none | CRUD own | not by default |
| Budgets | none | CRUD own | not by default |
| Alerts | none | view own | system-level only |
| Reports | none | view/export own | admin reports only |
| Debts | none | CRUD own | not by default |
| Sharing | none | access groups of membership | moderate if designed |
| Logs | none | none | view/manage |
| Backup/Recovery | none | none | manage |

---

## 11. Permission Test Cases

### Test Case 1
User A logs in and attempts to view User B's expense by modifying the URL.

**Expected result:**
- Access denied.
- Returns 403 or appropriate redirect.

### Test Case 2
A guest accesses `/dashboard/`.

**Expected result:**
- Redirected to login.

### Test Case 3
A regular user accesses `/admin/`.

**Expected result:**
- Cannot access the admin area.

### Test Case 4
Admin deactivates a user.

**Expected result:**
- The deactivated user cannot log in again.

### Test Case 5
A user exports a monthly report.

**Expected result:**
- Only that user's data is included in the export file.

---

## 12. Conclusion
This permission document is the foundation of the entire system because personal financial management is extremely sensitive in terms of data. From this point forward, every schema design, API, query, dashboard, and report must follow this principle:

**Each user may only view and operate on their own financial data.**

This rule must not be broken in any module of the system.
