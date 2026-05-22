수정 대상: evaluator
원인 분류: evaluator undercheck

# architecture-db P4 direct coverage mixed-case 차단 분석

## 문제

최종 독립 리뷰에서 `architecture_db_direct_tags()`가 `db-architecture`, architecture-db source reference, runtime architecture-db reference만 있으면 DB P4 tag를 direct coverage로 세는 문제가 확인됐다. 현재 pack의 mixed case는 우연히 `db-architecture`를 쓰지 않지만, 향후 mixed API/DDD/workflow case가 같은 tag와 DB reference를 넣으면 개별 architecture-db P4 coverage를 대체할 수 있다.

P4 기준은 여러 skill 연계와 subagent workflow 자체 평가는 P5로 넘기고, 개별 skill 평가를 닫는 것이다. 따라서 구조 validator는 direct architecture-db case와 mixed-boundary case를 구분해야 한다.

## 근거

- `case-response-order-create` 같은 mixed case는 DB 판단을 포함하지만 DDD/API/Test까지 함께 검증하므로 direct architecture-db P4 coverage로 세면 안 된다.
- direct architecture-db case는 `case-response-db-*` id로 추가되어 있고, public/answer 모두 DB 단독 또는 DB 제외 조건을 검증한다.
- 기존 validator는 case id나 mixed coverage tag를 보지 않아 future regression을 놓칠 수 있다.

## 수정 방향

- `architecture_db_direct_tags()`가 `case_id`를 읽고 `case-response-db-` prefix를 요구하게 한다.
- `mixed-boundary`, `db-api-architecture`, `strategic-ddd`, `architecture-api`, `django-ninja`, `workflow`, `risky-write-consistency` 같은 mixed/P5-adjacent tag가 있으면 direct DB coverage로 세지 않는다.
- regression test는 mixed case가 모든 DB P4 tag, `db-architecture`, architecture-db references를 갖고 있어도 missing direct coverage finding이 나오는지 확인한다.

## 리뷰 방식

리뷰 방식: real-subagent

최종 독립 subagent 리뷰에서 mixed-tag case가 direct DB coverage로 잘못 집계될 수 있다는 Major가 확인됐다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0
