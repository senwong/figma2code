# 采集、截图和坐标对齐

## Figma

优先用已授权的 Figma MCP。使用 REST API 时，从官方文件端点读取目标 nodes，并导出 frame 图像及图片填充资源。记录实际获得的版本与缓存 hash；若采集期间版本变化，重新取得一致快照。导出 URL 可能失效，应及时缓存字节。不要把凭证或带授权参数的 URL 写进报告。

来源：
- https://developers.figma.com/docs/rest-api/file-endpoints/
- https://developers.figma.com/docs/rest-api/file-node-types/

## 浏览器

复用现有浏览器工具或项目 Playwright。下面是集成示例，不是已安装的工具；确认运行环境后再使用。

```js
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
  locale: 'zh-CN',
  colorScheme: 'light',
  reducedMotion: 'reduce',
});
const page = await context.newPage();
await page.goto(url, { waitUntil: 'domcontentloaded' });
// 先执行页面所需的状态准备；等待真实的加载完成标志。
await page.evaluate(async () => {
  await document.fonts.ready;
  await Promise.all([...document.images].map(async image => {
    if (!image.complete) await new Promise((resolve, reject) => {
      image.addEventListener('load', resolve, { once: true });
      image.addEventListener('error', reject, { once: true });
    });
    if (!image.naturalWidth) throw new Error(`Image failed: ${image.currentSrc}`);
    await image.decode();
  }));
});
await page.screenshot({
  path: fullPath, fullPage: true, scale: 'css',
  animations: 'disabled', caret: 'hide',
});
```

懒加载图片先滚动触发再回到约定滚动位置；CSS 背景图、canvas、视频和虚拟列表需单独确认。不要仅以 networkidle 作为稳定依据。给导航、准备和截图设置有限超时；失败写入报告。

用 `locator.evaluate` 读取 `getBoundingClientRect()` 和 `getComputedStyle()`。显式采集 fontSize、fontWeight、lineHeight、letterSpacing、display、gap、padding、margin、border、borderRadius、objectFit、objectPosition 和 transform；按需要读父级数据。

元素截图会滚动目标入视口。若含 sticky/fixed 元素，截图前后重新记录滚动位置和边界框；优先从固定状态的全图裁取共同区域。伪元素、iframe 与 shadow DOM 单独标注采集边界。

来源：
- https://playwright.dev/docs/api/class-page
- https://playwright.dev/docs/api/class-locator

## 坐标换算

1. Figma 普通节点：`frameLocalX = nodeAbsX - frameAbsX`，Y 同理。
2. 浏览器普通文档流节点：`documentX = rect.left + scrollX`，Y 同理。fixed/sticky 节点按截图时实际绘制状态单独处理。
3. 图像像素：`pixel = (coordinate - captureOrigin) * imageScale`。记录捕获区域原点；不能把 viewport 坐标当 full-page 坐标。
4. CSS-scale 截图通常一 CSS px 对应一图像像素；device-scale 截图要使用实际像素尺寸校验倍率。Figma 导出倍率与浏览器 DPR 分开记录。
5. 已知倍率不同可以按声明的倍率归一化；不得为了消除布局错误拉伸某侧图像。主基准优先两侧从源头取得同尺度图像。
6. 裁剪时 floor 左上角、ceil 右下角；超出画布的请求报错或记录明确的边界处理。不要静默截短后继续比较。

只修正坐标原点、捕获区域和已知倍率；不要自动平移对齐目标元素来隐藏位置偏差。
