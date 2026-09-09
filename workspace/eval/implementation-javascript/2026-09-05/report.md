# implementation-javascript 완료 평가

2026-09-05. **신규 스킬 작성·검증 완료. 플러그인의 JS 허용 전환·agent 주입·백스톱 수정·배포는 미실행.**

## 산출물과 범위

- Claude: `dddjango-web/skills/implementation-javascript/{SKILL.md,references/final.md}`.
- Codex: 같은 skill 경로의 미러. SKILL의 Claude 전용 `user-invocable: false`만 제외하며 본문은 동일하다. reference는 byte 동일하다.
- source: `workspace/reference/implementation-javascript/reference/`의 research.md·review.md·final.md. final은 배포 reference의 byte 미러다.
- 이번 작업 전부터 있던 master·파일트리·웹 동작 흐름 문서와 이슈 보고서는 보존했다.

## 평가 방법

[사전 기준](preregistration.md)을 스킬 집필 전에 기록했다. 스킬을 읽지 않은 fresh baseline 구현자와 새 스킬을 읽은 fresh 구현자는 같은 [brief](brief.md)와 DOM 계약을 받았다. 서로의 소스·평가 기준·결과는 제공하지 않았다. 두 구현 모두 파일 하나, 외부 defer 1회 로드다. 별도의 fresh 적용자는 복사 안내와 범위 판단을 수행했다. 실제 코드·구현자 보고는 `baseline/`, `with-skill/`, `holdout/`에 보존했다.

기준선 B1–B9의 결과를 확인한 뒤, 스킬 집필 전 탐색 E1을 추가해 실패를 관찰했다. **E1은 사전 등록 비교 점수에 합치지 않는다.** 그 발견을 일반적인 정리 범위 지침으로 반영한 뒤 적용군을 평가했다. E1 재통과는 해당 지침의 작동 확인이며 독립 일반화 증거가 아니다.

실행은 `/tmp/dddjango-ui-js-20260905`의 격리 환경과 loopback 서버에서만 했다. 시스템/프로젝트 의존성이나 사용자 Chrome 프로필을 변경하지 않았다. 평가 코드 사본은 이 폴더에 보존한다.

| 환경 | 실행 값 |
|---|---|
| Python / Django | 3.14.7 / 5.2.17 |
| 브라우저 | headless Google Chrome 152.0.7977.82, 임시 프로필 |
| 자동화 | Playwright Python 1.62.0 |
| HTMX | 2.0.8; 실제 HTTP 응답으로 HTML 교체 |
| vendor 근거 | [HTMX 2.0.8 공식 배포 파일](https://raw.githubusercontent.com/bigskysoftware/htmx/v2.0.8/dist/htmx.min.js) |
| vendor SHA-256 | `22283ef68cb7545914f0a88a1bdedc7256a703d1d580c1d255217d0a50d31313` |

## 결과

| 검사 | 기준선/수정 전 | 스킬 적용/수정 후 | 근거 |
|---|---|---|---|
| B1–B9 파일 미리보기 | 9개 그룹 모두 통과 | 9개 그룹 모두 통과 | baseline-result.json, with-skill-result.json; B6는 outer/parent/delete로 나눠 관찰 |
| E1 독립 자식만 삭제 | 파일은 남지만 이미지·파일명 소실 | 파일·이미지·파일명 유지 | baseline-explore.json, with-skill-explore.json |
| C1–C9 별도 복사 UI | 미평가 | 9개 그룹 모두 통과 | holdout-result.json; pending/success 별도 관찰 |
| P1–P6 reference 비밀번호 예제 | P5 버튼 활성화, P6 input 상태 동기화 실패 | 6개 모두 통과 | example-before.json, example-after.json |
| 브라우저 pageerror | 없음 | 없음 | 각 실행 결과의 errors 배열 |

B 검사는 실제 이미지 decode·파일명 문자 출력·clear·인스턴스 격리·반복 load·실제 HTMX 교체·blob URL 해제를 확인했다. URL 계측은 브라우저 원본 API를 호출하며 생성/해제만 기록했다. B3의 수동 load 반복을 실제 swap 증거로 사용하지 않았다. baseline이 기본 검사를 이미 통과했으므로 “스킬이 있어야 기본 UI를 구현할 수 있다”거나 “전체 성공률이 개선됐다”고 결론내리지 않는다.

C 검사는 실제 DOM·실제 HTMX HTTP 교체와 **제어된 Clipboard Promise**를 조합했다. 완료 전 성공 문구 부재, 성공/실패, 뒤 작업의 결과 유지, 여러 UI 격리, root/input/output 교체, 독립 자식 보존, API 미지원, Enter 키 경로를 확인했다. 실제 OS 클립보드 쓰기나 브라우저 권한 승인을 검증한 것은 아니다.

추가 범위 판단 3건은 모두 기대와 일치했다: native details/summary로 충분하면 JS 파일 없음; 할인/관리자 판정은 서버 소유; 기존 금지가 있으면 새 스킬을 이유로 우회하지 않음. `holdout/report.md`에 적용자의 원문을 보존했다.

## 검토·수정·구조 검증

독립 검토자는 예제의 내부 교체 오류 1건을 발견했다. 브라우저에서 두 증상을 재현한 후 `activate`가 새 노드의 소유 root까지 수집하도록 수정했다. 같은 브라우저 검사와 제한된 독립 재검토를 통과했다. 나머지 코드·참고 자료가 구현 과제의 특정 selector나 파일 이름에 의존하도록 만들지 않았다. 수정된 예제는 비교 과제와 다른 기능이며 이 수정 후 비교 구현자를 다시 지시하지 않았다.

- Codex `quick_validate.py`: PASS. Claude 전용 YAML 키는 Codex 검사기에 넣지 않고 기존 Claude 형식과 매니페스트 검증으로 확인했다.
- Claude/Codex SKILL 플랫폼 차이·reference·workspace final 미러: `structure-result.json`에 결과 및 hash 기록.
- 문서 JS 예제와 독립 구현 3개: `node --check` PASS.
- `claude plugin validate dddjango-web --strict`: 종료 코드 0, validation passed.
- `make verify-web`: 종료 코드 0, 픽스처 파일 7개 실패 0개, scripts/assets/REQUEST_GUIDE 미러 및 요청 가이드 계약 통과. 기존 fixtures_backstop.sh:450의 `printf: --: invalid option` 출력 경고는 있었다. 검증 요약은 PASS=62 FAIL=0이며 해당 기존 스크립트는 수정하지 않았다.
- 커밋·릴리즈가 없고 backend/ontology는 변경하지 않아 전체 `make verify`는 실행하지 않았다.

초기 브라우저 실행은 샌드박스에서 SIGABRT로 끝나 임시 Chrome 검사 명령만 승인 검토를 거쳐 재실행했다. 초기 평가 서버에서 `/tmp` 심볼릭 경로 판정으로 static 404가 발생해 평가 harness 경로를 resolve하도록 수정했다. 이 두 환경 실패를 UI 구현 실패로 채점하지 않았다.

## 재현과 한계

저장된 server.py·check.py·explore.py·check_holdout.py·check_example.py·instrument.js와 구현 폴더들을 새 임시 폴더에 복사하고, 위 버전의 HTMX를 내려받아 hash를 확인한다. 동일 Python 패키지의 격리 환경에서 `python server.py`로 loopback 8771을 열고 다음을 각각 실행할 수 있다. Chrome 경로는 macOS 평가 환경 값이다.

```sh
python check.py baseline
python check.py with-skill
python explore.py baseline
python explore.py with-skill
python check_holdout.py
python check_example.py after
```

password.html·password_visibility.js는 **수정 후 reference 예제**의 추출 사본이다. `example-before.json`은 수정 전 실행 기록이며 현재 사본으로 과거 실패를 재현했다고 주장하지 않는다. 각 검사 스크립트는 관찰값을 JSON으로 남기므로 exit code만 보지 말고 모든 `pass` 값을 확인해야 한다. 이 harness는 제품의 영구 테스트 인프라로 설치하지 않는다.

한 모델 계열·제한된 독립 과제·한 브라우저·한 HTMX 버전의 평가다. Safari/Firefox, 실제 OS Clipboard, history/hx-preserve 확장 경로, 보조기술 전체 검증, 실제 dddjango-web 파이프라인과 기존 앱 적용은 이번 실행 증거에 포함하지 않는다. 해당 기능을 실제 사용하는 단계에서 그 조건을 검증해야 한다. 스킬 완성과 런타임 전환 완료는 별개다.

Serena: skipped — opt-in 표식이 없고 신규 스킬 문서 및 격리 UI 평가 범위여서 기본 도구를 사용했다.
