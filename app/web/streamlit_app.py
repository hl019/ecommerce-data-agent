# -*- coding: utf-8 -*-
r"""
W4 最小 Web UI —— 给 EcommerceAgent 套一页浏览器界面

运行（同一终端窗口先设好环境变量）：
    $env:MYSQL_RO_PASSWORD = "<只读账号密码>"
    $env:ZHIPU_API_KEY = "你的key"
    D:\projects\OpenManus\.venv\Scripts\python.exe -m streamlit run D:\projects\ecommerce-data-agent\app\web\streamlit_app.py
"""
import asyncio
import glob
import os
import re
import sys

# OpenManus 根目录：默认演示机路径，换环境用 OPENMANUS_HOME 覆盖
OPENMANUS_HOME = os.environ.get("OPENMANUS_HOME", r"D:\projects\OpenManus")
sys.path.insert(0, OPENMANUS_HOME)
os.chdir(OPENMANUS_HOME)

REPORTS_DIR = os.path.join(OPENMANUS_HOME, "workspace", "reports")

import streamlit as st


def extract_steps(messages):
    """从 Agent 记忆回放执行步骤。

    配对逻辑：assistant 消息里的 tool_calls（模型"下单"）↔ 随后 role=tool 的结果消息。
    这样能把一坨 "Step 1: ..." 的原始文本，还原成"思考 → 调工具 → 看结果"的可读时间线。
    """
    steps, pending = [], {}
    for m in messages:
        role = getattr(m, "role", "")
        if role == "assistant" and getattr(m, "tool_calls", None):
            for tc in m.tool_calls:
                fn = getattr(tc, "function", None)
                step = {
                    "name": getattr(fn, "name", "?"),
                    "args": getattr(fn, "arguments", "") or "",
                    "thought": (m.content or "").strip(),
                    "result": "",
                }
                steps.append(step)
                pending[getattr(tc, "id", "")] = step
        elif role == "tool":
            cid = getattr(m, "tool_call_id", "")
            if cid in pending:
                text = (m.content or "").strip()
                # 去掉框架加的技术前缀，只留工具真正返回的内容
                text = re.sub(r"^Observed output of cmd\s*`[^`]*`\s*executed:\s*", "", text)
                pending[cid]["result"] = text[:800]
    return steps


# 页面配置（必须是第一个 st.* 调用）
st.set_page_config(page_title="电商运营数据分析智能体", page_icon="📊", layout="centered")

st.title("📊 电商运营数据分析智能体")
st.caption("用一句话描述你的业务问题，Agent 会自动查数据、画图表、生成分析报告。")
st.caption("💡 试试这样问：`分析月度销售趋势并生成报告` ｜ `哪些商品卖得最好` ｜ `用户复购情况如何` ｜ `库存商品不可销售怎么设置`")

# ── 结果存进 session_state ──
# Streamlit 每次交互都会把整个脚本重跑一遍。不存的话，点"下载报告"
# 会触发重跑 → run_clicked 变 False → 结果区立刻消失。
for _k, _default in (("answer", ""), ("result_raw", ""), ("report_path", ""), ("steps", [])):
    if _k not in st.session_state:
        st.session_state[_k] = _default

question = st.text_input("业务问题", placeholder="输入你的业务问题…", key="q")
run_clicked = st.button("生成报告", type="primary")

if run_clicked and question.strip():
    from app.agent.ecommerce import EcommerceAgent

    # ── I1（差集法）：不依赖时钟 ──
    # 跑之前记下已有报告集合，跑完取差集 = 本次新生成的。
    before = set(glob.glob(os.path.join(REPORTS_DIR, "*.html")))

    agent = EcommerceAgent()
    with st.spinner("Agent 正在查数、画图、写报告……（约 1-2 分钟）"):
        result = asyncio.run(agent.run(question))

    # 最终回答：run() 返回的是各步骤拼接（含工具原始输出），
    # 从 Agent 记忆里倒查最后一条 assistant 消息 = 模型真正组织的回答
    answer = ""
    try:
        for m in reversed(agent.memory.messages):
            if getattr(m, "role", "") == "assistant" and getattr(m, "content", None):
                answer = m.content
                break
    except Exception:
        pass

    # I1：差集 = 本次新生成的报告（口径类问题本就不出报告 → 差集为空 → UI 如实说明）
    new_reports = [p for p in glob.glob(os.path.join(REPORTS_DIR, "*.html")) if p not in before]
    latest = max(new_reports, key=os.path.getmtime) if new_reports else ""

    st.session_state.answer = answer or result
    st.session_state.result_raw = result
    st.session_state.report_path = latest
    st.session_state.steps = extract_steps(agent.memory.messages)

# ── 渲染区（每次重跑都从 session_state 读，结果不会因交互丢失）──
if st.session_state.answer:
    st.subheader("分析回答")
    st.markdown(st.session_state.answer)

    if st.session_state.report_path:
        latest = st.session_state.report_path
        name = os.path.basename(latest)
        st.success(f"报告已生成：{name}")

        # ── I3：直接下载 ──
        # 原来的 file:// 链接会被 Chrome 从 http 页面拦截（跨协议导航），
        # 下载按钮绕开这个限制。
        try:
            with open(latest, "rb") as f:   # bytes 模式：避免编码边角
                st.download_button("⬇️ 下载报告（HTML）", f.read(), file_name=name, mime="text/html")
        except Exception as e:
            st.caption(f"（报告读取失败：{e}）")

        st.caption("💡 也可复制此路径到浏览器地址栏打开："
                   f"`file:///{latest.replace(chr(92), '/')}`")
    else:
        st.info("本次任务未生成报告——口径/知识类问题只输出带出处的回答（不生成数据分析报告）。")

    # ── P2：执行过程时间线（把"黑盒"变成"可观测"）──
    steps = st.session_state.steps or []
    if steps:
        st.subheader("🔍 Agent 执行过程")
        st.caption(f"本次共 **{len(steps)} 步**（ReAct 循环：思考 → 调工具 → 看结果 → 再思考）")
        for i, s in enumerate(steps, 1):
            with st.expander(f"步骤 {i} · `{s['name']}`", expanded=(i == 1)):
                if s["thought"]:
                    st.markdown(f"**💭 思考**：{s['thought']}")
                if s["args"]:
                    st.markdown("**🔧 调用参数**")
                    st.code(s["args"][:600], language="json")
                if s["result"]:
                    st.markdown("**📄 工具返回**")
                    st.text(s["result"][:600])

    with st.expander("查看原始输出（技术细节）"):
        st.text(st.session_state.result_raw)
