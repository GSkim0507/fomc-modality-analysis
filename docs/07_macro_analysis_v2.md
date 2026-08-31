# 07. v2 — 동료 피드백 반영: be-후행어 해소 + 거시 연계 분석 (검증 완료 결과)

> 실험: `experiments/01(개정), 06–09`. 표: `results/tables/A7, E1–E6, F1–F4, G1–G6`, `results/v2_verified_findings.json`.
> 문헌 근거: `literature/EVIDENCE_feedback3.md`. 검증 방식: 5개 렌즈 발견 → 발견별 적대적 재계산 검증(2020 제외·Spearman·반기 부호·희소성 점검) → 비평가 잔여 항목 8건 → 09 스크립트로 전부 실행.

## 0. 진행 정책 준수
- **정책1**: 주검정 = CFNAI-MA3(실시간 2개월 래그) + VIX(회의 전 28일 평균). 실업률갭·근원PCE갭은 E2 `robust+gaps` 열에만 사용 — 주결과 부호·유의성 유지 확인.
- **정책2**: 결론 선결정 없이 전수 스크린(BH-FDR) → 후보 발견 → **적대적 검증**으로 진행. 그 결과 초기 "스타 발견" 여럿이 사멸하고(아래 §4), 예상 밖의 새 구조(§2–3)가 드러남.

## 1. 피드백 1 — be-후행어 해소 결과
- 코퓰러 be head 4,223건 중 **91.9% 해소**(acomp/attr/prep/advmod → `predicate = be+보어`). 수동·진행·미래(be held/moving)는 기존 로직이 이미 어휘동사로 해소함을 확인.
- 드러난 것: **be appropriate 관용구군** — would+be+appropriate 303, will+be+appropriate 231, may+be+appropriate 79 (성명서: will 47, may 10). would+be+prepared 157. can의 보어는 화자 확신 형용사(patient 16, sure 7, confident 4).
- **관용구 내 조동사 선택의 이동**(minutes+press conf, be+appropriate 연도표): 2013–15 will 우세(포워드 가이던스) → 2018 will 0/would 23(정상화기 가정법화) → 2019 may 11·2023 **may 43**("additional policy firming *may* be appropriate" 국면) → 2021–22 will 복귀. 하나의 관용구 안에서 will/would/may가 **확신 눈금**으로 교체된다 — v1이 못 보던 현상.
- 논문 표 갱신: A1–A3, A5–A7 전부 predicate 기준 재생성(JSD 성명서 .76–1.0; would의 3위 collexeme가 be+prepared(2.9×)로 표면화).

## 2. 피드백 2 — 조동사×경기·후행동사×경기 (검증 생존 결과만)

### 2.1 총괄: 상관의 대상은 **불확실성(VIX)이지 실물(CFNAI)이 아니다** [CONFIRMED]
- E1의 BH-유의 12셀 중 11셀이 VIX; 유일한 CFNAI 셀(speech can)은 2020 인공물(excl-2020 부호 반전). 4개 장르 모두 6대 조동사 총밀도×CFNAI는 무상관(전체·excl-2020 공히), 반경기성 없음 — **Kawamura(2019, BoJ: 양태 반경기적)와 정반대**. 잔존 CFNAI 연계는 오히려 약한 순경기성(press conf 총밀도 excl-2020 r=+.36) 또는 국면-타이밍.
- E2 HAC 회귀의 유의한 CFNAI 계수 7개는 **전부 2020 인공물**(excl-2020에서 전멸·5개 부호 반전). 갭 추가·altlag 강건성 스펙은 이를 못 걸러냄 — 2020 제외가 필수 강건성 축임을 확인.

### 2.2 최강 셀: **minutes can × VIX (+)** [CONFIRMED, 한정]
- full r=.443/ρ=.464; excl-2020 r=.445/ρ=.443(p<1e-4); HAC b_vix=+.0094(p=.0002), 갭 추가 +.0066(p=.0003), altlag, excl-2020 +.0106(p=.0014), **국면 더미 추가에도 생존**(G5: b_vix p=.005, post2021 더미 n.s.); 이항(any-can) 지표만으로도 ρ=.43; can 포함 의사록의 사전 VIX 중앙값 18.9 vs 미포함 14.4(MWU p=2.6e-05); **2010–2026 확장에서도 생존**(G6: excl-2020 r=.30/ρ=.32).
- 한정: ① 얇은 계열(84토큰, 57% 제로) ② 반기별로는 2021–26에서만 유의(2014–19 ρ=.23 n.s.) ③ **AR(1) 프리화이트닝 시 소멸**(r=.036) — 회의 단위 혁신이 아니라 **저주파(국면) 공행**. 순환 시프트 검정은 통과(p=.024).

### 2.3 구문 수준(피드백 2.2): fair-weather / foul-weather / live-signal 3분법 [CONFIRMED]
- **Fair-weather(맑을 때만) 구문**: minutes would+expand·statement will+expand/warrant/evolve — VIX와 ρ=−.39~−.48(full·excl-2020 공히, CFNAI와는 무상관 = 불확실성 특이적). 핵심: minutes would+expand는 **자기 활성 기간(2014–18) 안에서도** ρ=−.40(p=.010) — 문장이 고VIX 회의에서 *보류*되었다. 2010–2026 확장 ρ=−.42.
- **Foul-weather처럼 보이는 것의 정체**: could+impede·would+be+prepared의 +VIX 상관은 **2020-09 일회성 채택 이벤트**의 산물(채택 후 리터럴 상수: 2021–26 의사록 43회 전부 be+prepared 정확히 2회). 스트레스 반응 언어가 아니라 위기-채택 정형문.
- **살아있는 신호**: minutes **would+be+appropriate**(n=247, 제로 회의 7%) — "it would be appropriate to [adjust/raise/maintain/reduce]" 심의 구문. VIX와 full ρ=.35/excl-2020 ρ=.31(r=.42), 2021–26 반기 내에서도 +, CFNAI와도 약한 +(ρ≈.23) — **정책 심의 강도의 실시간 지표**. G1: ANY be+appropriate(minutes)도 excl-2020 ρ=.28(q=.004).
- **집계의 은폐(masking)**: minutes would 총밀도는 VIX와 무상관(ρ=.10)이지만 내부 구문은 ρ −.48(expand)~+.38(be+prepared)로 정반대 — 조동사 집계 지표가 구문 신호를 상쇄·은폐한다. 역방향도 성립(will 유의, will+continue는 반대 부호). **양태 지표를 조동사 단위로 만들면 안 되는 직접 증거.**
- 의미 부류(G2 triage): 17개 유의 셀 중 생존 10 — will/mental(assess·monitor) × VIX **−**(statement ρ=−.45, minutes ρ=−.51 excl-2020), will/aspectual(continue) × VIX **+**(ρ=.39), would/copular_adj(minutes) +, would/activity(minutes) +, can/activity(press conf) +. 사멸 7(전부 2020 Pearson 레버리지). → 고불확실성 회의: "continue" 지속 서술↑·"assess/monitor" 평가 서술↓.
- statement 장르(excl-2020에서 드러남): will×VIX **−**(ρ=−.38; 2010–2026 확장 ρ=−.42) — 고VIX 시 성명서의 will 자체가 줄어든다. 단, would/could 동반 상승은 시대 구성(2020-09 이후) 효과라 대체 관계로 보고하면 안 됨(Simpson 역설 주의) [WEAKENED로 강등된 L4-2].
- G1 신규(be-해소가 가능케 한 발견): statement 코퓰러-형용사 보어 밀도 × VIX excl-2020 ρ=.39(q=.0000) — 불확실할 때 성명서는 서술어를 형용사 판단(appropriate/prepared 등)으로 옮긴다.

## 3. 피드백 3 — 선행지표 가능성 (정직한 결론)

### 3.1 문헌 근거(EVIDENCE_feedback3.md)
- 강함: 텍스트가 **정책금리·수익률·연준 자체 전망오차**를 선행 — Lucca & Trebbi(FFR FEV의 ~45% 6–12개월), Aruoba & Drechsel(연준 실업률 전망오차 1–2년 예측, R²≤.25), Kawamura(극성이 경기선행지수 3개월 선행, Granger 1%).
- 약함: **양태 고유의** 선행 증거는 문헌에도 없음 — Kawamura의 양태 상관은 월차분 시 소멸(n=207에서도). → 주장 문구는 "정책·기대를 선행"으로 제한하고 실물 선행성은 검정 결과로만 말한다.

### 3.2 우리 결과(2020 제외·희소성 정리 후)
- **사멸한 후보**: minutes neg_can "선행지표"(토큰 2개!); statement can→CFNAI Granger(토큰 4개, excl-2020 p=.46); press conf will×CFNAI k=+1 음(−.41→excl-2020 +.32 부호 반전).
- **생존한 시차 구조**(G3, excl-2020, Pearson·Spearman 동시 유의):
  | 특징 | 대상 | 피크 | 해석 |
  |---|---|---|---|
  | minutes could 밀도 | CFNAI | k=+6, r=−.45/ρ=−.32 | could↑ → 6개월 뒤 실물 둔화; Granger could→CFNAI **q=.040** |
  | statement will 밀도 | VIX | k=+4, r=−.42/ρ=−.48 | will↓ → 4개월 뒤 VIX↑; Granger will→VIX q=.066 |
  | statement will 밀도 | CFNAI | k=+3, r=+.29/ρ=+.25 | 약한 순방향 선행 |
  | press conf can | VIX | k=+7, r=.45/ρ=.41 | can↑ → 7개월 뒤 VIX↑ (해석 유보) |
  | press conf can→VIX·would→VIX | Granger | q=.040 | 역방향 n.s. |
  | minutes will+assess | VIX | k=−7, r=−.60 | **macro→text**(반응) — 방향 대조용 |
- **예측력의 한계**: F3 — CFNAI(+3m)·ΔVIX에 대한 증분 설명력, 113행 중 BH q<.10 **0건**(최소 q=.46). 결론 문구: *조동사 구문은 불확실성 국면의 동행·단기 선행 지표(설명 변수)로는 유의하나, CFNAI·VIX의 자체 지속성을 넘어서는 증분 예측력은 확립되지 않는다.*
- 사건창(F4): 기술적 참고용(2019 may 국면은 인하 선행, 2023 may 국면은 인상 정점 선행) — 인과 주장 없이 서사로만.

## 4. 인공물 처형 목록 (논문에 싣지 않을 것)
| 항목 | 사멸 사유 |
|---|---|
| statement/speech can×VIX, E1의 speech can×CFNAI | 2020 레버리지(excl-2020 소멸·부호 반전); statement can은 토큰 4개 |
| E2의 유의 CFNAI 계수 7개 전부 | excl-2020 전멸, 5개 부호 반전; Spearman 사전 경고 일치 |
| press conf can+do×VIX | 토큰 21%가 2020; 양쪽 반기 무상관 |
| minutes neg_can 선행지표 | 토큰 2개(1개는 추모문) |
| statement can→CFNAI 등 F2 최강 행들 | 희소 계열+2020 |
| E3 novel×VIX(r=.20) | excl-2020 r=−.06 (G4) |
| C6 편집 강도×VIX(r=.37) | ρ=.11, excl-2020 r=−.04 — 편집 강도는 불확실성이 아니라 **정책 국면 전환**을 따름 |
| E6의 "2010–2026" 블록 | B1이 2014 시작이라 전 표본과 동일(무의미) → G6로 진짜 확장 재계산 완료 |

## 5. v1 논지에 대한 함의
- "edited formulaicity"는 강화됨: 거시 신호조차 (i) 문장 **보류/채택 결정**(fair-weather 보류·2020 채택)과 (ii) 의사록의 심의 관용구(would be appropriate)에 산다. 집계 양태는 신호를 은폐한다.
- Kawamura 대비: BoJ의 "불리할 때 모호성↑(활동지수 반경기)"는 FOMC에서 재현되지 않음. FOMC의 상관 축은 활동이 아니라 **불확실성**이고, 그마저 저주파 국면 공행이다.
