# Obsidian Graph Viewer

Interactive force-directed graph visualization of your Obsidian vault notes, served as a static site via GitHub Pages.

## Live Demo

Visit: https://ludwa6.github.io/obsidian-graph-viewer/

## Features

- **Force-directed graph** — notes as nodes, wikilinks as edges
- **Color by folder** — each folder gets a distinct color
- **Size by connections** — more links = bigger node
- **Click to highlight** — click a node to see its neighbors
- **Search & filter** — find notes by title, folder, or path
- **Broken link detection** — dashed red edges for missing targets
- **Dark theme** — easy on the eyes
- **Responsive** — works on mobile

## How to Use with Your Vault

1. Clone this repo
2. Install PyYAML: `pip install pyyaml`
3. Run the parser against your vault:
   ```bash
   python parse_vault.py /path/to/your/vault graph-data.json
   ```
4. Commit and push — GitHub Pages will serve the updated graph

## Tech Stack

- **[force-graph](https://github.com/vasturiano/force-graph)** — canvas-based graph rendering via CDN
- **Vanilla HTML/CSS/JS** — no build step required
- **Python** — vault parser (stdlib + PyYAML)

## File Structure

```
index.html        — Single-file web app (CSS + JS inline)
graph-data.json   — Generated graph data from your vault
parse_vault.py    — Python script to parse .md files into graph JSON
```

## License

MIT
