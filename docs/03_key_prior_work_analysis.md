# 03. 핵심 선행연구 분석

## 1. Kawamura, Kobashi, Shizume & Ueda (2019). *Strategic central bank communication: Discourse analysis of the Bank of Japan's Monthly Report.* JEDC 100, 230–250.

**연구 질문** — 중앙은행이 사적 정보가 불리할 때 보고서를 모호하게(obfuscate) 만드는가?

**데이터** — 일본은행 『금융경제월보』 Summary 섹션, 1998-01 ~ 2015-03, 207호(일본어 원문). 현재 상태(present) 문단과 전망(forecast) 문단 구분.

**방법**
1. 극성(polarity): 일본어 감성극성사전(Kobayashi 2004; Higashiyama 2008) — 긍정/부정(경험/평가)/중립.
2. 양태(modality) = 모호성(ambiguity): 문말 술어에서 추출, 5회 이상 출현 표현을 **인간 코딩**으로 3범주 — high probability(seem/appear/expected/likely), low probability(may/warrant careful monitoring), unreal(should/it is important to). 기준: 명제 단정 여부, "~가 아닐 것"과의 충돌 여부 등 언어학적 테스트(Appendix B).
3. 정규화: 형태소 수 대비 비율. 형태소/문장(mor/sen)도 모호성 지표.
4. 통계: 선행·동행·후행 경기지수, CPI, 정책변경 더미와의 상관(n=207), 리드-래그(극성이 선행지수를 3개월 선행), VIX·닛케이 VI 통제 회귀(HAC), 월별 차분 강건성, Granger.
5. LDA(BIC로 토픽 수 선택; 양태·극성 표현만으로 구성한 절약 모형) → 양태 표현이 부정 표현과 같은 토픽에 묶임.
6. 이론: Dye(1985) 설득게임(persuasion game) 변형 — 은행은 거짓말은 못 하지만 정보를 보류할 수 있음 → 부정적 보고는 항상 모호.
7. 질적 증거: 정책위원회 회의록(10년 후 공개)에서 표현 수정 논의("etc." 추가, "need careful monitoring" 채택).

**결과** — 모호 표현(양태·긴 문장·etc.)은 경기 하강기에 증가(선행지수와 음의 상관), VIX를 통제해도 유지 → 내생적 불확실성만으로는 설명 불가 → **전략적 모호성**. 영어 번역본에서는 양태 표현이 줄고 상관도 약화.

**한계(논문 자인 + 우리 시각)**
- 일본어 문말 양태 구조에 의존 → 영어 텍스트로의 이식성 낮음(영어판 결과 약화).
- 양태를 3범주(high/low/unreal)로 뭉뚱그려 **개별 조동사·후행 동사 수준의 분석 없음**.
- 상관 중심; 월별 차분 시 양태 관련 결과 소실 → 수준(level) 효과에 의존.
- 매체가 단일 장르(월보 Summary)·2016 폐간.
- "모호성"과 "hedging/양태"를 동일시 — 언어학적으로 양태는 인식(epistemic)·의무(deontic)·동적(dynamic) 의미로 나뉘며 모두 모호성은 아님.

## 2. Resche, C. (2015). *Hedging in the discourse of central banks.* Studies in Communication Sciences 15(1), 83–92.

**연구 질문** — 고전적 hedge(어휘 목록) 계량만으로 중앙은행 담화의 hedging을 포착할 수 있는가?

**데이터** — 2008-01 ~ 2013-07 연설 103편(Bernanke 20, Trichet 19, Draghi 9, Carney 34, King 21), 210,915 단어.

**방법** — (i) 전량 정독(bottom-up)으로 잠재적 hedge 표지, (ii) AntConc로 hedge 목록(Appendix B: 근사어/모호 수량어, 시간 지시, 양태/확률(can, could, may, might, would, likely, seem…), 접속어, 논리/정당화, 가치·진리 판단/강조어) 빈도 집계, (iii) 수사학(ethos/pathos/logos)·화행·Grice 격률 관점의 질적 분석.

**결과** — 고전적 hedge는 어휘의 4.5–5.8%; 위기 초기(2008–09)보다 후기(2010–13)에 더 많거나 같음; ECB가 가장 낮음. 그러나 hedging은 "확산적(diffuse)" 현상 — 정당화·역사 인용·유연성 강조·은유·수사의문 등도 hedging 전략. 결론: "hedging을 수학적으로 측정하려는 시도는 헛될 것" — 맥락·장르·이해관계를 반영한 질적 접근 필요.

**한계** — 소규모 코퍼스·연설 단일 장르, 통계 검정 없음, hedge 목록에 이질적 범주(접속어·강조어) 혼재, 두 시기 비교만 가능(통시성 약함), 조동사를 하나의 범주로 처리하여 will/would/could 간 기능 차이 미분석, 연준 Statement(가장 편집된 텍스트)는 제외.

## 3. 우리 연구와의 차별점·개선점

| 차원 | Kawamura et al. (2019) | Resche (2015) | **본 연구** |
|---|---|---|---|
| 대상 | BoJ 월보 Summary(일본어), 1998–2015 | 5개 중앙은행 총재 연설, 2008–2013 | **FOMC Statement 2014–2026 (주) + Minutes·Press Conf·Speech(대조)**, 영어 원문 |
| 분석 단위 | 문말 술어 표현(인간 코딩 3범주) | hedge 어휘 목록 빈도 | **조동사 6종 × 후행 동사 구문(modal + V)**, 의존구문 기반 자동 추출 + 표본 검증 |
| 시간 해상도 | 월별 207호, 상관 | 2기간 비교 | **회의 단위 100+편, 구조 변화점·추세 검정·구문 생존(반감기)** |
| 설명 변수 | 경기지수·VIX | 위기 국면(정성) | **정책 프레임워크 사건(2017 정상화·2020 프레임워크·2022 인상·2024 인하)**, 의장, 장르, 정책 국면(점도표 라벨) |
| 언어학 이론 | 양태 = 모호성 | hedging = 확산적 전략 | **양태 의미론(epistemic/deontic/dynamic; Coates, Palmer) + 구문·정형성(collostruction, lexical bundles, formulaic language)** |
| 핵심 주장 | 불리할 때 모호 | hedging은 정량화 불가 | **조동사 분포는 정형 문장의 편집 이벤트로 설명되며, 각 조동사는 고정 구문에 결합해 장르별로 분업한다** |
| 재현성 | 일본어 인간 코딩 | 정독 | 공개 코퍼스·코드·CSV(재현 가능) |

**우리가 더 좋아지는 지점**
1. *해상도*: "양태 ↑/↓"가 아니라 **어떤 조동사가 어떤 동사와 결합해 언제 나타나고 사라지는지**를 문장 단위로 추적 — Kawamura의 3범주, Resche의 목록 계량 모두 이 층위를 보지 못함.
2. *인과적 서사*: 변화의 원인을 거시지표 상관이 아니라 **텍스트 내부 편집 이벤트 + 공식 정책 문서(프레임워크 개정·정상화 계획)**로 직접 대응시킴.
3. *Resche의 비판에 대한 응답*: 조동사만 세는 대신 후행 동사·주어·조건절 등 **co-text를 함께 계량**하여 "hedging은 맥락적"이라는 주장을 정량 분석 안으로 흡수.
4. *Kawamura의 확장 요청 수용*: 논문 결론이 "연준 등 다른 중앙은행에서의 검증"을 향후 과제로 명시 — 본 연구가 그 공백을 채우되, 양태를 모호성으로 환원하지 않고 **기능별로 분리**.
5. *통계*: Mann–Kendall/Sen slope, 변화점 탐지, Kaplan–Meier, Fisher-exact collostruction, 카이제곱 잔차 — 선행연구에 없던 검정들.

**이어받는 것**
- Kawamura: "양태 × 경제/정책 상태" 구도, 표현 정규화(토큰 대비), 질적 증거(회의록의 표현 수정 논의)와 정량 결과의 결합.
- Resche: 조동사가 hedging 자원이라는 관점, 시기·화자별 대조, 코퍼스 도구 기반 빈도 + 질적 해석의 병행.
