# 시나리오 S4_U2 — 4 genres, journalists removed, attribution labels × modal + predicate

> 권장안. 기자·진행자 발화 제거, 의사록 규정문·인용문 제거.

## 코퍼스 (T1 2014–2026)

| 층위 | 문서 | 토큰 | 6대 조동사 | per 1k |
|---|---:|---:|---:|---:|
| Statement | 101 | 41,906 | 770 | 18.37 |
| Minutes: Desk/markets (staff) | 99 | 71,942 | 553 | 7.69 |
| Minutes: staff review & outlook | 99 | 249,885 | 539 | 2.16 |
| Minutes: participants' views | 99 | 223,992 | 2,756 | 12.3 |
| Minutes: Committee policy action | 99 | 62,833 | 958 | 15.25 |
| Minutes: special topics | 40 | 40,777 | 783 | 19.2 |
| Press conf.: Chair | 80 | 533,106 | 10,686 | 20.04 |
| Chair speech | 124 | 234,853 | 3,203 | 13.64 |

## X-A 구문 인벤토리

- 주 층위 Statement: 조동사별 1위 단위 will→will+continue (21%), would→would+be+prepared (94%), could→could+impede (92%), can→can+be+patient (50%), should→should+help (64%), may→may+warrant (56%); 조동사 간 JSD 1.00–1.00

## X-B 구문 계단 (성명서)

- 회의 101회, 상위 단위 11개에서 PELT 변화점 25개, 그중 정책 사건 ±1회의 이내 17개.

| 단위 | 변화점 | 전→후 점유율 | 최근접 사건 | 원인 문장 |
|---|---|---|---|---|
| will+continue | 2019-07-31 | 0.03→0.26 | Mid-cycle cut (0d) | As the Committee contemplates the future path of the target range for the federal funds rate, it will continue to monitor the implications o |
| will+take | 2014-10-29 | 0.12→0.25 | QE3 ends (0d) | This assessment will take into account a wide range of information, including measures of labor market conditions, indicators of inflation p |
| will+take | 2015-12-16 | 0.25→0.11 | First hike (liftoff) (0d) | This assessment will take into account a wide range of information, including measures of labor market conditions, indicators of inflation p |
| will+take | 2018-06-13 | 0.12→0.29 | Powell chair (128d) | This assessment will take into account a wide range of information, including measures of labor market conditions, indicators of inflation p |
| will+take | 2020-03-03 | 0.28→0.09 | Pandemic ZLB (12d) | This assessment will take into account a wide range of information, including measures of labor market conditions, indicators of inflation p |
| will+take | 2022-03-16 | 0.12→0.22 | Hiking cycle begins (0d) | The Committee's assessments will take into account a wide range of information, including readings on public health, labor market conditions |
| will+assess | 2018-06-13 | 0.12→0.29 | Powell chair (128d) | In determining the timing and size of future adjustments to the target range for the federal funds rate, the Committee will assess realized  |
| will+assess | 2020-03-03 | 0.28→0.07 | Pandemic ZLB (12d) | In determining the timing and size of future adjustments to the target range for the federal funds rate, the Committee will assess realized  |
| will+assess | 2024-01-31 | 0.00→0.15 | Last hike (189d) | In considering any adjustments to the target range for the federal funds rate, the Committee will carefully assess incoming data, the evolvi |
| could+impede | 2020-09-16 | 0.00→0.12 | New framework (20d) | The Committee would be prepared to adjust the stance of monetary policy as appropriate if risks emerge that could impede the attainment of t |
| would+be+prepared | 2020-09-16 | 0.00→0.12 | New framework (20d) | The Committee would be prepared to adjust the stance of monetary policy as appropriate if risks emerge that could impede the attainment of t |
| will+be+appropriate | 2015-12-16 | 0.12→0.00 | First hike (liftoff) (0d) | The Committee sees this guidance as consistent with its previous statement that it likely will be appropriate to maintain the 0 to 1/4 perce |
| will+be+appropriate | 2020-09-16 | 0.00→0.12 | New framework (20d) | The Committee decided to keep the target range for the federal funds rate at 0 to 1/4 percent and expects it will be appropriate to maintain |
| will+be+appropriate | 2023-03-22 | 0.17→0.02 | Last hike (126d) | In support of these goals, the Committee decided to raise the target range for the federal funds rate to 1/4 to 1/2 percent and anticipates  |
| will+expand | 2018-06-13 | 0.12→0.00 | Powell chair (128d) | The Committee continues to expect that, with gradual adjustments in the stance of monetary policy, economic activity will expand at a modera |
| will+monitor | 2015-12-16 | 0.00→0.11 | First hike (liftoff) (0d) | In light of the current shortfall of inflation from 2 percent, the Committee will carefully monitor actual and expected progress toward its  |
| will+monitor | 2018-06-13 | 0.12→0.00 | Powell chair (128d) | The Committee will carefully monitor actual and expected inflation developments relative to its symmetric inflation goal. |
| will+depend | 2015-12-16 | 0.00→0.11 | First hike (liftoff) (0d) | However, the actual path of the federal funds rate will depend on the economic outlook as informed by incoming data. |
| will+depend | 2018-06-13 | 0.12→0.00 | Powell chair (128d) | However, the actual path of the federal funds rate will depend on the economic outlook as informed by incoming data. |
| will+depend | 2020-07-29 | 0.00→0.12 | New framework (29d) | The path of the economy will depend significantly on the course of the virus. |
| will+depend | 2021-07-28 | 0.12→0.00 | Hiking cycle begins (231d) | The path of the economy will depend significantly on the course of the virus. |
| should+help | 2014-10-29 | 0.00→0.12 | QE3 ends (0d) | This policy, by keeping the Committee's holdings of longer-term securities at sizable levels, should help maintain accommodative financial c |
| should+help | 2017-06-14 | 0.11→0.00 | Normalization addendum (0d) | This policy, by keeping the Committee's holdings of longer-term securities at sizable levels, should help maintain accommodative financial c |
| may+warrant | 2014-10-29 | 0.05→0.12 | QE3 ends (0d) | The Committee currently anticipates that, even after employment and inflation are near mandate-consistent levels, economic conditions may, f |
| may+warrant | 2015-12-16 | 0.12→0.00 | First hike (liftoff) (0d) | The Committee currently anticipates that, even after employment and inflation are near mandate-consistent levels, economic conditions may, f |

## X-C 지속성

- 보유율 반감기(회의 수): all=16.8, will=18.1, would=≥24, could=≥24, can=1.0, should=7.5, may=4.0, modal_sentences=4.5

## X-D 층위 분업

- 층위(8) × 조동사 χ²=6801, Cramér's V=0.259

## X-E 구문 × 거시

- Kawamura 검정(총 조동사 밀도 × CFNAI, Spearman): minutes T1 ρ=0.079 (p=0.4378); minutes T2 ρ=0.153 (p=0.1472); minutes T3 ρ=0.085 (p=0.334); press_conf T1 ρ=0.216 (p=0.0538); press_conf T2 ρ=0.258 (p=0.0302); press_conf T3 ρ=0.142 (p=0.1764); speech T1 ρ=-0.096 (p=0.2906); speech T2 ρ=-0.074 (p=0.4246); speech T3 ρ=-0.131 (p=0.084); statement T1 ρ=-0.124 (p=0.2158); statement T2 ρ=-0.178 (p=0.0909); statement T3 ρ=-0.096 (p=0.2697)
- 반기별 유의(총 밀도): press_conf × cfnai H2 ρ=0.317 (p=0.0385); statement × vix H1 ρ=-0.405 (p=0.0043); statement × cfnai H2 ρ=-0.518 (p=0.0004); statement × vix H2 ρ=-0.472 (p=0.0014)
- 총 조동사 밀도 × VIX: minutes T1 ρ=0.066 (p=0.5132); minutes T2 ρ=-0.008 (p=0.9406); minutes T3 ρ=-0.065 (p=0.4615); press_conf T1 ρ=0.319 (p=0.004); press_conf T2 ρ=0.297 (p=0.0118); press_conf T3 ρ=0.293 (p=0.0047); speech T1 ρ=-0.017 (p=0.8507); speech T2 ρ=-0.074 (p=0.4242); speech T3 ρ=-0.008 (p=0.9209); statement T1 ρ=0.061 (p=0.5425); statement T2 ρ=0.045 (p=0.6729); statement T3 ρ=-0.116 (p=0.185)
- 전수 스크린 2250행(층위 수준 집계): T1 BH q<.05 적중 48; **확정**(T1·T2 유의·동부호 + 2014–19/2021–26 반기 동부호) VIX 8건 / CFNAI 6건; T1에서만 유의(2020 의존) 35건; T1·T2 유의하나 반기 부호 불일치(시대 구성 효과) 25건

| 층위 | 단위 | 거시 | ρ T1 | ρ excl-2020 | ρ 2010– | ρ 2014–19 | ρ 2021–26 | 토큰 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| min_committee | would+continue | vix | 0.5 | 0.451 | 0.322 | 0.055 | 0.08 | 109 |
| min_committee | would+assess | cfnai | -0.491 | -0.43 | -0.392 | -0.379 | -0.394 | 49 |
| min_committee | would+depend | cfnai | 0.427 | 0.402 | 0.365 | 0.601 | 0.336 | 51 |
| min_committee | would+be+appropriate | cfnai | 0.407 | 0.391 | 0.4 | 0.22 | 0.538 | 63 |
| min_committee | could | cfnai | -0.251 | -0.37 | -0.13 | -0.415 | -0.548 | 83 |
| min_staff | ALL | vix | -0.333 | -0.361 | -0.393 | -0.197 | -0.235 | 539 |
| min_committee | would+be+appropriate | vix | 0.373 | 0.334 | 0.289 | 0.148 | 0.38 | 63 |
| min_staff | would | vix | -0.229 | -0.32 | -0.269 | -0.262 | -0.014 | 327 |
| min_committee | would | cfnai | 0.257 | 0.304 | 0.27 | 0.327 | 0.278 | 719 |
| min_staff_desk | could | cfnai | 0.213 | 0.252 | 0.182 | 0.241 | 0.269 | 138 |
| min_participants | should | vix | -0.239 | -0.244 | -0.292 | -0.085 | -0.155 | 149 |
| statement | will+assess | vix | -0.265 | -0.228 | -0.321 | -0.071 | -0.265 | 72 |

## X-F will/would + be appropriate

| 층위 | 단위 | 토큰 | ρ VIX T1 | ρ VIX excl-2020 | ρ CFNAI T1 | 제로 비율 T1 |
|---|---|---:|---:|---:|---:|---:|
| min_committee | may+be+appropriate | 13 | -0.092 (p=0.3658) | -0.058 (p=0.5824) | -0.222 | 0.89 |
| min_committee | will+be+appropriate | 7 | -0.102 (p=0.3139) | -0.155 (p=0.1425) | -0.012 | 0.93 |
| min_committee | would+be+appropriate | 63 | 0.373 (p=0.0001) | 0.334 (p=0.0012) | 0.407 | 0.55 |
| min_participants | may+be+appropriate | 11 | 0.022 (p=0.8306) | 0.055 (p=0.6052) | -0.154 | 0.94 |
| min_participants | would+be+appropriate | 143 | 0.21 (p=0.037) | 0.154 (p=0.1443) | -0.053 | 0.23 |
| min_special | would+be+appropriate | 23 | 0.217 (p=0.1787) | 0.325 (p=0.0531) | 0.289 | 0.6 |
| min_staff_desk | would+be+appropriate | 8 | 0.054 (p=0.5978) | 0.089 (p=0.4028) | -0.015 | 0.95 |
| pc_chair | may+be+appropriate | 21 | -0.09 (p=0.4249) | -0.044 (p=0.7154) | -0.122 | 0.89 |
| pc_chair | will+be+appropriate | 105 | -0.053 (p=0.6378) | 0.01 (p=0.932) | 0.203 | 0.42 |
| pc_chair | would+be+appropriate | 38 | -0.135 (p=0.2322) | -0.072 (p=0.5491) | -0.016 | 0.69 |
| speech_chair | will+be+appropriate | 21 | -0.033 (p=0.7157) | -0.046 (p=0.6179) | 0.047 | 0.86 |
| speech_chair | would+be+appropriate | 11 | -0.043 (p=0.6368) | -0.025 (p=0.7871) | -0.01 | 0.94 |
| statement | may+be+appropriate | 10 | -0.077 (p=0.4419) | -0.037 (p=0.7308) | -0.216 | 0.9 |
| statement | will+be+appropriate | 43 | 0.235 (p=0.018) | 0.287 (p=0.0058) | 0.364 | 0.61 |

## X-G 선행성 (부록)

- excl-2020 CCF 피크(Pearson·Spearman 동시 유의) 20건; Granger text→macro q<.10 0건
