# 적대 검토 G — 로드맵 4 동작 보존 장치(최소판) 설계 v1 (2026-09-26 밤)

- 대상: `step4-behavior-guard-design-v1.md`(이하 D4) · 바탕 `diag-B2-behavior-evidence.md`(이하 B2) · 사용자 결정 `evening-report.md` §5 결정 2.
- 규범 대조: `dddjango/commands/dddjango.md`(C) · `dddjango/agents/coder.md` · `acceptance-tester.md`(AT) · `discipline-reviewer.md`(DR).
- 현장: `/Users/hyun/Desktop/spring_dream_server`(SDS) — 읽기만 했다(파일 쓰기 0 · git 상태 변경 0 · manage.py·검사기 실행 0).
- 실측: scratch clone `bt/sds-main`(HEAD `12d876dcc`)에서만 돌렸다. 인터프리터 = SDS `.venv/bin/python`(Python 3.14) · `PYTHONDONTWRITEBYTECODE=1`. 실행 전후 `git status --porcelain --untracked-files=all` 이 같음을 매번 확인했다(CLEAN). 산출물·스크립트는 scratch `rv4/`(`probe1.py`·`probe2.py`·`probe3.py`·`wlayer.py`·`probe-*.json`).
- DB 접속: 하지 않았다. 모든 probe 는 `BaseDatabaseWrapper.connect` 를 막는 가드를 걸고 돌렸다. `probe3.py` 는 가드를 `django.setup()` **전에** 걸었고 접속 시도 0 이었다.
- Serena·Graphify 는 쓰지 않았다. 이 파일 밖에는 쓰지 않았다.

## 판정: **설계 수정 후 재검토** — blocker 2 · major 11 · minor 7

- 방향(창 · 정적+런타임 · W/D 분리 · 미측정 = STOP)은 맞다. SDS 에서 런타임 probe 는 실제로 된다(아래 «질문별 답 요약» 1행).
- 그러나 두 가지는 이대로 구현하면 장치가 제 목적을 못 한다.
  - **B-1** 마이그레이션 런타임 비교가 SDS 에서 **조용한 green** 이다. `manage.py makemigrations --check --dry-run` 이 시스템 체크 오류로 양 끝 모두 같은 exit 1 · 빈 stdout 을 내고, «무변»으로 판정된다. 실측으로 재현했다.
  - **B-2** 비교(compare)가 G2 직전(step 6)에만 돈다. red 가 기능 슬라이스를 슬라이스 0 위에 다 쌓은 뒤에야 나온다. 그래서 1차 처방 «원인 편집 철회»가 사실상 불가능하다.
- major 는 대부분 «창 경계의 미정의»와 «거짓 red 원천»이다. 거짓 red 원천은 실측 수치로 확인했다(W 층 description 444곳 · discriminator mapping · OHS 재수출 판정 · Ninja URL 이름).

## 질문별 답 요약

| 질문 | 답 | 관련 발견 |
|---|---|---|
| 1 런타임 probe 취약성 | SDS 는 `settings.test` 로 setup·URL·OpenAPI·마이그레이션 탐지가 **DB 0 · env 0 · 약 5~8초**에 된다. STOP 이 쏟아질 위험은 낮다. 진짜 위험은 셋이다: 시스템 체크가 makemigrations 를 막아 생기는 조용한 green, 입력(settings·env·DB)이 미고정인 것, 닫기 쪽 기동 실패를 «미측정»으로 분류하는 것 | B-1 · M-1 · M-2 |
| 2 보호 테스트 ↔ 입장 표 충돌 | 충돌은 실재한다. G1 이 승인한 «의미 보존 재조직»과 factories 이동이 강제하는 import 수정이 **항상** red → STOP 이 된다. 게다가 `--accepted-file` 의 항목 ID 는 compare 뒤에야 생기므로 사전 승인이 불가능하다 | M-3 · M-4 |
| 3 창 경계 | 정의되지 않은 경우가 다섯이다: 경계를 넘는 병렬 파견(C:115 가 허용) · G2 시점 «미룰 수 없음» 재상정으로 창 밖에 생기는 슬라이스 0 · 창 안 main 머지(현장 15/79 실행에 승인 머지) · 세션 재시작 · 폴더 재사용 시 이전 실행의 open.json | B-2 · M-5 · M-6 |
| 4 W 층 거짓 red | `$ref` 해소·title 제거만으로는 부족하다. 실측 잔여는 description 444곳 · discriminator mapping 의 스키마 이름 · 형제 키가 붙은 `$ref` · 순환 스키마 12곳 · security 스킴 이름이다. OHS·URL 표면에도 같은 종류의 거짓 red 가 있다 | M-7 · M-8 · M-9 |
| 5 Coordinator 부하 | 삽입 지점이 8곳이다(D4 §2 · B2 §3 표). 스크립트가 상태를 소유하게 하면 문면을 3문장으로 줄일 수 있다 | m-4 · B-2 |
| 6 빠진 표면 | 현장에서 리팩터 뒤 깨진 사례는 다섯 표면 밖(버킷 6)이 가장 많다: 문자열 BC 식별자 · 테스트가 대조하는 커밋 산출물 · mock/spy/patch 자리 · `import_module` 문자열 · 파일 기준 데이터 경로 · 배포 env 키 · 업로드 접두. B2 가 든 celery·signal·pickle 은 SDS 에 해당이 없다. 슬라이스 0 자체의 동작 깨짐은 약 7 실행 중 0 이었다 | M-11 · §6 |

## Blocker

### B-1. 마이그레이션 런타임 비교가 시스템 체크 오류에 가려 «무변 = green» 이 된다 (실측 재현)

- 근거
  - B2 §2.2(ii) 는 `manage.py makemigrations --check --dry-run` 의 «(exit, 정규화 stdout)»이 open = close 면 불변이라 한다. stderr 는 비교에서 뺀다. «exit 0 이 아니라 무변»이다(`diag-B2-behavior-evidence.md:66-68`).
  - Django `makemigrations` 는 `requires_system_checks` 를 덮어쓰지 않는다. 그래서 CLI 경로에서는 시스템 체크가 먼저 돈다(SDS venv `django/core/management/base.py:272` 기본값 `"__all__"`).
  - SDS 의 `settings.test` 는 `CHAT_RELAY_GENERATION_CAPACITY_PER_PROCESS`·`CHAT_RELAY_RESUME_CAPACITY_PER_PROCESS` 를 두지 않는다(`spring_dream_server/settings/base.py:259-260` 은 `os.getenv` · `settings/test.py` 에 없음). 그래서 `chat_relay.E001`·`E002` 가 난다(`application/chat_relay/composition_root/event_wiring.py:131` `checks.register`).
  - 실측(`rv4/probe2-test.json`): `ManagementUtility(["manage.py","makemigrations","--check","--dry-run"])` → **exit 1 · stdout 빈 문자열** · stderr 에 SystemCheckError. 자동 탐지기는 돌지도 않았다. 같은 명령에 `--skip-checks` 를 붙이면 exit 0 · `No changes detected` 가 나왔다.
  - 즉 open·close 가 모두 (1, "") 이다. 모델을 지워 DeleteModel 이 생겨도 판정은 «무변»이다. D4 가 금지한 «조용한 green»(`step4-…-v1.md:22`)이 바로 여기서 생긴다.
  - 반대 방향도 있다. 설정을 `settings.local` 로 잡으면 env 가 CHAT_RELAY 값을 주므로 체크는 통과한다. 대신 makemigrations 가 일관성 검사를 하려고 `POSTGRES_HOST`(개발 RDS)에 접속한다(`makemigrations.py:160` · `settings/local.py` `DATABASES = _base.postgresql_database()`). 공유 DB 상태가 open 과 close 사이에 바뀌면 결과도 바뀐다.
- 수정 제안
  - 마이그레이션 탐지는 CLI 가 아니라 **probe 프로세스 안**에서 한다. `MigrationLoader(None, ignore_no_migrations=True)` + `MigrationAutodetector(...).changes()` 를 `translation.override(None)` 안에서 돌린다. 이것은 `makemigrations` 의 `@no_translations` 와 같은 효과다. 이 줄이 없으면 `LANGUAGE_CODE="ko"` 때문에 거짓 변경 39 op 가 나온다(contenttypes 2 · sessions 4 · admin 8 · auth 20 · accounts 5 — `rv4/probe-test-1.json` 대 `probe2-test.json` 실측). 접속 가드를 건다. 비교 대상은 exit 이 아니라 **변경 목록(앱 · 연산 describe)** 이다. 실측으로 SDS 의 현재 목록은 `{}` 이다.
  - CLI 를 굳이 쓰려면 `--skip-checks` 를 필수로 하고, stdout 에 `No changes detected` 또는 `Migrations for` 가 없으면 «미측정(4)»로 판정한다. «exit 1 + 빈 stdout» 을 결코 비교 가능한 값으로 쓰지 않는다.
  - 일반 규칙으로 올린다: **어느 표면이든 «측정 산출물 부재»는 값이 아니라 미측정이다.** open·close 가 같은 방식으로 실패한 것을 «무변»으로 읽지 않는다(registry_gate 의 «앵커·현재 양측 동일 crash 의 상쇄 사각 = 측정 실패» `C:160` 과 같은 원칙이다).

### B-2. compare 가 step 6(G2 직전)에만 돌아, red 가 기능 슬라이스를 다 쌓은 뒤에 나온다

- 근거
  - D4 §2 는 compare 를 G2 쪽에 둔다(B2 §3 표 «step 6 새 하위 항목 — `compare` 실행·종료 계약», `diag-B2-behavior-evidence.md:129`). 닫기는 캡처만 한다(`:43-45` · `:127`).
  - 창은 슬라이스 0 이고, 슬라이스 0 뒤에 기능 슬라이스가 온다(C:113). B1 이후에는 서비스 레인 거의 전부가 이 모양이다(D4 §3-1).
  - red 처방은 «1차 = 원인 편집 철회»다(`step4-…-v1.md:22`). 그런데 step 6 시점에는 기능 슬라이스가 슬라이스 0 의 결과 위에 이미 올라가 있다. 슬라이스 0 의 이동을 되돌리면 기능 슬라이스의 import·배치도 함께 흔들린다. 1차 처방이 사실상 «전부 재작업»이 된다.
  - 같은 이유로 «창 이후 재편집» 집계(`diag-B2-…:147-148`)가 필요한 경우가 대부분이 된다. 그 경로는 기계 보증 밖이다(LLM).
- 수정 제안
  - **닫기 = 캡처 + 비교**로 바꾼다. 닫기에서 exit ≠ 0(승인 없는 Δ 또는 미측정)이면 첫 비리팩터 슬라이스를 파견하지 않고 그 자리에서 red 처방(철회 → 불가면 STOP)을 한다.
  - step 6 에는 «닫기 판정 결과 재확인 + 창 이후 재편집 집계»만 남긴다. G2 금지 조건은 «닫기 판정이 green 이 아니다» 하나로 줄인다(m-4).
  - 순수 리팩터 레인(K1·K2)에서는 닫기가 곧 G2 직전이라 차이가 없다.

## Major

### M-1. probe 입력(settings · env · 인터프리터 · DB)이 고정되지 않았다

- 근거
  - D4 는 B2 §2.0 을 그대로 쓴다: `--settings` 는 «Phase 2 step 1 이 감지한 값»이다(`diag-B2-…:49-50`). 그런데 step 1 은 **새 `add/update` 행이 있을 때만** pytest 설정을 확인한다(C:111). 순수 리팩터 레인(K1·K2)에는 add/update 가 없다. 그러니 장치가 가장 필요한 레인에서 입력의 출처가 비어 있다.
  - SDS 에는 후보가 둘이고 서로 다르다. `manage.py:10` 기본값은 `settings.local`, `pyproject.toml:62` 는 `settings.test` 다.
  - 실측: `settings.local` 은 env 파일이 없는 clone 에서 `RuntimeError: SECRET_KEY: missing required environment value` 로 기동하지 못한다(`settings/local.py:18` · `rv4/probe3.py` 실측). 레인 워크트리 4곳에는 `env/.env.local`·`.env.base` 가 복사돼 있어서 기동은 된다. 대신 개발 RDS 에 접속한다(B-1).
  - 전체 suite 는 명령행 env 로 체크 값을 채워서 돈다. 예: `CHAT_RELAY_GENERATION_CAPACITY_PER_PROCESS=1 … uv run --frozen --no-env-file pytest`(`docs/superpowers/orders/lane/REPORT-fortune-library-b0.md:350`). D4 는 `--python`·`--settings` 만 고정하고 env 는 고정하지 않는다. open 과 close 에서 env 가 다르면 체크·LLM 설정 로더(`settings/base.py:104-116` — 모르는 `LLM_` 키만 있어도 RuntimeError)가 다르게 반응한다.
- 수정 제안
  - probe 의 settings 는 «pytest 설정의 `DJANGO_SETTINGS_MODULE`(없으면 사용자 확인)»으로 고정한다. manage.py 기본값은 쓰지 않는다. open 에서 settings·인터프리터 경로·`sys.version`·Django/ninja 버전·**env 허용 목록의 값 해시**를 `open.json` 에 적는다. close 에서 하나라도 다르면 exit 1 이다.
  - probe 는 import 전에 DB 접속 가드를 건다(`rv4/probe3.py` 방식). 기동 중 접속 시도는 «미측정(DB 필요)»으로 사유를 적는다. SDS 는 이 가드 아래서 접속 시도 0 이었다.

### M-2. 닫기 쪽 기동 실패를 «미측정(4)»으로 두면, 앱을 못 띄우는 리팩터가 사용자 «미측정 승인»으로 G2 를 지난다

- 근거
  - D4 는 exit 4 = «일부 미측정(사유)»이고 «승인 안 된 미측정»만 G2 금지다(`step4-…-v1.md:20` · `:33`). open 은 되고 close 에서 `django.setup()`·URLconf import 가 실패하는 경우를 따로 구분하지 않는다.
  - SDS 의 settings 는 BC 코드를 import 한다(`settings/base.py:12` `application.llm_access.domain_layer.generation_audit.value_object.generation_settings` · `:15` `framework.django.unfold`). URLconf 는 13 BC 의 `api_router` 를 import 한다(`spring_dream_server/urls.py:21-39`). 슬라이스 0 이 이 모듈 가운데 하나를 옮기고 소비처를 빠뜨리면 close 에서 기동이 깨진다. 이것은 «측정 못 함»이 아니라 **동작이 깨짐**이다.
- 수정 제안
  - «open 성공 ∧ close 실패»는 **red(exit 2)** 로 둔다. 항목 이름은 `boot`, 원인은 트레이스백 마지막 줄이다. 미측정(4)은 «open 부터 실패» 또는 «환경 사유(DB 필요 · 인터프리터 부재)»만이다.
  - `--accepted-file` 은 `boot` 항목을 받지 않는다.

### M-3. 보호 테스트 무편집(P)과 G1 이 승인한 «의미 보존 재조직»이 정면으로 부딪친다 — 슬라이스 0 마다 STOP 이 구조적으로 난다

- 근거
  - 규범은 G1 이 명시 승인한 «의미 보존 move/split/rename/reorganization»을 허용한다. 조건은 새 case·assertion·Red 가 없고 전후 보호가 같다는 기록이다(C:97 · C:112 · AT:24 · DR:54).
  - 외부 계약 테스트(e2e)의 편집 주체는 acceptance-tester 다. coder 는 원래 e2e 를 고칠 수 없다(coder.md:73). 그래서 슬라이스 0 의 이동이 e2e import 수정을 강제하면, 규범상 정당한 경로는 «G1 에 acceptance-tester 소유 재조직 행 → 창 안에서 AT 가 import 만 수정»이다. D4 는 이 합법 경로를 무조건 red 로 만든다(§1 표 1행).
  - 현장 결합도(SDS 실측): e2e 69파일 중 **34파일이 `test.factories` 를 import** 한다(`application/*/test/e2e/**`). `tests/web/**` 78파일 중 20파일도 factories/fake 를 import 한다. e2e 가 BC 제품 모듈을 import 문으로 직접 import 하는 경우는 0 이다(grep). 즉 충돌의 거의 전부는 **factories·fake 이동이 강제하는 import 줄 수정**이다.
  - `--accepted-file` 로는 풀 수 없다. 항목 ID 는 compare 가 diff 를 만든 뒤에야 생긴다. 그래서 G1 에서 미리 승인할 수 없고, 창이 닫힌 뒤 STOP 이 반드시 한 번 난다. 위임 레인에서는 그 STOP 이 레인을 세운다(C:217).
- 수정 제안
  - P 비교를 blob 동일이 아니라 **«import 문을 뺀 AST 동일»**로 한다. import 줄만 바뀐 파일은 «import 전용 수정 n파일»로 보고한다. 그 밖의 변화(assertion · case · fixture 본문 · 파일 추가/삭제)는 red 다. factories 이동의 강제 수정은 이것으로 거의 다 흡수된다. 단 `import_module("scripts.seed_…")`·`patch("…")` 같은 **문자열 참조**의 수정은 흡수되지 않는다. 현장에서 seed 스크립트 이동이 e2e 2파일의 이런 문자열을 고치게 했다(§6 커밋 `ddf3f260b`). 이것은 아래 G1 입장 행 대조로 처리한다.
  - 파일 이동·개명(내용 AST 동일)은 G1 입장 표의 재조직 행(`candidate`·`owner/path` 의 전→후 경로)과 대조해 맞으면 보고, 안 맞으면 red 로 한다. 사전 승인 출처가 G1 승인 명세가 되므로 사후 STOP 이 생기지 않는다.
  - coder 규칙(«P 편집이 필요하면 STOP»)은 «P 편집이 필요하면 편집하지 말고 보고 — Coordinator 가 G1 입장 행 유무로 AT 파견 또는 STOP»으로 바꾼다. coder 에게 P 목록을 줄 필요는 남는다.

### M-4. P 의 범위가 규범에 없는 입력(«동결 테스트 경로» 줄)에 기대고, 기본값이 너무 좁다

- 근거
  - D4 §1 의 P 는 `application/*/test/e2e/**` ∪ «G0 스코프 메모의 동결 테스트 경로»다. 그런데 Coordinator 의 스코프 메모 규약(C:72 · C:80)에는 그런 줄이 없다. 누가·무엇을 출처로 쓰는지 정하지 않았다. 캠페인 발주 판형에만 있다(`refactor-campaign/plan-v2.md:44`).
  - 일반 서비스 레인에서는 P = e2e 뿐이다. 그러면 SDS `tests/web/**`(78파일 · dddjango-web 화면이 API 계약을 in-process client 로 소비)과 루트 `tests/*.py` 가 보호되지 않는다. 루트 `tests/` 중 6파일은 BC 제품 모듈을 직접 import 한다.
  - R3 F4 표(`refactor-campaign/review-R3-risk.md:89-107`)에서 e2e 0 인 BC 가 5개다. 이 BC 들은 P 가 비어 «보호막 0» 경고만 받는다. 그런데 그 BC 의 다른 BC 소비자 테스트는 보호받지 못한다.
- 수정 제안
  - 기본 P 를 «e2e ∪ **창 대상 BC 밖의 모든 테스트 파일**(다른 BC 의 `test/**` · 루트 `tests/**` · 기타 테스트 루트)»로 넓힌다. 동작 불변 리팩터가 남의 테스트를 고칠 정당한 이유는 import 경로뿐이다. 그것은 M-3 의 import 정규화가 흡수한다. 규범에 새 입력 줄을 만들 필요가 없어진다.
  - 스코프 메모에 줄을 두려면 C:72 의 스코프 메모 규약에 줄 이름과 출처(사용자·발주 원문)를 정의한다. Coordinator 가 스스로 채우지 않는다고 적는다.

### M-5. 창 경계에서 정의되지 않은 경우가 다섯이다

| 경우 | 현행 규범이 허용하는 것 | D4 에서 생기는 문제 | 제안 |
|---|---|---|---|
| ① 경계를 넘는 병렬 파견 | 슬라이스 ≥3 이면 경량 감사와 다음 슬라이스를 «파일이 안 겹치면 병렬 배차 가능»(C:115) | 마지막 리팩터 슬라이스의 감사 반영이 첫 기능 슬라이스와 동시에 진행된다. B2 의 닫기 정의(«감사 반영 수신 뒤 · 첫 비리팩터 파견 전», `diag-B2-…:44`)가 성립하지 않는다 | C:115 에 «창의 마지막 슬라이스는 감사 반영 완료 뒤 닫기 → 그다음 파견» 예외를 명문화한다 |
| ② G2 시점 «미룰 수 없음» 재상정 | «채택 시 G1′ 경유로 슬라이스 0 편입»(C:160) | 이때는 기능 슬라이스가 이미 끝났다. 새 «슬라이스 0»은 창 밖, 기능 변경 뒤에 온다. open 스냅숏에 기능 변경이 섞인다 | 창을 **여러 개** 허용한다(`window_id` = 1,2…). 창 k 의 open = 그 리팩터 슬라이스 파견 직전. 인터페이스(`--window`)를 지금 넣는다 |
| ③ 창 안 main→레인 머지 | 발주자 승인 머지(`approved-merges.txt` · C:30 · C:175). 현장에서 승인 머지 목록이 있는 실행 15/79(`diag-B3-pregate-field-frequency.md` 결론 2) | 머지로 들어온 e2e·마이그레이션·URL·OpenAPI 변화가 전부 창 Δ 로 잡힌다. registry_gate 와 달리 provenance 채널이 없다. 거짓 red → STOP | 창이 열려 있는 동안 머지를 금지한다(발주자 규약). 불가하면 «닫기 → 머지 → 새 창 열기»로 창을 끊는다. provenance 차분을 새로 만들지 않는다(단순한 쪽) |
| ④ 세션 재시작·compact | 현장에서 레인 중간 인계가 실재한다(`docs/superpowers/orders/lane/HANDOFF-*compact*.md` 14건 · dddjango-web 포함) | 새 세션이 창이 열려 있는지 알 방법이 `behavior/open.json` 존재뿐이다 | `refactor-scope.md` 실행 줄에 `· 창1 open <시각>` / `· 창1 close <시각>`을 덧붙인다(기존 «실행 줄 기계 기록»과 같은 채널 · C:85) |
| ⑤ 폴더 재사용 | «한 기능 = 한 폴더» · 산출물은 커밋이 기본(C:24-26) | 이전 실행의 `behavior/open.json` 이 남아 있다. 이번 실행이 open 을 빠뜨려도 compare 는 «open 부재 exit 1»을 내지 않는다. 낡은 기준선과 비교하게 된다 | `open.json` 에 실행 식별자(실행 줄의 G0 승인 시각 + `build_anchor`)를 적는다. compare 는 현재 실행 줄과 다르면 exit 1 로 거부한다 |

### M-6. 감수자 입력 `report.md` 가 감수자 호출보다 늦게 생긴다

- 근거
  - D4 §2: discipline-reviewer 는 `report.md` 를 입력으로 받는다(D 층 · 창 이후 재편집). B2 §3 표는 이 입력을 step 5 에 넣는다(`diag-B2-…:128`).
  - 그런데 `report.md` 는 compare 가 만들고, compare 는 step 6 이다(`diag-B2-…:129`). step 5(홀리스틱 감사)가 step 6 보다 먼저 돈다(C:116 → C:122). 감수자는 없는 파일 또는 낡은 파일을 받는다.
  - D4 는 «오라클 독립성은 완전하지 않다 — D 층·재편집은 LLM, 정직 표기가 대책»이라 한다(`diag-B2-…:166`). 그 LLM 판정자가 입력을 못 받으면 D 층 보고는 판정자가 없다.
- 수정 제안
  - B-2 대로 닫기에서 compare 를 돌리면 D 층 보고는 닫기 시점에 생긴다. 이것을 슬라이스 0 경량 감사(또는 홀리스틱)에 넣는다.
  - «창 이후 재편집» 집계는 step 5 호출 **직전**에 한 번 돌리고(registry_gate 의 ⓓ 동봉과 같은 자리 · C:116), step 6 에서는 그 뒤 편집이 있었는지만 다시 확인한다.

### M-7. W 층 정규화(`$ref` 해소 · title 제거 · required 정렬)로는 이름·문서 누출이 남는다 — 실측

- 방법: SDS OpenAPI 문서(경로 41 · operation 52 · 컴포넌트 173)를 두 프로세스에서 떠서 B2 §2.3 을 문면대로 구현해 비교했다(`rv4/wlayer.py`).
- 확인된 것
  - operationId 는 두 프로세스 사이에 **52개 중 50개가 달랐다**(ninja_extra 난수 접미). D 로 내린 판단은 옳다.
  - W 층은 두 프로세스 사이에 같았다(결정적이다).
- W 층에 남은 거짓 red 원천
  1. **description 444곳.** 컴포넌트 173개 중 108개가 클래스 docstring 에서 온 description 을 가진다(예: `POST /api/accounts` 요청 스키마 «가입 완료 본문 — …»). 슬라이스 0 이 docstring 을 고치거나 이름을 바꾸며 docstring 을 따라 고치면 W red 가 난다. W 정규화 규칙은 `title` 만 지운다(`diag-B2-…:77-78`). D 층 목록의 «summary/description»(`step4-…-v1.md:6` · `diag-B2-…:79`)이 스키마 내부 description 까지 뜻하는지는 문면이 정하지 않는다. 문면대로 구현하면 이 444곳이 W 에 남는다(`rv4/wlayer.py` 실측).
  2. **discriminator mapping.** `_EvidenceProvision` 의 `discriminator.mapping` 값이 `#/components/schemas/_AbstainedSchema` 같은 **문자열**이다. `$ref` 해소가 닿지 않는다. 그래서 Schema 개명이 W red 가 된다.
  3. **형제 키가 붙은 `$ref`**(OpenAPI 3.1). `{"$ref": "#/components/schemas/_EvidenceProvision", "description": "…"}` 가 1곳 있다. «`$ref` 단독 노드만 해소»로 구현하면 이름이 W 에 남는다.
  4. **순환 스키마 12곳**(chat_relay `payload` · decisive_fortune `chart` 의 JSON 재귀형). 순환을 막지 않고 인라인하면 무한 재귀다. 순환 표지에 스키마 이름을 쓰면 이름이 W 로 되돌아온다.
  5. **security 스킴 이름.** operation 의 `security: [{"SessionAuth": []}]` 는 인증 클래스 이름이다(스킴 2종: `SessionAuth` · `ChatRelaySessionAuth`). 인증 클래스 개명·이동이 W red 가 된다.
- 반대로 걱정할 필요가 없던 것: `Optional[int]`·`int | None`·`None | int` 는 pydantic 이 같은 스키마를 낸다. `dict[str, Any]`·`dict[str, object]`·`dict` 도 같은 스키마다(실측). 그래서 #647 의 `Any → object` 수리는 W 를 바꾸지 않는다. W 가 바뀌는 것은 구체 Schema·TypedDict 로 바꾸는 경우뿐이다(B2 §2.3 «잡는 것»은 이 경우로 한정해 적어야 정확하다).
- 수정 제안
  - W 정규화 규칙을 이렇게 명시한다.
    - description·summary·example(s)·title 은 **모든 깊이에서** D 로 보낸다.
    - `$ref` 는 형제 키가 있어도 해소한다(형제 키는 병합 뒤 위 규칙 적용).
    - `discriminator.mapping` 은 값(스키마 이름)을 해소된 구조의 해시로 바꾼다.
    - 순환은 «조상 스택 깊이 k»(`{"$cycle": k}`)로 표지한다. 이름을 쓰지 않는다.
    - security 는 스킴 이름 대신 `components.securitySchemes[이름]` 정의(type·in·name)로 바꾼다.
  - 이 다섯 규칙에 대한 smoke 픽스처를 `behavior_guard_smoke.py` 에 넣는다.

### M-8. OHS 표면 추출이 «import 한 이름»을 공개 이름으로 세서, 가장 흔한 빚(배치 이동)이 OHS red 를 낸다

- 근거
  - B2 §2.4 는 공개 이름을 «`__all__` 우선, 없으면 밑줄 제외»로 잡고, 재수출은 «대상 경로»를 비교한다(`diag-B2-…:90-92`).
  - SDS 의 OHS·published_event 파일 524개 중 `__all__` 이 있는 것은 **7개**뿐이다. OHS 서비스 모듈은 application_layer 의 query·result·use_case 클래스를 모듈 머리에서 import 한다(예: `fortune_catalog/driving_layer/open_host_service/catalog_inquiry/catalog_inquiry_service.py:1-26`). 이 규칙대로면 import 한 이름이 전부 «공개 이름·재수출»이다.
  - 캠페인 빚 스캔에서 두 번째로 많은 것이 layer-skeleton(배치) 46건 · 10 BC 다(`refactor-campaign/evidence/bc-scan-root-508a841a8.json`). 배치 이동은 application_layer 파일 경로를 바꾼다. 그러면 OHS 모듈의 import 대상 경로가 바뀌고 «변경 = red»가 된다. OHS 의 실제 계약(`contract/` 타입 · 서비스 함수 시그니처)은 그대로인데도 그렇다.
  - import 정리(쓰지 않는 import 삭제)도 «제거 = red»가 된다.
- 수정 제안
  - 공개 표면 = 그 모듈에서 **정의한** 이름(def·class·주석 붙은 대입) ∪ `__all__` ∪ `open_host_service/**/contract/`·`published_event/` 안의 정의로 향하는 재수출이다. 그 밖의 import 한 이름은 표면이 아니다.
  - 시그니처의 주석은 dotted 경로가 아니라 **이름**으로 비교한다(`ast.dump` 는 원래 이름만 담으므로 그대로 두면 된다 — 경로 해석을 추가하지 않는다).

### M-9. URL 표면에 거짓 red 원천이 둘 있고, «인터페이스 지금 확정»과 모순된다

- 근거
  - SDS URL 379행 중 API 55행이다. Ninja URL 이름은 **컨트롤러 메서드 이름**이다(예: `api:register_account` · `api:get_my_profile` — `rv4/probe-test-1.json`). `reverse("api:…")` 사용처는 제품·테스트 모두 **0건**이다(grep 실측). 템플릿 `{% url %}` 39곳·제품 `reverse("admin:…")` 16곳은 web·admin 이름이다.
  - 그래서 메서드 개명(명명 규칙 수리)은 소비자 0 인 이름 때문에 red → STOP 이 된다. B2 도 이것을 안다(`diag-B2-…:101` «red 유지(STOP 에서 판정)»).
  - 사용자 결정 1-b 의 리팩토링 커맨드는 «함수형 API → 클래스 컨트롤러»를 정리 대상으로 든다(`evening-report.md:52`). 이 변환은 Ninja URL 이름을 바꿀 수 있다. D4 §3-3 은 «로드맵 5 가 이 장치를 그대로 쓴다 — 인터페이스를 지금 확정한다»라 한다. 그런데 이 red 가 있으면 로드맵 5 의 대표 작업이 항목마다 STOP 한다.
  - admin `app_list` 행은 정규식 `(?P<app_label>accounts|wallet|fortune_teller|auth|…)` 한 줄이다. 대안(alternation) 순서는 admin 등록 순서다. SDS 에서 `auth` 가 `fortune_teller` 뒤에 끼어 있다. 이것은 import 부작용 순서를 뜻한다. admin 모듈을 표준 칸으로 옮기는 슬라이스 0 이 import 순서를 바꾸면, 라우트 의미는 같아도 이 문자열이 바뀐다.
- 수정 제안
  - URL 을 두 층으로 나눈다. **route(결합 문자열)** 는 red 다. **이름** 은 «그 namespace 가 Ninja API 이면 D(보고)», 그 밖(admin·web)은 red 다. Ninja 의 route×method 는 이미 OpenAPI W 가 지킨다.
  - 정규식 안의 alternation 은 정렬해 비교한다. admin 은 `admin.site._registry` 의 (app_label, model) 집합으로도 비교한다. 등록 누락은 이 집합이 더 직접 잡는다.

### M-10. `--accepted-file` 이 이번 수리의 재상정 규칙과 다른 제3의 경로를 연다

- 근거
  - 2026-09-26 규범: 슬라이스 0 을 동작 불변으로 정리할 수 없는 항목은 슬라이스 0 에서 빼고 STOP 한다. 선택지는 «동작 변경은 별도 요청으로 / 출처 있는 ⓑ / 작업 중단»이고, 답은 `ⓐ 재상정` 절에 쓴다(C:106). «리팩터링과 기능 변경을 한 슬라이스에 섞지 않는다»(C:113).
  - D4 의 `--accepted-file` 은 사용자가 W Δ 를 승인하면 exit 에서 뺀다(`step4-…-v1.md:21`). 이것은 «슬라이스 0 안에 동작 변경을 받아들임»이다. 위 두 규칙과 맞지 않는 새 경로다.
  - 파일의 소유자·경로·줄 형식·수명(실행 단위인지)도 정하지 않았다. 비교 대상 채널(legacy-debt·approved-merges)은 모두 소유자를 명시한다(C:30 · C:82).
- 수정 제안
  - red 의 STOP 선택지를 C:106 과 같게 한다: «철회해 별도 요청으로 / 출처 있는 ⓑ(항목을 슬라이스 0 에서 뺌) / 작업 중단» + «장치 오탐(측정 결함)». 답은 `ⓐ 재상정` 절에 쓴다.
  - `--accepted-file` 은 **«장치 오탐» 처분에만** 쓴다. 소유자는 Coordinator(사용자 답의 기계 기록)이고, 경로는 `<산출물 폴더>/behavior/accepted.txt`, 줄 형식은 `<항목 ID> · 장치 오탐 · 출처 = 본인 직접(<시각>) | 사용자 원문 <파일:행>` 이다. 이 줄은 `ⓐ 재상정` 절의 결정 줄과 짝을 이룬다. 실행 식별자를 달아 다음 실행에 이월하지 않는다.
  - 항목 ID 규칙을 정한다(표면 · 경로·op · 해시 12자). 그래야 G2 재실행 사이에도 같은 항목이 같은 ID 를 가진다.

### M-11. «알려진 사각» 목록이 현장에서 실제로 깨진 표면과 맞지 않다. 가장 싸고 효과가 큰 검사(옛 참조 잔존 스캔)가 빠져 있다

- 근거: 아래 §6. 현장에서 다섯 표면 밖에서 깨진 것은 문자열 BC 식별자 · 테스트가 대조하는 커밋 산출물 · mock/spy/patch 자리 · `import_module("…")` 문자열 · `Path(__file__)` 기준 데이터 경로 · 저장소 밖 배포 env 키 · 업로드 접두다. B2 §5 의 사각 목록(celery 태스크 이름 · signal 수신자 · pickle 경로 · settings 점 문자열, `diag-B2-…:168-169`)은 SDS 에 해당이 거의 없다. SDS 는 celery 0 · signal 수신자 0 · 세션은 DB+JSON 이다(grep 실측).
- 현장 사례 대부분은 **옮기거나 이름을 바꾼 대상의 옛 경로·옛 이름이 저장소 어딘가에 문자열로 남은 것**이다. 이것은 import 해석(B2 §5 완전판 «BC 밖 참조 해석»)으로는 못 잡는다. 문자열·비 Python 파일이기 때문이다.
- 수정 제안
  - 최소판에 **«옛 참조 잔존» 보고(비차단)** 를 넣는다. 창에서 삭제·이동된 Python 모듈마다 옛 dotted 경로와 옛 파일 경로를, 개명된 BC·app_label 이면 옛 식별자를 만든다. 그리고 close 트리 전체(`.py` 뿐 아니라 `.md`·`.json`·`.toml`·`.yml`·`.html`·`.js`·`env/*.sample`·`Makefile`)를 grep 해 적중 파일:행을 `report.md` 에 적는다. `.dddjango/` 와 `docs/` 는 뺀다. 감수자가 판정한다(M-6 의 입력). 정적이라 환경 위험이 0 이고, 비용도 창 변경 파일 수에 비례해 작다.
  - probe 에 두 가지를 싸게 더한다. ① 등록된 시스템 체크의 **함수 이름 집합**(`django.core.checks.registry.registry.registered_checks` — 모듈 경로는 빼고 이름만). SDS 에서는 `event_wiring` 이 `ready()` 에서 import 되며 체크 3종을 등록한다(`chat_relay`·`llm_access`·`rag_service_library` `composition_root/event_wiring.py`). ready() 의 import 가 빠지면 체크가 조용히 사라지는데, 다섯 표면은 이것을 못 본다. ② settings 의 점 문자열(`INSTALLED_APPS`·`MIDDLEWARE`·`STORAGES[*].BACKEND`·`AUTH_USER_MODEL`·`CSRF_FAILURE_VIEW`·`TEMPLATES` context processor)을 `import_string`/`apps.get_model` 으로 해석한 결과 집합.
  - B2 §5 사각 목록은 현장 목록(§6 표의 버킷 6)으로 바꾼다.

## Minor

| # | 위치 | 문제 | 제안 |
|---|---|---|---|
| m-1 | B2 §3 표 · §2.0 | Coordinator 인용 줄 번호가 커밋 `e3ad8e16` 이전 것이다. 예: step 1 `cmd:103` → 현재 C:111 · step 3 `cmd:105` → C:113 · step 4 `cmd:106` → C:114 · step 5 `cmd:108` → C:116 · 역할 보고 `cmd:110` → C:118 · step 6 `cmd:114` → C:122 · G2 `cmd:165` → C:173 · Phase 3 `cmd:174` → C:182 · 수정 모드 `cmd:187` → C:184-195. 지금 C:105 는 빈 줄이고 C:106 은 «슬라이스 0 과 비위반 이동의 STOP» 문단이다 | 계획서에서 절 이름으로 앵커를 다시 잡는다 |
| m-2 | B2 §2.0 «감사자가 언제든 재계산 가능» | 임시 인덱스로 만든 tree 객체는 어느 ref 도 가리키지 않는다. `git gc` 의 unreachable prune(기본 2주)이 지우면 재계산할 수 없다. untracked non-ignored 파일도 캡처마다 object DB 에 blob 으로 쓰인다(워크트리면 공유 object DB) | tree SHA 대신 **표면별 결과**(P 의 경로→AST 해시 · migrations 경로→blob · OHS 표면 JSON)를 `open.json` 에 직접 적는다. 슬라이스 0 커밋이 있으면 그 커밋을 close 기준으로 병기한다 |
| m-3 | 산출 `behavior/{open,close}.json` | SDS 한 번 캡처가 약 380KB(OpenAPI 원문 141KB · W 정규형 203KB · URL 34KB)다. `.dddjango/` 는 커밋이 기본이다(C:26). 실행마다 두 벌이 쌓인다 | 원문은 `report.md` 에 Δ 만 남기고, JSON 에는 표면별 정규형 해시와 항목 목록만 둔다. 전체 원문은 임시 폴더에 둔다 |
| m-4 | 질문 5 · C 문면 | 삽입 지점 8곳(B2 §3 표). 현장 G2 게이트 기록 중 09-04 이후 dddjango 레인 18건에서 고정 문구 «pre-gate 최신성» 행이 글자 그대로 있는 것은 9건이다. 나머지는 같은 정보를 표로 옮겨 적었다(`docs/superpowers/orders/lane/GATE-*-2.md` — 게이트 기록이 배너 사본이 아닐 수 있어 [추론]). 배너 고정 문구에 기대는 집행은 흔들린다 | Coordinator 문면을 3문장으로 줄인다: ① «슬라이스 0 이 있으면 그 첫 파견 직전에 `behavior_guard.py open`» ② «마지막 리팩터 슬라이스 보고·감사 반영 뒤, 다음 파견 전에 `behavior_guard.py close` — exit ≠ 0 이면 파견하지 않고 red 처방» ③ «G2 배너에 `behavior_guard.py verify` 의 `요약:` 행을 그대로 싣고, exit ≠ 0 이면 G2 금지(7번 금지 목록 한 항목)». 창 상태·실행 결합·입력 고정은 스크립트가 소유한다. 금지 조건 3개를 1개로 합친다 |
| m-5 | B2 §2.3 «잡는 것» | OpenAPI 는 모양만 본다. 값 수준 의미는 못 본다: pydantic `strict`·validator·serializer·ninja `resolve_*`. SDS 는 driving_layer validator 1파일 · serializer 0 · `resolve_` 0 · `model_config` strict/extra 11줄로 노출이 작다. 그러나 일반 프로젝트에서는 사각이다 | «알려진 사각»(B2 §5)에 명시한다. e2e 가 이 사각의 유일한 오라클임을 배너 «보호막» 수치와 함께 적는다 |
| m-6 | exit 4 at open | 환경 때문에 open 부터 미측정이면 슬라이스 0 이 있는 레인마다 매번 STOP 이 난다. 결정을 담을 곳이 없다 | open 미측정은 G0 결정 줄과 같은 정형으로 «정적만 측정 · 출처»를 한 번 받는다. 같은 실행 안에서 다시 묻지 않는다 |
| m-7 | 2.2(ii) «manage.py 부재 → 미측정» | B-1 제안(probe 안 탐지)으로 바꾸면 manage.py 는 필요 없다. `DJANGO_SETTINGS_MODULE` 만 필요하다 | 해당 없음 조건을 «settings 미확정»으로 바꾼다 |

## §6 질문 6 — 다섯 표면 밖에서 실제로 깨진 것 (현장 레인 기록)

- 방법: 레인 기록 `docs/superpowers/orders/lane/*.md`(STOP 315 · GATE 244 · REPORT 140 · HANDOFF 16 등 731개)와 `.dddjango/*/`(98폴더)를 grep 했다. 모든 스캔은 읽기 전용이다. 대량 스캔은 읽기 전용 하위 조사에 맡겼다. 핵심 인용 다섯은 원문을 직접 다시 확인했다(✔ 표시).
- 경로는 SDS 루트 기준이다. `lane/` = `docs/superpowers/orders/lane/`.

### 6.1 사례 (리팩터 = 이동 · 개명 · 분할 · 파일→패키지 · 재배치)

| 근거 | 옮긴·바꾼 것 | 깨진 것 | 발견 시점 | 표면 |
|---|---|---|---|---|
| `lane/REPORT-fortune-teller-rename.md:110`·`:132` ✔ | BC 개명 fortune_character → fortune_teller | `rag/service` 의 `SHOP_BCS` 튜플(`build_projection.py:26` · `db_schema/snapshot.py:14`)의 정렬이 깨져 `test_gateway_scan` red → 재정렬로 복구 | 레인 `make testp`(G2 전) | **6** BC 이름 문자열 리터럴 |
| `lane/REPORT-fortune-teller-rename.md:112-114`·`:130` ✔ | 같은 개명 | `tests/test_service_snapshot_db_seed.py:82` 가 커밋된 `rag/service/sources/db_schema/models.md` 의 BC 칸을 라이브 모듈 이름과 대조 → StopIteration. «알려진 red»로 main 에 착륙했다 | 레인 testp · 착륙 뒤에도 미해소 | **6** 테스트가 대조하는 커밋 산출물 |
| `lane/STOP-wallet-G2.md:87-99` | 모듈 수준 별칭(`reserve_currency` 등) 제거 | OHS·admin 통합 테스트 3파일 수집 시 `ImportError` ×3 | G2 | **4** OHS 공개 import 표면 |
| `lane/STOP-decisive-fortune-4-provide-chart-spy-seam.md:9-15` ✔ | `chart_calculation_adapter.py` → 패키지(`__init__` 은 클래스만 재수출) | 발주 조사·G1 리뷰가 놓친 5번째 테스트의 `mocker.spy(모듈, "calculate_chart_command")` 가 AttributeError | coder S2 실행 | **6** mock/spy 자리(모듈 객체) |
| `lane/REPORT-notification-2.md:51-56` ✔ · `REPORT-query-translation-1.md:22`·`:53` · `REPORT-decisive-fortune-4.md:34-35` | 어댑터 파일 → 패키지 | `patch` 문자열 대상(`_SEND_MAIL_PATH` · `_CONFIG_PATH` 등)이 재수출만 가리켜 leaf 전역을 못 바꿈. 수리 전 focused Red 3·4 failed | 슬라이스 실행 | **6** patch 문자열 대상 |
| `lane/REPORT-chat-relay-turn-refactor.md:23-30` | `turn_controller.py` 분할 | fake 의 monkeypatch 자리 재지정 필요. `CSRF_FAILURE_VIEW` 점 문자열은 재수출로 유지 | 슬라이스 실행 | **6** fake 자리 · settings 점 문자열 |
| `lane/REPORT-fortune-calculation-6.md:57-66` ✔ | 어댑터를 더 깊이 이동 · 스크립트를 `scripts/` 로 | `Path(__file__)` 기준이 밀려 JSON 데이터 위치가 바뀔 뻔 → `parents[2]`·`_DATA_DIR` 로 맞춤. `test_table_digest` green | 레인 실측 | **6** 파일 기준 패키지 데이터 경로 |
| 커밋 `ddf3f260b`(09-19 · main 직접 · 레인 아님) ✔ | `scripts/seed_*.py` → `scripts/seed/` | e2e 2파일(`fortune_house/test/e2e/test_fortune_house_live_smoke.py` · `fortune_intent/test/e2e/test_intent_configuration_admin.py`)과 conftest·통합 테스트 20여 파일의 `import_module("scripts.seed_…")` 문자열 수정 | 작성자 grep | **1** 보호 테스트 편집(문자열이라 M-3 의 import 정규화로도 흡수 안 됨) |
| `lane/STOP-chat-relay-G0.md:35-38` ✔ · `REPORT-chat-relay.md:74` | 슬라이스 0 의 `AI_CHAT_*` → `CHAT_RELAY_*` 개명 | 저장소 밖 배포 env 키를 바꾸지 않으면 기동 체크 `chat_relay.E001~E004` 실패 | G0 STOP(사전) | **6** 배포 env 키 이름(저장소 밖) |
| `lane/REPORT-fortune-teller-rename.md` §1·§2 · 발주 `docs/superpowers/orders/2026-09-17-fortune-teller-rename.md` | 같은 개명 | 옛 마이그레이션 5 삭제·새 0001 · 개발 DB RENAME SQL 필요 · admin URL 이름 문자열(`charging_test`) · REST 접두 · `upload_to` 접두(새 업로드만 새 접두 → 경로 혼재) · `tests/web/**`·e2e 편집 | 레인 계획 | **2 · 5 · 6(저장소 접두) · 1** — 계약 변경이라 red 가 옳다 |

- 제외(리팩터 아님): `lane/REPORT-llm-access-3.md:66` 재시도 통합은 의도된 동작 변경이다(슬라이스 0 없음).
- 검사기만의 red(동작 무변): 경로 기반 앵커 차분이 byte 동일 순이동을 신규 위반으로 계상한 사례 4건(`lane/STOP-fortune-calculation-6-any-relocation-attribution.md` · `REPORT-fortune-catalog-1.md:57-67` 등)과 슬라이스 0 의 #493·check-naming red 3건. 동작 보존 장치와는 무관하나, 같은 «순이동 오계상»이 OHS 표면(M-8)에도 생길 수 있다.

### 6.2 표면별 집계

| 표면 | 건수 | 비고 |
|---|---|---|
| 1 보호 테스트 편집 | 2 | 개명(계약 변경) 1 · seed 스크립트 이동 1(`import_module` 문자열) |
| 2 마이그레이션 | 1 | 개명(계약 변경) |
| 3 OpenAPI W | 0 | |
| 4 OHS 공개 표면 | 1 | wallet 별칭 제거 |
| 5 URL | 2 | 개명의 admin 이름·REST 접두(계약 변경) |
| **6 다섯 표면 밖** | **8행(+검사기 전용)** | 문자열 리터럴 1 · 커밋 산출물 1 · mock/spy/patch 자리 3 레인 이상 · 파일 기준 데이터 경로 1 · 배포 env 키 1 · 저장소 접두 1 |

### 6.3 슬라이스 0 의 기저율

- 하위 조사 집계(방법: `.dddjango/*/refactor-scope.md` 96개에서 ⓐ 결정·슬라이스 0 을 찾아 레인 GATE/REPORT 커밋 표와 대조)로는 **리팩터 슬라이스 0 이 실제로 있었던 실행은 약 7개**다. 그중 슬라이스 0 때문에 테스트·런타임이 깨졌다고 보고한 것은 **0**이다. 검사기 red 는 3, 저장소 밖 배포 위험 1 이었다. 실제로 깨진 사례는 전부 **전용 리팩터 레인**(개명 · 별칭 제거 · 파일→패키지)에서 나왔다.
- 해석
  - 지금까지 슬라이스 0 은 드물었고 작았다. B1(«항상 정리») 이후에는 표본이 크게 늘고, 캠페인(K1·K2)은 전용 리팩터 레인과 같은 모양이 된다. 그래서 위 버킷 6 의 사례가 앞으로의 주 위험이다.
  - 다섯 표면 중 현장에서 실제로 걸린 것은 4(OHS)와, 계약 변경이 섞인 개명의 1·2·5 다. **3(OpenAPI W)은 0건**이다. W 층의 가치는 과거 사례가 아니라 K1(#647 구체형 수리)의 예상 위험(B2 §2.3)에 기대고 있다.
  - mock/spy/patch 자리 깨짐은 모두 **테스트가 red 로 알려 줬다**. 동작 보존 장치가 따로 볼 필요는 없다. 다만 옛 경로가 재수출로 여전히 해석되는 경우 patch 는 조용히 헛돈다(`REPORT-notification-2.md:55` 의 원리). 이것은 M-11 의 «옛 참조 잔존» 보고가 잡는다.
