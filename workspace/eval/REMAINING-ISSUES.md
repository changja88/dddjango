# 최종 스모크 — 남은 문제 추적 (2026-05-30 기준)

> 출처: 최종 수동 스모크(Claude 태스크A 재고예약 · Codex 인터랙티브 태스크B 주문생성, clean fixture).
> 인사이트 HTML: `FINAL-SMOKE-INSIGHTS.html` · 메모리: `dddjango-final-smoke-findings`.
> **정직 경계**: 각 N=1 + 태스크 상이 → 런타임차/태스크차 분리 불가. 이 목록은 "표준 보강 대상"이지 "Claude>Codex 입증"이 아님.

## 상태 요약

| ID | 문제 | 런타임 | 상태 | 다음 액션 |
|----|------|--------|------|-----------|
| P1b | 의존성 버전 stale(④f) | Codex | ✅ **구현 완료** (커밋됨·동적검증 대기) | 라이브 검증 |
| P1a | ninja problem+json 처리(operation 품질) | Codex 위반/Claude 준수 | ✅ **구현 완료** (2026-05-30, 커밋) | 동적검증·집행 백스톱(Stage 4) 잔여 |
| P2 | 코더 가드레일 프로덕션 커스텀 백엔드 미차단 | Claude | 🔴 OPEN | 가드레일 재보강 (서브에이전트 리뷰 선행) |
| P3 | 동시성 행위 테스트 부재 | Codex | 🟡 점검 필요 | acceptance/coordinator가 race 테스트 요구하는지 점검 |
| P4 | ③ 판정-소유 이주 비결정 | 양 런타임 | ⚪ 데이터 부족 | N≥5 블라인드 정량화 후 판단 |

---

## ✅ P1b — 의존성 버전 stale (구현 완료)
- **증상**: Codex가 `django-ninja==1.4.5`(PyPI 최신 1.6.2)를 *기억 속 옛 버전*으로 핀. 핀=설치 일치 → 무핀 resolve 안 함.
- **보강(2026-05-30)**: `discipline-houserules` **§6.2 신설**(⚠️ ninja §6.2와 이름만 같고 다른 규칙) = "새 런타임 의존성=무핀 resolve→실제 설치값 핀, '최신'은 기존 프레임워크 핀과 호환되는 최신, 안정 릴리스만, 막힌환경 보고" + `ninja §2.1`→§6.2 교차참조 + `coder.md`(+codex 미러) 집행 불릿. 7파일·byte-identical·`claude plugin validate` ✔.
- **남은 것**: **동적검증**(다음 의존성-추가 런에서 무핀 resolve→핀+호환한계 처리 — 캐시 신선화 선행, LLM 행동이라 결정 보장 아닌 완화책). 커밋 완료(eval/codex-determinism-n2).

---

## ✅ P1a — ninja problem+json operation 품질 (구현 완료 2026-05-30)
- **분석 결론(전제 정정)**: 핵심 증상(operation 본문 수제 응답)은 **공백이 아니라 일탈** — `implementation-django-ninja §6.2`가 이미 3곳에서 금지하고 Claude는 준수했다. (b) OpenAPI 몽키패치는 (a)의 하류 보상 해킹. 근본 원인은 §6.2가 "problem+json 미디어타입 필수"와 "schema 매핑 우회 금지"를 동시 요구하는데 **ninja에선 에러에 대해 둘이 양립 불가**(실증). + 집행 갭(어떤 에이전트도 ninja §6.2 준수를 구현 후 독립 검증 안 함 — discipline-reviewer는 클린코드만·acceptance-tester는 content-type 미검증)도 확인.
- **해법(사용자 선택 = prohibition→positive 레시피)**: 금지를 완성된 긍정 레시피로 흡수 + 양립불가 긴장을 표준이 명시 해소. **실증검증**(ninja 1.6.2 probe ×3: per-status 미디어타입 부재·중앙핸들러=problem+json런타임/json-OpenAPI·tuple deprecated·`create_response` 일괄변환) + **서브에이전트 3리뷰**(ninja기술/정합성/작문) 반영.
- **구현(6파일, byte-identical 유지)**: §2.2 raise+`Status`(deprecated 튜플 예제 제거) / §6.2 전면 재작성 = 중앙 `@api.exception_handler`+단일 헬퍼가 **처방된 기본(A)** + `create_response` 오버라이드 **DRY 대안(B)** + 프레임워크 기본 5종(401/403/404/422/429) + **OpenAPI application/json은 수용된 한계** 명시(금지는 `get_openapi_schema` 사후변형만 — NinjaAPI 상속 자체는 허용; 1차 "상속 금지"안을 리뷰가 정정) + 1.6.x 핀 / §6.1·§8 정합 / SKILL ×2 / FINAL-SMOKE-PLAN 축4 채점기준. `claude plugin validate ./dddjango` ✔.
- **파일명 누수(c) `orders_ninja_api`**: 이번 범위 밖 — §4/houserules 별도 축, N≥2 재발 시 승격(미반영).
- **잔여**: 동적검증(다음 라이브 API 런에서 coder가 raise+중앙변환 하는지) · 집행 백스톱(Stage 4)은 레시피가 실패모델 뿌리를 쳐서 N≥5까지 보류.

## 🔴 P2 — 코더 메커니즘 가드레일 프로덕션 커스텀 백엔드 미차단 (OPEN)
- **증상**: Claude 코더가 `config/db_backends/sqlite3_immediate`(BEGIN IMMEDIATE)를 `settings.py` **프로덕션 DATABASES ENGINE에 배선**(테스트 race 관찰성용). `f9ea088` 가드레일이 *발화는*(env갭 보고+§3.2 개정 제안 — 옛 조용한 토끼굴보다 투명) *대체는 못 막음*(설계 반송 대신 자가결정·규율감사 통과).
- **대조**: Codex/B는 `select_for_update`+CAS+CHECK로 백엔드 없이 깨끗(단 동시성 테스트 없어 안 부딪힘 — confound).
- **boost 방향**: "테스트 관찰성용 DB 백엔드는 **테스트 전용 설정에 격리**·프로덕션 ENGINE 변경 금지, 아니면 설계 반송". 섬세한 코어 → 서브에이전트 리뷰 선행.

## 🟡 P3 — Codex 동시성 행위 테스트 부재 (점검 필요)
- **증상**: Codex/B(주문→재고차감=동시성 민감)에 CAS+CHECK 구조 가드만, oversell/race **행위 테스트 0**. P2의 거울상(Claude 과검증↔Codex 미검증).
- **점검**: acceptance-tester/coordinator가 동시성 기능일 때 race 테스트를 요구하는지 — 표준에 명시할지 검토.

## ⚪ P4 — ③ 판정-소유 이주 비결정 (데이터 부족)
- **증상**: Claude=catalog 완전 이주+Product 애그리거트 승격 / Codex=catalog 평면+published_service 함수(트랜잭션 스크립트). 정반대 착지지만 **둘 다 DR-16 허용 범위**(스코프 escape). 편차 큼(풀 DDD↔함수).
- **판단 보류**: 의도된 여지 vs 조여야 할 비결정 → **같은 태스크 N≥5 블라인드**로 빈도 정량화 후 결정. 지금 표준 손대는 건 시기상조.

---

## 방법론·운영 이연 (별도 트랙)
- **N≥5 블라인드 측정**: codex vs claude 우열 결론 + ③ 비결정 정량화(P4)의 전제. 같은 태스크·블라인드·루브릭 필요.
- **크로스-메모리 갱신**(P 분석 시): `dddjango-standard-hardening-verification`(가드레일 항목=P2) · `dddjango-stdgap-3-4`(축9 결판·P4) — 각 문제 분석할 때 그 메모리에 반영.
- **P1b 동적검증**: ~/.claude·~/.codex 캐시 신선화 후 의존성-추가 라이브 런.
- **릴리스 결정**: eval 브랜치 `eval/codex-determinism-n2`(DR-14~17 + P1b 보강, 로컬)의 main 머지/푸시(v1.0.1?).
