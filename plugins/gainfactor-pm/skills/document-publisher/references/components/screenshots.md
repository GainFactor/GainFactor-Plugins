# 产品截图与旅程证据

正式产品界面证据使用 `Screenshot`，不要依赖裸 Markdown 图片承担图号、证据编号或灯箱语义。

```ts
type ScreenshotProps = {
  src: string
  title?: string
  caption?: string
  evidenceId?: string
  device?: "desktop" | "tablet" | "mobile"
  step?: string | number
  maxHeight?: string | number
}

type ScreenshotGalleryProps = {
  children: ReactNode
  columns?: 1 | 2 | 3
  layout?: "grid" | "rail"
}

type EvidenceStepProps = {
  step: string | number
  title: string
  id?: string
  children?: ReactNode
  evidence?: ReactNode
}
```

```mdx
<Screenshot src="./assets/search-result.png" title="搜索结果页"
  caption="用户可在同一页面比较距离、时间与拥挤程度。"
  evidenceId="E-S01" device="desktop" step={2} />
```

单图默认 `maxHeight="70vh"`、`object-fit: contain`，点击可在灯箱查看原图。灯箱支持按钮缩放、`Ctrl/Command + 滚轮` 或触控板缩放手势，放大后可以拖动画布；Esc 关闭并恢复原焦点。`title`、`caption`、图号、步骤和 `evidenceId` 进入同一说明区；正式证据必须填写 `caption`。手机长图设置 `device="mobile"`，宽度限制在 280–380px 范围内。

多图使用 1–3 列响应式画廊：

```mdx
<ScreenshotGallery columns={2}>
  <Screenshot src="./assets/before.png" title="调整前" caption="入口层级较深。" evidenceId="E-S02" />
  <Screenshot src="./assets/after.png" title="调整后" caption="入口移动到首屏。" evidenceId="E-S03" />
</ScreenshotGallery>
```

同一任务有 3 张以上连续证据时使用单行证据带，避免图片墙挤压正文。证据带支持横向滚动，每张截图仍可点击查看原图：

```mdx
<ScreenshotGallery layout="rail">
  <Screenshot src="./assets/input.png" title="输入与首轮响应" caption="证明系统收到完整约束。" evidenceId="P01-E01" />
  <Screenshot src="./assets/process.png" title="任务执行过程" caption="证明系统拆解并执行关键步骤。" evidenceId="P01-E02" />
  <Screenshot src="./assets/result.png" title="结果与约束冲突" caption="证明最终结果未满足预算约束。" evidenceId="P01-E03" />
</ScreenshotGallery>
```

证据带只放最小充分证据，并按“输入 → 过程 → 结果/异常”的阅读顺序排列。不得用裸 `<div>`、Tailwind 网格或多个 `ImageZoom` 拼成截图墙。

需要把证据挂在旅程步骤旁时使用：

```mdx
<EvidenceStep step={2} title="核对推荐结果"
  evidence={<Screenshot src="./assets/result.png" title="结果页" caption="核对关键条件。" evidenceId="E-S04" />}>
  用户检查时间、距离和限制条件，再决定是否采用方案。
</EvidenceStep>
```

`EvidenceStep` 只组织步骤正文与证据，不替代存在分支、回路或多主体交互的 Mermaid。富组件不可用时降级为步骤标题、正文、受限尺寸图片和完整图注。
