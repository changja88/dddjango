---
날짜: 2026-08-11
대상: 저장소의 **`dddjango/`** — 여기가 정본이다. `codex-dddjango/` 와 `workspace/reference/` 는 미러이므로 직접 편집하지 않는다(`workspace/tools/corpus_mirror_sync.py --write` 가 전파한다).
근거: 정본 `docs/work_flow.html` sha `612f55e7ce52d5be`(트리 140행) · 명세 `workspace/design/2026-08-08-tree-revision-spec.md`(531규칙) · 술어 `workspace/design/2026-08-11-predicates.md`(140항목) · 결정 카드 57장 · 사용자 결정 T54~T57(2026-08-11)
상태: **계획 확정 — 6번(플러그인을 만든다)이 이 문서와 매핑표를 받는다**
선행 조각: ⓐ `2026-08-07-plugin-path-contract-and-fail-open-fix.md` · ⓑ `2026-08-09-migrations-hand-edit-ban.md` · ⓒ `2026-08-09-brownfield-refactor-obligation.md` — 각각 이 계획의 Phase 에 배정된다(§8).
---

# 5번 — 구현 계획: 명세 531규칙을 플러그인 자리 넷으로 나른다

## 0. 사용자 결정 셋 (2026-08-11)

1. **어디를 고칠지 = 누구 책임인지를 분명히 한다** → 단위는 «규칙 → 소유자» 매핑표다(T54).
2. **책임이 잘못 놓였거나 분산된 것도 이번에 찾아 고친다** → 완료 자에 «소유자 2+ 검출»이 들어간다(T55).
3. **플러그인 flow 는 건드리지 않는다** → 금지선은 §8. 예외는 하나뿐 — 조각 ⓒ ⑥⑦, 「리팩터링 먼저」의 실행 자리(T58 · 사용자 확정 2026-08-11 「중요한건 리팩터링 먼저가 실행이 되어야해」).

여기에 이 저장소가 이미 정한 것 둘을 더한다 — 실측은 «설계 입력»이 아니라 **«이관 목록»**으로만 쓴다(조각 ⓒ ⑤) · `workspace/eval/` v4 FROZEN 은 손대지 않는다(§4 정정 참조).

## 1. 자리 넷 — 무엇이 어디 사나

| 자리 | 파일 | 담는 것 | 안 담는 것 |
|---|---|---|---|
| **ⓐ 정본** | `skills/discipline-houserules/references/final.md` | 트리 140행 + 규칙 «값» 전부 | 절차·판정 코드 |
| **ⓑ 스킬** | `skills/*/SKILL.md` | «언제 어떻게 읽나»(트리거·결정 순서) | **값 0** — 불변식·목록·경로의 사본 금지 |
| **ⓒ 검사기** | `scripts/standard_tree.py` + `scripts/check-*.py` | 기계 판정(`path`·`ast`)과 `ast+` 의 «후보 술어» | 사람 물음 |
| **ⓓ 에이전트** | `agents/*.md` | 절차 + `human` 27건 + `ast+` 의 «사람이 답할 한 물음» | 값 사본 |

**등급 → 소유자 규칙** (매핑표의 자동 채움 규칙이자 완료 자의 근거):

```
path · ast   →  ⓒ 하나          (검사기 하나가 전담)
ast+         →  ⓒ 하나 + ⓓ 하나 (후보는 기계 · 마무리 물음은 사람 — 정의상 둘)
human        →  ⓓ 하나          (검사기 소유 금지 — 판정 = 최소 수단)
전 등급       →  ⓐ 에 값 · ⓑ 는 포인터만
```

## 2. 매핑표 — Phase 0 산출물

- **파일**: `workspace/plan/2026-08-11-rule-owner-map.md`
- **컬럼**: `# | 판정 | ⓒ 검사기 | ⓓ 에이전트 | 작업 | 비고` — `작업 ∈ {재작성, 치환, 무변, 신설}`
- **생성**: `spec_lint.py --emit-owner-map` 이 골격을 낸다. 명세의 `자리` 컬럼 중 **396건이 「트리 N행」을 이미 갖고 있어** 트리 행 → 검사기 후보로 기계 매핑되고, 나머지 **135건**(전역 제약·장 참조)은 사람이 확정한다. 확정 컬럼(ⓒ·ⓓ 최종값)은 사람 소유다.
- **완료 자 (T55 확정본)**:
  1. 소유자 없는 규칙 = **0**
  2. ⓒ와 ⓓ를 **둘 다** 가진 규칙 = **`ast+` 집합과 정확히 일치** (고정 수가 아니다 — Phase 0 린트가 #390·#603 을 `ast` 로 내려 지금은 55. «0» 을 자로 쓰면 ㉰ 의 등급 체계를 도로 무너뜨린다)
  3. 등급↔소유자 불일치 = **0** (§1 의 규칙 위반 행)
  4. **역방향**: 규칙이 하나도 닿지 않는 플러그인 파일은 사유가 목록으로 남는다 = 미설명 파일 **0** (예: `implementation-python` 2,673줄 — 책 코퍼스라 트리 무관, 치환만 대상)

## 3. Phase 0 — 도구가 먼저 선다

> 정합성 검사를 Phase 4 → 0 으로 당겼다. 매핑표가 명세를 «읽어서» 만들어지므로, 명세를 지키는 도구가 그보다 먼저 서야 한다. `#361`·`#34` 가 이번에 «손으로» 걸린 것이 근거다 — 531규칙은 손으로 못 지킨다.

**신설: `workspace/tools/spec_lint.py`** — `corpus_mirror_sync.py` 와 같은 부류(메인테이너 도구 · fail-closed · exit 0/2/3). 검사 여덟:

```
① 중복        같은 문면 규칙 쌍 (㉯ 가 71건을 손으로 걷었다)
② 끊긴 참조    #N 참조 중 죽은 번호 — <span> 정정 이력 «안»은 제외
③ 트리 커버리지 140행 중 규칙 0건인 행 = 0
④ 카드 커버리지 카드 57장(1~59, 19·23 없음) 중 인용 0건 = 0
⑤ 죽은 문면    걷어낸 낱말·옛 칸 이름이 규칙 문면에 재등장
⑥ 술어 정합    predicates.md 가 참조하는 규칙 번호 생존 + ast+ 행의 «셋»(확정·후보·물음) 완비
⑦ 등급 정합    판정 값 ∈ {path,ast,ast+,human} · 명세가 «스스로 적은» 집계표와 재실측 대조
⑧ 소유자 정합  §2 완료 자 1~4 (rule-owner-map 을 함께 읽는다)
```

```python
# workspace/tools/spec_lint.py — 서명만 (본문은 6번)
def load_rules(spec_path: Path) -> list[Rule]: ...          # 7컬럼 계약 — 볼드 번호 방어 포함
def load_tree(plugin_tree_path: Path) -> list[TreeRow]: ...
def check_duplicates(rules) -> list[Finding]: ...            # ①
def check_dangling_refs(spec_text, rules) -> list[Finding]: ...  # ② span 제외
def check_tree_coverage(rules, tree) -> list[Finding]: ...   # ③
def check_card_coverage(spec_text) -> list[Finding]: ...     # ④
def check_dead_phrases(rules, banned: list[str]) -> list[Finding]: ...  # ⑤
def check_predicates(rules, predicates_path: Path) -> list[Finding]: ...  # ⑥
def check_grades(rules) -> list[Finding]: ...                # ⑦
def check_owner_map(rules, owner_map_path: Path) -> list[Finding]: ...   # ⑧
def emit_owner_map_skeleton(rules, tree, out: Path) -> None: ...  # --emit-owner-map
def main(argv: list[str]) -> int: ...                        # 0=clean · 2=위반 · 3=구조 전제 깨짐
```

**Phase 0 완료 자**: spec_lint ①~⑦ 전부 0 위반 · 매핑표 531행 확정(ⓒ·ⓓ 빈칸 0) · ⑧ 통과.

## 4. Phase 1 — 수직 슬라이스: 골격(제1원칙) 하나를 넷 끝까지

한 줄기를 자리 넷 전부에 통과시켜 **방법 자체를 시험한다**. 여기서 안 통하면 잃는 것이 ~1,000줄이고, Phase 3 에서 알면 37,000줄이다.

```
트리 140행 §0(골격)  →  ⓐ final.md 재작성  →  ⓑ SKILL.md 값 제거
                      →  ⓒ standard_tree.py + check-layer-skeleton.py 재작성
                      →  ⓓ coder.md 골격 의무 절
                      →  fixture 실측 (exit 0/2)
```

### 파일 일곱 (T57 — 목록 + 서명 · 본문 0)

**⑴ 신설 `dddjango/scripts/standard_tree.py`** — 트리의 기계 가독 사본. 검사기 19개가 import 하는 유일한 트리 데이터(물음 ② 의 답). `check-` 접두 없음(게이트가 아니라 데이터).

```python
SOURCE_SHA: str = "612f55e7ce52d5be"      # docs/work_flow.html 출처 고정
@dataclass(frozen=True)
class TreeRow:
    r: int                                 # data-r (파트 순서)
    depth: int
    path: str                              # 예: "driving_layer/api/<area>/"
    kind: Literal["fixed", "placeholder", "reappear"]   # 제1원칙 T52 의 세 유형
ROWS: tuple[TreeRow, ...]                  # 140행
LEGACY_ALIASES: dict[str, str]             # 옛→새 6쌍 (조각 ⓐ ⑴) — 이중 수용의 단일 출처
def fixed_paths() -> tuple[PurePosixPath, ...]: ...       # ①고정 — BC 마다 무조건 존재
def placeholder_subtrees() -> tuple[TreeRow, ...]: ...    # ②<> — 값이 생길 때 전개
def normalize_legacy(path: PurePosixPath) -> PurePosixPath: ...  # 이관 기간 별칭 정규화
```

**⑵ 신설 `workspace/tools/tree_mirror_check.py`** — 삼중 동기 검사(`corpus_mirror_sync` 와 같은 계약: `--check`/`--write` · fail-closed · exit 0/2/3).

```
docs/mkrev2.py:ROWS  ≡  dddjango/scripts/standard_tree.py:ROWS  ≡  final.md 트리 블록
(정본은 mkrev2.py 쪽 — --write 는 정본→플러그인 한 방향만)
```

```python
def extract_rows_from_mkrev2(path: Path) -> list[TreeRow]: ...   # AST 로 뽑는다 (#609 재료)
def extract_rows_from_plugin(path: Path) -> list[TreeRow]: ...
def extract_tree_block_from_final_md(path: Path) -> list[TreeRow]: ...
def main(argv: list[str]) -> int: ...
```

**⑶ 재작성 `skills/discipline-houserules/references/final.md`** — 4번 재료를 그대로 받는다: 트리 140행(코드펜스 블록 — ⑵ 가 검증) · §별 규칙 문면(매핑표의 ⓐ 값) · 카드의 «왜»를 §근거로. 구성: `§0 제1원칙 → §1 트리 140행 → §2 층·칸별 규칙 → §3 명명 → §4 이관(이중 수용·brownfield=빚)`.

**⑷ 부분 재작성 `skills/discipline-houserules/SKILL.md`** — §1.2 불변식 13개(값 사본) **삭제** → `final.md §N` 포인터로. §1.1(기존 규약 존중 판단 순서)·§4(타입)·§5(언어)·§6(의존성)은 절차라 **남는다**. 단 §4 는 T49/D58(「타입은 어떤 상황에서도」)로 문면 갱신 — 이것은 값이 아니라 규율이라 ⓑ 소유가 맞다.

**⑸ 재작성 `scripts/check-layer-skeleton.py`** — 판정을 `standard_tree` 로부터. 조각 ⓐ 반영: 채택 신호 2+ 유지(`:232` 패턴) · 이중 수용 · 대상 0건→exit 2 · fail-closed.

```python
def _is_adopted(bc_dir: Path) -> bool: ...        # 새·옛 층 폴더 «또는» Django 앱 마커 — 신호 둘
def _missing_fixed(bc_dir: Path) -> list[Finding]: ...      # ①고정 행 부재
def _flat_violations(bc_dir: Path) -> list[Finding]: ...    # 평면 답습(칸을 파일로 접음)
def _foreign_dirs(bc_dir: Path) -> list[Finding]: ...       # 트리에 없는 칸 (#486 반환)
def main(argv: list[str]) -> int: ...             # 0=clean · 1=사용오류 · 2=blocker (계약 무변)
```

**⑹ 갱신 `agents/coder.md`** — 골격 생성 의무 절(T56 ㉮): 「BC 를 새로 만들거나 touched 하면 `standard_tree` 의 고정 행을 빈 채로 실현한다 — 위반은 check-layer-skeleton 이 잡는다」. 값 사본은 `final.md §N` 포인터로.

**⑺ 신설 fixture** — `workspace/eval/fixtures/skeleton/{good_bc/, bad_missing/, bad_legacy_flat/}` — ⑸ 가 각각 exit 0 / 2 / 2 를 내는지 실측. **백스톱 실측 0 → 실측 N 의 첫 항목**(물음 ④). 이후 모든 검사기 작업의 완료 자에 「자기 위반 fixture 에서 exit 2」가 붙는다.

> **★ 정정 — eval v4 로는 채점하지 않는다.** 앞서 「7번에서 v4 를 그대로 쓴다」고 한 것은 절반만 맞다: v4 는 **옛 표준에 동결**돼 있어(SH-2 문면이 옛 층 이름) 새 트리 산출물을 찍으면 전부 FAIL 이 난다. 기준 변경은 명시적 unfreeze 또는 **새 epoch 승인**이 필요하다고 v4 자신이 적고 있다 → **새 epoch(v5) 는 7번 소유**로 넘기고, 5·6번의 실측은 위 fixture 결정 레인만 쓴다. v4 결과 14개는 불변.

**Phase 1 게이트**: 일곱이 끝나면 **사용자 검토** — 여기서 방법이 확정돼야 Phase 2 로 넓힌다(skill-creator 의 «작게 돌려 보고 고친다» 루프).

## 5. Phase 2 — 순수 개명 6쌍: 스크립트가 친다

| 옛 | 새 |
|---|---|
| `presentation_layer/` | `driving_layer/` |
| `infra_layer/` | `driven_layer/` |
| `published_service/` | `open_host_service/` |
| `infra_layer/acl/` | `driven_layer/anticorruption_layer/` |
| `infra_layer/django_<app>/` | `driven_layer/django_<bounded_context>/` |
| 루트 `common/` | 루트 `framework/` |

- 대상: **산문 파일만**(스킬 final.md·SKILL.md·에이전트 md — 실행 결과 9파일 94건). **검사기 코드의 옛 이름은 Phase 2 에서 치환하지 않는다** — 상수만 절반 갈면 옛 저장소에서 «조용히 무동작»(fail-open 재생산)이 되므로, Phase 3 의 경로 계약(standard_tree 기반) 재작업과 «함께» 간다. LLM 이 손으로 치지 않는다 — 일회성 치환 스크립트(scratchpad)가 치고, diff 를 사람이 본다(`$CLAUDE_JOB_DIR/tmp/phase2-rename.diff`).
- **주의**: `published_service` 개명은 «폴더 이름»만 순수 개명이다 — OHS **내부 구조**(contract 3패키지 → 트리 22행 이하)는 규칙이 바뀐 것이라 Phase 3 매핑표 몫. **`common/` → `framework/` 도 자동 치환하지 않았다** — 승격 규칙(`common/enum` 등)과 얽힌 «내용» 문제라 Phase 3(후보 2파일 기록됨).
- **완료 자**: 옛 이름 등장 위치가 「`LEGACY_ALIASES`·`LEGACY_LAYERS`(코드) + 이관 조문(산문) + **Phase 3 대기 검사기 12종**」 허용 목록 안뿐 — 마지막 항목은 Phase 3 이 비운다.

## 6. Phase 3 — 나머지를 매핑표 순서로

매핑표의 `작업` 컬럼이 곧 작업 목록이다. 큰 덩어리 넷:

1. **검사기 18개** — 조각 ⓐ 전면 적용(경로 계약 · 채택 신호 2+ · 대상 0건→exit 2 · fail-open 차단 — `.git` 부재 전면 면제 같은 것) + 내용 치환. 각각 완료 자: 자기 위반 fixture 에서 exit 2.
2. **신설 검사기** — 매핑표의 `신설` 행이 정한다(예: broker 계약 · webhook 발신자 스펙 · `#629` 집합 차 후보 · 타입 전면(§4 검사기의 `FunctionDef→continue` 결함 — T49 실측) 등). **registry 에 항목 추가는 «내용»이고 실행·종료 계약 변경은 «flow»다** — 전자만 한다.
3. **에이전트 4** (`design-architect`·`discipline-reviewer`·`design-review-ddd`·`coder`) — 값 사본 → `final.md §N` 포인터. `human` 27건과 `ast+` 57건의 «사람 물음»을 ⓓ 로 배치. 절차 문면은 무변.
4. **조각 ⓑ·ⓒ 배정** — ⓑ(migrations 손수정 금지)는 매핑표가 소유자를 정한다(문면=ⓐ · 감수=ⓓ). ⓒ(brownfield=빚)의 ④⑤(낱말·「백스톱 위반=리팩터링 대상」)도 매핑표로.
5. **조각 ⓒ ⑥⑦ — 유일한 flow 예외 (T58 확정 2026-08-11)** — 「리팩터링 먼저」가 실행되는 자리. **검사기 재작업(위 1·2)이 끝난 «뒤»에 넣는다** — 검사기가 먼저 물어야 G0 에 올릴 빚이 잡힌다(지금은 위반이 «보이지도» 않는다 — 조각 ⓒ 실측: `api.py` 731줄에 0건). `commands/dddjango.md` 수정 세 곳:
   - **Phase 0 에 한 단계** — 대상 BC 범위로 백스톱을 실행해 위반 목록(=빚)을 얻고 G0 배너에 「이 BC 의 빚 N건」으로 올린다. AskUserQuestion 으로 「지금 갚기 / 미루기」를 묻되 **③(가만 있어도 해로운 위반)은 미루기 선택지가 없다**. 미루면 `.dddjango/<기능폴더>/refactor-scope.md` 에 기록한다(조각 ⓒ ⑦).
   - **Phase 2 슬라이스 도출에 한 줄** — 「지금 갚기」로 정한 빚은 **리팩터링 슬라이스**로 만들어 신규 개발 슬라이스보다 **앞에** 둔다. 동작 보존 — 리팩터링과 기능 변경을 한 슬라이스에 섞지 않는다(조각 ⓒ ②).
   - **G2 직전 19종 실행은 그대로** — ⑥은 «한 번 더»지 «이동»이 아니다.

## 7. Phase 4 — 역방향과 전체 완료 자

1. 역방향 커버리지: 플러그인 전 파일 → 닿는 규칙 목록. 미설명 파일 0 (§2 완료 자 4).
2. `spec_lint.py` ①~⑧ + `tree_mirror_check` + `corpus_mirror_sync` 전부 green.
3. 검사기 전수: 위반 fixture 실측표(19+신설 × exit 2 확인) — 「백스톱 실측 0」의 종결.
4. 미러 전파: `corpus_mirror_sync --write` (codex · workspace/reference) + scripts byte-copy.

## 8. flow 금지선 (사용자 결정 3)

| | 대상 |
|---|---|
| **무변** | `commands/dddjango.md` 의 Phase 0~3 구조 · G0/G1/G2 게이트 · 에이전트 호출 순서 · 19-registry **실행·종료 계약**(exit 0/1/2 의미 · 렌더 방식) · 12-slot 절차 |
| **내용(허용)** | registry «목록»에 신설 검사기 추가 · 각 자리의 문면·값·경로 |
| **예외(T58 확정)** | 조각 ⓒ ⑥⑦ — G0 백스톱 재실행·빚 배너 + 미루기 AskUserQuestion·`.dddjango/` 기록 + 리팩터링 슬라이스 선행. 「리팩터링 먼저」가 실행될 유일한 자리라 사용자가 재확인했다(2026-08-11). 상세 §6-5 |

## 9. 다섯 물음의 답

| 물음 | 답 | 자리 |
|---|---|---|
| ① 누가 파일을 만드나 | `coder` 가 규칙대로(T56 ㉮ · flow 무변) — 위반은 check-layer-skeleton | Phase 1 ⑹ |
| ② 트리를 어디 두나 | `scripts/standard_tree.py` — 검사기가 import · `tree_mirror_check` 가 정본과 삼중 동기 | Phase 1 ⑴⑵ |
| ③ 대상 0건의 낟알 | **검사기 단위**(조각 ⓐ ⓑ안) — 채택 신호 있는데 그 검사기의 대상 0건이면 exit 2 | Phase 1 ⑸ → Phase 3 |
| ④ 백스톱 실측 0 | fail-open 차단 + 검사기마다 «위반 fixture 에서 exit 2» 완료 자 | Phase 1 ⑺ → Phase 4-3 |
| ⑤ 정합성 검사 | `spec_lint.py` ①~⑧ — Phase 0 으로 당김 | Phase 0 |
