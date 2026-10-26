# dddjango 2.27.3 — 앞 두 판의 남은 몫(F4-121 사소 · F4-115 사소) · Python 3.12 ~ 3.14 pre-gate 실행 불능 (10-26)

## 바탕
- 바탕: main(dddjango 2.27.2 봉인 뒤). 2.27.3 은 patch — 새 질문 · 새 흐름 · 새 기록 칸 · 규범 문면 변경 없음. 매니페스트 판은 `make release` 가 올린다. dddjango-web 무변.
- 몫 셋:
  - **A**(F4-121 사소 1 ~ 4): 리팩토링 `refactor_audit.py deps` 의 HTTP 소비 셈에서 `.html` 주석을 지우는 낱말 끊기가 Django · 브라우저와 달라 실제 주소를 덜 세거나 주석 속 주소를 더 셌다.
  - **B**(F4-115 사소 s1 ~ s3): pre-gate 번역 출처 칸의 기존 빚 열쇠 — plan-2.27.0 한계 3 의 글이 갈래를 틀리게 불렀고, 열쇠를 넓히거나 차례를 바꾸는 변이를 막는 시험이 없었다.
  - **C**(2.27.0 에서 들어온 결함 · 이번 판에서 찾음 — 장부 번호 없음): Python 3.12 ~ 3.14 로 pre-gate 를 돌리면 번역 출처 칸이 있는 명세에서 «실행 불능» 으로 끝났다.
- 설계: 1판(재현 · Django 6.1 · Chromium 실측 · 시제품) → 적대 검토(고친 뒤 구현 · 차단 0 · 중요 3 · 사소 8) → 운영자 결정 → 구현.

## A — deps `.html` 주석 지우기를 Django · 브라우저와 맞춤(F4-121 사소)

원칙(plan-2.27.1)은 그대로다: **실행될 때 주소로 쓰일 수 없는 글만 뺀다 · 모를 때 원문.** 덜 셈(실행 때 쓰이는 주소를 지움)은 결함이다.

### 결함(2.27.1 재현)
- 사소 1: 짝 없는 `{%` · `{{` 가 여러 줄 뒤의 `%}` · `}}` 와 맞물려 사이 글(예: `<script>` 안 옛 숨김 `<!--` 속 `fetch`)을 주석으로 지움 — 덜 셈.
- 사소 2: 이름 붙은 `{% verbatim 이름 %}` 안의 이름 없는 `{% endverbatim %}` 에서 verbatim 을 닫아 그 뒤 `{# #}`(Django 는 글자로 냄)를 지움 — 덜 셈.
- 사소 3: `--!>` 로 닫힌 HTML 주석(브라우저는 닫음)을 닫히지 않은 것으로 봄 — 그 뒤 주석까지 지워 덜 셈 · `--!>` 만 있으면 주석 속 주소를 더 셈.
- 같은 뿌리의 덜 셈: Django 변수 문자열 속 `{#` · `{% comment %}`(`{{ "{#" }}` — Django 는 왼쪽부터 낱말을 끊어 변수로 읽음) · 날 글 요소 xmp · iframe · noembed · noframes · noscript 안의 `<!--`.
- 같은 뿌리의 더 셈: 짝 없는 `{%` 뒤 주석 · `{% comment %}` 안 verbatim 속 `{% endcomment %}`(Django 는 글자로 보고 뒤 endcomment 까지 주석).
- 사소 4: 원문 계열(`.js` · 주석 없는 `.html`) 글 전체 훑기의 (파일, 줄, 공급 BC) 가 줄마다 센 옛 판과 같음을 보이는 시험이 없었다(동작은 맞음).
- 검토 A-I1(2.27.1 부터): 날 글 요소의 끝을 `</script` 뒤가 `'` · `"` · `.` 여도 끝으로 봤다. 브라우저 «맞는 끝 태그» 는 이름 뒤가 탭 · LF · FF · 공백 · `/` · `>` 일 때뿐이다. 그래서 `document.write('…</script' + '>')` 뒤 script 본문의 옛 숨김 `<!-- … -->` 를 주석으로 지웠다(Chromium 에서 `fetch` 가 실제로 불림). 1판 시제품은 `--!>` 닫힘과 맞물려 2.27.1 이 세던 꼴 하나(`// --!>` 로 닫는 옛 숨김)를 새로 놓쳤다.

### 고침(`dddjango/scripts/refactor_audit.py` · Codex byte 미러)
- `_mask_django` 신설 — Django 렉서 · 파서 꼴 그대로 왼쪽부터 한 번 훑는다(옛 `_DJANGO_COMMENT` 정규식은 지움).
  - 낱말 `_DJANGO_TAG` = Django `tag_re` 와 같은 글(re.S 없음 — 태그 · 변수 · 주석은 한 줄 안).
  - verbatim: `{% verbatim[ 이름] %}` 부터 내용이 정확히 `endverbatim[ 이름]` 인 낱말까지 모든 낱말은 글자.
  - `{% comment … %}` 부터 그 뒤 첫 `{% endcomment %}` 낱말까지 지운다(닫는 태그가 없으면 Django 오류라 지우지 않는다). `{# #}` 는 verbatim · comment 밖에서만 지운다.
- Django 단계는 `{#` 가 있거나 `{%` 와 `comment` 가 함께 있을 때만 돈다(주석 없는 큰 템플릿은 건너뜀).
- HTML 단계(`_HTML_TOKEN`): 주석 닫힘에 `--!>` · 날 글 요소 다섯 더함(`_HTML_RAW` 한 곳) · 날 글 요소 끝은 이름 뒤가 탭 · LF · FF · CR · 공백 · `/` · `>` 일 때만(A-I1 · 못 찾으면 지금처럼 원문) · 템플릿 태그 · 변수 낱말은 한 줄 안 · 짝 없는 `{%` · `{{` 는 «닫히지 않은 것» 이 아니라 글자(Django 와 같음).
- `_lone_openers_blanked`(A-S1 — 선형 시간): 짝 없는 여는 글마다 정규식이 줄 끝까지 훑으면 긴 한 줄에 수천 개일 때 제곱 시간이다(9.6만 자 한 줄 · 8천 개에 5 초 — Django 렉서도 같은 글에서 같은 제곱). 그래서 낱말을 끊기 전에, 같은 줄 뒤에 닫는 글이 없는 `{%` · `{{` · `{#` 의 `{` 를 다른 글자로 바꾼 사본을 만든다(글자 자리 그대로 · 낱말 판정 전용 — 지울 글은 원문에서 자른다). 그런 여는 글은 어느 쪽 정규식에서도 낱말을 만들지 못하므로 낱말은 같다. 바로 앞 `{` 와 이어 닫히는 `{{` 를 이루는 자리는 두고, 줄 끝까지 256 자가 안 남은 것은 훑어도 싸서 둔다.
  - 선형 전 고친 판과 결과가 같음: 무작위 템플릿(조각 87 종 · 2 ~ 30 조각) 180만 개 · 문턱(256)을 0 · 1 · 3 · 8 로 낮춘 실행 포함 · `_mask_html` · `_mask_django` 결과 다름 0.

### 적대 검토 반영
| 항목 | 반영 |
|---|---|
| A-I1 날 글 요소의 거짓 끝 | 끝 태그를 브라우저 «맞는 끝 태그» 꼴로. 시험 F16 · F17. |
| A-S1 긴 한 줄의 제곱 시간 | 선형으로 만듦(위 `_lone_openers_blanked`). 시험 U8a ~ U8c. |
| A-S2 Django 밖 엔진의 여러 줄 태그 | 받아들인 한계 4 에 적음. |
| A-S3 2.27.1 부터 있던 덜 세는 길 | 받아들인 한계 3 을 넓혀 적음. |

### 시험(`workspace/tools/refactor_audit_fixture_run.py` — `deps_http_text_cases` · 접두 `RD-F121`)
| 사례 | 꼴 | 2.27.1 | 2.27.3 |
|---|---|---|---|
| T11 | 짝 없는 `{%` 뒤 다른 줄 HTML 주석 → 세지 않음 | ✗ | ✓ |
| T12 | `--!>` 로 닫힌 주석 → 세지 않음 | ✗ | ✓ |
| T13 | 이름까지 같은 endverbatim 뒤 `{# #}` → 세지 않음(지킬 꼴) | ✓ | ✓ |
| T14 | comment 안 verbatim 속 `{% endcomment %}` → 뒤 endcomment 까지 주석 | ✗ | ✓ |
| F11 ~ F15 | 짝 없는 `{%` · script 문자열 `%}` · 옛 숨김 `fetch` / 이름 붙은 verbatim 안 이름 없는 endverbatim / `--!>` 뒤 속성 / xmp 안 `<!--` / 변수 문자열 속 `{#` → 셈 | ✗ ×5 | ✓ |
| F16 | `<script>` 안 `</script` 뒤가 `'` · 옛 숨김 `<!-- … -->` 안 `fetch` → 셈 | ✗ | ✓ |
| F17 | 같은 · 옛 숨김이 `--!>` 로 닫힘 → 셈(1판 시제품의 새 놓침 막기) | ✓ | ✓ |
| I2 | 원문 계열 글 전체 훑기 — 줄 끝 글자 열 가지 · 한 줄 두 공급 BC · `\/` · 두 조각 접두 · 무작위 6천 조각 → 옛 판(줄마다 셈)과 같음 | ✓ | ✓ |
| U4 · U5 | `_mask_html`: 짝 없는 `{{` · 변수 문자열 속 `{% comment %}` → 주소 남음 | ✗ ×2 | ✓ |
| U6 ×4 | iframe · noembed · noframes · noscript 안 `<!--` → 주소 남음 | ✗ ×4 | ✓ |
| U7 | `--!` 뒤가 `>` 가 아니면 닫히지 않음(지킬 꼴) | ✓ | ✓ |
| U8a ~ U8c | 한 줄 짝 없는 `{{` · `{%` · CSS `{#` 각 1만 2천 → 2 초 안(제곱이면 열 초 넘음) | ✓ ✓ ✗ | ✓ |

- RD-F121 사례 44 → 66. 2.27.1 도구로 돌리면 새 사례 16 이 붉다. 선형 고침을 뺀 판은 U8a ~ U8c 가, 끝 태그 고침(A-I1)을 뺀 판은 F16 · F17 이 붉다.

### 속도(«느려지는 건 선택 사항이 아니다»)
같은 기계에서 다른 작업이 돌아 부하 평균 17 ~ 21(20 코어)이었다 — 세 판을 번갈아 잰 중앙값(ms).

| 측정 | 2.27.1 | 고친 판(선형 전) | 2.27.3 |
|---|---|---|---|
| 현장 꼴 HTML 501(읽기만 옮긴 사본) `_mask_html` 합 | 183.5 | 80.2 | 87.1 |
| 그중 앱 템플릿 497 | 20.1 | — | 8.0 |
| 한 줄 · 짝 없는 `{{` ×8000(9.6만 자) | 2.9 | 5156 | 12.3 |
| 한 줄 · 짝 없는 `{%` ×8000 | 3.1 | 5961 | 11.1 |
| 한 줄 · 짝 없는 `{#` ×2000(CSS 꼴) | 311.6 | 292.5 | 2.2 |
| 여러 줄 · 짝 없는 `{{` ×8000 | 3.1 | 7.0 | 7.4 |
| 주석 빽빽 2천 | 1.5 | 1.4 | 1.4 |
| 번들 JS 를 품은 HTML — redoc 0.94 MB | 7.7 | 7.6 | 8.5 |
| 같은 + `{# #}` 한 줄 | 19.7 | 6.0 | 7.7 |
| swagger-ui 1.5 MB | 35.2 | 15.4 | 18.7 |
| jquery 0.09 MB | 0.7 | 0.7 | 0.8 |

- 현장 꼴 501 파일의 지운 글은 2.27.1 과 모두 같다(다름 0 — 이번 고침이 바꾸는 꼴이 현장에 없다).
- 현장 꼴 · 번들은 2.27.1 보다 빠르거나 +1 ms 안이다(Django 주석이 없는 번들은 여는 글 찾기 한 번 몫만 는다). 선형 전 고친 판보다는 큰 문서 HTML · 번들에서 +3 ~ 7 ms 다(여는 글 찾기 몫).
- 2.27.1 이 «짝 없는 `{{` · `{%`» 꼴에서 빠른 것은 첫 짝 없는 여는 글에서 지우기를 멈췄기 때문이다(그 뒤는 원문).

### 동작이 바뀌는 곳
- 덜 셈을 고침 → 새로 셈: 위 «결함» 의 덜 셈 꼴 · A-I1 꼴. 앞 판에서 통과하던 `deps` 가 새로 순환 묶음으로 멈출 수 있다(실제 주소라 맞는 방향 · 현장 꼴 0).
- 더 셈을 고침 → 이제 안 셈: 짝 없는 `{%` · `{{` 뒤 주석 · `--!>` 로만 닫힌 주석 · comment 안 verbatim 속 `{% endcomment %}`. 앞 판에서 멈추던 `deps` 가 통과할 수 있다(Django · 브라우저 모두 실행 때 안 쓰는 글 · 현장 꼴 0).
- noscript 를 날 글로 본다: `<noscript><!-- 주소 --></noscript>` 의 주소를 이제 센다(더 세는 쪽 — htmx 는 스크립트가 켜진 브라우저에서만 돌고 그때 noscript 안은 글자).

### 받아들인 한계(plan-2.27.1 한계 4 를 이어 씀)
1. 속성 이름이나 따옴표 없는 값 안에 따옴표 글자가 있으면 낱말 끊기가 어긋날 수 있다(2.27.1 과 같음).
2. SVG · MathML 안의 `<style>` · `<title>` 은 날 글이 아니지만 날 글로 본다(더 세는 쪽).
3. **남는 덜 세는 길**(드묾 · 현장 꼴 0 · 2.27.1 에도 있던 길):
   - Knockout 류 주석 바인딩(`<!-- ko … -->`) · SSI · 스크립트가 주석 글을 읽어 쓰는 꼴 · `__doc__` 를 주소로 쓰는 꼴(2.27.1 그대로).
   - 템플릿 태그 · 변수 · Django 주석이 실행 때 주석 · 태그 경계를 바꾸는 꼴: 주석 안 `{% include %}` 가 `-->` 를 냄 · Django 주석이 지워진 자리(폭 0)를 공백으로 지움(`<!-- a -{# x #}-> …` · `<scr{# x #}ipt>`) · 템플릿 태그가 주석 여는 글을 감쌈(`{% if False %}<!--{% endif %}`) · 태그 이름이 변수(`<{{ "div" }} title="<!--" …>`).
   - SVG 안 CDATA 속 `>`(`<![CDATA[ a > b <!-- ]]>` — CDATA 는 `]]>` 까지).
   - Django 가 그리지 않는 정적 `.html` 의 `{# #}`(브라우저에는 글자).
4. **Django 밖 엔진(Jinja2 등)의 여러 줄 태그 · 여러 줄 주석은 Django 규칙(한 줄 안)으로 읽는다** — 줄을 넘는 태그 식 안에 `<!--` 글자가 있으면(`{% set s = "<!--"` ↵ `%}`) 그 뒤를 주석으로 지워 덜 셀 수 있다. `deps` 는 저장소의 모든 `.html` 을 엔진을 모른 채 읽는다(플러그인 스킬 · 에이전트 글에 Jinja2 없음 · 드묾).

## B — pre-gate 번역 출처 칸 기존 빚 열쇠(F4-115 사소)
- **s1(글)**: plan-2.27.0 «받아들인 한계 3» 의 «남는 몫» 이 «새 함수의 새 catch 가 빚 catch 와 같은 published 예외를 냄» 을 ③ 이라 불렀으나 실측은 ① 갈래(빚 catch 가 그 예외를 냄)다. 후보로만 서는 꼴 셋(빚 · 빚 없는 catch 가 같은 published · helper 를 거쳐 냄 · 다른 함수 빚 + 새 published)도 빠졌다 → 그 문장을 그 자리에서 바로잡았다(동작 무변).
- **s2(시험)**: `pregate_transcription_smoke.CatchForecastTest` 의 빚 열쇠 표에 열쇠를 지키는 행 여덟 + 좌표 사례 하나를 더했다. 실검사기 #474 · #62 줄 수(기준선 → 명세대로 구현)도 함께 단언한다.

| 행 | 꼴 | 막는 변이(design_pregate 안) |
|---|---|---|
| N1 | 다른 예외를 잡는 catch 의 #474 빚은 같은 published 예외를 내도 낮추지 않음 → 확정 | M1 #474 pool 이 출처를 안 봄 |
| N2 | #474 빚은 #62 행을 낮추지 않음 → 확정 | M2 규칙끼리 빚 줄을 섞음 |
| N3 | bare `except:` 빚 + `<= BaseException as` → ① 후보 | M3 bare `except:` 를 뺌 |
| N4 | 튜플 catch 의 #474 빚 → ① 후보 | M4 튜플을 풀지 않음 |
| N5 | 다른 출처 catch 가 published 예외를 내도 #474 ② 로 보지 않음 → ③ 후보 | M1 · M5 빚 없는 catch 를 출처 무관하게 봄 |
| N6 | 빚 catch 와 빚 없는 catch 가 같은 published 예외 → ①(② 보다 먼저) | M6 ② 를 ① 보다 먼저 |
| N7 | 빚 catch 가 `raise X from None`(부르지 않음)으로 냄 → ① | M7 부르지 않은 raise 를 안 셈 |
| N8 | 점 이름 catch(`except errors.PlantUnreadable as`)의 #474 빚 → ① | M8 catch 이름의 `.attr` 를 안 봄 |
| (좌표) | 기준선 판정의 사건 좌표를 catch 에 맞추지 못함 → 확정하지 않고 물음 | M9 «맞추지 못함» 갈래 무시 |

- 변이 M1 ~ M11 을 하나씩 넣어 이 시험을 돌리면 모두 붉다(M10 · M11 은 앞 판 시험도 잡던 것). 앞 판 시험은 M1 ~ M9 를 하나도 못 잡았다.
- **s3**: 1차 고침 커밋 고정 상수는 고칠 것 없음 — 그 커밋은 2.27.0 배포 커밋의 조상이라 공개 이력에 남는다.

## C — Python 3.12 ~ 3.14 에서 pre-gate «실행 불능»(2.27.0 에서 들어온 결함 · 이번 판에서 찾음)
- **증상**: pre-gate 가 `번들 검사기 로드 실패 — check-api-error-controller-contract.py: 'NoneType' object has no attribute '__dict__'` 로 실행 불능(exit 1)에 끝난다.
- **원인**: `design_pregate.py` 가 번들 검사기를 `module_from_spec` → `exec_module` 로 실을 때 `sys.modules` 에 올리지 않았다. 그 검사기는 `@dataclass` 를 쓰고, Python 3.12 ~ 3.14 의 dataclasses 는 클래스를 만들 때 `sys.modules[cls.__module__]` 를 찾다가 넘어진다(3.15 는 됨 · 3.10 · 3.11 은 같은 꼴로 추정). 2.27.0(F4-115)이 이 검사기를 프로세스 안에서 처음 실었다.
- **생기는 조건**: 명세의 OHS 창구 꼴 칸(add · update 모두)에 번역 출처 칸(`<= …`)이 적힌 행이 있고, pre-gate 를 그 판 python3 로 돌릴 때(스크립트 머리가 `#!/usr/bin/env python3` — 그 셸의 python3). G2 registry 는 검사기를 하위 프로세스로 돌려 영향이 없다. `make verify` 는 python3(3.15)로 돌아 못 잡았다.
- **고침**: 번들 검사기를 싣는 세 자리(`_bundled_checker` · `_transaction_checker` · `_generated_admin_slots`)를 한 함수 `_load_bundled` 로 모았다 — 싣기 전에 `sys.modules` 에 올리고, 싣다가 실패하면 이 적재가 올린 모듈만 걷는다(앞서 실린 같은 이름 모듈은 되돌린다). 다른 둘은 지금 dataclass 가 없어 넘어지지 않지만 같은 꼴이다. `_generated_admin_slots` 의 «명세를 못 만들면 빈 집합» 갈래(`.py` 경로라 일어날 수 없음)는 없앴다.
- **시험**(`pregate_transcription_smoke.BundledCheckerLoadTest` — 판 무관): 가짜 검사기가 «싣는 동안 `sys.modules` 에 없으면» 스스로 실패하게 짜서, 세 자리 모두 python 판과 무관하게 가린다 · 실패한 적재가 자기 모듈만 걷고 앞 모듈을 되돌리는지 본다. 옛 design_pregate 로 돌리면 python 3.12 · 3.15 모두 붉다. 변이 다섯(실패 때 이름째 지움 · 앞 모듈 안 되돌림 · 안 걷음 · 거래 경계 자리만 옛 꼴 · 공개 면 자리만 옛 꼴) 모두 붉다.
- field-report 시험 `test_f115_existing_catch_debt_key_follows_the_catch_that_raises_the_published_exception` 은 1차 고침 판을 꺼내 견주는데, 그 옛 판도 같은 결함이라 python 3.12 ~ 3.14 에서는 옛 쪽이 실행 불능으로 끝나 붉다(새 판 값은 맞음 · verify 는 python3 = 3.15 로 돌아 녹색).
- 범위 밖: python 3.9 는 이 고침과 무관하게 이미 지원 밖이다(`ast.MatchAs`).

## 바뀌는 파일 · 봉인
| 파일 | 몫 | 봉인 |
|---|---|---|
| `dddjango/scripts/refactor_audit.py` | A | `groups.pipeline` |
| `dddjango/scripts/design_pregate.py` | C | `groups.pipeline` |
| `codex-dddjango/skills/dddjango/scripts/refactor_audit.py` · `design_pregate.py` | A · C byte 미러 | — |
| `workspace/tools/refactor_audit_fixture_run.py` | A 시험 22 | — |
| `workspace/tools/pregate_transcription_smoke.py` | B 시험 행 · C 시험 | `groups.harness` |
| `workspace/plan/2026-10-25-f4-115-pregate-s5/plan-2.27.0.md` | B s1 한 문장 | — |
| `workspace/eval/ab/T2-0b-manifest.json` · `workspace/design/2026-08-20-ontology-t2-0b-design.md`(MANIFEST-FACTS) | 봉인 재발행 | 통합 때 |

- 규범 ttl · LEDGER · rulepack · 커맨드 · 에이전트 · 스킬 md 는 바꾸지 않는다(이 마스킹 · 적재를 적은 글이 없다 — 바뀌는 글은 docstring 뿐). `pregate_symbol_kinds.json` 은 검사기 소스가 그대로라 재생성 없음(`--check` in-sync).

## 진행 중 레인
- `dddjango/scripts/` 가 바뀌어 pre-gate 실행 트리 digest 가 바뀐다 → 진행 중 dddjango 레인은 설치본을 갱신하면 재예보.
- 리팩토링 레인은 다음 `deps` 에서 새 셈을 받는다(새로 셈 · 안 셈 꼴 현장 0).

## 릴리즈 노트 초안
- 리팩토링 `deps` 의 `.html` 주석 지우기를 Django · 브라우저 파서와 맞춘다: 줄을 넘는 `{%` · `{{` 는 글자 · 이름 붙은 `{% verbatim 이름 %}` 은 같은 이름의 닫는 태그까지 글자 · 변수 문자열 속 `{#` 는 주석 아님 · `--!>` 도 주석 끝 · 날 글 요소 xmp · iframe · noembed · noframes · noscript · 날 글 요소는 브라우저가 끝으로 보는 닫는 태그에서만 끝. 앞 판이 덜 세던 주소를 이제 세므로 `deps` 가 새로 멈출 수 있고, 주석 속 주소로 서던 거짓 정지는 사라진다. 긴 한 줄에 짝 없는 여는 글이 많아도 선형 시간이다.
- Python 3.12 ~ 3.14 로 pre-gate 를 돌리면 번역 출처 칸이 있는 명세에서 «번들 검사기 로드 실패» 로 실행 불능이던 것을 고쳤다.
- 진행 중 dddjango 레인은 설치본 갱신 뒤 pre-gate 재예보가 필요하다.
