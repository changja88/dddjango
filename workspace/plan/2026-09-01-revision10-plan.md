# 리비전 10호 계획 — 검사기·규범 정합 배치 (v2)

원인 정본: `workspace/design/2026-09-01-revision10-root-cause.md`.
사용자 확정(2026-09-01): 전 항목 한 배치·한 릴리즈 / A3 공유 스캔 셋(#416·#426·#52) 동일
정밀화 / #474 기각 확정 / B1 완주(성문 채번 포함) / 절차 = 원인 파악 → 계획 → 적대 리뷰 →
적용 → 적용 리뷰 → 배포.

상태: **v2 — 구현 완료(커밋 ①~⑩) · verify·적용 리뷰 대기.**
v1 대비 변경: BLOCKER 4건 수리(§3 A3 유지 목록·§4 B1 s018-5 노선+시그니처 확장·§5 C1
⊆response= 조건+화이트리스트) + 권고 전건 반영. 각 반영처에 [L1~L4] 레인 표기.

## 0. 불변 계약

- 규범 문장을 바꾸는 항목(B1 성문·C1·C3)은 «규범 개정 레시피» 전 단계: rdflib 구조 편집 +
  canon 재직렬화(왕복 byte 동일 선확인) → ontology_gate → `ontology_render.py --apply` →
  **ISSUED append(신설 시)** [L4] → LEDGER → **계수표(Expression/Norm 계수 변동 — 각 온톨로지
  커밋마다)** [L4] → q4 골든 → rulepack → final.md 소스 미러 수동 교체 → codex 의미 미러.
- 검사기 항목(A1·A2·A3·B1·C1)의 EXPECTED 4종·codex byte 미러·seal은 **⑨ 일괄 후치** —
  중간 커밋의 verify-base-core red는 확립 관례(리비전 9호 32b22e9→95f489d→b6507ba 선례)
  [L4]. 항목별 커밋은 관련 픽스처 스모크(해당 레인 good exit 0·bad exit 2·발화 목록)만 실증.
- 신설·수정 픽스처는 커밋 전 **타 26종 census 사전 실측(census-중립 저작)** [L2].
- 부칙·문면 변경 후 spec_lint ⑦⑧ 확인(부칙만이라 집계 수치 불변 — [L4] 실측).
- 브랜치 `norm/revision-10`, 머지 전 `make verify` 6/6 green.

## 1. A1 — #396 기술 목록 (검사기 + 픽스처)

- `check-business-vocabulary.py:81` `CURATED_TECH`에 `"pydantic"`·`"rest_framework"` 추가
  [L3 — rest_framework는 FRAMEWORK_TYPES 정합·동일 환경 의존에 걸리는 유일한 동반 후보.
  httpx 등 일괄 추가는 스코프 크리프로 기각].
- **발화면 3곳 명기** [L4]: 141행 #396(의도 목적) 외에 158행 #584(capability 이름 토큰)·
  599행 #19(BC 안 기술 폴더)도 CURATED_TECH 소비 — pydantic/rest_framework 이름의 BC 내
  폴더·capability가 신규 red가 됨(취지상 진탐 — 릴리즈 노트 기재).
- 픽스처: `business_vocabulary/good/`(기존 레인 안 [L4])에 `framework/pydantic/<module>.py`
  (pydantic import·annotation 완비 — census-중립 형태 [L2] 실증됨). 기존 #396 red 케이스는
  `framework/gizmo/`라 교체 불요 [L4].
- 잔존 한계 기록(수정 아님): ① naming ⓓ#36이 같은 `tech_names()`(환경 의존)를 씀 —
  후보 채널이라 게이트 무영향, 후속 후보로 기록 [L2] ② CURATED_TECH↔tech_names 고정
  목록 드리프트(boto3/http/rabbitmq/sns) 정렬 후속 후보 [L3] ③ 근본 완화(검사기를 대상
  프로젝트 venv python으로 실행하는 운용 규약 또는 의존 선언 기반 판정원)는 별건 후속 [L3].

## 2. A2 — DECLARATIVE_BASE_NAMES 3이름 (검사기 + 픽스처)

- `check-public-surface-annotation.py:73`에 `"AbstractBaseUser"`·`"PermissionsMixin"`·
  `"AbstractUser"` 추가. 순수 완화(면제 확대)라 brownfield-safe [L4].
- 픽스처: `public_surface/good/`에 커스텀 유저 모델(bare 프레임워크 필드) green 케이스.
- 후속 후보 기록: 구조적 마감(RHS가 `models.*Field(...)` 꼴이면 base 무관 면제)이 재발
  클래스 자체를 소멸 — 이번 배치 확장은 의미 변경 폭이 커서 기각 [L3].

## 3. A3 — #416·#426·#52 탐지 정밀화 (검사기 + 픽스처)

- `check-business-vocabulary.py:264` 스캔 대상 텍스트를 «스크럽 사본»으로 교체 — `\b` 정규식
  자체는 유지. 스크럽 규칙(**구현 계약: 토큰 span 공백 치환 — untokenize 재조립 금지** [L2]):
  1. COMMENT 토큰 → 공백 치환.
  2. STRING 토큰 → 공백 치환하되 다음은 **원문 유지**: ⓐ dotted-path 꼴(`^[A-Za-z_][\w.]*\.[\w.]*$`
     근사 — 모듈 경로 문자열) ⓑ **BC 이름과 정확 일치하는 단독 낱말**(`^<bc>$` — 앱 라벨·
     라우팅 키·getattr 인자 진탐 보전, 기존 #416 픽스처 생존) [L2 BLOCKER 해소]
     ⓒ **f-접두 문자열은 버전 무관 통째 원문 유지**(≤3.11 단일 토큰 vs 3.12+ FSTRING_*
     분해의 비결정 차단 — fail-closed) [L2·L4].
  3. tokenize 실패 시 **원문 유지**(fail-closed = 현행 동작) [L2].
- 결과: 신규 발화 0(부분집합 성질 — 31레인 실측 완료 [L2]), 소실은 «공백 포함 산문
  문자열·주석»뿐. 잔여 소실 한계(부칙 명기): 문자열 연결 조립(`"application." "promo"`)·
  docstring 안에 파묻힌 dotted-path·`reverse("bc:name")` 콜론 꼴·템플릿 경로 — 기계 탐지
  밖·리뷰어 소관 [L2·L3].
- 픽스처(`business_vocabulary/` 기존 레인): good에 주석·docstring에만 BC 이름(green 증명),
  bad에 dotted-path 문자열(red 유지)·기존 `ORDERS_APP = "orders"` 단독 낱말(red 유지 —
  규칙 2-ⓑ로 생존) 확인.
- 부칙: 행 #416(732행)에 탐지 매체 부칙 1건 — «(#426·#52 공유 스캔 동일)» 명시로 3행
  중복 부칙 회피 [L4], 진탐 한계 채널 명기 [L3].

## 4. B1 — #328↔#462 정합 + 성문 채번

### 4a. 검사기 정합 (check-context-isolation.py)

- **메커니즘** [L4 BLOCKER 해소]: `_apply_same_bc`는 경로를 모르고 `continue`가 성립하지
  않는다. `_scan_imports`(≈272행)에서 파일당 1회 `file_parts[1:]`(driven 상대)로 면제 2꼴을
  선판정해 bool을 `_apply_same_bc`에 전달(시그니처 확장), #328 방출 분기에서 그 플래그면
  방출 생략. 면제 2꼴(port-adapter-pairing 1007~1015와 조건 동치·경로 기준만 환산):
  driven 상대 `("adapter", <cap>, "django_adapter.py")`(len 3·cap ∉ {anticorruption_layer,
  external_system}) / `("adapter", <cap>, "django_adapter", "django_adapter.py")`(len 4 승격 꼴).
- `django_<bc>/admin/`은 loc="django"로 #328 원천 비도달 — 동기화 불요 확정 [L2·L4].
- 픽스처(`context_isolation/` 기존 레인): good에 면제 직꼴+승격 꼴(#462 면제의 첫 good
  실증 겸함 [L2]), bad의 기존 ACL red 1건은 면제 비해당·보존 실측 완료 [L2].
- `check-port-adapter-pairing.py:999~1000` TODO 주석을 «성문 = houserules §5(R-3423)»로
  갱신 — **이 커밋(③)에 동봉**(온톨로지 커밋에 실으면 byte 미러 드리프트 장기화) [L4].

### 4b. 명세 행 부칙

- 행 #328(642행)·#462(691행)에 09-01 부칙: «adapter/<capability>/ 의 django_adapter.py
  (동명 폴더 승격 꼴 포함·anticorruption_layer/external_system 제외)는 비애그리거트 ORM
  쓰기 능력의 기술 구현으로 django_<bc>/ ·ORM 모델 import 허용(2호 실증·사용자 A안 —
  houserules §5·R-3423 성문)». **⑧ 커밋(온톨로지 ⑤ 뒤)** — §5 선참조 dangling 방지 [L4].

### 4c. houserules 성문 채번 [L1 BLOCKER 해소 — 노선 교체]

- **위치: `discipline-houserules` final.md 문서 말미(«배경» 절 뒤)** — 새 절
  `## §5 driven 출구 면제 — 성문`, 절 키 **s018-5**. 밀림 0·IRI 재명명 0·원장 신규 1행
  append만(MEDIATION row J «신규 절만 다음 미사용 서수» 정합). ~~배경 직전~~ 노선은
  원장 부식 검사(verify-ontology 8/10) red — 기각.
- 값: persistence 셋 + `django_<bc>/admin/` + `adapter/<capability>/django_adapter.py`
  (승격 꼴 포함·ACL/external_system 제외) — #462 검사기 메시지와 동일 문면.
- 절차(한 커밋 ⑤): ① `discipline-houserules-final.ttl`에 Section s018-5·Block s018-5/b1·
  Norm R-3423(신설·revision 1) + **ISSUED append**(꼬리 R-3422 → R-3423 확정 [L1])
  ② wiring은 `ontology/wiring/discipline-houserules-final.ttl`에 enforcedBy
  check-context-isolation·check-port-adapter-pairing 2건(동일 쌍 선례 R-0577 등 4건·구조
  검사 통과 확인 [L1]) ③ **배포 final.md 말미에 `## §5 …` 헤딩 1줄 수동 시드**(--apply는
  절 신설 불가 — apply_to_corpus «현재 분할에 절 없음» [L1]) ④ `ontology_render --apply
  discipline-houserules-final` ⑤ LEDGER 신규 s018-5 1행 append ⑥ 소스 미러 수동 교체 →
  `corpus_mirror_sync --write` 11/11 ⑦ 계수표(Norm/Work +1·Expression +1)·q4 골든
  (distinct_works +1)·rulepack.

## 5. C1 — #63 tree 레인 게이트 + 문안

### 5a. 검사기 (check-openapi-error-declaration.py `_tree_slice63` 3435~3443행)

- 구현 구조 [L4]: walk 트리거는 유지하고, **kw.value가 top-level `ast.Dict`이고 그 안
  "responses" 키의 값이 `ast.Dict`인 꼴에만 통과 게이트 적용** — 그 밖(중첩 responses·
  변수 간접 등)은 현행 동작 그대로.
- **통과 조건(전부 충족 시에만 방출·`keys` append를 함께 생략** — `_suppress_overlapped_tree`
  zip 짝 불변 [L4]**)**:
  1. responses dict의 키 전부가 **리터럴**(`_literal_status` — 정수·숫자 문자열)로 해석되고,
  2. 전부 **100–399 화이트리스트** 안이며(0·600+·4xx·5xx는 방출 — 블랙리스트 반전 [L3]),
  3. **그 status 집합 ⊆ `_scan_response_statuses(node)`(`response=` 선언 집합)** —
     openapi_extra로 성공/리다이렉트 status를 «신설»하는 우회 차단 [L3 BLOCKER 해소],
  4. **splat(`**…` — 키 None)이 하나도 없다**(None 키는 정적 해석 불가 취급 → 방출 —
     code 레인의 None-skip 판형 복사 금지) [L2·L3].
- code 레인 둘·override·monkeypatch 사이트 무변.
- 픽스처(`openapi_error_declaration/` 기존 레인): good에 `response={200: X}` +
  `openapi_extra.responses[200].headers`(통과 증명), bad에 ① 오류 status red 유지(기존
  "404" 케이스) ② 변수 키 red ③ **splat 키 red** ④ `response=`에 없는 성공 status
  (`responses[201]`) red. 기존 픽스처 영향 0 실측 완료 [L2]. verify-base-backstop은
  성공-only 케이스 0건이라 무영향 [L4].

### 5b. 규범 리비전 4건 (amendment · 3문서)

- 대상(전수 확인 — 잔여 0 [L1·L4]): **R-0089**(ninja final «응답 선언과 OpenAPI» 절 —
  s023-6.2/**b34**, **R-0086~R-0090 5규범 공유 블록**) · **R-0683**(ninja final §2.2 불릿 —
  s009-2.2/b10) · **R-2932**(ninja skill 요약) · **R-0339**(command 검사기 #5 설명 «프로필
  무관 선행» — 현행 revision 2→3). ~~v1의 R-0089/R-0683 귀속은 뒤바뀌어 있었음~~ [L1].
- b34는 텍스트 개정 + **R-0089만 리비전**(나머지 4규범의 문장 무변 — 다규범 블록 개정
  선례(리비전 7호) 준용, 실행 시 재확인) [L1].
- 신문안 요지: «이 금지의 대상은 **오류 응답(4xx·5xx) 항목**이다. `response=`로 직접
  선언된 성공·리다이렉트 status(100–399)의 **메타데이터 보충**(header 문서화 등)은
  허용한다 — 보충 status 집합은 `response=` 선언 집합의 부분집합이어야 하며 [L3],
  openapi_extra의 responses에 오류 status가 하나라도 있거나 status 키를 **리터럴**로
  읽을 수 없으면(변수·상수 표현식·splat 포함) 위반이다(fail-closed) [L3 — «정적»이 아니라
  «리터럴»]. 성공 항목의 content/schema 기입은 #63의 기계 판정 밖이다 — `response=` 선언과의
  문서 정합은 리뷰어 소관 [L3 content 방침 명시]».
- 재투영 **3문서**(implementation-django-ninja-final·-skill·command-dddjango [L4]) + LEDGER +
  계수표(Expression +4) + 소스 미러 + codex 의미 미러(`codex-dddjango/skills/
  implementation-django-ninja/SKILL.md`(무접두 [L4])·`codex-dddjango/skills/dddjango/SKILL.md`).

### 5c. 명세 행 부칙

- 행 #63(387행) 부칙: 5b 요지 + 기존 사각 기록(변수 간접 `openapi_extra=EXTRA`·
  `NinjaAPI(openapi_extra=…)` 생성자 레벨은 현행/개정 공히 백스톱 미탐 — 규범 위반은
  위반, 커버리지 한계 명기) [L3].

## 6. C2 — #267 부칙 (명세만)

- 행 #267(589행) 부칙: «값 집합 **Enum 계열**(StrEnum·Enum·IntEnum·Choices 류 [L3])도
  값 객체다 — 공개 클래스 계수에 포함한다. 참고: ErrorSchema+ErrorCode 동거는 #572 소관
  (`bc_error_schema.py`는 driving_layer라 #267 대상 밖 [L4 — «예외» 표현 정정])».

## 7. C3 — 승격 스코프 조사 의무 (R-3417 amendment)

- `discipline-houserules-skill.ttl` s004-1/**b7**의 `djr:text` 개정 + R-3417 Expression
  revision 2(amendment) [L4]. 단독 노선 확정 — coder/command는 참조형 배선이라 자동 승계,
  reviewer 판정 의무 규범은 **R-3422**(~~v1의 R-3419는 오기~~)·개정 불요 [L1].
- 신문안 요지(주체 명시 — 감사자 «만» 목록과 모순 회피 [L1]): «② 승격의 **집행자**(발견을
  집행하는 coder)는 집행 전에, **기존 파일 승격(G0 ⓐ→슬라이스 0)의 제안·실행자는 제안
  전에**, 대상 모듈을 **모듈 객체·모듈 경로 문자열로 참조하는 곳** — 테스트 fixture의
  monkeypatch, `unittest.mock.patch("pkg.mod.attr")` 문자열형 [L3], settings 등 dotted-path
  문자열 참조, 동적 import — 을 저장소 전수에서 조사해 발견 전건을 슬라이스 스코프에
  편입한다. 재수출 `__init__`의 import 표면 불변은 **읽기 표면**만 보증하고 **패치 표면**은
  보증하지 않는다. 스코프 밖 발견이면 집행 전 보고(설계 반송 — R-3416 판형)한다. 감사자의
  판정 재료는 현행 유지».
- 재투영 discipline-houserules SKILL.md + LEDGER + 계수표(Expression +1) + rulepack +
  소스 미러 + codex 의미 미러(`dddjango-discipline-houserules`).

## 8. D — #474 기각 (산출물 없음)

- 원인 문서 §D가 기각 기록. 조감도 리비전 10호 행에 한 줄.

## 9. 커밋 구성 (자기완결 계약 [L4 반영])

① fix(checkers): A1+A2 + 픽스처 (census-중립 실측 동봉)
② fix(checkers): A3 스크럽 + 픽스처
③ fix(checkers): B1 면제(시그니처 확장) + pairing TODO 주석 상환 + 픽스처
④ fix(checkers): C1 tree 게이트 + 픽스처
⑤ ontology(B1): s018-5·R-3423·ISSUED·wiring·헤딩 시드·재투영·LEDGER·소스 미러·계수표·q4·rulepack
⑥ ontology(C1): 4리비전·3문서 재투영·LEDGER·소스 미러·codex 의미 미러 2·계수표·rulepack
⑦ ontology(C3): R-3417 rev2·재투영·LEDGER·소스 미러·codex 의미 미러·계수표·rulepack
⑧ spec: 부칙 5행(#328·#462·#63·#416·#267 — «4항목 5행» [L4])
⑨ EXPECTED 4종 재실측·codex scripts byte 미러(rsync)·`manifest_seal --write`
⑩ docs: 조감도 리비전 10호 행·원인 문서 정합·계획 상태 갱신
→ `make verify` 6/6 → 적용 리뷰(구현↔계획 독립 감사) → merge --no-ff → `make release` →
설치 안내 → 설치 확인 후 봉인 재발행.

중간 커밋(①~⑧)의 verify-base-core red(byte 미러·EXPECTED·seal)는 확립 관례상 허용 —
머지점 green이 계약 [L4]. ⑤~⑦ 각 커밋은 pre-commit(gate·ledger check) 통과를 위해
재투영+LEDGER 동봉 필수 [L4].

## 10. 적대 리뷰 처분 대장

| 발견 | 처분 |
|---|---|
| [L3-BLOCKER] C1 ⊆response= 부재 | §5a-3 채택 |
| [L1-BLOCKER] B1 배경-직전 노선 원장 부식 | §4c s018-5 말미 노선 교체 |
| [L2-BLOCKER] A3 진탐 소실(#416 픽스처·앱 라벨류) | §3-2ⓑ 단독 낱말 유지 채택 |
| [L4-BLOCKER] B1-4a continue 불성립·§0↔§9 모순 | §4a 시그니처 확장·§0/§9 관례 명문화 |
| [L2·L4] f-string 버전 비결정 | §3-2ⓒ 통째 원문 유지 |
| [L3] 100–399 화이트리스트·splat·«리터럴» 낱말·content 방침 | §5a·§5b 채택 |
| [L3] rest_framework 동반·#584/#19 발화면·재발 완화 후속 | §1 채택·기록 |
| [L3] A2 구조 마감·C2 Enum 계열·C3 mock.patch | §2·§6·§7 채택 |
| [L1] R-0089↔R-0683 귀속 스왑·b34 5규범·R-3419 오기·C3 주체 | §5b·§7 정정 |
| [L4] 계수 오기·④ 순서·TODO 커밋 위치·ISSUED/계수표 명기 | §4b·§9·§0 정정 |
| [L2] census-중립 조건·ⓓ#36 잔존·#462 good 실증 공백 | §0·§1·§4a 채택 |
| 과적합 판정(7건 전건 OK — L3) | 기록 |
