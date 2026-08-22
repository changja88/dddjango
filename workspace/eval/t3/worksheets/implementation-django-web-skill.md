# T3 이관 검수표 — implementation-django-web-skill

- 원문: `dddjango/skills/implementation-django-web/SKILL.md` (50행 · 센서스 일치 · 마커 0 — 미이관 문서)
- spec: `workspace/eval/t3/specs/implementation-django-web-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-django-web-skill.spec.json` → **exit 0** (블록 34 · Work 27 · `--write` 미사용)
- 배선 전 `dddjango/scripts/check-*.py` **27종 docstring 선두 전수 실독** 완료(§16 L-F 의무 — 묶음 «django-skills» 3문서 공통 1회).

## 1. census 대사 (절별 규범 수)

| 절 | 헤딩 | 발주서(센서스) | spec | 차 | 판정·사유 |
|---|---|---|---|---|---|
| s001 | (전문) | 2 | 2 | 0 | 일치 — 발주서의 adv 중재 정정(4→2)을 그대로 확인했다: 주제 설명 1문 비규범 · 병렬 위임 3건은 한 문장·한 축이라 1 Work · 로드 1 |
| s003 | 언제 쓰나 | 7 | 7 | 0 | 일치 — 로드 1 + 경계 불릿 6(13~18행 각 1) |
| s004 | 핵심 운영 원칙 | 9 | 16 | **+7** | **센서스 과소** — 센서스는 «불릿=1문장=1규범» 계수인데 이 절은 정본 §1~§11의 요약 사본(§5·§9 누락)이라 한 불릿이 정본의 2~4 Work를 삼킨다. 특히 30행은 정본 §11의 분류 원칙+세 경로를 한 줄에 접었다(정본 s012-11 b1·b3·b5·b6). 아래 불릿별 대조표 참조 |
| s005 | 상세 레퍼런스 | 2 | 2 | 0 | 일치 — 34행(준거)·50행(한정 로드). 주제↔§N 매핑표 11행은 목차라 비계수(P0 승계) |
| **계** | | **20** | **27** | **+7** | 불일치 1절 = «센서스 과소» 판정 — 과대 산정 판정 0 |

### s004 불릿별 대조 (센서스 문장 ↔ spec Work)

| 행 | 불릿 주제 | 문장 | spec Work | 분리 사유(정본 대조) |
|---|---|---|---|---|
| 22 | 뷰 thinness | 1 | 2 | 유지 의무 + 책임 6종 폐쇄 — 정본 s002-1 b10이 같은 축을 3 Work로, s003-2 b9가 «thin adapter 유지»를 별도로 채번 |
| 23 | CBV/FBV 선택 | 1 | 2 | 선택 기준 / mixin 재검토 — 정본 s003-2 b1·b8 |
| 24 | context | 1 | 2 | 표시 값 한정 / 도메인 동작 분리 — 정본 s004-3 b1 · s003-2 b9 |
| 25 | 템플릿 책임 | 1 | 1 | 일치 |
| 26 | web form 경로 | 1 | 1 | 5경로가 한 행위(폼 흐름 처리)의 열거라 1 Work |
| 27 | HTMX 보호 | 1 | 1 | 4수단이 «동일하게 보호» 한 행위의 열거라 1 Work |
| 28 | CSRF·XSS·헤더 | 1 | 1 | 동상 |
| 29 | render acceptance 보고 | 1 | 2 | 실행분 한정 기재 / 미실행 명시 — 정본 s011-10 b1이 같은 두 축 |
| 30 | 에러 출처 분류 | 1 | 4 | 분류 기준 + 세 경로(view-local 재렌더 / handler500 / 미들웨어 503) — 정본 s012-11 b1·b3·b5·b6 |
| **계** | | **9** | **16** | |

계수 규율(과대 방지): 열거가 **한 행위의 목록**이면 병합했다(26행 5경로·27행 4수단·28행 3대상 — 각 1 Work). 반대로 열거의 각 항이 **서로 다른 처리 경로·소유자**를 지정하면 분리했다(30행 3경로 — view-local / handler500 / 미들웨어, 처리 주체와 응답이 모두 다르다). §N 좌표는 비계수.

> **adv 중재 판형과의 관계**(W3 L2 보강 · 2026-08-22) — 이 발주서를 동결한 adv 중재(2026-08-19)는 s001을 «문장 단위 재계수 · 병렬 위임은 1문»으로 4→2로 줄였다. 30행의 1문→4 Work는 그 판형의 **반례가 아니라 같은 판별자의 반대편 적용**이다: 중재가 병합한 s001 description의 위임 열거는 술어가 «위임한다» 하나이고 목적어만 셋인 반면(→ 1 Work), 30행 열거는 **항마다 술어가 다르다**(도메인 예외→«view-local 재렌더» / 시스템·미식별→«`handler500`» / transient→«미들웨어 503»). 26·27·28행이 같은 이유로 병합된 것이 이 판별자가 양방향으로 쓰였다는 실증이고, 정본 `implementation-django-web-final`도 이 열거를 s012-11 b1·b3·b5·b6 네 Work로 이미 나눠 놓았다(그중 b6만 E=`check-transient-overmapping.py`로 소유가 갈린다 — 병합하면 배선이 손실된다).

## 2. 배선 근거 표 (전 규범 27건)

> 표는 spec JSON에서 기계 생성 — 수리 시 재생성한다. 근거 기호 ①문면 역할명 ②검사기 docstring 인용 ③P0 커버 ④registry #N.
> 기본값: §16 «implementation-* → `agent-discipline-reviewer`». 이탈 병기 — 스킬 로드·부착 축 `command-dddjango`, 계약 축 `agent-design-review-api`, 도메인 정책 축 `agent-design-review-ddd`, DB 축 `agent-design-review-db`.

| # | 절/블록(행) | Work label | class | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s001/b2 (3) | 서버렌더 뷰·템플릿·폼·HTMX 코드 작성·리팩터링 시 이 스킬 선로드 | Obligation | — | `agent-discipline-reviewer`·`command-dddjango` | ①문면 «…먼저 로드한다» — frontmatter description 은 스킬 로드 트리거(행 단위 norm) · ②check-*.py 27종 전수 — 스킬 로드·라우팅 술어 0 · §16 기본값(implementation-* → discipline-reviewer) + 절차 층 Coordinator(스킬 부착 결정 주체) |
| 2 | s001/b2 (3) | Django 코어·JSON API 어댑터·REST 계약의 소유 스킬 위임 | Obligation | — | `agent-discipline-reviewer`·`agent-design-review-api` | ①문면 «…로 위임» 3건 · ②27종 — 위임 경계 술어 0 · §16 문서군 표(implementation-django·-ninja → discipline-reviewer · architecture-api → design-review-api) · web-final s001 b1 «REST API 계약·Ninja 구현의 architecture-api·implementation-django-ninja 기준 준거»(design-review-api+discipline-reviewer) 동일 배선 |
| 3 | s003/b1 (10–12) | 서버렌더 표현계층 설계·작성 작업의 스킬 로드 조건 | Obligation | — | `agent-discipline-reviewer`·`command-dddjango` | ①문면 «…코드를 설계·작성할 때 로드한다» · ②27종 — 로드 판정 술어 0 · §16 기본값 + 절차 층 Coordinator · web-final s002-1 b1 «서버 렌더링 웹 화면 구현의 implementation-django-web 담당» 동일 축 |
| 4 | s003/b2 (13) | REST 리소스·HTTP 상태·Problem Details·OpenAPI 계약의 architecture-api 위임 | Obligation | — | `agent-design-review-api` | ①문면 «→ architecture-api» · ②27종 — 계약 설계 소유 술어 0 · §16 문서군 표 · web-final s002-1 b4 동일 배선 |
| 5 | s003/b3 (14) | Django Ninja Router/Schema/API 어댑터 구현의 implementation-django-ninja 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면 «→ implementation-django-ninja» · ②27종 — 스킬 경계 술어 0 · §16 기본값 · web-final s002-1 b5 동일 배선 |
| 6 | s003/b4 (15) | 모델·QuerySet·Manager·마이그레이션·트랜잭션의 implementation-django 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면 «→ implementation-django» · ②27종 — 동상 · §16 기본값 · web-final s002-1 b6 동일 배선 |
| 7 | s003/b5 (16) | DB locking·isolation·index·rollout/backfill 의 architecture-db 위임 | Obligation | — | `agent-design-review-db` | ①문면 «→ architecture-db» · ②27종 — 격리·인덱스 설계 술어 0 · §16 문서군 표 · web-final s002-1 b7 동일 배선 |
| 8 | s003/b6 (17) | pytest 픽스처·테스트더블·상세 테스트 구현의 implementation-test 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면 «→ implementation-test» · ②27종 — 테스트 mechanics 소유 술어 0 · §16 기본값 · web-final s002-1 b8 동일 배선 |
| 9 | s003/b7 (18–19) | 도메인 상태 전이·정책·불변식의 architecture-ddd 위임 | Obligation | — | `agent-design-review-ddd` | ①문면 «→ architecture-ddd» · ②27종 — 도메인 정책 결정 술어 0 · §16 문서군 표 · web-final s002-1 b9 «도메인 상태 전이·정책·불변식의 architecture-ddd 선결정» 동일 배선 |
| 10 | s004/b1 (21–22) | 뷰의 얇은 어댑터 유지 | Obligation | — | `agent-discipline-reviewer` | ①문면 «뷰는 얇은 어댑터»(§1) · ②27종 전수 — 뷰 두께 «의미» 판정 술어 0(check-ninja-boundary-middleware 는 전역 미들웨어 자가등록만) · §16 기본값 · web-final s003-2 b9 «view 의 thin adapter 유지» 동일 배선 |
| 11 | s004/b1 (21–22) | 뷰 책임의 6종 한정(도메인 동작 비소유) | Prohibition | — | `agent-discipline-reviewer` | ①문면 «요청 처리·auth/permission·form·context 조율·서비스 호출·응답 렌더링만» — 폐쇄 한정 · ②27종 — 술어 0 · web-final s002-1 b10 «웹 view·template 의 domain behavior 비소유»+«view 의 조합 책임 한정» 동일 배선 |
| 12 | s004/b2 (23) | TemplateView/Generic CBV/FBV 선택의 흐름 복잡도 기준 | Obligation | — | `agent-discipline-reviewer` | ①문면 «선택은 흐름 복잡도 기준»(§2) · ②27종 — 뷰 종류 선택 술어 0 · §16 기본값 · web-final s003-2 b1 3규범(선택 기준) 압축 사본 배선 승계 |
| 13 | s004/b2 (23) | mixin 심화 CBV 의 재검토 | Obligation | — | `agent-discipline-reviewer` | ①문면 «mixin이 깊어지면 재검토» · ②27종 — MRO·mixin 깊이 술어 0 · web-final s003-2 b8 «mixin 이 깊어지는 CBV — 재검토…» 동일 배선 |
| 14 | s004/b3 (24) | context 의 표시 값 한정 | Obligation | — | `agent-discipline-reviewer` | ①문면 «context에는 표시 값만»(§3) · ②27종 — context 적재 값 술어 0 · web-final s004-3 b1 «view·context builder … 표시 값 준비» 동일 배선 |
| 15 | s004/b3 (24) | 도메인 동작의 서비스/usecase boundary 분리 | Obligation | — | `agent-discipline-reviewer` | ①문면 «도메인 동작은 서비스/usecase boundary로 분리» — 행위 대상이 다른 별개 규범 · ②27종 — 배치 «의미» 술어 0(check-usecase-dto-placement 는 application_layer 자료 배치만) · web-final s003-2 b9 «쓰기 유스케이스·다중 모델 동작의 service/usecase boundary 이전» 동일 배선 |
| 16 | s004/b4 (25) | 템플릿의 presentation·presentation-related branching 한정 담당 | Obligation | — | `agent-discipline-reviewer` | ①문면 §4 · ②check-naming #589 «[ast+] 템플릿 업무 판정 후보 — {% if %} 조건의 비교 연산·업무 어휘(Q2)»가 이 규범의 위반면을 정확히 겨냥하지만 ast+ «후보» 채널이라 exit 불산입이고 마무리는 discipline-reviewer 몫 — 결정적 집행이 아니므로 enforcedBy 비배선(#588 «사람 문구는 템플릿에 — 유스케이스·도메인의 render_to_string·gettext 호출»은 반대 방향 축이라 이 규범과 무관) · 정본 web-final s005-4 b1·s002-1 b10 도 E=None 동일 배선 |
| 17 | s004/b5 (26) | web form 의 GET·valid POST·invalid POST·redirect·form error 전 경로 처리 | Obligation | — | `agent-discipline-reviewer` | ①문면 §6 · ②27종 — 폼 흐름 경로 커버 술어 0 · §16 기본값 · web-final s007-6 b7·b8·s011-10 b7 압축 사본 배선 승계 |
| 18 | s004/b6 (27) | HTMX fragment 의 method·auth·permission·CSRF 동급 보호 | Obligation | — | `agent-discipline-reviewer` | ①문면 §7 · ②27종 — CSRF·permission 적용 술어 0(check-ninja-boundary-middleware 는 JSON 경계 축) · web-final s008-7 b4 «state-changing HTMX/AJAX 의 non-HTMX POST 동급 auth·permission·CSRF 검증» 동일 배선 |
| 19 | s004/b7 (28) | CSRF·XSS 설정·보안 헤더의 Django 보안 프리미티브 유지 | Obligation | — | `agent-discipline-reviewer` | ①문면 §8 · ②27종 — 보안 설정·미들웨어 순서 술어 0 · §16 기본값 · web-final s009-8 b1·b6 압축 사본 배선 승계 |
| 20 | s004/b8 (29) | render acceptance 보고의 실행 검증 한정 기재 | Obligation | — | `agent-discipline-reviewer` | ①문면 «실제 실행한 검증만 기재»(§10) · ②27종 — 보고 정직성 술어 0 · §16 기본값 + rule-owner-map ⓓ · web-final s011-10 b1 동일 배선 |
| 21 | s004/b8 (29) | 미실행 검증의 미실행 명시 | Obligation | — | `agent-discipline-reviewer` | ①문면 «미실행은 미실행으로 명시» — 별개 행위(누락 고지) · ②27종 — 동상 · web-final s011-10 b1 둘째 규범 동일 배선 |
| 22 | s004/b9 (30–31) | 에러의 출처 기준 분류 | Obligation | — | `agent-discipline-reviewer` | ①문면 «에러는 출처로 분류»(§11) · ②27종 — 분류 기준 술어 0 · web-final s012-11 b1 «service/usecase 예외의 출처 분류» 동일 배선 |
| 23 | s004/b9 (30–31) | 도메인 예외의 view-local 재렌더 | Obligation | — | `agent-discipline-reviewer` | ①문면 «도메인 예외는 view-local 재렌더» · ②27종 — narrow except·재렌더 형태 술어 0 · web-final s012-11 b3 동일 배선 |
| 24 | s004/b9 (30–31) | 시스템·미식별 에러의 handler500 처리 | Obligation | — | `agent-discipline-reviewer` | ①문면 «시스템·미식별은 handler500» · ②27종 — handler500 회부 술어 0 · web-final s012-11 b5 동일 배선 |
| 25 | s004/b9 (30–31) | transient 의 미들웨어 503 매핑 | Obligation | `check-transient-overmapping.py` | `agent-discipline-reviewer` | ②check-transient-overmapping docstring «transient 인프라 예외 핸들러가 영구장애 변종을 구별하는 분기 없이 클래스 통째를 retryable status(503/409)로 무조건 매핑한 정확한 형태만 차단» — 이 규범의 오적용면을 결정적으로 문다 · ①문면 «transient는 미들웨어 503» · web-final s012-11 b6 동일 배선 |
| 26 | s005/b1 (33–35) | 주제별 references/final.md 해당 절 준거 | Obligation | — | `agent-discipline-reviewer` | ①문면 «주제별로 … 해당 절을 따른다» · ②27종 — 참조 문서 준거 술어 0 · §16 기본값 |
| 27 | s005/b14 (50) | 절 단위 필요 항목 한정 로드 | Obligation | — | `agent-discipline-reviewer` | ①문면 «필요한 항목만 읽는다(전체 로드 불필요)» · ②27종 — 로드 범위 술어 0 · §16 기본값. 표 11행은 주제↔§N 매핑 목차라 규범 비계수(P0 승계) |

### 27종 전수 실독의 산물 (배선/비배선 판단)

- **유일한 검사기 배선**: 30행 «transient는 미들웨어 503» → `check-transient-overmapping.py`. docstring이 «`OperationalError`/`DatabaseError`를 영구장애 변종 구별 분기 없이 클래스 통째를 retryable(503/409)로 매핑한 형태만 차단»이라 이 규범의 오적용면을 정확히 문다(정본 s012-11 b6과 동일 배선).
- **의도적 비배선**: 표현계층 규범 대부분은 27종의 사정거리 밖이다 — `check-ninja-boundary-middleware.py`는 *JSON 경계*의 전역 미들웨어 자가등록만(docstring «BC의 driving 층에서 자가 정의한 Django 미들웨어가 전역 `settings.MIDDLEWARE`에 자가등록»), `check-usecase-dto-placement.py`는 application_layer 자료 배치 축이라 24행 context 규범과 대상이 다르다. 정본 `implementation-django-web-final` 128 Work 중 검사기 배선이 2건(§11 두 자리)뿐인 사실이 이 공백을 뒷받침한다 — 기본값 도피가 아니라 실제 커버 부재다.
- **#588/#589 서술 교정**(W3 L9 · 2026-08-22): 초판은 25행 «템플릿은 presentation과 presentation-related branching만» 규범의 비배선 사유로 «#589는 후보 채널이고 대상은 유스케이스·도메인의 문구 호출 축»이라 적었는데, **그 대상 서술은 #588의 것**이다(`check-naming.py` docstring: #588 «[ast] 사람 문구는 템플릿에 — 유스케이스·도메인의 `render_to_string`·`gettext` 호출 위반» / #589 «[ast+] 템플릿 업무 판정 후보 — `{% if %}` 조건의 비교 연산·업무 어휘(Q2)»). #589는 오히려 **이 규범의 위반면을 정확히 겨냥한다** — 따라서 «술어 0»도 부정확했다. 비배선 결론은 유지한다: 근거가 «술어 부재»가 아니라 **«ast+ 후보 채널 — exit 불산입, 마무리는 discipline-reviewer»**이고, 정본 `web-final` s005-4 b1·s002-1 b10도 E=None이다. spec basis를 그 문면으로 교체했다.
- 30행의 «인프라 예외 합성 금지»(정본 s012-11 b7 → `check-synthetic-infra-exc.py`)는 SKILL 문면에 없으므로 붙이지 않았다(문면 없는 배선 금지).

## 3. 재진술 유예 (교차 문서 쌍 — 전 웨이브 후 소급 패스가 연결)

같은 문서 안 쌍 1건은 spec `restates`로 넣었다: `s001/b2`(description, 3행) → `s003/b1`(11행)·`s003/b2`(13행)·`s003/b3`(14행)·`s003/b4`(15행). description의 «먼저 로드한다 + 위임 3건(implementation-django·-ninja·architecture-api)»이 «언제 쓰나»의 로드 조건·경계 불릿 3건의 압축 사본이다(발주서 재진술 열 «Y:implementation-django-web-skill/s003»과 일치).

아래는 타 문서 상대라 유예한다. 좌표는 **마커 제거본=센서스 기준**(상대 문서 `implementation-django-web/references/final.md`는 이미 이관돼 마커 12행이 삽입돼 있어 현재 파일 행번호와 다르다). 상대 블록 서수는 병합된 `implementation-django-web-final.spec.json` 실물에서 확인했다.

| 사본 블록(행) | 상대 절/블록 (implementation-django-web-final) | 상대 행(센서스) | 확인 근거 |
|---|---|---|---|
| s001/b2 (3) | s002-1 b4·b5·b6 · s001 b1 | 28 · 29 · 30 · **2–7** | description 위임 3건 = §1 위임 표 3행 · s001 b1은 web-final 전문 규범 블록(W3 L8 좌표 수리 — 초판 «21–23»은 s002-1 b1의 행이었다) |
| s003/b1 (10–12) | s002-1 b1 | 21–23 | 스킬 담당 범위 선언 |
| s003/b2 (13) | s002-1 b4 | 28 | REST 계약 → architecture-api |
| s003/b3 (14) | s002-1 b5 | 29 | Ninja 어댑터 → implementation-django-ninja |
| s003/b4 (15) | s002-1 b6 | 30 | 모델·ORM → implementation-django |
| s003/b5 (16) | s002-1 b7 | 31 | DB 축 → architecture-db |
| s003/b6 (17) | s002-1 b8 | 32 | 테스트 mechanics → implementation-test |
| s003/b7 (18–19) | s002-1 b9 | 33–34 | 도메인 정책 → architecture-ddd |
| s004/b1 (21–22) | s002-1 b10 · s003-2 b9 | 35–36 · 51–52 | 뷰 책임 한정·thin adapter |
| s004/b2 (23) | s003-2 b1 · b8 | 38–40 · 49–50 | CBV/FBV 선택·mixin 재검토 |
| s004/b3 (24) | s004-3 b1 · s003-2 b9 | 100–102 · 51–52 | context 표시 값·도메인 동작 분리 |
| s004/b4 (25) | s005-4 b1 · s002-1 b10 | 112–114 · 35–36 | 템플릿 책임 한정 |
| s004/b5 (26) | s007-6 b7·b8 · s011-10 b7 | 173 · 174–175 · 273 | 폼 POST/Redirect/GET·invalid 렌더 |
| s004/b6 (27) | s008-7 b4 | 214 | HTMX 동급 auth·CSRF |
| s004/b7 (28) | s009-8 b1 · b6 | 239–241 · 247 | CSRF 프리미티브·미들웨어 순서 |
| s004/b8 (29) | s011-10 b1 | 263–265 | 실행분 한정 보고·미실행 명시 |
| s004/b9 (30–31) | s012-11 b1 · b3 · b5 · b6 | 282–284 · 287 · 289 · 290 | 출처 분류·재렌더·handler500·503 |

## 4. 경계 판단 메모

1. **frontmatter는 code가 아니라 행 단위 prose/norm**(웨이브 2 판례) — 1행 `---`가 절 헤딩(headingSnapshot), 3행 description만 norm, 5행 닫는 `---`+6행 빈 줄이 마지막 prose 블록.
2. **절 선두 빈 줄은 첫 블록 선두 귀속**(§13): s003 `b1=[10,12]`, s004 `b1=[21,22]`, s005 `b1=[33,35]`. 절 끝 빈 줄은 마지막 내용 블록 후행: s003 `b7=[18,19]`, s004 `b9=[30,31]`, s005 데이터 마지막 행 `[48,49]`.
3. **표는 행 단위 `table-row`** — 머리+구분행 `[36,37]`, 데이터 11행 각 1블록, 마지막 행이 빈 줄 흡수(`[48,49]`).
4. **s004 b1의 class 두 축** — «뷰는 얇은 어댑터»는 Obligation, «…만»의 폐쇄는 Prohibition으로 갈랐다. 정본 s002-1 b10이 같은 문장을 Prohibition(«domain behavior 비소유»)+Obligation(«조합 책임 한정»)으로 나눈 판형을 따랐다.
5. **26·27·28행을 1 Work로 병합한 근거** — 열거된 항목들이 «모두 처리»·«동일하게 보호»·«유지»라는 **하나의 술어**에 걸린다. 반면 30행은 술어가 항목마다 다르다(재렌더/handler500/503). 이 술어 단위 판별이 s004 계수의 1차 자다.
6. **kind=code 0** — 이 문서에 펜스가 없다.

## 5. 소급 패스 이월 — 그래프 전역 결정 대기 (W3 적대 리뷰 반영 · 2026-08-22)

묶음 «django-skills» 3문서 공통 이월 2건. 상세 근거는 `implementation-django-ninja-skill.md` §5에 1회 기록하고 여기서는 이 문서의 해당 좌표만 적는다.

1. **§15 «정본 1곳만 Work 승격»의 적용 범위**(W3 L1 · 개별 수리 **기각** · spec 불변) — 이 문서 좌표: `s001/b2`(3행)가 `restates`(→`s003/b1`~`b4`)와 자기 Work 2건을 겸한다. 기각 근거 요지 ⒜ §15 조항의 실물 스코프는 «축자 쌍»(파일럿 예시가 명시)이고 frontmatter description은 축자 사본이 아니다 ⒝ 발주서 센서스(adv 중재가 4→2로 확정)가 s001 규범 수 2를 못 박아 사본 판형(`norms` 0)으로 바꾸면 census 대사가 −2로 어긋난다 ⒞ 전 웨이브 `*-skill` 8종이 동형이라 3문서만 되돌리면 비일관이 커진다. **일괄 확정 대상**.
2. **로드 조건 규범의 위임 판형 불일치**(W3 L11 · 이 묶음 결함 아님 · 소급 정합 대상) — 이 문서 좌표: 배선 표 1행(`s001/b2`)·3행(`s003/b1`)의 `agent-discipline-reviewer`+`command-dddjango`. `architecture-*-skill` 3종은 `command-dddjango`+`design-review-*`, `discipline-tdd`·`implementation-python`·`implementation-test`-skill은 `agent-discipline-reviewer` 단독이다. 배선 불변(§16 기본값 표 2행 병용으로 문면 근거 성립) · 판형 통일은 소급 패스 몫.
