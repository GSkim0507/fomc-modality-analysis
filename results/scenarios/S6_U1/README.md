# 시나리오 S6_U1 — unfiltered 4 genres (v2-like) × modal

> 비교용: 기자 발화·규정문·인용 성명서를 제거하지 않은 v2 방식.

## 코퍼스 (T1 2014–2026)

| 층위 | 문서 | 토큰 | 6대 조동사 | per 1k |
|---|---:|---:|---:|---:|
| Statement | 101 | 41,906 | 770 | 18.37 |
| Statement (vote line) | 100 | 5,441 | 10 | 1.84 |
| Minutes: Desk/markets (staff) | 99 | 71,942 | 553 | 7.69 |
| Minutes: staff review & outlook | 99 | 249,885 | 539 | 2.16 |
| Minutes: participants' views | 99 | 223,992 | 2,756 | 12.3 |
| Minutes: Committee policy action | 99 | 62,833 | 958 | 15.25 |
| Minutes: special topics | 40 | 40,777 | 783 | 19.2 |
| Minutes: front matter | 99 | 59,650 | 78 | 1.31 |
| Minutes: quoted statement | 99 | 40,613 | 761 | 18.74 |
| Minutes: quoted directive | 99 | 22,084 | 102 | 4.62 |
| Minutes: vote & post-vote | 99 | 16,987 | 166 | 9.77 |
| Minutes: SEP addendum | 0 | 0 | 0 | 0.0 |
| Minutes: authorizations/boilerplate | 99 | 65,197 | 376 | 5.77 |
| Press conf.: Chair | 80 | 533,106 | 10,686 | 20.04 |
| Press conf.: journalists | 80 | 138,373 | 2,452 | 17.72 |
| Press conf.: moderator | 49 | 1,981 | 83 | 41.9 |
| Press conf.: pre-marker | 2 | 18 | 0 | 0.0 |
| Chair speech | 124 | 234,853 | 3,203 | 13.64 |

## X-A 구문 인벤토리

- 주 층위 Statement: 조동사별 1위 단위 will→will (100%), would→would (100%), could→could (100%), can→can (100%), should→should (100%), may→may (100%); 조동사 간 JSD 1.00–1.00

## X-B 구문 계단 (성명서)

- 회의 101회, 상위 단위 6개에서 PELT 변화점 14개, 그중 정책 사건 ±1회의 이내 10개.

| 단위 | 변화점 | 전→후 점유율 | 최근접 사건 | 원인 문장 |
|---|---|---|---|---|
| will | 2015-12-16 | 0.70→0.89 | First hike (liftoff) (0d) | The Committee currently expects that, with gradual adjustments in the stance of monetary policy, economic activity will continue to expand a |
| will | 2020-09-16 | 0.95→0.75 | New framework (20d) | The Committee will continue to monitor the implications of incoming information for the economic outlook, including global developments and  |
| could | 2020-09-16 | 0.00→0.12 | New framework (20d) | The Committee would be prepared to adjust the stance of monetary policy as appropriate if risks emerge that could impede the attainment of t |
| would | 2020-09-16 | 0.00→0.13 | New framework (20d) | The Committee would be prepared to adjust the stance of monetary policy as appropriate if risks emerge that could impede the attainment of t |
| should | 2017-06-14 | 0.11→0.00 | Normalization addendum (0d) | This policy, by keeping the Committee's holdings of longer-term securities at sizable levels, should help maintain accommodative financial c |
| may | 2015-12-16 | 0.14→0.00 | First hike (liftoff) (0d) | The Committee currently anticipates that, even after employment and inflation are near mandate-consistent levels, economic conditions may, f |
| may | 2019-01-30 | 0.00→0.09 | Mid-cycle cut (182d) | In light of global economic and financial developments and muted inflation pressures, the Committee will be patient as it determines what fu |
| may | 2019-07-31 | 0.09→0.02 | Mid-cycle cut (0d) | In light of global economic and financial developments and muted inflation pressures, the Committee will be patient as it determines what fu |
| may | 2023-03-22 | 0.00→0.11 | Last hike (126d) | The Committee anticipates that some additional policy firming may be appropriate in order to attain a stance of monetary policy that is suff |
| may | 2024-01-31 | 0.11→0.00 | Last hike (189d) | The Committee anticipates that some additional policy firming may be appropriate in order to attain a stance of monetary policy that is suff |
| can | 2014-09-17 | 0.00→0.03 | QE3 ends (42d) | Based on its current assessment, the Committee judges that it can be patient in beginning to normalize the stance of monetary policy. |
| can | 2015-03-18 | 0.03→0.00 | QE3 ends (140d) | Based on its current assessment, the Committee judges that it can be patient in beginning to normalize the stance of monetary policy. |
| can | 2020-01-29 | 0.00→0.03 | Pandemic ZLB (46d) | More information can be found on the Federal Reserve Board's website . |
| can | 2020-04-29 | 0.03→0.00 | Pandemic ZLB (45d) | More information can be found on the Federal Reserve Board's website . |

## X-C 지속성

- 보유율 반감기(회의 수): all=≥24, will=≥24, would=≥24, could=≥24, can=1.0, should=13.5, may=4.0, modal_sentences=4.5

## X-D 층위 분업

- 층위(11) × 조동사 χ²=8953, Cramér's V=0.274

## X-E 구문 × 거시

- Kawamura 검정(총 조동사 밀도 × CFNAI, Spearman): minutes T1 ρ=0.099 (p=0.3278); minutes T2 ρ=0.158 (p=0.1359); minutes T3 ρ=0.095 (p=0.2764); press_conf T1 ρ=0.233 (p=0.0374); press_conf T2 ρ=0.27 (p=0.0227); press_conf T3 ρ=0.154 (p=0.1438); speech T1 ρ=-0.096 (p=0.2906); speech T2 ρ=-0.074 (p=0.4246); speech T3 ρ=-0.131 (p=0.084); statement T1 ρ=-0.047 (p=0.6392); statement T2 ρ=-0.086 (p=0.4183); statement T3 ρ=-0.067 (p=0.4435)
- 반기별 유의(총 밀도): press_conf × cfnai H2 ρ=0.392 (p=0.0094); statement × vix H1 ρ=-0.374 (p=0.0089); statement × cfnai H2 ρ=-0.358 (p=0.0184); statement × vix H2 ρ=-0.433 (p=0.0038)
- 총 조동사 밀도 × VIX: minutes T1 ρ=-0.026 (p=0.8); minutes T2 ρ=-0.125 (p=0.2389); minutes T3 ρ=-0.104 (p=0.2372); press_conf T1 ρ=0.315 (p=0.0044); press_conf T2 ρ=0.276 (p=0.0198); press_conf T3 ρ=0.318 (p=0.002); speech T1 ρ=-0.017 (p=0.8507); speech T2 ρ=-0.074 (p=0.4242); speech T3 ρ=-0.008 (p=0.9209); statement T1 ρ=-0.03 (p=0.7635); statement T2 ρ=-0.078 (p=0.4643); statement T3 ρ=-0.188 (p=0.0299)
- 전수 스크린 914행(층위 수준 집계): T1 BH q<.05 적중 23; **확정**(T1·T2 유의·동부호 + 2014–19/2021–26 반기 동부호) VIX 5건 / CFNAI 5건; T1에서만 유의(2020 의존) 3건; T1·T2 유의하나 반기 부호 불일치(시대 구성 효과) 16건

| 층위 | 단위 | 거시 | ρ T1 | ρ excl-2020 | ρ 2010– | ρ 2014–19 | ρ 2021–26 | 토큰 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| min_committee | could | cfnai | -0.251 | -0.37 | -0.13 | -0.415 | -0.548 | 83.0 |
| min_staff | ALL | vix | -0.333 | -0.361 | -0.393 | -0.197 | -0.235 | 539.0 |
| min_staff | would | vix | -0.229 | -0.32 | -0.269 | -0.262 | -0.014 | 327.0 |
| min_committee | would | cfnai | 0.257 | 0.304 | 0.27 | 0.327 | 0.278 | 719.0 |
| min_vote | would | cfnai | 0.208 | 0.258 | 0.041 | 0.156 | 0.305 | 119.0 |
| min_staff_desk | could | cfnai | 0.213 | 0.252 | 0.182 | 0.241 | 0.269 | 138.0 |
| min_participants | should | vix | -0.239 | -0.244 | -0.292 | -0.085 | -0.155 | 149.0 |
| min_vote | ALL | cfnai | 0.224 | 0.228 | 0.12 | 0.09 | 0.291 | 166.0 |
| min_staff_desk | could | vix | 0.211 | 0.222 | 0.147 | 0.125 | 0.405 | 138.0 |
| speech_chair | should | vix | -0.193 | -0.191 | -0.059 | -0.039 | -0.155 | 210.0 |

## X-F will/would + be appropriate

| 층위 | 단위 | 토큰 | ρ VIX T1 | ρ VIX excl-2020 | ρ CFNAI T1 | 제로 비율 T1 |
|---|---|---:|---:|---:|---:|---:|
| min_boilerplate | would+be+appropriate | 9 | -0.029 (p=0.7771) | 0.006 (p=0.9563) | 0.15 | 0.91 |
| min_committee | may+be+appropriate | 13 | -0.092 (p=0.3658) | -0.058 (p=0.5824) | -0.222 | 0.89 |
| min_committee | will+be+appropriate | 7 | -0.102 (p=0.3139) | -0.155 (p=0.1425) | -0.012 | 0.93 |
| min_committee | would+be+appropriate | 63 | 0.373 (p=0.0001) | 0.334 (p=0.0012) | 0.407 | 0.55 |
| min_participants | may+be+appropriate | 11 | 0.022 (p=0.8306) | 0.055 (p=0.6052) | -0.154 | 0.94 |
| min_participants | would+be+appropriate | 143 | 0.21 (p=0.037) | 0.154 (p=0.1443) | -0.053 | 0.23 |
| min_special | would+be+appropriate | 23 | 0.217 (p=0.1787) | 0.325 (p=0.0531) | 0.289 | 0.6 |
| min_staff_desk | would+be+appropriate | 8 | 0.054 (p=0.5978) | 0.089 (p=0.4028) | -0.015 | 0.95 |
| min_statement_quote | may+be+appropriate | 10 | -0.069 (p=0.5002) | -0.036 (p=0.7369) | -0.218 | 0.9 |
| min_statement_quote | will+be+appropriate | 43 | 0.257 (p=0.0101) | 0.283 (p=0.0065) | 0.358 | 0.61 |
| pc_chair | may+be+appropriate | 21 | -0.09 (p=0.4249) | -0.044 (p=0.7154) | -0.122 | 0.89 |
| pc_chair | will+be+appropriate | 105 | -0.053 (p=0.6378) | 0.01 (p=0.932) | 0.203 | 0.42 |
| pc_chair | would+be+appropriate | 38 | -0.135 (p=0.2322) | -0.072 (p=0.5491) | -0.016 | 0.69 |
| speech_chair | will+be+appropriate | 21 | -0.033 (p=0.7157) | -0.046 (p=0.6179) | 0.047 | 0.86 |
| speech_chair | would+be+appropriate | 11 | -0.043 (p=0.6368) | -0.025 (p=0.7871) | -0.01 | 0.94 |
| statement | may+be+appropriate | 10 | -0.077 (p=0.4419) | -0.037 (p=0.7308) | -0.216 | 0.9 |
| statement | will+be+appropriate | 43 | 0.235 (p=0.018) | 0.287 (p=0.0058) | 0.364 | 0.61 |

## X-G 선행성 (부록)

- excl-2020 CCF 피크(Pearson·Spearman 동시 유의) 20건; Granger text→macro q<.10 0건
