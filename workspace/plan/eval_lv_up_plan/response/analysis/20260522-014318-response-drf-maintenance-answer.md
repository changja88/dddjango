수정 대상: answer
원인 분류: answer missing

# response DRF maintenance answer 누락 분석

## 문제

response bucket validator 실행 중 `case-response-django-drf-maintenance.md` public case에 대응하는 answer oracle이 없어 public/answer mismatch가 발생했다. 이 case는 architecture-db P4 직접 coverage는 아니지만, 현재 response bucket 전체 validator를 막고 있어 필수 검증을 완료할 수 없다.

## 근거

- public case는 기존 DRF `OrderViewSet` 유지보수, `fields = "__all__"` 노출 위험, viewset action 안의 상태 전이와 알림 발송 책임 이동을 묻는다.
- `implementation-django` skill은 existing DRF maintenance/review를 담당하며, 기존 DRF 코드는 adapter로 유지하되 durable business rule, transaction ownership, side-effect timing은 model/service/selector/database boundary로 옮기라고 안내한다.
- answer oracle이 없으면 response bucket pack 구조가 깨져 architecture-db P4 필수 validator를 실행할 수 없다.

## 수정 방향

- public case 문구는 그대로 둔다.
- `case-response-django-drf-maintenance.yaml` answer oracle을 추가한다.
- source basis는 `implementation-django`, DRF guardrail, service/selector reference로 둔다.
- answer 요구는 기존 DRF maintenance 범위에 제한하고, greenfield DRF 추천이나 강제 Django Ninja migration은 금지한다.

## 리뷰 방식

리뷰 방식: sequential-fallback

현재 발견은 validator 실행 중 확인한 구조 mismatch이며, architecture-db P4 리뷰 findings를 닫기 위한 부수 정리다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0
