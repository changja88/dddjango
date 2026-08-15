# lane-claude-permissions — claude 레인 도구 승인 allowlist 정본 (B0-2)

## 레인 기동 시 복사 절차

1. `cp /Users/hyun/Desktop/dddjango/workspace/tools/lane-claude-permissions.json <레인 저장소>/.claude/settings.local.json`
2. 대상에 settings.local.json 이 이미 있으면 덮지 말고 `permissions.allow` 배열만 병합한다 (`.claude/settings.json` 은 hooks 전용 — 건드리지 않는다).
3. 레인 세션 기동 후 `/permissions` 로 allow 7규칙 로드를 확인한다.

## 근거 — S3-r2″ 레인 A 세션(09566ef7) 실측

- 세션 jsonl 에 승인 이벤트는 명시 레코드로 남지 않는다(실측: permission 레코드 0·거부 0). 승인 왕복은 «tool_use→tool_result 타임스탬프 갭 ≥ 8s 이고 실행 시간으로 설명 불가»로 판정했다.
- 메인(Coordinator) 세션은 slash command 의 command_permissions 로 Bash 포함 blanket 허용 — 프롬프트 0. 승인 왕복은 전부 **subagent** Bash 호출에서 발생.
- subagent Bash 267회 중 **승인 왕복 59회**(경계 3~8s 4회 별도). 대기 중앙값 ~17s, 최대 16,363.7s(=4h33m 방치 사고 1건 — `for … do cat "$f" … done` read-only 루프의 승인 대기였음을 실측).

| 규칙 | 제거 근거(r2″ 실측 왕복 수) |
|---|---|
| `Bash(.venv/bin/python:*)` | 16회 — django introspection `-c`·플러그인 checker 실행. 기존 전역 `Bash(python:*)`·`Bash(python3*)` 와 등가 폭(경로만 venv 직접) |
| `Bash(DJANGO_SETTINGS_MODULE=broccoli_server.settings.test .venv/bin/python:*)` | 2회 — env-prefix 는 리터럴 매칭이라 별도 규칙 필요(기존 `Bash(PYTHONPATH=. uv run *)` 이 방증) |
| `Bash(cat:*)` | 5회 — 파일 읽기 체인. **4h33m 방치 1건 포함 클래스** |
| `Bash(sed -n:*)` | 6회 — 읽기 전용 범위 출력(`sed -n '…p'`)만. `-i` 는 prefix 밖 |
| `Bash(mkdir -p:*)` + `Bash(touch:*)` | 5회 — BC 골격·`__init__.py` 스캐폴딩. 생성 전용(파괴 불가) |
| `Bash(graphify query:*)` | r2″ 0회(전부 ~2s 무프롬프트)·이전 라운드 2회 실측 — 예방 등록. 읽기 전용 조회 |

**커버 합계: 59회 중 확실 ~29회 + cat 루프형 ~5회(엔진의 루프 정적 분석 여하에 따라 부분적) ≈ 34회(58%).**

## 잔여 — allowlist 로 못 없애는 승인 유형

| 유형 | r2″ 실측 | 사유·대안 |
|---|---|---|
| 변수 경유 실행 `$PY "$PLUGIN/scripts/check-….py"` | ~15회 | prefix 규칙은 변수 명령어를 해석 못 함. 대안: 레인 발주문에 «checker 는 `.venv/bin/python /Users/hyun/.claude/plugins/cache/changja88-dddjango/dddjango/<ver>/scripts/check-….py` 리터럴 경로로 호출» 1줄 추가 |
| `: > <파일>` 빈 파일 생성/절단 | 5회 | 쓰기 성격이라 미등록. 대안: Write 도구 사용(acceptEdits 에서 무프롬프트) 지시 |
| rm/mv 파괴 계열 | 1회 | 정책상 등록 금지(B0-2 원칙 ⓑ) |
| 복합 루프·함수 정의 커맨드 | ~3회 | 엔진이 정적 검증 못 하면 규칙이 있어도 프롬프트될 수 있음(동형 cat 커맨드가 한 번은 0.1s 통과·한 번은 프롬프트된 비결정 사례 실측) — allowlist 는 왕복을 «전부» 없앤다고 보장 못 함 |
| long tail(wc·awk·which·sleep 등 1회짜리) | 이전 라운드 각 1회 | 과적합 방지로 미등록 |

## 금지 확인

- 포괄 `Bash(*)` 없음 · rm/mv 없음 · git commit/push 없음(전역 `Bash(git:*)` 은 기존 규칙 — 이 파일이 추가하지 않음) · 네트워크 임의 접근 없음.
