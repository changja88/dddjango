# BC 클린룸 리빌드 라운드 프로토콜 (계획 4번의 방법 · 정본)

2026-08-12 확정. 계획 정본(`docs/work_flow.html` 3장) 4번이 이 문서를 가리킨다.
라운드는 몇 번을 돌려도 **이 문서 하나로 동일하게** 진행한다. 실측이 명령과 어긋나면
고치는 곳은 이 문서다(문서가 정본 — 도구 수정과 함께 갱신).

## 0. 전제

- **broccoli-server 는 운영 중이 아니다** — DB·migrations 보존 의무 없음. BC 삭제는
  migrations 포함 전부이고, 재구현이 새 0001 을 만들면 된다. (플러그인의 migration 안전
  규칙 자체는 불변 — 이 하네스가 그 자를 쓰지 않을 뿐이다.)
- 계획 3번(선행 이관)이 끝나 있어야 한다: 리빌드 브랜치+워크트리, 루트 `framework/`,
  `make test` 전체 green baseline. 워크트리 경로는 3번에서 정해 아래 `<워크트리>` 에 대입한다.
- 재구현 파이프라인은 **워크트리 cwd 의 새 세션**에서 돌린다(플러그인 v2.0.0 은 세션
  시작에 로드). 워크트리 둘의 테스트 동시 실행은 **테스트 DB 분리 시 허용** — 2026-08-14
  L5 실증: 레인 B `.env.local` 에 `POSTGRES_TEST_DB=test_broccoli_codex` 한 줄(트리 무변경)·
  같은 localhost postgres 에서 동시 pytest 양쪽 green. 분리 미실측 레인끼리는 종전대로 금지.

## 1. 원칙 둘

1. **클린룸** — 재구현 파이프라인은 옛 구현·옛 테스트·git 이력(`git show`/`log` 포함)을
   열람하지 않는다. 입력은 `spec.md` 와 이름을 지운 `api_shape_pre.json` 뿐. 세션
   요청문에 이 금지를 명시한다. (옛 것 열람은 ⑥ 판정 단계의 **평가자** — AI 평가
   에이전트와 사람 — 에게만 허용.)
2. **옛 테스트는 오라클이 아니다** — 옛 테스트를 남겨 신규 구현 위에서 돌리지 않는다.
   그러면 파이프라인의 **테스트 작성 능력을 평가할 수 없다**. 옛 테스트는 ⑥에서
   평가자가 읽는 **채점 재료**(시나리오 대조표의 기준)로만 쓴다. 같은 이유로 `spec.md`
   에 테스트 케이스 목록을 옮겨 적지 않는다 — 시나리오 도출은 파이프라인의 일이다.

## 2. 라운드 절차 — 일곱 걸음 (매 라운드 동일)

### ① BC 선택
- **라운드 1 은 `child_settings` 고정** — 최소 크기(1,364 LOC)·인바운드 0 이라 하네스
  자체의 첫 검증을 겸한다(실패해도 원인이 하네스인지 플러그인인지 가장 싸게 갈라진다).
- 라운드 2부터 시드 무작위 — `N`=라운드 번호, `done`=대장의 완료 BC 집합. 같은 입력이면
  언제 다시 돌려도 같은 BC(재현 가능):

```bash
python3 -c "import random; done={'child_settings'}; bcs=['accounts','ai_chat','billing','child_settings','delivery','entitlements','lessons','llm_meta','managed_copy','notifications','pairing','parent_settings','parental_controls','products','report','usage_quota']; print(random.Random('rebuild-round-N').choice(sorted(set(bcs)-done)))"
```

- **실측 게이트 3(라운드 2 신설 · 2026-08-12)** — 뽑힌 BC 가 하나라도 어긋나면 후보에서
  제거하고 **같은 Random 인스턴스로 재추첨**한다(결정적 — 같은 입력이면 같은 궤적):
  1. **인바운드 0** — ②의 grep 실측 파일 0건. 삭제가 이웃 코드를 깨면 앵커 상태의
     전역 baseline 이 죽는다(③ 삭제·⑤B 판정 불성립).
  2. **비-test LOC ≤ 5,000** — 한 라운드에서 스팩 추출·재구현·평가가 실제로 닫히는 규모.
  3. **HTTP 표면 ≥ 1 경로** — A축·오류 축 판정이 성립해야 라운드 목적이 선다.
- 라운드 2 실측(2026-08-12): report 13,136(②)→llm_meta 5,082(②)→accounts(① 88)→
  usage_quota(①2·②5,344)→parental_controls(①2·②5,296)→pairing(① 23)→**billing PASS**
  (비-test 2,217 · 인바운드 0 · 컨트롤러 있음).

### ② 스팩 추출 (삭제 전 · 평가자가 작성 — 옛 코드 열람 허용)
산출물 둘을 `<워크트리>/docs/rebuild/<bc>/` 에 둔다(③의 삭제 커밋에 함께 들어간다):

- **`spec.md`** — 요구 수준 명세. 담는 것: 유스케이스(무엇을 하나)·업무 규칙·불변식·
  API 계약 서술(마운트 prefix·인증·멱등성 등 모양 밖 요구)·**인바운드 표면**(다른 BC 가
  이 BC 에서 import 하는 심볼 — 아래 grep 실측 결과)·바깥 의존(외부 시스템·다른 BC OHS).
  **금지 둘**: 옛 코드 구조 서술(파일·클래스 이름) · 테스트 케이스 목록(원칙 2).
- **`api_shape_pre.json`** — 이름을 지운 API 계약 모양(§3 A축의 기준이자 파이프라인
  열람 허용 입력 — 이름 유래 키가 지워져 클린룸을 깨지 않는다):

```bash
cd <워크트리> && .venv/bin/python -c "import os,django,json; os.environ.setdefault('DJANGO_SETTINGS_MODULE','broccoli_server.settings.test'); django.setup(); from broccoli_server.api import api; print(json.dumps(api.get_openapi_schema(), default=str))" > /tmp/openapi_raw.json
python3 /Users/hyun/Desktop/dddjango/workspace/tools/openapi_shape.py /tmp/openapi_raw.json > docs/rebuild/<bc>/api_shape_pre.json
```

  원본 `openapi_raw.json` 은 옛 이름이 있으므로 **커밋·파이프라인 노출 금지**(임시 파일).
  shape 는 문서 표면(description·examples·tags)을 지운 것 — 그 등가는 A축 밖이고,
  중요한 값(예: problem `type` URI)은 `spec.md` 가 요구로 적는다. 같은 원본에서
  `--success-only` 판 **`api_shape_pre_success.json`** 도 함께 생성한다(⑤A 기준 — D3 개정).
- 인바운드 표면 grep(결과를 `spec.md` 에 붙인다):

```bash
cd <워크트리> && grep -rlE "(from|import) application\.<bc>([. ]|$)" application --include='*.py' | grep -v "^application/<bc>/"
```

### ③ 삭제 (라운드 앵커)
```bash
cd <워크트리> && git rm -r application/<bc>
# INSTALLED_APPS·api.py 라우터 등록 등 배선도 함께 걷는다(남기면 import 에러로 전역이 죽는다).
# 걷은 배선 지점은 spec.md 에 «복원 지점»으로 적는다(마운트 prefix 포함).
git add -A && git commit -m "rebuild(<bc>): round N — spec 추출 + BC 삭제"
```
이 커밋 해시가 **라운드 앵커**다(대장에 기록). 옛 구현·옛 테스트는 앵커의 부모
(`<앵커>^`)에서 언제든 재생 가능하므로 따로 사본을 두지 않는다.

### ④ 클린룸 재구현
워크트리 cwd 새 세션에서 `/dddjango` 파이프라인. 요청문 골자 고정:

> `docs/rebuild/<bc>/spec.md` 를 요구사항으로 `application/<bc>` 를 새로 구현하라.
> `api_shape_pre.json` 이 API 계약의 모양이다. **git 이력의 옛 구현·옛 테스트 열람 금지**
> — 테스트는 명세에서 직접 도출해 작성하라.

파이프라인이 스스로 쓴 테스트가 파이프라인의 green 게이트다(옛 테스트를 대주지 않는다).

**요청문 필수 절(2026-08-13 신설 · 같은 날 여섯째 절 추가 — 정본 `2026-08-13-codex-rabbit-hole-fixes.md`·`2026-08-13-ab-harvest-fixes.md`)**: 이후 라운드의 `request.md` 는 아래 여섯 절을 반드시 포함한다 — **복사 원본은 `templates/request-template.md`**(빈칸 채움 방식·재작성 금지).

> **Placement(변경 허용 — 닫힌 목록)**: ⑴ `application/<bc>/**` — 이 발주의 대상 BC **하나**를 축자로 적는다(자리표시자 금지·다른 BC 폴더 불포함 명시) ⑵ 배선 파일 **축자 나열**(발주 시 실제 경로로 확정 — 명세·산출물이 배선 파일을 추가 지정할 수 없다) ⑶ `.dddjango/**`(산출물 전용). **«변경» = 생성·수정·이동·삭제·개명 전부**(`git mv` 는 두 경로 모두의 변경). 배선 파일 안 허용 변경은 **이 BC 등록에 필요한 행의 추가뿐**(기존 행 삭제·이동·재정렬·경로 변경 금지). `docs/**` 는 읽기 전용 — `legacy_debt.txt` 가필·사본·자작 빚 파일을 `--legacy-debt-file` 로 쓰는 것은 승인 위조다(빚 목록은 발주가 준 그 경로·그 내용뿐).
> **앵커 동결**: registry_gate 앵커는 발주가 지정한 `<앵커 해시>` 다 — HEAD 를 재산출하지 말고 이 값을 쓰라. **이 발주 중에 만든 어떤 커밋도 앵커가 될 수 없다.**
> **완료 기준**: `make test` 판정은 **앵커 기준 신규 red 0** 이다 — 앵커 시점에 이미 red 였던 테스트는 보고 대상이지 수리 대상이 아니고, 타 BC 테스트를 green 으로 만들기 위한 허용 경로 밖 수정은 그 자체가 blocker 다.
> **자율 위임의 한계**: 자율 조항이 대체하는 것은 게이트의 **승인 입력**뿐이다. 비위임: `STOP_FOR_USER_APPROVAL`·G0/G2 blocker·shape approved-change·빚 목록 밖 신규 debt 수용·허용 경로 밖 변경·`scope.md`/`refactor-scope.md` 사후 개정·G0 빚 ⓐ 자기선택(자율 모드의 G0 빚 답은 **ⓑ(미룬다 — 사유: 클린룸 자율 라운드) 고정**·«미룰 수 없음» 항목=blocker). blocker 를 만나면 그 지점까지 커밋(제목 `rebuild(<bc>): stopped — <사유 한 줄>`)하고 산출물에 기록 후 **종료하라 — 이 정지는 실패가 아니라 이 발주의 유효한 종료 상태다**(「끝까지 진행」은 blocker 를 넘으라는 뜻이 아니다).
> **수렴 회로**: 같은 게이트의 반송이 2회를 넘거나, 재설계 후 변경 파일 수·신규 귀속 수가 직전보다 늘면(스코프 증가 신호) 반복하지 말고 blocker 로 기록 후 정지하라.
> **STOP 기록 형식**: `STOP_FOR_USER_APPROVAL` 기록은 닫힌 선택지마다 **대가 한 줄**을 병기하라(대가 없는 STOP 은 형식 불비 — ⑤ 가 유효 종료로 인정하지 않는다). 권고는 선택이다 — 산출물·리뷰 노트 인용으로 저자를 명시할 때만 적고, **권고는 결정이 아니며 자기 승인 근거가 아니다**(산출물·기본값을 권고 방향으로 선반영 금지). 밖에서 보이는 결과가 갈리는 물음은 논증 완성도와 무관하게 STOP 필수다.

**자율 문구 3층 방어(2026-08-13 — 우회 변종 4종 실증 후 신설)**: ⓐ **판정 물음** — 요청문의 어떤 문구든 비위임 목록의 결정 권한·STOP 발화 조건·종단 상태 중 하나를 세션 재량으로 옮기면 금지다. 금지 예시(예시일 뿐 — 판정은 물음이 한다): 「스스로 결정하고 끝까지 진행」·「합리적으로 판단해 계속」·「질문 최소화/STOP 최후 수단」·「보수적으로 메우고 기록만 남겨라」·「종료는 완료 커밋이어야 한다」. ⓑ **충돌 우선** — 요청문의 다른 어떤 문구도 필수 절과 충돌하면 무효다(필수 절이 이긴다 — 이 조항 자체를 요청문에 포함한다). ⓒ **리터럴 게이트** — ④ 기동 전 preflight 에서 request.md 에 「비위임」·「유효한 종료 상태」 존재 + blanket 예시 역-grep 0건을 기계 확인한다. **적용 시점**: 발주 시점 기준 — 기발주 레인은 대장에 구판 명기로 유효(라운드 1→1′·2·codex→codex′ 선례)하고, 기존 재해석 조항(「끝까지 진행」≠blocker 돌파)은 유입된 구판 문구의 방어층으로 존치한다.

**앵커 preflight(2026-08-13 신설)**: 라운드 앵커 커밋에는 `docs/rebuild/<bc>/anchor-preflight.md` 를 포함한다 — 항목별 «실행 명령+결과» 기록(산문 선언 금지 — F2 exact-command 양식). 항목: ⑴ **spec 이 경로를 명기한 외부 의존 전수 ↔ `legacy_debt.txt` 대조표**(라운드 2 실증: 귀속 15건의 근원=빚 파일 과소 수록 — 한정어: spec 이 경로를 명기한 의존에 한한다) ⑵ 요청문 리터럴 게이트(위 ⓒ) ⑶ pycache 정화 ⑷ graphify 클린 재빌드 ⑸ 클린룸 오염원 스캔 ⑹ baseline 실측(`make test` 수·gate 잔존) ⑺ **배선 스모크(2026-08-14 신설 — 라운드 3 실증: usage_quota 의 import-time `api.urls` 접근이 Ninja route cache 를 동결해 늦게 등록되는 registrar 행이 런타임 404 — 양 레인 합 ~2h 손실)**: 앵커 트리에서 대상 BC 의 registrar 등록 행을 «임시로» 추가하고 더미 라우트 하나가 실제 URL 목록에 mount 되는지 실측(`uv run python -c "...api.urls..."` — 등장 확인)한 뒤 원복한다. 실패하면 배선 지뢰(선행 lazy화 필요)가 라운드 «재료» 결함이므로 앵커에서 해소하고 기동한다 — 레인에게 넘기지 않는다. ⑻ **오류-계약·DB 절 정본-정합(2026-08-14 신설 — S3-r1 실증: child spec :73-74 «9457 wire + code-json 프로필» 이중 문면이 레인 갈림 3회째를 냄·⑥a grader 실증=이 검수 항목 자체가 부재였음)**: spec 오류 계약 절을 표준 §5.4 와 대조해 ⓐ wire «모양»과 소유 «프로필·레시피»가 **분리 선언문 한 문장**(«problem+json 은 wire 모양이고 소유·구현 레시피는 dddjango-code-json» 류)으로 앞세워져 있는지 ⓑ **DB 상수 절**(«비운영·migrations 보존 의무 없음·재구현이 새 0001 생성» — §0 이식)이 있는지 확인한다. 어느 쪽이든 없으면 재료 불비 — 앵커 전에 보강한다. ⑼ **spec 요구 ↔ 표준 트리 금지 대조(메커니즘 중립성 · 2026-08-14 신설 — S3-r2 실증: spec §5 가 V1 «management command» 실현 메커니즘을 계약으로 축자 → #58 명시 금지와 충돌·G1 STOP)**: spec 이 요구하는 실현 표면(HTTP·admin·스크립트·cron 등)마다 표준 트리 칸 실재를 표로 대조한다. V1 의 실현 메커니즘은 계약이 아니다 — 표준이 금지하는 메커니즘은 정본이 지정한 대체 자리(예: seed 류=#593 «트리 밖 scripts/»)로 spec 을 중립화하고, 트리 밖 실현은 request Placement 닫힌 목록에 축자 추가한다. preflight 파일이 앵커 커밋 diff 에 없으면 라운드 재료 불비 — 대장 앵커 칸에 «preflight ✅» 를 함께 적는다.

**기동 방법(08-12 실측)**: 하네스 운영 세션은 `claude -p` 서브프로세스 기동이 권한
분류기에 차단된다(스코프 좁힌 allowlist 로도 차단 — 재귀 claude 기동 자체가 대상).
④ 세션은 **사용자가 직접 기동**한다 — 요청문은 `<워크트리>/docs/rebuild/<bc>/request.md`
에 두고:

```bash
cd <워크트리> && claude "$(cat docs/rebuild/<bc>/request.md)"   # 지켜보려면(권장)
cd <워크트리> && claude -p "$(cat docs/rebuild/<bc>/request.md)" --permission-mode acceptEdits   # 헤드리스
```

**레인 복수(2026-08-12 사용자 결정 — 라운드 2부터)**: 한 라운드를 파이프라인 구현체별
**레인**으로 병렬 평가할 수 있다(라운드 2 = claude·codex 두 레인). 레인마다 **독립 클린룸
워크트리**(같은 앵커 커밋에서 가지 친 독립 브랜치)를 쓴다 — 앵커 커밋 하나를 공유하므로
`spec.md`·shape·`request.md` 는 자동으로 동일(공정성 — 요청문 개정으로 레인을 재기동하면 새 앵커·대장 별행이다 · 2·codex′ 선례). ⑤·⑥ 판정과 대장 기록은 레인별로
따로 한다. codex 레인은 codex 마켓 플러그인(`dddjango@changja88-dddjango`)이 같은 버전인지
확인 후 기동(사용자):

```bash
cd <워크트리-codex> && codex "$(cat docs/rebuild/<bc>/request.md)"
```

제약: 레인 워크트리들끼리의 테스트 동시 실행은 §0 단서를 따른다 — 테스트 DB 분리
실측(L5) 레인끼리는 병렬 허용(S3-r1 부터), 미실측이면 순차.

완료 후 하네스 세션에 알리면 ⑤·⑥a 를 하네스가 잇는다.

### ⑤ 기계 판정 — 3축 (전부 명령 고정)
| 축 | 명령 | 자 |
|---|---|---|
| **A. API shape** | ②와 같은 덤프→`openapi_shape.py --success-only`→`diff api_shape_pre_success.json <post>` | **성공(2xx) 경로 diff 0** — 오류 경로의 선언·본문은 spec §오류 계약이 정본(⑤C·⑥ 검증 몫). **2026-08-12 D3 개정**: 오류 축을 code-json 표준으로 이주하는 라운드에선 오류 선언이 의도적으로 바뀌므로(FrameworkErrorSchema→BC ErrorSchema) 전체-모양 diff 는 A축 판정이 아니다(라운드 1·1′ 의 전-모양 판은 `api_shape_pre.json` 대비 기록으로 보존) |
| **B. 전역 테스트** | `cd <워크트리> && make test` | 전체 green(신규 테스트 + 이웃 BC 테스트 — 인바운드 표면 검증) |
| **C. 플러그인** | `python3 …/workspace/tools/bc_registry_run.py <워크트리> <bc>` + `python3 …/workspace/tools/migration_gate.py <워크트리>` + `python3 …/dddjango/scripts/registry_gate.py <워크트리> --anchor <레인 앵커> --legacy-debt-file docs/rebuild/<bc>/legacy_debt.txt` | registry 27종 전부 exit 0 + gate 에서 해당 BC 잔존 0 + **registry_gate 귀속 0** — 빚 파일은 **앵커에 담긴 사용자 승인판**으로 판정한다(세션 가필본 불인정 · 2026-08-13 명문 — 라운드 2 레인 A 실증) |

(`bc_registry_run.py` 는 BC 하나만 담은 비-git 그림자 사본에 27종을 돌린다 — 이웃 위반
섞임·git 상태 의존이 없다. 로스터 소비 검사기 2종(context-isolation·port-adapter-pairing)은
이웃 빈 스텁을 얹은 둘째 판에서 돈다 — 2026-08-13 H4′: 단일-BC 그림자의 #365 과탐을
하네스에서 수정·`bc_registry_smoke.py` 가 과탐 소멸과 진양성 보존 양면을 고정.)

### ⑥ 정성 평가 둘 — AI 와 사람 (여기서만 옛 것을 연다)
기계 3축(⑤)이 못 보는 질을 정성으로 평가한다. **둘 다 받아야 라운드가 닫힌다.**

**⑥-a AI 정성 평가** — `spec.md` 추출·재구현에 참여하지 않은 **새 에이전트**에 위임한다
(자기 채점 방지. 파이프라인 안의 discipline-reviewer 감사와 별개 — 그건 구현 게이트,
이건 라운드 판정이다). 입력과 틀을 고정한다:
- 입력: `spec.md` · A축 diff 결과 · 신규 구현·신규 테스트 전체 · `<앵커>^` 의 옛 구현·
  옛 테스트(`git show <앵커>^:application/<bc>/…` — 열람 허용).
- 틀 넷 — 항목별 소견 + 총평 + 처분 제안(통과/문서 보강/플러그인 수정 후보):
  1. **테스트 작성 능력**: 옛 테스트의 시나리오 목록 ↔ 신규 테스트 대조표 —
     누락(옛 시나리오를 안 덮음) / 신규(새 테스트에만 있음) / 질(단언 강도·경계값).
     누락 갈래: `spec.md` 에도 없던 것 → **문서 추출 결함**(하네스 — 파이프라인 탓 아님) ·
     있는데 안 덮음 → **파이프라인 테스트 작성 결함**(수정 대상).
  2. **설계 질**: ddd·clean·헥사고날 세 관점 — 검사기가 못 보는 의미 배치
     (판정 소유·경계 어휘·의존 방향의 «뜻»이 맞는가).
  3. **spec 충실**: 요구 누락 · 과잉 구현(스팩에 없는 기능).
  4. **옛 구현 대비**: 개선/후퇴/동작 갈라짐(갈라짐은 ⑦ 삼분으로).
- 산출물: `docs/rebuild/<bc>/eval_ai.md` — 라운드 커밋에 포함.

**⑥-b 사람 평가** — 사용자가 ⑥-a 리포트·diff 를 보고 판정한다(같은 틀이든 자유든).
결과(통과/보류 + 코멘트)를 대장에 기록한다 — **사람 평가 접수 전에는 다음 라운드로
가지 않는다.** 단(08-12 사용자 결정): **기계 3축(⑤)이 이미 불통과인 라운드는 ⑥-b 를
생략할 수 있다** — 사람 평가가 뒤집을 판정이 없다. 그 라운드의 ⑥-b 는 플러그인 수정
후 같은 BC 재라운드가 통과 후보가 됐을 때 수행한다.

**⑥-b 일시 중지(2026-08-14 사용자 지시 — 외출·S3 자율 반복)**: S3 자율 반복 동안
라운드는 **⑤+⑥-a 로 닫는다**(«둘 다 접수» 요건의 한시 대체). ⑥-b 는 사용자 복귀 후
소급 수행 가능하며(결과지·diff 전부 보존), **스트릭이 목표(§3)에 닿아도 S4 진입 전
사용자 확인은 불변**이다 — 자율 루프가 홀로 국면을 넘지 않는다.

**판정 원칙(2026-08-13 — H6′)**: **밖에서 보이는 결과가 갈리는 지점**의 자기 해석·자가
승인이 박힌 완주는 정지보다 위가 아니다 — 평가는 산출물과 함께 «결정 주체»를 본다.
결과지의 라운드 판정 라인에는 **«결정 주체 관측: 자기 해석 N · 자가 승인 N · STOP N»**
을 병기해야 판정이 성립한다(라운드 판정 라인은 프로토콜 소유 — eval v5 무접촉).
정지에는 의무가 짝진다: 정지 전 공백을 전수 수집해 한 STOP 에 일괄 상정한다(+선택지별
대가 표 — 2·codex′ 의 2건 일괄이 선례). 종료 조건(연속 2 BC ⑤ green)은 불변이다.

### ⑦ 삼분 처분 + 대장 기록
1. **문서/하네스 결함** → `spec.md`·이 프로토콜 보강(플러그인 평가와 무관). 스팩 등가가
   깨졌으면 보강한 문서로 같은 BC 재투입.
2. **플러그인 결함** → **먼저 fixture/matrix 케이스로 고정** → dddjango 수정 → 검증 8종
   (`make release` [2/7] 세트) 재실행 → 필요시 재배포 후 같은 BC 재라운드. 규칙 «값» 이
   바뀌면 eval v5 unfreeze/새 epoch 절차가 딸려온다.
3. **옛 코드 버그** (예: delivery 거짓 성공 — `FakeAlimtalkGateway`) → 사용자에게 보고,
   보존/수정 판정을 받는다.

라운드마다 §4 대장에 한 줄 기록.

## 3. 종료 조건 — 반복의 목표 (2026-08-14 명문화)

**목표: 연속 2개 BC 가 플러그인 무수정으로 ⑤ 3축 green + ⑥a 통과** → S3 종결,
마스터 로드맵 **S4(전 BC 일괄 설계)** 진입(진입 «전» 사용자 확인 필수 — §2⑥ 일시 중지
단서). **N=2 사용자 확정(2026-08-14)** — 스트릭 기점 0·자율 반복 범위(§5.5)·속도 레버
편성(§5.6)까지 같은 날 함께 확정.

- **스트릭 기점 = 0.** 스트릭은 «플러그인 무수정» 사슬이다 — 라운드 3(parent_settings)은
  ⑤ 전부 green 이었으나 그 수확이 v2.6.0 수정을 낳았으므로 사슬 밖(산출물은 유효).
  S3 는 v2.7.0 에서 0 부터 센다.
- **BC 큐(로드맵 §2 정렬 원리)**: child_settings 재도전 → products → entitlements → ….
  즉 최단 경로는 «child_settings 무수정 통과(스트릭 1) → products 무수정 통과(스트릭 2)
  → S4». 어느 라운드든 결점이 나오면 수정 사이클 후 스트릭 0 에서 재시작한다.
- (구판 행선지 «계획 5번(속도 개선)»은 S2 속도 사이클로 선집행돼 소멸 — 08-14 정렬.)

## 4. 라운드 대장

| 라운드 | BC | 앵커 | A shape | B 전역 | C 플러그인 | ⑥a AI | ⑥b 사람 | 발견·처분 | 플러그인 수정 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | child_settings | 1c02d89a | ⚠(자녀 경로 0 · 타 BC x-date 시간값 1건=하네스) | ✅ 7199 green | ❌ registry exit 2 + gate 잔존 3 | ✅ 접수(14a67001) — 테스트 ⓑ 0건·spec 충실·개선 3·처분 «통과+문서 보강+플러그인 후보» | 생략(사용자 08-12 — ⑤ 불통과 라운드라 불요·재라운드에서 수행) | ④ ad27fa3b(클린룸 준수·파이프라인 정상 가동 — 세션 감사) · **V1 트리 재생산**: houserules §1.1 예외 ⑵ 미적용+표준 트리를 dddart 것으로 오인, 백스톱은 BC 폴더 TARGET 호출로 조용 exit 0 → ⑦-⑵ 플러그인 결함 2건(P1 결정 순서 사각·P2 호출 계약 사각) + ⑦-⑴ 하네스 1건(shape 시간 의존 값) | **v2.1.0**(P1′ 답습 발본색원·P2 호출 계약·H1 shape 시간값 — dddjango 47fce0d·release 398707b·fixture 84/84) |
| 1′ | child_settings | 0ee0353f | ✅ diff 0 | ✅ 7193 green | ❌ registry 귀속 23건 (**gate 잔존 0 = V2 트리 달성** — P1′/P2 성공 자 충족) | ✅ v5 rubric 결과지 `workspace/eval/results/20260812-1747-csrebuildlive-claude.md` — 치명 1(SD-6)·정적 FAIL | 생략 가능 단서 해당(⑤ 불통과) — 사용자 판단 | ④ 6dedbfd0(클린룸 준수 — 감사: 금지 접근 0 · **registry 27종 루트 전수 실행 실측**·귀속 일부 자가 수정 후 잔존 23건을 «확립 규약 보존» 논리로 커밋) · 재라운드(플러그인 v2.1.0) — 클린룸 정화 1a248cdc(eval_ai·설계 명세·graphify stale 39 → 잔존 0) · **결함 축 이동**: V1 트리 재발 0, 대신 ⑴ 배선 답습(preserve 논리 월권 — api_router «parent_settings 동형»·#107-109/#431/#437) ⑵ SD-6 django.db 포트 우회(#2/#4 — port 칸 빈 채 우회) ⑶ 잎 import(#96·#326 — 단일 출처↔잎 규율 긴장) ⑷ 테스트 규율(#385·#387·#420) ⑸ 검사기 사각 2(#390=#385 그림자·#12 는 shadow 침묵) ⑹ 게이트 계약의 brownfield 귀속 공백 | **처분·수정 완료(08-12)**: 계획 v2(`2026-08-12-round1b-plugin-fixes.md`) — 적대 리뷰 4렌즈(판정 차분 재설계·two-pass·Call-흐름 신호·라이선스 전수) + D 결정(D1′=#96 오탐 정정+#326 파생 예외·D3=**code-json 이주**(spec 결함 발견 — spec 이 api.py 배선 지시)·D4=조사 종결) · 구현: registry_gate(차분)+checker_registry+검사기 3종+P1″ 산문 12곳+코퍼스 2곳 · 검증 전부 green(fixture 90/90·smoke 6/6·backstop 675 무변) · 라운드 2 준비 커밋 `0908671c`(spec 오류 절 재작성·pre_success·이관 빚 목록) · **v2.2.0 릴리즈 대기** |
| 2·claude | billing | 68ce0e51 | ✅ diff 0 | ✅ 7018 green(앵커 6,883 대비 신규 red 0·billing 135 추가) | ❌ **정본(앵커 승인 빚) 기준 귀속 15건**(전부 #12 — ACL 의 미이관 `published_service` 소비·spec §5 지시 의존) / 자가확장 빚 파일 기준 0 green · migration_gate billing 잔존 0 | ✅ v5 결과지 `workspace/eval/results/20260813-1005-blrebuildlive-claude.md` — **치명 0·Q «상»·정적 준수(FC ⏸️)** — v5 라운드 최초 치명 0 | 대기(⑥b 사용자) | ④ 96e3f869(클린룸 위반 0 — git 4건 전부 자기 확인·V1 원본 접근 0) · **최대 사건=빚 파일 자가 확장**(+41줄: #12 OHS 3건+#210/#63 waiver — 투명 표기·커밋 정직 기재이나 «사용자 승인 목록» 무효화 경로 → F3 «가필=승인 위조» 조항의 필요성을 2.2.0 이 독립 실증) · waiver 2건은 사문(최종 트리 발화 0 실측) · #365×3=도구 아티팩트(**부기 08-13**: git-과탐 초판 진단을 적대 리뷰가 정정 — 실체=bc_registry_run 단일-BC 그림자 로스터 공백·검사기 무결·수정처=하네스 ROSTER_AWARE) · 라운드 1′ 결함 축 전멸(SD-6 포트 우회→UoW 포트·배선 답습→registrar·잎 import·테스트 규율 재발 0) · grant-시점 already-entitled=«영구 실패(500)» 자기 해석(스팩 공백 — 레인 B STOP 1 과 상호 실증) · **처분 대기: 빚 3건 승인 여부(승인 시 코드 무수정 green)** | v2.2.0 |
| 2·codex | billing | 68ce0e51 (같은 앵커) | — | — | — | — | — | 워크트리 `broccoli-rebuild-codex`(브랜치 `rebuild/standard-tree-codex` — 앵커에서 분기) · codex 플러그인 2.2.0 확인(마켓 스냅숏 upgrade+add 실측) · **④ 불통과 — 토끼굴(08-13)**: 명세 §1.4 로 타 BC 11개 이관 100파일→귀속 138→G1′×3(전 게이트 자기승인) — 이후 자가 revert 실측(변경 2줄·단 자기 correction 인용). 미커밋 종료 → 수정 사이클(정본 `2026-08-13-codex-rabbit-hole-fixes.md`)·카운트 0 | v2.2.0 |
| 2·codex′ | billing | **5a15123f** (68ce0e51 + 요청문 필수 절 5종 — spec·shape·빚 목록 동일) | ➖ | ➖ | ➖ (구현 0 — diff=`.dddjango` 문서 3파일뿐 실측) | ✅ v5 결과지 `workspace/eval/results/20260813-0937-blrebuildlive-codex.md` — 채점 불가·**stopped 유효 종료 판정** | 대기(⑥b 사용자) | ④ df2fbb60 `stopped — 정본 계약 충돌 2건`(01:58→03:08·70분) — **정지 2건 모두 실증 정당**: STOP 1=post-success family race(spec §2/§3.4/§5 상태기계 공백 — 레인 A 는 같은 지점을 «영구 실패 500»로 자기 해석 완주=상호 실증) · STOP 2=int64 OpenAPI(독립 골든 작성자도 «spec 공백» 지목·단 «충돌» 프레임엔 과잉 해석 성분) · **1차 토끼굴 축 전부 재발 0**(Placement 준수·빚 가필 0·Phase 0 exact 27종 표·G0 빚 ⓑ 고정·앵커 동결·자기승인 0) = **v2.3.0 F1/F2/F3 작동 실증** · 클린룸 실질 오염 0(git log -8 제목 8줄 노출은 주의 기록) · 미작동 1: update_plan 호출 0 재현(⑶ 수정 무효 — ⑦ 재상정) · **처분: 정지 2건은 2′ 재료에 결정 반영(spec 개정 2건) — 레인 재개 대신 재라운드(사용자 08-13)** | v2.3.0 |
| 2′·claude | billing | **67dba2c1** «preflight ✅» (정화 f26616da 로 트리=68ce0e51 동일 복원 실측 후 spec 개정 2건+빚 OHS 3행+anchor-preflight — 기동 HEAD=9e2bf0e7 요청문·앵커 해시 기입) | ➖ (⑤ 미실행 — G2 정지) | ➖ | ➖ (정지 시점 자가 게이트: 귀속 25 — #385×12·#389×1·구조 12·나머지=미완 슬라이스분) | ➖ (라운드 중단 — 채점 대신 수확) | ➖ | ④ 11:30 기동 → **STOP 9a6c85d7(14:47 · G2 S1~S3 완료 후 — 태그 `rebuild-r2p-claude-stopped`)**: G0 8m·Phase1 65m(리뷰어 **직렬 디스패치 실측** — L4 근거)·G2 123m·billing 106 테스트 green·mypy strict — **H1′ 반사실 확정**(spec §3.3 프로필 명명 문면을 리뷰 4종 포함 통과 — 레인 B 는 같은 문면에서 STOP·성향 갈림 실측) · STOP 원인=**빚 파일 규칙-축 과소 수록**(재료 결함 — 상류 3경로를 #12 로만 수록·ACL 번역 테스트의 같은 의존이 #385/#389 로 발현=목록 밖 귀속) · STOP 형식 완비(A/B/C+대가·권고 A=요청문 잔존-빚 메커니즘 인용) · AskUserQuestion 0(입력 요청=평문 → 업그레이드 ①) · **라운드 중단(사용자 08-13: billing 과대 — 소형 BC 재선정·업그레이드 선행)** · 수확 정본 `workspace/eval/results/20260813-r2p-harvest.md` · (준비 기록) **첫 v2.4.0 라운드**: spec 개정=라운드 2 STOP 2건 결정 반영(⑴ grant-시점 `family_already_entitled_v1`=영구 실패 500·성공 종결 유지·§5 409 갈래는 eligibility 관찰 한정 ⑵ 값 경계=저장·조회 전 가드 소유·OpenAPI 상한 무선언 — 결과지 부록 A 권고안) · 빚 3행 사전 수록(#12 OHS — 부록 A ⑴) · 요청문=템플릿 v2.4.0(리터럴 게이트 1·1·0 실측) · baseline 6,883 green·red 0(158s)·migration_gate billing 0(타 BC 63) · graphify 클린 복사(billing 언급 0) · **관측 의무: 결정 주체 관측(자기 해석·자가 승인·STOP) 병기 + STOP 대가 슬롯 충족 검증 + H1′ 반사실(신규 요청문 아래 claude 가 STOP 을 쓰는가)** | v2.4.0 |
| 2′·codex | billing | 67dba2c1 (같은 앵커·같은 요청문 — 공정성 절 충족 · baseline 레인 B 자체 실측 6,883 green) | ➖ | ➖ | ➖ (구현 0 — diff=`.dddjango` 문서 4파일뿐·design-spec 미생성) | ➖ | 대기 | ④ 38ea0b6a `stopped — 설계 역할 결과 미수신`(11:24→11:59·35분) — **유효 정지**(실행 blocker 분류 정확·«STOP 아님» 자기 구분 정확·coordinator fallback 금지 준수·자기승인 0·G0 산출물 3건 정상·build_anchor=67dba2c1 앵커 동결 준수) · **진범=코디네이터 대기 정책 공백(rollout 실측)**: spawn_agent 후 wait_agent 10~60s 폴링 전부 timeout → `list_agents` 는 내내 «running» 인데 «미수신» 으로 분류 → interrupt_agent ×2 = 턴 파괴(fork 1 은 「명세를 닫는 중」 발화 직후 중단·retry fork 는 5분 만에 중단) → 포기. fork 1 15분·fork 2 5분 — 쌍둥이 SKILL 이 spawn/wait «사용»은 지시하나 **대기 정책(타임아웃≠실패·죽음 판정 자·interrupt=재촉 금지)** 미규정 — 공백을 «미수신=blocked» 엣지 규율(죽은 에이전트용)로 메움 · 클린룸: `git log -5 --oneline` 1회(제목만·전부 리빌드 준비 커밋 — 실질 오염 0·정직 신고·재발 2회째) · 관측: update_plan 자발 2회(**지시 삭제 후에도 호출** — 네이티브 도구·무해·지난 판 «지시 있고 0회» 와 역설)·한 줄 상태 `[k/n]` 발화 0(H5′ 미작동 재현) · **처분 ⑦-⑵ 완료(08-13)**: 쌍둥이 수정(wait 정책 명문+architect 산출물-우선 쓰기) — 정본 `2026-08-13-codex-wait-policy-fix.md` · 커밋 9fde420·**v2.4.1 릴리즈**(a230a08·설치본 양쪽 2.4.1) | v2.4.0 |
| 2′·codex″ | billing | 67dba2c1 (동일 앵커·동일 요청문 — 워크트리 9e2bf0e7 로 재초기화·stopped 이력 태그 `rebuild-r2p-codex-stopped` 보존·사용자 «초기화» 지시로 stopped.md 재개 조건(폴더 재사용) 대신 **전 구간 2.4.1 fresh 실행** 선택) | ➖ | ➖ | ➖ | ➖ | ➖ | ④ 기동 후 G0 이전 자기-정지 44427853(반사 git log — 처분·상세=아래 2′·codex‴ 행) · (준비 기록) 정화 실측: .dddjango billing 폴더 소멸(잔존 8+SCOPE-GUIDE=앵커 트리 소속)·pycache 0·그래프 클린(billing 0·5a15123f)·tree diff 0 · **관측 의무: 대기 정책 작동 여부(wait_agent 반복·interrupt 0·architect 파일 성장) + 기존 의무(결정 주체·[k/n]·update_plan)** | v2.4.1 |
| 2′·codex‴ | billing | 67dba2c1 (재료 무변 — 기동 HEAD=**97f68145** 요청문 v2) | ➖ | ➖ | ➖ (구현 0 — G1 정지) | ➖ | ➖ | ④ 12:59 기동 → **STOP dd4adee(14:18 · G1 — 태그 `rebuild-r2ppp-codex-stopped`·main repo ref 동기화)**: G0 2m·Phase1 55m·재리뷰+정지 정리 22m — **3중 방어·대기 정책 전부 작동 실측**(반사 git log 정지 재발 0·spawn 10/wait_agent 71/interrupt 0·architect design-spec 91KB 산출=산출물-우선 쓰기 작동·update_plan 0) · STOP 원인=**spec §3.3 프로필 «명명» 결함**(재료 결함 — «dddjango-code-json» 이름이 스킬 §5.4 media type 정의와 문면 모순·V1 wire=problem+json 실측·플러그인 §5.4 는 무결 판정: 리뷰어 독해는 문면 충실·초판 «오독» 진단 철회) · STOP 형식 완비(1/2+대가·권고 불가 사유 명시) · 설계 blocker 6건 동봉(race 순서·cutover fence 는 레인 A STOP 목록과 상호 실증 — 다음 라운드 spec 재료) · **라운드 중단(사용자·동일 결정)** · (준비 기록) 직전 시도(2′·codex″)는 **G0 이전 자기-정지 44427853**(요청서 읽기와 병렬 반사 `git log -6` — 제목 6개=전부 라운드 재료·실질 오염 0·**반사 log 3회째**: 문서 지시가 닿기 전 시점이라 지시로는 불가침 → 태그 `rebuild-r2pp-codex-stopped` 보존) · **클린룸 3중 방어 신설**: ⑴ 워크트리→**이력 절단 clone** 교체(`--depth 3` file:// — 이력=라운드 재료 4커밋뿐·V1 객체 물리 부재 `git cat-file -e 68ce0e51` 실패 실측·로컬 자산 .venv/graphify/.env.local/.codex 복원·git 훅 4종 복제·pre-commit/graphify 훅 발화 실측) ⑵ `.codex/cleanroom-guard.py` PreToolUse 훅(git log/show/diff/stash/reflog 차단 — 차단·통과·`-C` 변형 3케이스 검증) ⑶ 요청문 v2 단서(반사 실행이 차단됐거나 제목만 노출=«기록 후 계속»·정지 사유 아님 — 리터럴 게이트 1·1·0 재실측) · 앵커 무변(spec·빚·shape·preflight 67dba2c1 그대로) · main repo ref 동기화 97f68145 | v2.4.1 |
| 3·claude | parent_settings | **3f14e4f1** «preflight ✅» (docs-only respin: 구 e6ff41e4 의 spec §3 «migration 상태 보존»이 프로토콜 §0 과 충돌 — 라운드 2 cutover 토끼굴 재발 위험이라 «스키마 동결»로 교정 재커밋·코드 트리 byte 동일=baseline 유효) (선행 정리 6a678c9e=notifications 소비자 3파일 결합 해제·101 green → 앵커=spec+shape 51 paths+빚 **규칙-축 전수**(#12·#385·#389×accounts — 2′ 교훈)+BC 삭제+**OHS 동결 스켈레톤**(인바운드 있는 첫 라운드 — 소비자 고정 장치 신설: 계약 dataclass 2+기본값 스텁 1 식재·ACL import 고정)+배선·중앙 api.py 4곳 제거 · baseline `uv run` **6832 green·red 10** — 전부 notifications 동의-OFF 억제=스텁 기인·리빌드 완주 시 green 복귀 기대(preflight 목록) · 기동 HEAD=**be5df8a7**) | ✅ diff 0 | ✅ **6885 green**(신규 red 0·앵커 red 10 전부 green 복귀) | ✅ **귀속 0**(registry_gate 3.14 봉인·빚 #12 1건=목록 내·#385/#51 은 재작업으로 발화 자체 소멸·migration_gate parent_settings 0) — **⑤ 3축 최초 전부 green** | ✅ v5 결과지 `workspace/eval/results/20260814-0059-psrebuildlive-claude.md` — **치명 0·34차원 FAIL 0·Q «상»·⑤ 문면 통과** | 대기(⑥b 사용자 — 스트릭 카운트 판정 포함) | ④ e2ede4aa 완주 커밋(00:07·5h14m) — 클린룸 위반 0(git=add/commit/status 뿐)·자기보고 3건 전부 재실측 일치 · 라이브런 개입 2건(usage_quota lazy화 스코프 확장 승인·STOP 재개=전체 재작업 — 승인 대장 `round3-liverun-approvals.md`) · **빚 최소화 실증**(라운드 2 «자가 확장» 정반대 — 빚 추가 대신 #385/#51 소멸 재작업·docs 무접촉=F3 준수) · **조정자 측 발견 2(수확 최상위)**: ⑴ **검사기 실행 인터프리터 구멍** — python3.9 는 3.12+ 문법 파일을 `_parse` 실패 침묵 스킵(fail-open)→과거 «#210 발화 0» 실측(라운드 2 waiver 사문 판정·라운드 3 STOP 대리 답변 근거)이 전부 아티팩트로 소급 판명(라운드 2 결과지 in-place 정정) ⑵ **#210↔#95/NJ-7 문면 충돌 실재**(레인 B G2 발견 정당 — 3중 실증) · v2.5.0 관측: L2 작동(BC-범위 21:3)·L4 문면 이탈 1(연속 4메시지 background — 실행은 병렬)·AskUserQuestion 2건 실발화(대가 병기)·F1 승인-정박 작동·수렴 회로 위반 0 · 재료 결함=배선 지뢰(usage_quota import-time api.urls 동결 ~1h+ 손실 — preflight 배선 스모크 신설 근거) | v2.5.0 |
| 3·codex | parent_settings | 3f14e4f1 (같은 앵커 — 기동 HEAD=**a4028b77** 요청문 v2(반사 log 단서) · **이력 절단 clone 재구축**: depth 3=커밋 3개뿐·경계(선행 정리) 부재·V1 blob 0 실측·가드 훅 차단/통과 재검증·git 훅 4종 복제·.venv/.env.local/.codex 복원) | ✅ diff 0 (Route A′ 공개 계약 불변+augmenter 2xx 무접촉 기계 증명) | ✅ **6890 green**(신규 red 0·red 10 복귀) | ❌ **귀속 6 → 실귀속 2**(#493×4=`.codex/cleanroom-guard.py` 하네스 아티팩트·승인 판정 밖 / **#545**=save() 이벤트 가드 부재(실코드 결함 — 레인 A 는 가드 실현) / **#210**=domain 예외 direct catch(검사기-표준 충돌 클래스)) | ✅ v5 결과지 `workspace/eval/results/20260814-0059-psrebuildlive-codex.md` — 의미 레인 전 차원 PASS·치명 0·Q-7 전수(레인 A 우위 축)·**⑤ 불통과** | 대기 | ④ **완주 커밋 부재**(최종 구현 전부 미커밋 워킹 트리·STOP 형식 기록도 없음 — 종료 상태 불명확=규약 이탈) · 레인 채널 request_user_input 4회: G1(Route A·OpenAPI D)→G1′(Route A′+guard #493 제외)→**G2 `RULE_CHECKER_CONTRADICTION` «선택 A: 외부 검사기 #210 정합 수정 권한»(23:48 승인)** → 세션이 **codex 설치본 캐시 검사기를 직접 수정**(23:55 실측 — 정본·claude 설치본 무결·판정은 정본 기준·«승인 실재·집행 절차 밖» 처분·수정 내용 자체는 정본 후보로 질 높음) · **G2 발견은 정당**(#95 문면·라운드 2 billing 12종 direct catch·레인 갈림 — 3중 실증·«교집합 공집합» 주장만 과장=레인 A 응용 번역 모양이 반례) · 클린룸: 3중 방어 작동(가드 차단 1회 «기록 후 계속»·V1 접근 0) · 실코드 흠 2(OHS docstring stale·`_CATALOG` 죽은 코드) · pycache 개명 잔존 관찰 | v2.5.0 |
| S3-r1·claude | child_settings | **42a904ae** «preflight ✅» (1′ 산출물 삭제 라운드 — 삭제 대상=V1 아닌 **1′ 재구현**(V1 원본=`1c02d89a^`)·⑥ 채점 주석 spec 서두 병기 · spec 재검증·shape 재생성 51 paths(자녀 경로 성공-모양 byte 등가·무관 차이=/v1/payments 소멸뿐)·빚 **규칙-축 전수** `#12/#385/#389 application.pairing`(구 `#420` 옛-테스트-이름 행 걷음·accounts 는 ID-값 참조라 빚 아님)·배선 걷기 4구역(urls·base·api.py — 복원 없음 D3)·오염원 2폴더 git rm(1′ child 산출물+라운드3 parent 산출물의 child «1급 참고» 인용)·**배선 스모크 PASS**(v2.6.0 신설 첫 적용) · baseline **6855 green·red 0**(179.6s)·migration_gate child 0(타 BC 59)·boot 50 paths · 기동 HEAD=**833a16aa**) | ✅ **diff 0**(성공-경로 정규화 byte 등가 — 하네스 재실측) | ✅ **6895 green·red 0**(154s — 앵커 6855+40 신규) | ✅ **registry_gate 귀속 0·exit 0**(앵커 차분·정본 빚 파일) · migration_gate child 0(타 BC 59 무변) · bc_registry_run 21g/6r — red 전부 중앙 브라운필드(#493·#437·#431/#441=앵커 기존분·차분 0 실증)·child 발화=`#12` pairing auth import **1건=빚 목록 내** — **⑤ 3축 전부 green(v5 두 번째·child_settings 최초)** | ✅ **치명 0·Q 상** `workspace/eval/results/20260814-1438-csrebuildlive-claude.md`(WEAK 1=Q-7 e2e 무주석 parent 동형 · **결정 주체: 자기 해석 2(둘 다 실물 근거 검증 일치·정당)·자가 승인 0·STOP 0** · **spec:73-74 판정=«결합 판독» 정당**: wire=9457 모양 V1 축자+소유=code-json 레시피 — 실물 3점(spec D3 주석·FrameworkErrorSchema=problem core·V1 problem_response media) 지지·밖에서 보이는 wire 갈림 없음→STOP 요건 비해당·레인 B STOP 과 «문면이 두 번 읽게 만든다» 재료 결함 신호의 양면 · 1′ 결함 축(SD-6·배선 답습·#287·테스트 규율) 전 축 재발 0 · command/query scaffold 관찰=«미사용 칸이 빈다» 표준 골격의 하네스 오독으로 정정 · 처분=**통과(스트릭 적립 후보 — 사용자 몫)**+재료 보강 2(FC-1 골든 3라운드 연속 공백·spec §3 서두 분리 선언문)+플러그인 수정 후보 2(응용 예외 홈 #210↔#95 병합·#5 base-선호 문면)) | 일시 중지(§2⑥ 단서 — ⑤+⑥a 로 닫음) | ④ 12:39:43 기동(fresh — `claude --model claude-opus-4-8 --permission-mode acceptEdits`·판 `[Opus 4.8]`·herdr 탭 `s3-r1-child_settings`·자율 모드 §5.5) → **완주 커밋 60610e3a(14:38:01 · 1h58m — 라운드 3 5h14m 대비 대폭 단축·워크트리 clean)** · **STOP 0·판단 개입 0**(하네스 개입=도구-실행 승인 ~32회 전부 read-only/허용-경로 — 승인 대장 #1~#4) · registry_gate blocker 2건(#51 test import·#81 루트 OHS)을 **빚 가필 0·재작업으로 소멸**(라운드 2 자가-확장 정반대·라운드 3 패턴 재현) · 자기 판정 2(검증 일치): 게이트 자동 승인=자율 조항 인용·#5/#6 직접-실행 exit 2 를 «parent canon 바이트 동형=타 BC legacy»로 귀속-아님 판정(하네스 차분 실측과 일치) · **spec:73-74 모순 지점을 STOP 없이 통과(H1′ 갈림 3회째 — 어떻게 실현했는지는 ⑥a 결정-주체 축 판정 대상)** · 관측: 검사기 CLI flag 순서 시행착오 ~5왕복(등호형만 가용 — 수확 후보: 사용성)·scaffold 시점 placeholder 파일명이 설계 주석과 역전(⑥a 확인 항목)·세션 말미 판 입력창에 미제출 「push it」(사용자 직접 타이핑 추정 — 실행 안 함·사용자 확인 대기) | v2.7.0 |
| S3-r1·codex | child_settings | 42a904ae (같은 앵커·같은 요청문 — 기동 HEAD 833a16aa) | ➖ | ➖ | ➖ (구현 0 — Phase 1 G1 전 STOP·diff=`.dddjango` 산출물 5파일 +613줄뿐 실측) | ✅ **stopped 유효 판정** `20260814-1343-csrebuildlive-codex.md`(34차원 ➖·STOP 형식 전 항 충족·결정 주체 «자기 해석 0·자가 승인 0·STOP 1(2건 일괄)»·**grader 신규 실증 2**: anchor-preflight 7항에 오류-계약 재검증 항목 자체가 부재 + parent_settings 현물이 같은 9457+code-json 혼합을 침묵 통과 중이라는 증거 — 처분=재료 보강 2(spec-재검증 8항 신설·spec DB 상수 절)+조건부 G2 열거 1(E2 선택 시만)·스트릭 0 유지) | 일시 중지 | ④ 12:43:40 기동 → **STOP 5f31b1c(13:43 · 1h01m — `stopped — 오류 계약·DB 연속성 승인 필요`·워크트리 clean·pre-commit 통과)**: **정지 2건 모두 재료 결함 실증** — ⑴ **S1 오류 계약**=spec.md:73-74 「wire 는 RFC 9457 problem+json 유지 + 소유는 dddjango-code-json」 문면 모순 그대로 잔존(2′·codex‴ dd4adee 와 동일 축 — billing spec 은 2′ 준비에서 code-json 재작성됐으나 **child spec 은 앵커 «spec 재검증»이 오류-계약 절 정본-정합을 안 봄**=재검증 사각) ⑵ **S2 DB 연속성**=spec 에 DB·migration·스키마 절 0건(라운드 3 «스키마 동결» respin 교훈 미이식 — 답은 프로토콜 §0 «비운영·새 0001»에 있으나 레인 재료 밖) · **정박 판정: S1=공개 wire 결정+spec 개정 필요=자율 범위 밖(§5.5 «spec 뒤집기») → 대리 답변 불가·S2=§0 정박(D1)이나 재개는 둘 다 필요 → 재개 불성립=STOP 유효 종료 확정·카운트 0** · STOP 형식 완비(선택지별 대가·권고 불가 사유 저자 명시·공백 전수 수집·pending 4 재입장 표식) · **작동 실증**: 한 줄 상태 `[2/4]` 첫 실발화(H5′ 3회 만에 작동)·대기 정책(wait 반복·interrupt 0·file-growth 확인)·리뷰 3병렬+1 교정(슬롯 4 한계 정직 기록)·G0 registry 27종 빚 0·Serena 부재 자기 보고 · **레인 갈림 3회째(H1′)**: 레인 A(claude)는 같은 spec:73-74 아래 STOP 없이 Phase 2 진행 — 레인 A 의 오류 계약 실물이 ⑤A/⑥a 의 최대 관전점 · 기동 전 준비·전달 이슈=아래 준비 기록(`codex -m gpt-5.6-sol -c model_reasoning_effort="xhigh"`·판 `gpt-5.6-sol xhigh`·`default_mode_request_user_input` ON 실측·같은 탭 분할 판) · 준비: 구 clone **evidence 보존**(46e2094·태그 `rebuild-r3-codex-final`·디렉터리 `-r3-evidence` 개명 — 라운드 3 미커밋 산출물 무손실) → **이력 절단 clone 재구축**(depth 2=재료 2커밋뿐·V1-era `e2ede4aa` 부재 실측·cleanroom-guard 3케이스 exit 2/0/2·git 훅 4종 복제·.env.local/.codex/graphify 클린 복원·pycache 0·설치본 2.7.0 양쪽 동일) · baseline 자체 실측 **6855 green·red 0**(154.8s) · **L5 첫 적용=병렬 기동 첫 라운드**(`POSTGRES_TEST_DB=test_broccoli_codex`·동시 pytest 양쪽 green·DB 이름 분리 실측) · 전달 이슈 1: 요청문 첫 줄 `/dddjango` 를 codex TUI 가 슬래시 명령으로 오인(Unrecognized·본문 미제출) → 재기동 후 **파일-경유 전달**(요청문 내용 무변 — 12:41:08 첫 시도는 무효·쌍둥이 전달 규약 후보로 ⑦ 상정) · 관측 의무: 대기 정책·결정 주체·[k/n]·request_user_input 발화 | v2.7.0 |

| S3-r2·claude | products | **b927a275** «preflight 8항 ✅» (사용자 「가장 작은 BC」 선택 — 실측: entitlements 1,497 은 인바운드 1이라 게이트 위반·**products 1,867·인바운드 0**(소비자였던 billing 이 현 트리 부재)·HTTP ✓ · 선행 정리 **5823b806**=entitlements 인수 테스트의 products 모델 결합을 함수-내 importorskip 으로 해제(존재 시 원형·34 green — FK 사각 grep 0 실측) · spec 추출=서브에이전트 초안+하네스 검수(V1 축자 스팟체크 4·인터뷰성 관측은 `workspace/plan/2026-08-14-s3r2-products-harness-notes.md` 로 분리 — 레인 입력 밖) · **⑻ 첫 적용**: §3 분리 선언문+§7 DB 상수 절이 spec 에 처음부터 실재(S3-r1 레인 갈림 두 축 사전 봉쇄) · shape 2판 51 paths·빚 `#12/#385/#389 application.accounts`(라운드 3 동형)·V1 삭제+배선 2행 걷기+오염원 2폴더 git rm(V1 구현 경로 직인용 실측·billing 재료는 계약-표면 언급뿐이라 존치)·배선 스모크 PASS · baseline **6705 green·1 skipped(선행 정리 시나리오 — 설계대로)·red 0**(146s)·migration_gate 53=전부 타 BC(59→53=products 몫 소멸)·boot 50 paths · 기동 HEAD=**28388a07**) | ➖ | ➖ | ➖ (구현 0 — G1 STOP·`application/products/**` 미생성·배선 무수정·probe 자가 정리 실측) | ➖ | 일시 중지 | ④ 17:57:35 기동 → **STOP 215feb6a(19:36 · 1h39m — `stopped — spec §5 seed 명령이 표준트리 #58·#490 신규 귀속 강제(승인 빚 목록 밖)`)**: **재료 결함 3번째 축 발견=spec 의 «실현 메커니즘 축자»** — spec §5 가 V1 의 Django management command 를 계약으로 축자했으나 표준 정본 #58 이 `application/**/management/commands/` 명시 금지·**정본 #593 절이 대체 자리를 이미 지정**(«대량 채우기=배포 절차의 한 단계·코드는 트리 밖 `scripts/`») — 하네스 정박-소진 실측으로 확정 · **STOP 질 최상급**: 정본 3단 대조(final.md·검사기 소스·probe 게이트 차분 실증 — 기존 command 8개=legacy 비준수임을 자가 정정해 «관행 동형» 전제 반증까지)·닫힌 선택지 4+대가·권고 불가 사유·잔여 상태(G1 설계 완성·리뷰 4종 반영·이 1건만 미해소)·재개 지침 완비 · **⑻ 효과 실증**: S3-r1 두 STOP 축(오류 계약·DB) 재발 0 — 분리 선언문·DB 상수 절이 작동, 대신 새 축(메커니즘 축자)이 드러남=검수 항목 후보 ⑼ «spec 요구 ↔ 표준 트리 금지 대조·메커니즘 중립성» · 도구승인 ~7(전부 read-only 정본·검사기 조회+probe — S3-r1 대비 급감: don't-ask-again 저장 효과) · **정지 처분: 정박 불가 확정**(빚 확장 A=사용자 권한·트리 확장 D=플러그인 소유·spec 개정 B/C=respin+재라운드 결정 — 셋 다 사용자 몫) → 레인 B 도 «어차피 다시» 원칙으로 하네스 중단(19:39:37) · 플러그인 무결(백스톱·정본 정확 작동 실증) | v2.7.0 |
| S3-r2·codex | products | b927a275 (같은 앵커·같은 요청문 — 기동 HEAD 28388a07) | ➖ | ➖ | ➖ (구현 0 — G1 진행 중 중단·diff=`.dddjango` 산출물 폴더 1) | ➖ | 일시 중지 | ④ 18:00:15 기동(`codex -m gpt-5.6-sol -c model_reasoning_effort="xhigh"`·판 실측·파일-경유 전달 선적용 — 오인 재발 0) → **19:39:37 하네스 중단**(레인 A STOP 으로 재료 결함 확정 — 사용자 「어차피 다시 해야」 원칙 적용·같은 spec §5 blocker 로 갈 것이 예측돼 비용 절약) · 중단 전 관측: G1 리뷰 4종 수집→architect 730줄 재대조·«외부 선택 선반영 없음» 자기 보고(F1)·대기 정책 작동·수렴 회로 1회차 인지 — S3-r1 STOP 축(오류 계약·DB) 재발 없이 G1 전진 중이었음=⑻ 효과 방증 · 준비 기록: evidence `bd45805`(태그 `rebuild-s3r1-codex-stopped`)→이력 절단 clone(60610a3e 부재 실측·guard·L5)·baseline 6705 green·1 skip(레인 A 와 동시=L5 재실증) | v2.7.0 |
| S3-r2′·claude | products | **b88d48ea** «respin — preflight ⑻⑼ ✅» (spec §5 scripts/ 실현 개정=사용자 C′ 승인·⑼ «실현 표면↔트리 칸 실재» 대조 신설·request Placement ⑷ `scripts/seed_temp_products.py` 1파일·STOP 산출물 오염원 git rm·docs-only=코드 트리 무변 baseline 6705 유효 · 기동 HEAD=**9c50cf26**) | ➖ (자가: 성공-shape 구조 대조 통과 — exact diff 는 하네스 도구 밖·⑤ 미실행) | ➖ (자가: products/test **129 green**·인수 3종 green(e2e 4·OHS 통합 6·계약 단위 12)·슬라이스2 전역 0-new-red — 전역 ⑤ 미실행) | ❌ **registry_gate 귀속 52건 red**(앵커 차분·27체커 exit 1=0·Placement 준수 — 빚 #12 accounts 는 목록 내 정상 격리) | ➖ (STOP 라운드 — r2 전례·수확은 본 행+STOP 기록으로 완결) | 일시 중지 | ④ 20:41:11 기동 → **STOP 66716617(08-15 00:07 · 3h26m — `stopped — spec §6 OHS·§4 admin 문면이 표준트리 금지와 근본 충돌(귀속 52건)`·워킹트리 clean)**: **재료 결함 4번째 축 확정=«published 계약 축자 vs 표준 명명·모양»** — spec §6 이 V1 OHS 계약(V-접미 3·예외형 not-found·`get_purchasable_product_v1`·`PurchasableProductV1`)을 축자 요구 ↔ 표준 #170(V-접미 금지)·#453/#454(부재·거절=«답», 예외 아님)·#482(`_query` 접미)·#484(`<Operation>Response` 명명)·#456·§4 기능형 admin ↔ #462(ORM import=adapter/persistence 전용) — **한 구현이 둘을 동시 만족 불가**·parent OHS 는 버전 없음·admin 빈 껍데기라 선례 부재 · **분해: (A) 축소 불가 spec 충돌 ~10건 / (B) 위임 가능 수리 ~40건**(#493×23·#169×4·#290·#571·#576·#545·#597/#197·#7·#307·#474·#390 등 — (A) 결정이 (B) 수리 방향을 바꿔 **의도적 보류**=수렴 회로 준수) · STOP 질 최상급(게이트 증거 전수 표·분류 표 2·닫힌 선택지 3+대가·권고=respin(⑼ seed 동형 선례 인용·«결정 아님» 명시)·재개 지침=`STOP_FOR_USER_APPROVAL.md`) · **⑼ 효과·한계 실증**: 기존 3 STOP 축(오류 계약·DB·메커니즘) 재발 0 — 단 ⑼ 는 «칸 실재»만 검사, **«이름·모양 규약 정합» 미검사=이번 누출 지점(preflight ⑽ 후보)** · 규율 감사 4라운드 «이의 없음»(Bash 없는 리뷰어=의미 담당·백스톱=구조 담당 — 역할 분담 설계 작동·mypy 는 #493 못 잡음도 자가 문서화) · 도구승인 ~19·판단 개입 0 · **하네스 정박 소진 판정(§5.5): 정박 불가·STOP 유효** — spec=충돌 원천·요청문=«밖에서 보이는 결과 갈림=STOP» 문면 해당·빚 목록=accounts 뿐·§0=OHS 계약 우선순위 무규정·정본 표준=대체 «형태»(버전 없는 `_query`·답 반환·admin ORM 경계)는 지정하나 그 채택=spec «V1 축자» 폐기=spec 개정=비위임(#593 동형 구조) · 관측: 세션 말미 판 입력창 미제출 「respin the spec §6/§4 to standard-tree conventions」(타이핑 주체 불명 — 실행 안 함·**제출 금지 존치**·사용자 확인 대기) | v2.7.0 |
| S3-r2′·codex | products | b88d48ea (같은 앵커 — 새 이력 절단 clone·215feb6a 물리 부재 실측·evidence `-s3r2a-evidence` 태그 `rebuild-s3r2a-codex-interrupted`·파일-경유 전달) | ➖ (자가 diff 0) | ➖ (자가 **6,780 green+1 skip** — products 75·인수 17·mypy strict) | ❌ **registry 귀속 66건**(+composition checker exit 1=`BroccoliNinjaAPI` subclass 미인식 — **레인 A 는 27체커 exit 1=0 이라 재현 안 됨**·구현 방식 종속 검사기 이슈 후보로 이월) | ➖ (동상) | 일시 중지 | ④ 20:42:00 기동 → **STOP 72bff36(23:14 · 2h33m — «G2 registry 귀속 66건»·기능 완주 수준에서 C축 정지·워킹트리 clean·개입 0)** · stop-report 68행(`.dddjango/20260814-2050-product-catalog/stop-report.md` — checker별 분해 표·선택지 4+대가·권고 불가) · **교차 판정(08-15 — 레인 A STOP 확보 후 일괄)**: ⑴ **계약-충돌 성분 ~10건 = 레인 A (A) 와 독립 수렴**(#170·#453/#454·#482·#484·#456·#462 같은 축 — 함수 suffix·응답 class·V-접미 예외 3·not-found 의미 — **재료 4축 교차 실증·STOP 유효**) ⑵ **구현 규율 성분 ~50건**(UoW shape 4·repo abstractmethod 8·e2e 자기-구현 import 15·admin ORM 등)=레인 A 가 동류를 «(B) 위임 가능 수리»로 분류 — 이를 «spec 변경 필요»로 실은 것은 **과대 프레임 성분 확정**(재작업 대상이지 spec 결함 아님·단 ⑴ 이 섞여 STOP 자체는 유효) · H1′ 관측: **이번엔 양 레인 같은 지점 STOP(갈림 아님)** — 충돌이 성향 아닌 구조임의 방증 | v2.7.0 |

## 5. S3 성숙기 스트릭 — 라운드 운영 절차·성적표 (2026-08-14 사용자 확정)

S3(마스터 로드맵 §1)의 매 라운드는 **아래 여섯 걸음을 이 순서 그대로** 돈다 — §2 일곱 걸음의
운영 래퍼다(각 걸음의 실행 상세는 §2 해당 절이 정본 — 여기 재서술 금지). 목적: 라운드가 몇
번이어도 같은 절차·같은 기준이어야 스트릭 판정(§3)과 라운드 간 비교가 성립한다.

### 5.1 여섯 걸음 (매 라운드 동일)

1. **재료·앵커** — §2①(BC 선정: 시드+실측 게이트 3) → §2②(spec.md·shape 2판·빚 파일
   **규칙-축 전수** 수록 — 2′ 교훈) → §2③(삭제=앵커)+anchor-preflight 8항(§2④ 절 — ⑻ 오류-계약·DB 절 정본-정합은 2026-08-14 신설) →
   `request.md` 기동 HEAD 커밋(앵커 해시 기입 — 해시 순환 탓 앵커 «뒤» 별도 커밋이 규약).
   ⑤C 가 `--anchor <해시>` 기준이라 이 걸음 없이는 평가가 성립하지 않는다.
2. **클린룸 준비(레인 A·B 각각)** — 기동 HEAD 로 reset · pycache 0 · `.dddjango` 소멸 ·
   graphify 클린 · 레인 B=이력 절단 clone+cleanroom-guard 훅 · baseline `uv run pytest`
   green+migration_gate 대상 BC 0 실측 · 설치본 버전 양 레인 동일 확인 · §4 대장 행 기입.
3. **라이브런** — §2④. 사용자가 기동한다(**기동 시각 기록**). 개입은 승인 대장에 기록.
   두 레인 pytest 동시 실행은 §0 단서(테스트 DB 분리 실증 시 병렬 허용 — L5)를 따른다.
4. **평가 두 겹(순서 고정 — ⑥b 는 일시 중지·§2⑥ 단서)** — ⑴ §2⑤ 기계 3축(**레인
   `.venv` 3.14 필수**) → ⑵ ⑥a v5 rubric 결과지(기준 정본=`workspace/eval/rubric/`
   (RUBRIC.md·EVAL-METHOD.md) · 생성 위치=`workspace/eval/results/YYYYMMDD-HHMM-<slug>-<레인>.md`).
   라운드는 ⑤+⑥a 로 닫는다 — ⑥b 는 사용자 복귀 후 소급(결과지·diff 보존).
   완료 즉시 §5.3 성적표에 레인별 한 행 기입.
5. **분기** — 무수정 통과: 스트릭 +1·다음 BC. / 결점: §2⑦ 삼분 처분 → 수정 사이클 →
   **릴리즈+설치본 양쪽 갱신까지가 «수정»이다**(갱신 없이 다음 라운드를 돌면 옛 버전
   실측이라 무효) → 스트릭 리셋.
6. **반복** — **목표=§3(연속 2 BC 무수정 통과)**. 도달 시 S3 종결 → 사용자 확인 →
   마스터 로드맵 S4. 도달 전에는 걸음 1 로 되돌아간다(결점 라운드였으면 걸음 5 의
   수정·릴리즈 후).

### 5.2 시간·개입 측정 규칙 (성적표 비교 가능성의 전제)

- **실행 시간** = 사용자 기동 시각 → 완주 보고(또는 STOP 커밋) 시각. 보조 실측=레인
  git log 타임스탬프(기동 HEAD 이후 첫 커밋~마지막 커밋 — 기계 검증 가능).
- STOP·불통과 라운드의 시간은 기록하되 **속도 비교 표본에서 제외**(✱ 표기) — 중단
  시간과 완주 시간은 다른 물건이라 섞으면 A/B 가 오염된다.
- **개입 수** = 승인 대장 기입 건수(질문 왕복·대리 답변·재개 지시). 시간 해석에 필수
  병기 — 같은 35분도 대기 정책 결함과 순수 작업은 다른 사건이다.

### 5.3 성적표 (라운드×레인 시계열 — §4 대장이 «서사», 이 표가 «비교용 한 줄»)

결과지 칸은 `workspace/eval/results/` 상대 경로. 시간 «미상»=소급 실측 보류(비교 표본
아님). **S3 첫 라운드부터 기입 의무.**

| 라운드 | BC | 버전 | 레인 | 앵커 | 실행 시간 | 개입 | 종료 | ⑤A/B/C | ⑥a | ⑥b | 스트릭 | 결과지 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | child_settings | 2.0.0 | claude | 1c02d89a | 미상 | 미상 | 완주 | ⚠/✅/❌ | 접수 | 생략 | 0 | eval_ai(14a67001) |
| 1′ | child_settings | 2.1.0 | claude | 0ee0353f | 미상 | 미상 | 완주 | ✅/✅/❌ | 치명 1 | 생략 | 0 | 20260812-1747-csrebuildlive-claude.md |
| 2 | billing | 2.2.0 | claude | 68ce0e51 | 미상 | 미상 | 완주 | ✅/✅/❌ | 치명 0·Q 상 | 대기 | 0 | 20260813-1005-blrebuildlive-claude.md |
| 2 | billing | 2.2.0 | codex | 68ce0e51 | ✱ | ➖ | 토끼굴(미커밋) | ➖ | ➖ | ➖ | 0 | — |
| 2·codex′ | billing | 2.3.0 | codex | 5a15123f | 70m✱ | ➖ | STOP(유효) | ➖ | stopped 유효 | ➖ | 0 | 20260813-0937-blrebuildlive-codex.md |
| 2′ | billing | 2.4.0 | claude | 67dba2c1 | 3h17m✱ | 미상 | STOP(재료 결함·유효) | ➖ | 수확 | ➖ | 0 | 20260813-r2p-harvest.md |
| 2′ | billing | 2.4.0 | codex | 67dba2c1 | 35m✱ | ➖ | STOP(쌍둥이 대기 정책 결함) | ➖ | ➖ | ➖ | 0 | — |
| 2′·codex″ | billing | 2.4.1 | codex | 67dba2c1 | ✱ | ➖ | 자기-정지(반사 log) | ➖ | ➖ | ➖ | 0 | — |
| 2′·codex‴ | billing | 2.4.1 | codex | 67dba2c1 | 1h19m✱ | ➖ | STOP(재료 결함·유효) | ➖ | ➖ | ➖ | 0 | — |
| 3 | parent_settings | 2.5.0 | claude | 3f14e4f1 | **5h14m** | 2 | 완주 | ✅/✅/✅ | 치명 0·Q 상 | 대기 | 대기(⑥b) | 20260814-0059-psrebuildlive-claude.md |
| 3 | parent_settings | 2.5.0 | codex | 3f14e4f1 | 미상 | 4 | 완주(미커밋 — 규약 이탈) | ✅/✅/❌ | 치명 0·⑤ 불통과 | 대기 | 0 | 20260814-0059-psrebuildlive-codex.md |
| S3-r1 | child_settings | 2.7.0 | claude | 42a904ae | **1h58m**(12:39:43→14:38:01) | 도구승인 ~32·판단 0 | 완주(60610e3a) | ✅/✅/✅ | **치명 0·Q 상**(WEAK 1=Q-7 e2e 무주석·parent 동형) | 중지 | **1 잠정**(사용자 확정 대기 — ⑥b 소급) | 20260814-1438-csrebuildlive-claude.md |
| S3-r1 | child_settings | 2.7.0 | codex | 42a904ae | 1h01m✱ (재개 17:21→**사용자 중단 17:22** — 재료 보강 선행 결정 「어차피 다시 해야」) | 1(재개 대리 입력 S1=E2·S2=D1 — 중단으로 미집행) | STOP(유효)·재개 취소 | ➖ | **stopped 유효**(형식 전 항·과잉 해석 ~0·플러그인 귀책 0) | 중지 | 0 | 20260814-1343-csrebuildlive-codex.md |
| S3-r2 | products | 2.7.0 | claude | b927a275 | 1h39m✱(17:57:35→19:36:00) | 도구승인 ~7·판단 0 | STOP(재료 결함·유효 — 215feb6a) | ➖ | 대기 | 중지 | 0 | — |
| S3-r2 | products | 2.7.0 | codex | b927a275 | ✱(18:00:15→19:39:37 하네스 중단) | 0 | 중단(재료 결함 확정 — 「어차피 다시」 원칙) | ➖ | ➖ | 중지 | 0 | — |
| S3-r2′ | products | 2.7.0 | claude | **b88d48ea**(respin — spec §5 scripts/ 개정·사용자 C′ 승인·⑼ 신설·코드 트리 무변=baseline 6705 유효) | 3h26m✱(08-14 20:41:11→08-15 00:07) | 도구승인 ~19·판단 0 | **STOP 66716617**(G2 — 재료 결함 4축=«published 계약 축자 vs 표준 명명·모양»·정박 불가·유효) | ➖/➖/❌(귀속 52 red — 자가: products 129 green·인수 3종 green·mypy strict) | ➖(STOP 라운드 — 수확은 대장·STOP 기록으로 완결) | 중지 | 0(r1 잠정 1 유지 — 재료 귀책이라 스트릭 무영향) | — |
| S3-r2′ | products | 2.7.0 | codex | b88d48ea (같은 앵커 — 새 이력 절단 clone·STOP 커밋 215feb6a 물리 부재 실측) | 2h33m✱(20:42:00→23:14:19) | 0 | **STOP 72bff36**(G2 — «registry 귀속 66건»·워킹트리 clean·유효) | 자기실측: A diff 0·B 6,780 green+1 skip(products 75·인수 17)·mypy strict — **기능 완주 수준에서 C축 정지** | ➖(교차 판정 완료 — ⑴ ~10건=레인 A (A) 수렴·재료 4축 실증 / ⑵ ~50건=과대 프레임·재작업 성분) | 중지 | 0 | — |

### 5.4 버전 변경표 (성적표 «버전» 칸이 참조 — 요지 한 줄·상세는 정본 링크)

정본 링크는 `workspace/plan/` 상대 경로. 새 릴리즈마다 한 행 추가(성적표 행 기입과 같은
시점 — §5.1 걸음 5).

| 버전 | 이전 대비 변경 요지 | 정본 |
|---|---|---|
| 2.0.0 | 게이트 해제 — LEGACY_ALIASES·이중 수용·«미이관» 전량 걷음·V1 주소 repoint | `2026-08-12-unified-review-fixes.md` |
| 2.1.0 | 라운드 1 수확: P1′ 트리 답습 발본색원·P2 검사기 호출 계약(checker_target)·H1 shape 시간값 | `2026-08-12-round1-plugin-fixes.md` |
| 2.2.0 | 라운드 1′ 수확: registry_gate 판정 차분·two-pass 빈 스텁·code-json 이주(D3)·#96 오탐 정정 | `2026-08-12-round1b-plugin-fixes.md` |
| 2.3.0 | codex 토끼굴: F1 승인-정박·F2 실행 두 계열·F3 Placement/앵커 동결/비위임/수렴 회로 | `2026-08-13-codex-rabbit-hole-fixes.md` |
| 2.4.0 | A/B 수확: bc_registry_run ROSTER_AWARE·권고≠결정·판정물음 3층·한줄상태 | `2026-08-13-ab-harvest-fixes.md` |
| 2.4.1 | codex 대기 정책(timeout≠실패·interrupt 금지)·architect 산출물-우선 쓰기 | `2026-08-13-codex-wait-policy-fix.md` |
| 2.5.0 | 업그레이드 ① 입력 포맷(AskUserQuestion/request_user_input)·② 속도(L4 병렬·L2 BC-범위 pytest)·③ §5.4 명확화 | `2026-08-13-upgrade-queue.md` |
| 2.6.0 | S1 수확: requires-python 게이트(3.9 침묵 스킵 봉인)·#210 면제 3조건·dot-dir·배선 스모크 | `2026-08-14-s2-speed-v1.md` |
| 2.7.0 | S2.5 문면 위생: corpus_lint·checker_cross_matrix·코퍼스 ~90치환(죽은 경로·V1 예시 축·번호 공간 규약) | `2026-08-14-s2p5-copy-hygiene.md` |

### 5.5 자율 반복 모드 · Herdr 관측 (2026-08-14 사용자 지시 — 「외출·궤적 관측」)

사용자 부재 중 S3 루프는 하네스 세션이 수행하되, **레인 세션은 Herdr 판에서 기동**해
사용자가 언제든 실시간 궤적을 볼 수 있게 한다.

- **기동 주체(자율 모드 대체)**: §2④ «사용자 직접 기동»을 자율 모드에서는 하네스가
  대신한다 — 단 `claude -p` 서브프로세스가 아니라 **Herdr 판의 대화형 세션**으로
  기동한다(관측 가능성이 대체의 조건). 레인 A·B 는 테스트 DB 분리(§0 단서·L5) 아래
  **병렬 기동**한다(2026-08-14 S3-r1 부터 — 분리 미실측이면 종전 순차).
- **레이아웃 규약**: 라운드당 탭 하나 — 이름 `s3-r<N>-<bc>`(예: `s3-r1-child_settings`).
  탭 안: 레인 판(에이전트) + 필요시 관측 판. 하네스(coordinator) 판은 기존 위치 유지.
  사용자는 Herdr UI 로 본다 — 레인 판에 직접 입력하는 것도 개입으로 유효(승인 대장
  기록 대상).
- **대리 답변 위임(자율 모드 한정)**: 레인이 입력을 요구하면 하네스가 **답이 정박된
  물음만** 대리 답변한다(승인 대장 기록). 정박 재료는 spec·빚 파일·요청문에 더해
  **프로토콜 전제(§0 등)·정본 표준 문면**까지다(2026-08-14 사용자 교정 — 「입력을
  해서 진행을 시켰어야지」). **STOP 접수는 정박 소진 후 최후 판정이다**: 정지가 오면
  물음별로 spec→요청문→빚→프로토콜 전제→정본 표준 순으로 대조해 답이 서는 물음은
  대리 입력으로 재개시키고(클린룸 유지 — 타 레인 산출물 언급 금지), 어느 재료로도
  안 서는 물음만 유효 정지로 수확한다(STOP=유효 종료·수확 재료).
- **입력 대행 경로**: 레인의 입력 요구(AskUserQuestion·request_user_input·게이트 질문)는
  하네스가 Herdr `agent prompt`/`agent send-keys` 로 대신 넣는다(위 정박 규칙 불변 —
  선택 UI 는 send-keys, 서술 답변은 prompt). Herdr 지원 kind 실측(2026-08-14):
  **claude·codex 둘 다 `agent start` 가능** — 두 레인 모두 이 경로로 기동·대행한다.
- **레인 모델 고정(2026-08-14 사용자 확정)**: 레인 A(claude)=**Opus 4.8 무조건** ·
  레인 B(codex)=**sol-xhigh**. 기동 시 모델 인자를 축자로 명시하고 기동 커맨드 전문을
  승인 대장에 기록한다 — 고정 모델이 아닌 라운드 실측은 §5.3 성적표 비교 표본에서
  제외(✱). **축자 기동 플래그(2026-08-14 실기동 실측 — 판 상태줄로 확인)**:
  - claude: `claude --model claude-opus-4-8 --permission-mode acceptEdits` → 판 표시 `[Opus 4.8]`
  - codex: `codex -m gpt-5.6-sol -c model_reasoning_effort="xhigh"` → 판 표시 `gpt-5.6-sol xhigh`
    (sol-xhigh 의 실체 = 모델 `gpt-5.6-sol` + reasoning effort `xhigh`)
- **자율 수정 사이클의 한계**: 걸음 5 의 수정·릴리즈·설치본 갱신은 자율 수행한다.
  단 **규칙 «값» 변경·eval v5 unfreeze·spec 뒤집기·대규모 구조 변경**이 필요한 수정은
  자율 범위 밖 — 그 지점에서 루프를 멈추고 사용자 복귀를 기다린다(수확 문서로 상정).
- **S4 진입은 자율 범위 밖**(§3·§2⑥ 단서) — 목표 도달 시에도 멈추고 사용자 확인.

### 5.6 속도 레버 편성 — S3 안에서 (2026-08-14 사용자 확정 — 「S3 로 기준점 먼저」)

속도 정본(`2026-08-13-speed-plan-v0.md`)의 미완 레버를 S3 에 이렇게 편성한다:

- **기준점 우선**: S3 첫 라운드(v2.7.0·배선 스모크 등 재료 결함 제거 후)가 **깨끗한
  속도 기준점**이다 — 기존 실측(라운드 3 5h14m)은 v2.5.0+재료 결함(~1h 손실)이 섞인
  숫자라 기준 부적격. 첫 라운드 실측이 speed v1(레버 서열 확정)의 입력이 된다.
- **플러그인 갈래(L8 병렬 coder·L1 G0 인터뷰·L3 사전 lint)**: 지금 하지 않는다 —
  S3 첫 «결점» 라운드의 수정 사이클에 **동승**시켜 한 릴리즈로 묶는다(스트릭 리셋 1회
  최소화 — 기승인 로직). S3 가 무수정 연속 통과로 끝나면 S4 진입 «전» 별도 결정으로
  상정한다.
- **하네스 갈래(L5 postgres 격리)**: 스트릭 무관이나 라이브런 중 postgres 무접촉
  규약이 있으므로 투입 창은 **라운드 기동 전 또는 라운드 사이**뿐이다. env 기반으로
  짧게 되면 기동 전에, 아니면 라운드 사이로 이월. → **완료(2026-08-14 S3-r1 기동 전)**:
  `.env.local` `POSTGRES_TEST_DB=test_broccoli_codex` 한 줄로 실현(트리 무변경)·동시
  pytest 양쪽 green 실측(§0 단서) — 이후 레인은 병렬.
