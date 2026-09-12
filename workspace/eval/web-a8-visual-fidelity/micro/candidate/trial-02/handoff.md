# 이름 입력 UI 코더 반환

작업 루트: `/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/candidate/trial-02`

구조 구현과 임시 정적 검사를 수행했다. **시각 검증은 미검증**이다. 대상은 `create-person-step1`, 요구 viewport는 `390×844`이다. 브라우저, URL, 원본/구현 캡처가 제공되지 않았고 scope가 브라우저 대체 실행·설치·임의 서버 실행을 금지한다. 소스 분석을 실제 렌더 관찰로 간주하지 않았다. 전체 Django/plugin inputs·visual gate는 이번 호출 범위 밖이므로 실행하지 않았다. 일정 담당자의 비권위 메모는 외형 일치나 완료 판단의 근거로 사용하지 않았다.

## 변경

- `feature.css`의 `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);`을 추가했다.
- 원본 `.source-scroll`의 `padding: 2px 2px 4px`을 기존 토큰 `--space-half: 2px`, `--space-1: 4px`으로 그대로 대응시켰다. 스크롤 부모의 가용 너비·여백 및 자식 포커스 효과와의 관계를 복원하는 변경이다. 실제 잘림 여부는 관찰하지 않았다.
- 원본 입력창의 일반·focus-within·아이콘·placeholder·native input 선언은 기존 DS와 토큰 값이 이미 정적으로 같아 재사용했다. `tokens.css`, `app.html`, `design-system.css`는 수정하지 않았다. 앱에서 원본 CSS를 로드하거나 원본 selector를 추가하지 않았다.
- 수정 파일은 `feature.css`와 새 `handoff.md`뿐이다. 별도 계획·명세·영구 테스트·서브에이전트는 만들지 않았다.

## 실제 읽은 파일

루트 상대 경로 기준:

- `scope.md` 전체
- `guidance/implementation-ui/SKILL.md` 전체
- `guidance/implementation-ui/references/final.md`: Python으로 파일을 읽고 라우팅된 §2만 출력·검토했다. 나머지 절은 내용 검토하지 않았다.
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전체

추가로 `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md`를 읽었다. 해당 파일의 SUBAGENT-STOP에 따라 다른 파이프라인은 시작하지 않았다. 작업 디렉터리 밖의 평가 결과나 다른 실행 파일은 읽지 않았다. Serena는 정확한 CSS 선언의 짧은 수정이며 이 호출의 셸/Python 범위로 충분해 사용하지 않았다. Graphify도 사용하지 않았다.

## 수정 전 코드 기준과 세 비교

수정 전 `feature.css` 전체는 다음과 같다. 실제 수정 전 렌더는 제공되지 않아 보존하지 못했다.

```css
.people-dialog { display: flex; flex-direction: column; width: var(--dialog-width); height: var(--dialog-height); padding: var(--space-5); gap: var(--space-5); border-radius: var(--radius-dialog); background: var(--surface-card); }
.people-dialog h1 { margin: var(--zero); font-size: var(--title-size); line-height: var(--title-line); }
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; }
.people-step { display: flex; flex-direction: column; gap: var(--space-6); }
.people-note { margin: var(--zero); color: var(--text-secondary); font-size: var(--caption-size); line-height: var(--caption-line); }
```

| 비교쌍 | 대상·양쪽 근거·차이 | 결과 |
|---|---|---|
| 기존 원본 ↔ 현재 기준 원본 | 이 호출에서 원본을 교체하지 않았다. `source.html` SHA-256 `269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090`, `source.css` SHA-256 `0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b`가 수정 전후 동일하다. 별도의 과거 원본·렌더 이력은 제공되지 않았다. | 이번 호출의 원본 파일 불변만 확인. 과거 버전 및 실제 렌더 비교는 미실행. |
| 현재 기준 원본 ↔ 수정 후 실제 구현 | `source.html/source.css`와 `app.html/design-system.css/tokens.css/feature.css`의 소스를 직접 읽고 정적으로 대조했다. 토큰 치환 후 16개 CSS 규칙의 선언이 일치한다. 실제 원본/구현 렌더·캡처는 없다. | 정적 선언 일치. 시각 일치는 미검증. |
| 수정 전 실제 구현 ↔ 수정 후 실제 구현 | 위 수정 전 코드 및 SHA-256 `30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d`와 수정 후 SHA-256 `1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e`를 연결했다. 차이는 `.people-scroll` padding 선언 하나다. | 코드 변경 범위 확인. 실제 렌더 회귀 비교는 미검증. 후속 담당자는 위 코드 기준을 별도 승인된 관찰 환경에서 복원해 비교할 수 있다. |

## 스타일 적용 근거

아래 모든 행의 대상 case는 `create-person-step1`, 요구 viewport는 `390×844`이다. viewport는 실행한 브라우저 설정이 아니라 인계된 요구다.

| case·대상/조작 상태 | 원본 위치·구성(관련 부모 포함) | 구현 위치·구성 | 실제 수행·관찰 근거 | 결과·차이 또는 미검증 사유/다음 실행자·필요 조건 |
|---|---|---|---|---|
| 기본 상태·입력창 배치 | `source.html`의 dialog → scroll → step → label → input wrapper/아이콘/native input 관계. `source.css`: dialog 344×316px, padding/gap 20px; scroll flex/min-height 0/gap 24px/overflow-y auto/padding 2px 2px 4px; step gap 24px, field gap 8px. | `app.html`의 동일 부모·자식 순서. `feature.css`의 `.people-dialog/.people-scroll/.people-step`, `design-system.css`의 `.ds-field`; dialog/space 토큰 사용. scroll의 누락 여백 추가. | HTML·CSS 원문 직접 읽기, 아래 CSS 선언 대조 명령. 브라우저 조작·URL·캡처 없음. | 코드의 관계 및 선언을 대조했다. 실제 위치·크기·스크롤 경계는 미검증. 후속 관찰 담당자가 원본/구현을 390×844에서 렌더해 확인해야 한다. |
| 기본 상태·입력창/아이콘/placeholder | `.source-input`: 높이 52px, gap 10px, 좌우 14px, 1px #d5d1c7 border, radius 16px, 흰 배경. icon 18px/20px #888276. native input flex/min-width 0/너비 100%/border·padding 0/outline none/inherited font/transparent, placeholder #888276. 부모 field/scroll은 위 행과 동일. | `.ds-input/.ds-icon/.ds-input input/::placeholder`가 기존 tokens를 사용하며 같은 값. 원본과 같은 `○` 자식과 placeholder 문구, label wrapper 유지. | 원문 및 토큰 치환 후 정적 선언 대조. 입력·포커스 조작, computed style, 실제 폰트/색/문자 렌더는 미관찰. | DS 재사용의 정적 근거만 확인. 입력 전/텍스트 입력 후 실제 외형은 후속 담당자가 원본과 구현 양쪽에서 대조해야 한다. |
| focus-within·전환·부모 클리핑 | `.source-input:focus-within`: border #8f675b, shadow `0 0 0 3px rgba(143, 103, 91, .18)`; 일반 상태 transition은 border-color·box-shadow 160ms ease. 관련 scroll은 overflow-y auto 및 2px/2px/4px padding. | `.ds-input:focus-within`: `--accent`, `--input-focus-shadow`; 일반 상태 `--duration-fast`. `.people-scroll`의 동일 overflow 및 복원한 여백. 자식 native outline none 그대로 유지. | 해당 선택자·토큰·부모를 직접 읽고 선언 비교했다. focus/blur/스크롤·전환/그림자 클리핑은 실제로 발동하지 않았다. | 시각 미검증. 후속 담당자가 원본/구현 양쪽에서 키보드 또는 클릭 포커스와 해제를 수행하고 스크롤 부모 경계에서 그림자와 잘림을 캡처·대조해야 한다. 원본 자체의 클리핑 여부도 추정하지 않았다. |
| 주변 배치·제목/안내문/버튼 | body 중앙 정렬·페이지 배경·14px/1.5 sans-serif; h1 20px/28px; note 13px/20px; 버튼 44px/radius 14px. dialog 및 step의 형제 순서·간격은 첫 행. | `design-system.css` body/`.ds-button`, `feature.css` h1/`.people-note`, 기존 tokens. DOM 문구·순서 유지. | 원문 읽기 및 정적 CSS 대조. 실제 렌더·캡처 없음. | 정적 선언 일치. 입력창 부모 여백 변경 후 안내문과 버튼 배치 회귀는 후속 담당자의 원본/수정 전/수정 후 렌더 비교가 필요하다. |

## 실행한 검증 명령과 출력

모든 명령의 cwd는 위 작업 루트다. 임시 검증은 스트림에서 실행했고 테스트 파일을 추가하지 않았다. 아래 세 명령은 모두 exit 0이었다.

### 1. 제공된 구조 검사

```sh
python3 smoke.py
```

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

### 2. CSS 정적 선언 대조

```sh
python3 - <<'PY'
from pathlib import Path
import re

def declarations(text):
    return dict(item.strip().split(':', 1) for item in text.split(';') if item.strip())

def rules(text):
    return {selector.strip(): {key: value.strip() for key, value in declarations(body).items()} for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', text)}

tokens = rules(Path('tokens.css').read_text())[':root']
source = rules(Path('source.css').read_text())
implementation = rules(Path('design-system.css').read_text() + '\n' + Path('feature.css').read_text())
selector_map = {
    '.source-dialog': '.people-dialog', 'h1': '.people-dialog h1',
    '.source-scroll': '.people-scroll', '.source-step': '.people-step',
    '.source-field': '.ds-field', '.source-label': '.ds-label',
    '.source-input': '.ds-input', '.source-input:focus-within': '.ds-input:focus-within',
    '.source-icon': '.ds-icon', '.source-input input': '.ds-input input',
    '.source-input input::placeholder': '.ds-input input::placeholder',
    '.source-note': '.people-note', 'button': '.ds-button',
}
for selector, expected in source.items():
    target = selector_map.get(selector, selector)
    actual = {key: re.sub(r'var\((--[\w-]+)\)', lambda match: tokens[match.group(1)], value) for key, value in implementation[target].items()}
    assert actual == expected, (selector, target, expected, actual)
print(f'PASS: {len(source)} source CSS rule declarations match mapped implementation rules after token substitution.')
print('STATIC ONLY: no browser cascade, computed styles, layout, focus interaction, clipping, or visual comparison was observed.')
PY
```

```text
PASS: 16 source CSS rule declarations match mapped implementation rules after token substitution.
STATIC ONLY: no browser cascade, computed styles, layout, focus interaction, clipping, or visual comparison was observed.
```

### 3. 파일 보존 및 최소 변경 확인

아래 expected 값은 첫 수정 전에 Python `sha256(Path(name).read_bytes()).hexdigest()`로 실제로 읽어 출력한 값이다.

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
expected = {
    'source.html': '269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090',
    'source.css': '0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b',
    'app.html': '7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3',
    'design-system.css': 'eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f',
    'tokens.css': 'c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c',
    'smoke.py': '85be8fb63c6370cad01069a0ca9659a273bb42f2e036eb2357ac402ae01a807c',
    'scope.md': 'dacdb19cc71870666eafed6c63e169b8f174fecf709ee3f7b0e10dd1e37b9ded',
    'guidance/implementation-ui/SKILL.md': '07984244deb9220f7ea5282b01bbac7b9f4747ad714adb458f3e1f2418b808e7',
    'guidance/implementation-ui/references/final.md': '7ef6ad2ede128aab920e3b5a2e41aed5d7dd7aba83e7c6ded4a59f6de9ccc464',
}
for name, digest in expected.items():
    assert sha256(Path(name).read_bytes()).hexdigest() == digest, name
feature = Path('feature.css').read_text()
addition = ' padding: var(--space-half) var(--space-half) var(--space-1);'
assert feature.count(addition) == 1
assert sha256(feature.replace(addition, '').encode()).hexdigest() == '30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d'
print('PASS: 9 source, guidance, and unchanged implementation files retain their initial SHA-256 hashes.')
print('PASS: feature.css differs from the initial version only by the people-scroll padding declaration.')
print('feature.css after SHA-256: ' + sha256(feature.encode()).hexdigest())
PY
```

```text
PASS: 9 source, guidance, and unchanged implementation files retain their initial SHA-256 hashes.
PASS: feature.css differs from the initial version only by the people-scroll padding declaration.
feature.css after SHA-256: 1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e
```

## 남은 검증과 다음 실행자

후속 브라우저 관찰 담당자가 승인된 브라우저·원본/구현 로드 경로 및 캡처 저장 위치를 제공받아 위 case를 `390×844`에서 관찰해야 한다. 기본 상태, placeholder, 텍스트 입력, focus/blur 전환 및 scroll 부모 경계의 효과·주변 배치를 원본과 직접 대조한다. 수정 전 코드는 위에 보존했지만 수정 전/후 실제 렌더 회귀 비교는 실행하지 않았다. 원본/구현 캡처를 확보하고 해당 실제 관찰을 Coordinator의 시각 검증 기록에 통합해야 시각 완료 여부를 판단할 수 있다. 이번 반환은 구조 수정과 정적 검사 완료이며, 시각 완료·visual gate 통과·배포 가능 판정이 아니다.
