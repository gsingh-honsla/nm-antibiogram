# NM Antibiogram Website Codex

This repository hosts the static website for the Digital Northwestern Medicine Antibiogram. It provides interactive susceptibility data and is deployed as a GitHub Pages site.

## Repository Structure

- `index.html` – Contains markup, styling, and JavaScript logic. The script aggregates the CSV data sources into the structure required by the UI.
- `*.csv` – Source antibiogram extracts segmented by site and specimen context. Each file shares the same set of headers.
- `CNAME` – Configures the custom domain `nmantibiogram.org`.

## Data Model (derived from CSV files)

Every CSV row includes the columns `Region`, `Site`, `Specimen_Type`, `Organism`, `Antibiotic`, and `Susceptibility_Percent`. During initialization the script groups rows by site and specimen type, then by organism, and produces antibiotic lists with susceptibility percentages. Context and antibiotic metadata such as badges, notes, or cautions are not provided by the CSVs, so the generated objects keep those arrays empty.

A site entry in memory includes:

- `id` – Slugified value of the `Site` column.
- `name` – Display label built from `Region` and `Site` (e.g., `"Northwest Region (Huntley/McHenry/Woodstock Hospitals)"`).
- `contexts` – Sorted list of specimen types available for the site.

Each context object contains:

- `id` – Slug based on `Specimen_Type`.
- `name` – Human-readable label (for example, `"ED"` is mapped to `"Emergency Department"`).
- `organisms` – Alphabetical list of organisms with susceptibility data.

An organism object carries:

- `id` – Slugified organism name.
- `display` – Original organism label from the CSV.
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

- `CSV_FILES` – Array of CSV filenames fetched at runtime.
- `loadData()` – Downloads all CSV files, builds the in-memory dataset, and initializes the UI.
- `loadCsv(path)` – Fetches an individual CSV and returns parsed row objects.
- `parseCsv(text)` – Lightweight parser that handles quoted values and produces objects for each row.
- `buildSites(rows)` – Groups rows into the site/context/organism hierarchy and sorts the resulting lists.
- `init()` – Wires event listeners and shows the initial view.
- `populateSites()`, `renderContexts()`, `renderOrganisms()` – Render each step of the selection workflow.
- `selectOrganism()` & `renderAntibiotics()` – Populate the detailed results view and respond to the ≥80% filter.

Accessibility considerations remain the same: `prefers-reduced-motion` styling, visually hidden labels, sticky header/footer, and consistent keyboard focus states.
