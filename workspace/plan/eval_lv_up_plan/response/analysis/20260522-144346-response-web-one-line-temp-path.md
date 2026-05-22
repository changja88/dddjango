수정 대상: case
원인 분류: skill

# response one-line web temp path 분석

## 문제

`case-response-django-web-one-line-edit` 재실행 run `20260522-144122-response-try02-targeted-p5-opt-out-restraint`에서 with-ddjango 응답이 `/private/tmp/dddjango-eval-workspaces/...` 절대 경로를 markdown file link로 노출했다.

검증 실패:

- `raw/case-response-django-web-one-line-edit-with-dddjango.txt: output contains temporary workspace path`

## 원인

`implementation-django-web` skill은 tiny template text change에서 direct answer를 요구하지만, 임시 workspace에서 파일명을 답할 때 repo-relative/plain path를 쓰라는 제한이 없다. Codex의 일반 file-link 지침과 결합되면 eval sandbox의 절대 경로가 사용자 응답에 새어 나올 수 있다.

## 조치 방향

- tiny template text change / short template explanation 규칙에 temp absolute path 노출 금지를 추가한다.
- copied/temporary workspace에서는 repo-relative plain path를 쓰도록 명시한다.
- runtime cache의 동일 skill 파일도 동기화해 targeted eval이 수정된 지침을 읽게 한다.

## 리뷰

리뷰 방식: sequential-fallback
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰: 추가 subagent 실행 없음. 원인은 run artifact의 응답 본문과 event stream에서 확인했다.
