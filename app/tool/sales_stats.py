# -*- coding: utf-8 -*-
"""
工具 2：sales_stats —— pandas 统计分析工具（填空式骨架）

预习包：《ZCode-W2工具2预习包.md》（review\）——填空指引、引导问题、PASS 标准都在那里。
你的蓝本：extracted_code.py 74-181 行（你自己写过的 groupby/agg/merge 逻辑）。
红线：description / parameters / execute / 错误处理全部学生亲手写。
"""
import json

import pandas as pd

from app.tool.base import BaseTool, ToolResult

VALID_TYPES = ["monthly", "category", "user", "top_products", "repurchase"]


class SalesStats(BaseTool):
    """pandas 统计工具（W2 工具 2）"""

    name: str = "sales_stats"

    # ── 填空 A：description ─────────────────────────────
    # 引导问题：模型靠哪句话决定传 monthly 还是 repurchase？
    # 五种类型各回答什么业务问题，用一句话各写清楚。
    description: str = ""

    # ── 填空 B：parameters ──────────────────────────────
    # B1：analysis_type 用 enum 限死（关键字 "enum"，值就是 VALID_TYPES）
    # B2：top_n 的 type 与默认值语义说明（为什么不进 required？）
    # B3：required 只放 analysis_type
    parameters: dict = {}

    # CSV 数据目录（复用你已有的电商仓库数据；不依赖 MySQL）
    DATA_DIR: str = r"D:\projects\hl019-ecommerce-viaapi\data"

    async def execute(self, analysis_type: str, top_n: int = 10) -> ToolResult:
        """
        ── 填空 1：读 CSV + 解析日期 ──
        三张表从 DATA_DIR 读；日期列 pd.to_datetime(errors="coerce")。
        引导问题：文件缺失/日期全解析失败时，fail_response 写什么模型才看得懂？

        ── 填空 2：五个分析函数 ──
        monthly / category / user / top_products / repurchase 各一个独立函数，
        逻辑拆自 extracted_code.py 74-181（你写过的，别重写轮子）。
        引导问题：一个 200 行大函数 vs 五个小函数，测试和复用上差在哪？

        ── 填空 3：分发 + 非法枚举兜底 ──
        认识的值路由到对应函数；不认识的 → return self.fail_response(...)，
        错误信息里必须回显 VALID_TYPES（模型靠它自我纠正）。
        引导问题：这和工具 1 的只读守卫是同一个思想吗？（代码层兜底+给模型可行动的反馈）

        ── 填空 4：输出 JSON ──
        结果转 list[dict]，json.dumps(..., ensure_ascii=False)，列名中文。
        引导问题：ensure_ascii 不关，中文列名会变成什么？模型还读得懂吗？
        """
        raise NotImplementedError("工具 2 还没写——按填空 1-4 顺序来，写完跑 tests/test_tools.py")
