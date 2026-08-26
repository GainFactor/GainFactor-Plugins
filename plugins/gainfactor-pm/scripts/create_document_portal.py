#!/usr/bin/env python3
"""Create or extend a document review portal from the bundled UI template."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = PLUGIN_ROOT / "assets" / "document-review-portal"
MANIFEST_NAME = ".gainfactor-documents.json"
LAUNCHER_SCRIPT = "portal-control.py"
GROUPS = {
    "product-requirements": {
        "title": "产品需求",
        "types": {
            "PRODUCT-DEFINITION",
            "USER-PERSONA",
            "COMPETITIVE-ANALYSIS",
            "PRODUCT-METRICS",
            "BRD",
            "PRD",
            "USER-JOURNEY",
            "DOMAIN-MODEL",
        },
    },
    "technical-design": {"title": "技术设计", "types": {"API", "API-CONTRACT", "HLD", "LLD"}},
    "quality-delivery": {
        "title": "质量与交付",
        "types": {"TEST-STRATEGY", "TEST-SPEC", "RUNBOOK"},
    },
    "other": {"title": "其他文档", "types": set()},
}
ARTIFACTS = {
    "product-definition": {"routeSuffix": "product-definition", "documentType": "Product-Definition"},
    "brd": {"routeSuffix": "brd", "documentType": "BRD"},
    "prd": {"routeSuffix": "prd", "documentType": "PRD"},
    "user-journey": {"routeSuffix": "user-journey", "documentType": "User-Journey"},
    "user-persona": {"routeSuffix": "user-persona", "documentType": "User-Persona"},
    "competitive-analysis": {"routeSuffix": "competitive-analysis", "documentType": "Competitive-Analysis"},
    "product-metrics": {"routeSuffix": "metrics", "documentType": "Product-Metrics"},
    "domain-model": {"routeSuffix": "domain-model", "documentType": "Domain-Model"},
    "api-contract": {"routeSuffix": "api-contract", "documentType": "API-Contract"},
    "hld": {"routeSuffix": "hld", "documentType": "HLD"},
    "lld": {"routeSuffix": "lld", "documentType": "LLD"},
    "test-strategy": {"routeSuffix": "test-strategy", "documentType": "Test-Strategy"},
    "test-spec": {"routeSuffix": "test-spec", "documentType": "Test-Spec"},
    "runbook": {"routeSuffix": "runbook", "documentType": "Runbook"},
    "guardrails": {"routeSuffix": "guardrails", "documentType": "Guardrails"},
}


def default_slug(path: Path) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")
    return slug or "document"


def infer_workspace_root(document: Path, explicit_target: Path | None) -> Path:
    for candidate in (document.parent, *document.parents):
        docs_root = candidate / "docs/gainfactor"
        if docs_root.is_dir() and document.is_relative_to(docs_root):
            return candidate
        if (candidate / ".git").exists():
            return candidate
    if explicit_target is not None:
        return Path(os.path.commonpath((document.parent, explicit_target.parent))).resolve()
    return Path.cwd().resolve()


def workspace_relative(path: Path, workspace_root: Path) -> str:
    return Path(os.path.relpath(path, workspace_root)).as_posix()


def load_manifest(target: Path) -> dict:
    path = target / MANIFEST_NAME
    if not path.exists():
        return {"documents": {}}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("documents"), dict):
        raise ValueError(f"Invalid portal manifest: {path}")
    return value


def default_group(document_type: str) -> str:
    normalized = re.sub(r"[ _]+", "-", document_type.strip().upper())
    for group, config in GROUPS.items():
        if normalized in config["types"]:
            return group
    return "other"


def write_navigation(target: Path, manifest: dict) -> None:
    docs_root = target / "content/docs"
    active_groups: dict[str, list[str]] = {}
    group_titles: dict[str, str] = {}
    for route, document in manifest["documents"].items():
        group = document["group"]
        active_groups.setdefault(group, []).append(Path(route).name)
        group_titles.setdefault(
            group,
            document.get("groupTitle") or GROUPS.get(group, {}).get("title") or group,
        )

    root_pages = ["index"]
    ordered_groups = [group for group in GROUPS if group in active_groups]
    ordered_groups.extend(group for group in active_groups if group not in GROUPS)
    for group in ordered_groups:
        pages = active_groups.get(group)
        if not pages:
            continue
        root_pages.append(group)
        group_root = docs_root / group
        group_root.mkdir(parents=True, exist_ok=True)
        (group_root / "meta.json").write_text(
            json.dumps(
                {"title": group_titles[group], "pages": pages},
                ensure_ascii=False,
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )

    (docs_root / "meta.json").write_text(
        json.dumps({"pages": root_pages}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_portal_data(target: Path, manifest: dict) -> None:
    serialized = json.dumps(manifest, ensure_ascii=False, indent=2)
    (target / MANIFEST_NAME).write_text(serialized + "\n", encoding="utf-8")
    (target / "lib/portal-data.generated.ts").write_text(
        "import type { PortalData } from './portal-data';\n\n"
        f"export const portalData: PortalData = {serialized};\n",
        encoding="utf-8",
    )
    write_navigation(target, manifest)


def install_launchers(target: Path) -> None:
    scripts_directory = target / "scripts"
    scripts_directory.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TEMPLATE_ROOT / "scripts" / LAUNCHER_SCRIPT, scripts_directory / LAUNCHER_SCRIPT)
    launchers = {
        "打开文档门户.command": "open",
        "关闭文档门户.command": "stop",
    }
    for filename, action in launchers.items():
        launcher = target / filename
        launcher.write_text(
            "#!/bin/zsh\n"
            "PORTAL_DIR=\"${0:A:h}\"\n"
            f'exec python3 "$PORTAL_DIR/scripts/{LAUNCHER_SCRIPT}" {action} "$PORTAL_DIR"\n',
            encoding="utf-8",
        )
        launcher.chmod(0o755)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("document", type=Path, help="Markdown or MDX document")
    parser.add_argument("target", type=Path, nargs="?", help="Portal output directory; defaults to .gainfactor/portal")
    parser.add_argument("--slug", default="", help="Stable URL slug inside the portal")
    parser.add_argument("--type", dest="document_type", default="")
    parser.add_argument("--collection", default="")
    parser.add_argument("--group", default="", help="Optional navigation group slug")
    parser.add_argument("--group-title", default="", help="Visible title for a custom navigation group")
    parser.add_argument("--subject-slug", default="", help="Stable product or project slug")
    parser.add_argument("--subject-title", default="", help="Visible product or project title")
    parser.add_argument("--artifact", default="", help="Standard artifact key")
    parser.add_argument("--dry-run", action="store_true", help="Resolve paths and identity without writing")
    parser.add_argument("--version", default="")
    parser.add_argument("--status", default="待评审")
    parser.add_argument("--owner", default="未指定")
    parser.add_argument("--updated", default=date.today().isoformat())
    parser.add_argument("--review", type=Path, help="Optional structured review JSON")
    parser.add_argument("--presentation", type=Path, help="Generic Portal Presentation JSON")
    parser.add_argument("--rich", action="store_true", help="Require a valid presentation manifest")
    args = parser.parse_args()
    if args.rich and not args.presentation:
        parser.error("--rich requires --presentation=<portal-presentation.json>")

    document = args.document.resolve()
    explicit_target = args.target.resolve() if args.target else None
    workspace_root = infer_workspace_root(document, explicit_target)
    target = explicit_target or workspace_root / ".gainfactor/portal"
    subject_slug = args.subject_slug.strip("/")
    subject_title = args.subject_title.strip()
    artifact_key = args.artifact.strip()
    standard_identity = any((subject_slug, subject_title, artifact_key))
    if standard_identity and not all((subject_slug, subject_title, artifact_key)):
        parser.error("--subject-slug, --subject-title, and --artifact must be provided together")
    if artifact_key and artifact_key not in ARTIFACTS:
        parser.error(f"Unsupported --artifact: {artifact_key}")
    artifact = ARTIFACTS.get(artifact_key)
    derived_slug = f"{subject_slug}-{artifact['routeSuffix']}" if artifact else ""
    slug = args.slug.strip("/") or derived_slug or default_slug(document)
    requested_group = args.group.strip("/") or subject_slug
    document_type = args.document_type or (artifact["documentType"] if artifact else "文档")
    collection = args.collection or subject_title or "产品文档"
    if not document.is_file():
        parser.error(f"Document does not exist: {document}")
    if subject_slug and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", subject_slug):
        parser.error("Subject slug must contain lowercase letters, digits, and hyphens")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        parser.error("Slug must contain lowercase letters, digits, and hyphens")
    if requested_group and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", requested_group):
        parser.error("Group must contain lowercase letters, digits, and hyphens")

    target_has_files = target.exists() and any(target.iterdir())
    if target_has_files and not (target / MANIFEST_NAME).is_file():
        parser.error(f"Target is not a GainFactor document portal: {target}")

    manifest = load_manifest(target) if (target / MANIFEST_NAME).is_file() else {"documents": {}}
    existing_route = next(
        (
            route
            for route, value in manifest["documents"].items()
            if value.get("sourceSlug") == slug or Path(route).name == slug
        ),
        None,
    )
    existing_document = manifest["documents"].get(existing_route, {})
    group = existing_document.get("group") or requested_group or default_group(document_type)
    group_title = (
        existing_document.get("groupTitle")
        or args.group_title.strip()
        or subject_title
        or GROUPS.get(group, {}).get("title")
    )
    if not group_title:
        parser.error("A custom --group requires --group-title")
    route = existing_route or f"{group}/{slug}"
    source_path = workspace_relative(document, workspace_root)
    tracked_source = existing_document.get("sourcePath")
    if tracked_source and tracked_source != source_path:
        parser.error(f"Route {route} already belongs to source {tracked_source}")

    if args.dry_run:
        print(json.dumps({
            "source": str(document),
            "sourcePath": source_path,
            "target": str(target),
            "group": group,
            "groupTitle": group_title,
            "route": route,
            "artifactKey": artifact_key or existing_document.get("artifactKey") or "",
            "action": "update" if existing_route else "create",
        }, ensure_ascii=False, indent=2))
        return 0

    if not target.exists() or not target_has_files:
        shutil.copytree(
            TEMPLATE_ROOT,
            target,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("node_modules", ".next", ".source", "out", "*.tsbuildinfo"),
        )
    if existing_route and "/" not in existing_route:
        route = f"{group}/{slug}"
        legacy_path = target / f"content/docs/{existing_route}.mdx"
        migrated_path = target / f"content/docs/{route}.mdx"
        migrated_path.parent.mkdir(parents=True, exist_ok=True)
        if legacy_path.is_file():
            legacy_path.replace(migrated_path)
        manifest["documents"].pop(existing_route)
    output_path = f"content/docs/{route}.mdx"
    (target / output_path).parent.mkdir(parents=True, exist_ok=True)
    command = [
        "node",
        "scripts/import-document.mjs",
        str(document),
        output_path,
    ]
    subprocess.run(command, cwd=target, check=True)
    compile_command = [
            "python3",
            str(PLUGIN_ROOT / "scripts/compile_portal_document.py"),
            str(target / output_path),
        ]
    if args.presentation:
        compile_command.append(f"--presentation={args.presentation.resolve()}")
    if args.rich:
        compile_command.append("--validate")
    compiled = subprocess.run(compile_command, capture_output=True, text=True)
    if compiled.returncode != 0:
        parser.error(compiled.stderr.strip() or compiled.stdout.strip() or "Portal document validation failed")
    presentation_payload = json.loads(compiled.stdout)

    review = {"conclusion": "尚未生成评审结果", "issues": []}
    if args.review:
        review_path = args.review.resolve()
        if not review_path.is_file():
            parser.error(f"Review JSON does not exist: {review_path}")
        review = json.loads(review_path.read_text(encoding="utf-8"))
        if not isinstance(review.get("conclusion"), str) or not isinstance(review.get("issues"), list):
            parser.error("Review JSON must contain a string conclusion and an issues array")
        for issue in review["issues"]:
            required = ("id", "severity", "title", "sectionId")
            if not isinstance(issue, dict) or any(not isinstance(issue.get(key), str) for key in required):
                parser.error(f"Each review issue must contain string fields: {', '.join(required)}")
            if issue["severity"] not in {"P0", "P1", "P2"}:
                parser.error("Review issue severity must be P0, P1, or P2")

    manifest["documents"][route] = {
        "sourceSlug": slug,
        "group": group,
        "groupTitle": group_title,
        "artifactKey": artifact_key or existing_document.get("artifactKey") or "",
        "sourcePath": source_path,
        "documentType": document_type,
        "collection": collection,
        "version": args.version or "—",
        "status": args.status,
        "owner": args.owner,
        "updated": args.updated,
        "presentation": presentation_payload["presentation"],
        "review": review,
    }
    write_portal_data(target, manifest)
    install_launchers(target)
    print(f"Added {document_type} document at /docs/{route}: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
