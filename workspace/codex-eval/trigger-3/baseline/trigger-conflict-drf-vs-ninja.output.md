현재 `/private/tmp/dddjango-codex-eval` 작업 디렉터리가 비어 있어서 API를 구현할 파일이 없습니다. 또한 세션이 `read-only`라 파일 생성/수정도 막혀 있습니다.

확인한 내용:
- 현재 디렉터리: `/private/tmp/dddjango-codex-eval`
- 프로젝트 파일 없음: `manage.py`, 앱 코드, settings 파일 없음
- `config.toml`은 `/private/tmp/dddjango-codex-home/.codex/config.toml`에 있었고, 기본 규칙은 “API는 Django Ninja”지만 이번 요청은 명시적으로 “이번 API만 DRF” 예외로 이해하겠습니다.

진행하려면 다음 중 하나가 필요합니다:
1. 실제 Django 프로젝트가 있는 경로를 알려주세요.
2. 이 디렉터리에 프로젝트 파일을 배치한 뒤 다시 요청해주세요.
3. 구현할 API 스펙을 주세요: 리소스명, 모델, URL, 메서드, 요청/응답 필드, 인증 여부.

프로젝트가 준비되면 이번 API만 DRF `Serializer`/`APIView` 또는 `GenericAPIView` 기반으로 붙이고, 기존 Ninja 라우팅과 충돌하지 않게 URL을 분리해서 구현하겠습니다.

---
> **관련 스킬 참조:**
> - DRF 예외 구현 및 Django 통합 → **implementation-django** 스킬