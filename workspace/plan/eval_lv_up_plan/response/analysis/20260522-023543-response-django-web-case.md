수정 대상: case
원인 분류: case

## 배경

`implementation-django-web` P4 점검에서 response bucket의 관련 case를 확인했다. 기존 `case-response-web-typing`은 Django Web과 Python typing 책임 구분을 보는 mixed-boundary case라서, 개별 skill 평가 기준으로 TemplateView/Generic CBV/FBV, templates/base/includes, static CSS/JS, web forms, HTMX/CSRF, auth/permissions, render acceptance, REST/ORM 제외 조건을 직접 검증하지 못한다.

## 문제

- 직접 positive case가 없다.
- public case가 `implementation-django-web`의 핵심 사용 조건과 제외 조건을 한 번에 유도하지 않는다.
- answer oracle은 mixed-boundary 판정이라 P4의 "개별 skill 평가" 종료 조건을 충분히 증명하지 못한다.

## 수정 방향

- response bucket에 `case-response-django-web-page` public case와 answer oracle을 추가한다.
- public case는 사용자 요청으로만 구성하고 answer oracle, private 기준, 이전 run finding을 포함하지 않는다.
- answer oracle은 source reference와 runtime bundled reference를 근거로 direct Django Web 기준만 검증한다.

## 리뷰 기록

리뷰 방식: not-run
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

Subagent 리뷰/순차 fallback: 아직 수정 전이므로 실행하지 않았다. 수정 후 별도 subagent 리뷰로 최종 판정한다.
