# AI Skill Demand Tracker

Python → SQL → Power BI project that tracks which skills (Python, SQL,
Power BI, Machine Learning, etc.) show up most often in job postings.

## Pipeline

```
raw_jobs.csv (synthetic job postings)
        │
        ▼
clean_and_extract.py   (Python / pandas)
   - drops duplicate postings
   - fills/handles missing values
   - extracts skills from job_description via keyword matching
        │
        ▼
cleaned_jobs.csv  +  job_skills.csv
        │
        ▼
analysis.sql   (run against the two CSVs above)
   - most demanded skills
   - skills by job title / location / experience level
   - AI vs Data-Analytics grouping
   - KPI values
        │
        ▼
Power BI dashboard (.pbix — build locally, see steps below)
```

## Files in this project

| File | Purpose |
|---|---|
| `generate_dataset.py` | Creates the synthetic raw dataset (`raw_jobs.csv`). Only needed if you want to regenerate/expand the sample data — swap this out for a real scraped/Kaggle job dataset if you have one. |
| `raw_jobs.csv` | Raw job postings (5,200 rows, with intentional duplicates & missing values). |
| `clean_and_extract.py` | **Main Python deliverable.** Cleans the data and extracts skills. |
| `cleaned_jobs.csv` | One row per job posting, with a `skills` column. |
| `job_skills.csv` | Long/normalized format: one row per (job_id, skill). This is what SQL and Power BI mostly query. |
| `analysis.sql` | **Main SQL deliverable.** Table setup + all the analysis queries. |

## Why I couldn't generate the `.pbix` file directly

Power BI Desktop files are a proprietary binary format tied to Microsoft's
desktop application — there's no way to author one outside Power BI Desktop
itself. What I've built instead is everything Power BI needs as input
(the cleaned CSVs + the SQL queries), plus exact build steps below so you
can put the dashboard together yourself in a few minutes.

## Building the Power BI dashboard

1. **Get Data → Text/CSV** → import `job_skills.csv` and `cleaned_jobs.csv`.
   (Alternatively: load them into a real database and use **Get Data → SQL
   Server/Postgres/MySQL**, then paste queries from `analysis.sql` as
   native queries.)
2. Create a **measure** for job count:
   `Job Count = DISTINCTCOUNT(job_skills[job_id])`
3. Build the visuals:
   - **Top In-Demand Skills** — horizontal bar chart. Axis = `skill`,
     Value = `Job Count`, sorted descending. This is your main visual,
     styled like the reference image.
   - **Skills by Job Title** — clustered bar chart. Axis = `job_title`,
     Legend = `skill`, Value = `Job Count`.
   - **AI vs Data Analytics Skills** — donut chart using the category
     query from `analysis.sql` (query 5). Add a calculated column in
     Power Query or DAX to bucket each skill.
   - **Skills by Experience** — bar chart. Axis = `experience_level`,
     Legend = `skill`.
   - **Top Skills by Location** — bar chart (Axis = `location`) or a
     filled map if you want geography (Location field → Map visual).
   - **KPI cards** — four Card visuals:
     `Total Jobs` = `DISTINCTCOUNT(job_skills[job_id])`
     `Total Skills` = `DISTINCTCOUNT(job_skills[skill])`
     `Top Skill` = skill with max Job Count (use a measure with
     `TOPN`/`CALCULATE` or just read it off the bar chart)
     `Top AI Skill` = same, filtered to the AI/ML bucket
4. Add a **slicer** for `experience_level` and `location` so the whole
   dashboard is filterable — this is what turns a static chart set into
   a "tracker."

## Color scheme — Charcoal & Teal

Apply this theme in Power BI via **View → Themes → Browse for themes**,
using a custom theme JSON, or by manually setting each visual's fill/
font colors to match:

| Role | Hex |
|---|---|
| Page background | `#12141c` |
| Card / visual background | `#1c2029` |
| Primary accent (main bars, KPI highlight) | `#2dd4bf` |
| Secondary accent (second series, hover state) | `#0e9488` |
| Text | `#f1f5f4` |
| Muted text / gridlines | `#8b95a1` |

Custom theme JSON you can import directly (**View → Themes → Browse for
themes**):

```json
{
  "name": "Charcoal & Teal",
  "dataColors": ["#2dd4bf", "#0e9488", "#f1f5f4", "#8b95a1", "#1c2029"],
  "background": "#12141c",
  "foreground": "#f1f5f4",
  "tableAccent": "#2dd4bf",
  "visualStyles": {
    "*": {
      "*": {
        "background": [{ "color": { "solid": { "color": "#1c2029" } } }],
        "outspacePane": [{ "backgroundColor": { "solid": { "color": "#12141c" } } }]
      }
    }
  }
}
```

Save that as `charcoal_teal_theme.json` and import it; then set each
card/visual background to `#1c2029` if the theme doesn't apply it
everywhere automatically.

## Putting it on GitHub

Yes — add all of it. A repo like this is exactly what makes a good
portfolio project, and recruiters specifically like seeing the full
pipeline rather than just a dashboard screenshot. A reasonable structure:

```
ai-skill-demand-tracker/
├── README.md
├── data/
│   ├── raw_jobs.csv
│   ├── cleaned_jobs.csv
│   └── job_skills.csv
├── python/
│   ├── generate_dataset.py
│   └── clean_and_extract.py
├── sql/
│   └── analysis.sql
├── powerbi/
│   ├── ai_skill_demand_tracker.pbix
│   └── charcoal_teal_theme.json
└── screenshots/
    └── dashboard.png
```

A few practical notes:
- `.pbix` files are binary — GitHub handles them fine as a normal
  committed file, just don't expect a diff view.
- Add a dashboard screenshot to the README (GitHub renders images
  inline) so people don't have to open Power BI to see the result.
- If any dataset ever contains real/scraped job postings with personal
  data, don't publish it — the synthetic dataset here is safe to publish
  as-is.
