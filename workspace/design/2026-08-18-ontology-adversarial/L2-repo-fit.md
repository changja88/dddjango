# L2 — dddjango 현실 정합성 적대 리뷰 (블루프린트 v2 · 2026-08-18)

- 심사 대상: `workspace/design/2026-08-18-ontology-blueprint-v2.md` (동결 후보)
- 방법: 블루프린트·P0 센서스·조사 종합 전문 정독 + 저장소 실물 대조(검사기 27종 docstring grep·표본 정독, rule-owner-map·spec_lint·corpus_lint·anchor_integrity_check·corpus_mirror_sync·fixture_matrix 정독, codex 디렉터리 실사, architecture-ddd final.md 앵커·인용 실측). 코퍼스·플러그인·설계 문서 무수정.
- 규율: 반박이 성립하지 않으면 성립하지 않는다고 기록한다(§B).

## A. 성립한 반박 (severity 순)

### F1 [blocker] S2의 «rule-owner-map 파싱 파생물 강등»은 현행 파생 체계와 정면 충돌하고, docstring 파싱으로는 재구성 자체가 불가능하다

- **claim**: 블루프린트 §4.1(L62) «검사기 docstring의 기존 정형구를 Rule-ID:로 승격 → rule-owner-map은 파싱 파생물로 강등(이중 장부 제거)»과 S2 완료 기준(L96) «rule-owner-map 파생물화»는, rule-owner-map이 **이미** 명세에서 생성·검증되는 파생물이라는 저장소 사실과 충돌한다.
- **evidence**:
  - `workspace/plan/2026-08-11-rule-owner-map.md` L3: «생성: `python3 workspace/tools/spec_lint.py --emit-owner-map` · 검증: 같은 도구 ⑧» — 파생원은 검사기가 아니라 **명세**(`workspace/tools/spec_lint.py` L44 `SPEC_REL = workspace/design/2026-08-08-tree-revision-spec.md`, L28 `--emit-owner-map`, L47 `MAP_REL`).
  - `spec_lint.py` L18 검사 ⑧: «rule-owner-map이 **명세와 1:1**»을 집행 — docstring 파싱으로 만든 map은 검사기가 인용한 부분집합만 담으므로 538규칙 명세와의 1:1이 즉시 깨져 ⑧ red가 된다. 두 파생 경로(명세→map vs docstring→map)가 같은 파일을 두고 경합하는 구조.
  - human 판정 규칙은 ⓒ 검사기가 없어 **어떤 docstring에도 존재하지 않는다**: rule-owner-map L25·L26·L32·L36 등(#15·#16·#23~#27, ⓒ=«—», ⓓ=discipline-reviewer). docstring 파싱 파생물에서는 이 행들이 소멸한다.
  - 블루프린트는 spec_lint·tree-revision-spec을 한 번도 언급하지 않는다 — «이중 장부 제거»가 전제한 «손 유지 이중 장부»는 실물과 다르다(생성+기계 검증되는 파생물).
- **fix**: §4.1을 재정의 — ⑴ docstring 승격은 «검사기→규칙 역지목 표기의 파싱 가능화(Rule-ID:)»로 한정, ⑵ rule-owner-map의 파생원은 현행 명세 경로(spec_lint) 유지를 명문화, ⑶ 목표를 «docstring↔map↔명세 삼각 대조(⑧ 확장)»로 고쳐 쓴다. ⓓ-전용(human) 규칙의 소유 정보 출처가 명세 등급이라는 사실도 함께 명시.

### F2 [major] «기존 정형구 승격» 전제가 실물 docstring 이질성과 다르다 — S2는 포맷 승격이 아니라 17종+ 재저작이다

- **claim**: P0 요약 §2-③(L46) «27종 중 25종이 docstring «담당 규칙 (rule-owner-map · 총 N)» 정형구로 명기»는 과대 표기이고, 이를 이어받은 블루프린트 §4.1의 «기존 정형구 승격»은 실제 작업 규모·성격을 잘못 잡는다.
- **evidence**:
  - 실측(grep, `dddjango/scripts/check-*.py` 27종 전수): «담당 규칙 (rule-owner-map …)» 정형구 보유 **8종**, rule-owner-map 언급 자체 **10종**. 나머지 17종은 전혀 다른 관례다 — «무엇을 잡나 (규칙 번호는 트리 개정 명세)»형(check-layer-skeleton·check-db-table), § 앵커형(check-app-container «houserules §0-1»), 비-#N 토큰형(check-synthetic-infra-exc «ACL-EX2», check-transient-overmapping «maj1», check-idempotency-scope-creep «DR-24 C3»).
  - 오류 가족 4종은 영어 요약 docstring에 규칙 번호 0이고, 번호는 **본문 주석에 산재**한다(A1 L14: check-error-centralization 4,692행 «본문에 #114·#414… docstring은 영어·요약형»; A1 L27: api-error-controller-contract 6,891행 동형). 2종은 주 규칙 근거 무기록(A1 L15·L25).
  - A1 자체는 판정 기준을 «docstring**·주석**에»로 넓혀 25/27을 셌는데(A1 L9), P0 요약이 이를 «docstring 정형구 25/27»로 압축하며 왜곡됐고 블루프린트가 그 압축본을 계승했다.
- **fix**: §4.1에 실물 분포(정형구 8~10 / 이형 관례 다수 / 본문 주석 산재 4 / 무기록 2)를 명기하고, S2 완료 기준에 «27종 전수 Rule-ID: 재저작(형식 통일)»을 작업으로 배정한다. P0 요약 §2-③도 정정 대상으로 기록.

### F3 [major] S1 미러 lint의 CI 차단 신호(«잔차 존재»)는 실측 영구 정당 잔차와 모순 — 첫날부터 영구 red이거나 차단 부재

- **claim**: §5 L71 «CI 차단은 결정 신호(해시·**잔차 존재**)만»은 A3 실측과 조합하면 성립 불가다 — 정당(플랫폼 재저작) 잔차가 영구 존재하는 쌍이 다수라, 잔차 존재를 차단 신호로 쓰면 S1 게이트는 항상 red이고, 리포트(L70 ③ «신호 등급 리포트»)로만 쓰면 «차단»이 없다. 갈라줄 장치가 블루프린트에 없다.
- **evidence**:
  - A3 실측 영구 잔차: coder 9행(L77)·design-architect 14행(L78)·discipline-reviewer 6행(L82)·**command 쌍 178행**(L86 — «대부분 의도된 플랫폼 재저작»). 잔차 0은 19쌍 중 4쌍(agents)뿐.
  - A3 §4(L105): «「플랫폼 정당 차이」와 「표류」를 가를 **표기 규약이 없다**» — coder 왕복 다이어트가 판별 불가였던 직접 원인. A3 L110은 «잔차 화이트리스트 방식» 성립 여지까지 제시했으나 블루프린트는 채택하지 않았다.
  - D4의 fuzzy+사람 해제(해제 상태 저장)는 «ID 도입 후 twins 필드»의 기제다(§5 L72) — S1은 레지스트리 독립(L69)이라 해제 상태를 저장할 자리가 없다.
  - 저장소에 동형 장치가 이미 있다: corpus_lint ③⑤의 위치 기반 allowlist(파일·지문·기대 건수 — `workspace/tools/corpus_lint.py` docstring), registry_gate의 N∖L 차분(귀속=신규분만 exit 2). 블루프린트가 이를 배선하지 않았을 뿐이다.
- **fix**: S1에 ⑴ 승인 잔차 화이트리스트(파일·지문·기대 건수 — corpus_lint 관례 동형)를 산출물로 명문화, ⑵ 차단 기준을 «신규 잔차(N∖L)»로 정의(registry_gate 원리 재사용), ⑶ 플랫폼 한정 표기 규약(«codex 전용 — 근거» 마커) 도입 여부를 S1 완료 기준에 포함.

### F4 [major] 최대 번호 공간인 무접두 #N(538규칙 명세)의 흡수·해소 경로가 설계에 없다

- **claim**: P0가 «참조 해소 경로는 P2 설계 대상»(P0 §6 L100)으로 이 설계에 명시 이관한 무접두 #N — 5종 번호 공간 중 최대(P0 횡단1 L80) — 이 블루프린트 전문에서 한 번도 다뤄지지 않는다(«무접두»·«538» 출현 0회, §2 alias 예시 L24도 registry#·의사결정#·§·D만).
- **evidence**:
  - 검사기 docstring·코퍼스가 #N을 대량 인용하고, corpus_lint ②가 «무접두 #N=명세 규칙(생존 집합)»으로 별도 집행 중(`corpus_lint.py` docstring ②) — S3 alias lint의 «미흡수 잔여 참조 검사»(§2 L24)가 개시 즉시 이 공간과 만난다.
  - #N 본문 정본은 플러그인 미동봉(E10 L28·P0 §3-A4 L76 «규칙 전문 그라운딩이 원천 불가한 축») — 배포본에서는 quote 대조(§4.1)도 앵커 해소도 불가능한데, 저장소 안(`workspace/design/2026-08-08-tree-revision-spec.md`)에는 실재한다. 어느 층에서 해소할지 미정.
- **fix**: §2 legacy 흡수에 무접두 #N 항을 추가 — 파생원=tree-revision-spec 명시, 대조·해소는 모노레포 층(workspace)에서 수행하고 배포본은 비해소 선언(또는 명세 동봉 결정)임을 명문화. S2 Rule-ID:의 값 공간에 legacy #N 토큰이 포함됨도 함께 명시(S3 이전엔 DJR ID가 없다).

### F5 [major] §3 quote 스키마는 비산문 규범 운반체와 불합치 — D3의 우선 등재 대상이 정확히 그 부류다

- **claim**: 레지스트리 doc.quote(L38-40)는 «규범 문장 인용 + lint 원문 대조»를 전제하나, 저장소 규범의 상당수는 문장이 아니라 표 셀·명사구 체크리스트·예제 코드로 운반되며, D3(L16)가 개정 시 등재하겠다는 밀집 클러스터(ninja §6.2·tdd §5.5)가 정확히 이 부류라 등재 개시 즉시 스키마가 깨진다.
- **evidence**:
  - P0 횡단4(L83): «예제 코드·표 셀이 규범의 1차 운반체인 절 다수(E01·E05) — «산문 추출» 방식 레지스트리는 통째 누락 위험. 명사구 체크리스트 55+항(E07)은 문장 계수 밖» — 블루프린트는 이 경고를 어디서도 처리하지 않는다.
  - E07 L17·L49·L79: ninja §6.1 상태코드 13항 매핑표는 «문장 아님», §2.1(5)·§3.2(4)·§8(10)·§9.1(8)·§9.2(5)·§10(10) 명사구 체크리스트 — 인용할 «규범 문장»이 없다.
- **fix**: §3 doc에 비산문 운반체 변형을 스키마로 정의 — 표 행(앵커+정규화 셀 값 지문)·체크리스트 항(§+항 서수)·예제 코드(코드 블록 지문) — 하거나, 비산문 규범의 등재 방식을 S3 완료 기준의 선행 결정으로 명시.

### F6 [major] glob 라우팅 축(§6·S5)은 D3 범위 결정과 충돌 — 라우팅할 규칙 ID가 사실상 없다

- **claim**: §6(L77) «diff 경로→BC/계층→**규칙 ID 집합**을 레지스트리에 기록»은 D3(소급 전면 등재 금지, ID는 신규·개정분만)·S3(첫 10~30건, L97) 하에서 공급 능력이 없다 — 표준 파일트리 경로에 실제로 걸리는 규칙 대부분(#N 538종, rule-owner-map ⓒ 소유)은 S5 시점에도 DJR ID가 없다.
- **evidence**:
  - 경로→계층은 이미 기계화돼 있다(`standard_tree.py` — 검사기 19종 import, A1 L50). 없는 절반은 «계층→규칙» 연결인데, 그 연결은 legacy #N 공간에만 존재한다(rule-owner-map ⓒ열·검사기 docstring). ID 없는 규칙은 glob 레코드가 가리킬 수 없다.
  - S5는 승격 시에만 진행(L99) — 승격 요건(S4)은 3개월 실적이지 커버리지 임계가 아니라, glob 축 가동 시점의 등재량이 수십 건 규모임이 설계 자체에서 따라 나온다.
- **fix**: §6·S5의 라우팅 값 공간을 «DJR ∪ legacy #N(rule-owner-map 경유)»으로 확장 명시하거나, glob 축을 «등재 커버리지 임계 도달 후»로 이연 조건을 단다.

### F7 [minor] §3 예시 레코드의 quote가 실문서에 없다 — 자기 lint를 통과 못 하는 견본

- **claim**: 예시 quote(L40) «도메인 판정은 도메인 계층이 소유한다»는 architecture-ddd final.md에 verbatim 부재하고(grep 0건), anchor(L39) «§3.2 «판정 소유→구조 이주»»의 실제 §3.2 헤딩은 «엔티티 (Entity)»다.
- **evidence**: `dddjango/skills/architecture-ddd/references/final.md` L539 `### 3.2 엔티티 (Entity)`, L636 «판정 소유→구조 이주» 볼드 문단(§3.2 본문 내 — 절 해소는 성립하나 헤딩이 아님). 인용문 grep 0건. 동결본의 예시는 첫 등재 때 그대로 복붙될 개연성이 높다.
- **fix**: 예시를 실존 인용문(예: L636 첫 볼드 문장)으로 교체하고, «§ + 본문 볼드 라벨» 2단 앵커가 코퍼스 관례임을 anchor 필드 규약에 명기(anchor_integrity_check ⑤가 이미 그 문법을 검증한다).

### F8 [minor] §4.4 픽스처 의무화 — 씨앗 오지정, 기존 90케이스 장치 미인지, Stage 미배정

- **claim**: «27종 위반/통과 픽스처 짝 의무화 … 기존 스모크 4종이 제4축의 씨앗»(L65)은 저장소 실물과 어긋난다 — 검사기별 픽스처 짝·기대 exit 전수 실측은 `workspace/tools/fixture_matrix.py`(90케이스)와 `checker_cross_matrix.py`(good/ 교차)가 이미 수행 중이고, 스모크 4종은 «게이트·하네스 행동 고정»이라는 다른 부류다(A2 L79).
- **evidence**: fixture_matrix docstring(케이스 구성 명기)·`workspace/eval/fixtures/` 30개 레인 실재. A2 L17·L77은 fixture/cross 매트릭스를 coverage_check 대응 후보로 분류. 블루프린트에는 두 도구 언급 0회 — 신규분은 «per-rule(ruleid:/ok:) 해상도»뿐인데 그 구분·Stage 배정이 없다(§8 표 어디에도 픽스처 작업 없음).
- **fix**: §4.4에 기존 자산(fixture_matrix·cross_matrix)을 명시하고, 의무화의 신규분을 «검사기 단위→규칙 단위 해상도 상향»으로 좁혀 S2 또는 S3에 배정.

### F9 [minor] 커버리지 표의 무앵커 절 등기 키 미정 — 55절(전문 8곳 포함)은 래칫이 흔들린다

- **claim**: S2 «606절 전수 4값 등기»(L96)에서 무앵커 55절(P0 §2-① L36)의 등기 키가 없다 — 센서스는 행번호 의사앵커(«coder.md L16» 등, E10 표)로 등기했는데 행번호는 편집마다 표류하고, D2(L15)는 참조 축 현상 유지라 새 앵커 신설도 없다. 래칫(스냅샷 대조, L64)이 무앵커 절에서 편집 때마다 오탐한다.
- **evidence**: E10 L126 «앵커 없음 8 = 헤딩 없는 전문», L134 «커맨드 전문은 번호 공간 규약(전역 해석 규칙)을 담는데 앵커가 없다». SKILL.md 무번호 헤딩·서문 인용구(E04~E06)도 동류.
- **fix**: 커버리지 표의 절 키 규약을 S2 설계에 명문화 — «경로 + 헤딩 경로 + 동일 헤딩 서수», 전문은 «(전문)» 고정 키. 행번호 키 금지.

### F10 [minor] 미러 축 관할 지도 미완 — 스크립트 33쌍 릴리즈-사이 공백 존치와 기존 도구 흡수·존치 관계가 미기록

- **claim**: D2 «미러 축 ⑤ 신설»과 S1은 19문서쌍만 다루고, 센서스가 지목한 나머지 무·반방비 지대 — 스크립트 33쌍의 릴리즈 사이 무검사(A3 L107 «반무방비»)·plugin.json 문면(A3 L108) — 의 존치 결정이 없다. 신설 3종(corpus_check·coverage_check·registry_lint)과 기존 21종 생태의 흡수·존치 관계도 A2의 «추측» 대응만 있고 블루프린트 결정이 없다.
- **evidence**: P0 §2-④ L54 «스크립트 33쌍도 릴리즈 시점(Makefile diff -rq)에만 검사». A2 §대응(L77-79) 전부 «추측 표시». 블루프린트에 corpus_mirror_sync·corpus_lint·anchor_integrity_check 등 실명 언급 0회(«anchor lint 계열»·«registry_gate와 동형» 2회뿐).
- **fix**: §8 Stage 표에 «기존 도구 처분» 열(흡수/존치/무관)을 추가하고, 스크립트 33쌍 상시화(byte diff는 1행짜리라 S1에 편승 가능) 여부를 명시 결정한다.

## B. 성립하지 않은 반박 (검증했으나 블루프린트가 옳았던 것)

1. **19문서쌍 목록은 실재와 일치** — claude(스킬 11 + agents 7 + command 1) ↔ codex 대응물 전부 실재. codex 개명 지도(충돌 4종만 `dddjango-` 접두·agents 전원 접두·command→`skills/dddjango/SKILL.md`)는 A3 §2 그대로이고 디렉터리 실사와 일치. §3 twins 예시 경로(`codex-dddjango/skills/dddjango-architecture-ddd/…`)도 실경로다.
2. **Coordinator 표류(#A~#B 누락)는 19쌍 범위 안** — command 쌍이 곧 Coordinator 정본 쌍이라 S1이 커버한다. «codex 전용이라 미커버» 반박은 성립하지 않는다(codex 전용은 openai.yaml뿐 — A3 L96).
3. **절 단위 4값 등기의 적용 가능성 자체는 실증됨** — 센서스가 이미 606절 전량에 절 단위 3값(커버/비커버/불명)을 배정 완료(E01~E10 합계 = 606 검산 일치). 표 셀·명사구도 «절 안»이므로 등기 단위 문제는 아니다(레지스트리 인용 문제는 F5로 분리). 초거대 절의 혼합값 문제는 센서스 방식(대표값)과 동일한 정밀도라 신규 결함이 아니다.
4. **래칫의 «registry_gate 동형» 주장 성립** — registry_gate는 실제로 N∖L 차분·fail-closed·legacy 빚 채널을 갖췄다(A1 §3 + 소스 확인). 오히려 그 동형성을 S1 잔차 게이트에 안 쓴 것이 F3다.
5. **개명 사전의 선행 구현 존재** — anchor_integrity_check ⑥이 codex `dddjango-` 접두 해소를 이미 구현. S1 정규화 1층의 실현 가능성 반박은 성립하지 않는다.
6. **«27종» 계수 정확** — checker_registry가 로스터 27을 import 시 assert, 실파일 27종 확인. 보조 6종 포함 33종도 일치.
7. **4/7쌍 잔차 0 인용 정확** — A3 §3.3 실측 그대로(acceptance-tester·design-review-api/db/ddd).

## C. 렌즈 종합

저장소 대조의 큰 절반은 성립한다 — 19쌍 목록·개명 지도·래칫 동형성·4값 등기 실행 가능성·도구 생태 인식은 실물과 맞고, 승격 사다리 골격 자체는 이 저장소의 «파생 먼저·정본 나중» 관행(rule-owner-map·standard_tree)과 결이 같다. 그러나 S2의 핵심 기제(F1·F2)가 저장소의 실제 파생 체계를 잘못 전제했고, S1의 차단 신호(F3)는 실측 잔차와 산술적으로 모순이며, 최대 번호 공간(F4)·비산문 규범(F5)·glob 공급 능력(F6)은 설계 공백이다. 여섯 건 모두 국소 개정(문단·스키마 필드·Stage 기준 수준)으로 해소 가능하므로, **현 문면 그대로의 동결은 불가, 개정 후 재상정이 옳다**.
