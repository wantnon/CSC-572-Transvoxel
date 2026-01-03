#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 从 LOGLEngine/Headers/Transvoxel.h 提取 transitionCellData[56] 并写回 marchingCubesTablesWrangle.txt（VEX 版）

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


def parse_transition_cell_data(transvoxel_text: str) -> list[int]:
    # 抓取 transitionCellData[56] 的初始化块（不包含最外层的 { }）
    block = _extract_block(
        transvoxel_text,
        r"const\s+TransitionCellData\s+transitionCellData\s*\[\s*56\s*\]\s*=\s*\{",
        r"\};",
    )

    # 每个 entry 形如：{0x00, { ... }},
    # vertexIndex[36] 可能跨多行
    entry_re = re.compile(r"\{\s*(0x[0-9A-Fa-f]+|\d+)\s*,\s*\{([^}]*)\}\s*\}", re.S)
    entries = entry_re.findall(block)
    if len(entries) != 56:
        raise RuntimeError(f"transitionCellData 条目数量异常：{len(entries)}（应为 56）")

    flat: list[int] = []
    for geom_str, idx_blob in entries:
        geometry_counts = int(geom_str, 16) if geom_str.lower().startswith("0x") else int(geom_str)

        idx_blob = idx_blob.strip()
        if not idx_blob:
            indices: list[int] = []
        else:
            parts = [p.strip() for p in idx_blob.split(",") if p.strip()]
            indices = [int(p, 0) for p in parts]  # 支持 0x / 十进制

        # 36 个索引，不足补 -1，多余截断（理论上不会多）
        if len(indices) > 36:
            indices = indices[:36]
        indices += [-1] * (36 - len(indices))

        flat.append(geometry_counts)
        flat.extend(indices)

    if len(flat) != 56 * 37:
        raise RuntimeError(f"展开后的元素数量异常：{len(flat)}（应为 {56*37}）")
    return flat


def format_vex_int_array(name: str, data: list[int], items_per_line: int = 16) -> str:
    # 生成 VEX: int name[] = { ... };
    lines = [f"int {name}[] = {{"]
    for i in range(0, len(data), items_per_line):
        chunk = data[i : i + items_per_line]
        lines.append("    " + ", ".join(str(x) for x in chunk) + ("," if i + items_per_line < len(data) else ""))
    lines.append("};")
    return "\n".join(lines)


def update_tables_file(vex_text: str, new_array_block: str) -> str:
    # 更新注释行（如果存在旧注释）
    vex_text = re.sub(
        r"//\s*transitionCellData:.*\n//\s*格式.*\n",
        "// transitionCellData: 2072 个元素 (56 个类 * 37 个元素)\n// 格式: geometryCounts, 然后是 36 个顶点索引（不足用 -1 填充）\n",
        vex_text,
        count=1,
    )

    # 替换 int transitionCellData[] = { ... };
    pat = re.compile(r"int\s+transitionCellData\s*\[\]\s*=\s*\{[\s\S]*?\n\};", re.M)
    if not pat.search(vex_text):
        raise RuntimeError("在 marchingCubesTablesWrangle.txt 中未找到 transitionCellData 数组定义")
    vex_text = pat.sub(new_array_block, vex_text, count=1)
    return vex_text


def main() -> None:
    transvoxel_text = TRANSVOXEL_H.read_text(encoding="utf-8", errors="ignore")
    flat = parse_transition_cell_data(transvoxel_text)
    new_block = format_vex_int_array("transitionCellData", flat, items_per_line=16)

    vex_text = VEX_TABLES.read_text(encoding="utf-8", errors="ignore")
    updated = update_tables_file(vex_text, new_block)
    VEX_TABLES.write_text(updated, encoding="utf-8")
    print("OK: 已更新 marchingCubesTablesWrangle.txt 的 transitionCellData（56*37）")


if __name__ == "__main__":
    main()


