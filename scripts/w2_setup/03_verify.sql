-- W2 数据验证查询（Navicat 里逐段执行，每段都应返回合理结果）

USE ecommerce_agent;

-- 1. 三张表行数（应为 199 / 100 / 1000）
SELECT 'Customers' AS tbl, COUNT(*) AS cnt FROM Customers
UNION ALL SELECT 'Products', COUNT(*) FROM Products
UNION ALL SELECT 'Transactions', COUNT(*) FROM Transactions;

-- 2. 外键完整性（应返回 0 行——没有孤儿交易）
SELECT t.TransactionID FROM Transactions t
LEFT JOIN Customers c ON t.CustomerID = c.CustomerID
WHERE c.CustomerID IS NULL;

-- 3. 月度销售额（sql_analysis.sql 第 1 段的简化版，W2 工具 1 的测试样例）
SELECT DATE_FORMAT(TransactionDate, '%Y-%m') AS month,
       ROUND(SUM(TotalValue), 2) AS sales
FROM Transactions
GROUP BY month
ORDER BY month;

-- 4. Top10 商品（工具 1 第二个测试样例）
SELECT p.ProductName, SUM(t.Quantity) AS qty, ROUND(SUM(t.TotalValue), 2) AS sales
FROM Transactions t
JOIN Products p ON t.ProductID = p.ProductID
GROUP BY p.ProductName
ORDER BY sales DESC
LIMIT 10;
