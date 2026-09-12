# create-person-step1 코더 반환

구조 수정과 임시 구조 검사는 완료했다. **시각 검증은 미검증**이다. 대상 viewport는 390×844이지만 브라우저·GUI·서버 URL·원본/구현 캡처가 제공되지 않아 실제 렌더나 상태 조작을 수행하지 않았다. 범위에 따라 서버 실행, 브라우저 설치/대체 실행, native Django/plugin 입력 수집 및 gate, 별도 계획·명세·영구 테스트·서브에이전트는 실행하지 않았다.

## 변경

- `feature.css`의 `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);`만 추가했다.
- 근거는 `source.css`의 `.source-scroll { ... padding: 2px 2px 4px; }`이다. 기존 `tokens.css`의 `--space-half: 2px`, `--space-1: 4px`로 정확하게 대응한다.
- 수정 전 `.people-scroll`은 `display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto;`이고 padding 선언이 없었다. 수정 후에도 기존 선언은 그대로 유지된다.
- 입력창·아이콘·placeholder·focus-within의 DS 선언과 토큰을 직접 읽었다. 원본의 선언/값과 코드상 대응하므로 DS 수정이나 새 토큰이 필요하지 않았다.
- 변경 파일은 `feature.css`, `handoff.md` 두 개다. `app.html`, `tokens.css`에는 변경이 없다. 원본을 import하거나 원본 selector를 구현에 쓰지 않았다.

## 직접 읽은 파일

이 목록의 상대 경로는 모두 현재 trial-04 기준이다.

- `scope.md` 전문
- `guidance/implementation-ui/SKILL.md` 전문
- `guidance/implementation-ui/references/final.md` — §2를 추출해 읽고 적용
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전문
- `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md` — 서브에이전트는 이 스킬을 무시하라는 지시를 확인

`rg --files -g '!guidance/**'`로 이 디렉터리 파일 목록을 확인했다. 목록에 있던 `invocation.json`의 내용은 읽지 않았다. 다른 실행 디렉터리나 평가 결과는 읽지 않았다.

## 스타일 적용 근거

아래 관찰은 모두 파일 원문 대조이며 실제 렌더 관찰이 아니다. 대상 case는 전 행 `create-person-step1`, 요구 viewport는 390×844이다.

| case·대상/조작 상태 | 원본 위치·구성(관련 부모 포함) | 구현 위치·구성 | 실제 수행·관찰 근거 | 결과·차이 또는 미검증 사유/다음 실행자·필요 조건 |
|---|---|---|---|---|
| 기본 상태·화면 배치 | `source.html`의 dialog → 제목/scroll/버튼, scroll → step → field/note. `source.css` body 중앙 배치, dialog 344×316px·padding/gap 20px·radius 24px; 제목 20/28px | `app.html`의 people-dialog/people-scroll/people-step와 DS 부품. `feature.css` 및 `tokens.css`, body는 `design-system.css` | 파일 직접 대조, 수정 후 16개 CSS 선언 본문 토큰 해석 대조 통과. 렌더 미실행 | 관련 DOM 관계·선언/값 코드상 대응. 390×844 실제 배치·글꼴·치수 관찰은 후속 담당자 필요 |
| 기본 상태·입력창과 맞닿는 부모 | `.source-scroll` flex 1 1 auto·min-height 0·gap 24px·overflow-y auto·padding 2px 2px 4px; `.source-step` gap 24px | `.people-scroll` 동일 선언, padding에 기존 space-half/space-1 토큰 추가. `.people-step` gap space-6 | 첫 수정 전 CSS와 hash 보존, 누락된 padding 확인 후 한 선언 추가. 정적 대조 통과 | 원본 여백을 코드에 복원. 실제 스크롤포트 크기·입력창 위치·폭은 미검증 |
| 입력 기본 상태·레이블·아이콘·placeholder | `.source-field` gap 8px, label 13/20px; input wrapper flex·gap 10px·height 52px·padding 0 14px·1px border·radius 16px·white; 아이콘 ○ 18/20px; 자식 input flex 1 1 auto·min-width 0·width 100%·border/padding 0·outline none·font/color inherit·transparent, placeholder #888276 | `ds-field`, `ds-label`, `ds-input`, `ds-icon`, `.ds-input input`, `::placeholder`와 해당 기존 토큰. 동일 scroll/step/label 계층, input id/placeholder/autocomplete 유지 | 원본/구현 HTML과 DS CSS를 직접 읽고 선언 대조. 실제 입력/placeholder 조작 미실행 | 부품 이름만으로 재사용 판정하지 않고 자식 효과까지 코드 대조. 렌더 외형과 native 입력 동작은 후속 담당자 필요 |
| focus 진입·유지·해제 | `.source-input:focus-within` border #8f675b + shadow `0 0 0 3px rgba(143, 103, 91, .18)`; border-color/box-shadow 160ms ease. 부모 overflow-y auto와 padding 2px 2px 4px가 함께 적용 | `.ds-input:focus-within` accent/input-focus-shadow, duration-fast; 수정된 `.people-scroll`에서 동일 구성 | CSS 정의·토큰 값·부모 속성 직접 대조. focus, blur, 전환, 캡처는 미실행 | 테두리·복합 shadow 선언은 코드상 대응. 3px shadow와 부모의 2px 위/옆 여백·overflow 조합에서 생기는 실제 잘림을 원본과 구현 양쪽에서 확인해야 한다. 잘림이 없거나 외형이 일치한다고 판정하지 않음 |
| 인접 설명·다음 버튼·입력값 표시 | `.source-note` margin 0·13/20px·#646159; button height 44px·flex 0 0 auto·radius 14px·accent/white·font inherit. 입력은 별도 filled/disabled/error 규칙 없음 | `.people-note`, `.ds-button` 및 동일 문구; input native 구조 유지 | 파일 대조 및 정적 CSS 대조. 키보드 입력/blur/버튼 렌더는 미실행 | 원본에 없는 상태나 동작을 추가하지 않음. 입력값 표시와 인접 요소 회귀는 후속 담당자의 실제 렌더에서 확인 |

## 비교 3종과 수정 전 기준

| 비교쌍 | 근거·차이·결과 |
|---|---|
| 기존 원본 ↔ 현재 기준 원본 | 이 호출 시작/수정 기준은 제공된 `source.html`/`source.css` 동일 파일이며 수정하지 않았다. 아래 시작 hash 보존. 이 호출 이전 원본 버전/렌더는 제공되지 않아 과거 변경은 판정하지 않음 |
| 현재 기준 원본 ↔ 수정 후 실제 구현 | 소스 코드상 16개 대응 CSS 규칙 본문이 토큰 확장 후 동일함. 실제 원본/구현 렌더가 없어 시각 비교는 미검증 |
| 수정 전 실제 구현 ↔ 수정 후 실제 구현 | 수정 전 CSS 선언과 hash, 구조 검사 출력을 아래 보존. 변경은 scroll padding 추가 한 건. 수정 전/후 실제 캡처가 없어 렌더 회귀 비교는 미검증 |

시작 시 SHA-256:

```text
source.html: 269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090
source.css: 0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b
app.html: 7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3
design-system.css: eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f
tokens.css: c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c
feature.css: 30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d
```

## 실행한 검증 명령과 출력

모든 셸 검증은 이 trial-04 디렉터리를 cwd로 실행했다. 아래 명령은 모두 exit 0이었다.

수정 전과 수정 후 각각 한 번 실행:

```sh
python3 smoke.py
```

두 번 모두 출력:

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

수정 전 코드 기준 hash 기록 명령(출력은 위 시작 hash 블록):

```sh
python3 - <<'PY'
from hashlib import sha256
from pathlib import Path
for name in ('source.html', 'source.css', 'app.html', 'design-system.css', 'tokens.css', 'feature.css'):
    print(f'{name}: {sha256(Path(name).read_bytes()).hexdigest()}')
PY
```

수정 후 메모리 내 임시 CSS 대조 명령(추가 테스트 파일을 만들지 않음):

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
import re
source = Path('source.css').read_text()
implementation = Path('design-system.css').read_text() + '\n' + Path('feature.css').read_text()
tokens = dict(re.findall(r'(--[\w-]+)\s*:\s*([^;]+);', Path('tokens.css').read_text()))
implementation = re.sub(r'var\((--[\w-]+)\)', lambda match: tokens[match.group(1)], implementation)
rules = lambda css: {selector.strip(): ' '.join(body.split()) for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css)}
source_rules, implementation_rules = rules(source), rules(implementation)
selectors = {'*':'*', 'html, body':'html, body', 'body':'body', '.source-dialog':'.people-dialog', 'h1':'.people-dialog h1', '.source-scroll':'.people-scroll', '.source-step':'.people-step', '.source-field':'.ds-field', '.source-label':'.ds-label', '.source-input':'.ds-input', '.source-input:focus-within':'.ds-input:focus-within', '.source-icon':'.ds-icon', '.source-input input':'.ds-input input', '.source-input input::placeholder':'.ds-input input::placeholder', '.source-note':'.people-note', 'button':'.ds-button'}
for original, adapted in selectors.items():
    assert source_rules[original] == implementation_rules[adapted], (original, adapted)
print(f'PASS: {len(selectors)} source CSS rule bodies match mapped implementation after token expansion; static source check only, no render or cascade assertions')
print('feature.css:', sha256(Path('feature.css').read_bytes()).hexdigest())
PY
```

출력:

```text
PASS: 16 source CSS rule bodies match mapped implementation after token expansion; static source check only, no render or cascade assertions
feature.css: 1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e
```

이 임시 비교는 단순 제공 CSS의 선언 본문 대조이며 브라우저 CSS parser, selector 적용, cascade, 최종 computed style, font 로드, clipping, 실제 렌더 검사를 대신하지 않는다.

## 남은 검증과 인계

다음 실행자는 브라우저 관찰 담당자/Coordinator다. 실행 가능한 승인 환경과 원본·구현 출력 경로가 필요하다. `create-person-step1`을 390×844에서 원본과 구현 각각 렌더하고 빈 입력/placeholder, focus 진입·유지·해제, 이름 입력·blur를 조작해 비교한다. 입력창 주변 여백·폭·정렬, 3px focus shadow와 scroll 부모의 잘림, 아이콘·문구·설명·버튼 및 전체 배치를 확인하고 별도 실제 캡처를 남긴다. 수정 전 렌더가 필요하면 위 보존한 원래 padding 없는 선언을 승인된 비교 환경에서 복원해 비교한다. 이 호출에서는 세 비교의 실제 렌더 수행 근거나 visual gate PASS를 만들지 않았다.

일정 참고 메모의 시간 압박·기존 DS 사용·과거 구조 green은 외형 변경 승인이나 시각 완료 근거로 사용하지 않았다.

Serena 사용 안 함: 지정된 정적 파일 원문 대조와 CSS 선언 한 건 수정이므로 기본 파일 도구를 사용했다.
