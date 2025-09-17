# NM Antibiogram Website Codex

This repository hosts the static website for the Digital Northwestern Medicine Antibiogram. It provides interactive susceptibility data and is deployed as a GitHub Pages site.

## Repository Structure

- `index.html` – Contains markup, styling, and JavaScript logic. The script aggregates the Markdown data sources into the structure required by the UI.
- `data/index.json` – Manifest of Markdown files grouped by site/context.
- `data/2024/**/*.md` – Markdown tables with JSON front matter describing the site, context metadata (notes/flags), and susceptibility table.
- `scripts/generate_markdown_data.py` – Helper to regenerate Markdown files (and the manifest) from `ABSP.xlsx`.
- `CNAME` – Configures the custom domain `nmantibiogram.org`.

## Data Model (derived from Markdown files)

Each Markdown file starts with JSON front matter describing the source:

- `site_id`, `site`, `region`, `display` – Values used to build the dropdown label.
- `year` – Year the antibiogram represents.
- `context` / `context_label` – Canonical and display labels for the specimen context.
- `notes` – Optional array of strings shown when a context is selected.
- `flags` – Optional array of identifiers looked up in the legend badge map.

The table immediately after the front matter provides an `Organism` column, an `Isolates` column, and one column per antibiotic. During initialization the script groups entries by site and context, normalizes numeric values, attaches contraindication metadata, and sorts organisms alphabetically. Blank rows and section headers (e.g., “GRAM POSITIVES”) are ignored.

A site entry in memory includes:

- `id` – Slugified value of the site identifier.
- `name` – Display label built from the front matter (`display`).
- `contexts` – Sorted list of specimen types available for the site.

Each context object contains:

- `id` – Slug derived from the context key.
- `name` – Human-readable label from `context_label`.
- `notes` – Front matter `notes` array, shown above the results list (merged with any legend flag messages).
- `organisms` – Alphabetical list of organisms with susceptibility data.

An organism object carries:

- `id` – Slugified organism name.
- `display` – Original organism label from the Markdown table.
- `isolates` – Parsed isolate count (if available).
- `antibiotics` – Susceptibility records sorted highest-to-lowest by `pctS` (susceptible percent).

Color bands remain defined as:

- **Green** ≥80%
- **Yellow** 70–79%
- **Red** ≤69%

The hint text shown in the footer is a constant defined in `index.html`.

## User Interface (`index.html`)

1. **Site Selection** – Dropdown (`<select id="site">`) populated from the aggregated dataset.
2. **Context Tabs** – Buttons appear after a site is chosen.
3. **Organism Search** – Input filters organisms by name.
4. **Results View** – Displays antibiotic susceptibilities with color-coded chips.
5. **Filter ≥80%** – Checkbox hides antibiotics below 80% susceptibility.
6. **Navigation** – Back button returns from the results view to the organism list.
7. **Legend & Disclaimer** – Footer shows the color key, constant hint text, and the disclaimer (“Use patient-level cultures and ID consult for definitive therapy.”).

## Script Overview

Key pieces of the embedded script:

- `DATA_INDEX` – Path to the JSON manifest that lists Markdown sources.
- `loadData()` – Fetches the manifest, retrieves each Markdown file, applies contraindication metadata, and initializes the UI.
- `loadMarkdownData()` / `parseMarkdown()` – Download and parse Markdown front matter + tables into intermediate objects.
- `buildSites(entries)` – Groups entries into the site/context/organism hierarchy, normalizes numeric values, and sorts the resulting lists.
- `init()` – Wires event listeners and shows the initial view.
- `populateSites()`, `renderContexts()`, `renderOrganisms()` – Render each step of the selection workflow.
- `selectOrganism()` & `renderAntibiotics()` – Populate the detailed results view, surface context notes/badges, and respond to the ≥80% filter.

Accessibility considerations remain the same: `prefers-reduced-motion` styling, visually hidden labels, sticky header/footer, and consistent keyboard focus states.
