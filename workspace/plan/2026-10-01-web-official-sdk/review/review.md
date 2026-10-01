수정 후 승인

검토 대상은 `2fffcb22..d6d2878d`의 4개 커밋(W6m·SDK S1·S2/S3·S4)이다. 동결 설계 `design-sdk.md` v3.3과 `design-W5-7.md` v3 §3-4·§3-5, 구현 기록의 차이 13항을 대조했다. **발견은 major 6건·minor 1건이며 blocker·nit는 없다.** major 6건을 수정하고 해당 반례를 회귀 검사에 추가한 뒤 다시 확인해야 한다. 기본 픽스처 통과와 미러 일치만으로 승인하기는 어렵다.

검증은 `$TMPDIR`의 `git clone --shared` 사본 및 그 옆 합성 프로젝트에서 수행했다. 실제 작업 트리에서는 이 보고서만 작성했다. 아래 줄 번호는 대상 HEAD의 Claude 정본 기준이며, byte 미러인 Codex에도 같은 결함이 있다.

**1. 발견 목록**

**F1 · major · `restore`가 목록의 경로·결속을 검사하기 전에 프로젝트 밖 파일을 덮어쓴다**

- 위치: `dddjango-web/scripts/sdk_vendor.py:647`, `:661`, `:664`.
- 근거: `cmd_restore`는 `entry.file`을 `root / 'web'`에 바로 붙이고 내려받은 바이트를 쓴 다음에야 `verify_findings`를 호출한다. 목록의 파일 경로가 잘못됐거나 승인 결속이 깨졌어도 쓰기가 먼저 일어난다. 마지막에 exit 2를 반환해도 이미 덮어쓴 외부 파일은 복구되지 않는다. `target.parent` 한 단계만 확인하므로 상위 성분의 링크에 대한 사전 방어도 충분하지 않다.
- 재현: 합성 프로젝트에 정상 SDK를 설치한다 → 프로젝트의 부모 폴더에 `restore-victim.js`를 만들고 `keep me`를 쓴다 → `web/sdk_registry.json`의 `sdks.kakao_js_sdk.file`만 `../../restore-victim.js`로 바꿔 정규 JSON으로 저장한다(결속은 재계산하지 않는다) → fixture의 가짜 fetch가 원래 등재 바이트를 반환하도록 하고 `restore <프로젝트> kakao_js_sdk`를 실행한다.
- 관찰: `ⓡ1 등재 바이트 복원 — ../../restore-victim.js`가 먼저 출력됐다. 뒤이어 WV1·WV3·WV2와 exit 2가 나왔지만, 피해 파일은 SDK 바이트와 같아졌다(`outside file overwritten => True`). 변경 대상은 모두 임시 폴더 안이었다.
- 권고: 어떤 쓰기나 링크 제거보다 먼저 목록 구조, id와 파일 경로의 결합, 승인 결속, 허용된 경로 성분을 확인한다. 파손된 사본·표지만 승인 없이 복원하고, **결속이 깨진 항목은 쓰기 없이 정지**시킨다. 모든 경로 성분의 링크와 허용 디렉터리 이탈을 검사하는 반례도 넣는다. 설계 §6-8의 “결속 불일치 → 재승인 또는 승인 기록으로 되돌림”과 맞춰야 한다.

**F2 · major · 최초 채택은 gateway 경로가 없는 대리 승인 원문으로 경로까지 승인한다**

- 위치: `dddjango-web/scripts/sdk_vendor.py:463`, `:474`, `:484`; 경로 낱말 검사를 수행하는 별도 분기는 `:399`의 `--scope-add` 쪽이다.
- 근거: 최초 설치는 운영자·제품 낱말과 판/표지만 검사한다. 이후 모든 사용 단위의 `namespace_sources`에 그 출처를 그대로 넣으므로, 초안에 들어 있는 gateway 경로가 원문에 없어도 승인된다. WV3도 이 상태를 통과시킨다.
- 재현: 합성 프로젝트의 `docs/order.md`에 `카카오 SDK 2.8.3 채택 승인 2026-10-01 15:00:00 +0900` 한 줄을 커밋한다 → 해당 커밋·행을 `사용자 원문 …` 출처로 사용한다 → 정상 초안에 `Kakao.API.request:/v2/user/me`, `API.request=gateway`/`API.cleanup=lifecycle` 분류 및 유효한 `gateway_paths`를 넣는다 → fixture `install --source <그 출처> --draft <초안>`과 `sdk_vendor.py verify`를 실행한다.
- 관찰: 원문에 `/v2/user/me`가 없는데 설치 exit 0, verify exit 0이다. `API.request:/v2/user/me`의 출처가 그 원문으로 저장됐다.
- 기준 확인: 사용자에게 이 해석을 질문했고, **최초 채택에 함께 들어오는 gateway도 경로 단위 범위 넓힘이며 대리 실행에는 경로 문자열 원문이 필수**라는 답을 받았다. 근거는 설계 §6-3·§3-4④다. 따라서 최초 채택 예외로 해석하지 않았다.
- 권고: 최초 채택·기존 등록에서도 gateway 단위별 경로 문자열을 승인 원문에서 검사한다. 일반 SDK 채택의 운영자/판 검사에 이를 추가하고, 원문이 없으면 설치 전에 정지한다. `--scope-add`만 검사하는 현재 분기를 통합하거나 동일한 판정을 적용한다.

**F3 · major · 운영자 문서의 리다이렉트 최종 URL은 검증하지 않는다**

- 위치: `dddjango-web/scripts/sdk_vendor.py:208`; 비교되는 원본 최종 URL 검사는 `:194`이다.
- 근거: SDK 원본은 최종 URL의 HTTPS·도메인·CDN 여부를 확인하지만, 문서 fetch가 돌려준 `_durl`은 버린다. 결과적으로 운영자 밖 HTTP 문서도 원본 인용과 SRI 값만 맞으면 `fetched_from=network`, 운영자 문서 검증 성공으로 기록된다. 설계 §7-1②와 `discipline-web-houserules/references/final.md:245`는 **원본·문서 모두 리다이렉트 최종 주소까지 운영자 공식 HTTPS**를 요구한다.
- 재현: `sdk_fixture.run_vendor`의 fetch 표에서 SDK URL은 정상 바이트를 반환하게 둔다. 공식 `docs_url=https://developers.kakao.com/docs/en/javascript/download`의 응답만 `[http://unrelated.example/docs, text/html, 정상 원본 인용·SRI가 든 문서 바이트]`로 설정한다 → `candidate` → 생성된 후보와 정상 초안으로 `install`을 실행한다. 실제 네트워크는 사용하지 않는다.
- 관찰: candidate exit 0, install exit 0. 배너에 “무결성 운영자 문서 공개 값과 일치”, “문서 인용 확인(network)”이 표시됐다.
- 권고: 문서의 최종 URL도 쓰기 전에 HTTPS와 운영자 도메인 조건을 확인하고 그 결과를 증거에 보존한다. 원본 최종 URL 거절 사례와 별도로 문서의 HTTP 전환·외부 호스트 전환 반례를 고정한다. 이는 구현 차이 6항의 추가 방어가 문서까지 완결되지 않은 문제다.

**F4 · major · 브라우저 gateway 정규화가 운영자 밖 URL을 승인 경로로 바꾼다**

- 위치: `dddjango-web/assets/sdk_boundary.js:22`, `:24`; 정적 판정과의 비교: `dddjango-web/scripts/src/sdk_registry.py:322`.
- 근거: 스니펫은 파싱 전 원문으로 `absolute`를 판단한 뒤 `new URL()`을 쓴다. URL 파서는 선행 공백이나 역슬래시를 다르게 해석하므로 실제 외부 호스트로 파싱돼도 `absolute=false`이면 호스트 검사가 생략된다. Python과 JS가 경로·dot segment를 다루는 방식도 다르다.
- 재현: 실제 `sdk_boundary.js`를 Node `vm`의 DOM 대역에서 실행한다. 설정은 `operatorDomains=['kakao.com','kakaocdn.net']`, 승인·전체 경로 모두 `API.request: ['/v2/user/me']`, 분류는 `API.request=gateway`다. 가로챈 `Kakao.API.request({url: …})`에 아래 표의 문자열을 넣고 기록과 `findings()`를 확인한다. 같은 문자열을 Python `normalize_gateway_url`에도 넣는다.

| 실제 인자 문자열 | Python 판정 | JS 기록기 판정 |
|---|---|---|
| `/v2/user/me` | `/v2/user/me` | 같은 경로, 허용 |
| `https://kapi.kakao.com/v2/user/me/?x=1` | `/v2/user/me` | 같은 경로, 허용 |
| `/v2/user/%6De` | `/v2/user/me` | 같은 경로, 허용 |
| ` https://evil.example/v2/user/me` (선행 공백 1개) | 운영자 밖 절대 주소로 거절 | `/v2/user/me`, `pathOk=true`, `pathKnown=true` |
| `\\evil.example/v2/user/me` (선행 역슬래시 2개) | `/`로 시작하지 않아 거절 | `/v2/user/me`, `pathOk=true`, `pathKnown=true` |
| `v2/user/me` | `/`로 시작하지 않아 거절 | `/v2/user/me`, 허용 |
| `/v2/user/../user/me` | dot segment를 남김 | `/v2/user/me`로 접어서 허용 |

- 관찰: 위 호출들을 기록한 뒤 `findings()`는 빈 배열이었다. 원래 SDK 함수는 호출되지 않게 한 시험이므로 **실제 외부 발송을 관찰한 것은 아니다**. 문제는 G2 호출 인자 검사에서 잘못된 호스트를 정상 승인 경로로 보고하는 것이다.
- 권고: 원문 정규식에 의존하지 않고 파싱된 URL의 호스트·프로토콜을 확인한다. 상대 경로의 허용 범위, 공백·역슬래시·dot segment·퍼센트 인코딩 처리 규칙을 양 구현에서 맞추고 같은 입력 표로 검증한다. 설계 §16②의 “같은 정규형”이 아직 성립하지 않는다.

**F5 · major · WV8의 문서 별칭·괄호 및 template-key 호출 우회가 남아 있다**

- 위치: `dddjango-web/scripts/src/check_vendor.py:290`, `:337`, `:345`.
- 근거: 문서 별칭은 괄호 없는 직접 우변에서 한 번만 추출하고, 호출 수신자 뒤의 괄호를 처리하지 않는다. `createElement` 문자열 검사는 backtick 리터럴을 명시적으로 제외한다. §16⑤의 고정 8꼴은 통과하지만, 바로 옆의 같은 의미인 표기에서는 덫이 사라진다.
- 재현: 정상 합성 프로젝트의 새 파일 `web/static/js/review_probe.js`에 아래 코드를 한 가지씩 쓰고 `python dddjango-web/scripts/backstop.py <프로젝트> --diff-base HEAD --only wv8`을 실행한다. `payload`·`tag`에는 외부 주소 리터럴을 넣지 않아 별도 URL 덫과 분리했다.

| JS | 실제 결과 |
|---|---|
| `const d = f.contentDocument; d.write(payload);` | exit 2, WV8 1건 — 대조군 |
| `const d = (f.contentDocument); d.write(payload);` | exit 0 |
| `(document).write(payload);` | exit 0 |
| `const d = document; const alias = d; alias.write(payload);` | exit 0 |
| `const d = f["contentDocument"]; d.write(payload);` | exit 0 |
| ``document[`createElement`](tag);`` | exit 0 |
| ``f[`srcdoc`] = html;`` | exit 2 — srcdoc의 template-key 대조군은 잡힘 |

- 영향: 앞의 문서 쓰기 표기는 여전히 같은 주입 싱크다. 설계 §16⑤는 parser script가 R5 실행 확인에도 보이지 않는 경로라 정적 덫이 맡는다고 명시한다. 일반적인 정적 분석의 한계만으로 이 짧은 표기 차이를 넘기기는 어렵다.
- 권고: 문서 수신자의 괄호·대괄호 접근·지역 별칭 전파를 처리하고, 보간 없는 template-key도 함수 이름 토큰으로 검사한다. 기존 8개 표본 외에 위 반례와 `logger.write` 같은 정상 대조군을 함께 추가한다.

**F6 · major · 미등재 vendor 단위가 디렉터리 심볼릭 링크만 가지면 WV13에서 사라진다**

- 위치: `dddjango-web/scripts/src/check_vendor.py:426`, `:444`.
- 근거: `unit_files()`는 `os.walk()`의 `names`만 모은다. 하위 디렉터리 심볼릭 링크는 `dirs`에 들어가지만 따라가지도, 자체를 수집하지도 않는다. 따라서 이런 링크만 가진 미등재 단위는 빈 단위로 보아 시대 판정에 넘기지 않는다. 등재 id 디렉터리의 WV5 링크 검사와 달리 미등재 단위에는 빈틈이 있다.
- 재현: 정상 SDK를 설치·커밋해 목록 시대를 만든다 → 임시 외부 폴더에 `other.js`를 둔다 → `web/static/vendor/new_sdk/nested`를 그 폴더로 향하는 디렉터리 심볼릭 링크로 만들고 커밋한다 → `sdk_vendor.py verify` 및 `backstop.py <프로젝트> --diff-base HEAD --only wv`를 실행한다. 같은 `new_sdk` 안에 같은 바이트를 일반 파일 `regular.js`로 놓은 경우도 대조한다.
- 관찰: 링크만 있을 때 verify·gated 모두 exit 0. 일반 파일을 두면 WV13 1건·exit 2다. 시대가 생긴 뒤 추가된 vendor 내용을 링크 형태만으로 전체 검사의 입력에서 제외할 수 있다. 실제 정적 서버가 그 링크를 제공하는지는 별도로 실행하지 않았다.
- 권고: 디렉터리 링크를 빈 폴더로 취급하지 말고 미등재 단위의 내용으로 수집해 판정하거나 명시적으로 거절한다. 링크를 무작정 따라가는 방식은 순환·루트 이탈이 있으므로 피한다. 중첩 디렉터리 링크를 포함한 WV12/WV13·빚 스캔 반례를 추가한다.

**F7 · minor · K51 픽스처가 설계의 단락·한 번 걸음 회귀를 고정하지 못한다**

- 위치: `dddjango-web/scripts/test/fixtures_sdk.sh:789`, `:792`, `:795`; 구현은 `dddjango-web/scripts/src/check_vendor.py:463`.
- 근거: 설계 K51은 목록 이력 없음/있음에 대해 각각 이력 걸음 0/1과 1초 미만을 요구한다. 현재 픽스처는 첫 경우에만 20초 상한을 검사하며, 두 경우 모두 이력 걸음 수를 단언하지 않는다. 이전 8~11초 수준의 성능으로 돌아가도 이 검사는 green일 수 있다. 구현 기록도 “단락 제거” 변이를 생략했다고 밝힌다.
- 독립 확인: `_git` 호출을 기록하며 200파일로 `classify_units()`를 측정했다. 단위 없음은 git 0회, 목록 이력 없음은 0.053초·raw 이력 걸음 0회(git 전체 3회), 목록 이력 있음은 0.156초·raw 이력 걸음 1회(git 전체 8회)다. **현재 구현이 느리다는 발견은 아니다.** 단락과 한 번 걸음은 실제로 작동한다.
- 권고: 시간만으로 변이를 구분하기 어렵다면 이력 전체 조회 호출 수 0/1을 고정하고, 두 경우에 모두 현실적인 시간 상한을 둔다. 단락 제거 변이도 호출 수 변화로 검출할 수 있다. 차이 12항은 이 이유로 재검토 필요다.

**2. §16 구현 단계 메모 ①~⑥ 대조**

| 항목 | 판정 | 코드·픽스처 근거 |
|---|---|---|
| ① 모든 이름공간의 lifecycle 통과 | 처리됨 | `assets/sdk_boundary.js:75`~`:85`에서 분류표의 lifecycle과 표 밖의 수명 이름을 원본 그대로 둔다. 제공된 `browser/rehearse.js`·`rehearse-all.out`의 R6 `API.cleanup 통과`/표 밖 cleanup 사례를 확인했다. 독립 Node 실행에서도 실제 cleanup 카운터 1·`pass:API.cleanup`을 확인했다. |
| ② WV9·기록기의 gateway 정규형 일치 | 부분 | `src/sdk_registry.py:322`, `assets/sdk_boundary.js:19`. `fixtures_sdk.sh:622`~`:628`의 K52b-4/5/6/7 및 제공 R6의 보통 절대 주소·쿼리·끝 `/`·퍼센트 짝은 충족한다. 공백·역슬래시·상대 주소·dot segment 반례에서는 일치하지 않는다(F4). |
| ③ 판 올림 경로표 재추출·사라진/새 경로 표시 | 처리됨 | `sdk_vendor.py:443`~`:456`에서 새 api-paths와 비교하고 거절보다 먼저 diff를 출력한다. `fixtures_sdk.sh:667`의 “③ 판 올림 dry-run — 사라진 경로 1·새 경로 1”, `:669`의 “③ 옛 경로표 초안 — 거절 2(diff 먼저)”를 재실행해 통과했다. |
| ④ 대리 실행의 경로 원문 안내 | 부분 — 문안은 처리됨 | `REQUEST_GUIDE.md:268`~`:269`에 요구 문구가 있고 Codex와 byte 동일하다. 실제 최초 채택 도구는 원문 경로가 없어도 통과하므로 안내대로 정지하지 않는다(F2). 사용자가 최초 채택에도 적용한다고 확인했다. |
| ⑤ WV8 토큰 규칙·우회 8꼴 | 부분 | `src/check_vendor.py:315`~`:357`, `test/sdk_fixture.py:283`~`:291`. 지정한 8꼴과 기존 표본은 `fixtures_sdk.sh:538`에서 통과한다. 추가한 괄호·별칭·template-key 반례는 놓친다(F5). spring_dream 전수 결과는 구현자 기록에 있으며 이번 리뷰에서 재실행하지 않았다. |
| ⑥ K50e 옛 판 임시 사본의 merge 복귀·출구 | 처리됨 | `fixtures_sdk.sh:732`에서 WV13, `:735`에서 치환 정리 후 0을 재확인했다. `commands/dddjango-web.md:278`와 Codex 대응 문단에 coder의 로드 줄 치환·Coordinator의 임시 사본 삭제 격리 커밋·G0 뒤 정지/다음 레인 안내가 있다. |

**3. 구현자가 적은 설계 차이 13항**

| # | 차이 | 판정 | 이유 |
|---|---|---|---|
| 1 | W6m touched 기준을 `pre_run_head`, 없으면 `git_snapshot`으로 맞춤 | 정당 | W4 `static_delta.py:575`의 기준 선택과 `:404`의 손댄 파일 계산을 따른다. 첫 부모 비병합·미커밋, main 이력 안 병합의 `--cc`, 이력 밖 병합 전체 유입이라는 의미도 같다. |
| 2 | WN8에서 vendor `.gitattributes` 예외 | 정당 | 도구가 쓰는 고정 표지에 기능 파일 이름 규칙을 적용하면 정상 설치가 red가 된다. 표지 바이트·git 속성 검사는 WV2/WV5가 맡는다. |
| 3 | 빚 참조 pathspec에서 목록 JSON도 제외 | 정당 | 목록은 설치 도구 소유이고 기능 컨테이너의 치환 대상이 아니다. `web/static/vendor`와 `web/sdk_registry.json`의 제외를 Coordinator·refactor_audit 양쪽에 맞췄다. vendor 전용 R0 경로와 관련 픽스처도 통과했다. |
| 4 | WV2를 id당 한 건으로 묶고, index blob 대신 필터 적용 저장 바이트를 비교 | 정당 | 판 올림 직후 index에 옛 판이 남아 있다는 이유로 새 정상 사본을 거절하는 문제를 피한다. 필터 적용 해시와 원본 blob의 비교, mode·속성 검사 및 gated WV10의 미커밋 금지가 함께 유지된다. index 자체의 동일성 검사로 설명해서는 안 되지만, 기록에 이 차이가 명시돼 있다. |
| 5 | 출처 거절 exit 1·동일 설치 멱등·upgrade diff 선출력 | 정당 | 잘못된 CLI 승인 입력의 exit 1과 이미 완료된 설치의 exit 0은 도구 계약상 구별 가능하다. 경로 diff 선출력은 §16③을 만족한다. F2는 종료 코드 선택과 별개의 승인 내용 누락이다. |
| 6 | candidate의 최종 URL 등록 가능 도메인 검사 추가 | 정당 | 원본 리다이렉트에 추가 경계를 두는 방향은 타당하다. 다만 문서 최종 URL 검사는 빠졌다(F3). 이 항목을 원본·문서 전체의 리다이렉트 검증 완료 근거로 사용할 수 없다. |
| 7 | 마지막 remove 뒤 미등재 내용이 있는 vendor 폴더는 보존 | 정당 | 마지막 등재 항목 제거가 별도 미등재 사본까지 지울 권한은 아니다. 빈 폴더만 제거하고 나머지는 WV12/WV13의 대상으로 남기는 것이 범위에 맞는다. |
| 8 | srcdoc 문자열 정상 짝을 발견으로 변경 | 정당 | §16⑤가 식별자·문자열 모두를 잡는 보수적 토큰 규칙으로 명시했다. 이전 K46c의 기대값보다 최종 메모가 우선한다. |
| 9 | G2 SDK 행을 ③″로 표기 | 정당 | 기존 정적 검사 행 ③′와 구분한다. 검사 내용·필수 보고는 줄이지 않았다. |
| 10 | 리팩토링 공개 설정 확인을 plan/install에 배치하고 R+를 픽스처로 고정 | 정당 | plan에서 배선 부족을 드러내고 `sdk_vendor.py:457`의 G1(리팩토링) 설치 경로도 거절한다. `fixtures_refactor_audit.sh` S1~S6가 해당 외부 동작을 다루며 전체 201개 검사가 통과했다. self-test에만 들어 있어야 할 이유는 없다. |
| 11 | 감사 렌즈에 HR §9·IJ §8 추가, 절 수 62→64 | 정당 | 새 SDK 규범 절을 감사 입력에서 빠뜨리지 않기 위한 변경이다. 양 플랫폼 self-test가 모두 점검 절 64·red 0이다. |
| 12 | “단락 제거” 변이를 측정하지 않음 | 재검토 필요 | 한 번 걸음 구현이어도 단락 제거는 조회 호출 수로 구분할 수 있다. 현재 K51은 20초 상한과 결과 분류만 보므로 설계의 회귀 검출 계약을 충족하지 못한다(F7). |
| 13 | K21a·K21c·K27·NAVER fixture 모양 변경 | 정당 | attrs의 index 상태, CRLF 원본 입력, 도메인 라벨 거절 기대값, 완전한 함수 분류표를 맞춘 시험 장치 변경이다. 관련 부정/정상 대조군이 통과하며 요구 판정을 없앤 변경으로 보이지 않는다. |

**4. 설계 정합·보안·회귀의 나머지 확인**

§3~§7의 목록·승인 결속·사본 설치 자리·로드·빚 처분·역할 소유는 대체로 구현돼 있다. WV1~WV13은 `backstop.py:50`의 `TOTAL_CHECKS=39`(WS8+WI4+WN8+WP6+WV13)에 반영됐고, usage의 `wv`/개별 id 선택, verify·debt·gated 경로도 들어 있다. 기존 26종에서 13종을 더한 값이다.

SDK가 없는 프로젝트에서는 기존 WS/WP 검사와 빚·refactor 흐름을 유지하면서, 설계가 의도한 WV8 외부 코드 덫 및 새 WP3 주소 규칙은 적용한다. “SDK 없음”을 새 검사의 전면 비활성으로 해석하지 않았다. 기존 `fixtures_backstop`, `fixtures_ui_javascript`, `fixtures_debt`, `fixtures_refactor_audit`, `fixtures_subst`, `fixtures_static_delta`를 포함한 전 묶음에서 추가 회귀는 관찰하지 못했다. 다만 green이라는 사실이 F1~F6의 누락을 해소하지는 않는다.

운영자 호스트·팝업 차단은 스니펫 단독 책임으로 오해하지 않았다. Coordinator의 G2 문안은 컨텍스트 요청 차단(팝업 포함), 운영자 `window.open`·폼의 기록 전용 래퍼, 시작 스택 귀속, case별 라우트 해제·새로고침을 요구한다. 양 플랫폼 의미도 같다. 실제 asset의 독립 Node 시험에서 운영자 open 1·폼 2는 기록됐고 원본 open/submit 호출은 각각 0이었다. 브라우저 컨텍스트 네트워크 차단 자체와 CDP 귀속은 제공된 실제 Chromium 리허설 코드·17개 PASS 로그를 검토했으며, 이번 리뷰에서 브라우저를 다시 실행한 결과로 주장하지 않는다.

얕은 이력은 두 계약을 구분했다. 미등재 단위의 목록 시대 판정은 `classify_units`가 exit 1로 정지하고 K51c가 통과한다. 승인 출처의 조상 판정은 설계 §5-2 **WV3가 명시적으로 notice를 허용**한다. 독립 시험에서도 다른 가지 원문이 얕은 이력에서는 notice·exit 0, 같은 객체의 전체 이력에서는 WV3·exit 2가 됐다. 이는 승인 출처 증명의 제한이지만 동결 설계에 따른 동작이므로 별도 구현 결함으로 세지 않았다. `.gitattributes` 삭제 뒤 verify가 0인 시험도 WV5의 “있으면 고정 바이트”와 WV2의 unspecified 허용 조건에 맞아 결함에서 제외했다.

**5. 미러 결과**

| 범위 | 독립 cmp 결과 |
|---|---|
| `dddjango-web/scripts/**` ↔ `codex-dddjango-web/skills/dddjango-web/scripts/**` | 53쌍, 불일치 0 |
| `dddjango-web/assets/**` ↔ Codex 대응 assets | 3쌍, 불일치 0 |
| 모든 배포 `skills/*/references/*` ↔ Codex 대응 references | 8쌍, 불일치 0 |
| `REQUEST_GUIDE.md` | 1쌍, 불일치 0 |
| 합계 | **65쌍, 불일치 0** (`__pycache__` 제외) |

역할 4쌍의 변경 문단과 변경된 라우팅 SKILL 4쌍도 대조했다. Coordinator/코디네이터 등 플랫폼 표현을 정규화하면 추가 문단은 같다. Coordinator의 변경 31개 추가 줄도 대응 비교했다. `${CLAUDE_PLUGIN_ROOT}`/`${SKILL_DIR}`, Bash/네이티브 셸, 역할 호출/`spawn_agent`, 리팩토링 입구 표기, Playwright/CDP 접근 방식의 차이는 런타임 치환이며 SDK 승인·격리·실패·검증 의무의 의미 누락은 발견하지 못했다.

`Makefile:103`에는 W6m touched 문단과 SDK 채택 G1 문단 표지가 있고, `:104`~`:105`에는 감사자 두 줄의 존재 가드 및 대조가 있다. `:115`의 implementation-javascript reference cmp, `:117`의 가이드 cmp도 실행돼 통과했다. W6m 설계가 이번 범위 밖이라고 명시한 기존 Coordinator 루프의 빈 결과 존재 가드는 새 발견으로 올리지 않았다.

**6. W6m 대조**

| 문면 쌍 | 결과 |
|---|---|
| Phase 2 step 4 첫 문장 — Claude `commands/dddjango-web.md:234` / Codex `skills/dddjango-web/SKILL.md:257` | 수정 모드도 G2 직전 1회+슬라이스 3개 이상이면 슬라이스별 경량이라는 리듬을 유지한다. |
| 수정 모드 4 — Claude `:258` / Codex `:281` | 머리 문구를 보존하고, 경량은 범위 제한이라는 뜻·홀리스틱 깊이 유지·3-1 뒤 최종 감사·범위 밖 의존 추적·누락 보고를 모두 명시한다. |
| 감사자 감사 빈도 — Claude `agents/discipline-reviewer-web.md:63` / Codex 역할 SKILL 대응 줄 | 최종 감사의 touched 제한과 슬라이스별 감사 추가가 양립한다. |
| 감사자 점검 1 — Claude `:67` / Codex 역할 SKILL 대응 줄 | 수정 모드의 최종 1회에서도 행위↔코드를 대조하며, 행위 추적은 감사 범위 밖 파일도 따라간다. |

`b707c531`은 이 문면 4쌍과 Makefile만 바꿨다. W4 도구를 변경하지 않았고, 기존 리팩토링 감사 구조·④ 치환 판정의 `approved-merges.txt` 의미론도 바꾸지 않았다. touched 정의는 W4 `touched_files()`의 첫 부모 사슬·미커밋·병합 구분과 일치한다. 범위 기준을 `pre_run_head` 우선으로 맞춘 차이 1항도 타당하다. W6m 자체에서 반송할 발견은 없다.

**7. 검증 결과와 재현 자료**

| 실행 | 결과 |
|---|---|
| 임시 공유 클론의 `make verify-web` | **exit 0**. 픽스처 파일 19개, 실패 0개. SDK 183·debt 97·refactor_audit 201·static_delta 65·subst 131·UI JavaScript 17 등 통과. |
| Claude/Codex `refactor_audit --self-test` | 각각 점검 절 64·어구 32·극성 표본 18·red 0. |
| 임시 공유 클론의 `make verify VENV_PY=<기존 venv python>` | **exit 2**. ontology·base-backstop·base-regen·base-cross green. base-core만 manifest의 `Makefile` 봉인 후 변경·`tree_sha256` 드리프트로 red. 356초. 봉인은 재발행하지 않았다. |
| 독립 반례 묶음 `probes.py` | F1·F2·F3·F5·F6 재현, 정상 대조군 확인. 가짜 fetch만 사용. |
| 실제 `sdk_boundary.js`의 Node VM 시험 | F4 재현. lifecycle 원본 통과·운영자 open/폼 기록 전용 동작도 확인. DOM 대역을 사용했으며 실제 브라우저 재실행은 아니다. |
| K51 독립 호출 수·시간 측정 | 단락 및 raw 이력 걸음 0/1 확인. 200파일 두 경우 모두 1초 미만. F7은 영구 회귀 검사의 부족이다. |
| 현재 워크트리의 tracked/index diff | 보고서 작성 전 모두 0. 원래 있던 `.venv`와 review 입력 파일은 보존했다. 커밋·push 없음. |

실행 사본·로그는 `/private/var/folders/50/f629pvj96jl1n3rrw444hz9h0000gn/T/web-sdk-review.Jk1VlJ/`에 있다. `repo/`가 공유 클론이고 `verify-web.log`, `verify.log`, `probes.py`, `probes.out`, `boundary-probes.cjs`, `boundary-probes.out`가 근거다. F1~F6은 보고서의 절차대로 fixture를 사용해 새 임시 프로젝트에서 재현할 수 있다. 개별 커밋 4개를 각각 checkout해 전체 검증을 반복한 것은 아니며, 대상 최종 HEAD에서 전체 검증을 수행했다. 구현자의 변이 35종·브라우저 17/17·spring_dream 전수 결과는 제공된 기록과 구분했고, 이번 리뷰의 독립 재실행으로 합산하지 않았다.

Serena·Graphify는 리뷰 지시서의 금지에 따라 사용하지 않았다. 네트워크를 사용하지 않았고, main 및 지정된 외부 작업 폴더에는 쓰기나 `git status`를 수행하지 않았다.

REPORT-DONE
