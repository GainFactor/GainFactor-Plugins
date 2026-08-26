# 文档门户数据契约

公共生成器接受 Markdown/MDX 文档、可选 Portal Presentation JSON 和可选评审 JSON。所有数据均在运行时写入生成目录，公共模板不保存业务内容。

## 内容构建前置契约

任何 Skill 只要计划把产物导入公共文档门户，就应使用 `$document-publisher`，按场景路由读取参考；新建完整内容进入 `authoring-workflow`，维护业务 Skill 集成进入 `upstream-contract`，只查询组件字段进入 `components/index`：

- 在写作阶段选择能力注册表中状态为 `registered` 的正文工具和首屏模块，并直接产出最终内容；
- JSX 组件写入 `.mdx`，普通 `.md` 只使用标准 Markdown 与 fenced Mermaid；
- 没有匹配工具时退回标准 Markdown，不编造组件名或属性；
- 需要新工具时先完成门户注册、目录写法和验证，再由业务 Skill 使用。

发布阶段不进行语义转换或视觉美化，只导入和验证业务 Skill 已经完成的内容。

机器可读的唯一能力注册表是 `assets/document-review-portal/portal-capabilities.json`。

## 文档标识

- 产品型正式产物以 `docs/gainfactor/{product-slug}/{artifact-key}.mdx` 为内容源；默认生成门户为工作区 `.gainfactor/portal`。
- `artifact-key` 当前支持 `product-definition`、`brd`、`prd`、`user-journey`、`user-persona`、`competitive-analysis`、`product-metrics`、`domain-model`、`api-contract`、`hld`、`lld`、`test-strategy`、`test-spec`、`runbook`、`guardrails`。标准产物的 group、collection 和 route 由发布器根据主体统一计算。
- `slug`：门户内稳定且唯一的文档标识，只允许小写字母、数字和连字符。
- `type`：用户可读的文档类型，例如 `Product Definition`、`User Persona`、`Competitive Analysis`、`BRD`、`PRD`、`HLD`、`LLD`、`Test Strategy` 或 `Runbook`。
- `collection`：面包屑中展示的集合名称，例如“产品文档”或“研发设计”。
- `group`：左侧一级导航分组。默认按文档类型映射为 `product-requirements`、`technical-design`、`quality-delivery` 或 `other`；文档本身作为二级条目。
- manifest 使用 `sourcePath` 追踪相对工作区的源文件，使用 `artifactKey` 记录稳定产物类型。相同 route 只能由已登记源文件更新；旧条目缺少追踪字段时，在下一次成功更新时渐进补齐。

## 本地图片

- Markdown 中使用相对于源文档的本地图片路径，例如 `![Persona](assets/user-persona/persona.png)`。
- 导入器会把本地图片复制到门户的 `public/document-assets/<route>/`，并把 Markdown 链接重写为门户绝对路径。
- `http:`、`https:`、`data:`、根路径和锚点引用不会被复制。
- 本地图片不存在时导入失败，避免门户发布后出现破图。
- 同一文档中的相同图片只复制一次；不同文档使用各自的 route 目录隔离资产。

## 评审 JSON

```json
{
  "conclusion": "通过 / 有条件通过 / 不通过",
  "issues": [
    {
      "id": "PRD-001",
      "severity": "P0 / P1 / P2",
      "title": "问题摘要",
      "sectionId": "目标标题的 HTML id",
      "sectionTitle": "目标章节名称",
      "suggestion": "修改建议"
    }
  ]
}
```

`id`、`severity`、`title` 和 `sectionId` 必填。`sectionTitle` 与 `suggestion` 可选。问题必须属于当前导入的文档，不能跨文档复用错误的章节 ID。
