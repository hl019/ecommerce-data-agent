# -*- coding: utf-8 -*-
"""
工具 1：sales_sql_query —— 对电商数据库执行只读 SQL 查询

━━━ 学生亲手写的部分（考核官红线，ZCode 不代填）━━━
1. description：用你自己的话写清楚"这个工具能干什么、什么时候该用"
   （模型靠这句话决定要不要调它——这就是提示词工程）
2. parameters：按《ZCode-03-W2工具设计草案》工具 1 的参数表，亲手写 JSON Schema
   （lab 01 实验 2 里你见过这个格式）
3. execute()：核心逻辑四步——
   ① 只读守卫：不是 SELECT 开头的语句直接 fail_response（面试考点：为什么只读？）
   ② pymysql 连接 ecommerce_agent 库（密码从环境变量或本地配置读，别硬编码）
   ③ 执行查询，row_limit 截断
   ④ 结果转 markdown 表格字符串，success_response 返回
   错误处理清单见设计草案工具 1 表格（连接失败/空结果/行数截断都要给可读信息）
"""
from app.tool.base import BaseTool, ToolResult


class SalesSQLQuery(BaseTool):
    """只读 SQL 查询工具（W2 工具 1）"""

    name: str = "sales_sql_query"

    # TODO(学生): 写 description——告诉模型这个工具做什么、返回什么格式
    description: str = ""

    # TODO(学生): 写 parameters JSON Schema
    #   参考设计草案：sql(必填, string) + row_limit(可选, integer, 默认50)
    #   格式参考 lab 01 实验 2 里的 tools 定义，或 app/tool/ask_human.py
    parameters: dict = {}

    async def execute(self, sql: str, row_limit: int = 50) -> ToolResult:
        """
        TODO(学生): 亲手实现。骨架故意留空——这是你简历项目的核心代码。

        提示（只指路，不给实现）：
        - 只读守卫：sql.strip().lower().startswith("select") 不满足 → self.fail_response(...)
        - 连接：pymysql.connect(host=..., user=..., password=..., database="ecommerce_agent", charset="utf8mb4")
        - 查询：cursor.execute(sql)  +  fetchmany(row_limit)
        - 输出：列名 + 每行拼成 markdown 表格（"| 列1 | 列2 |" 格式），self.success_response(表格字符串)
        - 任何异常：self.fail_response(可读错误信息)——错误也会变成 Observation 喂回模型
        """
        raise NotImplementedError("sales_sql_query 还没实现——这是你 W2 D1-D2 要亲手写的第一个工具")
