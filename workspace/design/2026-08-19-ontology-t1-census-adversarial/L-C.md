# L-C codex SAME 반증 결과

## 발견 (SAME→DIFF 주장)

| # | 문서쌍 | claude 문면 | codex 문면 | 판정 근거 |
|---:|---|---|---|---|
| 1 | acceptance-tester s001 | `skills:`<br>`- dddjango:discipline-tdd`<br>`- dddjango:implementation-test`<br>`- dddjango:architecture-api`<br>`- dddjango:architecture-ddd`<br>`- dddjango:implementation-django-ninja` | “`discipline-tdd`를 먼저 로드해 입장 결정을 확인한 뒤, `dddjango-implementation-test`, `architecture-api`, `dddjango-architecture-ddd`를 입장된 외부 행의 작성 근거로 로드한다.” | Claude의 필수 로드 목록은 5종인데 Codex는 4종이며 `implementation-django-ninja`가 삭제됐다. 인수 테스트의 mounted client·Ninja 계약 mechanics 근거가 빠진 목록 항 차이이므로 DIFF다. |
| 2 | acceptance-tester s004 | “implementation-test의 계약 테스트 패턴(기본은 실제 URLconf에 mount된 public client, 별도 승인된 adapter-local 계약만 그 경계의 client), discipline-tdd의 바깥 루프(Outside-In) 원칙, architecture-api·architecture-ddd의 계약·행위 정의를 근거로 따른다.” | “implementation-test의 계약 테스트 패턴(기본은 실제 URLconf에 mount된 public client, 별도 승인된 adapter-local 계약만 그 경계의 client), discipline-tdd의 바깥 루프(Outside-In) 원칙, architecture-api·architecture-ddd의 계약·행위 정의를 근거로 따른다.” | 문자열은 같지만 Codex에는 `implementation-test`·`architecture-ddd` 스킬이 없고 각각 `dddjango-implementation-test`·`dddjango-architecture-ddd`만 존재한다. Claude에서는 유효한 근거 지시가 Codex에서는 미치환된 무효 대상이 된 것으로, 2개 스킬명 치환 누락이므로 DIFF다. |
| 3 | implementation-django-ninja SKILL s001 | “테스트 픽스처·더블 구현은 implementation-test로 위임.” | “테스트 픽스처·더블 구현은 implementation-test로 위임.” | Codex 본문 경계에서는 정확히 `dddjango-implementation-test`로 치환됐지만 frontmatter description만 구명 `implementation-test`를 유지한다. Codex에 그 이름의 스킬이 없으므로 라우팅 규범이 서로 달라 DIFF다. |
| 4 | architecture-db SKILL s001 | “도메인 이벤트 채택 여부는 architecture-ddd로 위임.” | “도메인 이벤트 채택 여부는 architecture-ddd로 위임.” | Codex 본문은 `dddjango-architecture-ddd`로 올바르게 치환됐지만 description은 존재하지 않는 구명 `architecture-ddd`를 지시한다. 동일 문자열이 양 플랫폼에서 서로 다른 유효성을 가지는 치환 누락이므로 DIFF다. |

## 기존 DIFF 13건 타당성

13건 전부가 타당하지는 않다: E01 s001·E04 s001·E05 s001은 현 기준상 허용된 `dddjango-` 개명/`user-invocable: false` 유무뿐이므로 SAME이어야 하며, 나머지 10건은 타당하다(E03·E06 s001은 Codex description의 미치환 `implementation-test` 지시 때문에 DIFF 유지). Serena: skipped — `.serena/project.yml` opt-in 표식 없음.