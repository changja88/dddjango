# T3 전량 이관 실행 계획 (2026-08-22 — ultracode 병렬)

> 정본 준거: 블루프린트 v3.2 §8 T3 행 + T1 계획 v1.1 §T3 산출. 분모 = 게이트 1 동결 센서스 **REF 539절·규범 3,235문장**(926절 중). 파일럿 기이관 4절 제외 시 잔여 **REF 535절·약 3,145문장**. 사용자 결정(2026-08-22): ultracode 병렬 — 저작=Opus 5, 적대 리뷰=Fable 5, 배치별 사용자 동기 검수는 «운용 중 상시 품질 체크» 방식으로 전환(사용자 2026-08-22 «계속 쓰면서 그때마다 퀄리티 체크» 지시 준거), 대신 문서별 적대 리뷰 + 병합 전역 기계 검증 + 웨이브별 검수 패키지를 남긴다.

## 병렬 설계 (충돌 구조 제거)

- 에이전트 산출 = **migrate-spec JSON + worksheet만**(문서당 1조 — 판단만 병렬). 공유 자원(rules/wiring ttl·ISSUED 채번·LEDGER·기대표·마커 삽입)은 병합 단계에서 `ontology_migrate.py --write` → `ontology_render.py --apply`가 **직렬** 조립 — 채번 충돌·파일 충돌이 구조적으로 없다.
- byte 등가는 도구가 기계 보장(리터럴은 원문 스팬 절취) — LLM 품질 위험은 블록 경계·kind·규범 식별·배선·재진술 판단에 몰리고, 적대 리뷰 4렌즈가 그 네 곳을 겨눈다.
- **재진술 교차 문서 쌍은 전량 유예** → 전 웨이브 완료 후 소급 패스 1회가 일괄 연결(파일럿 유예분 ninja §6.2↔§2.2 포함). 병렬 저작 간 순서 의존을 제거하는 결정.

## 웨이브 구성 (실사용 코어 우선 — 문서 단위 소유 분할)

| 웨이브 | 문서 | 규모 |
|---|---|---|
| **1 (진행)** | command-dddjango(11절·314) · architecture-ddd-final 잔여(36절·206) · implementation-django-ninja-final 잔여(21절·182) · agent-discipline-reviewer(8절·237) · implementation-django-final(63절·223) · discipline-cleancode-final(89절·216) · agent-design-architect(7절·181) | REF 235절 · 1,559문장 |
| 2 | implementation-test-final(49·175) · architecture-api-final(32·167) · discipline-tdd-final(44·156) · implementation-django-web-final(12·129) · architecture-db-final(28·106) · agent-coder(6·105) · agent-design-review-api(7·97) · implementation-python-final(42·81) | REF 220절 · 1,016문장 |
| 3 | 잔여 15문서(스킬 SKILL 10종 + houserules 2종 + 소형 agent 3종 — 2~3문서/에이전트 묶음) | REF 80절 · ~570문장 |
| 4 (마감) | 재진술 소급 패스 · T3 게이트 조항 4건(무접두 #N 재검토 · alias 재검토 · rules 전량 병합 성능 실측 · 선행 계약 6종 contract_ref 조인) · 조감도·원장·기대표 최종 정리 | — |

## 웨이브 공정 (반복 판형)

1. `make_orders.py <docs…>` → 발주서 (기계)
2. **Workflow**: 문서별 pipeline — 저작(Opus·spec+worksheet·migrate 검증 전용 exit 0) → 적대 리뷰(Fable·4렌즈: 경계/kind·규범 식별 census 대사·배선 4원·재진술) → 수리(Opus·지적 시만)
3. **병합(직렬·메인)**: preflight → 문서 순서 고정으로 `ontology_migrate.py SPEC --write` → `ontology_render.py --apply` → 4단 게이트 + 계수 기대표 갱신 → `ontology_render_sync.py` → issued/ledger check → `make verify` → 커밋(문서 소유 전환 = 한 커밋 규율)
4. 게이트 ④ 병합 시간 실측 기록(T3 게이트 조항 — 성능 재평가 재료) · 조감도 갱신

## 재개 좌표

- 웨이브 중단(5시간 창 마감 등) 시: `Workflow resumeFromRunId` — 완료 문서는 캐시 재사용, 미완만 재실행. runId·scriptPath는 세션 기록.
- 세션 재시작 시: 이 파일 + `workspace/eval/t3/` 산출물 상태(specs/ 완료 여부)로 재개 지점 판정.
