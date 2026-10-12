# -*- coding: utf-8 -*-
"""
W4 最小 Web UI —— 给 EcommerceAgent 套一页浏览器界面（填空式骨架，A级）

运行（别直接 python 跑！streamlit 有自己的启动器）：
    双击 D:\\projects\\ecommerce-data-agent\\scripts\\w4_setup\\启动网页.bat
或命令行：
    D:\\projects\\OpenManus\\.venv\\Scripts\\python.exe -m streamlit run D:\\projects\\ecommerce-data-agent\\app\\web\\streamlit_app.py

★ 改这个（仓库正身）：
    D:\\projects\\ecommerce-data-agent\\app\\web\\streamlit_app.py
（本文件不 sync 进 OpenManus——它不属于底座包，从仓库直接运行，靠下面的 sys.path 找 app 包）

预习包：D:\\projects\\review\\ZCode-W4预习包-Streamlit最小UI.md
A级判断依据：本页全是 API 拼装（输入框/按钮/展示），无边界条件算法；
两个坑位已在填空里点名：①async 调用 ②报告怎么显示（别想成"重做一遍"，iframe 一行事）。
"""
import asyncio
import glob
import os
import sys

sys.path.insert(0, r"D:\projects\OpenManus")
os.chdir(r"D:\projects\OpenManus")

import streamlit as st

# ── 填空 A：页面标题 + 一句话说明 ──────────────────────
# 线索：st.title / st.caption
# 想一句给"运营人员"看的介绍，别写技术词——用户画像在 SYSTEM_PROMPT 里
st.title("")  # TODO(学生)

# ── 填空 B：问题输入区 ────────────────────────────────
# 线索：st.text_input(key=...) + st.button("生成报告")
# 引导问题：为什么 text_input 要带 key？（提示：填空 E 会用到它）
question = st.text_input("业务问题", placeholder="例如：分析月度销售趋势并生成报告", key="q")
run_clicked = st.button("生成报告", type="primary")

# ── 填空 C：点击后跑 Agent（本页最核心的一处）──────────
if run_clicked and question.strip():
    from app.agent.ecommerce import EcommerceAgent
    # 引导问题1：agent.run 是 async，streamlit 脚本是同步的——怎么桥接？（一行）
    # 引导问题2：跑一次要 1-2 分钟、烧几千 token，界面上什么都不显示像卡死了——用什么包住？
    #           （线索：st.spinner）
    with st.spinner("Agent 正在查数、画图、写报告……"):
        result = ""  # TODO(学生): asyncio.run(EcommerceAgent().run(question))
    # ── 填空 D：结果展示 ──
    # 1) Agent 的文字回答 → st.markdown(result)
    # 2) 报告文件 → 别去 parse result 里的路径字符串（脆弱）；
    #    直接扫最新报告：glob(r"D:\\projects\\OpenManus\\workspace\\reports\\*.html") 取 max(mtime)
    #    然后两行：st.html(f'<a href="file:///...">打开报告</a>') 或 st.components.v1.html(srcdoc=读文件内容, height=800) 内嵌显示
    #    引导问题：链接法和内嵌法各有什么毛病？（答上来就够面试用了）
    st.markdown(result)

# ── 填空 E（选做，10 分钟富余才碰）：会话状态 ──
# 现象：streamlit 每次交互整页重跑，上面的输入/结果会丢。
# 线索：st.session_state 存一个 messages 列表（问一句+答一句 append），
#       页面重跑时回放。做完你就理解了 streamlit 最反直觉的设计。
