# 재동결·재개 판정 검증 기록

현재 단계: 정본 3개·Codex 미러 3개 수정, 계획·구현 독립 적대 리뷰와 필수 검증을 완료했다. 이 기록은 구현·검증 단계의 결과다. 이후 사용자가 플러그인 배포를 별도로 승인했으며, 해당 실행은 계획의 후속 배포 절과 실제 릴리즈 태그로 확인한다. A8 앱 코드는 변경하지 않았다.

## 시작 상태

- 기준 commit: `382837c97c3dc3722d4e30368d879dd622e12dc2` (dddjango-web 1.1.11)
- 격리 경로: `/Users/hyun/.cache/dddjango-web-resume-20260913`
- primary 기존 변경 보존 SHA-256:
  - `docs/master.html`: `3515dcfab136b7e0bebdff32f7ac7decada1f124ab51cebd05c95028def5e360`
  - `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md`: `d36d7794b489353ca5b891b9ebcf2145f03ff6a753bcf8bc9cef6dd42a93096a`

## 실제 실패 기준선

원본 실행은 Claude A8 세션 `54754273-a334-4a58-bdd0-88a043c4010c.jsonl`이다. 관련 구간은 4470–4550행이다. 수집한 화면 HTML 한 개가 기존 파일과 같다는 사실에서 현재 구현도 정확히 반영한다는 결론으로 넘어갔다. 해당 구간의 실제 도구는 DesignSync 프로젝트/목록/화면 한 개 취득, 로컬 화면 Read·hash, 질문이다. 새 브라우저·역할 호출·Skill·현행 가이드 재독은 관찰되지 않는다. 이는 실제 실패지만 새 지침 전체 파이프라인을 다시 실행한 실패로 간주하지 않는다. 원문 로그에는 업무 맥락이 있으므로 저장소에 복사하지 않는다.

고정 행동 입력은 `scenarios.md`, 사전 합격 기준은 `../../plan/2026-09-13-web-refreeze-resume.md`의 시험 표에 둔다. 행동 시험은 독립 문맥의 판정 시험이며 실제 브라우저·A8 수정·전체 native 파이프라인 성공 증거가 아니다. 원본 해시 동일의 정확성은 별도 진단에서 두 실행자가 직접 검산했다.

## 최종 결과

- 계획 적대 리뷰: Critical 0 / Important 0 / Nit 2, 두 nit 반영. `plan-review.md`.
- 구현 적대 리뷰: runtime Spec·Quality PASS, Critical 0 / Important 0. 평가 README의 오래된 진행 상태 Nit 1은 이 갱신으로 정정했다. `implementation-review.md`.
- `make verify`: **6/6, exit 0, 279초**. `verification/final-verify.log`와 6개 그룹 원문 로그.
- 요청 가이드 self-test **157/157**, 실제 설치·발견·미러 계약 PASS, strict plugin validation PASS. 명령별 결과는 `verification/commands.json`.
- 수정 전/후 각각 1턴 판단 응답에서 핵심 기준 5개를 충족했다. 원문은 `baseline/`·`candidate/`, 판정은 `results.md`다. 기존판도 통과했으므로 성공률 개선이나 실제 실패의 RED→GREEN 재현을 주장하지 않는다.
- 주 모델은 양쪽 `claude-fable-5-1`로, 실제 A8 당시 모델과 다르다. 지침 본문을 직접 제공하고 도구를 비활성화한 시험이다. 실제 자동 적재·재개 도구 호출·역할 인계·브라우저·A8 앱 수정·Mac Chrome 메뉴 좌표 해결은 미검증이다.
- 일반 대화를 플러그인 본문만으로 통제할 수 없으므로 업데이트 후 기존 작업도 명시적으로 플러그인을 호출하는 가이드를 추가했다.

`candidate-hashes.json`은 독립 리뷰·필수 검증을 받은 runtime 파일을 식별한다. primary 반영 당시의 실측 결과는 `transfer.json`에 기록했다. 그 파일의 커밋·배포 false 값은 반영 당시의 상태다.

후속 배포의 커밋 직전 primary 전체 검증도 6/6·exit 0·261초로 통과했다. 원문은 `verification/release-precommit/verify.log`와 그룹별 로그다. 구현 단계의 279초 기록과 구분한다.
