# godot-game-autogen

一个给 WorkBuddy 用的**全流程 AI 游戏自动开发** skill：把一句模糊的游戏创意，自动推进成一个能跑、能玩、美术风格统一的 Godot 游戏工程。

## 能力

- **八阶段工作流**：概念设计(GDD) → 美术资产生成 → 工程初始化 → 场景脚本 → 技术栈集成 → 构建运行 → 截图自检迭代 → 打包交付
- **生图 API 集成 + 自检闭环**：OpenAI 兼容生图接口批量出图，脚本校验格式/透明通道/尺寸，AI 逐张回看、不合格自动重试
- **Godot MCP 接入指南**：四种方案对比，推荐 `@satelliteoflove/godot-mcp`
- **开源技术栈映射**：10 个仓库 → Godot 原生等价物（真正要装的只有 godot-jolt / Terrain3D / godot_voxel）
- **免费 CC0 素材库清单**：Kenney / Quaternius / KayKit / Poly Haven / ambientCG 等，含授权速查

## 目录结构

```
godot-game-autogen/
├── SKILL.md                         # skill 入口（WorkBuddy 识别靠它）
├── references/
│   ├── godot-mcp-setup.md           # Godot MCP 接入
│   ├── open-source-stack.md         # 开源技术栈映射
│   ├── art-asset-guide.md           # 美术资产需求 + 免费素材库清单
│   └── image-gen-pipeline.md        # 生图 API + 自检循环
└── scripts/
    ├── gen_image.py                 # 通用生图脚本（OpenAI 兼容）
    └── check_image.py               # 资产自检脚本
```

## 快速部署

WorkBuddy 通过 `SKILL.md` 识别 skill，放到 skills 目录即可（装完**开新会话**才生效）。

### 方式一：git clone（推荐，便于后续更新）

```bash
# macOS / Linux
cd ~/.workbuddy/skills
git clone https://github.com/<你的用户名>/godot-game-autogen.git

# Windows (PowerShell)
cd $env:USERPROFILE\.workbuddy\skills
git clone https://github.com/<你的用户名>/godot-game-autogen.git
```

后续更新：

```bash
cd ~/.workbuddy/skills/godot-game-autogen && git pull
```

### 方式二：下载 ZIP 手动解压

1. 在 GitHub 仓库页 `Code → Download ZIP`
2. 解压后把 `godot-game-autogen` 文件夹（含 `SKILL.md` 的那一层）整个放进 `~/.workbuddy/skills/`
3. 注意：解压出的路径若带仓库名前缀，要**取出含 `SKILL.md` 的那层文件夹**再放进去，否则 WorkBuddy 扫不到

## 前置条件

| 依赖 | 说明 |
|------|------|
| Godot 4.x | 推荐 4.4+，需知道可执行文件路径 |
| Godot MCP | 任选一种接入，见 `references/godot-mcp-setup.md` |
| 生图 API（可选） | OpenAI 兼容接口 + key，见 `references/image-gen-pipeline.md` |
| Python 3 | 运行 `scripts/` 下脚本（纯标准库，无外部依赖） |

## 使用

接入后对 WorkBuddy 说一句，例如：

> 帮我做一个 2D 平台跳跃小游戏

即可触发全流程自动开发。
