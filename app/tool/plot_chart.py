# -*- coding: utf-8 -*-
"""
工具 3：plot_chart —— Plotly 绘图工具（统计结果 → 交互图表 HTML 文件）

━━━ 学生亲手写的部分（考核官红线，ZCode 不代填）━━━
1. description：说清输入是什么格式（前两个工具的输出 JSON）、能画哪几种图
2. parameters：chart_type 用 enum（line/bar/barh/histogram/pie），
   data_json/title/x/y 各写清含义
3. execute()：
   ① json.loads(data_json) → DataFrame（解析失败给可读错误）
   ② 校验 x/y 列存在于数据（不存在 → fail_response 回显实际列名，模型能自纠）
   ③ chart_type 分发到对应 plotly.express 函数（你 notebook 87-170 行的 px 用法）
   ④ fig.write_html(路径)，路径=workspace/charts/时间戳_标题.html，目录自动创建
   ⑤ success_response 返回文件路径 + 一句图表解读提示
   面试考点：为什么返回路径而不是让模型复述数据？（防转录幻觉——设计草案工具 3）
"""
from app.tool.base import BaseTool, ToolResult


class PlotChart(BaseTool):
    """Plotly 绘图工具（W2 工具 3）"""

    name: str = "plot_chart"

    # TODO(学生): 写 description
    description: str = ""

    # TODO(学生): 写 parameters JSON Schema（5 个参数，见文件头注释）
    parameters: dict = {}

    # 图表输出目录（相对 OpenManus 运行目录；execute 里记得 os.makedirs(exist_ok=True)）
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
        TODO(学生): 亲手实现（W2 D5 任务）。
        提示：pie/histogram 可以没有 y 参数——分发时注意各图型需要的参数不同。
        """
        raise NotImplementedError("plot_chart 还没实现——这是你 W2 D5 的任务")
