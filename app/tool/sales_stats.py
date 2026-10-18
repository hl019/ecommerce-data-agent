# -*- coding: utf-8 -*-
"""

"""
import json
import os
import pandas as pd

from app.tool.base import BaseTool, ToolResult

VALID_TYPES = ["monthly", "category", "user", "top_products", "repurchase"]
def _analyze_monthly(transactions):
    """按月统计销售额/订单数/销量"""
    df = transactions.copy()
    df["Month"] = df["TransactionDate"].dt.to_period("M").astype(str)
    out = (
        df.groupby("Month", as_index=False)
        .agg(销售额=("TotalValue", "sum"), 订单数=("TransactionID", "count"), 销量=("Quantity", "sum"))
        .sort_values("Month")
    )
    return out.to_dict(orient="records")

def _analyze_category(transactions, products):
    """按品类统计销售额对比"""
    merged = transactions.merge(products[["ProductID", "Category"]], on="ProductID", how="left")
    out = (
        merged.groupby("Category", as_index=False)
        .agg(销售额=("TotalValue", "sum"), 销量=("Quantity", "sum"))
        .sort_values("销售额", ascending=False)
    )
    return out.to_dict(orient="records")

def _analyze_user(transactions, top_n):
    """按客户统计购买次数与消费额"""
    out = (
        transactions.groupby("CustomerID", as_index=False)
        .agg(订单数=("TransactionID", "nunique"), 消费额=("TotalValue", "sum"), 销量=("Quantity", "sum"))
        .sort_values("消费额", ascending=False)
        .head(top_n)
    )
    return out.to_dict(orient="records")

def _analyze_top_products(transactions, products, top_n):
    """按销售额排名的畅销商品 Top N"""
    out = (
        transactions.groupby("ProductID", as_index=False)
        .agg(销售额=("TotalValue", "sum"), 销量=("Quantity", "sum"))
        .merge(products[["ProductID", "ProductName"]], on="ProductID", how="left")
        .sort_values("销售额", ascending=False)
        .head(top_n)
    )
    return out.to_dict(orient="records")

def _analyze_repurchase(transactions):
    """复购用户占比 + 头部 20% 用户销售额贡献"""
    buy_count = transactions.groupby("CustomerID")["TransactionID"].nunique()
    repurchase_rate = (buy_count > 1).mean() * 100
    customer_spend = transactions.groupby("CustomerID")["TotalValue"].sum().sort_values(ascending=False)
    top20 = customer_spend.head(int(len(customer_spend) * 0.2))
    return [
        {
            "复购用户占比(%)": round(float(repurchase_rate), 2),
            "Top20%用户销售额占比(%)": round(float(top20.sum() / customer_spend.sum() * 100), 2),
        }
    ]

class SalesStats(BaseTool):
    """pandas 统计工具"""

    name: str = "sales_stats"

    #description ─────────────────────────────
    description: str = (
        "对电商交易数据做预设的统计分析，返回 JSON 结果。支持五种 analysis_type："
        "monthly=按月统计销售额/订单数/销量的趋势；category=按商品品类统计销售额对比；"
        "user=按客户统计购买次数与消费额；top_products=按销售额排名的畅销商品 Top N；"
        "repurchase=复购用户占比与头部 20% 用户的销售额贡献。"
        "适合聚合统计类问题；若只需查询具体明细数据，请改用 sales_sql_query 工具。"
    )

    #parameters ──────────────────────────────
    # B1：analysis_type 用 enum 限死（关键字 "enum"，值就是 VALID_TYPES）
    # B2：top_n 的 type 与默认值语义说明（为什么不进 required？）
    # B3：required 只放 analysis_type
    parameters: dict = {
        "type": "object",
        "properties": {
            "analysis_type": {
                "type": "string",
                "enum": VALID_TYPES,
                "description": "分析类型，必填。monthly=按月销售额趋势；category=品类销售额对比；user=客户购买次数与消费额；top_products=畅销商品 Top N；repurchase=复购率与头部 20% 用户贡献。",
            },
            "top_n": {
                "type": "integer",
                "description": "top_products 分析返回的前 N 名商品，默认 10。",
            },
        },
        "required": ["analysis_type"],
    }

    # CSV 数据目录（默认演示机路径，换环境用环境变量 ECOM_DATA_DIR 覆盖）
    DATA_DIR: str = os.environ.get("ECOM_DATA_DIR", r"D:\projects\hl019-ecommerce-viaapi\data")

    async def execute(self, analysis_type: str, top_n: int = 10) -> ToolResult:
        """
        #读 CSV + 解析日期 ──
        三张表从 DATA_DIR 读；日期列 pd.to_datetime(errors="coerce")。

        #五个分析函数 ──
        monthly / category / user / top_products / repurchase 各一个独立函数，
        五类聚合：monthly / category / user / top_products / repurchase。

        #分发 + 非法枚举兜底 ──
        认识的值路由到对应函数；不认识的 → return self.fail_response(...)，
        错误信息里必须回显 VALID_TYPES（模型靠它自我纠正）。

        #输出 JSON ──
        结果转 list[dict]，json.dumps(..., ensure_ascii=False)，列名中文。
        """
        #读三张 CSV（不依赖 MySQL，直接读文件）
        try:
            transactions = pd.read_csv(os.path.join(self.DATA_DIR, "Transactions.csv"))
            products = pd.read_csv(os.path.join(self.DATA_DIR, "Products.csv"))
            customers = pd.read_csv(os.path.join(self.DATA_DIR, "Customers.csv"))
        except FileNotFoundError as e:
            return self.fail_response(f"数据文件读取失败：{e}")

        # 日期列解析成 datetime（不解析，按月分组会出错）
        transactions["TransactionDate"] = pd.to_datetime(
            transactions["TransactionDate"], errors="coerce"
        )
        #分发 + 非法枚举兜底
        if analysis_type == "monthly":
            result = _analyze_monthly(transactions)
        elif analysis_type == "category":
            result = _analyze_category(transactions, products)
        elif analysis_type == "user":
            result = _analyze_user(transactions, top_n)
        elif analysis_type == "top_products":
            result = _analyze_top_products(transactions, products, top_n)
        elif analysis_type == "repurchase":
            result = _analyze_repurchase(transactions)
        else:
            return self.fail_response(f"非法 analysis_type：{analysis_type}，合法值：{VALID_TYPES}")
        #输出 JSON
        return self.success_response(json.dumps(result, ensure_ascii=False))
