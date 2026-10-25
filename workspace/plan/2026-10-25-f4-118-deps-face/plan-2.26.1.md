# dddjango 2.26.1 — deps 레인 겹침을 «실제로 만나는 자리»로 좁힘(F4-118) (10-25)

## 바탕
- 바탕: main `b1211309`(dddjango 2.26.0 · dddjango-web 2.8.1 봉인 뒤). 2.26.1 은 patch — deps 판정의 거짓 겹침 고침 + 규범 신설 1 · 개정 2(새 질문 · 새 흐름 · 새 기록 칸 없음 — 선례 2.24.1). 매니페스트 판은 `make release` 가 올린다. dddjango-web 무변.
- 결함(장부 F4-118): 2.26.0 `deps` 는 «대상 BC 의 이웃 BC 전부»를 BC 단위로 세서, 대상이 쓰기만 하는 공급 BC 의 다른 파일만 고치는 기능 실행도 «BC <공급 BC>» 겹침(exit 2)으로 리팩토링 레인을 막았다. web 실행은 `web/<첫 칸>` 단위(`web/application`)라 대상 API 를 소비하지 않는 web 단위만 고쳐도 파견 직전 밖 동작 V ≥ 1 이면 겹쳤다.
- 설계: 1판 → 적대 검토(차단 2 · 중요 5 · 사소 6) → 2판(운영자 결정 D1 = 나 · D2 = 뺀다) → 좁은 확인(차단 N1 · 사소 5) → 구현(2판 + N1 + 사소).

## 설계 요지

### 집합
- `consumers` = 대상 T 를 가리키는 BC(운영 · 시험 · 마이그레이션 간선) ∪ T API 를 HTTP 로 부르는 BC · `supplier_only` = T 가 가리키는 BC − `consumers` − {T}.
- BC 로 세는 집합 = {T} ∪ `consumers`(받는 쪽 · HTTP 소비 BC) · 상대가 리팩토링 실행이면 공급 BC 도 BC 로 센다(엮인 BC 는 동시에 돌리지 않는다).

### 공급 면(공급 BC 마다)
1. 그 BC 의 창구 · 창구 계약 · 발행 이벤트 자리 파일 전부(리팩토링이 다른 창구로 옮겨 탈 수 있다).
2. 대상 파일(운영 · 시험 · 마이그레이션)이 import · 문자열 · 모델 라벨로 가리키는 그 BC 파일 — import 경로는 긴 쪽부터 실재 파일 · 폴더(같은 이름의 `x.py` 와 `x/` 가 함께 있으면 둘 다) · 합성 경로(모델 라벨 · `get_model` · AUTH_USER_MODEL · 마이그레이션 의존)는 정확히 있을 때만 그 자리, 아니면 그 label 을 선언한 `apps.py` 폴더의 `models` · `migrations/<이름>`, 그것도 없으면 그 BC 전체. 마이그레이션 의존은 이름까지(새 마이그레이션 더하기는 안 만남).
3. 이름 사슬: 대상이 이름으로 들인 것은 그 이름을 정의한 모듈까지 — 최상위 정의(class · def · 상수 대입)가 없으면 그 이름을 들인 import(블록 안 · 별칭 · `*` 포함)를, 그것도 없으면(대입 다시 내보내기 `X = impl.X` 등) 그 모듈의 같은 BC import 를 모두 따라간다(합성 루트 제외). import 만으로 된 파일(파사드)은 그 import 를 모두 따라간다.
4. 대상 **운영** 코드의 HTTP 호출(문서 문자열 밖 문자열 상수) → 맞은 접두를 선언한 파일 + 그 폴더 + `driving_layer/api/`. 대상 **시험**의 준비용 HTTP 호출은 면 밖(D2).
5. 그 BC 전체(출력 `면 넓힘:` 줄 · deps.json `face_widened`): 그 BC 자신의 HTTP 표면 관찰 못 함 사유 · 그 BC 의 읽거나 파싱 못 한 파일(대상 파일이면 모든 공급 BC) · 따라가야 할 면 파일을 못 읽음 · 이름 사슬 상한(`FACE_CHAIN_CAP` 2000 걸음)에 닿음. 저장소 다른 곳의 못 읽은 소비 파일 하나는 공급 면을 넓히지 않는다.

### 고침 목록 신뢰(B1 · N1)
- 공급 BC 만 가리키는 dddjango 기능 · 수정 실행의 명세 file-plan 은 ⓐ 실행 줄에 `build_anchor` ⓑ 그 실행 `pregate-report.md` 의 마지막 실행 경계 행(머리 `- 실행 경계 —` — `design_pregate.py --check-report` 와 같은 머리 · 값 = 머리 뒤 첫 토큰이 그 실행 G0 승인 값) 뒤에 `## pre-gate 예보 — <UTC> · ` 절이 있을 때만 고침 목록이다. 경계 행이 없으면 `- pre-gate 기준선 —` 행이 하나 이하일 때만 처음부터 찾는다. 값을 못 읽거나 다르거나 기준선 행이 둘 이상이거나 그 파일을 UTF-8 로 못 읽으면 «고침 목록 모름»(해독 보류를 새로 만들지 않는다).
- `pregate-report.md` 를 실행 기록(`RUN_RECORDS`)에 더함 — 다른 작업 트리 사본 가르기(자기 변경 · MH 판)가 이 파일도 같은 판으로 읽는다.
- 덧씌움(그 트리 미착륙 커밋 경로) · web slices · web 명세 file-plan 은 언제나 고침 목록. 경로 · BC 겹침은 지금처럼 넓게(못 믿는 file-plan 포함).

### 판정
- 까닭: BC · **공급 면 <파일>**(믿는 고침 목록 ∩ 공급 면) · 경로 · web 단위 · 계획된 소비. 공급 면은 HTTP 까닭이 아니어서 예보 · 뺌 대상이 아니다.
- 공급 BC 기능 실행 · 고침 목록 모름(D1 = 나): G0 은 `예보 보류:`(exit 무변 · 밖 동작 V 무관) · 파견 직전은 보류(exit 2 → 파견 정지 · 재개 조건 `그 레인이 이번 실행 명세로 첫 파견(G1 승인 뒤)하거나 G2 로 끝난 뒤 다시 시작`).
- 면 밖 공급 실행은 `뺌:` 줄(서는 장치 = 그 실행의 G2 전체 suite 가 지금 대상 시험을 돈다 · 두 레인 조합은 착륙 뒤 처음 돈다).
- 출력: deps.json `supplier_faces` · `forecast_supplier` · `face_free` · `face_widened` · `our_bcs`(BC 로 세는 집합) · deps.md 머리 `- 공급 면(…)` · `요약:` 의 `공급 면 n BC · m 자리 · 면 밖 뺌 k` 와 G0 판정 시점 꼬리 끝 `예보 보류 가운데 공급 BC 고침 목록 모름 h`(기존 «판정 시점 G0 · 예보 보류 f · 예보 겹침 g» 글자 그대로).

### web 단위
- dddjango-web `unit_of` · `areas_of` 와 같은 규칙: `web/application/[<area>/]<bc>` · BC 미러 CSS(`web/static/application/…`)는 그 BC · `web/static/root/` → `web/root` · `web/static/<칸>` · `web/<칸>` · 외부 JS 사본(`web/static/vendor/`) · web 바로 밑 파일은 단위 없음. HTTP 소비 주인(`our_units` · deps.md «HTTP 소비»)과 web 실행 단위 둘 다.
- 단위 밖 web 파일만 고치는 web 실행은 «web 단위를 모른다» 보류가 아니다(web 파일이 하나도 없을 때만 보류).

## 규범(그래프 정본 `ontology/rules/command-dddjango.ttl` → 재투영 `dddjango/commands/dddjango.md` · Codex 짝 손 미러)
| 규범 | 바뀐 것 |
|---|---|
| **R-3687 신설** | deps 레인 겹침 단위 — BC · 우리 경로 · 공급 면(정의 · 면 넓힘) · web 단위 · 계획된 소비 · 공급 BC 기능 실행 고침 목록 신뢰 조건(경계 머리 · 첫 토큰 · 기준선 행 하나 이하) · 모르면 G0 예보 보류 · 파견 직전 보류 · 면 밖 뺌 줄 · 공급 BC 의 `예보 보류:` · `뺌:` 줄은 web HTTP 소비 줄이 아님(G1 ② 대가 줄 R-3639 대상 밖 — R-3639 글 무변). 블록 `s012/b1`(deps 문단 · `exit 2(…)` 문장 앞) · 배선 Coordinator 위임 + `refactor_audit.py` 집행 · ISSUED. |
| R-3672 rev2(amendment) | G0 예보에 «공급 BC 를 고치는 기능 실행의 고침 목록 모름 보류» · G0 정지 셈 = web HTTP 소비로만 선 예보(예보 겹침 + 예보 보류 − `요약:` 의 h)가 있고 «밖 b» ≥ 1 · 공급 BC 고침 목록 모름 예보는 «밖 b» 와 무관하게 정지하지 않는다. |
| R-3527 rev5(amendment) | G0 배너 ⑤ `… · 예보 겹침 g · 예보 보류 f(공급 BC 고침 목록 모름 h) · 공급 면 밖 뺌 k` · 출처 = deps `요약:` 의 같은 수. |
- 개정 없음: R-3625 · R-3673 · R-3674 · R-3675 · R-3676 · R-3482 · R-3494 · R-3626 · R-3627 · R-3639.
- 딸린 것: LEDGER `command-dddjango s012` 재기준선 1 행 · 계층 계수(Norm · Work +1 · Expression +3) · q4 골든 · `make rulepack`(양 런타임 byte 같음) · Codex `codex-dddjango/skills/dddjango/SKILL.md` deps 문단 · G0 배너 문단(렌더본과 문단 글자 같음) · `refactor_audit.py` Codex byte 미러.

## 받아들인 한계(설계 2판 §8 요약)
1. 창구 뒤 동작 변경: 창구 · 계약 · 이벤트 파일과 대상이 가리키는 파일을 안 고치고 그 BC 안쪽만 바꿔 결과가 달라지면 안 센다 — 서는 장치는 그 실행의 G2 전체 suite 하나 · 조합은 착륙 뒤 처음 돈다 · 안 센 실행은 `뺌:` 줄 · 배너 ⑤ «공급 면 밖 뺌 k».
2. D2 가 남기는 셋: 그 붉음을 `## G2 전체 확인` 목록으로 받을 수 있음 · 공급 실행이 G1′ 로 대상 시험을 고쳐 풀면 리팩토링은 다시 안 봄(착륙 때 글자 충돌) · 리팩토링이 공급 착륙 뒤 main 을 받으면 0T 규칙상 멈출 수 있음(운영 정지).
3. 출발 뒤 바뀌는 상대 고침 목록은 G0 · 첫 파견 · (조건부) G1′ 뒤에만 본다.
4. 명세 밖 미커밋 편집은 못 본다(커밋되면 덧씌움이 잡는다).
5. 초안 file-plan 이 면과 만나도 G0 은 예보(예보 줄 꼬리 «면 파일 n 과 만남»).
6. 이번 실행 명세 판별은 «명세를 바꾸면 pre-gate 를 다시 돈다» 규칙에 기댄다(블록 해시 대조는 pre-gate 실행기를 불러야 해 뺐다).
7. 그대로 둔 넓은 자리: 받는 쪽 BC 실행 · 공급 BC 의 이웃 BC 기능 실행이 G1 전이면 보류 · 옛 꼴 리팩토링 실행.
8. web 단위 규칙 두 벌(core · web) — 사례 W0 이 대조.
9. `apps.py` label 없음 · 하위 폴더 프로젝트 루트의 덧씌움 경로(2.26.0 과 같음).
10. HTTP 표면 관찰 못 함 공급 BC 는 그 BC 전체.
11. **창구 전부의 대가**: 공급 실행이 창구 파일에 함수만 더해도 겹친다(현장 대조 세 실행 만남 0).
12. 대상 BC 안 파일을 못 읽으면 대상이 가리키는 곳을 몰라 모든 공급 BC 가 그 BC 전체 면이다(안전 쪽).

## 시험(`workspace/tools/refactor_audit_fixture_run.py` — `deps_face_cases` · `deps_trust_cases` · `deps_web_unit_cases` · 접두 `RD-F118`)
- 공급 면: C1 · C1t · C1d · F1 · F1b · F2 · F3 · F4 · F7 · F8 · C2t · Y1 · Y2 · C2bt · 이름 사슬 상한 세 칸(S-cap · S-cap2 · S-cap3 — 상한은 도구 안 함수로 바꿔 잼) · C3t · C3m · C3n · F11 · F11b · F12 · F12b · F13 · F15 · F5 · S5 · S5b · C4t · F14 · F14b · F14c · C4b · 못 읽은 파일 U1 ~ U4.
- 고침 목록 신뢰: B1a · B1a2(요약 h) · B1b · B1e · B2a · B1u(UTF-8 아닌 pregate-report) · C5 · C5gd · C5ok · C5mm · N1 X1 · X2 · X2b · X2ok · X3 · X4 · C5g · B1c2 · 덧씌움 F9 · F10 · 사본 가르기 F16a · F16b · F16c.
- web 단위: W0(core = dddjango-web 규칙 · 경로 22) · W1 ~ W5 · C6 · C6d.
- 새 사례 70(기대 칸 수 — 공급 면 38 · 고침 목록 신뢰 23 · web 단위 9) · 기존 deps 사례 8 묶음 기대 글자 무변(RD-E1b 포함). 붉음 확인: 2.26.0 도구로 새 사례 66 붉음(남은 넷은 무변 갈래 F8 · C6 · C6d 와 2.26.0 에 없는 칸을 보는 U2) · 설계 2판 시제품으로 N1(X1 · X2 · X2b · X3 · X4 · C5mm) · Y1 · Y2 · 상한 · B1u 붉음.
- 현장 다시 보기(읽기만): 공급 BC 15 의 면 수 2판 시제품과 같음 · 면 넓힘 0 · 세 실행 만남 0 · 소비 단위 겹침 0 · 면 계산 0.2 초.

## 진행 중 레인
- `dddjango/scripts/` 가 바뀌어 pre-gate 실행 트리 digest 가 바뀐다 → 진행 중 dddjango 레인은 재예보(배포 보고에 적음).
