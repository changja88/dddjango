# R1 — 규칙 ID·번호 공간 통합: 선례와 모범 관행 조사

- 조사일: 2026-08-18 · 담당: 레인 R1 (외부 자료 조사)
- 맥락: dddjango 규칙 코퍼스 30문서·규범 문장 3,217개·606절, 번호 공간 5종 혼용(§N.M / 무접두 #N / registry #1~27 / 12-slot / 의사결정 #N) + 준-ID(D50·birth-enum·날짜 스탬프). 규칙 단위 ID 없음. 소유자 1인, 소비자는 에이전트·검사기·lint·사람.

## 조사 질문

여러 legacy ID 체계를 하나의 안정 ID 체계로 통합·이주한 선례와 모범 관행은 무엇인가? 특히 (a) 기존 번호를 깨지 않고 alias/redirect로 흡수하는 이주 전략, (b) ID에 의미를 넣을지(분류 접두) 말지(순번)의 트레이드오프, (c) 폐지·승계(supersedes) 표기.

---

## 발견들

### A. ID 구조 설계 — 의미 vs 불투명

**A-1. 생명과학 식별자 10원칙(McMurry et al., PLoS Biology 2017)** 〔사실〕
UniProt·EMBL-EBI 등 대형 데이터 제공자들의 합의 논문. 핵심 원칙:
- Lesson 4: "Avoid embedding meaning or relying on it for identifier uniqueness. Instead, favor opaque identifiers and convey meaning in the entity's metadata." — 의미는 ID가 아니라 메타데이터에 담아라.
- Lesson 2: 접두(prefix)와 URI 패턴 바인딩을 문서화·등록하라(로컬 ID가 밖에서 여행할 수 있게).
- Lesson 6: 버전 관리 정책을 문서화하라(엔티티의 변경 이력이 문서화되거나 조회 가능해야 함).
- Lesson 7: "Identifiers that you have exposed publicly must never be deleted or reassigned to another record" — 폐지된 ID는 tombstone 페이지로 해석(resolve)되게 유지.
- 출처: https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.2001414
- «dddjango 시사점» 규칙 ID의 헌장 조항으로 그대로 채택 가능: 불투명 ID + 의미는 레지스트리 메타데이터, ID 재배정·삭제 영구 금지, 폐지 ID는 tombstone 항목으로 잔존.

**A-2. W3C «Cool URIs don't change»(Berners-Lee, 1998 — 여전히 정본)** 〔사실〕
- "URIs don't change: people change them." 식별자에 넣지 말아야 할 것: 저자명, **주제 분류**("changes surprisingly fast"), 상태(draft/old), 파일 확장자, 접근 수준, 소프트웨어 메커니즘.
- 유일하게 안전한 의미 요소로 **생성 날짜**를 권장(예: `w3.org/1998/12/01/chairs`) — 날짜는 사후에 절대 변하지 않는 사실이므로.
- 출처: https://www.w3.org/Provider/Style/URI
- «dddjango 시사점» "어느 문서 §몇 절"은 전부 '주제 분류+상태' 성분이라 ID에 넣으면 안 되는 축이다. 반면 dddjango가 이미 쓰는 날짜 스탬프(2026-08-12식)는 Cool URIs가 인정하는 유일한 의미 성분과 정확히 일치한다.

**A-3. OBO Foundry ID 정책 — 안정 접두 + 불투명 순번 CURIE** 〔사실〕
- 형식: `IDSPACE:LOCALID`(예: GO:0050918), LOCALID는 숫자. CURIE↔URI 1:1 결정적 매핑(`purl.obolibrary.org/obo/GO_0050918`).
- "Each OBO ID is assigned to a only single term within the set of all OBO ontologies" — 전 생태계 범위 유일성, 재사용 금지.
- 접두는 3자 이상, 레지스트리(Bioregistry 등) 간 충돌 회피 의무. 버전은 YYYY-MM-DD.
- 출처: http://obofoundry.org/id-policy.html , http://obofoundry.org/principles/fp-003-uris.html
- «dddjango 시사점» 수백 개 온톨로지가 20년 넘게 유지한 검증된 패턴: "안정 네임스페이스 접두(굵고 소수) + 불투명 지역 순번". 규칙 ID를 `DJR:0417`식 CURIE로 하면 RDF 채택 시(D1) 그대로 IRI가 되고 YAML 채택 시에도 그냥 문자열 키로 쓰인다.

**A-4. 반대편 성공 사례 ①: NIST SP 800-53 통제 ID(의미 접두)** 〔사실〕
- `AC-2` = Access Control 패밀리 + 순번, 강화는 `AC-2(1)` 괄호 번호. 패밀리 2자 코드는 수십 년째 안정.
- Rev 4→Rev 5 개정에서도 기존 ID를 유지하고, 철회 통제는 ID를 남긴 채 "W(Withdrawn) — Incorporated into IR-9" / "Moved to IR-4(11)"식 처분 표기.
- 개정 시 MITRE 작성 Rev4↔Rev5 변경 분석 워크북(xlsx)을 공식 배포해 이주를 지원.
- 출처: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final (보조: https://www.saltycloud.com/blog/nist-800-53-controls-overview/ )
- «dddjango 시사점» 의미 접두가 성공하려면 분류 축이 통제 패밀리처럼 극도로 안정적이어야 한다. dddjango에서 그 조건을 만족하는 축은 "스킬 문서명"이 아니라 기껏해야 discipline/architecture/implementation 같은 층위 정도 — 그것도 개편 이력이 있다면 접두 후보 탈락. 〔추론〕

**A-5. 반대편 성공 사례 ②: ESLint 규칙 이름(의미 슬러그, 무번호)** 〔사실〕
- `no-unused-vars`처럼 검사 내용 자체가 이름. 번호 없음. 성립 이유: 이름이 분류가 아니라 **행위 기술**이라 분류 개편의 영향을 안 받고, 이름이 틀려지면 rename이 아니라 deprecate+신규로 처리.
- «dddjango 시사점» 검사기 27종의 이름은 ESLint식 슬러그가 자연스럽지만, 규범 문장 3,217개 급의 코퍼스에서 문장 단위 슬러그 작명은 유지 불가능 — 슬러그는 검사기 층, 순번은 규칙 층으로 역할 분리가 현실적. 〔추론〕

**A-6. 불투명 ID 옹호론(보조 출처)** 〔사실(출처 존재)+추론〕
- 이름이 바뀌면 라벨만 갱신하고 URI는 불변으로 두는 것이 불투명 ID의 핵심 이득이라는 정리.
- 출처(블로그·보조): https://donnywinston.com/posts/on-the-wisdom-of-opaque-identifiers/ , https://www.cronofy.com/blog/opaque-ids
- «dddjango 시사점» 규칙의 '제목'은 자주 다듬어지므로(리팩터링·개명 이력 존재) 제목·절 번호를 ID에서 배제해야 개명 자유를 지킨다.

### B. 불변성·재사용 금지 — 업계 공통 헌장

**B-1. ReqIF(OMG 요구사항 교환 표준) 실무** 〔사실〕
- "Once a SpecObject has been created, its Identifier must never change, period."(ReqIF 저자 Michael Jastram) — ID 변경은 새 객체를 의미.
- 표준 관행: 기계용 불변 GUID(ReqIF Identifier) + 사람용 가독 ID(ForeignID, 사람이 읽는 R-123식) **이중 ID** + 도구별 매핑 테이블. ForeignID/AlternativeID도 일단 부여되면 불변.
- 출처: https://www.reqif.academy/forums/topic/which-kind-of-identifier-to-use-for-which-purpos/ , https://hub.requisis.com/en/kb/kb/wissenswertes-zu-reqif.foreignid , https://www.doors-universe.com/req-roundtrip/reqif-standard/
- «dddjango 시사점» 기계 조인 키(불변 ID)와 사람 가독 표기(제목·§경로)를 한 필드에 욱여넣지 말 것. 레지스트리 스키마에서 `id`(불변)와 `label`/`anchor`(가변)를 처음부터 분리.

**B-2. RFC 번호 — 재사용 없음 + 관계 메타데이터 4종** 〔사실〕
- RFC 번호는 절대 재사용되지 않고, 대체는 새 번호 발행 + `Obsoletes`(전면 대체) / `Updates`(부분 개정) / 역방향 `Obsoleted-By` / `Updated-By` 관계로 기록.
- 출처: https://www.ietf.org/process/rfcs/ , https://www.rfc-editor.org/rfc-index-100a.html
- «dddjango 시사점» '전면 대체'와 '부분 개정'을 구분하는 이항 관계 어휘가 필요하다 — dddjango의 실측 사례(규범 정면 충돌 표류 2건)는 Updates 관계가 기록 안 된 채 문서만 고쳐진 상황과 동형. 〔추론〕

**B-3. BCP/STD 번호 — 안정 논리 번호에 의한 간접층** 〔사실〕
- BCP 9은 RFC 8곳으로 구성·갱신돼 왔지만 "BCP 9"이라는 번호는 불변 — 논리 ID(BCP N)가 현행 RFC 집합을 가리키는 **간접 참조**로 동작.
- 출처: https://www.rfc-editor.org/info/bcp9/ , https://www.ietf.org/rfc/bcp-index.txt
- «dddjango 시사점» 규칙 ID는 BCP 번호처럼 '살아있는 논리 주소'로, 실제 산문 위치(스킬 문서 §앵커)는 레지스트리가 해석해 주는 간접층으로 설계하면 문서 개편이 ID를 못 깨뜨린다. 블루프린트의 뼈대/산문 분업과 정확히 부합.

**B-4. Rust 컴파일러 에러 코드(E0308) — 제거해도 명부에서 안 지움** 〔사실〕
- rustc-dev-guide: 에러 코드는 레지스트리에서 제거하지 않고, 폐기 시 해당 마크다운에 주석("REMOVED: merged into …")을 남긴다. 번호 재사용 없음.
- 출처: https://github.com/rust-lang/rustc-dev-guide/blob/master/src/diagnostics/error-codes.md , https://rustc-dev-guide.rust-lang.org/diagnostics.html
- «dddjango 시사점» 검사기 27종이 docstring으로 규칙을 역지목하는 현 구조에서, 규칙 ID가 생기면 검사기→규칙 참조는 컴파일러 진단 코드와 동형이 된다 — 폐기 규칙도 명부에 사유와 함께 영구 잔존시키는 관행까지 같이 가져올 것.

### C. 폐지·승계(supersedes) 표기의 표준 문법

**C-1. OBO 폐지 절차 — 기계가독 승계의 2단 어휘** 〔사실〕
- IRI는 영구 유지, `owl:deprecated=true`, 라벨에 "obsolete " 접두, 정의 앞에 "OBSOLETE." 명기.
- 승계 어휘 2종 구분: **`term replaced by`**(1:1 확정 후계 — 소비자가 자동 치환 가능) vs **`consider`**(후보 다수 — 사람 판단 필요). 폐지 사유(`has_obsolescence_reason`)·추적 이슈 URL(`term tracker item`)도 표준 주석.
- 폐지 전 의무: 사용처(참조·주석) 전수 확인 + 영향 그룹 통지.
- 출처: https://oboacademy.github.io/obook/howto/obsolete-term/
- «dddjango 시사점» replaced_by(자동 치환 가능)와 consider(수동 심의 필요)의 구분은 에이전트 소비자에게 특히 유효 — 에이전트가 폐지 규칙을 만났을 때 자동으로 따라갈지 사람에게 물을지를 ID 메타데이터만으로 결정할 수 있다.

**C-2. ESLint 규칙 폐지 메타데이터(2024말~2025 확장 스키마)** 〔사실〕
- `meta.deprecated` 구조체: `message`, `url`, `deprecatedSince`(semver), `availableUntil`(제거 예정 버전 또는 `null`=영구 보존), `replacedBy[]`(각각 `message`/`url`/`plugin`/`rule` 지정, 빈 배열=대체 없음 명시).
- ESLint 코어는 규칙을 절대 제거하지 않는 정책(deprecate만).
- 출처: https://eslint.org/docs/latest/extend/rule-deprecation , https://github.com/eslint/eslint/pull/19238
- «dddjango 시사점» 레지스트리의 폐지 필드 스키마를 새로 발명할 필요가 없다 — ESLint의 이 스키마(사유·시점·시한·구조화된 후계 목록)를 거의 그대로 YAML 필드로 차용 가능하며, 린트 규칙이라는 도메인까지 동일하다.

**C-3. typescript-eslint — 제거를 허용하는 쪽의 규율** 〔사실〕
- minor에서 deprecate 표기 → 다음 major에서 제거 가능 → 제거 시에도 **tombstone 문서 페이지**를 남겨 새 규칙/문서로 안내(예: `camelcase`).
- 출처: https://typescript-eslint.io/maintenance/issues/rule-deprecations-and-deletions/
- «dddjango 시사점» '영구 보존(ESLint)'과 '기한부 제거+tombstone(ts-eslint)' 중 선택지 — 소비자가 에이전트·검사기뿐인 dddjango는 참조 갱신을 lint로 강제할 수 있으므로 기한부 제거도 가능하지만, 비용이 낮은 영구 보존이 기본값으로 안전. 〔추론〕

**C-4. ADR 관행 — 순번 불변 + Superseded 체인** 〔사실〕
- 순번 부여 후 재사용 금지, 수락 후 본문 불변(immutable). 결정 변경은 새 ADR + 구 ADR의 상태만 "Superseded by NNNN"으로 갱신. 거부된 결정도 삭제하지 않음("truth is the full chain, not the latest one").
- 출처: https://csse6400.uqcloud.net/handouts/adr.pdf (보조: https://www.archyl.com/blog/architecture-decision-records-complete-guide )
- «dddjango 시사점» dddjango의 '의사결정 #N' 공간은 이미 ADR과 동형 — 이 공간만은 재번호 없이 상태 필드(superseded_by)만 얹으면 즉시 정합화된다.

### D. 레거시 번호를 깨지 않고 흡수하는 이주 전략

**D-1. CVE: CAN-→CVE- 접두 통일(2005) — 번호부 보존형 이주** 〔사실〕
- 초기엔 후보 `CAN-1999-0067` / 승격 `CVE-1999-0067` 이원 체계. 승격 때 식별자가 바뀌는 부담(도구·프로세스 전면 갱신)이 커서 2005년 CAN 지위를 폐지, 전부 CVE- 단일 접두로 통일. **연도-순번 부분은 그대로 보존**해 이주 비용을 접두 치환 한 번으로 축소.
- 출처: https://www.cve.org/Resources/Media/Archives/OldWebsite/about/faqs.html (보조: https://medium.com/@giulio.saggin/cve-turns-21-how-it-made-it-to-this-milestone-db7ab75fecc9 )
- «dddjango 시사점» legacy 번호 중 이미 안정적으로 참조되는 것(registry #1~27, 의사결정 #N)은 번호부를 보존한 채 새 접두만 씌워 흡수하는 편이(예: #14 → DJR-REG:14) 참조 갱신 비용을 기계적 치환 수준으로 낮춘다. 〔추론〕

**D-2. ISO/IEC 27002:2022 — 전면 재번호를 감행한 유일 대형 사례, 성립 조건은 '매핑 표 내장'** 〔사실〕
- 114개(2013) 통제를 93개로 병합·재편하며 번호를 전면 교체. 대신 표준 문서 자체에 양방향 대응표를 내장: Annex A(신→구), Annex B(구→신). 병합은 N:1 매핑으로 명시.
- 출처: https://www.iso.org/obp/ui/#iso:std:iso-iec:27002:en (보조: https://www.schellman.com/blog/iso-certifications/iso-27002-2022-what-you-need-to-know , https://levelblue.com/blogs/security-essentials/iso-27002-2013-to-2022-mapping )
- «dddjango 시사점» 재번호가 불가피한 공간(§N.M처럼 위치 종속 번호)은 ISO식으로: 신 ID 발행 + 구↔신 양방향 매핑을 레지스트리 정본에 내장하고 lint가 매핑 무결성(빠진 구번호 없음)을 검사.

**D-3. w3id.org / PURL — 리다이렉트 간접층을 공동체가 운영** 〔사실〕
- "secure, permanent URL re-direction service": 식별자는 불변, 목적지는 `.htaccess` 규칙(GitHub PR 심사)으로 갱신. OBO도 PURL로 동일 구조.
- 출처: https://w3id.org/ , http://obofoundry.org/id-policy.html
- «dddjango 시사점» 저장소 안에서의 등가물은 "ID→현행 문서·§앵커" 해석 테이블을 레지스트리에 두고 문서 이동 시 테이블만 고치는 것 — 문서 쪽 §앵커 91%가 강하다는 실측은 이 해석 테이블의 목적지 품질이 이미 확보돼 있다는 뜻.

**D-4. NIST Rev4→Rev5 — ID 보존 + 공식 변경 분석 산출물** 〔사실〕
- 대개정에서도 통제 ID를 유지하고, 철회는 처분 사유와 함께 표기(§A-4), 별도 비교 워크북 배포.
- 출처: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final
- «dddjango 시사점» 대개정 때 "ID 보존 + 처분 주석 + 변경 대장" 3종 세트가 소비자(도구) 이주 비용을 최소화하는 표준 패키지.

### E. docs-as-code 환경에서의 규칙 ID 운영(dddjango와 동형 사례)

**E-1. sphinx-needs — 산문 문서 안의 요구사항 ID를 빌드로 강제** 〔사실〕
- `needs_id_required = True`면 ID 없는 요구사항에서 빌드 실패, `needs_id_regex`로 접두+번호 패턴 강제, 외부 프로젝트 needs에는 충돌 방지용 접두 부여. 제목+해시 기반 자동 ID 옵션도 있으나 수동 부여가 기본.
- 출처: https://sphinx-needs.readthedocs.io/en/latest/configuration.html , https://github.com/useblocks/sphinx-needs/discussions/1088
- «dddjango 시사점» "산문 정본 + ID는 문서 안 표기 + 빌드/lint가 ID 존재·패턴·유일성을 강제"는 이미 성숙한 도구 패턴 — 규범 문장 3,217개 전부가 아니라 '규칙 단위'(수백 개 수준)에만 ID를 강제하는 단계적 도입이 sphinx-needs 사용례와 일치.

**E-2. NIST OSCAL — 기계 정본 카탈로그와 산문의 분업** 〔사실〕
- OSCAL 카탈로그 모델은 통제 집합의 기계가독 정본(XML/JSON/YAML 등가)이되, "not a catalog document format" — 카탈로그의 서론적 산문은 지원하지 않음을 명시. 산문 문서와 기계 카탈로그의 역할 분리를 표준이 스스로 선언.
- 출처: https://pages.nist.gov/OSCAL/documentation/schema/catalog-layer/catalog/ , https://pages.nist.gov/OSCAL/learn/concepts/layer/control/catalog
- «dddjango 시사점» 블루프린트(뼈대=레지스트리 정본, 산문=스킬 문서 정본)는 OSCAL이 이미 표준화한 분업과 동형 — 방향 자체의 타당성을 외부 선례가 뒷받침. D1에서 어느 형식을 고르든 이 분업 구조는 유지 가치가 있다.

---

## 반례·주의

1. **의미 접두는 성공 사례가 있으나 조건부다.** NIST(패밀리 2자)·ESLint(행위 슬러그)가 성공한 건 그 축이 수십 년 안정적이거나 분류가 아닌 행위 기술이기 때문. Cool URIs는 "주제 분류는 놀랄 만큼 빨리 바뀐다"고 경고 — dddjango의 스킬 문서 구성은 최근에도 개편 이력이 있으므로(문서명·절 구조) 문서·절 기반 접두는 부적격. 〔추론〕
2. **전면 재번호(ISO식)는 최후 수단.** ISO도 매핑 표를 표준 자체에 내장해서만 성립했고, ReqIF·McMurry·RFC·OBO 전부가 반대편 원칙(불변·비재사용)이다. 이미 유통 중인 번호(registry #, 의사결정 #)를 갈아엎는 안은 채택하지 말 것.
3. **불투명 ID만 쓰면 사람 심의자의 가독성이 죽는다.** ReqIF 실무가 GUID+가독 ID 이중 체계로 귀결된 이유. 소유자 1인 체제라도 심의·diff 리뷰는 사람이 하므로, 레지스트리 항목에 불변 ID와 별개로 가독 라벨·현행 앵커를 병기해야 한다.
4. **alias 영구 유지에도 비용이 있다.** ESLint(영구 보존)와 typescript-eslint(major 제거+tombstone)가 갈린 지점. 단 dddjango는 소비자 참조를 lint로 전수 검사할 수 있어 양쪽 다 가능 — 기본값은 저비용인 영구 보존. 〔추론〕
5. **위치 번호(§N.M, 12-slot)는 ID가 아니라 좌표다.** Cool URIs의 status/디렉터리 논거와 동형: 재배치 순간 전부 깨진다. 좌표는 레지스트리의 '현행 위치' 필드(가변)로 강등하고 ID로 승격하지 말 것. 〔추론〕
6. **자동 생성 해시 ID(sphinx-needs의 title+hash)는 제목 개명에 취약** — 제목이 바뀌면 ID가 바뀌는 자기모순. 수동 순번 부여가 맞다. 〔추론〕
7. **최신성 주의**: ESLint 확장 폐지 스키마는 2024말~2025 도입(PR #19238)으로 안정 초기, OSCAL은 1.x 성숙 단계(2019 마일스톤 이후 지속 개정). OBO·RFC·Cool URIs 원칙은 20년 이상 생존한 검증 관행.

---

## dddjango 시사점 정리

1. **신규 단일 ID: 안정 접두 1개 + 불투명 순번(4자리 zero-pad).** 예: `DJR-0417`(또는 CURIE형 `djr:0417`). 의미(소유 문서·층위·집행 검사기·쌍둥이 여부)는 전부 레지스트리 메타데이터로. 날짜는 ID에 넣지 않되 메타데이터의 birth 필드로 보존(기존 날짜 스탬프 관례와 접속).
2. **5종 legacy 공간은 재번호 없이 alias로 흡수.** 각 규칙 항목에 `aliases: ["§3.2", "reg#14", "D50", …]` 배열을 두고 lint가 alias→ID 역인덱스의 전단사·잔여 미흡수 참조를 검사. 이미 안정 유통 중인 번호부(registry #1~27, 의사결정 #N)는 CVE식으로 번호 보존+접두 부여.
3. **폐지·승계 스키마는 발명하지 말고 차용.** `deprecated: {since, reason, tracker}` + `replaced_by`(1:1, 자동 추종 가능) / `consider`(후보, 사람 심의) 구분(OBO) + `supersedes`/`updates` 이항 관계(RFC). ID·항목은 영구 잔존(tombstone), 재사용 절대 금지.
4. **ID는 간접층(BCP식)으로.** ID→현행 스킬 문서·§앵커 해석은 레지스트리가 소유, 문서 이동·개편은 해석 테이블 갱신으로 끝난다. §앵커 91% 실측 강도는 목적지 품질이 이미 확보됐다는 신호.
5. **미러 쌍(claude/codex 19쌍)은 동일 규칙 ID를 공유**시키고, 쌍둥이 lint의 조인 키를 규칙 ID로 삼으면 의미 미러 대조가 문장 diff가 아니라 ID 단위 대조로 안정화된다. 실증된 충돌 표류 2건은 Updates 관계 미기록 문제로 재해석 가능.
6. **도입 단위는 규범 문장(3,217)이 아니라 규칙(수백 규모)부터.** sphinx-needs식으로 "ID 필수·패턴·유일성"을 lint로 강제하되, 문장 단위 ID는 필요가 실증될 때까지 미룬다(YAGNI).
