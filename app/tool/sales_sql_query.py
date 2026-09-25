# -*- coding: utf-8 -*-
"""
工具 1：sales_sql_query —— 对电商数据库执行只读 SQL 查询（填空式骨架）

预习包：《ZCode-W2工具1预习包.md》（review\）——每个空该填什么、引导问题、PASS 标准都在那里。
带写模式：考核官逐行带写，本文件是预习材料；写完跑 sync bat + tests/test_tools.py。

红线（考核官）：description / parameters / execute / 错误处理全部学生亲手写。
本骨架只给：类定义 + 空的填空位 + 引导问题。不许抄预习包里的"答案方向"原文当交付——
带写时你要能对着考核官讲出每一行为什么这么写。
"""
from app.tool.base import BaseTool, ToolResult


class SalesSQLQuery(BaseTool):
    """只读 SQL 查询工具（W2 工具 1）"""

    name: str = "sales_sql_query"

    # ── 填空 A：description ─────────────────────────────
    # 引导问题（答出来再写）：
    #   A1. 这个工具"能做什么"一句话怎么说？（模型靠这句话决定要不要调它）
    #   A2. "什么时候该调它、什么时候不该"要不要写进去？（对比：问题要画图时该调谁？）
    #   A3. 返回格式（markdown 表格）要不要告诉模型？为什么？
    description: str = ""

    # ── 填空 B：parameters（JSON Schema，四步填）──────────
    # 步骤 B1：外层骨架 {"type": "object", "properties": { … }, "required": [ … ]}
    # 步骤 B2：properties 里加 "sql"：type 是什么？description 写什么
    #         （提示：description 是给模型看的说明书，写"要执行的 SELECT 语句"够不够？
    #           想想模型可能传 INSERT 进来，你要不要在说明书里先劝它一句）
    # 步骤 B3：加 "row_limit"：type 是什么？要不要给默认值语义的说明？
    # 步骤 B4：required 数组里放谁？为什么 row_limit 不放？
    # 格式蓝本：lab 01 实验 2 的 tools 定义 / app/tool/ask_human.py
    parameters: dict = {}

    async def execute(self, sql: str, row_limit: int = 50) -> ToolResult:
        """
        ── 填空 1：只读守卫 ──
        判断 sql 是不是 SELECT 开头（提示：strip + upper/lower + startswith）。
        不是 → return self.fail_response(一句可读的拒绝理由)。
        引导问题：为什么必须在代码层守卫，而不是在 description 里"求"模型别传 INSERT？

        ── 填空 2：建立连接 ──
        pymysql.connect(host=?, user=?, password=?, database="ecommerce_agent", charset="utf8mb4")
        引导问题：password 从哪来？（环境变量/本地配置——为什么硬编码进 .py 是事故而不是偷懒？）

        ── 填空 3：执行并限量取数 ──
        cursor.execute(sql)；然后取 row_limit 行（提示：fetch 家族里哪个带限量参数？）。
        引导问题：fetchall 和它在这里的差别，对 Agent 的上下文窗口意味着什么？

        ── 填空 4：拼 markdown 表格 ──
        列名从 cursor.description 拿；表头一行 + 分隔一行 + 数据每行一行。
        引导问题：模型读 markdown 表格和读 JSON，哪个省 token？省在哪？

        ── 填空 5：收尾 ──
        成功 → self.success_response(表格字符串)；
        任何异常 → except 里 self.fail_response(可读错误)；finally 里关连接。
        引导问题：fail_response 的错误信息最终会到哪里去？（回忆 toolcall.py execute_tool 的兜底路径）
        """
        raise NotImplementedError("工具 1 还没写——按填空 1-5 顺序来，写完跑 tests/test_tools.py")
