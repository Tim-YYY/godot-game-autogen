# 生图管线与自检循环

## 接入生图 API

### 配置方式（任选其一）

**方式 A：环境变量**（推荐，`scripts/gen_image.py` 自动读取）
```
GAME_IMG_API_BASE   # 例如 https://api.openai.com/v1 或 https://api.siliconflow.cn/v1
GAME_IMG_API_KEY    # 你的 key
GAME_IMG_MODEL      # 例如 gpt-image-1 / dall-e-3 / 服务商指定的模型名
```

**方式 B：配置文件** `~/.workbuddy/game-assets/config.json`
```json
{
  "api_base": "https://api.openai.com/v1",
  "api_key": "sk-xxxx",
  "model": "gpt-image-1",
  "default_size": "1024x1024"
}
```

绝大多数生图服务都提供 **OpenAI 兼容** 的 `/images/generations` 接口，所以 `gen_image.py` 按该协议实现即可通用。

### 调用脚本

```bash
python scripts/gen_image.py \
  --prompt "flat vector art, cute slime enemy, vibrant palette, clean outlines, transparent background" \
  --size 1024x1024 \
  --out game_assets/sprites/enemy_slime.png
```

参数：`--prompt`（必填）、`--size`（默认 1024x1024）、`--n`（张数）、`--out`（输出路径或目录）、`--ref`（图生图参考图，可选）。

## 自检循环（"自己检查"）

生成后**必须回看**，不能生完就扔进工程。循环如下：

1. **生成** → `gen_image.py` 产出图片。
2. **校验** → `check_image.py` 检查：文件是否有效、格式、尺寸是否达标、精灵是否有透明通道、文件大小是否异常。
   ```bash
   python scripts/check_image.py game_assets/sprites/enemy_slime.png --expect-alpha
   ```
3. **目视** → 用 Read 工具直接打开图片**逐张看**，对照检查：
   - 风格是否与基准图统一（配色、笔触、比例）；
   - 有无乱码文字、多余肢体、畸形、半透明空洞；
   - 精灵背景是否已透明、有无白边。
4. **决定** → 通过 → 入库；不通过 → 调整 prompt（更具体的风格词 / 负向词 / 换参考图）重新生成，最多重试 3 次，仍不达标则降级为占位色块并记录待办。

## 游戏资产生图 Prompt 模板

| 资产 | 模板 |
|------|------|
| 角色精灵 | `{风格前缀}, {角色描述}, full body, centered, transparent background, game sprite, high quality` |
| 道具/图标 | `{风格前缀}, {道具描述}, game item icon, centered, transparent background, clean silhouette` |
| UI 按钮 | `{风格前缀}, rounded button, subtle gradient, no text, ui element, transparent background` |
| 2D 背景 | `{风格前缀}, {场景描述}, game background, layered parallax, no characters, no text, 16:9` |
| 天空盒 | `{风格前缀}, skybox panorama, seamless equirectangular, {环境描述}` |
| 特效帧 | `{风格前缀}, {特效描述}, particle effect sprite, black background, high contrast` |

> 负向词（OpenAI 兼容接口部分支持 `negative` 或塞进 prompt）常用：`text, watermark, logo, blurry, low quality, extra limbs, deformed`。

## 批量生成与一致性

- 同一类资产（如 10 个道具）用**同一条风格前缀**批量生成，循环里逐个调用 + 逐个自检。
- 同一角色多姿态：先生成基准图，再以基准图为 `--ref` 图生图，保持角色一致。
- 生成数量较大时，把结果目录结构规划好（见 `art-asset-guide.md`），避免后期导入混乱。

## 兜底：WorkBuddy 内置生图

若用户尚未提供外部 API key，可先用 WorkBuddy 内置的生图能力应急出图；等拿到 key 后切回 `gen_image.py` 走外部 API（可控性、批量、成本更优）。
