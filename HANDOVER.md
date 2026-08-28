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
| 2026-08-28 | 0 | 코퍼스·기존 분석·보고서·참고문헌 파악, venv 구축, 문서 골격 작성, GitHub 레포 생성 | 초기 커밋 |

## 5. 결정 사항 / 가정
- D1. 분석 기간 2014-01-01 ~ 2026-04-29(코퍼스 마지막 회의). 2010–2013은 비교·강건성용으로만 사용.
- D2. 6대 조동사 = will, would, could, can, should, may. might/must/shall은 보조 집계.
- D3. 주 분석 장르 = Statement(세미나 관찰의 원천). Minutes·Press Conference·Speech는 장르 대조·강건성 분석.
- D4. 조동사 판별은 spaCy `tag_ == "MD"` + 축약형(’ll/’d) 복원 + 표면형 정규화(ca n't 등).

## 6. 미해결 / 사용자 확인 필요
- (없음 — 진행하면서 추가)
