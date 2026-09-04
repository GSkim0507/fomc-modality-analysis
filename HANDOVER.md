# HANDOVER — 인수인계서

> 이 문서는 작업 진행 과정·결정 사항·환경 정보를 추적하기 위한 인수인계 기록이다.
> 작업 목록은 `TASKS.md`, 단계별 산출물은 `docs/`, `experiments/`, `results/`, `paper/` 참조.

## 1. 프로젝트 개요
- 목적: FOMC 코퍼스(2010–2026, 4장르 535문서, ~2.4M 단어)를 이용한 조동사(modal verb) 언어학 실험 → 학술논문화
- 세미나(지도교수) 결정 사항 — 분석 기간 **2014–2026**, 집중 실험:
  1. 조동사 **후행 동사** 전수 분석(조동사 뒤 결합 동사·의미 패턴)
  2. **6대 조동사별 추이** 세부 분석(빈도 추이·반감기 등 시계열 특성; 2018년 이후 should 소멸, will 감소, could/would 증가, can 저빈도의 원인; 각 조동사의 사용 상황)
  3. 관련하여 가능한 모든 언어학적 분석
- 핵심 참고문헌:
  1. Kawamura, Kobashi, Shizume & Ueda (2019). Strategic central bank communication: Discourse analysis of the Bank of Japan's Monthly Report. *JEDC* 100, 230–250.
  2. Resche, C. (2015). Hedging in the discourse of central banks. *Studies in Communication Sciences* 15(1), 83–92.
- 기존 보고서: 「미 연준의 양태 표현은 점도표와 정합하는가? — FOMC 텍스트 양태 분석 2010–2026」(NLP 개론 기말발표, 성균관대 언어AI대학원)

## 2. 환경
- 작업 루트: `/Users/ks.kim/Documents/airlab/fin_fomc_anal` (git root)
- Python: `.venv` (Python 3.9, spaCy 3.7 + en_core_web_sm). 실행: `.venv/bin/python experiments/<script>.py`
- 시스템 python3(3.9)에는 spaCy 없음. Homebrew python3.14는 spaCy 미지원 → 3.9 venv 사용.
- PDF 텍스트 추출: `pdftotext`(poppler) / `pypdf`
- **저장소(2026-09-04 확정): https://github.com/GSkim0507/fomc-modality-analysis (private).** 기존 airlab-tsw 레포는 사용자가 삭제. 첫 시도는 GSkim0507의 fine-grained PAT에 레포 생성 권한이 없어 실패했고, 사용자가 제공한 classic PAT를 `gh auth login --with-token`으로 gh 키체인에만 저장(파일·문서에 기록하지 않음)한 뒤 생성·푸시 완료. 이후 Phase 경계마다 커밋·푸시 재개.

## 3. 데이터 메모
- `FOMC_corpus/{statements,minutes,transcripts,speeches}/*.json` — 필드: doc_id, doc_type, date, chair, text, word_count 등
- 텍스트에 mojibake 존재(예: `â\x80\x93` = en-dash). 전처리 시 `text.encode('latin-1').decode('utf-8')` 복구 필요(실패 시 원문 유지).
- 기존 분석 산출물: `FOMC_corpus/analysis/` — `modal_instances.csv`(33,164 modal 토큰, spaCy MD 태그 기반), `pos_summary.csv`, `modality_index.csv`(MSI), `paper_b_stats.txt`(장르 ANOVA) 등
- 예비 검증(기존 modal_instances.csv, Statement 장르 조동사 점유율 %):
  - should: 2014 15.7 → 2016 11.1 → 2017 4.0 → **2018 이후 0** (2020 2.4 예외)
  - will: 2018 100 → 2021 72.5 → 2026 60.0 (지속 감소)
  - would/could: 2020까지 ~0 → 2021부터 각 12–20%
  - can: 전 기간 0–4.7% (항상 저빈도)
  → 세미나 관찰은 **Statement 장르** 패턴과 정확히 일치. 6대 조동사 = will, would, could, can, should, may (might/must/shall은 Statement에 거의 없음)

## 4. 진행 로그 (최신이 아래)
| 일시 | Phase | 내용 | 산출물/커밋 |
|---|---|---|---|
| 2026-08-28 | 0 | 코퍼스·기존 분석·보고서·참고문헌 파악, venv 구축, 문서 골격 작성, GitHub 레포 생성 | 843537b |
| 2026-08-28 | 1–3 | 기존 보고서 분석(docs/01), 세미나 초점·예비 검증·원인 진단(docs/02), 선행연구 분석·차별점(docs/03). 핵심 발견: Statement 조동사 추이는 정형 문장 편집 이벤트(should: 재투자 문장 2014-10~2017-05; would/could: 'would be prepared…could impede' 2020-09~전량)로 설명됨. Phase 5 OA 문헌 수집 에이전트 백그라운드 실행 중 | docs/01–03 커밋 |
| 2026-08-28 | 6–7 | 문장 코퍼스 재구축(ftfy 인코딩 보정), 의존구문 기반 조동사 추출(32,584 토큰), 실험 A(후행 동사·collostruction), B(MK 추세·PELT 변화점·AR(1) 반감기·준양태), C(정형 문장·편집 이벤트·KM 생존·보유율 반감기), D(맥락·장르 χ²·의미 유형·의장·국면). 비회의 성명서 4건 제외. 종합 분석 docs/06 작성 | 62ebf7d, docs/06 |
| 2026-08-28 | 8 | 논문 초안 v1 작성(영문, paper/draft_v1.md + .docx; 약 8,500단어; 초록·서론·배경·방법·결과(표 8·그림 9)·논의·결론·참고문헌·부록). 다음 단계: 비OA 문헌 반영, 2인 코딩 검증(κ), 저널 양식 맞춤, 저자·소속 기입 | paper/ |
| 2026-08-31 | 9 | v2 완성: be-후행어 해소(01 개정, 91.9%), 거시 정렬(06, FRED CFNAI/VIX/갭), 상관·FDR 스크린(07), 시차·Granger·예측(08), 적대적 검증 워크플로(발견 28건→검증 12건, 인공물 다수 처형)+비평 잔여항목 실행(09, G1–G6), 문헌 근거 워크플로(EVIDENCE_feedback3.md), docs/07 종합, 초안 v2(paper/draft_v2.md+.docx). 핵심: 상관 축은 VIX(불확실성)이지 CFNAI(실물) 아님(Kawamura 비전이); fair-weather 보류/위기 채택/심의 관용구 3기제; would be appropriate=살아있는 심의 신호; 예측력 증분 없음(F3 0/113) | Phase 9 커밋들, docs/07, paper/draft_v2 |
| 2026-08-31 | 9+ | 비OA 처리: Nuyts·Hyland 원문 수령(검증), 사용자 제공 3번째 파일은 오다운로드(ESP editorial)로 판명 — Donohue 미확보(정확 DOI 10.1016/j.esp.2005.02.009), Deng et al. 2024+Resche 2015로 대체. Leech 2003→Leech 2004(OA), Millar 2009→Bowie et al. 2013(OA, Millar 2차 인용 유지)로 교체. draft_v2 인용·참고문헌 갱신, docx 재생성 | literature/, docs/05, paper/draft_v2 |
| 2026-09-04 | 10.0 | 논문 미팅(지도교수) 녹취·팀 피드백 4건 분석 → 재실험 전략 docs/08. 층위 감사(qa_layer_audit.py → QA1–QA4): 기자회견 조동사 토큰의 19.7%가 기자 발화(could 48%, might 50%), 의사록 be+appropriate는 will=위원회 섹션(50/58)·would=참가자 섹션(142/247) → 교수님 will/would 질문의 답. Phase 10–13 계획 수립(TASKS.md) | docs/08, experiments/qa_layer_audit.py, results/tables/QA1–QA4 |
| 2026-09-04 | 10–12 | **v3 실행**: 층위 코퍼스(10: 정제·화자 분절·의사록 섹션 귀속·인용 성명서/지침 분리; QA Jaccard .94), 추출 v3(11: 32,388 토큰), QA(12), 데이터 카드(docs/09), CFNAI·VIX 근거(docs/10), 시나리오 러너(13: S1–S6 × U1–U3 = 18개, 블록 X-A~X-G, T1/T2/T3·반기 검사 내장), 보고서(14: results/report). 결과 요약 docs/11. 핵심: 반경기 양태 없음(전 시나리오); 성명서 계단 25 변화점 중 17 사건 일치; 성명서만(S1)으로는 확정 거시 신호 0–1; 의사록 위원회 층 would+be+appropriate × CFNAI +.39·VIX +.33 등 확정; v2 헤드라인 minutes can×VIX는 규정문·명단 오염(84 중 21)으로 소멸; Granger 전부 FDR 탈락 | ea0b4da + Phase 11–12 커밋 |
| 2026-09-04 | 12.7 | 실험 보고서 v3 작성(paper/report_v3.md + docx/html; 요약·데이터 v3·설계·결과 I 언어 구조·결과 II 구문×거시·시나리오 격자·주장 후보·CFNAI/VIX 근거·의사록 명분·v2 수정 항목). 러너 보정: U1 이중 집계 제거, T1-only/시대구성 플래그 분리 후 18개 재실행 | paper/report_v3.*, results/report/report_v3_artifact.html |
| 2026-09-04 | 14 (계획) | **사용자 재지시**: (1) 기존 실험이 없다고 보고 정제 데이터로 전 시나리오(의사록 포함·미포함 등 가능한 모든 코퍼스 조합) 실험을 완전히 다시 수행, (2) 산출은 코퍼스 언어학·경제학 각각의 관행을 따른 **실험 결과보고서**(HTML), (3) 모든 과정·판단·업무 목록은 인수인계서에 기록. → Phase 14 '전면 재실험 프로그램 v3' 설계: 코퍼스 조합 = 성명서{0,1} × 의사록{없음, 위원회층, 실질층} × 기자회견{없음, 의장} × 연설{0,1} = 23개 + 비교용 미정제 2개 = 25개 코퍼스 정의 × 단위 3종(조동사/구문/동사부류) = 75회 실행. 실험군 L(코퍼스 언어학: 코퍼스 기술·pmw·분산, 키니스(LL·log ratio), 통시 추세(MK·Sen·PELT), 연어·collostruction·distinctive collexeme·의미부류·KWIC, 정형성·생존·보유율·편집 이벤트, 문법 맥락(부정·수동·조건·인용·주어)·의미유형, 층위 분업(χ²·V·다항로짓), be appropriate, 의장·국면 대조) + 실험군 E(계량경제: 기술통계, 상관, HAC OLS 스펙 표(1)–(6), 구문 회귀, 전수 스크린·FDR·확정 ledger, CCF·Granger·예측 회귀, 사건 연구, 강건성(래그·회의간 VIX·정규화·1차 차분·2010 확장), Kawamura 재현 표). 가설 H1–H5 사전 명시. 13_run_scenarios(Phase 11)는 예비 실행으로 격하 | docs/12(설계), experiments/20–23 |
| 2026-09-04 | 14.1–14.6 | 전면 재실험 프로그램 구현: docs/12 설계(가설 H1–H5, 코퍼스 24종 × 단위 3종), experiments/20(공통: 코퍼스 열거·pmw/CI/DP·키니스·HAC·BH·MK·PELT), 21(L1–L9), 22(E1–E9 + 가설 판정), 23(실행기, 멀티프로세스). 스모크 테스트 9 run 전부 오류 0. **판단**: 위원회 층 총밀도의 1차 차분 회귀에서 ΔCFNAI −0.27***가 나왔으나 2020 제외 시 소멸(−1.9, p=.19) → 스펙 (8) 'Δ 2020 제외'를 E3·E4·E9에 추가하고 H3 판정은 수준·차분 모두 2020 제외에서도 유의할 때만 '지지'. 전체 72 run 실행 개시 | experiments/20–23, results/program/ |
| 2026-09-04 | 14.6 | 전체 72 run 실행. **문제·판단**: 4 워커 × 멀티스레드 BLAS 과다 구독으로 run당 20s → 최대 1,617s로 폭증(34 run에 55분) → 워커를 중지하고 23에 BLAS 단일 스레드 환경변수와 `--skip-existing`을 추가해 잔여 38 run을 112s에 완료. E7 사건 연구가 연설 단독 코퍼스(C13)에서 같은 날짜의 연설 중복으로 실패 → 날짜별 평균으로 수정 후 재실행. 최종 72 run 오류 0 | results/program/*, results/qa/program*.stderr |
| 2026-09-04 | 15 | 실험 결과보고서 HTML: 본문 paper/report_v3_program.md(요약·가설·데이터·설계·결과 A L1–L9·결과 B E1–E9·72 run 비교·가설 판정·논의·한계) + 빌더 24(표·그림 삽입 태그, run별 부록 페이지 72개). **72 run 판정 분포**: H1 지지 39/해당없음 33, H2 지지 60/해당없음 12, **H3 기각 72**, H4 지지 37/부분 26/기각 9, H5 기각 64/지지 8(경계). 본문 수치는 C11_U2 표로 검증(추세 τ, 회귀 계수, 사건 창, be appropriate 계수 등 5건 정정) | results/report_v3/index.html, run_*.html, paper/report_v3_program.md |
| 2026-09-04 | 15+ | 범용 문서 변환기 experiments/25_md_to_html.py 추가(보고서 스타일시트 재사용). docs/12 설계 명세를 docs/html/12_experiment_program_v3.html로 변환·게시 | docs/html/ |
| 2026-09-04 | 15.5 | **사용자 피드백**: 논문에 쓸 수 있는 수준·계층적 구성·버전(의사록 포함/미포함 등) 탭 비교·방법론→결과 순서·방법의 학술적 명분. 대응: (1) 본문 §3을 '방법론과 학술적 근거'로 확장(무엇을/왜/근거 표 8개 + 방법론 참고문헌 45편; 다중우주·명세곡선 분석으로 전 조합 설계를 정당화), (2) experiments/26_build_report_tabs.py — 탭 보고서: 개요 / 비교 / V1 성명서만(S1) · V2 +위원회 층(S2) · V3 +의사록 실질 층(S3) · V4 4장르 정제(S4) · V5 의사록만(S5) · V6 미정제(S6), 각 버전에 단위 서브탭(U2/U1/U3)과 1 데이터→2 언어학→3 계량경제→4 가설의 계층 구조, 표·그림 번호와 주석, 핵심 결과 상자; 비교 탭에 버전 × (가설·핵심 통계·총밀도 상관·회귀 계수·확정 단위 합집합·Kawamura) 표. 산출 results/report_v3/report_tabs.html(8.5 MB) | paper/report_v3_program.md §3, experiments/26, results/report_v3/report_tabs.html |
| 2026-09-04 | 15.6 | 사용자 피드백 2건 반영: (1) 강조 행 글자가 흐림 → 원인은 추천 상자용 `.reco` 클래스가 표 행에도 적용되어 흰 글자가 된 스타일 충돌; 행 클래스를 `hl`로 분리하고 진한 글자·왼쪽 강조선 적용, 표 글꼴 13.5px. (2) 여섯 버전 탭의 개요 요구 → 개요 탭 최상단에 '버전 개요' 표(버전별 선택 기준 / 진행 / 결과·가설)를 추가하고 각 버전 탭 상단에 같은 정보의 '이 버전' 상자 추가(VERSION_INFO, 결과는 summary.json에서 자동) | experiments/24·26, results/report_v3/report_tabs.html |

### ⚠ 2026-08-31 레포 삭제·재생성 사건
- Phase 9.1–9.3 푸시 시 GitHub 레포(airlab-tsw/fomc-modality-analysis)가 원격에서 존재하지 않음(404). airlab-tsw·GSkim0507 계정 어디에도 이름 변경/이전 흔적 없음 → 삭제된 것으로 판단.
- 로컬 이력은 온전하여 동일 이름의 private 레포를 재생성하고 전체 이력을 다시 푸시함.
- **의도적으로 삭제한 것이었다면 알려줄 것** (재삭제/이전 처리 가능).

## 5. 결정 사항 / 가정
- D1. 분석 기간 2014-01-01 ~ 2026-04-29(코퍼스 마지막 회의). 2010–2013은 비교·강건성용으로만 사용.
- D2. 6대 조동사 = will, would, could, can, should, may. might/must/shall은 보조 집계.
- D6. (v2) be-후행어 해소: head가 코퓰러 be일 때 보어(acomp/attr/prep/advmod)를 predicate로 승격(be+prepared 등), 형용사 보어는 표면형 유지. 수동·진행은 기존 로직이 이미 어휘동사로 해소.
- D7. (v2) 거시 정합: 주검정 = CFNAI-MA3(실시간 2개월 래그) + VIX(회의 전 28일 평균) — Kawamura 비교가능성. 실업률갭·근원PCE갭은 강건성 전용. 2020년 제외·2010-2026 확장·Spearman을 강건성 축으로 사용.
- D5. 조동사 추이의 1차 설명 가설 = 정형 문장(boilerplate) 편집 이벤트(docs/02 §3). 실험 6.4에서 문장 재사용률로 정량 검정.
- D3. 주 분석 장르 = Statement(세미나 관찰의 원천). Minutes·Press Conference·Speech는 장르 대조·강건성 분석.
- D8. (제안, 2026-09-04) 의사록: 층위(섹션) 라벨을 붙여 포함하고 statement-only(S1) 결과를 항상 병기. minutes-only는 불가(세미나 원 관찰과 계단식 편집이 성명서 현상). 명분은 docs/08 §4 — **팀 수용 여부 확인 필요**.
- D9. (제안) 코로나 2020: 포함(T1)·제외(T2) 두 버전 병기, T1에서만 튀는 결과는 "코로나 시기 반응"으로 서술. Figure 4(계단)는 T1만.
- D10. (제안) 주 코퍼스 = S4(4장르, 기자·진행자 제거, 귀속 라벨); S1·S2 비교 열.
- D11. (제안) 분석 단위 = 구문(modal+predicate)으로 전 RQ 통일; 조동사 단위는 "집계 시 은폐" 비교 열로만. RQ 5→3(인벤토리 / 구문 계단 / 구문×거시), 선행성은 부록.
- D12. (교수님 발언) 타깃 저널 = 경제학(JEL E58). Kawamura 비교는 인용 수준.
- D13. ECB 비교는 fallback으로만 준비.
- D14. 화용론 축(will/would vs can/could)은 교수님 문헌 검토 후 포함 결정; X-D 대조표만 준비.
- D15. (v3) 확정(confirmed) 규칙 = Spearman T1·T2 p<.05 동부호 + 2014–19/2021–26 반기 동부호 + 토큰≥40·제로회의≤60%, 층위 수준 집계. T1-only = 2020 의존, era_composition = 반기 부호 불일치.
- D16. (v3) 시나리오 폴더 = S × U; T(기간)·N(정규화)은 블록 내부 변형 열. 권장 메인 S4_U2, 비교 S1_U2·S2_U2.
- D17. (2026-09-04, 사용자) 실험은 v2 결과에 의존하지 않고 v3 정제 데이터로 전면 재수행. 가능한 모든 코퍼스 조합(의사록 포함/미포함 포함)을 실행하고 결과를 병렬 제시. 선택은 팀.
- D18. (사용자) 보고서 양식 = 실험 결과보고서: 코퍼스 언어학 관행(정규화 빈도 pmw·신뢰구간·분산, 키니스·효과크기, 연어·collostruction, KWIC 용례, 통시 검정) + 경제학 관행(기술통계표, 스펙별 회귀표(계수·HAC SE·유의성 별표·N·R²), 강건성 표, Granger·사건연구, FDR). 산출은 HTML.
- D19. (사용자) 과정·판단·업무 목록은 항상 HANDOVER.md에 기록. 저장소는 로컬 전용.
- D20. (v3 프로그램) 회귀 스펙 (1) CFNAI (2) VIX (3) 둘 다 (4) +갭 (5) +2020-09 더미 (6) 2020 제외 (7) 1차 차분 (8) 1차 차분·2020 제외. 가설 판정 규칙은 experiments/22 `hypotheses()`에 코드로 고정.
- D4. 조동사 판별은 spaCy `tag_ == "MD"` + 축약형(’ll/’d) 복원 + 표면형 정규화(ca n't 등).

## 6. 미해결 / 사용자 확인 필요
- (2026-09-04, Phase 15) 보고서 v3의 주 run = C11_U2. 팀이 조합·단위·결론 문장을 선택해야 논문 v3 착수 가능(D8–D11). H4 '부분' 판정의 원인인 성명서 will+assess × VIX(반기 −.07/−.27)를 '확정'으로 볼지 팀 판단 필요.
- (2026-09-04) 시나리오·주장 선택(D8–D11) — docs/11 §4 추천안 참조. 사람 검증 표본 3종 미완.
- (2026-09-04) `minutes_20121023`(T3 전용)은 PDF 유래 포맷으로 층위 미분류(데이터 카드 §8).
- (2026-09-04) D8 의사록 포함 명분(docs/08 §4)에 대한 팀 수용 여부.
- (2026-09-04) 이미지로 공유된 다른 세션의 화자 분절기(80문서 5,250턴 검증)는 이 레포에 없음 → Phase 10.2에서 재작성(qa_layer_audit.py의 정규식이 동일 수치 재현: 의장 2,194 / 기자 2,186 / 진행자 848턴).
- (2026-09-04) 회의에서 언급된 'E2(ECB?) 코퍼스'는 이 레포에 없음. 위치 확인 필요(D13 fallback용).
- 비OA 논문 5편 원문 필요: Leech 2003, Millar 2009, Hyland 1996, Donohue 2006, Nuyts 2001 (docs/05 §2). 브라우저 수동 다운로드 4편: Cannon 2015, Doh et al. 2022, Resche 2004, VerbNet thesis (docs/05 §3).
- 의미 유형(epistemic/deontic/dynamic) 휴리스틱은 저자 60문장 표본에서 ≈90% 일치. 논문 투고 전 2인 코딩(κ)으로 대체 권장 — `results/tables/D7_validation_sample.csv`(200문장)에 수작업 열 준비됨.
- `experiments/common.py`의 동사 의미 부류 사전(VERB_CLASS)은 저자 정의. Biber et al.(1999) 원 분류표와 대조 검토 필요.

## 7. 실행 방법(재현)

### v3 (Phase 10–12, 2026-09-04~)
```bash
.venv/bin/python experiments/10_build_corpus_v3.py     # ~3.5분: corpus_docs_v3.csv, corpus_sentences_v3.csv (layer 열), results/qa/build_v3_log.json
.venv/bin/python experiments/11_extract_modals_v3.py   # ~7분: modal_tokens_v3.csv (01의 추출 규칙 재사용 + layer/section/speaker)
.venv/bin/python experiments/12_qa_integrity.py        # results/qa/QA_report.md + 검증 표본 CSV
.venv/bin/python experiments/13_run_scenarios.py --corpus all --unit all   # results/scenarios/<S>_<U>/ (18개)
.venv/bin/python experiments/14_build_report.py        # results/report/*.html, report_all.html(단일 파일)
```
층위·시나리오 정의는 `experiments/common_v3.py`. 거시 지표 근거는 `docs/10`. v2 스크립트(00–09)는 보존.

### v2 (Phase 6–9)
```bash
.venv/bin/python experiments/00_build_corpus.py      # ~4분: results/tables/corpus_{docs,sentences}.csv
.venv/bin/python experiments/01_extract_modals.py    # ~6분: results/tables/modal_tokens.csv
cd experiments && for s in 02 03 04 05; do ../.venv/bin/python ${s}_*.py; done   # 각 1분 내
```
출력 표 접두어: A(후행 동사) B(시계열) C(정형성·생존) D(맥락·장르). 그림은 results/figures/.
