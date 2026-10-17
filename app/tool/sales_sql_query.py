# -*- coding: utf-8 -*-
"""

"""
import os
import re

import pymysql
from app.tool.base import BaseTool, ToolResult

class SalesSQLQuery(BaseTool):
    """只读 SQL 查询工具（W2 工具 1）"""

    name: str = "sales_sql_query"

    #description ─────────────────────────────
    description: str =  ("对电商销售数据库执行只读的 SQL 查询（SELECT），返回 markdown 格式的表格结果。"
        "当你需要查询具体的销售数据、客户信息或交易明细时调用本工具，例如某月的销售额、"
        "客户数量、订单明细等。注意：本工具只支持 SELECT 只读查询，不能修改任何数据；"
        "当需要把查询结果画成图表时，请改用 plot_chart 工具。")

    #parameters（JSON Schema，四步填）──────────
    parameters: dict =  {
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "要执行的 SELECT 只读查询语句。只允许 SELECT，禁止 INSERT/UPDATE/DELETE/DROP 等写操作。",
            },
            "row_limit": {
                "type": "integer",
                "description": "最多返回的行数，默认 50，用于控制返回长度、避免超出上下文窗口。",
            },
        },
        "required": ["sql"],
    }

    async def execute(self, sql: str, row_limit: int = 50) -> ToolResult:
        """
        #只读守卫 ──
        判断 sql 是不是 SELECT 开头（提示：strip + upper/lower + startswith）。
        不是 → return self.fail_response(一句可读的拒绝理由)。

        #建立连接 ──
        pymysql.connect(host=?, user=?, password=?, database="ecommerce_agent", charset="utf8mb4")

        #执行并限量取数 ──
        cursor.execute(sql)；然后取 row_limit 行（提示：fetch 家族里哪个带限量参数？）。

        #拼 markdown 表格 ──
        列名从 cursor.description 拿；表头一行 + 分隔一行 + 数据每行一行。

        #收尾 ──
        成功 → self.success_response(表格字符串)；
        任何异常 → except 里 self.fail_response(可读错误)；finally 里关连接。
        """

        #只读守卫（加强版）——剥注释 / 白名单开头 / 禁分号 / 防 CTE 绕过 / 防写文件
        clean_sql = re.sub(r"^\s*(--[^\n]*\n|/\*.*?\*/)+", "", sql, flags=re.S).strip()
        upper_sql = clean_sql.upper()

        if not upper_sql.startswith(("SELECT", "WITH", "(")):
            return self.fail_response(f"只允许 SELECT 只读查询，拒绝执行：{sql}")
        # H1 修复（Z13）：分号检查先剥掉字符串字面量内的内容——
        # 否则 SELECT ... WHERE CustomerName LIKE 'a;b' 里合法的分号会被误判为多语句
        # （这是"宁误杀勿放过"的反面：守卫要严，但不能伤到合法查询）
        sql_no_literals = re.sub(r"'(?:[^']|'')*'|\"(?:[^\"]|\"\")*\"", "", clean_sql)
        if ";" in sql_no_literals:
            return self.fail_response("只允许单条查询语句，不接受分号分隔的多语句。")
        if upper_sql.startswith("WITH") and re.search(r"(^|\))\s*(UPDATE|DELETE)\b", upper_sql):
            return self.fail_response(f"CTE 后只允许接 SELECT，检测到写操作，拒绝执行：{sql}")
        if re.search(r"\bINTO\s+(OUTFILE|DUMPFILE)\b", upper_sql):
            return self.fail_response(f"禁止 SELECT ... INTO OUTFILE，拒绝执行：{sql}")

        #建立连接（conn 先设为 None，finally 里要用）
        conn = None
        try:
            conn = pymysql.connect(
                host="127.0.0.1",
                user=os.environ.get("MYSQL_RO_USER", "ecom_ro"),
                password=os.environ.get("MYSQL_RO_PASSWORD", ""),
                database="ecommerce_agent",
                charset="utf8mb4",
                connect_timeout=5,   # H3 修复（Z13）：MySQL 挂起时避免 Agent 干等 TCP 超时
            )

            #执行并限量取数
            with conn.cursor() as cursor:
                cursor.execute(clean_sql)
                rows = cursor.fetchmany(row_limit)
                columns = [d[0] for d in cursor.description] if cursor.description else []

            #拼 markdown 表格
            if not columns:
                return self.success_response("查询完成，但没有返回列（可能不是 SELECT）")
            header = "| " + " | ".join(columns) + " |"
            sep = "|" + "---|" * len(columns)
            lines = [header, sep]
            for r in rows:
                cells = [str(v) if v is not None else "" for v in r]
                lines.append("| " + " | ".join(cells) + " |")
            table = "\n".join(lines)
            # 截断提示：取满 row_limit 行 → 可能还有更多数据没取
            if len(rows) == row_limit:
                table += f"\n\n> 注意：结果已按 row_limit={row_limit} 截断，可能还有更多数据未显示。"

            #成功收尾
            return self.success_response(table)
        except Exception as e:
            return self.fail_response(f"查询失败：{e}")
        finally:
            if conn:
                conn.close()
