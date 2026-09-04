# 09. 데이터 카드 — FOMC 코퍼스 v3 (층위 인식)

> 생성: `experiments/10_build_corpus_v3.py` → `11_extract_modals_v3.py` → `12_qa_integrity.py` (2026-09-04). 검증 결과 전문은 `results/qa/QA_report.md`.
> v2와의 차이: 정제 강화(각주·내비게이션·참고문헌·제목 블록 제거), 기자회견 화자 분절, 의사록 섹션 귀속, 인용 성명서·지침 분리, 층위별 분모 저장.

## 1. 출처와 범위
- 출처: 연준 이사회 웹사이트(`FOMC_corpus/_meta/collect_fomc_docs.py`), 2010-01 ~ 2026-04. 4장르: 회의 후 성명서(statements), 의사록(minutes), 의장 기자회견 녹취(transcripts), 의장 연설(speeches).
- 분석 창: **T1 2014-01-01 ~ 2026-04-29**(기본), T2 = T1에서 2020년 제외, T3 = 2010–2026 확장(강건성).
- 제외 문서(`EXCLUDE_DOCS`): 성명서로 분류됐지만 회의 후 성명서가 아닌 4건(2019-10-11 실행 성명, 2020-03-31 FIMA 레포, 2020-08-27·2025-08-22 프레임워크 성명).
- 회의 정합: 성명서 133건(2010–) 중 의사록 없는 날짜 2건(2020-03-03, 2020-03-23 긴급회의: 의사록은 정례 회의록에 통합), 의사록만 있는 날짜 1건(2012-10-23: 성명서는 10-24자, 하루 차이).

## 2. 층위(layer) 정의 — 장르 × 귀속

| 층위 | 정의 | 분석 포함 | 6대 조동사 토큰(T1) |
|---|---|---|---|
| `statement` | 성명서 본문 | 기본 | 788 |
| `statement_vote` | "Voting for/against …" 문단 | 제외 | 10 |
| `min_staff_desk` | 의사록 "Developments/Discussion in Financial Markets and Open Market Operations"(데스크·SOMA 보고) | S3·S4 | 553 |
| `min_staff` | "Staff Review of the Economic/Financial Situation", "Staff Economic Outlook" | S3·S4 | 539 |
| `min_participants` | "Participants' Views on Current Conditions and the Economic Outlook" | S3·S4 | 2,756 |
| `min_committee` | "Committee Policy Action(s)" 중 위원회 심의 서술(인용문·삽입 문서 제외) | S2·S3·S4 | 958 |
| `min_statement_quote` | 위원회 섹션 안에 그대로 인용된 성명서 전문 | 제외(성명서와 중복) | 761 |
| `min_directive_quote` | 인용된 데스크 지침(directive) 및 삽입된 채택 문서(예: 2022-05 Plans for Reducing…) | 제외 | 102 |
| `min_vote` | 표결·표결 후 행정 서술(이사회 IOER 표결, 다음 회의 일정) | 제외 | 166 |
| `min_special` | 특별 주제 섹션(Discussion of…, Review of Monetary Policy Strategy…, Long-Run Framework…, Balance Sheet…) | S3·S4 | 783 |
| `min_boilerplate` | 1월 회의 조직 사항·인가문(Authorization…)·외환 지침·장기목표 성명 전문·Notation Vote | 제외 | 376 |
| `min_front_matter` | 참석자 명단 등 첫 섹션 이전 | 제외 | 78 |
| `min_sep` | SEP 부록(있는 경우) | 제외 | — |
| `pc_chair` | 기자회견 의장 발화(모두, 모두발언 + 답변) | S4 | 10,686 |
| `pc_journalist` | 기자 질문 | 제외 | 2,452 |
| `pc_moderator` | 진행자(Michelle Smith) | 제외 | 83 |
| `pc_pre` | 첫 화자 마커 이전(제목 잔재) | 제외 | 0 |
| `speech_chair` | 의장 연설 본문(제목 블록·참고문헌·각주 제거) | S4 | 3,203 |

층위별 토큰 수(T1): pc_chair 533k, min_staff 250k, speech_chair 235k, min_participants 224k, pc_journalist 138k, min_staff_desk 71k, min_boilerplate 66k, min_committee 63k, min_front_matter 60k, statement 44k, min_special 41k, min_statement_quote 41k, min_directive_quote 22k, min_vote 17k.

## 3. 정제 규칙 (v3)
1. 인코딩: `ftfy.fix_text` (mojibake 복구). 잔재 3문장(0.003%).
2. 헤더·푸터: 발표 시각, 페이지 마커("Page x of y", "FINAL"), 회의 날짜 줄, 기자회견 제목 줄, "Last update", 각주 참조 숫자만 있는 줄.
3. 각주: 번호 문단 + "Return to text" 백링크 블록 제거(의사록·연설). 잔재 1문장.
4. 사이트 내비게이션(2010–2011 HTML 스크랩): "Home/Search/Print/Return to top/Accessibility/FOIA…" 줄 제거. 의사록은 "A (joint) meeting of the Federal Open Market Committee"에서 시작하고 "Return to top"/서명선에서 끝나도록 절단.
5. 연설: "References" 이후 절단(본문 40% 이후에 나타날 때), 문장부호로 끝나지 않는 선두 문단(제목·연사·장소·"Share/Watch Live") 제거.
6. 기자회견: 줄바꿈이 문장 중간에 있으므로 턴 내부 줄을 공백으로 연결. 화자 마커 = 줄 머리의 대문자 이름 + 마침표/콜론(대문자 비율 ≥ 70%, ≤ 5단어; "McGRANE", "HONORÉ" 허용). 역할: `CHAIR*`/`VICE CHAIR*` → chair, Michelle/Michele Smith → moderator, 나머지 → journalist. 168명 식별, 마커 이전 텍스트 60토큰 초과 문서 0건.
7. 의사록 섹션: 소제목 카탈로그(정규식)로 층위 전환. 위원회 섹션 안에서 문단 첫 글자가 따옴표이면 인용 블록 시작, 문단 끝이 따옴표이면 종료; 직전 문단에 "statement"가 있으면 성명서 인용, 아니면 지침 인용. 전부 대문자 제목의 삽입 문서는 지침 인용으로 처리. "Voting for/against"는 어떤 상태에서도 vote 층으로 강제 전환(인용 블록 안전장치).
8. 문장 분할: spaCy `en_core_web_sm`, 문단 단위로 처리, 3단어 미만 문장 제거. 문장별 토큰 수(`n_tok`, 공백·구두점 제외)를 저장하여 층위별 분모로 사용.

## 4. 조동사 추출 (v3 = v2 규칙 동일)
- Penn `MD` 태그 + 축약형('ll/'d; 'd는 다음 토큰이 원형동사일 때만 would). 6대 조동사 will/would/could/can/should/may(+ might/must/shall/ought 보조).
- 어휘 head 동사(조동사 사슬 건너뜀), 코퓰러 be 보어 해소(`be+appropriate` 등), 부정·수동·완료·진행, 주어 유형, 조건절 표지, 보고 동사 내포, 의문문 플래그.
- 결과: 32,388 토큰(2010–2026, 전 층위). T1 분석 층위 6대 조동사: statement 788, minutes(substantive) 5,589, pc_chair 10,686, speech 3,203.
- 정확도: v2에서 저자 60문장 표본 head 93%·의미유형 90%. **2인 코딩 200문장(`results/tables/D7_validation_sample.csv`) 미완** — 투고 전 필수.

## 5. 정규화 기준 (docs/08 §3.2, 10.5)
| 지표 | 정의 | 용도 |
|---|---|---|
| N1 밀도 | 층위 토큰 1,000개당 6대 조동사(또는 단위) 수 | 층위 비교, 거시 상관(기본) |
| N2 점유율 | 문서-층위 안의 6대 조동사 토큰 중 단위의 비율 | 구성 변화, 성명서 계단(X-B) |
| N3 문서당 수 | 문서-층위의 원시 수 | 성명서 전용(문서 길이 자체가 편집 결과) |
분모는 `corpus_docs_v3.csv`(문서 × 층위 × 토큰 수)에 저장. 모든 표·그림 캡션에 지표명을 표기한다.

## 6. v2 대비 변화(2014–2026)
| 장르 | v2 토큰 | v3 분석 층위 토큰 | 유지율 | v2 6대 조동사 | v3 분석 층위 |
|---|---:|---:|---:|---:|---:|
| minutes | 871,758 | 649,429 | 0.745 | 7,081 | 5,589 |
| press_conf | 697,340 | 533,106 | 0.764 | 13,221 | 10,686 |
| speech | 313,299 | 234,853 | 0.750 | 3,507 | 3,203 |
| statement | 49,210 | 43,763 | 0.889 | 798 | 788 |
- 의사록에서 빠진 조동사 1,492개 = 인용 성명서 761 + 규정문 376 + 표결·행정 166 + 지침 102 + 명단 78 + (특별 섹션 783은 유지).
- 기자회견에서 빠진 2,535개 = 기자 2,452 + 진행자 83. v2의 press_conf could 48%, might 50%가 기자 발화였음.
- 연설에서 빠진 304개 = 각주·참고문헌·제목.

## 7. 검증
- 인용 성명서 vs 성명서 문서(같은 회의) 문장집합 Jaccard: 131회의 중앙값 **0.94**, 0.5 미만 0건 → 인용 분리와 성명서 코퍼스가 서로를 검증.
- 중복 문서 0, 날짜 파싱 오류 0. 토큰 이상치는 대부분 1월 회의(규정문 큼)·긴급회의(짧음)로 설명됨.
- 사람 검증 표본: `results/qa/sample_speaker_roles.csv`(10문서 × 20턴), `results/qa/sample_minutes_layers.csv`(10문서 × 층위별 2문장) — `human_ok` 열 채우기.

## 8. 알려진 한계
- `minutes_20121023`(T3 전용)는 PDF 유래 텍스트로 소제목이 문단 경계가 아니어서 전부 front_matter로 분류됨(분석에서 사실상 제외). T1·T2 무관.
- `minutes_20220126`의 데스크 섹션 제목 변형("Financial Developments and Open Market Operations")은 코드에 반영됨.
- 화자 분절은 마커 형식에 의존; Bernanke 초기 기자회견의 "CHAIRMAN BERNANKE." 형식 포함 확인. 2018-09-26의 콜론 형식 처리.
- 의사록 `min_special`은 스태프·참가자 발언이 섞인 층이므로 귀속 해석에 주의(참가자 층과 분리 보고).
- 거시 정렬 표(`macro_by_doc.csv`)는 v2에서 생성(FRED 최종치, vintage 아님) — docs/10 §2.3.
