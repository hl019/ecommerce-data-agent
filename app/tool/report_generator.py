# -*- coding: utf-8 -*-
"""
工具 4：report_generator —— 最终 HTML 分析报告生成（填空式骨架 · W2 最后一个工具）

预习包（先读它）：D:\\projects\\review\\ZCode-W2工具4预习包.md
（含 PASS 标准、嵌图体积账、token 统计线索、写完后的 MVP 接通四步）

★ 改这个（仓库正身）：
    D:\\projects\\ecommerce-data-agent\\app\\tool\\report_generator.py
★ 不用改（OpenManus 运行副本，跑 D:\\projects\\ecommerce-data-agent\\scripts\\sync_to_openmanus.bat 自动同步）：
    D:\\projects\\OpenManus\\app\\tool\\report_generator.py

红线：description / parameters / execute / 错误处理全部学生亲手写。
"""
import json
import os
from datetime import datetime

from app.tool.base import BaseTool, ToolResult


class ReportGenerator(BaseTool):
    """HTML 报告生成工具（W2 工具 4）"""

    name: str = "report_generator"

    # ── 填空 A：description ─────────────────────────────
    # 引导问题（讲解提纲）：
    #   A1. 这句话决定调用时机——要不要写"前面查数/统计/画图都完成后，最后调用本工具出报告"？
    #   A2. sections 的结构怎么向模型描述？（给个形如 [{"heading":"结论","content":"..."}] 的例子）
    #   A3. 返回什么？（路径——和工具 3 同款防幻觉逻辑）
    description: str = (
        "生成最终的分析报告（HTML 文件），作为整个任务的最后一步交付物，返回报告文件路径。"
        "当数据查询、统计分析、图表都已完成后，调用本工具把结论整合成一份报告。"
        "sections 是要写入报告的章节列表，每项形如 {\"heading\":\"结论\",\"content\":\"月度销售额稳中有升\"}，"
        "由你根据前面的分析结果组织内容。"
        "chart_paths 可选：把 plot_chart 生成的图表 HTML 路径传进来，报告会嵌入这些图表。"
    )


    # ── 填空 B：parameters（W2 最有含金量的练手点：array/object 嵌套 schema）──
    # B1：title(string)
    # B2：sections = array，items 是 object{heading:string, content:string}
    #     ——三层嵌套：type/items/properties/required，想清楚每层各管什么
    # B3：chart_paths = array of string，可选（不进 required）
    parameters: dict = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "报告标题，会用作 HTML 文件名的一部分。",
            },
            "sections": {
                "type": "array",
                "description": "报告章节列表，每项含 heading（章节小标题）和 content（该章节正文）。",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {
                            "type": "string",
                            "description": "章节小标题",
                        },
                        "content": {
                            "type": "string",
                            "description": "该章节的正文内容",
                        },
                    },
                    "required": ["heading", "content"],
                },
            },
            "chart_paths": {
                "type": "array",
                "description": "可选：要嵌入报告的图表 HTML 文件路径列表（来自 plot_chart 工具的输出）。",
                "items": {"type": "string"},
            },
        },
        "required": ["title", "sections"],
    }


    REPORTS_DIR: str = "workspace/reports"

    async def execute(self, title: str, sections: list, chart_paths: list = None) -> ToolResult:
        """
        ── 填空 1：入参校验 ──
        sections 空 → fail_response；title 清洗非法文件名字符（工具 3 同款思路，怎么复用？）。

        ── 填空 2：chart_paths 逐个检查存在性 ──
        不存在的 → 跳过 + 在报告正文对应位置留一句警告（不中断整个报告）。
        引导问题：为什么是"警告跳过"而不是 fail_response 报错？（报告是终点交付物，宁缺勿断）

        ── 填空 3：HTML 模板拼接（f-string 或 Jinja2 二选一，建议 Jinja2——简历多一个词）──
        结构：标题 + 各 section(heading/content) + 嵌图区 + token 统计页脚。
        ★ 嵌图体积账（工具3审查已实测）：单个图表 HTML = 4.8MB（plotly.js 整份内联）！
          直接 iframe 多张图报告会上 20MB。线索：读图表文件里 <div id="plotly...">...</div>
          段 + 页面只引一次 plotly.js 的 <script src="CDN地址">。
          （或者反过来：改工具 3 write_html 传 include_plotlyjs="cdn" 生成 10KB 级小文件——
           两种路线自己评估，选定后在预习包第五节登记决定，考核官验收要听理由）

        ── 填空 4：token 消耗统计（0928 增补·"效果数字"来源，面试硬通货）──
        报告末尾附「本次任务累计消耗 N tokens ≈ ¥X」。
        取数线索：grep 一下 D:\\projects\\OpenManus\\app\\llm.py 里的 total_ 字样——
        LLM 类是全局单例（__new__ 里 _instances），整个会话的累计计数就存在那。
        找到字段名后想：工具怎么拿到那个实例？（提示：同名单例，再 new 一次拿到的是同一个）
        ¥ 换算：查 DeepSeek 官网当前定价，写常量并注明查询日期。
        引导问题：这个数字为什么必须"代码统计"而不是让模型估？（它看不见 usage——又一条防幻觉）

        ── 填空 5：落盘返回 ──
        目录自动创建 → workspace/reports/时间戳_标题.html → success_response(路径)。

        （面试考点：为什么报告由代码生成而不是模型直接吐 HTML？——确定性：结构与内容分离）
        """
        # 填空 1：入参校验
        if not sections:
            return self.fail_response(
                "sections 不能为空——报告至少需要一个章节，形如 [{\"heading\":\"结论\",\"content\":\"...\"}]。"
            )
        safe_title = "".join(c for c in title if c not in '\\/:*?"<>|')[:30] or "report"

        # 填空 2：逐个检查图表文件（缺失的跳过 + 记警告，不中断报告）
        chart_paths = chart_paths or []
        valid_charts = []
        missing_charts = []
        for p in chart_paths:
            if os.path.exists(p):
                valid_charts.append(p)
            else:
                missing_charts.append(p)

        # 填空 3：拼 HTML 片段
        sections_html = ""
        for s in sections:
            sections_html += f"<h2>{s.get('heading', '')}</h2>\n<p>{s.get('content', '')}</p>\n"

        charts_html = ""
        for p in valid_charts:
            # 关键：iframe 的 src 由浏览器按「报告文件所在目录」解析，
            # 而 p 是相对「进程工作目录(CWD)」的路径。两者基准不同，
            # 直接写 p 会被解析成 workspace/reports/workspace/charts/... → 裂图。
            # 所以必须换算成「相对报告目录」的路径（../charts/xxx.html）。
            rel = os.path.relpath(p, self.REPORTS_DIR).replace("\\", "/")
            charts_html += f'<iframe src="{rel}" width="100%" height="430" style="border:none"></iframe>\n'
        for p in missing_charts:
            charts_html += f'<p style="color:#c00">⚠ 图表未找到，已跳过：{p}</p>\n'

        # 填空 4：token 消耗统计（读 LLM 单例的累计计数）
        from app.llm import LLM
        llm = LLM()                     # 同名单例：再 new 一次拿到的是同一个实例
        total_in = llm.total_input_tokens
        total_out = llm.total_completion_tokens
        total_tokens = total_in + total_out
        PRICE_IN = 2.0   # 元/百万 tokens（DeepSeek-V4.1-Flash 输入·缓存未命中·高峰价，查询日期 2026-10-06）
        PRICE_OUT = 8.0  # 元/百万 tokens（DeepSeek-V4.1-Flash 输出·高峰价，同上）
        cost = total_in / 1_000_000 * PRICE_IN + total_out / 1_000_000 * PRICE_OUT

        # 填空 5：拼完整 HTML 并落盘
        report_html = f"""<!DOCTYPE html>
<html lang="zh">
<head><meta charset="utf-8"><title>{safe_title}</title></head>
<body style="font-family:sans-serif;max-width:900px;margin:40px auto">
<h1>{safe_title}</h1>
{sections_html}
<h2>图表</h2>
{charts_html}
<hr>
<footer style="color:#666">本次任务累计消耗 {total_tokens} tokens ≈ ¥{cost:.4f}</footer>
</body>
</html>"""

        os.makedirs(self.REPORTS_DIR, exist_ok=True)
        filename = f"{datetime.now():%Y%m%d_%H%M%S}_{safe_title}.html"
        path = os.path.join(self.REPORTS_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(report_html)
        return self.success_response(f"报告已生成：{path}（用浏览器打开查看）")

