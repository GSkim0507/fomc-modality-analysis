# C24 S6 — unfiltered 4 genres (v2-like) × modal + predicate

## 코퍼스 (T1)

| 층위 | 문서 | 토큰 | 6대 조동사 | pmw (95% CI) |
|---|---:|---:|---:|---|
| Statement | 101 | 41,906 | 770 | 18,374 (17,099–19,719) |
| Statement (vote line) | 100 | 5,441 | 10 | 1,838 (881–3,380) |
| Minutes: Desk/markets (staff) | 99 | 71,942 | 553 | 7,687 (7,059–8,355) |
| Minutes: staff review & outlook | 99 | 249,885 | 539 | 2,157 (1,979–2,347) |
| Minutes: participants' views | 99 | 223,992 | 2,756 | 12,304 (11,849–12,772) |
| Minutes: Committee policy action | 99 | 62,833 | 958 | 15,247 (14,296–16,244) |
| Minutes: special topics | 40 | 40,777 | 783 | 19,202 (17,880–20,595) |
| Minutes: front matter | 99 | 59,650 | 78 | 1,308 (1,034–1,632) |
| Minutes: quoted statement | 99 | 40,613 | 761 | 18,738 (17,430–20,118) |
| Minutes: quoted directive | 99 | 22,084 | 102 | 4,619 (3,766–5,607) |
| Minutes: vote & post-vote | 99 | 16,987 | 166 | 9,772 (8,342–11,377) |
| Minutes: SEP addendum | 0 | 0 | 0 | 0 (0–3,688,880) |
| Minutes: authorizations/boilerplate | 99 | 65,197 | 376 | 5,767 (5,199–6,381) |
| Press conf.: Chair | 80 | 533,106 | 10,686 | 20,045 (19,666–20,428) |
| Press conf.: journalists | 80 | 138,373 | 2,452 | 17,720 (17,026–18,436) |
| Press conf.: moderator | 49 | 1,981 | 83 | 41,898 (33,372–51,939) |
| Press conf.: pre-marker | 2 | 18 | 0 | 0 (0–204,938) |
| Chair speech | 124 | 234,853 | 3,203 | 13,638 (13,170–14,119) |

- L2 층위 × 조동사: χ²=8953.4, V=0.274
- L3 성명서 계단: 변화점 25개, 사건 ±1회의 17개
- L5 보유율 반감기: all=16.8, will=18.1, would=≥24, could=≥24, can=1.0, should=7.5, may=4.0, modal_sentences=4.5
- E5 ledger: VIX 확정 9 / 시대구성 31 / 2020의존 9; CFNAI 확정 8 / 8 / 2

## 가설

- H1: **지지** — 변화점 25개 중 사건 ±1회의 17개; 보유율 반감기 16.84087019382264
- H2: **지지** — χ²=8953.4, V=0.274
- H3: **기각** — 수준 회귀에서 어떤 층위의 총밀도도 CFNAI와 유의한 음의 관계 없음; 1차 차분에서도 없음
- H4: **부분** — 확정 VIX 단위 9 (비성명서 층 8, 성명서 층 1)
- H5: **기각** — Granger text→macro q<.10: 0건 (최소 q=0.37771446608365733); 예측 회귀 q<.10: 0/70 (최소 q=0.4788896821693258)