# -*- coding: utf-8 -*-
"""
工具 3：plot_chart —— Plotly 绘图工具（填空式骨架）

预习包（先读它）：D:\\projects\\review\\ZCode-W2工具3预习包.md
你的蓝本：D:\\projects\\hl019-ecommerce-viaapi\\extracted_code.py 第 87-170 行（px.* 画图你写过）

★ 改这个（仓库正身）：
    D:\\projects\\ecommerce-data-agent\\app\\tool\\plot_chart.py
★ 不用改（OpenManus 运行副本，跑 D:\\projects\\ecommerce-data-agent\\scripts\\sync_to_openmanus.bat 自动同步）：
    D:\\projects\\OpenManus\\app\\tool\\plot_chart.py

红线：description / parameters / execute / 错误处理全部学生亲手写。
"""
import json
import os
from datetime import datetime


import pandas as pd
import plotly.express as px
from app.tool.base import BaseTool, ToolResult

VALID_CHARTS = ["line", "bar", "barh", "histogram", "pie"]


class PlotChart(BaseTool):
    """Plotly 绘图工具（W2 工具 3）"""

    name: str = "plot_chart"

    # ── 填空 A：description ─────────────────────────────
    # 引导问题（讲解提纲用，考核官带讲）：
    #   A1. 输入数据从哪来？（提示：工具 1/2 的输出 JSON——模型会照原样传，你要说清格式）
    #   A2. 五种图型什么时候各选哪种，要不要在 description 里给模型一句选择指引？
    #   A3. 返回的是文件路径还是图表数据？为什么？（预习包第三节"假 PASS 陷阱"反着用）
    description: str = (
        "将表格数据绘制成交互式图表并保存为 HTML 文件，返回文件路径。"
        "data_json 是 JSON 数组字符串，形如 [{\"月份\":\"2024-01\",\"销售额\":66304}, ...]，"
        "通常直接使用 sales_stats 或 sales_sql_query 输出的数据。"
        "chart_type 五选一：line=折线图（看趋势）；bar=柱状图（比大小）；"
        "barh=横向条形图（类别名较长时）；histogram=直方图（看分布）；pie=饼图（看占比）。"
        "用 x 指定横轴字段名、y 指定纵轴字段名（pie 时 x=类别、y=数值）。"
        "返回生成好的 HTML 文件路径，浏览器打开即可查看。"
    )


    # ── 填空 B：parameters ──────────────────────────────
    # B1：data_json（type string；description 里给出 JSON 形状示例，如 [{"月份":"2024-01","销售额":66304},...]）
    # B2：chart_type 用 enum 限死（"enum": VALID_CHARTS——和工具 2 同款）
    # B3：x / y / title：哪些进 required？histogram 和 pie 各不需要 y 或 x+y 之一吗？
    #     （先想清楚再定 required，宁可 y 不进 required 在代码里按图型校验）
    parameters: dict = {
        "type": "object",
        "properties": {
            "data_json": {
                "type": "string",
                "description": "要绘图的 JSON 数组字符串，形如 [{\"月份\":\"2024-01\",\"销售额\":66304}, ...]，通常直接传入 sales_stats 的输出。",
            },
            "chart_type": {
                "type": "string",
                "enum": VALID_CHARTS,
                "description": "图表类型：line=折线图；bar=柱状图；barh=横向条形图；histogram=直方图；pie=饼图。",
            },
            "title": {
                "type": "string",
                "description": "图表标题，会用作 HTML 文件名的一部分。",
            },
            "x": {
                "type": "string",
                "description": "横轴字段名（必须是数据里的列名）；pie 图时表示类别字段。",
            },
            "y": {
                "type": "string",
                "description": "纵轴字段名（必须是数据里的列名）；histogram 不需要；pie 图时表示数值字段。",
            },
        },
        "required": ["data_json", "chart_type", "title", "x"],
    }


    # 图表输出目录（相对 OpenManus 运行目录）
    CHARTS_DIR: str = "workspace/charts"

    async def execute(
        self,
        data_json: str,
        chart_type: str,
        title: str,
        x: str,
        y: str = "",
    ) -> ToolResult:
        """
        ── 填空 1：解析数据 ──
        json.loads(data_json) → pd.DataFrame。
        引导问题：模型可能传来带外层键的对象（如 {"monthly": [...]}）而不是裸数组，
        你的容错底线是什么？解析失败时 fail_response 写什么让模型能重传？

        ── 填空 2：列名校验 ──
        x / y 必须在 DataFrame 列里，不在 → fail_response **回显实际列名**。
        引导问题：回显列名和工具 2 回显枚举值是不是同一个思想？（给模型可行动的反馈）

        ── 填空 3：图型分发 ──
        chart_type → plotly.express 对应函数（px.line/bar/barh/histogram/pie），
        非法值 → fail_response 回显 VALID_CHARTS。
        引导问题：pie 需要的参数（names/values）和 line 的（x/y）名字不同，分发时怎么统一处理？

        ── 填空 4：落盘与返回 ──
        目录自动创建 → fig.write_html(时间戳_标题.html) → success_response(路径+一句解读提示)。
        引导问题：文件名里的 title 可能带 \\ / : * ? 等非法字符，怎么办？
        （面试考点：为什么返回路径而不是让模型复述数据？——图表是真数据，文本才防幻觉）
        """
        # 填空 1：解析数据（JSON 字符串 → DataFrame）
        try:
            data = json.loads(data_json)
            if isinstance(data, dict):
                # 容错：模型可能包了一层（如 {"monthly": [...]}），挖出里面第一个 list
                data = next((v for v in data.values() if isinstance(v, list)), data)
            df = pd.DataFrame(data)
        except (json.JSONDecodeError, ValueError) as e:
            return self.fail_response(
                f"data_json 解析失败：{e}。请传入 JSON 数组字符串，形如包含「月份/销售额」两列的对象列表。"
            )
        if df.empty:
            return self.fail_response("数据为空，没有可绘制的内容。")

        # 填空 2：列名校验（回显实际列名，给模型可行动的反馈）
        cols = list(df.columns)
        if x not in cols:
            return self.fail_response(f"x 列「{x}」不存在，实际列名：{cols}")
        if y and y not in cols:
            return self.fail_response(f"y 列「{y}」不存在，实际列名：{cols}")
        if chart_type != "histogram" and not y:
            return self.fail_response(f"「{chart_type}」图需要 y 参数（纵轴字段名），请补充。")

        # 填空 3：图型分发
        if chart_type == "line":
            fig = px.line(df, x=x, y=y, title=title, markers=True)
        elif chart_type == "bar":
            fig = px.bar(df, x=x, y=y, title=title)
        elif chart_type == "barh":
            fig = px.bar(df, x=y, y=x, title=title, orientation="h")
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x, title=title)
        elif chart_type == "pie":
            fig = px.pie(df, names=x, values=y, title=title)
        else:
            return self.fail_response(f"非法 chart_type：「{chart_type}」，合法值：{VALID_CHARTS}")

        # 填空 4：落盘与返回
        os.makedirs(self.CHARTS_DIR, exist_ok=True)
        safe_title = "".join(c for c in title if c not in '\\/:*?"<>|')[:30] or "chart"
        filename = f"{datetime.now():%Y%m%d_%H%M%S}_{safe_title}.html"
        path = os.path.join(self.CHARTS_DIR, filename)
        fig.write_html(path)
        return self.success_response(f"图表已生成：{path}（用浏览器打开查看）")
