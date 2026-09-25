-- W2 MySQL 环境准备：建库 + 建表
-- 执行前提：MySQL 已安装并启动，Navicat 或命令行可连接
-- 执行方式：Navicat 打开此文件 → 执行；或 mysql -u root -p < 01_create_database.sql

-- 1. 建库
CREATE DATABASE IF NOT EXISTS ecommerce_agent
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ecommerce_agent;

-- 2. 建表（三张表，对应 CSV 结构）

-- Customers 表（200 行）
CREATE TABLE IF NOT EXISTS Customers (
  CustomerID VARCHAR(10) PRIMARY KEY COMMENT '客户ID，如 C0001',
  CustomerName VARCHAR(100) NOT NULL COMMENT '客户姓名',
  Region VARCHAR(50) COMMENT '地区，如 Asia/South America/Europe/North America',
  SignupDate DATE COMMENT '注册日期'
) ENGINE=InnoDB COMMENT='客户表';

-- Products 表（100 行）
CREATE TABLE IF NOT EXISTS Products (
  ProductID VARCHAR(10) PRIMARY KEY COMMENT '商品ID，如 P001',
  ProductName VARCHAR(200) NOT NULL COMMENT '商品名称',
  Category VARCHAR(50) COMMENT '品类，如 Books/Electronics/Clothing/Home Decor',
  Price DECIMAL(10, 2) COMMENT '单价'
) ENGINE=InnoDB COMMENT='商品表';

-- Transactions 表（1000 行）
CREATE TABLE IF NOT EXISTS Transactions (
  TransactionID VARCHAR(10) PRIMARY KEY COMMENT '交易ID，如 T00001',
  CustomerID VARCHAR(10) NOT NULL COMMENT '客户ID（外键）',
  ProductID VARCHAR(10) NOT NULL COMMENT '商品ID（外键）',
  TransactionDate DATETIME COMMENT '交易时间',
  Quantity INT COMMENT '数量',
  TotalValue DECIMAL(10, 2) COMMENT '交易总额',
  Price DECIMAL(10, 2) COMMENT '单价（冗余字段，与 Products.Price 一致）',
  FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
  FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
  INDEX idx_transaction_date (TransactionDate),
  INDEX idx_customer (CustomerID)
) ENGINE=InnoDB COMMENT='交易表';

-- 3. 验证
SELECT 'Customers' AS table_name, COUNT(*) AS row_count FROM Customers
UNION ALL
SELECT 'Products', COUNT(*) FROM Products
UNION ALL
SELECT 'Transactions', COUNT(*) FROM Transactions;
