---
name: godot-game-autogen
description: 全流程 AI 游戏自动开发。当用户要求"做一个游戏 / 开发一个游戏 / 用 Godot 做游戏 / AI 自动生成游戏"、已接入 Godot MCP 后需要构建调试游戏，或需要生成美术资产、集成开源游戏技术栈（物理 / 地形 / 导航 / 动画 / 粒子特效 / 网格优化 / 程序化噪声）时使用。覆盖 2D/3D Godot 游戏从概念设计 → 美术资产生成 → 场景搭建 → 脚本编写 → 技术栈集成 → 构建运行 → 截图自检 → 迭代修复的完整闭环。
agent_created: true
---

# Godot 全流程 AI 游戏自动开发

## 目的

把一句模糊的游戏创意，自动推进成一个**能跑、能玩、有统一美术风格**的 Godot 游戏工程。本 skill 是编排层：它协调 Godot MCP（引擎操作）、生图 API（美术资产）、开源技术栈（物理/地形/导航/动画/特效）与自检循环（截图回看），让 AI 在最小人工干预下完成从 0 到可玩 Demo 的全流程。

## 何时使用

- 用户说"帮我做一个 XXX 游戏"、"用 Godot 做个小游戏"、"AI 自动生成游戏"。
- 已接入 Godot MCP，需要读取/修改场景、运行游戏、读取报错。
- 需要生成美术资产（角色、道具、UI、背景、贴图）或集成开源游戏库。
- 用户要求"把这段帖子/这份清单做成游戏开发能力"——本 skill 即该能力的落地。

## 前置条件（首次使用前检查）

1. **Godot 引擎**：Godot 4.x（推荐 4.4+，UID 相关工具需要）。需知道可执行文件路径。
2. **Godot MCP**：任选其一并接入你的 AI 编码助手（Claude Code / Codex / Cursor 等），见 `references/godot-mcp-setup.md`。
3. **生图 API**：一个 OpenAI 兼容或 Stability 兼容的生图服务 + key，见 `references/image-gen-pipeline.md`。
4. **Python 3**：运行 `scripts/` 下的脚本（本项目已内置，无需外部依赖）。

## 核心编排原则

- **先问范围，再动手**：模糊需求先确认「2D 还是 3D」「核心玩法一句话」「美术风格」。若用户明确说"直接做一个出来"，则自行拍板并记录假设。
- **小步快跑**：先出「最小可玩闭环」（能移动、能交互、有美术），再叠加系统（物理、导航、特效）。
- **美术先行定风格**：在写代码前先定 3~5 张「风格基准图」（主角 + 场景 + UI 配色），保证全项目视觉统一。
- **能用引擎内置就别引入 C++ 库**：Godot 4 已内置导航网格（Recast 等价）、FastNoiseLite（FastNoise2 等价）、网格优化导入。Jolt 用 godot-jolt 插件。详见 `references/open-source-stack.md` 的映射表。

## 八阶段工作流

按顺序执行；每阶段产出物沉淀到 `项目根目录/game_assets/` 与 Godot 工程内。

### 阶段 1：概念与游戏设计文档（GDD）
- 把用户需求拆成结构化 GDD：核心玩法、视角（2D/3D）、美术风格关键词、目标平台、核心循环、MVP 范围。
- 产出：`game_assets/gdd.md`。明确 MVP 的「必须做」与「以后做」清单。

### 阶段 2：美术资产生成（生图 API）
- 依据 GDD 定「风格基准图」，再批量生成资产。详见 `references/art-asset-guide.md` 与 `references/image-gen-pipeline.md`。
- 用 `scripts/gen_image.py` 调用生图 API，用 `scripts/check_image.py` 自检。
- 产出：`game_assets/sprites/`、`textures/`、`ui/`、`bg/` 等，按维度分类。

### 阶段 3：Godot 工程初始化
- 通过 Godot MCP 或直接写文件创建工程：`project.godot`、目录规范（`scenes/`、`scripts/`、`assets/`）。
- 配置渲染器（2D 用默认，3D 用 Forward+）、窗口尺寸、输入映射（InputMap）。

### 阶段 4：场景与脚本搭建（核心玩法）
- 用 Godot MCP 读取/创建场景节点、挂载脚本、写 GDScript/C#。
- 先实现 MVP 核心循环：玩家控制、基本交互、胜负/得分。
- 导入阶段 2 生成的美术资产到对应节点。

### 阶段 5：技术栈集成（按需）
- 根据 GDD 需要，选择性集成：物理（godot-jolt）、地形（Terrain3D）、体素（godot_voxel）、导航（内置 NavigationServer）、粒子（GPUParticles/Effekseer）、程序化纹理（FastNoiseLite/Material Maker）。
- 集成顺序与"何时用哪个"见 `references/open-source-stack.md`。

### 阶段 6：构建与运行
- 用 Godot MCP 运行工程，读取 debug 输出与报错。
- 首次运行必须跑通，否则进入阶段 7 修复。

### 阶段 7：截图自检与迭代修复（核心闭环）
- 用 Godot MCP 截取运行画面（或用无头模式截图），**逐张回看**，对照 GDD 检查：
  - 美术是否统一、有无白块/缺纹理/错位；
  - 玩法是否可交互、有无明显 bug；
  - UI 是否可读、文字是否溢出。
- 发现问题 → 修复 → 重跑 → 再截图，循环直到满意。截图与结论沉淀到 `game_assets/qa/`。

### 阶段 8：交付与打包
- 用 Godot MCP 导出可执行文件（Windows/Linux/Web）。
- 汇总：GDD、截图、玩法说明、运行方式，一并 `present_files` 展示给用户。

## 关键决策规则

- **2D vs 3D**：没把握时选 2D（资产生成快、迭代快、可控性强），除非用户明确要 3D 或玩法本质需要 3D（如第一人称、开放世界）。
- **美术资产要不要生图 AI**：绝大多数需要。程序化工具（FastNoiseLite、Material Maker）只能覆盖地形/材质/噪声纹理；角色、道具、UI、背景、概念图等"手绘感"资产必须用生图 API。详见 `references/art-asset-guide.md` 的覆盖矩阵。
- **脚本语言**：默认 GDScript（与 MCP 工具链契合最好）；用户指定 C# 时用 C#。
- **风格统一**：所有生图 prompt 必须复用同一套「风格前缀」（来自阶段 2 的风格基准），避免大杂烩。

## 资源索引

| 资源 | 用途 |
|------|------|
| `references/godot-mcp-setup.md` | 接入 Godot MCP 的多种方案与各 AI 助手配置 |
| `references/open-source-stack.md` | 10 个开源仓库的归类、Godot 原生等价物映射、集成顺序 |
| `references/art-asset-guide.md` | 游戏所需美术资产清单、程序化 vs 生图覆盖矩阵、免费 CC0 素材库清单与授权速查、风格统一技巧 |
| `references/image-gen-pipeline.md` | 生图 API 调用方式、自检循环、游戏资产 prompt 模板 |
| `scripts/gen_image.py` | 通用生图脚本（OpenAI 兼容 / Stability 兼容） |
| `scripts/check_image.py` | 生成图片自检（格式/尺寸/透明通道/文件有效性） |

首次执行时，先读 `references/godot-mcp-setup.md` 确认 MCP 已通；需要生图时读 `references/image-gen-pipeline.md` 与 `references/art-asset-guide.md`。
