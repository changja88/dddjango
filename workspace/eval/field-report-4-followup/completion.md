# Field report 4 후속 수정 — 완료 기록

승인한 **F4-1 및 F4-9~F4-19, 총 12건**의 수정과 검증을 완료했다. 문제 검토 3명, 계획 적대적 리뷰 3명과 재리뷰, Task 1~6 구현 및 작업별 독립 검토, 전체 구현 리뷰 3명, 지적 보완과 재검토, 독립 최종 감사를 수행했다. 추가 사용자 정책 결정이 필요한 사항은 없었다.

| 범위 | 반영한 결과 |
|---|---|
| F4-1 · F4-18 | 명시된 use case 효과·UoW와 DTO 필드 출처를 설계 단계에서 대조한다. 지원하는 기존 테스트 마커의 최종 선언 상태를 전사하며, 불명·동적 변경은 미검증으로 보존한다. |
| F4-9 | 확인된 admin의 화면 context 전달·조립과 업무 소비를 구분한다. 실제 업무 소비·불명 탈출은 일반 검사나 후보로 남기고 필수 타입 규칙은 유지한다. |
| F4-10 · F4-11 | OHS builder 준비와 실제 use case 실행을 구분해 세고, 확인된 닫힌 표준 Enum은 불필요한 검증 후보에서 제외한다. |
| F4-12 | 정확히 생성된 after_commit 스텁의 #376만 S1 본문 미검증으로 분리한다. 실제 구현의 #376 및 #566 검사는 유지한다. |
| F4-13 | 잡은 인프라 예외의 내부 계약 번역과 외부 HTTP 응답 정책을 구분한다. 일반 저장소 실패의 기존 safe 500을 유지하며 새 공개 오류 계약을 만들지 않는다. |
| F4-14 · F4-15 | 확인된 lexical UoW 구간별로 애그리거트 종류를 세고, code/errno/status_code 비교는 실제 출처에 따라 판정한다. 불명 경계·출처는 후보로 보존한다. |
| F4-16 · F4-17 | 부품의 50행 하한을 폐지하고 응집·승격·200행 검토 규칙은 유지한다. 선택적 인스턴스에서 캐시만 남은 디렉터리를 직접 검사와 snapshot에서 동일하게 취급한다. |
| F4-19 | 초기 예보와 명시적 재예보의 기존 정책을 유지하면서 기준선·오버레이 충돌 원인과 해결 안내를 구분한다. |

정본 TTL 개정, Claude 투영, Codex 의미·byte 미러, rulepack과 현재 문서까지 반영했다. 현행 검사 요구에 따라 원장에 graph 기준선 9행과 검증된 원문 주소 2행을 추가했으며, 과거 원장·Expression 이력·채번 대장과 reference 원본을 보존했다.

전체 구현 리뷰 A/B의 5개 Major와 설명 Minor를 보완하고 독립 재검토에서 B0/M0/m0를 확인했다. [최종 독립 감사](final-audit.md)는 12건 모두 승인 범위 내 해결, 부분 미해결 0, 증거 부족 0으로 판정했다. 이후 최종 게이트에서 드러난 기대값·생성 메타데이터 7파일도 실제 HEAD/최종 레코드 차이를 근거로 맞추고 [별도 독립 재검토](evidence/final-gate-fix-review.md)를 통과했다. 검사기·규범·테스트의 기존 동결 54파일은 이 보완에서 변하지 않았다.

**완료 수치는 마지막 전체 실행(3차)의 원로그를 기준으로 한다.**

| 최종 검증 | 결과 | 원로그 |
|---|---|---|
| 정상 도구를 통한 봉인 재발행 | exit 0 · draft 봉인 | [final-seal.log](evidence/final-seal.log) |
| make verify-mutation | 11종 변이 모두 검출 · exit 0 | [final-verify-mutation.log](evidence/final-verify-mutation.log) |
| make verify | 6/6 green · 247초 · exit 0 | [final-verify.log](evidence/final-verify.log) |
| 같은 실행의 pre-gate 회귀 | 38 tests OK · 54.542초 | [regen 원로그](evidence/final-verify-groups/verify-base-regen.log) |
| 같은 실행의 checker 회귀 | 49 tests OK · 15.823초 | [regen 원로그](evidence/final-verify-groups/verify-base-regen.log) |
| git diff --check | exit 0 | [final-diff-check.log](evidence/final-diff-check.log) |

전체 실행 원로그 디렉터리는 `/tmp/djr-verify.3loR6v`이며, 6개 하위 로그를 `evidence/final-verify-groups/`에 보관했다. 실행 명령은 `env -u DJR_FINDINGS_JSON PYTHONDONTWRITEBYTECODE=1` 아래의 `python3 workspace/tools/manifest_seal.py --write`, `make verify-mutation`, `make verify` 순서였고 마지막에 `git diff --check`를 실행했다. 앞선 두 번의 실패와 그 수정 근거는 `evidence/final-attempt-1/`, `evidence/final-attempt-2/` 및 gate 수정 보고서에 역사적 증거로 보존했다. 이전 실행 수치를 마지막 green 수치로 대신하지 않았다.

검증한 실행 위치는 `/Users/hyun/.cache/dddjango-field4-followup-20260911`, 기준 HEAD는 `3355710dcbaf023a16856cb2f307aa2a03fc0996`이다. [최종 봉인 파일 해시 63개](evidence/final-sealed-source-hashes.json)로 원래 작업 폴더에 옮긴 소스의 동일성을 확인한다. 원래 작업 폴더 반영과 SHA 대조를 완료했으며 primary의 diff 검사와 draft 봉인 대조도 exit 0이다. 반영 실측과 보호 파일 확인은 [transfer-verification.json](evidence/transfer-verification.json)에 기록했다. 동일한 소스를 옮긴 뒤 전체 suite를 중복 실행하는 대신 SHA 대조와 primary의 diff·봉인 검사를 수행한다.

[현재 미처리 목록](../field-report-4/2026-09-10-spring-dream-overhaul-lanes.md)에서는 완료한 12건만 제거했다. 작업 중 추가된 **F4-20(#195, 팩토리 생성 컬렉션의 반복 변수 출처 전파)은 승인 범위 밖이므로 본문을 byte 그대로 보존하며 미처리 1건으로 남긴다.** 번호는 당기지 않았고 다음 신규 번호는 F4-21이다. 제거 전 원문은 `evidence/cleanup-primary-before.md`에 보존했다.

지원 한계도 유지한다. 생성 본문 S1은 미검증이며, 동적 Python 흐름·불명 출처는 후보 또는 S5로 남는다. UoW 판정은 현재 함수의 명시 구간과 repository/aggregate 종류에 한하며 같은 타입의 개별 인스턴스나 외부 호출자의 전체 트랜잭션을 증명하지 않는다. F4-13은 규범과 수동 의미 검토의 교정이다. 실사용 Django 프로젝트, fresh 역할 압력 실험, 설치 cache 발화·strict runready 검증을 실행했다고 주장하지 않는다.

버전은 2.18.2를 유지했다. 커밋·배포 전 개발 작업 상태이며, 실행 worktree와 수정 전 스냅샷은 보존한다. `docs/master.html`은 기존 SHA `3515dcfab136b7e0bebdff32f7ac7decada1f124ab51cebd05c95028def5e360`를 유지한다.

Serena/Graphify는 opt-in 표식이 없어 사용하지 않았다. 단계별 증거의 위치와 원본 SDD 대응은 [증거 안내](evidence/README.md)에 기록했다.
