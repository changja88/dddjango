# R3 — 문서↔검사기 양방향 트레이서빌리티 (외부 선례 조사)

조사일: 2026-08-18 · 레인: R3 · 작성: 외부 자료 조사 서브에이전트

## 조사 질문

산문 규범 문서와 자동 검사기 사이의 양방향 추적(요구↔검증)을 유지하는 검증된 방법은 무엇인가?
특히 dddjango처럼 「검사기→문서 단방향 정형구(docstring 25/27종)」가 이미 있을 때, 이를 양방향 대조로
승격하는 최소 비용 경로와, 커버리지 공백을 «명시된 위임»으로 등기하는 관례를 찾는다.

전제(P0 센서스 실측): 규칙 코퍼스 30문서·규범 문장 3,217개·606절, § 앵커 91% 강함, 규칙 단위 ID 없음,
번호 공간 5종 혼용, 검사기 27종 중 25종이 docstring으로 규칙 역지목(문서→검사기 방향 0), 소유자 1인.

---

## 발견들

### F1. 안전 표준의 RTM — «양방향»은 두 방향이 서로 다른 결함을 잡는 두 개의 질문이다

- [사실] DO-178C는 순방향(모든 시스템/소프트웨어 요구 → 코드·테스트 케이스)과 역방향(모든 코드 요소 →
  상위 요구)의 양방향 추적을 요구한다. 소프트웨어는 「테스트를 통과할 때」가 아니라 「그 테스트들이
  요구에 완전 추적될 때」 검증된 것으로 본다.
  출처: Parasoft DO-178C Requirements Traceability — https://www.parasoft.com/learning-center/do-178c/requirements-traceability/
- [사실] ISO 26262 전반과 Automotive SPICE의 SWE.1.BP6이 양방향 트레이서빌리티를 명시 요구한다.
  RTM(requirements traceability matrix)은 기능안전 심사·safety case의 전제 산출물이다.
  출처: Parasoft ISO 26262 — https://www.parasoft.com/learning-center/iso-26262/requirements-traceability/ ·
  LDRA 백서(ISO 26262·ASPICE) — https://ldra.com/wp-content/uploads/ldra/ISO-26262-and-ASPICE-WP_v1.1.pdf
- [추론] 두 방향은 잡는 결함이 다르다. 순방향 공백 = 집행 안 되는 규칙(누락된 검사기), 역방향 공백 =
  근거 없는 집행(유령 검사기·죽은 규칙 인용). dddjango는 역방향 원료(docstring)만 있고 순방향 뷰가 0이므로,
  현재 검출 불가능한 결함 클래스는 「규범 문장 3,217개 중 집행체 없는 것들」 전부다.

«dddjango 시사점» 순방향 뷰(문서 기준 커버리지 표)는 새 데이터 입력 없이 기존 docstring을 역전개하면
생성 가능한 산출물이며, 이것이 양방향 승격의 절반이다.

### F2. AWS Duvet — 산문 문서를 정본으로 둔 채 코드측 인용으로 양방향을 만드는 최근접 선례

Duvet(AWS Labs, Rust, Apache-2.0, 활발히 유지·s2n-quic/aws-encryption-sdk에서 사용)은 dddjango 상황과
구조적으로 가장 가까운 도구다.

- [사실] 스펙은 Markdown 또는 IETF RFC **원문 그대로**가 정본이다. RFC 2119 키워드(MUST/SHOULD/MAY…)가
  들어간 문장을 요구 단위로 **자동 추출**한다 — 즉 규칙 단위 ID를 새로 부여하지 않고
  «(스펙 URL#섹션 앵커) + (규범 문장 원문 인용)»이 요구의 정체성이다.
  출처: https://github.com/awslabs/duvet · https://github.com/awslabs/duvet/blob/main/guide/src/specifications.md
- [사실] 코드측 주석 정형구:
  ```
  //= https://www.rfc-editor.org/rfc/rfc2324#section-2.1.1
  //# A coffee pot server MUST accept both the BREW and POST method equivalently.
  ```
  주석 타입 6종: `implementation`(기본) · `test` · `implication`(구성상 자명 — 타입 시스템이 보증) ·
  `exception`(+`reason=` — **구현하지 않기로 한 명시적 면제 등기**) · `todo`(+`tracking-issue=`) ·
  `spec`(+`level=` — 키워드 없는 문장을 요구로 승격 등기, toml 파일로도 가능).
  출처: https://github.com/awslabs/duvet/blob/main/guide/src/annotations.md
- [사실] 리포트가 방향을 반전시킨다: HTML 리포트는 스펙 문서 쪽에 소스 코드로 가는 링크를 하이라이트해
  «소스↔스펙의 양방향 링크»를 만든다. 요구 상태는 Complete / Cited / Tested / Excused / Not started.
  출처: https://github.com/awslabs/duvet/blob/main/guide/src/reports.md · https://awslabs.github.io/duvet/
- [사실] `snapshot` 리포트: 커버리지 상태 전체를 `.duvet/snapshot.txt`로 직렬화해 저장소에 체크인하고,
  CI(`duvet report --ci`)가 파생 스냅샷과 비교해 불일치 시 실패 — **명시적 승인 없는 커버리지 변화(후퇴 포함)를
  기계적으로 차단하는 래칫**이다.
  출처: https://github.com/awslabs/duvet/blob/main/guide/src/reports.md

«dddjango 시사점» § 앵커 91% + docstring 역지목이라는 기존 자산은 Duvet 모델의 입력형과 거의 동형 —
docstring 정형구를 «문서 경로#§ + 규범 문장 인용»으로 승격하고 lint가 인용문↔문서 원문을 대조하면,
규칙 단위 ID 전면 부여 없이도 표류가 기계 검출된다.

### F3. OpenFastTrace(OFT) — revision 내장 ID, 위임 표기, 링크 오류의 분류학

OFT(itsallcode, Java, OSS)는 요구 추적을 «명시적 ID» 쪽에서 가장 정교하게 만든 도구다.

- [사실] 명세 항목 ID는 `타입~이름~revision` 3부 구성(`req~html5-exporter~1`). **revision 정수는 ID의
  일부이며, 의미가 바뀌면 revision을 올린다 → 그 항목을 가리키던 기존 커버리지 링크가 전부 무효화되어
  링크한 쪽이 재검토를 강제당한다.** 마침표 추가 같은 비의미 변경은 revision을 올리지 않는다.
- [사실] 문서에는 informative/normative 구분이 있고 `Needs:`(어떤 아티팩트 타입의 커버리지가 필요한가),
  `Covers:`(무엇을 커버하는가), `Status:`(draft/proposed/approved/rejected), `<!-- oft:off -->` 파싱 제외
  토큰이 있다. 코드측은 주석 태그 `[impl->dsn~validate-authentication-request~1]` 한 줄.
- [사실] **위임(Delegating Requirement Coverage)**: `arch --> dsn : req~web-ui-uses-corporate-design~1`
  한 줄로 «이 요구를 읽었고, 이 수준에서는 결정이 필요 없으며, 하위 아티팩트로 커버 책임을 넘긴다»를
  등기한다. 커버리지 공백을 침묵이 아닌 명시 표기로 바꾸는 정확한 선례.
- [사실] 링크 오류 분류학이 정립돼 있다 — 나가는 링크: Covers/Predated(더 새 revision 지목)/Outdated(옛
  revision 지목)/Ambiguous/Unwanted(요구 안 한 커버)/Orphaned(없는 항목 커버) · 들어오는 링크: Covered
  Shallow/Unwanted/Predated/Outdated · 양방향: Duplicate. 「Outdated 검출이 OFT의 가장 유용한 안전장치」라고
  명시한다. Deep coverage(이행적 완전 커버) vs shallow coverage 개념도 있다.
  출처: OFT 사용자 가이드 — https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide/user_guide.md ·
  저장소 — https://github.com/itsallcode/openfasttrace
- [사실] 비안전(non-safety) OSS 채용 실증: JabRef가 Markdown 개발 문서에 `req~ai.example~1`을 쓰고 코드에
  `// [impl->req~ai.example~1]`, Gradle `traceRequirements` 태스크로 CI 검사한다 — 1인~소규모 팀 비용으로
  운영 가능함을 보여준다.
  출처: https://devdocs.jabref.org/requirements/

«dddjango 시사점» 레지스트리 뼈대에 OFT식 revision 정수를 넣으면 «규칙 개정 → 그 규칙을 인용하는 검사기
전원 Outdated 격하»라는 개정 전파 기계가 생기고, OFT의 링크 상태표는 lint 오류 코드 어휘로 그대로 차용 가능하다.

### F4. Ferrocene — 스펙 문단 ID에 테스트를 주석으로 묶고 매트릭스를 자동 생성한 인증급 실사례

- [사실] Ferrocene(Rust 안전인증 툴체인)은 Ferrocene Language Specification(FLS)의 절·문단에 안정 ID를
  부여하고, 컴파일러 테스트 대다수에 «ferrocene annotation» 태그를 달아 테스트↔FLS 절을 연결한다.
  주석은 **디렉터리 수준(하위 테스트가 상속) + 개별 테스트 수준** 두 층으로 적용되고, 여기서 트레이서빌리티
  매트릭스가 자동 생성되어 공개 문서로 나온다. 이 체계로 TÜV SÜD 인증(ISO 26262 ASIL D·IEC 61508 SIL 3,
  2023 최초 인증; 2025년 libcore 부분집합 IEC 61508 SIL 2 추가)을 통과했다.
  출처: https://public-docs.ferrocene.dev/main/qualification/evaluation-report/rustc/method.html ·
  https://ferrous-systems.com/blog/officially-qualified-ferrocene/ ·
  https://ferrous-systems.com/blog/ferrocene-libcore-news-release/ ·
  FLS 공개 — https://ferrous-systems.com/blog/the-ferrocene-language-specification-is-here/
- [사실·반례 겸] web-platform-tests(WPT)의 `rel=help` 링크(테스트→스펙 절 단방향)는 CSS WG 시절 필수였다가
  wpt 통합 때 optional로 격하됐고, 스펙 커버리지 산출 도구가 이에 의존하는데도 관례가 침식됐다.
  출처: https://github.com/web-platform-tests/wpt/issues/10053

«dddjango 시사점» 디렉터리(검사기 모듈) 수준 기본 매핑 + 함수 수준 재정의의 2층 주석은 27종 검사기에
저비용으로 이식 가능하며, WPT 사례는 «링크 의무를 lint로 강제하지 않으면 형해화된다»는 경고다.

### F5. 검사기 메타데이터에서 문서를 생성·대조 — eslint-doc-generator의 update/--check 2모드 패턴

- [사실] eslint-doc-generator(eslint-community)는 ESLint 플러그인의 규칙 메타데이터(단일 출처)에서 규칙
  목록 표·문서 헤더를 자동 생성하고, `--check` 플래그가 «생성 결과 ≠ 커밋된 문서»일 때 CI를 실패시킨다.
  로컬용 `update:eslint-docs`(재생성)와 CI용 `lint:eslint-docs`(대조)의 2모드가 표준 UX이며,
  eslint-plugin-react 등 대형 플러그인이 채택했다. 문서 절 구성 일관성 검사(Options 절 존재, 옵션 전부
  언급 등)도 수행한다.
  출처: https://github.com/eslint-community/eslint-doc-generator ·
  https://github.com/jsx-eslint/eslint-plugin-react/pull/3469

«dddjango 시사점» «뼈대는 레지스트리 정본 → 파생 뷰 생성 → lint가 대조» 블루프린트와 동일 구조의 검증된
소형 선례로, generate/check 2모드 CLI가 그대로 벤치마크다.

### F6. 검사기 자신을 검사하는 meta-testing — fixture 짝 강제와 문서↔구현 불일치의 실증

- [사실] ESLint RuleTester는 규칙마다 valid/invalid 픽스처를 최소 1개씩 요구하며, 자동수정(fix)을 내는
  규칙이 `meta.fixable`을 선언하지 않으면 테스트 하네스가 throw한다(2020, PR #13489) — 검사기의 메타데이터
  선언과 실동작의 정합을 테스트 계층이 강제하는 사례. fixable 선언 규칙에 fixer를 실제로 작동시키는 테스트
  케이스 존재를 강제하자는 제안도 진행됐다(#18008).
  출처: https://eslint.org/docs/latest/contribute/tests · https://eslint.org/docs/latest/extend/custom-rule-tutorial ·
  https://github.com/eslint/eslint/pull/13489 · https://github.com/eslint/eslint/issues/18008
- [사실] Semgrep은 규칙 파일과 같은 이름의 픽스처 파일에 `# ruleid:`(위음성 방지)·`# ok:`(위양성 방지)·
  `# todoruleid:`·`# todook:` 주석을 달고 `semgrep --test`로 실행하는 규칙 테스트 관례를 공식화했다.
  출처: https://semgrep.dev/docs/writing-rules/testing-rules
- [사실] StaAgent(arXiv 2507.15892, 2025)는 **규칙 설명서(문서)에서 LLM으로 시드 프로그램을 생성해**
  의미 보존 변이와의 메타모픽 대조로 검사기 구현↔문서의 불일치를 검출, SpotBugs 28·SonarQube 18·
  ErrorProne 6·Infer 4·PMD 8 등 64개 문제 규칙을 발견했다(그중 53개는 기존 기법이 못 잡던 것).
  성숙한 상용·OSS 검사기에서도 문서↔구현 불일치가 대규모로 실재함의 실증이다.
  출처: https://arxiv.org/abs/2507.15892

«dddjango 시사점» 검사기 27종 각각에 «위반 픽스처 + 통과 픽스처» 짝을 의무화(Semgrep식)하는 것이 meta-testing의
최소 비용 형태이고, 규범 문장에서 픽스처를 생성하는 LLM 보조는 2025년 논문으로 검증된 방향이다.

### F7. 커버리지 공백의 «명시된 위임» 등기 관례 — MISRA deviation record가 원형

- [사실] MISRA Compliance:2020(공식 문서)은 규칙 위반을 허용하는 유일한 경로로 deviation record를
  요구한다. 필수 요소: 위반된 지침 · 위반이 허용되는 상황 기술 · 사유 · 배경 정보 · 리스크 평가와 예방
  조치. 반복 사례는 사전 합의된 **deviation permit**(재사용 가능한 면제 양식) 저장소로 처리한다.
  출처: MISRA Compliance:2020 — https://misra.org.uk/app/uploads/2021/06/MISRA-Compliance-2020.pdf
- [사실] 코드측 등기의 현대적 구현: Duvet `exception`(+reason)·`todo`(+tracking-issue) 주석(F2),
  OFT의 위임 표기 `arch --> dsn : req~x~1`(F3).
- [추론] 공통 원리: «집행 없음»을 상태의 부재가 아니라 1급 레코드로 만들면, 모든 규범 문장이
  {집행됨, 면제됨(사유), 예정(추적), 정보성} 중 정확히 하나가 되어 **커버리지 대차가 0으로 마감되는
  회계**가 성립한다. 그때에만 «커버리지 공백»과 «등기 누락»이 구분 가능해진다.

«dddjango 시사점» 에이전트·사람 재량에 맡기는 규칙(집행 불가능한 산문 규범)은 deviation record의 필드
(사유·범위·리스크)만 차용한 «위임 등기»로 레지스트리에 남기고, 1인 소유 맥락이므로 승인 절차는 생략한다.

### F8. docs-as-code 요구 관리 생태 — 경량 텍스트 형식 + 자체 lint가 지배적

- [사실] sphinx-needs: Sphinx 문서 안에 need 객체(ID·타입·링크·상태)를 정의하고 필터·표·매트릭스를
  생성하는 docs-as-code 사실상 표준. ISO 26262·DO-178B/C 대응 구성을 명시 지원.
  출처: https://sphinx-needs.readthedocs.io/ · https://www.sphinx-needs.com/
- [사실] Doorstop: 항목 1개 = YAML 파일 1개, 디렉터리 = 문서, 이력은 VCS가 담당. 트리 유효성·링크 검증
  API 제공(2014 논문 + 활성 저장소).
  출처: https://github.com/doorstop-dev/doorstop · 논문 — https://file.scirp.org/Html/6-9301807_44268.htm
- [사실] StrictDoc: SDoc DSL + tree-sitter 소스 파싱으로 요구↔소스 파일·함수 단위 추적, 순·역방향
  매트릭스 생성. 자기 자신을 DO-178C 요구 도구 요건에 셀프 추적한 데모 문서를 공개.
  출처: https://strictdoc.readthedocs.io/en/stable/sphinx/strictdoc_01_user_guide.html ·
  https://strictdoc.readthedocs.io/en/stable/stable/docs_extra/DO178_requirements-TRACE.html
- [추론·D1 관련 증거] 이 레인에서 확인된 검증 선례 전부(Duvet=toml+주석, OFT=markdown+태그,
  Doorstop=YAML, StrictDoc=자체 DSL, Ferrocene=주석+Sphinx)가 **경량 텍스트 형식 + 전용 lint** 조합이다.
  요구↔검증 트레이서빌리티 용도로 RDF/Turtle+SHACL을 채택한 유의미한 실전 선례는 이번 조사 범위에서
  확인하지 못했다(부재의 증명은 아니나, 선례 밀도의 비대칭은 뚜렷하다).

«dddjango 시사점» «뼈대 레지스트리(구조 데이터) + 산문 스킬 문서 정본» 분업은 이 생태의 표준 형태와
일치하며, R3 관점의 증거는 D1에서 YAML 자체 형식+자체 lint 쪽을 가리킨다.

---

## 반례·주의

1. **링크는 의미 일치를 보증하지 않는다.** StaAgent(2025)가 보여주듯 성숙한 검사기도 문서와 구현이
   64건 어긋나 있었다 — 트레이스 링크가 전부 «Covers»여도 검사기가 문서와 다른 것을 검사할 수 있다.
   링크 무결성 lint(구문 대조)와 의미 정합 검증(픽스처·메타모픽)은 별개 층이다. [사실+추론]
2. **강제 없는 관례는 침식된다.** WPT `rel=help`가 optional로 격하되자 커버리지 도구가 의존하는데도
   링크가 빠지기 시작했다. 주석 의무는 CI lint로 게이트해야 유지된다. [사실]
3. **Duvet 직도입의 한계.** 요구 자동 추출이 RFC 2119 영어 키워드에 묶여 있어 한국어 규범 문장에는
   자동 추출이 작동하지 않는다(spec 타입/toml 수동 등기로 우회 가능하나 3,217문장 전건 수동은 비현실).
   또 인용문 정확 일치 기반이라 문서 개정 시 인용 주석 대량 갱신 비용이 생긴다 — 모델(앵커+인용+면제 등기)을
   차용하되 도구는 자체 lint로 구현하는 편이 맞다. [추론]
4. **OFT revision 방식의 역위험.** revision 증가는 저자의 수동 판단이라, 올리는 것을 잊으면 표류가
   미검출된다. 기계 검출(인용문 해시 대조)과 수동 개정 신호(revision)는 상호 보완으로 병용해야 한다. [추론]
5. **RTM 형식주의 함정.** 안전 업계에서도 RTM은 심사 통과용 «링크 세탁»으로 전락할 수 있다는 경계가
   상존한다. 1인 소유 맥락에서는 MISRA식 승인 절차·리스크 평가 전문은 과잉이며, 필드만 차용해야 한다. [추론]
6. **도구 풀도입의 선행 조건.** sphinx-needs/StrictDoc류 풀도입은 문서 체계 재편(빌드 체인 포함)을
   동반한다 — 번호 공간 5종 혼용이 정리되기 전 도입하면 6번째 번호 공간을 추가하는 결과가 된다. [추론]

---

## dddjango 시사점 정리 — 최소 비용 승격 경로

P0 실측 자산(§ 앵커 91%, docstring 역지목 25/27, rule-owner-map)을 기준으로 한 단계적 경로:

1. **참조 정형구 승격(신규 ID 발행 없이).** Duvet 모델을 차용해 규칙 참조의 정형을
   «문서 경로#§앵커 + 규범 문장 원문 인용(+선택적 해시)»으로 정의한다. 규칙 단위 ID 전면 부여는
   이 단계에서 불필요 — § 앵커 91%가 이미 식별자 역할을 한다. (F2)
2. **역방향의 기계화.** lint 1: 각 검사기 docstring의 참조가 실존 문서·실존 §를 가리키고 인용문이
   문서 원문과 일치하는지 대조(불일치 = 표류 검출). rule-owner-map은 손으로 유지하는 문서에서
   docstring 파싱 «생성물»로 강등한다. (F2·F5)
3. **순방향의 신설.** lint 2: 606절·3,217 규범 문장을 축으로 커버리지 표를 생성 — 각 규범 문장의 상태를
   {enforced(검사기 ID), delegated(위임 대상+사유), todo(+추적), informative} 4값 중 하나로 강제한다.
   미등기 문장이 곧 lint 실패다. 위임 등기는 OFT 위임 표기와 MISRA deviation record 필드를 차용한다. (F1·F3·F7)
4. **래칫.** 커버리지 상태 전체를 스냅샷 파일로 체크인하고 CI가 파생 스냅샷과 대조 — 명시적 커밋 없는
   커버리지 후퇴를 차단한다(Duvet `--ci` 방식). (F2)
5. **개정 전파.** 레지스트리 뼈대의 규칙 항목에 OFT식 revision 정수를 두고, 의미 개정 시 증가 →
   그 규칙을 인용하는 검사기 전부가 Outdated로 격하되어 재검토가 강제된다. lint 오류 어휘는 OFT의
   Predated/Outdated/Orphaned/Unwanted/Duplicate 분류를 차용한다. (F3)
6. **meta-testing.** 검사기 27종 각각에 위반/통과 픽스처 짝 최소 1쌍을 의무화(Semgrep `ruleid:`/`ok:` 식).
   장기적으로 규범 문장→픽스처 LLM 생성 보조(StaAgent 방향)를 검토한다. (F6)
7. **D1 증거.** 이 레인의 선례 밀도는 경량 텍스트 형식(YAML/markdown/주석)+자체 lint 쪽으로 압도적이며,
   트레이서빌리티 용도의 RDF/SHACL 실전 선례는 확인되지 않았다. (F8)

## 인용 출처 목록 (26)

1. https://www.parasoft.com/learning-center/do-178c/requirements-traceability/
2. https://www.parasoft.com/learning-center/iso-26262/requirements-traceability/
3. https://ldra.com/wp-content/uploads/ldra/ISO-26262-and-ASPICE-WP_v1.1.pdf
4. https://github.com/awslabs/duvet
5. https://awslabs.github.io/duvet/
6. https://github.com/awslabs/duvet/blob/main/guide/src/annotations.md
7. https://github.com/awslabs/duvet/blob/main/guide/src/reports.md
8. https://github.com/awslabs/duvet/blob/main/guide/src/specifications.md
9. https://github.com/itsallcode/openfasttrace
10. https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide/user_guide.md
11. https://devdocs.jabref.org/requirements/
12. https://public-docs.ferrocene.dev/main/qualification/evaluation-report/rustc/method.html
13. https://ferrous-systems.com/blog/officially-qualified-ferrocene/
14. https://ferrous-systems.com/blog/ferrocene-libcore-news-release/
15. https://ferrous-systems.com/blog/the-ferrocene-language-specification-is-here/
16. https://github.com/web-platform-tests/wpt/issues/10053
17. https://github.com/eslint-community/eslint-doc-generator
18. https://github.com/jsx-eslint/eslint-plugin-react/pull/3469
19. https://eslint.org/docs/latest/contribute/tests
20. https://github.com/eslint/eslint/pull/13489
21. https://github.com/eslint/eslint/issues/18008
22. https://semgrep.dev/docs/writing-rules/testing-rules
23. https://misra.org.uk/app/uploads/2021/06/MISRA-Compliance-2020.pdf
24. https://arxiv.org/abs/2507.15892
25. https://sphinx-needs.readthedocs.io/
26. https://github.com/doorstop-dev/doorstop (+ 논문 https://file.scirp.org/Html/6-9301807_44268.htm, StrictDoc https://strictdoc.readthedocs.io/en/stable/sphinx/strictdoc_01_user_guide.html)
