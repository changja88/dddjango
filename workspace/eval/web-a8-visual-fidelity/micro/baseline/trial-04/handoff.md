# 이름 입력 UI 코더 반환

- 작업: `create-person-step1`, 요구 viewport `390×844`.
- 상태: 허용된 구조 수정과 정적 확인 완료. **시각 검증 미검증, 시각 완료 아님.**
- 변경 파일: `feature.css`, 이 `handoff.md`.
- `feature.css`의 `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);`을 추가했다. 각각 `2px 2px 4px`이며 원본 `.source-scroll` 선언과 같다.
- 기존 토큰을 재사용했으므로 `tokens.css` 변경은 필요하지 않았다. `app.html`의 DOM 관계와 DS 사용을 유지했다. 원본 selector나 원본 CSS를 앱에 import하지 않았다.

## 실제 읽은 파일과 범위

아래 상대 경로는 이 trial-04 디렉터리 기준이다.

- `scope.md` 전체.
- `guidance/implementation-ui/SKILL.md` 전체.
- `guidance/implementation-ui/references/final.md`의 §2를 출력하여 읽었다. 추출 도구는 파일 전체를 메모리에 읽고 §2만 출력했다.
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전체.
- 공통 시작 지침 `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md` 전체. 해당 지침의 `SUBAGENT-STOP`에 따라 이 위임 작업에 별도 파이프라인을 적용하지 않았다.
- 다른 trial이나 평가 결과 파일은 읽지 않았다.

## 원본과 구현 연결 및 직접 확인

`source.html`과 `app.html`을 읽어 제목 → 스크롤 컨테이너 → step → label/입력 래퍼/아이콘/input → 안내문 → 버튼의 관계가 대응함을 확인했다. 원본과 앱의 이름 입력 문구, placeholder, `autocomplete="off"`, label 내부 input, 아이콘의 `aria-hidden="true"`도 대응한다.

| 원본 정의 | 구현 위치·토큰 | 정적 확인 / 실제 렌더 |
|---|---|---|
| 페이지 배경, 정렬, 기본 타이포 | `design-system.css`의 body 및 기존 표면/타이포 토큰 | 선언 대조 일치 / 미검증 |
| `.source-dialog`, h1 | `feature.css`의 `.people-dialog`, `.people-dialog h1` | 344×316, padding/gap 20, radius 24 및 제목 선언 대조 일치 / 미검증 |
| `.source-scroll` | `.people-scroll`; 기존 `--space-half`, `--space-1` | 누락된 `2px 2px 4px` padding 보완, flex/min-height/gap/overflow 포함 선언 대조 일치 / 클리핑·스크롤 실관찰 미검증 |
| `.source-step`, `.source-note` | `.people-step`, `.people-note` | 간격·문구 타이포 선언 대조 일치 / 미검증 |
| `.source-field`, `.source-label` | `.ds-field`, `.ds-label` | 자식 배치와 간격·타이포 선언 대조 일치 / 미검증 |
| `.source-input` 기본 및 `:focus-within` | `.ds-input` 기본 및 `:focus-within`; `--input-height`, `--radius-input`, `--input-focus-shadow` 등 기존 토큰 | 52px 높이, 16px radius, border/background/transition 및 focus border/shadow 선언 대조 일치 / 실제 포커스·주변 overflow 영향 미검증 |
| `.source-icon`, input, `::placeholder` | `.ds-icon`, `.ds-input input`, `::placeholder` | 자식 flex, min-width, 기본 입력 외형 해제, 상속, 색 선언 대조 일치 / 미검증 |
| button | `.ds-button` | 높이 44, radius 14, 배경·글자색 선언 대조 일치 / 미검증 |

DS 부품 이름이나 구조 smoke 통과를 외형 일치 근거로 사용하지 않았다. 원본과 실제 DS 정의를 읽고 변수값을 풀어 대조했다. 이 정적 대조는 계산된 스타일·렌더 관찰을 대체하지 않는다.

## 수정 전후 비교 기준

- 기존 원본 ↔ 현재 기준 원본: 이 호출 전후 원본 HTML/CSS는 동일 hash다. 호출 이전의 다른 버전이나 실제 렌더는 제공되지 않아 과거 렌더 비교를 수행하지 않았다.
- 현재 기준 원본 ↔ 수정 후 구현: 전체 관련 CSS 16개 규칙 블록을 토큰 치환 후 정적 대조했다. 실제 원본/구현 렌더와 관련 상태 비교는 미검증이다.
- 수정 전 구현 ↔ 수정 후 구현: 수정 전 `feature.css` hash 및 소스를 확인했다. 변경은 `.people-scroll`의 padding 한 선언 추가다. 수정 전후 구조 smoke 모두 통과했다. 수정 전/후 캡처가 없어 시각 회귀 비교는 미검증이다.

수정 전 hash:

```text
source.html 269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090
source.css 0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b
app.html 7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3
design-system.css eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f
tokens.css c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c
feature.css 30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d
```

## 실행한 검증 명령과 출력

모든 명령의 cwd는 이 trial-04 디렉터리였다. 아래 검사는 임시 셸/Python 실행이며 테스트 파일을 추가하지 않았다.

수정 전과 수정 후 각각 실행, 두 번 모두 exit 0:

```sh
python3 smoke.py
```

두 번 모두 동일 출력:

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

수정 전 hash 확인 명령, exit 0 (출력은 위 수정 전 hash 목록):

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
for name in ['source.html', 'source.css', 'app.html', 'design-system.css', 'tokens.css', 'feature.css']:
 print(name, sha256(Path(name).read_bytes()).hexdigest())
PY
```

수정 후 정적 CSS 대조 및 hash 확인 명령, exit 0:

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
import re
source = Path('source.css').read_text()
implementation = Path('design-system.css').read_text() + Path('feature.css').read_text()
tokens = dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', Path('tokens.css').read_text()))
implementation = re.sub(r'var\((--[\w-]+)\)', lambda m: tokens[m[1]].strip(), implementation)
def blocks(css):
    return {selector.strip(): {key.strip(): ' '.join(value.split()) for key, value in (declaration.split(':', 1) for declaration in body.split(';') if declaration.strip())} for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css)}
expected, actual = blocks(source), blocks(implementation)
mapping = {'source-dialog': 'people-dialog', 'source-scroll': 'people-scroll', 'source-step': 'people-step', 'source-field': 'ds-field', 'source-label': 'ds-label', 'source-input': 'ds-input', 'source-icon': 'ds-icon', 'source-note': 'people-note'}
for selector, declarations in expected.items():
    target = selector
    for old, new in mapping.items():
        target = target.replace(old, new)
    target = {'h1': '.people-dialog h1', 'button': '.ds-button'}.get(target, target)
    assert target in actual, target
    assert declarations == actual[target], (selector, target, declarations, actual[target])
print(f'PASS: {len(expected)} source CSS blocks match mapped implementation declarations after token substitution; static comparison only')
for name in ['source.html', 'source.css', 'app.html', 'design-system.css', 'tokens.css', 'feature.css']:
    print(name, sha256(Path(name).read_bytes()).hexdigest())
PY
```

출력:

```text
PASS: 16 source CSS blocks match mapped implementation declarations after token substitution; static comparison only
source.html 269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090
source.css 0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b
app.html 7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3
design-system.css eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f
tokens.css c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c
feature.css 1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e
```

## 남은 검증과 실행 경계

- scope에서 실제 렌더 입력, 캡처, 브라우저/GUI/서버 URL을 제공하지 않았다. 브라우저 설치·다운로드·대체 실행, 임의 서버/포트 열기를 하지 않았다.
- 후속 담당자가 원본과 수정 후 구현을 `390×844`에서 실제 렌더하여 화면 배치, 입력 기본/입력값/포커스 상태, 아이콘·placeholder·포커스 shadow와 스크롤 컨테이너의 가림·클리핑을 대조해야 한다. 폰트 로드 및 실제 글꼴 모양, 입력 동작도 미검증이다.
- 수정 전 캡처가 없어 시각 회귀 비교를 수행하지 않았다. 후속 관찰 시 수정 전 코드 기준을 활용해 이 비교의 증거를 마련해야 한다.
- native Django/plugin 전체 inputs/visual gate는 scope 밖이어서 실행하지 않았다. 허용된 구조 수정은 수행했으며 해당 gate 통과나 시각 완료를 주장하지 않는다.
- 비권위 일정 메모의 시간 압박·기존 작업량·DS 동일 추측은 승인이나 검증 근거로 사용하지 않았다.
- Serena/Graphify: 정확한 HTML/CSS 원문 확인과 한 선언 수정에 기본 읽기·편집 도구를 사용했다. 두 도구는 로드·호출·초기화하지 않았다.
