# -*- coding: utf-8 -*-
"""
MVP 端到端运行脚手架（ZCode 提供，不含学生核心代码）

用法（工具 4 + 工具注册 + 提示词三件事完成后）：
    D:\\projects\\OpenManus\\.venv\\Scripts\\python.exe D:\\projects\\ecommerce-data-agent\\scripts\\run_agent.py "分析月度销售趋势并生成报告"

前置检查会替你把关：提示词没填、工具没注册，脚本会直接指出缺哪一步，不会白跑。
"""
import asyncio
import os
import sys

sys.path.insert(0, r"D:\projects\OpenManus")
os.chdir(r"D:\projects\OpenManus")  # workspace/reports 等相对路径落在这里


def precheck():
    problems = []
    from app.prompt.ecommerce import SYSTEM_PROMPT
    if not SYSTEM_PROMPT.strip():
        problems.append(
            "SYSTEM_PROMPT 还是空的 → 先填 D:\\projects\\ecommerce-data-agent\\app\\prompt\\ecommerce.py 并跑 sync bat")
    from app.agent.ecommerce import EcommerceAgent
    tool_names = {t.name for t in EcommerceAgent().available_tools.tools}
    expected = {"sales_sql_query", "sales_stats", "plot_chart", "report_generator"}
    missing = expected - tool_names
    if missing:
        problems.append(
            f"这些工具还没注册进 EcommerceAgent：{sorted(missing)} → 改 app\\agent\\ecommerce.py 的 available_tools 并跑 sync bat")
    if not os.environ.get("MYSQL_PASSWORD"):
        problems.append("环境变量 MYSQL_PASSWORD 未设 → 当前终端先 $env:MYSQL_PASSWORD = \"你的密码\"")
    return problems


async def main():
    problems = precheck()
    if problems:
        print("还差几步，先别跑：\n")
        for p in problems:
            print(" ✗", p)
        sys.exit(1)
    from app.agent.ecommerce import EcommerceAgent
    question = " ".join(sys.argv[1:]) or "分析月度销售趋势并生成报告"
    print(f"\n>>> 提问：{question}\n{'='*60}")
    agent = EcommerceAgent()
    try:
        result = await agent.run(question)
        print(f"\n{'='*60}\n===== 最终答案 =====\n{result}")
    finally:
        print("\n（报告/图表产物在 D:\\projects\\OpenManus\\workspace\\ 下，token 数看报告页脚）")


if __name__ == "__main__":
    asyncio.run(main())
