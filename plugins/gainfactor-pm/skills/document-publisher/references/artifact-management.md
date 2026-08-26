# 正式产物与门户管理

新建正式文档、确定产品或项目目录，或维护上游业务 Skill 时读取。已有外部文件不自动移动；保持原 slug 导入即可继续更新同一门户条目。

## 单一内容源

产品型产物统一放在：

```text
docs/gainfactor/{product-slug}/
├── product-definition.mdx
├── product-definition.portal.json
├── brd.mdx
├── brd.portal.json
├── prd.mdx
├── prd.portal.json
├── user-journey.mdx
├── user-journey.portal.json
├── user-persona.mdx
├── user-persona.portal.json
├── competitive-analysis.mdx
├── competitive-analysis.portal.json
├── product-metrics.mdx
├── product-metrics.portal.json
├── domain-model.mdx
├── domain-model.portal.json
├── api-contract.mdx
├── api-contract.portal.json
├── hld.mdx
├── hld.portal.json
├── lld.mdx
├── lld.portal.json
├── test-strategy.mdx
├── test-strategy.portal.json
├── test-spec.mdx
├── test-spec.portal.json
├── runbook.mdx
├── runbook.portal.json
├── guardrails.mdx
├── guardrails.portal.json
├── assets/{artifact-key}/
└── .work/
```

`product-slug` 只使用小写字母、数字和连字符，在首次产品定义时确定并冻结。非产品型文档把它替换为稳定 `{project-slug}`；无法确定主体时停止并向调用方取得名称，不使用 `general`、随机值或日期代替主体。

正文是内容源；同名 `.portal.json` 是可选首屏摘要，同名 `.review.json` 是可选结构化评审。图片进入 `assets/{artifact-key}/`，不发布的研究 sidecar 进入 `.work/`。不创建第二份人工文档索引。

正式文件名不带日期。版本、状态、更新时间和证据截止日期写入正文元信息、presentation 与门户 manifest；历史交给版本控制管理。

## 稳定身份

| artifact key | 正文 | route slug |
|---|---|---|
| `product-definition` | `product-definition.mdx` | `{product-slug}-product-definition` |
| `brd` | `brd.mdx` | `{product-slug}-brd` |
| `prd` | `prd.mdx` | `{product-slug}-prd` |
| `user-journey` | `user-journey.mdx` | `{product-slug}-user-journey` |
| `user-persona` | `user-persona.mdx` | `{product-slug}-user-persona` |
| `competitive-analysis` | `competitive-analysis.mdx` | `{product-slug}-competitive-analysis` |
| `product-metrics` | `product-metrics.mdx` | `{product-slug}-metrics` |
| `domain-model` | `domain-model.mdx` | `{product-slug}-domain-model` |
| `api-contract` | `api-contract.mdx` | `{product-slug}-api-contract` |
| `hld` | `hld.mdx` | `{product-slug}-hld` |
| `lld` | `lld.mdx` | `{product-slug}-lld` |
| `test-strategy` | `test-strategy.mdx` | `{product-slug}-test-strategy` |
| `test-spec` | `test-spec.mdx` | `{product-slug}-test-spec` |
| `runbook` | `runbook.mdx` | `{product-slug}-runbook` |
| `guardrails` | `guardrails.mdx` | `{product-slug}-guardrails` |

同一主体的文档使用 `{product-slug}` 导航组和产品显示名称作为 group title 与 collection。文件移动或人工迁移后继续使用原主体 slug 与 artifact key，不创建新身份。

## 生成门户

默认门户固定为工作区根目录的 `.gainfactor/portal`。它和 `.gainfactor-documents.json` 都是可由正式源文件重建的机器产物；不要在生成目录内手工维护正文。`.work/` 与 `.gainfactor/portal` 默认建议加入项目忽略规则，是否提交由项目自身政策决定。

标准产物省略 target，并让脚本统一计算 group、route 与 collection：

```bash
python3 <plugin-root>/scripts/create_document_portal.py \
  docs/gainfactor/{product-slug}/{artifact-key}.mdx \
  --subject-slug={product-slug} --subject-title="{产品名}" \
  --artifact={artifact-key}
```

预先检查解析结果时追加 `--dry-run`，该模式不得创建目录、复制模板或写 manifest。旧调用仍可显式传 target、slug、group 与 group title。
