# -*- coding: utf-8 -*-
r"""
相似客户检索工具 customer_lookalike（W4 · ML 工具）

定位：给一个客户ID，找出"消费构成最相似"的 top_k 个客户（营销上的 Lookalike 相似人群）。

    D:\projects\ecommerce-data-agent\app\tool\customer_lookalike.py
    D:\projects\OpenManus\app\tool\customer_lookalike.py

三个算法决策（面试要能讲，#7 口径：讲设计不推公式）：
  1) 特征 = "客户×商品"购买数量矩阵（pivot_table）——最朴素也最有效
  2) 标准化 + PCA：标准化拉平量纲（防大数吞小数）；PCA 去噪、抗维度灾难（🟢 公式不学）
  3) cosine 距离：只比"购买构成"、不比"购买规模"——业务上更合理
     （例：A 买 3 书 3 电器，B 买 30 书 30 电器 → 构成相同，业务上很像；欧氏距离会说不像）
"""
import json
import os

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from app.tool.base import BaseTool, ToolResult

DATA_DIR = r"D:\projects\hl019-ecommerce-viaapi\data"

class CustomerLookalike(BaseTool):
    """相似客户检索（Lookalike 相似人群）"""

    name: str = "customer_lookalike"

    description: str = (
        "根据一个客户ID，找出消费构成最相似的其他客户（营销上叫 Lookalike 相似人群）。"
        "返回相似客户ID、姓名、相似度分数，以及双方共同购买的商品。"
        "适用于：找高价值客户的相似人群做精准投放、分析客户结构。"
        "不适用于：查单个客户的消费金额或订单数（那类请用 SQL / 统计工具）。"
    )

    parameters: dict = {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "目标客户ID，例如 C0001",
            },
            "top_k": {
                "type": "integer",
                "description": "返回最相似的几个客户，默认 3",
            },
        },
        "required": ["customer_id"],
    }

    async def execute(self, customer_id: str, top_k: int = 3) -> ToolResult:
        #读三表（注意 CSV 带 BOM，用 utf-8-sig）──
        try:
            transactions = pd.read_csv(os.path.join(DATA_DIR, "Transactions.csv"), encoding="utf-8-sig")
            products = pd.read_csv(os.path.join(DATA_DIR, "Products.csv"), encoding="utf-8-sig")
            customers = pd.read_csv(os.path.join(DATA_DIR, "Customers.csv"), encoding="utf-8-sig")
        except Exception as e:
            return self.fail_response(f"读取数据失败：{e}（检查 {DATA_DIR} 下的三个 CSV）")

        # ── 特征：客户 × 商品 购买数量矩阵 ──
        merged = pd.merge(transactions, customers, on="CustomerID")
        merged = pd.merge(merged, products, on="ProductID")
        pivot = merged.pivot_table(
            index="CustomerID", columns="ProductID", values="Quantity", aggfunc="sum", fill_value=0
        )

        customer_id = str(customer_id).strip().upper()
        if customer_id not in pivot.index:
            sample = list(pivot.index[:5])
            return self.fail_response(
                f"客户ID「{customer_id}」不存在。合法 ID 示例：{sample}（本库共 {len(pivot.index)} 个客户）"
            )

        #标准化 + PCA 降维 ──
        scaler = StandardScaler()
        scaled = scaler.fit_transform(pivot.values)
        # n_components=0.95 = 自适应保留 95% 方差（比固定 3 维更稳）
        pca = PCA(n_components=0.95, random_state=42)
        reduced = pca.fit_transform(scaled)

        #KNN 检索（cosine）──
        # 坑：kneighbors 返回的第一个永远是"自己"（距离 0）→ 查 top_k+1 个，取的时候从 1 开始
        k = max(1, min(int(top_k), len(pivot.index) - 1))  # top_k ≤ 0 兜底为 1，避免 sklearn 抛 InvalidParameterError
        model = NearestNeighbors(n_neighbors=k + 1, metric="cosine")
        model.fit(reduced)

        idx = pivot.index.get_loc(customer_id)
        distances, indices = model.kneighbors([reduced[idx]])

        #输出设计（剔自己 + 共同商品）──
        name_map = customers.set_index("CustomerID")["CustomerName"].to_dict()
        product_names = products.set_index("ProductID")["ProductName"].to_dict()
        row_target = pivot.loc[customer_id]

        results = []
        for j in range(1, len(indices[0])):        # 从 1 开始 = 剔掉自己
            sim_id = pivot.index[indices[0][j]]
            similarity = round(1 - float(distances[0][j]), 4)   # cosine 距离 → 相似度

            row_sim = pivot.loc[sim_id]
            both = [
                (pid, row_target[pid] + row_sim[pid])
                for pid in pivot.columns
                if row_target[pid] > 0 and row_sim[pid] > 0
            ]
            both.sort(key=lambda x: -x[1])
            common = [product_names.get(pid, str(pid)) for pid, _ in both[:2]]

            results.append({
                "客户ID": sim_id,
                "姓名": name_map.get(sim_id, ""),
                "相似度": similarity,
                "共同购买商品": common,
            })

        if not results:
            return self.fail_response("没有找到相似客户（数据量不足）")

        #输出 ──
        return self.success_response(json.dumps({
            "目标客户": {"客户ID": customer_id, "姓名": name_map.get(customer_id, "")},
            "相似客户数": len(results),
            "相似客户": results,
        }, ensure_ascii=False, indent=2))
