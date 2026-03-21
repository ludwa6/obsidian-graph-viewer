# Obsidian Graph Viewer

Interactive force-directed graph visualization of your Obsidian vault notes, served as a static site via GitHub Pages.

## Live Demo

Visit: https://ludwa6.github.io/obsidian-graph-viewer/

## Features

- **Force-directed graph** — notes as nodes, wikilinks as edges
- **Color by folder** — each folder gets a distinct color
- **Size by connections** — more links = bigger node
- **Click to highlight** — click a node to see its neighbors and open detail panel
- **Hover to focus** — hover a node to dim unrelated nodes and edges
- **Search & filter** — find notes by title, folder, or tag (dims non-matching nodes)
- **Broken link detection** — dashed red edges for missing targets, with phantom nodes
- **Drag nodes** — reposition nodes interactively
- **Zoom & pan** — scroll to zoom, drag background to pan
- **Dark theme** — easy on the eyes
- **Responsive** — works on mobile

### Filter Controls

The filter panel (top-left, collapsible) provides Obsidian-style graph filtering:

- **Tag Edges** — Synthesize edges between notes sharing frontmatter tags. Each tag gets its own checkbox and color. Tags with more notes are listed first. Tags default to OFF so you can build up complexity incrementally — start with specific tags like `intent` (5 notes, 10 edges) before enabling broad tags like `active` (18 notes, 153 edges).
- **Show Orphans** — Toggle visibility of nodes with zero edges (after all other filters). Default ON. Turn OFF to focus on connected notes.
- **Show Broken Links** — Toggle visibility of phantom nodes representing missing wikilink targets. Default ON.
- **Existing Files Only** — Hide all phantom/broken nodes. Superset of the broken links toggle.

Tag edges are visually distinct from wikilinks: thinner, dashed, and colored per tag. The legend updates dynamically to show active tag edge colors, and the stats bar reflects filtered counts.

## Updating the Graph Data

To regenerate graph-data.json from your vault:

```bash
# Install dependency (one-time)
pip install pyyaml

# Parse your vault and generate the JSON
python parse_vault.py /path/to/your/vault graph-data.json

# Commit and push — GitHub Pages will serve the updated graph
git add graph-data.json
git commit -m "Refresh graph data"
git push
```

The site updates automatically via GitHub Pages after each push. Run the parser whenever your vault changes and you want a fresh visualization.

## Tech Stack

- **[D3.js](https://d3js.org/) v7** — force simulation + SVG rendering via CDN
- **Vanilla HTML/CSS/JS** — single-file app, no build step required
- **Python** — vault parser (stdlib + PyYAML)

## File Structure

```
index.html        — Single-file web app (CSS + JS inline, uses D3.js for SVG graph)
graph-data.json   — Generated graph data from your vault
parse_vault.py    — Python script to parse .md files into graph JSON
```

## How Tag Edges Work

The app reads `frontmatter.tags` from each node in graph-data.json. For any tag shared by 2+ notes, it synthesizes edges between all pairs. For example, if three notes share the tag `intent`, the app creates 3 edges (A↔B, A↔C, B↔C). These edges are computed at runtime — no changes to graph-data.json are needed.

Tag edge colors are assigned automatically and shown in the legend. The force simulation treats tag edges as weaker links (lower strength, shorter distance) so they cluster tagged notes without overwhelming the layout.

## License

MIT
