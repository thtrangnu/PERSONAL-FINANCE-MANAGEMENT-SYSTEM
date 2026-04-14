-- Personal Finance Management System (PFMS)
-- Stored procedures for transaction creation and monthly summary
-- Run after sql/schema.sql, sql/functions.sql, and sql/triggers.sql.

SET NAMES utf8mb4;
USE `pfms`;

DELIMITER $$

DROP PROCEDURE IF EXISTS `sp_create_expense`$$
CREATE PROCEDURE `sp_create_expense`(
  IN p_user_id BIGINT UNSIGNED,
  IN p_category_id BIGINT UNSIGNED,
  IN p_bank_account_id BIGINT UNSIGNED,
  IN p_amount DECIMAL(18,2),
  IN p_expense_date DATE,
  IN p_payment_method VARCHAR(20),
  IN p_description VARCHAR(255),
  IN p_note TEXT,
  OUT p_expense_id BIGINT UNSIGNED
)
BEGIN
  DECLARE v_start_date DATE;
  DECLARE v_end_date DATE;

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  SET p_expense_id = NULL;

  IF p_user_id IS NULL OR p_category_id IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Expense requires user_id and category_id';
  END IF;

  IF p_amount IS NULL OR p_amount <= 0 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Expense amount must be greater than 0';
  END IF;

  IF p_expense_date IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Expense date is required';
  END IF;

  IF p_bank_account_id IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `bank_accounts` ba
      WHERE ba.`bank_account_id` = p_bank_account_id
        AND ba.`user_id` = p_user_id
        AND ba.`is_active` = TRUE
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Bank account is invalid for this user';
  END IF;

  START TRANSACTION;

  INSERT INTO `expenses` (
    `user_id`,
    `category_id`,
    `bank_account_id`,
    `amount`,
    `expense_date`,
    `payment_method`,
    `description`,
    `note`,
    `status`
  )
  VALUES (
    p_user_id,
    p_category_id,
    p_bank_account_id,
    p_amount,
    p_expense_date,
    p_payment_method,
    p_description,
    p_note,
    'active'
  );

  SET p_expense_id = LAST_INSERT_ID();
  SET v_start_date = STR_TO_DATE(
    CONCAT(YEAR(p_expense_date), '-', LPAD(MONTH(p_expense_date), 2, '0'), '-01'),
    '%Y-%m-%d'
  );
  SET v_end_date = DATE_ADD(v_start_date, INTERVAL 1 MONTH);

  INSERT INTO `alerts` (
    `user_id`,
    `alert_type`,
    `severity`,
    `title`,
    `message`,
    `related_budget_id`,
    `is_read`,
    `created_at`
  )
  SELECT
    p_user_id,
    CASE
      WHEN bu.`amount_used` >= bu.`spending_limit` THEN 'budget_exceeded'
      ELSE 'budget_warning'
    END AS `alert_type`,
    CASE
      WHEN bu.`amount_used` >= bu.`spending_limit` THEN 'critical'
      ELSE 'warning'
    END AS `severity`,
    CASE
      WHEN bu.`amount_used` >= bu.`spending_limit` THEN 'Budget exceeded'
      ELSE 'Budget warning'
    END AS `title`,
    CONCAT(
      'Budget ', bu.`budget_name`, ' used ',
      ROUND((bu.`amount_used` / bu.`spending_limit`) * 100, 2),
      ' percent.'
    ) AS `message`,
    bu.`budget_id`,
    FALSE,
    CURRENT_TIMESTAMP
  FROM (
    SELECT
      b.`budget_id`,
      b.`budget_name`,
      b.`spending_limit`,
      b.`warning_percent`,
      COALESCE(SUM(e.`amount`), 0.00) AS `amount_used`
    FROM `budgets` b
    LEFT JOIN `expenses` e
      ON e.`user_id` = b.`user_id`
      AND e.`status` = 'active'
      AND e.`expense_date` >= v_start_date
      AND e.`expense_date` < v_end_date
      AND (
        b.`budget_scope` = 'overall'
        OR e.`category_id` = b.`category_id`
      )
    WHERE b.`user_id` = p_user_id
      AND b.`status` = 'active'
      AND b.`period_year` = YEAR(p_expense_date)
      AND b.`period_month` = MONTH(p_expense_date)
      AND (
        b.`budget_scope` = 'overall'
        OR b.`category_id` = p_category_id
      )
    GROUP BY
      b.`budget_id`,
      b.`budget_name`,
      b.`spending_limit`,
      b.`warning_percent`
  ) bu
  WHERE bu.`amount_used` >= (bu.`spending_limit` * bu.`warning_percent` / 100)
    AND NOT EXISTS (
      SELECT 1
      FROM `alerts` a
      WHERE a.`related_budget_id` = bu.`budget_id`
        AND a.`alert_type` = CASE
          WHEN bu.`amount_used` >= bu.`spending_limit` THEN 'budget_exceeded'
          ELSE 'budget_warning'
        END
    );

  COMMIT;
END$$

DROP PROCEDURE IF EXISTS `sp_create_income`$$
CREATE PROCEDURE `sp_create_income`(
  IN p_user_id BIGINT UNSIGNED,
  IN p_category_id BIGINT UNSIGNED,
  IN p_bank_account_id BIGINT UNSIGNED,
  IN p_title VARCHAR(150),
  IN p_amount DECIMAL(18,2),
  IN p_income_date DATE,
  IN p_description VARCHAR(255),
  IN p_note TEXT,
  OUT p_income_id BIGINT UNSIGNED
)
BEGIN
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  SET p_income_id = NULL;

  IF p_user_id IS NULL OR p_category_id IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Income requires user_id and category_id';
  END IF;

  IF p_title IS NULL OR TRIM(p_title) = '' THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Income title is required';
  END IF;

  IF p_amount IS NULL OR p_amount <= 0 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Income amount must be greater than 0';
  END IF;

  IF p_income_date IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Income date is required';
  END IF;

  IF p_bank_account_id IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `bank_accounts` ba
      WHERE ba.`bank_account_id` = p_bank_account_id
        AND ba.`user_id` = p_user_id
        AND ba.`is_active` = TRUE
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Bank account is invalid for this user';
  END IF;

  START TRANSACTION;

  INSERT INTO `incomes` (
    `user_id`,
    `category_id`,
    `bank_account_id`,
    `title`,
    `amount`,
    `income_date`,
    `description`,
    `note`,
    `status`
  )
  VALUES (
    p_user_id,
    p_category_id,
    p_bank_account_id,
    p_title,
    p_amount,
    p_income_date,
    p_description,
    p_note,
    'active'
  );

  SET p_income_id = LAST_INSERT_ID();

  COMMIT;
END$$

DROP PROCEDURE IF EXISTS `sp_create_debt_payment`$$
CREATE PROCEDURE `sp_create_debt_payment`(
  IN p_debt_id BIGINT UNSIGNED,
  IN p_bank_account_id BIGINT UNSIGNED,
  IN p_payment_date DATE,
  IN p_amount DECIMAL(18,2),
  IN p_note TEXT,
  OUT p_debt_payment_id BIGINT UNSIGNED
)
BEGIN
  DECLARE v_not_found BOOLEAN DEFAULT FALSE;
  DECLARE v_user_id BIGINT UNSIGNED;
  DECLARE v_remaining_amount DECIMAL(18,2);

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_not_found = TRUE;
  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  SET p_debt_payment_id = NULL;

  IF p_debt_id IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt payment requires debt_id';
  END IF;

  IF p_payment_date IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt payment date is required';
  END IF;

  IF p_amount IS NULL OR p_amount <= 0 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt payment amount must be greater than 0';
  END IF;

  SELECT d.`user_id`, d.`remaining_amount`
  INTO v_user_id, v_remaining_amount
  FROM `debts` d
  WHERE d.`debt_id` = p_debt_id
    AND d.`is_active` = TRUE
  LIMIT 1;

  IF v_not_found THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt is invalid or inactive';
  END IF;

  IF p_amount > v_remaining_amount THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Debt payment amount cannot exceed remaining debt';
  END IF;

  IF p_bank_account_id IS NOT NULL
    AND NOT EXISTS (
      SELECT 1
      FROM `bank_accounts` ba
      WHERE ba.`bank_account_id` = p_bank_account_id
        AND ba.`user_id` = v_user_id
        AND ba.`is_active` = TRUE
    ) THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Bank account is invalid for this debt owner';
  END IF;

  START TRANSACTION;

  INSERT INTO `debt_payments` (
    `debt_id`,
    `bank_account_id`,
    `payment_date`,
    `amount`,
    `note`
  )
  VALUES (
    p_debt_id,
    p_bank_account_id,
    p_payment_date,
    p_amount,
    p_note
  );

  SET p_debt_payment_id = LAST_INSERT_ID();

  COMMIT;
END$$

DROP PROCEDURE IF EXISTS `sp_monthly_summary`$$
CREATE PROCEDURE `sp_monthly_summary`(
  IN p_user_id BIGINT UNSIGNED,
  IN p_year SMALLINT UNSIGNED,
  IN p_month TINYINT UNSIGNED
)
BEGIN
  IF p_user_id IS NULL
    OR p_year IS NULL
    OR p_month IS NULL
    OR p_month NOT BETWEEN 1 AND 12 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Monthly summary requires valid user, year, and month';
  END IF;

  SELECT
    p_user_id AS `user_id`,
    p_year AS `period_year`,
    p_month AS `period_month`,
    fn_monthly_income_total(p_user_id, p_year, p_month) AS `total_income`,
    fn_monthly_expense_total(p_user_id, p_year, p_month) AS `total_expense`,
    fn_monthly_net_amount(p_user_id, p_year, p_month) AS `net_amount`,
    COALESCE((
      SELECT SUM(ba.`current_balance`)
      FROM `bank_accounts` ba
      WHERE ba.`user_id` = p_user_id
        AND ba.`is_active` = TRUE
    ), 0.00) AS `total_active_balance`,
    COALESCE((
      SELECT COUNT(*)
      FROM `alerts` a
      WHERE a.`user_id` = p_user_id
        AND a.`is_read` = FALSE
    ), 0) AS `unread_alert_count`,
    COALESCE((
      SELECT SUM(d.`remaining_amount`)
      FROM `debts` d
      WHERE d.`user_id` = p_user_id
        AND d.`is_active` = TRUE
        AND d.`status` IN ('pending', 'partially_paid', 'overdue')
    ), 0.00) AS `active_debt_remaining`;
END$$

DELIMITER ;
