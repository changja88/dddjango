# FC-1 골든 행위표 v2 — billing checkout (spec 2026-08-13 개정 2건 반영 · 2026-08-15 갱신)

> **작성자 격리 선언(작성 에이전트 축자)**: "코드 미열람 — 읽은 파일: `docs/rebuild/billing/spec.md`(2026-08-13 개정 2건 반영본), `docs/rebuild/billing/api_shape_pre_success.json`(`/v1/payments` 부분만), `workspace/eval/golden/20260813-billing-fc1-golden.md`(골든 v1) — 정확히 이 3개뿐." (`application/`·`framework/`·`broccoli_server/`·`.dddjango/`·git 이력(show/log/diff)·Grep/Glob 탐색 일절 미접촉 — 이 격리가 오라클 자격의 근거다.)
> **지위**: v1(2026-08-13 09:30 사전등록 — spec 개정 2건 «이전» 작성)은 사전등록 증거로 무접촉 보존하고, 이 v2 가 spec 개정 2건 반영 후의 실측·재개 라운드 오라클이다. 작성자⊥채점자 분리는 v1 과 동일하게 유지.
> **v1 대비 변경 요약**: ⑴ 신설 1행 — **I3**(발급 grant 시점 `family_already_entitled` = 영구 실패 500 · 개정 ① — v1 말미 ※가 지적한 부재 행 해소) ⑵ 확정 1행 — **J2**(product_id=2^63: 미정 → 입구 스키마 통과 후 저장·조회 전 가드 500 · 개정 ② — 구 공백 ① 해소) ⑶ 수정 1행 — **I2**(영구 실패 갈래에서 grant-시점 가족 보유를 I3 로 분리 명시·공백 참조 갱신) ⑷ 표기 갱신 3행 — C1/C2·G1·H2(공백 재번호 참조만·판정 무변) ⑸ 그 외 전 행 승계 무변(F1·F2·B4 는 개정 ①의 «409 갈래=checkout 확정 전 관찰에서만»과 정합 확인 — 둘 다 확정 전 관찰이라 무변) ⑹ 공백 9건 재감사 — 해소 1·잔존 8(새 번호 1~8).
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
| C1/C2 | 인증 없음·무효/자녀 토큰 | — | 401 + `WWW-Authenticate: Bearer` | framework 소유(body 모양 spec 미정의 — 잔존 4) | 없음 / 없음 / 미소비 | §3.1·§5 |
| D1 | 가족 없는 부모 | 정상 요청 | 409 | `family-required` | 없음 / 없음 / 미소비 | §2·§3.3 |
| D2 | 소유자 아닌 구성원 | 정상 요청 | 403 | `family-owner-required`(billing 고유 detail) | 동상 | §2·§3.3 |
| E1 | 부재 상품 | 부재 양의 정수 | 404 | `product-not-found` | 동상 | §2·§3.3 |
| E2 | 비활성·기간 밖 상품 | 그 상품 | 409 | `product-not-purchasable` | 동상 | §2·§3.3 |
| E3 | 판매 중 유료 상품 | 그 상품 | 422 | `paid-checkout-not-supported`·`retryable:false` | 동상 | §1·§2·§3.3 |
| F1 | 가족 이미 유효 entitlement(선행 검증 발견 — checkout 확정 **전** 관찰) | 새 키 정상 요청 | 409 · **Replayed 헤더 없음** | `family-already-entitled`·`retryable:false` | 없음 / 이중 발급 없음 / 미소비 | §2·§3.3 |
| F2 | 확정 직전 재확인에서 race 발견(checkout 확정 **전** 관찰) | 키 K′ | 409 · 헤더 없음 | F1 동일 | **원장 1행 failed(사유: 가족 이미 보유) 기록·보존** / 없음 / **K′ 점유**(→B4 전제) | §2 |
| G1 | 같은 가족 처리중 1건(K1) 존재 | 다른 키 K2 | 409 | `family-checkout-in-progress`·`retryable:true`(`Retry-After` 없음 — §3.3 표 미표기) | 새 행 없음 / 없음 / K2 미소비(도출 — 잔존 6) | §2 직렬화 |
| G2 | 같은 가족 동시 두 요청(다른 키) | 병행 | 한쪽 201·진 쪽 409 G1 — **DB 오류 노출 없이** | 각각 A1/G1 | 처리중 점유 최대 1(DB 유니크 수준) | §2 |
| H1 | 성공 종결+유효 임차(TTL 내·발급 기록 전) | 같은 키 | 409 + `Retry-After: 1` | `idempotency-key-in-progress`·`retryable:true` | succeeded 유지 / 미기록 / 점유 유지 | §2·§3.3 |
| H2 | 임차 만료 후(상품 삭제돼도 무관) | 같은 키 | 201 + Replayed `"false"`(도출 — 잔존 5) | A1 동일 스냅샷(재개 입력=원장 스냅샷만·상품 재조회 없음) | 발급 재개·완주(결제 ID 멱등 수렴) / 점유 유지 | §2 |
| H3 | 지금==만료 시각 정확히 | 같은 키 | H2 재개 경로(409 아님 — 경계=만료) | H2 동일 | H2 동일 | §2 |
| I1 | 발급 일시 실패(sqlstate 40001·40P01·55P03) | 정상 요청 | 503 + `Retry-After: 1` | `entitlement-unavailable`·`retryable:true`(framework DB 503 과 다른 갈래) | succeeded 유지·미기록 / 없음 / 점유 유지 + **임차 즉시 해제** | §2·§5·§3.3 |
| I2 | 발급 영구 실패 — 무효 요청·멱등 충돌 등 나머지 계약 위반(grant-시점 가족 보유는 **I3 분리**) | 정상 요청 | 500 | framework 기본 `internal-error`(BC problem 아님·catch-all 금지) | succeeded **유지**·미기록 / 없음 / 점유 유지 + 경보 로그(4식별자) · 임차 상태 미정(잔존 2) | §2·§3.3·§5 |
| **I3 (신설)** | 성공 종결+임차 후 **발급(grant) 호출 시점**에 `family_already_entitled_v1` 관찰(재확인 통과 뒤 딴 경로 권한 — H2 재개 경로 포함) | 정상 요청(키 K) | 500 · **`Retry-After` 없음(재시도 유도 없음)** | framework 기본 `internal-error`(BC problem 아님 — 409 `family-already-entitled` **아님**: 409 갈래는 checkout 확정 전 관찰 전용) | succeeded **유지**(성공 종결 되돌리는 전이 없음) / 발급 **미기록** / K 점유 유지 + 경보 로그(결제·가족·상품·사유 식별 가능) · 임차 상태 미정(잔존 2) | §2 개정 ①·§5·§3.3 미등재 500 |
| J1 | 기본 | product_id 누락·0·음수·비정수 | 422 | framework `validation-error`+`invalid-params`(BC 아님) | 없음 / 없음 / 미소비 | §3.3(a)·shape |
| **J2 (확정)** | 기본 | product_id = 2^63 (64-bit 초과) | **500**(입구 스키마 통과 — shape 의 `product_id` 는 `exclusiveMinimum: 0` 뿐·`maximum` 없음·추가 선언 금지) | framework 기본 `internal-error`(값 도메인 위반 — 미등재 500 갈래 · 422 `validation-error` 로 갈라지면 위반=스키마 선점 금지) | 원장 미저장(저장·조회 **전** 가드) / 없음 / 미소비(도출 — 원장 행 없음 ↔ 재사용 가능) | §2 값 경계 개정 ②·§3.3 미등재 500·shape |
| J3/J4 | products 가 손상 상품 반환(이름 0/101자·음수 가격) | 그 상품 | 500 | framework(값 도메인 위반 — 미등재 500 · 저장·조회 전 가드=개정 ② 동일 계열) | 원장 미저장 / 없음 / 미소비 | §2·§3.3 |
| M1 | 기본 | GET /v1/payments·POST /v1/payments/123 | 405·404 | framework | 없음 | §3.1 |
| M2 | 기본 | 본문 JSON 파싱 불가 | 400 | framework(slug 미기재) | 없음 / 없음 / 미소비 | §3.3 |

## v1 «spec 공백/모호 9건» 재감사 (개정 2건 반영 후)

| v1 번호 | 요지 | 판정 | 새 번호 |
|---|---|---|---|
| ① | 64-bit 초과 product_id(J2) 의 기대 미정 | **해소** — 개정 ②가 정답 부여: 입구 스키마 제약 아님(`maximum` 추가 선언 금지)·저장·조회 전 가드가 500 계열로 표면화 → J2 행 확정 | — |
| ② | 처리-중 키 + 다른 product_id 우선순위(409 vs 422) | 잔존 — 개정 무관 | 1 |
| ③ | 영구 실패 후 임차 상태·같은 키 재요청 기대 | 잔존(부분 좁혀짐) — 개정 ①이 «재시도 유도 없음»(`Retry-After` 미부착)은 확정했으나, 임차 상태와 재요청 시 동작(재차 500 루프? H1/H2 경로 진입?)은 여전히 미명시 · 적용 범위가 I2·I3 둘로 늘었다 | 2 |
| ④ | 상품명 스냅샷 trim 저장 여부(원본 vs trim 값) | 잔존 — «trim 후 1~100자»는 판정 규칙만 확정 | 3 |
| ⑤ | 401 body problem 모양·M2 400 slug 미기재 | 잔존 — 개정 무관 | 4 |
| ⑥ | H2 재개 성공의 `Idempotency-Replayed` 값(문면 도출 `"false"`·명시 문장 없음) | 잔존 — 개정 무관 | 5 |
| ⑦ | 직렬화 409(G1)의 키 소비(동치 문장 도출로만 확정) | 잔존 — 개정 무관 | 6 |
| ⑧ | F2 실패 행의 저장 실패-사유 코드 정확 문자열 | 잔존 — `[a-z0-9_]{1,100}` 규격만 확정 | 7 |
| ⑨ | 실패-종결 재생(B4)의 협력 호출 0 여부(성공 재생에만 명문) | 잔존 — «현재 가족 상태와 무관하게»로 도출만 가능 | 8 |

### 잔존 공백 8건 (v2 번호 — G0 스팩 인터뷰 재료)

1. 처리-중 키(유효 임차) + **다른** product_id 의 우선순위 — in-progress 409 vs conflict 422 미명시.
2. 발급 영구 실패(I2·I3) 후 임차 상태·같은 키 재요청 기대(재차 500 루프? 임차 만료 후 H2 재개 진입?) 미명시 — 개정 ①은 «재시도 유도 없음»만 확정.
3. 상품명 스냅샷의 trim 저장 여부(원본 vs trim 값) — «trim 후 1~100자»는 길이 판정 규칙.
4. 401 body 의 problem 모양(slug·본문) 미기재 — status+`WWW-Authenticate` 만 확정. M2 의 400 slug 도 동일.
5. H2 재개 성공의 `Idempotency-Replayed` 값 — §3.2 문면 도출로 `"false"`, 명시 문장 없음.
6. 직렬화 409(G1)의 키 소비 — 미소비 열거에 직렬화 부재(동치 문장 도출로만 확정).
7. F2 실패 행의 저장 실패-사유 코드 정확 문자열 미명시.
8. 실패-종결 재생(B4)의 협력 호출 0 여부 — 성공 재생에만 명문(«현재 가족 상태와 무관» 문면 도출).

※ v1 말미 ※(레인 B STOP 1 — post-success grant family-already-entitled 의 대응 행 부재)는 개정 ①과 I3 신설로 **해소**됐다. 레인 B STOP 2 와 동일 지점이던 구 공백 ①(J2)도 개정 ②로 해소 — v1 이 독립 재발견으로 표시한 두 STOP 지점이 전부 spec 개정으로 닫혔다.
