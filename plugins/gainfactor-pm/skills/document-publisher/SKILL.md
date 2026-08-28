---
name: document-publisher
description: Read, preview, design, sync, and release documents in the GainFactor local document portal. Use when opening an existing PRD or portal document, writing final portal MDX, validating manifests, importing or updating documents, attaching review findings, previewing affected routes, or performing a full portal release. Do not use for general Markdown writing or unrelated web publishing.
---

# Document Publisher

## 先确定本轮终点

调用本 Skill 不等于正式发布。先选择终点，不得自动升级：

- `source-written`：只完成正式源文件，不调用门户。
- `validated`：只校验源文件、引用和 manifest。
- `imported`：同步门户源码和 manifest，不构建、不跑视觉门禁。
- `previewed`：让本轮目标路由可查看，只验证受影响路由。
- `released`：执行完整构建、Full 和契约测试。

用户只要求写文档、修改内容或讨论方案时默认停在 `source-written`；“接入/写入门户”默认到 `imported`；“打开/预览/让我看”到 `previewed`；只有明确要求正式发布，或修改公共组件、Token、响应式、Mermaid、AntV、截图与门禁实现时才到 `released`。用户撤回写入授权时立即停止后续写入并说明已发生的操作，不擅自回滚。

同一工作流有多个文档时，先完成并导入全部变更，再统一构建和验证一次。

## 执行与恢复
```text
□ 终点与写入权限已确定  □ 文档身份已解析  □ 目标均已校验并导入
□ 构建状态已确认        □ 受影响路由已验证  □ 实际达到的状态已报告
```
失败或暂停后从第一个未满足项继续；源文件、导入结果或构建产物未变化时不重复已通过步骤。

## Shortcut 路由

**只读取当前动作需要的参考，每份参考在本轮只读一次。已有最终源文件且 artifact identity 明确时，直接校验或导入，不再读取 authoring、组件或视觉资料。**

### 内容构建

- 整篇新建或重构最终 MDX — [`authoring-workflow`](references/authoring-workflow.md)
- 查询正文组件 — [`components/index`](references/components/index.md)
- 修改主题、Token 或组件样式 — [`components/design-system`](references/components/design-system.md)
- 图标或 Mermaid — [`visuals`](references/visuals/index.md)
- AntV Infographic — [`infographic`](references/infographic/index.md)
- 可选首屏 `.portal.json` — [`presentation`](references/presentation.md)
- 产物目录与稳定身份 — [`artifact-management`](references/artifact-management.md)：仅在调用方未提供身份时读取。

### 校验、同步与发布

- 只验证源文件 — [`validation`](references/validation.md)
- 导入、目标路由预览或正式 release — [`publishing/publish`](references/publishing/publish.md)
- 挂载评审结果 — [`publishing/review-findings`](references/publishing/review-findings.md)
- 打开、关闭或检查门户 — [`publishing/preview`](references/publishing/preview.md)
- 失败排查 — [`publishing/troubleshooting`](references/publishing/troubleshooting.md)：仅在失败后读取。
- 维护上游交付契约 — [`upstream-contract`](references/upstream-contract.md)

## 验证强度

- 单文档正文、presentation、review 或私有资源：校验并导入；预览时只检查目标路由。
- route、导航或共享资源：构建一次，检查受影响路由和导航。
- 公共门户能力或正式 release：执行 Full；正式 release 额外执行契约测试。
- Quick 必须包含本轮目标路由；固定基础页通过不能证明目标文档已验证。

任何失败都停止提升状态。纯 Markdown 可用 `.md`；使用注册组件必须用 `.mdx`。发布器不判断业务结论、不在导入时改写正文或推导首屏。机器能力以 `../../assets/document-review-portal/portal-capabilities.json` 为准。
