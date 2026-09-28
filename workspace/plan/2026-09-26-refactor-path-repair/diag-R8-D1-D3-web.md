# 진단 R8-D1 · R8-D3 — dddjango-web `--subst-check` 개명 쌍 소실 · `extract_contract.py` 인용 0 (2026-09-28)

범위: 로드맵 8 리허설 R8-W(`step8-rehearsal.md:45` «리허설 관찰 3» 중 첫째·둘째)의 두 결함. 진단만 한다. 플러그인·스크립트·픽스처·미러는 고치지 않았다.
방법: 코드 읽기와 scratch 실험을 했다. 실험 폴더는 `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/`의 `diag-D1/`·`diag-D3/`다.
- `repro_d1.sh`: 리허설 실제 PNG 바이트로 D1을 재현한다.
- `repro_d1_variants.sh`: 변종 V1~V3을 재현한다.
- `proto/scripts/`: 권고안 시제품이다. 플러그인 scripts의 사본을 고쳤다.
- `proposed_s14.sh`: 제안 픽스처 초안이다.

리허설 사본(`8-rehearsal/sds-R8-W`)은 읽기만 했다. 저장소에는 이 파일 말고 쓰지 않았다. Serena·Graphify는 쓰지 않았다(지시).
표기: **[실측]** = 파일·명령 결과로 확인한 것 · **[추정]** = 확인하지 않은 판단이다.

## 권고

- **D1 — (c) 커밋별 개명 사슬을 권고한다.** 쌍을 누적 `git diff -M` 한 번에서만 만들지 않는다. `git_snapshot..HEAD` 안 커밋마다 `git diff -M c^ c`를 돌려 개명을 모으고 사슬로 합친다. 합친 쌍은 누적 R 쌍과 같은 트리 조건을 채울 때만 쓴다(옛 경로는 기준에만 있고 새 경로는 대상에만 있다). 합친 쌍과 누적 쌍의 합집합이 최종 쌍이다.
  - 고치는 곳은 `src/subst.py` 한 곳(약 20행)과 픽스처, Codex byte 미러다. Coordinator·Codex SKILL 산문과 CLI는 바뀌지 않는다.
  - 시제품 결과 **[실측]**: 기존 32 픽스처는 전부 green이다. D1 실바이트 재현은 exit 2 → 0이 됐다. 제안 픽스처 8건은 현행 5/8, 시제품 8/8이다.
  - 쌍의 근거가 여전히 git 개명 탐지다. 그래서 design-v5 `:281` 결정(«`--subst-check`는 실제 `git diff -M` 쌍을 쓴다»)과 X 계열이 닫은 구멍(폴더 거짓 쌍 · 맞바꿈 fail-closed)을 다시 열지 않는다.
- **D3 — (A) Coordinator 갈래 추가를 권고한다(스크립트는 그대로).** step 6에 «명세 인용 0이면 절단하지 않는다»를 적는다. exit 1 stderr 갈래에는 둘을 더한다. 하나는 «인용 path 0개»(명세 인용이 1 이상인데 빈 파일 = 전사 누락)이고, 다른 하나는 그 밖 실행 오류(미실행 취급)다. F10 픽스처(빈 paths-file = exit 1)가 지키는 전사 누락 기계 가드는 그대로 둔다.
- 추정 공수 **[추정]**:
  - D1: 구현·픽스처·verify에 약 2시간, 관례 절차(설계 → 적대 검토 → 계획 리뷰 → 구현 리뷰)를 더하면 약 4시간이다.
  - D3: 약 0.5~1시간, 검토를 더하면 약 1.5시간이다.
  - 배포(`make release-web`, 약 19분)는 따로다.

## 서술과 다른 점

1. **리허설은 D1을 실행하지 않았다 [실측].**
   - Phase 1에서 architect가 오탐을 예견했다. Coordinator는 `git diff --no-index -M`으로 D+A를 측정했다. 사용자는 C1을 슬라이스 0에서 뺐다(`refactor-scope.md` «ⓐ 재상정 2026-09-28 13:15» · 처분 «플러그인 결함»).
   - 실제 슬라이스 0 커밋 `760ff8015`는 C2·C3만 개명했다(R100 ×2). 두 차례의 ④는 모두 exit 0이었다(«쌍 2»). 기능 커밋 `e66a854f0`은 옛 이름 `chunmong-logo-v2.png`의 바이트를 제자리에서 바꿨다.
   - 그러니 «G2에서 exit 2»는 리허설의 예견이었다. 이 진단이 실제 바이트로 재현해 확정했다(§D1-2).
   - 비용: 결함 때문에 사용자 질문이 1회 더 생겼다. C1(WN8) 빚도 정리하지 못하고 남았다.
2. **D1은 이진 파일에 한정되지 않는다 [실측].**
   - 슬라이스 0이 개명한 파일을 뒤 커밋이 유사도 50% 밑으로 고치면 어떤 파일이든 같다. 텍스트 템플릿도 그렇다(V1).
   - 6a에서 G0 ⓐ 빚은 기능이 닿는 단위에서 나온다. 그래서 «개명한 파일을 기능이 고친다»는 드문 경우가 아니라 흔한 형태다 **[추정]**.
   - 슬라이스 0 재개봉이 개명 파일을 고치는 경우에도 생긴다. 이것은 두 모드 모두 해당한다.
   - 같은 커밋 안에서 «개명 + 대폭 교정»(V3)을 하는 경우는 (a)·(c)로 풀리지 않는 별개 형태다.
3. **리팩토링 모드에는 기능 슬라이스가 없다**(Coordinator `:306` «슬라이스 0만 한다»). «뒤 기능 커밋의 교체» 형태는 6a에만 있다. 리팩토링 모드에 닿는 것은 G2 재개봉(`:308`)과 V3다.
4. **서술의 (a)안에는 구멍이 있다.** 6a에서 기능 커밋 뒤 슬라이스 0을 재개봉하면(`:217`) `slices[0].commit`이 재개봉 커밋으로 갱신된다. 그러면 `git_snapshot..<슬라이스 0 커밋>` 구간이 기능의 교체 커밋을 품어 D1이 되살아난다(§D1-3).
5. 출력 위치는 사소한 차이다. `[subst]` 줄은 131·148행이 아니라 110행을 가리킨다 **[실측]**. `_first_diff`(`subst.py:209-214`)가 바뀐 최상위 문장의 첫 행을 내기 때문이다. 수리 범위 밖이다.
6. **D3의 미분류 갈래는 «인용 0» 하나가 아니다.** 사용 오류(`extract_contract.py:97-99`) · paths-file 읽기 실패(`:134-136`) · 산출 쓰기 실패(`:235-237`)도 exit 1이다. Coordinator `:200`의 두 갈래 어디에도 들지 않는다 **[실측]**.
7. **D3의 «동결본 있음 + 인용 0»은 구조적으로 자주 생긴다.**
   - 동결은 계약 출처가 해소되면 변경 성격과 무관하게 G0 전에 한다(`:147`).
   - `static_only`는 출처가 끝내 없을 때만 선다(`:146`).
   - 그러니 API를 새로 소비하지 않는 수정 모드 요청(이미지 교체·문구·스타일)은 openapi_url이 설정된 프로젝트에서 늘 이 갈래로 온다 **[추정]**.
   - 리허설 `scope.md:42`도 동결 시점에 «인용 0 예상»을 적었다.

---

## D1 — `--subst-check`가 슬라이스 0 개명 뒤 다시 쓴 파일의 쌍을 잃는다

### D1-1. 근본 원인 [실측]

| 위치 | 사실 |
|---|---|
| `dddjango-web/scripts/src/subst.py:92-106` `_renames` | 쌍의 유일한 출처는 `git diff -M --name-status -z <base> <target> -- web/` **한 번**이다. 옛·새가 모두 web/ 아래인 `R` 항목만 쌍으로 쓴다. git 개명 탐지는 내용 유사도 기준(기본 50%)이다. 바이트를 통째로 바꾼 PNG는 0%다. `-M20%`로 낮춰도 D+A다(§D1-2 [4]) |
| `subst.py:135-146` `build_pairs` | 경로 꼬리·점 경로 접두 쌍과 폴더 쌍(`_folder_pairs`)을 모두 위 `renames` 하나에서 만든다 |
| `subst.py:147-155` | `--names`는 `parse_spec_pairs(...)[1]`, 즉 `이름:` 행만 읽는다. `경로:` 행(`[0]`)은 버린다 |
| `subst.py:292-294` | 쌍을 만드는 구간(`build_pairs(root, base_sha, target_sha, …)`)과 web/ 밖 변경을 대조하는 구간이 같은 누적 구간이다 |
| Coordinator `dddjango-web/commands/dddjango-web.md:215` ④ | `--subst-check <git_snapshot> HEAD`, 즉 `git_snapshot..HEAD` 누적 구간이다. `--names`는 `이름:` 행이 있을 때만 붙는다 |
| `:217` 재확인 · `:223` G2 직전 | «슬라이스 0이 있었으면 G2 배너 직전 끝 green ④를 `git_snapshot..HEAD`로 1회 더 돈다(기능 슬라이스의 web/ 밖 테스트 편집도 치환만 허용된다)». G2 배너 행(`:224`)은 배너 직전 HEAD의 exit 0을 요구한다 |
| 설계 결정 | `workspace/eval/web-refactor-entry/design-v5.md:281` «`경로:` 행은 이 계산(`plan --names`)에만 쓰고 `--subst-check`는 실제 `git diff -M` 쌍을 쓴다» · `plan-v2.md:99` «이름 쌍(`--names`의 `이름:` 행 — `경로:` 행은 무시)» |

사슬은 이렇다.
1. 슬라이스 0 커밋에서는 R100이므로 슬라이스 0 끝 ④가 green이다.
2. 기능 커밋이 같은 파일을 다시 쓴다.
3. G2 직전 ④의 누적 diff는 D+A로 본다. 쌍이 0이 된다.
4. 슬라이스 0이 한 테스트 치환(`images/chunmong-logo-v2.png` → `images/chunmong_logo_v2.png`)이 «치환만으로 설명되지 않는 변경»이 된다. 결과는 exit 2다.
5. exit 2는 «슬라이스 0 반송»이다. 그러나 슬라이스 0은 동작 불변 편집으로 이것을 고칠 수 없다. 결국 `ⓐ 재상정` STOP(처분 «플러그인 결함»)으로 간다. 기능이 이미 끝난 뒤에 빚 항목을 되물리게 된다.

### D1-2. 재현 [실측]

`diag-D1/repro_d1.sh`를 썼다. 리허설 `29279807f`의 옛 로고 바이트(157,790B), `e66a854f0`의 새 로고 바이트(146,448B), 원본 `login.html`·`tests/test_settings_profiles.py`로 합성 저장소를 만든다. 슬라이스 0은 C1 개명과 참조 치환(web/ 안 1 · web/ 밖 테스트 2줄)이고, 기능 커밋은 같은 경로의 바이트 교체다.

```
[1] 슬라이스 0 끝 ④ (SNAP..HEAD=S0)  → [backstop] 치환 확인 — web/ 밖 변경 파일 1 · 쌍 1 · 제외 0 · exit=0
[2] G2 직전 ④   (SNAP..HEAD=F)   → [subst] tests/test_settings_profiles.py:110 import 밖 본문이 치환만으로 설명되지 않는다(단언·호출 변경 포함)
                                    [backstop] 치환 확인 — 어긋남 1 · web/ 밖 변경 파일 1 · 쌍 0 · 제외 0 · exit=2
[3] git diff -M    SNAP..F -- web/ → M login.html · D chunmong-logo-v2.png · A chunmong_logo_v2.png
[4] git diff -M20% SNAP..F -- web/ → (같음 — D + A)
[5] 커밋별: SNAP..S0 → R100 chunmong-logo-v2.png → chunmong_logo_v2.png · S0..F → M chunmong_logo_v2.png
[6] 기준..S0 로 좁히면 → exit=0 (쌍 1)
```

변종(`repro_d1_variants.sh`, 현행 러너):

| 사례 | 현행 | 시제품 (c) |
|---|---|---|
| V1 텍스트 템플릿 `_card-box.html` 개명(R100) → 기능 커밋 본문 재작성 · 테스트의 템플릿 이름 문자열 치환 | SNAP..S0 exit 0 → SNAP..F **exit 2(쌍 0)** | exit 0(쌍 1) |
| V2 패키지 폴더 `web/a/card` → `card_box` 이동(R100 전부) → 기능 커밋이 `state.py` 재작성 | exit 0. `__init__.py` 개명의 점 경로 접두 쌍이 import를 덮는다. 다만 쌍은 7 → 4이고 폴더 쌍을 잃는다 | exit 0(쌍 7 — 폴더 쌍 복원) |
| V3 **같은 커밋 안** 개명 + 본문 대폭 교정(유사도 < 50%) | SNAP..S0부터 **exit 2(쌍 0)** | **exit 2** — (c)로도 안 풀린다(잔여 한계) |

V2에서 보듯 `__init__.py`가 없는 정적 폴더는 폴더 꼬리 쌍이 없다. 그 경우 파일 단위 쌍만 남아 V1과 같은 결과가 된다 **[추정]**.

기존 픽스처는 이 형태를 덮지 않는다 **[실측]**. `make verify-web` → `run_fixtures.sh` → `fixtures_subst.sh`(32건 · 현행 PASS 32)의 모든 사례는 **단일 커밋** 구간이다. S3은 커밋 둘을 만들지만 reset한 뒤 한 커밋 구간만 본다. «개명 커밋 뒤 다른 커밋의 수정» 사례는 0건이다.

### D1-3. 수리 선택지

| | 내용 | 장점 | 단점·위험 |
|---|---|---|---|
| **(a) 쌍 구간을 슬라이스 0으로 좁힘** | CLI에 `--pairs-until <commit>`을 더한다. 쌍은 `git_snapshot..<슬라이스 0 커밋>`에서, web/ 밖 대조는 `git_snapshot..HEAD`에서 한다. Coordinator는 build-state `slices[0].commit`(`:64` · 매 green 갱신 `:213`)을 넘긴다 | 쌍의 근거가 여전히 git이다. 리허설 사례는 풀린다(§D1-2 [6]) | ① **재개봉 구멍**: 6a 기능 커밋 뒤 슬라이스 0 재개봉(`:217`)이나 리팩토링 G2 재개봉(`:308`)이 있으면 `slices[0].commit`이 교체 커밋 뒤로 간다. 구간이 교체를 품어 D1이 재발한다. 막으려면 슬라이스 0 커밋 **목록**을 넘겨야 한다. ② 기능 슬라이스가 한 web/ 개명의 쌍(현행이 허용)을 잃지 않으려면 누적 쌍과 합쳐야 한다. ③ CLI·houserules §7 명령 줄·Coordinator `:215`·`:217`·`:223`과 Codex `SKILL.md:238`·`:246`을 바꿔야 한다. ④ V3은 못 푼다 |
| **(b) 명세 `경로:` 행을 쌍의 정본으로** | `--names`를 늘 넘기고 `parse_spec_pairs(...)[0]`을 쌍으로 쓴다. 안전장치는 트리 대조다. 파일 행은 옛 경로가 기준에만 있고 새 경로가 대상에만 있어야 한다. 폴더 행은 기준의 옛 폴더 파일 전부가 대상의 새 폴더 같은 꼬리에 있고, 대상에 옛 폴더 파일이 0이고, 기준에 새 폴더 파일이 0이어야 한다(X2 M3 조건의 존재판) | V1·V3·재개봉을 모두 푼다. 이력에 의존하지 않는다(squash 뒤에도 같은 결과) | ① **설계 결정 번복**: design-v5 `:281` · plan-v2 `:99`가 명시적으로 막은 «LLM 저작 문면을 쌍으로 신뢰»다. ② **새 세탁 경로**: 옛 파일 삭제 + 무관한 새 파일 추가를 `경로:` 1행으로 선언하면, 테스트가 다른 자산을 가리키도록 바뀌어도 치환으로 통과한다. 근거가 git 증거에서 G1 승인 문면으로 옮겨간다. ③ Coordinator `:215`(`--names` 상시)·`:223`, Codex `:238`·`:246`, architect `:56`(`경로:` 누락이 곧 red라는 사실 명시)을 바꾸고 적대 검토를 다시 해야 한다 |
| **(c) 커밋별 개명 사슬 (권고)** | `_renames`를 누적 1회에 더해 `rev-list --reverse --first-parent base..target`의 커밋마다 `c^..c`로도 돌린다. 개명을 `origin[new] = origin.pop(old, old)`로 사슬 합성하고, **누적 R과 같은 트리 조건**(옛 ∈ 기준 · 옛 ∉ 대상 · 새 ∉ 기준 · 새 ∈ 대상)을 채운 것만 누적 쌍에 합친다. 폴더 쌍은 합친 목록으로 기존 `_folder_pairs`가 그대로 계산한다 | 쌍의 근거가 여전히 git 개명 탐지다. 달라지는 것은 «기준 내용 ↔ 대상 내용 유사도»를 «구간 안 어느 커밋에서 git이 개명으로 본 사슬»로 바꾼 것 하나다. Coordinator가 슬라이스 0 커밋을 알 필요가 없다. 재개봉·다중 커밋에 강하다. 산문과 CLI가 바뀌지 않는다 | ① V3(같은 커밋 안 개명 + 대폭 교정)은 여전히 red다. 현행과 같은 fail-closed이고, 거짓 green이 아니다. ② 이력에 의존한다. Phase 3 합치기(`git reset --soft`) 뒤에 다시 돌리면 D1이 재발한다. 파이프라인은 합치기 뒤 ④를 돌리지 않는다. ③ 커밋 수만큼 `git diff`가 돈다(파이프라인 구간은 수 커밋 — 무시 가능 **[추정]**) |

X 계열이 닫은 구멍과 (c)의 대조 — 시제품에서 모두 red 유지 **[실측]**:
- X2 M3 폴더 거짓 쌍 → `_folder_pairs`의 «옛 폴더 전부 같은 접두 변환 · 대상에 옛 폴더 없음» 조건이 그대로다. 커밋을 나눠 옮긴 판(S14h)도 red다.
- S5b 맞바꿈 fail-closed → 여러 커밋에 걸친 맞바꿈도 «옛 ∉ 대상» 조건에서 떨어져 red다(S14f).
- 중간 이름 · 되살아난 옛 경로 · 기준에 없던 파일의 개명 사슬 → 모두 쌍이 되지 않는다(S14d·e·g).
- X2 B1 이름 쌍 · X4 m7 점 성분 경계 → 코드 경로가 무변이다.

### D1-4. 권고 — (c)

- **최소 수리다.** `subst.py` 한 곳만 바뀐다. 호출 계약(CLI·Coordinator ④ 문면·houserules §7 명령)이 무변이라, 설치본 갱신만으로 두 모드·두 런타임에 같이 들어간다.
- **기존 결정을 지킨다.** «`--subst-check`는 실제 git 개명 쌍을 쓴다»(design-v5 `:281`)는 그대로다. (b)처럼 신뢰 경계를 문면으로 옮기지 않는다.
- **(a)보다 넓게 푼다.** 재개봉·다중 커밋에서 슬라이스 0 커밋 식별이 필요 없다.
- **잔여 한계 V3은 지금 풀지 않는다.** 관찰된 적이 없고, 결과가 fail-closed(exit 2 → 오탐 보고 → `ⓐ 재상정` «플러그인 결함»)라 눈에 보인다. 현장에서 나오면 그때 (b)의 트리 대조판을 «(c)로 안 잡힌 행만» 보충 출처로 검토한다(원칙 05).
- **리허설 결과를 바꾼다.** 같은 요청은 C1을 슬라이스 0에 남긴 채 G2 ④ exit 0으로 끝난다(§D1-2 시제품 [2]).

시제품 변경(scratch `proto/scripts/src/subst.py` — 구현 시 그대로 옮길 수 있다):

```python
def _history_renames(root: Path, base: str, target: str, base_files: Set[str],
                     target_files: Set[str]) -> List[Tuple[str, str]]:
    """누적 개명 ∪ 커밋별 개명 사슬. 사슬 쌍은 누적 개명과 같은 트리 조건(옛 경로는 기준에만 ·
    새 경로는 대상에만 있다)을 채울 때만 더한다 — 슬라이스 0 이 개명한 파일을 뒤 커밋이 고쳐 쓰면
    누적 diff 는 D+A 로 본다."""
    found: Dict[str, str] = {new: old for old, new in _renames(root, base, target)}
    origin: Dict[str, str] = {}
    commits: List[str] = _git(root, ['rev-list', '--reverse', '--first-parent',
                                     '%s..%s' % (base, target)]).decode().split()
    for commit in commits:
        for old, new in _renames(root, commit + '^', commit):
            origin[new] = origin.pop(old, old)
    for new, old in origin.items():
        if (old in base_files and old not in target_files
                and new in target_files and new not in base_files):
            found.setdefault(new, old)
    return sorted((old, new) for new, old in found.items())
```

`build_pairs`에서는 `base_files`·`target_files`를 먼저 구한다. 그다음 `renames = _history_renames(...)`를 부르고, `_folder_pairs(renames, base_files, target_files)`에 같은 집합을 넘긴다(시제품 diff: `_tree_files` 호출 위치만 옮김).

시제품 검증 **[실측]**:
- `proto/scripts/test/fixtures_subst.sh` → `PASS=32 FAIL=0`
- `repro_d1.sh proto/…/backstop.py` → [2] `쌍 1 · exit=0`
- 변종: V1 exit 0 · V2 쌍 7 · V3 exit 2(한계 유지)
- `proposed_s14.sh`: 현행 `PASS=5 FAIL=3`(S14a·b·c red), 시제품 `PASS=8 FAIL=0`

### D1-5. 변경 면

| 파일 | 변경 |
|---|---|
| `dddjango-web/scripts/src/subst.py` | `_history_renames` 신설(약 18행) · `build_pairs` 3행 · 머리 주석 4~5행(«쌍은 web/ 개명(git diff -M — 누적과 커밋별 사슬)») |
| `codex-dddjango-web/skills/dddjango-web/scripts/src/subst.py` | byte 미러 |
| `dddjango-web/scripts/test/fixtures_subst.sh` | S14a~h 8건(초안 = scratch `proposed_s14.sh`). 기존 사례의 쌍 계수(S6b «쌍 2» 등)를 건드리지 않도록, S14h가 쓰는 `web/a/x/{f,g}.py`는 공용 기준 저장소가 아니라 S3 방식의 사례 전용 기준 커밋에 둔다 |
| `codex-dddjango-web/skills/dddjango-web/scripts/test/fixtures_subst.sh` | byte 미러(`verify-web`의 `diff -rq`가 test/까지 본다) |
| `dddjango-web/scripts/backstop.py:20-21` 주석 | 무변(«기준..대상 사이 web/ 밖 변경이 … 치환뿐인지» — 여전히 참) |
| Coordinator `dddjango-web.md:215`·`:217`·`:223`·`:224` / Codex `SKILL.md:238`·`:246`·`:247` | **무변.** ④의 문면은 대조 구간(누적)만 말하고 쌍의 출처는 말하지 않는다. «런 중 커밋은 기능 슬라이스와 분리한다»(`:215`)가 이미 있어서, (c)가 기대는 «개명과 교체가 다른 커밋»은 기존 규칙이 보장한다 |
| houserules `final.md:200`·`:208` · architect `:56` · coder-web `:76` · REQUEST_GUIDE | 무변(쌍 출처를 서술하지 않는다) |

증명 명령:
- `bash dddjango-web/scripts/test/fixtures_subst.sh` — 32 → **40** PASS
- `make verify-web` — run_fixtures 전체와 scripts byte 미러 대조
- (선택) scratch `repro_d1.sh <설치본 backstop.py>` [2] exit 0

### D1-6. 공수 [추정]

구현 0.5시간 · 픽스처 0.75시간 · 미러·verify·자기 검토 0.5시간, 합계 약 2시간이다. web 수리 관례 절차(설계·적대 검토·계획 리뷰·구현 리뷰)를 모두 돌리면 약 4시간이다.

---

## D3 — `extract_contract.py`가 인용 0에서 exit 1을 내고, Coordinator에는 그 갈래가 없다

### D3-1. 근본 원인 [실측]

| 위치 | 사실 |
|---|---|
| `dddjango-web/scripts/extract_contract.py:146-148` | `if not cited:` → stderr `[extract-contract] 인용 path 0개 — paths-file이 비었다.` · `return 1`. `server-contract.json`을 쓰지 않는다 |
| 같은 파일 `:12-16` 독스트링 | «종료코드: 0=성공 / 1=인용 누락·파싱 실패». 해석은 두 갈래뿐이다(인용 부재 → 설계 반송 · 파싱 실패 → G0 계약 출처 재해소). 인용 0은 해석에 없다 |
| 같은 파일의 그 밖 exit 1 | 사용 오류 `:97-99` · paths-file 읽기 실패 `:134-136` · 산출 쓰기 실패 `:235-237` |
| `fixtures_contract.sh:162-165` F10 | «빈 paths-file — exit 1 + «인용 path 0개»»를 **의도된 동작으로 고정**한다. 전사 누락(명세는 인용했는데 파일이 빔)을 기계로 잡는 가드다 |
| Coordinator `dddjango-web.md:200` step 6 | 발동 조건은 «openapi 동결본이 있을 때»다. «**exit 1은 stderr로 가른다**»의 갈래는 «인용 path가 동결본에 없음 → 설계 반송»과 «파싱 실패 → G0 계약 출처 재해소» 둘뿐이다. 인용 0과 실행 오류 셋은 지시가 없다. «명세 인용 수 == 경량본 paths 수» 대조도 경량본이 없으면 설 자리가 없다 |
| `:212` coder-web 입력 | «`server-contract.json`(정적 화면 한정이면 없음을 명시)» — 인용 0은 언급하지 않는다 |
| `:267` 설계 반송 재진입 | «인용을 건드렸으면 … extract_contract.py를 재실행». 인용이 0이 되면 같은 exit 1을 만나고, 옛 경량본이 stale로 남는다 |
| `:146`·`:147` | 동결은 출처가 해소되면 G0 전에 무조건 한다. `static_only`는 출처가 없을 때만 선다. 그래서 «동결본 있음 + 인용 0»은 API를 새로 소비하지 않는 수정 요청마다 생긴다 |
| `agents/coder-web.md:27` | «정적 화면 한정 승인이면 '없음' 명시 입력» — 역시 인용 0은 언급하지 않는다 |

리허설 처리 **[실측]**: `scope.md:55` «동결본 불량·임의 가정이 아니라 인용 0이라 절단 대상이 없다 · `server-contract.json` 미생성 — coder-web에는 «소비 계약 없음(인용 0)»으로 전달». 결과는 맞았지만 규범 밖의 즉흥 처리였다.

### D3-2. 재현 [실측]

`diag-D3/`에서 리허설 동결본(`openapi-full.json` — OpenAPI 3.1.0 · 46 paths)으로 돌렸다.

```
[1] 리허설 원본 빈 contract-paths.txt    → [extract-contract] 인용 path 0개 — paths-file이 비었다. · exit=1 · server-contract.json 미생성
[2] 주석 1줄만(`# 명세 인용 0`)          → 같은 메시지 · exit=1
[3] 대조: 실존 path 1개(POST /api/accounts) → paths 1개 · components 10개 · exit=0
[4] paths-file 없음                        → paths-file 읽기 실패 · exit=1
    out 디렉터리 없음                      → 산출 쓰기 실패 · exit=1
    --out 누락                             → 사용: … · exit=1
```

기존 픽스처 `fixtures_contract.sh`는 현행 PASS 13이다. F10이 [1]을 exit 1로 고정한다. 인용 0을 «정상 생략»으로 다루는 사례는 없다(스크립트 밖 Coordinator 판단이라 픽스처 대상이 아니다).

### D3-3. 수리 선택지

| | 내용 | 장점 | 단점 |
|---|---|---|---|
| **(A) Coordinator 갈래 추가 (권고)** | step 6 앞머리에 쓴다: «명세가 인용한 엔드포인트가 0이면 절단하지 않는다 — `contract-paths.txt`·`server-contract.json`을 만들지 않고 `scope.md`에 `계약 절단: 명세 인용 0 — 생략(동결본 유지)` 1행을 적는다. coder-web 입력은 «server-contract.json 없음 — 명세 인용 0»이다». exit 1 갈래에 둘을 더한다. ③ «인용 path 0개»는 명세 인용이 1 이상인데 빈 파일이라는 뜻이다 → 전사 누락이니 `contract-paths.txt`를 재작성해 재절단한다. ④ 그 밖 stderr(사용 오류·paths-file 읽기·산출 쓰기 실패)는 미실행이다 → 원인을 고쳐 다시 돈다(설계 반송·계약 출처 재해소가 아니다) | 스크립트·픽스처 무변. F10의 전사 누락 기계 가드를 유지한다. 리허설의 즉흥 처리를 규범으로 굳힐 뿐이다 | 인용 0 판정은 Coordinator가 명세 §계약 소비를 읽어 한다(LLM 판단). 다만 이미 «명세 인용 수 == paths 수» 대조를 Coordinator가 하고 있어 새 재량은 아니다 |
| (B) 스크립트가 인용 0을 성공으로 | `:146-148`을 exit 0으로 바꾸고 `paths: {}` 경량본(openapi·info·servers·security·securitySchemes 보존)을 쓴다. F10 기대를 0으로 바꾼다 | 흐름이 한 가지다(늘 돌리고, 0 == 0 대조가 선다) | 빈 파일 = 전사 누락이라는 **기계 가드를 잃는다**. 명세가 N ≥ 1을 인용했는데 파일이 비어도 exit 0이 나고, 잡는 것은 Coordinator의 계수 대조(LLM)뿐이다. 스크립트·미러·F10·독스트링·Coordinator가 모두 바뀐다 |
| (C) `--expect <N>` 추가 | Coordinator가 명세 인용 수를 넘기면 스크립트가 `len(cited) == N`을 기계로 대조한다. N = 0이면 exit 0이고 산출이 없다 | 계수 대조가 LLM에서 기계로 올라간다(전사 누락 가드가 강해진다) | 결함 수리를 넘는 새 기능이다(원칙 05). 스크립트·미러·픽스처 2~3건·Coordinator·Codex가 모두 바뀐다 |

### D3-4. 권고 — (A)

결함은 «정상 상황에 규범이 없다»는 것이지 도구가 틀렸다는 것이 아니다. 빈 입력 파일은 전사 누락과 «인용 0»을 구별하지 못한다. 그러니 구별은 명세를 읽는 Coordinator가 하고, 도구는 지금처럼 빈 입력을 거부하는 쪽이 맞다. 같은 이유로 인용 0일 때는 빈 `contract-paths.txt`도 만들지 않는다. 빈 파일은 전사 누락과 모양이 같다.

### D3-5. 변경 면

| 파일 | 변경 |
|---|---|
| `dddjango-web/commands/dddjango-web.md:200` | 인용 0 생략 1문장 · exit 1 갈래 ③·④ 2구 |
| 같은 파일 `:212` | «`server-contract.json`(정적 화면 한정이거나 명세 인용 0이면 없음을 명시)» |
| 같은 파일 `:267` | «인용이 0이 되면 절단 생략 규칙대로 기존 경량본을 coder 입력에서 뺀다» 1구 |
| `codex-dddjango-web/skills/dddjango-web/SKILL.md:223`·`:235`·`:290` | 같은 의미의 미러(byte 미러 아님 — `verify-web`은 «적용 범위 규범» 문단만 byte 대조) |
| (권장) `dddjango-web/agents/coder-web.md:27` · `codex-dddjango-web/skills/dddjango-web-coder-web/SKILL.md:27` | «정적 화면 한정 승인이거나 명세 인용 0이면 '없음' 명시 입력» 1구. 무기억 coder가 «없음»을 정적 한정으로만 읽지 않게 한다 |
| `extract_contract.py`·`fixtures_contract.sh` | **무변**(F10 유지) |

증명 명령:
- `bash dddjango-web/scripts/test/fixtures_contract.sh` — 13 PASS 무변
- `make verify-web` — 적용 범위 규범 문단 byte 대조 · REQUEST_GUIDE 등 무영향 확인

행동 확인은 다음 리허설에서 한다. 인용 0 요청 1건에서 Coordinator가 추출기를 부르지 않고, 1행 기록과 coder 입력 «없음 — 인용 0»을 내는지 본다.

### D3-6. 공수 [추정]

산문 3곳 + 미러 3곳 + (권장) coder 2곳, 약 0.5~1시간이다. 검토를 포함하면 약 1.5시간이다.

---

## 부록 — 실험 파일(scratch · 저장소 밖)

- `diag-D1/repro_d1.sh [<backstop.py>]` — D1 실바이트 재현(인자로 러너를 바꿔 현행·시제품을 비교한다)
- `diag-D1/repro_d1_variants.sh [<backstop.py>]` — V1~V3
- `diag-D1/proto/scripts/` — (c) 시제품(플러그인 scripts 사본 + `subst.py` 패치)
- `diag-D1/proposed_s14.sh <scripts 디렉터리>` — 제안 픽스처 S14a~h 초안
- `diag-D3/` — 추출기 재현 입력(`comment-only.txt`·`one.txt`)
