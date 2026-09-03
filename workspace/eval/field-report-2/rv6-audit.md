# rv6 — ⑥ 독립 감사·재검 · 현장 보고 수리 2 (2026-09-04)

대상: 브랜치 `fix/field-report-2` HEAD **d9d76ac**(main c7573b6 기점 · 커밋 11 · 규범 35fc29b · 검사기 95a95cc · ⑤ 반영 d9d76ac). ⓪~⑤ 산출을 처음 보는 눈으로 재검했고 앞선 리뷰어 판정은 전제하지 않았다(재실측 우선). 저장소 3곳(dddjango·spring·kkebi)은 읽기·조회만 — 실행은 전부 `scratchpad/fr2/rv6/`(옛 검사기 = `git archive 35fc29b dddjango/scripts` · 새 검사기 = `git archive HEAD` · 격리 사본 `fr2/DE/iso/{spring,kkebi}` · `fr2/H/spring` 3커밋 detach 재실행 뒤 9c8814e 복원 · 프로브 14 · 매트릭스 옛-검사기 변종 3 · `make verify-ontology`/`verify-base-core`/`verify-base-cross` 로그). 감사 뒤 `git status`: dddjango 는 시작 시점과 동일(타 세션의 `M …django-stubs-generic-base.md` 1건뿐) · H/spring `9c8814e` detach · 원본 두 저장소 무접촉. Serena: skipped — `.serena/project.yml` 부재(기본 도구·격리 실행으로 충분).

## 1. 판정 표

| # | 항목 | 판정 | 한 줄 근거 |
|---|---|---|---|
| 1 | 결정 정합(결정 1·2 ↔ 구현) | **검증됨 + MAJOR(고지 1)** | 결정 1·2 는 문면·코드에 그대로(§2.1). 결정 «집행» 밖 확장 6건 열거(§3) — 그중 **R-3449 재수출 조항**은 정책 확장(발주측 기존 산출물 4 BC·except 13 이 규범 위반이 되고 승인 명세 2건의 «선례» 와 충돌) → 머지 브리프 고지 필수 |
| 2 | 무손실 재검(옛↔새 검사기 · 양 저장소 · 픽스처) | **검증됨** | A∖B = **0/0**(3검사기×2저장소) · B∖A = `#645` 78/121 + `ⓓ#645` 694/385 뿐 · `#493` 3,225/173 불변 · port/usecase 레코드 111/54·184/123 byte 동일 · 카탈로그 59d08c7 A∖B = 정확히 {#219×2, #635×3} · 99253ce 4/3 불변 · 옛 검사기로 현 픽스처 census: cross 차이 **정확히 2행**(skeleton×port-adapter (219,1)·skeleton×usecase-dto (635,1)) · count/baseline 불일치 **public-surface 1레인뿐**(§2.2) |
| 3 | 검사기 결정성·사각(#645 · H 가드) | **검증됨 + MINOR ×4** | fail-closed `names={"Any"}` 오탐 프로브: 모듈 상수·클래스 `Any` 그림자 ✓ · Enum 멤버 `Kind.Any` 무발화 ✓ · 함수 본문 `Any = 1` 은 그림자 안 됨(병리 코드 1형) · 별칭 `t.Optional[Any]`/`t.Union`/`t.Annotated` bare ✓ · **`Optional as Opt`/`Union as U`/`Annotated as A` 는 ⓓ 강등**(미문서) · **`from myproj.x import Any` 재수출은 무발화**(미문서 사각) · `Literal[Any]` 무발화(무효 타이핑이라 무해) · H 가드는 파싱 불능에 fail-closed(placeholder 아님 → 기존 `_parse` None 침묵 = 옛 동작 그대로) (§2.3) |
| 4 | 규범 정합(신설 5·개정 5 · 저작 규약 · 도구 · 미러) | **검증됨 + MINOR ×3** | 모순·중복 0(§2.4 — R-3449 «도메인 예외 칸 번역» 은 #92/#95·트리 69~70행·accounts 선례·exception-map «도메인→published» 와 정합, 도메인이 인프라를 import 하지 않음) · ISSUED 5·LEDGER 10행·계수(3568/3459/2903)·wiring 4원 기록·rev 종류 amendment ✓ · `verify-ontology` 11/11 green · `verify-base-core`/`-cross` green · byte 미러 `diff -rq` 0 · codex 손 미러 3 hunk 동일. MINOR: R-3449 에 «도메인 어휘로 이름» 단서 없음 · R-3449 delegatedTo 에 discipline-reviewer 미병기(재수출 위반은 코드에서만 보임) · `tree-revision-spec.md:1174` #645 행 «`Any` 와 None 의 합집합» 이 코드(«Any 가 섞인 합집합»)보다 좁음 |
| 5 | 효과 정직성·문서 | **MINOR ×3** | **«전부 `object` 치환 가능» 과대 문안이 3곳 잔존**(현장 보고 :14 E 행 · 로드맵 :59 R-19 · 루브릭 ④ — ⑤ 표 :147 은 «④ 절 정정» 이라 적었으나 ④ 에 정정 문장 부재 → ⑤ 반영 주장과 실물 불일치) · ④ «43/43 = usecase-dto 단독 grep» 은 출처 검증 불가 · 발주측 빚 4 BC 는 발주자 입력 문서(현장 보고 G 행)에 BC·건수까지 있으나 **파일:줄은 rv5-C §2.3 에만**. ⓒ 효과 표(rv5-C §5)는 과대 아님 |
| 6 | 회귀 위험(설치본 v2.17.16 → 이 배치) | **MINOR ×3** | #645 소급 형태 = Phase 0 빚 스캔 항목(spring 5 BC·kkebi 6 BC · 24건 = 미러 13·실질 5·factories 6) + 이름 변경 시 재귀속 — 진행 레인 fortune_calculation-2 는 [#645] 0 · «영구 빈 파일» 경로는 «하나» 검사 없는 칸(컨트롤러·애그리거트)과 같은 위험 등급(#488 존재만 · 인수 테스트·명세 대조 소관 — 신설 위험 아님) · R-3427 rev4 현재 명세 형식 red 0/8(사람 판정) · **R-0284 rev3 «ⓓ#645 동봉» 채널 = registry_gate 밖**(`_FINDING_RE` 가 `[ⓓ#` 를 버리고 sidecar 는 귀속 레코드만) → 루트 직접 실행 + 범위 필터로만 가능(BC 대상 실행은 검사기가 거절) — 선례 #4(ⓓ#644) 와 동형이라 집행 불능은 아니나 문면에 채널 없음 · 실행당 714/385행 |
| 7 | 머지 판정 | **조건부 머지 가능** | 조건 2(§4 — 문서 정정 1 · 브리프 고지 1) · 둘 다 브랜치 안 수리 가능(규범·검사기 무접촉) |

## 2. 상세

### 2.1 결정 정합

- **결정 1**(루브릭 :108 — «시그니처 bare `Any` 만 차단(exit 2) · 변수·제네릭 안은 ⓓ 후보 · 문면 무조건형(`Any` 0 · 경계 입력 `object`/정확 타입 즉시 좁힘 · `*args/**kwargs` 예외 없음)»)
  - 검사기: `check-public-surface-annotation.py:471-513 _check_explicit_any` — 시그니처 bare → `out.add("#645")`(:511 · exit 2) · 시그니처 nested·`AnnAssign` 전부 → `cands.add("#645")`(:513 · exit 불산입). 별표 인자 `:491` · 반환 `:499` · dunder 면제 없음(프로브 p10 `__call__(*args: Any, **kwargs: Any)` → `[#645]`×2). ✓
  - 문면: `discipline-houserules/SKILL.md` §4 b7(:76) — 무조건형 · «별표 인자 면제 관례와 다른 선택» 명시 · 경계 `object`·즉시 좁힘·`Mapping[str, object]`. R-3150(조건부 면제 금지)과 정합. ✓
- **결정 2**(루브릭 :109 — «#219/#635 가 `skeleton_placeholder` 를 건너뜀 · 형제-내용 조건 없음 · R-3181 개정 1줄 · 빈 파일 삭제는 #488 위반»)
  - `check-port-adapter-pairing.py:245` · `check-usecase-dto-placement.py:376` — 술어 `checker_target.skeleton_placeholder`(`:32-50` — 0B·공백·주석-only·docstring-only · `pass` 는 문장이라 대상 아님 · 읽기/파싱 불능 False) 재사용 · 형제 조건 없음 ✓. 침묵 집합은 명목상 {#219,#551,#220,#241,#212,#485}/{#635,#211,#194} 이나 빈 파일엔 클래스가 없어 실효 침묵 = #219/#635 뿐(나머지는 클래스 루프 안). ✓
  - R-3181 rev3(`discipline-houserules-final.ttl` s003-0/b3): «1줄» 요구가 3문장(시점 = R-0319 · 검사기 건너뜀 · 삭제 = #488 위반)으로 실현 — 결정 2 문면의 세 요소를 모두 담은 것이라 집행. ✓
- 결정 «집행» 으로 판정한 것: R-0345 rev2(registry #11 소개행) · `@staticmethod` 첫 인자 면제 해제(수신자 아닌 인자를 수신자로 오인하던 사각 수리 · 프로브 p10 `self: Any` → `[#645]`) · dunder 무면제 · `test/{factories,fake}` 포함(#493 과 같은 파일 집합).
- 결정 «확장» 으로 판정한 것 → §3.

### 2.2 무손실 재검(실측)

명령(전부 `scratchpad/fr2/rv6/`): `run_iso.sh` — `{spring,kkebi}` × `{scripts-old, scripts-new}` × `{public-surface, port-adapter-pairing, usecase-dto-placement}` · `DJR_FINDINGS_JSON` sink · 인터프리터 = 각 저장소 `.venv/bin/python` 3.14.7 · `diff.py` 로 (severity, rule, 상대경로, message) 다중집합 차분.

| 저장소 · 검사기 | old | new | A∖B | B∖A |
|---|---|---|---|---|
| spring public-surface | 3,312 | 4,084 | **0** | `#645` violation 78(application **10**) + `ⓓ#645` 694(application 114) |
| spring port-adapter / usecase-dto | 111 / 54 | 111 / 54 | 0 / 0 | 0 / 0 |
| kkebi public-surface | 345 | 851 | **0** | `#645` violation 121(application **14**) + `ⓓ#645` 385(application 134) |
| kkebi port-adapter / usecase-dto | 184 / 123 | 184 / 123 | 0 / 0 | 0 / 0 |

- `#493` old/new = 3,225/3,225 · 173/173. application `[#645]` 24건 파일:줄 = rv5-C §3 표와 동일(spring: fortune_record 2·promotion 2·service_policy 4·factories 2 / kkebi: identity 2·share 2·tarot 1·product_observability 2·saju 3·billing factories 4).
- 스크립트 트리 차이(`diff -rq scripts-old scripts-new`): 검사기 3 + `design_pregate.py`(S3 문자열) + `pregate_symbol_kinds.json` + `rulepack.json` **6파일뿐** → 나머지 24 검사기는 byte 동일이라 «#645 외 규칙 발화 라인 byte 동일» 은 3검사기 차분 0 으로 닫힌다.
- H 카탈로그(`fr2/H/spring` · `checkout --detach` 3커밋 → 9c8814e 복원 확인): `59d08c7` old {#219×2, #635×3} exit 2,2 → new **0 · exit 0,0**(A∖B 정확히 5 · B∖A 0 — 파일 5 = ⓪ 목록) · `99253ce` old=new(port 4 = #218×2+#576×2 · usecase 3 = #193×3) exit 2,2 불변 · `9c8814e` = 59d08c7.
- 픽스처 27종: 옛 검사기 변종(`S`·`ROOT` 만 교체한 `*_old.py`)으로 현 EXPECTED 대조 — `checker_cross_matrix` **차이 2건**(`skeleton × check-port-adapter-pairing.py (219,1)` · `skeleton × check-usecase-dto-placement.py (635,1)` — 결정 2 의 0B 재등장 칸) · `findings_count_matrix` 불일치 **1**(public-surface: 옛 12/2 vs 기대 20/3 = #645×8 + ⓓ 1) · `checker_baseline_matrix` 불일치 **1**(public-surface (2,12,12,4) vs (2,20,20,5)). 새 검사기 공식 실행(`verify-base-core`·`-cross`): fixture 104/104 · baseline 73/73 · count 73/73 · cross 348/348 차이 0 · registry_gate_smoke 31/31 · bc_registry ✓.

### 2.3 검사기 결정성·사각(프로브 14 · `scratchpad/fr2/rv6/probes/`)

| 프로브 | 형상 | 결과 | 판정 |
|---|---|---|---|
| p04/p05 | 모듈 `Any = 1` · `class Any` 뒤 `x: Any` | 무발화 | 그림자 ✓ |
| p14 | `class Kind(Enum): Any = "any"` · `x: "Kind.Any"` | 무발화 | Attribute receiver 가 mods 밖 ✓(오탐 없음) |
| p06 | 함수 본문 `Any = 1` + 중첩 `inner(x: Any)` | `[#645]` | 모듈 수준만 그림자 — 병리 코드 1형(MINOR·무해) |
| p07 / p09 | import 없는 `x: Any -> Any` / `from typing import *` | bare ×2 / bare | fail-closed(Δ5) ✓ |
| p02 / p13 | `t.Optional[Any]`·`t.Union[Any, None]`·`t.Annotated[t.Any, …]` / `te.Any` | bare ×3 / bare | 별칭 해소 ✓ |
| **p01** | `Optional as Opt`·`Union as U`·`Annotated as A` + `Opt[Any]`·`U[Any,int]`·`A[Any,"d"]` | **ⓓ ×3(강등)** | `_union_members`(:424)·Annotated(:446)가 `_name_of` 원문만 봄 — MINOR(문서화 권고) |
| **p08** | `from myproj.compat import Any` + `x: Any` | **무발화** | `_any_bindings` 가 typing 계열 출처만 인정(:368) — 프로젝트 재수출 사각 · docstring 검출 한계(:24-25)에 미기재 → MINOR |
| p03 | `Literal[Any]` / `Literal["Any"] \| Any` / `Literal["Any"]` / `dict[str, Literal["Any"]]` | 무발화 / bare / 무발화 / 무발화 | `Literal` 제외가 Name 까지 덮음(`:458` — `Literal[Any]` 는 무효 타이핑이라 무해) · 나머지 기대대로 ✓ |
| p10 | `@staticmethod f(self: Any)` · `__call__(*args: Any, **kwargs: Any)` | bare ×3 | ⑤ 반영 ✓ |
| p11 | `x: "Any["` | 무발화 | 재파싱 실패 = 원문 유지(한계 ✓) |
| p12 | `Any \| str` · `int \| Any` · `dict[str, Any] \| None` | bare · bare · nested | Δ5 의미론 ✓ |

- H 가드 fail-closed: `skeleton_placeholder` 는 OSError/SyntaxError 에 False(:44-45) → 건너뛰지 않음 → `_parse` None(usecase `:110-114` · port `:236`) → 무발화 = 35fc29b 이전과 동일 동작(새 침묵 0).
- 결정성: 파일 집합·출력 순서(lineno 정렬 `:509`)·exit 규약(2/0/1) 무변 · git 비의존.

### 2.4 규범 정합

- **R-3449**(`architecture-ddd-final.ttl` s023-3.6/b3 · 렌더 final.md:1021): «port 예외를 도메인 예외(`domain_layer/<aggregate>/exception/<exception>.py` 칸)로 번역 · 잎은 port 예외 타입 비의존(직접·재수출 동일) · 잎은 번역된 실패만 분기». 정합 근거: 트리 69~70행 칸 실존 · #92(houserules final.md:206 — 잎이 domain 에서 가져올 수 있는 것 = exception·값 객체 #95) · `check-usecase-dto-placement.py:180 _lawful_domain_exception_import` · architect exception-map «도메인→published»(design-architect.md:92) · spring accounts 선례 · openai-rag G1″ «domain-owned capability exception» 선례. «도메인이 인프라를 안다» 오해 여부: 번역 주체는 use case(application 층 — port·domain 양쪽 import 는 #185/#186 허용)이고 도메인 예외 모듈은 port 를 import 하지 않으므로 의존 방향 역전 없음 · #64(port→domain 상속 금지)와 서로소. 남는 위험은 **이름 누수**(예: `SmtpTransportError` 를 domain 칸에 두는 것) — 문면에 «도메인 어휘로 이름 짓는다» 단서가 없다(MINOR · 사후 clarification 권고). architecture-ddd :644 «도메인 예외 = 판정 위반» 문장과는 의미 확장 관계(모순 아님 — 선례가 이미 이 모델).
- **R-3447 «어디에도 쓰지 않는다» ↔ 테스트**: §4 b1(:64)이 «테스트와 테스트 재료(`test/fake/`·`factories/`)까지 전부» 라 같은 절 안에서 일관 · 검사기는 #493 과 같은 파일 집합(`test/{unit,integration,e2e}`·`test_*.py` 면제 — #384 «테스트 안이 자유» · 재료 칸은 검사)이라 «테스트 본문의 `Any`» 는 감수자 몫 — §4.1 분담 문장과 정합. 코퍼스 `Any` 언급: architecture-ddd 4(R-3443 1 + Knowledge Level 예제 3 — b6 «표준 문서군 예시 면제» 로 커버) · 그 밖 0. implementation-python §23.1 mypy 블록 무접촉 · R-3443 무접촉.
- **R-3427 rev4** ↔ `design_pregate.py:1527-1529` S3(«전사는 add 소비자 스텁만 · update 잎은 실존 판정만») 정합 · «(pre-gate 보고 헤더의 사각 목록 S3)» 로 해소 가능 · R-3449 와의 관계(«잎이 port 예외를 잡을 계획이면 행을 적어 #93 예보를 받는다» ↔ «잎은 port 예외 타입 비의존») = 채널의 목적 문장이 명시하듯 모순 아님.
- **R-3446**: 코퍼스 `NoReturn` 유일 언급 · R-2720 서로소 · `sys.exit` 미포함 ✓. **R-0719 rev2**: 문장 직후 삽입 · «꽂히는 자리의 Protocol·`Callable`» · spring HEAD 배선(`partial` 본문 안)이 준수형 ✓. **R-3450**: §5.5 화이트리스트 7번째 불릿 · Permission · quota 어휘 0 ✓(«fake 는 프로세스 밖 경계뿐» 은 유일 선례가 반쪽 자격 — ⑤ 결론대로 이상형 문면 유지 수용).
- **저작 규약**: ISSUED 5행 TAB 3필드·결번 0 · LEDGER 10행(35fc29b 8 + d9d76ac in-place 2 · 사유 기재) · Expression 신설 5 = rev 1 · 개정 5 = `prov:wasRevisionOf`+`revision-amendment` · Block IRI = 다음 서수(b3·b7) · 공백 소유 유지 · 계수 3568/3459/2903 · q4 골든 3450 · wiring 7간선 + §16 4원 근거(루브릭 :153 검수표 추기) · rulepack ×2 byte 동일.
- **도구**: `make verify-ontology` **exit 0**(gate 90/90 · issued 0 · ledger 0 · render-sync 540 red 0 · structural 7종 · query-golden 7종) · `make verify-base-core` **exit 0**(corpus_mirror 11/11 · spec_lint 규칙 547 위반 0 · tree 140행 in-sync · fixture/baseline/count 73/73 · rulepack --check · manifest_seal --check --draft · byte-copy diff 0) · `make verify-base-cross` **exit 0**(cross 348 차이 0 · registry_gate_smoke 31/31 · bc_registry A/B/C). 로그 `scratchpad/fr2/rv6/verify-*.log`.
- **미러**: `diff -rq -x __pycache__ dddjango/scripts codex-dddjango/skills/dddjango/scripts` exit 0 · codex 손 미러: houserules §4(마커 2행 외 동일) · architect «경계란 세 가지다» 행 동일 · Coordinator step 5/registry #11 hunk 동일(플랫폼 형식 차뿐).

### 2.5 효과 정직성·문서 불일치 목록

| # | 위치 | 기재 | 실물 | 심각도 |
|---|---|---|---|---|
| 1 | 현장 보고 :14 E 행 «전부 `object` 치환 가능» · 로드맵 :59 R-19 동일 · 루브릭 ④(:135-136) | 전부 치환 | 미러 13·factories 6 = 기계 치환 · 실질 5(kkebi `decision: Any`×2 · saju JSON 순회 ×3)는 본문 좁힘 수리 필요(⓪ 프로브는 Django 스텁 4형뿐) — 루브릭 ⑤ 표 :147 은 «④ 절 정정 · 미러 13 은 object 치환 · 실질 5 는 좁힘 수리» 라 적었으나 ④ 에 그 문장이 **없다**(grep 0) | MINOR(⑤ 반영 주장 ≠ 실물) |
| 2 | 루브릭 ④ :135 «④ 초안의 «43/43» 은 usecase-dto 단독 grep 수치» | 출처 설명 | 어느 계수와도 대응 불가(레코드 291·violation 27·진단행 27) — 차분 0 은 참 | MINOR(검증 불가 문구) |
| 3 | 발주측 빚 4 BC | 현장 보고 G 행(BC·except 수) · 루브릭 ④ · 계획 Δ2 | 발주자 입력 문서에 있어 «보는 자리» 는 맞음 · 파일:줄(5파일 · `translation_service.py:11/89-99` 등)은 rv5-C §2.3 에만 — 발주자가 실행하려면 경로가 필요 | MINOR(경로 병기 권고) |
| — | D n=2/효과 1 · E 10/14(8/10) · F 27/28 · G 0/7(⓪ 시점)·5레인·4 BC/13 · H 5행/12행·13:42·5→0 · 18파일 · ⓓ 114(d2eaafe)/134 · 167/291 · 104/73/73/348/31 | | 전부 실측 일치 | 검증됨 |

ⓒ 효과 표(rv5-C §5)는 정직 문안(E «ⓓ 집행률 미측정» · G «재수출 경로는 pre-gate·G2 둘 다 못 봄 → 리뷰어 전담» · H «잔여 위험 = 영구 빈 파일»)이며 과대 아님. 현장 보고 상태 블록의 효과 문장(«pre-content red 소거 결정적» · «블록에 적으면 실행기가 실제로 예보(exit 2)»)은 실측 뒷받침 있음.

### 2.6 회귀 위험

- **#645 신규 차단**: 귀속 키 = 경로+함수명+매개변수명(`registry_gate._normalize` · rv5-C 실증) → 기존 `Any` 파일을 스쳐도 파일 전체 red 아님. 소급 형태 = ⑴ Phase 0 빚 스캔 항목 spring 5 BC(fortune_character·product 는 factories 만)·kkebi 6 BC(billing 은 factories 만) ⑵ 이름 변경·이동 시 재귀속 ⑶ G2 배너 legacy 잔존 78/121 행. 진행 중 최신 레인 fortune_calculation-2(v2.17.16)는 `[#645]` 0·ⓓ 26 → 릴리즈 즉시 red 되는 레인 없음(표본 2저장소).
- **#219/#635 침묵 → 영구 빈 파일**: 잡는 규칙 = #488(존재만) · #576(빈 port 도 선언으로 계수 → 무발화) · 사용처 import 실패(테스트) · 명세 file-plan 대조(사람) — «하나» 검사 없는 칸(컨트롤러·애그리거트: kkebi tarot 12 · spring `translation_controller.py`)과 동일 등급의 기존 위험이지 신설 위험이 아니다. 루브릭 결정 2 에 잔여 위험으로 기록됨 ✓.
- **R-3427 rev4**: 현재 판본 형식 red 0/8(rv5-C · 재수출 계획 2건은 행이 블록에 있음) — «형식 red» 는 실행기 판정이 아니라 architect/Coordinator 사람 판정(실행기는 누락 행을 알 수 없다).
- **R-0284 rev3 «ⓓ#645 동봉» 집행 가능성**: `registry_gate.py:94 _FINDING_RE = ^\s*(\[#\d+\].*)$` → `[ⓓ#645]` 라인은 게이트 출력·sidecar(`:255-291` 귀속 레코드만) 어디에도 없고, 게이트는 검사기를 임시 스냅숏에서 돌려 `.dddjango/violations/` 부산물도 버린다. 따라서 동봉은 **Coordinator 가 `check-public-surface-annotation.py <루트>` 를 별도로 직접 실행**해 `[ⓓ#645]` 를 «해당 범위» 경로로 거르는 방법뿐(BC 폴더 대상 실행은 `checker_target.bc_shaped_target_reason` 이 exit 1 거절 · 게이트 증거의 경로 필터 금지는 감사 입력엔 비적용). 이는 기존 #4 ⓓ#644 채널(«무조건 방출 — diff 한정은 감사자 몫» · `check-layer-skeleton.py:282`)과 완전 동형이라 **집행 불능 문면은 아니다** — 다만 두 채널 모두 «어떻게 얻는가» 가 Coordinator 문면에 없고, brownfield 에선 실행당 714/385행이 나온다(MINOR · 사후 문면 보강 후보).

## 3. 사용자 고지 항목(결정 밖 확장 — 머지 브리프에 실을 것)

1. **R-3449 «재수출 경유 포함» 조항**(③ C → 35fc29b · 규범만·검사기 무발화): 발주측 기존 레인 산출물 **4 BC·5파일·except 13**(query_translation·fortune_intent·fortune_calculation×2·notification)이 규범 위반 «빚» 이 되고, 승인 명세 2건(notification-bc·fc-2)이 «확립 선례» 로 명문화한 패턴과 정면 충돌한다 — ①·결정 1·2 어디에도 없던 정책 확장. 처분 선택지: (a) 유지 + 빚 등재(현행) (b) 재수출 경유 허용으로 문면 축소. rv5-C 도 사용자 결정 사안으로 표시(미확인 3).
2. **R-0284 rev3**(Coordinator step 5 필수 입력에 ⓓ#645 동봉): 결정 1 «후보는 감수자 판단» 의 배선이나 Coordinator 규범 개정이며, 얻는 방법(루트 직접 실행·범위 필터)은 문면에 없다(§2.6).
3. **«bare» 의 의미 확장**(Δ5·⑤ A → d9d76ac): ① 결론의 bare 정의(별표·`| None`·`Optional`·문자열·별칭)를 넘어 `Any | str`·`Union[Any, X]`·`Annotated[Any, …]`·미해소 `Any` 이름(import 없음·`import *`)까지 차단. 양 저장소 증분 **0**(78/121·10/14 불변)이라 소급 영향 없음.
4. **소급 수치**: 결정 시점 제시 «시그니처 bare 0 = spring 8/kkebi 10» 은 프로덕션 한정 — 검사기는 `test/{factories,fake}` 도 보므로 실제 red **10/14**(+factories 2/4).
5. **D·F-1·F-2·G 재형식화**는 ① 결론에서 «합의(사용자 결정 불요)» 로 분류돼 집행됐다 — 루브릭이 기록한 사용자 발화는 결정 1(«1»)·2(«확정»)뿐이라 이 4건의 명시 확정은 **미확인**(⑥ 뒤 «머지 진행» 게이트가 곧 그 확정 자리).
6. **Phase 0 빚 스캔 변화**: 릴리즈 뒤 spring 5 BC·kkebi 6 BC 의 Phase 0 스캔에 #645 항목(미러 13·실질 5·factories 6)이 새로 뜬다 — 미러 13·factories 6 은 `object` 기계 치환, 실질 5 는 좁힘 코드 작성.

## 4. 조건 목록(전부 브랜치 안 수리 가능 · 규범·검사기 무접촉)

| # | 조건 | 성격 | 수리 위치 |
|---|---|---|---|
| C1 | «전부 `object` 치환 가능» → «미러 13·factories 6 은 `object` 기계 치환 · 실질 5(kkebi `decision: Any`×2·saju JSON 순회 3)는 좁힘 수리» 로 정정 — 현장 보고 :14 E 행 · 로드맵 :59 R-19 · 루브릭 ④ :135(⑤ 표 :147 이 이미 반영됐다고 적고 있으므로 실물을 맞춘다) | 문서 정직성(MINOR 3곳) | 산문 파일 3 · 커밋 1 |
| C2 | 머지 브리프(10줄 이하)에 §3 고지 1~6 을 실어 사용자 확정 뒤 머지 — 특히 1(R-3449 재수출 조항·4 BC 빚)은 처분 (a)/(b) 선택지로 | 결정 게이트 | 브리프 |
| 권고(머지 뒤 가능) | `check-public-surface-annotation.py` docstring 검출 한계에 «프로젝트 모듈 재수출 `Any`(`from <pkg> import Any`) 무검출 · `Optional/Union/Annotated` 별칭 import 는 ⓓ 강등» 1행(+ codex byte 미러·symbol_kinds·봉인) · R-3449 «도메인 어휘로 이름» 단서 + discipline-reviewer 병기 · `tree-revision-spec.md:1174` «`Any` 와 None 의 합집합» → «`Any` 가 섞인 합집합» · 현장 보고 G 행에 위반 5파일 경로 병기 · Coordinator step 5 에 ⓓ 채널 획득법(루트 직접 실행·범위 필터) 1구 | MINOR | 별도 소배치 |

## 5. 머지 판정

**조건부 머지 가능** — C1(문서 3곳 정정) 브랜치 안 반영 + C2(§3 고지 6건을 실은 브리프에 사용자 확정) 뒤 main 로컬 머지. 규범·검사기·미러·도구는 전부 green 이고 무손실이 재실측으로 닫혔으며, 남은 것은 문서 정직성 1건과 결정 밖 확장의 고지뿐이다.
