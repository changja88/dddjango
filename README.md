# dddjango

기존 Django 프로젝트에서 **하나의 기능**을 DDD(도메인 주도 설계) 방식으로 요구 정리 → 설계 → 구현(TDD)까지 단계별 게이트로 끝까지 빌드하는 Claude Code 플러그인이다.

단일 커맨드 `/dddjango <빌드할 기능>` 하나로 시작하면, Coordinator(메인 세션)가 설계·리뷰·인수 테스트·구현·규율 검토를 전문 subagent에 위임하고 사용자 승인 게이트(G0/G1/G2)로 진행을 통제한다.

## 설치

Claude Code에서:

```
/plugin marketplace add changja88/dddjango
/plugin install dddjango@changja88
```

## 사용법

기존 Django 프로젝트의 루트에서 Claude Code를 실행한 뒤:

```
/dddjango 재고가 있을 때만 주문을 생성하고 재고를 차감하는 기능
```

진행 흐름:

1. **G0 — 요구·경계 확정**: Coordinator가 스코프와 바운디드 컨텍스트(BC) 경계를 정리해 승인받는다.
2. **설계**: `design-architect`가 통합 설계 명세를 쓰고, `design-review-{ddd,api,db}` 세 리뷰어가 병렬로 독립 비평한다.
3. **G1 — 설계 승인**: 반영된 설계 명세를 사용자가 승인한다.
4. **구현(TDD)**: `acceptance-tester`가 인수 테스트를, `coder`가 구현을 작성하고 `discipline-reviewer`가 규율을 검토한다.
5. **G2 — 최종 검증**: 테스트 통과·설계 정합성을 보고한다.

산출물은 대상 프로젝트의 `application/<app>/{domain_layer,application_layer,infra_layer,presentation_layer}/` 4계층 구조로 생성되며, 진행 메모는 `.dddjango/<기능-slug>/`에 남는다.

## 구성

- **커맨드 1개**: `/dddjango`
- **에이전트 7개**: `design-architect`, `design-review-ddd`, `design-review-api`, `design-review-db`, `acceptance-tester`, `coder`, `discipline-reviewer`
- **스킬 11개**: 아키텍처(`architecture-ddd`/`-api`/`-db`), 규율(`discipline-houserules`/`-cleancode`/`-tdd`), 구현(`implementation-django`/`-django-ninja`/`-django-web`/`-python`/`-test`)

## 요구 사항

- Claude Code
- 기존 Django 프로젝트 (이 플러그인은 한 기능을 빌드하는 도구이지, 프로젝트를 새로 부트스트랩하지 않는다)

## 라이선스

[MIT](LICENSE)
