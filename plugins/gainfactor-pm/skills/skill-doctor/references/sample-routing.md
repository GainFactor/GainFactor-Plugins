# 参考样本路由

本文件仅在 Phase 1 需要比较现有做法时读取。每次选择最接近的 2–3 个样本，完整读取其入口和当前任务必需的 reference；不要一次加载全部样本。

## 选择顺序

1. 先匹配成功结果和写入权限；
2. 再匹配主要执行拓扑；
3. 最后匹配 artifact、Gate 或宿主环境；
4. 记录为什么选、借鉴什么、哪些不能照搬；
5. 双盲目标不得出现在参考集合中。

## 门禁评审型

- `api-reviewer`：串行契约 Gate、finding 和 review sidecar；
- `lld-reviewer`：多层技术依赖、最早阻断和复审；
- `test-strategy-reviewer`：策略覆盖、严重度和准出；
- `prototype-reviewer`：真实交互、视觉证据和可观察验收；
- `hld-reviewer`、`test-reviewer`、`guardrails-reviewer`：相应边界与交付物差异。

## 产物编写型

- `api-writer`：上游模型、稳定契约和下游消费；
- `lld-writer`：阶段产物、追溯和工程交接；
- `test-spec-writer`：覆盖映射、用例结构和自检；
- `hld-writer`：架构边界与高影响决策；
- `prd-writer`：业务事实、用户选择和正式 artifact；
- `guardrails-writer`、`test-strategy-writer`：治理或测试策略差异。

## 访谈发现型

- `brd-interviewer`：多轮业务发现、确认点、正式结论和流程交接；
- `uc-interviewer`：用户旅程、缺口提问、场景确认和恢复。

## 工程执行型

- `prototype-designer`：环境探查、修改边界、隔离实现与真实浏览器验收。

同型样本只有一个时，再选择具有相同拓扑的 Writer 或 Reviewer 比较 Gate 与中间产物，不用不相干领域凑数量。

## 流程导航型

- `guide`：机器事实源、artifact 识别、状态归一化、最早阻塞和少量推荐。

可对照 Reviewer 的最早停止或 Writer 的稳定 artifact，但不可让 Navigator 生产或批准产物。

## 研究综合型

- `user-persona`：独立研究输入、阶段门禁、综合边界、正式报告和下游复用。

可补充 Interviewer 的确认循环或 Writer 的正式产物行为，但不能把模拟信息升级为事实。

## Controller/Subagent 拓扑

- `runbook-writer`：Controller 准备上下文、隔离执行、独立审查、有限修复和最终汇总。

Controller/Subagent 是执行拓扑，不是第七种角色；仍需确定最终负责角色。

## 使用边界

- 样本提供行为证据，不是章节模板。
- 目标当前实现可用于 update/refactor 的改前合同，但不能在双盲创建阶段作为参考。
- 不从未列入本路由的 Skill 提炼方法经验。
- `skill-doctor` 不能作为自己的准出样本；自审依赖行为合同、结构报告和外部挑战。
