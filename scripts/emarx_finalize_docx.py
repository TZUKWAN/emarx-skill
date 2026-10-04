# -*- coding: utf-8 -*-
"""
emarx_finalize_docx.py — EMARX Word 交付后处理脚本。

在 emarx_build_docx.py 生成 Word 之后执行，处理构建层解决不了的三件事：

  1. 批注清理：删除 word/comments*.xml 批注部件、document.xml 中的
     commentRangeStart/commentRangeEnd/commentReference，以及包内关系和内容类型声明；
  2. 修订标记接受：unwrap w:ins / w:moveTo（保留内容），删除 w:del / w:moveFrom
     （删除内容），清除 *PrChange 属性变更记录；
  3. 目录缓存写回（--update-toc）：用 Word/WPS COM 以可写方式打开、更新目录域并
     保存，使目录内容直接可见，不再依赖用户按 F9。

用法：
  python scripts/emarx_finalize_docx.py final.docx
  python scripts/emarx_finalize_docx.py final.docx --update-toc

默认原地修改，修改前在同目录创建 <文件名>.finalize.bak 备份。
"""
import argparse
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from emarx_env import ensure_venv_and_reexec

# 批注相关部件
COMMENT_PARTS = {
    "word/comments.xml",
    "word/commentsExtended.xml",
    "word/commentsIds.xml",
    "word/commentsExtensible.xml",
}

# document.xml 中的批注标记元素
COMMENT_MARK_RE = re.compile(
    r"<w:commentRangeStart[^>]*/>"
    r"|<w:commentRangeEnd[^>]*/>"
    r"|<w:r\b[^>]*>\s*<w:rPr>\s*<w:rStyle\s+w:val=\"[^\"]*[Cc]omment[^\"]*\"\s*/>\s*</w:rPr>\s*<w:commentReference[^>]*/>\s*</w:r>"
    r"|<w:commentReference[^>]*/>"
)

# 修订标记：ins/moveTo 保留内容（unwrap），del/moveFrom 整段删除
REVISION_UNWRAP_RES = [
    re.compile(r"<w:ins\b[^>]*>(.*?)</w:ins>", re.DOTALL),
    re.compile(r"<w:moveTo\b[^>]*>(.*?)</w:moveTo>", re.DOTALL),
]
REVISION_DELETE_RES = [
    re.compile(r"<w:del\b[^>]*>.*?</w:del>", re.DOTALL),
    re.compile(r"<w:moveFrom\b[^>]*>.*?</w:moveFrom>", re.DOTALL),
]
REVISION_PR_CHANGE_RE = re.compile(r"<w:\w*PrChange\b[^>]*>.*?</w:\w*PrChange>", re.DOTALL)

# 内容类型与关系中的批注声明
CT_COMMENT_RE = re.compile(r'<Override[^>]*PartName="/word/comments[^"]*"[^>]*/>')
REL_COMMENT_RE = re.compile(r'<Relationship[^>]*comments[^"]*"[^>]*/>')


def clean_package_xml(docx_path: Path) -> dict:
    """清理 DOCX 包内的批注和修订标记。返回统计。"""
    tmp_path = docx_path.with_suffix(".finalize.tmp")

    stats = {
        "comment_parts_removed": 0,
        "comment_marks_removed": 0,
        "revision_ins_unwrapped": 0,
        "revision_del_removed": 0,
    }

    with zipfile.ZipFile(docx_path, "r") as zin:
        names = zin.namelist()
        items = {name: zin.read(name) for name in names}

    # 1. 删除批注部件
    for part in COMMENT_PARTS:
        if part in items:
            del items[part]
            stats["comment_parts_removed"] += 1

    # 2. document.xml：批注标记 + 修订标记
    doc_name = "word/document.xml"
    if doc_name in items:
        xml = items[doc_name].decode("utf-8")

        xml, n = COMMENT_MARK_RE.subn("", xml)
        stats["comment_marks_removed"] += n

        for pattern in REVISION_UNWRAP_RES:
            xml, n = pattern.subn(r"\1", xml)
            stats["revision_ins_unwrapped"] += n
        for pattern in REVISION_DELETE_RES:
            xml, n = pattern.subn("", xml)
            stats["revision_del_removed"] += n
        xml = REVISION_PR_CHANGE_RE.sub("", xml)

        items[doc_name] = xml.encode("utf-8")

    # 3. [Content_Types].xml：批注声明
    ct_name = "[Content_Types].xml"
    if ct_name in items:
        xml = items[ct_name].decode("utf-8")
        xml = CT_COMMENT_RE.sub("", xml)
        items[ct_name] = xml.encode("utf-8")

    # 4. word/_rels/document.xml.rels：批注关系
    rels_name = "word/_rels/document.xml.rels"
    if rels_name in items:
        xml = items[rels_name].decode("utf-8")
        xml = REL_COMMENT_RE.sub("", xml)
        items[rels_name] = xml.encode("utf-8")

    # 写回（保持原压缩顺序之外的新顺序不影响 Word 打开）
    try:
        with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for name, data in items.items():
                zout.writestr(name, data)
    except PermissionError:
        raise RuntimeError(
            f"无法写入 {docx_path}：文件正被 Word/WPS 占用。请关闭后重试。"
        )

    tmp_path.replace(docx_path)
    return stats


def update_toc_via_word(docx_path: Path) -> dict:
    """用 Word/WPS COM 可写方式更新目录域并保存，把目录缓存写进 DOCX。

    复用规则与 renumber_footnotes_per_page.py 一致：优先复用已运行实例，
    没有则新建隐藏实例；仅新建实例才 Quit。
    """
    import win32com.client

    abs_path = os.path.abspath(str(docx_path))
    word = None
    created_by_us = False

    for progid in ("Word.Application", "Kwps.Application", "Wps.Application"):
        try:
            word = win32com.client.GetActiveObject(progid)
            if word is not None:
                break
        except Exception:
            continue

    if word is None:
        for progid in ("Word.Application", "Kwps.Application", "Wps.Application"):
            try:
                word = win32com.client.Dispatch(progid)
                word.Visible = False
                word.DisplayAlerts = False
                created_by_us = True
                break
            except Exception:
                continue

    if word is None:
        raise RuntimeError("无法启动 Word/WPS COM，目录缓存写回失败（可不加 --update-toc 跳过）")

    doc = None
    try:
        try:
            doc = word.Documents.Open(abs_path, ReadOnly=False)
        except Exception as e:
            raise RuntimeError(
                f"无法以可写方式打开 {docx_path}：{e}。"
                "若文件正在 Word/WPS 中打开，请先关闭再重试。"
            )

        toc_count = doc.TablesOfContents.Count
        for i in range(1, toc_count + 1):
            doc.TablesOfContents(i).Update()
        # 域全量更新一遍，兜底页码域
        doc.Fields.Update()
        doc.Save()
        return {"toc_fields_updated": toc_count}
    finally:
        if doc is not None:
            doc.Close(False)
        if created_by_us:
            word.Quit()


def verify_package(docx_path: Path) -> dict:
    """验证清理结果：批注部件、批注标记、修订标记均应归零。"""
    with zipfile.ZipFile(docx_path, "r") as z:
        names = set(z.namelist())
        xml = z.read("word/document.xml").decode("utf-8")

    remaining_parts = sorted(names & COMMENT_PARTS)
    return {
        "comment_parts_remaining": remaining_parts,
        "comment_marks_remaining": len(COMMENT_MARK_RE.findall(xml)),
        "revision_ins_remaining": len(re.findall(r"<w:ins\b", xml)),
        "revision_del_remaining": len(re.findall(r"<w:del\b", xml)),
        "clean": (not remaining_parts
                  and not COMMENT_MARK_RE.findall(xml)
                  and "<w:ins " not in xml and "<w:del " not in xml),
    }


def main():
    ap = argparse.ArgumentParser(description="EMARX Word 交付后处理：批注清理 + 修订接受 + 目录缓存写回")
    ap.add_argument("docx", help="待处理的 docx 文件路径（原地修改）")
    ap.add_argument("--update-toc", action="store_true",
                    help="用 Word/WPS COM 更新目录域并保存，使目录打开即可见")
    ap.add_argument("--no-backup", action="store_true", help="不创建 .finalize.bak 备份")
    args = ap.parse_args()

    ensure_venv_and_reexec()

    docx_path = Path(args.docx).resolve()
    if not docx_path.exists():
        raise FileNotFoundError(f"找不到文件: {docx_path}")

    if not args.no_backup:
        backup = docx_path.with_suffix(docx_path.suffix + ".finalize.bak")
        shutil.copy2(docx_path, backup)
        print(f"备份: {backup}")

    print("步骤1: 清理批注部件与修订标记")
    stats = clean_package_xml(docx_path)
    print(f"  批注部件删除: {stats['comment_parts_removed']}")
    print(f"  批注标记删除: {stats['comment_marks_removed']}")
    print(f"  修订插入保留(unwrap): {stats['revision_ins_unwrapped']}")
    print(f"  修订删除移除: {stats['revision_del_removed']}")

    if args.update_toc:
        print("步骤2: 更新目录域并写回缓存（Word/WPS COM）")
        toc_stats = update_toc_via_word(docx_path)
        print(f"  目录域更新: {toc_stats['toc_fields_updated']}")
    else:
        print("步骤2: 跳过目录缓存写回（需要时加 --update-toc）")

    print("步骤3: 验证")
    verify = verify_package(docx_path)
    print(f"  批注部件残留: {len(verify['comment_parts_remaining'])}")
    print(f"  批注标记残留: {verify['comment_marks_remaining']}")
    print(f"  修订标记残留: ins={verify['revision_ins_remaining']} del={verify['revision_del_remaining']}")
    print(f"  结论: {'通过' if verify['clean'] else '未通过，请检查'}")

    print(f"\n完成: {docx_path}")


if __name__ == "__main__":
    main()
