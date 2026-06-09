# 채점 결과지 — ptbootlive-claude (도구 미설치 깨끗 baseline · Tier-1 부트스트랩 관측 + carve-out/이주배타성 재검증)

> **방법** EVAL-METHOD v3(+§1.1.T) · **채점일** 2026-06-09 · **픽스처** `~/Desktop/dddjango-ptboot-claude`(기존규약: 평면 `catalog.Product` 선재·baseline `298e204`·**테스트도구 미설치·pytest 설정 없음**) · **런타임** Claude(plugin 캐시 `1.0.0`·소스 `015945c` = carve-out/이주배타성 커밋 반영·16백스톱·⑰부재) · **N** 1 · **태스크 요지** "재고 부족 409·충분 시 차감 주문 생성 API"(ptboot-codex와 동일 — N=2 통제) · **게이트** 새 BC·내부전용·ninja-extra 클래스 컨트롤러·thinking OFF · **범례** ✅PASS ❌FAIL 🟡WEAK/경미 ⏸️보류 ➖N/A
> **⚠️ 단서**: `N_grader`=2(적대 2명)+조정자 결정레인 — full ≥3 미달 · **FC-2 조정자 직접 mutation 실측**(경계·부호 주입→pytest) · 백스톱 16종·pytest·EP 전부 **조정자 직접 검증**(자기보고 불신) · N=1·단일태스크 → 우열결론 아님
> **fixture 도구 환경(§1.1.T — 필수 필드)**: **baseline venv = 테스트도구 0**(조정자 미개입 깨끗 baseline) → 이번 런의 venv 도구·핀은 **전부 Claude 산출(`produced`)**. 채점은 Claude 산출 venv 그대로 실행(조정자 추가 설치 0 — 오염 없음).

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | **catalog = 판정 소유 BC 승격**(MQ0=Y·MQ1=Y·MQ2=N: `Product.deduct_stock` 재고판정+불변식+version)·ordering=신규 → §0 전부 강제 |
| ② 치명 게이트 | **FAIL 0건 → 통과.** SD-1~7(7/7)·SH-1·2·3·4·7·NJ-1·2·Q-4·FC-1·**2**·3 전부 PASS |
| ②.5 실질성 관문 | PASS(빈 골격 아님·양 BC 도메인 판정 실코드·테스트 58 실재·비-vacuous) |
| ③ 비치명·의미변종 | 의미적 변종 **0건** · **WEAK 0건** |
| ④ TIER-Q 등급 | 품질 **상**(WEAK 0·FAIL0: Q-1~7·NJ-1~7 전부 PASS) |

**한 줄 요지**: **§1.1.T Tier-1 설치+핀 완전 이행**(`requirements-dev.txt`로 production/dev 의존성 **분리** 핀 — 더 정교) · **FC-2 PASS**(경계 단위케이스 보유) · **에러 경로 완전**(ninja.responses.Response·HttpError 핸들러·IntegrityError·OperationalError 분기·ACL-EX2 전파) · **종합 PASS·품질 상**(WEAK 0). **ptboot-codex가 흠이었던 NJ-1/HttpError/NJ-5/ACL-EX2를 Claude는 전부 준수** — 단 N=1·런간 비결정(DR-34/35 반전 패턴) → 우열결론 아님.

**2차원 라벨**: (정적: **준수** — 치명0·WEAK0) × (라이브: **관측** — §1.1.T Tier-1 설치+핀·FC-2 mutation red·EP 매트릭스 problem+json 전수·백스톱16 exit0) · `폴더 동작`: 미검증(재빌드 아님) · `에러경로 계약`: **관측**(EP-1~4 + non-transient 전부 `application/problem+json` 실측·§6.2:516 HttpError 준수)

---

## §1.1.T 테스트 도구 관측 매트릭스 (env ≠ produced ≠ used)

| 축 | 관측 | 근거 |
|---|---|---|
| **env** (채점 전 venv) | 테스트도구 **0** | baseline `298e204`(조정자 미개입) |
| **produced** (Claude 설치+핀) | **설치 Y · 핀 Y (dev 분리)** | venv `pytest 8.3.5`·`pytest-django 4.9.0`·`pytest-mock 3.14.0`·`factory_boy 3.3.1`·`faker` 설치 + **`requirements-dev.txt`** `-r requirements.txt` + Tier-1 4종 핀(주석 "§2.1") + `pyproject.toml` pytest 설정. **production/dev 의존성 분리** = §2.1 핀 + 모범 패턴 |
| **used** (실제 사용) | **mocker·factory_boy 실사용** | `test_deduct_stock_command.py:34·54·69·84·106` `mocker.Mock()`·`test_place_order_cas_concurrency.py` `mocker.patch.object(autospec=True)` · `product_model_factory.py:9` `factory.django.DjangoModelFactory`·`factory.Sequence` |
| **판정** | **(설치 Y)×(핀 Y) = §2.1 완전 준수** | used에서 mocker/factory_boy *이름* 실사용(Codex의 수제 Fake와 대비·둘 다 정당). dev 분리는 더 정교 |

---

## A. TIER-S 척추 — S-DDD

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SD-1 | 빈혈: 판정 소유 | ddd §3.2 | `catalog/domain_layer/product/product.py:31-36` `if self.stock < quantity: raise OutOfStock`+`stock-=`+`version+=`·`ordering/domain_layer/order/order.py` `Order.place` 수량·단가·합계 불변식 | ➖ | ✅ | ✅ | ✅ |
| SD-2 | 빈혈: 프로덕션 호출 | §3.2·3.6 | `deduct_stock_command.py` 도메인 `Product.deduct_stock` 호출 + CAS 재시도 루프(소진→`StockUpdateContention`)·죽은코드 아님 | ➖ | ✅ | ✅ | ✅ |
| SD-3 | 빈혈: 무복제 | §3.2 | `catalog/infra_layer/repository/product_repository.py:37-45` `filter(id=,version=expected_version).update(stock=,version=)` — version CAS만·`stock__gte=` 복제 0(check-anemic exit0; DB CHECK stock>=0은 비음수 백스톱·판정 아님) | ✅ | ✅ | ✅ | ✅ |
| SD-4 | 애그리거트 경계 | §3.3 | 1 `atomic`·`order_model.py` `product_id=PositiveIntegerField`(ID참조·FK 0·DR-37)·CHECK 3종(quantity≥1·unit_price≥1·total=곱) | ✅ | ✅ | ✅ | ✅ |
| SD-5 | 모델 표현력 | §3.1·3.5 | `Product` bare 도메인·`Order`·VO·유비쿼터스(deduct/place) | ✅ | ✅ | ✅ | ✅ |
| SD-6 | 계층 순수성(P1a) | §5.1·6.1; ninja §6.2 | domain/application HTTP·status·problem 0(grep·docstring 1건 제외)·status 변환은 `config/api.py` 중앙핸들러만·command/controller 도메인예외 전파 | ✅ | ✅ | ✅ | ✅ |
| SD-7 | 컨텍스트 통신 | §3.2(3)·2.5 | ordering ACL `product_stock_adapter.py:17·28` catalog `DeductStockCommand`/`DjangoProductRepository` 직접 import·**OHS 미노출 시 ACL 직접통합 §2:144 명시 허가**·ordering 비-ACL 레이어 catalog import **0**(격리)·예외 3종 전수 치환(from) | ✅ | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| SH-1 | 컨테이너 | §0-1 | 신규앱 `application/<app>/`·**옛 루트 `catalog/` husk 없음**(`git mv`(R)로 이주·`catalog/` 디렉토리 0·INSTALLED_APPS 탈등록) — Codex의 빈 dir 잔존 결함 없음 | ✅ | ➖ | ✅ | ✅ |
| SH-2 | 4계층 | §0-2 | 양 BC `{domain,application,infra,presentation}_layer/` 완비 | ✅ | ➖ | ✅ | ✅ |
| SH-3 | 종류폴더+거주명명 | §0-3·4 | 양 BC `command/`·`dto/`·`query/`·`handler/`·`entity/`·`value_object/`·`repository/`·`specification/`·`event/`·`domain_service/`·`port/`·`api/`·`schema/` 실재(check-layer-skeleton exit0) | ✅ | ✅ | ✅ | ✅ |
| SH-4 | Django앱 위치 | §0-5 | `django_catalog/{models,migrations,admin}/`·`django_ordering/...`·`db_table='catalog_product'`·`label` 보존 | ✅ | ➖ | ✅ | ✅ |
| SH-5 | ORM 명명 | §0-6 | `ProductModel`·`OrderModel`·도메인 `Product`/`Order` bare | ✅ | ➖ | ✅ | — |
| SH-6 | 포트/구현 명명 | §4 | `ProductStockPort`↔`DjangoProductStockAdapter`·`Interface`/`Impl`/`_repo.py` 0 | ✅ | ➖ | ✅ | — |
| SH-7 | 협력 포트 위치 | §2 | `ordering/domain_layer/order/port/product_stock_port.py`·`product_snapshot.py` | ✅ | ➖ | ✅ | ✅ |
| SH-8 | ACL 분리 | §2·3 | `ordering/infra_layer/acl/product_stock_adapter.py`·repository 미혼합 | ✅ | ✅ | ✅ | — |
| SH-9 | 단일 레이아웃 | §1.4 | 단일 `test/` | ✅ | ➖ | ✅ | — |
| SH-10 | 테스트 의미군 | §1.3 | `test/{unit,integration,e2e,factories}/`·HTTP=integration | ✅ | ✅ | ✅ | — |

## TIER-S(조건부) — S-NINJA

| ID | 항목 | §근거 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| NJ-1 | 스택 채택 | §1.1·10 | `config/api.py:16` **`from ninja.responses import Response`**(§6.2:487 처방 준수)·`:36` `NinjaExtraAPI`·`order_controller.py:26` `@api_controller`·`ControllerBase` 미상속(DR-48)·DRF 0 | ✅ | ✅ | ✅ | ✅ |
| NJ-2 | operation 얇음 | §1.3·2.2 | `order_controller.py:43-60` schema→Request 매핑+`execute`+`Status(201,…)`만·json.loads/ORM/비즈분기 0 | ➖ | ✅ | ✅ | ✅ |
| NJ-3 | Schema 입출력 분리 | §2.2·3.1 | `schema_in.py OrderIn`(Field ge/le)/`schema_out.py OrderOut`/`error_out.py ErrorOut` 분리 | ✅ | ✅ | ✅ | —(강) |
| NJ-4 | status별 response 선언 | §2.2 | `order_controller.py:32-39` `response={201,409,404,422,503,500}` | ✅ | ✅ | ✅ | —(강) |
| NJ-5 | operation 문서화 | §2.2 | `order_controller.py:43` **`-> Status[OrderOut]` 타입파라미터 有**(Codex bare 대비 PASS)·`summary`/`description` | ✅ | ➖ | ✅ | —(경미) |
| NJ-6 | ninja 버전 핀 | §2.1 | `requirements.txt:2-3` ninja 2종 핀 + `requirements-dev.txt` 테스트스택 4종 핀(dev 분리) | ✅ | ➖ | ✅ | —(경미) |
| NJ-7 | 오류 변환 완전성(catch-all) | §6.2 | `config/api.py:161` `@api.exception_handler(Exception)`+`logger.exception`·**`:102` `@api.exception_handler(HttpError)`**(깨진본문→problem+json·§6.2:516 준수·실측 EP-1=problem+json)·`:155` `IntegrityError` 핸들러·`:140` `OperationalError` 시그니처 분기 | ✅ | ✅ | ✅ | —(강) |

## TIER-S(핵심) — FC

| ID | 항목 | Result(조정자 검증) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| FC-1 | 골든 오라클 | 재고충분→201∧차감∧order1 / 부족→409∧불변∧0 / 미존재→404 / 무효q=0→422 / 동시→oversell0 / 락→503 — 전부 일치(58 passed) | ➖ | ✅ | ✅ | ✅ |
| **FC-2** | 테스트 비-vacuous | **경계 `<`→`<=` = 3 failed(`test_deduct_stock_allows_exact_depletion_to_zero` 단위 경계케이스 보유) · 차감 `-=`→`+=` = 12 failed** → **다 red·복원 후 58 passed**. 단위+통합 경계 견고(Codex는 통합만) | ✅(주입실측) | ✅ | ✅ | ✅ |
| FC-3 | 도메인 정합 | 음수재고 불가(`product.py:31` 가드+migration CHECK stock>=0)·차감 정방향·인과 정상 | ➖ | ✅ | ✅ | ✅ |

## C. 기존규약 마스크 (적용 메모)

- **MQ0**=Y(옛 `catalog/*.py` git `D`/`R` + `application/catalog/` 재생성). **MQ1**=Y(`product.py:31-36` `Product.deduct_stock` 재고판정·차감·version). **MQ2**=N(판정 소유·순수 데이터소스 아님).
- → catalog **판정 소유 BC 승격**(도메인 실코드 SD-1~3 PASS 교차)·위치·골격 충족. ordering = 신규 주문 앱. **ptboot-codex(order 판정소유)와 반대 분해** — 재고판정 소유 BC가 런마다 다름(underdetermined·둘 다 방어가능). **ptcat-codex(catalog 판정소유)와는 동일 분해.**

## §1.1.T·D. TIER-Q 품질

| ID | 항목 | §근거 | Result(조정자 검증) | 종합 |
|---|---|---|---|---|
| Q-1 | 스코프/과설계 | ddd §6.8 | 415/406 발명 0(내부전용·design-spec C정책)·멱등성 범위외·503 transient 정당·과설계 없음 | ✅ |
| Q-2 | API 계약 | api §4~14 | RFC 9457 problem+json 단일 헬퍼(`config/api.py:39-55`)·안정 type URI(`urn:problem:ordering:*`)·503 Retry-After·**깨진본문도 problem+json**(HttpError 핸들러) | ✅ |
| Q-3 | §9.6 형식+테스트 | db §9.6 | catalog `test_deduct_stock_command_cas`(결정적 version 충돌 스파이·재시도 수렴·소진)·ordering `test_place_order_cas_concurrency`(`mocker.patch.object autospec` 충돌 주입·oversell0)·실 동시성·non-transient→500 테스트 | ✅ |
| Q-4 | 메커니즘 소유권 **[🔴치명]** | db §9.5 | 커스텀 백엔드/PRAGMA/몽키패치 0(check-mechanism-ownership exit0) | ✅ |
| Q-5 | 마이그레이션 안전 | db §11 | `0001` 불변·`0002` `SeparateDatabaseAndState`(state-only `RenameModel`+`AlterModelTable`·`database_operations=[]`)·`db_table='catalog_product'` 보존·version `AddField(default=0)` | ✅ |
| Q-6 | 테스트/TDD | impl-test | **§1.1.T (설치 Y)×(핀 Y·dev분리) 완전 준수**·pytest 58 passed·함수형·`mocker`·`factory_boy` 실사용·`@pytest.mark.django_db` | ✅ |
| Q-7 | 경미 | §4·4.1·5·6.2 | 공개표면 어노테이션(check-public-surface exit0·`MIN_PRICE`·`TYPE_*` 상수 명명)·**테스트스택 4종 핀(dev 분리)** | ✅ |

## 의미적 변종 / backstop-blind 메타

**의미적 변종 0건 · WEAK 0건** — 백스톱 16종 exit0 = 의미 PASS와 일치(적대 grader 2명 독립 줄인용·둘 다 종합 PASS·품질 상). 세 의심 벡터 전부 반증:
1. SD-7 ACL이 catalog 구체 import → **§2:144 OHS 미노출 시 ACL 직접통합 명시 허가**(거짓양성 기각·ordering 비-ACL 격리 grep 0).
2. ACL-EX2 합성/누수 → ACL이 OperationalError 미포착·**raw 전파→중앙 `_is_retryable_db_error` 분기**(503/500)·`IntegrityError` 명시 핸들러·합성 0(from 없는 인프라예외 raise 0).
3. SD-3 판정 SQL 복제 → repository version CAS만·`stock__gte=`는 DB CHECK(비음수)뿐.

## 에러 경로 라이브 관측 (§4.3.1)

> 통합 테스트(58 passed) + 조정자 직접 probe 실측(`setup_test_environment` 적용·DisallowedHost 위양성 차단).

| 키 | 관측 status | content-type | 화이트리스트 | 판정 |
|---|---|---|---|---|
| EP-1 깨진 본문 | **400**(probe: malformed/garbage JSON) | **application/problem+json** | {400} | ✅ 관측 — **§6.2:516 HttpError 핸들러 준수**(Codex 부분 대비 완전) |
| EP-2 무효 입력 | **422**(q=0·ValidationError→422 problem) | application/problem+json | {422,400} | ✅ 관측 |
| EP-3 transient 소진 | **503**(OperationalError 락 분기·CAS 소진→StockContention) | application/problem+json | {503,409} | ✅ 관측 — **500 아님**(ACL-EX2/maj1 회귀 없음) |
| EP-4 재고 부족 | **409**(InsufficientStock) | application/problem+json | {409} | ✅ 관측(FC-1 교차) |
| (비-EP) non-transient DB error | **500**(`test_error_mapping_api:85-103` disk I/O·malformed·no such table) | application/problem+json | — | ✅ ACL-EX2 깨끗(전파→영구장애 500 분기·테스트 검증·누수 없음) |

## 조정자 노트

- **이번 라이브 목적 = §1.1.T 깨끗 baseline에서 Claude Tier-1 설치+핀 관측 + carve-out/이주배타성/FC-2/에러경로 재검증. 전부 입증·우수**:
  1. **Tier-1 설치+핀 완전 이행**(§1.1.T (설치 Y)×(핀 Y)) — `requirements-dev.txt`로 **production/dev 의존성 분리** 핀(Codex 단일파일 대비 더 정교)·`pyproject.toml` 설정. Q-6·Q-7 PASS.
  2. **FC-2 PASS**(경계·부호 mutation red·**단위 경계케이스 `test_deduct_stock_allows_exact_depletion_to_zero` 보유** — Codex는 통합만). ptcat 치명 FAIL 해소·견고.
  3. **catalog 완전이주**(SH-1/4 PASS·`git mv`(R)로 이주·**husk 없음**·INSTALLED_APPS 탈등록·db_table 보존) — **Codex의 빈 dir 잔존 결함 없음**(이주배타성 §10.4 더 깨끗 이행).
  4. **에러 경로 완전**(ninja.responses.Response·HttpError·IntegrityError·OperationalError 분기·ACL-EX2 전파) — **ptboot-codex가 흠이었던 NJ-1/HttpError/NJ-5/ACL-EX2를 전부 준수**.
- **종합 PASS·품질 상**(치명0·WEAK0). 적대 grader 2명 독립 = 둘 다 품질 상·흠 0.
- **N=2 대조(ptboot-codex vs claude)**: 둘 다 종합 PASS·§1.1.T Tier-1 설치+핀·FC-2 PASS. **차이**: Claude가 에러경로(HttpError·NJ-1·NJ-5·ACL-EX2)·테스트 풍부(58 vs 17)·도구 관용구(mocker/factory_boy vs 수제 Fake)·git mv husk 없음에서 우위. 단 **N=1·런간 비결정**(DR-34/35 반전 패턴 — 과거 Claude가 흠·Codex 우수였던 런도 있음) → **우열결론 아님**. 판정소유 분해도 런마다 다름(Codex order·Claude catalog·둘 다 정당).
- `N_grader`=2(적대)+조정자 결정레인. 백스톱·pytest·FC-2 mutation·EP·§1.1.T 전부 조정자 직접 실측(자기보고 불신).

## 부록 — 후속 후보 (채점 골격 밖)

- **§1.1.T 신설 검증 완료**: ptcat 오염이 가렸던 "Codex/Claude가 Tier-1 설치+핀하는가"가 깨끗 baseline에서 **양 런타임 완전 이행** 확인. carve-out 처방 미검증 부분 입증.
- **EP-1 HttpError = 런타임 차**: Claude 준수(problem+json)·Codex 누락(application/json). architect 단계 차이(Codex design-spec "outside contract"). NJ-7 의미 레인/architect 집행 강화 후보(단 N=1).
- Claude 흠 0 — 이번 런 한정(런간 비결정 유의).
