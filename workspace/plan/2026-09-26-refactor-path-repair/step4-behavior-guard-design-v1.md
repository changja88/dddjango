# 로드맵 4 — 동작 보존 장치(최소판) 설계 v1 (2026-09-26 밤 · 적대 검토 전)

- 바탕은 `diag-B2-behavior-evidence.md`(설계 초안)다. 이 문서는 그 초안에 사용자 결정을 적용한 결과와 남은 쟁점만 적는다. 측정 설계의 세부(§2.0~2.5)는 초안을 그대로 쓴다.
- 사용자 결정(`evening-report.md` §5 결정 2):
  - Q1 **(가)** 정리(슬라이스 0)가 들어가는 **모든 작업**의 리팩터 창에 적용한다.
  - Q2 **(가)** OpenAPI 문서 층(operationId · 스키마 이름표 · summary/description/tags · info)은 **보고만** 한다. 내용(wire 층)은 red 다.
  - Q3 **(다)** 약한 단언 강화(§2.6)는 이번에 빼고 리팩토링 커맨드 설계(로드맵 5) 때 정한다.
- 범위: dddjango 만. dddjango-web 판(확인 대상이 화면)은 로드맵 6 에서 따로 설계한다.

## 1. 채택 범위 = 초안 §5 «최소판»

| 불변식 | 판정 | 초안 절 |
|---|---|---|
| 보호 테스트 무편집(P = `application/*/test/e2e/**` ∪ G0 스코프 메모 «동결 테스트 경로») | Δ≠0 red · P 공집합이면 «보호막 0» 경고 | §2.1 |
| 마이그레이션 무변 — 정적(`**/migrations/*.py` 집합) + 런타임(`makemigrations --check --dry-run` 정규화 출력 open=close) | Δ≠0 red | §2.2 |
| OpenAPI W 층(path×method 의 parameters · requestBody · responses · security — `$ref` 해소 · title 제거 · 정렬) | Δ≠0 red · D 층은 보고 | §2.3 |
| OHS · published_event 공개 표면(정적 AST) | 제거·변경 red · 추가 보고 | §2.4 |
| URL 목록(결합 route · `namespace:name` — admin 포함) | Δ≠0 red | §2.5 |

- 판정 exit: 0 = 불변 · 2 = 불변식 diff · 4 = 일부 미측정(사유) · 1 = 사용 오류/open 부재/재료 결손.
- 사용자 승인 diff 는 `--accepted-file`(항목 ID + 사용자 원문 인용)로 exit 에서 뺀다. 원문 요건은 이번 수리의 ⓑ 출처 규칙과 같다(본인 직접 또는 사용자 원문 파일:행).
- red 처방: 1차 = 원인 편집 철회 → 불가면 `STOP_FOR_USER_APPROVAL`. 미측정(4)도 STOP 이다(조용한 green 금지).

## 2. 소속

- 새 스크립트 `dddjango/scripts/behavior_guard.py`(stdlib · capture/compare)와 `behavior_probe.py`(프로젝트 인터프리터로 실행 · 플러그인 import 0)를 둔다. Codex byte 미러를 두고 봉인 글롭에 추가한다.
- 역할:
  - Coordinator: 캡처 · 비교 · 배너를 하는 유일한 실행자다.
  - coder: 보호 목록을 입력으로 받고, P 편집이 필요하면 편집하지 않고 STOP 한다.
  - discipline-reviewer: `report.md` 를 입력으로 받는다(D 층 · 창 이후 재편집).
- 규범(graph-owned): `command-dddjango`(산출물 위치 · Phase 2 step 3~7 · 수정 모드 · Phase 3) · `agent-coder` · `agent-discipline-reviewer`. 초안 §3 표를 따른다.
- G2 배너 1행(안): `동작 보존(창 S0~Sk): 보호테스트 Δ0(P n파일) · migrations Δ0/--check 동일 · OpenAPI W Δ0 (D n 보고) · OHS Δ0 (+m) · URL Δ0 · 미측정 0 · 창 이후 재편집 r파일`
- G2 제시 금지 조건: open 부재 · 승인 안 된 W/Δ · 승인 안 된 미측정.

## 3. 초안 대비 바뀐 점

1. 적용 범위는 초안의 «권장 (가)»가 결정으로 섰다. B1 이후 서비스 레인 거의 전부에 슬라이스 0 이 생기므로, 레인당 probe 2회가 기본 비용이다.
2. §2.6(보호 강화 슬라이스)와 G0 «불변식 충돌 예상» 표시는 이번 범위 밖이다(완전판 · 로드맵 5 에서 재론).
3. 리팩토링 커맨드(로드맵 5)는 창 = Phase 2 전체로 이 장치를 그대로 쓴다. 인터페이스(capture/compare · exit · report)를 그때 바꾸지 않도록 이번에 확정한다.

## 4. 적대 검토에 묻는 것

1. **런타임 probe 취약성**: `django.setup()` 을 한 프로세스가 import 시점 DB 질의 · `.env` · 설정 차이로 실패할 빈도. 실패하면 미측정 STOP 이 쏟아져 사용자 게이트 비용이 커지지 않는가. spring_dream 기준으로 실제로 setup 이 되는가.
2. **보호 테스트 무편집 규칙과 입장 표 규범의 충돌**: 영구 테스트 입장 표가 `update`·`move` 로 승인한 e2e 편집(정당한 계약 변경 슬라이스)이 창 안에 들어오는 경우. 창은 «리팩터 슬라이스»만이라 했지만, 슬라이스 0 이 e2e 가 import 하는 factories 를 옮기면(#390·#383~#392) e2e 편집이 강제된다(초안 §2.1). 이 충돌을 G0 에서 미리 보여 주지 않으면 슬라이스 0 마다 STOP 이 나지 않는가.
3. **창 경계**: acceptance-tester 산출 뒤·첫 리팩터 coder 파견 전이 open 이고, 마지막 리팩터 슬라이스 보고 뒤가 close 다. 슬라이스 0 이 여러 개거나 G1′ 반송 · STOP 재개 · 세션 재시작 · main 머지가 창 안에 끼면 거동이 정의돼 있는가.
4. **OpenAPI W 층 정규화의 거짓 red**: `$ref` 인라인 해소 뒤에도 스키마 이름이 바뀔 때 남는 차이(discriminator mapping · `allOf` title · enum 이름 등).
5. **Coordinator 부하**: 이미 고밀도인 프롬프트에 호출 2회 + 배너 1행 + 금지 조건 3을 더하는 것이 준수율을 떨어뜨리지 않는가. 더 줄일 수 있는가.
6. **빠진 것**: 동작 보존의 실제 위험(celery task 이름 · signal 수신자 · pickle 경로 · settings 점 문자열)이 이 5표면 밖에서 얼마나 자주 깨졌는가(현장 증거가 있다면).
