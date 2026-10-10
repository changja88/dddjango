---
name: discipline-test
description: dddjango-web이 생성한 코드의 회귀 안전망 테스트 규율 — 무엇을 테스트할지(무게중심)·오라클을 명세에서 끄는 법·헛테스트(vacuous)/디코이를 형태로 막는 단언 FORM·생략 목록·반송 규율. 테스트를 작성하거나 검수할 때 로드한다. Django·브라우저 테스트 메커니즘·결정성·더블 표기는 dddjango-web:implementation-test 소유.
user-invocable: false
---

# dddjango-web 테스트 규율

dddjango-web 테스트 = **회귀 안전망**(생성된 *명세-정확* 코드를 차후 수정으로부터 보호)이다 — 개발 드라이버(TDD)가 아니다(코드는 이미 생성됐다). 핵심은 **옳은(명세) 상태를 가두는 것**: 버그 상태를 가두면 디코이, 아무것도 안 가두면 헛테스트다. **단언 FORM·생략의 사실은 `references/final.md`가 단일 출처**이고, 이 본문은 그 사실을 쓰는 결정 규율이다. Django·브라우저 테스트 메커니즘·결정성·더블 표기는 implementation-test, 판정 소유(정렬·구별은 도메인)는 architecture-ddd, green 래칫·테스트 산출 의무는 coder 소유.

## 언제 쓰나

coder가 슬라이스의 행위 검증 테스트를 쓸 때, 또는 discipline-reviewer가 그 테스트의 비-vacuity를 감사할 때 로드한다. 전문을 읽지 말고 아래 표로 필요한 절만 부분 적재한다. 경계:

- Django 테스트 클라이언트·HTML 단언·브라우저 테스트 결정성·VM 대체·`unittest.mock` 더블·날짜 주입 헬퍼 → `implementation-test`
- 정렬·구별 등 판정이 누구 것인가(도메인 vs VM) → `architecture-ddd`(판정 소유 §5)
- 테스트 파일 위치(web_test/ = web 미러·sparse) → `discipline-houserules`(§1·§3)
- green 래칫·테스트 필수 산출 의무 → coder

## 핵심 운영 원칙

- **목적 = 회귀 안전망**: 명세-정확 행위를 가둬 *사후 수정*으로부터 지킨다 — 실사용처는 수정 모드다. 그래서 가두는 건 *현재 코드*가 아니라 *명세*다 (final.md §1).
- **오라클은 코드가 아니라 명세에서**: 기대값을 구현에서 베끼지 않는다 — LLM 생성 테스트의 구현-미러링이 디코이의 뿌리다(코드가 틀리면 테스트도 같이 틀린다) (final.md §2).
- **무게중심 = thick domain**: domain 판정·UseCase·Either 양갈래를 두텁게 → state/VM 상태전이·정렬/필터/매핑 → UI는 핵심 행위(탭→이동)만 얇게. 정렬·구별은 *도메인* 판정이라 도메인에서 두드린다 (final.md §1).
- **비-vacuity 자가점검**: "단언이 의존하는 로직을 한 곳 지웠다고 가정하면 red인가?" — '아니오'면 행위를 안 두드린 헛테스트다. §3 FORM으로 교체한다(존재만으론 닫히지 않는다) (final.md §2).
- **단언 형태로 디코이를 막는다**(§3.1만 충돌 시 자동 red·나머지는 형태 *가이드*·final.md §5 정직): 구별=집합 크기(`len({...}) == N` — 충돌 시 자동 red) / 매핑=case별 값 핀(`assert f(case) == 기대` 전수·필터 함수 직접 — swap 직격·distinct와 별개 축) / 순서=뒤섞은 입력(≠기대)+리스트 `==`+양끝 echo / 위치=`data-testid` 슬롯 선택자+비대칭·음수 fixture / 탭=non-edge(`[2]`·리스트 ≥3)+날짜-echo+상세 범위 안 정확 개수 `== 1`(`select_one`·`>= 1`·`in` 포함 검사는 "≥1"이라 금지). 셋업은 도메인 직접/VM 대체(repo 주입 seam 없음 — implementation-test §2). 5형 verbatim은 final.md §3.
- **생략한다**(테스트하지 않는다): getter·조건 없는 위임·private·템플릿 마크업 형태·시각 스타일·golden·프레임워크 내부 — 자명/구현-미러는 헛테스트를 부른다 (final.md §4).
- **반송 규율**: 명세-고정(spec-anchored) 테스트가 red면 *코드가 틀린* 것 — 코드를 고친다. 테스트를 약화·삭제해 green 만들지 않는다(discipline-reviewer FORM-감사 대상). 시도 한도 내 green 불가면 보고한다 (final.md §5).
- **날짜 결정성**: 도메인 판정은 기준일을 *인자로 받는 순수 함수*로 두고, 테스트는 고정 날짜를 주입한다 — `datetime.now()`·`timezone.now()` 실시각에 의존하는 테스트는 pre-commit에서 무관한 날 깨진다(주입 메커니즘은 implementation-test) (final.md §1).

- **영구 시험 재현성**: `web_test/`·호스트 시험 트리와 시험 지원 코드(`conftest.py`·`_support.py` 등)는 `.dddjango-web/`를 읽거나 쓰지 않고 프로젝트 루트 밖 머신 고정 고정물·기준판·캐시에 기대지 않는다. 기록 폴더(`.dddjango-web/`·`.dddjango/`)에 둔 시험 원문 사본은 영구 시험이 아니다 — 그 사본을 영구 시험으로 옮겨 오면 새 시험으로 본다. 고정물·기대 자료는 시험 트리에, 실행 기록은 `tmp_path` 등 임시 폴더에 둔다. 선택 도구 부재는 호스트 규칙대로 skip하고 설치된 도구의 고장은 실패로 남긴다. 레인 전용 환경 변수 존재 단언으로 실행 전제를 만들지 않는다 — 정상 환경 변수 행위 시험·필수 settings는 허용하며 환경 변수 의미 판정은 TG2 밖, discipline 감수와 G2 표준 실행이 확인한다.
- **이미지 비교 비채택**: 같은 실행·같은 브라우저의 옛 판 ↔ 지금 판 이미지 비교도 비채택이며, 승인 명세나 시험 목록에 있어도 예외가 아니다. 사람 눈 확인용 갈무리는 그대로 유지한다.

- **기존 시험 전환**: 같은 계약·같은 실패를 계속 보호한다. 메서드 자리 대응은 승인 함수에만, 함수 입구 전환은 별도 본인 승인 뒤 제품 고정 0T에서 준비·호출·전용 import만 바꾸며 정상 통과와 보호 실패별 옛/새 같은 단언 반례 실패·감수 B 0을 확인한 뒤 0C로 간다. 단언 유지와 값 잎 보존만으로 보존을 증명하지 않는다(final.md §1 · 허용 꼴과 생명주기는 discipline-houserules §8).

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| 왜 테스트하나·회귀 안전망·무게중심·날짜 결정성 | [`references/final.md`](references/final.md) §1 |
| 오라클을 명세에서 끄는 법·비-vacuity 자가점검 | final.md §2 |
| 단언 FORM 5형 verbatim(구별·매핑·순서·위치·탭)·Either 양갈래 | final.md §3 |
| 무엇을 생략하나 | final.md §4 |
| red일 때 코드 vs 테스트·reviewer FORM-감사 | final.md §5 |
| 테스트 클라이언트·HTML 단언·더블·VM 대체·날짜 주입 셋업 | `implementation-test` |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
