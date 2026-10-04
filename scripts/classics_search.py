# -*- coding: utf-8 -*-
"""
classics_search.py — 技能内嵌的经典文本向量库检索入口。

检索马恩全集与习近平谈治国理政向量库，作为 EMARX / MarxDoctorPaper 的
经典资料定位来源。向量库本体不在技能仓库内（体积约 900MB+），默认位于
本机 `D:\\BAOXUE\\classics-rag\\`，可用环境变量 CLASSICS_RAG_HOME 覆盖。

用法：
  python scripts/classics_search.py "精神生产" --db both --top-k 8
  python scripts/classics_search.py "宗教批判" --db marx --volume 3
  python scripts/classics_search.py --fetch marx 42 368
  python scripts/classics_search.py --info

依赖：chromadb==1.2.2、sentence-transformers（BAAI/bge-large-zh-v1.5）。
首次运行会自动进入技能 venv 并安装依赖。
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from emarx_env import ensure_venv_and_reexec

ensure_venv_and_reexec()

_RAG_HOME = os.environ.get("CLASSICS_RAG_HOME", r"D:\BAOXUE\classics-rag")
_MARX_DB = os.path.join(_RAG_HOME, "mega-rag", "chroma_db")
_XJP_DB = os.path.join(_RAG_HOME, "xjp-zglz", "chroma_db")
_MODEL_NAME = "BAAI/bge-large-zh-v1.5"
_QUERY_PREFIX = "为这个句子生成表示以用于检索相关段落: "

_model = None


def _ensure_utf8_stream():
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def load_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        t = time.time()
        print("[info] 加载嵌入模型...", file=sys.stderr)
        _model = SentenceTransformer(_MODEL_NAME, device="cpu")
        print(f"[info] 模型就绪（{time.time() - t:.1f}s）", file=sys.stderr)
    return _model


def get_collection(db_dir, name):
    import chromadb
    from chromadb.errors import NotFoundError
    if not os.path.isdir(db_dir):
        raise RuntimeError(
            f"向量库不存在: {db_dir}。"
            f"请确认经典文本库位于 CLASSICS_RAG_HOME（当前: {_RAG_HOME}），"
            "或先按 classics-vector-retrieval-protocol.md 部署数据库。"
        )
    client = chromadb.PersistentClient(path=db_dir)
    try:
        col = client.get_collection(name)
    except (ValueError, NotFoundError):
        raise RuntimeError(f"Collection '{name}' 不存在于 {db_dir}")
    if col.count() == 0:
        raise RuntimeError(f"Collection '{name}' 为空")
    return col


def search_marx(query, top_k, volume=None, min_score=0.0):
    model = load_model()
    col = get_collection(_MARX_DB, "marx_engels")
    vec = model.encode([_QUERY_PREFIX + query], normalize_embeddings=True)[0]
    where = {"volume": {"$eq": volume}} if volume else None
    raw = col.query(query_embeddings=[vec.tolist()],
                    n_results=min(top_k * 3, col.count()),
                    where=where, include=["metadatas", "distances"])
    hits, seen = [], set()
    for meta, dist in zip(raw["metadatas"][0], raw["distances"][0]):
        vol, pn = meta.get("volume", ""), meta.get("page_number", 0)
        score = 1.0 - dist
        if score < min_score or (vol, pn) in seen:
            continue
        seen.add((vol, pn))
        hits.append({"db": "marx", "volume": vol, "page_number": pn,
                     "address": f"v{vol} p{pn}", "score": round(score, 4)})
    hits.sort(key=lambda r: r["score"], reverse=True)
    return hits[:top_k]


def search_xjp(query, top_k, min_score=0.0):
    model = load_model()
    col = get_collection(_XJP_DB, "xjp_zglz")
    vec = model.encode([_QUERY_PREFIX + query], normalize_embeddings=True)[0]
    raw = col.query(query_embeddings=[vec.tolist()],
                    n_results=min(top_k * 2, col.count()),
                    include=["metadatas", "distances", "documents"])
    hits = []
    for meta, dist, doc in zip(raw["metadatas"][0], raw["distances"][0], raw["documents"][0]):
        score = 1.0 - dist
        if score < min_score:
            continue
        vol_label = meta.get("volume_label", "")
        chapter = meta.get("chapter", "")
        ps, pe = meta.get("page_start", 0), meta.get("page_end", 0)
        page_part = f" p{ps}-{pe}" if ps else ""
        hits.append({
            "db": "xjp",
            "volume_label": vol_label,
            "chapter": chapter,
            "address": f"{vol_label}{('《' + chapter + '》') if chapter else ''}{page_part}",
            "score": round(score, 4),
            "text": doc,
        })
    hits.sort(key=lambda r: r["score"], reverse=True)
    return hits[:top_k]


def fetch_marx(volume, pages):
    col = get_collection(_MARX_DB, "marx_engels")
    out = []
    for pn in pages:
        raw = col.get(where={"$and": [{"volume": {"$eq": volume}},
                                      {"page_number": {"$eq": pn}}]},
                      include=["documents", "metadatas"])
        for doc, meta in zip(raw.get("documents", []), raw.get("metadatas", [])):
            out.append({"db": "marx", "address": f"v{volume} p{pn}",
                        "volume_label": meta.get("volume_label", f"第{volume}卷"),
                        "text": doc})
    return out


def info():
    import chromadb
    result = {"rag_home": _RAG_HOME}
    for name, path, col_name in [("marx", _MARX_DB, "marx_engels"), ("xjp", _XJP_DB, "xjp_zglz")]:
        if not os.path.isdir(path):
            result[name] = {"exists": False, "path": path}
            continue
        client = chromadb.PersistentClient(path=path)
        try:
            col = client.get_collection(col_name)
            result[name] = {"exists": True, "count": col.count(), "path": path}
        except Exception:
            result[name] = {"exists": True, "count": 0, "path": path, "note": "collection 缺失"}
    return result


def main():
    _ensure_utf8_stream()
    ap = argparse.ArgumentParser(description="经典文本向量库统一检索（技能内嵌版）")
    ap.add_argument("query", nargs="?", help="查询文本")
    ap.add_argument("--db", choices=["marx", "xjp", "both"], default="both")
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--volume", type=str, default=None, help="限定马恩卷次")
    ap.add_argument("--min-score", type=float, default=0.0)
    ap.add_argument("--fetch", nargs="+", metavar=("DB", "VOL"), help="取原文：--fetch marx 42 368 369")
    ap.add_argument("--info", action="store_true")
    args = ap.parse_args()

    if args.info:
        print(json.dumps(info(), ensure_ascii=False, indent=2))
        return

    if args.fetch:
        if args.fetch[0] != "marx":
            print("目前仅支持 --fetch marx", file=sys.stderr)
            sys.exit(1)
        vol = args.fetch[1]
        pages = [int(p) for p in args.fetch[2:]]
        print(json.dumps(fetch_marx(vol, pages), ensure_ascii=False, indent=2))
        return

    if not args.query:
        ap.print_help()
        sys.exit(1)

    t = time.time()
    results = []
    if args.db in ("marx", "both"):
        results += search_marx(args.query, args.top_k, args.volume, args.min_score)
    if args.db in ("xjp", "both"):
        results += search_xjp(args.query, args.top_k, args.min_score)
    results.sort(key=lambda r: r["score"], reverse=True)
    print(f"[用时 {time.time() - t:.1f}s]", file=sys.stderr)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
