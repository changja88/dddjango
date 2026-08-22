# T3 적대 리뷰 — agent-design-review-api (findings)

- 대상: `workspace/eval/t3/specs/agent-design-review-api.spec.json` + `workspace/eval/t3/worksheets/agent-design-review-api.md`
- 대조 재료 실독: 발주서 · T3-authoring-brief · 원문 `dddjango/agents/design-review-api.md`(84행 전수 문장 계수) · authoring §13~§16 · `ontology_migrate.py` docstring · **check-*.py 27종 로스터 확인 + basis 인용 검사기 10종 + `check-transient-overmapping.py` docstring 직접 실독** · basis의 grep 주장 전건 재실행(marker 발행 3종·STOP 0·register_controllers 유일·Sunset 0·AuthenticationError 0·title 술어 0·204·406/415·pagination 0·str(exc) 자기수집) · 파일럿 `spec-implementation-django-ninja-final.json` slot-11·«기본 500» 배선 판형 대조 · `dddjango/agents/design-architect.md`·`design-review-db.md`·`design-review-ddd.md` 원문 대조.
- 검증 재현: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/agent-design-review-api.spec.json` → exit 0 (블록 52 · Work 104 — 검수표 기재와 일치).
- 2차 패스(재검증): F1~F8 전건을 실물 재대조로 재확인(architect raw L59 문단·R9 누락·E-only 4건·파일럿 판형·grep 전건) — 전건 존속. 추가 발견 F9(medium)·F10(low).
- 판정: **반송 1건(high) + 수리 3건(medium) + low 6건**. spec·worksheet 는 수정하지 않았다.

## F1 — high · ④재진술 · s006/b15 (L72)

**주장**: L72 의 인증 실패 규범 묶음(«모든 Ninja profile의 인증 실패는 `None`을 return하거나 framework `AuthenticationError`를 raise해야 한다 … `request.auth`에 저장하면 blocker … 별도 승인된 406/415는 … 함수형 `Router`나 global handler를 강제하면 안 된다 … preserve-established 는 … 협상 behavior를 보존해야 한다»)은 `dddjango/agents/design-architect.md` s005 의 한 행(raw L59)과 **근접 축자 사본**이고(«…인증 실패에서는 None을 return하거나 framework AuthenticationError를 raise한다. AuthenticationError object나 ErrorSchema을 return하지 않고 어느 것도 request.auth에 저장하지 않는다. 406과 415는 각각 별도 사용자 승인을 받은 경우에만 tested version-compatible Ninja-owned pre-body/framework HttpError 경로로 구현하며 함수형 Router나 전역 handler를 강제하지 않는다…» — 직접 실독 확인), `implementation-django-ninja/references/final.md` §6.2 기이관 블록(raw L398–399·L800–814)에도 동일 규범이 실재한다. 그런데 **worksheet §3 재진술 유예 표에 s006/b15 행이 없다**. 검수표 스스로 norm 88·89 의 basis 에 «파일럿 §6.2 **동일 규범**»·«파일럿 …와 동축»이라고 적어 상대의 실재를 인정했고, 같은 불릿 묶음의 L71(R8)·L73(R9)·L74(R10)·L76(R7)은 불릿 단위로 개별 채록했으면서 L72 만 빠졌다. R6 의 architect 병렬 좌표는 L56·L58–69 로 자기 한정돼 L72 를 덮지 못한다. 유예 표는 소급 패스의 유일한 입력이므로 이 공백은 교차 문서 중복 Work 가 영구 잔존하는 경로다.

**수정안**: worksheet §3 에 행 추가 — `R17 | s006/b15 (L72) | 인증 실패 None/AuthenticationError·request.auth 금지·별도 승인 406/415 경로·preserve 협상 보존 | agent-design-architect/s005 (architect raw L59 상당 센서스 행) · implementation-django-ninja-final §6.2 (기이관 — raw L398–399·L800–814 상당) | 규정판↔심사판 병렬(술어 «구현한다/않는다» ↔ «여야 하고/보존해야 한다»)`. 유예 총계 16→17 갱신.

## F2 — medium · ④재진술 · s006/b16 (L73)

**주장**: R9 는 L73(«native download/stream/redirect와 schema-less 204 carveout을 존중하는지 본다»)의 상대를 `implementation-django-ninja-final` §6.2 하나로만 기록했다. 그러나 `design-architect.md` s005 slot 12 말미(raw L57)에 «native download/stream/redirect와 schema-less 204는 선언 Schema 규칙의 carveout이다»가 실재한다(직접 실독 확인) — R9 가 기록한 것과 같은 «규정판↔심사판 병렬» 관계다. R8·R10 은 architect 를 병기했으면서 R9 만 빠뜨린 비대칭.

**수정안**: R9 의 상대 문서 열에 `agent-design-architect/s005 (slot 12 말미)` 병기.

## F3 — medium · ③배선 · s006/b12 (L68) norm 77

**주장**: norm 77(«slot 11 — 두 path 공통의 승인 ErrorSchema 생성·approved header의 주입 HttpResponse 설정·two-argument Status 직접 return **확인**»)의 원문 술어는 «…return하는지 **확인한다**» — 검수표 §0 P-B 가 스스로 세운 판별(«①문면 술어가 심사 행위 → D: agent-design-review-api, 검사기 실재 시 enforcedBy 병기로 분업»)에 정확히 해당하는데 delegatedTo 가 통째로 탈락하고 E-only 다. 같은 블록의 norm 74(«…선택됐는지 확인한다»)는 같은 술어 형태로 D 를 병기했다 — 동일 판별자 아래 상반된 배선. 파일럿 §6.2 의 E-only 판형 승계는 norms 75·76(술어가 «…해야 한다/blocker다»인 직접 요구)에는 성립하지만, 심사 술어인 77 에는 §16 «기본값 이탈은 문면 근거» 요건을 채우는 근거가 basis 에 없다.

**수정안**: norm 77 에 `delegatedTo: [agent-design-review-api]` 병기(spec + 검수표 §2 #77 행). 또는 존치하려면 basis 에 «심사 술어임에도 D 생략» 의 문면 근거를 신설.

## F4 — low · ③배선 · s006/b12 (L68) norms 75·76·78

**주장**: norms 75·76·78 도 D 전면 탈락(E-only)이다. 술어가 직접 요구·금지형이고 파일럿 spec 실물(`spec-implementation-django-ninja-final.json` s023-6.2 — exception path·Result/None path·두 인자 Status 행 전부 E-only·D:None, 직접 확인)과 동형이라 방어 가능하나, 그 파일럿은 **규정판**(implementation 스킬)이고 이 문서는 **심사판**이다. 검수표 §0 P-B 는 «s005·s006 이 여기 들고 … enforcedBy 를 병기해 분업»이라 선언했으므로 세 규범의 E-only 는 자기 선언과의 잔여 긴장이다. spec 104건 중 delegatedTo 부재는 이 4건(75~78)뿐 — 의도라면 §0 에 그 구분 기준 한 줄이 있어야 한다.

**수정안**: §0 P-B 에 «직접 요구형 문장(술어가 코드 계약 자체)은 파일럿 판형대로 E-only, 심사 술어(«…확인한다»)만 D 병기» 기준을 명시하거나, 75·76·78 에도 D 병기로 통일.

## F5 — low · ③배선 · s005/b3 (L49) norm 28

**주장**: norm 28(«실패 상태 코드의 정확성 점검(401/403 인증·인가, 406/415 협상, 409/422 충돌·검증)»)의 E 병기 2종은 술어 축이 어긋난다 — `check-business-vocabulary` #119 는 «framework 소유 status 의 BC 재선언 금지»(= L71/norm 86 의 축이고 거기 이미 정배선), `check-ninja-boundary-middleware` 는 «자작 전역 미들웨어 차단»(= L72/norm 90 의 축이고 거기 이미 정배선)이다. 둘 다 «상태 코드 선택이 의미론에 맞는가» 술어를 갖지 않는다. norm 29 에서 `check-idempotency-scope-creep` 을 «축이 반대·술어 없음»으로 배제한 §0 절제 원칙을 같은 강도로 적용하면 이 병기도 철회 대상이다. basis 가 «둘 다 코드 측 부분 축»이라 한계를 명시했고 오용-차단이 정확성의 부분 집행이라는 반론도 성립해 low.

**수정안**: E 철회(D-only) 권고. 존치 시 §0 절제 원칙에 «오용-차단 축은 부분 커버로 인정» 기준을 명시해 norm 29 배제 논리와의 경계를 그을 것.

## F6 — low · ②규범식별 · s006/b13 (L69) norm 82

**주장**: L69 2문째의 선두절 «slot 6 shape와 별도 변경 승인은 **유지하되**»가 norm 82(금지만 라벨링)에 미반영이다. 저작자는 같은 문서에서 한 문장 안 이질 축을 분리하는 판정(L52-3 분리·L56-3 분리·L71 분리 — 선행 적대 리뷰 F1 승계)을 반복 적용했는데 이 문장만 접었다. 다만 선두절을 slot 6 규범(norms 56–58)의 재확인·양보절로 읽으면 접기가 성립하고, architect 원문 slot 12 도 같은 2절 구조라 low.

**수정안**: 검수표 §4 에 이 접기의 근거 한 줄 추가(«유지하되 절은 slot 6 Work 재확인이라 미채번») 또는 Obligation 1건 분리 채번(+1 → 105).

## F7 — low · ④재진술 · s003/b3 (L25)

**주장**: 무규범 prose 로 처리된 L25 불릿 안의 «`create | approved-change`는 일반 G1과 분리해 받은 명시적 사용자 shape 승인»은 L63/norm 57(«일반 G1 승인과 분리된 explicit user approval evidence»)과 동축 문구다. prose 는 Work 미승격이라 spec 처리 자체는 규약대로지만, 검수표 §4 의 애매점 기록에 이 동거가 없다 — 소급 패스·후속 개정 시 L63 개정이 L25 문면과 어긋날 수 있는 자리다.

**수정안**: 검수표 §4 에 참고 기록 한 줄(«L25 불릿의 승인 문구는 L63 norm 57 의 정의 반향 — prose 유지»).

## F8 — low · ④재진술 · s001/b2 ↔ s007/b1

**주장**: «명세나 코드를 직접 수정하지 않는다»(L3, norm 3) ↔ «두 모드 모두 코드·명세를 수정하지 않는다(읽기 전용)»(L82, norm 102)는 문장 단위로 근접 축자다. spec `restates` 미기입의 방어(블록 대 블록 관계 불성립 — description 한 줄에 규범 3개 동거)는 §15 문면과 정합하고 양쪽 basis 에 «동축 재진술 의심»을 남겨 소급 탐지 가능하게 했다 — 처리 자체는 수용. 다만 결과적으로 같은 규범 내용의 Work 2건(3·102)이 그래프에 병존하므로, 소급 패스 재판단 대상임을 §4-④ 에 이미 적힌 수준보다 명시적으로(«Work 3↔102 통합 후보») 남기는 편이 안전하다.

**수정안**: 검수표 §4-④ 말미에 «소급 패스 통합 후보: Work #3 ↔ #102» 1행 추가.

## F9 — medium · ③배선 · s006/b11 (L67) norm 72 (+ s005/b3 norm 28 연좌)

**주장**: `check-transient-overmapping.py`가 spec·검수표 어디에도 등장하지 않는다(grep 0건 — §0 절제 목록에도 없음). 그 docstring은 «API 경계에서 OperationalError/DatabaseError 를 영구장애 구별 분기 없이 클래스 통째 retryable status(503/409)로 무조건 매핑한 형태만 차단»을 명시하고 실물 판정(`RETRYABLE_STATUSES = {503, 409}` L91 · 진단 문구 L225)을 갖는다 — 이는 norm 72(«raw infra 기본 500…») basis의 «‘기본 500’ 판정 자체는 미집행» 주장을 절하시킨다(기본 500 위반의 대표형인 blanket 비-500 매핑을 기계가 차단). norm 28(409/422 충돌·검증 축)에서도 #119·boundary-middleware보다 축이 가까운 후보인데 심의 흔적이 없다. 검수표 필독 선언(«27종 docstring 선두 전수 실독»)과 §0 절제 원칙(«축이 반대이거나 술어가 없는 검사기는 병기하지 않고 **그 사실을 basis 에 적었다**») 양쪽에 비추어 미등장은 이행 공백이다. 반론: 파일럿도 «기본 경로 = framework 미식별 500»을 D-only(discipline)로 배선해 transient-overmapping 을 안 썼고, 검사기 자기 축 선언이 slot 10 문면이 아니라 «과잉매핑 차단»이라 medium 에 둔다.

**수정안**: norm 72 에 `check-transient-overmapping.py` E 병기(한계 문구: «무조건 매핑형 한정 — 기본 500 일반 판정은 여전히 심사 몫») 후 basis 의 «미집행» 문구 완화, **또는** §0 절제 목록에 배제 근거 1행 등재(예: «transient-overmapping 은 preserve handler 방어선이라 신규 매핑 심사 축과 다름» — 성립 여부는 저작자 판단). norm 28 도 같은 심의를 §0 에 기록.

## F10 — low · ④재진술 · s004/b1 (L34) norm 13

**주장**: 같은 문서 안 «수정 금지» 동축은 2쌍이 아니라 3각이다 — s001 b2-3(norm 3 «명세나 코드를 직접 수정하지 않는다») · **s004 b1-2(norm 13 «명세를 직접 고치지 않는다(반영은 architect의 몫)»)** · s007 b1(norm 102). 검수표 §4-④는 ⑴ s001↔s007 ⑵ s001 b6↔s002 만 심의했고, norm 3·102 의 basis 에는 «동축 재진술 의심» 태그가 있으나 norm 13 basis 에는 없다 — 소급 패스가 세 번째 꼭짓점을 놓칠 수 있는 자리다. norm 13 은 모드·대상(DESIGN_CONTRACT_REVIEW 산출물의 명세 한정)이 좁아 부분 중첩 판정 자체는 타당해 low.

**수정안**: 검수표 §4-④ 심의 대상에 s004 b1-2 를 추가하고(판정은 부분 중첩 유지 가능), F8 수정안의 통합 후보 기록을 «Work #3 ↔ #13 ↔ #102 동축 3각»으로 확장.

## 성립 확인(반박 시도 후 기각한 주장 — 재검 불요 근거)

- marker 3종 공동 발행: `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED` 발행 문자열이 controller-contract·error-centralization·openapi-error-declaration 3종에 실재(grep 재실행) — norm 6 배선 성립.
- `STOP_FOR_USER_APPROVAL`·Sunset/deprecation·`AuthenticationError`·페이지네이션/레이트리밋 술어 보유 검사기 0 — 재실행 일치. norms 40·46·50·88·89·94·96 의 기본값 위임 성립.
- `title` 술어 0 주장 성립 — grep 히트 4건은 전부 `.title()` 문자열 메서드·`check-naming.py` 의 문구계 필드 상수(HTTP title property 술어 아님).
- 406/415 유일 보유 주장 성립 — `check-business-vocabulary.py` 의 «415» 히트는 규칙 번호 `#415`.
- `str(exc)` 자기 오류 수집 주장 성립 — 5개 검사기 히트 전부 errors/issues append 문맥.
- `register_controllers` 유일(check-composition-root)·204 carveout 실물(L1025)·«one narrow exception or try-free Result path»(L7125)·«direct two-argument Status»(L7126)·`HTTP_RESPONSE` 상수(L82)·`keyword.arg in {status, status_code}`(L3517)·«helper/handler/raw» 진단(L7126) — basis 인용 전건 실물 일치.
- census +7(97→104)의 분해 전건을 원문 문장 계수로 독립 재현 — s004 +2·s005 +1·s006 +4 모두 문장 실재. spec < census 절 0 — 누락 위험 주장 성립.
- 블록 경계·kind: 도구 exit 0(연속·비중첩·전체 커버 단언 통과) + 수기 대조 — 표·코드 펜스·체크리스트 0 문서라 오지정 표면 자체가 없음. 프론트매터 판형(`---` 헤딩·skills 한 덩이)은 architect 선행 판형과 동일. ①렌즈 지적 0건.
- Override 0건 판정 성립 — L66 canon 예외는 우선 철회가 아니라 carveout(Exception 적정).

## 처분 (수리자 — 2026-08-22)

- 대조 재실독: 원문 `dddjango/agents/design-review-api.md` 전문 · `dddjango/agents/design-architect.md`(마커 7행 확인 — raw L59 = 센서스 L54, raw L57 = 센서스 L52) · `dddjango/skills/implementation-django-ninja/references/final.md`(auth raw L397–401·L799–801 · carveout raw L832–834 · 406/415 §6.3 raw L843–860) · `check-transient-overmapping.py`·`check-business-vocabulary.py`·`check-ninja-boundary-middleware.py` docstring 실물 · 파일럿 `spec-implementation-django-ninja-final.json`(s022-6.1·s023-6.2 = 기이관 범위 확인).
- 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/agent-design-review-api.spec.json` → **exit 0**(블록 52 · Work 104 — 수리 전후 불변 · `--write` 미사용).

| # | 처분 | 근거 한 줄 |
|---|---|---|
| F1 | **fixed** | 성립 — architect raw L59(=센서스 L54)에 인증 실패 3문이 실재하고 ninja §6.2 auth 블록(raw L397–401·L799–801)도 실물 확인. R6 좌표(이 문서 L56·L58–69 ↔ architect L39·L41–52) 어느 쪽도 L72↔L54 쌍을 덮지 못해 소급 패스 입력 공백이 맞다 → **§3 에 R17 신설**, 406/415 절반의 규정판 상대가 §6.3(기이관 아님)임을 함께 명시, 유예 총계 16→17. |
| F2 | **fixed** | 성립 — architect slot 12 말미(raw L57 = 센서스 L52)에 «native download/stream/redirect와 schema-less 204는 선언 Schema 규칙의 carveout이다» 실재 확인 → **R9 상대 열에 architect 병기**(R8·R10 과의 비대칭 해소). ninja 좌표도 실측치(raw L832–834)로 정정. |
| F3 | **fixed** | 성립 — L68 해당 문장의 술어는 «…직접 return하는지 **확인한다**»(심사형)이고 같은 블록 norm 74 가 동일 술어형으로 D 를 가진다. §0 P-B 자기 판별과의 모순이 맞다 → **norm 77 에 `delegatedTo: [agent-design-review-api]` 신설**(spec + §2 #77 행). |
| F4 | **fixed** | 부분 성립(«의도라면 기준이 §0 에 있어야 한다») — norms 75·76·78 의 술어는 «…해야 한다/…하면 blocker다»(직접 요구형)이고 파일럿 규정판 s023-6.2 판형과 동형이라 **E-only 는 존치**하되, **§0 P-B 에 «심사형→D 병기 / 직접 요구형→E-only» 기준을 명문화**하고 D 부재가 3건으로 한정됨을 적었다. |
| F5 | **fixed(권고 채택 — E 철회)** | 성립 — #119 는 «framework 소유 status 의 BC 재선언·광고 금지»(norm 86 축·거기 정배선), boundary-middleware 는 «`driving_layer` 자작 미들웨어의 전역 자가등록 차단»(norm 90 축·거기 정배선)이고 둘 다 «상태 코드 선택의 의미 적합성» 술어가 없다(docstring 실독). norm 29 의 배제 논리와 대칭을 맞춰 **norm 28 을 D-only 로 철회**하고, «오용-차단 축은 부분 커버로 인정하지 않는다»를 §0 절제 원칙의 경계선으로 명문화. 같은 검사기를 자기 축 규범에만 두어 커버리지 이중 계상도 제거. |
| F6 | **fixed(첫째 안 — 접기 존치 + 근거 기록)** | 접기 판정 자체는 **유지**(«유지하되» 절은 술어가 없는 양보절이고 지시 대상이 이미 채번된 slot 6 norms 56–58 · architect 규정판도 동일 2절 구조). 분리 채번은 «절이 둘인가»가 아니라 «술어+소유자가 갈리는가»가 기준이므로 +1 채번은 하지 않고 **§4-⑧ 에 접기 근거와 분리 기준을 기록**. |
| F7 | **fixed** | 성립 — L25 불릿의 승인 문구는 norm 57 정의의 반향이 맞다. prose 유지는 규약대로이므로 spec 무변경, **§4-⑨ 에 동거 사실과 후속 개정 리스크를 기록**. |
| F8 | **fixed** | 성립 — spec `restates` 미기입 방어는 §15 와 정합하므로 존치하고, **§4-④ 에 «소급 패스 통합 후보» 행을 신설**(F10 과 합쳐 3각으로 기록). |
| F9 | **fixed(대안 채택 — 배제 근거 등재) / E 병기는 기각** | 공백 지적은 성립(«27종 전수 실독» 선언과 절제 원칙에 비추어 미등장은 이행 공백) → **§0 절제 목록 ⑴ 에 배제 근거를 실물 인용과 함께 등재**하고 norm 72·28 basis 에 심의 흔적 기록. 다만 **E 병기는 채택하지 않았다**: 이 검사기 docstring 이 자기 축을 «G1 승인된 `preserve-established` handler 방어선»으로 선언하고 «code-json 에서는 custom handler 자체가 독립적으로 위배되므로 이 checker 가 발화하지 않아도 근거가 되지 않는다»고 명시하며, 헬퍼 위장·register-only 를 «일부러 잡지 않는다(저-recall)» 하고 의미 렌즈를 architect·discipline 로 이양한다 — norm 72 는 slot 10 의 **code-json 분기** 문장이라 축이 어긋난다. 따라서 basis 의 «기본 500 일반은 미집행»은 절하되지 않고 문구만 정밀화했다. |
| F10 | **fixed** | 성립 — «수정 금지» 동축은 norm 3·13·102 의 3각이 맞고 초판은 norm 13 에만 의심 태그가 없었다 → **norm 13 basis 에 태그 추가 + §4-④ 심의 대상에 s004 b1-2 편입**(판정은 부분 중첩 유지), 통합 후보 기록을 «#3 ↔ #13 ↔ #102»로 확장. |

**집계: 반영 10건(그중 F4·F6·F9 는 제시된 대안 중 근거가 서는 쪽을 선택) · 전면 기각 0건 · 부분 기각 1건(F9 의 `enforcedBy` 병기 요구).** spec 변경은 4곳(norm 13 basis · norm 28 배선·basis · norm 72 basis · norm 77 배선·basis)이고 Work 채번·블록 경계는 불변이다.
