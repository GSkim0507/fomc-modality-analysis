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
- GitHub: `gh` CLI 인증 계정 `airlab-tsw` (활성). 레포 정보는 아래 §4.

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

## 5. 결정 사항 / 가정
- D1. 분석 기간 2014-01-01 ~ 2026-04-29(코퍼스 마지막 회의). 2010–2013은 비교·강건성용으로만 사용.
- D2. 6대 조동사 = will, would, could, can, should, may. might/must/shall은 보조 집계.
- D5. 조동사 추이의 1차 설명 가설 = 정형 문장(boilerplate) 편집 이벤트(docs/02 §3). 실험 6.4에서 문장 재사용률로 정량 검정.
- D3. 주 분석 장르 = Statement(세미나 관찰의 원천). Minutes·Press Conference·Speech는 장르 대조·강건성 분석.
- D4. 조동사 판별은 spaCy `tag_ == "MD"` + 축약형(’ll/’d) 복원 + 표면형 정규화(ca n't 등).

## 6. 미해결 / 사용자 확인 필요
- 비OA 논문 5편 원문 필요: Leech 2003, Millar 2009, Hyland 1996, Donohue 2006, Nuyts 2001 (docs/05 §2). 브라우저 수동 다운로드 4편: Cannon 2015, Doh et al. 2022, Resche 2004, VerbNet thesis (docs/05 §3).
- 의미 유형(epistemic/deontic/dynamic) 휴리스틱은 저자 60문장 표본에서 ≈90% 일치. 논문 투고 전 2인 코딩(κ)으로 대체 권장 — `results/tables/D7_validation_sample.csv`(200문장)에 수작업 열 준비됨.
- `experiments/common.py`의 동사 의미 부류 사전(VERB_CLASS)은 저자 정의. Biber et al.(1999) 원 분류표와 대조 검토 필요.

## 7. 실행 방법(재현)
```bash
.venv/bin/python experiments/00_build_corpus.py      # ~4분: results/tables/corpus_{docs,sentences}.csv
.venv/bin/python experiments/01_extract_modals.py    # ~6분: results/tables/modal_tokens.csv
cd experiments && for s in 02 03 04 05; do ../.venv/bin/python ${s}_*.py; done   # 각 1분 내
```
출력 표 접두어: A(후행 동사) B(시계열) C(정형성·생존) D(맥락·장르). 그림은 results/figures/.
