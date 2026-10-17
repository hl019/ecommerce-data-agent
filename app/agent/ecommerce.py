# -*- coding: utf-8 -*-
"""
电商运营数据分析智能体（EcommerceAgent）

设计要点：
- 继承 ToolCallAgent，复用 ReAct 循环（think/act）、错误兜底与卡死检测
- 工具集合为本项目 6 个自研工具 + Terminate（循环的正常出口）
- max_observe=10000：截断工具观察值，防大表格撑爆上下文
- max_steps=20：循环上限，作为死循环的硬边界（配合框架的卡死检测）
- run() 入口重置 LLM token 计数，使报告页脚的"本轮消耗"语义正确
"""
from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.prompt.ecommerce import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.sales_sql_query import SalesSQLQuery
from app.tool.sales_stats import SalesStats
from app.tool.plot_chart import PlotChart
from app.tool.report_generator import ReportGenerator
from app.tool.kb_search import KBSearch
from app.tool.customer_lookalike import CustomerLookalike

class EcommerceAgent(ToolCallAgent):
    """电商运营数据分析智能体：一句话业务问题 → 查数 → 统计 → 图表 → HTML 报告"""

    name: str = "EcommerceAgent"
    description: str = "电商运营数据分析智能体，能查询数据库、统计分析、绘制图表并生成 HTML 报告"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    # 与 Manus 对齐的观察值截断（防大表格撑爆上下文，面试考点）
    max_observe: int = 10000
    max_steps: int = 20

    # Terminate 是循环的正常出口，必须保留在工具集合中
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            SalesSQLQuery(),
            SalesStats(),
            PlotChart(),
            ReportGenerator(),
            KBSearch(),
            CustomerLookalike(),
            Terminate(),
        )
    )
    async def run(self, request=None):
        """B2 修复（Z13）：每次任务开始时重置 LLM token 计数。
        LLM 是进程级单例、计数从不重置，连问第二个问题时报告页脚会变成累计值。
        重置后 report_generator 读到的就是本轮消耗。"""
        from app.llm import LLM
        llm = LLM()
        llm.total_input_tokens = 0
        llm.total_completion_tokens = 0
        return await super().run(request)
