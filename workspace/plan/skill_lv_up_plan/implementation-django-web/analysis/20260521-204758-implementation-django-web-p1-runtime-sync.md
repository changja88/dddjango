수정 대상: runtime-sync
원인 분류: source-runtime drift
리뷰 방식: sequential-fallback
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

# implementation-django-web P1 runtime sync 분석

## 평가 범위

- Source skill: `dddjango/skills/implementation-django-web/`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/`

## 현재 평가

Source skill은 dedicated Django Web source reference 기준으로 갱신됐지만 runtime cache는 이전 provisional/fallback 내용을 유지한다. Runtime에서 skill을 사용하는 에이전트는 여전히 dedicated source reference가 없다고 안내받으므로 P1 종료 조건을 만족하지 못한다.

## 근거

- `diff -ru dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web` 결과가 `SKILL.md`, `agents/openai.yaml`, `references/*.md` 차이를 반환했다.
- Runtime cache의 `SKILL.md`는 `Dedicated Django Web source reference does not exist yet`와 `Fallback Source`를 포함한다.
- Runtime cache의 bundled references와 metadata도 provisional/fallback 또는 영어 이전 문구를 유지한다.

## 수정 필요 항목

| 항목 | 판정 | 필요한 수정 |
|---|---|---|
| runtime cache parity | Major | source skill 디렉터리를 runtime cache skill 디렉터리에 동기화한다. |
| sync 검증 | Major | 동기화 후 `diff -ru` 결과가 없어야 한다. |

## 수정하지 않을 항목

- Runtime cache를 source와 다르게 수동 편집하지 않는다.
- Source skill 내용을 runtime cache에 맞춰 되돌리지 않는다.
- 다른 skill cache는 이 P1 범위가 아니므로 건드리지 않는다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰/순차 fallback: runtime sync는 source/cache parity 검증이 핵심이므로 수정 전에는 순차 fallback으로 분류했다. 수정 후 real-subagent 리뷰와 `diff -ru` 검증 결과로 최종 판정을 갱신한다.

skill-creator 리뷰: runtime cache가 stale하면 source skill의 progressive disclosure와 trigger 개선이 실제 사용 경로에 반영되지 않는다. validation integrity 관점에서 Major다.

## 수정 후 재평가

Runtime cache를 source skill과 동기화했고 `diff -qr dddjango/skills/implementation-django-web /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web`에서 차이가 없음을 확인했다. Review-fix 후에도 다시 동기화했다.

최종 판정: Blocker 0, Major 0, 열린 Minor 0.
