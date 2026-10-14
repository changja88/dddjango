# dddjango-web 2.5.2 — 사용자 git 설정 · git 이 감싸 표시하던 이름 · 링크 너머 읽기에서 판정을 떼어 놓는다

## 문제
- 2.5.1 이 «알려진 기존 결함» 으로 미룬 여섯 갈래를 재현으로 확인했고(맨 위 · 하위 폴더 모두), 다섯을 고치고 같은 뿌리의 결함을 전수 조사 · 적대 검토 세 바퀴로 더 찾았다. 여섯째(미룬 키 파일을 web/ 밖으로 옮긴 이동 · 아래 «한계»)는 세 판을 시도한 뒤 덜어 내 다음 판으로 미뤘다. 진단 · 설계 기록: 운영 scratch `w252/`.
- 사용자 git 설정 · 속성이 기계가 읽는 git 출력의 꼴을 바꿨다.
  - 더한 줄 범위(`git diff -U0`)를 읽는 자리 — `color.ui` · `color.diff=always` · 전역 외부 diff 도구(`diff.external`) · 속성 textconv 는 범위를 비우거나 옮겨 IM24 거짓 통과(게이트 exit 2 → 0). `diff.algorithm`(histogram · patience) · 속성 드라이버의 `diff.<drv>.algorithm` 은 반복 줄 사이로 옮긴 옛 import 줄을 «더한 줄» 에서 빼 IM24 거짓 통과. `-diff` · `binary` 속성(사용자 `core.attributesFile` · 저장소 `.gitattributes`)이나 git 이 내용으로 바이너리로 본 파일(앞 8,000 바이트에 NUL — 속성 없음)은 범위를 비워 거짓 통과 — 저장소 속성 · 내용 NUL 은 기본 사용자 설정에서도. `diff.interHunkContext` 는 가까운 덩이를 합쳐 기준점의 옛 빚 줄을 더한 줄로 읽어 IM24 거짓 막음.
  - `color.ui` · `color.grep=always` — `refactor_audit.py plan` 참조 조회 실행 불능. `grep.column=true` — 참조 조회의 줄 글 앞에 열 번호(판정 무변). 사용자 전역 속성(`core.attributesFile` · 기본 자리)의 `-diff` — git grep 이 그 파일을 바이너리로 보아 `plan` 참조 조회(`-I`)가 소비자 · 참조 치환 줄을 놓치고, SDK 도구의 템플릿 참조 줄이 «Binary file … matches» 로 바뀜.
  - 커밋 서명 + `log.showSignature=true` — sdk 격리 커밋 «제목» 을 서명 확인 줄로 읽어 WV10 거짓 막음 · 0T 확인 도구가 사슬에 서명 줄을 섞어 거절 · 상시 답 표시가 `(커밋 Good · "git")` · 승인 병합 제목 표시에 서명 줄.
  - `apply.whitespace=error` — 반례에 끝 공백이 있으면 0T 확인 도구가 «적용되지 않는다» 로 거절.
- 경로를 줄 단위로 읽던 자리 여덟이 git 이 감싸 표시하는 이름(따옴표 · 역빗금 · 탭 · 줄바꿈 · CR · BEL · 백스페이스 등 제어 글자 — git 이 `"…"` 로 감싸는 모든 이름)을 감싼 꼴로 읽었다(기본 설정).
  - 빚 잔존이 미룬 키 파일의 개명을 놓쳐 «ⓑ 이동 묶음 의존» 이 서지 않음(거짓 통과) · 승인 병합이 들인 그런 이름 이동을 못 가름.
  - 벤더 시대 판정이 목록 이전 같은 자리 사본(벤더 폴더 · 하위 폴더 이름에 그 글자)을 거짓 WV13 으로 막고 SDK 정식 등재를 되돌림.
  - `refactor_audit.py residual` 이 옮긴 의미 항목 파일을 무변으로 보아 거짓 «결정적 잔존».
  - `plan` 참조 조회가 맞는 파일 이름에 `:` · 맞는 줄에 U+2028 · 폼 피드가 있으면 실행 불능.
- 프로젝트 밖으로 풀리는 자리를 읽었다(판정은 그대로): `plan` 조각 셈(링크 너머 줄 수로 조각 · 파견 수가 바뀜) · SDK 사본 검사(WV2 가 링크를 문제로 적은 뒤에도 읽음 · `hash-object` 입력) · O7(범위 넓힘 · 서비스 호스트)의 등재 사본 바이트 두 자리(폴더 링크를 따라감 · `..` 로 밖을 가리키는 항목도 거절 전에 읽음).
- 0T 확인 도구가 이름이 공백 · 줄바꿈으로 끝나는 저장소의 맨 위 프로젝트를 «최상위가 아니다» 로 거절.
- 빚 잔존의 개명 조회(web 범위)가 사용자 `diff.renameLimit` 이 작거나 web/ 안 변경이 아주 크면(지운 수 × 더한 수가 한도² 를 넘으면) 이름 바꿔 고친 이동을 놓쳤다 · 사용자 `diff.relative=true` 를 따를 여지가 있었다(2.5.1 은 명시 `--relative` 로 이김).
- 빚 잔존의 개명 조회(작업 트리 diff · web 범위)가 끝난 뒤 git 이 색인 전체를 새로 고치며 하위 폴더 프로젝트 밖의 stat 만 바뀐 추적 파일을 읽었다(clean filter 가 걸려 있으면 그 글이 filter 에 넘어감 · 판정은 그대로).

## 고침 (소스 11 파일 · Codex byte 미러)
- `src/common.py` 에 상수 하나 `GIT_PINS`(`-c color.ui=never -c color.diff=never -c color.grep=never -c grep.column=false -c log.showSignature=false -c diff.interHunkContext=0` — 파이프로 읽는 출력을 고정하는 값 · 파이프 출력에서는 git 기본과 같다). git 을 띄우는 29 자리 전부가 `['git', *GIT_PINS, …]` 로 싣는다 — 정적 시험이 test/ 밖의 프로세스 실행 자리를 «알려진 자리 표» 와 대조한다. 이 대조는 정직한 코드의 새 실행 자리를 잡는 울타리다: import 로 묶은 이름(`import subprocess` · `import os.path` · `from os import system` · 다른 모듈이 다시 내보낸 이름)의 모듈 수준 실행 함수 부름을 세고, 표에 없는 새 자리 · 셸 실행 · 튜플 · 경로 붙은 git · `*GIT_PINS` 없는 git 목록 · 그 실행 함수를 부르지 않고 꺼냄 · 실행 모듈(`subprocess` · `os` · `pty` · `asyncio`)을 값으로 씀(별칭 · `getattr`) · `from <실행 모듈> import *` · 이름 `sys.modules` · 속성 `__dict__` · 이름 `__import__` · importlib 을 붉게 한다. 일부러 숨긴 꼴(`sys` 별칭 · `from sys import modules` · `from os import __dict__` · `__getattribute__` · `os.path.os` · 하위 모듈 경로 `asyncio.subprocess` · 이벤트 루프 메서드 · 다른 모듈 속성 · `builtins.__import__` · `globals()` · 다른 표준 모듈이 안에서 띄우는 길(`_posixsubprocess` · `webbrowser` · `platform` · ctypes · multiprocessing) · 문자열 exec/eval)은 보지 않는다.
- 더한 줄 범위 diff(`src/common.py`)는 `--no-ext-diff --no-textconv --text --diff-algorithm=myers` — 사용자 · 저장소의 외부 diff · textconv · 알고리즘(설정 · 속성 드라이버) · `-diff`/binary 속성 · git 의 내용 바이너리 판단을 따르지 않는다(`-c diff.algorithm` 은 속성 드라이버를 못 이겨 명령 줄 선택지로). 0T 반례 `apply --check`(`src/switch_check.py`)는 `--whitespace=nowarn`(적용 줄과 같게). git grep 두 자리(`src/debt.py` 참조 조회 · `sdk_vendor.py` 템플릿 참조)는 `-c core.attributesFile=` — 사용자 전역 속성 파일을 끈다(저장소 `.gitattributes` 는 따른다 · 참조 조회의 `-I` 는 그대로).
- 경로를 읽는 여덟 자리를 `-z`(NUL 구분)로: `src/debt.py` 셋(`ls-tree` · 개명 둘 — 새 함수 `name_status_z` · `_diff_moves`) · 참조 조회 `git grep -z`(«경로 NUL 행 NUL 줄» 차례로 읽음 · 명령 기록의 옵션 상수는 그대로) · `refactor_audit.py` residual 셋(bytes 로 받아 줄바꿈을 바꾸지 않음 — 이름 속 CR 도 그대로) · `src/check_vendor.py` 벤더 시대 `log -z`(커밋 머리는 `%x01` 표지 뒤 해시).
- `refactor_audit.py` `_lines_of` 는 `_inside` 를 먼저(밖이면 0행). `src/sdk_registry.py` 새 함수 `link_component`(경로 성분 가운데 첫 링크) — WV2 는 링크 성분이 있으면 링크 · 색인 모드 · 무시 · 속성 문제만 적고 `hash-object` 입력 · 목록 · 바이트 읽기에서 뺀다. O7 의 등재 사본 바이트는 새 함수 `registered_copy_bytes` 하나로 모았다(`static/vendor/` 아래 정규형 · `..` 없음 · 링크 성분 없음일 때만 읽음 — 2.5.1 의 `check_vendor._copy_bytes` · `sdk_vendor._registered_bytes` 를 대신한다).
- `src/switch_check.py` 저장소 최상위 경로는 끝 줄바꿈 하나만 뗀다.
- 빚 잔존의 개명 조회(`src/debt.py` `_diff_moves` — 레인 개명 · 승인 병합 계보 둘 다)는 2.5.1 처럼 프로젝트 web 범위만 본다(같은 짝 · web/ 밖으로 옮긴 파일은 지움). 바꾼 것은 설정 · 이름 · 밖 읽기 내성뿐이다: `-z` · `GIT_PINS` · 개명 탐지 한도 없이 `-l0`(`check_tests` 의 시험 개명 조회와 같게 · 사용자 `diff.renameLimit` 도 이긴다) · `--no-relative` + `:(top,literal)<접두>web`(사용자 `diff.relative` 를 따르지 않는다) · `-c diff.autoRefreshIndex=false`(작업 트리 diff 끝의 색인 전체 새로 고침이 프로젝트 밖 파일을 읽지 않게). 승인 판정(`_inflow_moves`)의 경로는 저장소 기준(`_raw(…, repo=True)` · `ls-tree --full-tree`)으로 읽고, pathspec 은 모두 글자 그대로(`:(top,literal)`)다 — 하위 폴더 이름이 `:` 로 시작해도 마법으로 읽지 않는다.

## 바뀌는 동작
- 맨 위 프로젝트 · 기본 git 설정에서 일부러 바꾼 것:
  - git 이 감싸 표시하던 이름(따옴표 · 역빗금 · 탭 · 줄바꿈 · CR · BEL · 백스페이스 등)의 미룬 키(ⓑ) 파일을 레인이 옮기면 빚 잔존이 «ⓑ 이동 묶음 의존» 으로 멈춘다(exit 0 → 1 · `--debt-residual` · `refactor_audit.py residual` 의 의미 ⓑ). 승인 병합이 그런 이름 파일의 이동을 들였으면 승인 전 멈춤 · 승인 뒤 «승인 병합이 들인 이동» 알림(ASCII 이름과 같다).
  - `refactor_audit.py residual` — 그런 이름의 의미 항목 파일을 옮기면 «결정적 잔존»(exit 2) 대신 리뷰어 확인 대상 · 개명 쌍에 그 이름 그대로.
  - `plan` 참조 조회 — 맞는 파일 이름에 `:` · 맞는 줄에 U+2028 · 폼 피드가 있어도 실행 불능이 아니다 · 그런 이름의 참조 줄도 잡는다.
  - 벤더 시대 — 미등재 벤더 폴더 · 파일 이름(맨 위) 또는 하위 폴더 이름에 그 글자가 있어도 목록 이전 같은 자리 사본은 WV12(빚)다(거짓 WV13 · install 되돌림 없음).
  - 0T 확인 도구 — 이름이 공백 · 줄바꿈으로 끝나는 저장소의 맨 위 프로젝트를 받는다.
  - web/ 안 변경이 아주 큰 레인(지운 파일 수 × 더한 파일 수가 백만을 넘음) — 이름 바꿔 고친 미룬 키 파일의 web/ 안 이동을 이제 잡는다(`-l0` · 2.5.1 은 비슷함 탐지를 건너뛰어 놓쳤다).
  - git 이 바이너리로 보던 web 파일 — 저장소 `.gitattributes` 의 `-diff` · `binary`, 또는 속성 없이 내용에 NUL 이 든 파일(NUL 든 기능 JS · 템플릿 · UTF-16 글 등) — 을 고친 레인의 더한 줄에 줄 단위 검사(IM · PU · WV8 · 이름 · 셸)가 선다(전에는 더한 줄이 비어 조용히 지남 · 게이트 · 슬라이스 끝 exit 0 → 2 가능 · 참 발견). 이미지 · 글꼴 같은 진짜 바이너리는 검사 대상이 아니라 출력이 같다.
  - 프로젝트 밖으로 풀리는 자리: `plan` 조각 셈은 그 파일을 0행으로 · WV2 가 파이썬으로 읽는 사본 바이트와 `hash-object` 입력은 링크 너머 · `..` 를 읽지 않는다(속성 조회 `check-attr` 는 2.5.1 부터 그대로 — 사본 폴더가 링크면 링크 너머 `.gitattributes` 의 속성 줄이 실릴 수 있음 · 판정 무관)(판정 WV2 그대로 — 링크 너머를 읽어 붙이던 위반 줄(크기 · sha256 · 무결성 · origins 불일치 · «정확한 이름의 등재 파일이 없다» · «일반 파일이 아니다»)이 빠지고 링크 · 색인 모드 · 무시 · 속성 줄만 남는다) · O7 의 등재 사본 바이트는 꼴이 어긋나면(링크 · `..` · 정규형 아님) «없음».
- 사용자 git 설정 · 속성 — 위 «문제» 의 갈래(색 · 외부 diff · textconv · diff 알고리즘 · 속성 드라이버 알고리즘 · 사용자 속성 `-diff` — 더한 줄 · 참조 조회 · 템플릿 참조 줄 · `interHunkContext` · `grep.column` · 서명 확인 표시 · `apply.whitespace` · `diff.renameLimit` · `diff.relative`)는 기본 설정과 같은 출력이다.
- 그 밖의 맨 위 출력 · 하위 폴더 출력은 2.5.1 과 같다(하위 폴더 = 맨 위). 미룬 키 파일을 web/ 밖 · 프로젝트 밖으로 옮긴 레인도 2.5.1 과 같다(아래 «한계»).
- 빚 지문 `e49c83776ff9faf6` · 검사 92종 무변. 규칙 글은 바뀌지 않았다.

## 한계
- **2.5.1 부터의 한계(이번 판에서 덜어 냄)**: 미룬 키(의미 항목) 파일을 web/ 밖(하위 폴더 프로젝트면 프로젝트 밖)으로 옮긴 레인은 그 이동을 지움으로 본다 — 빚 잔존은 그 키를 «발견 0(해소 아님 · 보고만)» 으로 지나고, `refactor_audit.py residual` 은 그 의미 항목을 «결정적 잔존» 으로 본다. 승인 병합이 들인 web/ 밖 이동도 계보가 web/ 에서 끊긴다(2.5.1 과 같음). 세 판에 걸쳐 web/ 밖 새 자리를 좁혀 찾는 길을 시도했으나 좁힐수록 새 거짓 멈춤이 나와(승인 이동 + 프로젝트 안 복사본 · 키 지움 + web/ 밖 무관 개명 · 키 아닌 파일의 밖 이동 · 하위 폴더의 판정 불가 조건 · 명령 줄 길이) 덜어 냈다(장부).
- 사용자 전역 무시 규칙(`core.excludesFile`) · 줄 끝 설정(`core.autocrlf` · 속성 `eol`)은 그대로 따른다. 전역 무시에 `vendor/` 가 있으면 이미 커밋된 SDK 사본도 WV2 «무시 규칙에 걸린다» 로 막힌다 — 개인 무시 규칙을 셀지는 뜻 결정이 먼저라 이번 판에 넣지 않았다(장부). 줄 끝 변환으로 승인 유입 시험의 수신 증명이 서지 않는 것은 2.2.5 부터의 보수 쪽 한계 그대로.
- 게이트 · TG 검사기는 web/ 안의 파일 링크를 따라 밖 내용을 읽고 판정한다(폴더 링크는 내려가지 않음) — 밖을 가리키는 링크 파일을 어떻게 볼지는 규칙 결정이 먼저라 이번 판 밖(장부).
- 사용자 `status.renames=false` 면 0T 확인 도구의 «작업 트리 변경» 거절 목록 표시가 달라진다(개명이 지움 + 더함으로 · 거절 판정은 같음 · 2.5.1 부터 · 장부).
- 상시 답 파일 · 0T 행 파일이 링크면 밖을 읽는다(판정은 커밋 판 대조로 거절 쪽).
- SDK 사본 폴더가 링크면 WV2 의 속성 조회(`check-attr`)가 링크 너머 `.gitattributes` 를 읽어 속성 줄을 싣는다(판정 WV2 그대로 · 2.5.1 부터).
- 참조 조회(`-I`)는 저장소 `.gitattributes` · `.git/info/attributes` 가 `-diff` · `binary` 로 둔 파일을 바이너리로 보고 건너뛴다(2.5.1 과 같음 — 저장소가 선언한 뜻으로 둔다). 끄는 것은 사용자 전역 속성 파일뿐이다.
- 빚 잔존의 개명 조회는 web 범위를 한도 없이(`-l0`) 본다 — web/ 안에서 수천 개를 지우고 더한 레인은 느려질 수 있다. 그 밖의 `-M` 읽기 — 치환 확인(`src/subst.py:150`) · residual 개명 쌍(`refactor_audit.py:1837`) · TG 개명 대상(`src/check_tests.py:1076` `-M30%`) · 부품 CSS 개명(`src/check_component_css.py:599` `-M100%`) — 는 git 기본 한도 그대로다(바뀐 시험의 개명 조회 `src/check_tests.py:148` 는 전부터 `-l0`).
- 프로젝트 밖 작업 파일을 git 에게도 읽히지 않게 한 것은 빚 잔존의 개명 조회뿐이다. 다른 작업 트리 diff 자리(게이트 · 치환 확인 · residual 등)는 2.5.1 처럼 git 의 색인 새로 고침이 프로젝트 밖 stat 만 바뀐 파일을 읽을 수 있다(장부).
- 게이트(`src/common.py` `_git_raw` — `diff --name-status -z` · `status --porcelain -z` · `ls-tree -z`) · 부품 CSS 검사(`check_component_css.py` 같은 꼴 셋)의 파일 목록 읽기는 글 모드라 이름 속 CR 을 LF 로 읽는다 — 그런 이름의 새 web 파일은 검사에서 빠질 수 있다(2.5.1 부터 · 이번 판은 residual 세 자리만 바이트로 · 공용 함수라 다음 판에서 시험과 함께 · 장부).
- 정적 대조는 정직한 코드의 새 실행 자리를 잡는 울타리일 뿐이다 — 일부러 숨긴 꼴(위 «고침» 의 목록)은 보지 않는다.
- 표시 글(sdk_vendor «참조:» 줄 · refactor_audit ②③ 조건 표시 · 승인 병합 제목)의 특수 이름은 git 이 감싼 꼴 그대로다(판정 무관).
- 2.5.1 의 한계(0T 하위 폴더 · 대소문자 철자 루트 거절 · 두 인자 철자 거절 · 저장소 기준 표시 글 셋 · 경로 기준 둘)는 그대로.
- git 2.54.0 · macOS 하나로만 쟀다. 서명 장면은 `ssh-keygen` 과 ssh 서명을 하는 git 이 있어야 돈다(없으면 SKIP 한 줄).

## 시험
- 새 묶음 `fixtures_patch252_gitout.py`(장면 42 · 정적 둘 · 시험 177): C 사용자 설정 · 속성 22(색 넷 — IM24 둘 · plan 참조 조회 둘 · `diff.external` · `interHunkContext` · `grep.column` · 대조 기본 둘 · 서명 + `log.showSignature` 넷 · 대조 서명만 · `apply.whitespace` · `diff.algorithm=histogram` · 속성 드라이버 알고리즘 · `-diff` · textconv · 저장소 `.gitattributes` `binary` · 사용자 속성 `-diff` 아래 참조 조회 · 템플릿 참조 줄 · 속성 없이 내용 NUL 인 기능 JS) · N 이름 7(따옴표 · 탭 · 줄바꿈 · 역빗금 · BEL · 백스페이스 · CR 개명 · 승인 병합 · residual · `:` · U+2028 · 폼 피드 · 벤더 이름 둘 · residual 의 CR 이름 개명 · 미추적) · L 밖 읽기 3(plan · SDK 사본 링크 + `hash-object` 입력 기록 · O7 `..`) · T 갈래 10(T1 0T 끝 공백 · 빚 잔존의 web 범위 개명 조회 — T5 대조 web/ 밖 큰 변경 · T6 `diff.renameLimit=1` · T7 · T8 대조 web/ 밖 비슷한 · 같은 이름 파일 지움 · T9 · T10 대조 `diff.relative=true` 레인 · 승인 병합 · T11 대조 승인 병합 계보의 짝 · T13 하위 폴더만 — clean filter 로 잰 «프로젝트 밖 작업 파일을 git 자식에게도 읽히지 않음» · T16 대조 하위 폴더만 — 이름이 `:` 로 시작하는 하위 폴더의 승인 병합 · 번호는 검토 기록대로 둠) · S 정적 둘(실행 자리 표 대조 · 표본 28 — 표본마다 대조 규칙 하나에만 걸리게 갈라 그 규칙의 까닭을 단언한다(«새 실행 자리» 가 아닌 규칙의 표본은 그 표본 자리를 알려진 자리로 두어 뺀다). 대조 규칙 열넷 — 셸 실행 함수 · `shell=` · 튜플 · 경로 붙은 git · `*GIT_PINS` 없는 git 목록 · 실행 함수를 부르지 않고 꺼냄 둘(속성 · from 이름) · 새 실행 자리 · 모듈을 값으로 씀 · 별표 import · `sys.modules`/`__dict__` · 다시 내보낸 이름 · `import os.path` · `__import__` · importlib — 모두 그 규칙만 지운 사본에서 붉다). 설정은 장면마다 임시 전역 설정 파일(`GIT_CONFIG_GLOBAL`) · `GIT_CONFIG_NOSYSTEM=1` — 실행하는 사람의 전역 설정과 무관. 장면마다 꼴 · 하위 폴더 = 맨 위(0T 장면은 맨 위만 · T13 · T16 은 하위 폴더만) · R(고정 판 `RELEASE_251 = 11d84153` 은 그 꼴을 어겼다 / 대조 장면은 고정 판과 같다).
- 2.5.1 소스에 새 묶음만 넣으면 118/59 — 대조 장면 열(C8 · C13 · C19 · T5 · T7 ~ T11 · T16) 말고 모든 장면과 S1 이 붉다. 고친 자리를 하나씩 되돌린 사본 45 개는 모두 붉다(한 선택지만 뺀 것 포함 — `--no-textconv` · `--text` · `--diff-algorithm=myers` · `-l0` · `--no-relative` 둘 · `diff.autoRefreshIndex=false` · `hash-object` 입력의 링크 빼기 · `..` 거절 · git grep 의 사용자 속성 끄기 · 개명 조회 · 계보 조회를 저장소 전체로 넓힌 것 둘 · 정적 대조의 `sys.modules`/`__dict__` 규칙 · «모듈을 값으로 씀» 규칙 · 승인 HEAD 목록의 `:(top,literal)` · residual 의 bytes 읽기 셋 등).
- `fixtures_patch251_subfolder.py` — `BASELINE` 을 2.5.1 배포 커밋(`11d84153`)으로 올리고 `TOP_CHANGED` 를 비웠다(쓰지 않게 된 상수 둘 지움). `RELEASE_250` · `CASE_RED` 는 그대로.
- 다음 판에서 새 묶음의 `RELEASE_251` 은 올리지 않는다.
- 진단 · 설계 기록은 운영 scratch `w252/`.
