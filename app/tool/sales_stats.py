# -*- coding: utf-8 -*-
"""
工具 2：sales_stats —— pandas 统计分析工具（枚举参数，模型几乎不会传错）

━━━ 学生亲手写的部分（考核官红线，ZCode 不代填）━━━
1. description：说清 5 种分析类型各回答什么业务问题（模型靠这个选类型）
2. parameters：analysis_type 用 enum 枚举（monthly/category/user/top_products/repurchase）
   ——设计要点：枚举参数 > 自由文本参数（呼应考核题 6）
3. execute()：把你 hl019-ecommerce-viaapi/extracted_code.py 74-181 行的
   groupby/agg/merge 逻辑拆成 5 个独立分析函数，按 analysis_type 分发
   数据源：CSV（DATA_DIR 三张表），不依赖 MySQL
   错误处理清单见设计草案工具 2 表格（非法枚举值回显合法值/CSV缺失/日期解析失败）
"""
from app.tool.base import BaseTool, ToolResult


class SalesStats(BaseTool):
    """pandas 统计工具（W2 工具 2）"""

    name: str = "sales_stats"

    # TODO(学生): 写 description——把 5 种 analysis_type 各自的用途说清楚
    description: str = ""

    # TODO(学生): 写 parameters JSON Schema
    #   关键：analysis_type 的 schema 用 "enum": [...] 限死合法值
    parameters: dict = {}

    # CSV 数据目录（复用你已有的电商仓库数据）
    DATA_DIR: str = r"D:\projects\hl019-ecommerce-viaapi\data"

    async def execute(self, analysis_type: str, top_n: int = 10) -> ToolResult:
        """
        TODO(学生): 亲手实现。建议结构：

        if analysis_type == "monthly":    → 月度销售额（extracted_code.py 你写过）
        elif analysis_type == "category": → 品类分布
        elif analysis_type == "user":     → 用户分析（头部用户贡献）
        elif analysis_type == "top_products": → Top N 商品
        elif analysis_type == "repurchase":   → 复购率
        else: → fail_response，并把合法值列表回显给模型（它能自我纠正）

        输出：JSON 字符串（列名用中文，模型可直接引用），success_response 返回
        """
        raise NotImplementedError("sales_stats 还没实现——这是你 W2 D3-D4 的任务，5 个分析函数拆自你自己的 notebook")
