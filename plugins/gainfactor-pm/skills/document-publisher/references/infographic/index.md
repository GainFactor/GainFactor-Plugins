# AntV Infographic 路由

只有在页面蓝图已经确认需要视觉叙事，并且正文、表格、普通组件或 Mermaid 不能更直接表达时读取本入口。

按主要关系选择模板族：

| 关系 | 模板族 |
|-|-|
| 严格顺序、阶段演进、多角色交互、并列摘要 | `sequence-*` / `list-*` → [`list-and-sequence`](list-and-sequence.md) |
| 双方、SWOT 或象限对比 | `compare-*` → [`compare`](compare.md) |
| 树、结构、思维导图、节点关系 | `hierarchy-*` / `relation-*` → [`hierarchy-and-relation`](hierarchy-and-relation.md) |
| 单组统计、趋势、占比、词频 | `chart-*` → [`charts`](charts.md) |

先读取对应模板族参考。只有使用其中未覆盖的模板、主题高级配置或需要完整语法核验时，才继续读取完整 [`syntax`](../antv-infographic-syntax.md)。未选择 Infographic 时不要读取任何详细语法。

门户只使用本地 `@antv/infographic` 和 Lucide 资源，禁止 CDN、远程字体和远程图标。最终 MDX 必须把 DSL 写成内联模板字符串：

渲染后的信息图支持按钮缩放、复位和全屏，也支持 `Ctrl/Command + 滚轮`、触控板缩放与触屏双指缩放；放大后直接拖动画布查看不同区域。Mermaid、Infographic 与 Screenshot 使用一致的缩放和拖拽手势。

```mdx
<Infographic syntax={`infographic chart-bar-plain-text
  data
    title 完成率
    values
      - label 方案 A
        value 68
      - label 方案 B
        value 91`} caption="方案完成率" />
```

`syntax` 必须紧跟在 `<Infographic` 的同一行。MDX 会把模板字符串首行之后的每行统一左移两格，因此源码中的 `data` 必须写两格，其他层级也在正常 AntV DSL 基础上额外增加两格；编译后才会恢复为 `data` 顶格、子字段两格。不要在最终文档中只保留 fenced `infographic` 代码块：它只展示语法，不会渲染图形。也不要写 `syntax={...}` 占位符或未在 MDX 中定义的变量。只有用户明确只索要 DSL 时才单独输出 fenced 代码块。
