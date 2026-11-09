# dddjango 2.33.0 — 현장 보고 수리 10건

상태: 배포 끝(2026-11-09 15:03 · 태그 `dddjango--v2.33.0` · 커밋 8d08bbf2 · release a4f005ec · 봉인 a2a638ca). 계획 전문(항목마다 고친 자리 · 파일 · 일하는 법)은 `plan.md`, 규칙 글의 최종 문장은 렌더된 `dddjango/agents/design-architect.md` · `dddjango/agents/acceptance-tester.md` · `dddjango/commands/dddjango.md` · `dddjango/skills/implementation-django-ninja/references/final.md`.

## 범위

장부의 열린 항목 12건을 배포판 2.32.0(태그 `dddjango--v2.32.0` · f0bbe3a7)으로 재현했다(재현 10 · 일부 2). 이 판은 10건과 같은 결함으로 함께 닫히는 F4-140 · F4-144 를 고친다.

| 묶음 | 항목 | 고친 것 |
|---|---|---|
| 검사기 오탐 | F4-147(+F4-144) | BC 열거에서 `__pycache__` 를 거름(#488) |
| | F4-151 | 앵커에 없는 새 `--api-module` scope 의 옛 위반을 앵커 기존분으로(#2 · #5 · #15 · #16) |
| | F4-152(+F4-140) | 받는 쪽이 내장 타입으로 정해진 메서드 호출 · 묶지 않은 내장 이름을 업무 어휘에서 뺌(#562 · 판정 못 하면 옛 판처럼 다 셈) |
| | F4-153 | 포트 선언을 framework 전체(test 밖)에서 찾음(#623) |
| 예보기 | F4-48 | 저장소 채널이 #287 · #599 를 싣고 인자가 바뀐 기존 메서드도 투영 |
| | F4-155 | 조립 파일 update 칸 선언 예보(#85 · G2 와 같은 줄 키) |
| 규칙 글 | F4-146 · F4-148 · F4-149 · F4-154 | 재료 함수 조건 · arrange 셸 꼴 · 입장 표 인수 행 · 스킬 예시 차례 — 검사기 · 같은 절 산문과 맞춤 |
| | F4-48 · F4-155 글 | 넓어진 예보 범위를 architect 의무 · 조정자 S5 에 맞춤 |

## 결정

- 사용자 결정(2026-11-09 «가.»): 되돌아감 줄이기를 끝낸 뒤 현장 결함 수리 판으로 간다.
- 사용자 결정(2026-11-09 «나.»): F4-150 은 별도 API 객체 · 주소 뿌리(`/internal/`)를 표준 자리로 여는 쪽 — 이 판 뒤 따로 큰 판.
- 사용자 «진행»(2026-11-09 12:44): 계획 v2(계획 독립 검토 1 반영) 승인.
- 운영자 처분(질문 생략 · 설계 처리 · 이의 시 뒤집음): F4-156 은 결함이 아니라 속도 개선이라 뺐다(`plan.md` «뺀 것»).

## F4-150 재현 요지 (다음 큰 판의 출발점)

장난감 셋 — BC 하나가 공개 controller 와 내부 controller 를 하나씩 둔다. 공개 API 객체는 `/api/`, 내부 API 객체는 `/internal/` 에 붙인다. 배포판 2.32.0 의 결과:

| 꼴 | 조립 | 검사 결과 |
|---|---|---|
| API 객체 하나(비교 기준) | `config/api.py` 하나 · registrar 하나 | `check-composition-root` 트리 모드 exit 0 |
| API 객체 둘 · 파일 둘 | `config/api.py` · `config/internal_api.py` · BC registrar 에 `register_<bc>_api` 와 `register_<bc>_internal_api` | 트리 모드 #107(등록 함수 «하나»만) · code-json 공개 scope #107 · #109(정본 registrar 밖 등록) · 내부 scope 사용 오류 exit 1(API 객체 대응 분석 불능) |
| API 객체 둘 · 파일 하나 | `config/api.py` 에 둘 | 트리 모드 #107 · code-json 공개 scope 사용 오류 exit 1(생성 · 묶음이 각각 둘) |

뜻: 표준 트리에는 둘째 API 객체의 자리가 없어서, 두 객체를 두면 검사기가 막거나 분석을 포기한다. 큰 판에서 정할 것은 두 번째 API 객체의 파일 자리 · BC registrar 의 함수 이름과 수 · URLconf 결선 · code-json scope 가 객체마다 도는 법이다. 이번 판의 F4-151 옆자리 한계 둘(아래)도 그때 함께 본다.

## 한계

- F4-151: 새 api 모듈이 들이는 같은 패키지 도움 모듈의 옛 위반은 #15 에서 여전히 신규로 찍힌다 · #16 preserve 프로필에서는 urlconf 완화가 짝 검사에 막힌다 — F4-150 큰 판에서 함께 본다 · 그 사이는 이관 빚.
- F4-152: 계획 어림 20 ~ 30줄이 약 300줄이 됐다(다른 파일의 재귀 `type` 별칭과 `.items()` 에서 꺼낸 원소 타입까지 따라가야 현장 꼴이 닫힘). 새로 놓치는 자리는 내장 메서드 · 이름 목록에 든 낱말을 업무 낱말로 쓰는 코드와 주석이 실제 타입과 다른 코드뿐. 다음에 같은 오탐이 다른 꼴로 오면 이 장치를 넓히지 말고 빚으로 받을지 먼저 묻는다.
- F4-146 은 글만 맞췄다(update 재료 파일의 예보기 보강은 하지 않음). F4-148 은 강제 장치 없이 글만(쓰기 0 · 판정 바뀜 0 이 세 번 확인됨 · 소음만 줄임).

## 독립 검토 반영

- 계획 독립 검토 1: 차단 1 · 중요 9 — 차단은 F4-156 의 skip 열쇠(기준선 SHA · 작업 트리 · 유입 · 빚 목록 칸이 예보 출력에 없음)였고 F4-156 을 판에서 빼는 것으로 닫았다. 중요 9 는 계획 v2 에 반영.
- 구현 독립 검토 1: 차단 0 · 중요 0 · 사소 9 — 모두 받음. 그 가운데 F4-152 가 `Optional[()]` · 아주 긴 `+` 식에서 traceback 으로 죽던 꼴을 운영자가 재현했고(옛 판 exit 2 · 새 판 exit 1), 그 파일은 옛 판처럼 다 세는 가드를 넣었다.

## 검증

- 시험: 항목마다 픽스처 · 스모크 줄(옛 판 붉음 → 새 판 녹색) — fixture_matrix 줄 대조 2 · 변이 3 · anchor_diff_smoke(F4-151) · pregate_field_report_smoke 2 · field_report_checker_smoke(배포 스킬 예시를 #15 에 돌림).
- 커밋 뒤 push 전 `make verify` 6/6(1447초) · `make verify-mutation` exit 0(변이 12 · 74 · 줄 대조 54 · registry_gate 11 · pre-gate 4 · behavior_guard 9 · refactor_audit 5 전부 red 확인).
- 깨끗한 클론의 `make release` 안 `make verify` 6/6(1508초) · 봉인 `--check --draft` green.
- 장부: 계획 확정 때와 배포 직전 모두 마지막 F4-156 · 새 항목 없음 · 배포 뒤 12건에 처분 줄.
- 요청 가이드 · README · `docs/`: 바뀔 것 없음(사용자가 요청에 쓰는 칸 · 물음이 그대로이고, 문서가 이번에 바뀐 검사 · 예보 동작을 싣지 않는다).
- 레인 영향: `dddjango/scripts/` 가 바뀌어 진행 중인 실행의 pre-gate 예보는 툴체인 stale — 다시 예보해야 한다.

## 다음 판 후보

- F4-150 별도 API scope 정식 자리(위 재현 요지).
- #604: framework 에 `*_port.py` 가 0 개면 저장소 전체 diff 를 읽어 거짓 blocker(2줄 고침 후보).
- #518(check-broker-contract)도 내장 이름(`object` · `any`)을 업무 낱말로 셈.
