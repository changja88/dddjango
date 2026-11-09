# 현장 보고 수리 판 — 작은 수리 10건 계획 v2 (dddjango 2.33.0 후보 · 2026-11-09 · 계획 독립 검토 1 반영 12:40)

배포판 2.32.0(태그 `dddjango--v2.32.0` · f0bbe3a7)으로 12건을 재현했다(재현 yes 10 · partial 2). F4-150 은 사용자 결정(«나» — 별도 API scope 를 표준 자리로)으로 이 판 뒤 따로 큰 판. 이 판은 나머지 10건 + 같은 결함으로 함께 닫히는 F4-140 · F4-144. **F4-156 은 이 판에서 뺀다**(아래 «뺀 것»).

판 번호: 2.33.0 — 규범 의무가 늘고(F4-155 architect · F4-48 예보 범위) 예보 채널이 넓어지므로 minor.

## 항목 · 고침

### 단위 A — 검사기 오탐 · 도구 (검사기만 · graph-owned 글 없음)

| F4 | 고침 | 파일 |
|---|---|---|
| 147 (+144) | BC 열거에서 `__pycache__` 등 SKIP_DIRS 를 거름(:922) · 픽스처 하나(`application/__pycache__/` 가 있는 트리 → #488 0) | `scripts/check-layer-skeleton.py` |
| 151 | 기준선 모드에서 `--api-module` 필수를 풀고(:414) 앵커에 없는 api 모듈은 기준선 렌더에서 뺌(:684) · 같은 꼴인 #5 · #15 · #16 검사기 셋도 같은 두 자리 · 픽스처(앵커에 없는 새 api 모듈 scope → 옛 위반이 «앵커 기존분») | `check-error-centralization.py` · `check-api-error-controller-contract.py` · `check-openapi-error-declaration.py` · `check-composition-root.py` · `anchor_diff.py`(docstring) |
| 152 (+140) | 안 B 좁힌 꼴 — 받는 쪽이 내장 타입으로 정해진 때(주석 · 리터럴 · 내장 생성자로 묶인 이름)의 내장 메서드 호출(`.items()` · `.replace()` 등)과 파일 안에서 묶지 않은 내장 이름(`any` 등)만 업무 어휘 후보에서 뺌 · 받는 쪽 타입을 모르면 그대로 잡음(`lesson.title()` 같은 업무 객체 호출을 놓치지 않게) · 영향 받는 규칙 다섯 · `object_word_guard` 기대를 함께 고침 · 픽스처(내장 타입 받는 쪽 → 0 · 업무 객체 · 모르는 받는 쪽 → 그대로) | `check-business-vocabulary.py` · `business_vocab.py` |
| 153 | #623 이 포트를 framework 전체(test 밖)에서 찾음(:480-481) · 선언 없는 가짜는 그대로 잡힘 · 픽스처(두 단 아래 표준 포트의 가짜 → 0) | `check-business-vocabulary.py` |

### 단위 B — 예보기 (pre-gate 코드 · 픽스처)

| F4 | 고침 | 파일 |
|---|---|---|
| 48 | 저장소 채널에 #287 과 #599(`add_all` — #597 과 같은 이름 판정)를 싣고(`_REPOSITORY_RULES`), 기존 메서드는 인자(이름 · 주석 · 개수)가 바뀌면 투영(도메인 서비스 채널의 `_signature_key` 재사용) · 거름을 규칙별 표지로 · docstring 의 «싣지 않는다» 목록에 #283 을 남기는 까닭(투영에 데코레이터 없음)을 적음 · BLIND_SPOTS S5 문자열 · 스모크(새 이름 · 인자 바뀜 · 그대로 셋) | `scripts/design_pregate.py` · `workspace/tools/pregate_field_report_smoke.py` |
| 155 | 조립 파일 update 칸용 선언 예보 채널 — 기준선 실물의 최상단 정의 ∪ symbols 에 적은 함수 · alias 행을 투영해 번들 check-composition-root 의 `_check_dependency_wiring` 을 부르고 기준선에 없던 #85 줄만 선언 확정 · **줄 번호 다루기**: 함수 #85 는 경로에 줄 번호가 없어 그대로 옮기면 0건이 되고 alias · 대입 #85 는 줄 번호만 달라 거짓 red 가 난다 → G2 와 같은 `:N` 정규화 집합으로 견줌 · 스모크(함수 · alias · 대입 셋 · 기준선에 이미 있는 것 0) | `scripts/design_pregate.py` · 스모크 |

### 단위 C — 글(graph-owned · 그래프 → render → 미러 → rulepack)

| F4 | 고침 | 정본 |
|---|---|---|
| 146 | 재료 함수 반환 주석 조건(값 객체 클래스 이름 하나 또는 str · int · bool · float 하나 · 합 타입 안 됨 — 없음은 빈 값으로)과 값 객체 모듈의 `from __future__` 요구를 규칙 글에 — 검사기 · 설계 기록에 맞춤 · 같은 절에서 글과 검사기가 갈리는 다른 자리(dataclass 별칭 · async · 이름 겹침 · 한 번 묶기 · re)도 장난감으로 확인해 함께 맞춤 | `implementation-django-ninja-final.ttl` R-3618 |
| 148 | arrange 점검의 닫힌 목록에 해로움 없는 셸 꼴을 **조건을 붙여** 넣음 — `cd` 는 실행 기록 폴더로만(제품 폴더로 들어가 상대 경로 검색 금지) · `echo` · `printf` 는 명령 치환 · 리다이렉트 없이 · 파이프 뒤 `head` · `tail` · `tr` · `find` 읽기 조건 — 금지 핵심(제품 본문 · 제품 폴더 안 검색 · 계산 · 쓰기)은 그대로 | `agent-acceptance-tester.ttl` R-3615 |
| 149 | «acceptance-tester 몫 행 = 인수 행» 을 «`add/update` 행 가운데 owner/path 나 계약이 acceptance-tester 몫인 행» 으로 좁힘 · 기능 모드의 명시 승인 retain 재조직 행은 그 시험 파일을 바꾸는 슬라이스의 내부 행 칸에 적는다는 한 문장 | `command-dddjango.ttl` R-3607 · `agent-design-architect.ttl` R-3610 |
| 154 | 예시 두 줄 차례를 «오류 생성 → 머리 → 반환» 으로(검사기 · 같은 절 산문과 같음) · R-0069 에 차례 한 구 · **되돌아옴 막기**(같은 결함 둘째): 스킬 예시를 #15 검사기에 돌리는 계약 줄을 verify 에 | `implementation-django-ninja-final.ttl` 블록 §6.2 |
| 48 · 155 글 | 예보 범위가 넓어진 것을 조정자 S5 괄호 · architect 의무에 맞춤 — architect: «조립 파일 update 는 새로 두는 최상단 함수 · alias 를 symbols 함수 행에 다 적는다» | `agent-design-architect.ttl`(:91 · :95 자리 · R-3653) · `command-dddjango.ttl`(:147 S5 괄호) |

Codex 판(`codex-dddjango/skills/dddjango/SKILL.md` 등)은 같은 뜻으로 고친다. 검사기 · 예보기는 `codex-dddjango/skills/dddjango/scripts/` 와 byte 동일.

## 일하는 법

- 단위 A · B · C 는 맡은 파일이 겹치지 않게 나눠 병렬(구현자 셋 · Claude). 그래프 글은 단위 C 하나가 모아 고치고 `ontology_render.py --apply` 는 C 가 끝에 한 번.
- **단위 D — 묶기(운영자 · A · B · C 뒤)**: 어느 단위 몫도 아닌 파생물을 한 번에 — `pregate_symbol_kinds.json` · §3 체크리스트 8 의 EXPECTED · 그래프 체크리스트 3 ~ 5(F4-146 · F4-154 는 `final.md` 소스 미러 `corpus_mirror_sync.py --write`) · `make rulepack` · Codex 미러 byte 대조 · 봉인. A · B 는 기대 파일을 직접 고치지 않고 바뀔 줄만 보고한다(병렬 충돌 막기).
- 되돌아옴 막기: 항목마다 픽스처 · 스모크 줄(옛 판 붉음 → 새 판 녹색).
- 행동 시험: 재현 장난감(`workspace/scratch/f4-repair-1109/r1` · `r2` · `r3`)을 옛 판(f0bbe3a7 사본)과 새 판에 나란히 — 옛 판은 결함 재현 · 새 판은 해소.
- 구현 독립 검토 한 번(과적합 · 다른 규칙과 모순 · 런타임 실현성 · 커밋 뒤에도 같은가) → 지적 재현 → 처분.
- 검사: `make rulepack` · `make verify` 전체 · rulepack 이 바뀌므로 `make verify-mutation`. 봉인 대상은 커밋 직전 봉인 · 배포 뒤 chore 봉인.
- 문서: README · `docs/master.html` 이 이 동작을 싣는지 보고(F4-155 architect 의무 · F4-156 예보 재실행 판형) · `dddjango/REQUEST_GUIDE.md` 는 사용자가 쓰는 칸이 안 바뀌어 «바뀔 것 없음» 예상(확인해 보고에).
- 배포 직전 장부 다시 읽기(마지막 = F4-156 · 운영자 처분 줄 12:24).

## 받아들이는 한계

- F4-151 옆자리(구현 검토 1 사소 · 코드 읽기): 새 api 모듈이 들이는 같은 패키지 도움 모듈의 옛 위반은 #15 에서 여전히 신규로 찍힌다 · #16 preserve 프로필에서는 urlconf 완화가 짝 검사에 막힌다 — F4-150 큰 판(scope 자리)에서 함께 본다 · 그 사이는 이관 빚.
- F4-152 는 계획 어림 20 ~ 30줄 → 약 300줄(다른 파일의 재귀 `type` 별칭과 `.items()` 에서 꺼낸 원소 타입이 있어야 현장 꼴이 닫힘 · 구현 검토 1 «무겁지만 유지 — 가드만»). 새로 놓치는 자리는 내장 메서드 · 이름 목록에 든 낱말과 주석이 거짓인 코드뿐. 다음에 같은 오탐이 다른 꼴로 오면 이 장치를 넓히지 말고 빚으로 받을지 먼저 묻는다.

- F4-146 의 예보기 보강(update 재료 파일 #652 F3 선언 예보)은 이번에 하지 않는다 — 글만 맞춘다(실행기 30 ~ 60줄 · 효과는 따로 잼).
- F4-148 은 강제 장치(hook) 없이 글만 — 쓰기 0 · 판정 바뀜 0 이 세 번 확인돼 목적은 지켜지고 있고 소음만 줄인다.
- F4-151 의 #5 · #15 · #16 은 인자 읽기까지만 재현 — 구현 단계에서 끝까지 재현한 뒤 고친다(재현 안 되면 그 셋은 뺀다).

## 뺀 것 — F4-156 (질문 생략 · 설계 처리 · 이의 시 뒤집음)

- 계획 검토 1 차단: 예보 머리에 기준선 SHA 칸은 있지만(`design_pregate.py:4893`) 조정자가 견주는 `--block-hash` 출력은 블록 해시 · 실행 트리 digest 두 줄뿐이고 git 을 부르지 않는다(`:5309-5315`) · 작업 트리 변경 · 승인 유입 · 이관 빚 목록 해시 칸은 없다 → 글만 고쳐 skip 을 넓히면 기준선이 옮겨 간 뒤에도 옛 예보를 쓴다.
- 지금 조정자 글의 «무조건 재실행» 은 안전 쪽(느릴 뿐 틀리지 않음)이라 결함이 아니다. skip 을 넓히는 일은 속도 개선이다 — 10-06 사용자 결정(«속도 개선은 그만 · 결함만 고친다») · CLAUDE.md(속도 개선은 효과부터)에 따라 이 판에서 뺀다. 기준선을 열쇠에 넣으면 skip 가능 쌍이 60 → 25 이하로 줄어 효과도 작다.
- 장부 F4-156 처분 줄: 결함 아님 · 속도 개선 후보 · 다시 열면 열쇠(기준선 SHA · `.dddjango/<실행>/` 를 뺀 작업 트리 digest · 유입 · 빚 목록 해시)부터.

## 멈출 기준

- 구현 독립 검토 차단이 셋째 좁은 확인에도 안 닫히면 멈추고 묻는다.
- `make verify` 붉음이 이 판 밖 원인이면 멈추고 알린다.

## 구현 독립 검토 1 처분 (13:58)

차단 0 · 중요 0 · 사소 9 — 모두 받음.
- 사소 1(F4-152 가 `Optional[()]` · 아주 긴 `+` 식에서 traceback exit 1) — 운영자 재현(옛 판 exit 2 · 새 판 ValueError exit 1) → 가드(그 파일은 옛 판처럼 다 셈) + 픽스처 사례 · 단위 A.
- 사소 R-3618 값 객체 칸 경로 금지 한 구 · R-3426 «모듈 별칭 · 최상단 대입(상수 포함)» — 단위 C(같은 판 Expression 글 고침).
- 사소 F4-151 옆자리 둘 — 위 «받아들이는 한계».
- 사소 `pregate_transcription_smoke.py:524` — 운영자(단위 D)가 고침(#287 · #599 가 이제 예보되므로 기대 `[]` → `[("#287", True), ("#599", True)]` · 69 OK).

## 다음 판 후보 (이 판 밖에서 찾음)

- #604 — framework 에 `*_port.py` 가 0 개면 저장소 전체 diff 를 읽어 거짓 blocker(구현 검토 1 · 단위 A 가 따로 찾음 · 2줄 고침 후보).
- #518(check-broker-contract)도 내장 이름(`object` · `any`)을 업무 낱말로 셈(단위 A).
- F4-150 별도 API scope 정식 자리(사용자 결정 «나»).
