#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量更新 pointsVEX.txt，将所有创建点的代码替换为使用辅助函数
"""

import re

# 读取文件
with open('pointsVEX.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义替换模式
# LOD0 点（voxel_scale = voxel_scale_lod0）
lod0_pattern = r'(\s+)int pt = addpoint\(0, voxel_center\);\s+setpointattrib\(0, "voxel_x", pt, x\);\s+setpointattrib\(0, "voxel_y", pt, y\);\s+setpointattrib\(0, "voxel_z", pt, z\);\s+setpointattrib\(0, "voxel_size", pt, voxel_size\);\s+setpointattrib\(0, "min_bound", pt, min_bound\);\s+setpointattrib\(0, "voxel_scale", pt, voxel_scale\);\s+setpointattrib\(0, "corner_val", pt, corner_val\);\s+setpointattrib\(0, "corner_pos", pt, corner_pos\);\s+float center_density = volumesample\(0, "density", voxel_center\);\s+setpointattrib\(0, "Cd", pt, set\(center_density, center_density, center_density\)\);'

# 需要根据上下文判断是 LOD0 还是 LOD1
# 先找到所有匹配的位置
matches = list(re.finditer(r'(\s+)int pt = addpoint\(0, voxel_center\);\s+setpointattrib\(0, "voxel_x", pt, x\);\s+setpointattrib\(0, "voxel_y", pt, y\);\s+setpointattrib\(0, "voxel_z", pt, z\);\s+setpointattrib\(0, "voxel_size", pt, voxel_size\);\s+setpointattrib\(0, "min_bound", pt, min_bound\);\s+setpointattrib\(0, "voxel_scale", pt, voxel_scale\);\s+setpointattrib\(0, "corner_val", pt, corner_val\);\s+setpointattrib\(0, "corner_pos", pt, corner_pos\);\s+float center_density = volumesample\(0, "density", voxel_center\);\s+setpointattrib\(0, "Cd", pt, set\(center_density, center_density, center_density\)\);', content))

# 从后往前替换，避免位置偏移
for match in reversed(matches):
    start, end = match.span()
    indent = match.group(1)
    
    # 检查上下文，判断是 LOD0 还是 LOD1
    # 向前查找 200 个字符，看是否有 voxel_scale_lod0 或 voxel_scale_lod1
    context_start = max(0, start - 200)
    context = content[context_start:start]
    
    if 'voxel_scale_lod0' in context or 'voxel_scale = voxel_scale_lod0' in context:
        # LOD0 点
        replacement = f'{indent}// 创建 LOD0 点（同时添加到 output 0 和 output 1）\n{indent}CreateLOD0Point(voxel_center, x, y, z, voxel_size, min_bound, voxel_scale,\n{indent}                   corner_pos, corner_val);'
    elif 'voxel_scale_lod1' in context or 'voxel_scale = voxel_scale_lod1' in context:
        # LOD1 点
        replacement = f'{indent}// 创建 LOD1 点（同时添加到 output 0 和 output 2）\n{indent}CreateLOD1Point(voxel_center, x, y, z, voxel_size, min_bound, voxel_scale,\n{indent}                   corner_pos, corner_val);'
    else:
        # 无法确定，保持原样（可能是 transition cell 或 boundary_lowres）
        continue
    
    content = content[:start] + replacement + content[end:]

# 写回文件
with open('pointsVEX.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print("更新完成！")

