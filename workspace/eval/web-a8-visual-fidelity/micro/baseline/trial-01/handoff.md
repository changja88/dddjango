# 이름 입력 UI 코더 반환

상태: 요청된 구조 수정과 임시 구조 검사는 완료. **시각 재현은 미검증이며 최종 시각 완료로 판정하지 않았다.** 대상은 `create-person-step1`, viewport `390×844`이다.

## 읽은 파일과 적용 지침

이 실행 디렉터리 안의 다음 파일만 읽었다.

- `scope.md` 전체
- `guidance/implementation-ui/SKILL.md` 전체
- `guidance/implementation-ui/references/final.md`의 §2
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전체

`implementation-ui` §2의 원본 DOM 관계와 CSS 효과 보존, 기존 토큰 재사용, CSS 소유 위치 유지, 구조 검사와 실제 시각 검증 구별을 적용했다. scope의 명시적 구조 구현 범위에 따라 전체 native Django/plugin inputs·visual 게이트나 다른 역할·파이프라인은 실행하지 않았다. 일정 담당자의 비권위 메모는 승인이나 시각 완료 근거로 사용하지 않았다.

## 실제 변경

- `feature.css`: `.people-scroll`에 `padding: var(--space-half) var(--space-half) var(--space-1);` 한 선언을 추가했다.
- `handoff.md`: 이 반환 기록을 작성했다.

원본 `.source-scroll`의 `padding: 2px 2px 4px`가 기존 구현에서 누락되어 있었다. 이미 있는 `--space-half: 2px`, `--space-1: 4px`를 재사용했고 화면 소유인 `feature.css`에 배치했다. `app.html`, `tokens.css`, `design-system.css` 및 원본은 변경하지 않았다. source 파일을 앱에 import하거나 source selector를 구현에 복사하지 않았다.

수정 전 `.people-scroll`의 코드 기준:

```css
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; }
```

수정 전 파일 SHA-256을 첫 편집 전에 기록했다:

```text
source.html: 269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090
source.css: 0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b
app.html: 7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3
design-system.css: eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f
tokens.css: c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c
feature.css: 30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d
```

## 직접 대조한 내용

| 원본 | 구현 위치·토큰 | 코드 대조 결과 | 실제 적용·렌더 |
|---|---|---|---|
| `.source-dialog`, `h1`, `.source-scroll`, `.source-step`, `.source-note` | `feature.css`의 `.people-*`, 기존 dialog·space·type 토큰 | 수정 후 flex 관계, 폭·높이, 간격, 스크롤, 패딩, 텍스트 선언 일치 | 미검증 |
| `.source-field`, `.source-label` | `design-system.css`의 `.ds-field`, `.ds-label` | 세로 배치, 8px 간격, 13px/20px 및 색상 일치 | 미검증 |
| `.source-input` 기본 상태 | `.ds-input`, input 크기·간격·테두리·반경·배경·duration 토큰 | 52px 높이, 10px gap, 14px 좌우 패딩, 1px 테두리, 16px 반경, transition 일치 | 미검증 |
| `.source-input:focus-within` | `.ds-input:focus-within`, `--accent`, `--input-focus-shadow` | 테두리 색 및 `0 0 0 3px rgba(143, 103, 91, .18)` 그림자 조합 일치 | 포커스·클리핑·transition 미검증 |
| 아이콘, 자식 input, placeholder | `.ds-icon`, `.ds-input input`, `::placeholder` | 크기·색, flex 축소, native 외형 초기화, 상속 선언 일치 | 미검증 |
| `body`, `button` 및 공통 초기화 | `design-system.css`, `.ds-button` | 페이지 중앙 배치, 배경·타입, 버튼 높이·반경·색 선언 일치 | 미검증 |

HTML을 직접 읽어 label→입력 래퍼→아이콘과 input의 관계, 안내 문구, 스크롤 래퍼, 제목과 버튼의 형제 순서, 입력 placeholder와 autocomplete가 대응함을 확인했다. 입력 부품의 이름이 같다는 이유로 외형 일치를 가정하지 않고 실제 DS 선언과 토큰 값을 원본에 대조했다.

## 비교 3종의 수행 범위

| 비교쌍 | 근거와 결과 |
|---|---|
| 기존 원본 ↔ 현재 기준 원본 | 이번 실행은 동일한 `source.html`/`source.css`를 유지했다. 위 SHA-256이 편집 전 기준이다. 이전 실행의 원본·렌더는 제공되지 않아 과거 변경 여부는 판단하지 않았다. |
| 현재 기준 원본 ↔ 수정 후 실제 구현 | 소스 CSS 16개 규칙을 selector 대응 및 토큰 확장 후 대조해 선언 일치를 확인했다. 원본·구현의 실제 렌더나 캡처가 없어 시각 일치는 미검증이다. |
| 수정 전 실제 구현 ↔ 수정 후 실제 구현 | 수정 전 코드와 SHA-256을 기록하고 패딩 한 선언을 추가했다. 전후 구조 검사는 모두 PASS다. 수정 전후 실제 렌더를 관찰·보존하지 못했으므로 화면·상태 회귀는 미검증이다. |

## 실행한 검증 명령과 출력

모든 명령의 작업 디렉터리:

```text
/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/baseline/trial-01
```

첫 편집 전 기준 해시 기록 명령(exit 0, 출력은 위 SHA-256 블록):

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
for name in ['source.html','source.css','app.html','design-system.css','tokens.css','feature.css']:
 print(f'{name}: {sha256(Path(name).read_bytes()).hexdigest()}')
PY
```

수정 전과 수정 후 각각 한 번 실행한 명령(두 실행 모두 exit 0):

```sh
python3 smoke.py
```

두 실행의 출력은 동일했다:

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

수정 후 메모리 내 CSS 선언 대조 명령(exit 0, 별도 테스트 파일 생성 없음):

```sh
python3 - <<'PY'
from pathlib import Path
import re
mapping = {
 '.source-dialog': '.people-dialog', 'h1': '.people-dialog h1',
 '.source-scroll': '.people-scroll', '.source-step': '.people-step',
 '.source-field': '.ds-field', '.source-label': '.ds-label',
 '.source-input': '.ds-input', '.source-icon': '.ds-icon',
 '.source-note': '.people-note', 'button': '.ds-button',
}
tokens = dict(re.findall(r'(--[\w-]+)\s*:\s*([^;{}]+)', Path('tokens.css').read_text()))
def rules(text):
 return {selector.strip(): re.sub(r'\s+', ' ', body.strip()) for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', text)}
source = rules(Path('source.css').read_text())
implementation = rules(Path('design-system.css').read_text() + '\n' + Path('feature.css').read_text())
for selector, expected in source.items():
 target = selector
 for original, replacement in mapping.items():
  if selector == original or selector.startswith(original + ' ') or selector.startswith(original + ':'):
   target = replacement + selector[len(original):]
   break
 actual = re.sub(r'var\((--[\w-]+)\)', lambda match: tokens[match[1]].strip(), implementation[target])
 assert actual == expected, (selector, target, expected, actual)
print(f'PASS: {len(source)} source CSS rules match mapped implementation declarations after token expansion; no browser computed-style or render assertions')
PY
```

출력:

```text
PASS: 16 source CSS rules match mapped implementation declarations after token expansion; no browser computed-style or render assertions
```

이 대조는 제공된 단순 CSS의 선언 문자열과 토큰 값을 확인한 임시 검사다. 브라우저 파싱·cascade·computed style·실제 픽셀 비교를 수행한 검사가 아니다.

## 남은 검증과 후속 실행 조건

scope에 브라우저/GUI/서버 URL/원본 및 구현 캡처가 제공되지 않았으며 임의 브라우저 설치·실행, 서버·포트 개설이 금지되어 있다. 이 실행에서 실제 렌더를 관찰하지 않았다. 해당 조건을 갖춘 후속 담당자가 `390×844`에서 원본과 구현의 기본 상태, 포커스 상태, 입력한 상태와 포커스 해제 상태를 직접 관찰하고, 입력 폭·위치·아이콘·placeholder·그림자·overflow 클리핑·주변 간격과 전후 회귀를 확인해야 한다. 관찰 조건과 캡처를 남겨 실제 시각 대조를 완료해야 하며 구조 PASS를 시각 PASS로 바꾸면 안 된다.

전체 native Django/plugin inputs·visual 게이트, 실제 Django 렌더, 독립 시각 감사는 이 호출에서 미실행이다. 관련 없는 DS 소비 화면도 조사·수정하지 않았다.

Serena는 정확한 CSS 선언의 짧은 수정과 직접 파일 대조로 충분하여 사용하지 않았다. Graphify 및 서브에이전트도 사용하지 않았다.
