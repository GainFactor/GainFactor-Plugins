#!/usr/bin/env python3
"""Contract tests for the optional domain-modeling workflow."""

from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = PLUGIN_ROOT / "skills/domain-modeler"


class DomainModelerSkillTest(unittest.TestCase):
    def test_execution_protocol_is_trackable_and_resumable(self) -> None:
        entry = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phase in range(7):
            self.assertIn(f"## Phase {phase}", entry)
            self.assertIn(f"□ Phase {phase}", entry)
        for field in (
            "Goal",
            "Inputs",
            "Actions",
            "Intermediate Deliverable",
            "Exit Criteria",
            "Stop / Escalation",
            "Resume",
        ):
            self.assertGreaterEqual(entry.count(field), 7)
        self.assertIn("每轮只问 2–3 个会改变模型的问题", entry)
        self.assertIn("从最早未满足的 Exit Criteria 恢复", entry)

    def test_behavior_contract_covers_evidence_permissions_and_downstream_delivery(self) -> None:
        entry = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("输入与证据优先级", entry)
        self.assertIn("不替代 BRD", entry)
        self.assertIn("不决定 API、数据库、微服务、部署或技术选型", entry)
        self.assertIn("docs/gainfactor/{subject-slug}/domain-model.mdx", entry)
        self.assertIn("回读稳定路由", entry)
        self.assertIn("BRD、User Journey、PRD、API、HLD 和 LLD", entry)

    def test_domain_discrimination_precedes_user_interview(self) -> None:
        entry = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("分析优先、沟通后置", entry)
        self.assertIn("领域区分 Gate", entry)
        self.assertIn("不得开始领域访谈", entry)
        self.assertIn("初步判断、证据和待确认冲突", entry)
        self.assertLess(
            entry.index("## Phase 1：区分业务领域与候选模型边界"),
            entry.index("## Phase 2：在选定领域内还原场景与共同语言"),
        )

    def test_skill_has_progressive_references_and_clear_scope(self) -> None:
        entry = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for reference in (
            "references/ubiquitous-language.md",
            "references/bounded-contexts.md",
            "references/building-blocks.md",
            "references/domain-events.md",
            "references/repositories-factories.md",
            "references/strategic-design.md",
        ):
            self.assertIn(reference, entry)
            self.assertTrue((SKILL_ROOT / reference).is_file())
        self.assertIn("简单 CRUD", entry)
        self.assertIn("不是主流程硬门禁", entry)
        self.assertIn("docs/gainfactor/{subject-slug}/domain-model.mdx", entry)
        self.assertIn("评分：10 分制", entry)
        self.assertIn("快速诊断", entry)

    def test_skill_uses_readable_bilingual_ddd_terms(self) -> None:
        content = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [SKILL_ROOT / "SKILL.md", *sorted((SKILL_ROOT / "references").glob("*.md"))]
        )
        for term in (
            "团队共同使用的业务语言（Ubiquitous Language，行业常称“通用语言”）",
            "业务模型适用边界（Bounded Context，行业常称“限界上下文”）",
            "一致性单元（Aggregate，行业称“聚合”）",
            "唯一修改入口（Aggregate Root，行业称“聚合根”或“根实体”）",
            "核心域（Core Domain）",
            "始终必须成立的业务规则（Invariant）",
            "已经发生的重要业务事实（Domain Event，行业称“领域事件”）",
            "外部模型转换层（Anti-Corruption Layer, ACL，行业称“防腐层”）",
            "领域对象的读取与保存接口（Repository，行业称“仓储”）",
            "复杂业务对象的创建规则（Factory，行业称“工厂”）",
            "可复用、可组合的业务判断条件（Specification，行业称“规约”）",
        ):
            self.assertIn(term, content)
        self.assertNotIn("software-design-philosophy", content)
        self.assertNotIn("clean-architecture", content)
        self.assertNotRegex(content, r"(?m)^(author|license):")

    def test_six_stage_flow_and_ten_point_score_are_preserved(self) -> None:
        entry = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        headings = (
            "### 1. 团队共同使用的业务语言（Ubiquitous Language，行业常称“通用语言”）",
            "### 2. 业务模型的适用边界与协作关系",
            "### 3. 业务对象、业务值与一致性单元",
            "### 4. 已经发生的重要业务事实",
            "### 5. 领域对象的保存、创建与业务条件表达",
            "### 6. 识别核心业务能力并分配投入",
        )
        positions = [entry.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("快速诊断”的 7 项", entry)
        self.assertIn("再评估 3 项模型深度", entry)
        self.assertIn("9–10 分", entry)

    def test_score_output_is_plain_language_and_evidence_based(self) -> None:
        entry = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(
            "| 白话检查问题 | 对应 DDD 术语 | 得分 | 证据 | 未通过时的修正建议 |",
            entry,
        )
        for question in (
            "一组对象能否在一次业务操作后保持有效，并且存在唯一修改入口？",
            "跨一致性单元的协作是否通过重要业务事实传递？",
            "外部系统的数据进入本地前是否先转换成自己的业务模型？",
        ):
            self.assertIn(question, entry)

    def test_reference_titles_use_plain_language_first(self) -> None:
        expected_titles = {
            "ubiquitous-language.md": "# 团队共同使用的业务语言",
            "bounded-contexts.md": "# 业务模型的适用边界与协作关系",
            "building-blocks.md": "# 业务对象、业务值与一致性单元",
            "domain-events.md": "# 已经发生的重要业务事实",
            "repositories-factories.md": "# 领域对象的保存、创建与业务条件表达",
            "strategic-design.md": "# 识别核心业务能力并分配投入",
        }
        for filename, title in expected_titles.items():
            content = (SKILL_ROOT / "references" / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertTrue(content.startswith(title))
                self.assertNotIn("## 反模式", content)

    def test_hard_terms_are_explained_on_first_use(self) -> None:
        checks = {
            "building-blocks.md": {
                "聚合根": "唯一修改入口（Aggregate Root，行业称“聚合根”或“根实体”）",
            },
            "repositories-factories.md": {
                "仓储": "领域对象的读取与保存接口（Repository，行业常称“仓储”）",
                "规约": "可复用、可组合的业务判断条件（Specification，行业常称“规约”）",
            },
        }
        for filename, terms in checks.items():
            content = (SKILL_ROOT / "references" / filename).read_text(encoding="utf-8")
            for term, explained_form in terms.items():
                with self.subTest(filename=filename, term=term):
                    self.assertIn(explained_form, content)
                    self.assertEqual(
                        content.index(term),
                        content.index(explained_form) + explained_form.index(term),
                    )

    def test_guide_routes_domain_model_as_optional_context(self) -> None:
        guide = (PLUGIN_ROOT / "skills/guide/SKILL.md").read_text(encoding="utf-8")
        workflow = (PLUGIN_ROOT / "skills/guide/references/workflow-map.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("可选分支：领域建模", guide)
        self.assertIn("- id: DOMAIN_MODEL", workflow)
        self.assertIn("creation_command: $domain-modeler", workflow)
        self.assertIn("DOMAIN_MODEL: preferred_if_exists", workflow)
        self.assertIn("- BRD: approved_or_exists", workflow)
        domain_node = workflow.split("  - id: domain-modeler", 1)[1].split("\n  - id:", 1)[0]
        self.assertNotIn("PRD: approved", domain_node)

    def test_brd_can_start_domain_modeling_before_prd(self) -> None:
        brd = (PLUGIN_ROOT / "skills/brd-interviewer/SKILL.md").read_text(encoding="utf-8")
        template = (PLUGIN_ROOT / "skills/brd-interviewer/assets/brd-template.md").read_text(
            encoding="utf-8"
        )
        workflow = (PLUGIN_ROOT / "skills/guide/references/workflow-map.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("领域建模触发检查", brd)
        self.assertIn("直接发起 `$domain-modeler`", brd)
        self.assertIn("Domain Modeling Handoff", template)
        self.assertIn("业务模型边界不清", template)
        self.assertNotIn("聚合", template)
        self.assertNotIn("仓储", template)
        brd_node = workflow.split("  - id: brd-interviewer", 1)[1].split("\n  - id:", 1)[0]
        self.assertIn("next: [domain-modeler, uc-interviewer]", brd_node)

    def test_downstream_writers_consume_but_do_not_require_model(self) -> None:
        for skill in ("uc-interviewer", "prd-writer", "api-writer", "hld-writer", "lld-writer"):
            text = (PLUGIN_ROOT / f"skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                self.assertIn("domain-model.mdx", text)
                self.assertIn("可选上下文", text)
        workflow = (PLUGIN_ROOT / "skills/guide/references/workflow-map.yaml").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("- DOMAIN_MODEL: approved", workflow)

    def test_publisher_registers_domain_model_artifact(self) -> None:
        publisher = (PLUGIN_ROOT / "scripts/create_document_portal.py").read_text(encoding="utf-8")
        management = (
            PLUGIN_ROOT / "skills/document-publisher/references/artifact-management.md"
        ).read_text(encoding="utf-8")
        self.assertIn('"domain-model":', publisher)
        self.assertIn("`domain-model`", management)


if __name__ == "__main__":
    unittest.main()
