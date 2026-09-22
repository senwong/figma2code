---
name: figma2code
description: Implement or refine frontend pages from Figma designs using node data, original assets, browser screenshots, local image crops, and measured visual regression. Use for Figma-to-code, 1:1 reproduction, pixel-perfect UI, design-to-React/Next.js/HTML, and fixing spacing, typography, alignment or image-crop differences against a Figma frame.
---

# Figma2Code

把 Figma 节点数据、设计稿截图和浏览器实测结果结合起来，完成页面实现和视觉回归。使用项目现有技术栈、组件与样式约定；保留语义、可访问性和交互。

## 1. 明确目标与可用能力

- 阅读项目的 AGENTS.md、运行脚本、目标页面及相关组件；确认已有改动。
- 从请求和仓库提取 Figma 文件/frame、目标路由、运行命令、viewport、字体与交互状态。只询问缺失且阻止实施的信息；其余做合理假设并记录。
- 检查当前实际可用的 Figma MCP/API、浏览器和图片查看工具。下文的步骤是能力约定，不是假定存在的工具名称。
- 有 Figma 数据访问时采用双通道；只有截图时明确标记“截图推断”，请求原始字体/素材并继续可完成的实现。无浏览器能力时完成代码和静态检查，明确视觉验收待完成。
- 复制 [manifest 模板](assets/manifest.example.json) 到项目已有产物目录或 `.visual/`，记录设计版本、环境与映射。保持凭证在环境变量/授权工具中。

## 2. 获取设计事实

- 读取目标 frame 和必要子节点，保留 node ID、层级、边界框、Auto Layout、padding/gap、字体、填充、圆角及图片变换。先复用缓存，再读取改变的子树。
- 获取同版本 frame 截图，提取原始图片、SVG 和字体。使用现有资源；不要用整页截图替代可交互页面，不随意生成品牌图标或替代真实照片。
- 区分布局框与可见绘制边界：阴影、旋转、描边和裁切可能超出节点尺寸。
- 记录参考图倍率和 frame 原点。采集与截图前阅读 [capture-and-alignment.md](references/capture-and-alignment.md)。

## 3. 实现第一版

- 先确认字体和资源，再完成容器、响应式布局、排版、图片裁切和细节样式。
- 优先复用项目组件与 token；使用 flex/grid 表达布局关系，仅对设计中的叠层使用定位。
- 为关键节点建立稳定 selector 映射，可使用 `data-visual-id`。先覆盖 header、hero、标题、CTA、主图和重复卡片。
- 仅为有明确匹配的元素记录映射；多匹配、缺失和低置信度候选必须标记。将额外断点的推断布局与设计稿覆盖的断点区分。

## 4. 拍摄与定位差异

- 固定 viewport、DPR、浏览器版本、locale、字体和页面状态。等待字体及图片加载、数据稳定，停止动画、光标闪烁和非确定内容。
- 拍全图定位大差异，再取对应局部图；同时读取目标 DOM 的边界框和必要 computed style。检查字体实际加载状态，不能只看 font-family 声明。
- 使用共同坐标窗口保留位移证据；使用各自元素裁剪只比较内部形态。不要将元素截图独立缩放到同尺寸后宣称位置一致。
- 在同尺度、同画布尺寸的图像上执行确定性差异检查：

```bash
python3 <skill-dir>/scripts/compare_images.py \
  --reference .visual/reference.png --actual .visual/actual.png \
  --out .visual/run-01/hero --crop 80 120 1120 600 --threshold 16
```

- `<skill-dir>` 替换为本 Skill 的实际绝对目录；Python 依赖为 Pillow，缺失时使用现有虚拟环境或安装 `scripts/requirements.txt`。
- 查看脚本生成的 reference、actual、diff、overlay 图片，再判断差异原因。比例是超过阈值的像素占比，不是设计质量或“还原率”。参数、限制和测量方法见 [visual-review.md](references/visual-review.md)。

## 5. 视觉诊断与修正

- 每轮只提交最大差异的 1–3 个区域、对应节点、DOM 样式及必要父级上下文给当前支持图片输入的模型。无需强制接入另一个模型。
- 将观察、实测值、原因假设分开。模型猜测的 px 不得标为实测；查不到的值写 null。
- 排查顺序：资源/字体 → 父容器几何 → 子元素布局 → 行高/换行 → 图片裁切 → 颜色/描边/阴影。
- 每轮更改一个可解释的原因集合，运行项目现有相关检查，重新截图和测量。父级改动后检查受影响兄弟节点及目标断点；保留已知正确的功能。
- 像素图变差时检查是否只是渲染噪声，也检查实际回归。不要靠扩大 mask、放宽阈值或覆盖基准消除真实问题。
- 默认每个区域连续两轮无改善时换诊断方向；总计五轮后仍有偏差，保存证据并列出未解决项。用户指定迭代预算时遵循用户要求。

## 6. 验收与交付

读取 [acceptance.md](references/acceptance.md)，按设计覆盖的断点/状态验收，并检查基本交互。

交付页面代码、实际运行的检查结果、前后截图/差异报告、剩余问题。指出哪些尺寸来自数据、哪些来自推断；没有运行的检查写“未运行”。仅当实测支持时才报告达标；固定环境的像素差无法证明跨设备 100% 一致。
