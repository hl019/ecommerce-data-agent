# -*- coding: utf-8 -*-
"""
W2 数据库一键初始化：建库 + 建表 + 导入 CSV + 验证，一条命令全搞定。

用法（OpenManus 虚拟环境里）：
    python D:\\projects\\ecommerce-data-agent\\scripts\\w2_setup\\one_click_init.py

或直接双击同目录下的「一键初始化数据库.bat」。

密码来源（按优先级）：
    1. 环境变量 MYSQL_PASSWORD
    2. 运行时交互式输入（getpass，不回显、不落盘、不进 git）

前置：MySQL 服务已启动。依赖已随 W2 准备装好（pandas/sqlalchemy/pymysql）。
"""
import getpass
import os
import re
import sys
import warnings
from pathlib import Path

import pandas as pd
import pymysql
from sqlalchemy import create_engine

HERE = Path(__file__).parent
DDL_FILE = HERE / "01_create_database.sql"
DATA_DIR = Path(r"D:\projects\hl019-ecommerce-viaapi\data")
DB_NAME = "ecommerce_agent"

CSV_TABLES = [("Customers.csv", "Customers"), ("Products.csv", "Products"), ("Transactions.csv", "Transactions")]


def get_password() -> str:
    pwd = os.getenv("MYSQL_PASSWORD")
    if pwd is not None:
        return pwd
    return getpass.getpass("请输入 MySQL root 密码（不回显、不保存）: ")


def run_ddl(password: str):
    """执行 01_create_database.sql：建库建表（单一事实来源，不重复维护 DDL）"""
    sql_text = DDL_FILE.read_text(encoding="utf-8")
    # 去掉 "--" 注释行后按分号切分（本文件无存储过程，简单切分安全）
    lines = [ln for ln in sql_text.splitlines() if not ln.strip().startswith("--")]
    statements = [s.strip() for s in "\n".join(lines).split(";") if s.strip()]

    conn = pymysql.connect(host="localhost", user="root", password=password, charset="utf8mb4")
    try:
        with conn.cursor() as cur:
            for stmt in statements:
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()
    print(f"[1/3] DDL 执行完成：{len(statements)} 条语句（建库+三张表）")


def import_data(password: str):
    """CSV → MySQL（幂等：先清空再导，重复运行不会翻倍）"""
    engine = create_engine(
        f"mysql+pymysql://root:{password}@localhost:3306/{DB_NAME}?charset=utf8mb4"
    )
    specs = [
        ("Customers.csv", "Customers", ["SignupDate"]),
        ("Products.csv", "Products", []),
        ("Transactions.csv", "Transactions", ["TransactionDate"]),
    ]
    # 清空必须子表先于父表（外键约束），导入必须父表先于子表——顺序反了必报 1451
    with engine.begin() as conn:
        for table in ["Transactions", "Customers", "Products"]:
            conn.exec_driver_sql(f"DELETE FROM {table}")
    for filename, table, date_cols in specs:
        df = pd.read_csv(DATA_DIR / filename)
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        with engine.begin() as conn:
            with warnings.catch_warnings():
                # pandas 假警告：Windows 上 MySQL lower_case_table_names=1，表名实际小写存储，
                # pandas 写完后按原大小写回查不到就告警——数据无损，屏蔽以免误导
                warnings.filterwarnings("ignore", message="The provided table name", category=UserWarning)
                df.to_sql(table, conn, if_exists="append", index=False)
        print(f"[2/3] {filename} → {table}：导入 {len(df)} 行")


def verify(password: str) -> bool:
    """验证行数 + 跑一条真实分析 SQL（月度销售额 Top3）"""
    engine = create_engine(
        f"mysql+pymysql://root:{password}@localhost:3306/{DB_NAME}?charset=utf8mb4"
    )
    ok = True
    with engine.connect() as conn:
        for filename, table in CSV_TABLES:
            expected = len(pd.read_csv(DATA_DIR / filename))  # 期望值以 CSV 实际行数为准，不硬编码
            cnt = conn.exec_driver_sql(f"SELECT COUNT(*) FROM {table}").scalar()
            mark = "OK" if cnt == expected else f"!! 期望 {expected}"
            if cnt != expected:
                ok = False
            print(f"[3/3] {table}: {cnt} 行  [{mark}]")
        print("\n--- 验证查询：月度销售额 Top3（W2 工具 1 将让 Agent 自己跑这类 SQL）---")
        # pymysql 是 pyformat 参数风格：SQL 里字面的 % 必须写成 %%，否则被当占位符
        rows = conn.exec_driver_sql(
            "SELECT DATE_FORMAT(TransactionDate, '%%Y-%%m') AS month, "
            "ROUND(SUM(TotalValue), 2) AS sales "
            "FROM Transactions GROUP BY month ORDER BY sales DESC LIMIT 3"
        ).fetchall()
        for month, sales in rows:
            print(f"  {month}  {sales}")
    return ok


def main():
    print("=" * 50)
    print("W2 数据库一键初始化")
    print("=" * 50)
    if not DATA_DIR.exists():
        sys.exit(f"数据目录不存在：{DATA_DIR}")
    password = get_password()
    try:
        run_ddl(password)
        import_data(password)
        ok = verify(password)
    except pymysql.err.OperationalError as e:
        sys.exit(f"\nMySQL 连接失败：{e}\n请确认：① MySQL 服务已启动 ② 密码正确 ③ 端口 3306")
    print("\n" + ("✓ 初始化完成，W2 可以开工了" if ok else "!! 行数不符，检查上方输出"))
    print("验证方式二：Navicat 打开 ecommerce_agent 库，双击三张表看数据；或执行 03_verify.sql")


if __name__ == "__main__":
    main()
