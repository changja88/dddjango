# 스파이크 — 리팩토링 입구 위임 실측 (2026-09-27 · 검토 K-M1)

- 목적: 설계 v1 §1 «얇은 입구 → Skill 로 Coordinator 위임»이 실제 하네스에서 성립하는가. 검토 K-M1 이 [추정]으로 남긴 넷(치환 2 · 권한 · 표지 운반)과 Codex 적재.
- 환경: Claude Code 2.1.282 (`/opt/homebrew/bin/claude -p --plugin-dir … --output-format stream-json --no-session-persistence --model sonnet`) · Codex CLI 0.157.0 (`codex exec --ephemeral --skip-git-repo-check -C <app> --sandbox read-only --json` · 스킬은 app `.agents/skills/` 에 byte 사본 — 2026-09-05 선례 판형).
- 산출·원시 기록: 세션 scratchpad `spike5/`(run1~4.jsonl · codex1.jsonl) — 커밋 밖.

## 1. Claude

| 실행 | 구성 | 관측 |
|---|---|---|
| run1 | 장난감 플러그인 · 입구 `disable-model-invocation: true`(allowed-tools 없음) · 권한 auto | Skill 1회 · args = 표지 원문 그대로 · 대상 본문의 `$ARGUMENTS`·`${CLAUDE_PLUGIN_ROOT}` 둘 다 치환 · 대상 `allowed-tools: Bash` 로 Bash 실행 |
| run2 | 같은 구성 · 권한 default(`--permission-mode manual`) | **Skill 호출이 권한 거부**(`permission_denials: Skill`) — 대화형이면 프롬프트가 뜬다 |
| run3 | 입구에 `allowed-tools: Skill(spikeplug:target)` · 권한 default | 프롬프트 없음 · 대상 적재 뒤 대상의 `allowed-tools`(Bash) 적용 · 거부 0 |
| run4 | **작업 트리 dddjango 사본**(이름만 `dddjspike`) + `commands/refactor.md` · 권한 default · `--max-turns 2` | Skill 1회 · 적재 71,724자 = Coordinator 본문 68,893자 + 경로 치환분(끝 문장 일치 — **절단 없음**) · `빌드할 기능: 리팩토링 모드(입구 /dddjspike:refactor) · 대상: service_policy` · `${CLAUDE_PLUGIN_ROOT}` 미치환 0 / 치환 30 · Coordinator 가 Phase 0 조사로 정상 시작 |

결론(Claude):
- 입구 위임은 성립한다. 5A 가 Read 로 본 부분 적재(1~83행)는 Skill 경로에서 재현되지 않는다.
- 입구 frontmatter 에 **`allowed-tools: Skill(dddjango:dddjango)` 가 필수**다(없으면 기본 권한에서 프롬프트 · `-p` 에서는 거부).
- 표지 운반: sonnet 3/3 원문 보존. 모델 준수에 기대는 것은 사실이라 표지 손실은 fail-closed 로 막는다(설계 v2 §1).

## 2. Codex

| 실행 | 구성 | 관측 |
|---|---|---|
| codex1 | `.agents/skills/` 에 Coordinator 사본(`djspike` · 235행 · 125,755 bytes) + 얇은 스킬 `djspike-refactor`(«형제 `../djspike/SKILL.md` 전문을 끝까지 읽는다 — 잘리면 구간으로 이어 읽는다») · 프롬프트 `$djspike-refactor service_policy` | 얇은 스킬 적용 → `cat SKILL.md`(기록된 출력 70,198자) → 곧바로 `wc -l` + `sed -n '74,125p'` 재독 — 모델 쪽 출력이 중간 절단됐고 스스로 복구한 흔적 · 대상 프로젝트가 없어 경로를 묻고 정지(파일 변경 0) |

결론(Codex):
- 얇은 스킬 → Coordinator 적재는 `cat` + 구간 재독으로 성립했다(1회 관측). 절단은 실재한다 — 얇은 스킬 문면에 «`wc -l` 뒤 구간으로 끝까지»를 명시한다(설계 v2 §1).
- 암묵 호출 차단: Codex 0.157 바이너리에 `allow_implicit_invocation` 정책 문자열이 있다(`agents/openai.yaml` `policy`) — 구현 때 실측으로 확정한다.
- 관측 곁가지: 대상 폴더가 없자 모델이 `-C` 밖(`~/Desktop/dddjango`)을 읽기 전용으로 탐색했다. 입구 문제는 아니다.

## 3. 남은 확인(구현 단계 행동 시험으로)

- 실제 spring_dream 사본에서 G0 첫 질문까지(27종 절대 경로 실행 · 다발 산출이 Coordinator 컨텍스트로 들어오는 실부하) — 설계 v2 §8 R-T0.
- Codex 동형 1회.
