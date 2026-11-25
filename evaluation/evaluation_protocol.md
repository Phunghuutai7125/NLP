# Evaluation protocol

## Task

Given a Vietnamese natural-language query, rank economic-news articles in the
fixed UVN-1 business-category corpus. Query set has 10 dev and 40 test queries.
The project owner or a reviewer explicitly authorized by them must review
queries for clarity, answerability, topic coverage, and duplication before
freezing the test split by setting `review_status=locked`
for all 40 test rows in `data/queries.csv`. The evaluator refuses to score an
unlocked test split.

## Systems

- E0: word unigram/bigram TF-IDF cosine retrieval (lexical baseline).
- E1: multilingual sentence-transformer dense retrieval, model
  `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- E2: Reciprocal Rank Fusion (RRF) of E0 and E1, constant 60.

All systems use the same corpus and queries. Exact duplicate title/content
records are excluded from indexing (the preserved corpus snapshot is unchanged).
The retrieval script writes top-10
predictions and pools the top five candidates per query and system. The model
identifier, script version, corpus checksum, query version, and execution date
must be recorded with the final experiment.

## Relevance judgments

Use the 0-3 scale in `data/annotation_guideline.md`. The candidate pool in
`data/relevance_judgments_template.csv` is not gold until people judge it.
Ratings and adjudications are stored in SQLite; reviewed labels are exported
separately to `data/relevance_judgments.csv`. One reviewer may judge the full
pool; the exported rows are marked `single_annotator`, and no inter-annotator
agreement can be claimed. AI-provisional suggestions are not human judgments
and cannot be exported as `single_annotator` without actual human review.
Suggestions were generated from titles and snippets capped at 1,000
characters, not necessarily full article text. With multiple reviewers, resolve disagreements and
record final grades and review notes. Do not equate unjudged candidates with
grade 0. For each of 40 test queries, judge at least five distinct candidates;
preferably judge the entire union pool.
The course guide also requires a second-person audit of at least 20% of
group-created gold labels. For these 411 test labels, the minimum is 83. A
blinded, stratified sample covering all 40 queries is prepared in
`evaluation/second_reviewer_sample.csv` using seed 20261112. A second member
of the group (Tài) completed this independent audit of all 83 items without
viewing Duy's labels or model ranks. Results: 21/83 exact agreement (25.30%),
linear weighted Cohen's Kappa = 0.0778 (unweighted = 0.0311). Most disagreements
differ by only 1 grade (38/83, 45.8%). The full comparison is recorded in
`evaluation/second_reviewer_sample.csv` and `evaluation/second_reviewer_audit.csv`.

## Split discipline

Review and freeze the test queries before choosing a system or changing query
wording based on test results. Develop configurations on dev only. Run test
evaluation once after configuration selection. If test queries or labels need
changes, record the reason, version the protocol, and treat any re-evaluation
as exploratory unless the test is re-locked independently. All 40 test queries
were locked on 2026-11-11 after assistant-assisted review of query wording and
top-three candidate titles at the project owner's request. No query wording
changed during locking.

## Metrics

- nDCG@5 using grades 0-3.
- MRR@5 where grades 2 or 3 count as relevant.

The evaluator requires the entire test candidate pool to be judged before
scoring; dev judgments may remain blank. It also refuses to score if any
system's top five contains an unjudged document. This prevents silently treating
unknown documents as irrelevant. nDCG's ideal ranking is over the judged
candidate pool, not all 1,110 corpus documents. Recall@k is not reported until a
sufficiently complete relevant document set has been established.

## Current status

The test split is locked. AI produced provisional suggestions for 411
test-pool candidates. Duy has now human-reviewed all 411: the two q011 labels
already recorded and the remaining 409 supplied in `duy_judgments.csv`. All
are recorded as `single_annotator`; this supports evaluation but provides no
inter-annotator agreement estimate. Duy's two q011 grades are 2, whereas the
AI proposals were 1; AI is provisional, not a second human reviewer, so this is
not an unresolved human disagreement. The one-time evaluation using Duy's
labels was run on 2026-11-12 and is recorded in `experiments.csv` and
`metrics_summary.csv`:

| System | nDCG@5 | MRR@5 |
|---|---:|---:|
| E0 TF-IDF | 0.792227 | 0.852500 |
| E1 Dense | 0.561189 | 0.700000 |
| E2 RRF fusion | 0.782979 | 0.871667 |

E0 has the highest nDCG@5; E2 has the highest MRR@5. Interpret these as
single-annotator primary metrics on the candidate pool, supported by a 20.2%
second-person audit. The independent human audit by Tài matched Duy on 21/83 labels (25.30%);
62 differ, with 38 differing by 1 grade, 20 by 2 grades, and 4 by 3 grades.
Linear weighted Cohen's Kappa is 0.0778 (unweighted Kappa = 0.0311).
Per-item raw comparisons are documented in `second_reviewer_audit.csv`.
The 20% second-person audit requirement of the course syllabus is fulfilled.
If labels change, document the changes; any test re-evaluation is exploratory
unless the test is independently re-locked.
AI-based metric values remain exploratory and are preserved in
`ai_provisional_metrics.csv`; do not report them as gold evaluation results.
