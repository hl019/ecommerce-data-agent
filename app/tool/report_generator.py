# -*- coding: utf-8 -*-
"""
工具 4：report_generator —— 最终 HTML 分析报告生成（汇总统计结论 + 内嵌图表）

━━━ 学生亲手写的部分（考核官红线，ZCode 不代填）━━━
1. description：说清这是"最后一步"工具——前面查数/统计/画图都完成后才调用
   （这句话直接影响模型的工具调用顺序，好好措辞）
2. parameters：title(string) + sections(array of {heading, content}) + chart_paths(array of string)
   ——array/object 类型的 schema 比 string 难写，这是 W2 最有含金量的练手点
3. execute()：
   ① 清洗标题里的非法文件名字符（\\/:*?"<>|）
   ② sections 为空 → fail_response
   ③ chart_paths 逐个检查存在性：不存在 → 跳过并在报告里警告（不中断）
   ④ HTML 模板拼接：f-string 或 Jinja2 二选一（建议 Jinja2——简历多一个词）
      图表内嵌：读 plot_chart 生成的 HTML 里 <div>...</div> 段 + plotly.js CDN script 标签
   ⑤ 落盘 workspace/reports/时间戳_标题.html，success_response 返回路径
   面试考点：为什么报告由代码生成而不是模型直接吐 HTML？（确定性：结构与内容分离）
"""
from app.tool.base import BaseTool, ToolResult


class ReportGenerator(BaseTool):
    """HTML 报告生成工具（W2 工具 4）"""

    name: str = "report_generator"

    # TODO(学生): 写 description
    description: str = ""

    # TODO(学生): 写 parameters JSON Schema（含 array/object 嵌套类型）
    parameters: dict = {}

    REPORTS_DIR: str = "workspace/reports"

    async def execute(self, title: str, sections: list, chart_paths: list = None) -> ToolResult:
        """
        TODO(学生): 亲手实现（W2 D6-D7 任务，完成后即可跑端到端 MVP 验收）。
        """
        raise NotImplementedError("report_generator 还没实现——这是 W2 最后一个工具，写完它 MVP 就通了")
