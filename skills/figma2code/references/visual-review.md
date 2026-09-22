# 局部视觉审查

## 两种图像证据

- **共同窗口裁剪**：在两张已对齐全图上取完全相同矩形，保留元素位置、大小和上下文差异。`compare_images.py --crop X Y WIDTH HEIGHT` 使用图像像素单位。
- **元素各自裁剪**：用于观察文字、圆角、图像内容等内部细节。必须同时保留原始边界框差值；不得用于证明全局位置相同。

放大只帮助观察。插值没有新增信息，模型也可能再次压缩图像；优先局部原始分辨率，必要时提高两侧源图输出分辨率。精确尺寸由 Figma/DOM 提供，视觉模型提出原因假设。

## 脚本行为

依赖 Python 3 + Pillow：`python3 -m pip install -r <skill-dir>/scripts/requirements.txt`。复用项目环境，避免无关依赖升级。

脚本要求两张图像完整画布尺寸一致，不做自动缩放、对齐或动态区域识别。透明图先合成到约定背景（默认白色，可传 `--background '#111111'`）；对每像素取 RGB 通道最大绝对差，只有大于 `--threshold` 的像素算差异。阈值范围 0–255。

输出：`reference.png`、`actual.png`、`diff.png`（红色标记差异）、`overlay.png`（50% 叠图）、`report.json`。差异框使用完整输入图坐标；`changedFraction` 的分母是当前裁剪区域像素数。每轮使用新的输出目录，脚本拒绝覆盖已有证据文件。退出码 0 表示分析完成，不表示验收通过；2 表示输入错误。脚本不识别抗锯齿或做感知质量打分。

长页面高度不同先列为几何差异。可选择相同捕获区域重拍，或在其他工具里显式补边并记录规则；不得直接拉伸后送入脚本。全图比例容易被空白稀释，要看关键区域的独立报告。

## 给视觉模型的任务

提供两个标明 reference / actual 的局部图、区域整体定位、node ID、selector、边界框和所需样式。要求只报告有图像或数据证据的差异：

```json
{
  "nodeId": "482:10293",
  "selector": "[data-visual-id=hero-title]",
  "type": "typography",
  "observation": "实际标题第二行基线更低",
  "measurement": { "property": "lineHeight", "reference": 58, "actual": 64, "unit": "px" },
  "measurementSource": "figma-node-and-computed-style",
  "hypothesis": "继承了页面通用标题行高",
  "nextAction": "检查标题样式来源和父级继承",
  "confidence": "high"
}
```

这是格式示例，值必须来自当前任务。若只有截图，measurement 写 null，measurementSource 写 screenshot-estimate；不要生成看似测得的精确 CSS 值。

先检查共同父级：多个子元素同向偏移时，优先检查 padding、容器高度、字体或前序内容，不逐个加 margin 补偿。

## 控制上下文成本

首次全图建立区域索引；后续只读改变的节点、目标 CSS、关联父级和 1–3 对局部图。缓存设计版本、资产 hash、截图环境及每轮结果；不要每轮重新把完整 JSON、DOM 和长图塞入模型。
