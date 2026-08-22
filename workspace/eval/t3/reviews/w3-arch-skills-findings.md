# W3 적대 리뷰 — «arch-skills» 묶음 (architecture-ddd-skill · architecture-db-skill · architecture-api-skill)

- 리뷰어: Fable 5 적대 리뷰(4렌즈 전수) · 2026-08-22
- 대상: `workspace/eval/t3/specs/architecture-{ddd,db,api}-skill.spec.json` + worksheet 3종
- 검증 실측: ①migrate 검증 전용 3건 모두 **exit 0 재현**(Work 27/23/29 — worksheet 기재와 일치) ②전 절 블록 경계·kind를 원문 행 단위로 전수 대조(경계 위반 0) ③basis 인용 docstring을 검사기 실물에서 직접 대조(check-domain-model·db-table·transaction-boundary·usecase-dto-placement·context-isolation·layer-skeleton·port-adapter-pairing·business-vocabulary·event-publish·idempotency-scope-creep·broker-contract·missable-entrance·mechanism-ownership·error-centralization·api-error-controller-contract·openapi-error-declaration·response-schema-bypass·naming — 인용 #N·문면 전건 실재 확인) ④인용 판례(ddd-final s019·s022-3.5·s023-3.6·s024-3.7·s026·s036-5.1·s051-8·s009-2.3·s010-2.4 / db-final s019-4.2~s054-11.3 / api-final s013-3.1·s021-5.1·s022-5.2·s024-5.4·s042-9.2·s047-10.3·s049-11.1·s060-13.3·s065-14.3 / ninja s022-6.1·s023-6.2 / agent-coder s004 / design-architect s005 / discipline-tdd s012-3.4 / design-review-api s003)를 기이관 spec 실물에서 대조 ⑤census E01/E08 classify 행·api-final §2 NAR(부재) 실물 확인.
- 재진술 유예 대사: ddd 19건 = s004 Work 19 전량 · db 15건 = 15 전량 · api 18건+SKILL 고유 1건 = 19 전량 — **유예 누락 0**. same-doc 쌍(s001→s003)은 3문서 모두 spec `restates` 수록·방향(사본→정본)·제외 블록 사유(db b4·api b6) 정합.

## 발견 (심각도 순)

### F1 · medium · 배선 · architecture-ddd-skill · s004 (20행, b2 «유비쿼터스 언어의 BC 내 한정 유효»)

- **주장**: 기본값 단독 배선(D:design-review-ddd)이 **같은 규범의 정본 배선과 상충**한다. worksheet 자신이 유예표 #2에서 정본으로 지목한 `architecture-ddd-final` s009-2.3/b3 W3 «유비쿼터스 언어의 유효 범위는 BC 경계 안»은 `enforcedBy: check-business-vocabulary.py`(basis: «#47·#52 가 어휘의 BC 국지성을 집행»)로 기이관돼 있다. spec basis는 비커버 논거를 **다른 규범**(s010-2.4/b2 «의미가 갈리면 BC 분리» — E 없음)에서 빌려 왔고, worksheet 머리(«같은 규범에 같은 검사기를 달았다»)와 모순되며, 22행 갈림처럼 «정본과 갈린 자리» 기록도 없다. §16 «역도 성립»(담당 검사기 docstring 근거가 있는데 기본값 도피 = 오배선) 위험.
- **수정안**: 정본 배선을 승계해 `check-business-vocabulary.py`를 enforcedBy에 병기(basis에 #47·#52 «어휘의 BC 국지성» 인용)하거나, 반대로 정본 s009-2.3/b3 배선이 과대라는 판정이면 worksheet §4에 «정본과 갈린 자리»로 명시 기록하고 소급 패스 재료로 남길 것. 현재처럼 무기록 갈림은 불가.

### F2 · medium · 배선 · architecture-api-skill · s004 (24행, b4 W1 «상태 코드별 body·header·schema 명시 기록»)

- **주장**: basis의 «final s021-5.1·**s022-5.2 계열 배선과 동일**» 주장이 **허위**다. worksheet 유예표 #12가 정본으로 지목한 `architecture-api-final` s022-5.2/b1 «상태 코드별 본문 존재 여부·schema 분리 정의»는 `enforcedBy: check-response-schema-bypass.py`(docstring: «Block direct raw 200-203 returns that bypass a declared Ninja schema»)로 배선돼 있고, b5는 check-openapi-error-declaration을 진다. 같은 축 정본에 docstring 근거 있는 담당 검사기가 실재하는데 이 spec은 기본값으로 내려가면서 «배선 동일»이라 적었다 — basis 허위 + §16 역도 성립 위험의 이중 결함.
- **수정안**: `check-response-schema-bypass.py`를 enforcedBy에 병기하고 basis에 부분 커버(성공 2xx schema 우회 축만 — header·오류 표면은 별도/공백) 명기, 또는 기본값 유지 시 basis의 «배선과 동일» 문구를 삭제하고 정본 배선(b1=response-schema-bypass·b5=openapi-error-declaration)과의 의도적 갈림 사유를 worksheet §4에 기록.

### F3 · medium · 배선 · architecture-ddd-skill · s004 (25행, b7 W2 «디스패치 타이밍의 명시 — 커밋 직전 또는 직후»)

- **주장**: enforcedBy [check-usecase-dto-placement, check-transaction-boundary]가 **이 Work의 문면과 상충하는 다른 규범(final Override)의 집행**이다. #541은 «커밋 '전' 발행 금지 — .publish 직접 호출은 uow.after_commit 밖», #200은 after_commit 단일 경로를 집행한다(실물 확인). 즉 기계는 SKILL 문면이 허용하는 두 선택지 중 «커밋 직전» 가지를 위반으로 문다 — 이 Work를 집행하는 게 아니라 절반을 부정한다. 게다가 Work의 자기 축(«명시»)은 basis 스스로 검사 공백이라 인정한다. final s024-3.7/b3 W2(Override — «커밋 직전은 배경 이론»)의 배선을 문면이 다른 Work에 그대로 복사한 형태.
- **수정안**: enforcedBy를 비우고 D:design-review-ddd 단독(«명시»는 설계 판정)으로 내리거나, 유지하려면 basis를 «검사기는 '직후' 가지만 집행하고 '직전' 가지는 기계가 위반으로 무는 상충 — 소급 패스의 부분 재진술/불일치 판정 재료»로 고쳐 상충을 명시할 것(현 basis의 «타이밍 '실현'을 집행»은 절반만 참).

### F4 · low · 배선 · architecture-db-skill · s004 (24행, b6 W1 «외부 부수효과의 트랜잭션 내부 실행 금지»)

- **주장**: basis «final s043-9.6/b14 배선 준거»가 판례를 부정확하게 옮긴다. 정본 b14의 실물 배선은 E:[transaction-boundary, usecase-dto-placement, broker-contract] · D:[**discipline-reviewer**]인데 이 spec은 E 1종·D:design-review-db다. 배선 자체는 §16 기본값으로 옹호 가능하나 «준거» 주장과 실물이 갈리고 worksheet에 갈림 기록이 없다.
- **수정안**: basis를 «b14 배선의 부분 승계(E 1종만·D는 §16 문서군 기본값 유지)»로 정정하거나 정본대로 맞출지 판정해 worksheet §4에 한 줄 기록.

### F5 · low · 배선 · architecture-db-skill · s004 (20행, b2 W1 «인덱스 구성 규율»)

- **주장**: basis의 «final s028-7.1·**s029-7.2·s030-7.3** 계열 배선과 동일» 중 s029-7.2·s030-7.3은 final spec에 **부재**(센서스 NAR — Work 0)라 '동일할 배선'이 없다. worksheet 유예표 #3은 이 NAR 사실을 정확히 기록해 spec basis와 자기모순.
- **수정안**: basis에서 s029-7.2·s030-7.3 인용을 «NAR(대응 Work 부재)»로 정정 — worksheet 기록과 정합화.

### F6 · low · 규범식별 · architecture-api-skill · s004 (22행, b2 «URL 설계 / 동사 금지» 2 Work 분해)

- **주장**: 묶음 공통 «문장 분해 규율»의 상충 트리거를 문서 간 반대로 해소했다. ddd 24행 «…만 담당하고, …두지 않는다»는 «같은 축의 부정면 재진술»로 **병합**(1 Work)했는데, api 22행 «…로 설계하고 동사 행위를 포함하지 않는다»는 같은 구조(동일 주어·긍정+부정면)를 ⑵class 갈림으로 **분리**(2 Work)했다. 인용 판례도 어긋난다 — final s013-3.1/b2는 «명사 사용(**동사 금지**)»을 1 Work로 접었다(실물 확인). 계수 자체는 옹호 가능하나 규율의 우선순위(병합 «부정면 재진술» vs 분리 ⑵)가 미기록.
- **수정안**: worksheet 분해 규율에 두 트리거의 우선순위(예: 부정면이 독자 금지 대상을 가지면 ⑵ 우선)를 명문화하고 ddd 24행과 api 22행이 왜 반대 처분인지 한 줄 근거 추가(또는 한쪽을 재판정).

### F7 · low · 규범식별 · architecture-api-skill · s004 (23행, b3 W7/W8 채번 순서)

- **주장**: «문장 등장 순 = 채번 순» 대비, preserve-established Exception(W7)이 원문에서 자기보다 **앞서** 시작하는 레시피 절(«신규 범위는 … 구현하고» — 괄호는 그 뒤)보다 먼저 채번됐다. worksheet의 «정본 b1→b6 진행과 같은 방향» 주장도 실물과 불일치(정본 b6 순서는 preserve→불인정→레시피→G1→주어한정 — skill 순서와 다름). 하위 문장 단위 순서는 규약이 침묵하는 영역이라 low.
- **수정안**: W7·W8 순서를 원문 절 시작 순(레시피→preserve)으로 교환하거나, worksheet 경계 메모에 «괄호 삽입 조문은 등장 위치가 아니라 한정 대상 직후에 채번» 규칙을 명문화.

### F8 · low · 규범식별 · 묶음 공통 (ddd +9 · db +5 · api +9 — 센서스 대비 Work +23)

- **주장**: 묶음 공통 «단위 = 독립 종결절» 규율은 §13 «문장 해상도 = Work 채번 단위가 **문장**»의 저작자 자체 확장이다(한 문장→복수 Work: Vernon 4·birth-enum 4·에러 프로필 문장 3→6 등). 정본 final 분해와의 1:1 맞물림·worksheet 전건 기록으로 방어되나, 동결 센서스(3,235문장)를 분모로 쓰는 T3 계수 체계에서 파(波) 간 무비준 확산 시 기대표 드리프트가 누적된다. 판정 자체는 «센서스 과소(불릿 단위 계수)»가 대체로 옳다 — 단 25행처럼 규범 문장 1개를 2 Work로 나눈 자리는 «센서스 과소»가 아니라 «하위 문장 분해»로, 대사 표의 사유 문구가 부분 부정확.
- **수정안**: 병합 단계에서 «독립 종결절» 규율을 T3 공통 규약으로 비준(§13 문면 개정 또는 T3-EXECUTION 부기)하고, 기대표 diff 사유에 3문서 +23의 분해 내역을 승계. worksheet 대사 사유는 «불릿 단위 센서스의 과소 + 규약 내 하위 문장 분해»로 분리 서술.

## 지적 없음으로 판정한 검증 항목 (반박 시도 후 기각)

- **경계·kind**: 3문서 전 블록 연속·비중첩·절 전량 커버(도구 단언 + 수동 대조), frontmatter 행 단위 prose/norm 판례 준수, s001 헤딩=1행 `---`, 절 첫 블록의 선두 빈 줄 흡수·후행 빈 줄 선행 귀속(§13), 표 머리·구분행 포함 table-row(ddd 10·db 15·api 16행), code/checklist 0 — 오지정 0.
- **규범 수(계수 일치 절)**: s001 2/2/2 · s003 4/4/6 · s005 2/2/2 전건 일치. 미채번 처분(근거 서술·사실 전제·열거 조각) 전건 문면 확인.
- **배선 — 인용 docstring 실재**: 18개 검사기 인용 #N·문면 전건 실물 일치(#257·#258·#253·#252·#300·#302·#310·#8·#303·#301·#272·#542·#543·#547·#269 / #630·#631 / #195·#197·#200·#4·#599·D50 / #194·#539·#540·#541 / #12·#13·#1·#2·#9·#251·#322 / #486~#490 / #457·#460·#351 / #628·#47·#52 / #564 / §9.6 지목·G0 / #603⑴·#532·#181 위임 / #181 / ⑴AND·⑵#336~#338·#593 / profile-gate 문구 / controller-owned 문구 / openapi_extra 문구 / #28·#30·#33·#41). 오배선 회피 기록 3건×3문서의 비커버 논거도 docstring 실측과 부합.
- **§16 역할명→검사기 매핑 표** 적용 3건(api 23행 W5·W8, 28행) — 표·정본 s024-5.4/b5·b6·s065-14.3/b1 배선과 일치.
- **위임 판례**: coder s004→command-dddjango · architect s005/b25→command-dddjango · ninja s022-6.1/b1→design-review-api · ninja s023-6.2/b1→design-review-api · design-review-api s003/b1 Exception · discipline-tdd s012-3.4/b7 «Work 유지+restates» — 전건 실물 확인.
- **재진술**: same-doc 3건(방향·부분 재진술 Work 유지·제외 블록 사유) 정합, 교차 유예 52건+비재진술 판정 기록 전건 — 누락 0. api s004/b1 «SKILL 고유 정본» 기록은 final §2 NAR 부재를 spec 실물로 재확인(모범 사례).
- **api 23행 9 Work 분해**: 문장·절 대응 전건 재현 — 과대·과소 아님(F7 순서만 지적).

**총평**: high 0 · medium 3 · low 5. spec·worksheet 무수정 — 수리는 저작 에이전트 몫.

## 처분 (수리자 · 2026-08-22 · Opus 5)

각 지적을 원문·기이관 spec·검사기 docstring 실물로 다시 대조해 판정했다. **8건 중 8건 fixed · 0건 rejected**(단 F6·F7·F8 은 지적의 **부분 주장**을 기각하고 근거를 남겼다 — 아래 «부분 기각» 항). 3 spec 모두 `ontology_migrate.py` 검증 전용 **exit 0** 재확인(`--write` 미사용 · Work 27/23/29 불변).

| # | 처분 | 조치 | 근거 한 줄 |
|---|---|---|---|
| F1 | **fixed** | ddd spec `s004/b2` 에 `check-business-vocabulary.py` 병기 + basis 재작성 · 검수표 배선표 #8·§4 «정본과 갈린 자리»/«오배선 회피» 목록 재편 | 정본 `architecture-ddd-final` s009-2.3/b3 W3 이 같은 규범에 같은 검사기를 달고 있고, docstring 격리 절 #47(«capability 계약의 업무 어휘 0»)·#52(«BC 이름 0»)+#616/#617·#587·#426·#562 가 «업무 어휘는 BC 밖 공용 자리로 나가지 않는다»는 BC 국지성의 한 면을 실제로 집행한다 — §16 «역도 성립»상 기본값 도피가 오배선이 맞다. 커버 범위(공용 자리 유출 1축 한정)와 검사 공백(컨텍스트 간 의미 분기)을 basis 에 명기하고 기본값을 병기했다. |
| F2 | **fixed** | api spec `s004/b4` W1 에 `check-response-schema-bypass.py` 병기 + basis 준거 정정 · 검수표 #21·§4·유예 #12 갱신 | basis 의 «final s021-5.1·s022-5.2 계열 배선과 동일»은 실물 대조상 **s021-5.1 에만 참**이다(b1~b8 전건 기본값). s022-5.2 는 b1=`check-response-schema-bypass`·b5=`check-openapi-error-declaration` 이고, 유예표 #12 가 정본으로 지목한 b1 의 basis 논거(«선언 schema 우회만 차단하는 부분 백스톱»)가 이 Work 에도 그대로 성립한다 — 병기 + 커버 범위(성공 2xx 우회 1축) 명기로 정정. |
| F3 | **fixed** | ddd spec `s004/b7` W2 의 `enforcedBy` **제거**(D:`agent-design-review-ddd` 단독) + basis 재작성 · 검수표 #18·§3 유예 #12·§4 갱신 | docstring 실물 확인 — `check-usecase-dto-placement` #541 «커밋 «전» 발행 금지 — `.publish(` 직접 호출은 `uow.after_commit` 밖», `check-transaction-boundary` #200 «커밋 뒤 부작용은 `unit_of_work.after_commit`». 이 둘은 정본 s024-3.7/b3 W2(**Override** — «after_commit 한 경로 · 커밋 직전은 배경 이론»)를 집행하는 술어이고, SKILL 문면이 허용하는 «커밋 직전» 가지를 위반으로 문다. 이 Work 에 달면 «집행»이 아니라 «절반 부정»이므로 지적이 옳다. Work 자기 축(«타이밍을 명시한다» = 설계 기록)은 27종 전수에 술어 0이라 기본값 단독이 정합. 상충 사실은 유예 #12 에 소급 패스 재료로 명시. |
| F4 | **fixed** | db spec `s004/b6` W1 basis 를 «b14 배선의 **부분 승계** + 갈린 사유»로 정정 · 검수표 #17·§4 «정본과 갈린 자리» 신설 | 실물 대조 확인 — 정본 s043-9.6/b14 = E:[transaction-boundary, usecase-dto-placement, broker-contract]·D:[discipline-reviewer]. 배선 자체는 유지가 옳다고 판정했다(ⓐ b14 가 한 Work 에 접은 Outbox 축은 SKILL 24행에서 별도 Work 가 `check-broker-contract` 로 이미 짐 — 중복 배선 회피 ⓑ #541 은 «발행 자리» 규율이라 이 Work 축 밖 ⓒ D 를 discipline-reviewer 로 바꿀 문면 근거 없음). 감춰졌던 갈림만 명시 기록으로 노출. |
| F5 | **fixed** | db spec `s004/b2` W1 basis 의 §7.2·§7.3 인용을 **NAR(대응 Work 부재)**로 정정 · 검수표 #9·유예 #3 갱신 | `architecture-db-final` spec 실물에 `-7` 계열 절은 s028-7.1·s031-7.4 둘뿐 — s029-7.2·s030-7.3 은 부재. «동일할 배선»이 없다는 지적이 맞고 검수표 유예 #3 의 NAR 기록과 자기모순이었다. |
| F6 | **fixed**(주장 일부 기각) | 3 검수표의 «문장 분해 규율»에 **트리거 충돌 우선순위** 명문화(배타 표지 기준) + 두 실물 예시 · 판례 관계 정정. spec 무변(계수 유지) | 두 문서가 같은 트리거 충돌을 반대로 해소했는데 우선순위가 미기록이라는 **주장 본체는 옳다**. 가르는 자는 «긍정절의 배타 표지(«만»)»다 — ddd 24행은 «흐름 제어와 트랜잭션 관리**만** 담당»이라 부정절이 독자 위반 표면을 못 만들어 병합, api 22행은 배타 표지가 없고 `/orders/{id}/cancel` 처럼 세 형식 속성을 모두 지키면서 동사를 포함하는 URL 이 성립해 독자 위반 표면이 생기므로 분리. **부분 기각** → 아래 «부분 기각» ①. |
| F7 | **fixed**(주장 일부 기각) | api spec `s004/b3` 의 W7·W8 **순서 교환**(레시피 → preserve 배제) + 블록 note·검수표 #18/#19·§4 채번 규칙 명문화 | 원문 실물 대조 — «신규 범위는 … 구현하고»가 괄호 «(preserve-established …)»보다 먼저 시작한다. §13 «문장 등장 순 = 채번 순»의 단위를 «절의 시작 위치»로 못박고 순서를 교환했다(괄호 삽입 조문은 감싼 절 뒤). **부분 기각** → 아래 «부분 기각» ②. |
| F8 | **fixed**(쓰기 범위 밖 항목은 승계 요청으로 이관) | 3 검수표 대사 사유를 «⑴ 불릿 해상도 과소 + ⑵ 규약 내 하위 문장 분해»로 **분리 서술** · «병합 단계 승계 요청» 절 신설(규율 비준 + 기대표 diff 사유 3문서 +23 내역) | 대사 사유가 부분 부정확하다는 지적이 옳다 — ddd 25행처럼 규범 문장 1 → Work 2 인 자리는 «센서스 과소»가 아니라 «하위 문장 분해»가 사유다. 다만 **§13 부기·`T3-EXECUTION.md` 기록은 저작 계약 «금지» 조항(쓰는 파일 = 자기 spec + worksheet)상 이 에이전트의 쓰기 범위 밖**이라, 비준 요청과 승계할 내역(+23 = ddd +9·db +5·api +9)을 3 검수표에 명시해 병합 단계로 넘겼다. |

### 부분 기각 (지적 안의 틀린 부분 — 반영하지 않은 근거)

1. **F6 «인용 판례 final s013-3.1/b2 도 갈린다»** — 기각. 실물은 `dddjango/skills/architecture-api/references/final.md` 의 **좋은 예/나쁜 예 대조 표 한 행** «\| 명사 사용 (동사 아님) \| `/orders` \| `/create-order` \|» 이고, 괄호는 그 대조의 주석이지 독립 종결절이 아니다(표 행에 종결절 0). SKILL 22행은 «…포함하지 않는다»라는 독립 종결절이므로 **판형이 다르다** — 판례 이탈이 아니라 문면 형태 차이다. 따라서 «한쪽 재판정»은 불필요하고 우선순위 명문화만으로 충분하다(이 정정도 3 검수표에 기록).
2. **F7 «worksheet 의 «정본 b6 진행과 같은 방향» 주장이 실물 순서와 불일치»** — 기각. 검수표 원문은 «정본 `s024-5.4` 의 **b1→b6 진행**과 같은 방향»으로, **블록 간 진행**(b1 우선순위 선택 → b2 보존 → b3 code-json → b4 RFC → b5 wire 혼합 → b6 묶음)을 가리킨다. 리뷰가 대조한 «preserve→불인정→레시피→G1→주어한정»은 **b6 내부** Work 순서이고 검수표가 주장한 대상이 아니다. 다만 오독 가능한 표기였으므로 «블록 간 진행»임을 명기하고 b6 내부 순서와 대응하지 않는 이유(여러 조문을 한 블록에 접은 자리)를 §4 에 덧붙였다.
3. **F8 «판정 자체는 «센서스 과소»가 대체로 옳다»** — 이 부분은 수용하되 표현을 바꿨다. «과소»는 결과(계수 차)이지 사유가 아니므로 3 검수표 모두 사유를 ⑴ 불릿 해상도 미해상 / ⑵ 독립 종결절 분해 두 갈래로 갈라 적었다. ddd 25행·api 23행처럼 **한 문장 → 복수 Work** 인 자리는 ⑵ 단독 사유로 따로 표기했다.

### 수리 후 재검증

```
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/architecture-{ddd,db,api}-skill.spec.json
→ exit 0 · exit 0 · exit 0 (Work 27 / 23 / 29 · 블록 30 / 32 / 36 — 리뷰 실측치와 동일 · --write 미사용)
```

배선 변화 요약: **+2 병기**(ddd 20행 `check-business-vocabulary.py` · api 24행 `check-response-schema-bypass.py`) · **−2 제거**(ddd 25행 W2 의 `check-usecase-dto-placement.py`·`check-transaction-boundary.py`) · **채번 순서 1건 교환**(api 23행 W7↔W8) · **basis 정정 4건**(ddd 20·25행 · db 20·24행) · Work 계수·블록 경계·kind·`restates` **전건 불변**.
