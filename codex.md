# NM Antibiogram Website Codex

This repository hosts the static website for the Digital Northwestern Medicine Antibiogram. It provides interactive susceptibility data and is deployed as a GitHub Pages site.

## Repository Structure

- `index.html` – Contains all markup, styling, and JavaScript logic.
- `nm_antibiogram_full_final.json` – Primary dataset consumed by the web app.
- `nm_antibiogram_full_final_v6.json` – Previous version of the dataset retained for reference.
- `CNAME` – Configures the custom domain `nmantibiogram.org`.

## Data Model (`nm_antibiogram_full_final.json`)

Top-level keys:
- `version` – Dataset identifier.
- `legend` – Color band thresholds, hint text, and badge explanations.
- `sites` – Array of sites containing context and organism data.
- `generated_at` – ISO-8601 timestamp when the dataset was produced.

Each `site` entry contains an `id`, human-readable `name`, and a list of `contexts`. A `context` has its own `id`, `name`, data `source`, optional `flags`, and an array of `organisms`. Each `organism` lists its `id`, display name, `isolates` count, and an array of `antibiotics`.

An antibiotic record includes:
- `drug` – Name of the antimicrobial agent.
- `pctS` – Percent of isolates susceptible.
- `notes` – Free-text comments.
- `cautions` – Warnings or clinical considerations.
- `flags` – Tags that map to badges defined in the legend.

Color bands from the legend classify susceptibility:
- **Green** ≥80%
- **Yellow** 70–79%
- **Red** ≤69%

Legend badges include items such as `urine-mic-only`, `sdd`, and `limited-isolates`.

## User Interface (`index.html`)

1. **Site Selection** – A dropdown (`<select id="site">`) lists available sites from the dataset.
2. **Context Tabs** – After selecting a site, context buttons appear for further filtering.
3. **Organism Search** – A searchable list allows users to filter organisms by name.
4. **Results View** – Selecting an organism shows antibiotic susceptibilities with color-coded chips and optional badges.
5. **Filter ≥80%** – A checkbox filters antibiotics to only those with ≥80% susceptibility.
6. **Navigation** – A back button returns from results to the organism list.
7. **Legend & Disclaimer** – Footer displays the color key, a dynamic hint from the dataset, and a disclaimer (“Use patient-level cultures and ID consult for definitive therapy.”).

## Script Overview

The embedded JavaScript fetches the dataset (`const DATA_URL='nm_antibiogram_full_final.json';`) and initializes the interface. Core functions include:
- `init()` – Sets the hint text and wires event listeners.
- `populateSites()` – Renders the site dropdown.
- `renderContexts(siteId)` & `activateContext(ctxId)` – Manage context selection.
- `renderOrganisms()` & `filterOrganisms()` – Build and filter the organism list.
- `selectOrganism(id)` – Displays organism-specific data.
- `renderAntibiotics()` – Sorts, filters, and renders antibiotic entries, applying color bands and badges.

Accessibility considerations include `prefers-reduced-motion` styling and visually hidden labels for screen readers. The interface uses sticky headers/footers and CSS variables for theming.

