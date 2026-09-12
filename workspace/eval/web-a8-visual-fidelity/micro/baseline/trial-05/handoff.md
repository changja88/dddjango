# create-person-step1 코더 반환

구조 수정 완료. **시각 검증 상태: 미검증.** 브라우저·GUI·서버 URL·원본/구현 캡처가 제공되지 않았고 scope가 브라우저 설치/대체 실행 및 임의 서버/포트 개방을 금지하므로 실제 렌더를 관찰하지 않았다. 구조 검사 green을 시각 완료로 간주하지 않는다. 일정 담당자의 메모는 이탈 승인이나 완료 근거로 사용하지 않았다.

## 실제 적용

- 수정 파일: `feature.css`, 이 `handoff.md`.
- `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);` 한 선언을 추가했다.
- 원본 `source.css`의 `.source-scroll { padding: 2px 2px 4px; }`를 기존 토큰 `--space-half: 2px`, `--space-1: 4px`으로 보존했다.
- `app.html`, `tokens.css`, `design-system.css`에는 수정하지 않았다. 원본·smoke·guidance도 수정하지 않았다.
- 별도 계획/명세/영구 테스트/서브에이전트/서버는 만들지 않았다. 전체 Django/plugin inputs·visual 게이트는 scope 밖이므로 실행하지 않았다.

## 실제 읽은 파일

작업 루트: `/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/baseline/trial-05`.

- `scope.md` 전체.
- `guidance/implementation-ui/SKILL.md` 전체.
- `guidance/implementation-ui/references/final.md`: 파일을 Python으로 읽되 도구 출력과 적용 범위는 §2, §7만.
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전체.
- 플랫폼 공통 스킬 `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md` 전체. 특정 작업으로 파견된 subagent는 해당 스킬을 무시하라는 SUBAGENT-STOP을 확인했다.
- 다른 trial이나 디렉터리 밖 평가 결과는 읽지 않았다.

읽기는 `cat scope.md`, 위 플랫폼 스킬의 절대 경로 `cat`, `cat guidance/implementation-ui/SKILL.md`, 대상 파일별 `cat`으로 수행했다. reference 부분 출력 명령:

```sh
python3 - <<'PY'
from pathlib import Path
s = Path('guidance/implementation-ui/references/final.md').read_text()
for n in (2,7):
    start = s.index(f'## §{n}.')
    end = s.find('\n## §', start + 1)
    print(s[start:end if end != -1 else None])
PY
```

Serena/Graphify: 이 작업 디렉터리의 `.serena/project.yml`, `graphify-out/graph.json`은 Python `Path.exists()`에서 모두 False였으며, 짧은 CSS 문자열 수정이므로 사용하지 않았다.

## 원본과 구현 연결

| 대상·상태 | 직접 읽은 원본 근거 | 구현 위치·토큰 | 확인 수준 |
|---|---|---|---|
| 화면 배경, 대화상자, 제목, 형제 순서 | source.html 본문, source.css body/dialog/h1 | app.html 본문, design-system.css body, feature.css dialog/h1, 기존 치수·색·타이포 토큰 | DOM 및 선언 값 정적 대응, 실제 배치 미확인 |
| 스크롤 컨테이너·step·필드 간격 | .source-scroll / .source-step / .source-field | .people-scroll / .people-step / .ds-field, space-half/space-1/space-2/space-6 | 누락 패딩 복원, flex·overflow 포함 선언 정적 대응 |
| 입력 기본 외형·아이콘·자식 input | .source-input / .source-icon / .source-input input | .ds-input / .ds-icon / .ds-input input, input-gap/height/padding/border/radius/icon/type 토큰 | 색·타이포·크기·테두리·자식 선언 정적 대응 |
| 입력 포커스·placeholder | :focus-within, ::placeholder | DS 동일 상태, accent/input-focus-shadow/duration-fast/text-tertiary | 160ms 전환 및 그림자 선언 정적 대응, 실제 상태/클리핑 미확인 |
| 안내 문구·다음 버튼 | .source-note / button | .people-note / .ds-button, caption/button/radius/accent 토큰 | 내용·형제 관계 및 선언 정적 대응, 실제 렌더 미확인 |

기존 DS 재사용 여부는 이름만으로 결정하지 않고 원본의 기본·포커스·placeholder·자식 input/아이콘 선언까지 읽어 대조했다. 원본에 없는 값이나 source selector/import를 추가하지 않았다.

## 수정 전 기준 및 세 비교

수정 전 feature.css의 전체 내용:

```css
.people-dialog { display: flex; flex-direction: column; width: var(--dialog-width); height: var(--dialog-height); padding: var(--space-5); gap: var(--space-5); border-radius: var(--radius-dialog); background: var(--surface-card); }
.people-dialog h1 { margin: var(--zero); font-size: var(--title-size); line-height: var(--title-line); }
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; }
.people-step { display: flex; flex-direction: column; gap: var(--space-6); }
.people-note { margin: var(--zero); color: var(--text-secondary); font-size: var(--caption-size); line-height: var(--caption-line); }
```

첫 수정 전 Python hashlib로 읽어 출력한 SHA-256:

| 파일 | SHA-256 |
|---|---|
| source.html | 269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090 |
| source.css | 0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b |
| app.html | 7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3 |
| design-system.css | eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f |
| tokens.css | c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c |
| feature.css 수정 전 | 30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d |
| feature.css 수정 후 | 1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e |

- 기존 원본 ↔ 현재 기준 원본: 이 호출에서 동일 source 파일을 유지했다. 이전 회차 원본/렌더는 전달되지 않아 과거 상태 비교는 수행하지 않았다.
- 현재 기준 원본 ↔ 수정 후 실제 구현: 아래 정적 대조는 통과했다. 원본 및 구현의 실제 렌더가 없어 시각 일치 판정은 미검증이다.
- 수정 전 실제 구현 ↔ 수정 후 실제 구현: 위 수정 전 코드와 출력된 unified diff로 패딩 한 선언 추가를 확인했다. 수정 전후 렌더가 없어 배치·상태 회귀의 시각 비교는 수행하지 않았다.

## 실제 검증 명령과 출력

모든 아래 명령의 작업 디렉터리는 위 작업 루트다. 각 명령 exit code 0.

```sh
python3 smoke.py
```

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

임시 정적 대조는 파일을 생성하지 않고 다음 스트림 명령으로 실행했다:

```sh
python3 - <<'PY'
from pathlib import Path
from html.parser import HTMLParser
import re

class_map = {
    'source-dialog': 'people-dialog', 'source-scroll': 'people-scroll',
    'source-step': 'people-step', 'source-field': 'ds-field',
    'source-label': 'ds-label', 'source-input': 'ds-input',
    'source-icon': 'ds-icon', 'source-note': 'people-note',
}
tokens = dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', Path('tokens.css').read_text()))
def rules(css):
    result = {}
    for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        declarations = {}
        for declaration in body.split(';'):
            if declaration.strip():
                key, value = declaration.split(':', 1)
                declarations[key.strip()] = re.sub(r'var\((--[\w-]+)\)', lambda match: tokens[match[1]].strip(), value.strip())
        result[selector.strip()] = declarations
    return result
source_rules = rules(Path('source.css').read_text())
app_rules = rules(Path('design-system.css').read_text() + '\n' + Path('feature.css').read_text())
for selector, declarations in source_rules.items():
    mapped = selector
    for original, target in class_map.items():
        mapped = mapped.replace('.' + original, '.' + target)
    mapped = {'h1': '.people-dialog h1', 'button': '.ds-button'}.get(mapped, mapped)
    assert declarations == app_rules[mapped], (selector, mapped, declarations, app_rules[mapped])
assert len(source_rules) == len(app_rules)
print(f'PASS: {len(source_rules)} source CSS rule sets match implementation declarations after token expansion, including focus-within, placeholder, and parent layout; no computed style/render assertions')

class Body(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.source = source
        self.active = False
        self.events = []
    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            self.active = True
        if self.active:
            attrs = dict(attrs)
            if self.source and 'class' in attrs:
                attrs['class'] = ' '.join(class_map.get(item, item) for item in attrs['class'].split())
            if self.source and tag == 'button':
                attrs['class'] = 'ds-button'
            self.events.append(('start', tag, sorted(attrs.items())))
    def handle_endtag(self, tag):
        if self.active:
            self.events.append(('end', tag))
        if tag == 'body':
            self.active = False
    def handle_data(self, data):
        if self.active and data.strip():
            self.events.append(('text', data))
source = Body(True)
source.feed(Path('source.html').read_text())
app = Body(False)
app.feed(Path('app.html').read_text())
assert source.events == app.events
print('PASS: body DOM, content, attributes, and nesting match after explicit source-to-app class mapping; no browser/interaction assertions')
assert 'source.css' not in Path('app.html').read_text()
assert 'source-' not in Path('app.html').read_text() + Path('feature.css').read_text()
print('PASS: app has no source.css import or source- selector reuse')
PY
```

```text
PASS: 16 source CSS rule sets match implementation declarations after token expansion, including focus-within, placeholder, and parent layout; no computed style/render assertions
PASS: body DOM, content, attributes, and nesting match after explicit source-to-app class mapping; no browser/interaction assertions
PASS: app has no source.css import or source- selector reuse
```

이는 제공된 단순 CSS 규칙을 token 값으로 풀고 selector 대응 후 선언 사전을 비교하는 검사다. 브라우저 cascade/computed style, 레이아웃, 클리핑 또는 상호작용 성공을 증명하지 않는다.

## 후속 담당자에게 남은 검증

- case `create-person-step1`, viewport **390×844**에서 원본과 수정 후 구현의 실제 렌더를 각각 관찰·캡처하고 화면 전체 및 입력 부품의 배치/간격/폰트/색/외형을 대조한다.
- 기본 빈 입력·placeholder, 입력 포커스 및 blur 전환, 입력 값 표시에서 아이콘/텍스트 정렬, 입력 경계와 그림자의 스크롤 컨테이너 클리핑을 확인한다.
- 현재 제공되지 않은 수정 전 실제 렌더와 과거 증거의 비교 가능성을 확인하고, 불가능한 비교를 미확인으로 유지한다.
- 요구되는 시각 증적 및 독립 감사/visual 게이트는 후속 파이프라인 담당자가 수행한다. 이 반환은 구조 구현 결과이며 최종 시각 완료 반환이 아니다.
