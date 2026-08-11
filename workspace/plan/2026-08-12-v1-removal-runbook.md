# ㉡ V1 걷기 런북 — 이중 수용·legacy 슬라이스 제거 (8번 이관 마지막 조각)

**2026-08-12 작성 · 상태: ✅ 실행 완료(2026-08-12).**

## 실행 기록 (2026-08-12)

- **게이트 해제 근거 = 사용자 결정**: 「상관없어. 플러그인을 수정한 다음에 broccoli-server
  리빌드 할거야」 — §0 게이트의 목적(옛 모양 저장소의 fail-open 방지)이 «옛 모양을 계속
  지원할 필요»에 걸려 있었는데, 유일한 알려진 대상 broccoli-server 가 **새 트리로 리빌드**
  되기로 확정되어 그 필요 자체가 소멸했다. 잔존 72건은 리빌드 대상이지 지원 대상이 아니다.
- §2 순서대로 실행: standard_tree(LEGACY_ALIASES 제거·`tree_mirror_check --write` byte-멱등)
  → 검사기 26파일 걷기 → checker_lint ㉢ 켬(위반 49건 실측 → 0) → 산문 → fixture 재실측
  (bad_legacy_flat exit 2 무변 — 문구 «미이관»→«#81·#488 트리 밖» 확인) → 미러(byte-copy
  29/29·corpus 11/11).
- **계획 대비 달라진 것 넷(정직 기록)**:
  1. API-error 3대·composition-root 의 옛 경로는 «삭제»가 아니라 **새 트리 경로로
     repoint** 했다(`presentation_layer/schema/error_out.py`→`driving_layer/api/bc_error_schema.py` ·
     `common/ninja/…`→`framework/ninja/…` · registrar→`driving_layer/api/api_router.py` ·
     composition_root 정본=폴더). 08-04 선행 계약의 «기계»(profile·selector·본문 검증)는
     리빌드 뒤에도 유효해야 하므로 기계는 남기고 주소만 옮겼다.
  2. `legacy` 식별자 중 V1 트리와 무관한 것(Pydantic v1 중첩 `class Config` 분석·openapi
     저장소 전수 스캔)은 삭제 대상이 아니라 **개명**했다(`nested_config_*`·`_scan_*`/`_repo_scan_*`).
  3. ㉢ 구현 = 낱말 검사(`legacy`·`이중 수용`·`미이관`·LEGACY 상수·`brownfield`(preserve-established
     문맥 밖)) + 옛 층 이름 리터럴의 «검출 자리» 허용(±3줄 창에 #규칙 인용 — #146·#324 류).
  4. `migration_gate.py` 는 폐기하지 않고 **리빌드 실측기**로 재규정(옛 이름 목록은 역사적
     고정본으로 내장 — standard_tree 의존 제거).
  5. `api_error_backstop_matrix.py`(08-04 실행형 명세 675케이스)가 HEAD 기준 674/674 였는데
     작업 트리 기준으로는 낡아 있었다 — V1 주소·`<Bc>ErrorOut` 어휘 repoint + Phase 3 에서
     이동한 소유권(ctx 의 selector/root-API lane→전용 4종·«수용하되 무시»)과 소멸한
     grandfather lane 을 기대에 반영해 **675/675 로 재캘리브레이션**했다. 이 과정에서
     검사기 실결함 하나를 발견·수정: #636 이 `from enum import StrEnum as X` 별칭을
     못 풀어 오탐(check-error-centralization — strenum_names 별칭 해석 추가).
- 남은 바깥 일 하나: **broccoli-server 리빌드**(72건·BC 17+) — 완료 판정은
  `migration_gate.py` exit 0 + registry 27종 green.

---

이하는 실행 전 원문이다(역사 기록 — 게이트·인벤토리 수치는 실행 시점 것).

## 0. 게이트 (선행 조건 — 하나)

```bash
python3 workspace/tools/migration_gate.py <대상 저장소> [<대상 저장소> …]   # 전부 exit 0 이어야 실행
```

- 판정 = «대상 저장소들의 옛 이름 폴더 잔존 0» (#76 쌍조건의 왼쪽 항 — 오른쪽 항
  「검사기 옛 이름 리터럴 0」은 이 런북이 만든다).
- **2026-08-12 실측**: `broccoli-server` **잔존 72건**(`presentation_layer`·`infra_layer/acl`·
  `published_service`·루트 `common/` 등) → 게이트 닫힘. 지금 걷으면 이 저장소에서 채택
  신호가 죽어 검사가 «조용히 무동작»(fail-open 재생산 — 조각 ⓐ가 막은 바로 그것).
- 대상 저장소 «목록»은 사용자가 소유한다 — 실행 전 AskUserQuestion 으로 목록을 확정받는다
  (#592 방식 — 코디가 대신 판정하지 않는다).

## 1. 경계 — 걷는 것 / 안 걷는 것

| | 대상 |
|---|---|
| **걷는다** | `standard_tree.LEGACY_ALIASES` 와 그 소비 전부 · 검사기의 옛 층 이름 리터럴·legacy 갈래 · API-error 3대+composition-root 의 «옛 트리 모양 경로»(`presentation_layer/schema/error_out` 류) preserve/legacy 슬라이스와 조기 반환 · `final.md` §4 순수 개명 표(이관 종료 기록으로 대체) · naming 의 «제자리 옛 이름» 면제(#28 LEGACY) · eval·registry 설명문의 «옛 이름=미이관 빚» 문구 |
| **안 걷는다** | `preserve-established` **프로필 자체**(08-04 계약 — 소비자가 의존하는 wire 보존 lane 은 **영구**다. 근거는 «소비자 의존·되돌릴 수 없음»이지 «먼저 있었음»이 아니다 — S-R4). 걷는 대상은 «옛 트리 모양»이지 «wire 보존»이 아니다 |

## 2. 실행 순서 (#72 이행 순서 — 플러그인 셋을 «한 커밋에서 먼저», 코드는 다음)

1. **게이트 확인** — §0 명령 전 대상 exit 0 + 사용자 목록 확정.
2. **`standard_tree.py`** — `LEGACY_ALIASES` 제거 → `tree_mirror_check.py --write` 재생성(byte-멱등 확인).
3. **검사기 전수** — 아래 인벤토리 ⓐⓑⓒ의 legacy 갈래·리터럴 제거. 상수 절반 갈이 금지 —
   파일 단위로 걷고 인벤토리 명령을 재실행해 잔존 0 을 확인한다(Phase 2 의 «조용히 무동작» 교훈).
4. **집행 뒤집기** — `checker_lint` 의 ㉢ 슬라이스(#591㉢ — `legacy|brownfield|preserve` 조기 반환
   검출)를 «정직 기록 잔존»에서 «위반»으로 켠다. #73·#76 이행 조항이 그때부터 잔존 리터럴을
   위반으로 문다(preserve «프로필» 낱말은 ㉢ 검출식에서 profile 셀렉터 자리만 화이트리스트).
5. **산문** — `final.md` §4 개명 표를 «이관 종료(날짜) — 옛 이름은 더 알아보지 않는다» 한 줄로
   대체 · SKILL.md·registry 설명문·eval v5 의 «미이관 빚» 문구 정리(eval 은 기준 변경이 아니라
   문구 정리라 epoch 무관 — 애매하면 unfreeze 판정 먼저).
6. **fixture 재실측** — `skeleton/bad_legacy_flat` 은 이중 수용 제거 후에도 **exit 2 여야 한다**
   (옛 이름 폴더 = «미이관» 진단이 아니라 «트리 밖 칸» #490·#81 위반으로 문구가 바뀐다 —
   기대 exit 무변·문구 변화를 기록). `fixture_matrix.py` 57 전수 green.
7. **미러** — `corpus_mirror_sync --write` + scripts byte-copy(codex) + codex 코디네이터의
   «미이관» 문구 추종.
8. **검증 세트** — spec_lint·tree_mirror·corpus·checker_lint(㉢ 켠 채)·fixture_matrix·
   reverse_coverage 전부 green + `migration_gate` 재실행(오른쪽 항 0 이 됐는지는 checker_lint 가 판정).

## 3. 인벤토리 (2026-08-12 생성 — 실행 시 명령 재실행으로 재생성한다)

ⓐ **`LEGACY_ALIASES`/`LEGACY_LAYERS` 소비 26파일** —
`grep -ln "LEGACY_ALIASES\|LEGACY_LAYERS" dddjango/scripts/*.py workspace/tools/*.py`:
검사기 23종(api-error-controller·common-container·composition-root·context-isolation·db-table·
domain-model·error-centralization·event-publish·idempotency·layer-skeleton·mechanism-ownership·
missable-entrance·naming·ninja-boundary·openapi·port-adapter-pairing·public-surface·
response-bypass·synthetic-infra-exc·test-config·transaction-boundary·transient-overmapping·
usecase-dto) + `standard_tree.py` + `checker_lint.py` + `tree_mirror_check.py`.

ⓑ **옛 층 이름 리터럴 18파일** — `grep -rln "presentation_layer\|infra_layer" dddjango/scripts/*.py`
(V1 «옛 모양 경로» 슬라이스 포함 — api-error 3대·composition-root 의 preserve 기계가 몸통).

ⓒ **`preserve-established` 참조 16줄(scripts)** — `grep -rn "preserve-established" dddjango/scripts/*.py`
· 이 중 «프로필 셀렉터·계약» 자리는 **존치**(§1 경계), «옛 트리 모양» 조기 반환만 걷는다 —
실행 시 줄 단위로 갈라 표를 채운다.

ⓓ **산문** — `final.md` §4(개명 표·«알아보되 통과 안 시킴») · `commands/dddjango.md`(§4 참조
문구) · codex 코디네이터 동문 · eval v5 SH 행의 «옛 이름은 §4 미이관 빚» · agents 의 «미이관 빚
지목» 문구(discipline-reviewer ③).

## 4. 남는 회색 — 정직하게

- 게이트는 «아는 대상 저장소»만 잰다 — 플러그인을 쓰는 저장소 전체 목록은 저장소 밖 사실이라
  기계로 못 닫는다. 그래서 §0 이 사용자 확정을 요구한다.
- ㉢를 켠 뒤에는 옛 모양 저장소를 «다시» 지원할 수 없다(되돌리려면 이 런북의 역방향이 아니라
  git revert — 그래서 #72 가 «한 커밋»을 요구한다).
