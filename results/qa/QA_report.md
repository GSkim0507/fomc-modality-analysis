# QA report — corpus v3


## 1. Inventory (documents by genre × year, all layers pooled)

| year | minutes | press_conf | speech | statement |
|---|---|---|---|---|
| 2010 | 8 | 0 | 0 | 8 |
| 2011 | 8 | 3 | 19 | 8 |
| 2012 | 9 | 5 | 15 | 8 |
| 2013 | 8 | 4 | 16 | 8 |
| 2014 | 8 | 4 | 15 | 8 |
| 2015 | 8 | 4 | 11 | 8 |
| 2016 | 8 | 4 | 6 | 8 |
| 2017 | 8 | 4 | 13 | 8 |
| 2018 | 8 | 4 | 11 | 8 |
| 2019 | 8 | 8 | 17 | 9 |
| 2020 | 8 | 9 | 6 | 12 |
| 2021 | 8 | 8 | 9 | 8 |
| 2022 | 8 | 8 | 6 | 8 |
| 2023 | 8 | 8 | 9 | 8 |
| 2024 | 8 | 8 | 6 | 8 |
| 2025 | 8 | 8 | 12 | 9 |
| 2026 | 3 | 3 | 3 | 3 |

- statements (post-meeting, after EXCLUDE_DOCS): 133; minutes: 132; meeting dates in _meta: 138
- statement dates without minutes (2): 2020-03-03, 2020-03-23
- minutes dates without statement (1): 2012-10-23
- (expected: unscheduled/emergency meetings such as 2020-03-03 and 2020-03-15 issue statements whose minutes are combined; minutes dated by the last meeting day may differ by one day from the statement date)

## 2. Duplicates and dates

- identical-text document groups: 0 []
- duplicate doc_ids in corpus_docs_v3: 0
- unparseable dates: 0

## 3. Token outliers per genre × layer (|z| > 3)

| doc_type | layer | doc_id | n_tokens | z |
|---|---|---|---|---|
| minutes | min_boilerplate | minutes_20140129 | 4630 | 3.17 |
| minutes | min_boilerplate | minutes_20150128 | 4597 | 3.15 |
| minutes | min_boilerplate | minutes_20160127 | 5037 | 3.49 |
| minutes | min_boilerplate | minutes_20170201 | 4419 | 3.01 |
| minutes | min_boilerplate | minutes_20220126 | 4850 | 3.35 |
| minutes | min_directive_quote | minutes_20220504 | 589 | 6.29 |
| minutes | min_front_matter | minutes_20121023 | 6903 | 10.17 |
| minutes | min_special | minutes_20191030 | 2802 | 3.29 |
| minutes | min_staff_desk | minutes_20100127 | 1930 | 3.32 |
| minutes | min_staff_desk | minutes_20150318 | 1838 | 3.08 |
| minutes | min_vote | minutes_20100623 | 826 | 3.61 |
| minutes | min_vote | minutes_20111213 | 1758 | 8.99 |
| press_conf | pc_chair | transcript_20200303 | 1692 | -4.59 |
| press_conf | pc_journalist | transcript_20200303 | 609 | -3.88 |
| press_conf | pc_moderator | transcript_20220316 | 240 | 3.78 |
| press_conf | pc_pre | transcript_20200315 | 14 | 3.16 |
| statement | statement_vote | statement_20140917 | 149 | 3.44 |
| statement | statement_vote | statement_20141217 | 173 | 4.37 |

## 4. Residue in sentences

- encoding (â/Ã/�/Â): 3 sentences — e.g. 'Later in the period, AFE yields partially rebounded and foreign equity prices fully recovered on some easing of U.S.\xadâ€"'
- Return to text: 1 sentences — e.g. 'Return to text.'
- Watch Live / Share: 0 sentences
- page header: 0 sentences
- URL: 3 sentences — e.g. 'A report summarizing all of those events is available here: https://www.federalreserve.gov/publications/files/fedlistens'
- footnote digit glued: 7 sentences — e.g. 'We could pick them up somewhat if the economy is stronger.1 In terms of MBS versus Treasuries, we discussed that issue.'

## 5. Layer coverage

- minutes missing `min_staff_desk`: 1 ['minutes_20121023']
- minutes missing `min_staff`: 1 ['minutes_20121023']
- minutes missing `min_participants`: 1 ['minutes_20121023']
- minutes missing `min_committee`: 1 ['minutes_20121023']
- minutes missing `min_statement_quote`: 1 ['minutes_20121023']
- minutes missing `min_directive_quote`: 1 ['minutes_20121023']
- minutes missing `min_vote`: 1 ['minutes_20121023']
- unknown heading candidates in minutes (not used to switch layers; review): [('Bank of Canada', 34), ('Bank of England', 20), ('Bank of Japan', 20), ('Bank of Mexico', 15), ('Mark E. Van Der Weide', 9), ('Foreign bank', 8), ('Amount of arrangement', 8), ('Australian dollars', 7), ('Brazilian reais', 7), ('Canadian dollars', 7), ('Danish kroner', 7), ('Japanese yen', 7), ('Korean won', 7), ('Mexican pesos', 7), ('New Zealand dollars', 7), ('Norwegian kroner', 7), ('Pounds sterling', 7), ('Singapore dollars', 7), ('Swedish kronor', 7), ('Swiss francs', 7)]
- press conferences: 92; journalist token share mean 0.207 (min 0.134, max 0.278); docs with pc_pre > 60 tokens: 0
- distinct journalist/other speaker names: 168; sample: ['ADAM SHAPIRO', 'AKIHIRO OKADA', 'AKIO FUJII', 'ALISTER BULL', 'AMARA OMEOKWE', 'ANA SWANSON', 'ANDREW ACKERMAN', 'ANN SAPHIR', 'ANNALYN KURTZ', 'ANNEKEN TAPPE', 'ARCHIE HALL', 'BEIYI SEOW', 'BEN WEYL', 'BINYAMIN APPELBAUM', 'BINYAMIN APPLEBAUM']

## 6. Quoted statement in minutes vs statement document (sentence-set Jaccard, same meeting)

- meetings compared: 131; median Jaccard 0.94; < 0.5: 0
| minutes_date | statement_date | jaccard | n_quote | n_stmt |
|---|---|---|---|---|
| 2019-09-18 | 2019-09-18 | 0.692 | 11 | 11 |
| 2019-12-11 | 2019-12-11 | 0.692 | 11 | 11 |
| 2010-04-28 | 2010-04-28 | 0.769 | 11 | 12 |
| 2026-04-29 | 2026-04-29 | 0.786 | 12 | 13 |
| 2026-01-28 | 2026-01-28 | 0.786 | 12 | 13 |
| 2025-09-17 | 2025-09-17 | 0.8 | 13 | 14 |
| 2026-03-18 | 2026-03-18 | 0.8 | 13 | 14 |
| 2025-12-10 | 2025-12-10 | 0.812 | 14 | 15 |

## 7. v2 vs v3

| doc_type | v2_tokens | v3_tokens_all_layers | v3_tokens_analysis_layers | retained_share |
|---|---|---|---|---|
| minutes | 871758 | 853960 | 649429 | 0.745 |
| press_conf | 697340 | 673478 | 533106 | 0.764 |
| speech | 313299 | 234853 | 234853 | 0.75 |
| statement | 49210 | 49204 | 43763 | 0.889 |

| doc_type | v2_six_modal | v3_all_layers | v3_analysis_layers |
|---|---|---|---|
| minutes | 7081 | 7072 | 5589 |
| press_conf | 13221 | 13221 | 10686 |
| speech | 3507 | 3203 | 3203 |
| statement | 798 | 798 | 788 |

six-modal tokens by layer (v3, 2014–2026):
| layer | n | label |
|---|---|---|
| min_boilerplate | 376 | Minutes: authorizations/boilerplate |
| min_committee | 958 | Minutes: Committee policy action |
| min_directive_quote | 102 | Minutes: quoted directive |
| min_front_matter | 78 | Minutes: front matter |
| min_participants | 2756 | Minutes: participants' views |
| min_special | 783 | Minutes: special topics |
| min_staff | 539 | Minutes: staff review & outlook |
| min_staff_desk | 553 | Minutes: Desk/markets (staff) |
| min_statement_quote | 761 | Minutes: quoted statement |
| min_vote | 166 | Minutes: vote & post-vote |
| pc_chair | 10686 | Press conf.: Chair |
| pc_journalist | 2452 | Press conf.: journalists |
| pc_moderator | 83 | Press conf.: moderator |
| speech_chair | 3203 | Chair speech |
| statement | 788 | Statement |
| statement_vote | 10 | Statement (vote line) |

## 8. Human-validation samples

- `results/qa/sample_speaker_roles.csv` (10 docs × 20 turns) and `results/qa/sample_minutes_layers.csv` (10 docs × 2 sentences per layer) — fill `human_ok` (1/0).