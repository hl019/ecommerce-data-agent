# ecommerce-data-agent · 电商运营数据智能体

> 一句业务问题（如"分析 7 月销售下滑原因"）→ Agent 自动任务分解 → SQL/Pandas 分析 → Plotly 图表 → HTML 运营报告。
> 基于 [OpenManus](https://github.com/FoundationAgents/OpenManus)（MIT 协议）二次开发，学习笔记参考 [ai-agent-interview-guide](https://github.com/bcefghj/ai-agent-interview-guide)。

## 项目状态：W3 RAG 已闭环，W4 进行中（更新于 2026-10-12）

> 最新里程碑：2026-10-12 RAG 知识检索闭环——9 篇真实公开文档 / 82 个知识块，Agent 回答口径类问题**带出处引用**，无关问题**如实拒答**（防幻觉实测）；Streamlit 网页 UI 跑通（一句话→回答+报告链接）。

| 周 | 里程碑 | 状态 |
|---|---|---|
| W1 | 环境搭建、首跑 ReAct 循环、核心源码精读、MySQL 数据环境、JD 调研 | ✅ 已完成（2026-09-25） |
| W2 | 自有工具层 4 件 + EcommerceAgent + 场景化提示词；MVP「一句话→自动出报告」 | ✅ 已完成（2026-10-06） |
| W3 | RAG 知识库（ingest 幂等入库 82 块 + kb_search 带出处检索 + 引用来源 + 防幻觉实测） | ✅ 已完成（2026-10-12） |
| W4 | Streamlit UI ✅ / README+架构图+演示视频 🚧 / customer_lookalike ML 工具 ⬜ |  进行中 |
| W5+ | 简历三版润色 + 模拟面试 + 投递 | ⬜ |

## Roadmap · 二次开发深度验收清单

- [ ] ≥ 4 个自有工具（function schema 与核心逻辑独立编写）
- [ ] 自建真实 RAG 知识库（全部文档来源可查，不使用 AI 生成内容充数）
- [ ] 针对电商分析场景重写系统提示词（`app/prompt/`）
- [ ] 架构图明确标注自有模块与 OpenManus 原生模块的边界

## 技术要点

ReAct 循环 · Function Calling · 只读 SQL 守卫 · Pandas 聚合分析 · Plotly 可视化 · HTML 报告生成 · RAG（分块/向量检索）· 会话记忆 · MCP 工具协议 · Docker 部署

## 文档

- [学习笔记索引](docs/learning/) —— 环境搭建、源码带读、工具设计、踩坑故事

## 数据说明

演示数据集为 1000 笔交易合成样本（CSV 与初始化脚本见 `scripts/w2_setup/`）。`sales_sql_query` 读 MySQL、`sales_stats` 读 CSV，两工具在 demo 阶段为**同源快照**（均由 `one_click_init.py` 从同一份 CSV 幂等重建，跑一次即同步）；生产化会收敛为单库单源。

## 运行产物说明

`workspace/charts/` 与 `workspace/reports/` 为 Agent 运行产物：每执行一次任务生成一套带时间戳的图表/报告文件（时间戳防互相覆盖），**不入库、可随时整体清空重跑**，不影响项目功能。clone 后按 `scripts/w2_setup/README.md` 初始化数据、填 `config/config.toml`，用 `python scripts/run_agent.py "你的业务问题"` 即可重新生成全套演示产物。

## 致谢与许可

核心框架来自 OpenManus（MIT），感谢原作者团队。本项目遵循 MIT 协议开源。
