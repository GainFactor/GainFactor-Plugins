#!/usr/bin/env python3
"""Regression tests for the shared document review portal scaffold."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
import json
from pathlib import Path


SCRIPT = Path(__file__).parent.parent / "create_document_portal.py"


class CreateDocumentPortalTest(unittest.TestCase):
    def test_standard_artifacts_share_the_default_product_portal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_root = root / "docs/gainfactor/ctrip-wendao"
            source_root.mkdir(parents=True)
            artifacts = {
                "product-definition": "ctrip-wendao-product-definition",
                "brd": "ctrip-wendao-brd",
                "prd": "ctrip-wendao-prd",
                "user-journey": "ctrip-wendao-user-journey",
                "user-persona": "ctrip-wendao-user-persona",
                "competitive-analysis": "ctrip-wendao-competitive-analysis",
                "product-metrics": "ctrip-wendao-metrics",
                "domain-model": "ctrip-wendao-domain-model",
                "api-contract": "ctrip-wendao-api-contract",
                "hld": "ctrip-wendao-hld",
                "lld": "ctrip-wendao-lld",
                "test-strategy": "ctrip-wendao-test-strategy",
                "test-spec": "ctrip-wendao-test-spec",
                "runbook": "ctrip-wendao-runbook",
                "guardrails": "ctrip-wendao-guardrails",
            }

            for artifact, route_slug in artifacts.items():
                source = source_root / f"{artifact}.mdx"
                source.write_text(f"# {artifact}\n\n正文。\n", encoding="utf-8")
                subprocess.run([
                    "python3", str(SCRIPT), str(source),
                    "--subject-slug=ctrip-wendao", "--subject-title=携程问道",
                    f"--artifact={artifact}",
                ], cwd=root, check=True)
                self.assertTrue(
                    (root / f".gainfactor/portal/content/docs/ctrip-wendao/{route_slug}.mdx").is_file()
                )

            manifest = json.loads(
                (root / ".gainfactor/portal/.gainfactor-documents.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {f"ctrip-wendao/{route_slug}" for route_slug in artifacts.values()},
                set(manifest["documents"]),
            )
            for artifact, route_slug in artifacts.items():
                entry = manifest["documents"][f"ctrip-wendao/{route_slug}"]
                self.assertEqual(artifact, entry["artifactKey"])
                self.assertEqual(
                    f"docs/gainfactor/ctrip-wendao/{artifact}.mdx",
                    entry["sourcePath"],
                )
                self.assertEqual("携程问道", entry["collection"])
            subprocess.run([
                "python3", str(SCRIPT), str(source_root / "product-definition.mdx"),
                "--subject-slug=ctrip-wendao", "--subject-title=携程问道",
                "--artifact=product-definition", "--status=confirmed",
            ], cwd=root, check=True)
            manifest = json.loads(
                (root / ".gainfactor/portal/.gainfactor-documents.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(artifacts), len(manifest["documents"]))
            self.assertEqual(
                {
                    "title": "携程问道",
                    "pages": list(artifacts.values()),
                },
                json.loads(
                    (root / ".gainfactor/portal/content/docs/ctrip-wendao/meta.json").read_text(encoding="utf-8")
                ),
            )

    def test_dry_run_reports_resolution_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "docs/gainfactor/example/product-definition.mdx"
            source.parent.mkdir(parents=True)
            source.write_text("# 产品定义\n", encoding="utf-8")

            completed = subprocess.run([
                "python3", str(SCRIPT), str(source),
                "--subject-slug=example", "--subject-title=示例产品",
                "--artifact=product-definition", "--dry-run",
            ], cwd=root, check=True, capture_output=True, text=True)

            resolution = json.loads(completed.stdout)
            self.assertEqual("example/example-product-definition", resolution["route"])
            self.assertEqual("create", resolution["action"])
            self.assertEqual(str((root / ".gainfactor/portal").resolve()), resolution["target"])
            self.assertFalse((root / ".gainfactor").exists())

    def test_standard_artifact_requires_complete_subject_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "product-definition.mdx"
            source.write_text("# 产品定义\n", encoding="utf-8")

            completed = subprocess.run([
                "python3", str(SCRIPT), str(source),
                "--subject-slug=example", "--artifact=product-definition", "--dry-run",
            ], cwd=root, capture_output=True, text=True)

            self.assertEqual(2, completed.returncode)
            self.assertIn("--subject-title", completed.stderr)
            self.assertFalse((root / ".gainfactor").exists())

    def test_rejects_invalid_subject_slug_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "product-definition.mdx"
            source.write_text("# 产品定义\n", encoding="utf-8")
            completed = subprocess.run([
                "python3", str(SCRIPT), str(source),
                "--subject-slug=Example Product", "--subject-title=示例产品",
                "--artifact=product-definition", "--dry-run",
            ], cwd=root, capture_output=True, text=True)
            self.assertEqual(2, completed.returncode)
            self.assertIn("Subject slug", completed.stderr)
            self.assertFalse((root / ".gainfactor").exists())

    def test_rejects_non_portal_default_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "docs/gainfactor/example/product-definition.mdx"
            source.parent.mkdir(parents=True)
            source.write_text("# 产品定义\n", encoding="utf-8")
            target = root / ".gainfactor/portal"
            target.mkdir(parents=True)
            sentinel = target / "do-not-overwrite.txt"
            sentinel.write_text("preserve", encoding="utf-8")
            completed = subprocess.run([
                "python3", str(SCRIPT), str(source),
                "--subject-slug=example", "--subject-title=示例产品",
                "--artifact=product-definition",
            ], cwd=root, capture_output=True, text=True)
            self.assertEqual(2, completed.returncode)
            self.assertIn("not a GainFactor document portal", completed.stderr)
            self.assertEqual("preserve", sentinel.read_text(encoding="utf-8"))

    def test_updates_legacy_entry_with_source_tracking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "docs/gainfactor/example/product-definition.mdx"
            source.parent.mkdir(parents=True)
            source.write_text("# 产品定义\n", encoding="utf-8")
            target = root / "portal"

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target),
                "--slug=example-product-definition", "--group=example",
                "--group-title=示例产品", "--type=Product-Definition",
            ], cwd=root, check=True)
            manifest_path = target / ".gainfactor-documents.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = manifest["documents"]["example/example-product-definition"]
            entry.pop("sourcePath", None)
            entry.pop("artifactKey", None)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target),
                "--subject-slug=example", "--subject-title=示例产品",
                "--artifact=product-definition",
            ], cwd=root, check=True)

            updated = json.loads(manifest_path.read_text(encoding="utf-8"))["documents"]
            entry = updated["example/example-product-definition"]
            self.assertEqual("product-definition", entry["artifactKey"])
            self.assertEqual("docs/gainfactor/example/product-definition.mdx", entry["sourcePath"])

    def test_rejects_standard_route_owned_by_a_different_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = root / "first.mdx"
            second = root / "second.mdx"
            first.write_text("# First\n", encoding="utf-8")
            second.write_text("# Second\n", encoding="utf-8")
            target = root / "portal"
            subprocess.run([
                "python3", str(SCRIPT), str(first), str(target),
                "--slug=example-product-definition", "--group=example",
                "--group-title=示例产品",
            ], cwd=root, check=True)

            completed = subprocess.run([
                "python3", str(SCRIPT), str(second), str(target),
                "--subject-slug=example", "--subject-title=示例产品",
                "--artifact=product-definition",
            ], cwd=root, capture_output=True, text=True)

            self.assertEqual(2, completed.returncode)
            self.assertIn("already belongs", completed.stderr)

    def test_imports_document_metadata_and_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "input.md"
            target = root / "portal"
            source.write_text(
                "# 示例 PRD：结算流程\n\n这是本轮测试文档。\n\n## 一、版本说明\n\n正文。\n",
                encoding="utf-8",
            )
            review = root / "review.json"
            review.write_text(
                json.dumps({
                    "conclusion": "有条件通过",
                    "issues": [{
                        "id": "PRD-001",
                        "severity": "P1",
                        "title": "补充验收标准",
                        "sectionId": "一版本说明",
                        "sectionTitle": "一、版本说明",
                        "suggestion": "增加可量化结果。",
                    }],
                }, ensure_ascii=False),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    str(source),
                    str(target),
                    "--slug=settlement-prd",
                    "--type=PRD",
                    "--version=V2.1",
                    "--status=评审中",
                    "--owner=产品团队",
                    "--updated=2026-08-18",
                    f"--review={review}",
                ],
                check=True,
            )

            generated = (target / "content/docs/product-requirements/settlement-prd.mdx").read_text(encoding="utf-8")
            portal_data = (target / "lib/portal-data.generated.ts").read_text(encoding="utf-8")
            self.assertIn('title: "示例 PRD：结算流程"', generated)
            self.assertIn("这是本轮测试文档。", generated)
            self.assertIn('"version": "V2.1"', portal_data)
            self.assertIn('"status": "评审中"', portal_data)
            self.assertIn('"conclusion": "有条件通过"', portal_data)
            self.assertIn('"sectionId": "一版本说明"', portal_data)
            self.assertIn('"sectionTitle": "一、版本说明"', portal_data)
            self.assertNotIn("教务系统", (target / "app/(home)/page.tsx").read_text(encoding="utf-8"))
            self.assertTrue((target / "打开文档门户.command").is_file())
            self.assertTrue((target / "关闭文档门户.command").is_file())
            self.assertTrue((target / "scripts/portal-control.py").is_file())
            self.assertTrue((target / "打开文档门户.command").stat().st_mode & 0o111)

    def test_accepts_frontmatter_title_without_h1(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "input.mdx"
            target = root / "portal"
            source.write_text(
                '---\ntitle: "仅 Frontmatter 的 PRD"\ndescription: "原摘要"\n---\n\n正文。\n',
                encoding="utf-8",
            )

            subprocess.run(["python3", str(SCRIPT), str(source), str(target), "--slug=frontmatter-doc"], check=True)

            generated = (target / "content/docs/other/frontmatter-doc.mdx").read_text(encoding="utf-8")
            self.assertIn('title: "仅 Frontmatter 的 PRD"', generated)
            self.assertIn("正文。", generated)

    def test_adds_multiple_documents_to_one_portal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            target = root / "portal"
            for slug, document_type in (("requirements", "PRD"), ("architecture", "HLD")):
                source = root / f"{slug}.md"
                source.write_text(f"# {document_type} 示例\n\n正文。\n", encoding="utf-8")
                subprocess.run([
                    "python3", str(SCRIPT), str(source), str(target),
                    f"--slug={slug}", f"--type={document_type}",
                ], check=True)

            subprocess.run([
                "python3", str(SCRIPT), str(root / "requirements.md"), str(target),
                "--slug=requirements", "--type=PRD", "--status=已更新",
            ], check=True)

            manifest = json.loads((target / ".gainfactor-documents.json").read_text(encoding="utf-8"))
            self.assertEqual(
                {"product-requirements/requirements", "technical-design/architecture"},
                set(manifest["documents"]),
            )
            self.assertEqual("已更新", manifest["documents"]["product-requirements/requirements"]["status"])
            self.assertTrue((target / "content/docs/product-requirements/requirements.mdx").is_file())
            self.assertTrue((target / "content/docs/technical-design/architecture.mdx").is_file())
            self.assertEqual(
                {"pages": ["index", "product-requirements", "technical-design"]},
                json.loads((target / "content/docs/meta.json").read_text(encoding="utf-8")),
            )
            self.assertEqual(
                {"title": "产品需求", "pages": ["requirements"]},
                json.loads(
                    (target / "content/docs/product-requirements/meta.json").read_text(encoding="utf-8")
                ),
            )

    def test_groups_product_definition_with_product_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "product-definition.md"
            target = root / "portal"
            source.write_text("# 产品定义：示例产品\n\n正文。\n", encoding="utf-8")

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target),
                "--slug=product-definition", "--type=PRODUCT_DEFINITION",
            ], check=True)

            manifest = json.loads((target / ".gainfactor-documents.json").read_text(encoding="utf-8"))
            self.assertIn("product-requirements/product-definition", manifest["documents"])
            self.assertTrue(
                (target / "content/docs/product-requirements/product-definition.mdx").is_file()
            )

    def test_supports_product_named_navigation_group(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "product-definition.md"
            target = root / "portal"
            source.write_text("# 产品定义\n\n> Product: 携程问道\n", encoding="utf-8")

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target),
                "--slug=ctrip-wendao-product-definition",
                "--type=Product-Definition",
                "--collection=携程问道",
                "--group=ctrip-wendao",
                "--group-title=携程问道",
            ], check=True)

            manifest = json.loads((target / ".gainfactor-documents.json").read_text(encoding="utf-8"))
            route = "ctrip-wendao/ctrip-wendao-product-definition"
            self.assertIn(route, manifest["documents"])
            self.assertEqual("携程问道", manifest["documents"][route]["groupTitle"])
            self.assertEqual("携程问道", manifest["documents"][route]["collection"])
            self.assertEqual(
                {"title": "携程问道", "pages": ["ctrip-wendao-product-definition"]},
                json.loads((target / "content/docs/ctrip-wendao/meta.json").read_text(encoding="utf-8")),
            )
            generated = (target / f"content/docs/{route}.mdx").read_text(encoding="utf-8")
            self.assertIn('title: "产品定义"', generated)

            metrics = root / "product-metrics.md"
            metrics.write_text("# 产品指标分析\n\n正文。\n", encoding="utf-8")
            subprocess.run([
                "python3", str(SCRIPT), str(metrics), str(target),
                "--slug=ctrip-wendao-metrics",
                "--type=Product-Metrics",
                "--collection=携程问道",
                "--group=ctrip-wendao",
                "--group-title=携程问道",
            ], check=True)

            self.assertEqual(
                {
                    "title": "携程问道",
                    "pages": ["ctrip-wendao-product-definition", "ctrip-wendao-metrics"],
                },
                json.loads((target / "content/docs/ctrip-wendao/meta.json").read_text(encoding="utf-8")),
            )
            generated_metrics = (
                target / "content/docs/ctrip-wendao/ctrip-wendao-metrics.mdx"
            ).read_text(encoding="utf-8")
            self.assertIn('title: "产品指标分析"', generated_metrics)

    def test_groups_user_persona_with_product_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "user-persona.md"
            target = root / "portal"
            source.write_text("# 用户画像：示例产品\n\n> Artifact Type: USER_PERSONA\n", encoding="utf-8")

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target),
                "--slug=user-persona", "--type=User-Persona",
            ], check=True)

            manifest = json.loads((target / ".gainfactor-documents.json").read_text(encoding="utf-8"))
            self.assertIn("product-requirements/user-persona", manifest["documents"])
            self.assertTrue((target / "content/docs/product-requirements/user-persona.mdx").is_file())

    def test_copies_local_user_persona_images_into_portal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "docs" / "user-persona.md"
            image = root / "docs" / "assets" / "user-persona" / "example" / "zhou-min.png"
            target = root / "portal"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"persona-image")
            source.write_text(
                "# 用户画像研究报告：示例产品\n\n"
                "## 4. 用户群体与 Persona 档案\n\n"
                "![周敏，谨慎确认型用户](assets/user-persona/example/zhou-min.png)\n",
                encoding="utf-8",
            )

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target),
                "--slug=user-persona", "--type=User-Persona",
            ], check=True)

            generated = (
                target / "content/docs/product-requirements/user-persona.mdx"
            ).read_text(encoding="utf-8")
            copied = (
                target
                / "public/document-assets/product-requirements/user-persona/01-zhou-min.png"
            )
            self.assertIn(
                "![周敏，谨慎确认型用户]"
                "(/document-assets/product-requirements/user-persona/01-zhou-min.png)",
                generated,
            )
            self.assertEqual(b"persona-image", copied.read_bytes())

    def test_copies_persona_brief_component_image_and_rewrites_src(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "docs" / "profile.mdx"
            image = root / "docs" / "assets" / "person.png"
            presentation = root / "docs" / "profile.portal.json"
            target = root / "portal"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"profile-image")
            source.write_text(
                '# 主体档案\n\n'
                '<PersonaBrief name="赵宁" image={{ src: "./assets/person.png", alt: "赵宁人物画像" }} '
                'facts={[{ label: "地区", value: "成都" }]} />\n',
                encoding="utf-8",
            )
            presentation.write_text(json.dumps({
                "schemaVersion": 1,
                "layout": "report",
                "modules": [{
                    "id": "people",
                    "type": "cards",
                    "items": [{"title": "赵宁", "sourceImageAlt": "赵宁人物画像"}],
                }],
            }, ensure_ascii=False), encoding="utf-8")

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target), "--slug=profile",
                f"--presentation={presentation}", "--rich",
            ], check=True)

            generated = (target / "content/docs/other/profile.mdx").read_text(encoding="utf-8")
            copied = target / "public/document-assets/other/profile/01-person.png"
            self.assertIn('src: "/document-assets/other/profile/01-person.png"', generated)
            self.assertIn('alt: "赵宁人物画像"', generated)
            self.assertEqual(b"profile-image", copied.read_bytes())
            portal_manifest = json.loads((target / ".gainfactor-documents.json").read_text(encoding="utf-8"))
            card = portal_manifest["documents"]["other/profile"]["presentation"]["modules"][0]["items"][0]
            self.assertEqual("/document-assets/other/profile/01-person.png", card["image"])

    def test_rejects_persona_brief_image_without_alt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "profile.mdx"
            image = root / "person.png"
            image.write_bytes(b"profile-image")
            source.write_text(
                '# 人物导读\n\n<PersonaBrief name="赵宁" image={{ src: "./person.png" }} />\n',
                encoding="utf-8",
            )
            completed = subprocess.run([
                "python3", str(SCRIPT), str(source), str(root / "portal"), "--slug=profile",
            ], capture_output=True, text=True)
            self.assertNotEqual(0, completed.returncode)
            self.assertIn("PersonaBrief image must contain a non-empty alt field", completed.stderr)

    def test_copies_screenshot_component_image_and_rewrites_src(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "docs" / "report.mdx"
            image = root / "docs" / "assets" / "screen.png"
            target = root / "portal"
            image.parent.mkdir(parents=True)
            image.write_bytes(b"screenshot-image")
            source.write_text(
                '# 产品报告\n\n<Screenshot src="./assets/screen.png" title="结果页" '
                'caption="展示筛选结果。" evidenceId="E-S01" />\n',
                encoding="utf-8",
            )

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target), "--slug=report",
            ], check=True)

            generated = (target / "content/docs/other/report.mdx").read_text(encoding="utf-8")
            copied = target / "public/document-assets/other/report/01-screen.png"
            self.assertIn('src="/document-assets/other/report/01-screen.png"', generated)
            self.assertEqual(b"screenshot-image", copied.read_bytes())

    def test_rich_document_adds_generic_presentation_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "persona.md"
            target = root / "portal"
            image = root / "assets" / "zhao.png"
            image.parent.mkdir()
            image.write_bytes(b"portrait")
            source.write_text(
                "# 用户画像研究报告：示例\n\n"
                "## 0. 执行摘要\n\n"
                "| 结论项 | 当前判断 |\n|---|---|\n| 核心用户 | 低负担启动型 |\n\n"
                "## 4. 用户群体与 Persona 档案\n\n"
                "### 4.1 低负担启动型：赵宁\n\n"
                "#### 群体画像\n\n有旅行意愿，但不享受规划。\n\n"
                "#### Persona 名片\n\n"
                "| 字段 | 内容 |\n|---|---|\n"
                "| 姓名 | 赵宁 |\n| 所属群体 | 低负担启动型 |\n"
                "| 一句话认识她 | 我想出去，但不想再做一个项目 |\n"
                "| 核心任务 | 完成轻松休息 |\n| 最大顾虑 | 最后放弃 |\n"
                "| 产品接受条件 | 少量候选 |\n\n"
                "#### Persona 人物图片\n\n![赵宁](assets/zhao.png)\n",
                encoding="utf-8",
            )
            presentation = root / "persona.portal.json"
            presentation.write_text(json.dumps({
                "schemaVersion": 1,
                "layout": "report",
                "modules": [
                    {"id": "summary", "type": "metrics", "items": [{"label": "核心用户", "value": "低负担启动型"}]},
                    {"id": "personas", "type": "cards", "title": "代表性 Persona", "items": [{
                        "title": "赵宁", "eyebrow": "低负担启动型", "sourceImageAlt": "赵宁",
                        "quote": "我想出去，但不想再做一个项目",
                    }]},
                ],
            }, ensure_ascii=False), encoding="utf-8")

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target),
                "--slug=rich-persona", "--type=User-Persona", f"--presentation={presentation}", "--rich",
            ], check=True)

            manifest = json.loads((target / ".gainfactor-documents.json").read_text(encoding="utf-8"))
            presentation = manifest["documents"]["product-requirements/rich-persona"]["presentation"]
            self.assertEqual("report", presentation["layout"])
            self.assertEqual("赵宁", presentation["modules"][1]["items"][0]["title"])
            self.assertEqual(
                "/document-assets/product-requirements/rich-persona/01-zhao.png",
                presentation["modules"][1]["items"][0]["image"],
            )

    def test_rich_requires_presentation_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "report.md"
            source.write_text("# 报告\n", encoding="utf-8")
            completed = subprocess.run([
                "python3", str(SCRIPT), str(source), str(root / "portal"), "--rich",
            ], capture_output=True, text=True)
            self.assertEqual(2, completed.returncode)
            self.assertIn("--rich requires --presentation", completed.stderr)

    def test_groups_competitive_analysis_with_product_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "competitive-analysis.md"
            target = root / "portal"
            source.write_text(
                "# 竞品分析：示例产品\n\n> Artifact Type: COMPETITIVE_ANALYSIS\n",
                encoding="utf-8",
            )

            subprocess.run([
                "python3", str(SCRIPT), str(source), str(target),
                "--slug=competitive-analysis", "--type=Competitive-Analysis",
            ], check=True)

            manifest = json.loads((target / ".gainfactor-documents.json").read_text(encoding="utf-8"))
            self.assertIn("product-requirements/competitive-analysis", manifest["documents"])
            self.assertTrue(
                (target / "content/docs/product-requirements/competitive-analysis.mdx").is_file()
            )


if __name__ == "__main__":
    unittest.main()
