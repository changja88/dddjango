# 2.7.0 짓기 기록 — dddjango-web 시험 범위 좁히기 · 넓이 확인 · 브라우저 시험 꼴(TG4)

- 날짜: 2026-10-20. 배포 사본(저장소 clone · 앞 판 2.6.1 위)에서 지었다. 판 올림 · 커밋 · push · 배포는 이 기록 밖(`make release-web` 몫).
- 구현 기준: 설계 2판(§2 문면 블록 · §3 러너 · §4 픽스처 · §6 범위) · 좁은 재검토 · 시험판 · 시험판 도구 코드 검토 · 사용자 결정(슬라이스 끝 일꾼 최대 6). 판 계획 · 결정 · 숫자는 `plan-2.7.0.md`.

## 진행
1. **시험판 얹기** — 설계 §6-1 1 ~ 21 과 재검토 고침(R-B1 · R-I1 · R-I2 · R-S4 · R-S6) · G-5 (나)를 지은 시험판 두 플러그인 폴더를 배포 사본에 덮어 복사했다(더하고 바꾼 것만 — 지운 파일 없음). 바로 `make verify-web` 를 돌려 시험판 그대로 green 인지 확인했다(기준선 — 아래 «검증»).
2. **코드 고침**(동작 지킴 · 픽스처로 덮음 · Claude `scripts/` → Codex byte 미러) — 시험판 도구 코드 검토의 처분 표대로(아래 «처분»). 고칠 때마다 해당 픽스처 묶음을 돌렸고, 새 장면은 시험판 코드에서 먼저 붉음을 확인했다(시험 범위 26 붉음 · TG4 5 붉음 — 시험판 사본을 저장소 밖 임시 폴더에 복사해 돌림).
3. **사용자 결정 반영** — 슬라이스 끝 시험 줄 일꾼 최대 6(`SLICE_END_WORKERS` — auto · logical 은 `--maxprocesses=6` · 6 보다 큰 수는 `-n 6`) · 픽스처 S13 ~ S15e · 되돌림 변형 셋.
4. **문면** — 재검토 사소 · nit 처분(R-S3 · R-N4 ~ R-N8)과 시험판이 도구에 넣고 글에 옮기지 않은 동작을 discipline-houserules §8(TG4 · «시험 범위»)에, 한계 글(F4 · F5 · F7 · F11)을 같은 자리에 넣었다. Coordinator · coder-web 은 의미 미러, references 둘은 Claude 를 Codex 에 byte 복사.
5. **저장소 문서** — Makefile(MK-1 · MK-2) · AGENTS.md(AG 다섯) · README(RM 둘 — 프로젝트 전체 조건은 AG-1 과 같은 말) · docs/DEVELOPMENT.md(DV 셋) · 그림 문서 셋(«92종 → 93종» 9 자리 + 슬라이스 끝 «85종 → 86종» 두 자리 · TG 패밀리 «테스트 4종» · 패밀리 표 TG 4 · 합 93 · 표준 트리의 시험 도는 몫 설명 두 자리) · 가이드 페이지 coder-web 카드 · `plan-2.7.0.md` · 이 기록.
6. **검토 뒤 고침** — 글 검토 · 코드 검토 처분(아래 «검토 뒤 고침»).

## 처분 — 시험판 도구 코드 검토(F · D · T)와 재검토 남은 것(R)
| 번호 | 처분 | 자리 |
|---|---|---|
| F1 | 했음 | 단계 줄은 낱말마다 셸 따옴표로 다시 감싸되 `이름=값` 은 값만 감싼다(`_shell_word`) · `$` · 맨 앞 `~` · 앞 대입 값의 `~` · 글롭 `*?[` 가 든 낱말은 판정 불가 · 픽스처 W9c ~ W9g · S16 · 되돌림 변형 |
| F2 | 했음 | G2 더할 시험에 바뀐 W 밖 지원 모듈을 import 하는 W 밖 시험(한 걸음) · 바뀐 W 밖 conftest 폴더 · 픽스처 S17a · S17b · 되돌림 변형 |
| F3 | 했음 | `import a.b.c` 점 사슬을 맨 앞 이름보다 먼저 푼다 · 픽스처 F3 · 되돌림 변형 |
| F4 | 글로만 | `Test*` 클래스 안 도우미 메서드로 띄우기 = 지원 밖(§8 TG4) |
| F5 | 글로만 | 승인 병합이 들인 시험 파일을 이름만 바꾼 경우 = 늘어남으로 셀 수 있는 오탐 — Coordinator «검사기 이의»(§8 TG4) |
| F6 | 했음 | 해석 실패 파일의 이름 바꿈 짝도 두 쪽 셈에서 뺀다 · 픽스처 A7 · 되돌림 변형 |
| F7 | 글로만 | 바이트가 같아 읽지 않은 시험이 고친 지원 모듈 · conftest 를 거쳐 새로 띄우게 된 경우 = 지원 밖(§8 TG4) |
| F8 | 했음 | 값 받는 선택지에 `-r` · `--config-file` · `--override-ini`(`--numprocesses` 는 시험판에 있음) · 고르는 선택지에 `--sw-skip` · `--stepwise-skip` · 픽스처 W16a ~ W16e |
| F9 | 했음 | 설정 낱말 따옴표 오류 = 판정 불가 줄(traceback 아님) · 픽스처 W17 |
| F10 | 했음(R-N7 과 함께) | W 아래 파일 전부를 «프로젝트 전체 필요» 에서 뺀다 · 픽스처 P12 · P13 · 되돌림 변형 |
| F11 | 글로만 | 형제 import 미지원(모듈은 프로젝트 루트 기준) — §8 «시험 범위» · TG4 |
| F12 | 했음 | 산출물 폴더는 프로젝트 루트 기준 · `.dddjango-web/` 아래만(절대 경로도 받음) · 픽스처 W18a · W18b |
| F13 | 했음(줄 지움) | 글롭이 명령 읽기에서 판정 불가가 되어 `--ignore-glob` 앞부분 자르기가 죽은 줄 — 지웠다 |
| F14 | 했음 | `range` 길이의 OverflowError 를 판정 밖으로 · 픽스처 A8 |
| F15 | 했음 | 순환 도중의 «아님» 은 기억하지 않는다(맨 바깥 셈 · 순환 없는 셈만 기억) · 픽스처 F15 · 되돌림 변형 |
| D1 | 했음 | 죽은 갈래 · 중복 기록 폴더 확인 지움 · 시험 트리 JS 술어 `check_tests.js_in_test_tree` 하나 |
| D2 | 했음 | 마지막 회차의 현재판 쪽을 다시 씀 |
| D3 | 했음 | `Side.name` · `make()` 의 쓰지 않는 매개변수 · 쓰지 않는 지역 이름 |
| D4 | 했음 | TG4 기준판 git 읽기를 `subst` 도우미(`_git` · `_names` · `_tree`)로 · 알려진 실행 자리 표에서 한 줄 지움 |
| D5 | 했음 | 점 모듈 → 후보 파일 순수 도우미 `common.module_candidates`(존재 확인 · 거르기는 각자) |
| D6 | 했음 | `since_lines` 는 줄만 돌려준다 |
| D7 | 했음 | `git grep -f -`(표준 입력) — 임시 파일 · `tempfile` 지움 |
| D8 | 했음 | web 파일 · 폴더 집합은 한 번(ls-files) — `BackstopContext` 에서는 area 와 거꾸로 참조만 받는다(달라지는 곳은 web/ 아래 git 이 무시하는 .py 뿐) |
| D9 | 했음 | 한 줄짜리 `_docstring` 인라인 |
| D10 | 했음 | 고르는 선택지를 (이름, 값) 튜플로 |
| D11 | 안 함 | 지시(경우 수 세기 동작이 조금 바뀜 — 다음 판 후보) |
| D12 | 했음 | 픽스처의 쓰지 않는 매개변수 · 돌려준 값 |
| D13 | 안 함 | 지시(두 픽스처 공용 도우미 — 다음 판 후보) |
| T1 | 했음 | 바이트 같음 거르기를 blob id 견주기로(git 호출 없음) · 남는 기준점 쪽 읽기는 TG2 의 기준판 캐시를 함께 쓴다 |
| T2 | 했음 | 현재판 읽기 캐시 |
| T6 | 했음 | 바뀐 web 파일이 없으면 닫힘(`BackstopContext`)을 만들지 않는다 |
| T3 · T4 · T5 · T7 · T8 · T9 | 안 함 | 지시 밖(선택) — 다음 판 후보(`plan-2.7.0.md` §다음 판 후보 8) |
| R-S2 | 했음 | «바뀐 파일» 의 병합 유입을 승인 술어로 가름(상류판 그대로만 뺌 · 충돌 해소 · 미승인 · 목록 오류는 셈) · 픽스처 S12 · S12b ~ S12d · 되돌림 변형 둘 |
| R-N6 | 했음(코드 · 글) | TG4 브라우저 실행 파일 = 첫 낱말이 브라우저이거나 `--headless` 와 브라우저 전용 낱말이 함께 · `shell=True` 글자도 나눈다는 글 · 픽스처 N10 · P12 · 되돌림 변형 |
| R-N7 | 했음 | F10 과 함께 |
| R-N9 | 했음 | `test_web_paths` 원소가 다른 web 시험 경로의 조상 · 자손이면 판정 불가 · 픽스처 W8d · W8e |
| R-S1 · R-S3 · R-N1 ~ R-N5 · R-N8 · R-N10 | 했음(글) | 계획(R-S1 · R-N3 · R-N10 · R-S3 예시) · Coordinator G0 ㉡(R-S3) · README(R-N2) · 그림 문서(R-N1) · §8 «시험 범위»(R-N4 · R-N5) · implementation-test §1(R-N8) |
| R-S5 | 계획에만 | A/B 멈출 기준(메모리는 끝까지 돌린 뒤 묻기) |

설계 목록 밖으로 더한 작은 고침: 지운 conftest 폴더는 슬라이스 끝 · G2 줄에 넣지 않는다(없는 경로를 pytest 에 주지 않게).

## 검증
| 명령 · 대조 | 결과 |
|---|---|
| 시험판을 얹은 직후 `make verify-web`(기준선) | exit 0 · 묶음 합 PASS 4,981 / FAIL 0(시험 범위 82 · TG4 46) · 문단 · 역할 · scripts · references 대조 통과 |
| 새 장면을 시험판 코드에서(시험판 사본을 저장소 밖 임시 폴더에 복사) | 시험 범위 새 장면 26 붉음 · TG4 새 장면 5 붉음(되돌림 변형 줄은 «되돌릴 자리 없음»으로 붉음) — 고친 코드에서 모두 초록 |
| 최종 `make verify-web` | exit 0 · 묶음 합 **PASS 5,025 / FAIL 0**(시험 범위 116 · TG4 56 · 나머지 묶음은 기준선과 같은 수) · self-test 두 자리 106절 · 27어구 · 18표본 · red 0 · 입구 표지 · 문단 Claude·Codex 대조(새 표지 다섯 포함) · 역할 7 · scripts/assets byte · references 12 byte 대조 통과 |
| `diff -rq --exclude=__pycache__ --exclude=test dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts` | 출력 없음 |
| references 둘(`discipline-houserules` · `implementation-test`) `cmp` | 같음 |
| 빚 지문 · 종수 · 미룸(`debt.scanner_stamp()['checks']` · `TOTAL_CHECKS` · `SLICE_END_DEFERRED`) | `e49c83776ff9faf6 93 7`(지문 2.6.1 과 같음) |
| `claude plugin validate dddjango-web --strict`(설정 폴더를 임시 자리로) | `✔ Validation passed` |
| `git diff --check` | 출력 없음 |
| `make verify`(병렬 6 타깃) | verify-ontology · verify-base-backstop · verify-base-cross · verify-base-regen green. verify-base-core 는 검증 세트가 모두 일치한 뒤 manifest 봉인 대조만 붉음(`봉인 후 변경 — Makefile` · `tree_sha256 드리프트` — Makefile 을 바꾼 판의 정해진 꼴 · 커밋 뒤 봉인 재발행 chore 몫). verify-base-probe 는 부하가 높을 때(load 50 안팎) core 탐침 한 사례(xdist 워커 출력)가 한 번 달랐고, 그 사례만 세 번 · 타깃 전체 한 번 다시 돌려 510/510 일치(이 판은 core 를 바꾸지 않았다) |

- 새 모듈 크기: `scope.py` 1,006줄(시험판 933 — 고침 · 승인 술어 · 일꾼 상한 더함 · 덜어 내기 뺌) · `check_browser.py` 904줄(시험판 914).

## 검토 뒤 고침
글 검토(차단 0 · 중요 2 · 사소 10 · nit 8)와 코드 검토(차단 0 · 중요 2 · 사소 2 · nit 1)의 처분.

| 번호 | 처분 | 자리 |
|---|---|---|
| 글 I1 | 했음 | 계획 «사용자 결정»에 G-4 답(«두자.») 줄 · G-4 비용 줄을 답 받음으로 |
| 글 I2 | 했음 | 표준 트리 그림 — 슬라이스 끝 86종 · 패밀리 표 TG 4(TG4 설명 · 발화 범위) · 합계 93 · 시험 도는 몫 설명 두 자리(계층 중 · 슬라이스 끝 좁힌 실행 · G2 한 번). 같은 옛 설명이 남은 가이드 페이지 coder-web 카드도 |
| 글 S1 ~ S10 | 했음 | 빌드 기록 낡은 줄 · 사용자 말과 운영자 해석 가름 · Coordinator 일꾼 요약(`--maxprocesses`) · 완성 화면 그림 `-n0` · 따옴표 안 글롭 · F5 는 «검사기 이의»(오탐) · 감수자 «그 밖 §8 TG4 지원 밖 꼴» · 실행문 미실행 보고의 처분 · G2 배너 시험 행 열거 · 계획 메모리 줄 · TG4 픽스처 이름(고정물 · 화면 자리)을 일반 이름으로 |
| 글 nit | 했음(N3 · N4 · N5 그대로) | 21 시험 · A/B 감수 단서 · G-5 사전 확인 숫자 · coder-web 일꾼 괄호 자리 · AGENTS 판정 불가 · 도구 운용 메모 줄 지움 · N3 은 다음 판 후보 12 |
| 코드 A-I1 | 했음 | `scope._grep` 에 `-c grep.fullName=false -c core.attributesFile=`(빚 참조 grep 과 같은 고정) · 픽스처 S18a(하위 폴더 루트 + `grep.fullName=true`) · S18b(사용자 전역 속성 `*.py -diff`) · 되돌림 변형 |
| 코드 A-I2 | 했음 | G2 더할 시험에 바뀐 W 밖 지원 모듈을 import 하는 W 밖 conftest 의 폴더(한 걸음) — 루트 conftest 면 «프로젝트 전체 필요 — 루트 conftest 가 import 하는 지원 모듈 <파일>» · 픽스처 S17c · S17d · 되돌림 변형 · §8 «시험 범위» |
| 코드 A-S1 | 했음 | 슬라이스 끝 상한 — auto · logical 은 그 값을 두고 `--maxprocesses=6`(이미 6 이하면 그대로 · 단계의 더 큰 값은 뺌) · 6 보다 큰 수는 `-n 6` · 그 밖 그대로(`Stage._capped` · `maxprocesses_at`) · 환경 접두 일꾼 설정은 읽지 않는다는 한계 글 · 픽스처 S13 · S13c ~ S13e · S15b · S15d · S15e · 되돌림 변형(auto 를 `-n 6` 으로) |
| 코드 A-S2 | 글로만 | W 밖 시험 트리 비-.py 러너 바꿈은 도구가 잡지 않는다(감수 몫) — §8 «시험 범위» · 계획 «한계» · 다음 판 후보 11 |
| 코드 A-N1 | 했음 | 중괄호 펼침(`{` · `}`)이 든 낱말도 판정 불가 · 픽스처 W9h |

새 장면은 고치기 전 코드에서 먼저 붉음을 확인했다(W9h · S13 · S13c · S13e · S15b · S17c · S17d · S18a · S18b — 9 붉음 · S13d · S15d · S15e 는 고치기 전에도 초록인 지킴 장면).

| 명령 · 대조 | 결과 |
|---|---|
| 검토 고침 뒤 `make verify-web` | exit 0 · FAIL 0 — 시험 범위 129(+13) · TG4 56 · 나머지 묶음은 앞 실행과 같은 수 · self-test 두 자리 red 0 · 입구 표지 · 문단 Claude·Codex 대조 · 역할 7 · scripts/assets byte · references 12 byte 대조 통과 |
| `git diff --check` · scripts byte 미러 · references 12 | 출력 없음 · 같음 · 같음 |

- 새 모듈 크기(검토 고침 뒤): `scope.py` 1,028줄.

## 안 한 것 · 운영자 확인
- 판 올림(`plugin.json` 2.6.1 그대로) · 커밋 · 봉인 재발행 · push · 태그 · 배포는 하지 않았다.
- 작은 A/B ② 숫자 · 슬라이스 끝 `-n 6` 측정은 운영자가 채웠다(계획 «작은 A/B» · «슬라이스 끝 일꾼 수»).
