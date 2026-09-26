# 리팩터 요청 경로 수리 — 진행 기록 (2026-09-26)

캠페인 백로그 1순위(`workspace/plan/2026-09-26-refactor-campaign/plugin-improvement-backlog.md`) 수리. 사용자 부재 중 자율 진행 — 끝 지점 = **커밋 전**(사용자 선택 05:4x). 커밋·push·릴리즈 없음 · spring_dream_server 쓰기 없음.

## 사용자 결정 (2026-09-26)

- **B1 빚 방침**(05:2x): «퀄리티를 위해서는 모든 빚은 전부다 정리해야 하는게 맞는거 같아» → «예외 없이 항상 정리». 기록: 캠페인 plan-v2 §9 · 가이드 점검 synthesis-v2 §7.
- **R1 작은 수정**(05:4x): «작은 수정도 전부 정리» — 수정 모드 G0 에도 빚 스캔·ⓐ/ⓑ 질문을 넣는다(방침에 따라 ⓐ면 슬라이스 0 선행). 대가 수용: 작은 요청이 큰 작업이 될 수 있음.
- **R2 = B2 발주 지시 효력**(05:4x): «미루기만 사용자 원문 필수» — 발주서가 G0 빚 답을 ⓐ 로 미리 정하면 받는다 · ⓑ 로 미리 정하려면 사용자 원문(시각·출처) 인용이 있어야 하고, 없으면 G0 에서 멈춘다. 이번 수리에 포함.

## 범위

- 트랙 A(수리 전 절차): ① 정리 요청 → 빚 스캔 필수·폴더·ⓐ 경로 ② 수정 모드 G0 빚 스캔(R1) ③ 빚 0 + 정리 항목 0 → G0 정지 ④ 발주 고정 ⓑ 출처 규칙(R2) ⑤ REQUEST_GUIDE 문구 정합.
- 트랙 B(진단만): 백로그 3(F4-20 · F4-22/23 · F4-24) · 백로그 2 설계 초안.
- 밖: 커밋 · 릴리즈(8-B-5 Phase 2 — 창 닫힘) · 규칙 개정(#546 · #571) · spring_dream_server 쓰기.

## 운영

- 자율 진행 점검: 세션 cron **매시 :17 · :47**(ID 707a5168 — 09-26 compact 뒤 교체 · 옛 fe43041a 삭제 · 세션 한정 · 7일 만료). 사용량 한도(5시간 창)로 끊기면 한도 풀린 뒤 첫 발화(최대 ~30분 지연)가 끊긴 단계부터 재개. 서브에이전트 대기 중이면 무동작, 전 단계 완료 시 스스로 삭제.
- 운영 전제(m-16): 새 규칙은 릴리즈 뒤 시작하는 G0 부터(비소급) · 릴리즈 창 = dddjango 레인이 «G0 승인 ~ G2 승인» 사이에 0.
- 끊김 기록: ① 사용량 한도 — 회귀 시험 5건 실행 중(08:3x 이후) 도달 · 09:52 재개(한도 해제 알림으로). 백그라운드 시험은 한도 중에도 끝났고 결과 손실 없음.

## 단계 기록

| 단계 | 상태 | 산출물 |
|---|---|---|
| 0 결정 | 완료 | 이 문서 |
| A 설계 v1 | 완료(이력) | `design-v1.md` |
| A 설계 v2 | 완료 — 현장 증거 반영(법리 통일 · 좁힌 스캔 금지 · 암묵 ⓑ 차단 · 실행 판정) | `design-v2.md` |
| A 적대 검토 2건 | 완료 — A 수정 후 승인(blocker 3 = C5 운반체 모순·규칙 이전 폴더 세탁·«마무리» 관측 불가 · major 8) · B 수정 후 승인(blocker 2 = 대리 레인 출처 판별 불능·동작 불변 불가 빚/오탐 경로 없음 · major 6 · 현장 재생 11: 개선 4·동일 1·R1 수용 비용 2·악화 4) |
| A 설계 v3 | 완료 — 검토 처분표(§0) · 기각 2(git 종료 판정 = 한 브랜치 사용자 세탁 · 새 폴더 세탁 우회 = 앵커가 폴더별이라 불성립) · 보류 2(BC 밖 소비자 G0 grep · 결정 줄 검사 스크립트) | `design-v3.md` |
| A 구현 계획 v1 | 완료 — 블록별 새 문장 확정(E1~E16) · 개정 16 · 신설 26(N1~N26 · ISSUED R-3470~) · F4-20 수리 동반(트랙 B 에서 끌어옴 — 사용자에게 알릴 것) · 행동 시험 T1~T6 | `plan-v1.md` |
| A 구현 ① F4-20(E13) | 완료 — 수리안 B 적용(`_is_factory_call` 한 출처 추출 · 스칼라 판정도 이 함수로 · 반복 변수 2-walk 전파 · 정직 기록 문면 추가) · Codex byte 미러 · 픽스처 good `import_orders`·bad_rules `close_orders` · EXPECTED 15→16(findings_count · checker_baseline — emit 스플라이스 1행씩) · `pregate_symbol_kinds.json` 재소성(양쪽) · 실측: 시제품 B 와 출력 byte 동일(재현 트리·현장 사본·새 픽스처) · 기존 good/bad_rules HEAD 와 byte 동일 · cross 347/347 · fixture 104/104 · drift 8/8 | 작업 트리 |
| A 계획 리뷰 C | 완료 — 수정 후 승인(blocker 1 = 슬라이스 0 에서 뺀 ⓐ 의 출구 부재로 G2 영구 차단 · major 10 · minor 16) | `review-C-plan.md` |
| A 구현 계획 v2 | 완료 — 처분표(수용 26 · 기각 1 m-9 · 기록 1 m-14) · 개정 17(R-0164 제외 · R-0411·R-0133 추가 · clarification 2) · 신설 30(R-3470~R-3499) · 새 블록 6 · 행동 시험 T1~T11 합격 기준 | `plan-v2.md` |
| A 구현 ② 정본 | 완료 — `apply_edits.py`(v2) 적용 · ontology_gate 90/90 green · 렌더 2 doc · LEDGER 재기준선 9행 · target-counts(Block 2926 · Expr 3695 · Norm/Work 3508) · q4 골든 · `make rulepack`(양 런타임) · render_sync·ledger·issued·structural·parity·corpus 11/11·spec_lint·golden 23 전부 green | 작업 트리 |
| A 구현 ③ 가이드·미러 | 완료 — REQUEST_GUIDE §4·§6·§7(+M-3 한 줄) · Codex byte 미러 · 명세 §0 한 줄 · Codex Coordinator 의미 미러(치환 동일 적용 + Codex 표기 5종 치환 · 새 블록 2곳 · 평문 fallback 한 줄) · Codex houserules §1 · 새 토큰 14종 양쪽 계수 일치 | 작업 트리 |
| A 행동 시험 1차 | 완료 — **9/9 합격**(T1·T2a·T3·T4a·T4p·T5·T6·T7·T8) · 드러난 모호 5건(F1~F5 — 정리 요청 배치 질문 · 대화형 G0 정지 시점 · ⑶ 표시 노이즈 · 정지 때 scope.md · 질문 순서의 배치·승인 자리) → `apply_edits2.py` 로 보정(오늘 신설분 문장·라벨만 · gate 90 green · 렌더 · LEDGER 오늘 행 2개 갱신 · rulepack · Codex 동일 치환) · 범위 밖 관찰: `checker_registry.py` auto 3종 vs Coordinator 5종 | `behavior-tests.md` · scratch `bt/out/` |
| A 행동 시험 2차 | 완료 — **8/8 합격 + 대조 1**(개정 전 Coordinator 는 축소 지시대로 검사기 1종) · 합계 17/17 · T11 모호 → F6·F7 | `behavior-tests.md` |
| A 구현 리뷰 D | 완료 — 수정 후 승인(blocker 0 · major 4 = «미룰 수 없음» 별도 요청 탈출 · 오탐 STOP 경로 충돌 · F4-20 이름 단위 참양성 누락(실측) · 2차 보정이 R-0204 무개정 제한+scope.md 덮어쓰기 · minor 14) → 전부 처분(`plan-v2.md` §3) · `apply_edits3.py`(clarification 3 R-0204·R-0299·R-0442 · 라벨 12) · Codex 동일 · 가이드 2줄 · F4-20 이름 단위 fail-closed + bad 픽스처 2(HEAD 3/3 · 이전 수리본 0/3 · 현재 3/3) · EXPECTED 16→19 · 매트릭스 전부 green | `review-D-impl.md` · `plan-v2.md` §3 |
| A 회귀 시험 | 완료 — **5/5 합격**(T1r·T3r·T5r 재실행 · 책상 T11b·T12) · 총계 22/22 + 대조 1 · T12 빈틈 → F8(뺀 항목의 명세 반영은 architect 재호출) | `behavior-tests.md` |
| A 보정 F8 | 완료 — 재상정으로 뺀 항목의 명세 반영은 architect 재호출(s006/b11 · R-3498 라벨) · gate·렌더·LEDGER·rulepack·Codex | 작업 트리 |
| A 조감도 · 봉인 · 검증 | 완료 — 조감도 행 추가 · `manifest_seal.py --write`(09:53 · draft · 봉인 파일 261) · **`make verify` green 5/5**(09:54~09:58 · 268초) · **`make verify-mutation` green**(변이 11 전건 red) · 검증 뒤 작업 트리 무변 · 봉인 draft 대조 green | `evidence/verify-2026-09-26-0954.log` · `evidence/verify-mutation-2026-09-26.log` |
| **정지(커밋 전)** | 끝 지점 도달 — 저녁 보고 `evening-report.md` · 커밋은 사용자 승인 뒤(변경 커밋 → 봉인 재발행 chore 커밋) | `evening-report.md` |
| B3 F4-20 진단 | 완료 — 결함 실재 · 캠페인 #195 1건 = 이 오탐 · 수리안 B(원소식에 팩토리 판정 재적용) 시제품 검증(오탐 3 소멸·참양성 유지·기존 fixture byte 동일) · 첫 수리안 A 는 참양성 놓침 → 기각 | `diag-B3-F4-20.md` |
| B3 F4-24 진단 | 완료 — 틀린 쪽은 문언(SKILL.md:78 · 정본 discipline-houserules-skill.ttl b7), 검사기 면제가 설계 의도와 일치. **#647 94건 측정 영향 0**(Any 69·object 25 · 폼 clean 12건은 전부 `dict[str, Any]`라 어느 쪽이든 비면제) — 앞서 «빚 56% 측정 오류»라던 말은 틀림. pre-gate red 원인은 명세의 별칭 행 누락(코드 결함 없음). 권고 = 문언을 검사기에 맞추는 clarification + ModelForm good 픽스처 — graph-owned 문장이라 사용자 확정 1회 필요 | `diag-B3-F4-24.md` |
| B3 pre-gate 진단(F4-21·22·23 · digest) | 완료 — 셋 다 scratch 재현. 우선순위 ① 툴체인 digest(check-report 가 블록 해시만 봄 · registry_gate `_tree_digest` 재사용 · 스크립트만) ② F4-23(`--base`≠HEAD 면 HEAD 기준 dirty 겹치기로 사본 혼합 · 현장 red 24 = S1 커밋 파일 · 스크립트만) ③ F4-22(#574 는 스텁에서 원리상 불가 · «포트 인자로만 쓰이고 반환 안 되는 `_in`» 선언 검사 추가) ④ F4-21(`--approved-merge-file` pre-gate 확장 · graph-owned 3곳 · 폭 최대). 현장 보고 문면 정정 4건 | `diag-B3-pregate.md` |
| A 현장 증거 | 완료 — 순수 리팩터 12 중 사용자 ⓐ→S0 이동 권한 0 · 법리 4갈래 · 수정 모드 31(발주 지정 21 전부 추종 · 자발 스캔 27 · ⓐ 0) · ⓑ 51 중 사용자 원문 0 · 암묵 ⓑ(쓰기 경계 추론) 28 · 빚0+항목0 요청 0 · 낡은 앵커 수작업 우회 1 | `diag-A-field-evidence.md` |
| B2 동작 보존 증거 설계 초안 | 완료(적대 검토 전) — 현재 G2 는 슬라이스 0 동작 불변을 LLM 판단에만 기댄다 · 제안 `behavior_guard.py`(보호 테스트·마이그레이션·OpenAPI·OHS 공개 표면·URL/admin 5표면 스냅숏 전후 비교) · 발견: ninja_extra operationId 무작위 접미(`use_unique_op_id`) → OpenAPI 원시 diff 는 0 이 될 수 없음 → wire 층만 차단 · 최소판 4~5일 · 사용자 질문 3(적용 범위 · operationId 변화 취급 · 약한 단언 강화 위치) | `diag-B2-behavior-evidence.md` |
| 사용자 결정 1~6 (22시대) | 결정 기록 `evening-report.md` §5 · 로드맵 `roadmap-v1.md`(전부 진행 후 한 번에 배포 · 통합 검증 · 사본 리허설) · pre-gate 현장 빈도 실측 `diag-B3-pregate-field-frequency.md` | `evening-report.md` |
| 결정 5 반영 | ⑶ 규칙 이전 폴더 = 끝남 → 새 실행(s005/b13 · R-3483 라벨) · render · LEDGER · rulepack · Codex 미러 · 봉인 draft · **`make verify` green 5/5** · 재시험 T5n·T5c 합격 | `behavior-tests.md` · `evidence/verify-2026-09-26-decision5.log` |
| 로드맵 1 커밋 | `e3ad8e16` 변경 커밋 · `6c88ae1b` 봉인 재발행 chore(strict `--check` 는 이전에도 RED 19 — 실런 전용 · 이번 추가분은 설치본≠소스 트리 해시로 배포 전 정상 · draft 대조 green) | git |
| 로드맵 2 F4-24 | s007-4/b7 문언 정정 · R-3448 rev4 clarification(`@2026-09-26`) · render · LEDGER · 계수표 Expression 3699 · rulepack · Codex 미러 · 잠금 픽스처(`public_surface/good/…/form/line_form.py` ModelForm 별칭 기저 `clean() -> dict[str, object]` — 현행 exit 0 · 면제 좁힌 검사기 exit 2) · 행렬 4종 무변 | 이 표 아래 verify 로그 |
