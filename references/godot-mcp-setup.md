# Godot MCP 接入指南

## 为什么需要 Godot MCP

没有 MCP 时，AI 只能改文件、猜报错。有了 MCP，AI 能直接：
- 读场景树、节点属性、工程资源
- 创建/修改场景与节点、写脚本
- **运行游戏、读取 debug 输出与报错**
- 截取运行画面、注入输入
- 按需抓取 Godot 官方文档

这是"AI 自动开发游戏"闭环里最关键的一环——否则每改一次都要人肉把报错复制回来。

## 主流方案对比（2026-11 现状）

| 方案 | 形态 | 协议 | 特点 | 推荐场景 |
|------|------|------|------|----------|
| `@satelliteoflove/godot-mcp` | 编辑器 addon + npx 服务 | HTTP (默认 6550) | 场景/节点/动画/TileMap 直接操作、截图、注入输入、运行时控制 | **首选**（功能最全、可操作编辑器） |
| `@coding-solo/godot-mcp` | 独立 npx 服务，无需 addon | stdio | 无需装插件、能运行工程读输出，但操作场景能力较弱 | 快速起步、只读+运行调试 |
| Funplay MCP (`funplay-godot-mcp`) | 编辑器 addon | HTTP (默认 8765) | 105 个工具、语言感知（GDScript/C# 自动区分） | 需要大量工具面、商业项目 |
| `minimal-godot-mcp` (ryanmazzolini) | DAP/LSP 诊断 | stdio | 语言服务器诊断 + 控制台输出，无需 addon | 与上面任一**并行**使用，补诊断能力 |

## 推荐接入：`@satelliteoflove/godot-mcp`

### 1. 安装 addon
```bash
npx -y @satelliteoflove/godot-mcp --install-addon /path/to/your/godot/project
```
然后在 Godot 编辑器里 `Project Settings > Plugins` 启用 `Godot MCP`。

### 2. 配置到 WorkBuddy
WorkBuddy 的 MCP 配置文件在 **`~/.workbuddy/mcp.json`**（注意不是带点的 `.mcp.json`）。合并写入，不要覆盖已有 server：

```json
{
  "mcpServers": {
    "godot-mcp": {
      "command": "npx",
      "args": ["-y", "@satelliteoflove/godot-mcp"],
      "env": {
        "GODOT_PATH": "C:/Tools/Godot/Godot_v4.7-stable_win64.exe",
        "GODOT_PORT": "6550"
      }
    }
  }
}
```

若 addon 换了端口，`GODOT_PORT` 同步改；WSL2 下用 `GODOT_HOST` 指定宿主 IP。

### 3. 验证
- 重启会话后，确认出现 `godot-mcp` 前缀的工具（如 `get_godot_version` / 场景相关工具）。
- 冒烟测试：让 AI "用 Godot MCP 列出当前工程的所有场景"。

## 备选：`@coding-solo/godot-mcp`（最简单，无需 addon）
```json
{
  "mcpServers": {
    "godot": {
      "command": "npx",
      "args": ["-y", "@coding-solo/godot-mcp"],
      "env": { "GODOT_PATH": "C:/Tools/Godot/Godot_v4.7-stable_win64.exe" }
    }
  }
}
```
适合"只想让 AI 能跑工程、读报错"的轻量场景。

## 注意事项

- **Windows 下务必设 `GODOT_PATH`**，否则 MCP 可能找不到 Godot 可执行文件。
- addon 类方案要求 **Godot 编辑器保持打开**；`@coding-solo` 方案 Godot 可关闭。
- 配置写好后**不会自动生效**，需要在 WorkBuddy 右上角连接器管理页对新增 server 点「信任」启用。
- 若一个 MCP 不够用，可同时挂多个（如 `godot-mcp` + `minimal-godot-mcp`）互补。
