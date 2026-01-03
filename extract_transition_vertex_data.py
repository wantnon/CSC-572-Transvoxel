#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 从 Transvoxel.h 提取 transitionVertexData 数组并转换为 VEX 格式

import re

# 读取文件
with open('LOGLEngine/Headers/Transvoxel.h', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 transitionVertexData 数组的开始和结束
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'const unsigned short transitionVertexData' in line:
        start_line = i + 1  # 下一行开始
    elif start_line is not None and line.strip() == '};':
        end_line = i + 1
        break

if start_line is None or end_line is None:
    print("未找到 transitionVertexData 数组")
    exit(1)

print(f"找到数组：第 {start_line} 行到第 {end_line} 行")

# 提取数组内容
array_lines = lines[start_line:end_line-1]  # 排除最后的 };

# 解析数组数据 - 使用正则表达式匹配所有 {} 块
flat_data = []
content = ''.join(array_lines)

# 使用正则表达式匹配所有 {} 块（包括空块）
case_pattern = r'\{([^}]*)\}'
cases = re.findall(case_pattern, content)

for case_content in cases:
    case_content = case_content.strip()
    current_case = []
    
    if not case_content:
        # 空 case
        flat_data.extend([0] * 12)
        continue
    
    # 移除注释
    if '//' in case_content:
        case_content = case_content[:case_content.index('//')].strip()
    
    # 提取所有十六进制数
    hex_pattern = r'0x[0-9A-Fa-f]+'
    hex_values = re.findall(hex_pattern, case_content)
    
    if hex_values:
        # 转换为整数
        current_case = [int(val, 16) for val in hex_values]
    
    # 补齐到 12 个元素
    while len(current_case) < 12:
        current_case.append(0)
    
    # 只取前 12 个
    flat_data.extend(current_case[:12])

# 确保有 512 * 12 = 6144 个元素
while len(flat_data) < 6144:
    flat_data.append(0)

# 格式化为 VEX 数组字符串
vex_array_string = "int transitionVertexData[] = {\n    "
for i, val in enumerate(flat_data):
    vex_array_string += f"{val}"
    if i < len(flat_data) - 1:
        vex_array_string += ", "
    if (i + 1) % 12 == 0 and i < len(flat_data) - 1:  # 每 12 个元素换行
        vex_array_string += "\n    "
vex_array_string += "\n};"

print(vex_array_string)
