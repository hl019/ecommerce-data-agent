# -*- coding: utf-8 -*-
"""
语料入库脚本 ingest_corpus —— 切块→向量化→存库（跑一次，改了语料再跑）

★ 仓库正身（改这个）：
    D:\\projects\\ecommerce-data-agent\\scripts\\w3_setup\\ingest_corpus.py
（此脚本在仓库里直接跑，不需要 sync 进 OpenManus——它不 import app 包）

用法（语料按《ZCode-W3-语料建立.md》落盘后）：
    D:\\projects\\OpenManus\\.venv\\Scripts\\python.exe D:\\projects\\ecommerce-data-agent\\scripts\\w3_setup\\ingest_corpus.py
先 $env:ZHIPU_API_KEY = "sk-..."（key 只走环境变量）

红线同工具：核心逻辑学生亲手写。骨架只给步骤骨架 + 线索。
"""
import os

RAW_DIR = r"D:\projects\knowledge\raw"          # 语料源（仓库外，版权策略见语料文档）
KB_DIR = r"D:\projects\knowledge\ecom_kb"       # chromadb 持久化目录
COLLECTION = "ecom_kb"
EMBED_MODEL = "embedding-3"                     # 换这行任何值 = 必须重建整个库（向量与模型绑定！）


def chunk_document(text):
    """
    TODO(学生)：把一篇文档切成块，返回 list[dict{正文, 块标题}]
    线索：按行扫，遇标题行（如以【或#或行首无标点的短行）开新块；
    目标块长 300-500 字、块间重叠 ~50 字；标题行本身要进块（它是检索上下文）。
    验收题「为什么这么切」的答案就藏在你调参的过程里——留一条笔记记下你试过什么、为什么定这组数。
    """
    raise NotImplementedError("切块还没写")


def main():
    """
    TODO(学生)：主流程五步（对照《ZCode-W3-语料建立.md》第4节的四元组）——
    1) 遍历 RAW_DIR 下 *.txt，从文件头部固定格式里解析 来源URL/抓取日期/收录理由（格式见语料文档）
       （URL 口径小项：MANIFEST 里百分号编码/中文原样混用，解析时 urllib.parse.unquote 归一再入库）
    2) 每篇过 chunk_document 得块列表
    3) 全部块调智谱 embedding-3（批量，写法从 lab03 步骤2 搬）
    4) chromadb PersistentClient(KB_DIR).get_or_create_collection(COLLECTION)
       → upsert(ids=稳定的 f"{文件名}#{块号}", embeddings, documents, metadatas=四元组+标题)
    5) 打印：文件数 / 块数 / 平均块长（这就是你的第一份分块体检报告）
    错误处理自查：空文件跳过并警告？API 失败重试一次？id 撞车（重跑）会不会脏数据？——upsert 是答案提示
    """
    raise NotImplementedError("主流程还没写——按五步来，写完跑一次，看第5步的体检数字")


if __name__ == "__main__":
    main()
