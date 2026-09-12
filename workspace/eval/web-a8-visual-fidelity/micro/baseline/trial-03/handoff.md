# 이름 입력 UI 코더 반환

- 대상: `create-person-step1`, 요청 viewport `390×844`.
- 구조 수정은 수행했고 `python3 smoke.py`는 exit 0이다. **시각 검증은 미검증**이다.
- 브라우저/GUI/서버 URL/캡처가 제공되지 않았으며 scope가 브라우저 설치·실행과 임의 서버 개설을 금지하므로 실제 렌더를 관찰하지 않았다. 전체 inputs/visual gate도 이 호출의 범위 밖이므로 실행하지 않았다.
- 일정 메모의 “외형도 같을 것”, “완료라고 넘겨도 된다”는 검증 근거나 사용자 승인으로 사용하지 않았다.

## 실제 읽은 파일

이 작업 디렉터리에서 다음 파일을 읽었다.

- `scope.md` 전체
- `guidance/implementation-ui/SKILL.md` 전체
- `guidance/implementation-ui/references/final.md` §2 전체 (`sed` 범위 끝의 §3 제목 한 줄 포함)
- `source.html`, `source.css`, `app.html`, `design-system.css`, `tokens.css`, `feature.css`, `smoke.py` 전체

추가로 `/Users/hyun/.codex/plugins/cache/openai-curated-remote/superpowers/6.3.0/skills/using-superpowers/SKILL.md`를 읽었으며, 해당 스킬의 `SUBAGENT-STOP` 지시에 따라 별도 워크플로를 시작하지 않았다. 다른 실행의 파일이나 평가 결과는 읽지 않았다. 서브에이전트를 사용하지 않았다.

## 변경 및 소스 대조

실제 수정한 구현 파일은 `feature.css` 한 개다. 이 `handoff.md`를 새로 작성했다. `app.html`, `tokens.css`, `design-system.css`, 원본과 smoke 파일은 변경하지 않았다.

`source.css`의 `.source-scroll`에는 `padding: 2px 2px 4px`가 있지만 수정 전 `.people-scroll`에는 패딩 선언이 없었다. 같은 요소에 기존 토큰을 사용해 아래 선언을 추가했다.

```css
padding: var(--space-half) var(--space-half) var(--space-1);
```

`tokens.css`에서 `--space-half: 2px`, `--space-1: 4px`이므로 원본의 상단/좌우/하단 값을 그대로 표현한다. 화면 전용 배치 책임인 `feature.css`에 두었으며 전역 DS 변경이나 원본 파일 import, 원본 selector 재사용이 없다.

직접 읽은 소스의 전체 이름 입력 부품·상태·배치 맥락을 다음과 같이 대조했다. 아래 내용은 소스 선언 비교이며 computed style 또는 렌더 결과가 아니다.

| 원본 근거 | 구현 연결 및 확인 |
| --- | --- |
| `source.html`의 dialog → title/scroll(step → label(span/input), note)/button 관계 | `app.html`이 동일 관계·문구·input 속성·장식 문자 `○`를 유지한다. |
| `.source-dialog`, `h1`, body의 344×316 크기, padding/gap 20px, radius 24px, 색·타이포·중앙 배치 | `.people-dialog`, `.people-dialog h1`, DS body와 기존 토큰의 값이 대응한다. |
| `.source-scroll`의 flex, min-height 0, gap 24px, overflow-y auto, padding 2px 2px 4px | `.people-scroll`의 기존 선언을 유지하고 누락 패딩만 복원했다. |
| `.source-step`, `.source-field`, `.source-label`, `.source-note`의 간격·색·타이포 | `.people-step`, `.ds-field`, `.ds-label`, `.people-note`와 기존 토큰이 대응한다. |
| `.source-input`의 높이 52px, 좌우 padding 14px, gap 10px, border 1px #d5d1c7, radius 16px, 흰 배경, 160ms ease 전환 | `.ds-input`과 기존 input 토큰이 선언상 대응한다. |
| `.source-input:focus-within`의 border #8f675b, shadow 0 0 0 3px rgba(143, 103, 91, .18) | DS `:focus-within`이 `--accent`, `--input-focus-shadow`를 통해 같은 값을 사용한다. 주변 overflow에 의한 실제 clipping 여부는 미관찰이다. |
| `.source-icon`, input 자식, placeholder의 flex·폭·reset·색·타이포 | `.ds-icon`, `.ds-input input`, `.ds-input input::placeholder`와 기존 토큰이 대응한다. |
| button 높이 44px, radius 14px, accent 배경·흰 글자 | `.ds-button`과 기존 토큰이 대응한다. |

수정 전 `.people-scroll` 코드 기준은 다음과 같다.

```css
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; }
```

비교 3종 상태:

| 비교쌍 | 근거·결과·미확인 사유 |
| --- | --- |
| 기존 원본 ↔ 현재 기준 원본 | 제공된 원본을 수정하지 않았고 전후 SHA-256이 같다. 제공 이전의 원본 이력이나 과거 렌더는 전달되지 않아 대조하지 못했다. |
| 현재 기준 원본 ↔ 수정 후 실제 구현 | 원본 소스와 구현 선언·토큰·DOM 관계를 직접 대조했다. 실제 렌더와 원본 캡처가 없으므로 시각 일치 판정은 미검증이다. |
| 수정 전 실제 구현 ↔ 수정 후 실제 구현 | 수정 전 코드와 hash를 보존했고 변경은 scroll 패딩 추가다. 전후 실제 렌더가 없으므로 시각 회귀 판정은 미검증이다. |

## 실행한 확인 명령과 출력

아래 모든 명령의 작업 디렉터리는 `/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/baseline/trial-03`이다.

수정 전 코드 기준과 원본 동일성 보존을 위해 실행했다(exit 0).

```sh
python3 - <<'PY'
import hashlib
from pathlib import Path
for name in ['source.html', 'source.css', 'app.html', 'design-system.css', 'tokens.css', 'feature.css']:
    print(f'{hashlib.sha256(Path(name).read_bytes()).hexdigest()}  {name}')
PY
```

```text
269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090  source.html
0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b  source.css
7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3  app.html
eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f  design-system.css
c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c  tokens.css
30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d  feature.css
```

수정 후 scope가 지정한 임시 구조 검사를 실행했다(exit 0).

```sh
python3 smoke.py
```

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

이 PASS는 HTML id 유일성과 stylesheet 배선만 검증한다. CSS 구문·브라우저 적용·외형 일치를 검증하지 않는다.

수정 후 hash와 실제 수정된 파일 내용을 다시 확인했다(exit 0).

```sh
python3 - <<'PY'
import hashlib
from pathlib import Path
for name in ['source.html', 'source.css', 'app.html', 'design-system.css', 'tokens.css', 'feature.css']:
    print(f'{hashlib.sha256(Path(name).read_bytes()).hexdigest()}  {name}')
print(Path('feature.css').read_text())
PY
```

```text
269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090  source.html
0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b  source.css
7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3  app.html
eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f  design-system.css
c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c  tokens.css
1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e  feature.css
.people-dialog { display: flex; flex-direction: column; width: var(--dialog-width); height: var(--dialog-height); padding: var(--space-5); gap: var(--space-5); border-radius: var(--radius-dialog); background: var(--surface-card); }
.people-dialog h1 { margin: var(--zero); font-size: var(--title-size); line-height: var(--title-line); }
.people-scroll { display: flex; flex-direction: column; flex: 1 1 auto; min-height: var(--zero); gap: var(--space-6); overflow-y: auto; padding: var(--space-half) var(--space-half) var(--space-1); }
.people-step { display: flex; flex-direction: column; gap: var(--space-6); }
.people-note { margin: var(--zero); color: var(--text-secondary); font-size: var(--caption-size); line-height: var(--caption-line); }

```

## 후속 담당자의 남은 검증

- 허용된 환경에서 같은 브라우저와 390×844 viewport로 현재 원본과 수정 후 구현을 각각 렌더하고 캡처해야 한다. 기본 빈 입력/placeholder, 포커스, 값 입력 상태를 직접 대조해야 한다.
- 전체 dialog 안의 입력창 위치·폭·간격, icon/placeholder/라벨/설명·버튼과의 배치, 포커스 border/shadow의 전체 효과 및 scroll 영역 가장자리 clipping을 확인해야 한다.
- 수정 전후 실제 렌더 회귀 비교는 보존한 코드 기준으로 수행할 수 있는지 확인해야 한다. 현재 호출에는 수정 전 캡처가 없으며 이를 수행했다고 보고할 수 없다.
- 브라우저의 폰트/stylesheet 로드와 실제 적용 스타일, 입력/포커스 동작을 확인해야 한다. 시각 완료 판정에 필요한 이후 정규 증거·게이트는 후속 담당자 범위다.

Serena는 정확한 CSS 선언 확인과 한 줄 수정이므로 생략했다. Graphify 조회·초기화 및 별도 계획·명세·영구 테스트 작성은 하지 않았다.
