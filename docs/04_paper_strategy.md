# 04. 학술논문화 전략 및 논문 구성안

## 1. 포지셔닝

**한 줄 기여** — *FOMC 성명서(2014–2026)의 조동사 분포 변화는 소수의 정형 구문(modal + verb construction)의 도입·삭제로 설명되는 "편집된 정형성(edited formulaicity)"의 산물이며, 각 조동사는 고정된 후행 동사·주어·조건 구문에 결합해 장르별로 기능을 분업한다.*

**틈새(gap)**
- 중앙은행 텍스트 연구(Kawamura et al. 2019; Hansen & McMahon 2016; Ehrmann & Talmi 2020 등)는 양태/모호성을 집계 지표로만 다루고, 개별 조동사와 그 구문은 보지 않는다.
- 응용언어학의 hedging/modality 연구(Hyland 1996/1998; Resche 2004/2015; Donohue 2006)는 소규모·정성 중심이며, 회의 단위 시계열·변화점·생존분석을 적용한 예가 없다.
- 영어 조동사 통시 연구(Leech 2003; Millar 2009; Leech et al. 2009)는 일반 코퍼스(Brown/LOB/TIME)의 수십 년 변화를 다루며, **제도적 장르 내부의 단기(13년) 편집 동학**은 미개척.

**독자·저널 후보(우선순위)**
1. *Journal of Pragmatics* / *English for Specific Purposes* / *Journal of English for Academic Purposes* — 응용언어학·ESP: 조동사 구문 + 제도 담화(가장 자연스러운 착지점).
2. *Corpora* / *International Journal of Corpus Linguistics* / *Corpus Linguistics and Linguistic Theory* — 코퍼스 방법론 강조 시.
3. *Journal of Economic Dynamics & Control* / *Journal of Monetary Economics* — 경제학 독자를 겨냥하려면 시장 반응·정책 변수와의 연결이 추가로 필요(향후 논문 B).
4. 국내: 『언어와 정보』, 『담화와 인지』, 『영어학』, 『코퍼스언어학』(한국코퍼스언어학회) 등 — 한국어판/국내 학회 발표용 축약본.
→ **1차 타깃: ESP 계열(영문)**, 국내 학회 발표본을 병행.

**제목(안)**
- *Edited formulaicity: How modal verbs enter and leave FOMC statements (2014–2026)*
- *Will, would, could: Modal-verb constructions and their half-lives in Federal Reserve communication*

## 2. 논문 구성안 (섹션별 내용·표·그림 계획)

### 1. Introduction (≈1.5쪽)
- 후크: 2020-09-16 이후 모든 FOMC 성명서에 등장하는 한 문장("The Committee would be prepared … could impede …")이 would/could 점유율을 0에서 15–20%로 바꿨다.
- 문제 제기: 양태를 "확신도 점수"로 합산하는 접근(선행연구·기존 보고서)은 이런 구문 단위 사건을 볼 수 없다.
- RQ1 각 조동사는 어떤 동사·주어·구문과 결합하는가? RQ2 2014–2026 조동사 빈도는 어떻게 변했고, 변화는 점진적인가 계단형인가? RQ3 조동사 구문의 지속성(반감기)은 얼마이며 무엇이 변화를 유발하는가? RQ4 장르(성명서·의사록·기자회견·연설)에 따라 조동사 기능은 어떻게 분업되는가?
- 기여 3가지.

### 2. Background (≈2쪽)
- 2.1 영어 양태 조동사의 의미론: epistemic / deontic / dynamic (Coates 1983; Palmer 1990/2001; Collins 2009), 통시적 감소(Leech 2003; Millar 2009).
- 2.2 Hedging과 제도 담화: Hyland 1996/1998; Resche 2004/2015; Donohue 2006.
- 2.3 정형 언어와 구문: lexical bundles(Biber et al. 1999; Biber & Barbieri 2007), formulaic sequences(Wray 2002), collostructional analysis(Stefanowitsch & Gries 2003).
- 2.4 중앙은행 커뮤니케이션 텍스트 분석: Blinder et al. 2008/2024; Hansen & McMahon 2016; Kawamura et al. 2019; Acosta & Meade 2015(성명서 유사도); Ehrmann & Talmi 2020(성명서 재사용과 변동성).
- 2.5 FOMC 성명서 제도 배경: 편집 관행(전 회의 성명서를 수정), 2017 정상화, 2020 프레임워크, 2022–24 정책 사이클.

### 3. Data and Methods (≈2.5쪽)
- 3.1 코퍼스: 4장르 문서 수·토큰 수(2014–2026), 표 1.
- 3.2 추출: spaCy 의존구문 기반 modal 토큰 + 후행 어휘동사 + 부정/수동/완료/주어/조건절/간접인용 플래그; 축약형 처리; 표본 수작업 검증(정확도).
- 3.3 후행 동사 분석: 전수 빈도, 의미 부류 코딩(Biber 7범주 + 정책행동), collostruction strength(Fisher exact, log-likelihood), 조동사 간 JSD.
- 3.4 시계열: 회의별 밀도·점유율; Mann–Kendall + Sen slope; PELT 변화점; 정책 사건 대응.
- 3.5 반감기: (a) 구문 코호트 Kaplan–Meier 생존(회의 수), (b) 문장 재사용률 기반 편집 이벤트, (c) AR(1) 지속성.
- 3.6 장르·의장·정책국면 대조: 카이제곱·표준화 잔차, 로지스틱/다항 회귀(조동사 선택 ~ 장르 + 시기 + 주어 유형).

### 4. Results (≈5쪽)
- 4.1 개관: 조동사 6종 빈도(장르 × 기간), 그림 1(연도별 밀도, 장르 패널).
- 4.2 후행 동사(RQ1): 표 2(조동사별 상위 후행 동사 + collostruction), 그림 2(의미 부류 히트맵), 대표 구문 예문.
- 4.3 시계열(RQ2): 그림 3(성명서 회의별 점유율 + 변화점 + 정책 사건 수직선), 표 3(MK/Sen 결과).
- 4.4 편집 이벤트와 반감기(RQ3): 표 4(정형 문장 목록·도입·삭제 시점), 그림 4(구문 생존곡선, 조동사별 중위 생존), "should 소멸·would/could 도입·will 점유율 감소"의 분해(설명 비율).
- 4.5 장르 분업(RQ4): 그림 5(장르 × 조동사 잔차), can의 기자회견 집중, would의 의사록 간접인용, 성명서의 will 절차 약속.
- 4.6 의장·정책국면 강건성.

### 5. Discussion (≈2쪽)
- 편집된 정형성: 성명서는 "쓰는" 텍스트가 아니라 "고치는" 텍스트 → 조동사 통계는 제도적 편집 결정의 흔적.
- Kawamura의 전략적 모호성과의 관계: 미국 사례에서는 모호성 증가가 아니라 **조건부 약속 구문(would be prepared … if)**의 제도화.
- Resche의 "hedging은 확산적"에 대한 응답: 구문 단위 정량화로 co-text 포섭.
- 함의: 텍스트 지표(hawkish/dovish, uncertainty) 설계 시 정형 문장 효과 통제 필요.

### 6. Limitations & Future Work / 7. Conclusion
- 파서 오류, 의미 유형 자동 분류 한계, 성명서 표본 수, 시장 반응 미연결(후속 논문).

### 표·그림 목록(계획)
- 표 1 코퍼스 · 표 2 후행 동사/collostruction · 표 3 추세·변화점 · 표 4 정형 문장 이벤트 · 표 5 장르×조동사 잔차 · (부록) 검증 표본 정확도, 전체 후행 동사 목록
- 그림 1 밀도 시계열 · 그림 2 의미 부류 히트맵 · 그림 3 성명서 점유율+변화점 · 그림 4 생존곡선 · 그림 5 장르 잔차 · (부록) 의장별

## 3. 실험 설계 명세 (조작적 정의)

| 항목 | 정의 |
|---|---|
| 분석 창 | 2014-01-01 ~ 2026-04-29 (2010–2013은 부록 강건성) |
| 조동사 | will(’ll), would(’d), could, can, should, may (+ might, must, shall 보조) |
| 후행 동사 | 조동사가 지배하는 어휘동사 lemma(aux 사슬 have/be/get 건너뜀); 수동태는 과거분사 lemma |
| 밀도 | 회의(문서)별 조동사 수 / 토큰 수 × 1,000 |
| 점유율 | 회의별 해당 조동사 수 / 6대 조동사 합 |
| 구문 | (modal, head_verb) 쌍; 성명서에서 회의 t에 처음 등장한 구문 코호트의 생존 = 이후 연속 회의에서의 출현 |
| 반감기 | Kaplan–Meier 중위 생존(회의 수) 및 로그-선형 근사 |
| 변화점 | `ruptures` PELT (l2), penalty BIC; 최소 세그먼트 4회의 |
| 정책 사건 | 2017-06-14(정상화 부록), 2017-10(축소 개시), 2019-08(첫 인하), 2020-03(팬데믹), 2020-08-27(프레임워크), 2022-03-16(인상 개시), 2023-07(마지막 인상), 2024-09-18(인하 개시), 2025-08(프레임워크 재검토, 코퍼스 확인) |
| 의미 유형 | epistemic / deontic / dynamic — 규칙(주어 유형·후행 동사·부사) + 200문장 수작업 검증(κ 보고) |
