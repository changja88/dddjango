# dddjango 2.41.0 — 내부 API 객체의 표준 자리 · scope 렌더 분석 불능 · 한계 둘

상태: 배포 끝(2026-11-19 07:26 · 태그 `dddjango--v2.41.0` · 고침 5ae11b77 · 시험 고침 897b80ba · release 63e40084 · 봉인 21402747 · 8297696e).

- 설계 정리본: `design.md`(확정 v1.3 · 현장 이름 걷음). 계획: `plan.md`(v1.2 — 계획 독립 검토 · 좁은 재확인 처분 반영).
- 구현 중 바뀐 것은 이 문서 «결정» · «독립 검토 반영» 이 정본이다. 규칙 글의 최종 문장은 렌더된 파일에 있다(`implementation-django-ninja` §2.3 «내부 창구» · §4.1 · §6.2 · `architecture-api` · `discipline-houserules` §1 트리 · architect · review-api slot 1 · 2 · 8 · coder · reviewer · acceptance-tester · 조정자).
- 노트: GitHub Release `dddjango--v2.41.0`.

## 현장 보고

- **F4-150**(수리됨): 한 BC 가 손님용 창구와 앞단이 인터넷에 열지 않는 창구를 함께 가질 때 둘째 API 객체를 둘 표준 자리가 없어, 레인이 #429 · #107 · #109 를 빚으로 넘기고 내부 scope 렌더는 «분석 불능» 으로 멈췄다.
- **F4-151**(한계 둘 닫힘): 내부 scope #15 `--anchor` 기존분 · preserve 기준선의 selector 재실행.
- **F4-186**(수리됨 · 배포 직전 장부 다시 읽기에서 붙음): 내부 scope 렌더 #5 · #16 이 `api.py` 에서 들여온 루트 클래스로 지은 `internal_api.py` 를 «분석 불능»(exit 1) — 이번 판 설계 D5 가 고치는 결함과 같다. 대상 저장소 사본에서 옛 판 exit 1 두 글(보고와 같음) → 새 판 분석됨.

## 결정

- **사용자**:
  - 내부 API 는 별도 API 객체 · 주소 뿌리 `/internal/` 을 표준 자리로(11-09 «나.»).
  - 내부 창구 인증 의무 줄을 두지 않음 — 일반 규칙만(11-18 Q1 «나.»).
  - 앞단 안쪽 사설망에서 부르는 내부 창구는 http 허용 한 줄(11-18 Q2 «가»).
  - 계획 v1.2 «승인»(11-18).
- **운영자 처리**(질문 생략 · 설계 처리 · 이의 시 뒤집음):
  1. 설계 D1 ~ D12(설계 정리본 §0) — 자리 · 이름(`internal_api` · `register_<bc>_internal_api`) · R-0717 경계(닫힌 이름 · #437 닫힌 허용 목록 · #107 두 이름 · #440 이름 ↔ 객체 ↔ 주소) · 빈 `internal_api.py` 고정 칸 · 기존 `/api/internal/…` 보존 · 오류 식별자 공유 한계.
  2. «BC 골격 171행» 은 그대로 — 2.38.0 운영자 처분(BC 골격의 뜻이라 BC 밖 칸에 행을 끼워도 바꾸지 않음)을 따름. 트리 다시 매김 중 «172» 로 고쳤던 것을 독립 검토(RT 사2)대로 되돌림.
  3. G12 분류: R-3768 · R-3769 · R-2567 N · R-1647 T*(풀리는 «새» 한정과 남는 «확립 인스턴스 보존 — R-0715 재진술» 이 섞임).
  4. 받아들인 한계로 둔 검토 지적: IC S3(#437 파일 단위 overlap) · S5(공개 #5 CPU +0.8 초) · IC 재확인 사1(`urlpatterns` 통째 감싸기) · 사2(중간 목록 · `insert` · 키워드 `path` 의 #440) · IT 재확인 새3(R-3776 · R-3779 N 행 불요).
  5. construct_drift 보고서 md(`workspace/eval/ab/T2-construct-drift.md`)는 08-20 뒤 다시 만들지 않는 선례대로 둠(EXPECTED_SHA 두 줄만 갱신).
- 판 번호 **2.41.0**(minor) — 새 표준 자리 · 새 규범 열여섯 · 트리 행 · 검사기 판정 변경. dddjango-web 은 바뀌지 않는다.

## 사용자에게 보이는 흐름(전 → 후)

| 보고 | 2.40.0 | 2.41.0 |
|---|---|---|
| F4-150 | 내부 창구 둘째 API 객체의 표준 자리 없음 · `internal_api.py` 가 #429 · 공개 registrar 모듈의 둘째 등록 함수가 #107 · #109 | `<project>/internal_api.py`(트리 168행 · 없으면 빈 파일) · `register_<bc>_internal_api` · `path("internal/", internal_api.urls)` 가 표준 · 셋째 객체 · 별칭 · 공개 객체의 `internal/` mount · include · 변수 경유 mount 는 막힘 |
| F4-186 | 내부 scope #5 · #16 «분석 불능» exit 1(빚 불가) | 분석됨 |
| F4-151 | 내부 #15 `--anchor` 가 기존분을 신규로 · preserve 기준선이 positional 강등 | 기존분 · selector 재실행 |
| (새) | — | 처음 내부 창구를 여는 레인의 #16 `--anchor` 가 빈 `internal_api.py` 앵커에서도 selector 기준선 |

## 독립 검토 반영

| 검토 | 결과 | 처분 |
|---|---|---|
| 설계 T(글 · 그래프 · 트리 · 파이프라인) | 차단 0 · 중요 10 · 사소 7 → 좁은 재확인 둘 | 모두 받음 · 설계 v1.3 확정 |
| 설계 C(검사기 적대) | 차단 1 · 중요 4 · 사소 6 → 좁은 재확인 둘(v1.2 새 중요 3 포함) | 모두 받음 · 설계 v1.3 확정 |
| 계획 P | 차단 1 · 중요 8 · 사소 6 → 좁은 재확인 | 모두 받음 · 계획 v1.2 |
| 구현 IT(글) | 차단 0 · 중요 4 · 사소 8 → 좁은 재확인(새 사소 5) | 받음(새3 하나 안 받음) — D12 Literal 대상 · slot 1 의 `/api/internal/…` 보존 · README 셋째 객체 · master file_tree 글 |
| 구현 IC(코드) | 차단 1 · 중요 3 · 사소 5 → 좁은 재확인(새 사소 3) | 받음(S3 · S5 · 재확인 사1 · 사2 는 한계) — 빈 `internal_api.py` 앵커 기준선 · include · 변수 경유 mount · 보존 폴더 #440 오탐 · 시험 빈칸 |
| 트리 다시 매김 RT | 차단 0 · 중요 0 · 사소 4 | 모두 받음 — profile 낱말 · «BC 골격 171» 되돌림 · DEVELOPMENT 트리 개정 순서 행 수 인용 · spec #440 축자 |

차단 · 중요는 모두 고친 뒤 좁은 재확인 첫째(설계는 둘째)에서 닫혔다.

## 검사 수치(마지막 실행)

- 897b80ba 뒤 push 전: `make verify` 6/6(1304초) · `make verify-mutation` exit 0(변이 12 · 83 · fixture_matrix 208 · registry_gate 11 + 기준선 · 귀속 50 · pre-gate 21 · behavior_guard 9 · refactor_audit 61 전부 red).
- 검사기 행렬 989(928 + 61) · `fixture_matrix` 172 · 기준선 시험 150 · 귀속 시험 97(표 45/45) · 현장 보고 시험 184 · pre-gate 89 · 69 · 탐침 644/644 · `test_watch` 73.
- 골든: findings_count 두 행 메시지 지문 칸만 · construct_drift 두 줄 · checker_cross #488 +1 여섯 · checker_baseline 73 무변 · `pregate_symbol_kinds.json` 재소성(종류 56).
- 첫 `make verify`(5ae11b77 뒤)는 배포판 출력 byte 대조 시험 하나가 #16 안내 줄 고침에 붉었다 → 안내 줄만 가리는 시험 고침(897b80ba) 뒤 처음부터 다시 돌았다.
- 깨끗한 클론의 `make release` 안 verify: 첫 시도는 탐침 644 칸 가운데 한 칸(xdist 일꾼 출력 하나 빠짐 · 기계 부하 · 탐침 엔진 무변)이 붉어 배포 커밋 없이 멈춤 → 그 사례만 세 번 다시 돌려 세 번 맞음 → 다시 돈 release 안 verify 6/6(2035초).

## 받아들인 한계

설계 정리본 §6 + 노트 «받아들인 한계»(같은 목록) — 앞단 차단은 기계 밖 · 인증 의무 없음 · 기존 `/api/internal/…` 빚 아님 · 오류 식별자 공유 · `urlpatterns` 통째 감싸기 · 공개 `.urls` 변수 경유 · #437 파일 단위 overlap · V3 재대입 렌더 exit 1 · 비표준 루트 API #63 되풀이 · pre-gate 빈칸 · 진행 레인 명세의 «트리 N행» 낡음 · 채택 프로젝트마다 `internal_api.py` 없음 #488 옛 빚 한 줄.

## 교훈

1. 검사기 메시지를 고치면 «배포판과 byte 같음» 시험(anchor_diff_smoke 의 배포판 대조)이 글자 grep 없이 걸린다 — 메시지를 고친 회차는 anchor_diff_smoke 를 돈다.
2. 골든 스플라이스는 그 사전 블록 안으로 범위를 묶는다 — 같은 키 꼴의 다른 사전(봉인 커밋 표)을 덮을 수 있다.
3. 행 수 인용은 «트리 N행» 꼴만이 아니다(«표준 N행 템플릿» · «standard_tree N행 골격» · 생성기 안내 줄) — DEVELOPMENT §3 트리 개정 순서에 넣음.
4. 앞 판 처분이 있는 글자(«BC 골격 171행»)는 고치기 전에 그 처분부터 찾는다.
5. 배포 직전 장부 다시 읽기가 이번 판이 고치는 결함의 새 보고(F4-186)를 잡았다 — 판에 넣고 사본으로 재현해 닫는다.

## 다음 판

- 제안: F4-185(리팩토링 입구가 비동기 시험을 지원 밖으로 빼 G0 정지 · 높음) + 작은 넷(F4-181 · 182 · 183 · 184) — 재현부터.
