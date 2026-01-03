# Houdini 节点设置指南

## 节点连接顺序

```
[Volume/SOP] 
    ↓
[Detail Wrangle] (marchingCubesTablesWrangle.txt) - 创建查找表
    ↓
[Point Wrangle] (pointsVEX.txt) - 生成体素点云
    ↓
    ├─→ [Point Wrangle] (marchCubeVEX.txt) - 处理普通体素
    └─→ [Point Wrangle] (transvoxelVEX.txt) - 处理 transition cell
            ↓
        [Merge] - 合并两个 Point Wrangle 的输出
            ↓
        [Blast] - 删除标记的点（可选）
```

## 详细步骤

### 1. 创建查找表节点（Detail Wrangle）

**节点类型**: Detail Wrangle  
**代码文件**: `marchingCubesTablesWrangle.txt`

**设置**:
- **Input**: 可以是空几何体，或者一个简单的点（使用 Add SOP 创建一个点）
- **代码**: 复制粘贴 `marchingCubesTablesWrangle.txt` 的全部内容
- **注意**: 这个节点将查找表数据存储为 detail 属性，供后续节点使用

### 2. 生成体素点云（Point Wrangle）

**节点类型**: Point Wrangle  
**代码文件**: `pointsVEX.txt`

**设置**:
- **Input 0**: Volume 数据（你的体素数据）
- **Input 1**: 边界框几何体（Bound SOP 或 Box SOP）
- **代码**: 复制粘贴 `pointsVEX.txt` 的全部内容
- **Channel Parameters**:
  - `isolevel` (float): 等值面阈值，默认值 0.0

**输出**: 包含体素点云，每个点都有 `corner_pos`、`corner_val`、`is_transition` 等属性

### 3. 处理普通体素（Point Wrangle）

**节点类型**: Point Wrangle  
**代码文件**: `marchCubeVEX.txt`

**设置**:
- **Input 0**: 连接到步骤 2 的 Point Wrangle 输出
- **Input 1**: 连接到步骤 1 的 Detail Wrangle 输出
- **代码**: 复制粘贴 `marchCubeVEX.txt` 的全部内容
- **Channel Parameters**:
  - `isolevel` (float): 等值面阈值，默认值 0.0

**输出**: 普通体素的三角形网格

### 4. 处理 Transition Cell（Point Wrangle）

**节点类型**: Point Wrangle  
**代码文件**: `transvoxelVEX.txt`

**设置**:
- **Input 0**: 连接到步骤 2 的 Point Wrangle 输出（**注意：不是步骤 3 的输出**）
- **Input 1**: 连接到步骤 1 的 Detail Wrangle 输出
- **代码**: 复制粘贴 `transvoxelVEX.txt` 的全部内容
- **Channel Parameters**:
  - `isolevel` (float): 等值面阈值，默认值 0.0

**输出**: Transition cell 的三角形网格（用于接缝修补）

**重要**: 
- 这个节点需要从**原始的体素点云**（步骤 2）读取数据，而不是从步骤 3 的输出
- 因为步骤 3 会删除已处理的点（`@group_del = 1`），而 transition cell 需要完整的点云数据

### 5. 合并结果（Merge）

**节点类型**: Merge

**设置**:
- **Input 0**: 连接到步骤 3 的输出（普通体素网格）
- **Input 1**: 连接到步骤 4 的输出（transition cell 网格）

**输出**: 合并后的完整网格

### 6. 清理（可选 - Blast）

**节点类型**: Blast

**设置**:
- **Group**: `del`（删除标记为 `@group_del = 1` 的点）
- **Delete Non-Selected**: 选择 "Selected"

**注意**: 如果步骤 3 和 4 已经删除了不需要的点，这个节点可能不需要

## 完整节点网络示例

```
[Volume SOP: density]
    ↓
[Detail Wrangle: marchingCubesTables] ← (marchingCubesTablesWrangle.txt)
    ↓
[Point Wrangle: generatePoints] ← (pointsVEX.txt)
    ├─ Input 0: Volume SOP
    ├─ Input 1: Bound SOP (边界框)
    └─ Parameter: isolevel = 0.0
    ↓
    ├─→ [Point Wrangle: marchCubes] ← (marchCubeVEX.txt)
    │       ├─ Input 0: generatePoints
    │       ├─ Input 1: marchingCubesTables
    │       └─ Parameter: isolevel = 0.0
    │
    └─→ [Point Wrangle: transvoxel] ← (transvoxelVEX.txt)
            ├─ Input 0: generatePoints (原始点云)
            ├─ Input 1: marchingCubesTables
            └─ Parameter: isolevel = 0.0
                    ↓
            [Merge: combineMeshes]
                ├─ Input 0: marchCubes
                └─ Input 1: transvoxel
                    ↓
            [最终网格输出]
```

## 常见问题

### Q: 为什么 transvoxelVEX 的 Input 0 要连接到 generatePoints 而不是 marchCubes？

**A**: 因为 `marchCubeVEX.txt` 会删除已处理的点（`@group_del = 1`），而 `transvoxelVEX.txt` 需要访问所有点（包括普通体素和 transition cell）的完整数据。如果连接到 `marchCubes` 的输出，transition cell 的点可能已经被删除了。

### Q: 如何设置 isolevel 参数？

**A**: 在 Point Wrangle 节点的参数面板中：
1. 点击 "Create Parameters" 或 "Edit Parameter Interface"
2. 添加一个 Float 类型的参数
3. 参数名设为 `isolevel`
4. 默认值设为 `0.0`
5. 在代码中使用 `chf("isolevel")` 读取

或者直接在代码中修改：
```vex
float isolevel = 0.0;  // 直接设置值，而不是从 channel 读取
```

### Q: 如果遇到 "detail attribute not found" 错误怎么办？

**A**: 确保：
1. Detail Wrangle 节点（marchingCubesTables）在节点网络中**存在且已执行**
2. 即使 Detail Wrangle 的输入是空的，它也会创建 detail 属性
3. 检查 Detail Wrangle 节点的代码是否正确执行（没有语法错误）

### Q: 如何调试？

**A**: 
1. 在每个 Point Wrangle 节点后添加一个 Geometry Spreadsheet 节点，查看点的属性
2. 检查 `is_transition` 属性是否正确设置
3. 检查 `corner_pos` 和 `corner_val` 数组属性是否正确
4. 使用 Print 节点输出调试信息

## 性能优化建议

1. **并行处理**: 如果体素数据很大，可以考虑将数据分割成多个区域，分别处理后再合并
2. **LOD 优化**: 调整 `pointsVEX.txt` 中的 `voxel_scale_lod0` 和 `voxel_scale_lod1` 值来平衡质量和性能
3. **缓存节点**: 对于查找表节点（Detail Wrangle），可以缓存结果，避免重复计算

