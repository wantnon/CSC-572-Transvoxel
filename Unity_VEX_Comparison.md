# Unity Transvoxel 实现 vs VEX 实现对比

## 1. Half-Thickness 处理方式

### Unity 实现
```csharp
// 使用法线方向调整顶点位置（适用于任意方向的 transition）
private const float TRANSITION_CELL_WIDTH_PERCENTAGE = 0.5f;

// 计算 delta 向量
float3 delta = float3.zero;
if ((vertBoundaryMask & 4) == 4 && vertex.z < 1) {
    delta.z = 1 - vertex.z;
}
// ... 其他方向的 delta 计算

delta *= TRANSITION_CELL_WIDTH_PERCENTAGE;  // 0.5

// 使用法线投影调整顶点位置
float3 vertexSecondaryPos = vertex + new float3(
    (1 - normal.x * normal.x) * delta.x - normal.y * normal.x * delta.y - normal.z * normal.x * delta.z,
    -normal.x * normal.y * delta.x + (1 - normal.y * normal.y) * delta.y - normal.z * normal.y * delta.z,
    -normal.x * normal.z * delta.x - normal.y * normal.z * delta.y + (1 - normal.z * normal.z) * delta.z);
```

**特点**：
- 使用法线方向投影，适用于任意方向的 transition（X/Y/Z 轴）
- 更通用，但计算更复杂
- 使用 `SecondaryVertexData` 存储调整后的顶点位置

### VEX 实现
```vex
// 直接修改 Z 坐标（只适用于固定轴方向）
if (axis == 32) {  // Negative z axis
    if (c1 >= 9) cornerPos1.z += voxel_scale * voxel_size.z * 0.5;
    if (c2 >= 9) cornerPos2.z += voxel_scale * voxel_size.z * 0.5;
}
```

**特点**：
- 直接修改 Z 坐标，简单直接
- 只适用于固定轴方向（当前实现固定为 -Z 轴）
- 与 C++ 参考实现一致

---

## 2. 角点定义

### Unity 实现
```csharp
// 角点 9-12（低分辨率面）初始与角点 0, 2, 6, 8 相同
_trCellValues[0x9] = _trCellValues[0];  // 角点 9 = 角点 0
_trCellValues[0xA] = _trCellValues[2];  // 角点 10 = 角点 2
_trCellValues[0xB] = _trCellValues[6]; // 角点 11 = 角点 6
_trCellValues[0xC] = _trCellValues[8]; // 角点 12 = 角点 8
```

### VEX 实现
```vex
// 角点 9-12：低分辨率面的 4 个角点
// 注意：根据 C++ 代码，这些角点的初始 Z 坐标也是 z-voxelScale（与高分辨率面相同）
trans_corner_pos[9] = trans_corner_pos[0];   // 角点 9 = 角点 0
trans_corner_pos[10] = trans_corner_pos[2];   // 角点 10 = 角点 2
trans_corner_pos[11] = trans_corner_pos[6];   // 角点 11 = 角点 6
trans_corner_pos[12] = trans_corner_pos[8];   // 角点 12 = 角点 8
```

**结论**：两者一致 ✓

---

## 3. Transition Cell 宽度计算

### Unity 实现
```csharp
private const float TRANSITION_CELL_WIDTH_PERCENTAGE = 0.5f;
delta *= TRANSITION_CELL_WIDTH_PERCENTAGE;  // 0.5
```

### VEX 实现
```vex
voxel_scale * voxel_size.z * 0.5
```

**差异**：
- Unity: 使用百分比常量（0.5），在局部空间计算
- VEX: 使用世界空间的绝对偏移量（`voxel_scale * voxel_size.z * 0.5`）

**结论**：两者在数值上等价，但 Unity 的实现更通用（适用于任意方向）

---

## 4. 顶点位置计算

### Unity 实现
```csharp
// 对于低分辨率面的顶点，使用整数网格坐标
int3 vertLocalPos = FaceToLocalSpace(direction, ChunkSize, 
    x + cornerOffset.x / 2, y + cornerOffset.y / 2, 0);

// 对于高分辨率面的顶点，使用浮点坐标
float3 vert0LocPos = FaceToLocalSpace(direction, ChunkSize, 
    x + cornerOffset0.x * 0.5f, y + cornerOffset0.y * 0.5f, 0);
```

### VEX 实现
```vex
// 所有角点都使用整数网格坐标
vector pos0_grid = set(x - voxel_scale, y - voxel_scale, z_high);
trans_corner_pos[0] = min_bound + pos0_grid * voxel_size;

// 然后在插值时应用 half-thickness 偏移
if (c1 >= 9) cornerPos1.z += voxel_scale * voxel_size.z * 0.5;
```

**差异**：
- Unity: 区分高分辨率面（浮点坐标）和低分辨率面（整数坐标）
- VEX: 统一使用整数网格坐标，在插值时应用偏移

---

## 5. 法线计算

### Unity 实现
```csharp
// 对于低分辨率面，使用密度数据的梯度
normal = new float3(
    GetDensityValue(locX - 1, locY, locZ) - GetDensityValue(locX + 1, locY, locZ),
    GetDensityValue(locX, locY - 1, locZ) - GetDensityValue(locX, locY + 1, locZ),
    GetDensityValue(locX, locY, locZ - 1) - GetDensityValue(locX, locY, locZ + 1));

// 对于高分辨率面，使用生成器的值
normal = new float3(
    Generator.GetValue(new float3(wX - 1, wY, wZ)) - Generator.GetValue(new float3(wX + 1, wY, wZ)),
    Generator.GetValue(new float3(wX, wY - 1, wZ)) - Generator.GetValue(new float3(wX, wY + 1, wZ)),
    Generator.GetValue(new float3(wX, wY, wZ - 1)) - Generator.GetValue(new float3(wX, wY, wZ + 1)));
```

### VEX 实现
```vex
// 当前实现没有计算法线
// 如果需要，可以使用 volumesamplegradient 或手动计算梯度
```

**差异**：
- Unity: 计算法线用于 half-thickness 调整
- VEX: 当前不计算法线，直接使用 Z 轴偏移

---

## 6. LOD Smoothing

### Unity 实现
```csharp
// 使用二分法进行 LOD smoothing
int subEdges = bIsLowResFace ? LOD : LOD - 1;
for (int j = 0; j < subEdges; ++j) {
    float3 midPointLocalPos = (corner0Copy + corner1Copy) * 0.5f;
    float3 midPointWorldPos = ChunkMin + midPointLocalPos * LODScale;
    float midPointDensity = Generator.GetValue(midPointWorldPos);
    
    if (Mathf.Sign(midPointDensity) == Mathf.Sign(density0)) {
        corner0Copy = midPointLocalPos;
        density0 = midPointDensity;
    } else {
        corner1Copy = midPointLocalPos;
        density1 = midPointDensity;
    }
}
```

### VEX 实现
```vex
// 当前实现已移除 LOD smoothing（根据用户要求）
// 之前的实现使用 volumesample 在网格空间中采样
```

**差异**：
- Unity: 实现了 LOD smoothing，使用二分法迭代
- VEX: 当前不实现 LOD smoothing（已移除）

---

## 7. 坐标系统

### Unity 实现
```csharp
// 使用 FaceToLocalSpace 函数处理不同方向的 transition
private int3 FaceToLocalSpace(TransitionDirection direction, int chunkSize, int x, int y, int z) {
    switch (direction) {
        case TransitionDirection.ZMin:
            return new int3(x, y, z);
        case TransitionDirection.ZMax:
            return new int3(y, x, chunkSize - z);
        // ... 其他方向
    }
}
```

### VEX 实现
```vex
// 固定为 -Z 轴方向
int axis = 32;  // 1 << 5 = 32 (Negative z axis)
```

**差异**：
- Unity: 支持 6 个方向的 transition（X/Y/Z 轴的正负方向）
- VEX: 只支持固定方向（当前为 -Z 轴）

---

## 8. 边界处理

### Unity 实现
```csharp
// 使用 vertBoundaryMask 标记边界顶点
int vertBoundaryMask = ((locX == 0 ? 1 : 0)
                      | (locY == 0 ? 2 : 0)
                      | (locZ == 0 ? 4 : 0)
                      | (locX == ChunkSize ? 8 : 0)
                      | (locY == ChunkSize ? 16 : 0)
                      | (locZ == ChunkSize ? 32 : 0));

// 只对边界顶点应用 half-thickness 调整
if (vertBoundaryMask > 0) {
    // 计算 delta 并应用法线投影
}
```

### VEX 实现
```vex
// 对所有低分辨率面的角点（corner >= 9）应用 Z 偏移
if (c1 >= 9) cornerPos1.z += voxel_scale * voxel_size.z * 0.5;
```

**差异**：
- Unity: 只对边界顶点应用 half-thickness 调整
- VEX: 对所有低分辨率面的角点应用偏移（更简单但可能不够精确）

---

## 总结

### 主要差异点：

1. **Half-Thickness 处理**：
   - Unity: 使用法线投影，适用于任意方向
   - VEX: 直接修改 Z 坐标，只适用于固定轴

2. **通用性**：
   - Unity: 支持 6 个方向的 transition
   - VEX: 只支持固定方向（-Z 轴）

3. **边界处理**：
   - Unity: 精确识别边界顶点
   - VEX: 对所有低分辨率面角点应用偏移

4. **LOD Smoothing**：
   - Unity: 实现了 LOD smoothing
   - VEX: 当前不实现（已移除）

### 建议：

1. **如果需要支持多方向 transition**：考虑实现类似 Unity 的 `FaceToLocalSpace` 函数
2. **如果需要更精确的边界处理**：考虑实现类似 Unity 的 `vertBoundaryMask` 机制
3. **如果需要更平滑的过渡**：考虑重新实现 LOD smoothing（使用法线投影）

### 当前 VEX 实现的优势：

1. **简单直接**：直接修改 Z 坐标，易于理解和调试
2. **与 C++ 参考一致**：更接近原始 C++ 实现
3. **性能**：计算量小，适合实时渲染

