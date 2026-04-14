-- NUFI
-- Triggers for business rule validation and derived balance/status updates
-- Run after sql/schema.sql.

SET NAMES utf8mb4;
USE `pfms`;

DELIMITER $$

DROP TRIGGER IF EXISTS `trg_categories_bi_validate`$$
CREATE TRIGGER `trg_categories_bi_validate`
BEFORE INSERT ON `categories`
FOR EACH ROW
BEGIN
  IF NEW.`is_default` = TRUE AND NEW.`user_id` IS NOT NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Default category must not have user_id';
  END IF;

  IF NEW.`is_default` = FALSE AND NEW.`user_id` IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Personal category must have user_id';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_categories_bu_validate`$$
CREATE TRIGGER `trg_categories_bu_validate`
BEFORE UPDATE ON `categories`
FOR EACH ROW
BEGIN
  IF NEW.`is_default` = TRUE AND NEW.`user_id` IS NOT NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Default category must not have user_id';
  END IF;

  IF NEW.`is_default` = FALSE AND NEW.`user_id` IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Personal category must have user_id';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_incomes_bi_validate`$$
CREATE TRIGGER `trg_incomes_bi_validate`
BEFORE INSERT ON `incomes`
FOR EACH ROW
BEGIN
  IF NEW.`status` = 'active'
    AND NOT EXISTS (
      SELECT 1
      FROM `categories` c
      WHERE c.`category_id` = NEW.`category_id`
        AND c.`is_active` = TRUE
        AND c.`category_type` IN ('income', 'both')
        AND (c.`user_id` IS NULL OR c.`user_id` = NEW.`user_id`)
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid income category';
  END IF;

  IF NEW.`bank_account_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `bank_accounts` ba
      WHERE ba.`bank_account_id` = NEW.`bank_account_id`
        AND ba.`user_id` = NEW.`user_id`
        AND ba.`is_active` = TRUE
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid income bank account';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_incomes_bu_validate`$$
CREATE TRIGGER `trg_incomes_bu_validate`
BEFORE UPDATE ON `incomes`
FOR EACH ROW
BEGIN
  IF NEW.`status` = 'active'
    AND NOT EXISTS (
      SELECT 1
      FROM `categories` c
      WHERE c.`category_id` = NEW.`category_id`
        AND c.`is_active` = TRUE
        AND c.`category_type` IN ('income', 'both')
        AND (c.`user_id` IS NULL OR c.`user_id` = NEW.`user_id`)
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid income category';
  END IF;

  IF NEW.`status` = 'active'
    AND NEW.`bank_account_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `bank_accounts` ba
      WHERE ba.`bank_account_id` = NEW.`bank_account_id`
        AND ba.`user_id` = NEW.`user_id`
        AND ba.`is_active` = TRUE
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid income bank account';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_incomes_ai_update_balance`$$
CREATE TRIGGER `trg_incomes_ai_update_balance`
AFTER INSERT ON `incomes`
FOR EACH ROW
BEGIN
  IF NEW.`status` = 'active' AND NEW.`bank_account_id` IS NOT NULL THEN
    UPDATE `bank_accounts`
    SET `current_balance` = `current_balance` + NEW.`amount`
    WHERE `bank_account_id` = NEW.`bank_account_id`;
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_incomes_au_update_balance`$$
CREATE TRIGGER `trg_incomes_au_update_balance`
AFTER UPDATE ON `incomes`
FOR EACH ROW
BEGIN
  IF OLD.`status` = 'active' AND OLD.`bank_account_id` IS NOT NULL THEN
    UPDATE `bank_accounts`
    SET `current_balance` = `current_balance` - OLD.`amount`
    WHERE `bank_account_id` = OLD.`bank_account_id`;
  END IF;

  IF NEW.`status` = 'active' AND NEW.`bank_account_id` IS NOT NULL THEN
    UPDATE `bank_accounts`
    SET `current_balance` = `current_balance` + NEW.`amount`
    WHERE `bank_account_id` = NEW.`bank_account_id`;
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_expenses_bi_validate`$$
CREATE TRIGGER `trg_expenses_bi_validate`
BEFORE INSERT ON `expenses`
FOR EACH ROW
BEGIN
  IF NEW.`status` = 'active'
    AND NOT EXISTS (
      SELECT 1
      FROM `categories` c
      WHERE c.`category_id` = NEW.`category_id`
        AND c.`is_active` = TRUE
        AND c.`category_type` IN ('expense', 'both')
        AND (c.`user_id` IS NULL OR c.`user_id` = NEW.`user_id`)
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid expense category';
  END IF;

  IF NEW.`bank_account_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `bank_accounts` ba
      WHERE ba.`bank_account_id` = NEW.`bank_account_id`
        AND ba.`user_id` = NEW.`user_id`
        AND ba.`is_active` = TRUE
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid expense bank account';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_expenses_bu_validate`$$
CREATE TRIGGER `trg_expenses_bu_validate`
BEFORE UPDATE ON `expenses`
FOR EACH ROW
BEGIN
  IF NEW.`status` = 'active'
    AND NOT EXISTS (
      SELECT 1
      FROM `categories` c
      WHERE c.`category_id` = NEW.`category_id`
        AND c.`is_active` = TRUE
        AND c.`category_type` IN ('expense', 'both')
        AND (c.`user_id` IS NULL OR c.`user_id` = NEW.`user_id`)
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid expense category';
  END IF;

  IF NEW.`status` = 'active'
    AND NEW.`bank_account_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `bank_accounts` ba
      WHERE ba.`bank_account_id` = NEW.`bank_account_id`
        AND ba.`user_id` = NEW.`user_id`
        AND ba.`is_active` = TRUE
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid expense bank account';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_expenses_ai_update_balance`$$
CREATE TRIGGER `trg_expenses_ai_update_balance`
AFTER INSERT ON `expenses`
FOR EACH ROW
BEGIN
  IF NEW.`status` = 'active' AND NEW.`bank_account_id` IS NOT NULL THEN
    UPDATE `bank_accounts`
    SET `current_balance` = `current_balance` - NEW.`amount`
    WHERE `bank_account_id` = NEW.`bank_account_id`;
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_expenses_au_update_balance`$$
CREATE TRIGGER `trg_expenses_au_update_balance`
AFTER UPDATE ON `expenses`
FOR EACH ROW
BEGIN
  IF OLD.`status` = 'active' AND OLD.`bank_account_id` IS NOT NULL THEN
    UPDATE `bank_accounts`
    SET `current_balance` = `current_balance` + OLD.`amount`
    WHERE `bank_account_id` = OLD.`bank_account_id`;
  END IF;

  IF NEW.`status` = 'active' AND NEW.`bank_account_id` IS NOT NULL THEN
    UPDATE `bank_accounts`
    SET `current_balance` = `current_balance` - NEW.`amount`
    WHERE `bank_account_id` = NEW.`bank_account_id`;
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_budgets_bi_validate`$$
CREATE TRIGGER `trg_budgets_bi_validate`
BEFORE INSERT ON `budgets`
FOR EACH ROW
BEGIN
  IF NEW.`budget_scope` = 'overall' AND NEW.`category_id` IS NOT NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Overall budget must not have category_id';
  END IF;

  IF NEW.`budget_scope` = 'category' AND NEW.`category_id` IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Category budget must have category_id';
  END IF;

  IF NEW.`budget_scope` = 'category'
    AND NOT EXISTS (
      SELECT 1
      FROM `categories` c
      WHERE c.`category_id` = NEW.`category_id`
        AND c.`is_active` = TRUE
        AND c.`category_type` IN ('expense', 'both')
        AND (c.`user_id` IS NULL OR c.`user_id` = NEW.`user_id`)
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid budget category';
  END IF;

  IF NEW.`status` = 'active'
    AND EXISTS (
      SELECT 1
      FROM `budgets` b
      WHERE b.`user_id` = NEW.`user_id`
        AND b.`status` = 'active'
        AND b.`budget_scope` = NEW.`budget_scope`
        AND b.`period_year` = NEW.`period_year`
        AND b.`period_month` = NEW.`period_month`
        AND (
          (NEW.`budget_scope` = 'overall' AND b.`category_id` IS NULL)
          OR (NEW.`budget_scope` = 'category' AND b.`category_id` = NEW.`category_id`)
        )
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Duplicate active budget for this period';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_budgets_bu_validate`$$
CREATE TRIGGER `trg_budgets_bu_validate`
BEFORE UPDATE ON `budgets`
FOR EACH ROW
BEGIN
  IF NEW.`budget_scope` = 'overall' AND NEW.`category_id` IS NOT NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Overall budget must not have category_id';
  END IF;

  IF NEW.`budget_scope` = 'category' AND NEW.`category_id` IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Category budget must have category_id';
  END IF;

  IF NEW.`budget_scope` = 'category'
    AND NOT EXISTS (
      SELECT 1
      FROM `categories` c
      WHERE c.`category_id` = NEW.`category_id`
        AND c.`is_active` = TRUE
        AND c.`category_type` IN ('expense', 'both')
        AND (c.`user_id` IS NULL OR c.`user_id` = NEW.`user_id`)
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Invalid budget category';
  END IF;

  IF NEW.`status` = 'active'
    AND EXISTS (
      SELECT 1
      FROM `budgets` b
      WHERE b.`budget_id` <> NEW.`budget_id`
        AND b.`user_id` = NEW.`user_id`
        AND b.`status` = 'active'
        AND b.`budget_scope` = NEW.`budget_scope`
        AND b.`period_year` = NEW.`period_year`
        AND b.`period_month` = NEW.`period_month`
        AND (
          (NEW.`budget_scope` = 'overall' AND b.`category_id` IS NULL)
          OR (NEW.`budget_scope` = 'category' AND b.`category_id` = NEW.`category_id`)
        )
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Duplicate active budget for this period';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_alerts_bi_validate`$$
CREATE TRIGGER `trg_alerts_bi_validate`
BEFORE INSERT ON `alerts`
FOR EACH ROW
BEGIN
  IF (
    (CASE WHEN NEW.`related_budget_id` IS NOT NULL THEN 1 ELSE 0 END)
    + (CASE WHEN NEW.`related_expense_id` IS NOT NULL THEN 1 ELSE 0 END)
    + (CASE WHEN NEW.`related_debt_id` IS NOT NULL THEN 1 ELSE 0 END)
  ) > 1 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Alert can reference at most one related object';
  END IF;

  IF NEW.`alert_type` IN ('budget_warning', 'budget_exceeded')
    AND NEW.`related_budget_id` IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Budget alert requires related_budget_id';
  END IF;

  IF NEW.`alert_type` = 'debt_overdue'
    AND NEW.`related_debt_id` IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt overdue alert requires related_debt_id';
  END IF;

  IF NEW.`alert_type` = 'system_info'
    AND (
      NEW.`related_budget_id` IS NOT NULL
      OR NEW.`related_expense_id` IS NOT NULL
      OR NEW.`related_debt_id` IS NOT NULL
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'System info alert must not reference business objects';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_alerts_bu_validate`$$
CREATE TRIGGER `trg_alerts_bu_validate`
BEFORE UPDATE ON `alerts`
FOR EACH ROW
BEGIN
  IF (
    (CASE WHEN NEW.`related_budget_id` IS NOT NULL THEN 1 ELSE 0 END)
    + (CASE WHEN NEW.`related_expense_id` IS NOT NULL THEN 1 ELSE 0 END)
    + (CASE WHEN NEW.`related_debt_id` IS NOT NULL THEN 1 ELSE 0 END)
  ) > 1 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Alert can reference at most one related object';
  END IF;

  IF NEW.`alert_type` IN ('budget_warning', 'budget_exceeded')
    AND NEW.`related_budget_id` IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Budget alert requires related_budget_id';
  END IF;

  IF NEW.`alert_type` = 'debt_overdue'
    AND NEW.`related_debt_id` IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt overdue alert requires related_debt_id';
  END IF;

  IF NEW.`alert_type` = 'system_info'
    AND (
      NEW.`related_budget_id` IS NOT NULL
      OR NEW.`related_expense_id` IS NOT NULL
      OR NEW.`related_debt_id` IS NOT NULL
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'System info alert must not reference business objects';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_shared_transactions_bi_validate`$$
CREATE TRIGGER `trg_shared_transactions_bi_validate`
BEFORE INSERT ON `shared_transactions`
FOR EACH ROW
BEGIN
  IF (NEW.`expense_id` IS NULL AND NEW.`income_id` IS NULL)
    OR (NEW.`expense_id` IS NOT NULL AND NEW.`income_id` IS NOT NULL) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Share exactly one income or expense';
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM `group_members` gm
    WHERE gm.`group_id` = NEW.`group_id`
      AND gm.`user_id` = NEW.`shared_by_user_id`
      AND gm.`status` = 'active'
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'User is not an active group member';
  END IF;

  IF NEW.`expense_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `expenses` e
      WHERE e.`expense_id` = NEW.`expense_id`
        AND e.`user_id` = NEW.`shared_by_user_id`
        AND e.`status` = 'active'
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Shared expense is invalid';
  END IF;

  IF NEW.`income_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `incomes` i
      WHERE i.`income_id` = NEW.`income_id`
        AND i.`user_id` = NEW.`shared_by_user_id`
        AND i.`status` = 'active'
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Shared income is invalid';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_shared_transactions_bu_validate`$$
CREATE TRIGGER `trg_shared_transactions_bu_validate`
BEFORE UPDATE ON `shared_transactions`
FOR EACH ROW
BEGIN
  IF (NEW.`expense_id` IS NULL AND NEW.`income_id` IS NULL)
    OR (NEW.`expense_id` IS NOT NULL AND NEW.`income_id` IS NOT NULL) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Share exactly one income or expense';
  END IF;

  IF NOT EXISTS (
    SELECT 1
    FROM `group_members` gm
    WHERE gm.`group_id` = NEW.`group_id`
      AND gm.`user_id` = NEW.`shared_by_user_id`
      AND gm.`status` = 'active'
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'User is not an active group member';
  END IF;

  IF NEW.`expense_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `expenses` e
      WHERE e.`expense_id` = NEW.`expense_id`
        AND e.`user_id` = NEW.`shared_by_user_id`
        AND e.`status` = 'active'
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Shared expense is invalid';
  END IF;

  IF NEW.`income_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `incomes` i
      WHERE i.`income_id` = NEW.`income_id`
        AND i.`user_id` = NEW.`shared_by_user_id`
        AND i.`status` = 'active'
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Shared income is invalid';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_debt_payments_bi_validate`$$
CREATE TRIGGER `trg_debt_payments_bi_validate`
BEFORE INSERT ON `debt_payments`
FOR EACH ROW
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM `debts` d
    WHERE d.`debt_id` = NEW.`debt_id`
      AND d.`is_active` = TRUE
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt payment requires an active debt';
  END IF;

  IF NEW.`bank_account_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `debts` d
      INNER JOIN `bank_accounts` ba
        ON ba.`bank_account_id` = NEW.`bank_account_id`
        AND ba.`user_id` = d.`user_id`
        AND ba.`is_active` = TRUE
      WHERE d.`debt_id` = NEW.`debt_id`
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt payment bank account must belong to debt owner';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_debt_payments_bu_validate`$$
CREATE TRIGGER `trg_debt_payments_bu_validate`
BEFORE UPDATE ON `debt_payments`
FOR EACH ROW
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM `debts` d
    WHERE d.`debt_id` = NEW.`debt_id`
      AND d.`is_active` = TRUE
  ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt payment requires an active debt';
  END IF;

  IF NEW.`bank_account_id` IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `debts` d
      INNER JOIN `bank_accounts` ba
        ON ba.`bank_account_id` = NEW.`bank_account_id`
        AND ba.`user_id` = d.`user_id`
        AND ba.`is_active` = TRUE
      WHERE d.`debt_id` = NEW.`debt_id`
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt payment bank account must belong to debt owner';
  END IF;
END$$

DROP TRIGGER IF EXISTS `trg_debt_payments_ai_update_debt`$$
CREATE TRIGGER `trg_debt_payments_ai_update_debt`
AFTER INSERT ON `debt_payments`
FOR EACH ROW
BEGIN
  UPDATE `debts` d
  SET
    d.`remaining_amount` = GREATEST(d.`remaining_amount` - NEW.`amount`, 0.00),
    d.`status` = CASE
      WHEN GREATEST(d.`remaining_amount` - NEW.`amount`, 0.00) = 0 THEN 'paid'
      WHEN d.`due_date` IS NOT NULL AND d.`due_date` < CURDATE() THEN 'overdue'
      WHEN GREATEST(d.`remaining_amount` - NEW.`amount`, 0.00) < d.`original_amount` THEN 'partially_paid'
      ELSE 'pending'
    END
  WHERE d.`debt_id` = NEW.`debt_id`;
END$$

DROP TRIGGER IF EXISTS `trg_debt_payments_au_update_debt`$$
CREATE TRIGGER `trg_debt_payments_au_update_debt`
AFTER UPDATE ON `debt_payments`
FOR EACH ROW
BEGIN
  IF OLD.`debt_id` = NEW.`debt_id` THEN
    UPDATE `debts` d
    SET
      d.`remaining_amount` = LEAST(
        d.`original_amount`,
        GREATEST(d.`remaining_amount` - (NEW.`amount` - OLD.`amount`), 0.00)
      ),
      d.`status` = CASE
        WHEN LEAST(d.`original_amount`, GREATEST(d.`remaining_amount` - (NEW.`amount` - OLD.`amount`), 0.00)) = 0 THEN 'paid'
        WHEN d.`due_date` IS NOT NULL AND d.`due_date` < CURDATE() THEN 'overdue'
        WHEN LEAST(d.`original_amount`, GREATEST(d.`remaining_amount` - (NEW.`amount` - OLD.`amount`), 0.00)) < d.`original_amount` THEN 'partially_paid'
        ELSE 'pending'
      END
    WHERE d.`debt_id` = NEW.`debt_id`;
  ELSE
    UPDATE `debts` d
    SET
      d.`remaining_amount` = LEAST(d.`original_amount`, d.`remaining_amount` + OLD.`amount`),
      d.`status` = CASE
        WHEN LEAST(d.`original_amount`, d.`remaining_amount` + OLD.`amount`) = 0 THEN 'paid'
        WHEN d.`due_date` IS NOT NULL AND d.`due_date` < CURDATE()
          AND LEAST(d.`original_amount`, d.`remaining_amount` + OLD.`amount`) > 0 THEN 'overdue'
        WHEN LEAST(d.`original_amount`, d.`remaining_amount` + OLD.`amount`) < d.`original_amount` THEN 'partially_paid'
        ELSE 'pending'
      END
    WHERE d.`debt_id` = OLD.`debt_id`;

    UPDATE `debts` d
    SET
      d.`remaining_amount` = GREATEST(d.`remaining_amount` - NEW.`amount`, 0.00),
      d.`status` = CASE
        WHEN GREATEST(d.`remaining_amount` - NEW.`amount`, 0.00) = 0 THEN 'paid'
        WHEN d.`due_date` IS NOT NULL AND d.`due_date` < CURDATE() THEN 'overdue'
        WHEN GREATEST(d.`remaining_amount` - NEW.`amount`, 0.00) < d.`original_amount` THEN 'partially_paid'
        ELSE 'pending'
      END
    WHERE d.`debt_id` = NEW.`debt_id`;
  END IF;
END$$

DELIMITER ;
