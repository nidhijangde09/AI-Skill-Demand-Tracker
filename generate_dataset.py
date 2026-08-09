"""
generate_dataset.py
--------------------
Generates a synthetic (but realistic-looking) raw job postings dataset
for the "AI Skill Demand Tracker" project.

The dataset is deliberately made "dirty" (duplicate rows, missing values,
inconsistent casing) so that the cleaning step in clean_and_extract.py
has real work to do.

Output: raw_jobs.csv
"""

import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

# ---------------------------------------------------------------------
# Reference lists used to build synthetic job postings
# ---------------------------------------------------------------------

JOB_TITLES = [
    "Data Analyst", "Data Scientist", "Machine Learning Engineer",
    "AI Engineer", "Business Intelligence Analyst", "Data Engineer",
    "BI Developer", "Analytics Consultant", "NLP Engineer",
    "Data Science Manager", "Power BI Developer", "AI Research Engineer",
]

LOCATIONS = [
    "Mumbai", "Bengaluru", "Pune", "Hyderabad", "Delhi NCR",
    "Chennai", "Remote", "New York", "London", "Singapore",
]

EXPERIENCE_LEVELS = ["Entry", "Mid", "Senior", "Lead"]

COMPANIES = [
    "Alpha Analytics", "Nimbus Data", "Quantify Labs", "BrightPath AI",
    "Vertex Insights", "Northstar Tech", "Clarity Systems", "DataForge",
    "Skyline Solutions", "BluePeak Consulting",
]

# Skill "phrases" as they might actually appear in a job description,
# mapped to the canonical skill name used later in extraction.
SKILL_PHRASES = {
    "Python": ["Python", "python programming", "proficiency in Python"],
    "SQL": ["SQL", "advanced SQL", "SQL queries", "T-SQL"],
    "Power BI": ["Power BI", "PowerBI", "Power BI dashboards"],
    "Excel": ["Excel", "Advanced Excel", "MS Excel"],
    "Machine Learning": ["Machine Learning", "ML models", "machine-learning"],
    "Deep Learning": ["Deep Learning", "deep neural networks"],
    "NLP": ["NLP", "Natural Language Processing"],
    "Tableau": ["Tableau", "Tableau dashboards"],
    "AWS": ["AWS", "Amazon Web Services"],
    "Generative AI": ["Generative AI", "GenAI", "LLMs", "Large Language Models"],
}

DESC_TEMPLATES = [
    "We are looking for a {title} to join our team in {location}. "
    "The ideal candidate has hands-on experience with {skills}. "
    "You will work closely with cross-functional teams to deliver insights.",

    "{company} is hiring a {title} ({experience} level) based in {location}. "
    "Required skills: {skills}. Prior experience with analytics platforms is a plus.",

    "Join {company} as a {title}! We need someone comfortable with {skills} "
    "to help us build data-driven products.",

    "Exciting opportunity for a {title} at {company}, {location}. "
    "Must have strong knowledge of {skills} and a passion for solving business problems.",

    "{title} role open at {company}. Key requirements include {skills}. "
    "This is a {experience} level position, {location} based.",
]


def make_description(title, company, location, experience, skills_for_row):
    phrase_list = [random.choice(SKILL_PHRASES[s]) for s in skills_for_row]
    skills_text = ", ".join(phrase_list)
    template = random.choice(DESC_TEMPLATES)
    return template.format(
        title=title, company=company, location=location,
        experience=experience, skills=skills_text,
    )


def build_dataset(n_rows=1000):
    rows = []
    skill_names = list(SKILL_PHRASES.keys())

    for job_id in range(1, n_rows + 1):
        title = random.choice(JOB_TITLES)
        company = random.choice(COMPANIES)
        location = random.choice(LOCATIONS)
        experience = random.choice(EXPERIENCE_LEVELS)

        # Each job requires a random subset of 2-6 skills, weighted so that
        # Python / SQL / Power BI / Excel / ML show up more often (realistic).
        weights = np.array([0.9, 0.85, 0.6, 0.55, 0.7, 0.35, 0.4, 0.3, 0.45, 0.4])
        weights = weights / weights.sum()
        k = random.randint(2, 6)
        skills_for_row = list(np.random.choice(
            skill_names, size=k, replace=False, p=weights
        ))

        description = make_description(title, company, location, experience, skills_for_row)

        rows.append({
            "job_id": job_id,
            "job_title": title,
            "company": company,
            "location": location,
            "experience_level": experience,
            "job_description": description,
            "date_posted": pd.Timestamp("2026-01-01") + pd.Timedelta(days=random.randint(0, 200)),
        })

    df = pd.DataFrame(rows)

    # ---- Intentionally dirty the data --------------------------------
    # 1) Duplicate ~4% of rows (some exact, some with job_id changed but
    #    identical content, to mimic re-posted listings)
    dup_idx = np.random.choice(df.index, size=int(0.04 * n_rows), replace=False)
    dup_rows = df.loc[dup_idx].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    # 2) Introduce missing values in a few columns
    for col, frac in [("location", 0.03), ("experience_level", 0.02), ("company", 0.02)]:
        miss_idx = np.random.choice(df.index, size=int(frac * len(df)), replace=False)
        df.loc[miss_idx, col] = np.nan

    # 3) Inconsistent casing / whitespace on location & experience level
    def messy_case(x):
        if pd.isna(x):
            return x
        r = random.random()
        if r < 0.15:
            return x.upper()
        if r < 0.3:
            return x.lower()
        if r < 0.35:
            return f"  {x}  "
        return x

    df["location"] = df["location"].apply(messy_case)
    df["experience_level"] = df["experience_level"].apply(messy_case)

    # 4) Shuffle rows so duplicates aren't neatly at the bottom
    df = df.sample(frac=1, random_state=7).reset_index(drop=True)

    return df


if __name__ == "__main__":
    df = build_dataset(5000)
    df.to_csv("raw_jobs.csv", index=False)
    print(f"raw_jobs.csv written with {len(df)} rows (includes intentional dupes/missing values)")
