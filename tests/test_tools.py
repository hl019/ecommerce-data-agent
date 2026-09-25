# -*- coding: utf-8 -*-
"""
W2 工具自测脚本：每写完一个工具 → 跑一次 → 自己判断对不对，不依赖 ZCode 手把手。

运行方式（任意 python，需已装 pandas/sqlalchemy/pymysql/plotly）：
    python D:\\projects\\ecommerce-data-agent\\tests\\test_tools.py

判定规则：
    PASS = 实现正确     FAIL = 实现了但行为不对（看错误信息修）
    SKIP = 还是 NotImplementedError 空骨架（没写呢，不算错）

前提：
    1. 已跑过 scripts\\sync_to_openmanus.bat（把仓库 app\\ 同步进 OpenManus）
    2. sales_sql_query 的两个测试需要 MySQL 已初始化（one_click_init 跑过）
"""
import asyncio
import json
import os
import re
import sys

OPENMANUS_ROOT = r"D:\projects\OpenManus"  # 运行时环境（工具代码同步到这里）
sys.path.insert(0, OPENMANUS_ROOT)
os.chdir(OPENMANUS_ROOT)  # 让 workspace/charts 等相对路径落在这里

try:
    from app.tool.sales_sql_query import SalesSQLQuery
    from app.tool.sales_stats import SalesStats
    from app.tool.plot_chart import PlotChart
    from app.tool.report_generator import ReportGenerator
except ImportError as e:
    sys.exit(f"导入失败：{e}\n请先运行 scripts\\sync_to_openmanus.bat 把工具代码同步进 OpenManus")

RESULTS = []  # (工具, 用例名, 状态, 说明)


def run(tool_name, case_name, coro_factory, checker):
    """执行一个测试用例：NotImplementedError→SKIP，checker 断言失败→FAIL"""
    try:
        result = asyncio.run(coro_factory())
    except NotImplementedError as e:
        RESULTS.append((tool_name, case_name, "SKIP", str(e)))
        return
    except Exception as e:
        RESULTS.append((tool_name, case_name, "FAIL", f"execute() 抛了未捕获异常: {type(e).__name__}: {e}"))
        return
    try:
        checker(result)
        RESULTS.append((tool_name, case_name, "PASS", ""))
    except AssertionError as e:
        RESULTS.append((tool_name, case_name, "FAIL", str(e)))
    except Exception as e:
        RESULTS.append((tool_name, case_name, "FAIL", f"检查阶段异常: {type(e).__name__}: {e}"))


def output_text(result) -> str:
    """兼容 ToolResult / dict / str 三种返回形态"""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return json.dumps(result, ensure_ascii=False)
    return str(getattr(result, "output", result))


def error_text(result):
    return getattr(result, "error", None) if not isinstance(result, (str, dict)) else (
        result.get("error") if isinstance(result, dict) else None
    )


def find_html_path(text: str):
    m = re.search(r"[A-Za-z]:[\\/][^\s\"']+\.html|workspace[\\/][^\s\"']+\.html", text)
    return m.group(0) if m else None


# ============ 工具 1：sales_sql_query ============
t1 = SalesSQLQuery()

def check_count_199(result):
    text = output_text(result)
    assert "199" in text, f"输出里应包含 Customers 总行数 199，实际输出: {text[:200]}"

run("sales_sql_query", "SELECT COUNT(*) 返回 199",
    lambda: t1.execute(sql="SELECT COUNT(*) AS cnt FROM Customers"),
    check_count_199)

def check_readonly_guard(result):
    err = error_text(result)
    text = output_text(result)
    assert err or "拒绝" in text or "只读" in text or "SELECT" in text, \
        f"非 SELECT 语句必须被拒绝（fail_response 或明确提示），实际: {text[:200]}"

run("sales_sql_query", "只读守卫拒绝 DROP TABLE",
    lambda: t1.execute(sql="DROP TABLE Customers"),
    check_readonly_guard)

# ============ 工具 2：sales_stats ============
t2 = SalesStats()

def check_monthly_json(result):
    text = output_text(result)
    assert text.strip(), "monthly 分析输出为空"
    try:
        json.loads(text)
    except json.JSONDecodeError:
        raise AssertionError(f"输出应是合法 JSON（模型要直接引用），实际: {text[:200]}")

run("sales_stats", "monthly 返回合法 JSON",
    lambda: t2.execute(analysis_type="monthly"),
    check_monthly_json)

def check_invalid_enum(result):
    err = error_text(result) or ""
    text = output_text(result)
    combined = err + text
    assert "monthly" in combined, \
        f"非法 analysis_type 应报错并回显合法值列表（含 monthly），实际: {combined[:200]}"

run("sales_stats", "非法枚举值报错并回显合法值",
    lambda: t2.execute(analysis_type="不存在的类型"),
    check_invalid_enum)

# ============ 工具 3：plot_chart ============
t3 = PlotChart()
SAMPLE_DATA = json.dumps([
    {"month": "2024-01", "sales": 66304},
    {"month": "2024-02", "sales": 67973},
    {"month": "2024-03", "sales": 71250},
], ensure_ascii=False)

def check_chart_html(result):
    text = output_text(result)
    path = find_html_path(text)
    assert path, f"输出里应包含生成的 .html 文件路径，实际: {text[:200]}"
    assert os.path.exists(path), f"返回的图表文件不存在: {path}"

run("plot_chart", "bar 图生成 HTML 文件且路径存在",
    lambda: t3.execute(data_json=SAMPLE_DATA, chart_type="bar", title="月度销售额", x="month", y="sales"),
    check_chart_html)

def check_bad_column(result):
    err = error_text(result) or ""
    combined = err + output_text(result)
    assert err or "列" in combined or "month" in combined, \
        f"x/y 列不存在时应报错并回显实际列名，实际: {combined[:200]}"

run("plot_chart", "不存在的列名报错回显",
    lambda: t3.execute(data_json=SAMPLE_DATA, chart_type="bar", title="t", x="不存在的列", y="sales"),
    check_bad_column)

# ============ 工具 4：report_generator ============
t4 = ReportGenerator()

def check_report_html(result):
    text = output_text(result)
    path = find_html_path(text)
    assert path, f"输出里应包含报告 .html 路径，实际: {text[:200]}"
    assert os.path.exists(path), f"返回的报告文件不存在: {path}"

run("report_generator", "最小报告生成且路径存在",
    lambda: t4.execute(title="测试报告", sections=[{"heading": "结论", "content": "月度销售额稳中有升"}]),
    check_report_html)

def check_empty_sections(result):
    err = error_text(result)
    assert err or "空" in output_text(result), "sections 为空时应 fail_response，不应静默生成空报告"

run("report_generator", "空 sections 被拒绝",
    lambda: t4.execute(title="t", sections=[]),
    check_empty_sections)

# ============ 汇总 ============
print("\n" + "=" * 62)
print("W2 工具自测结果")
print("=" * 62)
icons = {"PASS": "[OK]  ", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}
for tool, case, status, msg in RESULTS:
    print(f"{icons[status]} {tool} :: {case}")
    if msg and status == "FAIL":
        print(f"        └─ {msg}")
n_pass = sum(1 for r in RESULTS if r[2] == "PASS")
n_fail = sum(1 for r in RESULTS if r[2] == "FAIL")
n_skip = sum(1 for r in RESULTS if r[2] == "SKIP")
print("-" * 62)
print(f"PASS {n_pass} / FAIL {n_fail} / SKIP {n_skip}（共 {len(RESULTS)} 用例）")
if n_skip:
    print("提示：SKIP = 该工具还是空骨架，写完 execute() 再跑一次")
if n_fail == 0 and n_skip == 0:
    print(">>> 四个工具全部就绪，可以接通 EcommerceAgent 跑端到端 MVP 了")
sys.exit(1 if n_fail else 0)
