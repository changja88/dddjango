# 로드맵 4 — 동작 보존 장치(최소판) 설계 v2 (2026-09-27 · 적대 검토 G 반영)

- v1 → v2: 적대 검토 G(`review-G-step4.md` — blocker 2 · major 11 · minor 7)를 전건 처분했다(§8 표).
- 바탕: `diag-B2-behavior-evidence.md` 의 측정 세부. 이 문서가 초안과 다르면 이 문서가 우선한다.
- 사용자 결정(결정 2 — Q1 가 · Q2 가 · Q3 다)은 그대로 적용한다.
- 현장 사실(검토 G 실측):
  - SDS 는 `settings.test` 로 DB 0 · env 0 · 약 5~8초에 probe 가 돈다.
  - 리팩터 뒤 실제로 깨진 사례는 다섯 표면 **밖**(옛 참조가 문자열로 남음)이 가장 많다.
  - OpenAPI W 층이 잡은 과거 사례는 0 이다(K1 구체형 수리의 예상 위험에 대한 대비).

## 1. 창(window)과 실행 시점

- **창** = 리팩터 슬라이스(슬라이스 0) 연속 구간. 한 실행에 창이 여러 개일 수 있다(`--window k`). 예: G2 때 «미룰 수 없음» 재상정이 G1′ 경유로 슬라이스 0 을 새로 만든 경우.
- 명령 세 개. 창 상태 · 실행 결합 · 입력 고정은 스크립트가 소유한다.
  - `behavior_guard.py open --window k` — 창 k 의 첫 리팩터 슬라이스 파견 **직전**(acceptance-tester 산출 뒤)에 한다.
  - `behavior_guard.py close --window k` — 창 k 의 마지막 리팩터 슬라이스 보고와 그 경량 감사 반영을 받은 **뒤, 다음 파견 전**에 한다. **캡처와 비교를 함께 한다.** exit ≠ 0 이면 다음 슬라이스를 파견하지 않고 그 자리에서 red 처방을 한다(§5).
  - `behavior_guard.py verify` — G2 배너 직전에 한다. 모든 창의 close 판정을 재확인하고, 창 이후 재편집을 집계한다. 출력은 `요약:` 1행이다.
- 경계 규칙:
  - ① **병렬 파견 예외**: 창의 마지막 슬라이스는 감사 반영이 끝난 뒤 close 하고, 그다음에 파견한다(C «슬라이스 ≥3 병렬 배차 가능»의 예외).
  - ② **다중 창**: 창 k 의 open 은 그 리팩터 슬라이스 파견 직전이다. 앞 창과 기능 슬라이스의 결과는 창 k 의 기준선에 들어간다.
  - ③ **창 안 main→레인 머지 금지**: 머지가 필요하면 close → 머지 → 새 창 open 으로 끊는다. 머지 provenance 차분은 만들지 않는다.
  - ④ **세션 재시작**: `refactor-scope.md` 실행 줄에 `· 창k open <시각>` / `· 창k close <시각>(green|red)` 을 덧붙인다. 기존 «실행 줄 기계 기록» 채널이고, 사후 개정이 아니다.
  - ⑤ **폴더 재사용**: `open.json` 에 실행 식별자(실행 줄의 G0 승인 시각 + `build_anchor`)를 적는다. close/verify 는 현재 실행 줄과 다르면 exit 1 로 거부한다.

## 2. 입력 고정 (M-1)

- settings 는 pytest 설정의 `DJANGO_SETTINGS_MODULE`(pyproject/pytest.ini/setup.cfg)로 정한다. 없으면 G0 에서 사용자에게 한 번 묻는다. `manage.py` 기본값은 쓰지 않는다.
- `open.json` 에 다음을 적는다. close 에서 하나라도 다르면 exit 1 이다.
  - settings
  - 인터프리터 경로 · `sys.version` · Django/ninja 버전
  - env 허용 목록의 값 해시: settings 모듈이 `os.getenv`/`os.environ` 으로 읽는 이름을 정적으로 모은 것. 값 자체는 적지 않는다.
- probe 는 import **전에** DB 접속 가드(`BaseDatabaseWrapper.connect` 차단)를 건다. 기동 중 접속 시도는 «미측정(DB 필요)» 사유가 된다.

## 3. 표면과 판정

모든 표면에 공통 원칙(B-1): **측정 산출물이 없으면 값이 아니라 미측정이다.** open 과 close 가 같은 방식으로 실패한 것을 «무변»으로 읽지 않는다.

| # | 표면 | 측정 | red | 보고(비차단) |
|---|---|---|---|---|
| 0 | **boot** | probe 프로세스 `django.setup()` · URLconf import | open 성공 ∧ close 실패(트레이스백 마지막 줄) — 승인 불가 | — |
| 1 | 보호 테스트 P | P = e2e ∪ **창 대상 BC 밖의 모든 테스트 파일**(다른 BC `test/**` · 루트 `tests/**` · 기타 테스트 루트). 파일별 «import 문을 뺀 AST 해시» | 본문 변화(assertion · case · fixture 본문) · 추가/삭제 · G1 입장 표 재조직 행과 안 맞는 이동 | import 줄만 바뀐 파일 n · G1 재조직 행과 맞는 이동 |
| 2 | 마이그레이션 | 정적: `**/migrations/*.py` 경로→blob. 런타임: probe 안에서 `MigrationLoader(None, ignore_no_migrations=True)` + `MigrationAutodetector.changes()` 를 `translation.override(None)` + DB 가드 아래 실행 → 변경 목록(앱 · 연산 describe) | 정적 Δ · 변경 목록 open≠close | — |
| 3 | OpenAPI W | ROOT_URLCONF 에서 NinjaAPI 발견 → `get_openapi_schema()` → W 정규화(§3.1) | W Δ | D 층(§3.1) |
| 4 | OHS 공개 표면 | 모듈에서 **정의한** 이름(def · class · 주석 붙은 대입) ∪ `__all__` ∪ `open_host_service/**/contract/`·`published_event/` 정의로 향하는 재수출. 시그니처 주석은 이름으로 비교(경로 해석 없음) | 제거 · 변경 | 추가 |
| 5 | URL | route(결합 문자열 — 정규식 alternation 은 정렬) · 이름 · admin `site._registry`(app_label, model) 집합 | route Δ · admin/web 이름 Δ · admin 등록 집합 Δ | Ninja API namespace 이름 Δ(D) |
| 6 | 시스템 체크 · settings 점 문자열 | 등록 체크 함수 **이름** 집합 · `INSTALLED_APPS`·`MIDDLEWARE`·`STORAGES[*].BACKEND`·`AUTH_USER_MODEL`·`CSRF_FAILURE_VIEW`·`TEMPLATES` context processor 의 해석 결과 | 체크 이름 제거 · 해석 실패 | 체크 이름 추가 |
| 7 | **옛 참조 잔존**(M-11) | 창에서 삭제 · 이동된 Python 모듈의 옛 dotted 경로 · 옛 파일 경로(개명된 BC·app_label 이면 옛 식별자)를 close 트리 전체(`.py`·`.md`·`.json`·`.toml`·`.yml`·`.html`·`.js`·`env/*.sample`·`Makefile` — `.dddjango/`·`docs/` 제외)에서 grep | — | 적중 파일:행 전건 → 감수자 판정 |

### 3.1 OpenAPI W/D 정규화 규칙 (M-7)

- description · summary · example(s) · title 은 **모든 깊이에서** D 로 보낸다.
- `$ref` 는 형제 키가 있어도 해소한다. 형제 키는 병합한 뒤 위 규칙을 적용한다.
- `discriminator.mapping` 의 값(스키마 이름)은 해소된 구조의 해시로 바꾼다.
- 순환은 `{"$cycle": k}`(조상 스택 깊이)로 표지하고 이름을 쓰지 않는다.
- security 는 스킴 이름 대신 `components.securitySchemes[이름]` 정의(type · in · name)로 바꾼다.
- operationId · components 이름 · tags · info 는 D 다.
- 알려진 사각(m-5): 값 수준 의미(pydantic strict · validator · serializer · ninja `resolve_*`)는 모양 비교로 보지 못한다. 이 사각의 오라클은 e2e 뿐이므로 배너에 «보호막» 수치를 함께 적는다.

## 4. 산출과 저장 (m-2 · m-3)

- `<산출물 폴더>/behavior/`:
  - `open-w<k>.json` · `close-w<k>.json`: 실행 식별자 · 입력 고정값 · 표면별 정규형 해시와 항목 목록. 원문은 싣지 않는다.
  - `report.md`: Δ 전건 · D 층 · 옛 참조 잔존 · 창 이후 재편집. 마지막 줄은 `요약:` 이다.
- tree SHA 에 기대지 않는다(gc 로 사라질 수 있다). 슬라이스 0 커밋이 있으면 그 SHA 를 close 기준으로 병기한다.
- 원문 캡처는 임시 폴더에 두고 지운다.

## 5. red 처방 (M-10 · B-2)

- close 의 red 처방은 C «슬라이스 0 과 비위반 이동의 STOP»과 같다.
  - 1차: 원인 편집을 철회한다(창 안이라 기능 슬라이스가 아직 없다).
  - 철회로 끝나지 않으면 STOP. 선택지는 «철회해 별도 요청으로 / 출처 있는 ⓑ(항목을 슬라이스 0 에서 뺌) / 작업 중단 / 장치 오탐(측정 결함)»이다. 답은 `ⓐ 재상정` 절에 쓴다.
- `--accepted-file` 은 **«장치 오탐» 처분에만** 쓴다.
  - 소유자는 Coordinator 다(사용자 답의 기계 기록).
  - 경로는 `behavior/accepted.txt` 다.
  - 줄 형식: `<항목 ID> · 장치 오탐 · 출처 = 본인 직접(<시각>) | 사용자 원문 <파일:행>`. `ⓐ 재상정` 결정 줄과 짝을 이룬다.
  - 실행 식별자를 달아 다음 실행으로 이월하지 않는다.
  - boot 항목은 받지 않는다.
- 항목 ID = `<표면>:<경로 또는 op>:<정규형 해시 12자>` 다. 재실행 사이에도 안정적이다.
- open 이 환경 사유로 미측정이면(m-6), 실행마다 한 번 «정적 표면만 측정 · 출처»를 결정 줄 정형으로 받는다. 같은 실행 안에서는 다시 묻지 않는다.
- close 의 미측정(open 은 됐는데 close 에서 환경 사유)은 STOP 이다. «앱 기동 실패»는 미측정이 아니라 boot red 다(M-2).

## 6. 역할과 규범 (M-3 · M-6 · m-4)

- Coordinator 문면은 세 문장으로 한다(graph-owned `command-dddjango`).
  - ① 슬라이스 0 이 있으면 그 첫 파견 직전에 `open`.
  - ② 마지막 리팩터 슬라이스 보고와 감사 반영을 받은 뒤, 다음 파견 전에 `close`. exit ≠ 0 이면 파견하지 않고 red 처방(§5).
  - ③ G2 배너에 `verify` 의 `요약:` 행을 그대로 싣는다. exit ≠ 0 이면 G2 금지(7번 금지 목록 한 항목).
  - 창 경계 예외(§1 ①)는 Phase 2 병렬 배차 문장에 한 구절로 둔다.
- coder(`agent-coder`): 보호 목록 P 를 받는다. P 편집이 필요하면 **편집하지 말고 보고**한다. Coordinator 가 G1 입장 표 재조직 행 유무로 acceptance-tester 파견 또는 STOP 을 정한다.
- discipline-reviewer(`agent-discipline-reviewer`): close 가 만든 `report.md`(D 층 · 옛 참조 잔존 · import 전용 수정)를 슬라이스 0 경량 감사 입력으로 받는다. «창 이후 재편집»은 홀리스틱 감사 직전에 한 번 집계해 준다.
- Codex 의미 미러 3곳과 스크립트 byte 미러를 둔다. 봉인 글롭에 새 스크립트 2종을 추가한다.
- 인용 앵커는 줄 번호가 아니라 절 이름으로 잡는다(m-1).

## 7. 검증 계획

- **탐지 시험**(동작을 일부러 바꾼 사본 — scratch clone `sds-main` 위 임시 커밋 · `settings.test` · DB 가드): 표면마다 양성 1 이상 · 음성(순수 이동) 1 이상.
  - boot: urls 가 import 하는 모듈을 옮기고 소비처를 빠뜨린다 → red.
  - P: e2e assertion 수정 → red · factories 이동 + import 줄만 수정 → 보고.
  - 마이그레이션: 모델 필드 삭제 → red · 모델 클래스 파일 이동(등록 유지) → 무변.
  - W: Schema 필드 제거 → red · Schema 개명 + docstring 수정 → D 보고만.
  - OHS: 공개 함수 시그니처 변경 → red · application_layer 이동으로 import 경로만 변경 → 무변.
  - URL: admin 등록 누락 → red · Ninja 메서드 개명 → D.
  - 체크: `ready()` 의 import 누락 → red.
  - 옛 참조: 모듈 이동 뒤 `import_module("옛.경로")` 문자열 잔존 → 보고 적중.
  - B-1 회귀: 시스템 체크 오류 상태에서도 마이그레이션 변경이 잡힌다.
- `behavior_guard_smoke.py`(W 정규화 5규칙 · 항목 ID 안정성 · 실행 식별자 거부 · 미측정 ≠ 무변) → verify 등재. 런타임 부분은 메인테이너 `.venv` 에 Django 가 없으면 skip 을 **명시 출력**한다.
- 행동 시험: 슬라이스 0 이 있는 레인을 Coordinator 로서 재현해 open/close 시점 · red 처방 · G2 금지를 확인한다.

## 8. 검토 G 처분

| 발견 | 처분 | 위치 |
|---|---|---|
| B-1 마이그레이션 조용한 green | 수용 — probe 안 autodetector · 미측정 ≠ 무변 일반 원칙 | §3 · §3 표 2 |
| B-2 compare 가 G2 직전 | 수용 — close = 캡처 + 비교 · 실패 시 파견 금지 | §1 · §6 |
| M-1 입력 미고정 | 수용 — pytest settings · 입력 해시 · DB 가드 | §2 |
| M-2 close 기동 실패 = 미측정 | 수용 — boot red · 승인 불가 | §3 표 0 · §5 |
| M-3 P ↔ 재조직 충돌 | 수용 — import 제외 AST · G1 재조직 행 대조 · coder 보고 | §3 표 1 · §6 |
| M-4 P 범위 | 수용 — 대상 BC 밖 전 테스트 · 새 입력 줄 없음 | §3 표 1 |
| M-5 창 경계 5 | 수용 — 병렬 예외 · 다중 창 · 머지 금지/끊기 · 실행 줄 창 표지 · 실행 식별자 | §1 |
| M-6 감수자 입력 시점 | 수용 — close 산출을 슬라이스 0 감사에 | §6 |
| M-7 W 거짓 red 5 | 수용 — 정규화 5규칙 + smoke | §3.1 · §7 |
| M-8 OHS import 이름 | 수용 — 정의 이름 기준 | §3 표 4 |
| M-9 URL 이름 | 수용 — Ninja 이름 D · alternation 정렬 · admin 등록 집합 | §3 표 5 |
| M-10 accepted-file 제3 경로 | 수용 — 장치 오탐 전용 · 재상정 절과 짝 | §5 |
| M-11 사각 목록 · 옛 참조 | 수용 — 표면 6 · 7 추가(7 은 비차단 보고) | §3 표 6·7 |
| m-1 줄 번호 | 수용 — 절 이름 앵커 | §6 |
| m-2 tree SHA 소실 | 수용 — 표면 결과 직접 저장 | §4 |
| m-3 산출 크기 | 수용 — 해시·목록만 | §4 |
| m-4 Coordinator 부하 | 수용 — 3문장 · 금지 1항목 | §6 |
| m-5 값 수준 사각 | 수용 — 사각 명시 · 보호막 수치 | §3.1 |
| m-6 open 미측정 반복 | 수용 — 실행당 1회 결정 | §5 |
| m-7 manage.py 조건 | 수용 — «settings 미확정»으로 | §2 |
