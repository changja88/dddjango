---
날짜: 2026-08-07
대상: 저장소의 **`dddjango/`** — 여기가 정본이다. `references/final.md` 는 `workspace/tools/corpus_mirror_sync.py --write` 가 `workspace/reference/` 와 `codex-dddjango/` 로 전파하고, `scripts/` 는 코덱스 자리에 byte-exact 복사한다. **미러를 직접 편집하지 않는다.**
근거: 수정안 트리 102행 (`docs/work_flow.html` sha `d7f917ab939e92b8`) · 2차 적대적 리뷰 S3·S4
상태: **명세 확정 · 코드 미적용** — 명세는 **4번 ⓐ** 로 편입, 적용은 **6번(플러그인을 만든다)**
번호: 이 문서가 «9번»이라 부르는 단계는 **정본 3장의 6번(플러그인을 만든다)** 이다(계획이 0~8로 다시 매겨졌다). 아래 본문의 「9번」을 전부 그렇게 읽는다.
편입: 이 문서는 **4번이 만들 명세**(`workspace/design/<날짜>-tree-revision-spec.md`)의 ⓐ 로 **그대로 편입**된다 — 지금 존재하는 유일한 선행 조각이다.
---

# 명세 조각 ① — 경로 계약 개명과 fail-open 차단

## 0. 무엇을 정했나

**결정 (2026-08-07 · 사용자):** 갈래 **ⓑ + 이중 수용**.

- **ⓑ** — 「저장소가 표준 레이아웃을 채택했다는 신호는 있는데 검사 대상이 0건」이면 **`exit 2`**.
- **이중 수용** — 이관 기간에는 **옛 이름과 새 이름을 둘 다** 받는다.

**둘은 짝이어야 한다.** 이행 순서가 «플러그인 먼저 → 코드 나중»(D32)이라, 9번 직후에는 16개 BC가 전부 옛 이름이다. 이중 수용 없이 ⓑ만 넣으면 그 구간에 매번 `exit 2`가 나서 **이관 자체가 막힌다.**

**왜 ⓑ가 새 발명이 아닌가** — `check-layer-skeleton.py:232`가 「이 BC가 표준을 따라야 하나」를 판정할 때 이미 신호를 **둘** 쓴다.

```python
return _has_any_layer(bc_dir) or _has_django_app_marker(bc_dir)
#      층 폴더가 있나           Django 앱 산출물이 있나  ← 층 이름이 바뀌어도 안 죽는다
```

문제의 6종은 신호가 **하나(층 경로 문자열)뿐**이라 개명에 통째로 죽는다. ⓑ는 **한 군데서 이미 하고 있는 것을 나머지에 맞추는 일**이다.

## 1. 경로 대응표

### ⑴ 순수 개명 — 이중 수용 대상

| 옛(플러그인) | 새(트리) | 트리 행 |
|---|---|---|
| `presentation_layer/` | `driving_layer/` | 3 |
| `infra_layer/` | `driven_layer/` | 59 |
| `published_service/` | `open_host_service/` | 12 |
| `infra_layer/acl/` | `driven_layer/anticorruption_layer/` | 75 |
| `infra_layer/django_<app>/` | `driven_layer/django_<bounded_context>/` | 60 |
| 루트 `common/` | 루트 `framework/` | 88 |

이 여섯은 **같은 것을 다르게 부르는 것**이라 「둘 다 받는다」가 성립한다.

### ⑵ 구조 변화 — 이중 수용이 «모양 둘을 다 인정»한다는 뜻

| 옛 | 새 | 비고 |
|---|---|---|
| `presentation_layer/schema/` (BC 레벨) | **없다** — `driving_layer/api/<feature>/schema/` | 트리 9행. BC 레벨 고정명 `schema/`는 트리에 존재 자체가 없다 → **필수 조건에서 삭제**(S4) |
| `presentation_layer/registrar.py` | `driving_layer/api/api_router.py` | 트리 5행 |
| `presentation_layer/schema/error_out.py` | `driving_layer/api/error_out.py` | 트리 6행 |
| `application_layer/<f>/{command,query}/` | `application_layer/<feature>/<use_case>/` | 트리 26~28행. D29가 command/query 축을 명시 기각 |
| `domain_layer/<agg>/repository/` **폴더** | `domain_layer/<agg>/<aggregate>_repository.py` **파일** | 트리 53행. 애그리거트당 하나라 폴더가 아니다(S4) |

여기서 이중 수용은 **「옛 모양도 새 모양도 위반이 아니다」**로 구현한다(둘 중 하나가 있으면 통과).

### ⑶ 이중 수용이 «불가능»한 것 — 즉시 반전해야 한다

| 옛 | 새 | 왜 둘 다 못 받나 |
|---|---|---|
| `check-layer-skeleton.py:106` `FOREIGN_PORT_LAYERS = ("application_layer","infra_layer")` | **삭제 또는 반전** | 옛 규칙은 「`application_layer/port/`는 위반」이고 트리는 「`application_layer/port/<capability>/`가 **정답**」(32~36행)이다. **같은 자리를 위반이자 정답이라고 동시에 말할 수 없다.** D32가 기록한 설계 역전이라 이중 수용 없이 바로 반전한다 |

## 2. 공유 헬퍼 — 6종에 같은 것을 넣는다

플러그인 스크립트 19종은 전부 **독립 실행 파일**이고 서로 import 하지 않는다(`import sys`·`from pathlib import Path`만 공통). 그래서 둘 중 하나다.

- **㉮ 공유 모듈** `scripts/_dddjango_layout.py` + 각 스크립트에 `sys.path.insert(0, str(Path(__file__).parent))` — **권고**. 어휘가 한 곳이라 다음 개편에 한 번만 고친다.
- ㉯ 6벌 복제 — 기존 독립 설계와 맞지만 어휘가 6곳으로 흩어진다. `jpatch`가 4벌로 갈라진 것과 같은 병이다.

```python
# scripts/_dddjango_layout.py
"""dddjango 표준 레이아웃 어휘 — 층 이름 개명에 죽지 않는 채택 판정.

V2 = 수정안 트리(102행) · V1 = 개명 전. 이관이 끝나면 V1 을 지운다.
"""
from __future__ import annotations
from pathlib import Path

DRIVING_LAYER = ("driving_layer", "presentation_layer")   # V2, V1
DRIVEN_LAYER = ("driven_layer", "infra_layer")
LAYER_DIRS = ("domain_layer", "application_layer") + DRIVEN_LAYER + DRIVING_LAYER

OHS_DIR = ("open_host_service", "published_service")      # V2, V1
ACL_DIR = ("anticorruption_layer", "acl")                 # V2, V1

DJANGO_APP_MARKERS = ("apps.py", "models.py", "views.py", "admin.py")
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", "build", "dist"}


def layout_adopted(root: Path) -> bool:
    """이 저장소가 표준 레이아웃을 채택했나 — «층 이름»에 기대지 않고 판정한다.

    층 폴더가 하나도 안 보여도 Django 앱 산출물이 있으면 채택으로 본다.
    그래서 층 이름을 또 바꿔도 이 판정은 안 죽는다.
    """
    for container in root.rglob("application"):
        if not container.is_dir() or set(container.parts) & SKIP_DIRS:
            continue
        for bc in container.iterdir():
            if not bc.is_dir() or bc.name in SKIP_DIRS:
                continue
            if any((bc / d).is_dir() for d in LAYER_DIRS):
                return True                                   # 신호 ①
            if any((bc / m).is_file() for m in DJANGO_APP_MARKERS):
                return True                                   # 신호 ②
            if (bc / "migrations").is_dir():
                return True                                   # 신호 ②
    return False
```

## 3. fail-open 가드 — 6종에 같은 다섯 줄

**놓는 자리가 중요하다.** 경로로 «대상 집합»을 만든 **직후**, touched 필터 **앞**이다.

> `commands/dddjango.md:93`이 「중간 커밋 후 재실행은 touched 공집합이라 검사가 비어 돈다」를 **의도된 성질**로 적어 놨다. 즉 «touched 가 비어서 0건»은 정상이고, 우리가 막을 것은 **«경로가 안 맞아서 0건»** 하나뿐이다. 가드를 touched 뒤에 두면 정상 커밋마다 blocker 가 난다.

```python
    targets = _find_<...>_files(root)          # ← 경로 게이트가 만든 집합
    if not targets:
        if layout_adopted(root):
            print(
                "[<check-name>] BLOCKER — 표준 레이아웃을 채택한 저장소인데 "
                "검사 대상이 0건이다. 스크립트의 경로 계약이 저장소 트리와 "
                "어긋났다는 뜻이고, 이 상태에서 exit 0 은 «깨끗하다»가 아니라 "
                "«검사가 꺼졌다»이다. 경로 계약을 트리에 맞춰라.",
                file=sys.stderr,
            )
            return 2
        return 0    # 표준 레이아웃 미적용 → 해당 없음(§1.1 존중 · 기존 동작)
    # ↓ 여기서부터 touched 필터 — 여기서 0건이 되는 것은 «정상»이다
```

**brownfield 저장소는 안 깨진다** — `layout_adopted()`가 거짓이면 예전과 똑같이 `exit 0`이다.

## 4. 파일별 패치 — 스크립트 10종

경로 리터럴을 코드(주석 제외)에 가진 것은 **10종**이다. 그중 **fail-open 확정 6종**에 §3 가드를 넣는다.

| 파일:줄 | 지금 | 고칠 것 | §3 가드 |
|---|---|---|---|
| `check-response-schema-bypass.py:66` | `if "presentation_layer" not in parts` | `DRIVING_LAYER` 이중 수용 | **넣는다** (151→0) |
| `check-openapi-error-declaration.py:56` | 같음 | 같음 | **넣는다** (151→0) |
| `check-synthetic-infra-exc.py:48` | `INFRA_DIR_NAME = "infra_layer"` | `DRIVEN_LAYER` 이중 수용 | **넣는다** (420→0) |
| `check-db-table.py:59` | `if p.parent.name != "infra_layer"` | 같음 + 폴더명 `django_<bc>` | **넣는다** (16→0) |
| `check-ninja-boundary-middleware.py:47` | 정규식 `\.presentation_layer\.` | `(?:driving_layer\|presentation_layer)` | **넣는다** (정규식 붕괴) |
| `check-usecase-dto-placement.py:127-129` | 부모 `command`/`query` + `*_command.py`/`*_query.py` | **축 교체** — `application_layer/<feature>/<use_case>/` | **넣는다** (127→0 · 개명과 무관하게 이미 죽어 있다) |
| `check-layer-skeleton.py:80` | `LAYER_DIRS` 4개 | 이중 수용 6개 | 불필요 — 신호가 이미 둘 |
| `check-layer-skeleton.py:90-92` | `("presentation_layer","api")`·`("presentation_layer","schema")`·`("infra_layer","acl")` | `("driving_layer","api")` · **`schema` 삭제**(S4 — 트리에 BC 레벨 `schema/`가 없다) · `("driven_layer","anticorruption_layer")` | 〃 |
| `check-layer-skeleton.py:97` | `AGG_CORE_KIND_DIRS = (…,"repository")` | `repository`를 **폴더 요구에서 빼고**, `<aggregate>_repository.py` **파일** 검사로(S4 · 트리 53행) | 〃 |
| `check-layer-skeleton.py:106` | `FOREIGN_PORT_LAYERS` | **삭제 또는 반전** — §1⑶ | 〃 |
| `check-common-container.py:36` | `LAYER_DIRS` | 이중 수용 | 9번에서 재검 |
| `check-common-container.py:88` | 안내문 `presentation_layer/` | `driving_layer/` · `common`→`framework` (`common` 9회) | 〃 |
| `check-composition-root.py:56` | `LAYER_DIRS` | 이중 수용 | 〃 |
| `check-context-isolation.py:70` | `LAYER_DIR_NAMES = {…,"infra_layer"}` | 이중 수용 | 〃 |
| `check-context-isolation.py:120·122` | `"published_service"` | `OHS_DIR` 이중 수용 | 〃 |
| `check-context-isolation.py:129` | `parts[i]=="infra_layer" and parts[i+1]=="acl"` | `DRIVEN_LAYER` × `ACL_DIR` 이중 수용 | 〃 |

## 5. 문서 쪽 — 13개 파일

경로 어휘는 스크립트보다 **문서에 더 많다.** 개명이 안 닿으면 `coder`·`design-architect`가 옛 경로로 코드를 쓴다.

```
skills/discipline-houserules/references/final.md      33회 — §0~§4 전체
skills/discipline-houserules/SKILL.md                        체크리스트
skills/architecture-ddd/references/final.md
skills/implementation-django-ninja/references/final.md
skills/implementation-django/references/final.md
skills/implementation-test/references/final.md
skills/discipline-cleancode/{SKILL.md,references/final.md}
agents/{discipline-reviewer.md,design-architect.md,design-review-ddd.md,coder.md}
commands/dddjango.md                                  93행 — 19종 설명이 한 문단에 다 들어 있다
```

`agents/discipline-reviewer.md`는 개명 말고 **내용 셋**이 더 바뀐다 — 협력 포트 소유자 **반전**(D32) · OHS 계약 접미(D27) · 응용 연산 어휘(D29).

## 6. 이행 순서

1. **플러그인 먼저.** 이중 수용 상태로 릴리스한다 — 이 시점의 저장소는 전부 옛 이름이고, 이중 수용이라 `exit 2`가 안 난다.
2. **코드를 BC 하나씩** 옮긴다(D32 — 618건을 한 커밋에 하지 않는다). 반쯤 옮긴 BC는 두 이름이 섞이지만 이중 수용이 둘 다 받는다.
3. **16개 BC가 다 끝나면 V1(옛 이름)을 지운다.** 이때부터 §3 가드가 진짜 안전망이 된다 — 이후 누가 층 이름을 또 바꾸면 **즉시 `exit 2`**.

**3단계를 잊으면 이 작업의 절반이 사라진다** — 옛 이름이 남아 있는 한 「경로가 안 맞아서 0건」이 영원히 안 일어난다. 이관 완료 조건에 **「V1 상수 제거」**를 명시로 넣는다.

## 7. 미러와 릴리스

`dddjango/**`와 `codex-dddjango/**`가 **바이트 동일**이라 **모든 편집은 ×2**다. `make release`의 `corpus_mirror_sync.py --check`가 드리프트를 차단하므로, 한쪽만 고치면 릴리스가 막힌다.

## 8. 이 문서가 닫는 것

- **S3** — fail-open 6종. 원인·갈래·결정·패치 자리까지 확정.
- **S4** — `check-layer-skeleton.py:90-92`(BC 레벨 `schema/` 삭제)·`:97`(`repository` 폴더→파일). §4 표에 들어갔다.

**남은 것은 실행뿐이다.** 스크립트 10 + 문서 13, 전부 ×2(미러).
