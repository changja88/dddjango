# T3 전량 이관 총괄 리포트 (2026-08-22 · 정본)

> 준거: 블루프린트 v3.2 §8 T3 행 · T1 계획 v1.1 §T3 산출 · 동결 §6 대안 경로 «구조 이득 명시 채택»(사용자 결정 2026-08-22). 실행 판형: ultracode 병렬(사용자 승인) — 저작 Opus 5 · 적대 리뷰 Fable 5 · 조립·검증은 도구 직렬. 배치별 사용자 검수는 «운용 중 상시 품질 체크»로 전환(사용자 지시).

## 1. 결과 요약

| 항목 | 값 |
|---|---|
| 이관 분모(게이트 1 동결 센서스) | REF 539절 · 규범 3,235문장 (926절 중 — NAR 387절은 설계대로 산문 존치) |
| **이관 실적** | **그래프 소유 539절 = REF 분모 전량** · 30/30 문서 |
| Work 채번 | **3,400**(파일럿 125 재사용 포함) · 블록 2,877 · Expression 3,400 |
| djr:restates | 616 트리플(같은 문서 133 · 교차 문서 483 — 웨이브 4 소급 428 주입 포함) · 댕글링 0 |
| byte 등가 | 마커 제거 후 잔차 0 — **전 절**(render_sync 상시 단언) |
| 계수 검산 | 3원(기대표=원장=ISSUED) 매 웨이브 일치 |
| 검증 | make verify 전체 green(웨이브마다 재확인) · 미러 11/11 in-sync |

## 2. 실행 기록 (4웨이브 + 마감)

| 웨이브 | 내용 | 커밋 | 적대 리뷰 처분 |
|---|---|---|---|
| 1 | 실사용 코어 7문서 — REF 235절·Work 1,635 | `fe1057c` | 79건(수리 70·기각 9) |
| 2 | 중형 8문서 — REF 220절·Work 1,029 | `71bdc81` | 81건(수리 70·기각 11) — 한도 정지 1회 resumeFromRunId 무손실 재개 |
| 3 | 소형 15문서(5묶음) — REF 80절·Work 611 | `148911d` | 43건(수리 41·기각 2) |
| 4 | 재진술 취합 6조+검증 · 조항 분석 4건 | `8b1555c`(산출물) | 연결표 후보 715 → link 510 → 중복 82 제거 → **좌표 기계 검증 428/428 통과 주입** |

에이전트 총 75기 · 오류 0 · 파이프라인 벽시계 합계 ≈3.3시간. 검수 재료 전량 보존: `orders/`(발주서) · `specs/`(migrate-spec) · `worksheets/`(census 대사·배선 근거·유예) · `reviews/`(지적·처분).

## 3. 판정 판례 축적 (운용 중 품질 체크의 기준)

- **census 대사 차이의 3유형**: ① 문서 내 재진술 흡수(센서스는 문장 계수라 사본 포함 — §15 «정본 1곳» 규율로 spec이 적음이 옳음) ② 장문 불릿 한 행 다규범(문장 해상도 재계수로 spec이 많음이 옳음 — agent·SKILL 문서군) ③ 동결 후 원문 개정(command-dddjango step 6′ — 센서스 개정 1로 좌표 재동결). 전건 worksheet에 사유 기록.
- **frontmatter**: code 아님 — 행 단위 prose/norm(웨이브 2 판례·웨이브 3 일관 적용).
- **로스터 밖 도구**(registry_gate·business_vocab 등): enforcedBy 불가 — basis에 도구명 명기한 위임.
- **«존재하지 않는 집행 주장 금지»**: docstring이 Phase 3 유예를 자기 선언한 검사기(#10·#82 등 ast 축)는 ④맵 지목이 있어도 enforcedBy 금지.
- **배선 4원 종합 + 27종 docstring 전수 실독 의무**(T1 L-F 교훈) — 전 웨이브 이행.

## 4. 마감 처분 (웨이브 4 메모 4건)

- **tree-coords(트리 N행 좌표)**: **ⓒ 채택·적용 완료** — 좌표 정본은 코퍼스 밖(`docs/file_tree.html data-r`), authoring §14 규약 1행 신설, worksheet §3 10·11번 «유예 기각» 전환. 별건 등재 2건: ① anchor_integrity_check에 트리 행 해소 백스톱 ⑦ 신설(≈20행 — 댕글링 좌표 방지) ② tree_mirror_check `--write` ↔ owner-graph 이중 기록자 처분(㉠ splice가 rules TTL 리터럴을 소스로 — **트리 개정 전 필수**).
- **hash-n-alias / contract-ref / q4-coverage**: 적용 전 적대 리뷰 경유(T2-2 선례 — 판단표 리뷰가 거짓 alias 4건을 막았음). 결과는 §5에 추기.

## 5. alias·contract#·q4 처분 결과 (2026-08-22 — 적대 리뷰 경유 후 적용 완료)

리뷰 판정: hash-n-alias·contract-ref = **apply_with_fixes**(blocker 각 3 — 전건 수정안 첨부), q4-coverage = **apply**. 리뷰 findings 정본 = `reviews/memo-*-findings.md`. 적용 내역:

- **alias 대장 3→28엔트리**(`wiring/aliases.ttl`): rule# 21(유지 #3·재귀속 #488→R-3181·신설 19 — 조건 A/B의 restates 선행은 소급 패스로 이미 충족 확인) + **contract# 7 신설**(선행 계약 레인 — 검사기 파일명 키·enforcedBy 간선 동반 의무). **rule#486→R-0118 취소**(합성 규칙 판명 — v2가 #119에 적용한 사유 동일). 무접두 #N 본문 편입은 **기각 유지**(정본 동일성 30종/538 = 5.6% — 계수 근거). reg#N·결정#N·slot#N 공간은 보류·소멸 등재(메모 §4).
- **⑥″ 2공간 문법**(structural_check): `rule#N | contract#check-*.py` + contract 축은 레인 7종 실재·enforcedBy 간선 fail-closed. self-test 9→**12/12**.
- **violation_adapter**: 2형 키(rule=#N·contract=원문), 계약 레인 조인 경로(«contract_joined/unjoined» 계수 분리 — 혼성 3종은 후자 잔존), self-test 하드코딩 제거(대장 파생 — 재귀속 재발 방지). **#488→R-3181 end-to-end 재실증 + R-0122 계약 왕복 실증** green.
- **q4 전량 포함 개정**: 무앵커 절 Work 1,707 포함(팩 = Work 3,400 전량), 정렬 키 = 절 IRI 서수(생성기 소유), rule# AliasEntry ⊆ by_alias **역방향 fail-closed 신설**, contract# 레인은 팩 제외(그래프 전용 — D12). 스키마 `rulepack/1` 유지(두 필드 소비자 0 실측 — rulepack.py docstring·T2-4 설계 정본 기입). 질의 골든 재기록 diff 검수: q2 재귀속 반영·q4 3,400·with_alias 28·q1/q3 불변.
- **검사기 docstring 27종 동기**(리뷰 B3 자기모순 수정 반영): layer-skeleton 9조인 · contract 레인 7종 · #74→R-3229 21종(제외 2종은 checker_lint 소유 명기) — 대장 교차검증 mismatch 0·codex 미러 27종 byte 동일.
- **검증**: rulepack 스모크 14/14 · 변이 11/11 전건 검출(M1 검출 조건 재구성 — 픽스처 쌍을 정순↔identity 사전순 역전으로) · 계수 기대표 AliasEntryShape 30 green · make verify 전체 green.
- **사용자 확인 잔여**(q4 메모 §8 — 적용은 완료·이의 시 되돌림 가능): ① q4 전량 포함이 설치본 계약 변경(2.17.0 탑재) ② 스키마 rulepack/1 유지 판단 ③ tier 2 주입 상한은 폐루프 재개 시 별건 심의.

## 6. 잔여·이월 (T3 밖)

- reg#N·결정#N alias 공간: 보류(문법·네임스페이스 선결 — hash-n-alias §4.1·4.2).
- tier 2 주입 상한: 폐루프 재개 결정 시 심의(측정 재료 부재 — q4 메모).
- 혼성 3종 계약 레인: contract-ref §7 범위 밖 명시.
- T4(codex 이중 렌더·불변식2 대체) · T5: 블루프린트 §8 대기.
- violation_id 산식 검사기 축 부재(contract-ref §6 부수 발견): 예방 처분 후보.
