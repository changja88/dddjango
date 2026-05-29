# 고정 테스트 입력 (스모크/비교평가 공통)

> 이 파일은 sample과 함께 모든 복제본(`dddjango-claude-index`·`dddjango-codex-index`)에 동일하게 들어간다.
> 두 런타임이 **토씨까지 같은 입력 + 같은 게이트 결정**으로 출발해야 차이가 "런타임 차이"로 읽힌다.

## 1. 기능 프롬프트 (토씨 그대로 붙여넣기)

```
재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.
```

## 2. 고정 게이트 답 (변수 제거 — 양 런타임 동일하게)

| 게이트 | 고정 답 | 이유 |
|---|---|---|
| G0 배치(BC) | **① 새 독립 영역**(별도 `orders` BC 앱) | 구조를 매번 동일하게(완전 §0 4계층) — `평면 vs full` 교란 제거(DR-14) |
| G0 렌즈 | **ddd + db + api** | HTTP 계약(409·주문 생성)이 있으므로 api 켬 |
| G0 스코프 | **제안대로**(주문 1건·단일 상품·수량; 충분 시에만 생성·차감) | 확장 금지 |
| API 프레임워크 | **plain Django**(JsonResponse) | 스택 변수 제거 — 코드품질만 비교 |
| 테스트 러너 | **Django 기본 test** | 〃 |
| G1 설계 승인 | 명백한 결함 없으면 **무수정 승인** | 설계 변동 자체가 결정성 관찰 대상 |
| G2 구현 승인 | 동일 기준 승인 | 〃 |
| thinking | **OFF** | 비용 레버(DR-08), 품질 무손실 |

원칙: **같은 선택지엔 같은 선택.** architect가 런마다 다른 설계를 내는 건 막지 않는다(그게 결정성 데이터). 사람은 *결정 축*만 고정한다.

> 비교 목적이 아니라 단순 스모크(파이프라인이 도는지)면 G0 배치를 "② 기존 catalog 최소변경"으로 바꿔도 된다 — 단 그때도 **양쪽을 똑같이**.

## 3. 시드 데이터 (setup.sh가 db.sqlite3에만 적재 — 테스트 DB 비오염)

| 상품 | price | stock |
|---|---|---|
| Widget | 1000 | 10 |
| Gadget | 2000 | 3 |

시드는 마이그레이션이 아니라 런타임 데이터다(테스트 DB는 매 실행 새로 만들어지므로 시드가 안 섞여 인수 테스트가 오염되지 않는다).

## 4. 실행 (이 폴더에서)

1. 이 폴더에서 해당 런타임을 연다.
   - **claude-index**: Claude Code 세션 → `/dddjango` 에 위 §1 프롬프트.
   - **codex-index**: `codex` 세션 → `dddjango` 스킬(코디네이터)이 트리거되도록 위 §1 프롬프트.
2. G0/G1/G2 게이트에서 §2 표대로 답한다.
3. 끝나면 테스트:
   ```bash
   .venv/bin/python manage.py check
   .venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate
   .venv/bin/python manage.py test
   ```
4. `git status` / `git diff` 로 파이프라인이 생성한 것 확인 → `workspace/eval/runs/<run>/` 로 캡처.

전체 방식·합격 기준·기록처는 레포 `workspace/DEVLOG.md §4 스모크 테스트 방식(정본)` 참고.
