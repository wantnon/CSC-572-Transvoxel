#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 从 LOGLEngine/Headers/Transvoxel.h 提取 transitionCellClass[512] 并写回 marchingCubesTablesWrangle.txt（VEX 版）

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TRANSVOXEL_H = ROOT / "LOGLEngine" / "Headers" / "Transvoxel.h"
VEX_TABLES = ROOT / "marchingCubesTablesWrangle.txt"


def _extract_block(text: str, start_pat: str, end_pat: str) -> str:
    m = re.search(start_pat, text)
    if not m:
        raise RuntimeError(f"未找到起始标记: {start_pat}")
    start = m.end()
    m2 = re.search(end_pat, text[start:])
    if not m2:
        raise RuntimeError(f"未找到结束标记: {end_pat}")
    end = start + m2.start()
    return text[start:end]


def parse_transition_cell_class(transvoxel_text: str) -> list[int]:
    block = _extract_block(
        transvoxel_text,
        r"const\s+unsigned\s+char\s+transitionCellClass\s*\[\s*512\s*\]\s*=\s*\{",
        r"\};",
    )
    # 去掉注释后抓取所有数（支持 0x.. 与十进制）
    block = re.sub(r"//.*", "", block)
    nums = re.findall(r"0x[0-9A-Fa-f]+|\d+", block)
    vals = [int(s, 0) for s in nums]
    if len(vals) != 512:
        raise RuntimeError(f"transitionCellClass 数量异常：{len(vals)}（应为 512）")
    return vals


def format_vex_int_array(name: str, data: list[int], items_per_line: int = 16) -> str:
    lines = [f"int {name}[] = {{"]
    for i in range(0, len(data), items_per_line):
        chunk = data[i : i + items_per_line]
        lines.append("    " + ", ".join(hex(x) for x in chunk) + ("," if i + items_per_line < len(data) else ""))
    lines.append("};")
    return "\n".join(lines)


def update_tables_file(vex_text: str, new_array_block: str) -> str:
    pat = re.compile(r"int\s+transitionCellClass\s*\[\]\s*=\s*\{[\s\S]*?\n\};", re.M)
    if not pat.search(vex_text):
        raise RuntimeError("在 marchingCubesTablesWrangle.txt 中未找到 transitionCellClass 数组定义")
    return pat.sub(new_array_block, vex_text, count=1)


def main() -> None:
    transvoxel_text = TRANSVOXEL_H.read_text(encoding="utf-8", errors="ignore")
    vals = parse_transition_cell_class(transvoxel_text)
    new_block = format_vex_int_array("transitionCellClass", vals, items_per_line=16)

    vex_text = VEX_TABLES.read_text(encoding="utf-8", errors="ignore")
    updated = update_tables_file(vex_text, new_block)
    VEX_TABLES.write_text(updated, encoding="utf-8")
    print("OK: 已更新 marchingCubesTablesWrangle.txt 的 transitionCellClass（512）")


if __name__ == "__main__":
    main()


