# -*- coding: utf-8 -*-
r"""
RAG 检索评测 —— 15 道正样本，统计 top-3 命中率。

用法（同一终端先设 ZHIPU_API_KEY）：
    $env:ZHIPU_API_KEY = "你的key"
    D:\projects\OpenManus\.venv\Scripts\python.exe D:\projects\ecommerce-data-agent\tests\eval_rag.py

口径说明：
  - 本脚本只测【检索层】：期望文档是否出现在 top-3（任一命中即算对）。
  - 判定依据 = 检索条目的完整元信息行（含 `source` 文档名，如 `重复购买率.txt`）。
    注意 metadata 里 `title` 是**块标题**（章节名），`source` 才是文档名。
  - "该不该拒答"属【生成层】判断（工具本身不拒答，交给 LLM 结合提示词），
    需端到端另测：见文末 TODO（负样本 5 题走 Agent）。
"""
import asyncio
import os
import re
import sys

sys.path.insert(0, r"D:\projects\OpenManus")
os.chdir(r"D:\projects\OpenManus")

# (问题, 期望命中的文档标题——任一命中即算对)
CASES = [
    # ── 库存状态 ──
    ("库存商品不可销售怎么设置", ["库存状态"]),
    ("库存商品有哪些状态（可用/待检/冻结/不良）", ["库存状态"]),
    # ── 应付款管理 ──
    ("应付款有哪几个业务环节", ["应付款管理"]),
    ("暂估应付和业务应付有什么区别", ["应付款管理"]),
    ("应付单、付款单、发票之间怎么核销", ["应付款管理"]),
    # ── 采购管理 ──
    ("采购订单到入库到应付的流程是什么", ["采购管理"]),
    ("采购入库单审核后会自动生成应付单吗", ["采购管理", "应付款管理"]),
    # ── 销售管理 ──
    ("销售订单到发货到销售出库的流程", ["销售管理"]),
    ("销售出库时选不到库存是什么原因", ["销售管理", "库存状态"]),
    # ── 总账 / 凭证 ──
    ("业务单据怎么生成凭证", ["总账或凭证"]),
    ("立账模式怎么影响应付账款的凭证", ["总账或凭证", "应付款管理"]),
    # ── 运营指标口径 ──
    ("复购率怎么算", ["重复购买率"]),
    ("重复购买率有哪几种口径", ["重复购买率"]),
    ("网站转化率怎么计算", ["网站转化率"]),
    ("客单价怎么算", ["客单价"]),
]

# 每条检索结果的完整元信息行：`[1] 【相关度 0.842 | 出处: 块标题 | 源文件.txt | url】`
# 判定时必须看整行——因为文档名在 `source`（源文件）里，`title` 只是块标题。
ENTRY_RE = re.compile(r"\[\d+\]\s*【([^】]+)】")

# ── 口语化难题组（故意不用文档原词，模拟真实用户的问法）──
# 用途：检验"基础题 100%"是否只是同分布偏置。
HARD_CASES = [
    ("我的商品在销售出库单里选不到，是什么原因", ["库存状态", "销售管理"]),
    ("客户要退货但钱还没付，账上该怎么处理", ["应付款管理", "销售管理"]),
    ("我怎么知道老客户还会不会再来买", ["重复购买率"]),
    ("单据做完以后财务那边怎么入账", ["总账或凭证"]),
    ("订单下了但货还没到，钱是怎么走的", ["采购管理", "应付款管理"]),
]


async def main():
    from app.tool.kb_search import KBSearch

    tool = KBSearch()
    ok = 0
    rows = []
    for i, (q, expects) in enumerate(CASES, 1):
        r = await tool.execute(query=q, top_k=3)
        out = r.output or r.error or ""
        entries = ENTRY_RE.findall(out)
        hit = any(any(e in entry for e in expects) for entry in entries)
        ok += hit
        rows.append((i, hit, q, expects, entries))

    print("=" * 96)
    print("RAG 检索评测（top-3 命中）")
    print("=" * 96)
    for i, hit, q, expects, entries in rows:
        mark = "✅" if hit else "❌"
        print(f"{mark} [{i:>2}] {q}")
        print(f"        期望: {expects}")
        print(f"        实际: {entries}")
    total = len(CASES)
    print("-" * 96)
    print(f"📊 基础题 top-3 命中率：{ok}/{total} = {ok / total * 100:.1f}%")
    print("-" * 96)

    # ── 口语化难题组（不用文档原词，模拟真实用户问法）──
    print("\n【口语化难题组】模拟真实用户问法（刻意不用文档原词）")
    print("-" * 96)
    hard_ok = 0
    for i, (q, expects) in enumerate(HARD_CASES, 1):
        r = await tool.execute(query=q, top_k=3)
        out = r.output or r.error or ""
        entries = ENTRY_RE.findall(out)
        hit = any(any(e in entry for e in expects) for entry in entries)
        hard_ok += hit
        print(f"{'✅' if hit else '❌'} [H{i}] {q}")
        print(f"        期望: {expects}")
        print(f"        实际: {entries}")
    print("-" * 96)
    print(f"📊 口语化题 top-3 命中率：{hard_ok}/{len(HARD_CASES)} = {hard_ok / len(HARD_CASES) * 100:.1f}%")
    print("-" * 96)
    print("说明：基础题验证覆盖度；口语化题检验真实场景。两组分开报、不合并。")

    # ── TODO（端到端，需消耗 token）──
    # 负样本建议 5 题：咖啡豆怎么保存 / 员工年假怎么申请 / 服务器怎么扩容 /
    #                竞品分析怎么做 / 公司给员工发奖金怎么算
    # 跑 Agent，判定标准：回答中出现"知识库中无相关内容"或不编造具体数字/流程。


asyncio.run(main())
