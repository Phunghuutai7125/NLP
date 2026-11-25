# Query draft review notes

This is a pre-lock review of query answerability, not an evaluation result.
Query wording was inspected with the initial top-ranked candidate lists while
the test split was still an unlocked draft. Fifteen questions were narrowed
before the current `draft-v2-prelock` run; the reasons are recorded in
`data/query_revision_log.csv`.

The current candidate lists give a plausible, on-topic first result from at
least one of E0/E1/E2 for the revised questions. This only shows that the
questions have candidate material worth judging. It does not certify relevance,
query quality, or system performance. For example, q021's E2 top result is not
an obvious answer, although E0/E1 return articles about banks selling bad debts.
All candidates still require human relevance judgments.

The query wording was reviewed against the top-three candidate titles from each
method. On 2026-11-11, at the project owner's request, the assistant completed
this title-level review and all 40 test rows were locked without wording
changes. This check does not certify relevance or replace human relevance
judgments. Do not revise test queries based on metric outcomes. If the test
wording changes after labels exist, the evaluator will reject stale labels.

AI generated provisional grades for all 411 test candidates from titles and
snippets capped at 1,000 characters. Duy has now human-reviewed all 411: two
q011 candidates previously recorded and the remaining 409 in
`duy_judgments.csv`. Duy's two q011 grades are 2 and the AI proposals were 1;
this is not a human-human disagreement because AI grades are provisional only.
All test labels are recorded as `single_annotator`, so inter-annotator
agreement cannot be measured. The one-time test evaluation is recorded in
`metrics_summary.csv` and `experiments.csv`; AI metric values remain
exploratory in `ai_provisional_metrics.csv`.
