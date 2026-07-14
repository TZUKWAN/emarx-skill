# -*- coding: utf-8 -*-
"""
emarx_bind_cnki_sources.py — 把 CNKI 文献绑定到 EMARX 论证功能。

CNKI 搜到的论文不会自动进正文。本工具生成一个 source-claim-map 模板，要求主模型为每篇候选文献明确：
- 功能（概念 / 机制 / 问题 / 材料 / 限制 / 反例）
- 支撑的具体判断
- 在正文中的使用位置
- 是否已回原文核实

只有绑定通过，该文献才能变成正文中的 [n]。

用法：
  python scripts/emarx_bind_cnki_sources.py \
    --sources workspace/sources.json \
    --outline workspace/outline.md \
    --output workspace/source-claim-map.json
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from emarx_env import ensure_venv_and_reexec
ensure_venv_and_reexec()


FUNCTIONS = ["概念", "机制", "问题", "材料", "限制", "反例"]


def load_sources(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    return data if isinstance(data, list) else data.get("sources", data.get("papers", []))


def generate_binding_template(sources: list[dict]) -> dict:
    """为每篇 CNKI 文献生成功能绑定模板。"""
    bindings = []
    for i, s in enumerate(sources, 1):
        bindings.append({
            "id": i,
            "title": s.get("title", ""),
            "authors": s.get("authors", ""),
            "source": s.get("source", ""),
            "year": s.get("year", ""),
            "gb_reference": s.get("gb_reference", ""),
            "abstract_url": s.get("abstract_url", s.get("url", "")),
            "origin": "cnki",
            "binding": {
                "function": "",  # 概念 / 机制 / 问题 / 材料 / 限制 / 反例
                "claim_supported": "",  # 支撑的具体判断
                "section": "",  # 使用位置：第几节第几段
                "verified_against_original": False,  # 是否已回原文核实
                "priority": "候选",  # 必引 / 候选 / 弃用
            },
        })

    return {
        "total": len(bindings),
        "instructions": "每篇文献必须绑定一个功能才能进入正文。'priority' 为'必引'的文献必须在正文中出现；'候选'表示可选；'弃用'表示不引用。",
        "functions": FUNCTIONS,
        "bindings": bindings,
    }


def main():
    parser = argparse.ArgumentParser(description="把 CNKI 文献绑定到 EMARX 论证功能")
    parser.add_argument("--sources", required=True, help="CNKI 文献池 JSON 路径")
    parser.add_argument("--outline", default=None, help="论文大纲文件（可选，用于提示使用位置）")
    parser.add_argument("--output", required=True, help="输出 source-claim-map.json 路径")
    args = parser.parse_args()

    sources_path = Path(args.sources)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sources = load_sources(sources_path)
    binding_map = generate_binding_template(sources)

    output_path.write_text(json.dumps(binding_map, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"文献功能绑定模板已生成：{output_path}")
    print(f"共 {binding_map['total']} 篇候选文献，请为每篇填写 function、claim_supported、section 和 priority")
    print(f"可选功能：{', '.join(FUNCTIONS)}")


if __name__ == "__main__":
    main()
