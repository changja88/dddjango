# L-F wiring 반증 결과

검토 배선: **117 Work**

`ⓒ = enforcedBy`, `ⓓ = delegatedTo`.  
규범 문면, 검사기 구현·docstring, P0 커버 판정, registry `#N`, spec `basis`를 서로 대조했다.

## 발견

**21 Work에서 반증 성립.** 나머지 96 Work는 현 배선을 유지한다.

| # | Work·문장 요지 | 현 배선 | 주장 배선 | 근거(docstring/문면 인용) |
|---:|---|---|---|---|
| R-0001 | 상태 코드 의미는 `architecture-api` 기준을 따른다 | ⓓ discipline-reviewer | **ⓓ design-review-api** | 문면이 판정 주체를 직접 `architecture-api`로 지정한다. implementation-* 기본값보다 명시 문면이 우선이다. |
| R-0004 | controller가 raw DB·infra 예외를 분류·변환하면 안 된다 | ⓒ ninja-boundary-middleware | **ⓒ api-error-controller-contract** | ninja-boundary는 `MIDDLEWARE` 경로만 검사한다. 반면 API 검사기는 catch 대상이 같은 BC의 application/domain 예외인지 직접 확인한다([API 검사기](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py:3136)). |
| R-0006 | validation error의 기본 body를 BC 전역에서 바꾸지 않는다 | ⓒ ninja-boundary-middleware | **ⓒ ninja-boundary-middleware + api-error-controller-contract, ⓓ discipline-reviewer** | ninja-boundary가 집행하는 것은 BC driving middleware 등록뿐이다([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-ninja-boundary-middleware.py:1)). API 검사기는 Ninja custom exception handler를 금지한다. 프로젝트 전역 converter·간접 등록까지는 정적 검사 범위 밖이므로 reviewer가 필요하다. |
| R-0017 | 상태 변경은 aggregate root 메서드를 실제 production 흐름에서 호출한다 | ⓒ domain-model, ⓓ discipline-reviewer | **현 배선 + ⓒ transaction-boundary** | domain-model은 root 구조를 보지만 호출 흐름은 보지 않는다. transaction-boundary의 `#195`가 변경 use case에서 root 호출 후 `save/remove`를 직접 검사한다([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-transaction-boundary.py:1)). spec basis의 owner-map `#17/#18`은 이 판정이 아니라 폴더 1축 규칙이다. |
| R-0018 | 같은 판단을 application·repository·infra에 복제하지 않는다 | ⓒ domain-model, ⓓ discipline-reviewer | **ⓓ discipline-reviewer만 유지** | domain-model은 모델 구조·root 통과를 검사하지만 infra/application에 복제된 조건식의 의미 동등성은 검사하지 않는다. reviewer 역할문은 “도메인 메서드는 죽어 있고 repository SQL/ORM update가 판단하는” 경우를 명시적으로 감사한다([reviewer](/Users/hyun/Desktop/dddjango/dddjango/agents/dddjango-discipline-reviewer.md:76)). |
| R-0019 | SQL predicate로 도메인 판정을 이전하지 않는다 | ⓒ domain-model | **ⓓ discipline-reviewer** | domain-model에는 SQL/QuerySet predicate 또는 domain 메서드 우회 판정 검사가 없다. 이 항목은 checker coverage가 아니라 의미 감사 대상이다. |
| R-0021 | enum/symbol 소비에서도 도메인 메서드를 우회하지 않는다 | ⓓ discipline-reviewer | **ⓒ choices-literal-consumption + ⓓ discipline-reviewer** | choices 검사기는 symbol-backed choices와 literal default·직접 queryset filter를 결정적으로 잡는다. 동시에 변수 경유·간접 queryset·비승격 판정은 reviewer 몫이라고 docstring이 범위를 명시한다([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-choices-literal-consumption.py:1)). 전부 기본값에 맡긴 것은 부분 누락이다. |
| R-0028 | ORM model→aggregate 이름으로 domain/data-source 골격을 도출한다 | ⓒ layer-skeleton | **ⓒ layer-skeleton + db-table, ⓓ design-review-ddd** | layer-skeleton은 정해진 디렉터리·placeholder 존재만 본다. model로부터 aggregate/data-source 의미를 도출하지 않는다. db-table은 driven ORM 배치를 보완하지만([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-db-table.py:1)), aggregate 경계 도출은 DDD 설계 판정이다. |
| R-0031 | 프로젝트 루트의 flat Django app도 application 안으로 옮긴다 | ⓒ layer-skeleton | **ⓒ app-container** | app-container docstring이 바로 이 차이를 명시한다. layer-skeleton은 `application/` 내부를 검증하고, app-container는 그 밖의 Django app을 차단한다([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-app-container.py:1)). |
| R-0037 | 플러그인은 기본 ErrorSchema 속성을 임의로 정의하지 않는다 | ⓒ error-centralization | **ⓓ discipline-reviewer** | error-centralization은 전달받은 canonical inventory·profile을 기준으로 검증한다. 그 inventory 자체가 “플러그인이 만든 기본값인지”는 판별할 수 없다. 자기 입력을 전제로 하는 검사기에 기본값 비채택 결정을 귀속한 순환 배선이다. |
| R-0038 | 기존 프로젝트 ErrorSchema가 있으면 그 계약을 보존한다 | ⓒ error-centralization | **ⓓ design-review-api** | 검사기 docstring은 `preserve-established`에서 schema semantics를 적용하지 않는다고 명시한다([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-error-centralization.py:1)). 기존 계약의 의미 보존 여부는 API 설계 리뷰 판정이다. |
| R-0044 | 동적 schema shape이면 schema checker가 marker를 항상 낸다 | ⓒ api-error-controller-contract | **ⓒ error-centralization** | 문면이 주체를 명시적으로 “schema checker”라고 부른다. 실제 error-centralization이 동적 inheritance·fields·mapping에서 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`를 발생시킨다. controller checker만 연결하면 schema-only 동적 shape를 놓친다. |
| R-0049 | 두 reviewer가 승인한 뒤 Coordinator가 진행한다 | ⓓ command-dddjango | **ⓓ design-review-api + discipline-reviewer + command-dddjango** | 규범 문면이 “두 reviewer의 확인 후 Coordinator”라는 3주체 절차를 직접 명시한다. Coordinator만 연결한 것은 승인 주체 두 명을 누락한 배선이다. |
| R-0070 | subtype 생성 시 required⊆actual⊆common, 임의 필드 추가 금지 | ⓓ discipline-reviewer | **ⓒ api-error-controller-contract** | API 검사기는 ErrorSchema constructor의 실제 keyword 집합, required/common field 포함관계, `**kwargs` 우회를 직접 검사한다([constructor 검사](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-api-error-controller-contract.py:2890)). 명백한 정적 담당 검사기를 기본 reviewer로 회피했다. |
| R-0085 | DTO를 application에 두고 composition root에서 조립한다 | ⓒ composition-root | **ⓒ composition-root + usecase-dto-placement** | composition-root는 DI와 registrar wiring만 검사하며 DTO 배치를 검사하지 않는다. usecase-dto-placement가 command/query/result DTO의 application 배치와 계약을 직접 담당한다([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-usecase-dto-placement.py:1)). |
| R-0095 | 401/403/404/422/429 등 framework-owned 오류는 BC가 소유하지 않는다 | ⓒ ninja-boundary-middleware | **ⓒ business-vocabulary + api-error-controller-contract, ⓓ discipline-reviewer** | ninja-boundary는 middleware 경로 검사라 오류 소유권을 집행하지 않는다. business-vocabulary docstring `#119`가 framework-owned 상태를 열거하고, API 검사기는 BC controller의 예외 provenance·global handler를 제한한다. 목록 전체의 간접 소유는 reviewer 보완이 필요하다. |
| R-0096 | framework 오류를 BC 전역 handler/catch-all mapper로 재포장하지 않는다 | ⓒ ninja-boundary-middleware | **ⓒ api-error-controller-contract** | API 검사기가 `exception_handler`/`add_exception_handler`, catch-all 및 own-BC 밖 예외 매핑을 직접 금지한다. middleware 설정만 읽는 ninja-boundary에는 이 계약을 집행할 코드가 없다. |
| R-0102 | controller가 SQLSTATE·vendor 문자열로 raw infra 오류를 판정하지 않는다 | ⓒ ninja-boundary-middleware | **ⓒ api-error-controller-contract + ⓓ discipline-reviewer** | API 검사기는 controller가 raw DB/framework 예외를 catch하는 직접 위반을 잡는다. SQLSTATE/vendor 문자열의 간접 recognizer 의미 판정은 reviewer 범위다. ninja-boundary는 둘 다 검사하지 않는다. |
| R-0105 | driven adapter가 raw 예외를 합성하지 않고, 다른 BC의 application exception을 통과시키지 않는다 | ⓓ discipline-reviewer | **ⓒ synthetic-infra-exc + context-isolation, ⓓ discipline-reviewer** | synthetic-infra-exc가 raw DB exception의 synthesis·catch-all translation을 직접 검사하고([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-synthetic-infra-exc.py:1)), context-isolation은 다른 BC 예외의 직접 import를 잡는다. 간접 경로만 reviewer에 남겨야 한다. |
| R-0111 | 200–203 성공 응답이 선언 schema를 우회하지 않는다 | ⓓ discipline-reviewer | **ⓒ response-schema-bypass** | 검사기 docstring이 “declared Ninja schema를 우회하는 direct raw 200–203 return 차단”을 정확히 계약으로 선언한다([docstring](/Users/hyun/Desktop/dddjango/dddjango/scripts/check-response-schema-bypass.py:1)). |
| R-0112 | File/stream/redirect 및 schema-less 204만 성공 schema 우회 예외다 | ⓓ discipline-reviewer | **ⓒ response-schema-bypass** | 같은 검사기가 FileResponse·StreamingHttpResponse·redirect·204 carveout을 구현하고, 그 밖의 raw 성공 응답만 차단한다. 예외 목록까지 구현된 담당 검사기를 reviewer 기본값으로만 둔 것은 누락이다. |

`basis` 필드와 TTL 트리플의 **기계적 불일치는 0건**이다. 117개 모두 spec의 `enforcedBy`/`delegatedTo` 기재와 TTL이 일치했다. 다만 R-0017처럼 basis가 인용한 registry 번호의 의미가 해당 Work를 뒷받침하지 않거나, R-0038처럼 인용 검사기가 해당 profile에서 의미 검사를 명시적으로 하지 않는 **근거 내용의 오인용**은 위 발견에 포함했다.

## 집계

### 검사기별 배선 수

| 검사기 | 현행 | 주장 배선 |
|---|---:|---:|
| api-error-controller-contract | 23 | **28** |
| app-container | 0 | **1** |
| business-vocabulary | 0 | **1** |
| choices-literal-consumption | 0 | **1** |
| composition-root | 1 | 1 |
| context-isolation | 1 | **2** |
| db-table | 0 | **1** |
| domain-model | 3 | **1** |
| error-centralization | 17 | **16** |
| layer-skeleton | 5 | **4** |
| ninja-boundary-middleware | 6 | **2** |
| openapi-error-declaration | 5 | 5 |
| response-schema-bypass | 0 | **2** |
| synthetic-infra-exc | 0 | **1** |
| transaction-boundary | 0 | **1** |
| usecase-dto-placement | 0 | **1** |
| **검사기 트리플 합계** | **61** | **69** |

### 에이전트별 배선 수

| 에이전트 | 현행 | 주장 배선 |
|---|---:|---:|
| design-review-api | 6 | **9** |
| design-review-ddd | 13 | **14** |
| discipline-reviewer | 29 | **31** |
| command-dddjango | 12 | 12 |
| **에이전트 트리플 합계** | **60** | **66** |

- 현행 배선 트리플: **121** — 117 Work 중 복수 배선 4건 포함.
- 주장 배선 트리플: **135** — 복합 규범을 검사기·의미 reviewer·Coordinator로 분해한 결과.
- 판정 변경: **21 Work**
- 판정 유지: **96 Work**
- spec basis–TTL 형식·값 불일치: **0 Work**
- 파일 변경: **없음**
- graphify: `graphify-out/graph.json` opt-in 표식이 없어 생략.
- Serena: `.serena/project.yml`이 없어 생략. 기본 읽기·검색으로 전수 대조.