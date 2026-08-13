# FC-1 골든 행위표 — billing checkout (라운드 2 사전등록 · 2026-08-13 09:30)

> **작성자 격리 선언(작성 에이전트 축자)**: "코드 미열람 — 읽은 파일: `spec.md`, `api_shape_pre_success.json` 뿐." (`docs/rebuild/billing/` 의 두 정본만 정독 · `application/`·`.dddjango/`·git 이력 일절 미접촉.)
> **지위**: EVAL-METHOD §1.4 의 사전등록 행위표. 이번 라운드(결과지 `20260813-1005-blrebuildlive-claude.md`)에서는 실행 어댑터·실측을 수행하지 않아 FC-1 은 ⏸️ 로 보고했다 — 이 표는 후속 실측·재개 라운드에서 오라클로 쓴다. 작성자⊥채점자 분리: 이 표의 작성 에이전트는 의미 레인 grader 와 별개 세션이다.
> 공통 전제: 오류 body = RFC 9457 problem+json(`type`=`https://broccoli.app/problems/<slug>`·title/status/detail 필수·retryable 미표기=미방출 — spec §3.3 축자). «키 미소비» = 원장 행 없음 ↔ 같은 키 즉시 재사용 가능. 성공 201 body = `{payment(9키 닫힘: id·status·product_id·product_name·amount_krw·daily_token_limit·weekly_token_limit·payment_method·succeeded_at), entitlement_id}` · `Idempotency-Replayed` 값은 문자열 `"false"|"true"`. 기본 사전 상태: 인증 가족 소유자 부모 P·가족 F(유효 entitlement 없음·처리중 없음)·판매 중 0원 상품 A·미사용 키 K.

| # | 사전 상태 | 요청 | 기대 status·헤더 | 기대 body 핵심 | 기대 부작용 (원장/entitlement/멱등키) | §근거 |
|---|---|---|---|---|---|---|
| A1 | 기본 | `Idempotency-Key: K`, `{product_id: A}` | 201 + `Idempotency-Replayed: "false"` | payment 9키: `status="succeeded"`·`payment_method=null`·`amount_krw=0`·스냅샷 이름/한도·tz 있는 `succeeded_at` + `entitlement_id` | 원장 1행 succeeded(스냅샷 보존·발급 기록 완료) / 발급 관찰 / K 점유 | §2·§3.2·§3.4 |
| B1 | A1 종결 후 | 같은 P·같은 K·같은 product_id | 201 + Replayed `"true"` | A1 저장 스냅샷 그대로(같은 payment.id·entitlement_id) | 새 행 없음 / 불변 / **협력 표면 호출 0** | §2 종결 재생 |
| B2 | A1 후 상품 삭제·개명·인상 | 같은 K·같은 product_id | 201 + Replayed `"true"` | 최초 결과 재생(옛 이름·0원 — 재조합 금지) | 새 행 없음 / 불변 / 호출 0 | §2 |
| B3 | K 종결 점유 | 같은 K + **다른** product_id | 422 | `idempotency-key-conflict` | 기존 결제 그대로 / 불변 / K 점유 유지 | §2·§3.3 |
| B4 | F2 로 K′ failed 종결 | 같은 K′·같은 product_id | 409 + Replayed `"true"` | `family-already-entitled`·`retryable:false` — 저장 사유 재생(현재 상태 무관) | 새 행 없음 / 불변 / K′ 점유 유지(failed 키 재사용 불가) | §2·§3.3 |
| B5 | 기본 | 키 헤더 누락 | 422 | `idempotency-key-required`(validation-error 아님 — 단일 수렴) | 없음 / 없음 / 미소비 | §2·§3.2 |
| B6 | 기본 | 키 형식 위반(129자·빈 값·0x21~7E 밖) | 422 | B5 와 동일 수렴 | 동상 | §2·§3.3 |
| B7 | P 가 K 로 성공 종결·다른 소유자 부모 Q | Q 가 같은 문자열 K | 201 + Replayed `"false"` | Q 가족 기준 신규 성공 | Q 가족 행/발급/Q-scope K 점유 — P 와 무충돌 | §2 키 scope=부모당 |
| C1/C2 | 인증 없음·무효/자녀 토큰 | — | 401 + `WWW-Authenticate: Bearer` | framework 소유(body 모양 spec 미정의 — 공백 ⑤) | 없음 / 없음 / 미소비 | §3.1·§5 |
| D1 | 가족 없는 부모 | 정상 요청 | 409 | `family-required` | 없음 / 없음 / 미소비 | §2·§3.3 |
| D2 | 소유자 아닌 구성원 | 정상 요청 | 403 | `family-owner-required`(billing 고유 detail) | 동상 | §2·§3.3 |
| E1 | 부재 상품 | 부재 양의 정수 | 404 | `product-not-found` | 동상 | §2·§3.3 |
| E2 | 비활성·기간 밖 상품 | 그 상품 | 409 | `product-not-purchasable` | 동상 | §2·§3.3 |
| E3 | 판매 중 유료 상품 | 그 상품 | 422 | `paid-checkout-not-supported`·`retryable:false` | 동상 | §1·§2·§3.3 |
| F1 | 가족 이미 유효 entitlement(선행 검증 발견) | 새 키 정상 요청 | 409 · **Replayed 헤더 없음** | `family-already-entitled`·`retryable:false` | 없음 / 이중 발급 없음 / 미소비 | §2·§3.3 |
| F2 | 확정 직전 재확인에서 race 발견 | 키 K′ | 409 · 헤더 없음 | F1 동일 | **원장 1행 failed(사유: 가족 이미 보유) 기록·보존** / 없음 / **K′ 점유**(→B4 전제) | §2 |
| G1 | 같은 가족 처리중 1건(K1) 존재 | 다른 키 K2 | 409 | `family-checkout-in-progress`·`retryable:true`(`Retry-After` 없음 — §3.3 표 미표기) | 새 행 없음 / 없음 / K2 미소비(도출 — 공백 ⑦) | §2 직렬화 |
| G2 | 같은 가족 동시 두 요청(다른 키) | 병행 | 한쪽 201·진 쪽 409 G1 — **DB 오류 노출 없이** | 각각 A1/G1 | 처리중 점유 최대 1(DB 유니크 수준) | §2 |
| H1 | 성공 종결+유효 임차(TTL 내·발급 기록 전) | 같은 키 | 409 + `Retry-After: 1` | `idempotency-key-in-progress`·`retryable:true` | succeeded 유지 / 미기록 / 점유 유지 | §2·§3.3 |
| H2 | 임차 만료 후(상품 삭제돼도 무관) | 같은 키 | 201 + Replayed `"false"`(도출 — 공백 ⑥) | A1 동일 스냅샷(재개 입력=원장 스냅샷만·상품 재조회 없음) | 발급 재개·완주(결제 ID 멱등 수렴) / 점유 유지 | §2 |
| H3 | 지금==만료 시각 정확히 | 같은 키 | H2 재개 경로(409 아님 — 경계=만료) | H2 동일 | H2 동일 | §2 |
| I1 | 발급 일시 실패(sqlstate 40001·40P01·55P03) | 정상 요청 | 503 + `Retry-After: 1` | `entitlement-unavailable`·`retryable:true`(framework DB 503 과 다른 갈래) | succeeded 유지·미기록 / 없음 / 점유 유지 + **임차 즉시 해제** | §2·§5·§3.3 |
| I2 | 발급 영구 실패(무효 요청·멱등 충돌 등) | 정상 요청 | 500 | framework 기본(BC problem 아님·catch-all 금지) | succeeded **유지**·미기록 / 없음 / 점유 유지 + 경보 로그(4식별자) · 임차 상태 미정(공백 ③) | §2·§3.3·§5 |
| J1 | 기본 | product_id 누락·0·음수·비정수 | 422 | framework `validation-error`+`invalid-params`(BC 아님) | 없음 / 없음 / 미소비 | §3.3(a)·shape |
| J2 | 기본 | product_id = 2^63 | **미정 — spec 공백**(공백 ①) | 미정 | 미정 | §2 값 경계=«저장 전 검증»·shape 에 maximum 없음 |
| J3/J4 | products 가 손상 상품 반환(이름 0/101자·음수 가격) | 그 상품 | 500 | framework(값 도메인 위반 — 미등재 500) | 원장 미저장 / 없음 / 미소비 | §2·§3.3 |
| M1 | 기본 | GET /v1/payments·POST /v1/payments/123 | 405·404 | framework | 없음 | §3.1 |
| M2 | 기본 | 본문 JSON 파싱 불가 | 400 | framework(slug 미기재) | 없음 / 없음 / 미소비 | §3.3 |

## spec 공백/모호 9건 (작성자 판정 — G0 스팩 인터뷰 재료·큐 ⑴)

1. **64-bit 초과 product_id(J2)** — §2 값 경계는 «저장 전 검증»(위반=500 계열)이지 입력 검증이 아니고 shape 에 `maximum` 없음 → 404/422/500 확정 불가. ※레인 B STOP 2 와 동일 지점(독립 재발견).
2. 처리-중 키 + 다른 product_id 의 우선순위(in-progress 409 vs conflict 422) 미명시.
3. 발급 영구 실패(I2) 후 임차 상태·같은 키 재요청 기대(재차 500 루프?) 미명시.
4. 상품명 스냅샷의 trim 저장 여부(원본 vs trim 값).
5. 401 body 의 problem 모양(slug·본문) 미기재 — status+`WWW-Authenticate` 만 확정. M2 의 400 slug 도 동일.
6. H2 재개 성공의 `Idempotency-Replayed` 값 — §3.2 문면 도출로 `"false"`, 명시 문장 없음.
7. 직렬화 409(G1)의 키 소비 — 미소비 열거에 직렬화 부재(동치 문장 도출로만 확정).
8. F2 실패 행의 저장 실패-사유 코드 정확 문자열 미명시.
9. 실패-종결 재생(B4)의 협력 호출 0 여부 — 성공 재생에만 명문.

※ 레인 B STOP 1(post-success grant family-already-entitled)은 이 표에도 대응 행이 없다 — 작성자도 그 갈래를 행위표로 확정하지 못한 것(공백 ③이 인접 지점). 공백 목록과 함께 G0 인터뷰 가다듬기(큐 ⑴)의 실증 재료다.
