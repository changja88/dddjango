# dddjango 2.21.1 — «타 BC 이름» 낱말 검사는 같은 컨테이너의 BC 만 센다 (F4-87)

## 현장 보고

- F4-87(10-1 G0 · 2026-10-12 14:57 · 낮음): `check-context-isolation` #364(포트 이름에 공급자 BC 이름 금지)가
  자매 플러그인 dddjango-web 의 화면 구역 이름(`web/application/chart` · `shared_chart`)까지 «다른 BC 이름» 으로 세어,
  낱말 chart 가 든 서버 포트 이름 15 건을 붉게 잡았다. 서버 업무 영역 가운데 chart 는 없다.
- 바라는 결과: #364 의 «영역 이름» 집합을 서버 업무 영역(`application/<영역>`)으로 한정 · web 화면 구역 이름은 세지 않는다.
- 덧붙임(16:19 · 10-1 G1 STOP-2): `web_test/application/` 도 컨테이너로 잡혀 web 화면 폴더 이름(chart · shared_chart · birth_hour ·
  preferences · showcase · client · admin …)이 든다 · #364 와 #151 이 새 이름 9 건(chart_establishment · chart_reading …)을 예보 red →
  10-1 은 G1 앞에서 수리판을 기다림(낮음 → 높음).

## 원인

검사기가 BC 를 `target.rglob("application")` 로 모은다. `web/application/` 도 컨테이너로 잡혀 그 아래 화면 구역 이름이
저장소 전체 이름 집합(`all_bcs` · `business_vocab.bc_names`)에 섞이고, 낱말 검사가 그 집합을 «타 BC 이름» 으로 썼다.

같은 집합을 같은 판정(«이 이름 낱말에 다른 BC 이름이 있나»)에 쓰는 자리가 셋이다 — 셋 모두 2.21.0 에서 재현했다.

| 규칙 | 검사기 | 재현(2.21.0) |
| --- | --- | --- |
| #364 포트 파일 · 폴더 이름 | check-context-isolation `_check_ports` | `web/application/chart` + `port/chart_load/` → #364 2 건 |
| #151 창구(OHS) 이름 | check-context-isolation `_check_ohs` | `web/application/chart` + `open_host_service/chart_lookup/` → #151 1 건 |
| #233 조회 능력 폴더 이름 | check-port-adapter-pairing `_check_bypass` | `web/application/chart` + `domain_bypass_query/chart_board/` → #233 1 건 |

## 고침

- `business_vocab.container_bc_names(bc)` — `bc` 가 든 `application/` 컨테이너의 BC 이름(자기 포함).
- #364 · #151 · #233 은 이 집합에서 자기 이름을 뺀 것을 «타 BC 이름» 으로 쓴다. 메시지 · 다른 규칙은 그대로.
- 그대로 둔 것: `_scan_imports` 의 import 경로 판정(`application.<x>` 이 BC 인지 — 이름 낱말 판정이 아니다) ·
  #365(ACL 대상이 우리 BC 인지 — 저장소 전체 이름이 맞다).
- 자매 선례(F4-56 · F4-63 의 `anchor_diff.sister_owned` · `sister_path`)를 쓰지 않은 까닭: 그 판정은 «발견이 놓인 경로» 를
  web 쪽으로 가르는 것이다. 이번 발견은 서버 경로(`application/<bc>/…`)에 놓이고, 틀린 것은 비교에 쓴 이름 집합이다.
  같은 컨테이너로 한정하면 web 표식(`.dddjango-web/`)이나 manage.py 판정 없이도 같은 결과가 나고, web 구역끼리의 검사
  (이 검사기가 `web/application/<단위>` 도 BC 로 도는 경우)도 web 구역 이름끼리만 비교한다.

## 시험

- 덧붙임 경우(`web_test/application/chart` 만 있음 · 서버 포트 `chart_reading`) — 2.21.0 #364 2 건 · 고친 판 0 건(운영자 손 재현).
- `field_report_checker_smoke.OtherContainerNameRegression` 3 건 — 규칙마다 «web 구역 이름은 안 셈(0) · 같은 컨테이너의
  서버 BC 이름은 그대로 셈(#364 · #151 · #233)». 2.21.0 검사기로 돌리면 3 건 모두 붉고, 고친 판에서 3 건 모두 통과.
- 기존 묶음: findings 계수 73 / 73(메시지 · 지문 무변) · 픽스처 표 107 / 107 · smoke 76 / 76.
- pre-gate 소스 지문(`pregate_symbol_kinds.json`) 재생성 — 두 검사기 소스가 바뀌었다.

## 범위 밖(관찰 · 다음 판 후보)

같은 뿌리(저장소 전체 `application/` 아래 이름 = 서버 BC 이름)지만 판정이 다르거나 이미 있던 사각이라 이번에 바꾸지 않았다.
10-1 레인이 이 판을 기다리고 있어 범위를 F4-87 의 판정(BC 마다 «남의 BC 이름 낱말») 셋으로 묶었다.

- framework «BC 이름 0»(#52 · #416 · #426 — check-business-vocabulary `bc_names(root)`): web 구역 이름이 BC 로 세어진다.
  Claude 검토 재현 — web 구역 `settings` + framework 의 `from django.conf import settings` → #52 붉음(오탐). BC 마다가 아니라
  «framework 에 어떤 BC 든» 판정이라 같은 컨테이너 집합은 맞지 않는다 — 서버 컨테이너로 좁히거나 자매 뿌리(`_SISTER_ROOTS`)를 빼는 쪽.
- #365(ACL 상대가 우리 BC 인가 — check-port-adapter-pairing `bc_names(root)`): web 구역 이름이 «우리 BC» 로 통과시킨다.
  Claude 검토 재현 — `acl/chart/` 가 urllib 를 import 해도 web 구역 `chart` 가 있으면 #365 가 사라진다(놓침).
- 여러 낱말 BC 이름(`fortune_saju`)은 #151 · #233 · #364 가 낱말 하나와만 맞춰 보아 원래 못 잡는다(옛 판 = 새 판). 이 판정을
  넓히려면 같은 컨테이너 한정이 먼저 있어야 한다(web 구역 `shared_chart` 등) — 이번 수리가 그 전제다.
- #444(celery packages 식) · `all_vocab`(#47 · #518 · #562 · #617)도 저장소 전체 이름 · 어휘를 쓴다(위험 낮음 · 오탐 단정 불가).

## 검토 · 검증

- Codex 독립 검토(gpt-6.1-sol · xhigh · 읽기 전용): 차단 0 · 사소 0.
- Claude 독립 검토: 차단 0 · 사소 5 — ① 봉인(커밋 뒤 봉인 chore 로 처리) ② · ③ · ④ 위 «범위 밖» ⑤ #233 시험을 정확 일치로(반영).
  기존 verify 묶음(픽스처 · 계수 · 기준선 · cross · smoke · registry_gate_smoke 등) 전부 green 을 따로 확인.
- `make verify`: green 6/6(771 초 · 기능 커밋 `11ee7ef0` + 봉인 chore `00c0e46e` 위 · 운영자 실행). 그 뒤 #233 시험 정확 일치(사소 ⑤)는 그 시험 묶음만 다시 돌림 — 배포 안 verify 가 최종 트리를 다시 잰다.
