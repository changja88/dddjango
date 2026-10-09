# dddjango-web 2.2.5 — 현장 보고 다섯(F4-64 · 65 · 66 · 68 · 69) (운영자 · 10-10 · 진단 · 설계 점검 · 구현 · 구현 검토 · 보완 셋 · 실제 장면 반영판)

## 바탕
- 바탕: R main `6090d3c5`(dddjango-web 2.2.4). 2.2.5 는 패치다 — 검사 84 → 86(TG2 · TG3 새로) · NM17 좁은 예외 · 글 맞춤.
- 사본 `<S>/web-225`(가지 `web-225`). `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`. 근거 기록 `<S>/web-225-notes/`(진단 · 계획 · 설계 점검 · 구현 · 구현 검토 · fix-1 ~ 3 · 재검토 · 실제 장면 로그).
- 현장 보고: `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md` F4-64(6-3-23) · F4-65(6-3-29 G0 멈춤) · F4-66 · F4-68 · F4-69(6-3-26 멈춤).
- 사용자(글자 그대로):
  - «워크트리에서 발생한 오류 보고야 확인하고 절차대로 수정진행해서 배포해줘»(10-10 03:36:46 date 뒤 · 03:47:42 date 앞).
  - 결정 11 «나.»(04:06:56 date 뒤 · 04:07:34 date 앞) = 홈 같은 기본 주소 하나만 그 주인 BC navigator 가 주인 router 상수를 가공 없이 돌려준다.
  - 결정 12 «가.»(04:07:34 date 뒤 · 04:07:59 date 앞) = 아이콘 글리프여도 font-size 는 토큰 · 폭 · 박스 높이는 기존 직접 인용.

## 판정과 넣은 것
| 항목 | 뿌리 | 넣은 것 |
|---|---|---|
| F4-68 View 파일의 필드 전용 타입 Protocol | NM17 이 주 view · 조각 함수 밖 모든 클래스를 막음(글은 함수만 말함 · dddart 는 타입 동거 허용) | NM17 좁은 예외: private 이름 · import 해석으로 확정된 `typing(_extensions).Protocol` 하나 · class keyword · 데코레이터 없음 · 값 없는 단순 `AnnAssign` 만(annotation 안 실행식 없음) · 별칭 재바인딩(wildcard import · 패턴 capture · 선언 시 실행 대입 · global) · 해석 실패면 면제 없음 · 소비 경계(호출 · isinstance 금지)는 감수 · 글 UI §2 · houserules §4 · 사용자 문구 |
| F4-69 아이콘 글리프 font-size | 규약 내부 충돌(UI §8 «아이콘 크기 직접 인용» ↔ §7 · houserules «font-size 는 토큰») | 결정 12 대로 글 맞춤(UI §7 · §8 · houserules §6 · Django · architect · discipline-reviewer · 요약): `font-size` 는 `app_spacing.css` 의 `--spacing-icon-*` · NM10 판정 무변 |
| F4-66 URLconf 독립 기본 홈 주소 | 규칙 빈자리(일반 이동은 이름 기반 · 기본 주소 계약 없음) | 결정 11 대로 글(UI §6 · 요약 · houserules 정의 · 채널 ③ · 트리 주석 · drift 표 · Django §2 · review-ui · state · ddd 연결) · 검사기 무변(IM5 · NM13 · IM10 · IM21 · CY1 에 안 걸림) · 특정 BC 고정 · 상수 복제 · 폴백 금지 |
| F4-65 같은 실행 옛 판 ↔ 지금 판 이미지 비교 | 비채택 규칙은 있었으나 G1 · 감수가 집행하지 않음 | 글(implementation-test §8 · discipline-test §4 · 요약 · architect 행위별 시험 방법 · review-ui · coder · discipline 순서) · Coordinator 두 벌 «**시험 방법 채택 확인**» 한 줄 문단(G1 · override 뒤 · G1′ 직접) · 새 검사 **TG3**(닫힌 단언 API · 서로 다른 두 screenshot 결과 비교 · 실행 JS 의 `.equals` / `Buffer.compare` · JS 실행기로 확정된 명령만) |
| F4-64 영구 시험의 기록 폴더 · 머신 경로 · 레인 변수 기댐 | 막는 관문이 없음 | 글(implementation-test §4 · §7 · discipline-test · coder · discipline) · Coordinator 두 벌 «**영구 시험 표준 실행**» 한 줄 문단(G0 확정 · G2 · 수정 모드는 레인 추가 변수만 뺀 같은 명령) · 새 검사 **TG2**(`--diff-base` 기준 바뀐 영구 시험 · 지원 파일의 **바뀐 줄에 걸린 사슬만** — `.dddjango-web` · 루트 밖 절대 경로 · `Path.home()` → 파일 I/O · 서버 실행 · subprocess · 실행 JS) |

- TG2 · TG3 은 슬라이스 끝에도 돈다(미룸 7 그대로) · 86 / 79 / 7 표기 · Makefile verify-web 문단 대조에 두 새 문단.

## 넣지 않은 것
- 환경 변수 단언의 자동 판정(감수 · G2 표준 실행 몫).
- 동적 경로 · 함수 간 전달 · 파일 저장 뒤 재읽기 · 해시 · 자유 하니스의 자동 판정(감수 몫 — `[info] TG2 일부 흐름 자동 판정 밖` 고지).

## 멈출 기준과 결과
| 기준 | 결과 |
|---|---|
| S1 픽스처 · `make verify-web` | 1,327 실패 0 · exit 0(fix-5 뒤) |
| S2 6-3-26 슬라이스 0 고정본(8c920b6da + 미커밋 202 · `--diff-base 613ef8e0` · `--slice-end`) | 2.2.4 NM17 25 · NM10 2 → **NM17 22(Protocol 3 해제 · 추가 함수 22 그대로) · NM10 2 · TG2 0** |
| S2 6-3-23 착륙 커밋 ab406b8fc(`--diff-base` 첫 부모) | **TG2 7 · TG3 1**(216행 JS 이미지 비교 · 18행 캐시 절대 경로가 338행 서버 실행에 · 기록 폴더 고정물 실행 24 · 쓰기 325 · 328 · 실행 JS 쓰기 181 · 213 · 214 — 340 행 node argv 의 기록 폴더 값은 그것을 쓰는 JS 쓰기 자리에서 잡힘) |
| S2 호스트 main bd783acde(`--diff-base 705e2cd72` = 6-3-21 착륙분 · 그리고 최근 커밋 약 40개 범위) | **TG 0 · exit 0** |
| 설계 점검 · 구현 검토(Codex) | 설계 «보완 후 진행» 반영 · 구현 검토 «고칠 것 8» → fix-1 · 운영자 실측 회귀 둘 → fix-2(build-state 하나의 해소 실패가 전체를 끔) · fix-3(조건식 sink 놓침 · 여러 줄 호출 전체를 바뀐 줄로 봄) · 재검토 «고칠 것 6»(TG3 호출 범위 · with 항목 순서 · JS 미사용 argv / eval 코드 재발화 · node `--` 뒤 인자 · typeof 뒤 정규식 · 세미콜론 없는 JS 놓침) + test_command 형상 격리 → fix-4 · 마지막 재검토(배포 차단 기준만 — 차단 1: 컴프리헨션 반복 변수 스코프) → fix-5 |

## 알려진 한계
- TG2 · TG3 의 자동 판정은 docstring 의 지원 꼴까지다(동적 경로 · 함수 간 전달 · 재읽기 · 해시 · 동적 iter 출처는 감수).
- 마지막 재검토가 남긴 드문 경계: 내용이 바뀐 미추적 이동은 새 파일로 취급될 수 있음 · 클래스 몸통의 `t.Protocol = object` 같은 모듈 attribute 변경은 뒤 Protocol 의 확정성을 유지할 수 있음(그 클래스 자체는 NM17 로 막힘).
- 하드코딩 실행 파일 절대 경로(예: `/opt/homebrew/bin/node`)도 TG2 대상이다(`shutil.which` 결과만 제외) — 바뀐 줄에 걸릴 때만 선다.
- 6-3-26 은 이 판으로 Protocol 3건만 풀린다 — 추가 함수 22건 · 로그인 typography 1건 · 아이콘 raw 16px(결정 12 로 토큰 필요)은 레인 몫으로 남는다.
- 진행 중 web 레인은 판 올림으로 TG2 · TG3 이 새로 돈다(바뀐 줄 한정).
