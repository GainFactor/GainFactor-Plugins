---
name: define-product
description: Create or maintain a reusable PRODUCT_DEFINITION for a new idea or an already-released product, including consumer, enterprise, and internal efficiency products. Use guided clarification for new products and evidence-backed web research for released products or published parent products. Use when product context is missing before persona, competitive, market, or requirements work. Do not use for detailed feature, interaction, technical, metric, or delivery design.
---

> **宿主兼容规则（必读）**：执行前完整读取 `../../references/host-compatibility.md`，并按当前宿主选择交互提问、联网检索和文件操作方式。

# Define Product

> **语言规则**：默认跟随用户输入语言；用户显式指定时以用户指定为准。稳定 artifact type 使用 `PRODUCT_DEFINITION`。详见 `../../references/language-policy.md`。

形成一份可被用户画像、竞品分析、市场研究和需求工作复用的产品定义。产品定义回答三个问题：**给谁用、解决什么问题、为什么是这个产品**。

本 Skill 定义产品，不展开详细功能、交互、技术方案、完整指标体系或项目排期。不要替用户决定新产品方向，也不要把公开营销表述当作已证实效果。

## 执行流程

先完整读取 `references/definition-flow.md`，严格执行其中唯一的产品定义流程：

1. **读取已有上下文**：提取用户已经给出的产品名称、产品状态和既有定义；已确认的信息不重复询问。
2. **选择信息获取方式**：新产品通过对话确认；现有产品通过联网检索确认。这里不产生两套业务流程。
3. **执行统一定义流程**：依次完成基础信息、用户与问题、核心机制与差异、角色关系、场景边界、采用循环与商业模式、一致性检查。新产品提问必须遵守流程中的“对话与参考选项规则”；涉及 AI 时必须执行固定 AI 确认子流程。
4. **形成三维定义**：回答给谁用、解决什么问题、为什么是这个产品，并处理高影响冲突与缺口。
5. **确定状态**：新产品需要用户最终确认；现有产品依据对象唯一性、证据和冲突情况确定 `confirmed` 或 `draft`。
6. **自动写入并启动预览**：直接形成最终门户正文，调用 `$document-publisher` 以 `previewed` 为终点写入并启动门户预览，不执行正式 release 或 Full。
7. **门户文档确认**：把可访问的文档页面交给用户检查，收到确认后才完成产品定义交付。
8. **可选下游任务**：门户文档确认后，满足条件时才询问是否继续定义产品指标。

每次回复前先判断当前处于哪个状态，只执行当前状态需要的动作。没有满足阶段完成条件时不得进入下一阶段；用户提前提供后续信息时先记录，到对应阶段复用。

## 参考文件路由

只保留三个职责清楚的参考文件：

| 文件 | 读取时机 | 唯一职责 |
|---|---|---|
| `references/definition-flow.md` | 每次执行开始时 | 唯一业务流程；包含各阶段确认项及产品类型、关系、AI、采用和商业模式规则 |
| `references/research-evidence.md` | 对象是现有产品，或存在现有母产品时 | 联网检索、对象消歧、来源可信度、证据状态和存疑处理 |
| `references/output-contract.md` | 进入一致性与最终定义阶段时 | 文档结构、状态判定、质量门禁和最终输出契约 |

参考文件之间不建立平行业务流程。`research-evidence.md` 取得的信息必须返回 `definition-flow.md` 当前阶段；同一任务内文件未变化时不重复读取。

已有 `PRODUCT_DEFINITION` 时，先读取现有状态。更新时展示变化及下游影响，只重新执行受影响的统一流程阶段；校验时检查证据时效、一致性和准出项。未经用户要求不覆盖已有定义。

## 信息纪律

始终区分：

- `已确认`：用户明确确认，或可靠且无冲突的材料／公开证据；
- `明确排除`：用户明确不做的范围；
- `当前理解`：基于已有信息形成、等待确认的解释；
- `待定义`：尚无足够信息，或只有工作假设；
- `待确认冲突`：两个不能同时成立的定义或证据。

不得把推断写成事实，不得重新引入已排除范围。发现冲突时展示双方和影响，让用户决定；分析外部已发布产品时，无法解决的冲突保留在文档中。

## 输出

输出前完整读取 `references/output-contract.md`，按其中结构生成 `PRODUCT_DEFINITION`。

- 新产品只有通过准出检查并由用户确认后，状态才为 `confirmed`。
- 已发布产品只有对象明确、核心字段有可靠证据且关键冲突已解决时，状态才为 `confirmed`。
- 其他情况交付 `draft`，明确缺口及其影响。

业务定义通过质量门禁后，进入门户正文成稿阶段。调用 `$document-publisher` 后按其 Shortcut 路由：完整正文成稿读取 `authoring-workflow`，只读取实际选用组件的参考，发布或更新读取 `publishing/publish`，启动或检查预览读取 `publishing/preview`；不要批量预读全部 references。先形成必要的页面蓝图，再直接写出最终门户正文，不得先生成朴素 Markdown 再交给发布 Skill 二次转换。

- 首次定义产品时确定并冻结 `{product-slug}`，正式正文固定写入 `docs/gainfactor/{product-slug}/product-definition.mdx`；目录、route 与门户位置遵守 `$document-publisher` 的 `artifact-management`。
- 只有首屏摘要能明显改善扫读时，才生成同名 `.portal.json`；其中不得出现正文没有的新事实。
- 每一种增强表达都必须服务于明确的阅读任务。正文必须可独立阅读，关键结论不能只存在于图表、组件或门户清单中。
- 不追求组件数量。短段落或普通表格已经足够清晰时，保持简单表达。
- 选择 AntV Infographic 时，必须先读取 `$document-publisher` 对应的语法参考；不确定语法或渲染能力时使用稳定回退表达。

### 自动交付与用户确认（默认执行）

产品定义通过质量门禁后，默认连续完成以下动作，不询问用户是否生成文档、写入门户或启动预览：

1. 按页面蓝图直接形成完整的最终门户正文；根据实际表达使用 Markdown 或 MDX，不生成等待后续转换的中间版本。
2. 调用 `$document-publisher`，以 artifact key `product-definition` 写入工作区统一门户；布局使用 `report`，导航标题使用“产品定义”。group、collection、route 和默认 `.gainfactor/portal` 由发布器统一解析。
3. 用户显式指定兼容门户时沿用该 target；否则使用工作区统一门户，不创建产品专属或随机临时门户，也不为选择门户重复提问。
4. 从实际门户路由读回正文，校验标题、章节、元信息、关键结论和可选首屏呈现均已正确写入。
5. 按 `$document-publisher` 的预览流程启动目标门户；若正确门户已经运行则复用。取得实际访问地址并确认页面可访问后，再把链接交给用户。
6. 请用户检查门户中的内容完整性、表达清晰度和页面呈现，并明确询问：“请查看门户文档；内容和呈现是否可以确认，还是需要修改？”此确认不能在启动或访问验证前询问。

用户提出修改时，根据反馈更新最终正文，重新写入同一稳定 slug，执行读回与页面验证，并再次请求确认。用户明确确认后，产品定义交付才完成，随后才能进入“可选下一步：产品指标”。

启动服务必须是非阻塞的，不得因为前台服务占用而无法继续请求用户确认。不能只返回预期端口或拼接地址；必须以实际启动结果和页面访问验证为准。

只有用户明确要求“仅在对话中输出”“不要写入门户”“不要启动预览”或给出其他交付方式时，才按其要求缩减自动交付。写入前确保目标门户和发布实现使用的目录处于当前任务允许的范围内；写入或启动失败时说明具体阻塞并保留已经成功形成的最终正文，不伪造访问地址，也不把未验证页面交给用户确认。

### 可选下一步：产品指标

门户文档已经由用户确认后，若 `Subject Relationship: own` 且核心用户、问题和价值机制足以支撑衡量，只询问一次：“产品定义已经完成，是否继续基于这份定义建立产品指标体系？”提供“继续定义产品指标”和“暂不继续”两个选择。

- 用户选择继续时调用 `$product-metrics`，传入当前 `PRODUCT_DEFINITION` 和门户路由；不得重复询问其中已经确认的定位、角色、场景、价值结果、商业模式或失败边界。
- 用户暂不继续时结束当前流程，不影响已完成的产品定义。
- `analysis-target`、存在高影响核心冲突，或用户已明确只需要产品定义时，不主动提供该选项；用户仍可显式调用 `$product-metrics`。
- 这是新的下游任务选择，不是文档生成或发布确认；产品定义仍按前述规则自动写入门户。

## 下游复用契约

下游任务把 `已确认` 的定位、用户、问题、机制和边界作为事实基线，不重复询问、不静默改写。`$product-metrics` 还应复用可观察结果、角色关系、生命周期、商业模式与失败边界，只补充战略目标、候选指标、数据能力、基线和阈值依据等指标专属信息。新证据与定义冲突时，列出冲突并请求确认。除明确要求它作为门禁的下游 Skill 外，`PRODUCT_DEFINITION` 是可选上下文。
