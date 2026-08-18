# L1 — 온톨로지 공학 정합성 적대 리뷰 (블루프린트 v2, 2026-08-18)

- 심사 대상: `workspace/design/2026-08-18-ontology-blueprint-v2.md` (동결 후보)
- 렌즈: 차용했다고 주장하는 표준·원리(OBO P19·CURIE·replaced_by/consider·supersedes/updates·SHACL severity·gettext fuzzy·Duvet·OFT revision·COSS)가 **정확하게** 차용됐는가. 오해·오용·반쪽 차용(이름만 빌리고 의미를 어긴 것), 그리고 학습된 원리(부위별 처방·과형식화 경계·CWA 검증·행위/절차 비대상)와의 모순.
- 방법: 블루프린트·P0 센서스·R1~R7 전문 정독 + 저장소 실측(grep/Read — 예시 레코드의 anchor·quote·alias·enforcement 4개 조인을 코퍼스 원본과 대조).

## 판정 요약

차용의 **방향**은 대체로 충실하다. 그러나 서로 다른 표준을 이어붙인 **접합부 3곳에서 의미 충돌·표현 불가·기전 미정의**가 확인됐고, 커버리지 모델은 차용 원형(Duvet)의 단위를 문장→절로 강등해 회계가 성립하지 않으며, 스키마의 유일한 예시가 차용 모델(Duvet 원문 인용)의 핵심 의미론을 스스로 위반한다. 전부 동결 전 국소 수정으로 해소 가능한 수준(blocker 없음, major 5·minor 4).

---

## MAJOR (동결 전 수정 필요)

### F1. OBO P19와 OFT revision이 같은 사건(의미 변경)에 상반된 처방 — 경계 기준 부재

- **지적**: §2는 «의미가 실질 변경되면 새 ID + `replaced_by`»(L22, OBO P19·McMurry L7)와 «revision 정수(OFT): 의미 개정 시 +1»(L26)을 나란히 확정했는데, 두 규약은 동일한 트리거(의미 변경)에 대해 **양립 불가한 행동**(새 ID 발급 vs 같은 ID에 revision+1)을 지시한다. «실질 변경»과 «의미 개정»을 가르는 기준이 문서 어디에도 없다.
- **근거**:
  - OBO P19(R6 발견 1): 지시 대상이 실질적으로 바뀌면 기존 용어를 고치지 말고 새 IRI 발급. 기존 용어에서 허용되는 것은 명확화·문법·구두점 수준뿐.
  - OFT(R3 F3): revision은 ID의 일부(`req~name~1`)이며 의미가 바뀌면 revision을 올린다. 비의미 변경(마침표 추가)만 revision 불변.
  - 즉 OBO에서는 «의미 변경 = 새 ID»가 전부이고, OFT에서는 «의미 변경 = revision+1»이 정상 경로다. 블루프린트는 ID(`DJR-0417`)와 revision을 분리 필드로 뒀으므로(§3 L32·34) OFT의 «revision이 곧 새 ID» 성질도 잃었다.
  - 표류는 정확히 이런 애매 경계에서 발생한다는 것이 P0의 실증(«updates 미기록» 유형 2건 — 블루프린트 L25가 스스로 인용).
- **수정안**: 경계를 한 줄로 명문화하고 lint 대상화. 예: «지시 대상(무엇에 대한 규칙인가)이 바뀌면 새 ID + `replaced_by`(구 레코드 deprecated) / 지시 대상 유지 + 규범 강도·범위·문구의 의미 개정이면 같은 ID revision+1 / 명확화·오탈자면 revision 불변». S3 등재 심사 체크리스트에 이 3분류를 포함.

### F2. §2가 확정한 승계 문법(replaced_by/consider)·차용 어휘(deprecated)를 §3 스키마가 표현하지 못함

- **지적**: D1(L14)은 «어휘는 OBO/OWL 표준에서 차용: status·deprecated·replaced_by·severity»를 확정하고 §2(L25)는 `replaced_by`(자동 추종) vs `consider`(사람 심의)의 구분을 승계 문법으로 확정했는데, §3 스키마(L30~55)에는 **`replaced_by`·`consider`·`deprecated`(폐지 메타데이터) 필드가 없다.** 관계 필드 `related`(L53)의 타입 열거는 `supersedes|updates|renamed|similar`뿐이라 OBO 승계 문법을 담을 자리가 없다.
- **근거**: §3 스키마 전문 필드 목록 — id·title·revision·status·severity·owner·doc·enforcement·coverage·twins·aliases·related·ext. 폐지 시점·사유(`deprecatedSince`·reason — R1 C-2/R6 발견 4d의 ESLint 차용 권고) 자리도 없다. 스키마는 «JSON Schema + registry lint가 집행»(L58)하는 확정 대상이므로, 표현 불가 필드는 곧 규약 사문화다. 특히 replaced_by/consider 구분은 «에이전트가 폐지 규칙을 만났을 때 자동으로 따라갈지 사람에게 물을지»(R1 C-1)라는 이 설계의 소비자 편익 핵심인데 그 편익이 스키마에서 실종됐다.
- **수정안**: `related` 타입에 `replaced_by`·`consider`를 추가하거나 별도 최상위 필드로 승격 + `deprecated: {since, reason}` 블록 추가 + supersedes↔replaced_by 역방향 대칭을 registry lint 검사 항목으로 명문화(R6 발견 3의 PEP `Replaces`/`Superseded-By` 양방향 관례).

### F3. OFT revision 차용이 반쪽 — 인용 측에 revision이 없어 «Outdated 강등» 기전이 정의 불가

- **지적**: §2(L26)는 «의미 개정 시 +1 → 그 ID를 인용하는 검사기·미러 절이 전부 Outdated로 강등(개정 전파의 기계화)»를 확정했지만, 검사기 측 표기는 `Rule-ID:`(§4.1 L62)뿐이고 §3 enforcement(L41~46)에도 «인용 시점의 revision»을 기록하는 자리가 없다. **OFT의 강등 기전은 링크가 revision을 포함하기 때문에 작동한다**(`[impl->dsn~x~1]` — 옛 revision을 지목하는 링크가 Outdated로 판정되고, 재검토 후 링크의 revision을 올려 해제). 인용에 revision이 없으면 (a) 무엇이 Outdated인지 판별할 근거가 없고 (b) 재검토 완료를 표시해 강등을 해제할 방법도 없다.
- **근거**: R3 F3(OFT 링크 오류 분류학 — Covers/Predated/Outdated는 전부 revision 지목 대조로 정의됨). 부가로 R3 반례 4(«revision 증가는 수동 판단이라 잊으면 표류 미검출 — 인용문 해시 대조와 병용해야»)가 v2에 반영되지 않았다: twins에는 `norm_hash`(L50)가 있으나 enforcement 축에는 대응물이 없어, doc.quote와 문서를 같은 커밋에서 함께 고치고 revision을 안 올리면 검사기는 아무 신호 없이 «현행»으로 남는다.
- **수정안**: ① `Rule-ID: DJR-0417@2`처럼 인용에 revision 명기(§4.1 정형구 정의에 포함), enforcement 항목에도 `attested_revision` 기록 → lint가 레코드 revision과 대조해 Outdated 판정, 재검토 후 인용 갱신으로 해제. ② `doc.quote` 변경 커밋에 revision 미증가면 registry lint가 차단(명확화 예외는 사유 필드로 등기) — 수동 망각의 기계 보완.

### F4. 커버리지 4값 등기의 단위가 절(606) — Duvet 원형의 요구 단위(규범 문장)에서 강등되어 «대차 0 마감»이 회계로 성립하지 않음

- **지적**: §4.2(L63)와 S2 완료 기준(L96)은 «모든 규범 절이 4값 중 **하나로** 등기돼 대차 0 마감 / 606절 전수 4값 등기»다. 그러나 차용 원형 Duvet의 요구 단위는 **개별 규범 문장**(RFC 2119 키워드 문장 자동 추출 — R3 F2)이고, MISRA deviation도 지침 단위다. P0 실측이 바로 이 강등의 위험을 문서화했다: ninja §6.2 한 절에 규범 85문장, tdd §5.5에 57문장(센서스 §2-① «해상도 부족 실증», 횡단 3 «밀도 편중»). 절 단위 단일값 아래에서는 «85문장 중 1문장만 enforced인 절»이 무엇으로 등기되든 나머지 문장들이 장부에서 사라진다 — 설계가 드러내겠다던 «불명 66%»가 절 내부로 숨을 뿐이다.
- **근거**: 블루프린트 자신의 예시도 이 문제를 노출한다 — §3 예시 레코드의 enforcement는 checker+delegated 혼합(L41~46)인데 `coverage: enforced` 단일값(L47)이고, 혼합 시 우선순위 규칙이 없다.
- **수정안**: ① 등기 단위를 «절 내 커버리지 항목 복수 허용»(문장 범위 또는 인용문 단위)으로 정의하거나, ② 절 단일값을 유지하려면 «절값 = 구성 문장의 최약값(worst-of) + 예외 문장 명시 등기» 규칙을 S2 착수 전에 확정. 최소한 혼합 절·혼합 enforcement의 판정 규칙을 동결본에 명문화.

### F5. 스키마 유일 예시가 삼각 대조 4조인 중 3개 불일치 — Duvet 인용 의미론을 예시가 스스로 위반

- **지적**: §3 예시 레코드(DJR-0417)의 실측 대조 결과:
  - `doc.anchor` «architecture-ddd/references/final.md §3.2 “판정 소유→구조 이주”» — **일치**(해당 단락은 final.md L636, §3.2 말미에 실재).
  - `doc.quote` «도메인 판정은 도메인 계층이 소유한다» — **코퍼스 어디에도 없는 문장**(원문 근접 문장은 «판정·불변식은 도메인이 소유하고 프로덕션 경로에서 실행된다(빈혈 차단)», final.md L632). Duvet 모델에서 인용문은 요구의 정체성 그 자체이며 lint가 **원문 정확 일치**로 대조한다(R3 F2) — 의역 인용은 차용 모델의 핵심 의미론 위반이고, §3 주석 «lint가 원문 대조»(L38)와도 자기모순.
  - `aliases`의 «의사결정#3(ddd)» — 실제 ddd 의사결정 #3은 «애그리거트가 도메인 서비스를 모르도록 분리한다»(final.md L901)로 판정 소유와 무관. **오귀속.**
  - `enforcement.ref` `check-transaction-boundary.py` — 이 검사기의 docstring 담당 규칙(#4·#195·#197·#200·#282·#283·#285·#287·#355·#597·#599)에 판정 소유/재판정 규칙 없음. rule-owner-map에도 «판정 소유» 항목 부재. **오귀속.**
- **왜 major인가**: S3 완료 기준이 «삼각 대조(레지스트리↔검사기↔문서) green»(L97)인데, 동결본의 유일한 시연 예시가 그 대조에서 3/4 실패한다. 특히 의역 quote는 «paraphrase도 된다»는 잘못된 용법을 S3 등재자에게 가르친다.
- **수정안**: 예시를 전부 실측값으로 교체(quote는 원문 그대로, alias·enforcement는 실제 대응) 하거나, 값들이 가공임을 명시하되 quote만은 반드시 실존 원문으로 시연.

---

## MINOR (기록)

### F6. 어휘 «표준 차용» 표기의 부정확 3건 — 값 집합·출처가 실제 표준과 어긋남

- `severity: gate-blocking | advisory | info (SHACL 관례 차용)`(L36): SHACL의 severity 값은 `sh:Violation|Warning|Info`이고, **명세상 severity는 적합성 판정에 영향을 주지 않는 주석**이다(적합성은 결과 존재 여부로 결정). 여기서는 severity가 게이트 판별자다 — 차용된 것은 표준이 아니라 도구 실무 관행(위반 등급으로 CI 차단)이며, 값 이름도 3개 중 1개(info)만 겹친다. «관례» 표기로 선해 가능하나, D1의 차용 동기(형식 전환 비용 절감 — R6 발견 2 추론)를 값 어휘 발명이 상쇄한다.
- `status: draft|active|deprecated|retired|complete`(L35): D1은 OBO/OWL 차용이라 했으나 실체는 COSS 5상태의 개명(Raw/Draft/Stable→draft/active)+R6 권고(complete)다. OBO/OWL에는 이런 status 값 어휘가 없다(용어 수준은 `owl:deprecated`뿐). 5값의 정의·전이 조건도 동결본에 없다.
- «전면 대체는 `supersedes`(RFC)»(L25): RFC의 전면 대체 관계어는 **Obsoletes**다(R1 B-2). supersedes는 ADR·schema.org 어휘. 의미론(전면/부분 구분)은 맞고 이름 출처만 오표기.
- (부수) «CURIE 호환(djr:0417)이라 RDF 투영 시 그대로 IRI가 된다»(L21): CURIE→IRI는 접두 바인딩(네임스페이스 URI) 등록이 있어야 성립(McMurry L2·OBO id-policy). 바인딩 예약 언급 부재 + `DJR-0417`/`djr:0417` 두 표면형 병존은 표기 통일 규칙 1줄이 필요.
- **수정안**: D1 표를 «표준 **의미론** 차용 + 자체 값 어휘»로 정정하고, 각 필드에 출처 주석을 실제 원천(COSS·SHACL 실무 관행·RFC Obsoletes 의미)으로 바로잡는다.

### F7. «alias→ID 전단사성» 용어 오류 — 예시 자체가 전단사가 아님

- §2(L24) lint 요구 «alias→ID 전단사성과 미흡수 잔여 참조 검사»: 같은 줄의 예시가 alias 4개→ID 1개(다대일)라 전단사(1:1 대응)가 원리적으로 성립하지 않고, 신규 규칙은 alias 0개다. 실제 요구는 **유일 해소**(각 alias가 정확히 하나의 ID로 해소 — 한 alias가 두 레코드에 등장 금지) + 미흡수 잔여 0. lint 스펙 문구이므로 구현 오도 위험이 있어 기록.
- **수정안**: «전단사성» → «유일 해소(함수성)»로 교체.

### F8. §5 내부 긴장 — K8s triage(게이트 아님) 차용과 «CI 차단은 결정 신호(해시·**잔차 존재**)만»의 충돌 독해

- L70은 잔차를 «신호 등급 리포트(K8s triage 모델 — **완전 자동 게이트가 아니라** 사람 결정 보조)»로 규정하는데, L71은 «CI 차단은 결정 신호(해시·잔차 존재)만»이라 하여 잔차 존재가 차단 신호로 읽힌다. 잔차 존재가 차단이면 그것이 곧 자동 게이트라 차용 모델(R4 B-4: 결정적 신호 추출→등급→사람 결정, «Automation should protect reviewer attention»)과 어긋나고, 아니면 어떤 결정 신호가 차단인지 미정의.
- **수정안**: 차단 신호(예: 해시 불일치=fuzzy 미해제 상태)와 리포트 신호(잔차 등급)를 명시적으로 분리해 한 줄로 확정.

### F9. gettext fuzzy 반쪽 차용 — fuzzy 상태의 배포·소비 의미론 부재

- gettext 모델에서 fuzzy는 표시로 끝나지 않는다: **fuzzy 엔트리는 기본적으로 빌드에서 제외**되고 원문으로 폴백된다(msgfmt 기본 동작·mdbook-i18n — R4 B-2 «확인 안 된 미러는 배포하지 않고 정본 폴백»). D4(L17)·§5는 표시(자동 true)+사람 해제만 차용했고, fuzzy 동안 stale codex 절이 계속 소비·배포되는지, 릴리즈가 차단되는지 미정의다. R4 시사점 5(«낡은 규범은 미번역보다 해롭다 — 정본 폴백 검토»)가 v2에 미반영. Stage 세부 계획에서 보완 가능하므로 minor로 두되, F8의 차단 신호 확정과 함께 정하면 한 번에 끝난다.
- **수정안**: fuzzy 미해제 상태의 정책 1줄 명문화(릴리즈 게이트 차단 / 정본 폴백 / 명시적 수용 중 택1).
- (연관 기록) §7 L87 «배포본(claude/codex)은 무버전 정본의 날짜 스냅샷 파생물(schema.org 모델)»은 과도기(D4: 두 판 수기 유지+대조)에는 사실이 아니고 수렴기(단일 정본+조건부 렌더)에만 성립 — «수렴기 이후» 한정어가 없으면 동결본의 두 조항이 서로 다른 현재를 주장한다.

---

## 반박 불성립 확인 (성립하지 않는 지적은 성립하지 않는다고 쓴다)

1. **학습된 원리 4종과의 모순 — 발견하지 못함.** 부위별 처방(D2 축별 처방·분류 축 보류), 과형식화 경계(승격 사다리·일몰 조건 §8 L101), CWA 검증(4값 전수 등기·대차 0 마감은 닫힌세계 검증의 정당한 적용), 행위/절차 비대상(§7 자기 등록은 절차 문서에 ID·상태 메타데이터를 붙이는 것이지 절차 내용의 형식화가 아님 — C4 원형과 동일) 모두 위반 없음.
2. **OBO replaced_by/consider의 의미 구분 자체**(자동 추종 vs 사람 심의)는 정확한 차용이다 — 문제는 스키마 표현 부재(F2)뿐.
3. **MISRA deviation 차용**(§3 L44 «명시된 위임»)은 «필드 차용»으로 명시 한정돼 있고, R3 F7이 이미 이 재해석(위임 등기)을 검증했다 — 의미 오용 아님.
4. **Duvet 래칫 차용**(§4.3): 스냅샷 체크인+CI 대조는 Duvet `--ci`와 정확히 동형 — 정당.
5. **COSS 1인 편집자 차용**(§7): COSS가 명세별 단일 책임 편집자·상태 전이 독점을 명문화한 것과 정확히 일치 — 정당. (상태 값 어휘의 출처 오표기는 F6에서만.)
6. **S1 미러 lint의 ID 선행 문제**: R4는 «gettext 모델은 단위 쌍(ID) 필수»라 했으나 블루프린트는 S1을 문서쌍 전체 정규화 대조(ID 불요)로, 절 단위 fuzzy는 ID 도입 후(§5 L72)로 순서를 명시 분리했다 — 연구 §3의 긴장 해소가 설계에 정확히 반영됨. 반박 불성립.

## 실측 검증 기록

- `check-transaction-boundary.py` 실재 확인(`dddjango/scripts/`), docstring 담당 규칙 11종 목록 확인 — 판정 소유 규칙 부재.
- «도메인 판정은 도메인 계층이 소유한다» 코퍼스 전문 grep — 0건. 원문 근접 문장은 architecture-ddd final.md L632.
- «판정 소유→구조 이주» 단락 위치 L636, §3.2(L539)~§3.3(L638) 사이 — anchor는 정확.
- ddd 의사결정 #3 = final.md L901 «애그리거트가 도메인 서비스를 모르도록 분리한다».
- rule-owner-map(`workspace/plan/2026-08-11-rule-owner-map.md`) 실재, «판정 소유» 항목 grep 0건.

Serena: skipped — 문서 검토 작업(코드 심볼 작업 아님)이라 기본 도구로 충분.
