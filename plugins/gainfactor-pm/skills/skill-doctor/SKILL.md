---
name: skill-doctor
description: 'Create, update, refactor, or audit gainfactor-pm Skills by modeling their executable behavior. Use when: 需要创建或修改 Skill、恢复阶段/Gate/暂停恢复能力、进行双盲行为挑战，或只读审计 Skill 与插件契约。'
---

> **宿主兼容规则（必读）**：执行前完整读取 `../../references/host-compatibility.md`，按当前宿主选择计划、提问、文件操作与验证方式。

# Skill Doctor

> **语言规则**：默认跟随用户输入语言；稳定标识、文件名、命令和机器字段保持英文。详见 `../../references/language-policy.md`。

为 `gainfactor-pm` 创建、修改、重构或审计 Skill。核心目标不是让目录符合统一模板，而是让 Skill 在相同用户目标、输入和约束下，稳定产生预期的执行行为。

## 行为等价标准

创建或重构已有类型的 Skill 时，以以下能力是否保留为准，而不是比较章节、行数或文件数量：

- 阶段及依赖顺序；
- 可跟踪、可恢复的执行进度；
- Gate、最早停止、降级与升级处理；
- 用户确认点和不可代替用户作出的决策；
- 每阶段可检查的中间产物；
- 写入权限、副作用和角色边界；
- 正式输出、稳定路径与机器字段；
- 真实、可观察的验证方式；
- 下游消费者和交接契约。

允许重新设计措辞、章节和文件组织；不得用“更短”或“更清晰”解释关键行为缺失。没有参考实现的新 Skill，也要先形成同样完整的行为合同。

## 操作模式与权限

首先确定本次任务类型，后续 Phase 不得反向扩大权限：

| 任务 | 允许行为 | 默认禁止 |
|---|---|---|
| `create` | 新建目标 Skill 及必要集成与测试 | 顺手重构相邻 Skill |
| `update` | 修改目标 Skill 并同步直接契约 | 扩大公开 API 或职责 |
| `refactor` | 在证明行为无退化后重组实现 | 以结构优化替代行为验证 |
| `audit` | 只读取证、运行只读检查并报告 | 写文件、自动修复、借审计获得修改权 |

若用户从 audit 改为要求修复，重新确认任务合同与修改范围，再进入可写路径；不要把末尾审计视为隐含授权。

## 二维控制模型

每个目标 Skill 选择一个**角色主模式**和一个**主要执行拓扑**。角色说明它负责什么，拓扑说明工作怎样推进，两者不可互相代替。

角色主模式：门禁评审型、产物编写型、访谈发现型、工程执行型、流程导航型、研究综合型。

主要执行拓扑：线性阶段、串行 Gate、访谈循环、增量写入、工程闭环、Controller/Subagent、状态导航。

完整选择方法见 [角色模式、执行拓扑与阶段设计](references/role-and-topology-method.md)。辅助模式或嵌套拓扑只能在明确阶段内生效，必须写明开始、结束和不可接管的职责。

## 执行进度清单

复杂任务使用宿主计划机制同步状态；没有专用机制时维护以下清单。阶段完成后立即更新，暂停后从最早未满足的 Exit Criteria 继续，而不是默认回到 Phase 0。

```text
□ Phase 0：建立任务契约与权限边界
□ Phase 1：提取目标行为并选择参考样本
□ Phase 2：选择角色模式与执行拓扑
□ Phase 3：设计 Skill 行为合同和文件结构
□ Phase 4：创建或修改（audit 跳过）
□ Phase 5：结构审计、语义审计与双盲挑战
□ Phase 6：插件验证与交付
```

进度清单是恢复协议，不是正文摘要。仅当它无法映射 Phase、不能跟踪状态或逐句复制正文时才需要调整。

## Phase 0：建立任务契约与权限边界

**Goal**：明确本次究竟要创建、修改、重构还是只读审计，以及什么结果才算完成。

**Inputs**：用户目标与约束、目标 Skill 或拟创建目录、工作区规则和已有修改、允许写入范围。

**Actions**

1. 写出典型请求、不适用请求和预期用户结果。
2. 明确输入、正式输出、副作用、稳定路径和下游消费者。
3. 仅对会改变职责、权限或产物的高影响歧义请求用户确认。
4. 对 update/refactor 记录改前测试与公开契约；对 audit 固定只读边界。

**Intermediate Deliverable**：任务合同，包括任务类型、目标范围、非目标、允许副作用、成功标准和待确认事项。

**Exit Criteria**：执行者能够判断哪些文件可改、哪些行为必须保持，以及如何观察完成。

**Stop / Escalation**：目标主体、修改授权或关键约束不明时停止并请求决定，不用假定替代授权。

**Resume**：回读任务合同和用户新增决定，从仍未明确的条目继续。

## Phase 1：提取目标行为并选择参考样本

**Goal**：先理解 Skill 要控制的真实工作，再选择近似样本；不从文件模板倒推行为。

**Inputs**：Phase 0 任务合同；目标 Skill、已路由资源、scripts、tests 和调用方，或新建任务简报与相邻契约。

**Actions**

1. 提取阶段、Gate、确认点、中间产物、停止恢复、正式输出、验证和下游关系。
2. 找出相邻 Skill 的职责边界，避免 Reviewer/Writer、Interviewer/Writer 或 Navigator/Builder 越权混合。
3. 需要借鉴时完整读取 [参考样本路由](references/sample-routing.md)，选择最接近的 2–3 个允许样本，再完整读取其 `SKILL.md` 和本任务确需的 reference。
4. 双盲挑战中目标 Skill 保持隐藏，不能同时作为参考样本；候选完成后才打开目标比较。

**Intermediate Deliverable**：改前行为清单或新建目标行为假设，以及样本选择理由。

**Exit Criteria**：每项核心行为都有用户约束、目标现状、插件契约或样本证据；未知项已标记。

**Stop / Escalation**：职责冲突、目标无法隔离或关键事实缺失且会改变设计时停止；不用常见模板补证据。

**Resume**：从未完成的行为项或新获得的事实源继续，不重新加载无关样本。

## Phase 2：选择角色模式与执行拓扑

**Goal**：确定谁控制工作、工作怎样推进，以及辅助行为在哪里开始和结束。

**Inputs**：Phase 1 行为清单和 [角色模式、执行拓扑与阶段设计](references/role-and-topology-method.md)。

**Actions**

1. 根据成功结果和权限选择一个角色主模式。
2. 根据依赖、循环、Gate、写入节奏和恢复需要选择一个主要执行拓扑。
3. 辅助模式或嵌套拓扑必须写明生效 Phase、结束 Phase、输入输出和不可接管职责。
4. 判断是否需要进度清单、Phase、Gate 和确认点；复杂度不足时不为形式添加。

**Intermediate Deliverable**：主模式、主要拓扑、有限辅助行为、阶段关系和角色边界。

**Exit Criteria**：控制模型能解释全部目标行为，没有模式替代权限、拓扑替代角色或无边界混合。

**Stop / Escalation**：若需要两个独立主角色才能成立，先判断是否拆成相邻 Skill；未经确认不扩大范围。

**Resume**：从有冲突的职责或拓扑节点继续，保留已证实选择。

## Phase 3：设计 Skill 行为合同和文件结构

**Goal**：把目标行为转换为可执行、可暂停恢复、可验证的 Skill 设计。

**Inputs**：任务合同、行为清单、控制模型和 [行为合同与双盲评估](references/behavior-equivalence.md)。

**Actions**

1. 形成内部行为合同，至少记录典型/不适用请求、事实源优先级、权限、副作用、Phase 顺序、确认点、Gate、停止降级恢复、中间产物、正式输出、验证和下游字段。
2. 为必要 Phase 定义 Goal、Inputs、Actions、Intermediate Deliverable、Exit Criteria、Stop/Escalation 和 Resume；简单 Skill 可采用轻结构，但不能丢失实际控制点。
3. 每次执行都需要的角色边界、Phase、Gate、停止恢复和完成条件保留在 `SKILL.md`。
4. 仅把特定协议、交付类型或互斥分支才需要的 substantial 内容放入 reference；总是一起读取的短文件合并。简单 Skill 可以没有 references。
5. 只添加真正需要的 scripts、assets、agents 元数据和测试。

**Intermediate Deliverable**：行为合同、文件职责表和预期测试/挑战清单。

**Exit Criteria**：每个文件有清晰触发条件；入口足以控制常规执行；拆分确实减少无关上下文且导航成本可接受。

**Stop / Escalation**：无法证明改前后关键行为一致时，不做破坏性重组；改变公开调用或稳定字段前先获授权。

**Resume**：从行为合同中最早未闭合的行为继续，不从目录重新设计。

## Phase 4：创建或修改

**Goal**：以最小改动实现行为合同，并保持直接契约同步。

**Inputs**：Phase 3 行为合同、文件职责表、目标目录和工作区已有修改。

**Actions**

1. `audit` 跳过本 Phase，继续保持只读。
2. `create` 只创建实际需要的入口、UI 元数据、references、assets、scripts 和 tests。
3. `update` 只修改目标行为及直接依赖；`refactor` 先保留基线，再移动或合并内容。
4. 同步 frontmatter、`agents/openai.yaml`、本地链接、调用方和契约测试。
5. 清理本次修改产生的孤立文件或重复内容，不处理无关遗留问题。

**Intermediate Deliverable**：可审计的候选实现及变更范围清单。

**Exit Criteria**：所有改动可追溯到行为合同，audit 没有写入，用户已有修改未被覆盖。

**Stop / Escalation**：遇到脏工作区重叠、未知调用方或新权限时暂停，不重置、覆盖或顺手迁移。

**Resume**：从未完成的行为合同条目和当前 diff 继续，先确认外部修改是否改变基线。

## Phase 5：结构审计、语义审计与双盲挑战

**Goal**：分别证明文件结构有效和执行行为完整；结构脚本不得替代语义判断。

**Inputs**：候选实现或 audit 目标、Phase 3 行为合同和 [行为合同与双盲评估](references/behavior-equivalence.md)。

**Actions**

1. 运行只读结构检查：

   ```bash
   python3 scripts/audit_skill.py <skill-directory> --pattern <declared-context>
   ```

   `--pattern` 只是调用方声明的上下文；脚本只检查 frontmatter、UI、路径、reference 可达性、Skill 调用、Phase ID 和统计信息，不提供语义准出。
2. 语义审计逐项检查真实依赖顺序、Gate、用户决策、越权、停止恢复、中间产物、正式输出、验证和下游消费。
3. create/refactor 或高风险 update 执行双盲挑战：只给原始任务简报和约束，候选完成后再打开保留目标，逐项比较行为合同。
4. audit 只报告证据、影响和建议；可写任务只修复本次范围内问题并重新验证。

**Intermediate Deliverable**：结构报告、语义行为差异表、双盲挑战结果和问题处理清单。

**Exit Criteria**：没有结构 error；行为合同核心项无缺失；warning 已处理或有理由。核心 Phase、Gate、确认点、中间产物、权限、恢复、正式输出、可观察验证或下游契约任一缺失，双盲即失败。

**Stop / Escalation**：结构通过但语义证据不足时不得宣称通过。目标不能用自己的说明自证；目标泄露后降级为普通对照。

**Resume**：从差异表中最早的行为缺口继续；已通过结构项无需重复推理。

## Phase 6：插件验证与交付

**Goal**：证明候选 Skill 能被插件加载、执行和维护，并交付关键设计决策。

**Inputs**：Phase 5 候选实现与审计证据、插件校验脚本和相关契约测试。

**Actions**

1. 运行 Skill 快速校验、`validate_codex_compat.py --all-plugins`、相关 Python 契约测试和 `git diff --check`。
2. 工程执行型还需真实运行；门禁评审型挑战最早停止与严重度；访谈型挑战增量提问和恢复；导航型挑战事实归一化；研究型挑战事实/推断边界。
3. 回看 diff，确认没有越界、孤立资源和无依据的契约变化。
4. 输出任务类型、控制模型、关键决策、修改范围、验证证据、保留 warning 和人工判断项。

**Intermediate Deliverable**：插件级验证记录和用户可复核的交付摘要。

**Exit Criteria**：相关测试通过，完成标准可观察，交付没有用“结构更清晰”替代证据。

**Stop / Escalation**：插件验证失败、真实运行不可用或下游契约未确认时不宣称完成；报告阻塞和恢复位置。

**Resume**：从失败验证对应的最早 Phase 继续；只重跑受影响检查。

## 渐进式披露尺度

- 不设置行数准出线；行数只作为统计信息。
- 每次执行都需要的控制协议留在 `SKILL.md`，即使入口因此较长。
- reference 必须有独立触发条件，并实质减少当前任务的无关上下文。
- 多个短文件若总是一起读取，应合并；几十行内容不因“渐进式”自动拆文件。
- 大文件优先使用目录、明确标题和检索词改善定位。
- 同时衡量上下文收益与导航成本；文件越多不代表设计越好。

## 结果严重度

- `error`：误路由、越权、不可执行、结构失效或稳定契约冲突；
- `warning`：行为控制、渐进式组织或维护性风险；
- `note`：不阻断正确性的改进机会。

自动脚本只产生结构证据。语义结论必须说明对应行为合同、真实证据和影响。
