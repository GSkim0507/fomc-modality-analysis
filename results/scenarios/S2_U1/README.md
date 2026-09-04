# 시나리오 S2_U1 — statement + minutes committee layer × modal

> 성명서의 '확장판': 의사록 중 위원회 정책조치 서술만(인용된 성명서·지침 제외).

## 코퍼스 (T1 2014–2026)

| 층위 | 문서 | 토큰 | 6대 조동사 | per 1k |
|---|---:|---:|---:|---:|
| Statement | 101 | 41,906 | 770 | 18.37 |
| Minutes: Committee policy action | 99 | 62,833 | 958 | 15.25 |

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

- 층위(2) × 조동사 χ²=1113, Cramér's V=0.803

## X-E 구문 × 거시

- Kawamura 검정(총 조동사 밀도 × CFNAI, Spearman): minutes T1 ρ=0.009 (p=0.9261); minutes T2 ρ=-0.019 (p=0.8556); minutes T3 ρ=0.101 (p=0.2492); statement T1 ρ=-0.124 (p=0.2158); statement T2 ρ=-0.178 (p=0.0909); statement T3 ρ=-0.096 (p=0.2697)
- 반기별 유의(총 밀도): statement × vix H1 ρ=-0.405 (p=0.0043); statement × cfnai H2 ρ=-0.518 (p=0.0004); statement × vix H2 ρ=-0.472 (p=0.0014)
- 총 조동사 밀도 × VIX: minutes T1 ρ=0.122 (p=0.2303); minutes T2 ρ=0.098 (p=0.3542); minutes T3 ρ=0.097 (p=0.2695); statement T1 ρ=0.061 (p=0.5425); statement T2 ρ=0.045 (p=0.6729); statement T3 ρ=-0.116 (p=0.185)
- 전수 스크린 200행(층위 수준 집계): T1 BH q<.05 적중 6; **확정**(T1·T2 유의·동부호 + 2014–19/2021–26 반기 동부호) VIX 0건 / CFNAI 2건; T1에서만 유의(2020 의존) 0건; T1·T2 유의하나 반기 부호 불일치(시대 구성 효과) 3건

| 층위 | 단위 | 거시 | ρ T1 | ρ excl-2020 | ρ 2010– | ρ 2014–19 | ρ 2021–26 | 토큰 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| min_committee | could | cfnai | -0.251 | -0.37 | -0.13 | -0.415 | -0.548 | 83.0 |
| min_committee | would | cfnai | 0.257 | 0.304 | 0.27 | 0.327 | 0.278 | 719.0 |

## X-F will/would + be appropriate

| 층위 | 단위 | 토큰 | ρ VIX T1 | ρ VIX excl-2020 | ρ CFNAI T1 | 제로 비율 T1 |
|---|---|---:|---:|---:|---:|---:|
| min_committee | may+be+appropriate | 13 | -0.092 (p=0.3658) | -0.058 (p=0.5824) | -0.222 | 0.89 |
| min_committee | will+be+appropriate | 7 | -0.102 (p=0.3139) | -0.155 (p=0.1425) | -0.012 | 0.93 |
| min_committee | would+be+appropriate | 63 | 0.373 (p=0.0001) | 0.334 (p=0.0012) | 0.407 | 0.55 |
| statement | may+be+appropriate | 10 | -0.077 (p=0.4419) | -0.037 (p=0.7308) | -0.216 | 0.9 |
| statement | will+be+appropriate | 43 | 0.235 (p=0.018) | 0.287 (p=0.0058) | 0.364 | 0.61 |

## X-G 선행성 (부록)

- excl-2020 CCF 피크(Pearson·Spearman 동시 유의) 10건; Granger text→macro q<.10 0건
