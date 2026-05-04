## [주요 내용]

현재 `/private/tmp/dddjango-codex-eval`은 프로젝트 파일이 없고, AGENTS가 참조한 `config.toml`도 존재하지 않습니다. 또한 현재 세션은 read-only라 Flask 파일 생성, 의존성 설치, pytest 실행, 서버 실행은 할 수 없습니다.

구현 전에 한 가지만 확인하겠습니다.

Todo 데이터 저장 방식은 무엇으로 할까요?

1. **인메모리 저장소**: 가장 단순합니다. 서버 재시작 시 데이터가 사라집니다.
2. **SQLite**: 작지만 실제 API에 가깝습니다. 재시작 후에도 데이터가 남습니다.
3. **기존 DB/ORM 전제**: 이미 쓰려는 데이터베이스나 구조가 있을 때 맞춥니다.

추천은 **SQLite**입니다. Todo 생성 API라도 `201 Created`, `Location` 헤더, 유효성 검증 실패 시 Problem Details 형식까지 확인하기에 적당합니다.

---
> **관련 스킬 참조:**
> - REST 엔드포인트/상태 코드/오류 응답 → **architecture-api** 스킬
> - Python 구현 컨벤션 → **implementation-python** 스킬
> - 테스트 우선 구현 흐름 → **implementation-tdd** 스킬