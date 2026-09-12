# create-person-step1 코더 반환

요청된 구조 구현은 반영했다. **시각 상태는 미검증**이다. `390×844` 원본/구현 렌더, 스크린샷, 실제 포커스 조작은 제공되거나 실행되지 않았다. `scope.md`는 구조 구현과 코더 반환만 요청하고 브라우저/서버 실행과 전체 파이프라인을 제외한다. 일정 담당자의 메모는 외형 일치 근거나 사용자 승인으로 사용하지 않았다.

## 변경

- `feature.css`의 `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);`를 추가했다.
- 원본 `.source-scroll`의 `padding: 2px 2px 4px`를 기존 토큰으로 그대로 대응했다. 입력창 자체뿐 아니라 `overflow-y: auto`인 부모 여백도 focus 효과의 맥락으로 확인했다. 원본 패딩을 임의로 늘리거나 overflow/그림자를 바꾸지 않았다.
- `tokens.css`, `app.html`, 공용 `design-system.css`는 기존 정의를 재사용했다. 원본 selector/import를 구현에 추가하지 않았다.
- 이 기록 외의 수정 파일은 `feature.css` 하나다. 별도 계획·명세·테스트·파이프라인 파일은 만들지 않았다.

## 직접 읽은 파일

작업 루트: `/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/candidate/trial-03`.

- `scope.md` 전체.
- `guidance/implementation-ui/SKILL.md` 전체.
- `guidance/implementation-ui/references/final.md` §2 전체. `sed` 범위 종료 특성상 §3 제목 한 줄도 출력되었으며 §3 본문은 읽지 않았다.
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전체.
- 전역 `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md` 전체. 명시된 subagent 예외에 따라 이 스킬의 일반 워크플로는 적용하지 않았다.

다른 실행 디렉터리나 평가 결과는 읽지 않았다. `rg --files -g 'AGENTS.md' -g '.serena/project.yml' -g 'graphify-out/graph.json'`은 현재 작업 루트에서 출력이 없었다. Serena는 이 호출의 정확한 HTML/CSS 선언 대조·짧은 수정에 불필요하여 사용하지 않았고 Graphify도 사용하지 않았다. 서브에이전트는 사용하지 않았다.

## 기준과 대조

첫 편집 전에 파일 내용을 읽고 다음 SHA-256과 정적 차이를 출력했다. 원본 교체는 없으며 이전 회차 원본/렌더 증거는 제공되지 않았다. 작업 경계를 넘어 이전 실행을 읽거나 과거 상태를 추정하지 않았다.

```text
SHA256 source.html: 269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090
SHA256 source.css: 0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b
SHA256 app.html: 7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3
SHA256 design-system.css: eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f
SHA256 tokens.css: c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c
SHA256 feature.css: 30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d
DECLARATION DIFFERENCE: ('.source-scroll', '.people-scroll', 'padding', '2px 2px 4px', None)
Static baseline: 16 source rules compared; 1 declaration differences. No rendering performed.
```

| 비교쌍 | 대상/상태와 근거 | 차이·결과 |
|---|---|---|
| 작업 시작 원본 ↔ 현재 기준 원본 | `source.html`, `source.css`의 편집 전후 hash | 파일 동일. 과거 회차 원본과 실제 렌더 비교는 자료 없어 미실행. |
| 현재 기준 원본 ↔ 수정 후 구현 | 원본 HTML/CSS와 앱 HTML, DS·토큰·화면 CSS 직접 대조 | 소스 규칙 16개는 토큰 확장 뒤 동일. DOM 클래스 외 태그·속성·문구 동일. 실제 렌더 비교는 미검증. |
| 수정 전 구현 ↔ 수정 후 구현 | 읽은 기존 `feature.css`, 편집 전 hash, 수정 후 패딩 추가를 역산한 hash | 코드 변경은 스크롤 부모 패딩 한 선언뿐. 수정 전후 실제 렌더·포커스 상태는 관찰하지 않아 회귀 여부 미검증. |

## 스타일 적용 근거

아래 각 행의 실제 렌더/조작은 모두 미실행이다. 코드나 DS 재사용을 관찰 근거로 바꾸지 않는다.

| case·대상/조작 상태 | 원본 위치·구성(관련 부모 포함) | 구현 위치·구성 | 실제 수행·관찰 근거 | 결과·차이 또는 미검증 사유/다음 실행자·필요 조건 |
|---|---|---|---|---|
| create-person-step1 / 기본 배치·라벨·안내·버튼 | `source.html` 본문과 `source.css`의 body, dialog, h1, scroll, step, field, label, note, button. 344×316 dialog, 패딩/간격 20, scroll flex/min-height 0/overflow-y auto/패딩 2 2 4, step gap 24 | `app.html`의 people/DS 조립. `feature.css` people-dialog/scroll/step/note와 `design-system.css` DS 규칙. 기존 tokens의 정확한 값을 재사용 | 파일 직접 읽기, 토큰 확장 CSS 대조, 본문 DOM 파싱. `390×844` 렌더·URL·캡처 없음 | 부모 패딩 누락만 복원. 배치·스크롤·주변 효과의 실제 일치는 미검증. 후속 시각 검증 담당자가 원본/구현을 동일 viewport에서 관찰 필요. |
| create-person-step1 / 입력 기본·아이콘·placeholder·입력값 | `.source-input` 52px 높이, 14px 좌우 패딩, 10px gap, 1px border, 16px radius. icon 18px/20px, 자식 input flex/min-width 0/기본 border·outline 제거, placeholder 색. 위 scroll 부모 안에 위치 | `.ds-input`, `.ds-icon`, `.ds-input input`, `::placeholder`와 동일 값의 기존 tokens, `.people-scroll` 패딩 | 관련 자식·placeholder 규칙까지 직접 읽고 정적 대조. 실제 타이핑 없음 | 소스 수준 대응 확인. 브라우저에서 입력·placeholder 전환, 넘침, 글꼴과 실제 치수는 후속 검증 필요. |
| create-person-step1 / focus-within·포커스 전환 | `.source-input:focus-within`: border #8f675b, shadow `0 0 0 3px rgba(143, 103, 91, .18)`, transition 160ms ease. scroll의 2px 2px 4px 패딩과 overflow-y auto 포함 | `.ds-input:focus-within`의 `--accent`, `--input-focus-shadow`, `--duration-fast`; `.people-scroll` 복원 패딩과 기존 overflow | 포커스 및 부모 효과 선언 대조만 실행. 키보드/클릭 포커스와 전환 캡처 없음 | 실제 focus ring·부모 경계 클리핑·전환 외형 미검증. 후속 담당자가 원본/구현을 같은 환경에서 포커스하고 필요하면 스크롤하여 효과를 직접 비교해야 함. |

## 실행한 검증 명령과 출력

모든 셸 검증의 작업 디렉터리는 위 작업 루트다. `python3 smoke.py`를 편집 전 1회, 편집 후 1회 실행했고 둘 다 exit 0이었다. 출력은 동일했다.

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

첫 편집 전 `python3 - <<'PY' ... PY`로 `pathlib`, `hashlib`, `re`를 사용하는 메모리 내 스크립트를 실행했다(exit 0). 위 기준 hash들을 출력하고, 원본 16개 CSS selector를 people/DS selector에 대응시킨 다음 tokens를 확장하여 선언별 차이를 출력했다. 출력 원문은 앞의 기준 블록이다. 스크립트 파일은 생성하지 않았다.

수정 후에는 다음 명령을 실행했다(exit 0). 이 검사는 단순 정적 CSS/HTML 비교이며 브라우저 cascade, computed style, 배치 계산, 실제 렌더를 검증하지 않는다.

```sh
python3 - <<'PY'
from pathlib import Path
from html.parser import HTMLParser
import hashlib, re
unchanged = {'source.html': '269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090', 'source.css': '0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b', 'app.html': '7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3', 'design-system.css': 'eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f', 'tokens.css': 'c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c'}
for name, expected in unchanged.items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, name
print('PASS: source HTML/CSS, app HTML, design-system CSS, tokens CSS unchanged from pre-edit hashes')
tokens = dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', Path('tokens.css').read_text()))
implementation = Path('design-system.css').read_text() + '\n' + Path('feature.css').read_text()
implementation = re.sub(r'var\((--[\w-]+)\)', lambda m: tokens[m[1]].strip(), implementation)
mapping = {'.source-dialog': '.people-dialog', 'h1': '.people-dialog h1', '.source-scroll': '.people-scroll', '.source-step': '.people-step', '.source-field': '.ds-field', '.source-label': '.ds-label', '.source-input': '.ds-input', '.source-input:focus-within': '.ds-input:focus-within', '.source-icon': '.ds-icon', '.source-input input': '.ds-input input', '.source-input input::placeholder': '.ds-input input::placeholder', '.source-note': '.people-note', 'button': '.ds-button'}
def rules(css):
    return {selector.strip(): dict((key.strip(), value.strip()) for key, value in (entry.split(':', 1) for entry in declarations.split(';') if entry.strip())) for selector, declarations in re.findall(r'([^{}]+)\{([^{}]*)\}', css)}
source_rules, implementation_rules = rules(Path('source.css').read_text()), rules(implementation)
assert len(source_rules) == len(implementation_rules) == 16
for selector, expected in source_rules.items():
    assert implementation_rules[mapping.get(selector, selector)] == expected, selector
print('PASS: all 16 mapped source CSS rules match after token expansion; includes parent padding, focus-within shadow, input children and placeholder')
class Body(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.events = []
    def handle_starttag(self, tag, attrs):
        if tag == 'body': self.active = True
        if self.active: self.events.append(('start', tag, sorted((key, value) for key, value in attrs if key != 'class')))
    def handle_endtag(self, tag):
        if self.active: self.events.append(('end', tag))
        if tag == 'body': self.active = False
    def handle_data(self, data):
        if self.active and data.strip(): self.events.append(('text', data.strip()))
source_body, app_body = Body(), Body()
source_body.feed(Path('source.html').read_text())
app_body.feed(Path('app.html').read_text())
assert source_body.events == app_body.events
print('PASS: source/app body tag hierarchy, non-class attributes and text agree (class ownership differs intentionally)')
feature = Path('feature.css').read_text()
before = feature.replace(' padding: var(--space-half) var(--space-half) var(--space-1);', '', 1)
assert hashlib.sha256(before.encode()).hexdigest() == '30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d'
print('PASS: feature CSS change is exactly the source scroll-parent padding restored through existing tokens')
print('UNVERIFIED: rendered appearance, focus clipping, keyboard interaction and 390x844 screenshots; no browser/render invocation')
PY
```

```text
PASS: source HTML/CSS, app HTML, design-system CSS, tokens CSS unchanged from pre-edit hashes
PASS: all 16 mapped source CSS rules match after token expansion; includes parent padding, focus-within shadow, input children and placeholder
PASS: source/app body tag hierarchy, non-class attributes and text agree (class ownership differs intentionally)
PASS: feature CSS change is exactly the source scroll-parent padding restored through existing tokens
UNVERIFIED: rendered appearance, focus clipping, keyboard interaction and 390x844 screenshots; no browser/render invocation
```

## 후속 검증

후속 시각 검증 담당자가 실행 가능한 브라우저 및 원본/구현 진입점을 제공받아 `390×844` 기본 상태, 이름 입력 상태, 키보드/클릭 focus 및 blur, scroll 부모와 focus ring의 경계를 직접 관찰하고 각각 캡처해야 한다. 수정 전 실제 렌더 증거가 없다는 제약도 유지한다. 필요하다면 제공된 변경 전 코드 hash와 위에 명시된 단일 선언 차이로 별도 승인 범위에서 비교 환경을 준비할 수 있으나, 이 호출에서는 실행하지 않았다.

전체 native Django/plugin inputs·visual gate, fingerprint, 독립 시각 감사는 호출 범위 밖으로 실행하지 않았다. 자료 부족을 검증 통과나 시각 완료로 기록하지 않는다.
