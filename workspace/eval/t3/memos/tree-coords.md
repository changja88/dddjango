# T3 게이트 조항 메모 — «houserules 트리 행 좌표 공백»

- 발단: `workspace/eval/t3/worksheets/discipline-houserules-final.md` §4 «트리 «행 번호» 는 파일 행 번호가 아니다» + §3 표 10·11번(웨이브 3 발견).
- 물음: 정본·검사기·에이전트 문서가 「트리 N행」으로 가리키는 좌표를 **그래프가 짚게** 할 것인가. 처분안 셋 — ⓐ 펜스 행 분해 재이관 · ⓑ alias형 좌표 대장 · ⓒ 현상 유지 + 소비층 규약.
- 판정: **ⓒ 채택**(백스톱 1건 신설 동반) · **ⓐ 기각** · **ⓑ 조건부 보류**. 근거는 §2~§4, 실행 항목은 §6.

---

## 1. 결론 먼저

「트리 N행」은 **이 문서의 좌표가 아니다.** 정본은 `docs/file_tree.html` 의 `data-r` 이고, 기계 사본은 `dddjango/scripts/standard_tree.py` 의 `Row.r` 이며, `final.md` §1 펜스는 그 **세 번째 사본**이다(`tree_mirror_check` 가 A≡B≡C 로 지킨다). 좌표를 실제로 **해소하는** 도구도, **생성하는** 도구도 전부 A·B 를 보며, **펜스의 행 오프셋을 세는 소비자는 저장소 전체에 0건**이다(§3 실측).

따라서 「그래프가 못 짚는다」는 것은 **검증 공백이 아니라 조인 공백**이고, 그 조인의 실수요는 프롬프트층 인용 **12건 · 5좌표**뿐이다. 그 12건조차 재진술 대상이 아니라 **괄호 주소**임이 문면 대조로 확인된다(§5-2). 펜스를 140행으로 분해하면 블록은 **7 → 148**(BlockShape +141)로 늘고 후행 블록 IRI 4건이 재번호되지만, 얻는 것은 «행 N = 블록 b(N+2)» 라는 **오프셋 산술**일 뿐 이름 있는 좌표가 아니다 — 트리가 개정되면 다시 밀린다.

---

## 2. 좌표계의 실물 — 정본은 그래프 밖이다

`workspace/tools/tree_mirror_check.py` 선두가 세 자리를 명시한다.

| 자리 | 실물 | 성격 |
|---|---|---|
| **A 정본** | `docs/file_tree.html` 의 `data-r` 행 140개 | 「트리 N행」의 **유일한 출처**(도구 문면: «명세 «자리»의 「트리 N행」이 이 번호다») |
| **B 플러그인** | `dddjango/scripts/standard_tree.py` — `Row.r` 필드 | 검사기 19종이 import 하는 유일한 트리 데이터 |
| **C 문서** | `final.md` §1 TREE 블록 = 그래프 `s004-1/b3` | 배포용 사본 — `tree_mirror_check --write` 가 **splice 로 덮어쓴다** |

불변식 `A ≡ B (r·depth·name·kind) · A ≡ C (r·depth·name)` 는 오늘 green 이다(`in-sync: 정본 ≡ 플러그인 ≡ 문서 (140행)`).

**A·B 는 30문서 코퍼스 밖이다**(`corpus-manifest.tsv` 30행 — `docs/`·`scripts/` 없음). 즉 그래프는 좌표계의 **정본을 담고 있지 않고**, 담고 있는 것은 사본 C 하나다.

> **부수 발견(별건 처분 필요)** — `s004-1` 은 `owner-graph` 이고 본문에 «이 본문 직접 수정 금지» 마커가 붙었는데, `tree_mirror_check.py:195 splice_final()` 은 같은 스팬을 **직접 `write_text` 한다.** 한 스팬에 기록자가 둘이다. 오늘은 트리 미개정이라 잠복 상태지만, 트리가 개정되는 순간 `--write` 가 그래프 소유 본문을 고쳐 `ontology_render_sync` 가 red 를 낸다. 처분안 ⓐ 는 이 충돌을 **해소하지 않고 141블록만큼 키운다**(재생성 대상이 문서 1스팬 → TTL 141리터럴로 늘어난다).

---

## 3. 소비층 실측 — 누가 이 좌표를 실제로 쓰는가

재현 명령은 §7. 계수는 `codex-dddjango/` 미러 제외(byte-identical 사본이라 이중 계상 금지).

| # | 층 | 실물 | 좌표를 다루는 방식 | 건수 | 해소 정본 |
|---|---|---|---|---|---|
| ① | **기계 해소** | `workspace/tools/spec_lint.py` ③ (`_expand_row_refs` + `load_tree_rows`) | 538규칙 명세의 「트리 N행」을 정규식으로 파싱해 **A(`data-r`)로 해소** · 140행 전수 커버리지 + 141행 이상 참조 fail-closed | 명세 내 **425**건 · 오늘 `위반 0건` | **A** |
| ② | **기계 생성** | `dddjango/scripts/check-layer-skeleton.py` 154·161·234·250·256행 | `f"… (트리 {crow.r}행)"` — **B 의 `Row.r` 에서 런타임 방출**(#488 진단) | **5**곳 | **B** |
| ③ | 정적 인용 | check-\*.py 27종 docstring·완료 메시지 | 하드코딩 문자열(출처 표기) — 해소 안 함 | **30**건 / 12파일 | — |
| ④ | 파생물 | `dddjango/scripts/rulepack.json` | ③의 파생 | 2건 | — |
| ⑤ | 앵커 검사 | `workspace/tools/anchor_integrity_check.py` ⑤ | ««트리 22~32행» 동반 … **행 번호 자체는 검증 대상 밖** — 절·제목 검증으로 갈음» **명시 선언** | — | — |
| ⑥ | **프롬프트층(그래프 코퍼스)** | agents 3 · command 1 · SKILL 1 · final 2 = **7문서** | LLM 실독용 **괄호 주소** | **14**건 | — |
| ⑦ | 문서 사본 | `final.md` §1 펜스(그래프 `s004-1/b3`) | 행 번호를 **텍스트로 인쇄**(값) | 1블록 | C |

**핵심 실측 셋.**

1. **펜스 행 오프셋을 세는 소비자 = 0.** ①은 A 를, ②는 B 를 본다. 워크시트 §4 가 계산한 «파일 행 = 트리 행 + 31» 오프셋을 쓰는 코드는 저장소에 없다.
2. **⑥ 14건 중 2건은 좌표가 아니다.** `discipline-reviewer.md:99` «§1(표준 트리 140행)» 과 `SKILL.md:29` «**§1 트리 140행**을 읽고» 는 트리의 **크기**이고, 140번째 행(`<environment>.py`)이 아니다. 같은 표기가 538규칙 명세 761행에서는 **행 포인터**로 쓰인다(«트리 140행 `<environment>.py` 가 자리표시자라») — 표층 문법이 크기/포인터를 구분하지 못한다. 어떤 기계 해소기도 이 중의성을 먼저 처리해야 한다.
3. **실좌표 12건 · 5범위뿐.** `트리 2~4행`×4 · `22~32행`×4 · `39~44행`×2 · `105~111행`×1 · `1행`×1. 전부 **범위**이고 단일 행이 아니다 — 처분안 ⓐ 가 만드는 행 단위 블록은 **한 인용을 한 IRI 로 못 받는다**(2~4행 → 블록 3개를 묶어야 한다).

---

## 4. byte 등가·재이관 비용 실측 (처분안 ⓐ)

스크래치 그래프에서 실제로 분해해 측정했다(저장소 무변경 — `--root scratchpad/ont-x`).

| 항목 | 현행 | 분해 후 | 판정 |
|---|---|---|---|
| **렌더 byte 잔차** | 절 스팬 == 렌더 | 절 스팬 == 렌더 | **등가 성립 — 0** |
| `s004-1` 블록 수 | 7 | **148**(펜스 142행 = 개펜스+140행+폐펜스) | +141 |
| `BlockShape` 기대표 | 2,881 | **3,022** | +4.9% |
| rules TTL 파일 크기 | 56,416 B | **98,669 B** | +74.9% |
| 게이트 ①~④(1파일 · rules 전량 병합) | 4.49 s · green | **4.78 s · green** | +6.5% · **차단 없음** |
| 재번호되는 블록 IRI | — | `b4→b145` `b5→b146` `b6→b147` `b7→b148` | 4건 |
| ISSUED / LEDGER | — | **무변**(펜스 행은 Work 0 — 문장 비계수 판정 승계) | 0 |
| `statesNorm` | R-3190·R-3191·R-3192 | 유지(Work IRI 불변, 부착 블록만 이동) | 0 |

**즉 ⓐ 는 기술적으로 막히지 않는다.** byte 등가도, 게이트도, 채번 원장도 통과한다. 반대 근거는 전부 **의미·소유·선례** 쪽이다.

- **의미** — 얻는 좌표가 «행 N = 블록 b(N+2)» 오프셋이다. 이름이 아니라 산술이고, 펜스 앞 블록이 하나만 늘어도 전 좌표가 밀린다. 워크시트 §4 가 지적한 «파일 행 = 트리 행 + 31» 문제를 **다른 상수로 옮겨 적는 것**에 가깝다.
- **소유** — §2 부수 발견의 이중 기록자 문제를 키운다. 트리 개정 시 `tree_mirror_check --write` 가 문서를 고치고, 그 뒤 rules TTL 의 141개 리터럴을 **손이나 새 도구가** 재생성해야 한다(그 도구는 아직 없다).
- **선례** — 코퍼스 전체 `kind-code` 블록 **270개 · 총 6,036행**이다. 「펜스는 행으로 분해한다」를 원칙으로 세우면 BlockShape 2,881 → 약 8,647(+200%). 이 펜스만 예외로 두려면 「내부 좌표계를 가진 펜스만」이라는 판별선이 필요한데, 그 판별선의 유일한 실물이 이 한 블록이다.

---

## 5. 처분안 대조

### 5-1. ⓑ alias형 좌표 대장 — 현행 문법으로는 성립하지 않는다

T2-2 대장(`ontology/wiring/aliases.ttl`)의 계약이 막는다.

- `AliasEntryShape-aliasFor sh:class djr:Work` — alias 의 표적은 **Work(규범)** 다. 트리 행은 «값이나 문장 비계수»(발주서 note · 워크시트 §1 `s004-1`)라 Work 가 아니다.
- `ontology_structural_check.py` ⑥′ 해소 4조건이 표적에 **ISSUED 발행 + `currentExpression` 1 + Expression 왕복**을 요구한다. 트리 행 140개를 alias 표적으로 만들려면 **Work 140개를 채번**해야 하고, 이는 「펜스는 값이고 문장 계수 0」이라는 P0 승계 판정을 뒤집는다(NormShape 3,409 → 3,549).
- `BlockShape` 는 `sh:closed true` 라 Block 에 좌표 속성을 붙일 수 없다. `SectionShape` 는 비폐쇄지만 절 단위 좌표는 해상도가 맞지 않는다.

**따라서 ⓑ 는 「alias 재검토」 조항 안에서 현행 문법으로 처리할 수 없고, 어휘 신설(§7 절차)이 전제다.** 신설한다면 옳은 모양은 alias 가 아니라 **정본 A 를 출처로 하는 `TreeRow` 노드 대장**이다 — `data-r` 를 그대로 IRI 로 삼아(`djr:tree-row-22`) 행 번호·depth·name·kind 를 싣고, `tree_mirror_check` 가 A 로부터 **네 번째 사본**으로 생성한다. 이때 비로소 그래프가 짚는 것은 사본의 사본이 아니라 정본이고, 범위 인용(2~4행)도 노드 3개로 정확히 받는다. 다만 이 투자는 **소비자가 생긴 뒤**에 한다 — 오늘 실수요는 §3-3 의 12건이고, 그 12건은 아래 5-2 에서 조인 대상이 아님이 확인된다.

### 5-2. 워크시트 §3 표 10·11번은 «재진술 유예»가 아니라 «기각»이다

두 행이 ⓐ 의 유일한 실수요로 지목됐다. 문면을 직접 대조하면 인용의 표적이 트리 행이 **아니다**.

- **11번** — `agent-coder.md:57` «import-time registration을 금지하며 BC `composition_root/`(`dependency_wiring.py` — final.md §1 트리 2~4행)가 dependency injection만 소유한다». 재진술되는 **규범**은 「`composition_root` 만이 네 칸을 다 안다」 = houserules `s006/b3`(#10)이다. 「트리 2~4행」은 그 칸이 **어디 있는지 알려주는 괄호 주소**다. 조인해야 할 블록은 이미 존재한다.
- **10번** — `agent-discipline-reviewer.md:84` «OHS published contract(`open_host_service/*/contract/`)의 discriminator wire `Literal`(contract 무의존이 우선 — houserules `references/final.md` §1 트리 22~32행)». 재진술되는 규범은 discriminator wire `Literal` 유지이고, 워크시트 자신이 상대를 `discipline-cleancode-final/s026-2.14` 로 이미 특정했다. 「트리 22~32행」은 OHS 계약 칸의 주소다.

**판정** — 두 행은 §3-1 «유예 기각» 절로 옮긴다. 사유: 「인용의 표적이 규범 문장이 아니라 트리 «값»의 좌표라 `djr:restates`(Block↔Block, `sh:class djr:Block`)의 주어가 성립하지 않는다」 — 15번(문서-코드 재진술)·`s015`(#74 가드) 기각과 **같은 부류**다. 이로써 ⓐ 를 요구하던 실수요가 0 이 된다.

### 5-3. 세 안 요약

| | 그래프가 짚나 | 기계 비용 | 유지 비용 | 선례 위험 | 오늘 실수요 |
|---|---|---|---|---|---|
| **ⓐ 펜스 행 분해** | 오프셋 산술로 부분 | 블록 +141 · TTL +74.9% · 게이트 +6.5% | 트리 개정마다 141리터럴 재생성 도구 필요(미존재) | 펜스 270개·6,036행 일반화 압력 | **0**(5-2 로 소멸) |
| **ⓑ alias형 대장** | 이름으로 정확히 | 어휘·셰이프·구조검사 신설 + Work 140 채번(또는 신 클래스) | 정본 A 로부터 생성 — 삼중→사중 동기 | 낮음(대장은 wiring 관례 안) | **0** — 소비자 생기면 재개 |
| **ⓒ 현상 유지 + 규약** | 안 짚는다(명시 선언) | ~0 | 0 | 없음 | 해당 없음 |

---

## 6. 권고와 실행 항목

**ⓒ 채택.** 「트리 N행」은 그래프 좌표가 아니라 **정본 A(`docs/file_tree.html data-r`) 의 좌표**임을 규약으로 못 박고, 해소 책임을 이미 green 인 두 도구(`spec_lint` ③ · `tree_mirror_check` 삼중 동기)에 남긴다. 이는 `anchor_integrity_check` ⑤ 가 이미 세운 선례(«행 번호 자체는 검증 대상 밖 — 절·제목 검증으로 갈음»)와 같은 자리다.

1. **`workspace/tools/ontology-authoring.md` §13 또는 §14 에 1행 신설** — 「펜스 «내부» 번호는 블록 좌표가 아니다. 문서·에이전트가 「트리 N행」으로 가리키는 것은 `docs/file_tree.html` 의 `data-r`(≡ `standard_tree.Row.r`)이고, 해소 주체는 `spec_lint.py` ③ 과 `tree_mirror_check.py` 삼중 동기다. 코드 펜스는 행 단위로 분해하지 않는다(§13 자연 단위 유지).」
2. **워크시트 §3 표 10·11번을 §3-1 «유예 기각»으로 이동** — 사유는 5-2. §4 «트리 «행 번호» 는 파일 행 번호가 아니다» 항목은 「소급 패스가 다뤄야 할 실물 공백」에서 「조인 대상 아님 — 좌표 정본은 코퍼스 밖」으로 문면 교체.
3. **백스톱 1건 신설(≈20행)** — 오늘 남는 유일한 실위험은 **댕글링 좌표**(트리가 개정돼 행이 밀렸는데 프롬프트층 12건이 옛 번호를 계속 가리키는 것)다. 이건 그래프가 아니라 `anchor_integrity_check.py` 의 자리다: ⑤ 의 «검증 대상 밖» 을 「⑦ 트리 행 좌표 해소」로 좁혀 승격하고, `spec_lint.load_tree_rows` / `_expand_row_refs` 를 재사용해 코퍼스 30문서 + check-\*.py 27종의 「트리 N행」을 A 로 해소한다. **크기/포인터 중의성 처리 필수** — 「§1 트리 140행」·「표준 트리 140행」꼴(직전 토큰이 `§1`·`표준 트리`)은 크기로 보고 제외한다(현재 코퍼스 2건).
4. **§2 부수 발견을 별건으로 등재** — `tree_mirror_check --write` ↔ `owner-graph` 이중 기록자. 트리 개정 전에 처분해야 하고(개정 순간 `ontology_render_sync` red), ⓐ 채택 여부와 무관하다. 처분 후보: ㉠ `splice_final()` 이 문서 대신 rules TTL `s004-1/b3` 리터럴을 쓰고 렌더가 문서를 투영 ㉡ `s004-1` 을 `owner-prose` 로 강등(§0·§2 규범 3건의 소유를 잃으므로 비권장). **㉠ 권고**.
5. **ⓑ 재개 조건 기록** — 「그래프 질의가 트리 칸을 **표적**으로 요구하는 소비자가 실제로 생기면」 재개하고, 그때도 펜스가 아니라 정본 A 를 출처로 `TreeRow` 노드 대장(`wiring/tree-rows.ttl`)을 저작한다. 지금 착수 금지 사유: 실수요 0 · 어휘 동결 개정 비용 · 사본 4중화.

**ⓐ 기각 사유(1줄 요약)** — byte 등가·게이트는 통과하지만(§4), 얻는 것이 이름 없는 오프셋이고, 정본이 코퍼스 밖이라 **사본의 사본을 141조각으로 쪼개는 것**이며, 유일하다던 실수요 2건이 재진술이 아닌 괄호 주소로 판명됐다(§5-2).

---

## 7. 재현 명령

```sh
# ① 소비층 전수(미러 제외)
grep -rnoE "트리 [0-9]+([~·, ]+[0-9]+)*행" --include="*.md" --include="*.py" --include="*.ttl" \
  --include="*.json" --include="*.tsv" . | grep -v "^./codex-dddjango" | sort -u | wc -l   # 1266

# ② 그래프 코퍼스 인용 전수(7문서 · 14건)
for f in dddjango/agents/{coder,design-architect,discipline-reviewer}.md \
         dddjango/commands/dddjango.md dddjango/skills/discipline-houserules/SKILL.md \
         dddjango/skills/discipline-houserules/references/final.md \
         dddjango/skills/architecture-ddd/references/final.md; do
  grep -noE "트리 [0-9]+([~·, ]+[0-9]+)*행" "$f" | sed "s|^|$f:|"; done

# ③ 런타임 생성(Row.r) 5곳
grep -n "\.r}행" dddjango/scripts/check-layer-skeleton.py

# ④ 해소기 green 실증
.venv/bin/python workspace/tools/spec_lint.py            # 규칙 538 · 위반 0건
python3 workspace/tools/tree_mirror_check.py --root .    # in-sync: 정본 ≡ 플러그인 ≡ 문서 (140행)

# ⑤ ⓐ byte 등가·비용 실측(스크래치 — 저장소 무변경)
#    분해본 렌더 == 현행 절 스팬 byte: True · 블록 7→148 · 게이트 green 4.78s
PYTHONPATH=workspace/tools .venv/bin/python scratchpad/treecoord_probe2.py
cp -R ontology scratchpad/ont-x && PYTHONPATH=workspace/tools .venv/bin/python scratchpad/write_split.py
.venv/bin/python workspace/tools/ontology_gate.py --root scratchpad/ont-x \
  scratchpad/ont-x/rules/discipline-houserules-final.ttl
```

측정 환경: 2026-08-22 · `.venv` · rdflib/pySHACL(게이트 ④ = 대상 파일 + vocab + wiring + rules 전량 병합).
