#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 更新 marchingCubesTablesWrangle.txt 中的 transitionVertexData 数组

import re

# 重新运行提取脚本获取数据
with open('LOGLEngine/Headers/Transvoxel.h', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到 transitionVertexData 数组的开始和结束
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'const unsigned short transitionVertexData' in line:
        start_line = i + 1
    elif start_line is not None and line.strip() == '};':
        end_line = i + 1
        break

# 提取数组内容
array_lines = lines[start_line:end_line-1]
content = ''.join(array_lines)

# 使用正则表达式匹配所有 {} 块（包括空块）
case_pattern = r'\{([^}]*)\}'
cases = re.findall(case_pattern, content)

flat_data = []
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
array_content = "\n    "
for i, val in enumerate(flat_data):
    array_content += f"{val}"
    if i < len(flat_data) - 1:
        array_content += ", "
    if (i + 1) % 12 == 0 and i < len(flat_data) - 1:
        array_content += "\n    "
array_content += "\n"

# 读取原始文件
with open('marchingCubesTablesWrangle.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到旧数组的位置
old_start = content.find('int transitionVertexData[] = {')
if old_start == -1:
    print("未找到 transitionVertexData 数组")
    exit(1)

old_end = content.find('};', old_start) + 2

# 替换数组内容
new_content = content[:old_start] + 'int transitionVertexData[] = {' + array_content + '};' + content[old_end:]

# 写回文件
with open('marchingCubesTablesWrangle.txt', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('更新完成！transitionVertexData 数组已替换为完整数据（6144 个元素）')

