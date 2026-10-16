# -*- coding: utf-8 -*-
r"""
W4 最小 Web UI —— 给 EcommerceAgent 套一页浏览器界面

运行（同一终端窗口先设好环境变量）：
    $env:MYSQL_RO_PASSWORD = "只读账号密码"
    $env:ZHIPU_API_KEY = "你的key"
    D:\projects\OpenManus\.venv\Scripts\python.exe -m streamlit run D:\projects\ecommerce-data-agent\app\web\streamlit_app.py
"""
import asyncio
import glob
import os
import sys
import time

sys.path.insert(0, r"D:\projects\OpenManus")
os.chdir(r"D:\projects\OpenManus")

import streamlit as st

REPORTS_DIR = r"D:\projects\OpenManus\workspace\reports"

# 页面配置（必须是第一个 st.* 调用）
st.set_page_config(page_title="电商运营数据分析智能体", page_icon="📊", layout="centered")

st.title("📊 电商运营数据分析智能体")
st.caption("用一句话描述你的业务问题，Agent 会自动查数据、画图表、生成分析报告。")
st.caption("💡 试试这样问：`分析月度销售趋势并生成报告` ｜ `哪些商品卖得最好` ｜ `用户复购情况如何` ｜ `库存商品不可销售怎么设置`")

# ── I3 配套：把结果存进 session_state ──
# Streamlit 每次交互都会把整个脚本重跑一遍。不存的话，点"下载报告"
# 会触发重跑 → run_clicked 变 False → 结果区立刻消失。
for _k in ("answer", "result_raw", "report_path"):
    if _k not in st.session_state:
        st.session_state[_k] = ""

question = st.text_input("业务问题", placeholder="例如：分析月度销售趋势并生成报告", key="q")
run_clicked = st.button("生成报告", type="primary")

if run_clicked and question.strip():
    from app.agent.ecommerce import EcommerceAgent

    # ── I1 修复：记录任务开始时间 ──
    # 只认"本次任务生成"的报告。否则问口径类问题时（本就不出报告），
    # 页面会误显示文件夹里遗留的旧报告，误导使用者。
    task_start = time.time()

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

    # I1：只取本次任务生成的报告（文件修改时间晚于任务开始）
    all_reports = glob.glob(os.path.join(REPORTS_DIR, "*.html"))
    fresh = [p for p in all_reports if os.path.getmtime(p) > task_start]
    latest = max(fresh, key=os.path.getmtime) if fresh else ""

    st.session_state.answer = answer or result
    st.session_state.result_raw = result
    st.session_state.report_path = latest

# ── 渲染区（每次重跑都从 session_state 读，结果不会因交互丢失）──
if st.session_state.answer:
    st.subheader("分析回答")
    st.markdown(st.session_state.answer)

    if st.session_state.report_path:
        latest = st.session_state.report_path
        name = os.path.basename(latest)
        st.success(f"报告已生成：{name}")

        # ── I3 修复：直接下载 ──
        # 原来的 file:// 链接会被 Chrome 从 http 页面拦截（跨协议导航），
        # 下载按钮绕开这个限制。
        try:
            with open(latest, encoding="utf-8") as f:
                html = f.read()
            st.download_button("⬇️ 下载报告（HTML）", html, file_name=name, mime="text/html")
        except Exception as e:
            st.caption(f"（报告读取失败：{e}）")

        st.caption("💡 也可复制此路径到浏览器地址栏打开："
                   f"`file:///{latest.replace(chr(92), '/')}`")
    else:
        st.info("本次任务未生成报告——口径/知识类问题只输出带出处的回答（不生成数据分析报告）。")

    with st.expander("查看 Agent 执行过程（原始输出）"):
        st.text(st.session_state.result_raw)
