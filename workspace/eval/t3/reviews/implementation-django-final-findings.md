# T3 적대 리뷰 — implementation-django-final (2026-08-22)

- 대상: `workspace/eval/t3/specs/implementation-django-final.spec.json` + `workspace/eval/t3/worksheets/implementation-django-final.md`
- 대조: 발주서 · T3-authoring-brief · 원문 final.md(1789행) · `dddjango/scripts/check-*.py` 27종 docstring 전수 실독 + 쟁점 3건은 구현부 실독(choices-literal-consumption의 default 판정 · db-table #630 값 검사 · domain-model #549)
- 기계 확인: `ontology_migrate.py`(--write 없음) exit 0 재현 · 63절/246블록/220 Work/재진술 6블록 실측 일치 · 절별 Work 수 발주서 대사 전건 일치(문서 내 재진술 3건 흡수 포함 — §15 계약 합치)
- 판정: **불합격(반박 성립)** — high 2 · medium 7 · low 4

---

## HIGH

### F1 [배선 · s015-2.5] «domain Enum 파생의 .value 평탄화» enforcedBy 오배선 — 집행 불능 검사기 부착

- 주장: 이 Obligation의 위반형은 «직렬화 자리에 StrEnum 멤버를 `.value` 없이 직접 두는 것»(`default=OrderStatus.PENDING`)이다. `check-choices-literal-consumption.py`는 구현부(167~174행)가 **`default=<문자열 Constant>`만** 잡고, 비-Constant(Attribute)는 `.value` 유무와 무관하게 전부 «정상» 통과시킨다 — 즉 `default=OrderStatus.PENDING`(위반)과 `default=OrderStatus.PENDING.value`(준수)를 구별하지 못한다. basis가 인용한 docstring 5)는 담당 규칙이 아니라 **거짓양성 회피(면제) 조항**이다. spec 스스로 바로 옆 규범(«직렬화 자리의 StrEnum 멤버 직접 배치 금지»)에서 "checker 5)가 비-Constant를 «정상»으로 통과시킴"이라며 D2 위임했고, worksheet 메모 5는 «인용이 있다고 배선하면 오배선이다»라는 원칙까지 명문화했다 — 같은 원칙이 이 행에 적용되지 않았다.
- 수정안: s015-2.5/b4의 `.value` 평탄화 norm에서 `enforcedBy` 제거, D2 위임(근거: docstring 5)는 면제 조항 — 멤버 직접 배치와 `.value`를 구별 못 함). worksheet 배선 표 해당 행의 E → D2 정정, 집계 연동 수정.

### F2 [배선 · s052-10.4] check-db-table #630 basis 허위 — docstring은 «존재 + 값» 검사인데 «존재만 본다»로 인용

- 주장: «기존 테이블명의 db_table 명시 보존» norm의 basis는 "②check-db-table #630 «신규 모델 Meta.db_table 존재» — 문면 스스로 «존재만 보고 값 형태는 보지 않는다»고 부분 커버 명시"라 적었다. 그러나 검사기 docstring 실물은 "#630 신규 모델 `Meta.db_table` **존재 + 값 `<app_label>_<entity_snake>`**"이고, 구현부(417~420행)는 신규 파일 모델의 db_table 값이 규약과 다르면 blocker를 낸다(«db_table ≠ 규약» 메시지 실재). ② 인용이 «+ 값» 부분을 잘라낸 허위 인용이다 — 실제로 잘못된 주장의 출처는 원문 §10.4(1037~1039행) 자체이고(원문↔검사기 표류), 4원 대조 의무는 바로 이런 표류를 잡으라고 있는 것이다. 파생 문제: 같은 블록군의 Override «신규 db_table 규약 대비 이력 보존 우선»도 E 배선인데, 인용문 «기존 테이블명 보존(개명 강제 아님)»은 docstring상 **추적된(기존) 모델 한정**이다 — §10.4의 이주 경로(신규 파일로 떨어지는 보존 db_table, legacy명 `tbl_product` 등)에서는 #630이 이 Override와 **정반대로 발화**한다(보존명 규약 불일치 → blocker). 검사기가 규범을 집행하는 게 아니라 대적하는 케이스다.
- 수정안: ① basis를 docstring 실문면(존재+값·신규 파일 한정·기존 추적 모델은 미검사)으로 정정하고 «신규 파일 이주 시 #630이 보존명을 차단하는 충돌» 명시(E 유지 시 «부분·충돌» 표기, 아니면 D2 강등). ② Override 행도 동일 충돌 주석. ③ 원문 §10.4 ↔ check-db-table #630 표류(문서가 검사기 행동을 거짓 서술)를 T3 원장/소급 패스 비고로 상신 — 원문 수정은 이 공정 밖.

---

## MEDIUM

### F3 [배선 · s072-15.1 (+s047-9.2/911 동형)] check-ninja-boundary-middleware 부착 2건 — 데이터 소스 공유는 4원 근거가 아니다

- 주장: 검사기의 유일한 판정은 «BC driving 층 자가정의 미들웨어의 전역 MIDDLEWARE 자가등록 적출»이다(docstring 실독). «SecurityMiddleware 최선두·Session은 Authentication 앞»(순서)과 «request_started/finished의 미들웨어 대체»(시그널 회피)의 어떤 위반형도 이 검사기에 잡히지 않는다 — 순서가 틀려도, 시그널을 계속 써도 MIDDLEWARE 자가등록이 아니면 exit 0. «MIDDLEWARE를 AST로 읽는 유일 검사기»라는 basis는 데이터 소스 공유 서술이지 담당 규칙 근거가 아니고, worksheet 메모 10의 «부분 커버» 표기는 커버 0을 부분이라 부른 것이다. §16 역방향 문면(담당 근거 없는 부착 = 오배선)에 해당.
- 수정안: 두 norm 모두 `enforcedBy` 제거 → D2(근거: 검사기 판정 축은 자가등록 적출 — 순서·대체 판정 규칙 부재).

### F4 [배선 · s049-10.1] «마이그레이션 파일의 버전 관리 포함» → check-mechanism-ownership #336·#337 오배선

- 주장: #336(마이그레이션 자리 — 중앙 폴더 금지)·#337(파일명 django 채번 꼴)은 VCS 포함 여부와 무관하다. gitignore된 마이그레이션도 자리·이름이 맞으면 통과한다 — 위반형 커버 0. 같은 블록의 쌍둥이 규범 «migrations/의 gitignore 등재 금지»는 «.gitignore 판독 검사기 없음»으로 정확히 D2 처리됐다. 같은 내용의 앞뒷면이 다른 배선을 받았다.
- 수정안: `enforcedBy` 제거 → D2(gitignore 쌍둥이 규범과 동일 근거).

### F5 [배선 · s078-16.4/1587] «Idempotency-Key 계약과 DB idempotency storage 정합» → check-idempotency-scope-creep 부착 — 자기 기준 비일관

- 주장: 검사기 축은 G0 «미요청 멱등성 도입 차단»이다(docstring: scope가 미요청 단정 + G1 승인 부재일 때만 발화). 정당 채택된 멱등성의 계약↔storage **불일치**는 어떤 형태로도 잡히지 않는다 — 정합 obligation의 위반형 커버 0. spec은 같은 절의 «필수 불변식의 DB boundary 동반 설계»에서 정확히 같은 이유("미요청 도입 차단 축")로 이 검사기 부착을 **거부**했다. 같은 축 논거가 한 행에서는 D2 사유, 다른 행에서는 E 근거로 쓰였다.
- 수정안: `enforcedBy` 제거 → D2(동반 설계 행과 동일 논거로 통일).

### F6 [배선 · s052-10.4] «기존 0001_initial 불변» #593 부분 커버 주장 — 핵심 함정(도구 재생성)이 정확히 면제된다

- 주장: #593 docstring은 "주어는 «사람»이라 **도구가 만들고 지우는 변경은 손편집이 아니다**"라고 명시한다. 원문 §10.4가 경고하는 핵심 함정은 코더가 `makemigrations`로 0001을 **재작성(fresh initial)**하는 것 — 도구 산출물 모양이라 #593 허용 목록을 통과한다. basis의 «재작성은 손편집의 한 형태(부분 커버)»는 손 편집 재작성에만 성립하고, 문서가 명명한 대표 위반형은 빠져나간다.
- 수정안: E(부분) 유지하되 basis에 «도구 재생성형 재작성은 #593 주어(사람) 밖 — 이력 정합(0002 연쇄·적용 기록) 판정 전체가 reviewer» 명시, 또는 D2 강등.

### F7 [배선 · s052-10.4] «이주 완료 시 옛 루트 앱 통째 삭제» → check-app-container — 규범의 중심 위반형이 정확히 면제 케이스

- 주장: 원문이 명명한 실패 모드는 «move를 copy로 떨어뜨려 새 트리만 만들고 옛 루트를 git에 방치»다. 이 상태는 G2(옛 루트에 *새 도메인 작업* — 신규 디렉터리이거나 신규 마이그레이션) 불성립이고, 성립하더라도 G3(application/ 하위 실질 이주 대응 앱 존재 시 면제)가 정확히 이 케이스를 면제한다 — 이주 완료 후 옛 루트 잔존은 검사기가 구조적으로 발화하지 않는 형태다. basis가 G3 면제를 밝히긴 했으나 «부분 커버»라는 결론이 남는 커버(이주 대응 앱이 비었는데 옛 루트에 새 작업 = 미이주 방치 — 다른 시나리오)와 이 규범을 혼동시킨다.
- 수정안: `enforcedBy` 제거 → D2(근거: G2∧G3 합성이 «완료 후 잔존» 형태를 면제 — 검사기 담당은 «미이주 방치» 축), 또는 basis에 커버되는 시나리오가 이 규범의 위반형이 아님을 명시.

### F8 [배선 · worksheet §2 집계] enforcedBy 집계 오기 — 표·spec 실측과 자기모순

- 주장: worksheet §2 집계 문장은 «enforcedBy 부착 Work 25건 · 링크 30건 · 2종 부착 5건»이라 적었으나, spec 실측(기계 계수)은 **부착 Work 30건 · 링크 33건 · 2종 부착 3건**(s078/1585 외부 side effect · s079 디스패처 자리 · s079 at-least-once)이다. 같은 단락의 검사기별 계수(7+4+4+4+2+2+2+2+2+1+1+1+1)는 33으로 실측과 일치 — 한 단락 안에서 자기모순.
- 수정안: 집계 문장을 30/33/3으로 정정(검사기별 계수는 유지).

### F9 [재진술 · s015-2.5] 교차 문서 유예 누락 — architecture-ddd §3.2와의 최대 쌍이 유예 목록에 없다

- 주장: `architecture-ddd/references/final.md` 635행은 s015-2.5의 내용을 거의 전부 담는다 — «단일 출처는 도메인 enum»·«TextChoices 자체 선언은 순수 인프라 필드 한정»·«.value 평탄화 — implementation-django §2.5»·«소비는 심볼로만, 비교는 ==»·«복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티»·«승격 판정·허용 목록은 discipline-cleancode §2.14». 637행은 «기존 배치는 규약이 아니라 아직 안 갚은 빚 — 트리 결정의 입력이 아니다(2026-08-12)»로 b2의 빚 선언과 대응한다. worksheet §3은 같은 §3.2를 상대로 더 약한 쌍(s024-4.1/b1·s076-16.2/b2)은 유예했으면서 s015-2.5/b2·b4·b5는 올리지 않았다 — 소급 패스가 이 문서군 최대의 재진술 군집을 놓칠 위험.
- 수정안: worksheet §3에 s015-2.5/b2·b4·b5 ↔ architecture-ddd-final §3.2(및 b2의 빚 선언 ↔ discipline-houserules §4/architecture-ddd §3.2 말미) 행 추가. 정본 방향 판정은 소급 패스 몫이므로 좌표 기록만.

---

## LOW

### F10 [배선 · s079-16.5] #546 검사기 귀속 오류 (위임 사유 내)

- 주장: «outbox 행과 비즈니스 write의 동일 atomic» D2 사유가 "check-transaction-boundary #546·#599"라 했으나 #546은 transaction-boundary docstring 담당 규칙 11종에 없다(진단 메시지에 원리 인용만 존재). #546의 진단 소유는 check-domain-model 응용 축(구현부 «#257 확정 · #542 · #546 …» 레인)이다. 위임 결론은 안 바뀌므로 low.
- 수정안: 사유의 #546 귀속을 정정(#599만 남기거나 domain-model 응용 축으로 표기).

### F11 [배선 · s047-9.2/884] 쌍둥이 규범의 비대칭 배선 — #541 미부착

- 주장: «외부 부수효과의 커밋 전 실행 금지»가 두 Work로 존재하는데(재진술 아님 판정은 메모 4로 수긍), s078/1585 판은 transaction-boundary + usecase-dto-placement(#541 커밋 전 발행 금지)를 받고 s047-9.2 판은 transaction-boundary만 받았다. #541의 커버 여부(.publish 한정이라 email 부수효과 비커버)로 정당화될 수는 있으나 그 논거라면 1585 판의 #541도 같은 한계다 — 어느 쪽이든 비대칭.
- 수정안: 두 판의 배선을 일치시키고(둘 다 #541 병기 또는 둘 다 제외) 사유 한 줄.

### F12 [배선 · s019-3.1] «테스트 파일 평면 나열 금지» E — 평면/표준 갈림 기준과의 긴장

- 주장: 운반체(287행 blockquote)는 TSD 앱별 `apps/<app>/tests/` 배치의 예시 문맥인데, 부착된 check-test-config #383/#384는 표준 트리 BC `test/` 직계 구조만 문다. worksheet 메모 7의 원칙(평면 문맥 규범에 표준 트리 검사기를 부착하지 않는다)대로면 이 행도 D2 후보다. 다만 금지문 자체는 배치 불문 일반형으로 읽을 여지가 있고 basis가 «앱별 tests/ 변종은 reviewer»로 한정을 밝혀 low.
- 수정안: 유지 시 basis에 «표준 트리 한정 커버» 명시 강화, 또는 D2 강등 — 메모 7 기준과의 정합 한 줄.

### F13 [규범식별 · worksheet §1 s078-16.4] «bullet 14» 산술 오기

- 주장: 분해 표기 (1581:1·1582:2·1583:2·1584:6·1585:2·1586:1·1587:1)의 합은 15인데 «bullet 14»로 적혔다. 절 합계 28은 실측과 일치하므로 계수 자체는 무결 — 표기 오기.
- 수정안: «bullet 15»로 정정.

---

## 검증에서 살아남은 것 (반박 실패 기록 — 재론 방지)

- 블록 타일링·경계: 63절 전수 — `line_start+1` 시작·연속·비중첩·절 끝 커버를 migrate 도구 exit 0으로 기계 확인. 헤딩 직후 빈 줄 선두 귀속·후행 빈 줄 선행 귀속·`---` 흡수 전건 §13 합치. 표 머리행+구분행 병합·s067-14.1 표 전체 1블록은 §13 «표 행 묶음» 문면상 적법.
- 규범 수 대사: 60절 일치 + 3절 차이(-3)는 §15 «정본 1곳만 Work 승격» 계약 합치, 사본 6블록의 restates 좌표(s015-2.5/b2·b5, s054-11.1/b1) 전건 원문 대조 확인.
- 배선 표본 정합 확인: s087 #631(문면 정확 일치) · s050-10.2 #593 2건 · s078-16.4 커스텀 백엔드 ⑴ AND 게이트 · s079 디스패처 #58+#172·#174 · at-least-once #532+#181 · s069-14.3 #387·#389 · s046-9.1 #502·#507·#508 · «값 비교는 ==» D2(docstring «보지 않는 것» 실재) · «IntegrityError 명시 제외» D2(transient-overmapping 문면 실재) · #549 D2(domain-model 문면 실재) · §10.4 historical 동결 비배선(choices 3) 면제 조항 — 메모 5 원칙 타당). 미부착 14종 검사기의 담당 규칙에서 이 문서 규범과 겹치는 누락 배선 발견 못 함.

---

## 처분 (수리자 판정 — 2026-08-22)

- 대조 근거: 원문 `dddjango/skills/implementation-django/references/final.md` 실독 + 쟁점 검사기 **docstring·구현부** 실독(`check-choices-literal-consumption` 167~174행 · `check-db-table` 414~420행 · `check-mechanism-ownership` #336/#337/#593 · `check-app-container` G2/G3 · `check-idempotency-scope-creep` G0 · `check-ninja-boundary-middleware` 판정 문단 · `check-transaction-boundary` 담당 11종 · `check-domain-model` #546 · `check-usecase-dto-placement` #541 · `check-test-config` #383/#384/#596) + `architecture-ddd/references/final.md` 635·637행.
- 결과: **13건 전건 fixed · rejected 0**. 기계 검증 `ontology_migrate.py`(--write 없음) **exit 0** 재확인(63절·220 Work 무변 — 수리는 wiring/basis 한정, 블록 분해·Work 계수는 손대지 않았다).

| # | 처분 | 근거 한 줄 |
|---|---|---|
| F1 | **fixed** | 구현부 167~174행이 `default=<문자열 Constant>`만 적출함을 확인 — 위반형 `default=OrderStatus.PENDING`(멤버 직접)은 통과하므로 커버 0. docstring 5)는 면제 조항. `enforcedBy` 제거 → D2(옆 규범·메모 5 원칙과 일관). |
| F2 | **fixed(+확대)** | docstring 19행 실물이 «존재 **+ 값**»이고 구현부 420행이 값 불일치 blocker를 냄을 확인 — ② 인용의 «존재만»은 원문 §10.4(1037~1039행)의 거짓 서술을 옮긴 것. basis를 실문면(존재+값·신규 파일 한정·추적 모델 미검사)으로 정정하고 «부분·충돌» 표기. **확대**: Override «이력 보존 우선»은 지적이 요구한 충돌 주석을 넘어 **D2로 강등**했다 — #630의 «개명 강제 아님»은 부작위(면제) 조항이라 이 Override의 위반형(보존명을 규약으로 개명)을 못 잡아 커버 0이고, 신규 파일 이주에서는 반대로 발화한다(면제 인용 배선 = 오배선, F1과 동일 원칙). §10.4↔#630 표류는 spec·worksheet 양쪽에 소급 패스 상신 문구로 남겼다. |
| F3 | **fixed** | docstring 판정 문단이 «BC driving 자가정의 미들웨어의 전역 MIDDLEWARE 자가등록 적출» 단일 축임을 확인 — 순서·시그널 대체 위반형 커버 0. s072-15.1·s047-9.2/911 둘 다 `enforcedBy` 제거 → D2. 초판 basis 자체가 «순서는 비커버»라 적고 E를 유지한 자기모순이었다. 메모 10도 정정. |
| F4 | **fixed** | #336(자리)·#337(파일명 꼴)은 VCS 포함과 독립 — gitignore된 마이그레이션도 통과하므로 커버 0. gitignore 쌍둥이 규범(D2)과 배선 일치. |
| F5 | **fixed** | docstring이 G0 «미요청 도입 차단»(scope 미요청 단정 ∧ G1 승인 부재)만 판정함을 확인 — 정당 채택된 멱등성의 계약↔storage 불일치는 비커버. 같은 절 «필수 불변식의 DB boundary 동반 설계» 행과 논거 통일. |
| F6 | **fixed** | #593 docstring의 «도구가 만들고 지우는 변경은 손편집이 아니다»를 확인 — `makemigrations` 재생성형 재작성과 삭제는 주어 밖. 지적의 1안대로 **E(부분) 유지 + basis 명시**(허용 목록을 깨는 손 편집만 결정적 · 이력 정합 판정 전체는 reviewer). |
| F7 | **fixed** | G2(옛 루트는 추적된 기존 디렉터리·새 마이그레이션 없음) 불성립, 성립해도 G3(실질 이주 대응 앱 존재)가 면제 — 문면이 명명한 «move를 copy로» 실패 모드에 구조적으로 발화 불가. `enforcedBy` 제거 → D2. |
| F8 | **fixed** | 초판 spec 기계 계수 30/33/3이 지적대로 맞았고 집계 문장 25/30/5가 오기였음을 확인. 다만 F1·F3·F4·F5·F7·F2(Override) 제거와 F11 추가로 배선 자체가 바뀌었으므로 최종 수치는 **23 Work · 27 링크 · 2종 4건 · 검사기 10종**(재계수)으로 적었고, 초판 오기 이력을 각주로 남겼다. |
| F9 | **fixed** | architecture-ddd-final 635행이 s015-2.5/b2·b4·b5의 계층 소유·`.value` 평탄화·소비 규율(==·1차 시정·§2.14 포인터)을 거의 전부 담고 637행 말미가 b2의 «안 갚은 빚» 선언과 대응함을 실독 확인. worksheet §3에 좌표 4행(16~19) 추가 — 정본 방향은 소급 패스 몫이라 판정하지 않았다. |
| F10 | **fixed** | `check-transaction-boundary` 담당 11종에 #546 부재, 진단 소유는 `check-domain-model`(631·735행 응용 축)임을 확인. D2 사유에서 귀속 정정(위임 결론 무변). |
| F11 | **fixed** | 두 판 모두 «외부 부수효과의 커밋 전 실행 금지»로 위반형 집합이 같고 `.publish(`는 그 부분집합이다 — 1585 문면이 «message publish»를 명시 열거한다는 차이는 있으나 배선 차등 근거로는 부족. **둘 다 #541 병기**로 일치시켰다(기본값 도피 방지 방향으로 통일). |
| F12 | **fixed** | #383/#384(+#596)가 표준 트리 `test/` 직계만 판정함을 확인. 금지문 자체는 배치 불문 일반형이라 부착은 유지하되, basis에 «표준 트리 한정 커버·앱별 `tests/` 변종은 reviewer»를 명시 강화하고 메모 7 기준과의 정합(일반형 금지문의 부분집합 커버)을 한 줄로 적었다. |
| F13 | **fixed** | (1:2:2:6:2:1:1) 합 15 · 절 합계 2+1+15+1+6+3=28 확인 — «bullet 15»로 정정하고 검산식을 병기. |

- 반영 파일: `workspace/eval/t3/specs/implementation-django-final.spec.json`(norm 12곳 — `enforcedBy` 제거 7 · 추가 1 · basis 정정 12) · `workspace/eval/t3/worksheets/implementation-django-final.md`(§1 검산 1행 · §2 배선 표 12행 + 집계 문단 · §3 유예 4행 추가 · §4 메모 10 개정).
- 소급 패스 상신 1건: **원문 §10.4(1037~1039행) ↔ `check-db-table` #630 표류** — 원문이 «백스톱은 존재만 보고 값 형태는 보지 않는다»고 서술하나 검사기는 신규 파일 모델의 db_table 값을 규약과 대조해 blocker를 낸다. 이주 경로에서 legacy 보존명(`tbl_product`)은 §10.4의 Override와 정반대로 차단된다. 원문 수정은 이 공정 밖이라 좌표만 남긴다.
