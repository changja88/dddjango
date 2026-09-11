# Whole implementation review B — 규범·입력·보고·의미 미러

검토 기준: `/Users/hyun/.cache/dddjango-field4-followup-20260911`의 커밋 전 작업 bytes, 기준 HEAD `3355710dcbaf023a16856cb2f307aa2a03fc0996`. `whole-review-brief.md`, 승인 12건의 `workspace/eval/field-report-4-followup/brief.md`, `whole-review-inventory.md`를 먼저 읽었다. 이전 Task6 리뷰의 승인을 이번 판단의 근거로 사용하지 않았다.

**독립 B 렌즈 판정: B0 / M1 / m1 — CHANGES REQUIRED. 규범 자체의 새 정책 선택이나 양 런타임 의미 충돌은 발견하지 않았지만, 지원하는 명시 별칭에서 UoW 미해소 후보를 잃는 M1이 있어 최종 감사 준비 완료로 판정할 수 없다. 이는 전체 구현 승인이나 F4 항목 삭제 승인이 아니다.** 다른 독립 리뷰가 확인한 실행 결함, 최종 봉인, 전체 `make verify`, 독립 최종 감사는 별도 선행 조건이다.

## 발견 사항

### M1 — 지원하는 명시 별칭을 사용하면 미해소 UoW 주입의 선언 후보가 사라진다

- 위치: `dddjango/scripts/design_pregate.py:1717`의 타입 해소 이후 `:1720`의 `if "UnitOfWork" in ast.unparse(annotation)` 조건. Codex byte 미러도 동일하다.
- 승인/규범 근거: 명시 read-only/UoW 출처를 확인하고 미해소 출처를 후보로 남긴다(`dddjango/agents/design-architect.md:87`, 현행 스펙 #197). Task1 보고의 더 좁은 표현도 “미해소 suffix는 후보”라고 한다. 이 반례에는 `StrangeUnitOfWork`라는 명시 suffix와 지원되는 단순 module alias가 모두 있다. 임의의 unrelated P 타입을 UoW라고 추측하라는 요구가 아니다.
- 실제 입력: file-plan `update application/garden/application_layer/books/list_books/list_books_use_case.py`; symbols는 순서대로 `...::alias U = StrangeUnitOfWork`, `...::ListBooks`, `...::ListBooks.__init__(self, uow: U)`; effects는 `...::ListBooks read-only uow=none`.
- 실제 관찰: public `parse_spec(text)`는 `errors=[]`를 반환한다. `check_declarations(plan, copy)`는 `[]`다. 별칭 행을 빼고 매개변수 주석을 `StrangeUnitOfWork`로 직접 적은 대조는 `('#197', False, 'bare 타입 StrangeUnitOfWork 출처 미해소…')`를 반환한다. 별칭 resolver가 같은 미해소 issue를 얻더라도 원래 매개변수의 철자 `U`에 `UnitOfWork`가 없어서 이를 버린다.
- 영향: 표현만 다른 동일한 선언에서 확인 질문이 사라진다. 효과를 명시했고 지원되는 단순 별칭으로 UoW 의도를 남겼는데도 “후보0”으로 보고되어 승인한 provenance 기반 후보 경계를 깨뜨린다. 확정 위반을 새로 만들어야 한다는 지적은 아니다.
- 필요한 수정: 지원하는 별칭을 따라 얻은 named-UoW 미해소 근거를 후보 판단까지 보존한다. 직접 표기와 별칭 표기가 같은 후보를 내고, 확인된 비-UoW 계약·write 대조는 계속 clean이어야 한다.
- 증거 종류: 이번 B 리뷰에서 `python3 -B`로 번들 `design_pregate`를 import해 public parser와 declaration checker를 호출했다. 두 입력 모두 메모리 문자열로 만들었으며, 실제 파일이 없는 `/private/tmp/no-such-review-B-source`를 조회 root로 전달했다. 사용자 프로젝트·Git·fixture suite·source mutation은 없었다. 이 경로는 선언 채널의 최소 반례이며 전체 CLI 실존 게이트 통과를 주장하지 않는다.

재현 핵심(실제로 실행한 두 경우):

```python
for ann, alias in [
    ("StrangeUnitOfWork", ""),
    ("U", f"{path}::alias U = StrangeUnitOfWork\n"),
]:
    # file-plan update + symbols(alias, ListBooks, __init__) + effects fence
    plan, errors = pg.parse_spec(text)
    found = pg.check_declarations(plan, Path("/private/tmp/no-such-review-B-source"))
# direct: errors=[]; [("#197", False, ...)]
# alias:  errors=[]; []
```

### m1 — 현행 골격 검사기 설명 네 곳이 폐지한 #642를 범위 표기에 계속 포함한다

- 위치: `dddjango/scripts/check-layer-skeleton.py:27`, `:89`, `:130`, `:246`. 동일 위치의 `codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py`도 같다.
- 현행 설명은 `형태 검증(#638~#643)` 또는 동등한 범위를 쓴다. #642는 그 범위에 포함된다. 이번 승인 방향은 #642의 크기 하한 자체를 폐지하는 것이며, 현행 스펙 `workspace/design/2026-08-08-tree-revision-spec.md:931`과 owner map `workspace/plan/2026-08-11-rule-owner-map.md:8`은 이를 폐지로 기록했다. 스펙의 #490/#644 및 predicates는 이미 `#638~#641·#643`으로 고쳤다.
- 영향: 실제 #642 emission은 제거되어 이 설명이 검사를 다시 발동시키지는 않는다. 따라서 MAJOR가 아니다. 다만 현행 설치본의 검사 범위 설명을 읽는 사람이 폐지 규칙을 아직 형식 검사 대상이라고 오해할 수 있는, 이번 정합화 범위의 잔존 문구다.
- 필요한 최소 수정: 위 네 설명의 범위를 `#638~#641·#643`으로 맞추고 byte 미러를 갱신한다. 동작·규칙·테스트 추가는 필요하지 않다.
- 증거 종류: 현행 파일 직접 검색/읽기. scratch 실행으로 재현한 기능 결함이라는 주장은 하지 않는다.

## 규범별 독립 판단

| 승인 범위 | 검토 결과와 직접 근거 |
|---|---|
| F4-13 내부 실패와 외부 HTTP 경계 | architect slot10, API reviewer slot10, discipline reviewer raw 경계/ACL 전수성, Ninja SKILL, Ninja reference의 총 여섯 canonical 문단이 같은 조항을 가진다. 이미 잡은 IntegrityError만 대상으로 알려진 승인 제약은 concrete 계약 예외, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository=domain, capability=port 소유를 구분하며 일반 실패의 기존 safe500, 새 ErrorCode/ErrorSchema/4xx/503 금지, uncaught unknown catch-all 금지, 별도 public meaning 승인, 기존 계약 예외 관찰 후 재던짐을 모두 명시한다. `dddjango/agents/design-architect.md:54`, `dddjango/agents/discipline-reviewer.md:94`, `:100`과 Ninja reference §6.2를 직접 읽었다. unchanged synthetic-infra checker도 raw DB exception 합성 및 broad catch-all 번역을 대상으로 하므로 이 문면과 충돌하지 않는다. 여섯 문단 존재는 새 에이전트의 실제 역할 수행 증거가 아니다. |
| F4-9 admin 범위 | architect `:89`, discipline reviewer `:126`, houserules §4에 #493 유지 / #645 확인된 framework 슬롯 / #646 유지 / #647 열린 UI context / #650 실제 JSON 검증 유지의 동일 다섯 규칙이 있다. Django/Parler 출처, 연결된 private helper, form/inline/media·UI metadata 병행, 업무 소비 시 기존 규율 복귀, 동적/재귀 escape 후보, 별도 업무 dict·bare Any·admin 경로 전면 면제 금지가 구체적이다. pre-gate의 생성 private helper는 S1로만 다룬다. 이 문면은 승인 범위에 맞는다. 실제 checker의 모든 flow가 문면을 충족한다고 일반화하지 않는다. |
| F4-1 / F4-18 효과·선언 후상태 | `design_pregate.py:804` 이후 parser와 `:841` hash, `:1502` 이후 선언 타입 조회, `:1687` declaration checker를 직접 대조했다. 선택 효과, add/update 선행 클래스, 무기재 S5, 무효/중복 형식 red, 기존 해시 유지 및 효과 원문 마지막 결합, 실물 본문을 덮지 않는 선언 후상태가 규범에 반영되어 있다. #197의 명시 모순과 출처 기반 UoW 주입, #202의 명시 출처·별칭·컨테이너·private DTO 추적 및 VO 허용은 본문 검증과 분리되어 있다. 미해소 UoW 주입 후보는 구현상 원래 annotation의 `UnitOfWork` 철자만 단서로 하여, 지원하는 별칭 뒤의 명시 suffix를 놓친다. M1은 이 구체적 반례이며 일반 임의 타입을 전부 UoW로 취급하라는 요구가 아니다. |
| F4-1 marker update | 문면은 무기재 유지 / 빈 module 목록 / 정적 교체와 함수·클래스 decorator 및 본문 보존을 명확히 구분한다. base/client·nodeid·동적 변경의 S5 한계를 쓴다. Task1 마지막 append와 Task2 provenance 최종 재계산 append를 읽어 초기 보고보다 최종 인터페이스를 기준으로 삼았다. 정적 marker 전사의 성공을 기존 테스트 본문의 검증으로 주장하지 않는다. |
| F4-12 / F4-19 S1·실행 모드·보고 | `design_pregate.py:1966–2055`는 원 record의 checker/full normalized key, 생성 최종 AST 위치와 정확한 슬롯으로 S1을 나누고 #566 및 미결합 evidence를 유지한다. 선언 확정은 S1과 별도이며 `:2925` 이후 materialized0에서도 확정 exit2, 후보/실존 결손은 별도 상태다. `:2458`의 S1/S2/S3/S5 현재 문구는 생성 본문·물리 import 전사·선언 검사·update 실본문을 혼동하지 않는다. Task1 actual CLI 기록의 선언확정 exit2 → 처분 없는 check-report3 → 처분 후0과 Task2/3 최종 보고 인터페이스를 대조했다. 초기/명시 재예보 구분은 기실현 add 기본 허용으로 확대되지 않았고, 기록 파일을 file-plan으로 편입하지 말라는 안내도 docs 전면 제외 정책으로 쓰이지 않는다. |
| F4-10 / F4-11 / F4-14 / F4-15 | current predicates의 #153은 builder 준비와 실제 execute를 구분하고 미해소/반복 수 후보를 남긴다. #268은 closed standard Enum 제외, custom/open Enum 후보를 constructor raise 존재와 별개로 설명한다. #546/#557은 spec·predicates·owner map·reviewer에서 `ast+` 및 checker+감수자 역할로 맞춰졌고, 해소된 영역/출처만 확정으로 다룬다. same-type instance identity, 임의 helper 실행, 동적 출처까지 증명한다는 문장은 없다. Task4의 세 fix append를 읽었다. |
| F4-16 폐지와 보존 | canonical houserules의 R-3417 승격 술어와 R-3410 부품 출생 하한이 제거되었고, current #189의 간접 `하한 충족`도 최종본에서 제거됐다. #192 부품별 사설 조각 규율, 유스케이스 간 공유 금지, module-object/string 참조 전수 조사, G0 기존 빚 경로, #643 부품0 환원, #644 200행 감사 신호는 유지된다. current spec/owner map에는 active642 행이 없고 폐지 이력만 남는다. m1 이외의 현행 배포/runtime 문면에서 강제50 하한을 발견하지 않았다. tree row50 인용과 과거 Expression·동결 source 기록은 현행 하한으로 취급하지 않았다. |
| F4-17 cache-only 대상 | Task5 최종 appendix와 shared predicate/snapshot 소유 경계를 확인했다. cache 흔적을 가진 optional instance 제외이며 fixed 골격·실제 source·untracked source 제외로 일반화하지 않는다. 빈 cache directory 하나만으로 제외하지 않는 보수적 제한과 파일시스템 관찰의 비원자성은 보고에 명시되어 있다. |

## 온톨로지·미러·현행 문서 증거

`whole-review-B-norms.diff`의 canonical 규범/current-document 변경을 읽고, 긴 중복 TTL/rulepack 부분은 실제 RDF 전후 비교와 현행 의미 블록 대조로 확인했다. 이번 읽기 전용 검증에서 다음 결과를 직접 얻었다. 이미 green인 검증 suite는 재실행하지 않았다.

- 8 TTL 파일의 changed text는 **23개**이며, 검토한 `task-6-block-changes.json`의 23 after 블록과 전수 동일하다. 기존 currentExpression이 바뀐 Work는 **31개**다. 각 새 Expression의 `wasRevisionOf`, revision +1, 이전 Expression triples 보존을 직접 assertion했다. 삭제 predicate는 currentExpression/prefLabel/text에 한정되며 Work/Expression 이력 삭제를 발견하지 않았다.
- Codex의 **20개** changed meaning block은 플랫폼상 필요한 skill 참조명, spawn 후 shell 실행 순서, `Phase2 6번`, 스크립트 경로 표현의 기존 변환만 적용하면 전수 동일하다. 해당 차이들은 실행 모델을 맞추는 표현이며 오류·효과·admin·승격 정책을 바꾸지 않는다. 현재 changed script/rulepack **10 byte pair**도 직접 동일성을 확인했다.
- LEDGER의 이전 행 전체가 prefix로 보존되고 **11행 append**만 있다. 9행 graph baseline 재기준선 및 2행 source address는 기존 `ontology_render_sync.py:123`, `corpus_mirror_sync.py:171–183`의 현재 동작과 맞는다. 두 source는 Task6 이전 snapshot과 bytes 동일하고, 새 migrated hash가 각각 **유일한 원문 section span**에 대응함을 직접 검사했다(houserules `s003-0`, Ninja source `s024-6.2`). 이는 과거의 정확한 migration 날짜를 입증하는 메타데이터가 아니라 보존 원문을 찾는 주소다. append note도 그렇게 한정한다.
- 현행 spec의 active rule 행을 독립 집계한 결과 **552 = path172 + ast290 + ast+63 + human27**, active642=0이다. 545 reading-guide 수치는 552−7과 맞는다. #546/#557의 grade와 감수자 소유를 현행 세 문서에서 직접 대조했다.

## 증거의 한계와 준비 상태

Task1–6 보고의 최종 appendix를 읽었으며 earlier freeze/hash/초기 PASS를 최신 상태의 증명으로 재사용하지 않았다. Task6의 normative scenario 표는 스스로 manual reading/text-contract라고 분류하므로 이를 unsupported fresh-role 성공 주장으로 지적할 근거는 없다. 실제 코드 실행 로그는 해당 fixture와 해당 시점만 입증한다. S1은 미검증이고 green은 설계 전체·실구현 전체 검증이 아니다.

다른 전체 리뷰 A가 marker mutation/admin kwargs/UoW origin과 관련된 source 문제를 조사 중이라는 메시지를 받았다. 이는 이 B 보고의 독립 재현이나 신규 finding으로 계산하지 않았다. 그 결과가 확정되면 현재 규범의 보존 경계를 충족하도록 소스가 수정되어야 하며, 이 B 판정으로 그 결함을 무시하거나 원 보고서를 삭제해서는 안 된다.

이번 리뷰는 제품/테스트/Git 상태를 변경하지 않았고 실제 사용자 프로젝트를 실행하지 않았다. 작성한 파일은 이 보고서뿐이다. full `make verify`, seal, 최종 evidence audit 및 원 보고서의 승인된 항목 정리는 아직 완료로 주장할 수 없다.

Serena/Graphify: worktree opt-in 부재 및 배정 지시에 따라 검색·로드·호출·초기화하지 않았다. 서브에이전트를 생성하지 않았다.
