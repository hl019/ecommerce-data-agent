# -*- coding: utf-8 -*-
"""

报告生成工具：汇总结论与图表，产出可独立转发的单文件 HTML 报告。

    D:\\projects\\ecommerce-data-agent\\app\\tool\\report_generator.py
    D:\\projects\\OpenManus\\app\\tool\\report_generator.py

"""
import json
import os
from datetime import datetime
from html import escape

from app.tool.base import BaseTool, ToolResult

class ReportGenerator(BaseTool):
    """HTML 报告生成工具"""

    name: str = "report_generator"

    #description ─────────────────────────────
    description: str = (
        "生成最终的分析报告（HTML 文件），作为整个任务的最后一步交付物，返回报告文件路径。"
        "当数据查询、统计分析、图表都已完成后，调用本工具把结论整合成一份报告。"
        "sections 是要写入报告的章节列表，每项形如 {\"heading\":\"结论\",\"content\":\"月度销售额稳中有升\"}，"
        "由你根据前面的分析结果组织内容。"
        "chart_paths 可选：把 plot_chart 生成的图表 HTML 路径传进来，报告会嵌入这些图表。"
    )

    # parameters：sections 为 array[object{heading,content}] 三层嵌套 schema；
    # chart_paths 为可选 array[string]（不进 required）
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
        """流程：入参校验 → 图表存在性检查（缺失警告跳过，交付物宁缺勿断）
        → 图表内联进报告（单文件自包含，可独立转发）
        → token 消耗页脚（读 LLM 进程单例本轮计数，Agent 入口起算为 0）
        → 落盘 workspace/reports/时间戳_标题.html → success_response(路径)。
        报告由代码模板生成而非模型直出 HTML：结构确定性归代码、内容归模型；
        token 数字必须代码统计：模型看不见 usage，估算即幻觉。"""
        #入参校验
        if not sections:
            return self.fail_response(
                "sections 不能为空——报告至少需要一个章节，形如 [{\"heading\":\"结论\",\"content\":\"...\"}]。"
            )
        # sections 元素类型校验：元素必须是 dict，且 heading/content 必须是字符串
        for s in sections:
            if not isinstance(s, dict):
                return self.fail_response(
                    f"sections 元素必须是字典，收到 {type(s).__name__}。正确格式：[{{\"heading\":\"结论\",\"content\":\"...\"}}]"
                )
            # 字段值校验：content=None 会让 escape() 抛 AttributeError，这里先归一成空串
            for _k in ("heading", "content"):
                if s.get(_k) is None:
                    s[_k] = ""
                elif not isinstance(s[_k], str):
                    return self.fail_response(
                        f"sections 元素字段 {_k} 必须是字符串，收到 {type(s[_k]).__name__}。"
                        f"正确格式：[{{\"heading\":\"结论\",\"content\":\"...\"}}]"
                    )

        safe_title = "".join(c for c in title if c not in '\\/:*?"<>|')[:30] or "report"

        #逐个检查图表文件（缺失的跳过 + 记警告，不中断报告）
        chart_paths = chart_paths or []
        valid_charts = []
        missing_charts = []
        for p in chart_paths:
            if os.path.exists(p):
                valid_charts.append(p)
            else:
                missing_charts.append(p)

        #拼 HTML 片段
        sections_html = ""
        for s in sections:
            sections_html += f"<h2>{escape(s.get('heading', ''))}</h2>\n<p>{escape(s.get('content', ''))}</p>\n"

        # ── I2：图表内联进报告（单文件自包含，报告可独立发送）──
        # 原实现用 iframe 引用 ../charts/xxx.html：相对路径依赖本机目录，
        # 报告一旦发给别人（或移到别处）图表就裂。
        # 现改为：把图表文件 body 内的内容（空容器 div + Plotly.newPlot 脚本）
        # 整段嵌入报告，并在 <head> 里只引一次 plotly CDN。
        import re as _re
        charts_html = ""
        plotly_script = ""
        _CDN_RE = r'<script[^>]*src="https://cdn\.plot\.ly/[^"]*"[^>]*>\s*</script>'
        for p in valid_charts:
            try:
                with open(p, encoding="utf-8") as _f:
                    _src = _f.read()
            except Exception as e:
                charts_html += (
                    f'<p style="color:#c00">⚠ 图表读取失败（{e}），已跳过：{os.path.basename(p)}</p>\n'
                )
                continue
            # 从首个图表里提取 plotly CDN 标签（版本与图表生成时一致）
            if not plotly_script:
                _m0 = _re.search(_CDN_RE, _src)
                if _m0:
                    plotly_script = _m0.group(0)
            # 取 body 内容并剔除其中的 CDN 标签（避免重复引入）
            _m = _re.search(r'<body[^>]*>(.*?)</body>', _src, _re.S)
            _content = _m.group(1) if _m else _src
            _content = _re.sub(_CDN_RE, '', _content)
            charts_html += _content.strip() + "\n"
        for p in missing_charts:
            charts_html += f'<p style="color:#c00">⚠ 图表未找到，已跳过：{os.path.basename(p)}</p>\n'

        #token 消耗统计（读 LLM 单例的累计计数）
        from app.llm import LLM
        llm = LLM()                     # 同名单例：再 new 一次拿到的是同一个实例
        total_in = llm.total_input_tokens
        total_out = llm.total_completion_tokens
        total_tokens = total_in + total_out
        PRICE_IN = 2.0   # 元/百万 tokens（DeepSeek-V4.1-Flash 输入·缓存未命中·高峰价，查询日期 2026-10-06）
        PRICE_OUT = 8.0  # 元/百万 tokens（DeepSeek-V4.1-Flash 输出·高峰价，同上）
        cost = total_in / 1_000_000 * PRICE_IN + total_out / 1_000_000 * PRICE_OUT

        #拼完整 HTML 并落盘
        report_html = f"""<!DOCTYPE html>
<html lang="zh">
<head><meta charset="utf-8"><title>{safe_title}</title>
{plotly_script}</head>
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
