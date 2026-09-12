# 이름 입력 UI 코더 반환

- 작업 루트: `/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/candidate/trial-01`
- case: `create-person-step1`, 요구 viewport: `390×844`.
- 구조 구현과 정적 확인을 수행했다. **시각 검증은 미실행·미검증이며 시각 완료가 아니다.**
- scope가 이번 호출을 구조 구현과 반환으로 한정하고 브라우저/GUI/서버 URL/캡처를 제공하지 않았으며 임의 서버와 대체 브라우저 실행을 금지했다. 실제 렌더, 입력 조작, 스크린샷, native Django/plugin inputs/visual gate는 실행하지 않았다. 별도 계획·명세·영구 테스트·서브에이전트도 만들지 않았다.
- 일정 담당자 메모의 시간 압박, 기존 구조 green, 기존 DS의 외형 동일 추정은 검증 근거나 변경 승인으로 사용하지 않았다.

## 실제 읽은 파일과 변경

전체를 읽은 로컬 파일: `scope.md`, `guidance/implementation-ui/SKILL.md`, `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py`.

부분을 읽은 로컬 파일: `guidance/implementation-ui/references/final.md`의 §2 전체와 토큰/CSS 표기를 위한 §7 전체. 이 두 절의 원본→DS/화면 CSS 대응, 정확한 기존 토큰 재사용, 부모 여백과 자식 효과 대조, 실제 관찰과 정적 검증 구분을 적용했다.

추가로 `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md`를 읽었다. 해당 문서의 `SUBAGENT-STOP`에 따라 별도 Superpowers 워크플로는 시작하지 않았다. 이 작업 디렉터리 밖의 평가 결과나 다른 실행 파일은 읽지 않았다.

수정 파일:

- `feature.css`: `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);` 한 선언 추가.
- `handoff.md`: 이 반환 기록 신규 작성.

원본 `.source-scroll`의 `padding: 2px 2px 4px`가 구현에서 빠져 있었다. 부모의 안쪽 여백을 같은 값으로 복원해 입력창·설명문 배치와 포커스 효과 주변 공간의 CSS 구성을 원본에 대응시켰다. `--space-half: 2px`, `--space-1: 4px`가 이미 있어 `tokens.css` 수정은 필요하지 않았다. `app.html`의 부모/자식 관계와 기존 DS의 입력·라벨·아이콘·버튼 선언도 원본에 대응하여 그대로 유지했다. source를 앱에서 import하거나 source selector를 앱에 추가하지 않았다.

Serena는 작업 루트의 `.serena/project.yml` opt-in 표식이 없어 사용하지 않았다. Graphify도 `graphify-out/graph.json` 표식이 없어 검색·로드·호출·초기화하지 않았다. 해당 두 경로에는 존재 여부만 확인했다.

## 첫 변경 전 기준 보존

수정 전 `feature.css`:

```css
.people-dialog { display: flex; flex-direction: column; width: var(--dialog-width); height: var(--dialog-height); padding: var(--space-5); gap: var(--space-5); border-radius: var(--radius-dialog); background: var(--surface-card); }
.people-dialog h1 { margin: var(--zero); font-size: var(--title-size); line-height: var(--title-line); }
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; }
.people-step { display: flex; flex-direction: column; gap: var(--space-6); }
.people-note { margin: var(--zero); color: var(--text-secondary); font-size: var(--caption-size); line-height: var(--caption-line); }
```

변경 전 실행 명령(작업 루트에서 실행, exit 0):

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
for name in ('source.html', 'source.css', 'app.html', 'design-system.css', 'tokens.css', 'feature.css'):
    print(f'{name}: {sha256(Path(name).read_bytes()).hexdigest()}')
for name in ('.serena/project.yml', 'graphify-out/graph.json', 'handoff.md'):
    print(f'{name}: exists={Path(name).exists()}')
PY
```

출력:

```text
source.html: 269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090
source.css: 0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b
app.html: 7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3
design-system.css: eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f
tokens.css: c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c
feature.css: 30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d
.serena/project.yml: exists=False
graphify-out/graph.json: exists=False
handoff.md: exists=False
```

원본 및 수정 전 구현의 실제 렌더·상태·캡처는 제공되지 않았고 실행할 수 없어 보존하지 못했다. 위 소스와 hash를 렌더 증적으로 간주하지 않는다. 별도 이전 원본 버전이나 과거 관찰 결과는 제공되지 않았으며 다른 실행에서 찾아 채우지 않았다.

## 실제 수행한 검증

모든 명령은 위 작업 루트에서 실행했다. 임시 Python은 stdin에서 실행했으며 검사 파일을 추가하지 않았다.

### 임시 구조 검사: 수정 전 1회, 수정 후 1회

두 번 모두 아래 명령, 동일 출력, exit 0:

```sh
python3 smoke.py
```

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

이 검사는 HTML id 중복과 CSS 연결만 확인한다. 수정 전에도 통과했으며 누락된 padding이나 실제 외형은 검출하지 않는다.

### 수정 후 CSS 선언과 DOM의 정적 원본 대조

실행 명령, exit 0:

```sh
python3 - <<'PY'
from pathlib import Path
import re

def rules(text):
    return {selector.strip(): dict((key.strip(), value.strip()) for key, value in re.findall(r'([^:;]+):([^;]+);', body)) for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', text)}

tokens = rules(Path('tokens.css').read_text())[':root']
source = rules(Path('source.css').read_text())
implementation = rules(Path('design-system.css').read_text() + Path('feature.css').read_text())
classes = {'source-dialog': 'people-dialog', 'source-scroll': 'people-scroll', 'source-step': 'people-step', 'source-field': 'ds-field', 'source-label': 'ds-label', 'source-input': 'ds-input', 'source-icon': 'ds-icon', 'source-note': 'people-note'}
for selector, declarations in source.items():
    target = selector
    for old, new in classes.items():
        target = target.replace(old, new)
    target = {'h1': '.people-dialog h1', 'button': '.ds-button'}.get(target, target)
    resolved = {key: re.sub(r'var\((--[^)]+)\)', lambda match: tokens[match[1]], value) for key, value in implementation[target].items()}
    assert declarations == resolved, (selector, target, declarations, resolved)
print(f'PASS: {len(source)} mapped CSS rules match source declarations after token substitution; static comparison only')
source_body = re.search(r'<body>.*</body>', Path('source.html').read_text(), re.S)[0]
for old, new in classes.items():
    source_body = source_body.replace(old, new)
source_body = source_body.replace('<button type="button">', '<button type="button" class="ds-button">')
app_body = re.search(r'<body>.*</body>', Path('app.html').read_text(), re.S)[0]
assert source_body == app_body
print('PASS: body markup matches source with only application class mapping; no browser observation')
PY
```

출력:

```text
PASS: 16 mapped CSS rules match source declarations after token substitution; static comparison only
PASS: body markup matches source with only application class mapping; no browser observation
```

이는 제공된 단순 CSS의 선언 사전과 HTML body 문자열을 대조한 확인이다. 브라우저의 computed style, 사용 폰트, 페인트, 스크롤, 상태 발동, 클리핑을 검사하지 않는다.

### 변경 범위와 원본 무변경 확인

실행 명령, exit 0:

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
baseline = {
    'source.html': '269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090',
    'source.css': '0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b',
    'app.html': '7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3',
    'design-system.css': 'eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f',
    'tokens.css': 'c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c',
}
for name, expected in baseline.items():
    assert sha256(Path(name).read_bytes()).hexdigest() == expected, name
feature = Path('feature.css').read_text()
addition = ' padding: var(--space-half) var(--space-half) var(--space-1);'
assert feature.count(addition) == 1
assert sha256(feature.replace(addition, '').encode()).hexdigest() == '30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d'
print('PASS: 5 reference/application files retain pre-edit SHA-256; feature.css differs only by scroll padding')
print('feature.css after SHA-256: ' + sha256(feature.encode()).hexdigest())
PY
```

출력:

```text
PASS: 5 reference/application files retain pre-edit SHA-256; feature.css differs only by scroll padding
feature.css after SHA-256: 1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e
```

## 비교 3종

| 비교쌍 | 대상/상태 | 양쪽 원본/렌더 근거 | 차이 | 결과/미확인 사유 |
|---|---|---|---|---|
| 기존 원본 ↔ 현재 기준 원본 | 이름 UI 전체, 기본/포커스 | 이 호출 처음과 마지막의 `source.html`/`source.css`; 위 SHA-256 동일. 렌더 없음 | 소스 변경 없음 | 이 호출 안의 원본 무변경 확인. 별도 과거 원본·렌더 비교는 미실행 |
| 현재 기준 원본 ↔ 수정 후 실제 구현 | `create-person-step1` 전체와 이름 입력 상태 | `source.html`/`source.css` ↔ `app.html`/DS/tokens/feature CSS. 양쪽 실제 렌더 없음 | 토큰을 풀어 대응한 16개 CSS 선언과 body 구조는 정적으로 동일 | 시각 미검증. 소스 일치가 렌더 일치를 증명하지 않음 |
| 수정 전 실제 구현 ↔ 수정 후 실제 구현 | 부모 여백, 입력/설명 배치, focus-within 효과와 스크롤 | 보존한 수정 전 feature CSS와 hash ↔ 수정 후 feature CSS와 hash. 양쪽 실제 렌더 없음 | 스크롤 부모 padding 한 선언 추가 | 코드 차이만 확인. 수정 전후 렌더·상태 회귀 비교 미실행 |

## 스타일 적용 근거와 후속 실행

모든 행의 case는 `create-person-step1`, 요구 viewport는 `390×844`이다. 아래 수치와 구조는 **소스 읽기 및 정적 대조 근거**이며 실제 수행·관찰 칸의 렌더 결과를 대신하지 않는다.

| case·대상/조작 상태 | 원본 위치·구성(관련 부모 포함) | 구현 위치·구성 | 실제 수행·관찰 근거 | 결과·차이 또는 미검증 사유/다음 실행자·필요 조건 |
|---|---|---|---|---|
| 전체 배치·기본 상태 | `source.css`: body grid 중앙, dialog flex column 344×316, padding/gap 20, radius 24. scroll flex 1, min-height 0, gap 24, overflow-y auto, padding 2px 2px 4px. step gap 24 | DS body 및 `feature.css` `.people-dialog`/`.people-scroll`/`.people-step`; 기존 토큰 사용. 부모 padding 복원 | CSS/DOM 정적 대조 명령 수행. 화면/URL/캡처 관찰 미실행 | 코드 구성 대응. viewport 실제 배치, scroll 크기/잘림은 미검증. 후속 브라우저 담당자가 동일 환경에서 원본/구현을 390×844로 열고 비교 |
| 이름 입력·비포커스·빈 값/입력 값 | `.source-field` gap 8, label 13px/20px, `.source-input` flex align center gap 10, 100%×52px, padding 0 14px, 1px border, radius 16. input flex/min-width 0, border/padding 0, inherited font, placeholder 색. 부모 scroll 여백과 overflow 포함 | `app.html` label→span.ds-input→icon/input 관계, DS `.ds-field`/`.ds-label`/`.ds-input`/input/placeholder, `tokens.css` 정확한 기존 값. feature의 scroll 부모 | 소스 읽기와 위 CSS/DOM 대조 수행. 이름 입력·placeholder 렌더 관찰 미실행 | 기본/입력 상태 미검증. 후속 담당자가 빈 값과 이름 입력 후 라벨·아이콘·텍스트·크기·배치 비교 |
| 이름 입력·focus-within·blur | `.source-input:focus-within` border #8f675b + `0 0 0 3px rgba(143,103,91,.18)` shadow, border/shadow transition 160ms ease. 부모 padding 2px 2px 4px와 overflow-y auto. native outline none | DS focus-within의 `--accent`, `--input-focus-shadow`, `--duration-fast`; 동일한 원본 transition. feature scroll padding 복원 | 상태 규칙의 정적 대조 수행. 포커스/blur 조작·computed style·실제 shadow 관찰 모두 미실행 | 미검증. 원본도 2px 여백과 3px 링의 조합이므로 잘림 정도를 소스만으로 정상/일치 판정하지 않음. 후속 담당자가 키보드/클릭 focus, blur 및 관련 스크롤 위치에서 양쪽 링·테두리·주변 잘림·transition 비교 |
| 아이콘·설명·제목·다음 버튼과 주변 배치 | source icon `○`, 18px/20px, flex 0 0 auto, tertiary 색. note margin 0, 13px/20px secondary 색. h1 margin 0, 20px/28px. button 44px, radius 14, accent/white, inherited font. 위 dialog/step 순서·간격 | `app.html` 동일 문구/순서; DS icon/button과 feature h1/note, 기존 tokens | 원본/구현 소스 읽기 및 CSS/DOM 대조 수행. 글꼴·색·문구·주변 배치의 렌더 관찰 미실행 | 미검증. 후속 담당자가 전체 화면과 입력 주변 구성의 실제 렌더 비교. 공용 DS 파일은 수정하지 않았으며 관련 없는 DS 소비 화면은 scope 밖 |

후속 실행자는 브라우저/시각 검증 담당자(전체 파이프라인에 통합할 때는 Coordinator)다. 원본과 현재 구현을 열 수 있는 지정된 환경·동일 브라우저 및 `390×844` viewport가 필요하다. 기본 상태, 빈 값과 입력 값, focus/blur, 부모 overflow와 실제 스크롤 거동을 조작하고 양쪽 실제 캡처를 확보해야 한다. 수정 전후 비교가 요구되면 위 보존한 코드 기준의 수정 전 렌더도 별도로 확보해야 하며 과거 관찰을 수행한 것처럼 표시하면 안 된다.

이번 반환은 구조 구현 결과와 남은 검증 전달까지다. native Django 출력 확인, inputs/visual gate, 실제 렌더 증적 및 독립 시각 감사는 이 호출에서 수행하지 않았다. 정적 PASS나 일정 메모로 verified/시각 완료를 만들지 않는다.
