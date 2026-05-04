`superpowers:brainstorming` 지침에 따라 바로 구현 전에 범위를 한 가지 확인해야 합니다. 현재 `/private/tmp/dddjango-codex-eval`은 빈 디렉터리이고 read-only sandbox라 파일 생성/수정은 실행할 수 없습니다. 승인 후에는 코드 내용을 바로 제공하겠습니다.

어떤 형태의 CLI parser가 필요하세요?

1. **무의존성 단일 파일**: `process.argv`만 사용해서 `--name value`, `--flag`, `-v` 정도를 파싱
2. **조금 구조화된 유틸 함수**: 타입 변환, 기본값, 필수 옵션 검사 포함
3. **패키지 기반**: `commander`나 `yargs` 사용

추천은 **2번**입니다. 간단하지만 실제 CLI에서 바로 쓰기 좋은 수준까지 커버할 수 있습니다.