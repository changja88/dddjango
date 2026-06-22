# 채점 결과지 — comprootlive-codex (DR-59 V3 라이브 검증)

> **방법**: EVAL-METHOD v3 · **채점일** 2026-06-22 · **픽스처** `/Users/hyun/Desktop/dddjango-run/codex-comproot/`(신선 무오염 brownfield baseline — Django 4.2.30·평면 `catalog.Product`·빈 DB, 기존 규약 없음=신규 앱뿐) · **런타임** codex-dddjango **plugin 1.12.0**(백스톱 16종·⑯ check-composition-root V3 포함) · **태스크** "재고 부족 409·충분 시 차감·주문 생성 API"(FC-GOLDEN verbatim) · **게이트** BC=architect 위임 / 내부전용 / ninja-extra 클래스 컨트롤러 / 멱등성·동시성 미적용 / G1·G2 승인 / thinking OFF.
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ➖ N/A.
> **⚠️ 필수 단서**:
> - **결정 레인 = empirical 전수**(백스톱 16종·FC-1 골든·FC-2 mutation·Q-6 스위트 실측, 조정자 봉인). **의미 레인 = 조정자(준비자) read-only 정독 1인** — `N_grader=1`, **blind 미집행**(§1.0 독립 grader 패널 아님; 안전판정 모델 가용성 장애로 grader 서브에이전트 디스패치 불가). 따라서 의미 차원은 *조정자 직접 검증·줄 인용*이되 N≥3 합의·적대 grader는 부재. **이 시트는 DR-59(V3) 라이브 검증 + 배포 가능성 판정용**이며, 형식 eval "완료"(N≥5·태스크 2종) 대용 아님.
> - **fixture 도구 환경**(§1.1.T): 채점 착수 전 `.venv` = Django 4.2.30 + ninja 1.6.2 + ninja-extra 0.31.5 + pytest/pytest-django/pytest-mock/factory_boy(코디 `produced`·`requirements.txt` 핀). 조정자 추가 도구 0(라이브 baseline venv 그대로 사용). `test_golden_fc.py`(루트)는 **조정자 FC 실행 어댑터**(코디 산출물 아님).
> - **측정 프로세스 주의**: macOS 시스템 python `.pyc`는 `~/Library/Caches/com.apple.python/`에 중앙 캐시됨 — mutation/재실행 시 그 캐시를 청소하거나 `PYTHONDONTWRITEBYTECODE=1`을 전 런에 적용해야 stale 바이트코드 오판이 없다(본 채점 중 G2/G4가 일시 200으로 보였으나 중앙 캐시 청소 후 409 확정).

## 종합 판정 (사전식 집계)
| 단계 | 결과 |
|---|---|
| ① 마스크 C | 신규 앱뿐(baseline=평면 catalog 시드, 런이 application/로 전개) → §0 전부 강제 |
| ② 치명 게이트 | **FAIL 0** (SD-1~7·FC-1~3·SH-1·2·3·4·7·NJ-1·2·Q-4 전부 통과) |
| ②.5 실질성 관문 | degenerate 0(도메인 판정 실코드·테스트 비-vacuous 실측) |
| ③ 비치명 의미변종 | 경미 🟡 2(NJ-1 에러 `JsonResponse`·NJ-5 summary 부재) — 치명 아님 |
| ④ TIER-Q 등급 | **상~중**(WEAK ≤2·FAIL 0) |

**2차원 라벨**: **(정적: 준수) × (라이브: 발화·관측)**. 단 N_grader=1·blind 미집행이라 "준수"는 *조정자 검증 등급*(독립 패널 미반영). 형식 "완료"는 N=1·단일 태스크형이라 **미선언**(정직).

## 결정 레인 (empirical · 조정자 봉인)
| 검사 | 결과 |
|---|---|
| 백스톱 16종 | **16/16 exit=0** (check-composition-root V3 포함) |
| FC-1 골든 G1~G6 | **6/6 통과** (재고10·주문3→201∧잔7 / 재고2·주문5→409∧불변 / 재고5·주문5→201∧잔0 / 재고5·주문6→409 / 없는상품→404 / 수량0→422) |
| FC-2 mutation | **3/3 red** — M1 차감부호역전 4 failed · M2 경계`<`→`<=` 1 failed · M3 status 409→200 1 failed (코더 스위트 비-vacuous) |
| Q-6 코더 테스트 | **19/19 green** (pytest 관용구·`@pytest.mark.django_db`) |

## A. TIER-S 척추 — S-DDD
| ID | 항목 | Result(조정자 검증·줄 인용) | 종합 | 치명 |
|---|---|---|---|---|
| SD-1 판정소유 | `domain_layer/product/product.py:13-19` `Product.consume_stock`: `quantity<1`→ValueError·`stock<quantity`→`InsufficientCatalogStock`·`stock-=quantity` | ✅ | ✅ |
| SD-2 프로덕션 호출 | `published_service/stock.py:33` `product.consume_stock(quantity)` 호출(조회→도메인→CAS persist) | ✅ | ✅ |
| SD-3 무복제 | `published_service/stock.py:37-40` CAS `.filter(id=,version=).update(...)` — `stock__gte=` 등 비즈조건 SQL 복제 **0** | ✅ | ✅ |
| SD-4 애그리거트 경계 | order/catalog 분리·`OrderModel.product_id` PositiveInt(타 BC FK 없음) | ✅ | ✅ |
| SD-5 모델 표현력 | `PlaceOrderRequest` frozen dataclass·도메인 bare 네이밍 | ✅ | ✅ |
| SD-6 계층순수(P1a) | operation 성공 schema만 반환(`order_controller.py:38-41`)·예외 중앙 핸들러(`config/api.py`)·domain HTTP import 0 | ✅ | ✅ |
| SD-7 컨텍스트 통신 | `infra_layer/acl/product_stock_adapter.py` → catalog `published_service`(OHS) 소비·catalog 예외→order 경계 예외 번역 | ✅ | ✅ |

## B. TIER-S 척추 — S-HR
| ID | Result | 종합 | 치명 |
|---|---|---|---|
| SH-1 컨테이너 | 신규 앱 `application/order/`·`application/catalog/` | ✅ | ✅ |
| SH-2 4계층 | 양 BC 4계층 물리 분리(백스톱 check-layer-skeleton exit=0) | ✅ | ✅ |
| SH-3 종류폴더+명명 | 종류 폴더 골격·`…Command`/`…Request` 명명(`place_order_command.py`·`place_order_request.py`) | ✅ | ✅ |
| SH-4 Django앱 위치 | `infra_layer/django_<app>/models/`·`migrations/`·루트 평면 0 | ✅ | ✅ |
| SH-7 협력포트 위치 | `domain_layer/order/port/product_stock_port.py`(백스톱 외래 port 0) | ✅ | ✅ |
| SH-5/6/8/9/10 | 명명·ACL 분리·단일 레이아웃·테스트 의미군(unit/integration) — 백스톱·구조 정합 | ✅ | — |

## TIER-S(조건부) — S-NINJA (HTTP operation 有)
| ID | Result | 종합 | 치명 |
|---|---|---|---|
| NJ-1 스택 | `config/api.py:15` `NinjaExtraAPI`·`order_api_router.py:7` `register_controllers(OrderController)` | 🟡 | ✅ |
| NJ-2 operation 얇음 | `order_controller.py:31-41` 팩토리→execute→`Status(201,…)` 매핑만(비즈로직·ORM·수동파싱 0) | ✅ | ✅ |
| NJ-3 schema 분리 | `OrderIn`/`OrderOut`/`ProblemOut`·`ValidationProblemOut` | ✅ | — |
| NJ-4 status 선언 | `order_controller.py:21-29` `response={201·400·404·409·422·500·503}` 전부 선언 | ✅ | — |
| NJ-5 문서화 | `tags=["orders"]` 有·**summary 없음** | 🟡 | — |
| NJ-7 catch-all | `config/api.py:120` `@api.exception_handler(Exception)`→500(되던지기 0) | ✅ | — |

> **🟡 NJ-1 경미**: 중앙 핸들러가 `django.http.JsonResponse`로 반환(`config/api.py:37`) — `ninja.responses.Response`(§6.2 처방) 아님. 가시성·problem+json은 충족이라 *경미*(Q-a), SD-6/치명 아님.

## FC — 기능 정확성 (치명)
| ID | Result | 종합 | 치명 |
|---|---|---|---|
| FC-1 골든 오라클 | **6/6 통과**(결정 레인 실측) | ✅ | ✅ |
| FC-2 비-vacuous | **mutation 3/3 red**(결정 레인 실측) | ✅ | ✅ |
| FC-3 도메인 정합 | 차감 방향·경계(stock=qty→0)·인과 정상, 음수재고 CHECK 백스톱 | ✅ | ✅ |

## C. 기존규약 마스크
신규 앱뿐(baseline=평면 catalog 시드 → 런이 `application/{order,catalog}/`로 전개·루트 잔재 0). MQ: order=판정 적재(use-case)·catalog=stock 판정 소유. §0 전부 강제 대상이며 위반 0.

## D. TIER-Q 품질
Q-1 스코프(멱등성·협상 발명 0·요청 범위 내) ✅ / Q-2 problem+json RFC9457 일관 ✅ / Q-3 동시성 미적용(CRIB) ➖ / **Q-4 메커니즘 ✅[🔴치명 통과]**(커스텀 백엔드·PRAGMA·몽키패치 0·check-mechanism-ownership exit=0) / Q-5 마이그레이션(신규 앱 0001·`db_table` 보존) ✅ / Q-6 테스트 **19/19 green** ✅ / Q-7 경미(어노테이션·핀) ✅. **등급 상~중**.

## 의미적 변종 / backstop-blind 메타
- `[결정 PASS ∧ 의미 FAIL]` 칸 **빔** — 치명 차원 의미변종 0.
- backstop-blind: NJ-1 `JsonResponse` vs `ninja.responses.Response`는 결정 레인이 안 보는 의미 경미(조정자 정독으로 포착·🟡).

## §6 관측 — 컴포지션 루트 V3 (이 라운드 초점 · 완료 비산입)
**라벨: 컴포지션 루트 = 정상(정본 생성·면제 정확)**
1. **정본 생성**: `application/order/composition_root.py` + 매요청 `build_place_order_command()` 팩토리(`order_controller.py:32`가 매요청 호출·모듈/lru_cache 싱글톤 아님). ✅
2. **off-tree 재발 0**: `composition/`·`di/`·`wiring/` 등 폴더 부재(직전 codex 1.10.0 런의 `order/composition/place_order_provider.py` off-tree 버그 **정정**). ✅
3. **데이터소스 BC 면제 정확**: catalog는 application_layer use-case 없음(로직=domain+published_service) → **composition_root 없이 V3 exit=0**(거짓양성 0). ✅
4. V3 백스톱 **자연 발화 검증**: check-composition-root exit=0(order 정본 충족·catalog 면제). 거짓양성 0 실측.

## 조정자 노트
- 직전 `dddjango-run/codex/`(1.10.0)의 off-tree `composition/` 버그가 이번 1.12.0 런에서 **정본 composition_root로 정정** — DR-59 V3 보강의 1차 목적 달성.
- 의미 레인 N_grader=1·blind 미집행은 본 라이브 검증의 한계(독립 패널 부재). 결정 레인(empirical)은 봉인·재현 가능.
- **배포 판정**: 결정 레인 전부 green + 치명 차원 0 FAIL + §6 정본 → **GO**(claude 시트와 교차).
