수정 대상: runtime-sync
원인 분류: source skill 수정 후 runtime cache 불일치

# implementation-django-web P3 runtime-sync 분석

## 점검 범위

- source skill: `dddjango/skills/implementation-django-web/`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/`

## 현재 상태

`dddjango/skills/implementation-django-web/SKILL.md`를 P3 기준에 맞게 수정한 뒤 runtime cache의 `SKILL.md`와 차이가 발생했다. Bundled references와 `agents/openai.yaml`은 수정하지 않았으므로 source 기준을 runtime cache에 반영하면 된다.

## 수정 필요 항목

| 항목 | 상태 | 조치 |
|---|---|---|
| `SKILL.md` | source/runtime differ | source `SKILL.md`를 runtime cache `SKILL.md`로 동기화한다. |
| `agents/openai.yaml` | 변경 없음 | 동기화 불필요. 최종 `diff -qr`로 확인한다. |
| bundled references | 변경 없음 | 동기화 불필요. 최종 `diff -qr`로 확인한다. |

## 리뷰 방식

리뷰 방식: real-subagent
- skill-creator 리뷰: P3 skill 분석에서 real subagent 리뷰를 수행했다. runtime-sync 자체는 source/cache parity 작업이므로 별도 subagent 수정 리뷰는 실행하지 않는다.
- Subagent 리뷰/순차 fallback: real-subagent 결과를 P3 skill 분석에 통합했다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 완료 조건

- source skill과 runtime cache의 `implementation-django-web` 디렉터리가 `diff -qr` 기준으로 동일하다.
- plan constraint와 skill docs 검증이 통과하거나, 실패가 대상 외 drift임을 명확히 분리한다.
