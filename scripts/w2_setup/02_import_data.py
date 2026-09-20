# -*- coding: utf-8 -*-
"""
W2 MySQL 数据导入脚本
功能：把 CSV 数据导入 MySQL（ecommerce_agent 库）
前提：
  1. MySQL 已启动，01_create_database.sql 已执行（表已建好）
  2. 已安装依赖：pip install pandas sqlalchemy pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple

运行方式：
  python D:\\projects\\ecommerce-data-agent\\scripts\\w2_setup\\02_import_data.py

数据源：D:\\projects\\hl019-ecommerce-viaapi\\data\\（Customers.csv / Products.csv / Transactions.csv）
"""
import pandas as pd
from sqlalchemy import create_engine
import os

# ============ 配置区（学生按自己情况改）============
MYSQL_USER = "root"           # MySQL 用户名
MYSQL_PASSWORD = ""           # MySQL 密码（空字符串=无密码）
MYSQL_HOST = "localhost"      # MySQL 地址
MYSQL_PORT = 3306             # MySQL 端口

# 数据源路径（复用你已有的电商仓库）
DATA_DIR = r"D:\projects\hl019-ecommerce-viaapi\data"
# ================================================

# 数据库连接字符串
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/ecommerce_agent?charset=utf8mb4"

def import_csv_to_mysql(csv_filename, table_name, date_columns=None):
    """
    读取 CSV 并导入 MySQL 表
    :param csv_filename: CSV 文件名（不含路径）
    :param table_name: MySQL 表名
    :param date_columns: 需要解析为日期的列名列表
    """
    csv_path = os.path.join(DATA_DIR, csv_filename)
    print(f"\n>>> 正在导入 {csv_filename} → {table_name} 表...")

    # 读取 CSV
    df = pd.read_csv(csv_path)
    print(f"  读取到 {len(df)} 行数据")

    # 解析日期列（如果有）
    if date_columns:
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                print(f"  已解析日期列: {col}")

    # 连接 MySQL 并导入
    engine = create_engine(DATABASE_URL)
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"  ✓ 成功导入 {len(df)} 行到 {table_name} 表")

def verify_import():
    """验证导入结果"""
    print("\n" + "="*50)
    print("验证导入结果")
    print("="*50)

    engine = create_engine(DATABASE_URL)
    tables = ['Customers', 'Products', 'Transactions']

    for table in tables:
        result = pd.read_sql(f"SELECT COUNT(*) AS cnt FROM {table}", engine)
        count = result['cnt'][0]
        print(f"  {table}: {count} 行")

    print("\n>>> 如果行数与 CSV 一致（199/100/1000），导入成功！")
    print(">>> 下一步：用 Navicat 打开 ecommerce_agent 库，查看三张表的数据。")

if __name__ == "__main__":
    print("="*50)
    print("W2 MySQL 数据导入脚本")
    print("="*50)

    # 检查依赖
    try:
        import pymysql
    except ImportError:
        print("\n✗ 缺少依赖，请先执行：")
        print("  pip install pandas sqlalchemy pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple")
        exit(1)

    # 导入三张表
    import_csv_to_mysql("Customers.csv", "Customers", date_columns=["SignupDate"])
    import_csv_to_mysql("Products.csv", "Products")
    import_csv_to_mysql("Transactions.csv", "Transactions", date_columns=["TransactionDate"])

    # 验证
    verify_import()

    print("\n" + "="*50)
    print("✓ 全部完成！W2 工具层开发可以开始了。")
    print("="*50)
