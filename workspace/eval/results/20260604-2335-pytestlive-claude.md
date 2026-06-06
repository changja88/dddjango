# 채점 결과지 — pytestlive · Claude (DR-42 라이브 검증)

> **런타임**: Claude (`/dddjango`) · **fixture**: `~/Desktop/dddjango-pytestlive-claude` · **채점 일시**: 2026-06-04 23:35
> **목적(정직 경계)**: N=1 sanity — "DR-42(pytest 표준·§6.1 부트스트랩 해지·백스톱 ⑬)가 라이브 런에서 작동하나". **우열·결정성 결론 아님** (Codex와 대조하되 N=1).
> **태스크**: 주문 생성 API(단일 상품+수량, 재고 부족 409) — Codex와 **동일 입력**. 게이트: G0 스코프(멀티라인 trim→단일)·lens ddd·api·db·배치 **설계자가 정함**(미강제, orders 분리 강제 안 함) / G1 승인(API 버전=v1 path 유지·멱등성 미도입) / G2 승인·잔여 nit 미선택 / coder thinking OFF.
> **architect 자율 결정**(배치 미강제): order **별도 독립 BC** + catalog 4계층 이주 — 올바른 분리에 스스로 도달. **구 `catalog/` 완전 삭제로 이주 완결**(Codex와 차이).

---

## ★ DR-42 핵심 축 — 🟢 **pytest 모범 채택** (Codex와 정반대)

| # | 축 | 관측 | 판정 |
|---|---|---|---|
| **ⓐ** | pytest 관용구 | 테스트 전부 **함수형 `def test_*()` + plain `assert` + `@pytest.mark.django_db` + `@pytest.mark.parametrize`**. mock=**`mocker`** 픽스처(`mocker.Mock`·`assert_called_once_with`·`side_effect`, 외부 경계 §7.1 한정). ORM 시드=**factory_boy**(`ProductModelFactory`). per-app `conftest.py`(블랙박스 픽스처). TestCase 0·`self.assert*` 0 | ✅ **PASS** |
| **ⓑ** | greenfield 부트스트랩 (§6.1 해지) | `requirements.txt`에 **pytest==8.4.2·pytest-django==4.11.1·pytest-mock==3.15.1·factory_boy==3.3.3 핀**(§6.2 주석). `pyproject.toml` `[tool.pytest.ini_options]` `DJANGO_SETTINGS_MODULE="config.settings"`(**감지** — 하드코딩 settings.test 아님). **`.venv`에 스택 실제 설치**(부트스트랩 end-to-end 작동) | ✅ **PASS** |
| **ⓒ** | 백스톱 ⑬ (`check-test-config`) | fixture 실행 → **exit 0 = 진짜 준수**(pyproject.toml이 diff에 있고 DSM 바인딩 확인). **Codex의 *부재 fail-open* exit0과 정반대 의미** — 여기선 설정 존재+DSM 결합을 ⑬이 실제 검증해 통과 | ✅ **준수 통과** |
| **ⓓ** | 하니스 pytest 채점 (FC-2 falsifiable) | Claude가 셋업한 `.venv/bin/pytest`로 **48 passed**(0.42s). mutation 주입 시 red(아래 FC-2) | ✅ **PASS** |

**DR-42 결론(Claude·N=1)**: 표준이 pytest를 **모범적으로 자연 채택**. 생산자(coder)가 함수형+`mocker`+factory_boy+`@django_db`로 산출, 부트스트랩(러너 준비)이 venv+핀+설정까지 end-to-end 실행. **Codex(0% 채택·TestCase 폴백)와 N=1 정반대** → DR-42 집행 갭이 **런타임 특정 가능성**(보편 표준 실패 아님)을 시사. 단 N=1이라 run-variance 배제 못 함.

---

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **SD-1** 빈혈: 판정 소유 | `Product.decrease_stock()`(`product.py`)가 `stock<qty→InsufficientStock`·`stock-=qty`·`version+=1`을 도메인 메서드로 소유. "판정 SQL·CAS·재시도는 여기 안 둠" docstring 명시 | ➖ | ✅ | ✅ | 치명 |
| **SD-2** 빈혈: 프로덕션 호출 | catalog `DecreaseStockService.decrease`가 **`repo.get→product.decrease_stock→persist_decrease` 3단계**(빈혈 회귀 차단 명시). OHS→service→domain 경로 실호출 | ➖ | ✅ | ✅ | 치명 |
| **SD-3** 빈혈: 무복제 | `persist_decrease` = `filter(id=, version=captured_version).update(stock=<도메인 절대값>, version=F('version')+1)`. WHERE=version 가드만, SET=도메인 절대값(상대 `F('stock')-qty` 아님). `save()` 금지 docstring. CHECK `stock>=0`은 백스톱 | ➖ | ✅ | ✅ | 치명 |
| **SD-4** 애그리거트 경계 | `place_order_service`가 `Order.place`(도메인 검증) 후 1 `transaction.atomic`에 stock_port.decrease + order_repo.add — **동일 DB 동기 즉시일관성**(§0.3·§0.4 명시). `product_id` ID 값 참조, **ORM FK 없음** | ➖ | ✅ | ✅ | 치명 |
| **SD-5** 모델 표현력 | `Order.place` 팩토리+`quantity≥1` 불변식, `Product`에 `captured_version` 캡슐화(CAS 출처). 도메인서비스 무상태 | ➖ | ✅ | ✅ | 치명 |
| **SD-6** 계층 순수성(P1a) | **clause1=✅(깨끗)**: 도메인 프레임워크 import **0**(grep 확인) — order에 `created_at` 자체가 없어 timezone 불필요(**Codex의 contested `django.utils.timezone` 이슈 회피**). `from __future__ import annotations`로 타입만. **clause2=✅**: 예외→status가 `problem.py` `@api.exception_handler` 중앙 단일 소유, app/domain은 raise만 | ➖ | ✅ | ✅ | 치명 |
| **SD-7** 컨텍스트 통신 | order ACL이 catalog `published_service.write`(OHS) 호출 + catalog 예외 번역을 **ACL 내부에 격리**(final.md:143 허용 지점). presentation/application은 catalog 예외 직접 import 0. OHS는 자기 atomic 안 열고 호출자 경계 합류 | ➖ | ✅ | ✅ | 치명 |

## B. TIER-S 척추 — houserules 충실도 (S-HR)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | catalog·order `application/<app>/` 하위. **구 `catalog/` 완전 삭제**(`D catalog/*` 8파일) = 이주 완결·루트 평면 잔존 0 (**Codex의 §0-1 위반과 정반대**) | ✅ | ✅ | ✅ | 치명 |
| **SH-2** 4계층 | 4 `*_layer/` 양 BC 물리 분리 | ✅ | ✅ | ✅ | 치명 |
| **SH-3** 종류 폴더 | 종류 2차 폴더 충실(`entity/value_object/repository/domain_service/event/specification`·`command/query/dto`·`port`) — §0-4 always-create를 Codex보다 더 완전 실현 | ✅ | ✅ | ✅ | — |
| **SH-4** Django앱 위치 | `models/`·`migrations/`가 `infra_layer/django_{catalog,order}/`. INSTALLED_APPS=점경로 | ✅ | ✅ | ✅ | 치명 |
| **SH-5** ORM 명명 | `ProductModel`/`OrderModel`, 도메인 bare | ✅ | ✅ | ✅ | — |
| **SH-6** 포트/구현 명명 | `ProductStockPort`/`DjangoProductStockAdapter`·`ProductRepository`/`DjangoProductRepository`·`OrderRepository`/`DjangoOrderRepository`. DR-41 헥사고날·`Interface`/`Impl` 0 | ✅ | ✅ | ✅ | — |
| **SH-7** 협력 포트 위치 | `ProductStockPort`가 `order/domain_layer/order/port/` | ✅ | ✅ | ✅ | 치명 |
| **SH-8** ACL 분리 | ACL이 `order/infra_layer/acl/`(+도메인 `port/`), `repository/`에 안 섞임. **단 빈 `infra_layer/adapter/` 폴더 과생성**(경미) | ✅ | ✅ | ✅ | — |
| **SH-9** 단일 레이아웃 | 구 catalog 삭제로 catalog 1개만 존재 — dual-layout 0 (**Codex와 차이**) | ✅ | ✅ | ✅ | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration,e2e}/` + `factories/`. HTTP=integration, 평면 0. e2e 빈 패키지(허용) | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명(조건부) |
|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | `NinjaAPI`(problem.py 소유)+`Router`. plain view·DRF 0. `POST /api/v1/orders` | ✅ | ✅ | ✅ | 치명 |
| **NJ-2** operation 얇음 | `place_order` = command 조립 + `_build_service().place` + `Status(201, OrderOut)`. 비즈로직·ORM·수동파싱 0. **415는 DR-35 `add_decorator(enforce_json_content_type, mode="view")` 공식 레시피**(수제 Parser 아님) | ➖ | ✅ | ✅ | 치명 |
| **NJ-3** Schema 입출력 분리 | `OrderIn`/`OrderOut`/`ProblemOut` 분리, 도메인 직접 직렬화 0 | ✅ | ✅ | ✅ | — (강) |
| **NJ-4** status별 response 선언 | `response={201,404,409,415,422}` + `by_alias`(invalid-params 하이픈 키) | ✅ | ✅ | ✅ | — (강) |
| **NJ-5** operation 문서화 | `summary='주문 생성'`·`tags`·`description`·`Status[OrderOut]` 타입 | ✅ | ✅ | ✅ | — (경미) |
| **NJ-6** ninja 버전 핀 | `django-ninja==1.6.2` + 테스트 스택 핀 | ✅ | ✅ | ✅ | — (경미) |

> **협상 주(ninja 활용 — Codex 대조)**: Claude는 415를 **DR-35 §6.3 공식 데코레이터 레시피**로, 깨진 본문 `Cannot parse request body`→422를 **ninja 1.6.x 버그 인지해 problem.py에서 매핑**, 406 over-build 없음, 수제 JsonResponse 0(중앙 problem 헬퍼 재사용). presentation 파일(`content_negotiation.py`+`problem.py`)은 **표준 처방**이라 과다 아님 — Codex의 수제 Parser+406보다 **leaner·ninja-idiomatic**.

## TIER-S(핵심) — 기능 정확성 (FC)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | 48 passed 그린. 재고10·주문3→201∧남은7 / 재고부족→409∧불변 / 없는상품→404 / 동시(재고1,주문2)→1·201+1·409∧재고0(oversell 0) 인수 테스트로 덮음 | ✅(실행) | ✅ | ✅ | 치명 |
| **FC-2** 테스트 비-vacuous | **mutation 3종 다 잡힘**: M1 차감 `-=`→`+=`=**9 failed** / M2 경계 `<`→`<=`=**2 failed** / M3 `version+=1`→pass=**1 failed**(CAS version까지 테스트가 덮음). 복원 후 48 passed | ✅(mut) | ✅ | ✅ | 치명 |
| **FC-3** 도메인 정합 | 음수 재고 불가(도메인 reject+CHECK), 차감 방향·인과 정상 | ➖ | ✅ | ✅ | 치명 |

## D. TIER-Q 품질

| ID | 항목 | Result | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|
| **Q-1** 스코프/과설계·G1 | 멱등성 **미도입**(코드 grep 0)·멀티라인 없음(단일)·고-blast 트레이드오프 G1 상정(CAS·즉시일관성). presentation은 표준 레시피라 과다 아님. **경미: 빈 `adapter/`·`django_order/admin/` 폴더 과생성**(스켈레톤 약간 초과) | ➖ | ✅ | ✅ |
| **Q-2** API 계약 | RFC 9457 problem+json 일관·`urn:problem:<slug>` 안정 type·422 invalid-params·`/api/v1` URL 버전 일관 | ➖ | ✅ | ✅ |
| **Q-3** §9.6 형식+테스트 실현 | Risky Write **실현**: 인수(oversell 0 블랙박스) + **결정적 주입 스파이**(`_FailingOrderRepository`로 Order 영속 실패→재고 롤백 관찰 = §20.5 결정적 idiom, Codex real-thread보다 엄격) + catalog CAS integration 3종 | ➖ | ✅ | ✅ |
| **Q-4** 메커니즘 소유권 [🔴치명] | 커스텀 백엔드/PRAGMA/몽키패치 0. `OperationalError "locked"` 재시도=표준 예외 처리 | ✅ | ✅ | ✅ |
| **Q-5** 마이그레이션 안전 | 0001 보존·0002 `SeparateDatabaseAndState` state-only rename(db_table 보존)·0003 additive(version+CHECK) | ✅ | ✅ | ✅ |
| **Q-6** 테스트/TDD | `check`+`pytest` 48 그린·행위 덮음·의미군 분리·**pytest 관용구 완전**(함수형·`@django_db`·`@parametrize`)·**`mocker`**·**factory_boy**(영속 시드, 만능 아님) = **DR-42 모범 실현** | ➖ | ✅ | ✅ |
| **Q-7** 경미 | 공개 표면 어노테이션 충실(상수·필드 타입)·주석 한국어 일관·의존성 핀 완전. 경미: 빈 스켈레톤 폴더 2개·StockConflict design-spec 미동기(Claude 자기 nit으로 표면화) | ➖ | 🟡 | 🟡 |

---

## 종합 판정 (EVAL-METHOD §2 사전식 집계)

### 치명 레인 집계 — **전부 ✅**
- **SD-1~7 ✅ · SH-1·2·4·7 ✅ · NJ-1·2 ✅ · FC-1·2·3 ✅ · Q-4 ✅** — 빈혈·경계·순수성(P1a)·통신·컨테이너·스택·기능정확성·메커니즘 **치명 0 위반**.

### 픽스처 판정 = **PASS**
- **치명 레인 무위반 + 비치명 거의 ✅**(Q-7만 🟡 — 빈 폴더·doc nit, 장식성).
- **헤드라인(DR-42) = pytest 모범 채택**(ⓐⓑⓒⓓ 전부 ✅) — 이번 런의 본질 관측이 **성공**.
- **품질 = Codex보다 전반적으로 깨끗**(SD-6 timezone 회피·catalog 이주 완결·ninja 공식 레시피·결정적 CAS 스파이).

---

## ★ 사용자 4개 피드백 렌즈 — Codex vs Claude 대조

| 렌즈 | Codex | Claude |
|---|---|---|
| **① catalog 두 개** | 🔴 구 `catalog/` 잔존(§0-1 위반·SH-1 ❌) | ✅ **완전 삭제·이주 완결** |
| **② pytest 미사용** | 🔴 TestCase 폴백(ⓐⓑ FAIL) | ✅ **함수형+mocker+factory 모범 채택** |
| **③ order published_service 없음** | omit(방어가능) | ✅ **빈 폴더로 포함**(always-create 해석) — *표준 모호점이 런타임 차이로 실증*: Codex=조건부 해석, Claude=always-create 해석 |
| **④ presentation 파일 과다(ninja)** | 🟡 수제 Parser+406+override(과다) | ✅ **DR-35 공식 데코레이터 레시피·406 없음·중앙 problem 재사용**(leaner) |

> **메타**: 4개 렌즈 전부 Claude가 깨끗하거나 우월. 특히 ③은 **표준 텍스트 모호(published_service 필수성 미명시)가 두 런타임의 정반대 해석으로 드러난** 귀중한 데이터 — Codex omit·Claude empty-skeleton. 표준 의도를 명시하면 수렴.
> **🔴 N=1 경계**: 이 대조는 **우열 결론 아님**. 동일 입력 1회씩이라 run-variance·태스크 외 요인 배제 불가. 확정엔 N≥2 + 적대 cross-check 필요. 단 DR-42 집행 갭(Codex 폴백)이 **런타임 특정일 가능성**은 이 런이 강하게 시사.

## 채점 방법 주
- **Serena**: skipped — fixture는 active project 무관 별도 디렉토리·1회성 감사라 기본 도구로 충분.
- **자기보고 검증**: G2 자기보고("48 passed·13 backstop exit0")를 **파일 직접 읽기 + `.venv/bin/pytest` 실행 + 백스톱 ⑬ 직접 실행 + mutation 3종 주입**으로 독립 확인. 모두 일치.
- **N=1 단독 grader 1차 패스** — 우열/결정성 결론 금지. Codex 채점지(`20260604-2311-pytestlive-codex.md`)와 짝.
