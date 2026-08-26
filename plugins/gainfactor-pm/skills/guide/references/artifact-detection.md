# Artifact Detection Guide

本指南定义 `guide` 在扫描项目文档时如何识别 artifact 类型、状态、审查证据与推荐置信度。

## 目标

Guide 需要把仓库中的文档与证据，归一化为可用于路由的结构化状态：

- `artifact_type`
- `status`
- `evidence_level`
- `confidence`
- `chosen_candidate`

Guide 不需要做到“100% 自动理解所有文档”，但必须做到：

1. 优先依赖强证据
2. 在弱证据下显式标注低置信度
3. 在歧义会改变推荐时主动向用户确认

## 总体检测顺序

对每个候选文档，按以下顺序检测：

1. **TRACEABILITY-METADATA**
2. **文档内状态字段**
3. **审查/准出证据**
4. **标题与文件名关键词**
5. **目录上下文**

如果上一级已经足够确定，不要继续用弱证据推翻强证据。

## 证据等级

| 等级 | 名称 | 典型信号 | 说明 |
|------|------|----------|------|
| E1 | 强证据 | `TRACEABILITY-METADATA`、明确 `artifact.type`、明确 `status` | 优先级最高 |
| E2 | 审查证据 | 准出证书、审查报告、明确“通过/不通过” | 用于确认 `approved/in_review` |
| E3 | 结构证据 | 文档标题、章节结构、模板特征 | 可辅助确认 artifact 类型 |
| E4 | 启发式 | 文件名、目录名、邻近文件 | 只在前三级不足时使用 |

## 状态归一化

所有文档状态必须统一映射为：

- `missing`
- `draft`
- `in_review`
- `approved`
- `unknown`

### 状态映射规则

| 原始信号 | 归一化状态 |
|----------|------------|
| `status: approved` | `approved` |
| `status: in_review` | `in_review` |
| `status: draft` | `draft` |
| 标题含“准出证书”且明确通过 | `approved` |
| 标题含“审查报告”且未发现通过结论 | `in_review` |
| 文档存在，但无批准证据 | `draft` |
| 只能弱匹配到类型，无法确认状态 | `unknown` |

### 同义词映射

以下词汇可按等价处理：

- `approved`：`已批准`、`准出`、`通过`
- `in_review`：`in review`、`reviewing`、`评审中`、`审核中`
- `draft`：`草稿`、`初稿`、`draft`

如果同一文档同时出现冲突状态：

- 优先以 `TRACEABILITY-METADATA` 中的 `artifact.status` 为准
- 其次以最新的审查/准出证据为准
- 再次才看正文顶部的表格/标题状态

## Artifact 识别规则

### 0. PRODUCT_DEFINITION

强信号：

- 明确声明 artifact type 为 `PRODUCT_DEFINITION`
- 标题含“产品定义”或 `Product Definition`
- 同时包含产品定位、用户角色、价值机制、冷启动、商业闭环和定义状态等结构

弱信号：

- 文件名含 `product-definition`、`product_definition` 或“产品定义”

注意：

- 产品介绍、宣传文案或单页概览不能仅凭标题判为正式产品定义
- 该 artifact 是可选上下文，不参与主流程最早阻塞点计算
- 文档存在但没有明确状态时按 `draft` 处理

### 1. BRD

强信号：

- 标题含 `BRD`
- 文档结构偏业务需求、背景、目标、成功指标、范围与约束

弱信号：

- 文件名含 `brd`
- 内容强调业务价值、stakeholder、现状量化

状态来源：

- 文档正文顶部状态表
- 若无统一元数据，则以文档内“初稿/已审核/已批准”为主

### 2. USER_JOURNEY

强信号：

- `TRACEABILITY-METADATA` 中 `artifact.type: USER_JOURNEY`
- `schema.profile: journey-profile-v1`
- 标题含 `Journey` / `User Journey`
- 含步骤流转、异常路径、边界情况、Mermaid 流程图

弱信号：

- 文件名含 `journey`、`user-journey`、`uc`

注意：

- 不要把单个页面流程说明误判成正式 User Journey 基线
- 若 metadata 存在，状态优先取 `artifact.status`

### 3. PRD

强信号：

- `TRACEABILITY-METADATA` 中 `artifact.type: PRD`
- `schema.profile: prd-profile-v1`

辅助信号：

- 标题含 `PRD`
- 有需求列表、验收标准、影响范围、追溯元数据块

状态来源：

- 优先 `artifact.status`
- 其次 `PRD 准出证书`
- 再次文档状态行

### 可选上下文：DOMAIN_MODEL

强信号：

- `TRACEABILITY-METADATA` 中 `artifact.type: DOMAIN_MODEL`
- 标题明确为“领域模型”或 `Domain Model`
- 同时包含团队共同使用的业务语言（Ubiquitous Language）、业务能力分类、业务模型适用边界（Bounded Context）和模型协作关系

弱信号：

- 文件名含 `domain-model`、`domain_model` 或“领域建模”

注意：

- 普通数据模型、数据库 ER 图或类图不能判为正式领域模型
- 该 artifact 是按复杂度触发的可选上下文，不参与主流程最早阻塞点计算
- API、HLD 和 LLD 在它存在时应读取；不存在时不得把它当成硬阻塞

### 4. API_CONTRACT

强信号：

- OpenAPI / AsyncAPI / GraphQL schema / `.proto` / 契约 index
- 标题或内容明确为 API Contract

弱信号：

- 文件名含 `openapi`、`swagger`、`asyncapi`、`contract`、`schema`、`proto`

注意：

- 不要把普通接口设计章节误判成正式 API Contract
- 没有 reviewer 或明确 `approved` 证据时，默认只算 `draft`

### 5. HLD

强信号：

- `TRACEABILITY-METADATA` 中 `artifact.type: HLD`
- `schema.profile: hld-profile-v1`

辅助信号：

- 标题含 `HLD`
- 内容包含架构决策、模块关系、风险、发布策略

### 6. TEST_STRATEGY

强信号：

- `TRACEABILITY-METADATA` 中 `artifact.type: TEST_STRATEGY`
- `schema.profile: test-strategy-profile-v1`

辅助信号：

- 标题含 `Test Strategy`
- 内容强调分层、范围、环境、入口/出口标准

### 7. LLD

强信号：

- `TRACEABILITY-METADATA` 中 `artifact.type: LLD`
- `schema.profile: lld-profile-v1`

辅助信号：

- 标题含 `LLD`
- 内容含模块设计、接口签名、伪代码、错误处理、测试设计

### 8. TEST_SPEC

强信号：

- `TRACEABILITY-METADATA` 中 `artifact.type: TEST_SPEC`
- `schema.profile: test-spec-profile-v1`

辅助信号：

- 标题含 `Test Spec` / `Test Package`
- 内容含测试矩阵、详细 case、环境数据、追溯矩阵

#### GainFactor-PM Automation Handoff（嵌入于 TEST_SPEC）

Guide 不把它当成独立 artifact，但在 `TEST_SPEC = approved` 时，应该额外检查文档中是否存在：

- 标题 `GainFactor-PM Automation Handoff`
- 或 YAML block 顶层 key 为 `gainfactor_pm_automation_handoff`

状态归一化：

| 原始信号 | 归一化结果 |
|----------|------------|
| `status: ready` | automation branch `ready` |
| `status: partial` | automation branch `partial` |
| `status: not_planned` | automation branch `not_planned` |
| section 缺失或无法解析 | automation branch `unknown` |

使用规则：

- `ready`：当用户目标涉及 GainFactor-PM 自动化时，可以直接推荐 `$case-writing`
- `partial`：可推荐 `$case-writing`，但要注明仍有 handoff 缺口
- `not_planned`：默认保持文档主线，不主动推荐 `$case-writing`
- `unknown`：若用户明确要 GainFactor-PM 自动化，优先回到 `$test-spec-writer` 补 handoff；必要时才以 `low confidence` 推荐 `$case-writing`

### 9. RUNBOOK

强信号：

- 标题含 `Runbook`
- 内容包含部署、回滚、监控、故障处理、值班信息

弱信号：

- 文件名含 `runbook`

### 10. PROTOTYPE

强信号：

- 存在 `_prototype-manifest.md`
- 存在 prototype 沙箱目录与 prototype 专属 README / 交付摘要

弱信号：

- 文件名或目录名含 `prototype`

注意：

- 原型是“目录级工件”，不能只凭单个 Markdown 文件判定

### 11. GUARDRAILS

强信号：

- 标题含 `Guardrails`
- 文档内容包含规则分级、例外流程、验证方式、下游钩子

弱信号：

- 文件名含 `guardrails`、`engineering-standards`

注意：

- 不要把单个 feature 的实现规范误判为项目级 Guardrails

## 审查证据识别

### 准出证书

识别为“强批准证据”的条件：

- 标题含 `准出证书`
- 或标题含 `certificate`
- 且正文明确写出 `通过` / `approved` / `准出`

### 审查报告

识别为“评审中/已评审未通过证据”的条件：

- 标题含 `审查报告`
- 或标题含 `review report`
- 且正文列出问题清单、P0/P1/P2、门禁结论

注意：

- “有审查报告”不等于“已批准”
- “审查报告 + 问题清单”通常更接近 `in_review`

## 候选选择与去重

同一 artifact 类型可能找到多个候选时，按以下顺序选“当前有效候选”：

1. `approved` 优先于 `in_review`
2. `in_review` 优先于 `draft`
3. 强证据优先于弱证据
4. 时间更新更晚者优先
5. 用户显式提供的路径优先

如果两个候选都像“当前有效版”，且会影响下一步推荐，必须使用宿主交互提问机制。

## 置信度规则

### High

满足任一：

- 有 `TRACEABILITY-METADATA` + 明确 `artifact.type`
- 有明确准出证书或 `artifact.status`
- 文档结构与文件名、目录上下文一致，且无冲突信号

### Medium

满足任一：

- 无元数据，但有清晰标题与结构证据
- 有审查报告但缺少统一状态字段
- 文件名和内容匹配度高，但缺少正式证书

### Low

满足任一：

- 只有文件名关键词
- 目录上下文弱匹配
- 存在多个冲突候选，暂未澄清

Guide 在 `low confidence` 下可以给建议，但必须显式标注并列出待确认项。

## 前端仓库识别（Prototype 分支）

以下信号可用于判断是否应展示 Prototype 分支：

强信号：

- 根目录存在 `package.json`
- 存在 `src/`、`app/`、`pages/`、`components/`
- 依赖中出现 React / Vue / Next.js / Nuxt / Vite / Angular

弱信号：

- 文档中频繁提到页面、路由、组件、交互状态
- 用户明确说“前端仓库”“页面原型”“UI 流程”

如果只有弱信号，Prototype 建议必须标注 `low confidence`。

## Guardrails 触发识别

Guide 不负责完整判断 Guardrails 内容是否过期，但可以用以下信号决定是否提示：

强触发：

- 用户明确提到架构/平台/合规/部署方式变化
- 用户明确提到事故复盘
- 仓库中反复出现 Guardrails 相关 reviewer 问题

弱触发：

- 项目已有多份设计文档，但无任何 Guardrails 基线
- 有 Guardrails 文件，但明显缺失规则分级、例外流程、下游钩子

弱触发只能作为补充建议，不要抢占主链路第一推荐。

## 禁止误判

- 不要把普通开发笔记当成 HLD/LLD 基线
- 不要把临时评审评论当成准出证书
- 不要把 feature-local 文档当成 Guardrails
- 不要因为文件名像 `spec` 就自动当成 Test Spec
