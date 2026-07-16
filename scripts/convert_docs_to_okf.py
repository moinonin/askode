#!/usr/bin/env python3
"""
Convert markdown documentation files to OKF v0.2 format.

Usage:
    python scripts/convert_docs_to_okf.py [--source docs] [--output docs/okfs/docs_bundle]
"""

import argparse
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional


# Type mapping based on filename patterns
TYPE_MAP = {
    "SPEC": "Spec",
    "DEPLOYMENT": "DeploymentGuide",
    "QUICKSTART": "Quickstart",
    "WORKFLOW": "Workflow",
    "THRESHOLDS": "Config",
    "STRATEGY": "Strategy",
    "DOCKERFILE": "Config",
    "COMPOSE": "Config",
    "MAKEFILE": "Config",
    "TEMPLATE": "Config",
    "LEGACY": "Config",
    "RDQL": "Workflow",
}

# Domain tags based on content keywords
KEYWORD_TAGS = {
    "freqtrade": "freqtrade",
    "karakana": "karakana",
    "docker": "docker",
    "strategy": "strategy",
    "deployment": "deployment",
    "threshold": "threshold",
    "rl": "rl",
    "trading": "trading",
    "rl_hft": "rl-hft",
    "policy": "policy",
    "sgo": "sgo",
    "shadow": "shadow-trading",
    "artifact": "artifacts",
    "inference": "inference",
    "training": "training",
    "capital": "capital-guard",
    "governor": "governor",
    "risk": "risk-management",
}


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract existing YAML frontmatter if present."""
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            try:
                return yaml.safe_load(parts[1]) or {}, parts[2]
            except yaml.YAMLError:
                pass
    return {}, content


def infer_type_and_title(filepath: Path, content: str) -> tuple[str, str]:
    """Infer OKF type and title from filename and content."""
    name = filepath.stem.upper()
    
    # Check patterns
    for pattern, otype in TYPE_MAP.items():
        if pattern in name:
            title = filepath.stem.replace("-", " ").replace("_", " ").title()
            return otype, title
    
    # Check first heading in content
    heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if heading_match:
        title = heading_match.group(1).strip()
    else:
        title = filepath.stem.replace("-", " ").replace("_", " ").title()
    
    return "Document", title


def build_tags(filepath: Path, content: str, source_dir: Path) -> list[str]:
    """Generate tags from path and content."""
    tags = []
    
    # Path-based tags
    rel = filepath.relative_to(source_dir)
    parts = rel.parts
    if len(parts) > 1:
        tags.append(f"domain:{parts[0]}")
    tags.append(f"ext:{filepath.suffix[1:]}")
    
    # Content-based keyword tags
    content_lower = content.lower()
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword.lower() in content_lower:
            tags.append(tag)
    
    # File-type specific tags
    if filepath.suffix in [".mk", ".makefile"]:
        tags.append("makefile")
    if "docker" in filepath.name.lower():
        tags.append("docker")
    
    return list(set(tags))  # deduplicate


def extract_description(content: str, max_len: int = 200) -> str:
    """Extract first meaningful paragraph as description."""
    # Remove frontmatter if present
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            content = parts[2]
    
    # Find first non-heading paragraph
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("```"):
            return line[:max_len].strip()
    
    return ""


def convert_file(src: Path, dest: Path, source_dir: Path, repo_info: dict) -> None:
    """Convert a single markdown file to OKF format."""
    content = src.read_text(encoding="utf-8")
    existing_fm, body = extract_frontmatter(content)
    
    otype, title = infer_type_and_title(src, body)
    tags = build_tags(src, body, source_dir)
    description = existing_fm.get("description") or extract_description(body)
    
    # Build OKF frontmatter
    fm = {
        "okf_version": "0.2",
        "type": otype,
        "title": existing_fm.get("title", title),
        "description": description,
        "resource": f"github.com/your/repo/blob/main/{src}",
        "tags": tags,
        "timestamp": datetime.now().isoformat() + "Z",
        "concept_id": str(src.relative_to(source_dir).with_suffix("")),
    }
    
    # Add repo metadata if available
    if repo_info.get("branch"):
        fm["git_branch"] = repo_info["branch"]
    if repo_info.get("repo"):
        fm["git_repo"] = repo_info["repo"]
    
    # Preserve any additional existing frontmatter fields
    for key, value in existing_fm.items():
        if key not in fm:
            fm[key] = value
    
    # Write OKF file
    dest.parent.mkdir(parents=True, exist_ok=True)
    output = "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n\n" + body.lstrip()
    dest.write_text(output, encoding="utf-8")


def generate_index(bundle_dir: Path, source_dir: Path) -> None:
    """Generate root index.md for the bundle."""
    concepts = list(bundle_dir.rglob("*.md"))
    concepts = [c for c in concepts if c.name not in ("index.md", "log.md")]
    
    lines = ["# Documentation Knowledge Bundle\n"]
    lines.append(f"> OKF v0.2 bundle | {len(concepts)} concepts\n")
    
    # Group by type
    by_type = {}
    for c in concepts:
        content = c.read_text(encoding="utf-8")
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 2:
                try:
                    fm = yaml.safe_load(parts[1]) or {}
                    otype = fm.get("type", "Unknown")
                    title = fm.get("title", c.stem)
                    rel = c.relative_to(bundle_dir)
                    by_type.setdefault(otype, []).append((title, rel))
                except yaml.YAMLError:
                    pass
    
    for otype in sorted(by_type.keys()):
        items = sorted(by_type[otype])
        lines.append(f"\n## {otype}s\n")
        for title, rel in items:
            lines.append(f"- [{title}]({rel})")
    
    (bundle_dir / "index.md").write_text("\n".join(lines), encoding="utf-8")


def generate_log(bundle_dir: Path) -> None:
    """Generate log.md for the bundle."""
    ts = datetime.now().strftime("%Y-%m-%d")
    content = f"""# Change Log

## {ts}
* **Creation**: Initial OKF bundle generated from documentation
"""
    (bundle_dir / "log.md").write_text(content, encoding="utf-8")


def get_git_info(source_dir: Path) -> dict:
    """Get git metadata for tagging."""
    import subprocess
    info = {}
    try:
        branch = subprocess.check_output(
            ["git", "-C", str(source_dir), "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL, timeout=3
        ).decode().strip()
        info["branch"] = branch
    except Exception:
        pass
    try:
        remote = subprocess.check_output(
            ["git", "-C", str(source_dir), "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL, timeout=3
        ).decode().strip()
        repo = re.sub(r".*[:/](.+?)(\.git)?$", r"\1", remote)
        info["repo"] = repo
    except Exception:
        pass
    return info


def main():
    parser = argparse.ArgumentParser(description="Convert markdown docs to OKF format")
    parser.add_argument("--source", default="docs", help="Source documentation directory")
    parser.add_argument("--output", default="docs/okfs/docs_bundle", help="Output bundle directory")
    parser.add_argument("--exclude", action="append", default=["okfs"], help="Directories to exclude from scan")
    args = parser.parse_args()

    source_dir = Path(args.source).resolve()
    bundle_dir = Path(args.output).resolve()

    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}")
        return 1

    bundle_dir.mkdir(parents=True, exist_ok=True)

    # Get git info
    repo_info = get_git_info(source_dir)

    # Find all markdown files, excluding specified directories
    md_files = list(source_dir.rglob("*.md"))
    md_files = [f for f in md_files if f.is_file() and not any(excl in f.parts for excl in args.exclude)]

    # Also include .mk makefiles and dockerfiles
    mk_files = [f for f in source_dir.rglob("*.mk") if f.is_file() and not any(excl in f.parts for excl in args.exclude)]
    docker_files = [f for f in source_dir.rglob("Dockerfile*") if f.is_file() and not any(excl in f.parts for excl in args.exclude)]
    compose_files = [f for f in source_dir.rglob("docker-compose*") if f.is_file() and not any(excl in f.parts for excl in args.exclude)]
    makefiles = [f for f in source_dir.rglob("Makefile*") if f.is_file() and not any(excl in f.parts for excl in args.exclude)]

    all_files = md_files + mk_files + docker_files + compose_files + makefiles
    print(f"Converting {len(all_files)} files...")

    for src in all_files:
        if src.is_file():
            rel = src.relative_to(source_dir)
            dest = bundle_dir / rel.with_suffix(".md")
            convert_file(src, dest, source_dir, repo_info)
            print(f"  {rel} → {dest.relative_to(bundle_dir)}")

    generate_index(bundle_dir, source_dir)
    generate_log(bundle_dir)

    print(f"\nBundle created at: {bundle_dir}")
    print(f"Total concepts: {len(all_files)}")
    return 0


if __name__ == "__main__":
    exit(main())