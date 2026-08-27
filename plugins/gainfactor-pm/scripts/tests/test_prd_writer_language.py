#!/usr/bin/env python3
"""Behavior contracts for readable Chinese PRD authoring."""

from __future__ import annotations

import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).parent.parent.parent
WRITER_ROOT = PLUGIN_ROOT / "skills/prd-writer"
ASSET_ROOT = WRITER_ROOT / "assets"
REVIEWER_ROOT = PLUGIN_ROOT / "skills/prd-reviewer"


class PrdWriterLanguageTest(unittest.TestCase):
    def test_writer_translates_domain_terms_before_using_them_in_prd(self) -> None:
        text = (WRITER_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in (
            "模型边界、领域事件和能力名称必须先转换",
            "不得用领域名称直接命名页面或功能模块",
            "不依赖领域模型或 metadata",
            "产品端、页面、区域、控件和业务对象",
        ):
            self.assertIn(expected, text)

    def test_ui_template_describes_page_conditions_content_actions_and_results(self) -> None:
        text = (ASSET_ROOT / "new-feature-ui.md").read_text(encoding="utf-8")
        for expected in (
            "### 5.X [页面名称]",
            "页面区域与展示内容",
            "| 页面区域 | 展示内容 | 信息来源 | 显示条件 |",
            "用户操作与页面反馈",
            "| 触发条件 | 用户操作 | 页面反馈 | 操作后变化 |",
            "| 页面状态 | 触发条件 | 展示内容 | 可用操作 |",
        ):
            self.assertIn(expected, text)
        self.assertNotIn("### 5.X [模块/页面名称]", text)
        self.assertNotIn("| 元素 | 交互 | 结果 |", text)

    def test_writer_instructions_use_direct_chinese_without_changing_workflow(self) -> None:
        text = (WRITER_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for expected in (
            "只写有依据的现状",
            "只确认关键问题",
            "根据状态使用文档",
            "主体、动作、对象、适用条件和结果",
            "阶段零：上下文收集（强制）",
            "阶段四：强制审查",
        ):
            self.assertIn(expected, text)
        self.assertNotIn("按状态消费", text)

    def test_backend_template_is_organized_around_business_behavior(self) -> None:
        text = (ASSET_ROOT / "new-feature-backend.md").read_text(encoding="utf-8")
        for expected in (
            "业务触发与前置条件",
            "业务结果与失败恢复",
            "对外提供的产品能力",
            "请求方式、接口字段、认证协议和错误码属于 API Contract 或 HLD",
        ):
            self.assertIn(expected, text)

    def test_every_chinese_template_routes_to_shared_language_guide(self) -> None:
        for name in (
            "new-feature-ui.md",
            "new-feature-backend.md",
            "integration.md",
            "refactoring.md",
            "optimization.md",
        ):
            with self.subTest(template=name):
                text = (ASSET_ROOT / name).read_text(encoding="utf-8")
                self.assertIn("../../../references/product-language-guide.md", text)

    def test_reviewer_uses_context_instead_of_keyword_matching(self) -> None:
        skill = (REVIEWER_ROOT / "SKILL.md").read_text(encoding="utf-8")
        checklist = (REVIEWER_ROOT / "references/review-checklist.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("主体、动作、对象、适用条件和结果", skill)
        self.assertIn("不得仅凭关键词报错", skill)
        self.assertIn("不是仅凭关键词报错", checklist)


if __name__ == "__main__":
    unittest.main()
