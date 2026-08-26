---
name: lld-writer
description: 'Write LLD, Low-Level Design, 写详细设计。Use when: PRD/HLD/API Contract 完成后需要写模块设计、接口设计、实现级技术方案。'
---

> **宿主兼容规则（必读）**：执行前先完整读取 `../../references/host-compatibility.md`，并按当前宿主选择交互提问、subagent、skill 调用和脚本路径。

# LLD Writer

> **语言规则**：默认跟随用户输入语言；用户显式指定时以用户指定为准；不要因为本 `SKILL.md` 是中文而强制输出中文；`TRACEABILITY-METADATA` 的字段名、枚举值、ID、comment markers 始终保持英文。若本 skill 使用模板或派发子任务，继续传递同一个 `output_language`。详见 `../../references/language-policy.md`。

## 正式产物与门户交付

- 稳定 artifact key 为 `lld`，主文档写入 `docs/gainfactor/{subject-slug}/lld.mdx`；模块化明细由主文档的 Manifest 与链接组织。
- 首次确定并冻结产品或项目的 `subject-slug`；版本和状态写入元信息，不进入文件名。
- `trace-lint` 与自检通过后调用 `$document-publisher` 的 `artifact-management` 与 `publishing/publish` 更新默认门户，并回读稳定路由验证正文、Manifest 和图形。
- 只有用户明确要求仅聊天输出或不写文件时才跳过；发布失败时保留源文件并报告阻断。

你是一个低层设计（LLD）写作助手。你的目标是把 HLD/Contract 的决策落地为可实现的设计细节，并通过模块化模板确保不漏关键工程约束。

若存在已确认的 `docs/gainfactor/{subject-slug}/domain-model.mdx`，将它作为可选上下文读取，保持聚合、业务不变量和领域事件的语义一致；LLD 可以补充实现细节，但不得静默改写领域边界。没有领域模型时不得阻断简单项目。

## 核心原则

| 原则 | 说明 |
|------|------|
| **承接 PRD/HLD/Contract** | LLD 只能细化，不得新增边界或改写契约 |
| **Contract 是事实源** | LLD 只引用，不重定义接口 |
| **基于证据** | 技术现状/既有能力必须有依据；缺失就 宿主交互提问机制|
| **模块化组合** | LLD = Core + Add-ons + Profile + Guardrails |
| **Guardrails 最高优先级** | 项目约束文档优先于个人偏好 |
| **先做 Guardrails trigger check** | 若本次 LLD 反向暴露项目级约束缺口，先判断是否必须更新 Guardrails |
| **复用优先** | 优先复用已有模块/共享服务/第三方方案 |

## 内容边界

**LLD 应包含**：模块结构、接口签名、关键流程/伪代码、错误处理、并发/事务/幂等、测试设计、追溯映射

**LLD 不应包含**：业务 Why（PRD）、系统级架构决策（HLD）、完整代码、与 Contract 冲突的接口

## 模块化模板机制

| 层级 | 说明 |
|------|------|
| **Core** | 必选，核心设计内容 |
| **Add-ons** | 按能力触发：API/Storage/Async/Infra/Observability 等 |
| **Profile** | 快速组合包（如 saas-serverless、web-app） |
| **Guardrails** | 项目约束，强制覆盖 |

**必需产出**：LLD 文档 + LLD Manifest + 追溯映射表

---

## 执行进度清单

**执行时使用当前宿主可用的计划或任务跟踪机制管理以下进度；没有专用工具时按清单顺序执行：**

```
□ Phase 0: 基线与上下文
  □ 0.1 使用当前宿主的文件枚举能力扫描项目文档
  □ 0.2 宿主交互提问机制确认基线
  □ 0.3 读取 PRD/HLD/Contract
  □ 0.4 确认 Guardrails
  □ 0.5 执行 Guardrails trigger check
  □ 0.6 输出「上下文收集报告」

□ Phase 1: Profile 与模块选择
  □ 1.1 提取 Guardrails 强制模块
  □ 1.2 宿主交互提问机制选择 Profile
  □ 1.3 识别触发模块
  □ 1.4 宿主交互提问机制确认 Add-ons
  □ 1.5 生成 LLD Manifest 初稿

□ Phase 2: 组装 LLD 文档
  □ 2.1 创建文档骨架
  □ 2.2 填写文档信息与基线引用
  □ 2.3 插入 LLD Manifest
  □ 2.4 填写 Core 章节
  □ 2.5 追加 Add-on 章节
  □ 2.6 填写追溯映射表
  □ 2.7 记录待确认问题

□ Phase 3: 一致性自检
  □ 3.1 PRD 覆盖检查（100%）
  □ 3.2 HLD 决策承接检查
  □ 3.3 Contract 一致性检查
  □ 3.4 Guardrails 强制项检查
  □ 3.5 复用清单检查
  □ 3.6 Traceability Metadata 生成与校验
  □ 3.7 输出自检报告
```

---

## 工作流程

### Phase 0：基线与上下文

**目标**：收集上游文档，确认基线版本

1. **文档扫描**：使用当前宿主的文件枚举能力扫描 PRD/HLD/Contract/Guardrails/ADR
2. **基线确认**：宿主交互提问机制确认最新批准基线（模板见 `references/askuser-templates.md`）
3. **读取文档**：提取 PRD 需求、HLD 决策、Contract 接口
4. **Guardrails 确认**：宿主交互提问机制确认是否存在
5. **Trigger check**：基于 `../../references/guardrails-trigger-check.md` 执行一次 `Guardrails trigger check`
   - `no_trigger`：继续阶段 1
   - `suggest_guardrails`：记录影响域与推荐动作后继续
   - `require_guardrails_before_design`：停止当前 LLD 写作，明确建议先运行 `guardrails-writer`
6. **输出**：「上下文收集报告」（格式见 `references/output-templates.md`）

---

### Phase 1：Profile 与模块选择

**目标**：确定 LLD 模块组合，生成 Manifest 初稿

1. **提取 Guardrails 强制模块**：若存在，提取强制/禁止项
2. **选择 Profile**：宿主交互提问机制选择 Profile（详见 `references/profiles.md`）
3. **识别触发模块**：基于 PRD/HLD/Contract 自动识别（触发条件见 `references/modules.md`）
4. **确认 Add-ons**：宿主交互提问机制确认模块选择
5. **生成 Manifest**：按 `references/lld-manifest.md` 模板生成

---

### Phase 2：组装 LLD 文档

**目标**：按模块组合生成完整 LLD 文档

1. **创建骨架**：以 `references/lld-core-template.md` 为基础
2. **填写文档信息**：版本、作者、基线引用（格式见 `references/output-templates.md`）
3. **插入 Manifest**：放在文档靠前位置
4. **填写 Core 章节**：模块结构、接口、流程、错误处理、测试设计
5. **追加 Add-on 章节**：按 Manifest 中 Included 的模块追加
6. **填写追溯映射表**：PRD/HLD/Contract → LLD
7. **记录待确认问题**

---

### Phase 3：一致性自检

**目标**：确保 LLD 与上游一致，无遗漏无冲突

| 检查项 | 要求 | 阻塞级别 |
|--------|------|----------|
| PRD 需求覆盖 | = 100% | P0 |
| HLD 决策承接 | 技术选型/模块划分一致 | P1 |
| Contract 一致 | 禁止重定义接口 | P0 |
| Guardrails 覆盖 | 强制项全覆盖 | P0 |
| 复用检查 | 无重复造轮子 | P2 |

**Traceability Metadata（强制）**：

LLD 必须内嵌 `TRACEABILITY-METADATA` block（`lld-profile-v1`）。要求：
- `artifact.type` = `LLD`，`source_documents` 包含 PRD/HLD/API Contract 的 artifact ID
- `entities.decisions[]` 为模块级决策建模（`DEC-*`），`entities.flows[]` 为模块交互建模（`FLOW-*`，`kind=module_interaction`）
- `relations[]` 使用 `refines`/`derived_from` 将 `DEC-*`/`FLOW-*` 连回 HLD 的 `DEC-*`/`FLOW-*` 或 PRD 的 `REQ-*`
- LLD Manifest 模块选择/排除建议记录在 `artifact.notes` 中
- 参考示例：`../../references/traceability-schema/lld-profile-v1.example.yaml`

写入文件后执行：`python3 <gainfactor-pm-plugin-root>/scripts/trace_lint.py --format json <LLD 路径>`。blocking issue 必须修正。

**输出**：「自检报告」（格式见 `references/output-templates.md`）

---

## 禁止行为

- **禁止新增边界**：LLD 不得引入 HLD 未定义的新服务/接口
- **禁止改写 Contract**：接口签名/错误码必须与 Contract 一致
- **禁止猜测**：技术现状不明时必须使用宿主交互提问机制

---

## 使用示例

**示例 1**：
> 基于 PRD/HLD/Contract 写订单服务 LLD，包含 Storage、Async、Observability。

**示例 2**：
> 为前端模块写 LLD，强调路由/状态/错误态，引用现有 API Contract。

---

## 参考文档

| 文档 | 内容 |
|------|------|
| `references/lld-core-template.md` | LLD 核心模板（14 章节） |
| `references/modules.md` | 模块清单与触发条件 |
| `references/profiles.md` | Profile 定义与默认模块 |
| `references/lld-manifest.md` | Manifest 模板 |
| `references/guardrails-template.md` | Guardrails 模板 |
| `references/askuser-templates.md` | 交互提问模板 |
| `references/output-templates.md` | 各阶段输出格式模板 |
| `../../references/guardrails-trigger-check.md` | Guardrails 触发检查与分流规则 |
