# Transvoxel 三角面生成问题诊断指南

## 问题：没有生成三角面

### 诊断步骤

#### 1. 检查是否有 Transition Cell 点

**方法**：在 `pointsVEX.txt` 节点后添加一个 **Group** 节点

- **Group Name**: `transition_cells`
- **Group Type**: Points
- **Base Group**: `@is_transition == 1`

然后查看节点输出，检查是否有任何点被选中。

**如果没有点被选中**：
- 检查 `pointsVEX.txt` 是否正确生成了 transition cell 点
- 检查 LOD 边界设置是否正确（`lod_boundary`）
- 检查 volume 数据是否覆盖了边界区域

#### 2. 检查查找表数据是否加载

**方法**：在 Detail Wrangle 节点（`marchingCubesTablesWrangle.txt`）后添加一个 **Attribute Wrangle** 节点

```vex
// 检查查找表数据
printf("transitionCellClass length: %d\n", len(detail(0, "transitionCellClass")));
printf("transitionCellData length: %d\n", len(detail(0, "transitionCellData")));
printf("transitionVertexData length: %d\n", len(detail(0, "transitionVertexData")));
```

**预期结果**：
- `transitionCellClass`: 512
- `transitionCellData`: 应该是一个较大的数组（取决于查找表大小）
- `transitionVertexData`: 6144 (512 * 12)

**如果数组长度为 0**：
- 检查 `marchingCubesTablesWrangle.txt` 代码是否正确执行
- 检查是否有语法错误
- 确保 Detail Wrangle 节点已执行

#### 3. 使用调试版本代码

**方法**：使用 `transvoxelVEX_debug.txt` 替换 `transvoxelVEX.txt`

这个调试版本会在 Houdini 的 Console 窗口输出详细的调试信息：
- 查找表数组长度
- 每个点的处理状态
- cube index 值
- 顶点数和三角形数
- 创建的三角形数量

**查看调试输出**：
1. 在 Houdini 中打开 **Windows > Python Shell** 或查看 **Console** 窗口
2. 运行节点网络
3. 查看输出的调试信息

#### 4. 检查常见问题

##### 问题 A: 所有点都被过滤掉

**可能原因**：
- `transCubeIndex == 0` 或 `transCubeIndex == 511`（体素完全在内部或外部）
- `vertex_count == 0`（没有顶点需要生成）

**解决方法**：
- 检查 `isolevel` 值是否合适
- 检查 volume 数据是否在边界区域有变化
- 尝试调整 `isolevel` 值

##### 问题 B: 查找表数组索引越界

**可能原因**：
- `transCubeIndex` 值超出范围（应该 < 512）
- `transCellClass` 值导致 `baseIndex` 超出范围

**解决方法**：
- 使用调试版本查看实际的索引值
- 检查查找表数据是否正确加载

##### 问题 C: 角点数组无效

**可能原因**：
- `trans_corner_pos` 或 `trans_corner_val` 数组长度 < 13
- 数组属性没有正确设置

**解决方法**：
- 检查 `pointsVEX.txt` 是否正确设置了 `trans_corner_pos` 和 `trans_corner_val` 属性
- 使用 Geometry Spreadsheet 查看点的属性

##### 问题 D: 顶点索引越界

**可能原因**：
- `edge_vertices` 数组的实际长度小于 `vertex_count`
- `transitionCellData` 中的索引值超出范围

**解决方法**：
- 使用调试版本查看实际的顶点数和索引值
- 检查 `transitionVertexData` 是否正确提取

#### 5. 快速测试方法

**创建一个简单的测试场景**：

1. **创建测试 Volume**：
   - 使用 **Volume** SOP 创建一个简单的 volume
   - 确保在 Z 轴中间位置（LOD 边界）有数据变化

2. **简化代码测试**：
   - 暂时注释掉 LOD Smoothing 部分
   - 简化插值逻辑
   - 只处理一个 transition cell 点

3. **逐步调试**：
   - 先确保能读取到 transition cell 点
   - 再确保能读取到查找表数据
   - 最后确保能生成三角形

### 常见错误消息

#### "Invalid source /obj/box1/transvoxel/attribvop1"
- **原因**：Input 1 没有正确连接到 Detail Wrangle 节点
- **解决**：确保 transvoxelVEX 的 Input 1 连接到 marchingCubesTables 节点

#### "detail attribute not found"
- **原因**：查找表数据没有正确创建
- **解决**：检查 Detail Wrangle 节点是否正确执行，查找表数组是否正确设置

#### "array index out of range"
- **原因**：数组索引超出范围
- **解决**：使用调试版本查看实际的索引值，检查查找表数据

### 验证节点连接

确保节点连接顺序正确：

```
[Volume] 
  ↓
[Detail Wrangle: marchingCubesTables] ← 创建查找表
  ↓
[Point Wrangle: pointsVEX] ← 生成点云
  ├─ Input 0: Volume
  ├─ Input 1: Bound/Box
  ↓
  ├─→ [Point Wrangle: marchCubeVEX] ← 普通体素
  │     ├─ Input 0: pointsVEX
  │     └─ Input 1: marchingCubesTables
  │
  └─→ [Point Wrangle: transvoxelVEX] ← Transition cell
        ├─ Input 0: pointsVEX (重要！)
        └─ Input 1: marchingCubesTables
```

### 下一步

如果以上步骤都无法解决问题，请：
1. 使用调试版本代码
2. 复制 Console 中的调试输出
3. 检查 Geometry Spreadsheet 中的点属性
4. 提供具体的错误信息或调试输出

