# hard-clean-error-contract

Variant: dddjango
Category: clean-code
Title: Hard error contract cleanup
Fixture: none
Mode: refactoring

## Prompt

서비스 함수들이 성공하면 dict, 실패하면 None 또는 문자열 에러코드를 반환해서 API 코드가 if문으로 엉켜 있어. Django Ninja 기준으로 도메인 예외, application service, exception handler, 테스트 구조까지 리팩터링 방향을 보여줘.
