# TASKS — FOMC 조동사(Modal Verb) 언어학 실험 및 학술논문화

> 상태 표기: `[ ]` 미착수 · `[~]` 진행 중 · `[x]` 완료 · `[!]` 블로킹(사용자 입력 필요)
> 각 Phase 완료 시 커밋·푸시. 상세 진행 기록은 `HANDOVER.md` 참조.

## Phase 0 — 프로젝트 세팅
- [x] 0.1 코퍼스 구조·기존 분석 산출물 파악 (`FOMC_corpus/`, `analysis/`)
- [x] 0.2 기존 보고서 PDF·핵심 참고문헌 2편 텍스트 추출
- [x] 0.3 Python 가상환경(.venv) + spaCy en_core_web_sm 설치
- [x] 0.4 TASKS.md / HANDOVER.md / README / .gitignore 작성
- [x] 0.5 git init → GitHub 레포 생성 → 첫 커밋·푸시

## Phase 1 — 기존 리포트 분석 (`docs/01_prior_report_analysis.md`)
- [x] 1.1 연구 질문(RQ1–3)·데이터·방법·결과·한계 정리
- [x] 1.2 "어떤 의도로 실험했는가" — 연구 동기·설계 논리 재구성
- [x] 1.3 기존 결과 중 재사용 가능한 자산(코드·CSV·그림) 목록화

## Phase 2 — 세미나 결과 파악 (`docs/02_seminar_focus.md`)
- [x] 2.1 세미나에서 결정된 집중 실험 2건의 정의·범위(2014–2026) 명세
- [x] 2.2 기존 데이터로 세미나 관찰(should 소멸·will 감소·would/could 증가·can 저빈도) 예비 검증
- [x] 2.3 논문화 대상 실험 우선순위 및 "추가로 가능한 언어학적 분석" 목록

## Phase 3 — 핵심 선행연구 분석 (`docs/03_key_prior_work_analysis.md`)
- [x] 3.1 Kawamura et al. (2019, JEDC) — 방법·결과·한계 정리
- [x] 3.2 Resche (2015, SComS) — 방법·결과·한계 정리
- [x] 3.3 우리 연구와의 차별점·개선점 매트릭스

## Phase 4 — 학술논문화 전략 (`docs/04_paper_strategy.md`)
- [x] 4.1 논문 포지셔닝(기여·타깃 저널/학회·프레이밍)
- [x] 4.2 논문 구성안(섹션별 내용·표·그림 계획)
- [x] 4.3 실험 설계 명세(분석 단위·조작적 정의·통계 방법)

## Phase 5 — 추가 자료 조사 (`docs/05_literature_list.md`, `literature/`)
- [x] 5.1 필요 선행연구 리스트 작성(언어학/중앙은행 커뮤니케이션/시계열)
- [x] 5.2 OA 논문 자동 다운로드 시도 → `literature/` 저장
- [x] 5.3 비OA 논문 목록 정리(사용자 원문 제공 요청)

## Phase 6 — 실험 수행 (`experiments/`, `results/`)
- [x] 6.1 문장 단위 코퍼스 재구축(2014–2026, 4장르, 인코딩 정리)
- [x] 6.2 조동사 추출 파이프라인 개선(축약형·간접인용·부정·수동 처리)
- [x] 6.3 실험 A: 조동사 후행 동사 전수 분석(동사 빈도·의미 부류·collostruction)
- [x] 6.4 실험 B: 6대 조동사 시계열(빈도 추이·구조 변화점·반감기·의장별)
- [x] 6.5 실험 C: 조동사별 사용 맥락(주어·대상·조건절·부정·장르)
- [x] 6.6 추가 언어학 분석(양태 의미 분류 epistemic/deontic/dynamic 등)
- [x] 6.7 결과 표·그림 생성

## Phase 7 — 종합 분석 (`docs/06_synthesis.md`)
- [x] 7.1 실험 결과 + 선행연구 + 추가 자료 종합
- [x] 7.2 논문 주장(claim) 확정 및 근거 매핑

## Phase 8 — 논문 초안 작성 (`paper/`)
- [x] 8.1 초안 v1 (영문, 학술지 형식)
- [x] 8.2 표·그림 삽입, 참고문헌 정리
- [x] 8.3 한계·향후 연구·부록

## Phase 9 — v2: 동료 피드백 반영 (`experiments/06–09`, `docs/07`, `paper/draft_v2`)
- [x] 9.1 be-후행어 해소(코퓰러 be → 보어 predicate)
- [x] 9.2 거시 정렬(CFNAI-MA3 + VIX) 및 상관·FDR 스크린
- [x] 9.3 시차·Granger·예측력 검정
- [x] 9.4 적대적 검증 워크플로 + 강건성 배터리 G1–G6
- [x] 9.5 종합(docs/07) + 초안 v2(md+docx), 문헌 v2

## Phase 10 — 데이터 재정제·정규화 v3 (2026-09-04 회의 결정; `docs/08` §3.2)
- [x] 10.0 회의록 분석·재실험 전략 문서(docs/08), 층위 감사(QA1–QA4)
- [ ] 10.1 원문 정제 v3: 헤더/푸터, "Return to text", "Share/Watch Live", 참석자 명단, 1월 조직사항·인가문·지침 → `boilerplate` 층 분리
- [ ] 10.2 기자회견 화자 분절(chair / moderator / journalist) + 수작업 검증(10문서×20턴)
- [ ] 10.3 의사록 섹션 귀속 파서(staff_desk / staff / participants / committee / vote / boilerplate / special / front_matter) + QA(미분류 <2%)
- [ ] 10.4 연설 Q&A 여부 점검, `chair_personal` 층
- [ ] 10.5 정규화 기준 고정(밀도 per 1k / 점유율 / 문서당 count 용도 명시), 층위별 분모 저장 (`common_v3.py`)
- [ ] 10.6 조동사 추출 v3(층위 라벨 전달) + 200문장 2인 코딩 정확도
- [ ] 10.7 무결성 QA 스크립트(회의일 정합, 중복·누락, 인코딩 잔재 0, v2 대비 차이 리포트) → `results/qa/QA_report.md`
- [ ] 10.8 데이터 카드 `docs/09_data_card_v3.md`

## Phase 11 — 시나리오 매트릭스 실험 (`docs/08` §3.3)
- [ ] 11.1 시나리오 러너 `run_scenarios.py` (코퍼스 S1–S4 × 단위 U1–U3 × 기간 T1–T3 × 정규화 N1–N3; 출력 `results/scenarios/<S>_<U>_<T>_<N>/` + `summary.json`)
- [ ] 11.2 X-A 구문 인벤토리(층위별)
- [ ] 11.3 X-B 구문 계단(Figure 4 구문판: 성명서 회의별 구문 점유율 스택 + PELT + 원인 문장 표) — 메인
- [ ] 11.4 X-C 편집 이벤트·보유율 반감기(지표 1개)
- [ ] 11.5 X-D 장르×귀속 분업 + will/would vs can/could 화용 대조표
- [ ] 11.6 X-E 구문×거시(사전 지정 구문 8–10개, CFNAI+VIX, T1/T2 병기, HAC) — 메인
- [ ] 11.7 X-F will/would 비대칭(be appropriate × 조동사 × 귀속 층 × VIX)
- [ ] 11.8 X-G 선행성(CCF·Granger·증분예측) 부록화
- [ ] 11.9 주 비교 3종(S1·S2·S4) × U2 × (T1,T2) 산출 확인

## Phase 12 — 비교 보고서·웹 열람 (`docs/08` §3.4)
- [ ] 12.1 `results/report/` 시나리오별 페이지(표·그림·한 줄 결론·시나리오 간 차이)
- [ ] 12.2 시나리오 비교 대시보드 + 한 문장 주장 후보 3개(C1–C3) 근거 격자
- [ ] 12.3 정적 HTML 배포(GitHub Pages 또는 Artifact) → 팀 회의
- [ ] 12.4 minutes 포함 명분(docs/08 §4) 팀 제출 → D8 결정

## Phase 13 — 논문 v3 재구성 (교수님 결정 후; `docs/08` §3.5)
- [ ] 13.1 시나리오·한 문장 주장 확정(D8–D14)
- [ ] 13.2 RQ 5→3 구조로 재작성(경제학 저널 지향), 일본 §5.2 → 인용 2–3문장, 추후연구 삭제
- [ ] 13.3 문헌 보강(be appropriate: Van linden 2012 등; 화용론: Collins 2009, Ward et al. 2003 등)
- [ ] 13.4 draft_v3.md + .docx
