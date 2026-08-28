# 01. 기존 리포트 분석 — 「미 연준의 양태 표현은 점도표와 정합하는가?」

> 원문: `NLP 개론 기말발표(최종)`, 성균관대학교 언어AI대학원 영어공학과, 2026-1 (슬라이드 16장)
> 코드·산출물: `FOMC_corpus/analysis/` (스크립트 01–18, CSV, figures/)

## 1. 연구 질문과 설계 논리 (어떤 의도로 실험했는가)

| RQ | 내용 | 대응 실험 | 결론(보고서) |
|---|---|---|---|
| RQ1 | 2010–2026 FOMC 문서에서 양태(modality) 표현은 어떤 양상을 띠는가? | ① 조동사 분포 ② N-gram ③ 감성×MSI ④ 장르별 MSI ⑤ 2021 will→would 전환 | would(9.7k)·will(7.8k) 양극 공존; Statement의 MSI가 압도적으로 높음(제도화된 register); 2021년부터 Statement에서 would 급증 |
| RQ2 | 양태가 점도표(dot plot)의 매파/비둘기 방향과 정량적으로 상관이 있는가? | ⑥-① LM(Loughran-McDonald) modal × Δ점도표 (n=39) | r = −0.374, p = 0.019 — 양태가 강할수록 점도표는 **인하** 방향(역상관) |
| RQ3 | 방향 신호와 확신도 신호가 같은 어휘 채널을 공유하는가? | ⑥-② 정책 행동 동사(raise/tighten/hike…) × Δ점도표 | r = +0.549, p < 0.001 — 방향은 행동 동사, 확신은 양태가 담당(채널 분리) |

**설계 의도(재구성)**
1. 출발점은 언어학적 직관 — *양태 조동사는 화자의 확신도를 부호화하는 문법 자원*(Coates 1983; Palmer 1990; Hyland 1998). 연준 텍스트에서 이 자원이 어떻게 쓰이는지 대규모로 보고자 했다.
2. "정합성(consistency)" 프레임 — 텍스트(soft signal)와 점도표(hard, 정량 signal)를 같은 회의에서 짝지어, 언어적 확신도가 정책 방향과 정렬되는지 검정하려 했다. 즉 **양태를 정책 커뮤니케이션의 전략 변수**로 본다는 것이 핵심 가설.
3. 수업 코드(POS, N-gram, VADER) + α(MSI) — 교과 요구를 충족하면서 이론 기반 지표(MSI)를 추가해 "인용 가능한 정량 지표"를 만들려 했다.
4. 최종 주장: *"연준의 양태 표현은 정책 방향과 역으로 평활화되어 있으며, 이 역상관 자체가 통화정책 커뮤니케이션의 전략이다(hedging as policy)"* — Kawamura et al. (2019)의 "strategic ambiguity" 논지를 FOMC로 옮긴 형태.

## 2. 데이터·방법 요약

- 코퍼스: 535문서, ≈2.4M 단어. Statement 137 / Minutes 132 / Press Conference 92 / Chair Speech 174 (2010–2026).
- 점도표 라벨: FRB SEP 표 파싱 → 39회차 (H 16 / D 12 / N 11).
- 방법: ① spaCy `en_core_web_sm` MD 태그로 조동사 추출(`01_pos_pipeline.py`) ② 조동사 ±3토큰 N-gram(`04_ngrams.py`) ③ VADER 문장 감성(`16_vader_sentiment.py`) ④ MSI — 조동사별 확신 가중치(must/will=1.0, would=1.0, should/shall=0.7, can/could=0.4, may/might=0.3) + 인식양태 부사/형용사 가중치(`02_modality_index.py`) ⑤ LM 사전, 행동 동사, 점도표 상관(`07`, `10`, `11`, `15`).

## 3. 주요 결과 (재사용 가치 순)

1. **장르 register 효과** — MSI ANOVA F = 151, η² ≈ 0.46–0.59, Tukey: Statement ≫ 나머지 3장르; 세 의장 시기 모두 재현(`paper_b_stats.txt`). 카이제곱(조동사 × 장르) V = 0.277; 표준화 잔차: Statement는 will(+34.9) 과다, would/can 과소; Minutes는 would/could/shall 과다; Press Conf는 can(+21.7) 과다; Speech는 may/must 과다.
2. **2021년 Statement will→would 구조 전환** — 2010–2020 Statement에서 will 75–100% → 2021부터 would 15–25%. 보고서는 이를 "데이터 의존 정책으로의 전환 → 무조건(will)에서 조건(would)로의 의도적 이동"으로 해석.
3. N-gram 상위: `the committee will`(809), `will continue to`(536) vs `it would be`(465), `the committee would`(458), `would be appropriate`(267).
4. LM modal × Δ점도표 r = −0.374; 행동 동사 × Δ점도표 r = +0.549.
5. 오태깅 한계 L1–L4: 축약형(’ll/’d), em-dash 결합 토큰, 단순 미래 will(Minutes will의 8–12%), 간접 인용 would(Minutes would의 18–25%).

## 4. 비판적 평가 — 세미나에서 조동사 자체로 초점을 옮긴 배경

| 쟁점 | 문제 | 본 연구에서의 처리 |
|---|---|---|
| MSI 가중치 | will = would = 1.0은 언어학적으로 무리(would는 가정/조건/과거시제 will/간접인용 등 다의). 가중치 자체가 임의적이라 "MSI가 높다"의 의미가 불명확 | 가중치 합산 대신 **조동사별 분리 분석** + 후행 동사·구문 맥락으로 의미를 직접 관찰 |
| 점유율 vs 밀도 | "will 감소"가 점유율(share)인지 밀도(per 1k tokens)인지 혼재. 예비 확인 결과 Statement의 will 밀도는 9–17/1k로 대체로 평탄, 점유율 감소는 would/could 유입에 따른 **구성 효과** | 점유율·문서당 빈도·토큰 정규화 밀도를 모두 보고 |
| 장르 혼합 | 4장르를 합산한 결과(예: would 9.7k)는 대부분 Minutes/Press Conf에서 나옴. 세미나의 관찰(should 소멸 등)은 Statement 고유 패턴 | Statement를 주 분석 단위로, 타 장르는 대조군 |
| 검정력 | 점도표 상관 n = 39 | 조동사 시계열은 회의 단위(2014–2026 Statement 100편, 전 장르 500편+) |
| 태깅 | MD 태그 의존, 축약형·간접인용 미처리 | 의존구문 기반 추출 + 축약형 복원 + 간접인용/조건절 플래그 |
| 해석 | "의도적 이동"이라는 강한 해석을 빈도만으로 뒷받침 | 문장 단위로 어떤 문장이 생기고 사라졌는지(정형 문장 편집 이벤트) 추적하여 인과적 서사를 텍스트 증거로 제시 |

## 5. 재사용 가능한 자산

- `analysis/modal_instances.csv` (33,164 조동사 토큰; 문장·head verb 포함) — 예비 검증용. 본 실험에서는 재추출.
- `analysis/pos_summary.csv`, `modality_index.csv` — 문서별 토큰 수·MSI (장르 대조 강건성).
- `analysis/dotplot_labels.csv`, `dotplot_medians.csv`, `frb_sep_medians.csv` — 정책 국면(매파/비둘기) 외생 라벨로 재활용 가능.
- `analysis/paper_b_stats.txt` — 장르 ANOVA·카이제곱 결과(논문의 배경 통계).
- `figures/04_modal_freq_by_year.png`, `07_modal_share_stacked.png`, `15_paperB_modal_share_by_genre.png`.
- 참고 코드: `08_genre_stats.py`(Tukey 구현), `04_ngrams.py`(윈도 N-gram).
