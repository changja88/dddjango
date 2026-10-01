# 구현 기록 — web 2차분 W6m · 공식 SDK 개방(design-sdk v3.3) (2026-10-01)

- 워크트리 `.claude/worktrees/agent-a98990edf7b131c66` · 가지 `worktree-agent-a98990edf7b131c66` · 기준 main `2fffcb22`
- 입력 설계: `workspace/plan/2026-09-30-speed-improvement/design-W5-7.md` v3 §3-4·§3-5·§6 · `workspace/plan/2026-10-01-web-official-sdk/design-sdk.md` v3.3(동결) §11-1·§11-2·§6-10·§16
- 이 파일은 커밋하지 않는다(untracked).

## 커밋

| 해시 | 묶음 | 단독 검증(scratch 공유 클론에서 그 커밋만) |
|---|---|---|
| `b707c531` | W6m — 문면 4쌍 + Makefile 표지·감사자 2줄 대조 | `make verify-web` 0 · `make verify` 5/5(임시 봉인 — 봉인 chore 는 만들지 않음) |
| `4934e5be` | S1 검사기·도구 — WV 13종 · sdk_vendor.py · sdk_boundary.js · 픽스처 · Codex byte 미러 · Coordinator grep pathspec 2곳 | `make verify-web` 0(픽스처 19 파일 실패 0 · self-test red 0) |
| `ef3cf78a` | S2 규범 + S3 역할 · refactor_audit 렌즈 절 · Makefile IJ cmp | `make verify-web` 0 · `make verify` 5/5(임시 봉인) |
| `d6d2878d` | S4 Coordinator(A1~A26)·REQUEST_GUIDE·Makefile 문단 표지·AGENTS.md·docs | `make verify-web` 0 · `make verify` 5/5(임시 봉인) · `claude plugin validate dddjango-web --strict` 통과 |

봉인: Makefile 이 W6m·S2·S4 에서 바뀌었다 → 착지 때 `manifest_seal.py --write` 봉인 chore 가 필요하다(운영자 몫).

## W6m 문면(전 → 후)

1. Phase 2 step 4 첫 문장(CL·CX) — 전: «기본 G2 직전 홀리스틱 1회 + 슬라이스 **3개 이상**이면 슬라이스별 경량» / 후: 같은 문장 뒤에 «(수정 모드도 이 리듬이다 — «수정 모드» 4 는 G2 직전 1회의 범위를 정한다)».
2. 수정 모드 4(CL·CX · Makefile 대조 표지 추가) — 머리 «4. **discipline 감사 = touched 파일 한정 경량 1회**(…경량으로 충분).» 그대로 + 덧붙임(설계 문안 그대로 · touched 정의만 W4 와 맞춤 — 아래 «설계와 다른 점» 1).
3. 감사자 «감사 빈도»(RL·RX) — 전: «수정 모드에서는 touched 범위 한정 경량 1회다.» / 후: «수정 모드에서는 G2 직전 1회의 범위가 touched 로 한정되고, 슬라이스가 3개 이상이면 슬라이스별 경량 감사도 기본 리듬 그대로 추가된다.»
4. 점검 항목 1(RL·RX) — 전: «1. **행위 목록 ↔ 코드 실현 대조** (홀리스틱 감사에서)» / 후: «… (홀리스틱 감사에서 — 수정 모드는 «수정 모드» 4 의 G2 직전 1회에서 · 행위 추적은 감사 범위 밖 파일도 따라간다)».
5. Makefile verify-web — 문단 대조 루프에 '**discipline 감사 = touched 파일 한정 경량 1회**' · RL/RX 두 줄 byte 대조(존재 가드 · «Coordinator가→코디네이터가» 치환).

## §16 구현 메모 처리

- ① `assets/sdk_boundary.js` — 분류표의 `lifecycle` 함수는 모든 이름공간(gateway 이름공간 포함)에서 원본 그대로(`pass:<ns>.<fn>`). 표에 없어도 이름이 수명 꼴(cleanup·destroy·dispose·teardown)이면 원본 그대로 두되 «표에 없는 함수»로 센다. 리허설 R6 «API.cleanup 통과» 고정.
- ② gateway 정규형 — 백스톱 `src/sdk_registry.py::normalize_gateway_url`(WV9) 과 스니펫 `normPath` 가 같은 규칙(운영자 호스트 점 경계 → 경로만 · 쿼리·조각 제거 · 퍼센트 해제 · 끝 `/` 제거 · 소문자 · api-paths 밖이면 발견). 픽스처 K52b-4·5·6·7 · 리허설 R6 같은 짝.
- ③ `sdk_vendor.py install --replace` — 새 판 api-paths 와 승인된 `request:<경로>` 를 대조해 «사라진 경로 · 새 경로(승인 밖)» 줄을 거절 판정 **전에** 낸다(dry-run 포함). 픽스처 «③ 판 올림 dry-run»(사라진 1 · 새 1) · «③ 옛 경로표 초안 거절(diff 먼저)».
- ④ REQUEST_GUIDE §7 문안 한 줄(Codex byte 미러).
- ⑤ WV8 토큰 규칙 — `srcdoc` 토큰(식별자·문자열) · `createElement`/`createElementNS` 토큰 뒤가 «( + 단일 문자열 리터럴»이 아니면 발견(.call·.bind·괄호 문자열 포함) · `document`·`contentDocument`·`ownerDocument` 와 그 별칭의 `write`/`writeln`(점·괄호). `src/check_vendor.py::scan_js`. 표본(설계 47 + 8꼴 + 짝) 어긋남 0(`sdk_fixture.py wv8`). spring_dream 전수(공유 클론 main·레인 가지 머리 7 · main 작업 트리 · 레인 워크트리 6 — 읽기만): WV8 적중은 어디서나 `conversation.js` `createElement("script")` 2줄뿐 · 새 토큰 규칙 적중 0 · WP3 0.
- ⑥ K50e — 판 올림 뒤 옛 판 임시 사본(참조 중)이 merge 로 돌아오면 WV13, §6-8 #6b 치환 정리 뒤 0(픽스처). Coordinator 엣지 «공식 SDK 늘 red·미등재 벤더» 에 출구 문장.

## 검증·리허설

- 픽스처: `fixtures_sdk.sh` 183 · `fixtures_debt.sh` 97(새 D30~D38 17) · `fixtures_refactor_audit.sh` 201(새 S1~S6 10) · 전체 19 파일 실패 0.
- 변이(scratch 복사본): 35종 전부 red — 단 «단락 제거(K51 시간 상한)»는 한 번 걸음 구현이라 시간으로 가를 수 없어 넣지 않았고, «--full-history 제거»는 git 2.54 에서 `-m` 만으로도 곁가지가 보여 단독으로는 무력(둘 다 지운 변이는 K49b red).
- ① 실제 카카오 2.8.3(네트워크 — 원본·운영자 문서만): candidate 87,110 B · sha256 b2ff7b30deff… · 문서 sha384 일치 · 인용 확인 · 이름공간 7 · api 경로 30 · 열거 함수 표(로컬 밖 차단 0) → install(dry-run 배너) → verify 0 → gated 0 · 빚 0. P13·P14·K40·K50c·K42·K48·K43 재현 기대대로. 낱말 표 «전자서명»·«친구 고르기»·«친구 선택»은 다운로드 문서 등장 0(1급 표시가 뜬다).
- ② cdnjs html2canvas · ajax.googleapis `/ajax/libs/` 원본 → candidate 거절(네트워크 전).
- ③ 실제 Chromium(headless shell 1234 · playwright-core 1.64 · 로컬 서버 · 로컬 밖 전부 abort): R4 E0~E4 · R4+ · R4++ · R5 · R6 17/17 통과. 브라우저 변이 7종(폼 래퍼 · 수명 함수 · 함수 목록 · 라우트 해제 생략 · 정규형 · 스택 없음 · 같은 출처 script) 전부 red.
- ④ 목록 없는 사본이 레인 도중 main 병합으로 들어오면 레인 G2 diff 게이트 WS6·WP1·WP2 red · WV 0(사실 확인).
- scratch: `…/scratchpad/impl-web2/`(mutate.py · browser/rehearse.js · rehearse1.sh · rehearse4.sh · sd_scan.py · 로그).

## 설계와 다른 점(이유)

1. W6m touched 정의 — 설계 문안의 «`git_snapshot` 이후 이번 실행이 만든 …» 대신 W4(`static_delta.py`)·«G2 전 정적 검사»의 «손댄 파일» 정의(범위 기준 `pre_run_head`, 없으면 `git_snapshot` · 첫 부모 비병합 커밋 + 미커밋 + 병합 안 수정 `--cc` + 기준 가지 밖 둘째 부모 병합은 들여온 파일 전부)로 맞췄다 — 지시대로.
2. WN8 — vendor 표지 `.gitattributes` 를 WN8(파일명 규칙) 예외로 뒀다(고정 바이트 표지라 이름 규칙 대상이 아님 · 없으면 WN8 오탐).
3. 빚 참조 pathspec — `web/static/vendor` 외에 `web/sdk_registry.json` 도 뺐다(컨테이너 계획의 `web` 꼬리 소비자가 목록 파일을 잡는 잡음). Coordinator grep 문면 2곳도 같이(S1 커밋 — refactor_audit self-test 문면 대조 때문).
4. WV2 — 한 id 당 발견 1건으로 묶고, ④ 바이트 대조는 index 가 아니라 `git hash-object --stdin-paths`(필터 적용) 대 원본 blob(판 올림 직후 index 가 낡아 거짓 WV2 → 자동 되돌림이 나던 것).
5. `install` — 출처 문면 거절은 exit 1(사용 오류 쪽) · 같은 항목 재실행은 «이미 같은 항목» exit 0(멱등) · 판 올림 gateway 경로 diff 줄은 거절보다 먼저 찍는다(§16③).
6. `candidate` — 최종 URL 의 등록 가능 도메인이 source·docs 도메인 안인지 추가 확인(리다이렉트로 밖에 떨어지면 거절).
7. `remove` — 마지막 항목이면 목록·표지·빈 vendor 폴더를 지우되, 비어 있지 않은 vendor 폴더는 남긴다(미등재 사본을 도구가 지우지 않음).
8. WV8 — §16⑤ 의 srcdoc 토큰 규칙 때문에 K46c 의 한 짝(srcdoc 문자열을 다른 용도로 쓰는 꼴)이 «발견»으로 바뀐다 — 표본 기대를 토큰 규칙 쪽으로 맞췄다.
9. G2 배너 SDK 행 이름 — 기존 ③′ 와 겹쳐 «③″ SDK 행»으로 붙였다.
10. 리팩토링 R1(공개 설정) — `refactor_audit plan` 의 벤더 단위 «SDK 등재 정리» 절에서 settings 유무를 보이고, `install` G1(리팩토링) 경로에서도 같은 확인을 한다. R+ 경우는 `--self-test` 가 아니라 픽스처(S1~S6)로 고정.
11. refactor_audit 렌즈 점검 절에 houserules §9 · implementation-javascript §8 추가(새 절이 감사 렌즈에서 빠지지 않게 · self-test 점검 절 62 → 64) — S2 커밋.
12. 변이 «단락 제거(K51 시간 상한)» 는 한 번 걸음 구현이라 시간으로 가를 수 없어 측정하지 않았다.
13. K 케이스 일부는 픽스처 장치 사정으로 꼴을 바꿨다(K21a 커밋 필요 — check-attr 가 index 의 `.gitattributes` 를 읽음 · K21c CRLF 원본을 `--crlf` 로 · K27 기대 «라벨 둘 이상» 하나 · NAVER 초안에 Share 표).

## 새 결함(고치지 않음)

- 기존 코드에서 새로 본 결함 없음.
- 관찰: spring_dream 전 가지·워크트리의 `web/static/js/conversation.js` `createElement("script")` 2줄이 WV8 에 걸린다 — 설계 §1-11 실측(v3.1·v3.3)과 같은 2건이고 새 토큰 규칙 적중은 0. 빚 스캔에서 미룰 수 있는 키다(첫 G0 에 뜬다).

## 남은 일

- 착지 때 봉인 chore(`manifest_seal.py --write`) — Makefile 변경(W6m·S2·S4) 때문. 운영자 몫.
- `make release-web`(배포) · 설치본 갱신 · Codex 쪽 설치 확인.
- 첫 실제 레인에서 SDK 채택 흐름(candidate → G1 SDK 행 → ②″ 격리 커밋 → 3-1 경계 확인) 관찰.
- 워크트리 `.venv` 는 검증용 심링크(untracked · 커밋 안 함).

Serena: 사용 안 함(프로젝트 opt-in 없음 · 지시).

## 리뷰 반영(독립 구현 리뷰 «수정 후 승인» · major 6 · minor 1)

리뷰 문서: `~/.herdr/worktrees/dddjango/review-web-sdk/workspace/plan/2026-10-01-web-official-sdk/review/review.md`(읽기만). 기존 4커밋은 그대로 두고 그 위에 두 커밋을 올렸다.

| 해시 | 묶음 | 단독 검증(scratch 공유 클론) |
|---|---|---|
| `ca53b20a` | F1·F2·F3 — `sdk_vendor.py` · houserules §9 한 문장(+Codex byte) · 픽스처 F1~F3 | `make verify-web` 0(fixtures_sdk 205 · 19 파일 실패 0 · self-test red 0) |
| `66781e89` | F4·F5·F6·F7 — `sdk_registry.py`·`check_vendor.py`·`assets/sdk_boundary.js`·`sdk_fixture.py`·`test/boundary_probe.cjs` · 픽스처 | `make verify-web` 0(fixtures_sdk 226 · 19 파일 실패 0 · self-test claude·codex red 0) |

Makefile·core 는 바꾸지 않았다(`make verify` 대상 변화 없음 · 봉인 chore 없음).

### 발견별 수정 · 픽스처 · red → green

수정 전 red 는 리뷰 대상 HEAD(`d6d2878d`) 코드에 새 픽스처 파일만 얹어 돌린 결과다(`scratchpad/impl-web2/red-before.log` — fixtures_sdk 197 통과 · 29 실패). 수정 뒤는 같은 픽스처 226/226.

- **F1** `sdk_vendor.py::cmd_restore` + `_dir_chain_problem` — 쓰기·링크 제거 전에 ⓡ2 뒤 내용(NFC)으로 WV1(최상위·그 id — file 꼴·id 결합) · WV3(결속·출처) · 경로 성분(`web`·`web/static`·`web/static/vendor` 링크·비디렉터리 아님 · 자리가 일반 파일)을 확인하고 어긋나면 «승인 불요 복원 대상이 아니다(쓰기 0)»로 정지. id 디렉터리 링크는 확인 뒤 링크 자체만 지운다. 픽스처 F1a(file `../../` · 결속 그대로) · F1b(같은 꼴 · 결속 재계산) · F1c(결속 깨짐 + 사본 변조 → 덮지 않음) · F1d(`web/static` 이 밖 링크) — 넷 다 수정 전 red(밖 파일 덮어씀 · «ⓡ1» 출력) → green. 짝 F1e(id 디렉터리 링크 → 링크만 지우고 ⓡ1 · 링크 너머 파일 그대로)는 전후 green.
- **F2** `sdk_vendor.py::_unit_groups`(옛 `_scope_groups` 에서 운영자 묶음을 호출부로) — 첫 채택·기존 등록 분기도 gateway 단위마다 경로 문자열 묶음을 같은 함수로 더한다(판 올림은 단위를 새로 들이지 않아 제외). houserules §9 승인 줄에 «범용 함수 경로는 첫 채택·기존 등록에 함께 들어와도 경로마다 그 경로 문자열을 담은 원문» 한 문장. 픽스처 F2a(리뷰 재현 — 원문에 판·운영자만 → exit 1 · 목록·사본 없음) 수정 전 red(exit 0) → green. 짝 F2b(원문에 `/v2/user/me` → 설치 0 · verify 0) · F2c(본인 직접 → 0).
- **F3** `sdk_vendor.py::_final_problems` — 원본과 문서 모두 리다이렉트 최종 주소를 https · 라이브러리 CDN 아님 · 원본·문서의 운영자 도메인(등록 가능 도메인) 안으로 확인하고, 문서 최종 주소를 후보 `docs_final_url` 에 보존(후보 schema `dddjango-web-sdk-candidate/2`) · `install` 이 operator_domains 점 경계로 다시 확인 · 배너에 표시. 픽스처 F3a(http 외부) · F3b(https 외부) · F3c(`developers.kakao.com.evil.example`) · F3f(후보의 최종 주소가 operator_domains 밖 → install 거절) 수정 전 red → green. 짝 F3d(운영자 도메인 안 리다이렉트 → 통과 · 최종 주소 보존) · F3e(dry-run 배너에 최종 주소) — 둘은 새 보존 칸을 보므로 수정 전에도 red 였다.
- **F4** `src/sdk_registry.py::normalize_gateway_url` 와 `assets/sdk_boundary.js` `normPath` 를 URL 파서 없이 글자 단위 같은 규칙으로 다시 썼다 — 출력 가능 ASCII·역슬래시 없음 → 스킴이나 `//` 면 `https://<운영자 호스트>` 만(소문자 · `[a-z0-9.-]` · userinfo·포트 거절) · 아니면 `/` 시작 → 쿼리·조각 제거 → 비예약 문자로 풀리는 `%XX` 만 → 끝 `/` 제거 · 빈 조각·`.`·`..` 거절 → 소문자. 픽스처 F4a(`sdk_fixture.py gwsame` — Python 과 실제 스니펫(node vm · `test/boundary_probe.cjs`)이 표본 27(리뷰 표 7 포함)에서 기대와 같고 승인 밖 발견 수·원 함수 호출 0·수명 함수 통과 1) · F4b(앞 공백 + 외부 호스트) · F4c(점 조각) — 수정 전 red → green. F4d(`/` 없는 상대)는 수정 전에도 Python 은 거절(green · 회귀 고정).
- **F5** `src/check_vendor.py::scan_js` + `_member_view`·`_grouped`·`_doc_names` — 괄호 접근(`x['n']`·`` x[`n`] `` · 자리표시 없는 리터럴 · 식별자 값)을 점 접근으로 편 뷰에서 문서 수신자·`createElement` 를 본다. 문서 수신자의 묶음 괄호(`(document).write` — 앞이 식별자·`)`·`]` 인 호출 괄호는 제외 · return·typeof 류 뒤는 묶음) · 괄호 RHS·괄호 접근 별칭·별칭의 별칭 전파(별칭 이름은 `.` 뒤 속성 이름이면 제외). 픽스처: 백스톱 실행 6(리뷰 표 5 + `` document[`write`] ``) · 짝 4(`logger.write` · `const d = logger; d.write` · `stream(document).write` · `` el[`textContent`] ``) · WV8 표본 19 추가(66 → 85). 수정 전 red 5(리뷰 표 5꼴 — `` document[`write`] `` 는 수정 전에도 잡혔다) + 표본 묶음 → green.
- **F6** `src/check_vendor.py::unit_files`·`unregistered_units`·`classify_units` — 미등재 단위의 심볼릭 링크를 따라가지 않고 링크 자체를 내용으로 센다(하위 디렉터리 링크는 `dirs` 에서 수집 · 단위 자체가 링크면 링크 단위 · 내용은 git 처럼 대상 경로 문자열 → 탄생 커밋 대조). 픽스처 F6a(목록 시대 + 하위 디렉터리 링크만 → verify·gated WV13) · F6d(목록 이전 링크 단위 → 빚 WV12 · WV13 아님) 수정 전 red → green. F6b(단위 자체가 링크 → WV13)는 수정 전에도 green 이었다(링크를 따라가 대상 파일로 판정) — 이제 따라가지 않고 같은 답. F6c(일반 파일 대조) 전후 green.
- **F7** `sdk_fixture.py walks` — `classify_units` 의 git 호출을 세어 이력 전체 조회(`log --raw`) 횟수와 시간을 낸다. K51 옆 F7a(목록 이력 없음 → 0회 · 3 s 미만) · F7b(있음 → 1회 · 3 s 미만 · WV12). 현재 구현은 전후 green(리뷰 독립 확인과 같음). 변이로 red 확인(`scratchpad/impl-web2/mut_f7.sh`): 단락 제거 → F7a raw_walks=1 red · 단위마다 걸음 → F7b raw_walks=201 · 3.42 s red. 설계 차이 12항(«단락 제거 변이 측정 안 함»)은 이 걸음 수 고정으로 닫는다.

### 추가 확인

- 리뷰어 재현 자료(`probes.py`·`boundary-probes.cjs` 사본 — 후보 거절로 산출 폴더가 없어 초안 쓰기 전 `mkdir` 한 줄만 더함)를 수정 코드에 그대로 돌림(`scratchpad/impl-web2/revprobe/`): WV8 5꼴 전부 exit 2 · 문서 http 리다이렉트 candidate 거절 2 · 첫 채택 gateway 원문 경로 없음 exit 1 · 링크 단위 verify·gated 2 · restore 밖 파일 덮어씀 False · 스니펫 기록기 4 반례 path null · 승인 밖 발견 4.
- 실제 Chromium 리허설 재실행(수정한 스니펫 · 로컬 밖 전부 abort): 17/17 통과(`browser/rehearse-all-r2.out`).
- spring_dream 재스캔(공유 클론 머리 8 · main 작업 트리 · 레인 워크트리 — 읽기만): WV8 은 여전히 `conversation.js` `createElement("script")` 2줄뿐 · WP3 0. (`lane-admin-1` 워크트리는 그 사이 다른 쪽에서 지워져 0 파일로 보였다.)
- 전체 `run_fixtures.sh` 19 파일 실패 0(fixtures_sdk 226 · debt 97 · refactor_audit 201 · backstop 62 …).

### 리뷰와 다르게 한 판단 · 설계와 다른 점

- F2 는 리뷰 권고대로 설치 시점 판정만 넣었다. WV3 에 경로 문자열 대조를 더하지 않은 것은 설계 §5-2 WV3 정의(결속·조상·행 해시)를 따른 것이다 — 목록을 손으로 고치면 결속(WV3)이 이미 잡는다.
- F4 정규형은 리뷰 표를 닫는 데 그치지 않고 설계 §16② 문면(«운영자 호스트 점 경계 → 경로만 · 쿼리·조각 제거 · 퍼센트 해제 · 끝 `/` 제거 · 소문자»)보다 엄격하다 — `//호스트`·포트·userinfo·비예약 밖 퍼센트(`%2F`·`%25`)·빈 조각도 거절한다. 운영자 API 경로는 비예약 문자뿐이라 정상 호출은 영향이 없고, 두 구현이 같은 답을 내는 것이 목적이라 해석 여지를 없앴다.
- F3 로 후보 schema 가 `/2` 가 됐다 — 이 판 이전에 뽑은 후보는 install 이 받지 않는다(다시 뽑는다). 아직 배포 전이라 실제 영향 없음.
- F5 에서 `` document.createElement(`li`) `` 같은 backtick 태그 인자가 발견인 것은 기존 동작(단일 «문자열» 리터럴만 통과)이고 이번에 바꾸지 않았다.
- 리뷰 지적에 동의하지 않는 부분은 없다.
