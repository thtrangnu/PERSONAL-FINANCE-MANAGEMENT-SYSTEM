-- Personal Finance Management System (PFMS)
-- Views for reporting and dashboard queries
-- Run after sql/schema.sql.

SET NAMES utf8mb4;
USE `pfms`;

CREATE OR REPLACE VIEW `vw_monthly_expense_summary` AS
SELECT
  e.`user_id`,
  YEAR(e.`expense_date`) AS `period_year`,
  MONTH(e.`expense_date`) AS `period_month`,
  e.`category_id`,
  c.`category_name`,
  c.`category_type`,
  COUNT(*) AS `expense_count`,
  COALESCE(SUM(e.`amount`), 0.00) AS `total_expense`
FROM `expenses` e
INNER JOIN `categories` c
  ON c.`category_id` = e.`category_id`
WHERE e.`status` = 'active'
GROUP BY
  e.`user_id`,
  YEAR(e.`expense_date`),
  MONTH(e.`expense_date`),
  e.`category_id`,
  c.`category_name`,
  c.`category_type`;

CREATE OR REPLACE VIEW `vw_monthly_income_summary` AS
SELECT
  i.`user_id`,
  YEAR(i.`income_date`) AS `period_year`,
  MONTH(i.`income_date`) AS `period_month`,
  i.`category_id`,
  c.`category_name`,
  c.`category_type`,
  COUNT(*) AS `income_count`,
  COALESCE(SUM(i.`amount`), 0.00) AS `total_income`
FROM `incomes` i
INNER JOIN `categories` c
  ON c.`category_id` = i.`category_id`
WHERE i.`status` = 'active'
GROUP BY
  i.`user_id`,
  YEAR(i.`income_date`),
  MONTH(i.`income_date`),
  i.`category_id`,
  c.`category_name`,
  c.`category_type`;

CREATE OR REPLACE VIEW `vw_budget_usage` AS
SELECT
  b.`budget_id`,
  b.`user_id`,
  b.`budget_name`,
  b.`budget_scope`,
  b.`category_id`,
  c.`category_name`,
  b.`period_year`,
  b.`period_month`,
  b.`spending_limit`,
  b.`warning_percent`,
  b.`status`,
  COALESCE(bu.`amount_used`, 0.00) AS `amount_used`,
  ROUND(b.`spending_limit` - COALESCE(bu.`amount_used`, 0.00), 2) AS `remaining_amount`,
  ROUND((COALESCE(bu.`amount_used`, 0.00) / b.`spending_limit`) * 100, 2) AS `usage_percent`,
  CASE
    WHEN COALESCE(bu.`amount_used`, 0.00) >= b.`spending_limit` THEN 'exceeded'
    WHEN COALESCE(bu.`amount_used`, 0.00) >= (b.`spending_limit` * b.`warning_percent` / 100) THEN 'warning'
    ELSE 'normal'
  END AS `usage_status`
FROM `budgets` b
LEFT JOIN `categories` c
  ON c.`category_id` = b.`category_id`
LEFT JOIN (
  SELECT
    b2.`budget_id`,
    COALESCE(SUM(e.`amount`), 0.00) AS `amount_used`
  FROM `budgets` b2
  LEFT JOIN `expenses` e
    ON e.`user_id` = b2.`user_id`
    AND e.`status` = 'active'
    AND e.`expense_date` >= STR_TO_DATE(
      CONCAT(b2.`period_year`, '-', LPAD(b2.`period_month`, 2, '0'), '-01'),
      '%Y-%m-%d'
    )
    AND e.`expense_date` < DATE_ADD(
      STR_TO_DATE(CONCAT(b2.`period_year`, '-', LPAD(b2.`period_month`, 2, '0'), '-01'), '%Y-%m-%d'),
      INTERVAL 1 MONTH
    )
    AND (
      b2.`budget_scope` = 'overall'
      OR e.`category_id` = b2.`category_id`
    )
  GROUP BY b2.`budget_id`
) bu
  ON bu.`budget_id` = b.`budget_id`;

CREATE OR REPLACE VIEW `vw_dashboard_snapshot` AS
SELECT
  u.`user_id`,
  u.`username`,
  u.`full_name`,
  u.`default_currency`,
  COALESCE(ba.`total_balance`, 0.00) AS `total_balance`,
  COALESCE(mi.`current_month_income`, 0.00) AS `current_month_income`,
  COALESCE(me.`current_month_expense`, 0.00) AS `current_month_expense`,
  ROUND(
    COALESCE(mi.`current_month_income`, 0.00) - COALESCE(me.`current_month_expense`, 0.00),
    2
  ) AS `current_month_net_amount`,
  COALESCE(al.`unread_alert_count`, 0) AS `unread_alert_count`,
  COALESCE(db.`active_debt_count`, 0) AS `active_debt_count`,
  COALESCE(db.`total_debt_remaining`, 0.00) AS `total_debt_remaining`,
  NOW() AS `snapshot_at`
FROM `users` u
LEFT JOIN (
  SELECT
    `user_id`,
    COALESCE(SUM(`current_balance`), 0.00) AS `total_balance`
  FROM `bank_accounts`
  WHERE `is_active` = TRUE
  GROUP BY `user_id`
) ba
  ON ba.`user_id` = u.`user_id`
LEFT JOIN (
  SELECT
    `user_id`,
    COALESCE(SUM(`amount`), 0.00) AS `current_month_income`
  FROM `incomes`
  WHERE `status` = 'active'
    AND `income_date` >= CAST(DATE_FORMAT(CURDATE(), '%Y-%m-01') AS DATE)
    AND `income_date` < DATE_ADD(CAST(DATE_FORMAT(CURDATE(), '%Y-%m-01') AS DATE), INTERVAL 1 MONTH)
  GROUP BY `user_id`
) mi
  ON mi.`user_id` = u.`user_id`
LEFT JOIN (
  SELECT
    `user_id`,
    COALESCE(SUM(`amount`), 0.00) AS `current_month_expense`
  FROM `expenses`
  WHERE `status` = 'active'
    AND `expense_date` >= CAST(DATE_FORMAT(CURDATE(), '%Y-%m-01') AS DATE)
    AND `expense_date` < DATE_ADD(CAST(DATE_FORMAT(CURDATE(), '%Y-%m-01') AS DATE), INTERVAL 1 MONTH)
  GROUP BY `user_id`
) me
  ON me.`user_id` = u.`user_id`
LEFT JOIN (
  SELECT
    `user_id`,
    COUNT(*) AS `unread_alert_count`
  FROM `alerts`
  WHERE `is_read` = FALSE
  GROUP BY `user_id`
) al
  ON al.`user_id` = u.`user_id`
LEFT JOIN (
  SELECT
    `user_id`,
    COUNT(*) AS `active_debt_count`,
    COALESCE(SUM(`remaining_amount`), 0.00) AS `total_debt_remaining`
  FROM `debts`
  WHERE `is_active` = TRUE
    AND `status` IN ('pending', 'partially_paid', 'overdue')
  GROUP BY `user_id`
) db
  ON db.`user_id` = u.`user_id`
WHERE u.`is_active` = TRUE;

CREATE OR REPLACE VIEW `vw_monthly_financial_summary` AS
SELECT
  tx.`user_id`,
  tx.`period_year`,
  tx.`period_month`,
  COALESCE(SUM(tx.`total_income`), 0.00) AS `total_income`,
  COALESCE(SUM(tx.`total_expense`), 0.00) AS `total_expense`,
  ROUND(
    COALESCE(SUM(tx.`total_income`), 0.00) - COALESCE(SUM(tx.`total_expense`), 0.00),
    2
  ) AS `net_amount`
FROM (
  SELECT
    i.`user_id`,
    YEAR(i.`income_date`) AS `period_year`,
    MONTH(i.`income_date`) AS `period_month`,
    COALESCE(SUM(i.`amount`), 0.00) AS `total_income`,
    0.00 AS `total_expense`
  FROM `incomes` i
  WHERE i.`status` = 'active'
  GROUP BY
    i.`user_id`,
    YEAR(i.`income_date`),
    MONTH(i.`income_date`)

  UNION ALL

  SELECT
    e.`user_id`,
    YEAR(e.`expense_date`) AS `period_year`,
    MONTH(e.`expense_date`) AS `period_month`,
    0.00 AS `total_income`,
    COALESCE(SUM(e.`amount`), 0.00) AS `total_expense`
  FROM `expenses` e
  WHERE e.`status` = 'active'
  GROUP BY
    e.`user_id`,
    YEAR(e.`expense_date`),
    MONTH(e.`expense_date`)
) tx
GROUP BY
  tx.`user_id`,
  tx.`period_year`,
  tx.`period_month`;

CREATE OR REPLACE VIEW `vw_category_cashflow_summary` AS
SELECT
  tx.`user_id`,
  tx.`period_year`,
  tx.`period_month`,
  tx.`category_id`,
  c.`category_name`,
  c.`category_type`,
  COALESCE(SUM(tx.`income_count`), 0) AS `income_count`,
  COALESCE(SUM(tx.`expense_count`), 0) AS `expense_count`,
  COALESCE(SUM(tx.`total_income`), 0.00) AS `total_income`,
  COALESCE(SUM(tx.`total_expense`), 0.00) AS `total_expense`,
  ROUND(
    COALESCE(SUM(tx.`total_income`), 0.00) - COALESCE(SUM(tx.`total_expense`), 0.00),
    2
  ) AS `net_amount`
FROM (
  SELECT
    i.`user_id`,
    YEAR(i.`income_date`) AS `period_year`,
    MONTH(i.`income_date`) AS `period_month`,
    i.`category_id`,
    COUNT(*) AS `income_count`,
    0 AS `expense_count`,
    COALESCE(SUM(i.`amount`), 0.00) AS `total_income`,
    0.00 AS `total_expense`
  FROM `incomes` i
  WHERE i.`status` = 'active'
  GROUP BY
    i.`user_id`,
    YEAR(i.`income_date`),
    MONTH(i.`income_date`),
    i.`category_id`

  UNION ALL

  SELECT
    e.`user_id`,
    YEAR(e.`expense_date`) AS `period_year`,
    MONTH(e.`expense_date`) AS `period_month`,
    e.`category_id`,
    0 AS `income_count`,
    COUNT(*) AS `expense_count`,
    0.00 AS `total_income`,
    COALESCE(SUM(e.`amount`), 0.00) AS `total_expense`
  FROM `expenses` e
  WHERE e.`status` = 'active'
  GROUP BY
    e.`user_id`,
    YEAR(e.`expense_date`),
    MONTH(e.`expense_date`),
    e.`category_id`
) tx
INNER JOIN `categories` c
  ON c.`category_id` = tx.`category_id`
GROUP BY
  tx.`user_id`,
  tx.`period_year`,
  tx.`period_month`,
  tx.`category_id`,
  c.`category_name`,
  c.`category_type`;

CREATE OR REPLACE VIEW `vw_debt_summary` AS
SELECT
  d.`user_id`,
  d.`debt_type`,
  d.`status`,
  COUNT(*) AS `debt_count`,
  COALESCE(SUM(d.`original_amount`), 0.00) AS `total_original_amount`,
  COALESCE(SUM(d.`remaining_amount`), 0.00) AS `total_remaining_amount`,
  MIN(d.`due_date`) AS `nearest_due_date`,
  SUM(
    CASE
      WHEN d.`status` <> 'paid'
        AND d.`due_date` IS NOT NULL
        AND d.`due_date` < CURDATE()
      THEN 1
      ELSE 0
    END
  ) AS `overdue_count`
FROM `debts` d
WHERE d.`is_active` = TRUE
GROUP BY
  d.`user_id`,
  d.`debt_type`,
  d.`status`;
