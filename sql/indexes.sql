-- Personal Finance Management System (PFMS)
-- Additional/index deployment script for MySQL 8.x
-- Run after sql/schema.sql.
--
-- The base schema already defines most indexes inline with table creation.
-- This file keeps index deployment explicit for DBMS submission and is
-- idempotent when re-run after schema.sql.

SET NAMES utf8mb4;
USE `pfms`;

DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_add_index_if_not_exists`$$

CREATE PROCEDURE `sp_add_index_if_not_exists`(
  IN p_table_name VARCHAR(64),
  IN p_index_name VARCHAR(64),
  IN p_create_index_sql TEXT
)
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.statistics
    WHERE table_schema = DATABASE()
      AND table_name = p_table_name
      AND index_name = p_index_name
  ) THEN
    SET @create_index_sql = p_create_index_sql;
    PREPARE create_index_stmt FROM @create_index_sql;
    EXECUTE create_index_stmt;
    DEALLOCATE PREPARE create_index_stmt;
  END IF;
END$$

DELIMITER ;

-- users(email) and users(username) are covered by uq_users_email and uq_users_username.
CALL `sp_add_index_if_not_exists`('users', 'idx_users_role',
  'CREATE INDEX `idx_users_role` ON `users` (`role`)');
CALL `sp_add_index_if_not_exists`('users', 'idx_users_is_active',
  'CREATE INDEX `idx_users_is_active` ON `users` (`is_active`)');

CALL `sp_add_index_if_not_exists`('categories', 'idx_categories_user_id',
  'CREATE INDEX `idx_categories_user_id` ON `categories` (`user_id`)');
CALL `sp_add_index_if_not_exists`('categories', 'idx_categories_category_type',
  'CREATE INDEX `idx_categories_category_type` ON `categories` (`category_type`)');
CALL `sp_add_index_if_not_exists`('categories', 'idx_categories_is_default',
  'CREATE INDEX `idx_categories_is_default` ON `categories` (`is_default`)');
CALL `sp_add_index_if_not_exists`('categories', 'idx_categories_is_active',
  'CREATE INDEX `idx_categories_is_active` ON `categories` (`is_active`)');

CALL `sp_add_index_if_not_exists`('bank_accounts', 'idx_bank_accounts_user_id',
  'CREATE INDEX `idx_bank_accounts_user_id` ON `bank_accounts` (`user_id`)');
CALL `sp_add_index_if_not_exists`('bank_accounts', 'idx_bank_accounts_account_type',
  'CREATE INDEX `idx_bank_accounts_account_type` ON `bank_accounts` (`account_type`)');
CALL `sp_add_index_if_not_exists`('bank_accounts', 'idx_bank_accounts_is_active',
  'CREATE INDEX `idx_bank_accounts_is_active` ON `bank_accounts` (`is_active`)');

CALL `sp_add_index_if_not_exists`('incomes', 'idx_incomes_user_id',
  'CREATE INDEX `idx_incomes_user_id` ON `incomes` (`user_id`)');
CALL `sp_add_index_if_not_exists`('incomes', 'idx_incomes_category_id',
  'CREATE INDEX `idx_incomes_category_id` ON `incomes` (`category_id`)');
CALL `sp_add_index_if_not_exists`('incomes', 'idx_incomes_income_date',
  'CREATE INDEX `idx_incomes_income_date` ON `incomes` (`income_date`)');
CALL `sp_add_index_if_not_exists`('incomes', 'idx_incomes_bank_account_id',
  'CREATE INDEX `idx_incomes_bank_account_id` ON `incomes` (`bank_account_id`)');
CALL `sp_add_index_if_not_exists`('incomes', 'idx_incomes_user_income_date',
  'CREATE INDEX `idx_incomes_user_income_date` ON `incomes` (`user_id`, `income_date`)');
CALL `sp_add_index_if_not_exists`('incomes', 'idx_incomes_user_status_income_date',
  'CREATE INDEX `idx_incomes_user_status_income_date` ON `incomes` (`user_id`, `status`, `income_date`)');

CALL `sp_add_index_if_not_exists`('expenses', 'idx_expenses_user_id',
  'CREATE INDEX `idx_expenses_user_id` ON `expenses` (`user_id`)');
CALL `sp_add_index_if_not_exists`('expenses', 'idx_expenses_category_id',
  'CREATE INDEX `idx_expenses_category_id` ON `expenses` (`category_id`)');
CALL `sp_add_index_if_not_exists`('expenses', 'idx_expenses_bank_account_id',
  'CREATE INDEX `idx_expenses_bank_account_id` ON `expenses` (`bank_account_id`)');
CALL `sp_add_index_if_not_exists`('expenses', 'idx_expenses_expense_date',
  'CREATE INDEX `idx_expenses_expense_date` ON `expenses` (`expense_date`)');
CALL `sp_add_index_if_not_exists`('expenses', 'idx_expenses_user_expense_date',
  'CREATE INDEX `idx_expenses_user_expense_date` ON `expenses` (`user_id`, `expense_date`)');
CALL `sp_add_index_if_not_exists`('expenses', 'idx_expenses_user_category_expense_date',
  'CREATE INDEX `idx_expenses_user_category_expense_date` ON `expenses` (`user_id`, `category_id`, `expense_date`)');
CALL `sp_add_index_if_not_exists`('expenses', 'idx_expenses_user_status_expense_date',
  'CREATE INDEX `idx_expenses_user_status_expense_date` ON `expenses` (`user_id`, `status`, `expense_date`)');
CALL `sp_add_index_if_not_exists`('expenses', 'idx_expenses_user_category_status_expense_date',
  'CREATE INDEX `idx_expenses_user_category_status_expense_date` ON `expenses` (`user_id`, `category_id`, `status`, `expense_date`)');

CALL `sp_add_index_if_not_exists`('budgets', 'idx_budgets_user_id',
  'CREATE INDEX `idx_budgets_user_id` ON `budgets` (`user_id`)');
CALL `sp_add_index_if_not_exists`('budgets', 'idx_budgets_category_id',
  'CREATE INDEX `idx_budgets_category_id` ON `budgets` (`category_id`)');
CALL `sp_add_index_if_not_exists`('budgets', 'idx_budgets_period_year_month',
  'CREATE INDEX `idx_budgets_period_year_month` ON `budgets` (`period_year`, `period_month`)');
CALL `sp_add_index_if_not_exists`('budgets', 'idx_budgets_user_period_year_month',
  'CREATE INDEX `idx_budgets_user_period_year_month` ON `budgets` (`user_id`, `period_year`, `period_month`)');

CALL `sp_add_index_if_not_exists`('alerts', 'idx_alerts_user_id',
  'CREATE INDEX `idx_alerts_user_id` ON `alerts` (`user_id`)');
CALL `sp_add_index_if_not_exists`('alerts', 'idx_alerts_alert_type',
  'CREATE INDEX `idx_alerts_alert_type` ON `alerts` (`alert_type`)');
CALL `sp_add_index_if_not_exists`('alerts', 'idx_alerts_is_read',
  'CREATE INDEX `idx_alerts_is_read` ON `alerts` (`is_read`)');
CALL `sp_add_index_if_not_exists`('alerts', 'idx_alerts_created_at',
  'CREATE INDEX `idx_alerts_created_at` ON `alerts` (`created_at`)');
CALL `sp_add_index_if_not_exists`('alerts', 'idx_alerts_user_is_read_created_at',
  'CREATE INDEX `idx_alerts_user_is_read_created_at` ON `alerts` (`user_id`, `is_read`, `created_at`)');

CALL `sp_add_index_if_not_exists`('debts', 'idx_debts_user_id',
  'CREATE INDEX `idx_debts_user_id` ON `debts` (`user_id`)');
CALL `sp_add_index_if_not_exists`('debts', 'idx_debts_status',
  'CREATE INDEX `idx_debts_status` ON `debts` (`status`)');
CALL `sp_add_index_if_not_exists`('debts', 'idx_debts_due_date',
  'CREATE INDEX `idx_debts_due_date` ON `debts` (`due_date`)');
CALL `sp_add_index_if_not_exists`('debts', 'idx_debts_user_status_due_date',
  'CREATE INDEX `idx_debts_user_status_due_date` ON `debts` (`user_id`, `status`, `due_date`)');

CALL `sp_add_index_if_not_exists`('debt_payments', 'idx_debt_payments_debt_id',
  'CREATE INDEX `idx_debt_payments_debt_id` ON `debt_payments` (`debt_id`)');
CALL `sp_add_index_if_not_exists`('debt_payments', 'idx_debt_payments_payment_date',
  'CREATE INDEX `idx_debt_payments_payment_date` ON `debt_payments` (`payment_date`)');
CALL `sp_add_index_if_not_exists`('debt_payments', 'idx_debt_payments_bank_account_id',
  'CREATE INDEX `idx_debt_payments_bank_account_id` ON `debt_payments` (`bank_account_id`)');

CALL `sp_add_index_if_not_exists`('groups', 'idx_groups_owner_user_id',
  'CREATE INDEX `idx_groups_owner_user_id` ON `groups` (`owner_user_id`)');
CALL `sp_add_index_if_not_exists`('groups', 'idx_groups_status',
  'CREATE INDEX `idx_groups_status` ON `groups` (`status`)');

-- group_members(group_id, user_id) is covered by uq_group_members_group_user.
CALL `sp_add_index_if_not_exists`('group_members', 'idx_group_members_user_id',
  'CREATE INDEX `idx_group_members_user_id` ON `group_members` (`user_id`)');
CALL `sp_add_index_if_not_exists`('group_members', 'idx_group_members_status',
  'CREATE INDEX `idx_group_members_status` ON `group_members` (`status`)');

CALL `sp_add_index_if_not_exists`('shared_transactions', 'idx_shared_transactions_group_id',
  'CREATE INDEX `idx_shared_transactions_group_id` ON `shared_transactions` (`group_id`)');
CALL `sp_add_index_if_not_exists`('shared_transactions', 'idx_shared_transactions_shared_by_user_id',
  'CREATE INDEX `idx_shared_transactions_shared_by_user_id` ON `shared_transactions` (`shared_by_user_id`)');
CALL `sp_add_index_if_not_exists`('shared_transactions', 'idx_shared_transactions_expense_id',
  'CREATE INDEX `idx_shared_transactions_expense_id` ON `shared_transactions` (`expense_id`)');
CALL `sp_add_index_if_not_exists`('shared_transactions', 'idx_shared_transactions_income_id',
  'CREATE INDEX `idx_shared_transactions_income_id` ON `shared_transactions` (`income_id`)');

DROP PROCEDURE IF EXISTS `sp_add_index_if_not_exists`;
