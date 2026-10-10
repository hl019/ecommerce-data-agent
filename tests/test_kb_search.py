# -*- coding: utf-8 -*-
"""
kb_search 独立测试：直接调工具类，不经过 Agent。

跑法：
    $env:ZHIPU_API_KEY = "sk-..."
    D:\\projects\\OpenManus\\.venv\\Scripts\\python.exe D:\\projects\\ecommerce-data-agent\\tests\\test_kb_search.py

用途：① 验证检索能通；② 打印每个块的相关度分数——这是调置信阈值的唯一依据。
（跑完可删，或保留作回归测试）
"""
import asyncio
import os
import re
import sys

import chromadb
import requests

# 让 import app.tool.kb_search 找得到（用 OpenManus 运行副本）
sys.path.insert(0, r"D:\projects\OpenManus")
os.chdir(r"D:\projects\OpenManus")

from app.tool.kb_search import KBSearch, KB_DIR, COLLECTION, EMBED_MODEL

ZHIPU_KEY = os.environ.get("ZHIPU_API_KEY", "")

QUERIES = [
    "库存商品不可销售怎么处理",      # 期望命中 库存状态.txt
    "采购订单到应付单的流程",        # 期望命中 采购管理.txt
    "销售出库单为什么选不到库存",    # 期望命中 销售管理.txt / 库存状态.txt
    "咖啡豆怎么保存",                # ⭐ 干扰项：期望"无相关内容"（分数低于阈值）
]


def embed(text):
    r = requests.post(
        "https://open.bigmodel.cn/api/paas/v4/embeddings",
        headers={"Authorization": f"Bearer {ZHIPU_KEY}"},
        json={"model": EMBED_MODEL, "input": text, "dimensions": 256},
        timeout=30,
    )
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    return r.json()["data"][0]["embedding"]


def raw_probe(query, k=5):
    """不走工具类，直接查库，打印原始距离/分数——看阈值该怎么划"""
    col = chromadb.PersistentClient(path=KB_DIR).get_collection(COLLECTION)
    hit = col.query(query_embeddings=[embed(query)], n_results=k)
    print(f"  [原始分数] top-{k}：")
    for doc, meta, dist in zip(hit["documents"][0], hit["metadatas"][0], hit["distances"][0]):
        score = 1.0 / (1.0 + dist)
        print(f"    score={score:.3f} dist={dist:6.3f} | {meta['title'][:16]:16s} | {meta['source'][:18]:18s} | {doc[:34]}")


async def main():
    if not ZHIPU_KEY:
        print("✗ 环境变量 ZHIPU_API_KEY 未设")
        return

    tool = KBSearch()
    for q in QUERIES:
        print("=" * 78)
        print(f"【问题】{q}")
        raw_probe(q, k=5)                       # 先看原始分数（调阈值用）
        result = await tool.execute(query=q)    # 再看工具实际返回
        out = result.output if hasattr(result, "output") else str(result)
        print("  [工具返回]")
        for line in out.splitlines()[:12]:
            print(f"    {line}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
