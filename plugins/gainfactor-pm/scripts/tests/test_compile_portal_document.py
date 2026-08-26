#!/usr/bin/env python3
"""Tests for generic portal presentation compilation."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "compile_portal_document.py"
PORTAL_ROOT = SCRIPT.parent.parent / "assets/document-review-portal"


class CompilePortalDocumentTest(unittest.TestCase):
    def test_registered_content_components_exist_in_mdx_context(self) -> None:
        registry = json.loads((PORTAL_ROOT / "portal-capabilities.json").read_text(encoding="utf-8"))
        mdx_context = (PORTAL_ROOT / "components/mdx.tsx").read_text(encoding="utf-8")
        registered_components = {
            item["component"] for item in registry["contentTools"] if item["component"]
        }
        for component in registered_components:
            self.assertRegex(mdx_context, rf"\b{component}(?:,|:)")

    def test_antv_infographic_is_version_locked_and_local_only(self) -> None:
        registry = json.loads((PORTAL_ROOT / "portal-capabilities.json").read_text(encoding="utf-8"))
        package = json.loads((PORTAL_ROOT / "package.json").read_text(encoding="utf-8"))
        component = (PORTAL_ROOT / "components/infographic.tsx").read_text(encoding="utf-8")
        capability = next(item for item in registry["contentTools"] if item["id"] == "antv-infographic")
        self.assertEqual(capability["version"], package["dependencies"]["@antv/infographic"])
        self.assertEqual("local-only", capability["network"])
        self.assertNotIn("https://", component)
        self.assertNotIn("unpkg", component)
        self.assertIn("registerResourceLoader", component)
        self.assertIn("font.fontWeight = {}", component)
        self.assertIn("ref:(?:url|remote|search)", component)
        self.assertEqual(["syntax"], capability["props"]["required"])
        self.assertIn("renderGeneration", component)

    def test_accepts_static_multiline_infographic_syntax(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            document = Path(temporary_directory) / "doc.mdx"
            document.write_text(
                "<Infographic syntax={`infographic chart-bar-plain-text\n"
                "  data\n    title 完成率\n    values\n      - label A\n        value 68`} />\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["python3", str(SCRIPT), str(document), "--validate"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual([], json.loads(completed.stdout)["errors"])

    def test_rejects_fenced_only_and_dynamic_infographic_references(self) -> None:
        cases = {
            "fenced": "```infographic\ninfographic chart-bar-plain-text\n```\n",
            "dynamic": "<Infographic syntax={chartSyntax} />\n",
            "invalid": "<Infographic syntax={`chart-bar-plain-text\ndata`} />\n",
            "indented-attribute": "<Infographic\n  syntax={`infographic chart-bar-plain-text\ndata\n  title X`}\n/>\n",
            "missing-mdx-indent": "<Infographic syntax={`infographic chart-bar-plain-text\ndata\n  title X`} />\n",
        }
        for name, source in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary_directory:
                document = Path(temporary_directory) / "doc.mdx"
                document.write_text(source, encoding="utf-8")
                completed = subprocess.run(
                    ["python3", str(SCRIPT), str(document), "--validate"],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(1, completed.returncode)
                self.assertIn("Infographic", completed.stdout)

    def test_mermaid_measurement_nodes_remain_laid_out_during_render(self) -> None:
        styles = (PORTAL_ROOT / "app/global.css").read_text(encoding="utf-8")
        component = (PORTAL_ROOT / "components/mermaid.tsx").read_text(encoding="utf-8")
        self.assertNotIn("body > div[id^='dmermaid-']", styles)
        self.assertNotIn("body > svg[id^='mermaid-']", styles)
        self.assertIn("cleanupMermaidArtifacts", component)

    def test_mermaid_fullscreen_styles_target_the_requested_element(self) -> None:
        styles = (PORTAL_ROOT / "app/global.css").read_text(encoding="utf-8")
        component = (PORTAL_ROOT / "components/mermaid.tsx").read_text(encoding="utf-8")
        self.assertIn('className="mermaid-fullscreen-root"', component)
        self.assertIn(".mermaid-fullscreen-root:fullscreen", styles)
        self.assertIn(".mermaid-fullscreen-root:fullscreen .mermaid-frame", styles)
        self.assertNotIn(".mermaid-frame:fullscreen", styles)

    def test_sidebar_active_state_is_scoped_to_the_public_layout_container(self) -> None:
        styles = (PORTAL_ROOT / "app/global.css").read_text(encoding="utf-8")
        layout = (PORTAL_ROOT / "app/docs/layout.tsx").read_text(encoding="utf-8")
        visual_gate = (PORTAL_ROOT / "scripts/visual-release-gate.mjs").read_text(encoding="utf-8")
        self.assertIn("containerProps={{ className: 'gainfactor-docs-layout' }}", layout)
        self.assertIn(".gainfactor-docs-layout [data-sidebar-placeholder] a[data-active='true']", styles)
        self.assertNotIn("#nd-sidebar", styles)
        self.assertNotIn("\na[data-active='true']", styles)
        self.assertIn("brandContrastExemption", visual_gate)
        self.assertNotIn("disableRules(['color-contrast'])", visual_gate)

    def test_lucide_icons_are_registered_without_a_business_allowlist(self) -> None:
        registry = json.loads((PORTAL_ROOT / "portal-capabilities.json").read_text(encoding="utf-8"))
        capability = next(item for item in registry["contentTools"] if item["id"] == "lucide-icon")
        icon_component = (PORTAL_ROOT / "components/lucide-icon.tsx").read_text(encoding="utf-8")
        infographic = (PORTAL_ROOT / "components/infographic.tsx").read_text(encoding="utf-8")
        self.assertEqual("all", capability["coverage"])
        self.assertEqual("local-only", capability["network"])
        self.assertIn("iconNames", icon_component)
        self.assertIn("dynamicIconImports", infographic)

    def test_generic_report_components_are_registered_with_fallbacks(self) -> None:
        registry = json.loads((PORTAL_ROOT / "portal-capabilities.json").read_text(encoding="utf-8"))
        tools = {item["id"]: item for item in registry["contentTools"]}
        for tool_id in ("persona-brief", "field-list", "panel", "board", "evidence-step"):
            self.assertEqual("registered", tools[tool_id]["status"])
            self.assertTrue(tools[tool_id]["fallback"])
        components = (PORTAL_ROOT / "components/document-blocks.tsx").read_text(encoding="utf-8")
        styles = (PORTAL_ROOT / "app/global.css").read_text(encoding="utf-8")
        for component in ("PersonaBrief", "FieldList", "Panel", "Board"):
            self.assertIn(f"function {component}", components)
        self.assertIn("@media print", styles)
        self.assertIn(".gf-persona-brief", styles)
        self.assertIn(".gf-board", styles)
        self.assertIn("level?: 2 | 3 | 4", components)
        self.assertIn("identity?: string", components)
        self.assertIn("tone?: 'neutral' | 'info' | 'warning' | 'critical'", components)
        self.assertIn("group.tone ?? 'neutral'", components)
        self.assertNotIn("group.title.toLowerCase", components)

    def test_compiles_generic_modules_and_resolves_imported_image(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            document = root / "report.mdx"
            manifest = root / "report.portal.json"
            document.write_text("# 研究报告\n\n![赵宁](/document-assets/report/zhao.png)\n", encoding="utf-8")
            manifest.write_text(json.dumps({
                "schemaVersion": 1,
                "layout": "report",
                "modules": [
                    {"id": "summary", "type": "metrics", "items": [{"label": "核心用户", "value": "低负担启动型"}]},
                    {"id": "people", "type": "cards", "items": [{"title": "赵宁", "sourceImageAlt": "赵宁"}]},
                    {"id": "path", "type": "steps", "items": [{"content": "表达约束"}]},
                ],
            }, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run([
                "python3", str(SCRIPT), str(document), f"--presentation={manifest}", "--validate",
            ], check=True, capture_output=True, text=True)
            presentation = json.loads(completed.stdout)["presentation"]
            self.assertEqual("report", presentation["layout"])
            self.assertEqual(3, len(presentation["modules"]))
            self.assertEqual("/document-assets/report/zhao.png", presentation["modules"][1]["items"][0]["image"])

    def test_persona_brief_image_alt_is_available_as_a_source_image(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            document = root / "report.mdx"
            manifest = root / "report.portal.json"
            document.write_text(
                '<PersonaBrief name="赵宁" image={{ alt: "赵宁人物画像", src: "/document-assets/report/zhao.png" }} />\n',
                encoding="utf-8",
            )
            manifest.write_text(json.dumps({
                "schemaVersion": 1,
                "layout": "report",
                "modules": [{
                    "id": "people",
                    "type": "cards",
                    "items": [{"title": "赵宁", "sourceImageAlt": "赵宁人物画像"}],
                }],
            }, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                ["python3", str(SCRIPT), str(document), f"--presentation={manifest}", "--validate"],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual([], payload["errors"])
            self.assertEqual(
                "/document-assets/report/zhao.png",
                payload["presentation"]["modules"][0]["items"][0]["image"],
            )

    def test_card_source_image_alt_resolves_a_persona_brief_image(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            document = root / "report.mdx"
            manifest = root / "report.portal.json"
            document.write_text(
                '<PersonaBrief name="赵宁" image={{ src: "/document-assets/report/zhao.png", alt: "赵宁人物画像" }} />\n',
                encoding="utf-8",
            )
            manifest.write_text(json.dumps({
                "schemaVersion": 1,
                "layout": "report",
                "modules": [{
                    "id": "people",
                    "type": "cards",
                    "items": [{"title": "赵宁", "sourceImageAlt": "赵宁人物画像"}],
                }],
            }, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                ["python3", str(SCRIPT), str(document), f"--presentation={manifest}", "--validate"],
                check=True,
                capture_output=True,
                text=True,
            )
            card = json.loads(completed.stdout)["presentation"]["modules"][0]["items"][0]
            self.assertEqual("/document-assets/report/zhao.png", card["image"])
            self.assertEqual("赵宁人物画像", card["imageAlt"])

    def test_rejects_ambiguous_alt_across_markdown_and_persona_brief_images(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            document = root / "report.mdx"
            manifest = root / "report.portal.json"
            document.write_text(
                '![代表人物](/document-assets/report/first.png)\n\n'
                '<PersonaBrief name="示例" image={{ src: "/document-assets/report/second.png", alt: "代表人物" }} />\n',
                encoding="utf-8",
            )
            manifest.write_text(json.dumps({
                "schemaVersion": 1,
                "layout": "report",
                "modules": [{
                    "id": "people",
                    "type": "cards",
                    "items": [{"title": "示例", "sourceImageAlt": "代表人物"}],
                }],
            }, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                ["python3", str(SCRIPT), str(document), f"--presentation={manifest}", "--validate"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, completed.returncode)
            self.assertIn("sourceImageAlt 对应多个不同图片", completed.stdout)

    def test_duplicate_alt_with_the_same_src_is_not_ambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            document = root / "report.mdx"
            manifest = root / "report.portal.json"
            src = "/document-assets/report/person.png"
            document.write_text(
                f'![代表人物]({src})\n\n<PersonaBrief name="示例" image={{{{ src: "{src}", alt: "代表人物" }}}} />\n',
                encoding="utf-8",
            )
            manifest.write_text(json.dumps({
                "schemaVersion": 1,
                "layout": "report",
                "modules": [{
                    "id": "people",
                    "type": "cards",
                    "items": [{"title": "示例", "sourceImageAlt": "代表人物"}],
                }],
            }, ensure_ascii=False), encoding="utf-8")
            completed = subprocess.run(
                ["python3", str(SCRIPT), str(document), f"--presentation={manifest}", "--validate"],
                check=True,
                capture_output=True,
                text=True,
            )
            card = json.loads(completed.stdout)["presentation"]["modules"][0]["items"][0]
            self.assertEqual(src, card["image"])

    def test_validation_rejects_unknown_module(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            document = root / "report.md"
            manifest = root / "report.portal.json"
            document.write_text("# 报告\n", encoding="utf-8")
            manifest.write_text('{"schemaVersion":1,"layout":"report","modules":[{"id":"x","type":"persona"}]}', encoding="utf-8")
            completed = subprocess.run([
                "python3", str(SCRIPT), str(document), f"--presentation={manifest}", "--validate",
            ], capture_output=True, text=True)
            self.assertEqual(1, completed.returncode)
            self.assertIn("type 不受支持", completed.stdout)

    def test_plain_markdown_needs_no_presentation_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            document = Path(temporary_directory) / "doc.md"
            document.write_text("# 普通文档\n", encoding="utf-8")
            completed = subprocess.run(["python3", str(SCRIPT), str(document)], check=True, capture_output=True, text=True)
            self.assertEqual([], json.loads(completed.stdout)["presentation"]["modules"])

    def test_rejects_invalid_or_orphaned_citations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            document = Path(temporary_directory) / "doc.mdx"
            document.write_text(
                '<Citation source="S01" />\n<SourceIndex><Source id="S02">孤立来源</Source></SourceIndex>\n',
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["python3", str(SCRIPT), str(document), "--validate"], capture_output=True, text=True,
            )
            self.assertEqual(1, completed.returncode)
            self.assertIn("引用目标不存在：S01", completed.stdout)
            self.assertIn("存在孤立来源：S02", completed.stdout)

    def test_accepts_stable_citation_mapping_and_warns_on_long_field_list_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            document = Path(temporary_directory) / "doc.mdx"
            document.write_text(
                '<FieldList items={[{ label: "说明", value: "' + ('长文本' * 30) + '" }]} />\n'
                '<Citation source="S01" />\n<SourceIndex><Source id="S01">有效来源</Source></SourceIndex>\n',
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["python3", str(SCRIPT), str(document), "--validate"], check=True, capture_output=True, text=True,
            )
            self.assertIn("Panel 正文", completed.stderr)
            self.assertTrue(json.loads(completed.stdout)["warnings"])

    def test_screenshot_requires_src_and_warns_when_caption_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            missing_caption = root / "missing-caption.mdx"
            missing_caption.write_text('<Screenshot src="./screen.png" title="结果页" />\n', encoding="utf-8")
            completed = subprocess.run(
                ["python3", str(SCRIPT), str(missing_caption), "--validate"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("缺少 caption", completed.stderr)

            missing_src = root / "missing-src.mdx"
            missing_src.write_text('<Screenshot title="结果页" caption="界面证据" />\n', encoding="utf-8")
            rejected = subprocess.run(
                ["python3", str(SCRIPT), str(missing_src), "--validate"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(1, rejected.returncode)
            self.assertIn("src 必须是非空字符串", rejected.stdout)


if __name__ == "__main__":
    unittest.main()
