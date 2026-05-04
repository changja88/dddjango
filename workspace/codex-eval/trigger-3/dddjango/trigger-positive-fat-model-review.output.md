**검토 결과**

현재는 Django 모델을 실제로 리뷰할 수 없습니다. 지정된 작업 디렉터리인 `/private/tmp/dddjango-codex-eval`이 비어 있고, AGENTS.md에서 지시한 `config.toml`도 해당 경로에 없습니다.

확인한 내용:

```bash
pwd
# /private/tmp/dddjango-codex-eval

ls -la
# total 0
# . ..
```

Django 모델/프로젝트 파일도 발견되지 않았습니다.

```bash
rg --files -g '!*migrations*'
find . -maxdepth 3 -type f \( -name 'models.py' -o -path '*/models/*.py' \)
find /private/tmp -maxdepth 5 -type f \( -name 'models.py' -o -name 'manage.py' -o -name 'settings.py' -o -name 'config.toml' \)
```

발견된 것은 `/private/tmp/dddjango-codex-home/.codex/config.toml`뿐이고, 리뷰 대상 Django 코드가 아닙니다.

리뷰하려면 다음 중 하나가 필요합니다.

1. 리뷰할 Django 모델 파일 경로
2. `models.py` 또는 모델 클래스 코드
3. 실제 프로젝트가 있는 디렉터리 경로

코드를 받으면 다음 기준으로 위험도 순서대로 보겠습니다.

- Django 모델이 유스케이스 조율, 외부 I/O, 트랜잭션, 알림 발송까지 맡는지
- 도메인 규칙과 ORM 영속성 책임이 과하게 결합됐는지
- `save()` 내부에 비즈니스 플로우나 외부 호출이 숨어 있는지
- 상태 전이가 단순 필드 대입으로 열려 있는지
- 값 객체/도메인 예외로 표현해야 할 개념이 원시 타입이나 일반 예외로 남아 있는지
- 단순 CRUD인데 과한 Repository/Service 추상화를 도입하려는 상황인지

---
> **관련 스킬 참조:**
> - Django fat model / 클린 아키텍처 리뷰 → **architecture-implementation-patterns** 스킬
> - 애그리거트·도메인 규칙 위치 판단 → **architecture-ddd** 스킬
> - God Class·SRP·CQS 관점 코드 품질 리뷰 → **implementation-cleancode** 스킬