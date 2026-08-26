#!/usr/bin/env python3
"""Contract and structural-auditor tests for skill-doctor."""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = PLUGIN_ROOT / "skills/skill-doctor"
AUDITOR = SKILL_ROOT / "scripts/audit_skill.py"
REFERENCE_NAMES = {
    "role-and-topology-method.md",
    "behavior-equivalence.md",
    "sample-routing.md",
}
EXCLUDED_SOURCES = {
    "document-publisher",
    "product-metrics",
    "competitive-analysis",
    "define-product",
    "domain-modeler",
}


class SkillDoctorTest(unittest.TestCase):
    def make_skill(self, root: Path, name: str, body: str, *, with_ui: bool = True) -> Path:
        skill = root / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: 'Test skill. Use when: contract testing.'\n---\n\n{body}\n",
            encoding="utf-8",
        )
        if with_ui:
            (skill / "agents").mkdir(parents=True)
            (skill / "assets").mkdir(parents=True)
            (skill / "assets" / "small.png").write_bytes(b"small")
            (skill / "assets" / "large.png").write_bytes(b"large")
            (skill / "agents" / "openai.yaml").write_text(
                yaml.safe_dump(
                    {
                        "interface": {
                            "display_name": name,
                            "short_description": "test",
                            "default_prompt": "use test skill",
                            "icon_small": "./assets/small.png",
                            "icon_large": "./assets/large.png",
                        }
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
        return skill

    def run_audit(self, skill: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(AUDITOR), str(skill), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_entry_contains_complete_phase_protocol_and_routes_three_references(self) -> None:
        entry = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phase in range(7):
            self.assertIn(f"## Phase {phase}", entry)
        for field in ("Goal", "Inputs", "Actions", "Intermediate Deliverable", "Exit Criteria", "Stop / Escalation", "Resume"):
            self.assertGreaterEqual(entry.count(field), 7)
        self.assertIn("执行进度清单", entry)
        self.assertIn("行为等价标准", entry)
        self.assertEqual(REFERENCE_NAMES, {path.name for path in (SKILL_ROOT / "references").glob("*.md")})
        for reference in REFERENCE_NAMES:
            self.assertIn(f"references/{reference}", entry)

    def test_role_topology_contract_and_blind_challenges_are_complete(self) -> None:
        method = (SKILL_ROOT / "references/role-and-topology-method.md").read_text(encoding="utf-8")
        for role in ("门禁评审型", "产物编写型", "访谈发现型", "工程执行型", "流程导航型", "研究综合型"):
            self.assertIn(role, method)
        for topology in ("线性阶段", "串行 Gate", "访谈循环", "增量写入", "工程闭环", "Controller/Subagent", "状态导航"):
            self.assertIn(topology, method)

        blind = (SKILL_ROOT / "references/behavior-equivalence.md").read_text(encoding="utf-8")
        for challenge in ("Reviewer 挑战", "Writer 挑战", "Interviewer 挑战", "Builder 挑战", "Navigator 挑战", "Research / Controller 挑战"):
            self.assertIn(challenge, blind)
        for invariant in ("核心 Phase", "必要 Gate", "用户确认点", "中间产物", "写入权限", "暂停与恢复", "正式输出", "可观察验证", "下游契约"):
            self.assertIn(invariant, blind)

    def test_ui_metadata_and_brand_assets_are_complete(self) -> None:
        data = yaml.safe_load((SKILL_ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
        interface = data["interface"]
        for key in ("display_name", "short_description", "default_prompt", "icon_small", "icon_large"):
            self.assertIn(key, interface)
        self.assertTrue((SKILL_ROOT / interface["icon_small"]).is_file())
        self.assertTrue((SKILL_ROOT / interface["icon_large"]).is_file())

    def test_excluded_skills_are_not_used_as_sources(self) -> None:
        content = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [SKILL_ROOT / "SKILL.md", *sorted((SKILL_ROOT / "references").rglob("*.md"))]
        )
        for source in EXCLUDED_SOURCES:
            with self.subTest(source=source):
                self.assertNotIn(source, content)

    def test_missing_frontmatter_broken_link_and_missing_ui_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "broken"
            skill.mkdir()
            (skill / "SKILL.md").write_text("# Broken\n\n[missing](references/no.md)\n", encoding="utf-8")
            result = self.run_audit(skill, "--pattern", "writer", "--format", "json")
            report = json.loads(result.stdout)
            self.assertEqual(1, result.returncode)
            codes = {item["code"] for item in report["findings"]}
            self.assertTrue({"SD001", "SD005", "SD009"} <= codes)

    def test_template_link_placeholder_is_not_treated_as_a_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp), "template-writer", "## 输出\n[模块文档](路径)")
            result = self.run_audit(skill, "--format", "json")
            report = json.loads(result.stdout)
            self.assertEqual(0, result.returncode)
            self.assertNotIn("SD009", {item["code"] for item in report["findings"]})

    def test_unreachable_reference_is_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp), "sample-writer", "## 输出\n正式产物。")
            (skill / "references").mkdir()
            (skill / "references" / "orphan.md").write_text("# Orphan\n", encoding="utf-8")
            report = json.loads(self.run_audit(skill, "--format", "json").stdout)
            self.assertIn("SD011", {item["code"] for item in report["findings"]})

    def test_phase_checklist_and_body_mismatch_is_warning(self) -> None:
        body = """## 执行进度清单
□ Phase 0：开始
□ Phase 1：结束

## Phase 0：开始
完成。

## Phase 2：错误编号
完成。
"""
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp), "phase-skill", body)
            report = json.loads(self.run_audit(skill, "--format", "json").stdout)
            finding = next(item for item in report["findings"] if item["code"] == "SD012")
            self.assertEqual("warning", finding["severity"])
            self.assertEqual(["0", "1"], report["metrics"]["checklistPhaseIds"])
            self.assertEqual(["0", "2"], report["metrics"]["bodyPhaseIds"])

    def test_long_entry_only_changes_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            body = "\n".join(f"普通说明 {index}" for index in range(700))
            skill = self.make_skill(Path(tmp), "long-skill", body)
            report = json.loads(self.run_audit(skill, "--format", "json").stdout)
            self.assertGreater(report["metrics"]["entryLines"], 700)
            self.assertEqual([], [item for item in report["findings"] if "行" in item["message"] and item["code"] != "SD012"])

    def test_pattern_keywords_do_not_create_semantic_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(
                Path(tmp),
                "keyword-reviewer",
                "证据 P0 禁止 通过 Gate 正式输出 用户确认 中间产物 暂停恢复 下游契约",
            )
            report = json.loads(self.run_audit(skill, "--pattern", "reviewer", "--format", "json").stdout)
            self.assertEqual("structural", report["scope"])
            self.assertIsNone(report["semanticApproval"])
            self.assertFalse(any(item["code"].startswith("SD018") for item in report["findings"]))

    def test_invalid_skill_invocation_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp), "caller", "调用 $missing-skill。")
            report = json.loads(self.run_audit(skill, "--format", "json").stdout)
            self.assertIn("SD013", {item["code"] for item in report["findings"]})

    def test_currency_amounts_are_not_skill_invocations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp), "pricing-skill", "预算示例：$1、$10、$100。")
            report = json.loads(self.run_audit(skill, "--format", "json").stdout)
            self.assertNotIn("SD013", {item["code"] for item in report["findings"]})

    def test_explicit_pattern_is_context_only_and_audit_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = self.make_skill(Path(tmp), "sample-reviewer", "## 工作\n执行。")
            before = self.digest_tree(skill)
            json_result = self.run_audit(skill, "--pattern", "writer", "--format", "json")
            text_result = self.run_audit(skill, "--pattern", "writer", "--format", "text")
            report = json.loads(json_result.stdout)
            self.assertEqual("writer", report["pattern"])
            self.assertEqual("explicit", report["patternSource"])
            self.assertIn("Scope: structural (no semantic approval)", text_result.stdout)
            self.assertIn(f"Summary: {report['summary']['errors']} error", text_result.stdout)
            self.assertEqual(before, self.digest_tree(skill))

    def test_self_audit_does_not_self_certify_semantics(self) -> None:
        report = json.loads(self.run_audit(SKILL_ROOT, "--pattern", "auto", "--format", "json").stdout)
        self.assertEqual("builder", report["pattern"])
        self.assertEqual("inferred-for-reporting", report["patternSource"])
        self.assertEqual("structural", report["scope"])
        self.assertIsNone(report["semanticApproval"])
        self.assertEqual(0, report["summary"]["errors"])

    @staticmethod
    def digest_tree(root: Path) -> str:
        digest = hashlib.sha256()
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
            digest.update(str(path.relative_to(root)).encode())
            digest.update(path.read_bytes())
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
