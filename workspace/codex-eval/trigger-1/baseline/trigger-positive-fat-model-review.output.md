현재 `/private/tmp/dddjango-codex-eval`에는 리뷰할 Django 소스가 없습니다.

확인한 내용:
- 작업 디렉터리: `/private/tmp/dddjango-codex-eval`
- 디렉터리 내부 파일 없음
- `models.py`, `manage.py`, `settings.py`, Python 파일 모두 없음
- 사용자 메시지의 `config.toml`은 현재 디렉터리가 아니라 `/private/tmp/dddjango-codex-home/.codex/config.toml`에만 존재했습니다.

그래서 지금 상태로는 “이 Django 모델이 fat model인지”를 구체적으로 판단할 수 없습니다. 리뷰하려면 `models.py` 내용이나 해당 모델 클래스 코드를 보내 주세요. 그러면 다음 기준으로 바로 리뷰하겠습니다:

- 모델이 비즈니스 유스케이스를 직접 수행하는지
- 외부 API, 이메일, 파일, 결제, 알림 같은 I/O를 모델이 직접 호출하는지
- 트랜잭션 흐름이나 orchestration이 모델 메서드에 들어가 있는지
- 도메인 규칙과 애플리케이션 서비스 책임이 섞였는지
- Django ORM 의존이 도메인 로직을 과도하게 잠그고 있는지
- 클린 아키텍처 기준으로 service/usecase/repository로 분리할 지점이 있는지