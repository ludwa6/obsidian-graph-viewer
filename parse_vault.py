#!/usr/bin/env python3
"""Obsidian Vault Parser - Extracts wikilinks, tags, metadata from .md files and generates graph-data.json"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any

try:
    import yaml
except ImportError:
    yaml = None


def normalize_node_id(file_path: Path, vault_root: Path) -> str:
    relative = file_path.relative_to(vault_root)
    return str(relative.with_suffix('')).replace('\\', '/')


def extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    if not content.startswith('---'):
        return {}, content
    lines = content.split('\n', 1)
    if len(lines) < 2:
        return {}, content
    remaining = lines[1]
    end_match = remaining.find('\n---\n')
    if end_match == -1:
        return {}, content
    frontmatter_text = remaining[:end_match]
    content_after = remaining[end_match + 5:]
    try:
        if yaml:
            frontmatter = yaml.safe_load(frontmatter_text) or {}
        else:
            frontmatter = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    except Exception:
        frontmatter = {}
    return frontmatter, content_after


def extract_wikilinks(content: str) -> List[str]:
    content_clean = re.sub(r'```[\s\S]*?```', '', content)
    content_clean = re.sub(r'`[^`]*`', '', content_clean)
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    matches = re.findall(pattern, content_clean)
    return [match.strip() for match in matches]


def extract_tags(content: str) -> List[str]:
    content_clean = re.sub(r'```[\s\S]*?```', '', content)
    content_clean = re.sub(r'`[^`]*`', '', content_clean)
    pattern = r'(?<![/\w#:.])#([\w\-]+)(?!\s|\d)'
    matches = re.findall(pattern, content_clean)
    return list(set(tag.lower() for tag in matches))


def extract_title(file_path: Path, content: str) -> str:
    lines = content.split('\n')
    for line in lines:
        if line.startswith('# '):
            return line[2:].strip()
    return file_path.stem


def parse_vault(vault_root: str) -> Dict[str, Any]:
    vault_path = Path(vault_root).resolve()
    if not vault_path.is_dir():
        raise ValueError(f"Vault path does not exist: {vault_root}")
    md_files = [f for f in vault_path.rglob('*.md') if '.obsidian' not in f.parts]
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, str]] = []
    all_targets: Set[str] = set()
    broken_links: List[Dict[str, str]] = []

    for file_path in md_files:
        node_id = normalize_node_id(file_path, vault_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception:
            continue
        frontmatter, md_content = extract_frontmatter(file_content)
        title = extract_title(file_path, md_content)
        tags = extract_tags(md_content)
        folder = str(file_path.parent.relative_to(vault_path)).replace('\\', '/')
        if folder == '.':
            folder = ''
        nodes[node_id] = {
            'id': node_id, 'title': title, 'folder': folder, 'tags': tags,
            'link_count': 0, 'has_frontmatter': len(frontmatter) > 0, 'frontmatter': frontmatter
        }
        all_targets.add(node_id)

    for file_path in md_files:
        node_id = normalize_node_id(file_path, vault_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except Exception:
            continue
        _, md_content = extract_frontmatter(file_content)
        wikilinks = extract_wikilinks(md_content)
        seen_edges = set()
        for target in wikilinks:
            target_node_id = None
            if target in all_targets:
                target_node_id = target
            else:
                current_folder = nodes[node_id]['folder']
                if current_folder:
                    potential_id = f"{current_folder}/{target}"
                    if potential_id in all_targets:
                        target_node_id = potential_id
            nodes[node_id]['link_count'] += 1
            edge_key = (node_id, target_node_id if target_node_id else target)
            if edge_key not in seen_edges:
                if target_node_id:
                    edges.append({'source': node_id, 'target': target_node_id, 'type': 'wikilink'})
                else:
                    edges.append({'source': node_id, 'target': target, 'type': 'broken'})
                    broken_links.append({'source': node_id, 'target': target})
                seen_edges.add(edge_key)

    orphan_notes = [nid for nid, n in nodes.items() if n['link_count'] == 0]
    folders = sorted(set(n['folder'] for n in nodes.values() if n['folder']))
    return {
        'version': '1.0.0', 'generated_at': datetime.utcnow().isoformat() + 'Z',
        'vault_root': str(vault_path),
        'nodes': sorted(nodes.values(), key=lambda n: n['id']), 'edges': edges,
        'metadata': {'total_notes': len(nodes), 'total_links': len(edges),
                     'folders': folders, 'orphan_notes': sorted(orphan_notes),
                     'broken_links': broken_links}
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_vault.py <vault_path> [output_file]", file=sys.stderr)
        sys.exit(1)
    vault_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        graph_data = parse_vault(vault_path)
        output_json = json.dumps(graph_data, indent=2)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_json)
            print(f"Graph data written to {output_file}", file=sys.stderr)
        else:
            print(output_json)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
