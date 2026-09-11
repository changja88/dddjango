# field-report-4 — spring_dream_server 대공사 플러그인 미처리 목록

- 보고 출처: spring_dream_server 발주자 세션 · 2026-09-10~11 현장 보고.
- 정리 기준: 2026-09-11 · dddjango 2.18.2 개발 작업 기준 · 미처리 1건(F4-20).
- 관리 원칙: 이 문서에는 미처리건만 남긴다. 수정·검증 완료 또는 비결함 종결이 확인되면 요약표와 본문에서 함께 제거한다. 일부만 해결됐으면 해당 번호에는 남은 범위만 적는다.
- 레인의 임시 우회·waiver·설계 정정은 플러그인 문제의 처리 완료로 보지 않는다. 개선 후보는 채택·기각이 결정될 때까지 남긴다.
- 항목 번호는 재사용하거나 다시 매기지 않는다. 다음 신규 항목은 F4-21부터 추가하며 요약표도 함께 갱신한다.
- 완료 근거: 기존 [수정·검증 기록](../../plan/2026-09-10-field-report-4-fixes.md), 이번 [후속 수정 계획](../../plan/2026-09-11-field-report-4-followup.md)과 [최종 독립 감사](../field-report-4-followup/final-audit.md), [최종 검증 기록](../field-report-4-followup/completion.md). 이번 개발 작업의 커밋·배포 완료를 뜻하지 않는다.

| # | 남은 문제 | 영향 | 상태 |
|---|---|---|---|
| F4-20 | 팩토리 생성 컬렉션의 원소 출처를 반복 변수에 전파하지 못함(#195) | 정당한 일괄 생성·검증·저장 코드 차단 | 미처리 · 이번 승인 12건 밖의 추가 보고 |

## F4-20 — `check-transaction-boundary.py` #195 가 «팩토리 호출로 태어난 이름」을 `for` 원소·컴프리헨션 원소로 전파하지 않음 → 명세가 요구한 «전량 생성 → 전량 검증 → 없는 행만 저장」 순서의 정당한 코드가 귀속(A5 STOP-03 · 2026-09-11 18:40 KST · 중 · AST 추적 한계)

- 실측(2.18.2 · registry_gate 앵커 a6e3692d · 귀속 1): `[#195] application/fortune_library/application_layer/search_term_mapping/import_search_term_candidates/import_search_term_candidates_use_case.py:N: save/remove 인자 `mapping` — 같은 함수 안에서 루트 메서드 호출을 받은 적이 없다`. 실물 = `mappings: tuple[SearchTermMapping, ...] = tuple(SearchTermMapping.create_pending(...) for candidate in command.candidates)` → `for mapping in mappings: self._reference_policy.validate(mapping, …)` → `for mapping in mappings: if self._repository.load_by_identity(mapping.identity) is None: self._repository.save_new(mapping)`.
- 원인: `_check_execute_body`(468~515행)는 `Assign/AnnAssign(target=Name, value=Call)` 에서만 `factory_born` 에 target 이름을 넣는다(여기선 `mappings`). `ast.For` target(`mapping`)·컴프리헨션 원소로의 전파 분기가 없고, 저장 인자 이름 `mapping` 은 `method_called`/`factory_born` 어디에도 없어 #195. 검사기 33~35행 «정직 기록」(«도메인 팩토리 호출로 태어났으면 통과」)과 실측이 어긋난다. 도메인 서비스 호출 `self._reference_policy.validate(mapping, …)` 은 수신자가 Attribute 라 `method_called` 에 안 들어가는데 이는 의도된 정의(루트 메서드 아님).
- 왜 회피 불가: «첫 쓰기 전 전체 검증」 계약은 집합을 두 번 순회해야 하므로 저장 인자는 필연적으로 반복 변수다. 우회 후보(원소마다 no-op 루트 메서드 호출 · 저장 직전 변수 재대입 · 저장소 집합 메서드 신설)는 전부 «AST 인식만을 위한 재작성」 또는 설계 변경이라 규율 위반.
- 발주자 처분: waiver 레코드 1(A5 발주서 개정 3 · REPORT 별개 보고 · 파일 구조 유지). 기대: `for target in <factory_born 이름>` 과 컴프리헨션 `for x in <factory_born>` 의 원소 이름을 factory_born 으로 전파(iterable 이 `tuple/list/frozenset(<genexpr of Call>)` 이면 원소도 팩토리 출생) — 또는 «집합 정렬 저장」 정형(`tuple(Factory(...) for …)` → `for m in …: repo.save(m)`)을 화이트리스트로.
