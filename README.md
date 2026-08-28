# GainFactor-Plugins

GainFactor 的 Codex / ChatGPT 插件市场，为产品研究、需求分析、技术设计、测试与交付提供可复用的 AI 工作流。

当前收录 [`gainfactor-pm`](plugins/gainfactor-pm/README.md)：一套面向产品与研发团队的插件，包含 27 个 Skill，并提供本地文档阅读与评审门户。

## 快速开始

在 Codex 或 ChatGPT 的插件市场页面中：

1. 选择“添加插件市场”。
2. 在“来源”中填写 `https://github.com/GainFactor/GainFactor-Plugins`。
3. “Git 引用”留空以使用默认分支 `main`；如需固定版本，可填写对应标签或 Git 引用。
4. 添加市场后，安装 `gainfactor-pm`。

仓库级 Marketplace 清单位于 [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json)。添加整个仓库时，无需填写稀疏路径。

安装完成后，如果不确定从哪里开始，可以直接输入：

```text
$guide 扫描当前项目并推荐下一步
```

## gainfactor-pm 能做什么

`gainfactor-pm` 当前覆盖以下工作：

- **产品研究**：产品定义、用户画像、竞品分析与产品指标；
- **需求与交互**：BRD 访谈、用户旅程、PRD 编写与评审、交互原型设计与评审；
- **领域与技术设计**：领域建模、API Contract、HLD 与 LLD 的编写和评审；
- **测试与交付**：测试策略、测试规格、测试门禁评审与 Runbook；
- **项目治理**：项目 Guardrails 的编写与评审，以及 Skill 创建、优化和审计；
- **文档门户**：将产品与研发文档导入本地阅读、展示和评审门户。

插件聚焦产品研发文档与评审工作流，不包含测试平台中的 case 注册、pipeline 编排、trigger 或 execution 管理能力。完整的 Skill 清单、工作流、示例和能力边界见 [`plugins/gainfactor-pm/README.md`](plugins/gainfactor-pm/README.md)。

## 仓库结构

```text
.
├── .agents/plugins/marketplace.json       # 插件市场清单
├── plugins/
│   └── gainfactor-pm/
│       ├── .codex-plugin/plugin.json      # 插件元数据
│       ├── skills/                        # 27 个可调用 Skill
│       ├── scripts/                       # 校验、追溯与门户工具
│       ├── references/                    # 共享规范与契约
│       ├── assets/                        # 文档与原型评审资源
│       └── README.md                      # 插件完整文档
└── examples/
    └── prd-portal/                        # PRD 门户示例
```

## 本地开发与校验

基础要求：

- Python 3；
- 如需开发或构建文档门户，还需要 Node.js 与 pnpm。

从仓库根目录运行兼容性检查和测试：

```bash
python3 plugins/gainfactor-pm/scripts/validate_codex_compat.py
python3 -m unittest discover -s plugins/gainfactor-pm/scripts/tests -v
```

如本机已安装 OpenAI 的 `plugin-creator` skill，还可以运行插件结构校验：

```bash
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/gainfactor-pm
```

其中 `/path/to/plugin-creator` 需要替换为本机 `plugin-creator` skill 的实际目录。

## 参与贡献

提交变更前，请确保：

1. 变更范围只涉及对应的 Skill、脚本或共享契约；
2. 插件元数据与实际目录保持一致；
3. 上述兼容性检查和单元测试通过；
4. 新增或调整的能力已同步更新相关文档。

问题与改进建议可通过 [GitHub Issues](https://github.com/GainFactor/GainFactor-Plugins/issues) 提交。
