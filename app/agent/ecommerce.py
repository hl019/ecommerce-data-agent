# -*- coding: utf-8 -*-
"""
电商数据分析 Agent 子类骨架（W2）

结构说明（这部分是脚手架，ZCode 备好；工具实现和提示词是你亲手写的部分）：
- 继承 ToolCallAgent：think/act 循环、错误兜底、卡死检测全部白拿
  （就是你 W1 精读过的 toolcall.py:39-172）
- 与 manus.py 的区别：工具集合换成你的 4 个 + 提示词换成场景化的

TODO(学生) 两步激活：
1. 提示词：把 app/prompt/ecommerce.py 里两个空字符串填好
2. 工具注册：在下面 available_tools 的 ToolCollection(...) 里，
   把你写完的工具逐个加进来（import 记得同步加）：
       from app.tool.sales_sql_query import SalesSQLQuery
       from app.tool.sales_stats import SalesStats
       from app.tool.plot_chart import PlotChart
       from app.tool.report_generator import ReportGenerator
   建议顺序：写一个、加一个、用 tests/test_tools.py 测一个，别攒到最后。
"""
from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.prompt.ecommerce import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection


class EcommerceAgent(ToolCallAgent):
    """电商运营数据分析智能体：一句话业务问题 → 查数 → 统计 → 图表 → HTML 报告"""

    name: str = "EcommerceAgent"
    description: str = "电商运营数据分析智能体，能查询数据库、统计分析、绘制图表并生成 HTML 报告"

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    # 与 Manus 对齐的观察值截断（防大表格撑爆上下文，面试考点）
    max_observe: int = 10000
    max_steps: int = 20

    # TODO(学生): 每写完一个工具就加进来一个（见文件头注释）
    # Terminate 必须保留——它是循环的正常出口（W1 你亲眼看它终止过斐波那契任务）
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            Terminate(),
        )
    )
