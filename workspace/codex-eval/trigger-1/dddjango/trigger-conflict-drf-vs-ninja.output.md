이 프로젝트 정책상 DRF는 사용하지 않고 Django Ninja로 작성합니다.

`Serializer`, `ViewSet`, `APIView`, `DefaultRouter` 기반 코드는 만들지 않고, 같은 API를 Django Ninja의 `Schema` / `Router` / `NinjaAPI.add_router()` 구조로 변환해서 구현하겠습니다.

필요한 정보만 주시면 바로 Ninja 버전으로 작성할 수 있습니다.

- 리소스 이름: 예 `orders`, `products`, `users`
- 필요한 동작: 목록/상세/생성/수정/삭제 중 무엇인지
- 모델 필드 또는 기존 모델 코드
- 인증 필요 여부

참고로 현재 작업 디렉터리(`/private/tmp/dddjango-codex-eval`)에서는 `config.toml`을 찾지 못했고, sandbox가 read-only라 파일 수정이나 실행은 할 수 없습니다. 대신 붙여 넣을 수 있는 Django Ninja 코드로 제공하겠습니다.

---
> **관련 스킬 참조:**
> - API 구현 → **implementation-django-ninja** 스킬
> - REST 엔드포인트 설계 → **architecture-api** 스킬