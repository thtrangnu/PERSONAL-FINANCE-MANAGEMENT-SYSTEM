# Project Overview — Personal Finance Management System

## 1. Project Name
**Project 13 — Personal Finance Management System**

Suggested product names:
- **Smart Finance Hub**
- **MyBudget Manager**
- **Personal Finance Tracker**

Throughout this documentation, the system will be referred to as:
**NUFI**.

---

## 2. Problem Context
Many individual users struggle with managing their personal finances day-to-day for the following reasons:
- They do not track all income and expenses.
- They do not know which bank accounts hold their money.
- They have no visibility into total spending by day, month, or year.
- They lack a clear budget plan for each spending category.
- They only discover overspending after the money is gone.
- They have no visual reports to evaluate their financial habits.
- Manual data aggregation in Excel is error-prone, time-consuming, and hard to scale.

To address this, NUFI is built to provide a platform that helps users:
- manage their personal profile,
- record income and expenses,
- track account balances,
- plan budgets,
- receive over-limit alerts,
- view reports in table and chart form,
- extend into debt tracking, financial sharing groups, report exports, and cloud sync.

---

## 3. General Project Objectives
The system must fulfill these core needs:

1. **User Management**
   - Users can register, log in, and update their profile.
   - The system must ensure each user's financial data is isolated.

2. **Income and Expense Management**
   - Users can add, edit, delete, and view income/expense records.
   - Transactions can be categorized by category.
   - Transactions can be linked to a specific bank account.

3. **Bank Account / Wallet Tracking**
   - Users can manage multiple accounts.
   - The system reflects balance changes when transactions occur.

4. **Budget Planning**
   - Users set monthly or category-based budgets.
   - The system monitors budget usage and alerts when nearing or exceeding the limit.

5. **Reports and Statistics**
   - Provides daily/monthly/yearly summaries.
   - Displays visual charts and detailed tables.

6. **Advanced Database Requirements**
   - Uses **indexes, views, procedures, functions, triggers**.
   - Includes mechanisms for **security, backup, recovery**.

7. **Extensibility**
   - Supports debt tracking.
   - Supports financial sharing groups.
   - Supports Excel/PDF export.
   - Supports cloud sync.

---

## 4. Project Scope

### 4.1. In-Scope
The following features are officially within project scope:

#### A. User Accounts and Profile
- User registration.
- Login / logout.
- Personal profile management.
- Password change.
- Account lock / unlock at admin level.

#### B. Income Management
- Add income.
- Edit income.
- Delete income.
- View income list.
- Filter by date, type, and account.

#### C. Expense Management
- Add expense.
- Edit expense.
- Delete expense.
- View expense list.
- Assign category to expense.
- Filter by category, date, and bank account.

#### D. Category Management
- Create personal categories.
- Edit categories.
- Activate/deactivate categories.
- Select category type: income / expense / both.
- Assign color, icon, and description.

#### E. Bank Account / Wallet Management
- Create bank accounts.
- Edit account information.
- Track current balance.
- View related transaction history.

#### F. Budget Management
- Create a total monthly budget.
- Create category-based budgets.
- Track amount used, remaining, and usage percentage.
- Generate alerts when nearing or exceeding the limit.

#### G. Reports
- Daily summary.
- Monthly summary.
- Yearly summary.
- Table-based reports.
- Chart-based reports.

#### H. Extension Features (after core)
- Debt tracking.
- Financial sharing groups.
- Report export.
- Cloud sync.

#### I. Infrastructure and Deployment
- Backend: Django.
- Database: MySQL.
- Containerized with Docker.
- Django management commands and Kubernetes CronJob for scheduled tasks, backup, and summaries.
- Kubernetes + Helm for deployment and operations.
- Cloudflare Tunnel for public demo access when needed.

---

### 4.2. Out-of-Scope
The following are **not prioritized in the first version** or are reserved for future extension:
- Direct electronic payment integration with banks.
- Real-time bank balance sync via API.
- AI-powered OCR for receipts.
- Advanced financial forecasting with Machine Learning.
- Financial advisory chatbot.
- Multi-currency support with real-time exchange rates.
- Native mobile app for iOS/Android.
- Investment, stock, or crypto analysis.

---

## 5. Main User Groups
The system has 3 main actors:

### 5.1. Guest
A user who has not logged in.
Key permissions:
- View the landing page.
- Register.
- Log in.
- View some system introduction content.

### 5.2. User
A logged-in user.
Key permissions:
- Manage their own financial data.
- Create/edit/delete income, expense, category, bank account, budget.
- View alerts, reports, dashboard.
- Track personal debts.
- Join sharing groups if available.

### 5.3. Admin
A system administrator.
Key permissions:
- Manage users.
- Manage default system categories.
- View activity logs.
- Monitor system errors.
- Check backup, recovery, and data operations.

---

## 6. Value Delivered by the System

### 6.1. For Individual Users
- Know where money comes from and goes every day.
- Better control over spending habits.
- Get warned before exceeding the budget.
- Make financial decisions more easily.

### 6.2. For Academic and Project Work
- Covers all components of a real-world data management system.
- Opportunity to apply backend, database, cloud, container, and workflow scheduling.
- Easy to present — clear business processes, clear data, and visual reports.
- Suitable for demonstrating database design, API development, security, and deployment skills.

---

## 7. Technology Stack

### 7.1. Django
Why chosen:
- Rapid web development.
- Built-in authentication, admin site, and ORM.
- Suitable for the multi-module CRUD model.
- Easy to organize by app/module.

Role in the project:
- Handles business logic.
- Handles user authentication.
- Creates APIs or renders web UI.
- Connects to MySQL.

### 7.2. MySQL
Why chosen:
- Clear relational model, suitable for financial data.
- Easy to design primary keys, foreign keys, and indexes.
- Supports views, procedures, functions, and triggers.
- Meets course requirements for DBMS.

Role in the project:
- Stores users, transactions, budgets, alerts, sharing groups.
- Supports aggregation queries and reporting.

### 7.3. Docker
Why chosen:
- Consistent runtime environment for all team members.
- Eliminates "works on my machine" issues.
- Easy to package Django + MySQL and related background components.

Role in the project:
- Containerizes the backend.
- Containerizes the database.
- Provides a consistent environment for periodic commands.

### 7.4. Kubernetes and Helm
Why chosen:
- Suitable for packaging and deploying the system in a production-like manner.
- Easy to manage configurations per environment.
- Easy to attach monitoring, scheduled jobs, and periodic backup.

Role in the project:
- Kubernetes: runs Django/Gunicorn application as pods and services.
- Helm: manages deployments, secrets, configmaps, cronjobs, and monitoring via chart.
- Persistent volume or local storage: stores backups, export files, and media as needed.

### 7.5. Cloudflare Tunnel
Why chosen:
- Suitable for quickly making the demo public from a local machine or Kubernetes.
- No need to open router ports or set up separate public infrastructure.
- Convenient for sharing demo links during development and presentations.

Role in the project:
- Creates a temporary public URL pointing to the NUFI instance running on a local port.
- Supports live UI and feature demos over the Internet without changing the main deployment architecture.
- Can be extended to a `named tunnel` if a fixed domain is needed.

---

## 8. Confirmed Extension Features

### 8.1. Debt Tracking
Allows users to:
- record debts they owe,
- record debts others owe them,
- set due dates,
- view payment history,
- track status: paid / outstanding / overdue.

### 8.2. Sharing Groups
Allows groups of users to:
- create a group,
- invite members,
- share selected transactions,
- track group expenses together.

### 8.3. Export Excel/PDF
Allows exporting:
- monthly reports,
- income/expense details,
- budgets,
- charts and tables.

### 8.4. Cloud Sync
Allows:
- syncing data to the cloud,
- periodic backup,
- supporting recovery on failure.

---

## 9. High-Level Architecture
Proposed architecture:

**Frontend/UI**
- Django templates or Django + REST API + separate frontend.

**Backend**
- Django apps per module:
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

**Database**
- MySQL relational database.
- Normalized tables with clear PK/FK.
- Includes views, procedures, functions, and triggers.

**Scheduler / Background Jobs**
- Django management commands.
- Kubernetes CronJob for backup, alert checks, smoke tests, and periodic summaries.

**Infrastructure**
- Docker Compose for local development.
- Kubernetes + Helm for deployment and operations.
- Cloudflare Tunnel for public demo access when sharing from the Internet.

---

## 10. General Business Flow

### 10.1. Basic User Flow
1. User registers or logs in.
2. User updates profile and creates a bank account.
3. User creates categories if needed.
4. User enters income and expenses.
5. System updates the corresponding account balance.
6. User creates a budget for the month or category.
7. When an expense is recorded, the system compares it against the budget.
8. If nearing or exceeding the limit, the system generates an alert.
9. User views the dashboard, statistics tables, and charts.
10. User can export reports or track debts / sharing groups.

### 10.2. Admin Flow
1. Admin logs into the admin area.
2. Checks users, logs, and default categories.
3. Checks backup and background tasks.
4. Monitors system errors and security.

---

## 11. General Non-Functional Requirements
The system must not only function correctly but also meet the following criteria:

### 11.1. Security
- Each user can only see their own data.
- Financial data must not leak between accounts.
- Passwords must be securely hashed.
- APIs and forms must prevent unauthorized access.

### 11.2. Data Integrity
- Every transaction must be linked to the correct user.
- Foreign keys and constraints must be rigorously designed.
- Triggers/procedures must not corrupt balances.

### 11.3. Performance
- Index frequently searched columns.
- Monthly/yearly reports must respond reasonably as data grows.

### 11.4. Recoverability
- Periodic backups.
- Recovery documentation.
- Data can be restored when the system fails.

### 11.5. Extensibility
- New modules can be added without breaking the existing structure.
- Can be deployed to the cloud and scaled in the future.

---

## 12. Expected MVP Deliverables
The first version should focus on:
- User registration / login / profile.
- Income management.
- Expense management.
- Category management.
- Bank account management.
- Budget management.
- Basic dashboard.
- Daily/monthly/yearly reports.
- Basic budget exceeded alerts.

This is sufficient to:
- demo the business logic,
- demonstrate the database schema,
- present use cases,
- show CRUD + reporting,
- extend with more modules later.

---

## 13. Project Success Criteria

### 13.1. Functional
- Users can fully manage their personal financial data.
- The system generates meaningful reports and alerts.
- Access permissions between actors are accurate.

### 13.2. Data
- Schema is rational, normalized, with PK/FK/indexes.
- Views/procedures/functions/triggers are used appropriately.
- No cross-user data leaks.

### 13.3. Technical
- Runs with Docker.
- MySQL connection is stable.
- Periodic job mechanism via Django management commands and Kubernetes CronJob.
- Clear path for Kubernetes/Helm deployment.

### 13.4. Presentation
- Clear documentation.
- Use cases, ERD, and schema available.
- UI and flow illustrations available.
- Realistic demo data that is convincing.

---

## 14. Conclusion
NUFI is a project with a clear scope, close to real-world problems, and suitable for developing into a complete personal finance web application. With the confirmed stack of **Django + MySQL + Docker + Kubernetes + Helm + Cloudflare Tunnel**, the project can deliver a product that meets both the academic DBMS requirements and demonstrates modern software system design capabilities.

In the first phase, the project focuses on core features: profile, income, expenses, categories, bank accounts, budgets, and reports. Once the core is stable, it will expand into debt tracking, sharing groups, export, and cloud sync.
