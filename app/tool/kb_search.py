# -*- coding: utf-8 -*-
"""
检索工具 kb_search —— 电商知识库语义检索（填空式骨架，W3 主工具）

预习包：D:\\projects\\review\\ZCode-W3预习包-第1课-RAG.md
向量与 embedding 模型绑定：换 embedding 模型必须整库重建（考核官 1007 提醒，验收会问）

★ 改这个（仓库正身）：
    D:\\projects\\ecommerce-data-agent\\app\\tool\\kb_search.py
★ 不用改（OpenManus 运行副本，跑 D:\\projects\\ecommerce-data-agent\\scripts\\sync_to_openmanus.bat 自动同步）：
    D:\\projects\\OpenManus\\app\\tool\\kb_search.py

红线：description / parameters / execute / 错误处理全部学生亲手写。
embedding 调用的完整写法你已在 lab03 步骤2 见过——搬过来改，别从零猜。
"""
from app.tool.base import BaseTool, ToolResult

KB_DIR = r"D:\projects\knowledge\ecom_kb"     # 知识库存放处（ingest_corpus 写、本工具读）
COLLECTION = "ecom_kb"


class KBSearch(BaseTool):
    """电商知识库检索工具（W3）"""

    name: str = "kb_search"

    # ── 填空 A：description ─────────────────────────────
    # 引导问题：什么时候该查知识库而不是查数据库？
    # （口径类/操作类问题→kb_search；数字类问题→SQL/stats。模型靠这句话选路）
    description: str = ""

    # ── 填空 B：parameters ──────────────────────────────
    # query: string 必填；top_k: integer 可选默认 3
    # 引导问题：top_k 为什么不该让模型随便开大？（token 账 + 噪音块）
    parameters: dict = {}

    async def execute(self, query: str, top_k: int = 3) -> ToolResult:
        """
        ── 填空 1：query 向量化 ──
        调智谱 embedding-3（写法从 D:\\projects\\lab\\03_embeddings_first_contact.py 步骤2 搬）。
        错误处理：key 没设 / API 挂了 → fail_response 说人话。

        ── 填空 2：连接 chromadb 并检索 ──
        PersistentClient(path=KB_DIR) → get_collection(COLLECTION) → query(n_results=top_k)。
        错误处理：库不存在（还没跑 ingest？）→ fail_response 提示先入库。

        ── 填空 3：结果拼装（引用来源就在这）──
        把命中的 documents 逐条拼成：
            【出处: 标题 | 来源URL】正文
        引导问题：出处字段从哪来？（metadata 四元组——lab 步骤3 你刚看过它原样带回）

        ── 填空 4：无命中兜底 ──
        相似度都很低/结果为空 → 返回"知识库无相关内容"而不是硬塞最差的。
        引导问题：top-k 永远凑满 k 条，第 3 名是垃圾也照给——怎么防？
        （考核官带写讨论：距离阈值 or 让模型自己判断相关性，各有账）

        输出格式想清楚再写：这份文本会被塞进录音带给模型看——
        是答案吗？不是，是"带出处的资料片段"。description 里也要这么定位。
        """
        raise NotImplementedError("kb_search 还没写——W3 主工具，按填空 1-4 来")
