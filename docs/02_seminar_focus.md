# 02. 세미나 결과 파악 — 무엇에 집중해 논문화할 것인가

## 1. 세미나 결정 사항 (사용자 전달 내용)
- 분석 기간: **2014–2026**
- 집중 실험
  1. **조동사 '후행 동사' 전수 분석** — 조동사 뒤에 결합하는 동사 및 의미 패턴
  2. **6대 조동사별 추이 세부 분석** — 사용 빈도 추이·반감기 등 시계열 특성. 질문: *왜 2018년 이후 should는 사라졌고, will은 점점 감소하며, could/would는 늘고, can은 항상 낮은가? 각 조동사는 주로 어떤 상황에서 쓰이는가?*
  3. 관련하여 가능한 **모든 언어학적 분석**

## 2. 예비 검증 — 세미나 관찰은 Statement 장르의 패턴이다

기존 `modal_instances.csv`(spaCy MD)로 Statement 장르의 조동사 점유율(%)을 연도별로 보면:

| year | will | would | could | can | should | may |
|---|---|---|---|---|---|---|
| 2014 | 74.4 | 0.0 | 3.3 | 0.8 | **15.7** | 5.8 |
| 2015 | 74.6 | 0.0 | 0.0 | 1.5 | 11.9 | 11.9 |
| 2016 | 88.9 | 0.0 | 0.0 | 0.0 | 11.1 | 0.0 |
| 2017 | 94.7 | 1.3 | 0.0 | 0.0 | 4.0 | 0.0 |
| 2018 | **100.0** | 0.0 | 0.0 | 0.0 | **0.0** | 0.0 |
| 2019 | 84.6 | 0.0 | 5.1 | 0.0 | 0.0 | 10.3 |
| 2020 | 82.4 | 4.7 | 3.5 | 4.7 | 2.4 | 1.2 |
| 2021 | 72.5 | **14.5** | **11.6** | 0.0 | 0.0 | 1.4 |
| 2022 | 67.3 | 16.3 | 16.3 | 0.0 | 0.0 | 0.0 |
| 2023 | 62.9 | 12.9 | 12.9 | 0.0 | 0.0 | 11.3 |
| 2024 | 71.4 | 14.3 | 14.3 | 0.0 | 0.0 | 0.0 |
| 2025 | 67.3 | 16.3 | 16.3 | 0.0 | 0.0 | 0.0 |
| 2026 | 60.0 | 20.0 | 20.0 | 0.0 | 0.0 | 0.0 |

→ 세미나의 네 가지 관찰(should 소멸·will 감소·would/could 증가·can 저빈도)이 **모두 Statement 장르에서 정확히 재현**된다. 전 장르 합산에서는 이 패턴이 희석된다(Minutes·Press Conf가 토큰의 95%를 차지). 따라서 **주 분석 단위 = FOMC Statement**, 타 장르는 대조군.

## 3. 원인 진단(1차) — 정형 문장(boilerplate)의 도입·삭제 이벤트

Statement 원문을 정규식으로 추적한 결과, 조동사 추이는 점진적 문체 변화가 아니라 **특정 정형 문장의 편집 이벤트**로 설명된다.

| 조동사 | 담당 정형 문장 | 존속 기간(Statement) | 정책 맥락 |
|---|---|---|---|
| should | *"This policy, by keeping the Committee's holdings of longer-term securities at sizable levels, **should help maintain** accommodative financial conditions."* (선행형: *"…**should maintain** downward pressure on longer-term interest rates…"* 2012-12~2014-09) | 2014-10-29 → **2017-05-03** (21편) | 재투자 정책 문구. 2017-06 정상화 계획 부록 → 2017-10 대차대조표 축소 개시와 함께 삭제 → **2018 이후 should 소멸** |
| would / could | *"The Committee **would be prepared** to adjust the stance of monetary policy as appropriate if risks emerge that **could impede** the attainment of the Committee's goals."* | **2020-09-16 → 2026-04-29 (46편, 전량)** | 2020-08 새 통화정책 프레임워크(Statement on Longer-Run Goals 개정) 직후 도입된 상시 조건절 문장 → 2021부터 would/could 각 12–20% |
| may | *"…economic conditions **may**, for some time, **warrant** keeping the target federal funds rate below levels the Committee views as normal in the longer run."* | 2014-03-19 → 2015-10-28 (14편) | 제로금리 해제 전 포워드 가이던스 |
| will | *will take into account*(98편, 2014-03~), *will assess*(72편), *will continue to monitor*(67편), *will be appropriate*(47편, ~2024-07), *will carefully assess*(19편, 2024-01~), *will continue to reduce*(27편, 2022-06~2025-09) | 지속 | 절차적 약속(procedural commitment) 문장군. **밀도는 9–17/1k tokens로 평탄**, 문서당 빈도는 11(2013–14) → 3–5(2022–26)로 감소 = Statement 길이 축소(839 → 340 토큰)와 would/could 유입에 따른 **점유율 구성 효과** |
| can | *"…the Committee judges that it **can be patient** in beginning to normalize…"*(2014-12, 2015-01) 외 극소수 | 산발 | Statement는 위원회의 예측·약속(epistemic/volitional)을 진술하는 장르라 능력·허용(dynamic/deontic) 양태인 can이 구조적으로 배제됨. Press Conf(즉흥 발화)에서는 can 과다(+21.7 잔차) |

**함의**: FOMC Statement의 조동사 시계열은 (i) 정책 프레임워크 사건과 정렬된 **계단형(step) 변화**이고, (ii) 각 조동사는 특정 구문(construction: modal + following verb)에 고정되어 있으며, (iii) "반감기"는 구문 단위의 **생존(survival)**으로 조작화하는 것이 자연스럽다(도입된 modal 구문이 몇 회의 뒤 절반이 소멸하는가).

## 4. 논문화 대상 실험 정의

### 실험 A — 후행 동사 전수 분석 (Modal + V construction)
- 단위: 의존구문 기반 (modal, 후행 어휘동사 lemma, 부정 여부, 수동/진행/완료 여부, 주어 head).
- 산출: 조동사별 후행 동사 빈도표(전수), 의미 부류(Biber et al. 1999의 동사 의미 범주: activity / communication / mental / causative / occurrence / existence / aspectual + 정책 행동 동사), **collostructional analysis**(Stefanowitsch & Gries 2003: 어느 동사가 어느 조동사에 유의하게 끌리는가/밀리는가, Fisher exact / log-likelihood), 조동사 간 후행 동사 분포 거리(JSD), 장르별·시기별 변화.

### 실험 B — 6대 조동사 시계열 (will, would, could, can, should, may)
- 지표: 회의별 원빈도, 문서당 빈도, per-1k 밀도, 점유율(share).
- 추세: Mann–Kendall 검정 + Sen's slope; 구조 변화점(PELT/Binary segmentation, `ruptures`) → 정책 사건(2017-06 정상화, 2020-08 프레임워크, 2022-03 인상 개시, 2024-09 인하 개시)과 대조.
- **반감기**: (a) 조동사 구문(modal+V lemma) 코호트 생존곡선(Kaplan–Meier) → 구문 반감기; (b) 조동사별 시계열의 자기상관/AR(1) 지속성(persistence half-life = ln0.5/lnρ); (c) 정형 문장 재사용률(문장 단위 Jaccard/edit distance)과 조동사 변화의 연결.
- 의장별(Yellen 2014-02~2018-01, Powell 2018-02~) 대조, 정책 국면(인상/동결/인하) 대조.

### 실험 C — 사용 맥락(각 조동사는 어떤 상황에서 쓰이는가)
- 주어 유형(the Committee / it / economic conditions / risks / inflation …), 조건절(if/should/as/when) 동반 여부, 부정, 수동, 시간 부사, 간접 인용(Minutes), 1인칭(Press Conf), 양태 의미 유형(epistemic / deontic / dynamic; Coates 1983·Palmer 1990 기준으로 규칙+수동 샘플 검증).
- 장르 4종 × 조동사 6종 대조(카이제곱 + 표준화 잔차), 조동사별 대표 구문(lexical bundles) 추출.

### 추가로 가능한 언어학적 분석(우선순위 순)
1. 정형성(formulaicity) 측정: 연속 Statement 간 문장 재사용률, 신규/삭제 문장에서의 조동사 비율 → "조동사 변화 = 편집 이벤트" 가설의 직접 검정.
2. 양태 의미 유형 분류(epistemic/deontic/dynamic) — 규칙 기반 + 표본 수작업 검증(κ).
3. 조건 구문(*if … could*, *would be prepared*) 네트워크: 조동사 공기(co-occurrence) 분석.
4. Press Conf 즉흥 발화 vs Statement 편집 텍스트의 조동사 프로파일 비교(register variation).
5. 정책 국면(점도표 H/D/N 라벨 재사용)에 따른 조동사 분포 차이.
6. 준양태(be going to, be expected to, be likely to, need to)와의 대체 관계 — will 감소가 준양태로 이전했는지.

## 5. 우선순위와 논문 핵심 주장(가설)
- H1 (정형성): Statement의 조동사 분포 변화는 소수의 정형 문장 도입·삭제로 대부분 설명된다(설명 비율 정량화).
- H2 (구문 고정성): 각 조동사는 소수의 후행 동사에 강하게 결합한다(collostruction strength 높음; Statement > 타 장르).
- H3 (정책 정렬): 변화점은 정책 프레임워크 사건과 시점이 일치한다.
- H4 (장르 분업): can/could/would의 분포는 장르의 발화 상황(즉흥 vs 편집, 보고 vs 약속)에 의해 결정된다.
- 반감기: Statement 조동사 구문의 중위 생존 기간(회의 수)을 처음으로 보고한다.
