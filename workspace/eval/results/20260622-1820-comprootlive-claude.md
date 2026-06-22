# 채점 결과지 — comprootlive-claude (DR-59 V3 라이브 검증)

> **방법**: EVAL-METHOD v3 · **채점일** 2026-06-22 · **픽스처** `/Users/hyun/Desktop/dddjango-run/claude-comproot/`(신선 무오염 brownfield baseline — Django 4.2.30·평면 `catalog.Product`·빈 DB, 기존 규약 없음=신규 앱뿐) · **런타임** dddjango(Claude Code) **plugin 1.15.0**(백스톱 16종·⑯ check-composition-root V3 포함) · **태스크** "재고 부족 409·충분 시 차감·주문 생성 API"(FC-GOLDEN verbatim) · **게이트** BC=architect 위임 / 내부전용 / ninja-extra 클래스 컨트롤러 / 멱등성·동시성 미적용 / G1·G2 승인 / thinking OFF.
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ➖ N/A.
> **⚠️ 필수 단서**:
> - **결정 레인 = empirical 전수**(백스톱 16종·FC-1 골든·FC-2 mutation·Q-6 스위트 실측, 조정자 봉인). **의미 레인 = 조정자(준비자) read-only 정독 1인** — `N_grader=1`, **blind 미집행**(§1.0 독립 grader 패널 아님; 안전판정 모델 가용성 장애로 grader 서브에이전트 디스패치 불가). 이 시트는 **DR-59(V3) 라이브 검증 + 배포 가능성 판정용**이며, 형식 eval "완료"(N≥5·태스크 2종) 대용 아님.
> - **fixture 도구 환경**(§1.1.T): 채점 착수 전 `.venv` = Django 4.2.30 + ninja 1.6.2 + ninja-extra 0.31.5 + pytest/pytest-django/pytest-mock/factory_boy(코디 `produced` 핀). 조정자 추가 도구 0. `test_golden_fc.py`(루트)는 **조정자 FC 실행 어댑터**(코디 산출물 아님).
> - **측정 프로세스 주의**: macOS 시스템 python `.pyc`는 `~/Library/Caches/com.apple.python/`에 중앙 캐시 — mutation/재실행 시 청소 또는 `PYTHONDONTWRITEBYTECODE=1` 전 런 적용 필수(본 채점 중 stale 200 바이트코드로 G2/G4 일시 오판→중앙 캐시 청소 후 409 확정).

## 종합 판정 (사전식 집계)
| 단계 | 결과 |
|---|---|
| ① 마스크 C | 신규 앱뿐 → §0 전부 강제 |
| ② 치명 게이트 | **FAIL 0** (SD-1~7·FC-1~3·SH-1·2·3·4·7·NJ-1·2·Q-4 통과) |
| ②.5 실질성 관문 | degenerate 0(도메인 판정 실코드·테스트 비-vacuous 실측) |
| ③ 비치명 의미변종 | 경미 🟡 1(NJ-4: 400·500이 `response=` 밖·핸들러 전담) — 치명 아님 |
| ④ TIER-Q 등급 | **상**(WEAK ≤2·FAIL 0) |

**2차원 라벨**: **(정적: 준수) × (라이브: 발화·관측)**. N_grader=1·blind 미집행이라 "준수"는 *조정자 검증 등급*. 형식 "완료"는 N=1·단일 태스크형이라 **미선언**.

## 결정 레인 (empirical · 조정자 봉인)
| 검사 | 결과 |
|---|---|
| 백스톱 16종 | **16/16 exit=0** (check-composition-root V3 포함) |
| FC-1 골든 G1~G6 | **6/6 통과** |
| FC-2 mutation | **3/3 red** — M1 차감부호 7 failed · M2 경계`>`→`>=` 3 failed · M3 status 409→200 3 failed |
| Q-6 코더 테스트 | **46/46 green** (codex 19보다 두터운 커버리지) |

## A. TIER-S 척추 — S-DDD
| ID | 항목 | Result(조정자 검증·줄 인용) | 종합 | 치명 |
|---|---|---|---|---|
| SD-1 판정소유 | `domain_layer/product/product.py:31-44` `Product.decrease_stock`: `quantity<1`→ValueError·`quantity>stock`→`InsufficientStock`·`stock-=quantity`(애그리거트 단일 소유) | ✅ | ✅ |
| SD-2 프로덕션 호출 | `published_service/write.py:24` `build_decrease_stock_command().execute(...)`→`DecreaseStockCommand`→도메인 호출 | ✅ | ✅ |
| SD-3 무복제 | ACL/도메인 판정 소유·infra SQL 판정 복제 0(`product_stock_adapter.py:4-7` docstring 명시·실코드 부합) | ✅ | ✅ |
| SD-4 애그리거트 경계 | order/catalog 분리·`OrderModel.product_id` PositiveInt db_index(타 BC FK 없음, `order_model.py` docstring) | ✅ | ✅ |
| SD-5 모델 표현력 | `Product.reconstitute` load 경로 불변식 비재검증(변경 메서드만)·`PlaceOrderRequest` dataclass | ✅ | ✅ |
| SD-6 계층순수(P1a) | operation 성공 schema만(`order_controller.py:56-64`)·예외 중앙 핸들러(`config/api.py`)·"application·domain은 HTTP 모름"(docstring·실코드) | ✅ | ✅ |
| SD-7 컨텍스트 통신 | `infra_layer/acl/product_stock_adapter.py:37` → catalog `published_service.write`(OHS)·catalog 예외→order 경계 예외 `raise … from`(원인 보존) | ✅ | ✅ |

## B. TIER-S 척추 — S-HR
| ID | Result | 종합 | 치명 |
|---|---|---|---|
| SH-1 컨테이너 | `application/order/`·`application/catalog/` | ✅ | ✅ |
| SH-2 4계층 | 양 BC 4계층(check-layer-skeleton exit=0) | ✅ | ✅ |
| SH-3 종류폴더+명명 | 종류 폴더 골격·feature `place_order/`·`decrease_stock/`·`…Command`/`…Request` 명명 | ✅ | ✅ |
| SH-4 Django앱 위치 | `infra_layer/django_<app>/models/`·루트 평면 0 | ✅ | ✅ |
| SH-7 협력포트 위치 | `domain_layer/order/port/product_stock_port.py`(외래 port 0) | ✅ | ✅ |
| SH-5/6/8/9/10 | 명명·ACL 분리·단일 레이아웃·테스트 의미군 — 백스톱·구조 정합 | ✅ | — |

## TIER-S(조건부) — S-NINJA (HTTP operation 有)
| ID | Result | 종합 | 치명 |
|---|---|---|---|
| NJ-1 스택 | `config/api.py:39` `NinjaExtraAPI`·`order_api_router.py:15` `register_controllers(OrderController)` | ✅ | ✅ |
| NJ-2 operation 얇음 | `order_controller.py:47-64` 팩토리→execute→`Status(201,…)`+Location 헤더(비즈로직·ORM·수동파싱 0) | ✅ | ✅ |
| NJ-3 schema 분리 | `OrderIn`/`OrderOut`/`ErrorOut`·`ValidationErrorOut` | ✅ | — |
| NJ-4 status 선언 | `order_controller.py:33-39` `response={201·404·409·422·503}` — 비즈 오류 선언 ✅; 단 400·500은 `response=` 밖(핸들러 전담) | 🟡 | — |
| NJ-5 문서화 | `summary="Place an order"`+`description`+`tags=["orders"]` | ✅ | — |
| NJ-7 catch-all | `config/api.py:113` `@api.exception_handler(Exception)`→500(traceback 본문 차단·되던지기 0) | ✅ | — |

> **🟡 NJ-4 경미**: 비즈 오류(404·409·422·503)는 `response={}`에 선언(NJ-4 충족) — 400(깨진 본문)·500(catch-all)만 핸들러 전담(프레임워크 status·operation 결과 아님). 치명 아님·codex는 400·500까지 선언(차이는 경미).

## FC — 기능 정확성 (치명)
| ID | Result | 종합 | 치명 |
|---|---|---|---|
| FC-1 골든 오라클 | **6/6 통과**(결정 레인 실측) | ✅ | ✅ |
| FC-2 비-vacuous | **mutation 3/3 red**(결정 레인 실측) | ✅ | ✅ |
| FC-3 도메인 정합 | 차감 방향·경계(stock=qty→0)·인과 정상, 음수재고 CHECK 백스톱 | ✅ | ✅ |

## C. 기존규약 마스크
신규 앱뿐(baseline=평면 catalog 시드 → `application/{order,catalog}/`로 전개·루트 잔재 0). order=판정 적재(use-case)·catalog=stock 판정 소유 + 자체 use-case(`DecreaseStockCommand`). §0 전부 강제·위반 0.

## D. TIER-Q 품질
Q-1 스코프(요청 범위 내·과설계 0·docstring에 "멱등성 미보장" 명시) ✅ / Q-2 problem+json 일관 ✅ / Q-3 동시성 미적용(CRIB) ➖ / **Q-4 메커니즘 ✅[🔴치명 통과]**(check-mechanism-ownership exit=0) / Q-5 마이그레이션(신규 앱 0001·`db_table` 보존) ✅ / Q-6 테스트 **46/46 green** ✅ / Q-7 경미(어노테이션·핀) ✅. **등급 상**.

## 의미적 변종 / backstop-blind 메타
- `[결정 PASS ∧ 의미 FAIL]` 칸 **빔** — 치명 차원 의미변종 0.
- backstop-blind: NJ-4의 400·500 `response=` 밖은 결정 레인(check-openapi-error-declaration이 선언분만 봄)이 통과시키나 조정자 정독으로 경미 포착(🟡).

## §6 관측 — 컴포지션 루트 V3 (이 라운드 초점 · 완료 비산입)
**라벨: 컴포지션 루트 = 정상(정본 생성·발화 정확)**
1. **정본 생성(양 BC)**: `application/order/composition_root.py` **AND** `application/catalog/composition_root.py` — 둘 다 매요청 팩토리(`build_place_order_command()`·`build_decrease_stock_command()`). order docstring에 **"presentation/OHS는 매요청 팩토리만 호출·직접 new-up 금지(Q-7)"** 명시. ✅
2. **off-tree 재발 0**: `composition/`·`di/`·`wiring/` 등 부재. ✅
3. **V3 발화 정확(양방향의 발화 쪽)**: catalog가 application_layer use-case(`DecreaseStockCommand`) 보유 → **V3가 catalog에도 composition_root를 요구**, 코디가 생성 → check-composition-root exit=0. (codex는 catalog가 use-case 없어 *면제*; Claude는 use-case 있어 *발화* — **조건부 게이트가 양 런타임에서 정반대로 정확히 작동**.)
4. 매요청 팩토리·싱글톤 부재 reviewer 의미 점검 통과(docstring·실코드 부합).

## 조정자 노트
- **V3 조건부 게이트의 결정적 양방향 검증**: 동일 태스크를 두 런타임이 다르게 분해(codex catalog=데이터소스적·use-case 없음 / Claude catalog=use-case `DecreaseStockCommand` 보유) → V3가 한쪽은 **면제**, 한쪽은 **발화·충족**. 무조건 게이트였다면 codex catalog를 거짓 차단했을 것 — 2라운드 적대검증으로 수렴한 조건부 설계가 실세계에서 입증.
- 의미 레인 N_grader=1·blind 미집행은 본 라이브 검증의 한계. 결정 레인(empirical)은 봉인·재현 가능.
- **배포 판정**: 결정 레인 전부 green + 치명 0 FAIL + §6 정본·발화 정확 → **GO**(codex 시트와 교차).
