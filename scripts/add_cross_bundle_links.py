#!/usr/bin/env python3
"""
Add cross-bundle links between OKF bundles (as per OKF_SPECS.md Phase 4).

Creates explicit links between:
- Documentation concepts ↔ Code implementation concepts
- Specs ↔ Strategy classes
- Deployment guides ↔ Docker configs
- Workflows ↔ Pipeline scripts
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


# Cross-bundle link mappings based on your project structure
# Use the actual concept_ids from the bundles
CROSS_BUNDLE_LINKS = [
    # Docs → Code links
    {
        "source_bundle": "docs_bundle",
        "source_concept": "FREQTRADE_STRATEGY_SPEC",
        "target_bundle": "strategies_bundle",
        "target_concept": "Strategy322sgo",
        "relationship": "specifies",
    },
    {
        "source_bundle": "docs_bundle",
        "source_concept": "rdql-karakana-freqtrade-workflow",
        "target_bundle": "scripts_bundle",
        "target_concept": "quizgen",
        "relationship": "describes_pipeline",
    },
    {
        "source_bundle": "docs_bundle",
        "source_concept": "rdql-karakana-freqtrade-workflow",
        "target_bundle": "scripts_bundle",
        "target_concept": "convert_docs_to_okf",
        "relationship": "uses_tool",
    },
    {
        "source_bundle": "docs_bundle",
        "source_concept": "freqtrade-karakana-deployment",
        "target_bundle": "docs_bundle",
        "target_concept": "docker-compose",
        "relationship": "references_config",
    },
    {
        "source_bundle": "docs_bundle",
        "source_concept": "freqtrade-karakana-deployment",
        "target_bundle": "docs_bundle",
        "target_concept": "freqtrade-karakana-thresholds",
        "relationship": "uses_thresholds",
    },
    {
        "source_bundle": "docs_bundle",
        "source_concept": "freqtrade-karakana-quickstart",
        "target_bundle": "docs_bundle",
        "target_concept": "freqtrade-karakana-deployment",
        "relationship": "guides_to",
    },
    {
        "source_bundle": "docs_bundle",
        "source_concept": "freqtrade-karakana-quickstart",
        "target_bundle": "strategies_bundle",
        "target_concept": "Strategy322sgo",
        "relationship": "starts_strategy",
    },
    
    # Code → Docs links (reverse)
    {
        "source_bundle": "strategies_bundle",
        "source_concept": "Strategy322sgo",
        "target_bundle": "docs_bundle",
        "target_concept": "FREQTRADE_STRATEGY_SPEC",
        "relationship": "implements",
    },
    {
        "source_bundle": "strategies_bundle",
        "source_concept": "Strategy322sgo/populate_entry_trend",
        "target_bundle": "docs_bundle",
        "target_concept": "FREQTRADE_STRATEGY_SPEC",
        "relationship": "implements_section",
    },
    {
        "source_bundle": "strategies_bundle",
        "source_concept": "Strategy322sgo/populate_exit_trend",
        "target_bundle": "docs_bundle",
        "target_concept": "FREQTRADE_STRATEGY_SPEC",
        "relationship": "implements_section",
    },
    {
        "source_bundle": "strategies_bundle",
        "source_concept": "Strategy322sgo/confirm_trade_entry",
        "target_bundle": "docs_bundle",
        "target_concept": "freqtrade-karakana-deployment",
        "relationship": "used_in_deployment",
    },
    {
        "source_bundle": "scripts_bundle",
        "source_concept": "quizgen",
        "target_bundle": "docs_bundle",
        "target_concept": "rdql-karakana-freqtrade-workflow",
        "relationship": "generates_qa_for",
    },
    {
        "source_bundle": "scripts_bundle",
        "source_concept": "convert_docs_to_okf",
        "target_bundle": "docs_bundle",
        "target_concept": "rdql-karakana-freqtrade-workflow",
        "relationship": "converts_docs_for",
    },
    {
        "source_bundle": "code_bundle",
        "source_concept": "bot/NVIDIAEmbeddings",
        "target_bundle": "docs_bundle",
        "target_concept": "rdql-karakana-freqtrade-workflow",
        "relationship": "provides_embeddings_for",
    },
]


def find_concept_file(bundle_dir: Path, concept_id: str) -> Path | None:
    """Find the .md file for a concept ID."""
    # Try exact match first
    concept_file = bundle_dir / f"{concept_id}.md"
    if concept_file.exists():
        return concept_file
    
    # Try with path components
    parts = concept_id.split("/")
    if len(parts) > 1:
        concept_file = bundle_dir.joinpath(*parts).with_suffix(".md")
        if concept_file.exists():
            return concept_file
    
    # Search recursively
    for md_file in bundle_dir.rglob("*.md"):
        if md_file.name in ("index.md", "log.md"):
            continue
        try:
            content = md_file.read_text()
            if content.startswith("---\n"):
                fm_end = content.find("\n---\n", 4)
                if fm_end > 0:
                    import yaml
                    fm = yaml.safe_load(content[4:fm_end])
                    if fm.get("concept_id") == concept_id:
                        return md_file
        except Exception:
            pass
    
    return None


def add_cross_link(
    source_file: Path,
    target_bundle: str,
    target_concept: str,
    relationship: str,
) -> bool:
    """Add a cross-bundle link to the source concept file."""
    try:
        content = source_file.read_text()
        
        if not content.startswith("---\n"):
            return False
        
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return False
        
        import yaml
        fm = yaml.safe_load(parts[1]) or {}
        body = parts[2]
        
        # Build the link
        link_text = f"[{target_concept.split('/')[-1]}](/{target_bundle}/{target_concept}.md)"
        link_line = f"\n* {relationship}: {link_text} (in {target_bundle})\n"
        
        # Add to Relationships section or create one
        if "## Relationships" in body:
            body = body.replace("## Relationships", f"## Relationships{link_line}", 1)
        else:
            # Add at end of body
            body = body.rstrip() + f"\n\n## Cross-Bundle Links\n{link_line}"
        
        # Write back
        new_content = "---\n" + yaml.dump(fm, default_flow_style=False, allow_unicode=True) + "---\n" + body
        source_file.write_text(new_content)
        return True
        
    except Exception as e:
        print(f"  Error updating {source_file}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Add cross-bundle links between OKF bundles")
    parser.add_argument("--bundles-dir", default="docs/okfs", help="Directory containing bundles")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without writing")
    args = parser.parse_args()
    
    bundles_dir = Path(args.bundles_dir).resolve()
    
    print("=== Adding Cross-Bundle Links ===")
    print(f"Bundles directory: {bundles_dir}")
    print(f"Links to add: {len(CROSS_BUNDLE_LINKS)}")
    
    success = 0
    failed = 0
    
    for link in CROSS_BUNDLE_LINKS:
        source_bundle = bundles_dir / link["source_bundle"]
        target_bundle = bundles_dir / link["target_bundle"]
        
        source_file = find_concept_file(source_bundle, link["source_concept"])
        
        if not source_file:
            print(f"  ❌ Source not found: {link['source_bundle']}/{link['source_concept']}")
            failed += 1
            continue
        
        # Verify target exists
        target_file = find_concept_file(target_bundle, link["target_concept"])
        if not target_file:
            print(f"  ⚠️  Target not found: {link['target_bundle']}/{link['target_concept']} (linking anyway)")
        
        if args.dry_run:
            print(f"  Would link: {source_file.relative_to(bundles_dir)} → {link['target_bundle']}/{link['target_concept']} ({link['relationship']})")
            success += 1
        else:
            if add_cross_link(source_file, link["target_bundle"], link["target_concept"], link["relationship"]):
                print(f"  ✅ Linked: {source_file.name} → {link['target_bundle']}/{link['target_concept']} ({link['relationship']})")
                success += 1
            else:
                print(f"  ❌ Failed: {source_file.name}")
                failed += 1
    
    print(f"\nDone: {success} linked, {failed} failed")
    
    if failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit(main())