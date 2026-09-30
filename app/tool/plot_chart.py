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
    description: str = ""

    # ── 填空 B：parameters ──────────────────────────────
    # B1：data_json（type string；description 里给出 JSON 形状示例，如 [{"月份":"2024-01","销售额":66304},...]）
    # B2：chart_type 用 enum 限死（"enum": VALID_CHARTS——和工具 2 同款）
    # B3：x / y / title：哪些进 required？histogram 和 pie 各不需要 y 或 x+y 之一吗？
    #     （先想清楚再定 required，宁可 y 不进 required 在代码里按图型校验）
    parameters: dict = {}

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
        raise NotImplementedError("工具 3 还没写——按填空 1-4 顺序来，写完跑 tests/test_tools.py")
