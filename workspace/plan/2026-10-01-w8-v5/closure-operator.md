# 닫힘 확인(운영자) — W8 작은 판 구현 리뷰 M1·M2·minor 4 (2026-10-02 00시)

대상 `89ae4738`(design/w8-v5) · 사본 scratch `closure-w8/repo` · 리뷰 원문 `review-impl-claude.md` 의 재현 명령을 그대로 다시 돌렸다.

| 지적 | 재현 | 수정 전(리뷰) | 수정 뒤 |
|---|---|---|---|
| M1 있는 토큰을 «신규 등록 필요» | P1 시안 census(측정 사본) + spring_dream 실제 `tokens.css` 로 시트 | `color(srgb…)` 282행 후보 0 · 리뷰 실례 5토큰 모두 «신규 등록 필요» | `--glass-tint-strong` · `--shadow-2` · `--success-soft` · `--surface-muted` · `--font-sans` 모두 일치 · «신규 등록 필요» 0 · 일치 190/314 · 수동 확인 124(해석 못 한 토큰이 걸린 속성 · 분류 미지원 — 보수 처리) |
| M2 시트 크기·잡음 | 같은 명령 | P1 1,108,053B · 46.6초 · P2 790,258B · 37.1초 | P1 87,938B · 0.57초 · P2 71,871B · 0.37초 · 기본값 행 제외 · 속성 종류 한정 후보 · 값 → 토큰 색인 |
| minor 1~4 | 구현자 시험(`fixtures_style_census.sh` 35) | 실패 재현(구현자 기록) | 35 OK |
| 판정 보존 · 결정성 | 리뷰어 `my_replay.py` 시드 0·3 | — | 6회차 모두 eq_v4_live · eq_saved · P1 G2#1 T 35/35 · prod_sha 시드 무관 동일(리뷰 때 값과 같음) |

착지 사본(main `6a188c02` + cherry-pick 5 + 봉인 `259ec081`): `make verify` 5/5 · `make verify-web` exit 0(W8 35 tests). 판정: 닫힘.
