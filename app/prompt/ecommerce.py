# -*- coding: utf-8 -*-
"""
场景化提示词骨架（W2 · 学生亲手填）

━━━ 为什么这是简历差异化清单第 3 条 ━━━
同一个模型，提示词决定它是"通用助手"还是"电商运营分析师"。
OpenManus 原版提示词在 app/prompt/manus.py——你可以先读它，学结构，再写你自己的。

SYSTEM_PROMPT 至少要包含（考核官验收点）：
1. 角色定位：你是电商运营数据分析智能体，服务的是运营人员（不是程序员）
2. 工具使用守则：什么问题先查数（sales_sql_query / sales_stats）、
   什么时候画图（plot_chart）、最后必须用 report_generator 出报告
3. 数据口径说明：三张表的结构（Customers/Products/Transactions，字段含义）
   ——模型不知道你的库里有什么，你不说它就瞎猜列名
4. 输出要求：中文回答、金额保留两位小数、报告结论要给运营建议

NEXT_STEP_PROMPT：每轮循环结束时追加的催促语（参考 app/prompt/manus.py 的写法，
一句话即可，告诉模型"继续下一步，任务全部完成后调用 terminate"）。
"""

# TODO(学生): 亲手写系统提示词（写完对照上面 4 个验收点自查）
SYSTEM_PROMPT = ""

# TODO(学生): 亲手写下一步提示词
NEXT_STEP_PROMPT = ""
