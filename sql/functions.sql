-- Personal Finance Management System (PFMS)
-- Scalar functions for budget and debt calculations
-- Run after sql/schema.sql.

SET NAMES utf8mb4;
USE `pfms`;

DELIMITER $$

DROP FUNCTION IF EXISTS `fn_budget_usage_percent`$$
CREATE FUNCTION `fn_budget_usage_percent`(p_budget_id BIGINT UNSIGNED)
RETURNS DECIMAL(7,2)
READS SQL DATA
BEGIN
  DECLARE v_not_found BOOLEAN DEFAULT FALSE;
  DECLARE v_user_id BIGINT UNSIGNED;
  DECLARE v_budget_scope VARCHAR(20);
  DECLARE v_category_id BIGINT UNSIGNED;
  DECLARE v_period_month TINYINT UNSIGNED;
  DECLARE v_period_year SMALLINT UNSIGNED;
  DECLARE v_spending_limit DECIMAL(18,2);
  DECLARE v_amount_used DECIMAL(18,2) DEFAULT 0.00;
  DECLARE v_start_date DATE;
  DECLARE v_end_date DATE;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_not_found = TRUE;

  SELECT
    `user_id`,
    `budget_scope`,
    `category_id`,
    `period_month`,
    `period_year`,
    `spending_limit`
  INTO
    v_user_id,
    v_budget_scope,
    v_category_id,
    v_period_month,
    v_period_year,
    v_spending_limit
  FROM `budgets`
  WHERE `budget_id` = p_budget_id
  LIMIT 1;

  IF v_not_found OR v_spending_limit IS NULL OR v_spending_limit <= 0 THEN
    RETURN NULL;
  END IF;

  SET v_start_date = STR_TO_DATE(
    CONCAT(v_period_year, '-', LPAD(v_period_month, 2, '0'), '-01'),
    '%Y-%m-%d'
  );
  SET v_end_date = DATE_ADD(v_start_date, INTERVAL 1 MONTH);

  SELECT COALESCE(SUM(e.`amount`), 0.00)
  INTO v_amount_used
  FROM `expenses` e
  WHERE e.`user_id` = v_user_id
    AND e.`status` = 'active'
    AND e.`expense_date` >= v_start_date
    AND e.`expense_date` < v_end_date
    AND (
      v_budget_scope = 'overall'
      OR e.`category_id` = v_category_id
    );

  RETURN ROUND((v_amount_used / v_spending_limit) * 100, 2);
END$$

DROP FUNCTION IF EXISTS `fn_remaining_budget`$$
CREATE FUNCTION `fn_remaining_budget`(p_budget_id BIGINT UNSIGNED)
RETURNS DECIMAL(18,2)
READS SQL DATA
BEGIN
  DECLARE v_not_found BOOLEAN DEFAULT FALSE;
  DECLARE v_user_id BIGINT UNSIGNED;
  DECLARE v_budget_scope VARCHAR(20);
  DECLARE v_category_id BIGINT UNSIGNED;
  DECLARE v_period_month TINYINT UNSIGNED;
  DECLARE v_period_year SMALLINT UNSIGNED;
  DECLARE v_spending_limit DECIMAL(18,2);
  DECLARE v_amount_used DECIMAL(18,2) DEFAULT 0.00;
  DECLARE v_start_date DATE;
  DECLARE v_end_date DATE;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_not_found = TRUE;

  SELECT
    `user_id`,
    `budget_scope`,
    `category_id`,
    `period_month`,
    `period_year`,
    `spending_limit`
  INTO
    v_user_id,
    v_budget_scope,
    v_category_id,
    v_period_month,
    v_period_year,
    v_spending_limit
  FROM `budgets`
  WHERE `budget_id` = p_budget_id
  LIMIT 1;

  IF v_not_found OR v_spending_limit IS NULL THEN
    RETURN NULL;
  END IF;

  SET v_start_date = STR_TO_DATE(
    CONCAT(v_period_year, '-', LPAD(v_period_month, 2, '0'), '-01'),
    '%Y-%m-%d'
  );
  SET v_end_date = DATE_ADD(v_start_date, INTERVAL 1 MONTH);

  SELECT COALESCE(SUM(e.`amount`), 0.00)
  INTO v_amount_used
  FROM `expenses` e
  WHERE e.`user_id` = v_user_id
    AND e.`status` = 'active'
    AND e.`expense_date` >= v_start_date
    AND e.`expense_date` < v_end_date
    AND (
      v_budget_scope = 'overall'
      OR e.`category_id` = v_category_id
    );

  RETURN ROUND(v_spending_limit - v_amount_used, 2);
END$$

DROP FUNCTION IF EXISTS `fn_debt_remaining`$$
CREATE FUNCTION `fn_debt_remaining`(p_debt_id BIGINT UNSIGNED)
RETURNS DECIMAL(18,2)
READS SQL DATA
BEGIN
  DECLARE v_not_found BOOLEAN DEFAULT FALSE;
  DECLARE v_original_amount DECIMAL(18,2);
  DECLARE v_paid_amount DECIMAL(18,2) DEFAULT 0.00;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_not_found = TRUE;

  SELECT
    d.`original_amount`,
    COALESCE(SUM(dp.`amount`), 0.00)
  INTO
    v_original_amount,
    v_paid_amount
  FROM `debts` d
  LEFT JOIN `debt_payments` dp
    ON dp.`debt_id` = d.`debt_id`
  WHERE d.`debt_id` = p_debt_id
  GROUP BY d.`debt_id`, d.`original_amount`
  LIMIT 1;

  IF v_not_found OR v_original_amount IS NULL THEN
    RETURN NULL;
  END IF;

  RETURN GREATEST(ROUND(v_original_amount - v_paid_amount, 2), 0.00);
END$$

DROP FUNCTION IF EXISTS `fn_monthly_income_total`$$
CREATE FUNCTION `fn_monthly_income_total`(
  p_user_id BIGINT UNSIGNED,
  p_year SMALLINT UNSIGNED,
  p_month TINYINT UNSIGNED
)
RETURNS DECIMAL(18,2)
READS SQL DATA
BEGIN
  DECLARE v_start_date DATE;
  DECLARE v_end_date DATE;
  DECLARE v_total DECIMAL(18,2) DEFAULT 0.00;

  IF p_user_id IS NULL
    OR p_year IS NULL
    OR p_month IS NULL
    OR p_month NOT BETWEEN 1 AND 12 THEN
    RETURN NULL;
  END IF;

  SET v_start_date = STR_TO_DATE(
    CONCAT(p_year, '-', LPAD(p_month, 2, '0'), '-01'),
    '%Y-%m-%d'
  );
  SET v_end_date = DATE_ADD(v_start_date, INTERVAL 1 MONTH);

  SELECT COALESCE(SUM(i.`amount`), 0.00)
  INTO v_total
  FROM `incomes` i
  WHERE i.`user_id` = p_user_id
    AND i.`status` = 'active'
    AND i.`income_date` >= v_start_date
    AND i.`income_date` < v_end_date;

  RETURN ROUND(v_total, 2);
END$$

DROP FUNCTION IF EXISTS `fn_monthly_expense_total`$$
CREATE FUNCTION `fn_monthly_expense_total`(
  p_user_id BIGINT UNSIGNED,
  p_year SMALLINT UNSIGNED,
  p_month TINYINT UNSIGNED
)
RETURNS DECIMAL(18,2)
READS SQL DATA
BEGIN
  DECLARE v_start_date DATE;
  DECLARE v_end_date DATE;
  DECLARE v_total DECIMAL(18,2) DEFAULT 0.00;

  IF p_user_id IS NULL
    OR p_year IS NULL
    OR p_month IS NULL
    OR p_month NOT BETWEEN 1 AND 12 THEN
    RETURN NULL;
  END IF;

  SET v_start_date = STR_TO_DATE(
    CONCAT(p_year, '-', LPAD(p_month, 2, '0'), '-01'),
    '%Y-%m-%d'
  );
  SET v_end_date = DATE_ADD(v_start_date, INTERVAL 1 MONTH);

  SELECT COALESCE(SUM(e.`amount`), 0.00)
  INTO v_total
  FROM `expenses` e
  WHERE e.`user_id` = p_user_id
    AND e.`status` = 'active'
    AND e.`expense_date` >= v_start_date
    AND e.`expense_date` < v_end_date;

  RETURN ROUND(v_total, 2);
END$$

DROP FUNCTION IF EXISTS `fn_monthly_net_amount`$$
CREATE FUNCTION `fn_monthly_net_amount`(
  p_user_id BIGINT UNSIGNED,
  p_year SMALLINT UNSIGNED,
  p_month TINYINT UNSIGNED
)
RETURNS DECIMAL(18,2)
READS SQL DATA
BEGIN
  DECLARE v_income_total DECIMAL(18,2);
  DECLARE v_expense_total DECIMAL(18,2);

  SET v_income_total = fn_monthly_income_total(p_user_id, p_year, p_month);
  SET v_expense_total = fn_monthly_expense_total(p_user_id, p_year, p_month);

  IF v_income_total IS NULL OR v_expense_total IS NULL THEN
    RETURN NULL;
  END IF;

  RETURN ROUND(v_income_total - v_expense_total, 2);
END$$

DELIMITER ;
