# 수리 배치 2 계획 v2 (v2.17.16 후보) — 3부 구성 + 3단계 리뷰 반영 델타(말미)

- 날짜: 2026-09-03 · 지위: 루브릭(`2026-09-03-repair-batch-2-rubric.md`) 1단계 결과 표의 재정의 처방 7건을 3부로 분할한 계획 v1(3단계 적대 리뷰 전). 판형은 `2026-09-02-pregate-repair-plan.md` 준용 + 항목별 3축(코퍼스 정합·일반화·무손실).
- 병합 순서: **Part 1(소규모 묶음) 선머지 → Part 2(대형 A) rebase → Part 3(대형 B)**. 근거: Part 1의 `registry_gate.py`·`design_pregate.py` 변경은 출력/파서 국한이고 Part 2·3은 판정 로직을 고침 — 헝크 비중첩.
- 공통 비범위: 검사기 27종 판정 무변경 · MODE(관찰) 불변 · 마커 검사기 드롭 · 소비 명세 §6.3 래퍼 pin(발주자 소유) · G0 하드 검사 · 레인 경로 필터 · 자동 재앵커.

---

# Part 1 — 소규모 묶음 5건 (④′ 파서 · ⑤ Migration 정형 · ⑧ skip 기록 · ③ 툴체인 헤더 · ⑥ 중반 재발화)

- 스코프: 실행기 `dddjango/scripts/design_pregate.py` 3계열(파서 분류·마이그레이션 정형·`--base` 조건부 기실현) + 게이트 `dddjango/scripts/registry_gate.py` 출력 1행 + 그래프 리비전 7건(신규 규범 0·ISSUED 무변경) + 픽스처 확장.
- 이월: `abc.ABC`/다중 base ABC 렌더 · update 시뮬레이션 확장 · `--print-toolchain` 플래그(대형 A 충돌면 — 이번 배치 비채택) · 소급 명세의 저장소 픽스처 편입(대상 venv 의존 — 수동 채널 유지).

## 0. 원인 확정 총괄 (전건 코드 실독 + 인메모리 재현 완료)

| # | 실측(레인·ID) | 원인 (코드 지점 — 실독 확정) | 재현 |
|---|---|---|---|
| ④′ | 레인 1 형식 red ×2 «함수에 필드 목록» (`_GroupMediaAssetItem {…}`) · 1단계 B MINOR «`_Class(Base)` 무경고 함수 스텁» | `design_pregate.py:352` `if head[:1].islower() or head[:1] == "_":` — 언더스코어 선두 전부를 함수 분기로 보냄. `_CLASS_HEAD_RE`(:133 `^([A-Z]\w*)`)·`_METHOD_RE`(:129-130 `^([A-Z]\w*)\.`)도 `_` 선두 불수용 → `_Class.method` 행은 :358 «파싱 불가» red. `_FUNC_RE`(:131-132 `^([a-z_]\w*)`)가 `_Class(Base)`를 params=`Base`인 함수로 흡수 → `render_stub` :629-633이 `def _Class(Base) -> object:` 렌더 → `compile` 통과(무경고) | 인메모리: `_GroupMediaAssetItem {id: UUID}` → «함수에 필드» / `_Class(Base)` → `('function','_Class','Base')` + 스텁 compile OK / `_Class.method(self, x: int)` → 파싱 불가 / `M(Model) {kind = models.CharField(max_length=32)}` → 필드 정상(대입식 기허용 확인) / `M(Model) {kind, language}` → :369-370 문면 red |
| ⑤ | 레인 3 #593 `0001_initial.py`(안정 ID `0c3ee0342328`, 2·3차 연속) · B MINOR `__init__.py` 헤더 방출 | `render_stub` :599 헤더(`"""pre-gate 팬텀 스텁."""` + `from __future__ import annotations`)를 모든 add에 방출. 검사기 `check-mechanism-ownership.py` `_check_migration_file` :210-220은 `__init__.py`에 docstring 외 statement(ImportFrom 포함)가 있으면 #593, :222-246은 `Migration` 클래스 정확히 1개 없으면 #593(:245-247). symbols 없는 `0001_*.py` add는 헤더뿐인 빈 모듈 → red | 인메모리: `…/migrations/__init__.py` add 렌더 = 헤더 2행 → ImportFrom → #593 경로 확정 |
| ⑧ | 레인 1 관측 공백(블록 해시 f227e2a→4abb563 변동에도 재실행 흔적 0 — 규범 미준수 미관측) | 규범 `dddjango/commands/dddjango.md:94` «기계가독 블록 해시가 불변이면 재실행을 skip» — skip의 기록 의무·해시 판형(입력·알고리즘) 미성문 → skip과 미실행이 구별 불능. 실행기에는 캐시 없음(`main` :963-1075 실독) | 규범 결손(코드 아님) |
| ③ | 조사 §10 툴체인 계통 2건(Codex 캐시 2버전 보존 × 장수 레인) | `registry_gate.py:367-368` 헤더에 판정 도구의 정체(버전·트리 내용) 0 → «exact command 기록»(`dddjango.md:77` R-0192 · `:148` R-0365)이 경로 pin 계약으로 오독될 여지 | 출력 실독 |
| ⑥ | 레인 3 4·5차 형식 red(add 충돌 — 4차 base HEAD·5차 `--base 9906931`에서 WIP `…/email_notice_template/__init__.py` 충돌) | `materialize` :778-780 `if target.exists(): raise FormError` 단일 조건. 사본 = `git archive <base>`(:1017) + `_overlay_dirty`(:1018 — porcelain은 HEAD 기준, :681-682) → `--base <G1>`이면 슬라이스 커밋분은 사본에 없어 충돌 0이나 미커밋 WIP는 겹쳐져 충돌. 기존 관용 경로는 `empty` 태그(:793-794 `already_built`)뿐 | 코드 경로 실독 + 레인 3 리포트 :108-122 대조 |

## 1. ④′ 파서 `_Class` 분류 수리 + b35 문면

### 1.1 변경 (실행기 — 함수 단위)
1. 정규식(`design_pregate.py:129-133`): `_METHOD_RE` → `^(_?[A-Z]\w*)\.([A-Za-z_]\w*)\((.*)\)…`, `_CLASS_HEAD_RE` → `^(_?[A-Z]\w*)\s*(?:\((.*)\))?\s*$`. `_FUNC_RE` 무변경.
2. `_parse_symbol_rest` :352 분류식 → `is_function = head[:1].islower() or (head[:1] == "_" and not head[1:2].isupper())` — `_`+대문자 선두는 클래스 분기. :354 메시지에 «(클래스는 대문자 또는 `_`+대문자 선두)» 병기.
3. :368-370 필드 반송 메시지 → «`name: Type[ = default]` · `NAME = "literal"` · `name = <식>`(Django 필드 대입식 등)만 허용 — 타입도 값도 없는 bare 이름 불가». `_FIELD_RE`(:134) 무변경.
4. 모듈 docstring §4 문법(:36-39)에 `_Symbol`·`name = <식>` 반영.
5. `_parse_symbols` :399-400 owner 탐색은 `s.name == cls_name`이라 `_Class.method` 결합 자동 성립 — 무변경.

### 1.2 규범 — R-3426 rev3 (amendment, `ontology/rules/agent-design-architect.ttl:1703` · 블록 s005/b35 :2086)
b35 문장에 3항 추가(⑤의 등재와 한 리비전): ① «Symbol은 대문자 선두 또는 `_`+대문자 선두(주 계약이 참조하는 사설 보조 타입도 적는다 — 파서가 클래스로 분류하고 검사기의 사설 면제 판정 경로를 스텁이 그대로 탄다)» ② 필드 문면 = 1.1-3과 동일 문구 ③ ⑤의 마이그레이션 칸 정형(§2.2). 렌더 `--apply agent-design-architect` → `dddjango/agents/design-architect.md:89` 재투영 + codex 의미 미러 `codex-dddjango/skills/dddjango-design-architect/SKILL.md:83` 수동 동기.

### 1.3 3축
- **코퍼스 정합**: R-3426(rev2→rev3 amendment) 1건. 인접 R-3427·R-3424/3425·rulepack 무접촉. 검사기 27종 무변경(사설 클래스 면제는 기존 판정: `check-domain-model.py:150`, `check-usecase-dto-placement.py:201/:325`, `check-naming.py:313`, `check-context-isolation.py:395/:561/:606`, `check-port-adapter-pairing.py:245` 전부 `startswith("_")` 제외 — 충돌·중복·약화 없음).
- **일반화**: kkebi-server 표본 산문에 사설 보조 타입 `_SajuProductBundleItem`×4·`_UpstreamNotifyResult`×3·`class _Unset`×2·`_FakeNotifyResult` 등장, Django 대입식 `= models.TextField(`×6 — 기계 블록 도입 시 동일 형식 red가 재현될 표기. 런타임 무관.
- **무손실**: ⓐ 검출 집합 단조 증가 — `_Class {…}`는 형식 red(예보 0)→클래스 스텁 예보로, `_Class(Base)`는 무경고 함수 스텁→베이스 있는 클래스 스텁으로(contract 칸 `_Foo(BaseModel)`이 BASE_IMPORTS 합성으로 #472 진탐 가시화 — fail-closed 구멍 폐쇄). ⓑ 오차단 0 — 사설 클래스는 실코드와 같은 면제 경로(레인 1 실코드 `_GroupMediaAssetItem` 동파일 공존이 G2 귀속 0·#571 통과 실증). ⓒ 함수+필드(`_helper {…}`) red·bare 이름 red 유지.

## 2. ⑤ 정형 Migration 스텁 렌더 (+ `__init__.py` 빈 파일)

### 2.1 변경 (실행기)
1. 상수 `_MIGRATION_INIT_RE = ^(?:.+/)?migrations/__init__\.py$` · `_MIGRATION_FILE_RE = ^(?:.+/)?migrations/(\d{4}_\w+)\.py$`(검사기 `MIGRATION_NAME_RE` :74와 동형). 위치 무관 — 오배치 진탐은 경로 기반 검사기(#336 `check-mechanism-ownership.py:290-292` 중앙 · #325 check-db-table BC 안 오배치 · #81/#490 check-layer-skeleton)가 내용 불문으로 잡으므로 «표면 제외» 없이 보존.
2. `_migration_stub(path) -> str | None`(신설, `render_stub` 위): `__init__.py` → `""`(진짜 빈 파일). `NNNN_*.py` → 정형:
   ```
   """pre-gate 팬텀 스텁 — 마이그레이션 정형(도구 산출물 모양 · #593)."""
   from django.db import migrations


   class Migration(migrations.Migration):
       initial = True
       dependencies = []
       operations = []
   ```
   대입은 무어노테이션 `Assign`(검사기 :253-265가 `AnnAssign`을 #593으로 봄) · docstring 1개는 :233-235에서 제거되어 무해 · `django.db` import는 `_is_repo_import` :200-205에서 비-저장소.
3. `render_stub` :598 진입부에서 `_migration_stub` 결과가 있으면 즉시 반환.
4. `parse_spec` :521-540 apps.py 후처리 옆에 후처리 추가: 마이그레이션 경로 add에 symbols/imports/raises 전사가 있으면 `plan.notes`에 «마이그레이션 정형 — 채널 전사 무시(도구 산출물 #593)» 기록 후 비움(침묵 금지).
5. 검사기 exit 0 확인: 정형 스텁을 `check-mechanism-ownership.py` :210-266 규칙 전부에 대조(이름 #337 ✓ · repo import #338/#593 ✓ · 클래스 1 ✓ · 데코레이터 0 ✓ · 대입 4종 안 ✓ · operations 리스트 리터럴 ✓). `check-public-surface-annotation.py:112`는 migrations 스캔 제외 → #493 무발화.

### 2.2 규범 — R-3426 rev3 ③항(위 1.2와 동일 리비전)
«값 축 유도 2행»을 «값 축 정형 3항(2026-09-03)»으로: 마이그레이션 칸(`migrations/NNNN_*.py`·`migrations/__init__.py`)은 makemigrations 산출물이라 symbols 전사 대상이 아니다 — file-plan `add`만 적으면 실행기가 정형(Migration 클래스 1·`__init__` 빈 파일)으로 실체화하고 전사는 무시·채널 메모. b35 «생략 = 규약 준수 확약» 논리와 정합: #593이 손편집 자체를 금지하므로 «규약 밖 값»이 존재하지 않는 칸 — **전사 불가** 칸으로 등재(유도 2행과 구별 문면).

### 2.3 3축
- **코퍼스 정합**: R-3426 rev3(합산 1건). #593/#336/#337/#338/#325/#81/#490 검사기·rulepack 무변경. `standard_tree.py` Row 80·81 무변경.
- **일반화**: kkebi 20레인 중 8레인 명세가 `migrations/0001_initial.py` 계획 · kkebi 실물 `migrations/__init__.py` 12개 중 11개 0바이트(1개 개행만) · spring_dream_server 동일 — 정형이 두 프로젝트 실물과 일치. Claude/Codex 무관.
- **무손실**: ⓐ 표면 제외가 아니므로 오배치 진탐(#336/#325/#81/#490) 보존 — 신규 red 픽스처로 고정(§7). ⓑ 정형 스텁은 실물 makemigrations 산출물의 부분집합 모양 → 오차단 0. ⓒ 레인 3 소급에서 `0c3ee0342328` 소멸·타 ID 유지.

## 3. ⑧ 캐시 skip 기록 + 해시 병기 (Coordinator 소유 · 실행기 무변경)

### 3.1 규범 — R-3432 rev2 (amendment, `command-dddjango.ttl:2757` · 블록 s006/b9 :3147 ↔ `dddjango.md:94`)
«기계가독 블록 해시가 불변이면 재실행을 skip한다» 뒤에 병기:
- **해시 판형 고정**(구현 시 macOS/GNU sed 양쪽 실측 후 확정): `sed -n '/<!-- machine: /,/^```$/p; /^| *candidate *|/,/^$/p' design-spec.md | git hash-object --stdin | cut -c1-12` — 기계 블록 4종 + 영구 테스트 입장 표(physical-signals 채널)를 문서 순서로 이어 붙인 blob 해시. git은 실행기 전제라 양 런타임·양 OS 공통.
- **skip 기록 의무**: skip마다 `pregate-report.md` 말미에 1행 append — `- pre-gate skip — 블록 해시 <값> 불변 · 재실행 생략 <UTC> · 직전 예보 <UTC>(판정 <문면>)`. 이 행은 `## pre-gate 예보` 문자열을 쓰지 않는다(픽스처 러너 헤더 계수 비오염). 해시가 바뀌었으면 skip 불가.
- R-3438(리포트 append 의무)·R-3437(배너 1행)·R-3436(구형 명세 skip — 별개)은 무변경·정합 확인만.

### 3.2 3축
- **코퍼스 정합**: R-3432 rev2 1건(⑥과 같은 리비전). R-3436의 «skip»(블록 부재)과 용어 충돌 방지를 위해 «캐시 skip»으로 지칭.
- **일반화**: 프로젝트 무관(명세 파일 내부 판형만 입력) · herdr/STOP 비의존 · 양 런타임 Bash 공통.
- **무손실**: 실행기·게이트 무변경 → 검출 집합 동일. 규범 위반(미실행)을 «skip 행 부재 ∧ 해시 변동»으로 관측 가능해지는 순증. 신규 규범(R-3439) 대신 amendment 택(09-02 R-3433 rev2 선례).

## 4. ③ registry_gate 헤더 버전+실행 트리 digest + «기록 ≠ pin» 정리

### 4.1 변경 (게이트 — 출력 함수 국한)
1. `registry_gate.py` 상단(:44 부근) `_SCRIPTS_DIR: Path = Path(__file__).resolve().parent` + `import hashlib`.
2. `_toolchain_line() -> str`(신설 — `_normalize` :103 직후): 버전은 `_SCRIPTS_DIR.parent/.claude-plugin/plugin.json` → `_SCRIPTS_DIR.parents[2]/.codex-plugin/plugin.json` 순 probe, 실패 시 `(unknown)`(판정 영향 0). digest = sha256(sorted 파일별 `name\0sha256(bytes)\n` 결합)[:16] — 대상 **34파일**: `registry_gate.py`·`anchor_diff.py`·`checker_target.py`·`findings.py`·`checker_registry.py` + `REGISTRY` 27종 + `business_vocab.py`·`standard_tree.py`(검사기 7종/25종이 import — 판정 입력이므로 포함; 제외하면 «동일 digest ≠ 동일 판정»).
3. `main` :367 직후 `print(_toolchain_line())` 1행: `툴체인: dddjango v2.17.16 · 실행 트리 digest <16hex>(34파일 sha256 결합) · 경로 <SCRIPTS_DIR>`.
4. codex 미러 byte 동기 · 봉인 재발행(`registry_gate.py`는 manifest «pipeline» 그룹 — `workspace/tools/manifest_seal.py:73-77`).

### 4.2 규범 — 명확화 2건(clarification)
- R-0192 rev2(`command-dddjango.ttl:551` · s005/b8 :3071 ↔ `dddjango.md:77`) · R-0365 rev3(:1965 · s007/b46 :3441 ↔ `:148`): «exact command 기록은 재현·감사용이지 **경로 고정 계약이 아니다** — 같은 플러그인 버전·같은 실행 트리 digest(registry_gate 헤더 «툴체인» 행)면 설치 경로가 달라도 같은 측정이다. 발주서·래퍼가 캐시 경로를 pin하는 것은 이 규범의 요구가 아니다». 헤더 행은 stdout 수집 의무(R-0365)로 자연히 증거에 실린다.
- codex 의미 미러 `codex-dddjango/skills/dddjango/SKILL.md:96`·`:165` 수동 동기.

### 4.3 대형 A와 병합 순서
Part 1 선머지 → Part 2 rebase. 본 변경은 `main` 밖 헬퍼 1함수 + `main` :367 1행 삽입이고, A는 귀속 로직(:355-365·`_write_introduced` :163-201·`anchor_diff`)을 고침 — 헝크 비중첩. A에 «헤더 2행 순서 유지» 조건 전달.

### 4.4 3축
- **코퍼스 정합**: R-0192·R-0365 clarification 2건. R-0191(차분 도구 빚 스캔 대체 금지)·R-0366~0378 무접촉. 검사기 무변경.
- **일반화**: 레이아웃 probe 2경로로 Claude/Codex 설치본·저장소 개발본 4곳 동일 코드. 편익은 Codex 장수 레인 한정이나 관측성은 공통.
- **무손실**: 판정 경로 무접촉(출력 1행). `registry_gate_smoke.py` 단언은 부분문자열(:84-164)이라 통과. `design_pregate.run_gate` :857-875는 `introduced.json`만 소비 → 예보 리포트 형식 불변.

## 5. ⑥ 중반 재발화 프로토콜 (규범 본체 + `--base` 조건부 기실현)

### 5.1 규범 — R-3432 rev2 (⑧과 동일 리비전) + 포인터 3건
- R-3432 rev2 문면(pre-gate 문단 실행 판형 뒤): «**Phase 2 진입 후 재발화 판형** — 반송·STOP으로 design-spec이 개정돼 재실행할 때는 `--base <G1 승인 시점 기준선 SHA>`를 명시한다(값은 G1 배너 직전 최종 실행의 pregate-report 헤더 «기준선 SHA» · `build_anchor`는 읽지 않는다(R-3434)). 미커밋 WIP는 커밋 또는 stash 후 실행한다. 실행기는 `--base` 명시 시 기준선 트리에 없던 계획 add가 오버레이에 실존하면 «기실현 add»로 already-built에 기록하고 스텁을 생략하며, 기준선 트리에 있는 add는 여전히 형식 red(계획↔실물 모순)다. 재발화의 판정자는 G2 앵커 차분이고, 재발화 형식 red는 승격 기준 ⑶ 계상에서 별도 계수한다.»
- 포인터(clarification): R-0287 rev3(`:1323` · s007/b6 :3532 ↔ `dddjango.md:104`) · R-0419 rev3(`:2409` · s009/b3 :3592 ↔ `:174`) · R-0442 rev3(`:2599` · s010/b6 :3660 ↔ `:189`) — 각 재실행 조항에 «(Phase 2 중이면 재발화 판형 — `--base <G1 기준선 SHA>`·WIP 커밋/stash · pre-gate 문단)» 1절.
- codex 미러 `SKILL.md:112/:121/:189/:203` 수동 동기.

### 5.2 변경 (실행기)
1. `main` :967 `--base` 기본값 `None` → `base_ref = ns.base or "HEAD"`, `explicit_base = ns.base is not None`(리포트 헤더 문면 불변).
2. `main` :1017-1018 사이: archive 직후·overlay 전에 `in_baseline = {p for p in plan.entries if (copy / p).exists()}`(archive == 기준선 트리 — git 추가 호출 0·결정적).
3. `materialize(copy, plan, *, explicit_base: bool = False, in_baseline: frozenset[str] = frozenset(), base_short: str = "")` :770 시그니처 확장. :778-780 →
   ```
   if target.exists():
       if explicit_base and entry.path not in in_baseline:
           report["already_built"].append(f"add(기실현 — 기준선 {base_short} 부재·오버레이 실존 · 스텁 생략): {entry.path}")
           continue
       raise FormError(...)  # 기준선 트리 실존 = 진짜 모순 — 기존 문면 그대로
   ```
   기본 경로(`--base` 미지정)는 byte 동일 동작.
4. `BLIND_SPOTS` :886-895 +1행: «기실현 add(`--base` 명시 시): 오버레이 실물이 스텁 대신 판정된다 — 예보에 실물 판정이 혼입되며 유일 판정자는 G2 앵커 차분». (사각 목록 6행→7행 — v2.17.16 판별 신호.)
5. `write_report` :920-925 무변경.

### 5.3 3축
- **코퍼스 정합**: R-3432 rev2(amendment, ⑧ 합산) + R-0287/R-0419/R-0442 rev3(clarification). R-3434와 정합 문면 포함. 총 Expression +7 → `workspace/eval/fixtures/ontology_gate/target-counts.json` ExpressionShape 3522→3529.
- **일반화**: herdr/STOP 규약 비의존(입력은 git ref와 리포트 헤더값뿐). SD 2레인 실측(reading 4회·레인 3 2회). kkebi는 pre-gate 이전이라 대조 불가(표본 외 미검증 병기).
- **무손실**: ⓐ 기본 경로 불변(E3 회귀 픽스처). ⓑ `--base` 명시 시 기준선 실존 add는 red 유지(E4). ⓒ 기실현 add는 형식 red(예보 0)→예보 진행이므로 검출 집합 순증. ⓓ 형식 red는 P/S/I 판정이 아니라 명세 형식 반송 — 게이트 강도 무관.

## 6. 규범 리비전 총괄 (그래프 저작 절차 — `docs/DEVELOPMENT.md` §3)

| 규범 | 파일:행 | rev | kind | 항목 | 렌더 대상 |
|---|---|---|---|---|---|
| R-3426 | `agent-design-architect.ttl:1703` · b35 :2086 | 3 | amendment | ④′·⑤ | `agents/design-architect.md:89` |
| R-3432 | `command-dddjango.ttl:2757` · s006/b9 :3147 | 2 | amendment | ⑧·⑥ | `commands/dddjango.md:94` |
| R-0192 | `:551` · s005/b8 :3071 | 2 | clarification | ③ | `:77` |
| R-0365 | `:1965` · s007/b46 :3441 | 3 | clarification | ③ | `:148` |
| R-0287 | `:1323` · s007/b6 :3532 | 3 | clarification | ⑥ | `:104` |
| R-0419 | `:2409` · s009/b3 :3592 | 3 | clarification | ⑥ | `:174` |
| R-0442 | `:2599` · s010/b6 :3660 | 3 | clarification | ⑥ | `:189` |

절차: Expression 노드 추가(`prov:wasRevisionOf`·`djr:revision N`·`djr:revisionKind`)+`currentExpression`·`prefLabel` 갱신+블록 `djr:text` 수정(e9fd824 판형) → `ontology_gate.py` 4단 → `ontology_render.py --apply` 2문서 → LEDGER 재기준선 6행 → `make rulepack` → q4 골든 재확인 → codex 의미 미러 8곳 수동 → 봉인 재발행. ISSUED 무변경.
산문 정합: `2026-09-01-pregate-design.md` §7-5(해시 판형)·§8 ⑶(중반 재발화 별도 계수) 추기 · ledger 헤더 «사각 7행 = v2.17.16 판별» 동기 · `design_pregate.py` docstring §4.

## 7. 검증 게이트

1. **픽스처 러너 확장** (`workspace/tools/pregate_fixture_run.py`)
   - `_unit_checks` 추가: `_Item {a: int}`→class · `_Item(Base)`→class base · `_Item.method(self, x: int)`→params `x: int` · `_helper {a: int}`→red 유지 · `_helper(x: int)`→function · `M(Model) {kind = models.CharField(max_length=32)}`→필드 OK · `M(Model) {kind}`→메시지에 «`name = <식>`» 포함 · `render_stub(migrations/__init__.py)==""` · `render_stub(migrations/0001_initial.py)` compile + «class Migration(migrations.Migration)» 포함 + `check-mechanism-ownership.py`의 `_check_migration_file` 직접 호출 Findings 0.
   - `green3-spec.md` 신설(billing BC): `_PrivateItem {…}`+`_PrivateItem.method` + Django 대입식 필드 모델 + `add …/django_billing/migrations/0001_initial.py`·`add …/migrations/__init__.py` → exit 0. 헤더 계수 4→5.
   - `red2-spec.md` 신설: `add application/billing/migrations/0001_initial.py`(BC 안 오배치) → exit 2 + 귀속 규칙 집합 실측 고정(«표면 제외 금지» 증거).
   - **E 계열(`midlane-spec.md`, 별도 합성 저장소·별도 리포트)**: E1 기준선 커밋 → 계획 add 파일 커밋 → `--base <기준선>` → exit 0·충돌 0 / E2 미추적 WIP → `--base <기준선>` → exit ≠3 + «already-built: add(기실현» / E3 E2 상태 `--base` 미지정 → exit 3 유지 / E4 계획 add가 기준선 트리에 실존 → exit 3 유지.
2. **소급 대조(스크래치 격리 사본 — `git clone /Users/hyun/Desktop/spring_dream_server` · 수동 채널)**
   - 레인 3 `9906931` + email-template 명세: S₁ = S₀ ∖ {`0c3ee0342328`}, 타 ID 전건 유지.
   - 레인 2 `7b0befd` + notification-bc 명세(`empty …/migrations/__init__.py`): #14 `3dc440496a29` 유지·건수 1 불변.
   - 레인 1 `c489ac0` + media-library 명세: 전후 ID 집합 동일 + `_GroupMediaAssetItem {…}` 재구성 행이 파싱 통과·신규 ID 0(오차단 0).
   - 레인 3 재발화 리플레이: `625f6a6` + `2a12d18` 판 명세 + WIP 1개 → `--base 9906931` exit ≠3 / 미지정 exit 3.
3. `make verify` 전 그룹 green + codex byte 미러 diff 0 + `ontology_gate` 4단 + 계수 3529 + q4 골든.

### 7-2 실측 결과 (2026-09-03 구현 — 스크래치 `git clone` 사본 · 수리 전 = `a782dcd` 판 실행기 · 수리 후 = 본 배치 · 동일 트리 전후 비교, 레인 당시 실측 건수와 무관 · `--python` = 대상 venv py3.14)

| 레인 | 트리 | 명세 | 수리 전 S₀ | 수리 후 S₁ | 판정 |
|---|---|---|---|---|---|
| 3 email-template | `9906931` | 라이브 `20260902-1842-…/design-spec.md` | exit 2 · 1건 {`0c3ee0342328` #593 `…/migrations/0001_initial.py`} | exit 0 · 0건 | S₁ = S₀ ∖ {`0c3ee0342328`} ✓ · 타 ID 소멸 0 |
| 2 notification-bc | `7b0befd` | 라이브 `20260902-1458-…/design-spec.md`(`empty …/migrations/__init__.py`) | exit 2 · 1건 {`3dc440496a29` #14} | exit 2 · 1건 {`3dc440496a29`} | 유지·건수 1 불변 ✓ |
| 1 media-library 원문 | `c489ac0` | 워크트리 `feat-fortune-reading/.dddjango/20260902-0128-…/design-spec.md` | exit 2 · 6건 {`0545691c4eac` #160 · `508cb023eceb` #392 · `749595497241` #376 · `8140c1c059f4` #329 · `992a5a0575bf` #332 · `cc49ccf434d0` #484} | exit 2 · 6건(동일) | 전후 ID 집합 동일 ✓ |
| 1 media-library 재구성 | `c489ac0` | 위 명세 + `…/list_group_media_assets_result.py::_GroupMediaAssetItem {id: UUID, kind: str}` 행 삽입 | — | exit 2 · 6건(원문과 집합 동일) | 사설 타입 행 파싱 통과·신규 ID 0(오차단 0) ✓ |
| 3 재발화 리플레이 | `625f6a6` + 미추적 WIP `…/email_notice_template/__init__.py` | `2a12d18` 판 명세(add 20건 중 7건이 트리 실존) | — | `--base 9906931` → exit 0 · 실체화 30 · 기실현 1 / 미지정 → exit 3(add 충돌 `email_notice_template_content.py`) | 재발화 판형 ✓ · 기본 경로 불변 ✓ |

- 픽스처 러너: 묶음 base(green·green2·form-red·red — 헤더 4) · p1(green3 exit 0 · red2 exit 2 귀속 {#81, #325} 2건 — 헤더 각 1) · mid(E1 exit 0·사본 스텁·기실현 0 / E2 exit 0·기실현 1·스텁 대체(실물 #267 미혼입) / E3 exit 3 / E4 exit 3 — 헤더 4) + 유닛(파서 7케이스·compile 힌트·마이그레이션 정형 3파일 `_check_migration_file` Findings 0·전사 우선·블록 해시 4단언+CLI 동치·버전 probe Claude/Codex 레이아웃 동치·툴체인 행 형식) PASS.
- 계수 실측: ExpressionShape 3522→**3529**(+7) · BlockShape 2896→**2897**(s006/b10) · Norm/Work 3447 불변 · q4 골든 3438/3438 불변 · LEDGER graph 절 rebaseline +6(command-dddjango s005·s006·s007·s009·s010 · agent-design-architect s005) · ISSUED 무변경.
- 계획과 달라진 점: **s006/b10 은 `statesNorm` 없는 후속 블록**이다 — rulepack 생성기(`ontology_rulepack.py`)의 «1 Work = 1 Block» 계약(q4 주석·fail-closed)상 R-3432 를 b9·b10 둘이 진술할 수 없고 ISSUED 무변경 조건상 신규 채번도 불가하므로, R-3432(rev2 Expression)는 b9 에 남기고 b10 은 같은 문단의 속행(문서 내 선례 s010/b7 — statesNorm 없는 kind-norm 블록 45건)으로 뒀다. 렌더·계수(+1)·LEDGER 는 계획대로.
4. 5단계 입력: §0 표의 코드 지점 ↔ diff 헝크 1:1 대조표 첨부.

## 8. 배포·이월
- 릴리즈 v2.17.16(관찰 모드 유지) — **릴리즈 시점은 사용자 결정 게이트**(reading 레인 진행 중 codex 캐시 교체 위험). 판별: 사각 목록 7행·skip 행·게이트 헤더 «툴체인» 행.
- 이월: `--print-toolchain` · 소급 명세 픽스처 편입 · `abc.ABC`/다중 base · update 시뮬레이션.

---

# Part 2 — 대형 A: registry_gate 귀속의 병렬 머지 유입 사각 수리 (provenance 차분)

- 스코프: `registry_gate.py`·`anchor_diff.py`에 «발주자 승인 머지 목록 + provenance 차분» 채널 신설 + 상호작용 위반 별도 채널 + 앵커·first-parent 사슬 진단 + 규범 리비전(신규 3·amendment 4·clarification 2·s002 블록 1) + 스모크 확장 P0~P8. **비범위(§9)**: 레인 경로 필터 · 자동 재앵커(epoch) · 라인 단위(blame) provenance · 직접 실행 계열 5종 확장 · 앵커 비조상 exit 승격.
- **병합 순서 결정(통합자)**: Part 1 선머지 유지. Part 1 ③의 툴체인 헤더 digest 행은 스크립트 트리가 바뀌면 값이 바뀌므로, 본 Part의 P0 «수리 전/후 byte 동일» 비교는 **툴체인 행의 digest 값을 마스킹한 정규화 출력**으로 수행한다(양 Part 근거 동시 충족). ③ 픽스처는 헤더를 정규식으로 단언·A 스모크는 관계 검사만.

## 1. 원인 확정 (코드 지점 · 3사례 실측)

| 계통 | 실측 | 원인(코드 지점) |
|---|---|---|
| accounts 804(STOP-E) | 앵커 `03f8252` · 발주자 머지 `a000cd6`(부모 `88749ba`,`1f1667e`)가 `framework/technology/rag/**` py 18→34 · 머지 직전 귀속 0 → 직후 804(`#493` 단일). 실측: `git diff --name-only a000cd6^1 a000cd6 -- framework/technology/rag` = **341 파일, 341/341이 `blob(M)==blob(M^2)`**(충돌 해소 0) | `registry_gate.py:355` `attributed = sorted(n_set - l_set)` — 차분의 유일 변수가 앵커 한 커밋이라 «누가 넣었든» 앵커 이후면 귀속. 유일 감산 채널은 `:359-365` 빚 매칭뿐 — 타 레인 804줄을 «이 BC의 빚»으로 등재할 수 없어 코디네이터가 ⓓ(sed/grep 경로 분류)를 발명 |
| fortune-reading anchor-drift 463(#416 포함) | 앵커 `b5392f0` · first-parent 머지 3건 `7fd0433`·`d5d6d94`·`d892894`. `#493` 462 = 9파일 — provenance 실측: **5파일(349줄)은 `d892894`, 4파일(113줄)은 `d5d6d94`** 경유(전건 blob 3중 일치) — STOP 기록의 «전건 d892894»는 부정확. `#416` 1 = `yeonhae_release.py` blob 앵커=HEAD 동일, `application/promotion`은 `d5d6d94`에서 유입 | 같은 지점 + 파일 무변인데 검사기 환경(BC 어휘 집합)이 바뀐 «상호작용 위반»을 도구가 구별할 어휘가 없음 → 발주자가 R-0309(앵커 재기록 금지)를 ad hoc 개정(epoch A)해야 했음 |
| kkebi identity web-login 4건 | 앵커 `a1a254a` · tip `c2b2bfd`는 main `e57490b` 위에 얹힘. first-parent 사슬: **비머지 main 직접 커밋 4 + 머지 7 + 레인 커밋 4**. 4건 중 `#546` consultation은 `0b2b436` blob 3중 일치, `#493 web/home/urls.py`는 `f2a66a8` 3중 일치. `#493 settings/base.py` 2건은 **레인이 같은 파일을 수정**, `_s3_bucket_name`은 main 직접 커밋 `e219608` 유입 | 앵커가 레인 분기점보다 앞선 «앵커 조상 문제». 도구는 앵커가 HEAD의 조상인지·사슬 구성을 진단하지 않음(`:330-341`은 resolve·공허만 검사). (1단계 C의 «20머지» 수치는 본 실측(머지 7+직접 4)과 다름 — 5단계에서 산정 기준 대조) |

## 2. 변경 — 실행기 (`registry_gate.py` · `anchor_diff.py` + codex byte 미러)

### 2.1 판정식
귀속(N∖L)에서 빚 매칭을 뺀 나머지 각 라인 ℓ(파일 p·검사기 c)에 대해, 승인 머지 집합 𝓜가 주어졌을 때:

> **승인 유입(ℓ) ⟺ W(p) ∧ (F1(p) ∨ F2(p)) ∧ L(ℓ)**
> - W: worktree의 p가 HEAD와 동일(`git status --porcelain -- p` 공백)
> - F1(파일 유입): ∃M∈𝓜: `blob(M^1:p) ≠ blob(M:p)` ∧ `blob(M:p) == blob(M^2:p) == blob(HEAD:p)` — 승인 머지의 incoming 측에서 verbatim 전달·레인 미수정(충돌 해소분은 `M≠M^2`라 탈락)
> - F2(파일 무변 = 상호작용 서명): `blob(HEAD:p) == blob(anchor:p)`
> - L(원인 증명): ∃M∈𝓜: ℓ ∈ R_c(M^2) ∖ R_c(M^1) — 검사기 c를 M^2(incoming)·M^1(레인 측) 스냅숏에서 재실행해 «incoming 측에는 있고 레인 측 직전에는 없던» 진단임을 증명

네 조건 전부 통과한 라인만 exit에서 빠지며, 판정 불능(레코드 없음·비-blob·스냅숏 실패)이면 귀속 유지(fail-closed). **L 없는 blob-only 설계는 기각** — 반례: 레인이 BC `promotion`을 신설하고 승인 머지가 리터럴 `"promotion"`을 가진 파일 q를 verbatim 들여오면 q의 `#416`은 F1 통과하나 원인은 레인의 BC. L은 M^2(레인 BC 부재)에서 그 진단이 안 나므로 귀속 유지(P6). `R(M)∖R(M^1)` 대신 `R(M^2)∖R(M^1)`인 이유가 이 반례 — R(M)은 레인 측 산출물을 포함해 이중 원인을 못 가림.

### 2.2 함수 단위 변경
`anchor_diff.py`: ① `APPROVED_MERGE_FLAG = "--approved-merge-file"`(`DEBT_FLAG :52` 옆). ② `load_approved_merges(path, root, anchor_sha, head_sha) -> list[ApprovedMerge]` — 줄 형식 `<SHA> [메모]`·`//` 주석(`load_debt :159-177` 동형). 검증(fail-closed → `AnchorDiffUsage` exit 1): ⓐ `rev-parse --verify <sha>^{commit}` ⓑ 부모 정확히 2 ⓒ `git rev-list --first-parent <anchor>..HEAD` 사슬 위 존재. ⓓ `merge-base --is-ancestor M anchor` 참이면 «앵커 이전 — 판정 불참»으로 제외(epoch 넘긴 목록 허용). 반환: `sha, parent1, parent2, subject, position`.
`registry_gate.py`: ③ argparse `--approved-merge-file`(`:275` 옆) — 비-git TARGET 병용 시 exit 1. ④ `_run_registry(…, only: frozenset[str] | None = None)` — 지정 검사기만 실행(`:135`). ⑤ `_tree_blobs(root, sha)` — `git ls-tree -r` 1회 경로→blob 사전(SHA 캐시). ⑥ `_line_paths(attributed, records, prefixes)` — `_write_introduced :175-188`과 같은 키 매칭(`findings.line_of_record` → `_normalize`)으로 라인↔레코드를 잇고 `file` 필드에서 p 추출. 레코드 없음·`(target)`·디렉터리·미추적 → `None`(귀속 유지). ⑦ `_provenance_split(root, anchor_sha, head_sha, merges, attributed, records, prefixes, td) -> ProvenanceResult` — (i) 경로 (ii) W·F1·F2 blob 판정 (iii) 후보 라인의 검사기 집합 C만 `anchor_diff.snapshot_anchor`로 필요한 스냅숏을 풀고 `_run_registry(snap, only=C)` → R_c(M^1)·R_c(M^2) 캐시 (iv) L 탐색: F1은 전달 머지 먼저, 다음 first-parent 순; F2는 first-parent 순 — 첫 적중 중단 (v) 후보 0이면 스냅숏 0. 결과: `inflow[(line, merge_sha, kind∈{파일,상호작용})]`, `retained{line: reason}`(사유 어휘: `레코드 없음`·`비-blob 경로`·`worktree 수정 중`·`레인 커밋 수정`·`충돌 해소분(M≠M^2)`·`미승인 머지 경유 <sha>`·`직접 커밋 경유 <sha>`·`상호작용 미증명`·`유입 증명 실패(R 측정 실패|이중 원인)`), `chain` 통계. ⑧ `main()` 순서: attributed(:355) → 빚 분리(무변) → provenance 분리(flag 시) → 출력; attributed 잔여 = exit 근거. ⑨ 출력(flag 시만 추가 — 없으면 현행 byte 동일): 귀속 라인 아래 `↳ 귀속 유지: <사유>` 보조 행 / `== 승인 유입(발주자 승인 머지 경유 · provenance 증명 — exit 제외·기록 의무) N건 ==` 머지 표(`[M sha12] <subject> · ^1 · ^2 · 파일 n · 상호작용 m` — 역방향 머지 오기입 가시화) + 라인마다 `↳ 유입: M · 파일 verbatim|상호작용` / `== provenance 진단 ==` 사슬 통계 + 「비머지 커밋이 첫 승인 머지보다 앞서면 앵커가 분기점보다 앞선다 — epoch 재앵커는 발주자 결정」 / `판정:` 행 형식 유지·`(승인 유입 N건 제외)` 꼬리. ⑩ 상시 진단 1건(병리 시만 발화): `merge-base --is-ancestor <anchor> HEAD` 거짓이면 `주의: 앵커 … HEAD의 조상이 아니다` — **exit 무변**(승격은 별도 결정 게이트). ⑪ sidecar `_write_introduced`: `attributed_lines`·`records`는 잔여만; flag 시 `"provenance": {approved_merges, inflow_lines, retained_reasons, chain}` 추가(스키마 `gate-introduced/0` 유지·flag 없으면 payload byte 동일). ⑫ exit 규약: 0/2 의미 무변; 신규 exit 1 사유 = 목록 파일 부재·형식/resolve/비머지/사슬 밖·비-git 병용.

### 2.3 비용
blob 판정은 ls-tree 사전만(머지 수 선형·수 초). L은 «후보 라인 검사기 × 관련 스냅숏»만 — accounts 스냅숏 2+검사기 2회, anchor-drift 최대 스냅숏 6+검사기 ≤12회. 후보 0이면 0.

## 3. 변경 — 규범 (그래프 리비전)
1. **R-0306 rev2(amendment)** «게이트 증거 = 귀속 0 + legacy 잔존 별도 보고» → «… + `approved-merges.txt`가 있으면 `--approved-merge-file` 동반, provenance 증명으로 분리된 **승인 유입은 exit 제외·별도 보고(기록 의무·즉석 수리 금지)** + **상호작용 위반(파일 무변·미증명)은 귀속 유지·별도 표기**». **R-3131 rev2** 동문(houserules §1 — `discipline-houserules-skill.ttl:806`).
2. **신규 R-NEXT+0(Obligation · s007/b12 인접)** — «Phase 2 중 main→레인 머지는 발주자 승인 사안. 승인 머지 SHA를 **발주자가 머지 승인 시점에** `<산출물 폴더>/approved-merges.txt`에 append(`<SHA> [메모]`). 코디네이터·실행자는 이 파일을 쓰지 않는다(앵커를 actor가 고르지 않는 것과 같은 이유 — 자기 세탁 차단). 역방향 머지·squash·rebase는 등재 대상 아님(게이트가 subject·부모를 표기해 가시화)».
3. **신규 R-NEXT+1(Obligation)** — 코디네이터: 파일이 있으면 registry_gate 실행에 동반(있는데 안 주면 증거 불비)·G2 배너에 «승인 유입 N건(머지 SHA 열거)» 별도 항목 → **R-0411 rev2(amendment)** «legacy 잔존 별도 보고 항목»에 «승인 유입도 별도 항목».
4. **신규 R-NEXT+2(Exception — R-0310/R-3133 «스코프 밖 귀속 1차 처방=철회»에 대한)** — «승인 유입은 레인의 변경이 아니므로 철회 대상 아님. 파일 무변 귀속(상호작용 미증명)은 철회할 변경이 없다 — 1차 처방은 `STOP_FOR_USER_APPROVAL`(빚 등재 또는 상류 소유 레인 해소)이며 게이트의 `↳ 귀속 유지: 상호작용 미증명` 표기를 STOP에 인용».
5. **R-0307 rev2·R-3132 rev2(clarification)** — «좁힌 TARGET green은 증거 아님»에 «**귀속 목록을 경로 필터(sed/grep)로 나눈 서술도 게이트 증거가 아니다** — 유입 분리는 provenance 채널만(STOP-E ⓓ 관행 폐기)».
6. **s002 산출물 위치 새 블록(b9)** — `approved-merges.txt`(발주자 소유·머지 승인 시 append·코디네이터 무기록).
7. **R-0372 rev2(amendment · 실행·종료 계약 ⓑ)** — «귀속 red만 blocker·legacy 잔존·**승인 유입**은 별도 보고 의무».
8. R-0309·R-0304·R-0305 **무변** — provenance 채널이 머지 유입형에서 epoch 재앵커 압력을 없애 불변식이 오히려 지켜짐.
절차: `ontology/ISSUED` append(다음 번호 — Part 1과 채번 경합 시 후행 착지자가 다음 번호) → 4단 게이트 → `--apply command-dddjango discipline-houserules-skill` → `make rulepack` → codex SKILL 재투영 → 계수표 갱신. graph-owned만 → LEDGER 무변.

## 4. 무손실 증명 (검출 집합 단조성 · 픽스처)
원리: 새 코드는 «감산»이 아니라 «분할» — `N∖L` = 빚 ⊔ 승인 유입 ⊔ 귀속(잔여). 어떤 라인도 인쇄되지 않는 채널로 가지 않음. exit에서 빠지는 유일한 새 경로는 «발주자 소유 파일 ∧ blob 3중 일치 ∧ R(M^2)∖R(M^1) 증명» — 빚 채널과 같은 «사용자 승인 입력» 부류.
픽스처: `workspace/tools/registry_gate_smoke.py` 확장(기존 8케이스 무변). 재료 `skeleton/good_bc` + `_VIOLATION_SRC`. 격리 git 사본은 tempdir·고정 `GIT_*_DATE`(결정적 SHA). 골격 «A(앵커) → lane 커밋 → main 위반 커밋 → lane에서 `git merge main`(M) → 판정».

| 케이스 | 구성 | 기대 |
|---|---|---|
| **P0 회귀** | flag 없이 실행 | 현행 판형(귀속 3·exit 2). 수리 전 사본 실행과 정규화(digest 마스킹) 출력 diff 0. 상시 스모크: «flag 없는 출력에 새 절 제목 3종 부재» + «flag 유/무의 legacy·해소 절 동일·(귀속∪승인 유입) 집합 동일» |
| **P1 승인 유입** | 목록 = {M} | 유입 3(파일)·귀속 0·exit 0·sidecar `attributed_lines`=[] |
| **P2 blob 불일치** | 머지 뒤 lane이 위반 파일 수정 | 귀속 3·사유 `레인 커밋 수정`/`worktree 수정 중`·exit 2 |
| **P2′ 충돌 해소분** | 양쪽 수정 → 충돌 해소 M | 귀속 유지·`충돌 해소분(M≠M^2)` |
| **P3 미승인/무효** | ⓐ 빈 목록 ⓑ 비머지 SHA ⓒ 사슬 밖 ⓓ 앵커 이전 머지 | ⓐ 귀속 3·`미승인 머지 경유 M`·exit 2 ⓑⓒ exit 1 ⓓ «판정 불참»·귀속 3 |
| **P4 상호작용 승인 유입** | 앵커에 `framework/redis/redis_cache.py`(`activation_type: str = "promotion"`), main이 `application/promotion/` 추가 → M | `#416` 1 = 승인 유입(상호작용)·귀속 0·exit 0 |
| **P4′ 상호작용 미증명** | P4에서 목록 비움 | 귀속 1·`상호작용 미증명`·exit 2 |
| **P5 kkebi형(직접 커밋)** | main이 위반 파일 직접 커밋, lane을 그 뒤에서 분기 | 귀속 3·`직접 커밋 경유 X`·진단 «비머지 커밋 1이 첫 승인 머지보다 앞섬»·exit 2 |
| **P6 이중 원인(L 필요성)** | lane이 `application/promotion/` 신설, main이 `"promotion"` 리터럴 파일 추가 → M 승인 | F1 통과·L 실패 → 귀속 1·`유입 증명 실패(이중 원인)`·exit 2 |
| **P7 빚+유입 공존** | P1 + 빚 파일 `#95` | `#95` 빚 절, 나머지 2 승인 유입(빚 우선) |
| **P8 앵커 비조상** | 앵커를 무관 가지로 | «주의: 앵커 … 조상이 아니다» 1행·exit 현행 |

3사례 결정적 재현(스크래치 `git clone --shared` → 지정 커밋 checkout·라이브 무접촉):

| 사례 | 좌표 | 승인 목록 | 기대 출력 |
|---|---|---|---|
| accounts(STOP 시점) | SD 사본 HEAD=`a000cd6` · `--anchor 03f8252` · 빚 동일 | `a000cd6` | 유입(파일) **804**·귀속 **0**·빚 14·**exit 0** |
| accounts(레인 tip) | HEAD=`b6e98bd` | first-parent 머지 39건 | 유입 N·귀속 0·exit 0(N은 재현 시 확정) |
| anchor-drift | HEAD=`99b3caa` · `--anchor b5392f0` | `7fd0433`·`d5d6d94`·`d892894` | 유입(파일) **462**(d892894 349·d5d6d94 113)·유입(상호작용) **1**(#416←d5d6d94)·귀속 **0**·**exit 0** → epoch 재앵커 불요. 목록이 `d892894`뿐이면 유입 349·귀속 114·exit 2 |
| kkebi identity | kkebi 사본 HEAD=`c2b2bfd` · `--anchor a1a254a` · 빚에서 «범위 밖 4건» 제거 | 7머지 | 유입(파일) **2**·귀속 **2**(`settings/base.py` — `레인 커밋 수정`)·**exit 2**·진단 «비머지 4가 첫 승인 머지보다 앞섬». 잔여 2건은 현행 빚 STOP(결정적 사유 인용) |

## 5. 코퍼스 정합
- 규칙: R-0306·R-3131(amendment) · R-0307·R-3132(clarification) · R-0411·R-0372(amendment) · 신규 3 · s002 b9. R-0303(판정 차분) — 귀속 산식 무변(분할만) 무충돌. R-0309 — 강화. R-0310/R-3133 — Exception이 «변경 없는 귀속»에 한정·본체 약화 없음. R-0373(exit 1 = 측정 실패) — 신규 exit 1 사유 동류. R-0374/R-0376 — 승인 유입에도 즉석 수리 금지 동반. 검사기 27종·rulepack selector 무변.
- 머리말 §5~10 «경로 매칭식 5계열 공격»과의 정합: ① base 자기 선택 — 앵커·승인 목록 모두 actor 밖·사슬 검증 ② #488 부재 — blob 없는 경로 귀속 유지 ③ 출력 형식 이질 — `findings` 레코드 단일 출처·대응 없으면 귀속 유지 ④ 빈 변경 집합 — 변경 집합 비사용·L이 incoming 존재 요구 ⑤ .gitignore — 커밋 blob 없으면 불성립. 머리말에 «provenance 차분 — 귀속의 분할이지 재정의가 아니다» 절 추가.
- «판정 차분» 논증: 승인 유입은 정의상 이번 런의 변경이 아니며, 그 판정을 코디네이터 서술이 아니라 게이트의 결정적 증명으로 옮김 — R-0306 정신 유지하며 STOP-E ⓓ 폐기하는 유일 형태.

## 6. 일반화
입력은 git 오브젝트와 평문 SHA 목록뿐 — 발주서·herdr·STOP·브랜치명 무의존. Claude/Codex 동일. 표본 외: kkebi identity(유입 2·귀속 2) + kkebi `STOP-s6`(#308/#310 레인 신작 — 목록 있어도 F1/F2 불성립 → 귀속 유지·진짜 검출 보존). 한계: 직접 커밋·역방향 머지·라인 단위는 비범위 — 진단 표면화만.

## 7. 검증 게이트
1. 스모크 P0~P8 green(기존 8 무변) — `verify-base-cross` 등록. 2. P0 정규화 byte 동일 증거. 3. `make verify` 전건(4단 게이트·렌더 동기·`derive_path_globs --check`·`ontology_rulepack --check`·`diff -rq` scripts 양쪽·`manifest_seal --check --draft`). 4. 봉인 재발행(`anchor_diff.py` measurement·`registry_gate.py`·commands·codex SKILL·skills md). 5. `make verify-mutation`. 6. 3사례 재현 결과 ↔ §4 표 대조(불일치 = 구현 드리프트). 7. 종점: 다음 병렬 레인에서 `approved-merges.txt` 운용 실측.

## 8. 이월·비범위(명시)
레인 경로 필터(금지 성문) · 자동 재앵커 · 라인 단위 provenance · 직접 실행 계열 채택 · 앵커 비조상 exit 승격(별도 결정 게이트) · 상호작용 미증명분의 exit 제외(채택 안 함 — 이중 원인 배제 불가). 사각: git-touched 판정 검사기는 스냅숏에서 대칭 붕괴 가능 → L 실패 시 귀속 유지 · 역방향 머지 등재는 도구 구별 불가(발주자 소유·subject 표기로 가시화).

---

# Part 3 — 대형 B: pre-gate boundary-imports «계약 실존» 3단 검사 (R-3427 확장)

- 스코프: 실행기 1채널 신설(읽기 전용 판정) + 규범 amendment 5건(신규 채번 0) + 픽스처/러너 확장 + 설계 v3→v4·ledger 산문 정합. **관찰 모드 유지(권고·비차단)**.
- 격리 재현(09-03·스크래치): 3단 해소 프로토타입을 픽스처 3종·media-library 실명세(28행)·notification 실명세(22행)에 적용 → **결손 0 / 서드파티 skip 20·8 / 자기 add 해소 10·12 / 실존 확인 1·5**. 오차단 0의 필수 조건 2개 실측 확정: ⓐ `from <패키지> import <서브모듈>` 행은 서브모듈 우선 해소 ⓑ 자기 add 대상의 이름 판정(⑶)은 생략(symbols 문법이 모듈 상수·재수출을 표현 못 함).

## 1. 원인 확정
| 계통 | 실측 | 원인 |
|---|---|---|
| SD형 — 상류 모듈 부재 | fortune-reading 개시 9분 STOP + G1 전 STOP. `9b354fb^`의 `application/`에 `fortune_calculation` 없음(0) · `138359f`(09-01 17:02)엔 있음 | pre-gate는 R-3427 채널을 **스텁 전사 재료로만** 소비(`_parse_imports` :410~431 → `entry.imports` → `render_stub` :615~620) — import **대상** 실존은 어디서도 안 봄. 검사기 27종도 import를 «경로 모양»으로만 판정(`check-context-isolation.py:182~200` — 부재 규칙 0). 부재는 사람이 STOP으로 찾거나(SD 5.5분) ImportError로 드러남(kkebi 144분) |
| kkebi형 — 0B 자리표시자 | `STOP-s2-s3.md`(S1 @`dd876b7`): `profile_lookup_published_error.py`·`account_lookup_published_error.py` **0B 실측** → S2 착수 조건 미충족. 41호 병합 후 `5af8bb6` 137B → 재개. 현재 kkebi 0B `.py` 1,181(비-`__init__` 161) | 「파일은 있으나 계약이 비어 있음」은 `checker_target.skeleton_placeholder` 술어가 이미 정의하지만 pre-gate가 안 씀 |
| 교차-워크트리 오판 | kkebi `STOP-365-identity-acl.md`: identity가 다른 워크트리라 #365가 «저장소 밖 계약»으로 오판 | 검사기는 타 워크트리를 모름 — 이 브랜치 기준 부재가 사실. 새 검사는 «**이 브랜치에 이 계약 모듈 없음**»으로 정직 명명 |
시간 절감 수치는 주장하지 않음 — 기대 효과는 «kkebi형 0B/ImportError 반송 사전화·SD형 분 단위» 그대로.

## 2. 변경 — 실행기 (`design_pregate.py` + codex byte 미러)
원칙: **기존 경로(파서 결합·`render_stub`·`materialize`·`run_gate`·`_stable_id`)는 한 줄도 바꾸지 않는다** — 신설은 읽기 전용 판정 함수군 + 리포트/exit 배선뿐.
### 2.1 파서 — 행 보존
`Plan.import_rows: list[ImportRow(consumer, stmt)]` 추가. `_IMPORT_ROW_RE` 통과 행은 소비 파일 태그·등재 여부와 무관하게 전부 보존한 뒤 기존 분기 유지. 근거: kkebi S2 소비자는 기존 어댑터 **update** — 실존 판정은 «대상»의 문제. 메모 문면만 «스텁 미반영(… — 실존 판정에는 포함)»으로 조정.
### 2.2 신설 «계약 실존 — 3단 판정» 함수군
- `_repo_root_packages()`: `standard_tree.children(None)` depth-0 → `{application, framework}`(하드코딩 아님).
- `_is_repo_target(copy, top, plan)`: 최상위 패키지 ∨ 사본 실존 ∨ file-plan 첫 세그먼트. 거짓 = «저장소 밖 — 검사 밖» 계수만.
- `_realize_module(copy, parts, plan)` → `planned-add | planned-empty | package | module | namespace-dir | missing`(file-plan 조회 → `__init__.py` → `.py` → 디렉터리 → missing). planned-remove 대상은 자연히 missing.
- `_top_level_names(path)`: ClassDef/FunctionDef/Assign/AnnAssign/Import alias(`asname or name` — 승격 폴더 재수출 인정)/`__all__`; 최상위 If/Try/With 재귀(`TYPE_CHECKING`·try-import 관용). SyntaxError → None(판정 불능).
- `check_import_existence(copy, plan) -> ExistenceReport`: `ast.parse(stmt)` → `import a.b.c`는 ⑴⑵ / `from M import n…`(level>0은 소비 파일 기준 상대 해소 — `_resolve_relative` 동식)은 이름마다 서브모듈 우선 → ⑴ missing=«모듈 부재» ⑵ `skeleton_placeholder`(0B·공백·주석/docstring-only — #256/#351/#114와 같은 술어·재구현 금지)=«자리표시자»(부가: 자기 `empty`/골격 빈 칸/기존 실물) ⑶ 이름 미바인딩=«심볼 미정의». **planned-add 대상은 ⑴⑵⑶ 생략·«자기 add 해소» 계수**. `*`는 판정 밖 메모. 집계: 행 R·이름 판정 T·실존 확인 K·자기 add S·저장소 밖 X·판정 불능 U + 결손 목록((모듈,이름) 쌍 합치기·소비자 병기).
- `_existence_id(module, name) = "e-" + sha256(f"{module}+{name}")[:12]` — 단계는 키에 넣지 않음(⑴→⑵→해소에도 ID 유지). 접두 `e-`로 기존 12hex ID·러너 `_FORECAST_RULE_RE`와 절대 불충돌.
- `BLIND_SPOTS` +2행(이 브랜치 사본 기준·타 워크트리 미조회 / 동적 import·`import *`·저장소 밖·파싱 실패).
### 2.3 리포트 절(예보 항목과 already-built 사이 상시 절 — 행 0이어도 출력)
`### 계약 실존 (boundary-imports 3단 · 결손 M건 · 안정 ID = e-…)` — 항목 `- \`e-…\` ⑴ 모듈 부재 :: <모듈> import <이름> ← 소비 <파일>` / 집계 행 / 판정 불능(U>0) / 결손 0이면 «(없음) — 전건 실존(저장소 밖 X·자기 add S)». 헤더 `- 판정:`에 ` · 계약 실존 결손 M건(권고·비차단)`. stdout에 `== 계약 실존 결손 M건 ==` 블록 + 배너 재료 1행 `요약: 귀속 N건 · 실존 결손 M건 · 기준선 <sha12> · 모드 관찰`.
### 2.4 채널 구분 — 예보 항목과 **합치지 않는다**
예보 ID는 registry 규칙 귀속이고 §8 판정식은 «P/S/I ∩ G2 귀속». 실존 결손은 어떤 registry 규칙도 판정하지 않아 G2가 귀속 못 함 — 섞으면 «G2 미귀속 red = 오탐» 오계상·라벨 오용(발견 ① 재생산). 별도 절·ID·계수가 판정식 보전의 유일 형태. 러너 red 정규식·ledger «귀속 예보» 열 무변.
### 2.5 exit — **별도 코드 5**
| 상황 | exit |
|---|---|
| 귀속 0·결손 0 | 0 |
| 귀속 ≥1 | 2(결손은 병기) |
| 형식 red | 3 |
| 블록 부재 skip / 실체화 0·결손 0 | 4 |
| **결손 ≥1 ∧ (귀속 0 ∨ 실체화 0)** | **5**(신설 — `write_report_stub`도 결손 목록 탑재) |
| 실행 불능 | 1 |
exit 2 공유 기각 근거: ⓐ 차단 승격이 «exit 2 = 차단»이라 공유하면 승격과 동시에 실존 결손이 자동 차단(G0 하드 검사 재현 — 1단계 기각 방향) ⓑ ledger «귀속 예보 red» 계수가 exit 2와 결속. 실존 채널 차단 여부는 별도 결정 게이트(§10 이월).
### 2.6 docstring — 기계 블록 정본 문법 절에 실존 의미론·exit 5 추기(규범 개정과 같은 커밋).

## 3. 변경 — 규범(amendment 5·신규 채번 0·산문 3)
1. **R-3427 rev2**(architect s005/b36 `:2093~2098`) — «각 행은 실행기가 격리 사본에서 3단 실존 판정을 받는다 — 저장소 밖 검사 밖·자기 add 자기 해소. 판정 기준은 **이 브랜치** — 타 워크트리·미머지 브랜치 미조회. 상류 소유 계약을 소비할 계획이면 그 행을 **그대로 적는다** — 결손 예보가 선행 조건의 기계 표현이며, 행을 빼서 green을 만드는 것은 채널 은폐(전수 의무 위반)».
2. **R-3433 rev3**(Coordinator s006/b9) — 채널 한정 처분: «**계약 실존 결손의 처분 라벨은 `corrected | deferred | filtered`** — corrected=개정 해소(다음 실행 소멸) · deferred(선행 대기)=결손 대상이 상류 레인/후행 슬라이스 소유임을 명세가 명시하고 해소 조건(소유 레인·머지 커밋 또는 슬라이스 번호) 병기 — 증거는 조건 충족 시점 재실행 소멸 · filtered=도구 한계(근거 병기). **`ignored`는 이 채널에 없다** — 부재는 ImportError 예약이며 G2 귀속·legacy-debt 어느 증거도 성립 안 함. 실존 채널은 승격 판정식의 **입력이 아니다** — 별도 계수. 결손은 권고 — 선행 대기가 발주자 사안이면 STOP 규약(R-0459/R-0460)대로 상신». 기존 3라벨 문장은 «예보 항목(registry 귀속)의 처분 라벨은…»으로 주어 한정.
3. **R-3434 rev2** — 비대체 목록에 «계약 실존 채널은 G0 선행 조건 확인·상류 머지 판단(발주자 소관)을 대체하지 않는다 — 하드 검사 아님»(1단계 항목 1 기각의 성문 고정).
4. **R-3437 rev2**(s003/b10) — 배너 1행 `pre-gate: 귀속 N건 · 실존 결손 M건 · 커버 P/S/I · 기준선 <SHA>`(실체화 0·결손 M>0이면 `실체화 0 · 실존 결손 M건`).
5. **R-3438 rev2**(s002 `:2913`) — pregate-report 문면에 «계약 실존 절(자체 ID `e-…`·채널 한정 라벨)» 추기.
6. 산문: 설계 v3→**v4**(§3-D4 채널 절·ID·라벨 / §8 «실존 채널 비입력·별도 계수·차단 여부 별도 게이트» / §1 비목표 «타 워크트리 조회») · ledger 헤더 동기 + 총괄 표 «실존 결손/처분» 열(레인 1~3 «채널 부재») · codex 손 미러 2건(SKILL.md pre-gate 문단·배너·산출물 / architect SKILL :84).
7. 봉인 재발행(commands·agents·codex SKILL 2건). `design_pregate.py`는 봉인 밖.

## 4. 무손실 증명
1. **구조적**: 신설 = `Plan.import_rows` + 읽기 전용 함수군 + 배선. `render_stub`·`_class_stub`·`materialize`·`run_gate`·`_stable_id`·`BASE_IMPORTS`·`parse_spec` 결합 분기 **diff 0**(5단계 `git diff -U0` 함수 단위 확인) → 스텁 byte 불변 → 귀속·ID 불변.
2. **소급 대조**: ⓐ notification — `git show 7b0befd:.dddjango/20260902-1458-notification-bc/design-spec.md` + 기준선 `1eb8507` → 예보 ID 집합 diff 0(`3dc440496a29` 1건)·결손 0(자기 add 12·실존 5·저장소 밖 8)·exit 2 동일 ⓑ media-library — 명세(읽기) + `c489ac0` → ID diff 0·결손 0(저장소 밖 20·자기 add 10·실존 1 `FrameworkErrorSchema`). 두 실명세가 exit 5로 바뀌지 않음(오차단 0 실전 증거). (지시문의 `fixtures/pregate/notification-design-spec.md`는 저장소에 없음 — 출처는 워크트리 히스토리.)
3. **기존 픽스처 4종·`mini_repo` 무변경**(한 byte도).
4. **신규 픽스처**: 유닛 매트릭스 ⓐ~ⓟ(실존 확인·⑶ 미정의·⑵ 0B·⑵ docstring-only·⑴ 부재·자기 add 해소(⑶ 생략)·자기 `empty`·승격 폴더 재수출·서브모듈 형·서드파티 skip·`framework.*` 부재 ⑴·`import a.b.c`·상대 import·`import *` 불능·planned-remove ⑴·ID 안정성) + e2e 3종(합성 저장소 2 = `mini_repo` + `imports_overlay/`(`framework/test/frozen_clock.py`·0B `placeholder_helper.py`)): `imports-green-spec` exit 0 / `imports-red-spec` exit 5(⑴⑵⑶ 각 1) / `imports-update-only-spec` exit 5 + «실체화 0»(kkebi S2 판형). 러너 `_EXISTENCE_LINE_RE` 추가·append 계수 기대 갱신(**Part 1 green3와 합산 — §통합 참조**).
5. **게이트 강도 불변**: 완화 0 · 강화는 권고 채널 추가뿐 · exit 5 비차단 · 비-add 소비자의 문법 불량은 판정 불능 메모(형식 반송 계수 보호).

## 5. 사례 정합 — 당시 행이 있었다면
| 사례 | 기준선 | 기대 출력 |
|---|---|---|
| SD fortune-reading G1 전 | `9b354fb^` | `⑴ 모듈 부재 :: application.fortune_calculation.… import CalculateChartResponse` 1건 · exit 5(귀속 0 시) — 처분 `deferred`(소유 레인·해소=머지) → `138359f` 이후 소멸. #365와 상보(«저장소 밖?» vs «이 브랜치에 없음») |
| kkebi notification-settings-http S1 | `dd876b7` | `⑵ 자리표시자(0B — 기존 실물)` 2건 · «실체화 0 · 실존 결손 2건» exit 5 — S2 착수 조건의 기계 표현. `5af8bb6` 재실행 → 결손 0 = 재개 조건 기계 증거 |
| kkebi STOP-365 | `217d815` | `⑴ 모듈 부재` × 행 수(identity BC 전체) · `deferred` — #365 오판 문면 정정. #365 자체 불변(이월) |
적용 한정: 구형 명세(기계 블록 없음 — kkebi 0/20)는 R-3436대로 exit 4 — 신규·개정 명세 한정.

## 6. 정합 논증 — R-3134(닫힌 목록)·1단계 A MINOR 8
R-3134 주어는 «신규 산출물의 **형태**». 이 검사는 형태를 결정하지 않음 — 명세가 스스로 선언한 행의 참조 대상 실재만 boolean으로 반환. 같은 종류 관찰이 실행기에 이미 있음(`add 충돌(실존)` :779·registry 27종). → 닫힌 목록 밖 새 축 아님·목록 개정 불요. MINOR 8: 새 축은 «관찰이 대기를 **강제**할 때» — 이 계획은 대기를 도구가 만들지 않음(exit 5 비차단·R-3434 rev2 비대체·`deferred`는 명세가 소유 레인·조건 명시·발주자 사안은 STOP 규약). 재량 관찰이 되지 않는 성문 3건(R-3427 rev2 범위·R-3433 rev3 처분·R-3434 rev2 비대체)을 실행기와 **같은 릴리즈**에 묶음. R-3435(격리 사본 읽기만) 정합.

## 7. 코퍼스 정합 — 규칙 ID 전수
R-3427 rev2(확장·약화 없음) · R-3433 rev3(채널별 닫힌 정의·기존 3라벨 불변) · R-3434 rev2 · R-3437 rev2(필드 추가) · R-3438 rev2(절 추가) · 무변경 정합 확인: R-3424(fail-closed 동형)·R-3425·R-3426(자기 add ⑶ 생략 근거)·R-3432·R-3435·R-3436(실체화 0 분기만 «결손→5» 세분)·R-3134·R-0459/0460·registry #13/#385/#365/#472 · `checker_target.skeleton_placeholder`·`standard_tree.children(None)` 재사용(재구현 금지).

## 8. 일반화
의존: Python import 의미론·표준 트리 최상위·격리 사본. 무의존: herdr·STOP 규약·발주서·프로젝트명. 런타임 byte 미러 단일. 표본 외 ≥2(kkebi STOP-s2-s3 ⑵·STOP-365 ⑴) + SD ⑴ + 실명세 오차단 대조 2. 한정: 신규·개정 명세.

## 9. 검증 게이트
1. `pregate_fixture_run.py` PASS — 기존 4종 문자 동일 + 유닛 ⓐ~ⓟ + e2e 3종. 2. 소급 대조 2건(ID diff 0·결손 0·exit 불변) 표 추기. 3. 온톨로지 4단 → `--apply command-dddjango agent-design-architect` → rulepack → verify 전 단. 4. codex 미러 byte + SKILL 2건 손 반영. 5. 봉인 재발행. 6. 5단계 3축: «결합 분기 diff 0»·«자기 add ⑶ 생략»·«exit 5 비차단» 드리프트. 7. 종점: 다음 레인 ledger «실존 결손/처분» 열 실측.

## 10. 이월·비범위
비범위: G0 하드 검사·선행 조건 자동 STOP(R-3434 rev2로 봉인) · 타 워크트리 조회 · 발주 운영 권고 · #365 정밀화. 이월: 실존 채널 차단 승격(표본 ≥2 후 별도 게이트) · update 소비자 스텁 · 자기 add ⑶(symbols 문법 확장 선행) · 동적 import·`import *`·네임스페이스 이름 판정 · 캐시 skip 행에 «실존 결손 M건» 병기.

---

# 통합 — 교차 정합·병합 순서 (통합자 판정)

1. **병합 순서**: Part 1 → Part 2 → Part 3. Part 2·3은 파일이 분리되나(`registry_gate.py`/`anchor_diff.py` vs `design_pregate.py`) 규범은 `command-dddjango.ttl`을 셋 다 건드린다 — 공유 블록: **s006/b9(pre-gate 문단)** = Part 1 R-3432 rev2 + Part 3 R-3433 rev3·R-3434 rev2(같은 `djr:text`) · **s002** = Part 2 신규 b9(approved-merges) + Part 3 R-3438 rev2. 후행 Part는 선행 착지 후 그래프에서 rebase(Expression 사슬 rev 번호는 착지 순서로 확정).
2. **채번**: Part 2만 신규 규범 3건(ISSUED R-3439~3441 예정) — Part 1·3은 신규 0.
3. **픽스처 러너 계수**: Part 1(green3 +1·red2 +1·E 계열 별도 저장소) · Part 3(e2e 3 — 합성 저장소 2·별도 리포트 파일). 구현 시 **리포트 파일을 픽스처 묶음별로 분리**해 `header_count` 기대를 묶음별로 둔다(교차 오염 방지).
4. **P0 byte 동일 증거(Part 2)**: Part 1 ③ 툴체인 헤더 행의 digest 값 마스킹 후 비교.
5. **exit 코드 성문**: Part 3의 exit 5 신설은 Coordinator/설계 문서의 exit 열거(«0/2/3/4/1»)를 찾아 전부 갱신해야 한다 — 3단계 코퍼스 정합 리뷰 지정 항목.
6. **1단계 C 수치 대조**: kkebi identity «20머지»(C) vs «머지 7+직접 4»(Part 2 실측) — 5단계에서 산정 기준 확정.
7. **기록 정정**: 계획 지시문의 `fixtures/pregate/notification-design-spec.md` 경로는 저장소에 없음(스크래치 보관) — 소급 대조 출처는 워크트리 히스토리로 통일.


---

# v2 반영 델타 — 3단계 적대 리뷰 4기(Part 1·2·3·교차) 전건 반영 (2026-09-03)

리뷰 결과: BLOCKER 1(Part 2 — 조건부 해제)·MAJOR 17·MINOR 30. 방향 변경·퀄리티 트레이드오프·게이트 완화 사유 없음 → 아래 델타를 v1 본문 위에 우선 적용해 구현한다(충돌 시 델타가 정본).

## D-P1 (Part 1)
- **④′** 검증됨. m-1: `_Class(Base)`의 base에 `:`가 있어 compile 실패하면 «`_`+대문자 선두는 클래스 — 사설 함수는 소문자 선두» 힌트를 형식 red 메시지에 병기. m-2: 5단계 대조표에 «동일 트리 전후 비교(레인 당시 15건과 무관)» 명기.
- **⑤ 전사 우선 변형(m-3·m-4·m-5)**: «전사 불가 칸» 신개념 폐기. 마이그레이션 add에 symbols 전사가 있으면 **기존 렌더러로 전사 우선**(`migrations.Migration` base는 BASE_IMPORTS 밖·compile OK·검사기 base 무검사 — 리뷰 실측), 결손 시만 정형 스텁. `initial = True`는 `0001_`에만. `__init__.py`는 빈 파일. R-3426 rev3 문면은 «마이그레이션 칸의 결손 보충(값 축 유도 3행째)»으로 — b35 «전사 우선·결손 보충» 원리와 동형. 단조성 예외(RunPython 전사 예보 불능) 해소.
- **⑧ 실행기 소형 변경으로 전환(M-1·M-2·m-6·m-7 + 교차 M-1)**: 해시 산출은 실행기 `--block-hash`(출력 전용·판정 무접촉 — 파서와 **같은 정규식**으로 기계 블록 4종+입장 표 추출 → sha256[:12]; sed/git 판형 폐기·OS 무관·git 0회). 실행기가 **매 실행 리포트 헤더에 `블록 해시 <값>` 병기**(리포트만으로 skip 대조 가능). Coordinator 규범: «`--block-hash` 값이 직전 실행 헤더 값과 같으면 skip 가능 — skip 행 `- pre-gate skip — 블록 해시 <값> 불변 · 기준선 <sha12> · 재실행 생략 <UTC> · 직전 예보 <UTC>` append 의무(`## pre-gate 예보` 문자열 비사용)». bare git 금지 문장 무접촉.
- **③(m-8·m-9 + 교차 M-2·m-13)**: digest 대상을 `scripts/*.py + *.json`(`__pycache__` 제외) 전량으로(목록 논쟁 제거) + 인터프리터 `X.Y` 병기. R-0192 clarification은 «플러그인 버전» 기준만·digest 참조는 R-0365(G2)에 한정. **버전 판별은 사각 행 수 휴리스틱을 폐기하고 pregate-report 헤더 `실행기: design_pregate.py · dddjango vX.Y.Z · 블록 해시 <값>` 스탬프로 교체**(probe 헬퍼를 design_pregate.py에도 — 두 스크립트 독립 파일이라 각자 보유·유닛으로 동치 가드). ledger 헤더 판별표 동기.
- **⑥ 스텁 대체 변형(M-3·m-10 + 교차 m-9)**: `--base` 명시 시 오버레이 실존 add는 **사본에서 스텁으로 덮어쓰기**(실물 판정 혼입 0 — E1/E2 의미 통일) + already-built «기실현(오버레이 실존 — 스텁 대체 예보)» 기록. BLIND_SPOTS 행 문면: «`--base` 명시 시 사본 = 기준선 트리 + (worktree−HEAD) 오버레이의 스텁 대체 — 기준선 이후 커밋분은 사본에 없다». 명시 `--base HEAD`도 재발화 판형임을 문면에. E1 단언 강화(materialized ∋ 경로 ∧ 기실현 0)·E2(미커밋 → 기실현 1·스텁 판정)·E3·E4 유지. R-3432 rev2 문면에서 «승격 ⑶ 계상» 평가 부기 제거(설계 v4·ledger로 이동)·**s006 새 블록 b10 신설**(기존 괄호 내부 삽입 금지).
- 러너 계수(교차 m-1): 묶음별 리포트 파일 분리·기대값은 묶음별(Part 1 green3+red2 = 별도 리포트 각 1). LEDGER(교차 m-3): 관행대로 graph 절 rebaseline 행 +6.

## D-P2 (Part 2)
- **B-1 사슬 검증 강화(해제)**: `anchor ∈ git rev-list --first-parent HEAD`(도달 필수) ∧ M ∈ 그 구간. 미도달 상태에서 목록 지정 → exit 1 «앵커가 HEAD first-parent 사슬 밖 — 승인 목록 판정 불가». 3사례 통과 실측(오차단 0). 픽스처 **P9**(역방향 합성 머지 → exit 1)·**P9′**(앵커 사슬 밖 → exit 1).
- **M-1 custody 성문**: R-NEXT+0에 «도구는 소유를 검증하지 않는다 — 빚 목록과 같은 사용자 승인 입력» + 머지 표에 `^2` ref 도달성 정보 행(`git name-rev --refs='refs/*' M^2`) + G2 배너 열거 유지.
- **M-2 측정 유효성**: M^1·M^2 어느 쪽이든 검사기 c 측정 무효(exit∉{0,2} ∨ 합성행 존재) → 해당 c 라인 전부 귀속 유지(사유 `측정 무효(M^1|M^2)`) — R-0372 «미파싱=측정 실패» 정합. 픽스처 **P10**(M^1에 SyntaxError 심기 → 귀속 유지). 스냅숏 실행은 `git_root=None`·`snapshot_anchor` 규약 명시.
- **M-3 표기·표 정정**: `↳ 유입: M`은 **L 증명 머지** 기준. §4 «d892894뿐이면 유입 349·귀속 114» 삭제 → «부분 목록 시 잔여 라인에 `미승인 머지 경유 <sha>`로 누락 SHA 표면화 — 수치는 구현 후 실측 확정(라인 단위 L)».
- m-1 사유 어휘 통합 `비머지 커밋 경유 <sha>`(레인/직접 구별 불가 인정)·kkebi 기대 «첫 승인 머지보다 앞선 비머지 = 1(e219608)». m-2 P0 마스킹 목록 성문(툴체인 행 전체·sidecar tempdir 경로·`ts`/`run_id`/`record_id`)·불변식 3종 유지. m-3 ① R-3131 rev2 «확립 규약 수용 금지» 절 보존 ② R-NEXT+0 «레인 first-parent 사슬 위의 2-부모 머지» ③ R-NEXT+2 처방에 «레인 설계 반송(레인 원인)» 병기 ④ «rulepack.json 재소성» 문면 ⑤ houserules §3 신호 +1행(경로 필터 서술). m-4 P4는 `application/promotion/` 완전 BC 캘리브레이션. m-5 스냅숏 수 진단 1행.
- 교차: `anchor_diff.py` 봉인 그룹 = **scorer**. 신규 Work 3건은 `ontology/wiring/command-dddjango.ttl` `delegatedTo` 3행 필수·R-NEXT+1/+2는 **s007 새 블록 b13** 신설. codex 의미 미러 2파일(`dddjango/SKILL.md`·`dddjango-discipline-houserules/SKILL.md`). LEDGER +3.

## D-P3 (Part 3)
- **MAJOR-1** `_top_level_names`에 `ast.TypeAlias`(PEP 695)·`AsyncFunctionDef` 추가 + 유닛 + **양 저장소 실코드 전수 import 자가 대조 스캔(오차단 0 증명 — 리뷰 프로토타입 `proto_existence.py` 판형)**을 검증 게이트 수동 채널로 편입(릴리즈 조건).
- **MAJOR-2** `_realize_module` 승격 해소: 상위 `<parts[:-1]>.py`가 planned-add(슬롯)면 하위 부품은 «자기 add 해소»; 기존 실물은 `checker_target.slot_file` 역방향 판형 재사용(재구현 금지).
- **MAJOR-3** ⑵ 자리표시자 판정은 «이름 import(`from M import n`)의 대상 M»에 한정 — 모듈 import(`import M`·`from P import M`)는 ⑵ 비적용(ImportError 아님). kind=module만·빈 패키지 `__init__` 제외(교차 m-8).
- **MAJOR-4** §1·§5·§8의 SD fortune-reading 사례 삭제(fortune_reading→fortune_calculation import 0 — 계약 fixture 의존이지 import 의존 아님). 효과는 **kkebi형 한정**(S2 ⑵ 실측 재현 + STOP-365 ⑴)으로 재기술·1단계 표 «SD형 분 단위» 철회 주석.
- **MAJOR-5 + 교차 M-3** 설계 v4 §8 ⑷ «실존 채널 계수·판정식» 신설: 결손 건수·처분 분포·**도구 오류**(대상 실존인데 결손 — filtered와 분리 계수)·오탐=도구 오류·미탐=행이 있었는데 ImportError/0B STOP 발생·차단 승격 전제 «도구 오류 0 ∧ 진탐 ≥1 over ≥2 레인»·**exit 5는 승격 후에도 비차단 유지(별도 게이트 전까지)**. §8 ⑶에 Part 1 «재발화 형식 red 별도 계수» 승계. ledger 열 정의 동기. 설계·ledger 산문 rebase 절차를 통합 절에.
- **MAJOR-6** `corrected` = «대상 실존 확보(K 증가) 또는 경로 오기 정정(대상 기실존)» 한정; 행 삭제·소비 철회로 결손이 소멸하면 리포트가 «결손 소멸 ∧ 행 수 R 감소»를 표기하고 처분은 `corrected(철회: <근거>)` 근거 병기 의무(발주자 사안이면 STOP) — 라벨 집합 3 유지. R-3427 rev2 «채널 은폐» 문면과 정합.
- **MAJOR-7** exit 열거 갱신 지점 전수: 실행기 docstring(양 미러)·**설계 D3(:74)**·조감도 :638·러너 docstring·R-3437. 
- **교차 M-4** 예보 항목 채널에 «`deferred`는 없다(이연은 ignored+빚 매칭 또는 filtered)» 대칭 문면 + «각 채널의 정의 밖 재량 라벨은 없다».
- MINOR: `_repo_root_packages` placeholder 필터·첫 세그먼트 명시 / `remove@Ln` 후행 제거 대상은 G1 시점 상태로 실존 판정 / U 명시(namespace-dir+비서브모듈·`import *`·`__getattr__`) / 사각 병기(TYPE_CHECKING·gitignore) / `deferred(<소유>; until <SHA|Sn>)` 정형 권고·린트 이월 / 실행기 인터프리터 하한 검사 / 조감도 갱신 / `import a.b` 바인딩 `a`·Assign 튜플 `ast.walk` / 실존 검사 삽입 지점 = materialize(+골격·`__init__` 체인) 뒤·실체화-0 분기 앞 / «파서 한 줄도» → 열거 함수 한정·«기존 4종 문자 동일» → exit·귀속·ID 동일 한정. LEDGER +4.

## D-통합
- **릴리즈 단위: 단일 v2.17.16(3부 합산)** — 릴리즈마다 라이브 레인 캐시 교체 위험이 있으므로 1회로. 시점은 사용자 결정 게이트. 판별 = 리포트 헤더 버전 스탬프(행 수 휴리스틱 폐기).
- 계수표 최종 기대: ExpressionShape **3543**(+7+9+5) · Norm/Work **3450**(+3) · Block **2897~2900**(s002/b9·s006/b10·s007/b13) · ISSUED **R-3439~3441** · LEDGER **+13** · BLIND_SPOTS **9**(Part 1 +1 문면·Part 3 +2).
- 통합 절 1 정정: 세 Part 규범 ID 집합은 서로소 → rev 번호는 착지 순서와 무관. rebase 대상은 s006/b9·s002·s007 `djr:text`뿐. 통합 절 5 정정: Coordinator 규범엔 exit 수치 열거 없음(실재 지점 5곳은 D-P3 MAJOR-7).
- `make verify-mutation`은 3 Part 전부(rulepack 재소성). codex 의미 미러 대상: Part 1 8곳·Part 2 2파일·Part 3 2파일.
- 5단계 입력 추가: 1단계 C «kkebi 20머지» vs Part 2 «머지 7+비머지 8» 산정 기준 확정 · Part 3 오차단 0 스캔 결과표.
