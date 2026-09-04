# 시나리오 S5_U3 — minutes only (substantive layers) × modal + verb class

> 진단용: 의사록만으로 무엇이 보이는가.

## 코퍼스 (T1 2014–2026)

| 층위 | 문서 | 토큰 | 6대 조동사 | per 1k |
|---|---:|---:|---:|---:|
| Minutes: Desk/markets (staff) | 99 | 71,942 | 553 | 7.69 |
| Minutes: staff review & outlook | 99 | 249,885 | 539 | 2.16 |
| Minutes: participants' views | 99 | 223,992 | 2,756 | 12.3 |
| Minutes: Committee policy action | 99 | 62,833 | 958 | 15.25 |
| Minutes: special topics | 40 | 40,777 | 783 | 19.2 |

## X-A 구문 인벤토리

- 주 층위 Minutes: Desk/markets (staff): 조동사별 1위 단위 will→will/other (26%), would→would/other (20%), could→could/occurrence (18%), can→can/policy_action (40%), should→should/other (37%), may→may/occurrence (24%); 조동사 간 JSD 1.00–1.00

## X-D 층위 분업

- 층위(5) × 조동사 χ²=470, Cramér's V=0.145

## X-E 구문 × 거시

- Kawamura 검정(총 조동사 밀도 × CFNAI, Spearman): minutes T1 ρ=0.079 (p=0.4378); minutes T2 ρ=0.153 (p=0.1472); minutes T3 ρ=0.085 (p=0.334)
- 총 조동사 밀도 × VIX: minutes T1 ρ=0.066 (p=0.5132); minutes T2 ρ=-0.008 (p=0.9406); minutes T3 ρ=-0.065 (p=0.4615)
- 전수 스크린 1022행(층위 수준 집계): T1 BH q<.05 적중 21; **확정**(T1·T2 유의·동부호 + 2014–19/2021–26 반기 동부호) VIX 9건 / CFNAI 7건; T1에서만 유의(2020 의존) 14건; T1·T2 유의하나 반기 부호 불일치(시대 구성 효과) 8건

| 층위 | 단위 | 거시 | ρ T1 | ρ excl-2020 | ρ 2010– | ρ 2014–19 | ρ 2021–26 | 토큰 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| min_committee | would/copular_adj | vix | 0.487 | 0.54 | 0.422 | 0.123 | 0.4 | 126 |
| min_participants | would/activity | vix | 0.468 | 0.489 | 0.278 | 0.312 | 0.397 | 158 |
| min_committee | would/aspectual | vix | 0.475 | 0.422 | 0.271 | 0.027 | 0.098 | 116 |
| min_committee | would/existence | cfnai | 0.425 | 0.401 | 0.38 | 0.6 | 0.336 | 52 |
| min_committee | would/mental | cfnai | -0.479 | -0.398 | -0.407 | -0.285 | -0.42 | 71 |
| min_staff | would/policy_action | vix | -0.351 | -0.394 | -0.352 | -0.155 | -0.095 | 58 |
| min_committee | could | cfnai | -0.251 | -0.37 | -0.13 | -0.415 | -0.548 | 83 |
| min_staff | ALL | vix | -0.333 | -0.361 | -0.393 | -0.197 | -0.235 | 539 |
| min_participants | would/existence | cfnai | 0.344 | 0.342 | 0.268 | 0.376 | 0.352 | 93 |
| min_staff | would | vix | -0.229 | -0.32 | -0.269 | -0.262 | -0.014 | 327 |
| min_participants | would/policy_action | vix | -0.268 | -0.319 | -0.324 | -0.323 | -0.11 | 152 |
| min_committee | would | cfnai | 0.257 | 0.304 | 0.27 | 0.327 | 0.278 | 719 |

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

## X-G 선행성 (부록)

- excl-2020 CCF 피크(Pearson·Spearman 동시 유의) 14건; Granger text→macro q<.10 0건
