---
name: document-publisher
description: Read, preview, design, and publish documents in the GainFactor local document portal. Use when opening an existing PRD or other portal document, writing final portal MDX, using registered components, validating manifests, importing or updating a document, attaching review findings, or verifying a portal publication. Do not use for general Markdown writing or unrelated web publishing.
---

# Document Publisher

## 场景与 Shortcut 路由

**CRITICAL：先判断当前动作，只读取该场景的参考文件；不要在开始时批量读取 references。每份参考只在首次进入对应阶段时读取一次。**

### 内容构建

- **设计并直接编写最终 MDX — [`authoring-workflow`](references/authoring-workflow.md)**：新建完整报告、重构整篇文档或需要在多种表达方式间做选择时读取。局部文案或字段更新不要求重新制作页面蓝图。
- **查询或使用正文组件 — [`components/index`](references/components/index.md)**：先读索引，再只读取被选组件的参考文件。
- **维护统一组件样式 — [`components/design-system`](references/components/design-system.md)**：只在修改门户主题、视觉 Token、组件样式或视觉门禁时读取。
- **使用图标或 Mermaid — [`visuals`](references/visuals/index.md)**：按索引进入图标或关系图说明。
- **使用 AntV Infographic — [`infographic/index`](references/infographic/index.md)**：只有已经确认需要 Infographic 时读取，再进入详细语法。
- **生成或更新 `.portal.json` — [`presentation`](references/presentation.md)**：只处理正文之前的可选首屏摘要。
- **确定正式产物目录、稳定文件名与门户位置 — [`artifact-management`](references/artifact-management.md)**：新建文档、确定主体 slug 或维护上游 Skill 时读取。

### 发布操作

- **只验证现有 MDX / manifest — [`validation`](references/validation.md)**：只检查源文件、引用和内容契约，不构建门户。
- **发布或更新最终文档 — [`publishing/publish`](references/publishing/publish.md)**：门户发现、导入、构建、视觉门禁与发布状态。
- **挂载结构化评审结果 — [`publishing/review-findings`](references/publishing/review-findings.md)**。
- **查看已有 PRD 或其他门户文档，打开、关闭或检查门户 — [`publishing/preview`](references/publishing/preview.md)**：用户要求阅读、定位、运行或预览已有文档时读取。
- **发布、构建或预览失败 — [`publishing/troubleshooting`](references/publishing/troubleshooting.md)**：仅在失败发生后读取。

### 上游 Skill 集成

- **定义业务 Skill 的门户交付契约 — [`upstream-contract`](references/upstream-contract.md)**：仅在创建或维护调用本 Skill 的业务 Skill 时读取。

### 分阶段验证入口

- **局部内容或样式修改**：类型检查、Lint 和 Quick；进入 [`publishing/publish`](references/publishing/publish.md) 的“日常修改”。
- **公共组件、Token、响应式或图形能力完成**：执行 Full；进入 [`publishing/publish`](references/publishing/publish.md) 的“能力阶段完成”。
- **正式发布**：构建、Full 和契约测试全部通过；进入 [`publishing/publish`](references/publishing/publish.md) 的“正式发布”。

## 不在本 Skill 范围

- 不判断 PRD、画像、竞品分析或其他业务文档应该得出什么结论。
- 不把普通 Markdown 在发布阶段自动“美化”或转换成富组件。
- 不在导入阶段从正文推导首屏模块、图形或业务语义。
- 专业 Reviewer 负责生成评审结论；本 Skill 只校验和挂载调用方提供的结构化评审数据。

纯标准 Markdown 文档可以使用 `.md`；使用任何注册组件时最终源文件必须为 `.mdx`。富组件不可用时，在同一文件中降级为标准 Markdown。机器可读能力以 `../../assets/document-review-portal/portal-capabilities.json` 为准。
