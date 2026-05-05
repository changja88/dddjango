지정된 fixture 경로와 워크스페이스를 확인했지만 리뷰할 파일이 없습니다.

확인 결과:
- `/Users/hyun/Desktop/dddjango/none`: 존재하지 않음
- `/private/tmp/dddjango-codex-eval`: 파일 없음

그래서 “fixture 파일을 읽은 뒤”라는 조건을 만족할 수 없어, 특정 테스트에 대한 라인 단위 리뷰나 unified diff는 만들 수 없습니다.

일반적인 pytest/Django 테스트 개선 기준은 다음처럼 잡으면 됩니다.

1. DB fixture 의존 줄이기
- 전역 JSON/YAML fixture보다 테스트 안에서 필요한 데이터만 생성
- `factory_boy`, `model_bakery`, pytest fixture factory 사용
- 테스트가 fixture 내부의 숨은 PK, 정렬, 기존 데이터 개수에 의존하지 않게 하기
- 공통 fixture는 “도메인 의미가 분명한 최소 객체”까지만 허용

2. assert 강화
- `assert response.status_code == 200`만 두지 말고 응답 본문, DB 변경, 권한 효과까지 검증
- `count()`만 검증하지 말고 생성된 객체의 핵심 필드 검증
- 실패 케이스는 에러 메시지, form errors, validation code까지 확인
- list/detail API는 포함되어야 할 객체와 제외되어야 할 객체를 함께 검증

3. 테스트 독립성 확보
- 테스트 실행 순서에 의존하지 않기
- fixture 데이터의 기존 상태를 수정하지 않기
- PK 하드코딩 대신 생성된 객체 참조 사용
- 시간, 사용자, 권한, 설정값은 테스트 안에서 명시적으로 고정

4. pytest 스타일 개선
- Given/When/Then 흐름이 보이도록 테스트 본문 정리
- fixture 이름은 데이터 의미를 드러내기: `user`, `admin_user`, `published_post`
- 너무 큰 fixture는 작은 fixture factory로 분리
- parametrization으로 같은 규칙의 입력/출력 케이스를 명확히 표현

리뷰 대상 파일이나 fixture 디렉터리를 다시 제공해주면, 실제 코드 기준으로 finding 형식이나 unified diff 형태로 정리할 수 있습니다.