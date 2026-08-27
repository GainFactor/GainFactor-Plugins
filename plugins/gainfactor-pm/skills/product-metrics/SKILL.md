---
name: product-metrics
description: Define or review a PRODUCT_METRICS system from an existing product definition, including a product-level north-star or task-level primary metric, driver and process metrics, guardrails, measurement contracts, and conditional AI efficiency measurement. Use after product definition when a product owner needs to decide how product value, progress, and unacceptable failure will be measured. Do not use for product positioning, persona, competitor analysis, metric diagnostics, dashboards, or analytics implementation.
---

> **宿主兼容规则（必读）**：执行前完整读取 `../../references/host-compatibility.md`，并按当前宿主选择交互提问、联网检索和文件操作方式。

# Product Metrics

> **语言规则**：默认跟随用户输入语言；用户显式指定时以用户指定为准。稳定 artifact type 使用 `PRODUCT_METRICS`。详见 `../../references/language-policy.md`。

从 `PRODUCT_DEFINITION` 已确认的用户价值出发，建立能够支持产品决策的主要指标、驱动指标和底线指标。任何进入候选比较或最终体系的指标都必须说明如何计算、数据如何定义、是否可统计、是否真正可衡量目标价值。对用户先使用业务问题、通俗定义和通俗公式解释，再提供数据实施口径。

## 输入与边界

- 优先读取已有 `PRODUCT_DEFINITION`，复用其中的用户、问题、价值机制、核心场景、可观察结果、产品阶段、商业模式和失败边界，不重复询问。
- 没有产品定义，或核心用户、问题、价值机制存在高影响冲突时，说明阻塞并建议先运行 `$define-product`。
- 上游为 `analysis-target` 时，默认只分析公开可观察的候选指标；制定内部指标前确认用户拥有该产品或已获授权。
- 不改写 `PRODUCT_DEFINITION`，不实现埋点、数据管道、看板、实验平台或绩效制度，也不诊断已有指标为何变化。

## 指标任务路由

展示精简产品价值链后，只确认本次任务，不追问用户角色、评审人或评审周期：

| 指标任务 | 主要指标 |
|---|---|
| 长期产品指标体系 | 一个唯一北极星指标 |
| 上线或采用判断 | 一个主要成功指标 |
| 专项优化 | 一个专项结果指标 |
| 实验评估 | 一个主要实验指标 |

统一称为“主要指标”。只有长期产品指标体系使用“北极星指标”；其他任务不得为了形式强行命名为北极星。上游没有且会改变指标定义时，再确认产品阶段、战略目标、历史基线或关键数据限制，每轮最多 2 个问题。

## 渐进读取

- 定义长期产品北极星时，读取 [北极星指标方法](references/north-star-method.md)；其他任务不读取。
- 生成任何指标候选或检查数据时，读取 [测量契约](references/measurement-contract.md)。
- 开始拆解主要指标和定义底线时，读取 [驱动、过程与底线方法](references/driver-and-guardrail-method.md)。
- 第一次写入门户前，读取 [产物与发布契约](references/artifact-and-publishing.md)，从上游产品定义继承产品级导航分组，后续阶段继续沿用。
- 每次实际写入前，按 `$document-publisher` 当前要求读取其表达能力与发布流程；本 Skill 负责业务内容，发布器负责实现和预览。

## 执行流程

### 1. 建立产品价值链

从上游建立：

```text
核心用户 → 触发场景 → 关键行为 → 有效结果 → 持续价值 → 商业或组织结果
```

多边产品分别梳理关键参与方，再定位共同完成的价值交换；内部效率产品连接任务质量、时间、成本和组织目标，不强行连接营收。有效结果不能只是点击、访问、创建或生成。用 Mermaid 展示复杂关系；简单关系用文本即可。

### 2. 确认指标任务

让用户只选择本次任务类型。确认后进入对应主要指标设计，不额外询问与定义无关的信息。

### 3. 定义主要指标

- 长期体系按北极星方法，从价值单元、合格条件、统计主体和自然周期生成 2–3 个候选；相似产品只用于校准，不用于照抄。
- 其他任务从本次要支持的决策和产品有效结果生成 2–3 个候选。
- 所有候选先完成最小测量契约，再比较价值代表性、战略或任务一致性、反馈速度、可影响性、可统计性、可衡量性和抗博弈性。
- 推荐一个候选，并用 `✅`、`⚠️`、`❌` 展示会改变结论的门禁结果。硬门禁不通过则修正候选，最多再比较 2 个替代候选；仍无法通过时标为 `待定义`。

用户确认的是完整业务定义和最小测量契约，不是指标名称。确认后自动调用 `$document-publisher`，以 `previewed` 为终点第一次创建或更新同一 `PRODUCT_METRICS` 门户文档，不执行正式 release 或 Full。

### 4. 拆解驱动与过程指标

以已确认的主要指标公式为根节点建立数学拆解和驱动树，不在确认后才补写或暗改主要指标口径。若拆解暴露出口径不可复算或价值关系不成立，返回阶段 3 重新确认。

选择默认 3 个真正推动主要指标、适合当前决策周期且团队可影响的核心过程指标；局部任务只保留会改变决策的必要指标。再指出 2 个本产品最容易误用的虚荣指标及其正确诊断用途。所有最终指标补全完整测量契约并通过门禁。

用户确认后自动调用 `$document-publisher`，以 `previewed` 为终点第二次更新同一文档，不执行正式 release 或 Full。

### 5. 定义底线与行动契约

先回答：“即使主要指标增长很好，发生什么事情时我们仍会认为产品失败？”从质量、信任、角色失衡、成本、履约、合规和产品责任边界中选择默认 3 个真正制衡主要指标的底线指标；局部任务按风险保留必要数量。再指出 2 个容易被误当成底线的指标。

涉及 AI 时，按增效、赋能或决策价值模式识别不可接受失败，不机械套用幻觉率、准确率或生成成功率。阈值必须有法规／合同、产品承诺、历史分布或实验依据；没有依据时标为 `待验证`，不得编造红线。

用户确认后自动调用 `$document-publisher`，以 `previewed` 为终点第三次更新同一文档并完成交付，不执行正式 release 或 Full。

## 状态纪律

分别记录两个状态，不用一个 `draft` 混淆业务确认和数据准备：

- **Definition Status**：`proposed | confirmed`，表示指标业务定义是否由用户确认；
- **Measurement Readiness**：`unverified | partially-ready | ready`，表示公式、数据、基线和证据是否足以投入使用。

用户确认定义不等于数据已经就绪。新产品可以是 `confirmed / unverified`；成熟产品存在数据缺口时可以是 `confirmed / partially-ready`。不得编造业务数据、外部产品指标、行业基准、目标或阈值。

## 完成条件

完成时必须满足：上游可追溯、任务明确、主要指标唯一、公式可复算、驱动关系可解释、底线对应真实失败、每个最终指标都有测量契约、状态诚实、同一门户路由已读回验证且预览可访问。存在数据或证据缺口时可以完成定义工作，但必须保留对应 Measurement Readiness 和验证动作。
