# figma2code

用于 Figma → 前端高保真还原的 Agent Skill，适合 Claude Code、Codex 和其他支持 `SKILL.md` 的工具。

核心流程：Figma 节点 + 原图 → 复用项目组件实现 → 浏览器截图 → 局部裁剪与差异诊断 → 修改并复测。

## 安装

克隆仓库后，把 `skills/figma2code` **整个目录**复制到所用工具的技能目录。已有同名目录时先比较内容，避免覆盖自定义修改。

```bash
git clone https://github.com/senwong/figma2code.git
```

- Claude Code：项目内 `.claude/skills/figma2code/`。
- Codex：项目内 `.agents/skills/figma2code/`。
- 也可直接让 Agent 阅读仓库中的 `skills/figma2code/SKILL.md` 并遵循步骤。

工具的技能发现规则可能随版本变化，必要时以所安装版本为准。

## 使用

```text
使用 figma2code skill，将这个 Figma frame 还原到现有项目的 /landing 页面：
<Figma 链接和 node-id>
目标 viewport：1440 × 900。
复用现有组件和字体，完成后用浏览器截图与设计稿做局部比对，修正差异并给出验收结果。
```

在 Codex 中可使用 `$figma2code`；在 Claude Code 中可使用 `/figma2code`。也支持“对比已有页面与 Figma，修正间距/字体/裁切”的任务。

## 内容

- [Skill 主流程](skills/figma2code/SKILL.md)
- `references/`：截图坐标、视觉审查和验收清单
- `assets/manifest.example.json`：任务输入与映射模板
- `scripts/compare_images.py`：同尺度截图裁剪、叠图、像素差异和 JSON 报告

Skill 会使用当前 Agent 可用的 Figma/浏览器能力，不会自行安装或连接 MCP，也不绑定具体视觉模型。缺少节点数据时可以从截图推断，但会标明限制。Python 图像辅助脚本需要 Pillow；运行方法见 Skill。

目标是在固定环境下获得有测量依据的高保真实现；像素差异比例不代表设计质量评分。

官方说明：[Claude Code Skills](https://code.claude.com/docs/en/skills) · [Codex Skills](https://developers.openai.com/zh-Hans/docs/build-skills)
