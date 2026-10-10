# -*- coding: utf-8 -*-
"""
语料入库脚本 ingest_corpus —— 切块→向量化→存库（跑一次，改了语料再跑）

★ 仓库正身（改这个）：
    D:\\projects\\ecommerce-data-agent\\scripts\\w3_setup\\ingest_corpus.py
（此脚本在仓库里直接跑，不需要 sync 进 OpenManus——它不 import app 包）

用法（语料按《ZCode-W3-语料建立.md》落盘后）：
    D:\\projects\\OpenManus\\.venv\\Scripts\\python.exe D:\\projects\\ecommerce-data-agent\\scripts\\w3_setup\\ingest_corpus.py
先 $env:ZHIPU_API_KEY = "sk-..."（key 只走环境变量）

★ 重跑方式（考核官§六确认口径）：本脚本设计为【全量扫描 → 幂等重建】——
  语料目录以后加新文件（如 ecom-metrics 三篇），**重跑一次即可**，不产生重复块/脏数据
  （幂等靠什么实现，见 main 第 4 步提示；跑两次然后数块数，自己验证）。
扫描范围 = RAW_DIR 下所有子目录递归：kingdee\\(5篇) + ecom-sop\\(干扰项) + ecom-metrics\\(闭环后新增3篇)

红线同工具：核心逻辑学生亲手写。骨架只给步骤骨架 + 线索。
"""
import os
import re
import time
import glob
import urllib.parse
import requests
import chromadb

RAW_DIR = r"D:\projects\knowledge\raw"          # 语料源（仓库外，版权策略见语料文档）
KB_DIR = r"D:\projects\knowledge\ecom_kb"       # chromadb 持久化目录
COLLECTION = "ecom_kb"
EMBED_MODEL = "embedding-3"                     # 换这行任何值 = 必须重建整个库（向量与模型绑定！）
ZHIPU_KEY = os.environ.get("ZHIPU_API_KEY", "")  # key 只从环境变量来，绝不写进文件


# ══════════════ 切块 ══════════════

def is_heading(line, max_len=20):
    """判断一行是不是标题：短 + 不以标点结尾"""
    line = line.strip()
    if not line or len(line) > max_len:
        return False
    # 结尾是标点 → 这是一句话，不是标题
    if line[-1] in "，。；：、！？,.;:!?":
        return False
    return True


def chunk_document(text, min_len=200, max_len=600, overlap=50):
    """
    把一篇文档切成块，返回 list[dict{"正文", "块标题", "块号"}]

    规则（1010 修复版·治"碎块"）：
      标题**不再立即切块**——它只更新"当前块标题"，内容继续攒；
      攒到 min_len 之后遇到**新标题**才切（保证每块有完整内容，不产生"只有标题的空块"）；
      攒到 max_len 硬切（防御超长段落），切缝留 overlap 重叠。
    """
    chunks = []
    cur_title = "开头"      # 当前块的标题
    cur_lines = []          # 当前块攒的行
    cur_len = 0             # 当前块的字数

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # ── 遇到标题：不立即切！只更新标题，内容接着攒 ──
        if is_heading(line):
            # 只有"当前块已经攒够 min_len"时才把旧块封存、开新块
            if cur_len >= min_len:
                chunks.append({"正文": "\n".join(cur_lines), "块标题": cur_title})
                cur_lines = []
                cur_len = 0
            cur_title = line
            # 关键：即使不切块，也要把标题写进正文，它是检索上下文
            cur_lines.append(line)
            cur_len += len(line)
            continue

        # ── 普通行：攒进当前块 ──
        cur_lines.append(line)
        cur_len += len(line)

        # ── 超过 max_len（比如某段超长没有任何标题）→ 硬切，留重叠 ──
        if cur_len > max_len:
            chunks.append({"正文": "\n".join(cur_lines), "块标题": cur_title})
            tail = "".join(cur_lines)[-overlap:]   # 尾巴 50 字
            cur_lines = [tail]                     # 抄到新块开头
            cur_len = len(tail)

    # 最后一块别忘吐出来
    if cur_lines:
        chunks.append({"正文": "\n".join(cur_lines), "块标题": cur_title})

    # 编号 + 合并"内容过少"的尾块（防止最后剩一个只有标题的碎片）
    if len(chunks) >= 2 and len(chunks[-1]["正文"]) < min_len // 2:
        chunks[-2]["正文"] += "\n" + chunks[-1]["正文"]
        chunks.pop()

    for i, c in enumerate(chunks):
        c["块号"] = i + 1

    return chunks


# ══════════════ 智谱 embedding ══════════════

def zhipu_embed(texts, retries=3):
    """调智谱 embedding-3，支持批量。写法从 lab03 步骤2 搬。
    texts: str 或 list[str]；返回 list[向量]"""
    if not ZHIPU_KEY:
        raise RuntimeError("环境变量 ZHIPU_API_KEY 未设！先跑：$env:ZHIPU_API_KEY = \"sk-...\"")
    if isinstance(texts, str):
        texts = [texts]

    last_err = None
    for attempt in range(retries):
        r = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/embeddings",
            headers={"Authorization": f"Bearer {ZHIPU_KEY}"},
            json={"model": EMBED_MODEL, "input": texts, "dimensions": 256},
            timeout=60,
        )
        if r.status_code == 200:
            return [d["embedding"] for d in r.json()["data"]]
        body = r.text[:300]
        biz = re.search(r'"code"\s*:\s*"?(\w+)"?', body)
        last_err = f"HTTP {r.status_code} 业务码 {biz and biz.group(1)}: {body[:120]}"
        print(f"  ✗ {last_err}")
        if r.status_code == 429 and attempt < retries - 1:
            wait = 2.0 * (attempt + 1)
            print(f"  …等 {wait}s 重试（1113/1308 类重试无用，看业务码定性）")
            time.sleep(wait)
            continue
        break
    raise RuntimeError(last_err)


# ══════════════ 解析文件头 ══════════════

def parse_header(text):
    """从文件头部解析 [来源URL]/[抓取日期]/[收录理由]，返回 (meta_dict, 正文)
    格式见语料文档：前三行 [key] value，第四行 ====== 正文开始 ======"""
    lines = text.splitlines()
    meta = {}
    body_start = 0
    for i, line in enumerate(lines):
        if "正文开始" in line:
            body_start = i + 1
            break
        m = re.match(r"\[(.+?)\]\s*(.*)", line.strip())
        if m:
            meta[m.group(1)] = m.group(2).strip()
    body = "\n".join(lines[body_start:])
    return meta, body


# ══════════════ 主流程 ══════════════

def main():
    # ── 第0步：前置检查 ──────────────────────────────
    if not ZHIPU_KEY:
        print("✗ 环境变量 ZHIPU_API_KEY 未设！先跑：$env:ZHIPU_API_KEY = \"sk-...\"")
        return

    # ── 第1步：遍历语料，解析头部 ─────────────────────
    files = sorted(glob.glob(os.path.join(RAW_DIR, "**", "*.txt"), recursive=True))
    print(f"发现 {len(files)} 个语料文件")

    all_chunks = []   # 每项：{正文, 块标题, 块号, 文件名, meta}
    for fp in files:
        fname = os.path.basename(fp)
        with open(fp, encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        if not raw.strip():
            print(f"  ⚠ 跳过空文件：{fname}")
            continue
        meta, body = parse_header(raw)
        if not body.strip():
            print(f"  ⚠ 跳过（正文为空）：{fname}")
            continue

        # ── 第2步：切块 ──────────────────────────────
        chunks = chunk_document(body)
        for c in chunks:
            c["文件名"] = fname
            c["meta"] = meta
            all_chunks.append(c)
        print(f"  ✓ {fname}：{len(chunks)} 块（meta: {list(meta.keys())}）")

    if not all_chunks:
        print("✗ 没有可入库的块，检查语料目录")
        return
    print(f"合计 {len(all_chunks)} 块")

    # ── 第3步：向量化（带间隔，防 429）──────────────
    print("开始向量化（每批间隔 0.6s，防限流）…")
    texts = [c["正文"] for c in all_chunks]
    vectors = []
    batch = 10
    for i in range(0, len(texts), batch):
        batch_texts = texts[i:i + batch]
        vectors.extend(zhipu_embed(batch_texts))
        print(f"  已向量化 {min(i + batch, len(texts))}/{len(texts)}")
        if i + batch < len(texts):
            time.sleep(0.6)

    # ── 第4步：入 chromadb（upsert = 幂等，重跑不重复）──
    client = chromadb.PersistentClient(path=KB_DIR)
    try:
        client.delete_collection(COLLECTION)      # 重跑时先清空，保证干净
    except Exception:
        pass
    col = client.get_or_create_collection(COLLECTION)

    ids, docs, metas = [], [], []
    for c in all_chunks:
        src = c["meta"].get("来源URL", "")
        src = urllib.parse.unquote(src)            # 百分号编码归一
        ids.append(f"{c['文件名']}#{c['块号']}")
        docs.append(c["正文"])
        metas.append({
            "source": c["文件名"],
            "title": c["块标题"],
            "url": src,
            "chunk_id": f"{c['文件名']}#{c['块号']}",
        })
    col.upsert(ids=ids, embeddings=vectors, documents=docs, metadatas=metas)

    # ── 第5步：体检报告 ────────────────────────────
    avg_len = sum(len(t) for t in texts) / len(texts)
    print("\n========== 入库体检报告 ==========")
    print(f"文件数：{len(files)}")
    print(f"块总数：{len(all_chunks)}")
    print(f"平均块长：{avg_len:.0f} 字")
    print(f"库内实存：{col.count()} 块（应与块总数一致）")
    print(f"持久化目录：{KB_DIR}")
    print("=================================")


if __name__ == "__main__":
    main()
