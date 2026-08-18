# R6 — 거버넌스·개정·수명주기

조사일: 2026-08-18 · 담당: 레인 R6 (외부 자료 조사) · 도구: WebSearch/WebFetch(1차 출처 우선)

## 조사 질문

소규모(1인 심의)로 유지되는 규칙·온톨로지 정본의 개정 거버넌스 검증 관행은 무엇인가?
— 탐색 축: OBO Foundry 원칙, 온톨로지 버저닝(owl:deprecated·versionInfo), ADR supersede, RFC 프로세스 경량화 변형, schema.org 개정 프로세스, 규칙 lifecycle 상태 기계. 특히 «동결하되 개정 절차 내장» 관행, 1인 심의 형식화의 성공/실패 실증, 죽은 온톨로지의 원인 목록.

표기 규약: 【사실】 = 출처에서 확인된 내용, 【추론】 = 본 조사자의 해석. 각 발견 끝에 «dddjango 시사점» 1줄.

---

## 발견 1. OBO Foundry — 불변 ID·삭제 금지·obsolete 마킹이 정본 안정성의 뼈대

【사실】 OBO Foundry 원칙 P19(용어 의미 안정성)는 다음을 규정한다(현행, 2020년대 지속 개정):

- 용어의 지시 대상이 실질적으로 바뀌면 기존 용어를 고치지 말고 **새 IRI를 발급**한다. 명확화·문법·구두점 수준의 개선만 기존 용어에서 허용.
- 용어는 **삭제하지 않고 obsolete 처리**한다: `owl:deprecated true` 표기, 라벨에 `obsolete ` 접두사(소문자+공백까지 규격), 논리 공리 전부 제거, 타 용어에서의 참조 제거.
- 대체 관계를 구조화 메타데이터로 남긴다: 정확한 대체는 `replaced_by`, 부정확한 후보는 `consider`.
- 변경은 원칙 13(변경 공지)에 따라 사전 공지하고 단계적으로 폐기한다.

【사실】 ID 정책: 모든 용어 ID는 `IDSPACE:LOCALID` 형태 CURIE이고, PURL(`http://purl.obolibrary.org/obo/IDSPACE_LOCALID`)과 **예측 가능한 양방향 매핑**이 존재해야 한다. IDSPACE 선정 시 타 레지스트리와의 충돌 확인이 요구된다.

출처:
- https://obofoundry.org/principles/fp-019-term-stability.html
- http://obofoundry.org/id-policy.html

【추론】 P19의 본질은 "ID는 의미에 결박된 불변 계약"이라는 것. 의미가 바뀌면 ID를 고치는 게 아니라 ID를 새로 발급한다 — ID 공간의 무결성을 사람의 기억이 아니라 절차가 지킨다.

«dddjango 시사점» 규칙 단위 ID를 새로 도입하는 지금이 "삭제 없음·obsolete 마킹·replaced_by 포인터·의미 실질 변경=새 ID"를 상태 모델에 처음부터 내장할 유일한 기회다(사후 소급은 5종 번호 공간 혼용이 증명하듯 실패한다).

## 발견 2. 버전 표기 — OBO P4와 OWL 2의 표준 어휘

【사실】 OBO 원칙 P4(버저닝): 온톨로지 제공자는 **문서화된 버저닝 절차를 반드시(MUST)** 갖춰야 하고, 버전 식별자는 날짜형(`YYYY-MM-DD`) 또는 번호형(semver류 `NN.n`) 중 하나여야 하며, 각 버전은 표시·보관·공식 릴리스되어야 한다.

【사실】 OWL 2 구조 명세(W3C 권고, 2012)는 버전 관련 표준 어휘를 정의한다:

| 어휘 | 의미 |
|---|---|
| ontology IRI + versionIRI | 정본 위치(무버전)와 특정 버전 위치의 이원화. 현재 버전은 두 IRI 모두에서 접근 가능해야 함 |
| `owl:versionInfo` | 버전 설명 문자열 |
| `owl:priorVersion` | 직전 버전 IRI |
| `owl:backwardCompatibleWith` / `owl:incompatibleWith` | 호환·비호환 이전 버전 명시 |
| `owl:deprecated` | `true`면 해당 IRI 사용 중단 표시 |

출처:
- http://obofoundry.org/principles/fp-004-versioning.html
- https://www.w3.org/TR/owl2-syntax/#Ontology_IRI_and_Version_IRI

【추론】 이 어휘는 RDF를 채택하지 않아도 **필드명 차원에서 차용 가능**하다. D1(RDF/Turtle+SHACL vs YAML 자체 형식)이 어느 쪽으로 결정되든, 거버넌스 필드의 이름과 의미론을 표준에서 빌리면 나중에 형식을 갈아타도 의미가 보존된다.

«dddjango 시사점» dddjango의 기존 날짜 스탬프 준-ID는 OBO P4의 날짜형 버전과 자연 정합 — 버리지 말고 릴리스 식별자로 승격시키되, 규칙 ID와는 역할을 분리하라.

## 발견 3. «동결하되 개정 절차 내장» — IETF RFC·PEP·ADR의 3가지 변형

【사실】 IETF RFC: **출판된 RFC는 절대 수정되지 않는다**("once an RFC is published, it is never changed"). 수정이 필요하면 새 RFC가 기존 것을 `Obsoletes`(전체 대체) 또는 `Updates`(부분 수정)한다. 오류는 본문을 고치지 않고 별도 errata 데이터베이스(Verified/Rejected/Held for Document Update 상태)로 처리한다. RFC 번호는 재사용되지 않는다.
출처: https://www.ietf.org/process/rfcs/

【사실】 PEP 1(Python, Active 문서로 지속 개정): PEP 상태는 Draft/Active/Accepted/Provisional/Final/Deferred/Rejected/Withdrawn/Superseded 9종. Accepted·Final·Rejected·Superseded 도달 후엔 실질 수정 금지("역사적 문서" 취급). 단 **Process·Informational 유형의 "Active" PEP은 계속 수정 가능** — 완결되는 결정 문서와 살아있는 절차 문서를 유형으로 구분한다. 대체는 새 PEP의 `Replaces` 헤더 + 원본의 `Superseded-By` 헤더로 양방향 링크.
출처: https://peps.python.org/pep-0001/

【사실】 ADR(Nygard 2011 계보): 상태는 최소 proposed→accepted→deprecated/superseded. **accepted 후 내용은 불변**이고, 결정 변경은 새 ADR 작성 + 구 ADR의 상태를 superseded로 바꾸며 양쪽 파일에 상호 링크를 남기는 방식으로만 한다. ADR의 집합이 프로젝트의 결정 로그(decision log)를 구성한다.
출처: https://adr.github.io/ , https://csse6400.uqcloud.net/handouts/adr.pdf

【추론】 세 관행의 공통 핵심: **본문 동결 + 메타데이터(상태·supersede 링크)만 가변 + 개정은 새 문서 발행이라는 단일 절차**. 그리고 PEP의 기여는 "모든 문서가 동결 대상은 아니다"라는 유형 구분 — 결정 기록은 동결하고, 살아있는 규범 산문은 Active로 계속 고친다.

«dddjango 시사점» 의사결정 #N 계열은 ADR/RFC형(동결+supersede 체인)으로, 스킬 문서 산문 본문은 PEP-Active형(계속 개정, 단 레지스트리 뼈대와 lint 대조)으로 — 문서 유형별로 동결 정책을 이원화하라.

## 발견 4. 규칙 수명주기 상태 기계의 실전 설계 4종

### 4a. COSS — 1인 편집자를 명시적으로 내장한 명세 수명주기

【사실】 COSS(Consensus-Oriented Specification System, ZeroMQ 계열): 상태는 **Raw → Draft → Stable → Deprecated → Retired**(+ Raw/Draft에서 폐기 시 Deleted). 전이 조건이 구현·사용 증거에 결박된다: Raw→Draft는 구현이 생겼을 때, Draft→Stable은 제3자가 사용할 때, Stable→Deprecated는 새 Draft가 대체할 때. **Stable에서는 미용적 수정·오류 정정·명확화만 허용**, 실질 변경은 새 명세로 분기. 각 명세는 **단 한 명의 책임 편집자**를 갖고 그 편집자만 수명주기 상태를 전이시킨다. 참조는 `<도메인>/spec:<번호>` 형식, 분기하면 새 번호.
출처: https://github.com/unprotocols/rfc/blob/master/2/README.md , https://rfc.zeromq.org/spec/2/

### 4b. Rust RFC — 결정 순간을 명시적 이벤트로 만드는 FCP

【사실】 Rust RFC 수명주기: 토론 → 팀원이 처분(merge/close/postpone)을 명시한 **FCP(Final Comment Period, 10일)** 발의 → 병합 → tracking issue에서 구현 논의 → 안정화도 다시 FCP 결정. rfcbot이 비동기 의사결정 상태를 기계로 관리한다.
출처: https://rust-lang.github.io/rfcs/ , https://github.com/rust-lang/rfcs

### 4c. Oxide RFD — 소기업용 초경량 변형

【사실】 Oxide Computer의 RFD(Request for Discussion, 2020년대 현행): 상태는 **prediscussion / ideation / discussion / published / committed / abandoned** 6종. 순차 4자리 번호. "완성도보다 시의성" — **한 문장짜리도 유효한 RFD**. published 이후에도 개정 브랜치(`0001_rfd_modification`)로 수정 가능, 토론은 원 PR에서 지속. 회사 프로세스 변경·아키텍처 결정·API 변경·내부 도구까지 하나의 제도로 커버.
출처: https://rfd.shared.oxide.computer/rfd/0001

### 4d. ESLint — 기계가독 폐지 메타데이터(검사기 생태계의 규칙 lifecycle)

【사실】 ESLint의 규칙 폐지 메타데이터(신형 `DeprecatedInfo`, 2024~ 도입): `deprecatedSince`(폐지 버전), `availableUntil`(제거 예정 버전, **`null`이면 영구 보존**), `replacedBy`(대체 규칙 배열 — **빈 배열로 "대체 없음"을 명시적으로 표현**), `message`(폐지 사유), `url`. 폐지 표시는 minor에서, 실제 삭제는 다음 major에서만 허용. typescript-eslint도 별도의 문서화된 deprecation/rename/deletion 정책을 운영한다.
출처: https://eslint.org/docs/latest/extend/rule-deprecation , https://github.com/eslint/eslint/pull/19238 , https://typescript-eslint.io/maintenance/issues/rule-deprecations-and-deletions/

【추론】 4종을 포개면 dddjango 규칙 레코드의 최소 필드가 도출된다: `status`(draft/active/deprecated/retired) + `deprecatedSince` + `replacedBy`(빈 값 허용) + supersede 양방향 링크. COSS는 "1인 편집자 + 상태 전이 권한 독점"이 표준 문서에 명문화될 수 있음을 보여주는 직접 선례고, ESLint는 이 메타데이터를 **검사기가 소비**하는 실증이다.

«dddjango 시사점» 검사기 25종이 docstring으로 규칙을 역지목하는 현 구조에서, 레지스트리의 규칙 레코드에 ESLint형 기계가독 lifecycle 필드를 넣으면 문서→검사기 방향 0 문제를 lint가 양방향 대조로 메꿀 수 있다.

## 발견 5. schema.org — 삭제 없는 어휘 + pending 멜팅팟 + 1인 웹마스터 운영

【사실】 schema.org 개정 프로세스(현행):

- 용어는 사실상 제거되지 않고 **`supersededBy` 속성으로 표시**되어 구·신 용어의 관계가 어휘 안에 남는다.
- 승인 전 제안은 **pending 영역**(별도 네임스페이스)에 먼저 공개되어 나란히 검토된다 — 정본 오염 없이 후보를 노출하는 "멜팅팟".
- 릴리스 절차: 커뮤니티 토론(GitHub·W3C CG) → **웹마스터 1인**이 릴리스 후보 준비 → 스티어링 그룹 검토, 10 영업일 내 무이의면 배포. 일상 운영·후보 구현·제안 종합은 웹마스터 1인의 역할로 명문화되어 있다.
- 소비자에게는 **무버전 URL**(https://schema.org/Place) 사용을 권장하고, 각 릴리스는 날짜 스냅샷으로 따로 보존("용어 의미는 급격히 변하지 않는다"는 점진 진화 계약).

출처: https://schema.org/docs/howwework.html , https://www.w3.org/community/schemaorg/how-we-work/work-in-progress-mechanisms-webschemas-and-the-pending-area/

【추론】 "무버전 정본(살아있는 최신) + 날짜 스냅샷(배포)"의 이원화는 dddjango의 정본(스킬 문서·레지스트리) vs 배포본(claude/codex 두 판) 구조와 정확히 동형이다. 두 판 미러의 표류 2건은 schema.org 어법으로 말하면 "스냅샷이 정본에서 파생되지 않고 각자 정본 행세"하는 상태다.

«dddjango 시사점» 배포본은 정본의 스냅샷 파생물임을 절차로 강제하고(파생 방향 단일화), pending류의 "후보 규칙" 상태를 두면 정본 오염 없이 제안을 굴릴 수 있다.

## 발견 6. 1인 심의 형식화 — 성공과 실패의 실증

### 성공 사례

【사실】 SQLite: "open-source, not open-contribution" — 외부 패치를 받지 않고(공개 도메인 서약 없는 패치 거부), Hwaci 소속 소수 개발자만 커밋하며, 외부 제안은 팀이 처음부터 재작성한다. 극소수 인원 + 강한 내부 형식 절차(전량 추적 가능한 원저자, 오염 없는 코드베이스)로 수십 년 유지.
출처: https://www.sqlite.org/copyright.html

【사실】 Python BDFL 모델: 1인 최종 심의자(Guido) + 형식화된 PEP 절차의 조합이 1991~2018년까지 언어 정본을 지탱했다 — 1인 심의가 형식 절차와 결합하면 장기간 작동한다는 실증.

### 실패·한계 사례

【사실】 2018년 7월, Guido van Rossum은 PEP 572 논쟁의 소모전 끝에 BDFL 사임("so many people despise my decisions… 스스로에게 영구 휴가를 준다"). 후계 규정이 없어 거버넌스 공백이 생겼고 핵심 개발자들이 새 모델(스티어링 카운슬, PEP 8016)을 사후에 만들어야 했다.
출처: https://lwn.net/Articles/759654/ , https://lwn.net/Articles/759756/

【사실】 xz-utils 백도어(CVE-2024-3094, 2024): 1인 무급 유지자의 소진 상태에서, 위장 계정들이 "릴리스가 느리다·유지가 안 된다"는 압박을 조직적으로 가해 공동 유지자 추가를 유도했고, 2.6년의 신뢰 축적 끝에 심의권이 비형식적으로 이양되어 백도어가 주입됐다. 심의권 이양에 절차가 없던 것이 공격 표면이었다.
출처: https://securelist.com/xz-backdoor-story-part-2-social-engineering/112476/

【사실】 Tidelift 2024 유지자 설문(응답 437명): 무급 유지자의 61%가 1인 유지, 약 60%가 프로젝트 유지 중단을 했거나 고려, 43%가 개인 스트레스 가중을 보고.
출처: https://www.businesswire.com/news/home/20240917030299/en/ , https://assets-eu-01.kc-usercontent.com/ef593040-b591-0198-9506-ed88b30bc023/d325a56f-05be-4379-bfd1-ee4776fcad41/2024-tidelift-state-of-the-open-source-maintainer-report-.pdf

【추론】 실패 사례들의 공통 원인은 "형식 절차의 존재"가 아니라 **1인에게 걸리는 심의 부하와, 그 1인이 빠졌을 때를 규정하지 않은 것**이다. 성공 사례(SQLite·BDFL기 Python·COSS의 1인 편집자)는 모두 1인 권한을 숨기지 않고 명문화했다. 즉 1인 심의는 결함이 아니라 명문화 대상이다.

«dddjango 시사점» 소유자 1인을 레지스트리에 명시 필드로 박고(COSS의 editor처럼), 심의 부하는 사람이 아닌 결정적 검사기·lint에 전가하는 설계가 1인 프로젝트의 지속 조건이다.

## 발견 7. 죽은 온톨로지의 실증 원인 목록

【사실】 Geller·Keloth·Musen, "How Sustainable are Biomedical Ontologies?" (AMIA, 2018): BioPortal 716개 온톨로지 중 약 **47%가 2016-01 이후 미갱신**. 대형(개념 1,000+) 미갱신 83개에 이메일 조사(응답 48개):

| 유지 중단 원인 | 비율 |
|---|---|
| 자금·인력 부족 | 31.25% |
| 다른 온톨로지로 통합(folding) | 18.75% |
| 느린/간헐적 개발 | 14.58% |
| 조직·프로젝트 종료 | 12.5% |
| 논문 발표 후 재설계 중 | 6.25% |
| **개념적 완성 도달(정당한 종료)** | 6.25% |
| 실제로는 개발 지속, 레지스트리만 미갱신 | 6.25% |

권고: 프로젝트 초기에 장기 유지보수 계획을 수립하라.
출처: https://pmc.ncbi.nlm.nih.gov/articles/PMC6371329/

【사실】 OBO Foundry는 **온톨로지 전체 단위에도 상태 기계**를 운영한다: active / inactive / unresponsive / orphaned / obsolete — 축은 Maintenance(P16, 편집 활동 여부)와 Responsiveness(P20, 연락 가능한 담당자 존재) 2개. 재활성화는 최근 활동 증거를 첨부한 메타데이터 PR로만 가능하다. obsolete는 상위 기관이 아니라 프로젝트 스스로 선언하는 특수 상태다.
출처: https://obofoundry.org/docs/OntologyStatus.html , https://pmc.ncbi.nlm.nih.gov/articles/PMC8546234/ (OBO Foundry in 2021, 2021)

【추론】 죽음의 1순위 원인은 절차 부재가 아니라 **유지 자원의 소멸**이다. 1인 프로젝트 번역: 유지자의 시간·관심이 절차 유지 비용을 감당 못 하는 순간 정본이 죽는다. 따라서 절차의 러닝 코스트를 최소화하고 집행을 자동화하는 것이 곧 생존 설계다. 또 "완성 도달"과 "레지스트리만 미갱신"이 합쳐 12.5% — 죽은 것처럼 보이는 상태와 실제 죽음을 구분하는 상태(예: complete/frozen)가 필요하다.

«dddjango 시사점» 규칙 상태 기계에 deprecated와 별개로 "완성·동결(complete)"을 정당한 종료 상태로 두고, '활동 없음=죽음'으로 오판하지 않게 하라.

## 발견 8. C4 — 거버넌스 문서 자신이 수명주기를 따르는 자기 적용

【사실】 ZeroMQ C4(Collective Code Construction Contract, Hintjens, 2012~): "올바른 패치란 무엇인가·어떻게 병합되는가"를 계약으로 형식화한 거버넌스 명세인데, 이 명세 자체가 RFC 번호와 deprecation 체인을 가진다 — 22/C4 → 42/C4(rev.2, 22를 deprecate) → 44/C4(rev.3, 42를 deprecate). 거버넌스 규칙의 개정도 일반 명세와 같은 절차(COSS)로만 이뤄진다.
출처: https://rfc.zeromq.org/spec/42/ , https://rfc.zeromq.org/spec/44/

«dddjango 시사점» dddjango의 개정 절차 문서 자체를 레지스트리의 규칙 레코드(ID·상태 보유)로 등록해 자기 적용시키면, "변경은 절차로만"이 절차 문서에도 강제된다.

---

## 반례·주의

1. **"영구 보존"은 공짜가 아니다.** ESLint조차 폐지 규칙을 major에서 삭제할 수 있게 열어 두었다(`availableUntil=null`은 옵션이지 기본이 아님). OBO식 "절대 삭제 금지"는 외부 참조가 통제 불능인 공공 어휘의 조건이다. dddjango의 소비자(에이전트·검사기·lint)는 전수 파악 가능하므로, retired 레코드의 본문을 아카이브로 옮기는 절충이 가능하다. 【추론 포함】
2. **형식 절차는 그 자체가 부채가 된다.** Rust RFC는 규모가 커지자 병목·미결 적체 문제로 단계형 프로세스 재설계 제안이 나왔다(Matsakis, 2018: https://smallcultfollowing.com/babysteps/blog/2018/06/20/proposal-for-a-staged-rfc-process/ ). 1인 프로젝트에 FCP류 대기 기간·다단 승인은 무의미한 의식(儀式)이 된다 — 형식은 상태·기록·기계 검증에 두고, 시간 지연과 합의 의식은 빼야 한다. 【추론 포함】
3. **schema.org의 무이의 승인(lazy consensus)은 심의자가 복수일 때의 장치다.** 1인 프로젝트의 "셀프 무이의"는 형식만 남는다. 대신 그 자리를 lint 게이트(통과해야 병합)가 맡는 것이 구조적 등가물이다. 【추론】
4. **BioPortal 원인 목록의 이식 한계.** 자금·인력(31%)은 학술 온톨로지 맥락의 원인이고, 1인 도구 프로젝트의 대응물은 "유지자의 시간·관심"이다. 원인 목록을 그대로 리스크 목록으로 복사하면 안 된다. 【추론】
5. **상태 기계도 진행형이다.** OBO의 온톨로지 상태 정의조차 운영위원회가 아직 정련 중이다(문서에 명시). 처음부터 완결된 상태 기계를 조각하려 들지 말고, COSS처럼 상태 수를 적게(5±1) 시작하는 편이 실증에 부합한다. 【사실+추론】
6. **ADR 불변성의 오적용 주의.** 불변성은 "결정"에 적용되는 것이지 규범 산문 전체에 적용하면 문서가 supersede 체인 파편으로 흩어진다. PEP의 유형 구분(동결형 vs Active형)이 해독제다. 【추론】

---

## dddjango 시사점 정리

P0 실측(규칙 3,217문장·ID 없음·번호 공간 5종·검사기 역지목 25종·미러 19쌍 무방비·심의자 1인)에 대한 R6 결론:

1. **ID 규약을 OBO식으로.** 규칙 단위 불변 ID + 삭제 금지 + obsolete 마킹 + `replaced_by` 포인터 + "의미 실질 변경 = 새 ID". 기존 날짜 스탬프는 릴리스 식별자(P4 날짜형)로 역할 분리.
2. **상태 기계는 COSS 규모로 작게.** draft → active → deprecated → retired(+ 정당한 종료 상태 complete). 전이 권한은 명문화된 1인 편집자(사용자)에게. ESLint형 기계가독 필드(`deprecatedSince`·`replacedBy`, 빈 값 허용)를 레지스트리 레코드에.
3. **동결 정책은 문서 유형별 이원화.** 의사결정 #N = ADR/RFC형 동결 + supersede 양방향 링크(번호 재사용 금지). 스킬 산문 본문 = PEP-Active형 지속 개정(단 레지스트리 뼈대와 lint 양방향 대조). — 블루프린트의 "뼈대=레지스트리, 산문=스킬 문서" 분업과 정합.
4. **"변경은 절차로만"의 1인 프로젝트 번역 = "변경은 lint를 통과한 레지스트리 레코드 변경으로만".** 합의 의식(FCP·무이의 대기)은 도입하지 않고, 그 자리를 결정적 검사기가 맡는다. 심의 부하를 사람에게서 기계로 옮기는 것이 BDFL 소진·xz형 실패의 예방책이자 죽은 온톨로지 1순위 원인(유지 자원 소멸)에 대한 대비다.
5. **배포본은 스냅샷.** schema.org의 무버전 정본 + 날짜 스냅샷 모델을 차용해 claude/codex 두 판은 정본에서 파생되는 스냅샷임을 절차로 강제(미러 표류의 구조적 봉쇄).
6. **개정 절차 문서의 자기 등록.** C4처럼 거버넌스 문서 자체가 ID·상태를 갖는 레코드가 되게 하라.
7. **D1에 대한 R6 관점.** 거버넌스 어휘(deprecated·replaced_by·versionInfo·status·prior/backwardCompatibleWith)는 형식 중립적으로 차용 가능 — YAML 자체 형식을 택하더라도 필드명·의미론은 OWL/OBO 표준에서 빌려 두면 형식 전환 비용이 낮아진다.

---

## 인용 출처 목록 (20)

1. https://obofoundry.org/principles/fp-019-term-stability.html — OBO P19 용어 의미 안정성
2. http://obofoundry.org/principles/fp-004-versioning.html — OBO P4 버저닝
3. http://obofoundry.org/id-policy.html — OBO ID 정책
4. https://obofoundry.org/docs/OntologyStatus.html — OBO 온톨로지 상태 5종
5. https://pmc.ncbi.nlm.nih.gov/articles/PMC8546234/ — OBO Foundry in 2021 (Database, 2021)
6. https://www.w3.org/TR/owl2-syntax/#Ontology_IRI_and_Version_IRI — OWL 2 구조 명세(W3C)
7. https://www.ietf.org/process/rfcs/ — IETF RFC 불변성·obsoletes/updates·errata
8. https://peps.python.org/pep-0001/ — PEP 1 상태 수명주기
9. https://adr.github.io/ — ADR 홈(결정 로그)
10. https://csse6400.uqcloud.net/handouts/adr.pdf — ADR 강의 노트(불변성·supersede)
11. https://github.com/unprotocols/rfc/blob/master/2/README.md — COSS 명세
12. https://rfc.zeromq.org/spec/44/ — C4 rev.3 (42를 deprecate)
13. https://rfc.zeromq.org/spec/42/ — C4 rev.2
14. https://rust-lang.github.io/rfcs/ — Rust RFC Book
15. https://rfd.shared.oxide.computer/rfd/0001 — Oxide RFD 1
16. https://eslint.org/docs/latest/extend/rule-deprecation — ESLint DeprecatedInfo
17. https://typescript-eslint.io/maintenance/issues/rule-deprecations-and-deletions/ — typescript-eslint 폐지 정책
18. https://schema.org/docs/howwework.html — schema.org 개정 프로세스
19. https://pmc.ncbi.nlm.nih.gov/articles/PMC6371329/ — Geller et al., How Sustainable are Biomedical Ontologies? (2018)
20. https://lwn.net/Articles/759654/ — Guido BDFL 사임 (LWN, 2018)

보조(블로그·보도, 본문에 표기): https://securelist.com/xz-backdoor-story-part-2-social-engineering/112476/ (Kaspersky Securelist, 2024) · https://www.businesswire.com/news/home/20240917030299/en/ (Tidelift 2024 설문 보도) · https://smallcultfollowing.com/babysteps/blog/2018/06/20/proposal-for-a-staged-rfc-process/ (Matsakis, 2018) · https://lwn.net/Articles/759756/ (Python post-Guido)
