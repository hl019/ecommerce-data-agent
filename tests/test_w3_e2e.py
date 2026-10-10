# -*- coding: utf-8 -*-
"""
W3 闭环实测：EcommerceAgent + kb_search 端到端问答。

跑法：
    $env:ZHIPU_API_KEY = "sk-..."
    D:\\projects\\OpenManus\\.venv\\Scripts\\python.exe D:\\projects\\ecommerce-data-agent\\tests\\test_w3_e2e.py

测两个用例：
  ① 口径类问题（该查知识库并给出处）
  ② 无关问题（该如实说"知识库无相关内容"，不强行作答）
"""
import asyncio
import os
import sys

sys.path.insert(0, r"D:\projects\OpenManus")
os.chdir(r"D:\projects\OpenManus")

from app.agent.ecommerce import EcommerceAgent


async def ask(agent, question):
    print("=" * 78)
    print(f"【提问】{question}")
    print("=" * 78)
    try:
        result = await agent.run(question)
        text = result if isinstance(result, str) else str(result)
        print(f"\n【最终回答】\n{text}\n")
    except Exception as e:
        print(f"\n✗ 运行出错：{type(e).__name__}: {e}\n")


async def main():
    if not os.environ.get("ZHIPU_API_KEY"):
        print("✗ 环境变量 ZHIPU_API_KEY 未设")
        return

    agent = EcommerceAgent()

    # 用例①：口径类问题 → 应走 kb_search，命中金蝶文档，带出处回答
    await ask(agent, "库存商品不可销售是怎么设置的？")

    # 用例②：无关问题 → 应如实说"知识库无相关内容"
    agent2 = EcommerceAgent()
    await ask(agent2, "咖啡豆应该怎么保存？")


if __name__ == "__main__":
    asyncio.run(main())
