#!/usr/bin/env python3
"""Read-only deterministic structural audit for gainfactor-pm Skills."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

import yaml


SCHEMA_VERSION = "2.0"
PATTERNS = {"reviewer", "writer", "interviewer", "builder", "navigator", "research"}
INTERFACE_KEYS = {"display_name", "short_description", "default_prompt", "icon_small", "icon_large"}
LINK_RE = re.compile(r"!?\[[^]]*]\(([^)]+)\)")
INVOCATION_RE = re.compile(r"\$([a-z][a-z0-9-]*)")
CHECKLIST_PHASE_RE = re.compile(r"^\s*[□☐☑✓✔-]\s*(?:Phase|阶段)\s*(\d+(?:\.\d+)?)\b", re.MULTILINE | re.IGNORECASE)
HEADING_PHASE_RE = re.compile(r"^#{2,6}\s*(?:Phase|阶段)\s*(\d+(?:\.\d+)?)\b", re.MULTILINE | re.IGNORECASE)
PLACEHOLDER_TARGETS = {"path", "url", "路径", "链接", "待补充"}
PLACEHOLDER_INVOCATIONS = {"skill-name", "xxx", "yyy", "zzz"}
# These canonical calls belong to the companion automation plugin rather than gainfactor-pm.
EXTERNAL_INVOCATIONS = {"case", "case-writing", "pipeline", "trigger", "execution"}


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    path: str
    line: int
    message: str
    recommendation: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", type=Path)
    parser.add_argument("--pattern", choices=["auto", *sorted(PATTERNS)], default="auto")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    return parser.parse_args()


def line_of(text: str, needle: str) -> int:
    index = text.find(needle)
    return 1 if index < 0 else text.count("\n", 0, index) + 1


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("SKILL.md frontmatter is incomplete")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError("SKILL.md frontmatter must be a mapping")
    return data


def infer_declared_context(name: str, description: str, text: str) -> str:
    """Return a reporting hint only; it never grants semantic approval."""
    source = f"{name} {description}".lower()
    if name == "skill-doctor":
        return "builder"
    if name.endswith("-reviewer") or " review" in source or "评审" in description:
        return "reviewer"
    if name.endswith("-writer") or "write " in source or "撰写" in description:
        return "writer"
    if "interviewer" in name or "访谈" in description:
        return "interviewer"
    if name == "guide" or "流程导航" in description:
        return "navigator"
    if "prototype" in name or "前端仓库" in text:
        return "builder"
    return "research"


def local_target(source: Path, raw: str) -> Path | None:
    target = raw.split("#", 1)[0].strip()
    if not target or target.lower() in PLACEHOLDER_TARGETS or "://" in target or target.startswith("#"):
        return None
    return (source.parent / target).resolve()


def reachable_markdown(skill_dir: Path) -> set[Path]:
    start = (skill_dir / "SKILL.md").resolve()
    seen: set[Path] = set()
    pending = [start]
    while pending:
        source = pending.pop()
        if source in seen or not source.is_file() or source.suffix.lower() != ".md":
            continue
        seen.add(source)
        source_text = source.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(source_text):
            target = local_target(source, raw)
            if target and target.suffix.lower() == ".md" and target.is_file():
                pending.append(target)
    return seen


def plugin_skill_names(skill_dir: Path) -> set[str]:
    skills_root = skill_dir.parent
    return {path.name for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()}


def phase_ids(pattern: re.Pattern[str], text: str) -> list[str]:
    return list(dict.fromkeys(pattern.findall(text)))


def audit(skill_dir: Path, requested_pattern: str) -> dict:
    skill_dir = skill_dir.resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_dir.is_dir() or not skill_md.is_file():
        raise ValueError(f"skill directory must contain SKILL.md: {skill_dir}")

    text = skill_md.read_text(encoding="utf-8")
    findings: list[Finding] = []

    def add(code: str, severity: str, path: Path, line: int, message: str, recommendation: str) -> None:
        try:
            display = str(path.resolve().relative_to(skill_dir))
        except ValueError:
            display = str(path)
        findings.append(Finding(code, severity, display, line, message, recommendation))

    try:
        frontmatter = parse_frontmatter(text)
    except (ValueError, yaml.YAMLError) as exc:
        add("SD001", "error", skill_md, 1, str(exc), "添加包含 name 和 description 的有效 YAML frontmatter。")
        frontmatter = {}

    name = str(frontmatter.get("name", ""))
    description = str(frontmatter.get("description", ""))
    if not name or not description:
        add("SD002", "error", skill_md, 1, "frontmatter 缺少 name 或 description。", "补齐稳定名称和可区分的使用说明。")
    if name and name != skill_dir.name:
        add("SD003", "error", skill_md, 2, "frontmatter name 与目录名不一致。", "使用与目录逐字一致的 name。")
    if description and "use when" not in description.lower():
        add("SD004", "error", skill_md, line_of(text, "description:"), "description 未说明 Use when 路由条件。", "补充真实使用时机和必要边界。")

    declared_context = requested_pattern if requested_pattern != "auto" else infer_declared_context(name, description, text)
    context_source = "explicit" if requested_pattern != "auto" else "inferred-for-reporting"

    openai_yaml = skill_dir / "agents" / "openai.yaml"
    if not openai_yaml.is_file():
        add("SD005", "error", openai_yaml, 1, "缺少 agents/openai.yaml。", "补充 GainFactor Skill UI 元数据。")
    else:
        openai_text = openai_yaml.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(openai_text) or {}
            interface = data.get("interface", {}) if isinstance(data, dict) else {}
            missing = sorted(INTERFACE_KEYS - set(interface)) if isinstance(interface, dict) else sorted(INTERFACE_KEYS)
            if missing:
                add("SD006", "error", openai_yaml, 1, f"UI 元数据缺少：{', '.join(missing)}。", "补齐全部 interface 字段。")
            if isinstance(interface, dict):
                for key in ("icon_small", "icon_large"):
                    value = interface.get(key)
                    if isinstance(value, str) and not (skill_dir / value).resolve().is_file():
                        add("SD007", "error", openai_yaml, line_of(openai_text, key), f"{key} 指向不存在的文件。", "复用插件品牌资源或修正路径。")
        except yaml.YAMLError as exc:
            add("SD008", "error", openai_yaml, 1, f"agents/openai.yaml 无法解析：{exc}", "修正 YAML。")

    references_dir = skill_dir / "references"
    reference_files = sorted(references_dir.rglob("*.md")) if references_dir.is_dir() else []
    markdown_files = [skill_md, *reference_files]
    for source in markdown_files:
        source_text = source.read_text(encoding="utf-8")
        for raw in LINK_RE.findall(source_text):
            target = local_target(source, raw)
            if target and not target.exists():
                add("SD009", "error", source, line_of(source_text, raw), f"本地引用不存在：{raw}", "修正引用或补充真实资源。")
            if target and "assets" in target.parts and target.suffix.lower() == ".md":
                add("SD010", "warning", source, line_of(source_text, raw), "Markdown 说明文件位于 assets 并被当作指令读取。", "将说明移入 references；assets 只保留输出资产。")

    reachable = reachable_markdown(skill_dir)
    for reference in reference_files:
        if reference.resolve() not in reachable:
            add("SD011", "warning", reference, 1, "reference 无法从入口或已路由 reference 到达。", "添加带使用条件的链接，或删除无用文件。")

    checklist_ids = phase_ids(CHECKLIST_PHASE_RE, text)
    heading_ids = phase_ids(HEADING_PHASE_RE, text)
    if checklist_ids and heading_ids and set(checklist_ids) != set(heading_ids):
        add(
            "SD012",
            "warning",
            skill_md,
            1,
            f"进度清单 Phase ID {checklist_ids} 与正文 Phase ID {heading_ids} 不一致。",
            "让清单和正文使用相同 Phase ID；名称可以简写，正文不必复制清单。",
        )

    valid_invocations = plugin_skill_names(skill_dir) | EXTERNAL_INVOCATIONS | PLACEHOLDER_INVOCATIONS
    for source in markdown_files:
        source_text = source.read_text(encoding="utf-8")
        for invocation in sorted(set(INVOCATION_RE.findall(source_text)) - valid_invocations):
            add(
                "SD013",
                "error",
                source,
                line_of(source_text, f"${invocation}"),
                f"引用不存在或未登记的 Skill：${invocation}",
                "改用当前 canonical Skill 名称；若属于配套插件，先在检查器的显式外部清单中登记。",
            )

    assets_dir = skill_dir / "assets"
    scripts_dir = skill_dir / "scripts"
    metrics = {
        "entryLines": len(text.splitlines()),
        "referenceFiles": len(reference_files),
        "reachableReferenceFiles": sum(path.resolve() in reachable for path in reference_files),
        "assetFiles": sum(path.is_file() for path in assets_dir.rglob("*")) if assets_dir.is_dir() else 0,
        "scriptFiles": sum(path.is_file() for path in scripts_dir.rglob("*")) if scripts_dir.is_dir() else 0,
        "checklistPhaseIds": checklist_ids,
        "bodyPhaseIds": heading_ids,
    }
    summary = {severity + "s": sum(item.severity == severity for item in findings) for severity in ("error", "warning", "note")}
    return {
        "schemaVersion": SCHEMA_VERSION,
        "scope": "structural",
        "skill": name or skill_dir.name,
        "pattern": declared_context,
        "patternSource": context_source,
        "semanticApproval": None,
        "metrics": metrics,
        "summary": summary,
        "findings": [asdict(item) for item in findings],
    }


def render_text(report: dict) -> str:
    summary = report["summary"]
    metrics = report["metrics"]
    lines = [
        f"Skill: {report['skill']}",
        f"Scope: {report['scope']} (no semantic approval)",
        f"Pattern context: {report['pattern']} ({report['patternSource']})",
        f"Metrics: {metrics['entryLines']} entry lines, {metrics['referenceFiles']} references, {metrics['assetFiles']} assets, {metrics['scriptFiles']} scripts",
        f"Summary: {summary['errors']} error, {summary['warnings']} warning, {summary['notes']} note",
    ]
    for item in report["findings"]:
        lines.append(f"[{item['severity'].upper()}] {item['code']} {item['path']}:{item['line']} {item['message']}")
        lines.append(f"  Recommendation: {item['recommendation']}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        report = audit(args.skill_directory, args.pattern)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
