# S04 Baseline: 같은 파일 충돌의 순차 통합

필수 기대 기준:

- `orders/api.py`를 여러 역할이 병렬 편집하지 않도록 순차 실행을 선택한다.
- Domain Agent는 도메인 로직 분리 기준을 제안하고 API/Django 역할은 같은 파일의 최종 편집자가 되지 않는다.
- Coordinator가 파일 소유권 충돌을 해결하고 최종 적용 순서를 정한다.
- Django Ninja Router/Schema/response mapping은 유지하되 비즈니스 조건은 유스케이스나 도메인으로 이동한다.
- `Handoff Contract`와 `Integration Checklist`를 포함한다.

