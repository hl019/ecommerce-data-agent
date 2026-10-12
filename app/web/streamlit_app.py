# -*- coding: utf-8 -*-
r"""
W4 最小 Web UI —— 给 EcommerceAgent 套一页浏览器界面

运行（先设环境变量，再启动）：
    $env:MYSQL_PASSWORD = "你的密码"
    $env:ZHIPU_API_KEY = "你的key"
    D:\projects\OpenManus\.venv\Scripts\python.exe -m streamlit run D:\projects\ecommerce-data-agent\app\web\streamlit_app.py
"""
import asyncio
import glob
import os
import sys

sys.path.insert(0, r"D:\projects\OpenManus")
os.chdir(r"D:\projects\OpenManus")

import streamlit as st

# 页面配置（必须是第一个 st.* 调用）：改浏览器标签页的标题与图标
st.set_page_config(page_title="电商运营数据分析智能体", page_icon="📊", layout="centered")

# ── 填空 A：页面标题 + 一句话说明（给运营人员看，不写技术词）──
st.title("📊 电商运营数据分析智能体")
st.caption("用一句话描述你的业务问题，Agent 会自动查数据、画图表、生成分析报告。")
st.caption("💡 试试这样问：`分析月度销售趋势并生成报告` ｜ `哪些商品卖得最好` ｜ `用户复购情况如何` ｜ `库存商品不可销售怎么设置`")

# ── 填空 B：问题输入区 ──
question = st.text_input("业务问题", placeholder="例如：分析月度销售趋势并生成报告", key="q")
run_clicked = st.button("生成报告", type="primary")

# ── 填空 C：点击后跑 Agent ──
if run_clicked and question.strip():
    from app.agent.ecommerce import EcommerceAgent

    agent = EcommerceAgent()
    with st.spinner("Agent 正在查数、画图、写报告……（约 1-2 分钟）"):
        result = asyncio.run(agent.run(question))

    # ── 填空 D-1：最终回答 ──
    # run() 返回的是"Step 1: 工具输出 / Step 2: ..."的拼接，太乱；
    # 改从 Agent 记忆里倒着找最后一条 assistant 消息 = 它真正写给你的回答
    answer = ""
    try:
        for m in reversed(agent.memory.messages):
            if getattr(m, "role", "") == "assistant" and getattr(m, "content", None):
                answer = m.content
                break
    except Exception:
        pass

    st.subheader("分析回答")
    st.markdown(answer or result)

    # ── 填空 D-2：报告文件（扫最新，别去 parse 字符串，更稳）──
    reports = glob.glob(r"D:\projects\OpenManus\workspace\reports\*.html")
    if reports:
        latest = max(reports, key=os.path.getmtime)
        file_url = "file:///" + latest.replace("\\", "/")
        st.success(f"报告已生成：{os.path.basename(latest)}")
        st.markdown(f"[📄 在新标签页打开报告]({file_url})")

    # 原始执行过程折叠起来（想看细节时展开）
    with st.expander("查看 Agent 执行过程（原始输出）"):
        st.text(result)
