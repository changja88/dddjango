# 이름 입력 UI 코더 반환

상태: **요청된 구조 수정 완료, 시각 검증 미검증**. 대상은 `create-person-step1`, viewport `390×844`이다. 실행 경로는 이 `trial-02` 디렉터리다. 실제 원본/구현 렌더와 캡처는 제공되지 않았고 생성하지 않았다. 일정 담당자의 비권위 메모는 완료 판정이나 이탈 승인으로 사용하지 않았다.

## 읽은 파일과 적용 범위

- `scope.md` 전체.
- `guidance/implementation-ui/SKILL.md` 전체.
- `guidance/implementation-ui/references/final.md`의 §2만. 소스의 DOM 관계·스타일 효과 보존, 토큰 재사용, 코드 대조와 실제 시각 검증 구분을 적용했다.
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전체.
- 전역 `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md` 전체. 지정 작업을 실행하는 서브에이전트는 이 스킬을 무시하라는 `SUBAGENT-STOP`에 따라 추가 워크플로를 시작하지 않았다.

다른 실행의 파일이나 이 디렉터리 밖 평가 결과는 읽지 않았다. 서브에이전트, 서버, 브라우저, 설치, inputs/visual gate, native Django/plugin 파이프라인, 별도 계획·명세·영구 테스트는 실행/생성하지 않았다. scope의 구조 구현 및 반환 범위가 전체 파이프라인 지침보다 구체적이므로 구조 수정만 수행했다.

## 수정한 파일

- `feature.css`: `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);` 한 선언 추가.
- `handoff.md`: 이 작업의 사실 기록을 신규 작성.

`tokens.css`, `app.html`, `design-system.css`, 원본은 변경하지 않았다. 원본의 `2px 2px 4px`과 정확히 같은 기존 토큰을 재사용했다. 원본 파일 import와 원본 selector 복사는 하지 않았다.

수정 전 구현 코드:

```css
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; }
```

수정 후 구현 코드:

```css
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; padding: var(--space-half) var(--space-half) var(--space-1); }
```

## 직접 대조한 범위

| 원본 → 구현 | 소스에서 확인한 값/구성 | 적용 위치 및 결과 |
|---|---|---|
| `.source-dialog` → `.people-dialog` | flex column, 344×316px, padding/gap 20px, radius 24px, white | 기존 `feature.css` + `tokens.css` 선언 대응 |
| `.source-scroll` → `.people-scroll` | flex 성장, min-height 0, gap 24px, overflow-y auto, padding 2px 2px 4px | 누락된 padding을 기존 `--space-half`/`--space-1`로 보존 |
| `.source-step`, `.source-field` → `.people-step`, `.ds-field` | 세로 배치와 gap 24px/8px, label-input 부모/자식 관계 | 기존 HTML 및 CSS 대응 |
| `.source-input` → `.ds-input` | 52px 높이, 10px gap, 좌우 14px padding, 1px border, radius 16px, white 배경, 160ms border/shadow transition | 기존 DS와 토큰 대응 |
| `.source-input:focus-within` → `.ds-input:focus-within` | accent border 및 `0 0 0 3px rgba(143, 103, 91, .18)` shadow | 기존 DS와 `--accent`/`--input-focus-shadow` 대응. 포커스 실제 화면은 미관찰 |
| icon, input, placeholder → DS 자식/상태 | 원형 문자, icon 18px/20px, tertiary 색, input flex/min-width/outline/background/font, placeholder 색 | 원본/구현 HTML과 DS 소스를 직접 확인 |
| 제목, label, note, button | 문구, 형제 순서, 타이포, 색, button 44px/radius 14px | 기존 HTML, DS, feature 및 토큰 대응 |

원본 16개 CSS 규칙 블록 전체를 구현의 대응 selector에 연결하고 토큰을 풀어 선언 사전이 동일함을 임시 정적 검사로 확인했다. 이는 CSS 선언의 대응 확인이며 최종 computed style, 가림·클리핑, 실제 화면의 일치 판정은 아니다.

## 비교 3종 및 증거 한계

| 비교쌍 | 범위/근거 | 차이와 결과 |
|---|---|---|
| 기존 원본 ↔ 현재 기준 원본 | 이번 호출 처음 읽은 `source.html`/`source.css`의 SHA-256를 수정 후 재확인 | 원본 변경 없음. 이 호출 이전 원본 버전이나 렌더 이력은 전달되지 않음 |
| 현재 원본 ↔ 수정 후 구현 | 전체 이름 입력 부품과 화면 배치의 HTML/CSS 대조 및 16개 규칙 토큰 확장 검사 | 선언 대응 확인. 원본/구현 캡처가 없어 실제 시각 비교는 미검증 |
| 수정 전 구현 ↔ 수정 후 구현 | 수정 전 `.people-scroll` 원문과 파일 hashes를 변경 전에 보존, 수정 후 hashes 확인 | padding 한 선언 추가. 실제 수정 전/후 렌더가 없어 시각 회귀는 미검증 |

## 실행한 검증 명령과 출력

아래 명령은 모두 이 `trial-02` 디렉터리에서 실행했다. 별도 검사 파일은 만들지 않았다.

### 수정 전/후 구조 검사

수정 전 1회, 수정 후 1회 실행했으며 두 실행 모두 exit 0, 출력 동일:

```sh
python3 smoke.py
```

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

### 수정 전 코드 기준 보존

명령(exit 0):

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
for name in ('source.html', 'source.css', 'app.html', 'design-system.css', 'tokens.css', 'feature.css'):
    content = Path(name).read_bytes()
    print(f'{name}: {sha256(content).hexdigest()}')
print('BEFORE .people-scroll:')
print(next(line for line in Path('feature.css').read_text().splitlines() if line.startswith('.people-scroll')))
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
BEFORE .people-scroll:
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; }
```

### 수정 후 정적 선언 대조 및 불변 파일 확인

명령(exit 0):

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
import re

def rules(text):
    return {
        selector.strip(): dict((name.strip(), value.strip()) for name, value in
        (item.split(':', 1) for item in body.split(';') if item.strip()))
        for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', text)
    }

tokens = rules(Path('tokens.css').read_text())[':root']
source = rules(Path('source.css').read_text())
implementation = rules(Path('design-system.css').read_text() + '\n' + Path('feature.css').read_text())
selector_map = {
    '.source-dialog': '.people-dialog', 'h1': '.people-dialog h1',
    '.source-scroll': '.people-scroll', '.source-step': '.people-step',
    '.source-field': '.ds-field', '.source-label': '.ds-label',
    '.source-input': '.ds-input', '.source-icon': '.ds-icon',
    '.source-note': '.people-note', 'button': '.ds-button',
}
for selector, declarations in source.items():
    target = selector
    for original in sorted(selector_map, key=len, reverse=True):
        if selector == original or selector.startswith(original + ' ') or selector.startswith(original + ':'):
            target = selector_map[original] + selector[len(original):]
            break
    actual = {
        name: re.sub(r'var\((--[\w-]+)\)', lambda match: tokens[match.group(1)], value)
        for name, value in implementation[target].items()
    }
    assert declarations == actual, (selector, target, declarations, actual)
print(f'PASS: {len(source)} source CSS rule blocks match mapped implementation declarations after token expansion; static only')
print('source scroll padding:', source['.source-scroll']['padding'])
print('implementation scroll padding:', implementation['.people-scroll']['padding'])
expected = {
    'source.html': '269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090',
    'source.css': '0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b',
    'app.html': '7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3',
    'design-system.css': 'eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f',
    'tokens.css': 'c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c',
}
for name, digest in expected.items():
    assert sha256(Path(name).read_bytes()).hexdigest() == digest, name
print('PASS: source.html, source.css, app.html, design-system.css, tokens.css unchanged')
print('feature.css after:', sha256(Path('feature.css').read_bytes()).hexdigest())
PY
```

출력:

```text
PASS: 16 source CSS rule blocks match mapped implementation declarations after token expansion; static only
source scroll padding: 2px 2px 4px
implementation scroll padding: var(--space-half) var(--space-half) var(--space-1)
PASS: source.html, source.css, app.html, design-system.css, tokens.css unchanged
feature.css after: 1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e
```

## 후속 담당자의 남은 검증

원본과 구현을 허용된 브라우저 환경에서 같은 `390×844`로 실제 관찰·별도 캡처해야 한다. 기본/빈 값 placeholder, 이름 입력 후, 포커스 진입·해제와 160ms 전환을 대조하고 입력/아이콘/문구/버튼의 주변 배치, 스크롤 영역의 여백과 포커스 shadow의 가림·클리핑을 확인해야 한다. 수정 전 화면의 렌더 비교도 아직 없으며 보존된 수정 전 코드와 hashes를 근거로 허용 범위 내에서 준비해야 한다. 이번 호출은 브라우저/GUI/서버 URL/캡처를 제공받지 않았고 실행도 금지되어 있어 이 검증을 넘긴다. 이 반환을 visual 완료나 배포 승인으로 사용할 수 없다.

Serena는 사용하지 않았다. 이 작업은 지정 HTML/CSS의 정확한 선언 대조와 한 줄 수정으로 기본 파일 도구가 직접 해당하며, 도구 초기화나 심볼 조사가 필요하지 않았다. Graphify도 사용하지 않았다.
