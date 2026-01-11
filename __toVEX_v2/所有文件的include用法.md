# __toVEX_v2 目录中所有 .txt 文件的 #include 用法

本文档列出了 `__toVEX_v2` 目录中所有已封装为函数的 VEX 文件的 `#include` 使用方法。

---

## Detail Wrangle 节点（Run Over: Detail only once）

这些文件用于 Detail Wrangle 节点，不需要传递 `@ptnum` 参数。

### 1. chunkVEX.txt
**功能**：根据 chunkID 生成 chunk 体素点阵

```c
#include "chunkVEX.txt"
chunk_main();
```

### 2. regularCellVEX.txt
**功能**：从 chunkVEX 输出中过滤出 regular cell 点

```c
#include "regularCellVEX.txt"
regularCell_main();
```

### 3. transCellVEX.txt
**功能**：生成 Transition Cell 点阵

```c
#include "transCellVEX.txt"
transCell_main();
```

### 4. boundaryCellVEX.txt
**功能**：生成 Boundary Cell 点阵（补一圈版本）

```c
#include "boundaryCellVEX.txt"
boundaryCell_main();
```

### 5. marchingCubesTablesWrangle.txt
**功能**：存储 Marching Cubes 查找表数据为 detail 属性

```c
#include "marchingCubesTablesWrangle.txt"
marchingCubesTables_main();
```

---

## Point Wrangle 节点（Run Over: Points）

这些文件用于 Point Wrangle 节点，需要传递 `@ptnum` 参数。

### 6. marchCubeVEX_modify.txt
**功能**：对 regular cell 进行 Marching Cubes 三角化

```c
#include "marchCubeVEX_modify.txt"
marchCubeVEX_modify_main(@ptnum);
```

### 7. marchCubeForBoundaryVEX.txt
**功能**：对 boundary cell 进行 Marching Cubes 三角化

```c
#include "marchCubeForBoundaryVEX.txt"
marchCubeForBoundary_main(@ptnum);
```

### 8. transvoxelVEX.txt
**功能**：对 transition cell 进行 Transvoxel 三角化

```c
#include "transvoxelVEX.txt"
transvoxel_main(@ptnum);
```

### 9. visualizeCell.txt
**功能**：将 regular cell 或 boundary cell 以线框形式可视化

```c
#include "visualizeCell.txt"
visualizeCell_main(@ptnum);
```

### 10. visualizeTransCell.txt
**功能**：将 transition cell 以线框形式可视化

```c
#include "visualizeTransCell.txt"
visualizeTransCell_main(@ptnum);
```

### 11. visualizeChunk.txt
**功能**：将 transition cell 以线框形式可视化（与 visualizeTransCell.txt 相同）

```c
#include "visualizeChunk.txt"
visualizeChunk_main(@ptnum);
```

---

## 完整示例

### 示例 1：生成 Chunk 体素点阵（Detail Wrangle）

```c
#include "chunkVEX.txt"
chunk_main();
```

### 示例 2：过滤 Regular Cell（Detail Wrangle）

```c
#include "regularCellVEX.txt"
regularCell_main();
```

### 示例 3：Regular Cell 三角化（Point Wrangle）

```c
#include "marchCubeVEX_modify.txt"
marchCubeVEX_modify_main(@ptnum);
```

### 示例 4：Transition Cell 三角化（Point Wrangle）

```c
#include "transvoxelVEX.txt"
transvoxel_main(@ptnum);
```

### 示例 5：Boundary Cell 三角化（Point Wrangle）

```c
#include "marchCubeForBoundaryVEX.txt"
marchCubeForBoundary_main(@ptnum);
```

### 示例 6：可视化 Cell（Point Wrangle）

```c
#include "visualizeCell.txt"
visualizeCell_main(@ptnum);
```

---

## 注意事项

1. **文件路径**：确保 `.txt` 文件在 Houdini 的搜索路径中，或使用相对路径（相对于 `.hip` 文件）。

2. **节点类型**：
   - Detail Wrangle：使用 `*_main()` 无参数版本
   - Point Wrangle：使用 `*_main(@ptnum)` 带参数版本

3. **查找表数据**：使用 `marchingCubesTablesWrangle.txt` 时，确保在 Detail Wrangle 节点中运行，以便将查找表数据存储为 detail 属性。

4. **删除标记**：某些函数内部使用 `setpointgroup(0, "del", ptnum, 1, "set")` 来标记删除点，后续可以使用 Blast 节点删除标记的点。

5. **参数设置**：某些函数需要节点参数（如 `chi("lodLevel")`），确保在节点参数面板中设置了相应的参数。

---

## 文件列表总结

| 文件名 | 节点类型 | 函数名 | 参数 |
|--------|---------|--------|------|
| chunkVEX.txt | Detail | `chunk_main()` | 无 |
| regularCellVEX.txt | Detail | `regularCell_main()` | 无 |
| transCellVEX.txt | Detail | `transCell_main()` | 无 |
| boundaryCellVEX.txt | Detail | `boundaryCell_main()` | 无 |
| marchingCubesTablesWrangle.txt | Detail | `marchingCubesTables_main()` | 无 |
| marchCubeVEX_modify.txt | Point | `marchCubeVEX_modify_main()` | `@ptnum` |
| marchCubeForBoundaryVEX.txt | Point | `marchCubeForBoundary_main()` | `@ptnum` |
| transvoxelVEX.txt | Point | `transvoxel_main()` | `@ptnum` |
| visualizeCell.txt | Point | `visualizeCell_main()` | `@ptnum` |
| visualizeTransCell.txt | Point | `visualizeTransCell_main()` | `@ptnum` |
| visualizeChunk.txt | Point | `visualizeChunk_main()` | `@ptnum` |

---

## 典型工作流程

### 流程 1：生成 Chunk 体素点阵
```
Detail Wrangle: chunkVEX.txt → chunk_main()
```

### 流程 2：过滤 Regular Cell 并三角化
```
Detail Wrangle: regularCellVEX.txt → regularCell_main()
Point Wrangle: marchCubeVEX_modify.txt → marchCubeVEX_modify_main(@ptnum)
```

### 流程 3：生成 Transition Cell 并三角化
```
Detail Wrangle: transCellVEX.txt → transCell_main()
Point Wrangle: transvoxelVEX.txt → transvoxel_main(@ptnum)
```

### 流程 4：生成 Boundary Cell 并三角化
```
Detail Wrangle: boundaryCellVEX.txt → boundaryCell_main()
Point Wrangle: marchCubeForBoundaryVEX.txt → marchCubeForBoundary_main(@ptnum)
```

### 流程 5：初始化查找表
```
Detail Wrangle: marchingCubesTablesWrangle.txt → marchingCubesTables_main()
（将查找表数据存储为 detail 属性，供其他节点通过 input1 读取）
```

