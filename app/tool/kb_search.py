# -*- coding: utf-8 -*-
"""
检索工具 kb_search —— 电商知识库语义检索（W3 主工具）

★ 改这个（仓库正身）：
    D:\\projects\\ecommerce-data-agent\\app\\tool\\kb_search.py
★ 不用改（OpenManus 运行副本，跑 sync_to_openmanus.bat 自动同步）：
    D:\\projects\\OpenManus\\app\\tool\\kb_search.py
"""
import os
import re
import requests
import chromadb

from app.tool.base import BaseTool, ToolResult

KB_DIR = r"D:\projects\knowledge\ecom_kb"     # 知识库存放处（ingest_corpus 写、本工具读）
COLLECTION = "ecom_kb"
EMBED_MODEL = "embedding-3"                   # 必须与 ingest 时一致（向量与模型绑定！）
ZHIPU_KEY = os.environ.get("ZHIPU_API_KEY", "")

# ★ 置信阈值（1010 实测后调整）：
#   实测发现——向量检索的绝对分数**天然挤在 0.77-0.89 窄带里**（同维归一化 + 中文短文本特征稀疏），
#   连"完全无关"的咖啡文都能拿 0.79。所以【硬阈值 0.35 毫无作用】。
#   结论：向量检索是"排序器"不是"打分器"——**绝对分数不可靠，排序才可靠**。
#   对策（工业界主流）：改为 **低阈值兜底 + 把分数亮给模型 + 提示词要求"不相关就说不确定"**。
MIN_SCORE = 0.0        # 不硬卡（保留字段便于以后按需启用）；相关性判断下放给 LLM


class KBSearch(BaseTool):
    """电商知识库检索工具（W3）"""

    name: str = "kb_search"

    description: str = (
        "在电商/ERP 知识库中检索操作口径、业务规则、指标定义类问题的资料片段，"
        "返回带出处（文档标题+来源URL）和相关度的原文段落。"
        "适用于：业务规则/操作步骤/口径定义类问题（如『库存不可销售怎么设置』『复购率怎么算』）。"
        "不适用于：需要用数据算出的数字类问题（如『上个月销售额多少』）——那类请用 SQL/统计工具。"
        "注意：本工具返回的是资料片段和出处，不是最终答案；相关度分数仅供排序参考（绝对值不可靠）。"
        "若返回的资料与问题无关，必须如实说明『知识库中无相关内容』，不要强行作答。"
    )

    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "检索问题，用自然语言描述，如『库存商品不可销售怎么处理』",
            },
            "top_k": {
                "type": "integer",
                "description": "最多返回几个资料片段，默认 3。不建议调大：片段越多 token 消耗越大、越可能混入不相关噪音。",
            },
        },
        "required": ["query"],
    }

    def _embed(self, text: str):
        """把一段文本向量化（必须与 ingest 用同一个模型 embedding-3）"""
        if not ZHIPU_KEY:
            raise RuntimeError("环境变量 ZHIPU_API_KEY 未设")
        r = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/embeddings",
            headers={"Authorization": f"Bearer {ZHIPU_KEY}"},
            json={"model": EMBED_MODEL, "input": text, "dimensions": 256},
            timeout=30,
        )
        if r.status_code != 200:
            body = r.text[:200]
            biz = re.search(r'"code"\s*:\s*"?(\w+)"?', body)
            raise RuntimeError(f"embedding 调用失败 HTTP {r.status_code} 业务码 {biz and biz.group(1)}: {body}")
        return r.json()["data"][0]["embedding"]

    async def execute(self, query: str, top_k: int = 3) -> ToolResult:
        # ── 填空 1：query 向量化 ──
        try:
            q_vec = self._embed(query)
        except Exception as e:
            return self.fail_response(f"问题向量化失败：{e}（检查 ZHIPU_API_KEY 与环境变量是否设置）")

        # ── 填空 2：连接 chromadb 并检索 ──
        try:
            client = chromadb.PersistentClient(path=KB_DIR)
            col = client.get_collection(COLLECTION)
        except Exception as e:
            return self.fail_response(
                f"知识库打开失败：{e}（可能还没跑 ingest_corpus.py 建库；"
                f"先跑 D:\\projects\\ecommerce-data-agent\\scripts\\w3_setup\\ingest_corpus.py）"
            )
        if col.count() == 0:
            return self.fail_response("知识库为空——先跑 ingest_corpus.py 入库语料")

        hit = col.query(query_embeddings=[q_vec], n_results=min(top_k, col.count()))
        docs = hit["documents"][0]
        metas = hit["metadatas"][0]
        dists = hit["distances"][0]        # chromadb 默认 L2 距离：越小越像

        # ── 填空 4：阈值过滤（先做，再拼装）──
        # chromadb 默认距离是 L2（越小越像），换算成 0~1 相似度：score = 1 / (1 + dist)
        picked = []
        for doc, meta, dist in zip(docs, metas, dists):
            score = 1.0 / (1.0 + dist)
            if score >= MIN_SCORE:
                picked.append((score, doc, meta))

        # ── 填空 4-兜底：全被过滤掉了 ──
        if not picked:
            return ToolResult(output="知识库中未找到与问题相关的内容（相关度均低于阈值）。请换一种问法，或确认问的是业务口径/操作类问题。")

        # ── 填空 3+4：结果拼装（引用来源 + 相关度分数）──
        lines = [f"知识库检索到 {len(picked)} 条资料（已按相关度降序；分数仅供排序参考，绝对值不可靠）：\n"]
        for i, (score, doc, meta) in enumerate(picked, 1):
            title = meta.get("title", "未知")
            url = meta.get("url", "")
            source = meta.get("source", "")
            lines.append(f"[{i}] 【相关度 {score:.3f} | 出处: {title} | {source} | {url}】\n{doc}\n")
        lines.append(
            "（以上为知识库原文片段。请基于这些内容作答并注明出处；"
            "**若以上内容与用户问题明显无关，必须如实说明『知识库中无相关内容』，不要强行作答。**）"
        )
        return ToolResult(output="\n".join(lines))
