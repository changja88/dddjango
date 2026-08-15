# billing spec preflight 검수(⑻⑼⑽) + 개정안 — S4-r1 기동 준비 2단계 (2026-08-15)

재료: `docs/rebuild/billing/`(양 레인 diff 0 — 08-13 라운드 2′ 산출). 검수 기준 =
r2″ 확정 판형(products anchor-preflight 9표면) + 설치본 v2.11.0. 실측 트리 = 레인 A
`6969ef85` · 레인 B `13c79a6`.

## 검수 결과 요약 — 충돌 3 + stale 빚 1

| 축 | 항목 | 판정 |
|---|---|---|
| ⑻-S1 | §3 분리 선언문(«소유는 표준 프로필 dddjango-code-json») | ✅ 실재(:124) — 이중 문면 없음 |
| ⑻-S2 | DB·migrations 상수 절 | ❌ **부재** — S3-r1 레인 B STOP 축 그대로 → **A1** |
| ⑼ | §3 controller=`driving_layer/api/` · §3.3 ErrorSchema=`driving_layer/api/bc_error_schema.py`(products 실증) · §3.5 admin=`driven_layer/django_<bc>/admin/`(#462·v2.8.0+) · §6 배선=프로젝트 소유 · OHS 발행 0·이벤트 0·seed 0 | ✅ 전부 칸 실재 — 충돌 0 |
| ⑽ | §3.3 말미 «BC 는 상태 코드 선언만: 201·400·401·403·404·409·422·500·503» | ❌ **#5 충돌**(직접 반환 없는 framework status 선언) — r2″ §3 축 동형 → **A2** |
| ⑽ | §5 products 의존 사실 | ❌ **stale** — `published_service/product_catalog_service/`·`get_purchasable_product_v1`·«계약 예외 번역» 전부 부재. 실물=r2″ 재구현 `driving_layer/open_host_service/`·`get_purchasable_product_query`·**답 갈래**(FOUND/NOT_FOUND/NOT_PURCHASABLE). 이대로 기동=coder 가 부재 경로에 막힘 → **A3** |
| ⑽ | §5 accounts·entitlements 의존 | ✅ 실재 일치(`family_purchase_context_service`·`entitlement_grant_service` — V-접미·예외형은 미이관 트리 «현존 계약» 사실 기록이라 정당) |
| ⑽ | §6-3 api.py 공유 행(멱등 3 slug=SMS 소유·`family-owner-required`=accounts 소유) | ✅ 실물 유지(:252·:264-266·:353-355·:399) |
| 빚 | `legacy_debt.txt` `#12 application.products.published_service` | ❌ **stale**(products 이관 완료로 예고대로 소멸) → **A4** |
| 전제 | 설치본 검사기 v2.8.0+ | ✅ 양 하네스 **2.11.0** byte 검증 |

주의(레인 갈림 실측): products OHS 재량 지점이 레인별로 다르다 — 레인 A
`open_host_service/get_purchasable_product/`(Outcome StrEnum 소문자·`outcome` 필드) /
레인 B `open_host_service/purchasable_product_catalog/`(`code: Literal` 대문자).
**창구 함수명 `get_purchasable_product_query` 와 답-갈래 3종 의미는 동일**하다. 따라서
A3 은 경로·모양 축자가 아니라 «현 트리 계약 파일이 정본» 형태로 쓴다.

## 개정안 (spec 개정=비위임 — 사용자 승인 후 양 레인 docs 에 동일 적용·docs-only respin)

### A1 — DB 상수 절 신설(⑻-S2): `spec.md` 현행 §7 앞에 삽입·검증 조건은 §8 로 개번

```markdown
## 7. DB 상수

**이 서버는 운영 중이 아니다 — DB·migrations 보존 의무 없음.** 재구현이 새 `0001` 을
만들면 된다. 과거 migration record·table·data 연속성 상정 불요. (V1 의 마이그레이션
사슬·테이블/제약 이름은 계약이 아니다 — §2 의 키 점유·가족 «처리 중» 최대 1 을 DB
유니크 수준에서, 상태별 필드 조합·금액 0 이상 등 불변식을 DB CHECK 백스톱으로도
집행한다는 **요구**만 승계한다.)
```

부수 개정: `:158` «기계 판정하고(§7)» → «기계 판정하고(§8)» · 현행 `## 7. 검증 조건` →
`## 8. 검증 조건`.

### A2 — §3.3 선언 집합 wire 한정(⑽·#5): `:155-158` 문단 교체

현행: «… 500 은 **framework 소유 그대로**(BC 는 상태 코드 선언만: 201·400·401·403·
404·409·422·500·503). …»

개정: «본문 파싱 불가 400·인증 401·DB 일시 경합 503(`service-unavailable`)·500 은
**framework 소유 그대로 — wire 한정**이다. OpenAPI 선언 집합은 **BC 가 직접 반환하는
갈래만**이다: 201·403·404·409·422·503(503 은 `entitlement-unavailable` 갈래) — 400·
401·500 은 BC controller 가 직접 반환하지 않으므로 선언하지 않는다(#5·products spec
§3 2026-08-15 개정과 동논리. validation 422 wire 는 framework 소유 그대로이고 422
선언은 BC 갈래 몫이다). 오류 응답 «선언 스키마»는 V1 과 달라질 수 있다(BC ErrorSchema
로) — A축 등가는 성공(2xx) 경로만 기계 판정하고(§8), 오류 경로는 이 절이 정본이다.»

### A3 — §5 products 의존 사실 갱신(⑽ stale): `:200-203` 불릿 교체

개정: «**상품 관찰(products OHS)**: products 는 표준 트리로 이관 완료됐다(2026-08-15
재구현) — `application/products/driving_layer/open_host_service/` 아래
`get_purchasable_product_query`(`GetPurchasableProductRequest` →
`GetPurchasableProductResponse`) 창구를 쓴다. **갈래는 예외가 아니라 «답»**이다:
응답 outcome 세 갈래 — FOUND(payload 5필드: `product_id`·`name`·`price_krw`·
`daily_token_limit`·`weekly_token_limit`)·NOT_FOUND·NOT_PURCHASABLE — 를 이 BC 의
404/409 로 번역한다. 정확한 계약 모듈 경로·응답 표현은 **현 트리의 계약 파일이
정본**(현존 코드·열람 가능)이다.»

### A4 — `legacy_debt.txt` products 행 소멸(예고 실현)

`#12 application.products.published_service` 행 삭제 + 주석 갱신: «(2026-08-15 갱신)
products 는 open_host_service/ 로 이관 완료 — 예고대로 자동 소멸. 잔존 상류 빚은
accounts·entitlements 2곳.»

### A5 — `request.md` 를 r2″ 판형으로 respin(발주문 — 재료 아님·하네스 소유)

products request 판형을 BC 치환해 승계. 라운드 2′ 판 대비 추가되는 절: **계약 표면
사전 대조(G1 걸음)**(대조 대상=BC ErrorSchema·admin 실행 화면 배치·OHS «소비» 창구
실재) · **STOP (a)/(b) 분해** · **차단·노출 단서** · Placement graphify-out 조항.
billing 고유: scripts 신설 조항 없음(spec 에 seed 없음). 앵커 해시=`ANCHOR_HASH_TBD`
(순환 규약 — 앵커 커밋 후 기입). 완료 기준 참조=«spec.md §8 검증 조건». 커밋 제목=
`rebuild(billing): S4-r1 — 클린룸 재구현`.

## 앵커 상태 실측(참고 — 기동 걸음에서 재실측)

- 양 레인 `application/billing` **이미 부재**(라운드 2 앵커에서 삭제·배선 걷기 유지 —
  urls·INSTALLED_APPS 에 billing 행 0·`SITE_SUBHEADER` 브랜딩 문구는 §6-4 대로 존치).
- 기동 시 남는 앵커 걸음: docs respin 커밋(A1~A5) → pycache 정화 → graphify 클린
  재빌드 → baseline 실측(양 레인 `uv run pytest`) → 배선 스모크(⑺) → build_anchor
  기록 → request 해시 기입 → 기동 HEAD 커밋.
