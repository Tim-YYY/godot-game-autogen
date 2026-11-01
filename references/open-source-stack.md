# 开源游戏技术栈映射与集成顺序

原文推荐 10 个仓库，但其中多数是 **C++ 库或独立工具**，在 Godot 里不能直接拿来用。AI 自动化开发的正确做法是：**能用 Godot 内置/原生插件的，绝不去编译 C++ 库**。下表是逐一映射。

## 映射表：仓库 → Godot 里的正确用法

| # | 仓库 | 本质 | 在 Godot 里该怎么做 |
|---|------|------|---------------------|
| 1 | Jolt Physics (`jrouwe/JoltPhysics`) | C++ 物理引擎 | 用 **godot-jolt** 插件（`godot-jolt/godot-jolt`），drop-in 替换默认物理，无需碰 C++ |
| 2 | Terrain3D (`TokisanGames/Terrain3D`) | 地形系统 | **本身就是 Godot 插件**，直接装 addon，用于大场景地形雕刻/高度图/植被 LOD |
| 3 | Material Maker (`RodZill4/material-maker`) | 程序化材质工具 | **独立 App**，离线用它生成纹理/材质，导出 PNG/EXR 后导入 Godot；不适合在游戏内实时调用 |
| 4 | Effekseer (`effekseer/Effekseer`) | 粒子特效工具 | 独立工具；Godot 4 有**内置 GPUParticles2D/3D** 可覆盖大多数需求，需要复杂特效时用 Effekseer 导出动画后导入 |
| 5 | Voxel Tools (`Zylann/godot_voxel`) | 体素地形 | **本身就是 Godot 插件**（`godot_voxel`），用于可挖掘/破坏的世界、洞穴、流式加载 |
| 6 | Recast Navigation (`recastnavigation/recastnavigation`) | 导航网格 | Godot 4 **内置 NavigationServer + NavigationRegion3D**，已含 Recast 等价烘焙，直接用内置 |
| 7 | ozz-animation (`guillaumeblanc/ozz-animation`) | 动画混合库 | 仅自研引擎需要；Godot 用**内置 AnimationPlayer + AnimationTree**（状态机/混合树）即可 |
| 8 | The Forge (`ConfettiFX/The-Forge`) | 跨平台图形基础设施 | 仅自研引擎需要；用 Godot 就完全不需要 |
| 9 | meshoptimizer (`zeux/meshoptimizer`) | 网格优化 | Godot 导入管线**已内置**网格简化/压缩，改导入设置即可，无需单独集成 |
| 10 | FastNoise2 (`Auburn/FastNoise2`) | 程序化噪声 | Godot 4 **内置 FastNoiseLite** 节点，直接用于地形/纹理噪声，无需外部库 |

## 结论（重要）

10 个仓库里，**真正需要"装"的只有 3 个 Godot 原生插件**：
1. `godot-jolt`（物理）
2. `Terrain3D`（地形，可选）
3. `godot_voxel`（体素，可选）

其余要么是内置能力（导航/噪声/网格优化/粒子），要么是离线工具（Material Maker / Effekseer），要么只在自研引擎时才用（The Forge / ozz）。

## 集成顺序（按需，从简到繁）

1. **先跑通 MVP**：默认物理 + 内置导航 + 内置粒子 + FastNoiseLite。这些零成本，覆盖 90% 的 2D 和多数 3D 需求。
2. **3D 且要更好的物理表现** → 加 `godot-jolt`（刚体/碰撞/载具，性能与稳定性优于默认）。
3. **大型开放地形** → 加 `Terrain3D`（雕刻 + 高度图 + 植被 LOD）。
4. **可破坏/可挖掘世界** → 加 `godot_voxel`（洞穴/隧道/流式地形）。
5. **离线生成复杂材质/纹理** → 用 Material Maker 生成后导入。
6. **需要 2D 序列帧/复杂 3D 特效** → Effekseer 导出后导入。

## 各插件安装要点

- **godot-jolt**：下载对应 Godot 版本的 release，解压到 `addons/godot-jolt/`，`Project Settings > Plugins` 启用，物理引擎选 Jolt。
- **Terrain3D / godot_voxel**：均从 GitHub release 下载，放入 `addons/`，启用插件后按各自文档初始化（Terrain3D 需建 `Terrain3D` 节点 + 数据文件）。
- 插件启用后记得用 Godot MCP 验证（读取插件状态、确认节点可创建）。

## 性能/体积提醒

- 大模型务必配合网格简化（导入设置里的 LOD / 简化），3D 场景用 LOD + 剔除。
- 贴图统一用压缩格式（BC/ETC2），移动端注意内存。
