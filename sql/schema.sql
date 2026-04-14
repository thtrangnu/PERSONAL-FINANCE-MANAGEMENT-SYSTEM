-- NUFI
-- MySQL 8.x schema
-- This file uses plural table names consistently.
-- Cross-column business rules that are awkward in MySQL CHECK/FK combinations
-- should be enforced in Django, stored procedures, or triggers.

SET NAMES utf8mb4;

DROP DATABASE IF EXISTS `pfms`;

CREATE DATABASE `pfms`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `pfms`;

CREATE TABLE `users` (
  `user_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(150) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `full_name` VARCHAR(120) NOT NULL,
  `phone_number` VARCHAR(20) NULL,
  `avatar_url` VARCHAR(255) NULL,
  `default_currency` VARCHAR(10) NULL DEFAULT 'VND',
  `timezone` VARCHAR(50) NULL,
  `role` ENUM('user', 'admin') NOT NULL DEFAULT 'user',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `last_login_at` DATETIME NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `uq_users_username` (`username`),
  UNIQUE KEY `uq_users_email` (`email`),
  KEY `idx_users_role` (`role`),
  KEY `idx_users_is_active` (`is_active`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Application users';

-- Rule for triggers/backend:
-- 1. If is_default = TRUE then user_id should be NULL.
-- 2. If is_default = FALSE then user_id should not be NULL.
-- 3. category_type controls whether a category is valid for income, expense, or both.
CREATE TABLE `categories` (
  `category_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NULL,
  `category_name` VARCHAR(100) NOT NULL,
  `category_type` ENUM('income', 'expense', 'both') NOT NULL DEFAULT 'expense',
  `description` VARCHAR(255) NULL,
  `color_code` VARCHAR(20) NULL,
  `icon_name` VARCHAR(50) NULL,
  `is_default` BOOLEAN NOT NULL DEFAULT FALSE,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`category_id`),
  CONSTRAINT `fk_categories_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  UNIQUE KEY `uq_categories_user_name` (`user_id`, `category_name`),
  KEY `idx_categories_user_id` (`user_id`),
  KEY `idx_categories_category_type` (`category_type`),
  KEY `idx_categories_is_default` (`is_default`),
  KEY `idx_categories_is_active` (`is_active`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Reusable categories for income, expense, or both';

CREATE TABLE `bank_accounts` (
  `bank_account_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `account_name` VARCHAR(100) NOT NULL,
  `account_type` ENUM('bank', 'cash', 'e_wallet', 'other') NOT NULL,
  `provider_name` VARCHAR(100) NULL,
  `account_number_masked` VARCHAR(30) NULL,
  `currency` VARCHAR(10) NOT NULL DEFAULT 'VND',
  `opening_balance` DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  `current_balance` DECIMAL(18,2) NOT NULL DEFAULT 0.00,
  `note` VARCHAR(255) NULL,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`bank_account_id`),
  CONSTRAINT `fk_bank_accounts_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  KEY `idx_bank_accounts_user_id` (`user_id`),
  KEY `idx_bank_accounts_account_type` (`account_type`),
  KEY `idx_bank_accounts_is_active` (`is_active`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Bank, cash, and e-wallet accounts';

CREATE TABLE `incomes` (
  `income_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `category_id` BIGINT UNSIGNED NOT NULL,
  `bank_account_id` BIGINT UNSIGNED NULL,
  `title` VARCHAR(150) NOT NULL,
  `amount` DECIMAL(18,2) NOT NULL,
  `income_date` DATE NOT NULL,
  `description` VARCHAR(255) NULL,
  `note` TEXT NULL,
  `status` ENUM('active', 'deleted') NOT NULL DEFAULT 'active',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`income_id`),
  CONSTRAINT `chk_incomes_amount`
    CHECK (`amount` > 0),
  CONSTRAINT `fk_incomes_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_incomes_category`
    FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_incomes_bank_account`
    FOREIGN KEY (`bank_account_id`) REFERENCES `bank_accounts` (`bank_account_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  KEY `idx_incomes_user_id` (`user_id`),
  KEY `idx_incomes_category_id` (`category_id`),
  KEY `idx_incomes_income_date` (`income_date`),
  KEY `idx_incomes_bank_account_id` (`bank_account_id`),
  KEY `idx_incomes_user_income_date` (`user_id`, `income_date`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Income transactions';

CREATE TABLE `expenses` (
  `expense_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `category_id` BIGINT UNSIGNED NOT NULL,
  `bank_account_id` BIGINT UNSIGNED NULL,
  `amount` DECIMAL(18,2) NOT NULL,
  `expense_date` DATE NOT NULL,
  `payment_method` ENUM('cash', 'bank', 'e_wallet', 'credit_card', 'other') NULL,
  `description` VARCHAR(255) NULL,
  `note` TEXT NULL,
  `status` ENUM('active', 'deleted') NOT NULL DEFAULT 'active',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`expense_id`),
  CONSTRAINT `chk_expenses_amount`
    CHECK (`amount` > 0),
  CONSTRAINT `fk_expenses_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_expenses_category`
    FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_expenses_bank_account`
    FOREIGN KEY (`bank_account_id`) REFERENCES `bank_accounts` (`bank_account_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  KEY `idx_expenses_user_id` (`user_id`),
  KEY `idx_expenses_category_id` (`category_id`),
  KEY `idx_expenses_bank_account_id` (`bank_account_id`),
  KEY `idx_expenses_expense_date` (`expense_date`),
  KEY `idx_expenses_user_expense_date` (`user_id`, `expense_date`),
  KEY `idx_expenses_user_category_expense_date` (`user_id`, `category_id`, `expense_date`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Expense transactions';

-- Rule for triggers/backend:
-- 1. budget_scope = overall  => category_id must be NULL.
-- 2. budget_scope = category => category_id must not be NULL.
-- 3. For category budgets, category_type should be expense or both.
CREATE TABLE `budgets` (
  `budget_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `budget_name` VARCHAR(120) NOT NULL,
  `budget_scope` ENUM('overall', 'category') NOT NULL,
  `category_id` BIGINT UNSIGNED NULL,
  `period_month` TINYINT UNSIGNED NOT NULL,
  `period_year` SMALLINT UNSIGNED NOT NULL,
  `spending_limit` DECIMAL(18,2) NOT NULL,
  `warning_percent` DECIMAL(5,2) NOT NULL DEFAULT 80.00,
  `status` ENUM('active', 'inactive', 'closed') NOT NULL DEFAULT 'active',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`budget_id`),
  CONSTRAINT `chk_budgets_period_month`
    CHECK (`period_month` BETWEEN 1 AND 12),
  CONSTRAINT `chk_budgets_spending_limit`
    CHECK (`spending_limit` > 0),
  CONSTRAINT `chk_budgets_warning_percent`
    CHECK (`warning_percent` > 0 AND `warning_percent` <= 100),
  CONSTRAINT `fk_budgets_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_budgets_category`
    FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  KEY `idx_budgets_user_id` (`user_id`),
  KEY `idx_budgets_category_id` (`category_id`),
  KEY `idx_budgets_period_year_month` (`period_year`, `period_month`),
  KEY `idx_budgets_user_period_year_month` (`user_id`, `period_year`, `period_month`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Overall or category-based monthly budgets';

CREATE TABLE `debts` (
  `debt_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `debt_type` ENUM('i_owe', 'owed_to_me') NOT NULL,
  `counterparty_name` VARCHAR(150) NOT NULL,
  `original_amount` DECIMAL(18,2) NOT NULL,
  `remaining_amount` DECIMAL(18,2) NOT NULL,
  `due_date` DATE NULL,
  `status` ENUM('pending', 'partially_paid', 'paid', 'overdue') NOT NULL DEFAULT 'pending',
  `description` VARCHAR(255) NULL,
  `note` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (`debt_id`),
  CONSTRAINT `chk_debts_original_amount`
    CHECK (`original_amount` > 0),
  CONSTRAINT `chk_debts_remaining_amount`
    CHECK (`remaining_amount` >= 0 AND `remaining_amount` <= `original_amount`),
  CONSTRAINT `fk_debts_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  KEY `idx_debts_user_id` (`user_id`),
  KEY `idx_debts_status` (`status`),
  KEY `idx_debts_due_date` (`due_date`),
  KEY `idx_debts_user_status_due_date` (`user_id`, `status`, `due_date`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Debt tracking';

-- Rule for triggers/backend:
-- 1. A single alert should reference at most one related object.
-- 2. budget_* alerts should use related_budget_id only.
-- 3. debt_overdue alerts should use related_debt_id only.
CREATE TABLE `alerts` (
  `alert_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `alert_type` ENUM('budget_warning', 'budget_exceeded', 'debt_overdue', 'system_info', 'other') NOT NULL,
  `severity` ENUM('info', 'warning', 'critical') NOT NULL,
  `title` VARCHAR(150) NOT NULL,
  `message` TEXT NOT NULL,
  `related_budget_id` BIGINT UNSIGNED NULL,
  `related_expense_id` BIGINT UNSIGNED NULL,
  `related_debt_id` BIGINT UNSIGNED NULL,
  `is_read` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`alert_id`),
  CONSTRAINT `fk_alerts_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_alerts_budget`
    FOREIGN KEY (`related_budget_id`) REFERENCES `budgets` (`budget_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_alerts_expense`
    FOREIGN KEY (`related_expense_id`) REFERENCES `expenses` (`expense_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  CONSTRAINT `fk_alerts_debt`
    FOREIGN KEY (`related_debt_id`) REFERENCES `debts` (`debt_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  KEY `idx_alerts_user_id` (`user_id`),
  KEY `idx_alerts_alert_type` (`alert_type`),
  KEY `idx_alerts_is_read` (`is_read`),
  KEY `idx_alerts_created_at` (`created_at`),
  KEY `idx_alerts_user_is_read_created_at` (`user_id`, `is_read`, `created_at`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='User alerts and notifications';

CREATE TABLE `debt_payments` (
  `debt_payment_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `debt_id` BIGINT UNSIGNED NOT NULL,
  `bank_account_id` BIGINT UNSIGNED NULL,
  `payment_date` DATE NOT NULL,
  `amount` DECIMAL(18,2) NOT NULL,
  `note` TEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`debt_payment_id`),
  CONSTRAINT `chk_debt_payments_amount`
    CHECK (`amount` > 0),
  CONSTRAINT `fk_debt_payments_debt`
    FOREIGN KEY (`debt_id`) REFERENCES `debts` (`debt_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_debt_payments_bank_account`
    FOREIGN KEY (`bank_account_id`) REFERENCES `bank_accounts` (`bank_account_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  KEY `idx_debt_payments_debt_id` (`debt_id`),
  KEY `idx_debt_payments_payment_date` (`payment_date`),
  KEY `idx_debt_payments_bank_account_id` (`bank_account_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Debt repayment history';

CREATE TABLE `groups` (
  `group_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `owner_user_id` BIGINT UNSIGNED NOT NULL,
  `group_name` VARCHAR(120) NOT NULL,
  `description` VARCHAR(255) NULL,
  `status` ENUM('active', 'inactive', 'archived') NOT NULL DEFAULT 'active',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`group_id`),
  CONSTRAINT `fk_groups_owner_user`
    FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  KEY `idx_groups_owner_user_id` (`owner_user_id`),
  KEY `idx_groups_status` (`status`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Financial sharing groups';

CREATE TABLE `group_members` (
  `group_member_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `group_id` BIGINT UNSIGNED NOT NULL,
  `user_id` BIGINT UNSIGNED NOT NULL,
  `member_role` ENUM('owner', 'member') NOT NULL DEFAULT 'member',
  `joined_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` ENUM('active', 'left', 'removed') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`group_member_id`),
  CONSTRAINT `fk_group_members_group`
    FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_group_members_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  UNIQUE KEY `uq_group_members_group_user` (`group_id`, `user_id`),
  KEY `idx_group_members_user_id` (`user_id`),
  KEY `idx_group_members_status` (`status`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Membership of users in financial sharing groups';

-- Rule for triggers/backend:
-- 1. Exactly one of expense_id or income_id should be non-NULL.
-- 2. shared_by_user_id should belong to the group as an active member.
CREATE TABLE `shared_transactions` (
  `shared_transaction_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `group_id` BIGINT UNSIGNED NOT NULL,
  `shared_by_user_id` BIGINT UNSIGNED NOT NULL,
  `expense_id` BIGINT UNSIGNED NULL,
  `income_id` BIGINT UNSIGNED NULL,
  `visibility_status` ENUM('visible', 'hidden') NOT NULL DEFAULT 'visible',
  `note` VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`shared_transaction_id`),
  CONSTRAINT `fk_shared_transactions_group`
    FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_shared_transactions_user`
    FOREIGN KEY (`shared_by_user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_shared_transactions_group_member`
    FOREIGN KEY (`group_id`, `shared_by_user_id`) REFERENCES `group_members` (`group_id`, `user_id`)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT `fk_shared_transactions_expense`
    FOREIGN KEY (`expense_id`) REFERENCES `expenses` (`expense_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_shared_transactions_income`
    FOREIGN KEY (`income_id`) REFERENCES `incomes` (`income_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  KEY `idx_shared_transactions_group_id` (`group_id`),
  KEY `idx_shared_transactions_shared_by_user_id` (`shared_by_user_id`),
  KEY `idx_shared_transactions_expense_id` (`expense_id`),
  KEY `idx_shared_transactions_income_id` (`income_id`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Tracks sharing of an existing income or expense into a group';
