# 플러그인 개정 배치 계획 — plugin-revision-decisions.md 이행

- 작성: 2026-08-25 · 정본 판정: 루트 `plugin-revision-decisions.md`(소유자 확정본) · 이 문서는
  적대 리뷰(2026-08-25) 소견과 그 해소 확정 4건, 작업 분해를 기록하는 **이행 계획서**다.
- 절차 준거: v2.17.4 사이클(`workspace/plan/2026-08-25-checker-measurement-fixes-plan.md`)과 동일 —
  검사기 수정마다 양·음성 fixture 짝 + codex byte 미러 + `make verify` green, 계수 변동 시
  EXPECTED류 하네스 갱신, 성문 리비전은 그래프 정본 경유·검사기와 «한 커밋»(#72).

## 1. 적대 리뷰 소견 → 확정 (2026-08-25 · 소유자 선택)

리뷰 결과 판정 12건의 방향(무엇을/왜)은 전건 실물 정합. «어떻게» 층위 소견 7건 중 결정 필요
4건을 소유자가 확정했다:

| # | 쟁점 | 확정 |
|---|---|---|
| D1 | #247 구현 접두 — 현행은 임의 접두 허용(문서의 «Django만 인정»은 오기) | **동작 보존** — `^[A-Z][A-Za-z0-9]*{Bc}([A-Z][A-Za-z0-9]*)?UnitOfWork$`(접두 1어절 이상 필수). ^Django 조이기 비채택 |
| D2 | #247 축약 불허의 집행 — 현행 루프는 비-UnitOfWork 접미 클래스 불가시 | **전수 가시화** — unit_of_work/ 파일의 모든 공개 클래스에 정규식 적용(포트·구현 양쪽). 사적(밑줄) 제외 |
| D3 | #245 — L84 UOW_METHODS는 미사용 죽은 상수·현행 집행은 __enter__/__exit__ 부재 불검·임의 dunder 허용 | **exact-set 실집행** — 메서드 집합 == `{__enter__, __exit__, after_commit}`(+`__init__` 허용). 존재+초과 양방향. async UoW(__aenter__)는 canon 밖(후속 개정 사항) |
| D4 | #256/#351 빈 골격 술어 — 정본 문서 안에 0바이트/strip-빈 혼재 | **#114 동일 술어** — «parse 결과 docstring 밖 문장 0개»(0바이트·공백·주석-only·docstring-only 전부 skip). pass·내용 실재·parse 불능은 진단 유지(fail-closed). 정본 문서 ④의 음성 fixture 문면은 «pass만 유지»로 개정된 것으로 본다 |

결정 불요·기본값 채택(동작 보존 방향 — 이의 시 재론):
- **#456 경우의 수**: 어디서도 raise 안 되는 validation-형 이름 클래스(죽은 대외 계약)·contract와
  service **양쪽** raise → 둘 다 위반 유지. 판별은 자리 기반 — «contract/ 서브트리 내 raise = 형식
  검증(위반) · driving service·usecase의 outcome 매핑 raise만 = semantic(인정)».
- **⑫ ㉮ 되돌림**은 그래프 리비전 동반이 필수(검사기 주석 «#417 부칙 · 그래프 리비전 동반» 명시):
  R-0029(implementation-django-ninja-final)·R-2918(-skill) 리비전 3(철회 amendment) → render →
  corpus mirror → rulepack → 계수 → LEDGER → 스펙 대장 #417 부칙(되돌림 기록) → 검사기와 한 커밋.
- **배치 제외**: #63(3번·기확정 상세 부재)·#195(8번·worklist 미실재)·#16(9번·무행동)·#189/#205
  (10번·선택) — 상세 제공 시 후속 편입.

## 2. 작업 분해

| W | 대상 | 내용 | fixture 레인 |
|---|---|---|---|
| W1 | check-naming.py #247 | D1+D2 정규식화·전수 가시화 | naming |
| W2 | check-port-adapter-pairing.py #245 | D3 exact-set 실집행·문구 dunder 교정 | port_adapter_pairing |
| W3 | check-domain-model.py #256 · check-port-adapter-pairing.py #351 | D4 빈 골격 skip(#114 동일 술어 — 공유 헬퍼) | domain_model · port_adapter_pairing |
| W4 | check-context-isolation.py #157/#484 | PEP 695 type 별칭 해소(모듈-로컬 테이블·재귀+순환 가드) | context_isolation |
| W5 | check-public-surface-annotation.py #456 | 이름 토큰 → raise-지점(자리 기반) 판정 | public_surface |
| W6 | check-error-centralization.py ㉮ + 그래프 | 변형 B 제거·_select_canonical 철거 + 성문 세트(위 참조) | error_centralization_canonical_alt 처분 |
| W7 | check-transaction-boundary.py #197 | :491 진단 문구 교정(with 나열 제거 — 구현 정합) | (문구만 — 거동 불변) |
| W8 | 하네스 | count-golden·cross-matrix EXPECTED 갱신 · codex byte 미러 · make verify | — |

구현 순서: W7 → W3 → W4 → W1 → W2 → W5 → W6 → W8 (저위험·독립 먼저, 성문 동반은 마지막).

## 3. 릴리즈·통지

- 전 W green 후 `make release`(차기 버전). 릴리즈 후 kkebi tarot 정적 런의 django_ninja 신규 red는
  **의도된 회복**(v2.17.4 판례와 동일 통지) — tarot 재작업 사이클(판정 ⑤~⑫ 제품분)이 새 플러그인으로
  수행되며 해소한다.
