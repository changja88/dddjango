# pre-gate 수리 배치 계획 v2 — 스텁 충실도 + 처분 라벨 성문 (v2.17.15 후보)

> v1 → 적대 리뷰 1레인(BLOCKER 1·MAJOR 6·MINOR 9 — 주경로는 검사기 코드로 확증) → v2 전건 반영.

- 날짜: 2026-09-02 · 지위: 관찰 실측 2레인(`workspace/eval/pregate-observe/ledger.md`)의 발견 ①·②에 대한 수리 배치. 사용자 결정(09-02): «ⓐ 소규모 수리 후 재실측 1레인 → 전 기준 통과 시 승격».
- 스코프: 라벨 정의 성문(그래프 1리비전) + 실행기 스텁 충실도 4계열. **이월(이번 배치 밖)**: #392 factory_boy·#160/#484 OHS aux 예외·#635 시그니처 세부·update 시뮬레이션 확장·캐시 skip 관측성·pytest 마커 검사기.

## 1. 원인 확정 (전건 결정적 재현 완료)

| 계통 | 실측 | 원인 (코드 지점) |
|---|---|---|
| #493 self ×15 (레인 2) | 스텁만 red·실코드 0건 | 명세 메서드 행이 `self`를 명시(성문 b33은 표기 미규정) + `_class_stub`이 무조건 `self,` 접두(design_pregate.py:528) → `def send(self, self, …)` 중복. 자가검증 `ast.parse`는 중복 인자를 **못 잡고**(AST 단계 — compile/symtable만 잡음·실측 확정) 검사기(#493)는 i=0만 면제라 두 번째 self가 red |
| #212 ×7·#283 ×3 (양 레인) | port/repo 선언 «구현 있음»·«@abstractmethod 없음» | `_class_stub`이 모든 메서드 body를 `raise NotImplementedError`로 렌더 + 데코레이터 무합성 — ABC 선언(base=ABC 명시)에 대한 선언형 렌더 부재 |
| #329/#332 (레인 1) | apps.py label/name 부재 | 정형 골격(`_write_apps_py`)은 **골격 채움 경로에만** 적용 — 명세가 apps.py를 file-plan add+symbols로 실으면 render_stub 경로로 생성돼 정형 값 누락 |
| #630 (레인 1) | 모델 `Meta.db_table` 부재 | symbols 문법에 Meta 내부 클래스 표기가 없어 스텁이 Meta 미합성 |

## 2. 변경 (실행기 — `dddjango/scripts/design_pregate.py` + codex byte 미러) — 적대 리뷰 v1 반영

1. **수신자 정규화(파서)**: Method params의 첫 청크를 `_split_top`으로 얻어 **완전 일치**(`self`/`cls`)일 때만 제거(M-6 — regex 접두 매칭은 `self_x` 침묵 훼손·실측 확증). 어노테이션 수신자(`self: Self`)는 제거하지 않음 → 중복으로 형식 red 귀결(MINOR-1 수용 — b35 리비전에 «수신자 표기는 무어노테이션 self/cls만» 병기).
2. **자가검증 격상**: `ast.parse` → `compile(stub, path, "exec")`, 포착은 `(SyntaxError, ValueError)`(MINOR-3). **선행 조치(M-1)**: render_stub이 boundary-imports 전사에서 `from __future__` 행을 필터(하드코딩 최상단 1회로 dedupe) — 정당한 헤더 통째 전사가 신규 형식 red가 되는 경로 봉쇄.
3. **ABC 선언형 렌더**: base 원문 strip이 정확히 `ABC`일 때만(MINOR-2 판별식 고정) 메서드 → `@abstractmethod` + `...`. 검사기 확증: #212/#283 판정은 데코레이터 유일 조건(body 불문 — 리뷰 «검증됨 C») → 확실 통과. `abc.ABC`·다중 base 미발동은 수용·이월.
4. **apps.py 정형 «필드 단위 보충»**(M-5): `application/*/driven_layer/django_*/apps.py` add에서 전사된 필드는 유지하고 **결손 필드(name/label)만 정형 값 주입**. 메서드 전사(ready 등)는 기존 렌더 유지 — #535 잠재 아티팩트는 사각 병기. 산문으로 규약 밖 값을 계획한 명세가 green이 되는 사각(MINOR-6)은 BLIND_SPOTS에 1행 병기.
5. **모델 Meta 합성**: `driven_layer/django_*/models/*.py`의 `*Model` 클래스에 `class Meta: db_table` 합성. **snake 변환은 check-db-table.py `_snake`의 2-pass regex를 문자 그대로 복제**(M-3 — 재구현 드리프트 금지)하고 연속 대문자·숫자 케이스 픽스처로 동치 고정. 명세가 클래스 필드로 커스텀 db_table을 전사하면 전사 우선(합성은 결손 시만). 커스텀 label 계획 시 유도 불일치(MINOR-5)는 #330 진탐 동반 — 사각 병기.
## 3. 변경 (규범 — 그래프 리비전 2건 + 산문 정합) — B-1·M-2 반영

1. **R-3433 rev2(amendment)** — 처분 라벨 닫힌 정의 + **확인 증거 규칙**(B-1):
   > `corrected`=개정으로 해소(다음 실행에서 소멸) · `ignored`=실위반으로 인지하되 개정하지 않음 — 실위반 확인 증거는 **G2 귀속 red 해소 트레이스 또는 legacy-debt 매칭 기록(STOP 병기)** 둘 중 하나다 · `filtered`=pre-gate 도구(스텁·문법·시뮬레이션) 한계 판정 — 실코드 대조·기존 통과 선례 등 근거 병기 의무.
2. **R-3426 rev2(amendment — architect s005/b35)** — «생략 허용분 공집합» 충돌 해소(M-2): 값 축 유도 2행(apps.py `name`/`label` 정형 · 모델 `Meta.db_table` 유도)을 **성문 유도 등재**하고, 메서드 행 수신자 표기(«무어노테이션 self/cls는 적어도·안 적어도 된다 — 파서가 정규화»)를 병기. 인용 좌표는 b35(R-3426)가 정본(MINOR-8 — 본 계획 §1의 b33 표기는 오기).
3. **산문 정합**: 설계 v3 §8 ⑴의 ignored 판정식에 같은 증거 이원화 추기 + `workspace/eval/pregate-observe/ledger.md` 헤더 판정 규칙 동기화(B-1 — Coordinator 문장만 고치면 §8 판정식이 여전히 재량 회귀).
## 4. 검증 게이트

1. 픽스처 회귀 + 확장(M-4): ⓐ green-spec에 4계열 케이스(self 표기 메서드·ABC 포트·apps.py add·`HTTPLogModel`류 모델 — 인접 규칙 완전형으로 설계, MINOR-9 노동 수용) ⓑ **form-red 픽스처 신설**(중복 인자 명세 → exit 3 기대)과 러너 3채널 확장(`pregate_fixture_run.py`가 exit 0/2만 검사하는 현행 구조 변경 — 형식 red 채널 자기검증) ⓒ `self_x` 첫 인자 훼손 부재 케이스(M-6).
2. **notification 명세 재실행(소급 대조) — 실측 완료(09-02)**: 수리 전 19건 → **수리 후 1건**(#14 진탐 정확 유지 — 안정 ID `3dc440496a29` 동일). 아티팩트 18건 전 소멸: #493×15·#212×2에 더해 #635도 소멸(중복 self가 파라미터 수 오판의 원인이었음이 판명 — 기대 초과). 기준선 1eb8507·머지본 히스토리에서 명세 복구·격리 사본 실행.
3. **백테스트 3판 회귀 → 갈음(사유 명시)**: 편입 전사본은 프로토타입 파서 전용 형식이라 정본 실행기 재실행에 형식 브리지 신작이 필요 — 소규모 배치 범위 밖. 회귀 증거는 ⓐ red 픽스처(#81/#267/#472 정확 재현) 유지 ⓑ notification 실전 정답지 소급(진탐 #14 유지·19→1) ⓒ 적대 리뷰 «검증됨 F»(수리 영향면이 백테스트 진탐 축(이름·경로·import)과 코드 수준에서 분리 — 검사기·실행기 실독 확증)로 갈음. ⑥ 감사 확인 항목.
4. `make verify` 6/6 green + codex byte 미러 동일성.

## 5. 배포·승격 경로

- 릴리즈 v2.17.15(관찰 모드 유지 — MODE 불변) → 다음 실전 레인 1개 재실측 → §8 3항 전 기준(형식 ≤1 포함) 충족 시 승격 브리프 재상신.
