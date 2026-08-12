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
  시작에 로드). 워크트리 둘에서 `make testp` 동시 실행 금지(로컬 postgres 충돌).

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

**요청문 필수 절(2026-08-13 신설 — 라운드 2 레인 B 토끼굴 재발 방지 · 정본 `2026-08-13-codex-rabbit-hole-fixes.md`)**: 이후 라운드의 `request.md` 는 아래 다섯 절을 반드시 포함한다.

> **Placement(변경 허용 — 닫힌 목록)**: ⑴ `application/<bc>/**` — 이 발주의 대상 BC **하나**를 축자로 적는다(자리표시자 금지·다른 BC 폴더 불포함 명시) ⑵ 배선 파일 **축자 나열**(발주 시 실제 경로로 확정 — 명세·산출물이 배선 파일을 추가 지정할 수 없다) ⑶ `.dddjango/**`(산출물 전용). **«변경» = 생성·수정·이동·삭제·개명 전부**(`git mv` 는 두 경로 모두의 변경). 배선 파일 안 허용 변경은 **이 BC 등록에 필요한 행의 추가뿐**(기존 행 삭제·이동·재정렬·경로 변경 금지). `docs/**` 는 읽기 전용 — `legacy_debt.txt` 가필·사본·자작 빚 파일을 `--legacy-debt-file` 로 쓰는 것은 승인 위조다(빚 목록은 발주가 준 그 경로·그 내용뿐).
> **앵커 동결**: registry_gate 앵커는 발주가 지정한 `<앵커 해시>` 다 — HEAD 를 재산출하지 말고 이 값을 쓰라. **이 발주 중에 만든 어떤 커밋도 앵커가 될 수 없다.**
> **완료 기준**: `make test` 판정은 **앵커 기준 신규 red 0** 이다 — 앵커 시점에 이미 red 였던 테스트는 보고 대상이지 수리 대상이 아니고, 타 BC 테스트를 green 으로 만들기 위한 허용 경로 밖 수정은 그 자체가 blocker 다.
> **자율 위임의 한계**: 자율 조항이 대체하는 것은 게이트의 **승인 입력**뿐이다. 비위임: `STOP_FOR_USER_APPROVAL`·G0/G2 blocker·shape approved-change·빚 목록 밖 신규 debt 수용·허용 경로 밖 변경·`scope.md`/`refactor-scope.md` 사후 개정·G0 빚 ⓐ 자기선택(자율 모드의 G0 빚 답은 **ⓑ(미룬다 — 사유: 클린룸 자율 라운드) 고정**·«미룰 수 없음» 항목=blocker). blocker 를 만나면 그 지점까지 커밋(제목 `rebuild(<bc>): stopped — <사유 한 줄>`)하고 산출물에 기록 후 **종료하라 — 이 정지는 실패가 아니라 이 발주의 유효한 종료 상태다**(「끝까지 진행」은 blocker 를 넘으라는 뜻이 아니다).
> **수렴 회로**: 같은 게이트의 반송이 2회를 넘거나, 재설계 후 변경 파일 수·신규 귀속 수가 직전보다 늘면(스코프 증가 신호) 반복하지 말고 blocker 로 기록 후 정지하라.

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
`spec.md`·shape·`request.md` 는 자동으로 동일(공정성). ⑤·⑥ 판정과 대장 기록은 레인별로
따로 한다. codex 레인은 codex 마켓 플러그인(`dddjango@changja88-dddjango`)이 같은 버전인지
확인 후 기동(사용자):

```bash
cd <워크트리-codex> && codex "$(cat docs/rebuild/<bc>/request.md)"
```

제약: 레인 워크트리들끼리 `make test`/`make testp` 동시 실행 금지(로컬 postgres 공유 —
§0 전제의 확장). 순차로 돌린다.

완료 후 하네스 세션에 알리면 ⑤·⑥a 를 하네스가 잇는다.

### ⑤ 기계 판정 — 3축 (전부 명령 고정)
| 축 | 명령 | 자 |
|---|---|---|
| **A. API shape** | ②와 같은 덤프→`openapi_shape.py --success-only`→`diff api_shape_pre_success.json <post>` | **성공(2xx) 경로 diff 0** — 오류 경로의 선언·본문은 spec §오류 계약이 정본(⑤C·⑥ 검증 몫). **2026-08-12 D3 개정**: 오류 축을 code-json 표준으로 이주하는 라운드에선 오류 선언이 의도적으로 바뀌므로(FrameworkErrorSchema→BC ErrorSchema) 전체-모양 diff 는 A축 판정이 아니다(라운드 1·1′ 의 전-모양 판은 `api_shape_pre.json` 대비 기록으로 보존) |
| **B. 전역 테스트** | `cd <워크트리> && make test` | 전체 green(신규 테스트 + 이웃 BC 테스트 — 인바운드 표면 검증) |
| **C. 플러그인** | `python3 …/workspace/tools/bc_registry_run.py <워크트리> <bc>` + `python3 …/workspace/tools/migration_gate.py <워크트리>` | registry 27종 전부 exit 0 + gate 에서 해당 BC 잔존 0 |

(`bc_registry_run.py` 는 BC 하나만 담은 비-git 그림자 사본에 27종을 돌린다 — 이웃 위반
섞임·git 상태 의존이 없다. 도구 둘 다 2026-08-12 실측 검증됨.)

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

### ⑦ 삼분 처분 + 대장 기록
1. **문서/하네스 결함** → `spec.md`·이 프로토콜 보강(플러그인 평가와 무관). 스팩 등가가
   깨졌으면 보강한 문서로 같은 BC 재투입.
2. **플러그인 결함** → **먼저 fixture/matrix 케이스로 고정** → dddjango 수정 → 검증 8종
   (`make release` [2/7] 세트) 재실행 → 필요시 재배포 후 같은 BC 재라운드. 규칙 «값» 이
   바뀌면 eval v5 unfreeze/새 epoch 절차가 딸려온다.
3. **옛 코드 버그** (예: delivery 거짓 성공 — `FakeAlimtalkGateway`) → 사용자에게 보고,
   보존/수정 판정을 받는다.

라운드마다 §4 대장에 한 줄 기록.

## 3. 종료 조건

**연속 2개 BC 가 플러그인 무수정으로 ⑤ 3축 green + ⑥ 평가 둘(AI·사람) 통과**
→ 계획 5번(속도 개선)으로.

## 4. 라운드 대장

| 라운드 | BC | 앵커 | A shape | B 전역 | C 플러그인 | ⑥a AI | ⑥b 사람 | 발견·처분 | 플러그인 수정 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | child_settings | 1c02d89a | ⚠(자녀 경로 0 · 타 BC x-date 시간값 1건=하네스) | ✅ 7199 green | ❌ registry exit 2 + gate 잔존 3 | ✅ 접수(14a67001) — 테스트 ⓑ 0건·spec 충실·개선 3·처분 «통과+문서 보강+플러그인 후보» | 생략(사용자 08-12 — ⑤ 불통과 라운드라 불요·재라운드에서 수행) | ④ ad27fa3b(클린룸 준수·파이프라인 정상 가동 — 세션 감사) · **V1 트리 재생산**: houserules §1.1 예외 ⑵ 미적용+표준 트리를 dddart 것으로 오인, 백스톱은 BC 폴더 TARGET 호출로 조용 exit 0 → ⑦-⑵ 플러그인 결함 2건(P1 결정 순서 사각·P2 호출 계약 사각) + ⑦-⑴ 하네스 1건(shape 시간 의존 값) | **v2.1.0**(P1′ 답습 발본색원·P2 호출 계약·H1 shape 시간값 — dddjango 47fce0d·release 398707b·fixture 84/84) |
| 1′ | child_settings | 0ee0353f | ✅ diff 0 | ✅ 7193 green | ❌ registry 귀속 23건 (**gate 잔존 0 = V2 트리 달성** — P1′/P2 성공 자 충족) | ✅ v5 rubric 결과지 `workspace/eval/results/20260812-1747-csrebuildlive-claude.md` — 치명 1(SD-6)·정적 FAIL | 생략 가능 단서 해당(⑤ 불통과) — 사용자 판단 | ④ 6dedbfd0(클린룸 준수 — 감사: 금지 접근 0 · **registry 27종 루트 전수 실행 실측**·귀속 일부 자가 수정 후 잔존 23건을 «확립 규약 보존» 논리로 커밋) · 재라운드(플러그인 v2.1.0) — 클린룸 정화 1a248cdc(eval_ai·설계 명세·graphify stale 39 → 잔존 0) · **결함 축 이동**: V1 트리 재발 0, 대신 ⑴ 배선 답습(preserve 논리 월권 — api_router «parent_settings 동형»·#107-109/#431/#437) ⑵ SD-6 django.db 포트 우회(#2/#4 — port 칸 빈 채 우회) ⑶ 잎 import(#96·#326 — 단일 출처↔잎 규율 긴장) ⑷ 테스트 규율(#385·#387·#420) ⑸ 검사기 사각 2(#390=#385 그림자·#12 는 shadow 침묵) ⑹ 게이트 계약의 brownfield 귀속 공백 | **처분·수정 완료(08-12)**: 계획 v2(`2026-08-12-round1b-plugin-fixes.md`) — 적대 리뷰 4렌즈(판정 차분 재설계·two-pass·Call-흐름 신호·라이선스 전수) + D 결정(D1′=#96 오탐 정정+#326 파생 예외·D3=**code-json 이주**(spec 결함 발견 — spec 이 api.py 배선 지시)·D4=조사 종결) · 구현: registry_gate(차분)+checker_registry+검사기 3종+P1″ 산문 12곳+코퍼스 2곳 · 검증 전부 green(fixture 90/90·smoke 6/6·backstop 675 무변) · 라운드 2 준비 커밋 `0908671c`(spec 오류 절 재작성·pre_success·이관 빚 목록) · **v2.2.0 릴리즈 대기** |
| 2·claude | billing | 68ce0e51 | — | — | — | — | — | 준비 완료(08-12): 시드 재추첨 게이트 궤적 report→…→billing · D3 code-json 스팩(wire 11종 축자·admin 표면 포함·이관 빚 #12 accounts 인증 1건) · 2레인 신설(사용자 지시 「코덱스도」·「지난번과 다른 BC」 — child_settings 재라운드는 이월) · **앵커 baseline `make test` 6,883 green 실측**(billing 삭제 후·2:44) · pycache 잔존 정화(git rm 이 안 지우는 삭제-구현 바이트코드) · ⑤A 자 개정: `--success-only` 가 `x-problem-slugs` 도 걷음(billing 실측 — child_settings 판정 재료도 재생성·두 라운드 동일) | v2.2.0 |
| 2·codex | billing | 68ce0e51 (같은 앵커) | — | — | — | — | — | 워크트리 `broccoli-rebuild-codex`(브랜치 `rebuild/standard-tree-codex` — 앵커에서 분기) · codex 플러그인 2.2.0 확인(마켓 스냅숏 upgrade+add 실측) | v2.2.0 |
