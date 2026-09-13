# ecommerce-data-agent · 电商运营数据智能体

> 一句业务问题（如"分析 7 月销售下滑原因"）→ Agent 自动任务分解 → SQL/Pandas 分析 → Plotly 图表 → HTML 运营报告。
> 基于 [OpenManus](https://github.com/FoundationAgents/OpenManus)（MIT 协议）二次开发，学习笔记参考 [ai-agent-interview-guide](https://github.com/bcefghj/ai-agent-interview-guide)。

## 项目状态：W1 环境与学习阶段

| 周 | 里程碑 | 状态 |
|---|---|---|
| W1 | 环境搭建、首跑 ReAct 循环、核心源码精读、踩坑记录 | 🚧 进行中 |
| W2 | 自有工具层：SQL 查询 / Pandas 统计 / Plotly 绘图 / 报告生成（schema 与核心逻辑手写） | ⬜ |
| W3 | RAG：真实文档知识库（金蝶公开文档 + 公开电商 SOP）+ 会话记忆 | ⬜ |
| W4 | Streamlit UI + Docker 部署 + 演示 | ⬜ |

## Roadmap · 二次开发深度验收清单

- [ ] ≥ 4 个自有工具（function schema 与核心逻辑独立编写）
- [ ] 自建真实 RAG 知识库（全部文档来源可查，不使用 AI 生成内容充数）
- [ ] 针对电商分析场景重写系统提示词（`app/prompt/`）
- [ ] 架构图明确标注自有模块与 OpenManus 原生模块的边界

## 技术要点

ReAct 循环 · Function Calling · RAG（分块/向量检索）· 会话记忆 · MCP 工具协议 · Docker 部署

## 文档

- [学习笔记索引](docs/learning/) —— 环境搭建、源码带读、工具设计、踩坑故事

## 致谢与许可

核心框架来自 OpenManus（MIT），感谢原作者团队。本项目遵循 MIT 协议开源。
