---
title: "FOMC 조동사 구문 실험 결과보고서 v3"
subtitle: "코퍼스 언어학 실험군(L1–L9)과 계량경제 실험군(E1–E9), 코퍼스 정의 24종 × 분석 단위 3종 = 72 run, 2014–2026"
date: "2026-09-04 · Phase 14–15"
---

# 0. 요약 (Executive Summary)

**목적.** 연구질문은 하나다: *FOMC 커뮤니케이션의 조동사(구문)는 경제 상황을 설명하는가?* 이 보고서는 정제된 v3 코퍼스(장르 × 귀속 층위 18종)로 **가능한 모든 코퍼스 조합**(성명서 포함/제외 × 의사록 없음/위원회 층/실질 층 × 기자회견 없음/의장 × 연설 포함/제외 = 23 + 미정제 1 = 24) × **분석 단위 3종**(조동사 / 구문 / 동사 부류) = 72 run에 대해, 코퍼스 언어학 실험군 9블록(L1–L9)과 계량경제 실험군 9블록(E1–E9)을 같은 코드로 실행하고, 사전에 명시한 가설 H1–H5를 run마다 판정한 결과다. 본문은 권장 조합 **C11 = S4(4장르 정제) × U2(구문)**을 기준으로 서술하고, §6–7에서 72 run 전체를 비교한다.

**데이터.** 404문서·1.93M 토큰(2014-01 ~ 2026-04). 기자회견은 화자 분절(의장/기자/진행자), 의사록은 섹션 귀속(스태프·참가자·위원회·인용 성명서·지침·표결·규정문)으로 나눴다. 6대 조동사 토큰: 성명서 770, 의사록 실질 층 5,589, 의장 기자회견 10,686, 연설 3,203. 검증: 의사록 안 인용 성명서와 성명서 원문의 Jaccard 중앙값 0.94.

**가설 판정 (주 run C11_U2).**

| 가설 | 판정 | 핵심 근거 |
|---|---|---|
| H1 편집 가설: 성명서 조동사 변화 = 정형문 편집의 계단 | **지지** | 구문 변화점 25개 중 17개(68%)가 정책 사건 ±1회의 이내; 구문 보유율 반감기 16.8회의; 각 계단에 책임 문장 1개 |
| H2 층위 분업 가설 | **지지** | 층위 × 조동사 χ² = 6,801 (df 35), Cramér's V = .259; 다항로짓 유사 R² = .163, 참가자 층 could 상대위험비 12.3 |
| H3 반경기 가설 (Kawamura) | **기각** | 어떤 층위의 총밀도도 CFNAI와 유의한 음의 관계 없음(수준·차분·2020 제외 모두); 의장 기자회견은 순경기(+) |
| H4 불확실성 가설 (비편집 층에서만) | **부분** | 확정 VIX 단위 8개 중 7개가 의사록 층(위원회 결정 서술·스태프), 성명서 층 1개(will+assess) |
| H5 선행성 가설 | **기각** | Granger text→macro q 최소 .36; 예측 회귀 64건 중 q<.10 0건 |

**72 run 판정 분포.** H1 지지 39 / 해당 없음 33(성명서 없는 조합) · H2 지지 60 / 해당 없음 12(단일 층위) · **H3 기각 72** · H4 지지 37 / 부분 26 / 기각 9 · H5 기각 64 / 지지 8(경계 사례).

**모든 조합에서 성립하는 것.** (i) 반경기 양태는 없다(72/72). (ii) 성명서가 포함된 모든 run(39/39)에서 계단은 정책 사건과 일치한다. (iii) 성명서만으로는 확정 거시 신호가 0–1개다. (iv) 선행성은 실질적으로 없다(예측 회귀 72 run 전부 0건). **조합에 따라 달라지는 것.** 의사록(특히 위원회 결정 서술 층)을 넣어야 CFNAI·VIX와의 확정 신호가 나타나고(U2: 1/0 → 3/5 → 7/6), 기자회견은 확정 신호보다 시대 구성·2020 의존 적중을 늘리며, 기자 발화·규정문을 제거하지 않은 미정제 조합은 인공물이 가장 많다(시대 구성 39).

**추천.** 주 조합 C11(S4) × 구문(U2), 비교 열 C02(S1 성명서만)·C06(S2 성명서 + 위원회 층). 결론 문장: *성명서의 조동사 변화는 정책 사건에 따른 정형문 편집의 계단이며(H1), 층위마다 조동사는 다른 일을 하고(H2), 조동사 총량은 경기와 무관하지만(H3 기각) 편집되지 않은 의사록 층의 특정 구문은 실물·불확실성과 공변한다(H4 부분). 선행지표는 아니다(H5 기각).*

---

# 1. 서론

## 1.1 연구질문
지도교수 미팅(2026-09-04)에서 논문의 질문은 하나로 좁혀졌다: 조동사(구문)가 경제 상황을 설명할 수 있는가, 없는가. 이 보고서는 그 질문을 다섯 개의 검정 가능한 가설로 풀고, 데이터 정제 이후 모든 실험을 처음부터 다시 수행한 결과를 실험 결과보고서 양식으로 정리한다.

## 1.2 가설

| 가설 | 진술 | 검정 블록 | 지지 기준 |
|---|---|---|---|
| H1 편집 | 성명서의 조동사 분포 변화는 정책 사건에 따른 정형문의 삽입·삭제로 설명된다 | L3·L5·E7 | PELT 변화점의 50% 이상이 정책 사건 ±1회의 이내 |
| H2 층위 분업 | 층위마다 조동사·구문 프로파일이 유의하게 다르다 | L2·L7 | χ² p < .001, Cramér's V ≥ .10 |
| H3 반경기 | 조동사 밀도는 실물 활동(CFNAI)과 음의 관계 (Kawamura et al. 2019) | E3·E9 | 총밀도 CFNAI 계수가 음·유의(T1과 2020 제외 모두); 차분에서만 성립하면 '부분' |
| H4 불확실성 | 조동사(구문) 밀도는 VIX와 양의 관계이며 편집되지 않은 층에서만 성립 | E4·E5 | 확정 VIX 단위 ≥ 1 이고 성명서 층 확정 0 → 지지; 성명서 층에도 있으면 '부분' |
| H5 선행성 | 텍스트 지표가 거시를 선행한다 | E6 | Granger text→macro 또는 예측 회귀에서 BH q < .10 ≥ 1건 |

## 1.3 보고서 구성
§2 데이터, §3 설계·통계 방법, §4 결과 A(코퍼스 언어학: 정규화 빈도·신뢰구간·분산, 키니스·효과크기, 연어·collexeme·KWIC, 통시 검정, 정형성, 문법 맥락, 다항로짓), §5 결과 B(계량경제: 기술통계, 스펙별 회귀표(계수·HAC SE·별표·N·R²), 구문 회귀, 전수 스크린과 FDR·ledger, Granger·예측 회귀, 사건 연구, 강건성, Kawamura 재현), §6 72 run 비교, §7 가설 판정, §8 논의, §9 한계. run별 전체 표·그림은 부록 페이지(`run_<id>.html`)에 있다.

---

# 2. 데이터

## 2.1 코퍼스 구축과 층위
연준 이사회 웹사이트의 4장르(회의 후 성명서, 의사록, 의장 기자회견 녹취, 의장 연설) 2010-01 ~ 2026-04, 535문서. 분석 창 T1 = 2014-01 ~ 2026-04(비회의 성명서 4건 제외 후 404문서). 층위(layer)는 장르 × 귀속이다.

| 층위 | 정의 | 분석 포함 |
|---|---|---|
| statement | 성명서 본문("Voting for…" 문단 제외) | 기본 |
| min_staff_desk / min_staff | 의사록 데스크·시장 보고 / 스태프 경제·금융 리뷰와 전망 | 실질 층 |
| min_participants | 참가자 견해 섹션 | 실질 층 |
| min_committee | 위원회 정책조치 섹션의 심의·결정 서술(인용 성명서·지침·삽입 문서 제외) | 실질 층 |
| min_special | 특별 주제 섹션 | 실질 층 |
| min_statement_quote / min_directive_quote / min_vote / min_boilerplate / min_front_matter | 인용 성명서 전문 / 지침·삽입 문서 / 표결·행정 / 1월 규정문 / 참석자 명단 | 제외(미정제 조합에서만 포함) |
| pc_chair / pc_journalist / pc_moderator | 기자회견 의장 발화 / 기자 질문 / 진행자 | 의장만 |
| speech_chair | 의장 연설 본문(제목 블록·참고문헌·각주 제거) | 포함 |

## 2.2 정제 규칙과 무결성 검사
인코딩 복구(ftfy), 헤더·푸터·페이지 마커·각주("Return to text")·사이트 내비게이션·연설 참고문헌 제거; 기자회견 화자 마커(대문자 이름 + 마침표/콜론, 대문자 비율 ≥ 70%)로 턴 분절; 의사록 소제목 카탈로그로 섹션 귀속, 따옴표 블록으로 인용 성명서·지침 분리, ALL-CAPS 제목의 삽입 문서 처리, "Voting for/against"는 어떤 상태에서도 표결 층으로 강제 전환. QA(`results/qa/QA_report.md`): 중복 문서 0, 날짜 오류 0, 인코딩 잔재 3문장, 의사록 99건 전부 핵심 5섹션 존재, 기자회견 80건 전부 의장 마커 인식(기자 168명 식별), 인용 성명서–원문 Jaccard 중앙값 0.94. 추출은 v2와 동일 규칙(spaCy 의존구문, 코퓰러 be 보어 해소; 저자 표본 정확도 head 93%·의미유형 90%). **미완**: 화자·층위 사람 검증 표본, 200문장 2인 코딩.

## 2.3 코퍼스 기술 (L1)
{{tbl:C11_U2:corpus}}
{{tbl:C11_U2:modal_pmw}}
**읽기.** 밀도는 층위에 따라 10배 차이가 난다(스태프 리뷰 2,157 pmw vs 의장 기자회견 20,045 pmw). 성명서 780 vs 기자회견 13,000이라는 원시 개수 차이는 정규화하면 사라지고, 남는 것은 담화 기능의 차이다: 사실 서술(스태프) → 심의(참가자 12,304) → 결정(위원회 15,247) → 대화(의장 20,045) 순으로 조동사가 많아진다. 분산 DP는 성명서 will(≈ 0.1대)처럼 모든 문서에 고르게 퍼진 조동사와, 성명서 can·should처럼 소수 문서에 몰린 조동사를 구분한다.

## 2.4 거시 변수 (E1)
{{tbl:C11_U2:descriptives}}
CFNAI-MA3(회의 월 −2)는 평균 −0.09, SD 1.10(2020-04 −7.55 포함), AR(1) .25; VIX 회의 전 28일 평균은 평균 18.3, SD 6.7, AR(1) .76. 텍스트 총밀도의 AR(1)은 층위별로 .3–.5 수준이라 HAC 표준오차가 필요하다. 지표 선택 근거는 `docs/10`(여섯 조건: 회의 단위 정렬, 실시간성, 실물/불확실성 분리, Kawamura 비교가능성, 텍스트 지표의 순환성 회피, 반응함수 변수 회피).

---

# 3. 방법론과 학술적 근거

이 절은 "무엇을 했는가"와 함께 "왜 그 방법이어야 하는가"를 문헌으로 뒷받침한다. 각 표의 마지막 열이 근거 문헌이며, 전체 서지는 §3.9에 있다.

## 3.1 설계 원칙: 다중 코퍼스 정의와 사전 가설
- **다중 코퍼스 정의(24종) × 단위(3종)를 같은 코드로 실행**한다. 코퍼스 정의(의사록 포함 여부 등)와 단위 선택은 연구자의 재량 변수이므로, 한 조합만 보고하면 결론이 그 선택에 얼마나 의존하는지 알 수 없다. 이는 심리학·경제학에서 표준화된 **다중우주 분석**(Steegen et al., 2016)과 **명세 곡선 분석**(Simonsohn, Simmons & Nelson, 2020)의 논리를 코퍼스 설계에 적용한 것이다: 재량 선택의 전 조합을 열거하고 결과가 조합에 따라 어떻게 바뀌는지를 그 자체로 결과로 보고한다.
- **가설을 사전에 명시하고 판정 규칙을 코드로 고정**한다(§1.2). 판정 규칙이 run마다 동일하므로 조합 간 비교가 가능하고, 결과를 본 뒤 기준을 바꾸는 유연성(garden of forking paths; Gelman & Loken, 2014)을 차단한다.
- **주 run(C11_U2)**을 서술의 기준으로 삼되, 모든 주장은 §6–7의 72 run 분포로 강건성을 확인한다.

## 3.2 코퍼스 구축과 층위(장르 × 귀속)
| 무엇을 | 왜 | 근거 |
|---|---|---|
| 4장르(성명서·의사록·기자회견·연설)를 하나의 코퍼스로 모으되 장르를 분석 변수로 유지 | 언어 변이는 레지스터(register)에 따라 체계적으로 달라지며(Biber, 1988), 조동사는 레지스터 민감도가 큰 자질이다(Biber et al., 1999, ch. 6). 장르를 섞어 세면 구성비 효과가 결과를 지배한다 | Biber 1988; Biber et al. 1999 |
| 기자회견을 화자(의장/기자/진행자)로 분절 | 기자의 질문은 연준의 발화가 아니다. v2 감사에서 could의 48%, might의 50%가 기자 발화였다. 화자 귀속 없는 대화 코퍼스는 발화 주체를 잘못 지정한다 | 대화 코퍼스의 화자 주석 관행(Love et al., 2017) |
| 의사록을 섹션(스태프/참가자/위원회/인용문/규정문)으로 귀속 | 의사록은 서로 다른 화자 집단의 텍스트가 정해진 순서로 병치된 문서다. 스태프 리뷰(사실 서술), 참가자 견해(심의), 위원회 정책조치(결정 서술)는 담화 기능이 다르고, 위원회 섹션에는 성명서 전문이 인용되어 성명서와 이중 집계된다. 심의를 측정한 경제학 연구는 이 구조를 전제로 한다 | Hansen, McMahon & Prat 2018 |
| 성명서를 편집되는 정형문으로 취급(문장 재사용·삽입·삭제 추적) | 성명서는 직전 성명서를 수정해 작성되며 문구 변화 자체가 시장 정보다 | Acosta & Meade 2015; Ehrmann & Talmi 2020 |
| 정제: 각주·내비게이션·참고문헌·규정문 제거, 인코딩 복구 | 웹 스크랩 텍스트의 비본문 요소가 빈도를 왜곡한다(1월 의사록 규정문에서 shall 199·must 87개) | 코퍼스 구축 관행(Brezina, 2018, ch. 1) |

## 3.3 분석 단위: 조동사가 아니라 구문
| 무엇을 | 왜 | 근거 |
|---|---|---|
| 기본 단위 = 조동사 + 서술어(구문); 코퓰러 be는 보어로 해소(will be appropriate) | 조동사의 의미(인식·의무·역동)는 공기하는 주어·동사·조건·인용에 의해 결정된다. 조동사만 세면 will continue(절차 약속)와 will be appropriate(가이던스)가 한 수치로 합쳐진다 | Coates 1983; Palmer 1990; Nuyts 2001 |
| 구문–서술어 연관을 collexeme 통계로 측정 | 구문과 어휘 충전물의 유인·배척은 단순 빈도가 아니라 기대빈도 대비 편차로 측정해야 한다 | Stefanowitsch & Gries 2003; Gries & Stefanowitsch 2004 |
| 서술어 의미 부류(활동·소통·정신·인과·사건·존재·상태·정책행동·코퓰러) | 동사 의미 부류는 레지스터 변이의 표준 기술 범주다 | Biber et al. 1999, ch. 5 |
| 단위 축 3종(조동사/구문/부류)을 모두 실행 | 단위 선택이 결과를 바꾸는지 보여 주기 위해(§3.1) | Steegen et al. 2016 |

## 3.4 정규화와 분산
| 무엇을 | 왜 | 근거 |
|---|---|---|
| 빈도를 pmw(백만 단어당)와 per 1k로 정규화하고 Poisson 95% CI를 붙임 | 층위 크기가 780 vs 13,000처럼 다르므로 원시 개수는 비교 불가; 신뢰구간은 작은 층위의 불확실성을 드러낸다 | Biber et al. 1999; Brezina 2018, ch. 2 |
| 문서 간 분산 DP | 총빈도가 같아도 소수 문서에 몰린 자질(성명서 can·should)과 고르게 퍼진 자질(will)은 다른 현상이다 | Gries 2008 |
| 점유율(N2)은 성명서 계단에, 문서당 수(N3)는 성명서 전용 | 성명서는 길이 자체가 편집 결과이므로 밀도와 원시 수를 모두 봐야 한다 | Acosta & Meade 2015 |

## 3.5 코퍼스 언어학 실험군 (L1–L9)
| 블록 | 방법 | 왜 이 방법인가 | 근거 |
|---|---|---|---|
| L1 | pmw·CI·DP·연도별 빈도 | 기술 통계의 표준 형식; 이후 모든 추론의 분모 | Biber et al. 1999; Gries 2008 |
| L2 | 키니스: log-likelihood G², log ratio, %DIFF, BH q; 층위 × 조동사 χ²·Cramér's V·표준화 잔차 | 두 (하위)코퍼스 간 빈도 차의 유의성은 LL, 효과 크기는 log ratio/%DIFF로 분리해 보고해야 한다(유의성만으로는 큰 코퍼스에서 모든 것이 유의). χ²·V는 분업의 전체 강도, 잔차는 셀별 방향 | Rayson & Garside 2000; Hardie 2014; Gabrielatos 2018; Cramér 1946 |
| L3 | Mann–Kendall τ·Sen 기울기; PELT 변화점; 계단 그림 | 회의 단위 빈도는 비정규·자기상관 계열이므로 분포 가정 없는 순위 기반 추세 검정이 적합하다. 정형문의 삽입·삭제는 점진적 추세가 아니라 단절이므로 변화점 탐지가 맞는 도구이며, PELT는 최적 분할을 선형 시간에 찾는다 | Mann 1945; Kendall 1975; Sen 1968; Killick, Fearnhead & Eckley 2012 |
| L4 | 서술어 프로파일, distinctive collexeme(Fisher exact), JSD, 의미 부류, KWIC | §3.3. JSD는 조동사 간 서술어 분포의 거리를 대칭·유계로 측정한다. KWIC 용례는 코퍼스 언어학 보고의 필수 요소 | Gries & Stefanowitsch 2004; Lin 1991; Sinclair 1991 |
| L5 | 정형 문장 비율, 구문 코호트 Kaplan–Meier, 보유율 반감기, 편집 이벤트 | 정형 표현의 "수명"은 생존 분석의 대상이다(우측 중도절단: 마지막 회의까지 살아 있는 구문). 보유율은 집합 수준의 지속성을 하나의 수치로 요약한다 | Kaplan & Meier 1958; Wray 2002; Biber & Barbieri 2007 |
| L6 | 부정·수동·조건·인용·의문·주어 유형·의미 유형; χ² | 조동사 의미 해석의 결정 요인들(공기 자질)을 층위별로 계량화한다 | Coates 1983; Palmer 1990; Hyland 1998 |
| L7 | 다항 로짓(기준 will) | 층위 효과를 시기·주어·조건·인용을 통제한 뒤 확인하기 위한 다범주 반응 모형 | Agresti 2013 |
| L8·L9 | be appropriate 계열; 의장·국면 대조 χ² | 교수님 질문(will/would)에 대한 직접 검정; 개인 문체 vs 제도 편집의 분리 | — |

## 3.6 거시 지표 (요약; 전문은 docs/10)
실물 활동 = CFNAI 3개월 이동평균(회의 월 −2, 실시간 래그), 불확실성 = VIX(회의 전 28일 평균). 선택 근거 여섯 가지: 회의 단위 정렬 가능, 실시간성, 실물/불확실성 분리, Kawamura et al.(2019)과의 비교가능성(경기지수 + VIX), 텍스트 기반 지표(EPU·MPU)의 순환성 회피, 연준 반응함수 변수(실업률·인플레이션)의 기계적 상관 회피. 근거: Stock & Watson 1999; Evans, Liu & Pham-Kanter 2002; Bloom 2009; Bekaert, Hoerova & Lo Duca 2013; Whaley 2009; Baker, Bloom & Davis 2016; Husted, Rogers & Sun 2020.

## 3.7 계량경제 실험군 (E1–E9)
| 블록 | 방법 | 왜 이 방법인가 | 근거 |
|---|---|---|---|
| E1 | 기술통계(평균·SD·범위·AR(1)·제로 회의 비율) | 계열의 지속성(AR(1) .3–.8)과 희소성(제로 회의)이 이후 추론의 전제이므로 먼저 보고 | 표준 보고 관행 |
| E2 | Pearson·Spearman × {CFNAI, VIX} × {T1, T2, T3, H1, H2} | 순위 상관은 극단값(2020-03 VIX 50, CFNAI −7.6)에 강건; 기간 분할은 레버리지 점검 | — |
| E3 | 회의 단위 OLS, Newey–West HAC(4 lag); 스펙 (1)–(8) | 회의 계열은 자기상관·이분산이 있으므로 HAC 표준오차가 필요하다. (4) 갭 통제는 연준의 목표 변수를 통제했을 때도 관계가 남는지, (5) 2020-09 더미는 프레임워크 구조 변화(문장 채택)를 통제했을 때, (6)은 팬데믹 레버리지를 제거했을 때, (7)(8) 1차 차분은 지속성 기반 허위 상관을 제거했을 때의 관계다 — Kawamura et al.도 월차분에서 결과가 사라짐을 보고했으므로 같은 검정을 둔다 | Newey & West 1987; Kawamura et al. 2019 §3.3.1 |
| E4 | 구문 회귀(사전 지정 구문 + be appropriate 계열) | 집계 밀도가 반대 부호의 구문을 상쇄할 수 있으므로 구문 수준 검정이 필요 | §3.3 |
| E5 | 전수 스크린 + BH-FDR + 확정/시대 구성/2020 의존 분류 | 수천 셀의 스크린은 다중검정 통제 없이는 무의미하다(BH). 확정 규칙의 세 요소는 각각 (i) 2020 레버리지, (ii) 2020-09 문장 채택이 만드는 시대 구성 효과(반기 부호 검사 = 분할표본 안정성), (iii) 희소 계열의 상관 불안정(토큰·제로 회의 하한)에 대응한다 | Benjamini & Hochberg 1995; Simonsohn et al. 2020 |
| E6 | CCF k = −9…+9; Granger 1–3 lag 양방향(BH); 예측 회귀(ΔR², 텍스트 계수) | "선행지표" 주장은 Granger 인과와 표본 내 증분 예측력으로 검정하는 것이 관행이며, 텍스트가 정책·기대를 선행한다는 문헌의 기준 결과와 비교한다 | Granger 1969; Lucca & Trebbi 2009; Romer & Romer 2000 |
| E7 | 정책 사건 창(텍스트 ±3회의, 거시 ±6개월) | 편집 사건의 타이밍이 거시 환경과 정렬되는지 보는 사건 연구 논리 | MacKinlay 1997 |
| E8 | 래그·회의 간 VIX·정규화·2010 확장 변형 | 결과가 정렬·정규화 선택에 의존하는지 점검 | §3.1 |
| E9 | Kawamura 방식 재현(총밀도·헤징군·약속군, 수준·차분·2020 제외) | 벤치마크와 같은 형태의 표를 제시해야 "이전되지 않는다"는 주장이 비교 가능하다 | Kawamura et al. 2019 |

## 3.8 판정 규칙과 보고 관행
- 가설 판정은 '지지 / 부분 / 기각 / 해당 없음' 네 값이며 기준은 §1.2에 사전 명시했다.
- 코퍼스 언어학 표는 원시 빈도·정규화 빈도·신뢰구간·효과 크기·용례를 함께 제시한다(Brezina, 2018). 계량경제 표는 계수·(HAC 표준오차)·유의성 별표·N·R²를 스펙별 열로 제시한다.
- 신뢰도: 추출 정확도는 저자 표본(head 93%, 의미 유형 90%)에 근거하며, 독립 2인 코딩과 κ(McHugh, 2012)는 투고 전 과제다.

## 3.9 방법론 참고문헌
- Acosta, M., & Meade, E. E. (2015). Hanging on every word: Semantic analysis of the FOMC's postmeeting statement. *FEDS Notes*, Board of Governors of the Federal Reserve System.
- Agresti, A. (2013). *Categorical Data Analysis* (3rd ed.). Wiley.
- Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty. *Quarterly Journal of Economics*, 131(4), 1593–1636.
- Bekaert, G., Hoerova, M., & Lo Duca, M. (2013). Risk, uncertainty and monetary policy. *Journal of Monetary Economics*, 60(7), 771–788.
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society B*, 57(1), 289–300.
- Biber, D. (1988). *Variation across Speech and Writing*. Cambridge University Press.
- Biber, D., & Barbieri, F. (2007). Lexical bundles in university spoken and written registers. *English for Specific Purposes*, 26(3), 263–286.
- Biber, D., Johansson, S., Leech, G., Conrad, S., & Finegan, E. (1999). *Longman Grammar of Spoken and Written English*. Longman.
- Bloom, N. (2009). The impact of uncertainty shocks. *Econometrica*, 77(3), 623–685.
- Brezina, V. (2018). *Statistics in Corpus Linguistics: A Practical Guide*. Cambridge University Press.
- Coates, J. (1983). *The Semantics of the Modal Auxiliaries*. Croom Helm.
- Cramér, H. (1946). *Mathematical Methods of Statistics*. Princeton University Press.
- Ehrmann, M., & Talmi, J. (2020). Starting from a blank page? Semantic similarity in central bank communication and market volatility. *Journal of Monetary Economics*, 111, 48–62.
- Evans, C. L., Liu, C. T., & Pham-Kanter, G. (2002). The 2001 recession and the Chicago Fed National Activity Index. *Economic Perspectives*, 26(3), 26–43.
- Gabrielatos, C. (2018). Keyness analysis: Nature, metrics and techniques. In C. Taylor & A. Marchi (Eds.), *Corpus Approaches to Discourse* (pp. 225–258). Routledge.
- Gelman, A., & Loken, E. (2014). The statistical crisis in science. *American Scientist*, 102(6), 460–465.
- Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. *Econometrica*, 37(3), 424–438.
- Gries, S. Th. (2008). Dispersions and adjusted frequencies in corpora. *International Journal of Corpus Linguistics*, 13(4), 403–437.
- Gries, S. Th., & Stefanowitsch, A. (2004). Extending collostructional analysis: A corpus-based perspective on 'alternations'. *International Journal of Corpus Linguistics*, 9(1), 97–129.
- Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. *Quarterly Journal of Economics*, 133(2), 801–870.
- Hardie, A. (2014). Log ratio: An informal introduction. *ESRC Centre for Corpus Approaches to Social Science*. ※
- Husted, L., Rogers, J., & Sun, B. (2020). Monetary policy uncertainty. *Journal of Monetary Economics*, 115, 20–36.
- Hyland, K. (1998). *Hedging in Scientific Research Articles*. John Benjamins.
- Kaplan, E. L., & Meier, P. (1958). Nonparametric estimation from incomplete observations. *Journal of the American Statistical Association*, 53(282), 457–481.
- Kawamura, K., Kobashi, Y., Shizume, M., & Ueda, K. (2019). Strategic central bank communication: Discourse analysis of the Bank of Japan's Monthly Report. *Journal of Economic Dynamics and Control*, 100, 230–250.
- Kendall, M. G. (1975). *Rank Correlation Methods* (4th ed.). Griffin.
- Killick, R., Fearnhead, P., & Eckley, I. A. (2012). Optimal detection of changepoints with a linear computational cost. *Journal of the American Statistical Association*, 107(500), 1590–1598.
- Lin, J. (1991). Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory*, 37(1), 145–151.
- Love, R., Dembry, C., Hardie, A., Brezina, V., & McEnery, T. (2017). The Spoken BNC2014. *International Journal of Corpus Linguistics*, 22(3), 319–344.
- Lucca, D. O., & Trebbi, F. (2009). Measuring central bank communication: An automated approach with application to FOMC statements. *NBER Working Paper* 15367.
- MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13–39.
- Mann, H. B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245–259.
- McHugh, M. L. (2012). Interrater reliability: The kappa statistic. *Biochemia Medica*, 22(3), 276–282.
- Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
- Nuyts, J. (2001). *Epistemic Modality, Language, and Conceptualization*. John Benjamins.
- Palmer, F. R. (1990). *Modality and the English Modals* (2nd ed.). Longman.
- Rayson, P., & Garside, R. (2000). Comparing corpora using frequency profiling. *Proceedings of the Workshop on Comparing Corpora* (ACL), 1–6.
- Romer, C. D., & Romer, D. H. (2000). Federal Reserve information and the behavior of interest rates. *American Economic Review*, 90(3), 429–457.
- Sen, P. K. (1968). Estimates of the regression coefficient based on Kendall's tau. *Journal of the American Statistical Association*, 63(324), 1379–1389.
- Simonsohn, U., Simmons, J. P., & Nelson, L. D. (2020). Specification curve analysis. *Nature Human Behaviour*, 4, 1208–1214.
- Sinclair, J. (1991). *Corpus, Concordance, Collocation*. Oxford University Press.
- Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing transparency through a multiverse analysis. *Perspectives on Psychological Science*, 11(5), 702–712.
- Stefanowitsch, A., & Gries, S. Th. (2003). Collostructions: Investigating the interaction of words and constructions. *International Journal of Corpus Linguistics*, 8(2), 209–243.
- Stock, J. H., & Watson, M. W. (1999). Forecasting inflation. *Journal of Monetary Economics*, 44(2), 293–335.
- Whaley, R. E. (2009). Understanding the VIX. *Journal of Portfolio Management*, 35(3), 98–105.
- Wray, A. (2002). *Formulaic Language and the Lexicon*. Cambridge University Press.

※ 표시는 투고 전 서지 확인 필요.

---

# 4. 결과 A — 코퍼스 언어학 (주 run C11_U2: S4 × 구문)

## 4.1 L1 빈도와 분산
§2.3의 표가 L1의 결과다. 6대 조동사 순위는 층위마다 다르다: 성명서 will(14,485 pmw) ≫ could·would; 참가자 견해 would(6,862) > could(3,906); 위원회 결정 would(11,443); 의장 기자회견 will(8,143) > would(5,866) > can(3,020). DP로 보면 성명서의 would/could/should/can은 특정 시기 문서에만 몰려 있어(높은 DP) 시계열이라기보다 사건이다.

## 4.2 L2 키니스와 층위 분업
{{fig:C11_U2:L2_residuals|그림 1. 층위 × 조동사 표준화 잔차 (χ² = 6,801, df = 35, V = .259). 양수 = 기대보다 과다 사용.}}
{{tbl:C11_U2:residuals}}
{{tbl:C11_U2:keyness:statement}}
{{tbl:C11_U2:keyness:min_participants}}
{{tbl:C11_U2:keyness:min_committee}}
{{tbl:C11_U2:keyness:pc_chair}}
**읽기.** H2의 직접 증거다. 성명서는 will(+23.8; LL 650, log ratio +1.86)과 그 구문(will+take, will+assess, will+continue: log ratio 3.7–6.4)의 장르이고, 참가자 견해는 could(+28.4, log ratio +1.53)·would의 장르, 위원회 결정은 would(+21.4, log ratio +1.35)의 장르, 의장 기자회견은 will(+17.8)과 can(+13.8, log ratio +2.33)의 장르, 연설은 may(+13.8)의 장르다. 스태프 리뷰에서 will은 log ratio −6.3으로 사실상 부재한다(스태프는 미래를 will로 말하지 않는다). 조동사 하나를 세는 지표는 이 분업을 층위 구성비의 함수로 만든다.

## 4.3 L3 통시: 추세와 계단
{{fig:C11_U2:L3_yearly_main|그림 2. 성명서 조동사의 연도별 pmw.}}
{{tbl:C11_U2:mk}}
{{fig:C11_U2:L3_staircase_T1|그림 3. 성명서 구문 계단: 회의별 구문 점유율(N2)과 PELT 변화점(점선), 정책 사건(라벨), 2014–2026, 단위 = 구문.}}
{{fig:C11_U1:L3_staircase_T1|그림 4. 같은 그림의 조동사 단위판(단위 = 조동사; v2 Figure 4에 해당).}}
{{tbl:C11_U2:changepoints}}
**읽기.** H1의 핵심 증거다. 구문 단위 변화점 25개 중 17개가 정책 사건 ±1회의 이내이고, 각 변화점은 문장 하나의 삽입·삭제로 귀속된다: should+help는 2014-10 재투자 문장으로 등장해 2017-06 정상화 부속서에서 삭제되고, would+be+prepared·could+impede는 2020-09 새 프레임워크의 조건부 약속 문장으로 함께 등장하며, will+be+appropriate는 2015-12 첫 인상에서 삭제, 2020-09 재등장, 2023-03 마지막 인상 국면에서 삭제된다. 조동사 단위(그림 4)로는 변화점 14개(사건 일치 10개)만 보이고, will 점유율 하락은 would/could 문장 등장의 구성 효과로 드러난다. Mann–Kendall 추세는 성명서 would(τ = +.59)·could(+.58)의 계단, should(−.39)·may(−.12)의 소멸, 그리고 성명서 총밀도의 상승(+.34: 성명서가 짧아지면서 조동사 문장의 비중이 커짐)에서 유의하다. 의사록에서는 스태프 리뷰의 would(−.30)·총밀도(−.20)가 감소하고 위원회·참가자 층의 could(+.50, +.24)가 증가하며, 의장 기자회견에서는 can(+.26)만 증가한다.

## 4.4 L4 연어·구문
{{tbl:C11_U2:profiles:statement}}
{{tbl:C11_U2:collo:statement}}
{{tbl:C11_U2:jsd:statement}}
{{tbl:C11_U2:profiles:min_committee}}
{{tbl:C11_U2:profiles:min_participants}}
{{tbl:C11_U2:collo:pc_chair}}
{{fig:C11_U2:L4_verb_class_main|그림 5. 성명서 서술어의 의미 부류 × 조동사 (Biber 부류 + 정책행동 + 코퓰러 유형).}}
{{tbl:C11_U2:kwic:statement}}
**읽기.** 성명서에서 조동사 하나는 구문 하나다: would의 94%가 be prepared, could의 92%가 impede, should의 64%가 help, may의 56%가 warrant; 조동사 간 JSD가 0.76–1.00으로 서술어 분포가 거의 겹치지 않는다. 위원회 결정 서술은 성명서 문장을 과거형으로 되풀이하고(would take, could impede), 참가자 견해는 심의(would be appropriate, could lead), 스태프 리뷰는 전망(would expand, could increase, may edge), 의장 발화는 화자 표지(would say, can do)다. collexeme 분석은 성명서 will의 유인 서술어(take, continue, assess, expand, monitor)가 모두 정책 절차 동사임을 보여 준다.

## 4.5 L5 정형성
{{fig:C11_U2:L5_retention_edits|그림 6. 성명서 구문 보유율 곡선(왼쪽)과 연도별 구문 삽입·삭제(오른쪽).}}
{{tbl:C11_U2:retention}}
**읽기.** 성명서 구문 집합은 한 회의 뒤 89%가 남고 16.8회의(약 2년) 뒤 절반이 남는다. will 구문은 18.1회의, should 7.5, may 4.0, can 1.0회의이고 2020-09 이후의 would/could 구문은 24회의 안에 반감하지 않는다. 편집은 국면 전환 해(2014, 2020)에 몰린다. 성명서 조동사 토큰의 83%가 3개 이상 성명서에 재출현하는 정형 문장 안에 있다.

## 4.6 L6 문법 맥락과 의미 유형
{{fig:C11_U2:L6_context_main|그림 7. 성명서 조동사의 문법 맥락 비율.}}
{{tbl:C11_U2:context:statement}}
{{tbl:C11_U2:context:min_participants}}
{{tbl:C11_U2:context:pc_chair}}
**읽기.** 성명서 would/could는 조건절 안(94%/92%)의 조동사이고 주어는 위원회다. 참가자 층 would/could는 보고 동사 아래의 백시프트(71%/51%)이고 주어는 경제 변수다. 의장 발화의 would·can은 1인칭(56%/40%)이고 can은 부정(17%)·2인칭이 많다 — 교수님이 언급한 "will/would는 비슷하게, can/could는 화용적으로 다르게"는 의장 발화에서 can만 청자 지향·부정 지향이라는 형태로 확인된다. 의미 유형 휴리스틱은 성명서 will을 volitional(위원회 주어)과 predictive(경제 주어)로 나눈다.

## 4.7 L7 다항 로짓
{{tbl:C11_U2:mnlogit}}
**읽기.** 층위·시기·주어 유형·조건·인용을 넣은 다항 로짓의 유사 R²는 .163이다. 성명서 대비 참가자 층은 could의 상대위험비가 12.3배, may 5.5배; 의장 기자회견은 can 3.7배; 연설은 can 5.0배. 층위 효과는 시기·주어를 통제해도 남는다 — H2의 두 번째 증거.

## 4.8 L8 be appropriate
{{tbl:C11_U2:be_appropriate}}
**읽기.** will be appropriate는 성명서(43)와 의장 기자회견(105)의 구문이고, would be appropriate는 참가자 견해(143)와 위원회 결정(63)의 구문이며 위원회 층에는 will이 7개뿐이다. 즉 두 형태는 같은 관용구의 시제 변형이 아니라 **문서 기능이 배정한 형태**다: will은 성명서·의장이 시장에 말하는 약속의 조동사, would는 의사록이 결정을 기록하는 조동사.

## 4.9 L9 의장·국면 대조
{{tbl:C11_U2:contrasts}}
**읽기.** 성명서의 Yellen–Powell 차이는 2020-09 프레임워크 문장에 집중되고, 의장 기자회견에서는 개인 문체 차이가 작다. 정책 국면별 성명서 점유율은 계단 그림의 표 형태다.

---

# 5. 결과 B — 계량경제 (주 run C11_U2)

## 5.1 E2 상관
{{fig:C11_U2:E2_heatmap|그림 8. 층위별 조동사 밀도 × CFNAI / VIX, Spearman ρ, T1(왼쪽)과 2020 제외(오른쪽). * p < .05.}}
{{tbl:C11_U2:corr_all}}
**읽기.** 총밀도 수준에서 유의한 상관은 의장 기자회견(CFNAI +.26*, VIX +.30*)과 스태프 리뷰 층(VIX −.36***)뿐이다. 성명서·의사록 총밀도는 어느 거시 변수와도 무관하다.

## 5.2 E3 회귀 스펙 표
{{tbl:C11_U2:regtable:statement:ALL}}
{{tbl:C11_U2:regtable:min_committee:ALL}}
{{tbl:C11_U2:regtable:min_participants:ALL}}
{{tbl:C11_U2:regtable:min_staff:ALL}}
{{tbl:C11_U2:regtable:pc_chair:ALL}}
**읽기.** H3의 검정이다. 스펙 (3)에서 CFNAI 계수가 음·유의한 층위는 없다. 위원회 층에서 2020-09 더미를 넣은 스펙 (5)와 1차 차분 스펙 (7)은 CFNAI에 음의 계수(−0.37***, −0.27***)를 주지만 2020을 제외한 스펙 (8)에서 사라진다(−1.92, p = .19) — 2020-03/04의 극단적 CFNAI 변화가 만든 결과다. 갭을 넣은 스펙 (4)에서는 위원회 층 총밀도가 실업률 갭(+1.01***)·근원 PCE 갭(+1.13***)과 양의 관계인데, 이는 정책 조정이 논의된 회의(갭이 큰 회의)에서 결정 서술이 길어지는 효과로 읽힌다. 의장 기자회견 총밀도는 스펙 (3)에서 CFNAI +0.34**, VIX +0.18***로 활동이 강하고 불확실할수록 조동사가 많다(순경기·불확실성 동행). 스태프 리뷰 층은 VIX −0.044**(2020 제외 −0.072***)로 반대다.

## 5.3 E4 구문 회귀
{{tbl:C11_U2:regtable_units:statement}}
{{tbl:C11_U2:regtable_units:min_committee}}
{{tbl:C11_U2:regtable_units:min_participants}}
**읽기.** 성명서의 VIX 계수가 큰 구문(would+be+prepared, could+impede, will+continue)은 모두 스펙 (6)·(8)에서 부호가 뒤집히거나 사라지는 채택 사건 구문이다. 위원회 층 would+be+appropriate는 (3)에서 VIX +.087**, 2020을 제외한 (6)에서 CFNAI +1.86***·VIX +.095***이고(차분에서는 n.s.), would+assess는 (3) CFNAI −0.26***, (6) −1.78***, (7) Δ −0.11***로 반대 방향이다: 활동이 강한 회의의 결정 서술은 "적절하다"를, 약한 회의는 "평가하겠다"를 쓴다. 두 구문 모두 2020 제외 차분 (8)에서는 유의하지 않아, 관계는 수준(국면)의 것이다.

## 5.4 E5 전수 스크린과 ledger
{{tbl:C11_U2:ledger:confirmed}}
{{tbl:C11_U2:ledger:era_composition:12}}
{{tbl:C11_U2:ledger:T1_only:12}}
**읽기.** 2,000여 개의 단위 × 층위 × 거시 × 기간 셀 중 확정은 VIX 8·CFNAI 6이고, 시대 구성 22·2020 의존 9가 걸러졌다. 확정 VIX 단위 8개 중 7개는 의사록 층(위원회: would+continue, would+be+appropriate; 스태프: 총밀도·would; 참가자: should; 데스크: could)이고 성명서 층은 will+assess 1개(반기 −.07/−.27로 약함)다 → H4 '부분'. 시대 구성의 대표는 성명서·위원회의 would+be+prepared·could+impede(2020-09 채택 이전 토큰 0)와 statement will+continue(2019-07 채택)다.

## 5.5 E6 선행성
{{tbl:C11_U2:granger}}
**읽기.** H5 기각. Granger text→macro의 최소 q는 .36이고, 예측 회귀 64건 중 q < .10은 없다(최소 .54). CCF 피크는 있으나(의사록 could → CFNAI k = +6 ρ −.27 등) 약하고 대부분 macro → text 방향이다. 조동사 구문은 상태 변수이지 예측 변수가 아니다.

## 5.6 E7 사건 연구
{{fig:C11_U2:E7_event_macro|그림 9. 정책 사건 주변 ±6개월의 CFNAI-MA3(파랑)와 VIX(주황). k = 0이 사건 월.}}
{{tbl:C11_U2:event_text}}
**읽기.** 성명서 총밀도는 사건 회의에서 계단처럼 움직이지만(QE3 종료 18.9→12.5 per 1k, 정상화 부속서 20.9→17.8, Powell 취임 직후 성명서 축약 19.1→13.8, 팬데믹 긴급 성명서 10.8→16.2, 2024-09 인하 개시 23.6→19.9), 사건 주변의 거시 창은 사건마다 다르다(2015-12 저VIX, 2020-03 고VIX, 2022-03 중간). 편집의 타이밍은 정책 일정이지 거시 환경이 아니다 — H1을 거시 쪽에서 보강한다.

## 5.7 E8 강건성
{{tbl:C11_U2:robustness}}
**읽기.** 총밀도 상관은 CFNAI 래그, 회의 간 VIX, 점유율·문서당 수 종속, 2010 확장에서 부호가 유지된다. 의장 기자회견 VIX(+)와 스태프 리뷰 VIX(−)가 모든 변형에서 남는 두 신호다.

## 5.8 E9 Kawamura 재현
{{tbl:C11_U2:kawamura}}
**읽기.** Kawamura et al.(2019)이 BoJ 월보에서 보고한 "경기가 나쁠수록 헤징 표현 증가"는 FOMC 어디에도 없다. 헤징군(would/could/may/might)은 성명서에서 CFNAI와 **양**(+0.47***)의 관계인데 이는 2020-09 채택 이후의 회복기 구성 효과이고, 연설에서는 수준·차분 모두 양(+0.44***, Δ +0.69***)이다. 의장 기자회견의 헤징군은 VIX와 약한 음(−0.065**)이다. 일본 결과는 이전되지 않는다.

---

# 6. 전 조합 비교 (72 run)

{{grid}}

## 6.1 판정 분포 (72 run)
- **H1 편집**: 성명서가 포함된 39 run 전부 '지지'(변화점의 50% 이상이 정책 사건 ±1회의 이내), 성명서가 없는 33 run은 '해당 없음'. 단위·다른 장르의 포함 여부는 결과를 바꾸지 않는다 — 계단은 성명서 고유의 사실이다.
- **H2 층위 분업**: 층위가 2개 이상인 60 run 전부 '지지'(V .15–.80). 단일 층위 12 run은 '해당 없음'.
- **H3 반경기**: **72 run 전부 '기각'**. 어떤 코퍼스 정의·단위·기간(수준, 2020 제외, 1차 차분, 차분·2020 제외)에서도 총밀도의 CFNAI 계수가 음·유의하지 않다. Kawamura형 반경기 양태는 FOMC 텍스트에 없다.
- **H4 불확실성(비편집 층에서만)**: '지지' 37, '부분' 26, '기각' 9. 패턴이 뚜렷하다: 성명서가 **없는** 조합(의사록 또는 연설 포함)은 거의 전부 '지지', 성명서가 **있는** 조합은 U2·U3에서 '부분'(성명서 층의 will+assess × VIX 1건 때문; 반기 −.07/−.27로 약함), U1에서는 '지지'. '기각' 9건은 기자회견 단독(C15)과 위원회 층 단독의 조동사 단위처럼 확정 단위가 0인 소표본 조합이다.
- **H5 선행성**: '기각' 64, '지지' 8. 8건은 모두 Granger 셀 1–2개가 q .05–.09에 걸린 경계 사례이고(주로 동사 부류 단위·연설 단독), 예측 회귀는 72 run 전부 0건이다. 실질적으로 선행성은 없다.

## 6.2 각 축이 바꾸는 것 (구문 단위 U2 기준)
- **의사록 포함**: 확정 단위(VIX / CFNAI)가 성명서만 1 / 0 → 위원회 층 추가 3 / 5 → 실질 층 전부 7 / 6으로 늘어난다. 새 신호는 전부 의사록 층에서 나온다(위원회: would+continue·would+be+appropriate·would+assess·would+depend·could; 스태프: 총밀도·would; 참가자: should; 데스크: could). 의사록만(C21)으로도 6 / 6이 나오지만 계단(H1)은 잃는다.
- **기자회견(의장) 포함**: 확정 단위는 0–1개 늘 뿐인데 시대 구성 적중은 +10, 2020 의존 적중은 +6이 늘어난다. 의장 발화의 조동사는 국면(2020-09 이후)과 함께 움직이는 계열이 많아 확정 규칙에 자주 걸린다. 총밀도는 순경기(CFNAI +.26*)·불확실성 동행(VIX +.30*)이다.
- **연설 포함**: 확정 VIX +1(연설 should × VIX −.19). 연설 헤징군은 수준·차분 모두 순경기(+).
- **미정제(C24, v2 방식)**: 확정 9 / 8로 가장 많아 보이지만 시대 구성 39·2020 의존 11로 인공물도 가장 많다. 추가된 확정 단위 3개는 제외했어야 할 층(표결, 인용 성명서)에서 나온다.
- **단위**: 조동사(U1) → 구문(U2)에서 확정 단위가 늘고(S2: VIX 0 → 3) 계단이 정확해진다(14 → 25 변화점, 사건 일치 10 → 17). 동사 부류(U3)는 확정도 인공물도 가장 많다(스크린 폭이 넓어서).
- **코로나·기간**: 2020 제외는 성명서 층의 VIX 상관을 오히려 키우지만(would/could +.34 → +.45) 반기 검사에서 죽는다 — 문제는 2020의 극단값이 아니라 **2020-09의 문장 채택**이다.

---

# 7. 가설 판정

{{tbl:C11_U2:hypotheses}}

{{hgrid}}

---

# 8. 논의

## 8.1 교수님의 질문: will은 왜 안 나오나
L8·E4의 답은 "will과 would는 다른 문서 기능이 배정한 형태"라는 것이다. will be appropriate는 성명서와 의장의 약속 문장이며 프레임워크 사건에 따라 계단으로 움직이고(2015-12 삭제, 2020-09 채택, 2023-03 삭제), would be appropriate는 의사록이 결정을 기록하는 문장이며 위원회 층에서 실물(CFNAI +.39)·불확실성(VIX +.33) 모두와 공변한다. 참가자 층의 would be appropriate(n = 143)는 약하다. v2의 "살아있는 심의 관용구" 해석은 "위원회 결정 서술의 관용구"로 고쳐야 한다.

## 8.2 Kawamura와의 비교
같은 지표 쌍(경기지수 + VIX), 같은 강건성(차분)으로 재현했을 때 FOMC에서는 반경기 양태가 없고, 의장 발화는 순경기적이다. 차이는 문서의 성격에 있다: BoJ 월보는 스태프가 매달 새로 쓰는 평가문이고, FOMC 성명서는 편집되는 정형문이며, 의사록 위원회 서술은 결정의 기록이다. 우리 데이터에서 BoJ 월보에 가장 가까운 층(스태프 리뷰)은 불확실할수록 조동사를 **줄인다**(VIX −.36).

## 8.3 결론 문장 후보
- C2 편집 우선(주 후보): *성명서의 조동사 변화는 정책 사건에 따른 정형문 편집의 계단이며, 경제 상황과의 공변은 편집되지 않은 의사록 층의 특정 구문에서만 나타난다.*
- C1 불확실성·구문 특이(결합): *조동사 총량은 경기와 무관하지만, 위원회 결정 서술의 구문은 실물·불확실성과, 스태프 서술은 불확실성과 정합한다.*
- C3 부정(성명서만 쓰는 경우): *조동사를 세는 것으로는 경제 상황을 읽을 수 없다.*

---

# 9. 한계·검증 필요·다음 단계
- 사람 검증 미완: 화자 역할 표본(10문서 × 20턴), 의사록 층위 표본, 추출 200문장 2인 코딩 — 투고 전 필수.
- 관측치 약 100회의; 제로 회의가 많은 구문의 상관은 불안정(제로 ≤ 60% 규칙). 반기 부호 검사는 보수적이어서 진짜 신호도 걸러낼 수 있다.
- 거시 지표는 FRED 최종치(vintage 아님); EPU·JLN 등 대안 불확실성 지표는 미실행.
- 다음: 팀이 조합·단위·결론 문장을 정하면(D8–D11) 논문 v3 작성. 문헌 보강: be appropriate(Van linden 2012; Femia, Friedman & Sack 2013), will/would vs can/could 화용론(Collins 2009; Ward, Birner & Kaplan 2003).

---

# 부록
- A. run별 상세 페이지: `results/report_v3/run_<Cxx>_<U>.html` (L1–L9·E1–E9 전체 표·그림, 오류 로그). 격자의 "열기" 링크.
- B. 재현: `experiments/10_build_corpus_v3.py` → `11_extract_modals_v3.py` → `12_qa_integrity.py` → `23_run_program.py --corpus all --unit all --workers 4` → `24_build_report_v3.py`.
- C. 설계 명세 `docs/12`, 데이터 카드 `docs/09`, 지표 근거 `docs/10`, 인수인계서 `HANDOVER.md`.
