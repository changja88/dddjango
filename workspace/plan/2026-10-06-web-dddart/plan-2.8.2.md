# dddjango-web 2.8.2 — 임베드 받는 페이지 머리의 자식 조각 CSS (IM5 예외 하나 · F4-120)

## 문제
- 문서 이동 셸 페이지가 채널 ④ 로 다른 BC view 를 임베드하면, 그 임베드가 그리는 자식 BC 조각 CSS 를 실을 자리가 없었다.
  규칙 글은 «조각 응답에는 `<link>` 를 넣지 않는다 · 부품 CSS 는 받는 문서가 싣는다»(implementation-django §10)인데, 받는 페이지
  `{% block head %}` 의 `{% static %}` link 는 IM5(교차 BC 4채널 밖)였다 — 다른 BC 조각 CSS 는 `ref_path` 로
  `…/presentation_layer/<f>.css` 가 되어 view 채널에 들지 않는다. 통과하는 길은 셸 머리(root — 4채널 면제)뿐이라 한 화면의 CSS 가
  셸의 모든 화면에 실렸다.
- 지속 셸은 SH4 가 셸 머리에 그 제품 BC CSS 전부를 요구하고 페이지 block head 는 SH3 금지라 이 문제가 없다.

## 고침
- **IM5 예외 하나**(`scripts/src/embed.py` 새 모듈 · `check_imports.py` IM5 정적 참조 갈래): 문서 셸(선언된 셸 집합)을 글자
  `{% extends %}` 로 상속한 페이지가 셸 `<head>` 안 block(이름은 셸에서 읽는다)에서 `{% static %}` link 로, 그 페이지가 채널 ④ 로
  실제로 임베드한 자식 view 가 그리는 템플릿의 짝 조각 CSS 를 실으면 IM5 가 아니다. 러너가 글자로 따라가는 증거 네 고리:
  ① 자리 — 페이지와 그 include 닫힘이 실제로 그리는 요소의 `hx-get` · `data-hx-get` 값 `{{ <점 이름> }}`(extends 한 템플릿은 사슬이
  정의한 block 안만 · verbatim 은 글자 · include 닫힘도 그려지는 include 만) ② href — 짝 VM 이 칸 이름 키워드 · 같은 이름 대입의 값으로
  바로 자식 navigator 호출(들여온 원래 클래스) ③ 라우트 — 그 메서드의 `reverse` 첫 인자 라우트가 모두 `<화면>_embed_fragment`(router
  별칭은 원래 이름 · 동기 · async) ④ 렌더 — 그 함수가 render 하는 템플릿과 그 include 닫힘 가운데 그 BC view · section · widget 의 짝 CSS.
  자식의 자식 · 같은 BC view 경유 · 제품을 넘는 임베드도 같다. 허용 대조는 꼬리(`?v=`) · 앞머리 `/` 를 뗀 실제 파일.
- **위반 줄은 그 참조와 그 파일만으로**(승인 유입 `inflow._key` · 조정자 «검사기 이의» 대조의 키): 자리 맞음 꼴
  «… — 타 BC `application/<c>/` 임베드 증거가 없다(…)» · 그 밖 꼴 «… — 교차 BC 정적 참조는 이 자리에서 받지 않는다(문서 이동 셸이면 …)».
  «없다» 대상이 BC 폴더라 조정자 기존 미룸 ⓐ 가 받는다(자식 화면이 뒤 슬라이스면 그 끝에 선다 · 조정자 글 무변).
- **교정 줄(키 밖 · 한 줄)은 셸 방식으로**: 지속 셸 = SH4 갈래(다른 제품 BC 면 theme 뒤 덧줄 안내) · 문서 이동 셸 자리 맞음 = 첫 빈 고리
  + 네 고리 · 그 밖 = 그 자리가 왜 예외가 아닌지.
- **증거 파싱 경고 막음**: 증거로 읽는 파이썬의 `ast.parse` 를 `warnings.catch_warnings()` 로 감싼다 — 잘못된 이스케이프의
  SyntaxWarning 이 stderr 로 새면 승인 유입의 부모 측정이 무효가 된다.
- 링크 · 실제 경로가 web 밖인 증거 파일은 증거 없음(2.5.2 밖 읽기 막음과 같은 뜻) · git 은 부르지 않는다 · 컨텍스트 캐시는
  getattr/setattr. 판정할 새 줄에서만 증거를 읽는다.
- 새 검사 ID · 패밀리 · 빚 지문 · 빚 키 의미론 · build-state 칸 · 게이트 · 조정자 글 무변. 판정은 완화만(정적 참조 IM5 의 문구만 바뀜).

## 바뀐 파일
- 검사기: `dddjango-web/scripts/src/embed.py`(새) · `scripts/src/check_imports.py` · `scripts/backstop.py`(머리 주석) — Codex byte 미러.
- 규칙 글: discipline-houserules §5(참조 문단 끝 · 채널 ④ 행 · 새 문단 «교차 BC CSS — 임베드 받는 페이지 머리만») · §8(교차 BC CSS 게이트 ·
  못 읽는 꼴 · 받아들인 한계) · implementation-django §10 «조각 CSS» · implementation-htmx §7 · SKILL.md 둘(houserules · implementation-django) ·
  역할 셋(design-architect-web · design-review-ui-web · discipline-reviewer-web) — references byte 미러 · SKILL.md · 역할 의미 미러.
- 고정물: `scripts/test/fixtures_patch282_embed_css.py`(새) + `run_fixtures.sh` 한 줄. F8 그대로.

## 시험(`fixtures_patch282_embed_css.py` — 비교 판은 2.8.1 배포 커밋 상수 · HEAD 에 묶지 않음)
- R 받음(2.8.1 IM5 → 0): 기본 꼴 · 현장 꼴(area 부모 · 개념 1차 자식 · 도우미 키워드 · 두 단 include `{% elif %}` · 자식 view · section ·
  widget · 손주 허용 / 임베드 안 한 화면 · 손주가 그리지 않는 view · 본문 link 막음) · 손주 · 같은 BC view 경유 · `?v=` · 앞머리 `/` ·
  async · 규칙 예 꼴 · 중첩 칸 · 제품 한 개 · 두 제품 · 머리 block 이름이 head 가 아닌 셸 · `--slice-end` · 게이트 전체.
- S 그대로(2.8.1 과 그 파일의 IM5 줄 같음): 증거 없음 · 지역 이름 경유 · 일반 라우트 · 렌더 닫힘 밖 CSS · 본문 link · `@import` ·
  section 템플릿 link · block 밖 · 셸에 없는 block · verbatim · 다른 속성 이름 · 글자 본문 · navigator 두 클래스 · 임베드 상수 읽기만 ·
  extends 없는 view · router 별칭 · include `with` 이름 바꿈 · 모듈째 import · 링크(VM · 템플릿) · 그려지지 않는 include 셋 · textarea ·
  다른 속성 값 · 증거를 지운 커밋의 옛 줄 · `..` · PRE1(둘 다 0 — 이 판 밖).
- K 위반 줄 키: 증거 파일만 다른 네 트리의 `위반:` 줄 글자 같음 · 교정 줄 넷 다름 · 한 줄 · 부모 측정 꼴 판독 · 키 같음.
- H 셸 갈래 · W 경고(게이트 · 부모 측정 stderr 없음) · D 빚 지문(키 하나만 사라짐 · 지문 같음).
- M 검사기 변이 열다섯 — 조건 하나(셸 extends · 렌더 뷰 둘 · 속성 이름 · 원래 클래스 · reverse 첫 인자 · router 별칭 · 링크 · 렌더 닫힘 ·
  자식의 자식 · 꼬리 · 앞머리 `/` · async · 경고 막음 · 위반 줄 키)를 빼면 그 장면이 뒤집힌다.

## 받아들인 한계(해는 «안 쓰는 다른 BC CSS 한 줄 실음»)
- 정적 거짓 가지(`{% if False %}`) 안 자리 · VM 의 부르지 않는 함수 · 다른 State 생성 안 같은 이름 키워드 · navigator 의 같은 이름 클래스
  두 번 정의(앞 것을 읽는다) · 버린 reverse 뒤 다른 값을 돌려주는 메서드.
- 못 읽는 꼴은 모두 IM5 쪽(보수): 변수 include · include `with` 이름 바꿈 · 필터 붙은 hx-get · 지역 이름 · 함수 반환 · 조건식 경유 href ·
  navigator 모듈째 import · 도우미를 거친 render · 동적 템플릿 · path 이름 위치 인자 · 위임 navigator · JS 로 여는 자리.
- 받는 문서가 자식 CSS 를 아예 싣지 않는 빠짐은 러너가 잡지 않는다(설계 파일 목록 문서 행 · UI 리뷰 · 감수 몫).
- 증거는 다른 파일이라 증거를 지워도 옛 link 줄은 새 줄이 아니다(게이트 — IM13 과 같은 선택 · 빚 스캔은 전수).
- 정적 참조 IM5 의 위반 문장이 바뀌어, 2.8.1 에서 «플러그인 결함» 으로 처분한 정적 참조 IM5 줄은 판 올림 뒤 한 번 다시 묻는다.
- 누름 · JS 로 여는 층(채널 ④ 꼴이 아닌 화면)은 이 판으로 받지 않는다 — 그 화면을 임베드 꼴로 고치는 별도 요청.

## 다음 강화 판 후보(minor 권장 — 빚 결과가 바뀌는 강화)
- `..` 정적 경로 구멍: `{% static 'web/application/<자기 BC>/../<다른 BC>/….css' %}` 는 `static_target` 이 `..` 를 접지 않아 자기 BC 로
  읽혀 IM5 를 비켜 간다. IM5 정적 참조 분류를 `loaded_file` 로 바꾸면 막히지만 빚 스캔에 새 키가 생기고 개명 파일의 옛 줄이 새로
  붉다(진행 중 리팩토링 레인이 G2 에서 낯선 blocker 를 만난다) — 배포 알림과 함께 따로 낸다.
- PRE1: `static/application/<bc>/view/x.css` 처럼 BC 정적 폴더 아래 `view/` 를 두면 view 채널로 지나간다(새 파일은 NM19 · ST12 가 잡고
  남는 것은 옛 파일) — 같은 판에서 정적 참조에는 view 채널 `ok` 를 쓰지 않게.
- 빠짐 검사: `embed.py` 로 «임베드 조각 → 받는 문서» 를 이어 CS 쪽 새 검사(빚 스캔 밖).

## 검증
- `make verify-web` rc=0(고침 전 사본도 rc=0) — 본 묶음 PASS 171 / FAIL 0(F8 그대로) · 새 묶음 `2.8.2 임베드 CSS 픽스처: PASS 138 / FAIL 0` ·
  나머지 하위 묶음 FAIL 0 · Codex scripts · references byte 미러 대조 같음.
- `make verify` green 6/6(`[manifest]` green — 봉인 대상 무변).
- `claude plugin validate dddjango-web --strict` 통과.
