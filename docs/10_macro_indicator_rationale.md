# 10. 거시 지표 선택의 학술적 근거 — 왜 CFNAI와 VIX인가

> 목적: 논문 §3(Data)와 심사 답변에 그대로 쓸 수 있는 형태로, 실물 활동 지표로 **CFNAI(Chicago Fed National Activity Index)**, 불확실성 지표로 **VIX**를 주검정 변수로 택한 이유, 대안 지표를 채택하지 않은 이유, 정렬(alignment) 규칙을 정리한다. 결정 D7(HANDOVER)의 근거 문서.

---

## 0. 한 문단 요약

연구질문 "조동사 구문이 경제 상황을 설명하는가"는 (i) 6주 간격의 회의 단위로 정렬 가능하고, (ii) 회의 시점에 위원회가 실제로 알 수 있었던(real-time) 정보이며, (iii) **실물 활동**과 **불확실성**이라는 두 차원을 분리하고, (iv) 벤치마크 연구(Kawamura et al., 2019)와 비교 가능하며, (v) 텍스트로 만든 지표가 아니어서 종속변수와 **순환성**이 없고, (vi) 연준 반응함수의 목표 변수가 아니어서 성명서가 직접 언급하는 수치와 **기계적 상관**을 만들지 않는 지표를 요구한다. 이 여섯 조건을 동시에 만족하는 조합이 CFNAI(3개월 이동평균, 2개월 실시간 래그)와 VIX(회의 전 28일 평균)다. 실업률 갭·근원 PCE 갭은 조건 (vi)에 걸리므로 강건성 전용, EPU·MPU는 조건 (v)에 걸리므로 강건성 전용, GDP·JLN 불확실성은 조건 (i)(ii)에 걸린다.

---

## 1. 연구질문이 지표에 요구하는 조건

| 조건 | 내용 | 걸리는 대안 |
|---|---|---|
| (i) 빈도·정렬 | FOMC 회의는 연 8회(약 6주 간격). 월별 이상 빈도가 필요하고 회의일 기준으로 정렬 가능해야 함 | 분기 GDP, 분기 SPF |
| (ii) 실시간성 | 회의 시점에 공개되어 있던 값. 사후 개정치·지연 발표치는 위원회의 정보집합이 아님 | 개정 전 GDP, 개정이 큰 고용 통계(단독 사용 시), JLN 불확실성 |
| (iii) 두 차원의 분리 | 연준 커뮤니케이션 문헌은 "경기 상태 정보" 채널과 "불확실성·위험관리" 채널을 구분(Greenspan, 2004의 risk-management approach) | 단일 지표 |
| (iv) 비교가능성 | Kawamura et al.(2019)은 경기지수(내각부 CI: 선행·동행·후행)와 VIX·닛케이 VI를 사용 | 벤치마크와 다른 축 |
| (v) 비순환성 | 뉴스 텍스트 기반 지표는 연준 발언이 지표 자체에 들어감 | EPU, MPU |
| (vi) 반응함수 변수 회피 | 성명서는 실업률·인플레이션 수치를 직접 서술 → 텍스트와 지표의 상관이 "언급"에 의해 기계적으로 생김 | 실업률(갭), 인플레이션(갭), 정책금리 |

---

## 2. 실물 활동: CFNAI

### 2.1 무엇인가
- 시카고 연준이 매월 발표하는 **85개 월별 실물 지표의 가중 평균(제1 주성분)**. 생산·소득, 고용·실업·근로시간, 개인소비·주택, 판매·주문·재고의 4개 범주. 평균 0, 표준편차 1로 정규화되어 "추세 성장 대비 활동 수준"을 뜻한다(0 = 추세 성장).
- 방법론적 원천은 Stock & Watson(1999)의 활동 지수. **3개월 이동평균(CFNAI-MA3)**은 월별 잡음을 걸러내기 위해 시카고 연준이 권장하는 형태이며, 확장기 이후 −0.70 아래로 내려가면 경기침체 진입 가능성이 높아진다는 공식 해석 기준이 있다(Evans, Liu & Pham-Kanter, 2002; Brave, 2009).
- 예측·현황 판단(nowcasting) 용도로 검증됨(Brave & Butters, 2014).

### 2.2 왜 CFNAI인가
1. **광범위성**: 단일 지표(실업률, 산업생산)와 달리 실물 경제 전반을 요약 → "경제 상황"이라는 연구질문의 대상과 맞는다.
2. **연준 시스템 내부 지표**: 연준의 정보집합에 가까운 지표(Romer & Romer, 2000이 강조한 연준의 정보 우위와 정합).
3. **조건 (vi)**: 성명서는 "the unemployment rate has remained low", "inflation … 2 percent"처럼 목표 변수를 직접 서술하지만 CFNAI를 서술하지는 않는다 → 텍스트-지표 상관이 언급 효과가 아니라 상태 효과.
4. **조건 (iv)**: Kawamura et al.(2019)의 일본 내각부 경기동향지수(CI)에 대응하는 미국 지표. CI 동행지수 ↔ CFNAI(동행·활동), CI 선행지수 ↔ Conference Board LEI. 우리는 동행 활동 지수를 주검정에 쓰고, 선행성은 X-G에서 리드 변수(cfnai_ma3_lead1/3/6)로 별도 검정한다.
5. **월별·안정적 발표 일정**(익월 하순).

### 2.3 실시간 정렬 규칙
- 회의 월 *m*의 CFNAI는 *m+1* 하순에 발표된다. 따라서 회의 시점에 확실히 공개된 최신값은 **m−2월치**(보수적) 또는 m−1월치(회의가 월말이면 공개되어 있음). 주검정 = `cfnai_ma3_lag2`, 강건성 = `cfnai_ma3_lag1`. Kawamura et al.(2019)도 종합지수에 2개월 래그를 적용한다.
- 한계: FRED의 최종 개정치를 사용하며 발표 당시 vintage가 아니다. CFNAI는 구성 지표 개정으로 소폭 수정되므로 결론에 영향은 작다고 보지만, ALFRED vintage로 재검정하는 것이 향후 강건성 항목이다.

### 2.4 채택하지 않은 실물 지표
| 대안 | 미채택 이유 |
|---|---|
| 실질 GDP 성장률 | 분기 빈도, 발표 지연·대폭 개정 → (i)(ii) 위반 |
| 실업률 / 실업률 갭(UNRATE−NROU) | 연준 반응함수 변수, 성명서가 직접 언급 → (vi). **강건성 전용**(E2 `robust+gaps`) |
| 근원 PCE 인플레이션 갭 | 동일 이유 → 강건성 전용 |
| 정책금리·금리 변화 | 지표가 아니라 정책 결과(내생) |
| Conference Board LEI | 선행지수는 X-G 선행성 검정에서 lead 변수로 대체; 주검정은 동행 지수 |
| Sahm rule, 침체 더미 | 이진·희소 → 100회 표본에서 검정력 부족 |

---

## 3. 불확실성: VIX

### 3.1 무엇인가
- CBOE가 S&P 500 지수 옵션 가격에서 산출하는 **30일 내재변동성**(Whaley, 2009). 일별·실시간·무개정. 시장 참여자가 가격에 반영한 향후 한 달의 불확실성(과 위험회피)을 측정한다.

### 3.2 왜 VIX인가
1. **불확실성 충격의 표준 측정치**: Bloom(2009)은 VIX를 거시 불확실성 충격의 대표 지표로 확립했고, 이후 문헌이 이를 따른다.
2. **통화정책과의 연결**: Bekaert, Hoerova & Lo Duca(2013)는 VIX를 불확실성 성분과 위험회피 성분으로 분해하고, 통화정책 완화가 위험회피를 낮추는 경로를 보였다 → 연준 커뮤니케이션과 VIX의 관계는 이론적으로 정당화된 연구 대상이다.
3. **조건 (iv)**: Kawamura et al.(2019)이 "내생적 불확실성만으로 모호성 증가가 설명되는가"를 검정할 때 통제변수로 쓴 것이 VIX다. 같은 변수를 쓰면 "일본에서는 경기(CI)가, 미국에서는 불확실성(VIX)이 관련된다"는 대조가 지표 차이가 아닌 실제 차이로 읽힌다.
4. **조건 (ii)(v)**: 회의 전날까지의 시장 가격 → 위원회가 회의 당일 아침에 정확히 알고 있던 값이며, 텍스트에서 만들어진 값이 아니다.
5. **연준 커뮤니케이션 문헌의 관행**: 성명서 문구 변화와 시장 변동성을 연결한 Ehrmann & Talmi(2020)를 비롯해 시장 내재변동성이 표준 결과 변수/통제변수로 쓰인다.

### 3.3 정렬 규칙
- 주검정 `vix_pre28` = **회의 전날까지 28일간 일별 VIX 평균**: 회의 직전 6주 정보집합의 후반부를 대표하면서, 회의 당일 발표 후 시장 반응(내생성)은 제외한다.
- 강건성 `vix_intermeeting` = 직전 정례회의 이후 평균(정보집합 전체).
- 선행성 검정용 `vix_post28`, `d_vix_28` = 회의 후 28일 평균과 그 변화.

### 3.4 채택하지 않은 불확실성 지표
| 대안 | 미채택 이유 |
|---|---|
| EPU (Baker, Bloom & Davis, 2016) | 신문 기사 텍스트 기반. 연준 발언·성명이 기사에 인용되어 지표에 들어감 → (v) 순환성. 강건성 후보 |
| MPU (Husted, Rogers & Sun, 2020) | 통화정책 불확실성 뉴스 지수. 연준 커뮤니케이션에 직접 반응하도록 설계됨 → (v). 강건성 후보 |
| 시장 기반 통화정책 불확실성 (Bauer, Lakdawala & Mueller, 2022) | 금리 옵션 기반으로 순환성은 없으나, 정책 자체의 불확실성이라 "경제 상황"이 아닌 "정책 상황"을 측정 |
| JLN 거시 불확실성 (Jurado, Ludvigson & Ng, 2015) | 대규모 예측오차 기반의 우수한 지표이나 월별 발표 지연·개정 → (ii). 강건성 후보 |
| NFCI (시카고 연준 금융조건지수) | VIX를 포함하는 합성지수 → 해석 중복 |
| 실현 변동성 | 후행적; 내재변동성이 기대를 담음 |

### 3.5 한계와 대응
- VIX는 **금융시장** 불확실성이지 거시·정책 불확실성 그 자체가 아니다 → 본문에서 "불확실성 환경(uncertainty environment)"으로 서술하고, EPU·JLN 강건성을 향후 항목으로 명시.
- 2020년 3월(VIX ≈ 50–80)은 극단 관측치 → 모든 거시 표에 T1(포함)·T2(2020 제외)를 병기(D9).

---

## 4. 왜 두 지표를 "한 쌍"으로 쓰는가

1. **판별 목적**: 연구질문의 답은 "실물인가, 불확실성인가"의 판별을 포함한다. 두 지표를 같은 회귀에 넣어야 한 쪽의 효과가 다른 쪽의 대리로 나타나는지 가릴 수 있다(Kawamura et al.도 CI와 VIX를 함께 넣어 "내생적 불확실성으로는 설명되지 않는다"는 결론을 얻었다).
2. **간결성**: 관측치가 회의 수(약 100)이므로 설명변수는 최소로. 두 변수 + 상수 + Newey–West HAC(4 lag) 표준오차가 주모형. 갭 변수는 강건성 열에서만 추가.
3. **해석의 대칭성**: 두 지표 모두 "높을수록 나쁜/불확실한 상태"가 아니라, CFNAI는 높을수록 호황, VIX는 높을수록 불확실 → 부호 해석이 독립적이다.

---

## 5. 정렬 스펙 요약

| 변수 | 정의 | 역할 | FRED 코드 |
|---|---|---|---|
| `cfnai_ma3_lag2` | CFNAI 3개월 이동평균, 회의 월 m−2 | 주검정(실물) | CFNAIMA3 |
| `cfnai_ma3_lag1` | 동일, m−1 | 강건성 | CFNAIMA3 |
| `vix_pre28` | 회의 전날까지 28일 평균 | 주검정(불확실성) | VIXCLS |
| `vix_intermeeting` | 직전 정례회의 이후 평균 | 강건성 | VIXCLS |
| `unrate_gap_lag1` | UNRATE(m−1) − NROU | 강건성 전용 | UNRATE, NROU |
| `corepce_gap_lag2` | 근원 PCE yoy(m−2) − 2 | 강건성 전용 | PCEPILFE |
| `cfnai_ma3_lead{1,3,6}`, `vix_post28`, `d_vix_28` | 회의 후 값 | 선행성(X-G) | — |

---

## 6. 논문용 문단 (영문 초안)

> *Macroeconomic anchors.* Following Kawamura et al. (2019), who pair a composite activity index with the VIX, we relate construction frequencies to two variables: the Chicago Fed National Activity Index (three-month moving average; Stock & Watson, 1999; Evans et al., 2002) as a broad, monthly, real-time measure of real activity that FOMC statements do not themselves cite, and the CBOE VIX (Whaley, 2009) as the standard market-priced measure of uncertainty (Bloom, 2009; Bekaert et al., 2013). Both are observable to the Committee at the meeting: CFNAI enters with the two-month publication lag, and VIX as the mean over the 28 days ending the day before the meeting. We deliberately exclude the Committee's own target variables (unemployment and inflation gaps), which statements describe verbatim and which would induce mechanical correlation, and text-based uncertainty indices (Baker et al., 2016; Husted et al., 2020), whose construction incorporates Federal Reserve communication itself; both enter only as robustness checks.

---

## 7. 참고문헌 (투고 전 서지 재확인 필요 표시 ※)

- Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty. *Quarterly Journal of Economics*, 131(4), 1593–1636.
- Bauer, M. D., Lakdawala, A., & Mueller, P. (2022). Market-based monetary policy uncertainty. *Economic Journal*, 132(644), 1290–1308. ※
- Bekaert, G., Hoerova, M., & Lo Duca, M. (2013). Risk, uncertainty and monetary policy. *Journal of Monetary Economics*, 60(7), 771–788.
- Bloom, N. (2009). The impact of uncertainty shocks. *Econometrica*, 77(3), 623–685.
- Brave, S. (2009). The Chicago Fed National Activity Index and business cycles. *Chicago Fed Letter*, No. 268. ※
- Brave, S., & Butters, R. A. (2014). Nowcasting using the Chicago Fed National Activity Index. *Economic Perspectives*, 38(1), 1–20. ※
- Ehrmann, M., & Talmi, J. (2020). Starting from a blank page? Semantic similarity in central bank communication and market volatility. *Journal of Monetary Economics*, 111, 48–62.
- Evans, C. L., Liu, C. T., & Pham-Kanter, G. (2002). The 2001 recession and the Chicago Fed National Activity Index: Identifying the business cycle turning point. *Economic Perspectives*, 26(3), 26–43.
- Greenspan, A. (2004). Risk and uncertainty in monetary policy. *American Economic Review*, 94(2), 33–40.
- Husted, L., Rogers, J., & Sun, B. (2020). Monetary policy uncertainty. *Journal of Monetary Economics*, 115, 20–36.
- Jurado, K., Ludvigson, S. C., & Ng, S. (2015). Measuring uncertainty. *American Economic Review*, 105(3), 1177–1216.
- Kawamura, K., Kobashi, Y., Shizume, M., & Ueda, K. (2019). Strategic central bank communication: Discourse analysis of the Bank of Japan's Monthly Report. *Journal of Economic Dynamics and Control*, 100, 230–250.
- Romer, C. D., & Romer, D. H. (2000). Federal Reserve information and the behavior of interest rates. *American Economic Review*, 90(3), 429–457.
- Stock, J. H., & Watson, M. W. (1999). Forecasting inflation. *Journal of Monetary Economics*, 44(2), 293–335.
- Whaley, R. E. (2009). Understanding the VIX. *Journal of Portfolio Management*, 35(3), 98–105.
