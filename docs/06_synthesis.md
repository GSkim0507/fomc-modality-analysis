# 06. 종합 분석 — 실험 결과 × 선행연구 × 추가 자료

> 실험 스크립트: `experiments/00–05`, 표: `results/tables/`, 그림: `results/figures/`. 모든 수치는 2014-01-01 ~ 2026-04-29, 회의 후 성명서가 아닌 4개 문서(2019-10-11 시행 성명, 2020-03-31 FIMA, 2020-08-27·2025-08-22 프레임워크 발표) 제외 후 값.

## 0. 코퍼스 (2014–2026)

| 장르 | 문서 | 토큰 | 문장 | 6대 조동사 | /1k 토큰 |
|---|---|---|---|---|---|
| Statement | 101 | 47,351 | 1,816 | 780 | 16.5 |
| Minutes | 99 | 871,758 | 28,473 | 7,081 | 8.1 |
| Press conference | 80 | 697,340 | 35,277 | 13,221 | 19.0 |
| Chair speech | 124 | 313,299 | 13,870 | 3,507 | 11.2 |
| **계** | **404** | **1,929,748** | **79,436** | **24,589** | 12.7 |

장르 × 조동사(계수): Statement will 612 / would 49 / could 50 / can 4 / should 38 / may 27. Minutes would 3,556 · could 1,659 (will 887). Press conf will 4,832 · would 3,911 · can 1,992. Speech will 1,227 · may 439.

추출 검증(저자 코딩 60문장 표본): 후행 동사 식별 정확 56/60(≈93%; 오류는 인용부호·긴 병렬문), 의미 유형 휴리스틱 일치 ≈90%(주어 유형 개선 후).

## 1. 실험 A — 후행 동사 전수 분석 (RQ1)

### 1.1 조동사별 후행 동사 (전 장르)
| 조동사 | 상위 후행 동사(빈도) | 유의하게 끌리는 동사(collexeme, Fisher −log10 p) | 유의하게 밀리는 동사 |
|---|---|---|---|
| will (7,558) | be 1229, continue 608, take 445, have 269, see 186, do 177, assess 171 | **continue**(2.0×, 90), take(48.7), **assess**(2.4×, 40.9), **monitor**(26.3), watch(22.8) | say(−31), expect(−18.5), lead, affect |
| would (8,172) | be 1785, **say 694**, continue 278, like 235, take 214, expect 164 | **say**(2.2×, 145), **like**(3.0×, 111), be(40.7), expect(36.8), want(33.9), hold | do(−26.7), see(−24.8), impede |
| could (3,307) | be 382, **impede 162**, lead 92, have 91, follow 81, affect 81, help 78 | **impede**(6.9×, 124), follow(4.6×), lead(4.2×), pose(5.2×), talk, affect | say(−38.7), continue(−29), be(−21), take |
| can (2,651) | be 202, do 200, see 115, say 91, give 68, tell 60 | **do**(3.6×, 62.8), "everything"(*can't do everything*), tell, give, see, find | **be**(−50), continue(−23.6), remain |
| should (1,351) | be 191, **help 93**, continue 40, take 33, do 29, see 26 | **help**(4.2×, 31.9), interpret(13×), affirm(18×), note, acknowledge, understand | say(−15.7), be, depend, warrant |
| may (1,550) | be 434, **warrant 64**, have 39, need 34, contribute 33 | be(1.6×, 27.2), **warrant**(4.9×, 26.7), authorize(14.6×; 시행 노트의 허가), contribute(6.8×), edge | continue(−15), do, look |

### 1.2 성명서만 (n=780)
- will(612): **continue 125, take 123, assess 72**, be 55, expand 34, monitor 32, depend 28, warrant 21 → "절차적 약속(procedural commitment)" 동사군: *will continue to monitor / will take into account / will (carefully) assess / will continue reducing*.
- would(49): **be 46** ("would be prepared"), continue 2, reduce 1.
- could(50): **impede 46**, pose 4.
- can(4): be, find(*More information can be found*).
- should(38): **help 21**, maintain 6, promote 6 ("should help maintain accommodative financial conditions", "should maintain downward pressure … should promote a stronger recovery").
- may(27): **warrant 15**, be 10 ("may … warrant keeping the target …", "may be appropriate").
→ 성명서에서 조동사별 후행 동사 분포 간 JSD는 0.69–1.0(최대 1)로 **거의 완전 분리**; 전 장르 합산에서는 0.20(will–would)–0.46 수준. 성명서의 조동사는 사실상 하나의 구문(construction)에 고정되어 있다.

### 1.3 의미 부류(Biber 7범주 + 정책행동)
- could → **causative** 비율이 두드러짐(전 장르 21.8%, Minutes 29%, 성명서 100%: impede/pose/affect/lead): *위험이 목표 달성을 저해할 수 있다*는 **위험 조건절**의 전용 조동사.
- may → **existence(be)** 33%(성명서 36%) + causative 57%(warrant): 인식적 가능성 + "warrant".
- can → **activity/do** 24.6%, 존재 동사(be)는 강하게 회피(−50): 능력·행위의 조동사(기자회견 "we can't do everything", "you can see").
- will → existence 23%, activity 20%, mental 12%(assess/monitor/see), aspectual 10%(continue): 위원회의 절차적 행위.
- would → existence 27%, communication 12.7%(*I would say*): 완곡 화행 표지.
- should → activity 20.5%, mental 13.8%; 성명서에서는 **help**(epistemic expectation, "정책은 ~에 도움이 될 것") 57%.

## 2. 실험 B — 6대 조동사 시계열 (RQ2)

### 2.1 성명서(101회) Mann–Kendall + Sen slope
| 조동사 | 밀도(/1k) 추세 | 점유율 추세 | 초기(2014–16) → 말기 평균 |
|---|---|---|---|
| will | **추세 없음**(p=.21, τ=−.09) | **감소**(p<.0001, τ=−.32) | 밀도 12.7→12.4 ; 점유율 .79→.66 |
| would | 증가(τ=+.57) | 증가(τ=+.57) | 0 → 2.8/1k ; 0 → .155 |
| could | 증가(τ=+.56) | 증가(τ=+.56) | .18 → 2.8 ; .01 → .155 |
| can | 없음 | 없음 | ≈0 |
| should | 감소(τ=−.41) | 감소(τ=−.43) | 2.1 → 0 |
| may | 약한 감소(p=.015) | 약한 감소 | .88 → .67 |

→ **"will 감소"는 밀도가 아니라 점유율의 감소**: would/could 유입에 따른 구성 효과 + 성명서 길이 축소(839→340토큰)로 문서당 빈도만 감소.

### 2.2 변화점(PELT, 점유율)
| 조동사 | 변화점(회의일) | 전→후 평균 | 대응 사건·문장 |
|---|---|---|---|
| should | **2017-06-14** | .130 → .000 | 정상화 계획 부록(2017-06-14) 회의에서 재투자 문장 삭제 |
| would | **2020-09-16** | .002 → .151 | 새 프레임워크(2020-08-27) 직후 첫 회의에 "would be prepared … could impede" 도입 |
| could | **2020-09-16** | .004 → .146 | 동일 문장 |
| will | 2015-12-16 (.72→.94), **2020-09-16** (.94→.68) | | 이륙(liftoff) 시 will 3문장 포워드 가이던스 도입(20회 지속) ; 2020-09 would/could 유입 |
| may | 2015-12-16 (.10→0), 2019-01-30/07-31, 2023-03-22/2024-01-31 | | "may … warrant"(2014-03~2015-10) 삭제 ; "will be patient … may be appropriate"(2019-01~06) ; "additional policy firming may be appropriate"(2023-03~12) |
| can | 2014-09/2015-03, 2020-01/04 | | 산발("can be patient" 2014-12~2015-01, 2020 시행 문구) |

→ 6개 조동사 전부에서 변화점이 **식별 가능한 정책 사건·문장 편집**과 일치.

### 2.3 지속성(AR(1))과 반감기
| 조동사 | ρ(점유율) | 반감기(회의) | 해석 |
|---|---|---|---|
| could | .97 | 23.4 | 2020-09 이후 46회 연속 동일 문장 |
| would | .93 | 10.1 | 동일 |
| should | .90 | 6.8 | 21회 지속 후 삭제 |
| will | .85 | 4.3 | 문장 교체가 잦으나 총량 안정 |
| may | .67 | 1.7 | 단기 포워드 가이던스 문구 |
| can | .43 | .8 | 사실상 무작위 |

### 2.4 타 장르 추세(밀도, 2014–2026)
- Minutes: will 감소(τ=−.40, 1.49→0.77/1k), would 감소(−.18), could 증가(+.18), should 감소(−.31).
- Press conf: **can 증가**(+.21, 1.95→2.92), should 감소(−.15); will/would 무추세.
- Speech: will 증가(+.20), should 감소(−.24).
→ **should는 4장르 모두에서 감소**(Leech 2003·Millar 2009의 일반 영어 should 감소와 부합) ; would/could 증가는 성명서 고유(정형 문장) ; can 증가는 기자회견 고유(Powell의 구어체).

### 2.5 준양태 대체(성명서)
*be going to / need to / have to* = 0. *be expected to*(2016–17 ≈2/문서)·*be likely to*는 소멸, *be prepared to*는 2020-09부터 1/문서 고정, *expect(s)/anticipate(s)* 3.1(2014)→0(2025–26)으로 감소. → will의 밀도 유지 + 기대동사 감소 = 성명서가 "전망 서술"에서 "절차적 약속 서술"로 이동.

## 3. 실험 C — 정형성·편집 이벤트·구문 생존 (RQ3)

### 3.1 정형 문장(≥5회 반복, 조동사 포함) — 핵심 표
| 회수 | 존속 | 조동사 | 문장 |
|---|---|---|---|
| 52 | 2014-03-19 → 2020-07-29 | will | This assessment **will take into account** a wide range of information… |
| 46 | 2020-09-16 → 2026-04-29 | will | …the Committee **will continue to monitor** the implications of incoming information… |
| 46 | 2020-09-16 → 2026-04-29 | would, could | The Committee **would be prepared** to adjust… if risks emerge that **could impede**… |
| 46 | 2020-09-16 → 2026-04-29 | will | The Committee's assessments **will take into account** a wide range of information… |
| 21 | 2014-10-29 → 2017-05-03 | should | This policy… **should help maintain** accommodative financial conditions. |
| 20 | 2015-12-16 → 2018-05-02 | will | …economic conditions **will evolve** in a manner that **will warrant** only gradual increases… |
| 20 | 2015-12-16 → 2018-05-02 | will | …the actual path of the federal funds rate **will depend** on the economic outlook… |
| 14 | 2014-03-19 → 2015-10-28 | may | …economic conditions **may**, for some time, **warrant** keeping the target… |
| 13 | 2023-02-01 → 2024-07-31 | will | …the Committee **will continue reducing** its holdings… |
| 6 | 2014-01-29 → 2014-09-17 | should | …holdings… **should maintain** downward pressure… **should promote** a stronger economic recovery… |
| 5 | 2023-06-14 → 2023-12-13 | may, will | …additional policy firming that **may be appropriate**… the Committee **will take into account**… |

### 3.2 정형 문장 비중
성명서 조동사 토큰 중 정형 문장(≥3회 반복) 안에 있는 비율: will 0.68–1.00(연도별), would 0.8–1.0, could 1.0, should 0.74–1.0, may 0.7–1.0. 2021 이후 **would/could는 100%가 한 문장**에서 나온다.

### 3.3 편집 이벤트(연속 성명서 간 조동사 문장 추가/삭제)
2014 20/23, 2015 11/12, **2016 0/1**, 2017 8/9, 2018 6/8, 2019 6/7, **2020 31/26**, 2021 10/11, 2022 5/6, 2023 7/7, 2024 6/7, 2025 5/5. → 편집은 국면 전환기(2014 테이퍼·2020 팬데믹/프레임워크)에 집중, 안정기(2016)에는 거의 없음.

### 3.4 생존·반감기(반감기 조작화 3종)
| 단위 | 지표 | will | would | could | can | should | may | 전체 |
|---|---|---|---|---|---|---|---|---|
| 구문(modal+V) 코호트 | KM 중위 생존(회의) | 3 | 2 | (4) | 1 | 1 | 1 | 3 |
| 구문 코호트 | 평균 존속 / 1회성 비율 | 7.9 / .40 | 16.3 / .33 | — | 1.5 / .5 | 4.8 / .63 | 4.5 / .50 | 7.9 / .41 |
| 구문 집합 | 보유율(retention) 반감기(회의) | **20.2** | ∞(24회 내 .95) | ∞(.91) | 1.0 | 6.1 | 4.0 | **17.8** |
| 조동사 문장 집합 | 보유율 반감기 | | | | | | | **6.4** (k=1 보유율 .81) |

해석: (i) 구문의 **분포는 이봉(bimodal)** — 40%는 1회성(그 회의의 결정 서술), 나머지는 수십 회 지속되는 정형 구문; (ii) 회의 t의 조동사 구문 집합은 평균 17.8회(≈2년)의 반감기로 유지되며, 문장 단위로는 6.4회(≈9개월); (iii) would/could 구문은 2020-09 이후 사실상 소멸하지 않음(반감기 ∞).

## 4. 실험 D — 사용 맥락과 장르 분업 (RQ4)

### 4.1 장르 × 조동사(χ²=4,638, df=15, V=.251) 표준화 잔차
| | will | would | could | can | should | may |
|---|---|---|---|---|---|---|
| Statement | **+24.0** | −13.1 | −5.4 | −8.7 | −0.7 | −3.2 |
| Minutes | −27.6 | **+24.8** | **+22.9** | −24.6 | +0.2 | +2.6 |
| Press conf | +12.1 | −7.3 | −13.4 | **+15.0** | −1.3 | −8.7 |
| Speech | +4.5 | −14.9 | −3.9 | +9.9 | +2.5 | **+14.7** |

### 4.2 맥락 특징(비율)
- **조건절 동반**: 성명서 would .94, could .92(단일 문장 효과); 기자회견 could .42, would .25; 연설 would .31.
- **간접 인용/내포(reported)**: Minutes should .70, would .64, could .43 — Minutes의 would는 *participants noted that … would*의 시제 일치(backshift); 성명서 will .24는 *expects that … will*의 내포.
- **부정**: 기자회견 can .15(*can't*), should .09, would .09; 성명서는 거의 0.
- **의문문**: 기자회견 could .26, should .20, can .15(기자 질문: *Could you…?*).
- **축약형**: 기자회견 will .28(*we'll*), would .09(*I'd*); 다른 장르 0.
- **주어**: 성명서 will 44% Committee, 23% 경제 변수; would 94% Committee; could 92% 관계절(*risks that could*); should 74% 경제/정책 변수(*policy should help*); may 63% 경제 변수. 기자회견 will/would 40–46% we/I, can 33% 인칭(you/they)+34% we/I. Minutes will 32% Committee, would/could 29–32% 경제 변수.

### 4.3 의미 유형(휴리스틱)
성명서: will = 46% 의지·약속(dynamic volitional, 주어 Committee) + 54% 예측(epistemic predictive, 주어 경제); would = 96% 조건·가정; could/may = 100% 인식적 가능성; should = 89% 인식적 기대(*should help*), 11% 의무(*should be patient* — 반대표 위원의 발언 인용). 전 장르: can = 능력 59% + 상황적 가능성 35%; would = 조건 40% + 간접인용 37% + 완곡 11%(*I would say*).

### 4.4 의장·정책 국면
- 의장 대조(성명서 Yellen vs Powell): χ²=111, V=.38 — Powell 시기 would/could 1.8/1.7 per 1k(Yellen 0.05/0.15), should 0(Yellen 1.8). 기자회견에서는 V=.09로 작음(Powell can 3.1 vs Yellen 1.9/1k). → 성명서 차이는 **의장 문체가 아니라 프레임워크 문장**의 효과(2020-09 이전 Powell 성명서는 Yellen과 동일 패턴).
- 정책 국면(성명서 점유율 %): ZLB/테이퍼 will 74·should 15·may 8 → 인상기 I will 93 → 팬데믹 will 80·would 10·could 8 → 인상기 II·정점 유지·인하기 will 65–69·would/could 13–17. 즉 국면보다 **프레임워크 시기(2020-09 전/후)**가 결정적.

## 5. 세미나 질문에 대한 답
| 질문 | 답 |
|---|---|
| 왜 2018년 이후 should가 사라졌나? | should는 성명서에서 오직 재투자 정책 문장(*should help maintain…*, 2014-10~2017-05, 21회)과 그 전신(*should maintain downward pressure*)에만 쓰였다. 2017-06-14 정상화 계획 채택 회의에서 이 문장이 삭제되면서 should가 소멸했다(변화점 2017-06-14, 이후 0). 4장르 모두에서 should 밀도가 감소하는 일반적 경향(Leech 2003)도 배경에 있다. |
| 왜 will은 점점 감소하나? | 밀도(/1k)는 감소하지 않는다(MK p=.21). 감소하는 것은 (a) 점유율 — 2020-09 프레임워크 문장으로 would/could가 회의당 각 1건씩 상시 유입되어 분모가 커졌고, (b) 문서당 빈도 — 성명서 길이가 839→340 토큰으로 줄었기 때문이다. will의 구문은 계속 교체되지만(2015-12 이륙 문장군, 2020-09 프레임워크 문장군, 2022 대차대조표 축소 문장, 2024 인하 국면 문장) 총량은 안정적이다. |
| 왜 could/would가 늘었나? | 단 하나의 문장 — *The Committee would be prepared to adjust the stance of monetary policy as appropriate if risks emerge that could impede the attainment of the Committee's goals* — 이 2020-09-16부터 46회 연속 포함되었기 때문이다(2021 이후 would/could의 100%). 이는 2020-08 프레임워크 개정 직후 도입된 **조건부 대응 약속(conditional commitment)** 구문으로, would(가정적 의지) + could(위험의 인식적 가능성)가 하나의 if-절 구조 안에 결합되어 있다. |
| 왜 can은 항상 낮은가? | can은 능력·행위(dynamic)의 조동사로 주어가 행위자(we/you/they)일 때 쓰이며(기자회견 can 주어의 67%가 인칭), 위원회의 예측·약속을 3인칭으로 서술하는 성명서 장르에서는 구조적으로 자리가 없다(성명서 4건: *can be patient*, *can be found*). 반면 기자회견에서는 2014–2026 동안 유일하게 증가한 조동사다(Powell의 *we can't…*, *you can see*). |
| 각 조동사는 어떤 상황에서 쓰이나? | will = 위원회의 절차적 약속(continue/take into account/assess/monitor) + 경제 예측; would = 조건부 약속(성명서)·간접인용 시제 일치(의사록)·완곡 화행(*I would say*, 기자회견); could = 위험 조건절의 인식적 가능성(impede/pose/lead/affect); can = 능력·허용(기자회견·연설); should = 정책 효과에 대한 인식적 기대(*should help*)와 의무(*we should do*, 기자회견); may = 인식적 가능성(*may be appropriate*, *may warrant*)과 시행 노트의 허가(*may authorize/delegate*). |

## 6. 선행연구와의 연결
- **Kawamura et al. (2019)**: 그들은 양태 표현 빈도가 경기와 역상관한다는 "전략적 모호성"을 보였다. 우리 결과는 FOMC 성명서의 양태 변화가 경기가 아니라 **제도적 프레임워크 사건**에 의해 계단형으로 결정됨을 보인다 — 양태는 "모호성의 양"이 아니라 "약속의 구조(조건부/무조건부)"를 부호화한다. 또한 그들이 강조한 "부정 정보 + 양태"의 결합은 우리의 could-impede 구문(위험 + 가능성)에서 정형화된 형태로 재발견된다.
- **Resche (2015)**: hedging은 어휘 목록으로 환원되지 않는다는 주장에 동의하되, 후행 동사·주어·조건절을 함께 계량하면 구문 단위의 hedging 전략(would be prepared … if … could impede)이 정량적으로 포착됨을 보인다. 4.5–5.8%의 hedge 비율보다 "어떤 구문이 몇 회의 동안 유지되는가"가 더 많은 정보를 담는다.
- **Meade & Acosta (2015), Ehrmann & Talmi (2020)**: 성명서가 이전 성명서를 편집해 만들어진다는 관찰(문장 유사도)을 조동사 수준에서 확인 — 조동사 문장 보유율 k=1에서 .81, 반감기 6.4회.
- **Leech (2003), Millar (2009)**: 일반 영어에서 should/may의 감소, will의 안정은 우리 4장르 데이터에서도 재현된다(should 4장르 모두 감소). 그러나 성명서의 would/could 증가는 언어 변화가 아니라 편집 결정의 산물이다.
- **Campbell et al. (2012)의 Odyssean/Delphic 포워드 가이던스**: will(무조건적 절차 약속)과 would…if(조건부 약속)의 구분은 이 이분법의 문법적 대응물이다.

## 7. 논문 주장(확정)
1. **편집된 정형성(edited formulaicity)**: 성명서 조동사 토큰의 70–100%는 3회 이상 반복되는 정형 문장 안에 있으며, 조동사 빈도의 모든 변화점은 특정 정형 문장의 도입·삭제와 일치한다.
2. **구문 고정성**: 성명서에서 각 조동사는 사실상 하나의 후행 동사 구문에 결합한다(JSD .69–1.0); 전 장르에서도 조동사별 collexeme이 뚜렷이 분리된다(could-impede 6.9×, would-say 2.2×, can-do 3.6×, should-help 4.2×, may-warrant 4.9×, will-continue 2.0×).
3. **반감기**: 조동사 구문 집합의 보유율 반감기는 17.8회의(≈2.2년), 문장 단위 6.4회의; 2020-09 이후 도입된 would/could 구문은 관측 기간 내 소멸하지 않았다.
4. **장르 분업**: will(성명서·약속), would/could(의사록·간접인용/조건), can(기자회견·능력), may(연설·인식적 가능성) — χ² V=.25; 성명서 내 의장 차이(V=.38)는 프레임워크 문장으로 설명된다.
5. 세미나의 네 관찰은 각각 하나의 편집 사건으로 환원된다(§5).
