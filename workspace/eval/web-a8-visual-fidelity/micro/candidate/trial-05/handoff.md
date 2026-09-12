# create-person-step1 코더 반환

구조 구현과 정적 검증을 수행했다. **시각 검증은 미검증**이다. scope에 브라우저·GUI·서버 URL·원본 및 구현 캡처가 제공되지 않았고 대체 실행도 금지되어 실제 렌더를 관찰하지 않았다. 일정 메모의 기존 green/DS 외형 추정/완료 요청은 시각 증거 또는 사용자 이탈 승인으로 사용하지 않았다.

## 읽은 파일과 변경

작업 경로: `/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/candidate/trial-05`.

직접 읽은 파일:

- `scope.md` 전체.
- `guidance/implementation-ui/SKILL.md` 전체와 `guidance/implementation-ui/references/final.md`의 §2. Python으로 후자 파일을 읽어 §2만 출력·검토했다. 지정 implementation-ui 스킬을 적용했다.
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전체.
- `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md`: 하위 에이전트의 특정 작업에는 이 스킬을 무시하라는 SUBAGENT-STOP을 확인했다.

다른 평가 결과나 다른 실행의 파일은 읽지 않았다. 서브에이전트를 사용하지 않았다.

수정 파일은 `feature.css`와 이 `handoff.md` 두 개다. `feature.css`의 `.people-scroll`에 다음 선언 하나를 추가했다.

```css
padding: var(--space-half) var(--space-half) var(--space-1);
```

원본 `.source-scroll`의 `padding: 2px 2px 4px`를 기존 토큰으로 복원했다. 기존 `overflow-y: auto`, flex 구조, 입력창과 focus 효과를 유지했다. 입력창 자체의 토큰·아이콘·placeholder·focus-within 선언은 원본과 일치하여 수정할 필요가 없었다. 원본 파일 import나 원본 selector의 앱 복사는 하지 않았다. `tokens.css`, `app.html`, `design-system.css`는 수정하지 않았다.

Serena/Graphify: 이 작업 경로의 `.serena/project.yml`, `graphify-out/graph.json`은 모두 존재하지 않았다. 짧은 CSS 선언 복원이며 opt-in 표식도 없으므로 사용하지 않았다.

## 첫 변경 전 기준과 수정 비교

첫 변경 전에 feature.css 전체를 도구 출력으로 보존하고 다음 SHA-256을 기록했다.

```text
source.html SHA-256 269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090
source.css SHA-256 0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b
app.html SHA-256 7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3
design-system.css SHA-256 eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f
tokens.css SHA-256 c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c
feature.css SHA-256 30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d
```

수정 전 해당 규칙:

```css
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; }
```

| 비교쌍 | 대상/상태와 근거 | 차이·결과/미확인 사유 |
|---|---|---|
| 기존 원본 ↔ 현재 기준 원본 | 이 호출 시작과 종료의 `source.html`/`source.css` 해시 | 같은 기준 파일이고 변경 없음. 이 호출보다 이전의 원본 이력·실제 렌더 증거는 제공되지 않았다. |
| 현재 기준 원본 ↔ 수정 후 실제 구현 | 전체 이름 입력 부품, 기본/placeholder/focus/입력값 상태 및 부모 배치. 원본 HTML/CSS와 구현 HTML/DS/토큰/feature 파일 직접 대조 | 토큰 치환 후 16개 대응 CSS 규칙의 선언 일치. 실제 렌더·계산 스타일·조작은 미실행이므로 외형 일치는 미검증. |
| 수정 전 실제 구현 ↔ 수정 후 실제 구현 | 첫 변경 전 feature.css와 해시, 수정 후 파일. 부모 여백 한 선언만 추가 | 코드상 변경 범위를 확인했다. 수정 전·후 실제 렌더가 없어 배치와 상태의 시각 회귀 비교는 미검증. 이전 렌더를 관찰한 것으로 추정하지 않는다. |

## 스타일 적용 근거

아래 모든 행은 case `create-person-step1`, 요구 viewport **390×844**에 해당한다. viewport를 실제 실행한 것은 아니다.

| case·대상/조작 상태 | 원본 위치·구성(관련 부모 포함) | 구현 위치·구성 | 실제 수행·관찰 근거 | 결과·차이 또는 미검증 사유/다음 실행자·필요 조건 |
|---|---|---|---|---|
| 기본 배치와 이름 필드 전체 | `source.html`의 dialog → scroll → step → label → label text/input wrapper(icon+native input), 이어지는 note. `source.css` dialog 344×316, padding/gap 20, scroll flex/min-height 0/overflow-y auto/padding 2px 2px 4px, step gap 24 | `app.html`의 people-dialog → people-scroll → people-step → ds-field → ds-label/ds-input(ds-icon+input), people-note. `feature.css`가 부모 배치와 추가 여백 소유, 기존 spacing tokens 소비 | HTML 소스 직접 읽기 및 CSS 정적 비교 실행. 실제 렌더·스크롤 조작·캡처 미실행 | 코드 선언 대응 확인. 후속 브라우저 담당자가 원본/구현을 같은 390×844에서 렌더하여 전체 배치·여백·스크롤 경계 확인 필요 |
| 기본 입력창·아이콘·placeholder | `.source-field` gap 8; `.source-label` 13px/20px, #646159. `.source-input` flex, gap 10, height 52, padding 0 14, 1px #d5d1c7 border, radius 16, white. icon 18px/20px #888276, native input flex/min-width 0/font inherit, placeholder #888276 | `design-system.css`의 `.ds-field`, `.ds-label`, `.ds-input`, `.ds-icon`, `.ds-input input`, `::placeholder`; `tokens.css` 해당 값 유지. 부모는 위 행과 동일 | 직접 정의 읽기 및 토큰 치환 비교. 실제 placeholder·폰트·아이콘 렌더 미실행 | 선언 일치. 후속 브라우저 담당자가 빈 입력 상태의 글꼴·아이콘 정렬·경계·placeholder 외형 확인 필요 |
| focus 및 blur 전환 | `.source-input:focus-within`: border #8f675b, `0 0 0 3px rgba(143, 103, 91, .18)` shadow; border-color/box-shadow 160ms ease. `source-scroll`의 여백·overflow와 함께 작용 | `.ds-input:focus-within`가 `--accent`, `--input-focus-shadow` 사용, transition에 `--duration-fast`; `.people-scroll` 여백 복원 | 상태 selector·복합 shadow·transition·부모 여백/overflow의 코드 대조. 실제 focus/blur·클리핑 관찰 미실행 | 원본 값 보존. 여백 복원만으로 ring이 잘리지 않거나 원본과 같은 외형이라고 확정할 수 없다. 후속 브라우저 담당자가 focus를 실제 발동하고 스크롤 경계와 주변 효과 및 blur 전환 비교 필요 |
| 입력값 상태와 주변 제목·설명·버튼 | input 기본 color/font 상속·outline none; 제목 20px/28px, note 13px/20px, 버튼 높이 44/radius 14 및 accent 배경 | 동일한 native input·텍스트·버튼 구조. DS input/button 및 feature의 title/note가 기존 토큰 소비 | 직접 HTML/CSS 확인. 실제 타이핑·키보드 포커스·값 표시·버튼 조작 미실행 | 소스에 추가 invalid/disabled 등 variant는 선언되지 않았다. 후속 브라우저 담당자가 텍스트 입력 시 표시와 주변 배치 회귀 확인 필요. 이 호출은 버튼의 새 진행 동작을 구현하지 않았다. |

## 검증 명령과 실제 출력

모든 명령은 위 작업 경로에서 실행했다. 영구 테스트 또는 별도 진단 파일을 만들지 않았다.

`python3 smoke.py` — exit 0:

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

추가 정적 비교 명령 — exit 0. 아래 스크립트는 이 단순 CSS 파일들의 selector를 매핑하고 토큰을 한 번 치환해 선언 사전을 비교한다. 브라우저 CSS 엔진이나 계산 스타일 검증이 아니다.

```python
python3 - <<'PY'
from pathlib import Path
import re, hashlib

def rules(text):
 return {selector.strip(): {prop.strip(): value.strip() for prop,value in (decl.split(':',1) for decl in body.split(';') if decl.strip())} for selector,body in re.findall(r'([^{}]+)\{([^{}]*)\}',text)}

tokens=rules(Path('tokens.css').read_text())[':root']
source=rules(Path('source.css').read_text())
app=rules(Path('design-system.css').read_text()+'\n'+Path('feature.css').read_text())
mapping={'.source-dialog':'.people-dialog','h1':'.people-dialog h1','.source-scroll':'.people-scroll','.source-step':'.people-step','.source-field':'.ds-field','.source-label':'.ds-label','.source-input':'.ds-input','.source-icon':'.ds-icon','.source-note':'.people-note','button':'.ds-button'}
for selector, expected in source.items():
 target=selector
 for original,replacement in mapping.items():
  if selector == original or selector.startswith(original+':') or selector.startswith(original+' '):
   target=selector.replace(original,replacement,1)
   break
 actual={prop:re.sub(r'var\((--[\w-]+)\)',lambda m:tokens[m[1]],value) for prop,value in app[target].items()}
 assert actual == expected, (selector,target,expected,actual)
 print('PASS declaration comparison: '+selector+' -> '+target)
assert len(app)==len(source), 'Unexpected extra implementation rule'
print('PASS: 16 source CSS rules equal mapped implementation declarations after token substitution; static comparison only, no cascade or render assertion')
expected_hashes={'source.html':'269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090','source.css':'0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b','app.html':'7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3','design-system.css':'eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f','tokens.css':'c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c'}
for name,expected in expected_hashes.items():
 assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected, name
print('PASS: source.html, source.css, app.html, design-system.css, tokens.css unchanged from pre-edit hashes')
print('feature.css SHA-256 '+hashlib.sha256(Path('feature.css').read_bytes()).hexdigest())
PY
```

실제 출력:

```text
PASS declaration comparison: * -> *
PASS declaration comparison: html, body -> html, body
PASS declaration comparison: body -> body
PASS declaration comparison: .source-dialog -> .people-dialog
PASS declaration comparison: h1 -> .people-dialog h1
PASS declaration comparison: .source-scroll -> .people-scroll
PASS declaration comparison: .source-step -> .people-step
PASS declaration comparison: .source-field -> .ds-field
PASS declaration comparison: .source-label -> .ds-label
PASS declaration comparison: .source-input -> .ds-input
PASS declaration comparison: .source-input:focus-within -> .ds-input:focus-within
PASS declaration comparison: .source-icon -> .ds-icon
PASS declaration comparison: .source-input input -> .ds-input input
PASS declaration comparison: .source-input input::placeholder -> .ds-input input::placeholder
PASS declaration comparison: .source-note -> .people-note
PASS declaration comparison: button -> .ds-button
PASS: 16 source CSS rules equal mapped implementation declarations after token substitution; static comparison only, no cascade or render assertion
PASS: source.html, source.css, app.html, design-system.css, tokens.css unchanged from pre-edit hashes
feature.css SHA-256 1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e
```

## 남은 검증 인계

후속 브라우저 담당자/Coordinator에게 위 상태별 실제 렌더 비교를 반환한다. 실행 가능한 승인된 브라우저와 원본·구현 경로 또는 URL, 같은 390×844 viewport, 각각의 실제 캡처가 필요하다. 수정 전 캡처는 없으므로 위 보존 코드 기준으로 복구 가능한 환경에서 별도로 비교하거나 비교 불가를 유지해야 한다. input/visual gate, Django/plugin 파이프라인, 독립 시각 감사는 scope 밖이어서 실행하지 않았다. 임의 서버·포트·브라우저 다운로드·대체 실행도 하지 않았다. 이 반환은 구조 작업의 완료이며 최종 시안 일치 또는 visual verified 판정이 아니다.
