# H01 Baseline: DRF legacy code migration without reproducing DRF

좋은 답변은 기존 DRF 코드를 분석 대상으로만 다루고, 신규 코드는 Django Ninja
Router, Schema, response mapping으로 작성해야 한다. 새 코드 블록에
`rest_framework`, `ModelSerializer`, `ViewSet`을 재생성하면 실패한다.

마이그레이션 계획은 호환 기간, URL 전환, 테스트, 검증 명령을 포함해야 한다.
