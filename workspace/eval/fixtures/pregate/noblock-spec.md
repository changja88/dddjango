# 미니 설계 명세 — orders BC 프로모션 슬라이스 (블록 부재 픽스처 · 차단 모드 exit 3)

형식 규범 시행 «전»에 승인된 구형 명세의 판형이다 — machine 마커가 하나도 없고 파일 계획은 산문 표로만
적혀 있다(kkebi-server 20/20 명세 판형). 관찰 모드에서는 «구형 명세 skip 한정» 조항으로 exit 4 였으나,
차단 모드(2026-09-03 승격)에서는 블록이 의무이므로 «형식 red(블록 부재)» exit 3 이 기대값이다.

## 파일 계획 (산문 표 — 기계 블록 아님)

| 태그 | 경로 | 비고 |
|---|---|---|
| add | application/orders/domain_layer/shared_value_object/promo_code.py | 값 객체 |
| add | application/orders/test/unit/test_promo_code.py | 단위 테스트 자리 |

## 공개 심볼 (산문)

- `PromoCode {code: str}` — 값 객체 · 빈 코드 거부.

## 영구 테스트 입장 표

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| PromoCode 검증 | 값 객체 생성 시점 검증 계약 | 빈 코드 유입 | 없음 | add | `application/orders/test/unit/test_promo_code.py` |
