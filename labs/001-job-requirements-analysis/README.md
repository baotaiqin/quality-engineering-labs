# 2027 Graduate QA Job Requirements Analysis

This experiment turns a manually curated set of public 2027 graduate job posts into a small, auditable dataset. It compares job-level frequency with company-level frequency so that companies publishing several specialized roles do not dominate the result.

## Scope

- 18 QA-related positions
- 13 companies or institutions
- Access date: 2026-08-02
- Tracks: software testing, test development, AI software quality, algorithm testing, and model evaluation

This is a purposive sample, not a random survey of the entire recruitment market. The results describe only the selected posts.

## Repository layout

```text
.
├─ data/
│  └─ job_samples.csv
├─ src/
│  ├─ analyze_jobs.py
│  └─ generate_charts.py
├─ tests/
│  └─ test_analyze_jobs.py
├─ outputs/
│  ├─ capability_prevalence.csv
│  ├─ skill_frequency.csv
│  ├─ track_distribution.csv
│  ├─ source_distribution.csv
│  ├─ summary.json
│  └─ charts/
└─ requirements.txt
```

## Method

1. Keep positions that explicitly target 2027 graduates or interns and are directly related to testing or model evaluation.
2. Manually map job descriptions to canonical tokens for programming languages, testing foundations, automation tools, engineering systems, AI quality, and quality activities.
3. Validate required fields and duplicate IDs.
4. Remove exact company/title/URL duplicates.
5. Calculate prevalence by job and by distinct company.
6. Export CSV/JSON results and reproducible PNG charts.

Manual coding is used because job descriptions express similar requirements with different wording. The raw descriptions are not republished; the dataset contains short summaries, canonical tags, source links, and access dates.

## Run

Python 3.10 or newer is recommended.

```bash
python -m pip install -r requirements.txt

python src/analyze_jobs.py \
  --input data/job_samples.csv \
  --output-dir outputs

python src/generate_charts.py \
  --analysis-dir outputs \
  --output-dir outputs/charts
```

On Windows PowerShell, replace the line continuation character as needed or run each command on one line.

## Test

```bash
python -m unittest discover -s tests -v
```

The tests cover token parsing, duplicate handling, company-level weighting, AI capability classification, dataset integration, and chart generation.

## Main observations

| Capability group | Job-level | Company-level |
|---|---:|---:|
| Testing foundations and test design | 94.4% | 92.3% |
| Programming languages | 88.9% | 92.3% |
| Automation and tool development | 88.9% | 92.3% |
| Performance, stability, and diagnosis | 88.9% | 84.6% |
| Computer and system fundamentals | 66.7% | 76.9% |
| AI and model evaluation | 66.7% | 61.5% |
| Engineering and infrastructure | 22.2% | 23.1% |

These numbers represent explicit mentions in this sample. A missing token does not prove that a skill is unimportant, and a mentioned skill is not necessarily a strict screening threshold.

## Limitations

- 12 of 18 posts came from Nowcoder, so platform selection bias is substantial.
- Alibaba and ByteDance published multiple specialized positions; company-level aggregation reduces but does not eliminate that bias.
- Some community or aggregator pages may lag behind the original company page.
- Job descriptions mix required and preferred qualifications.
- The taxonomy is manually coded and can contain judgment errors.
- Closed positions remain useful as requirement snapshots but should not be treated as active application links.

## Related article

CSDN link: pending review and publication.
