# dddjango 2.19.2 — 서버 게이트가 자매 플러그인(dddjango-web) 영역의 정상 지적을 «보고만»으로 가른다 (운영자 · 10-09)

## 바탕
- 바탕: R main `793449dd`(dddjango 2.19.1 + dddjango-web 2.2.2) → web 2.2.3 배포(`f8ad8152`) 위로 옮겨 착지. 패치(검사기 27종 · 로스터 · 트리 그대로).
- 사본 `<S>/core-2192`(가지 `core-2192`). `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`. 근거 기록 `<S>/core-2192-notes/` · 재현 `<S>/core-g51/`.
- 현장 보고(10-09 · spring_dream 서버 레인 admin-5-1): S5 뒤 main 을 합치자 web 레인(6-3-25)이 들인 web BC(`web/application/showcase` · `web_test/…` · `web/static/application/…`)를 서버 검사기가 서버 BC 로 재어, registry_gate 귀속 248(전부 web · 폴더 · 없는 파일 꼴 — 승인 유입으로 증명 불가)로 G2 앞에서 멈췄다. 운영자 재현에서 범위 렌더 검사기 #6(`check-context-isolation --anchor`)의 앵커 차분 신규분 7(전부 web)도 G2 차단이었다.
- 사용자 결정(10-09 · 글자 그대로):
  - «web을 사용하고 있는 프로젝트에서 들어온 오류 보고야. 실제 문제인지 확인해줘» → 배포판 도구로 재현 · 실제 문제.
  - «가.»(18:44:23 date 뒤 · 18:46:00 date 앞) = **결정 5 — 서버 검사기가 web 폴더를 빼도록 고쳐 이 수리만 담은 2.19.2 로 먼저 낸다**(배포는 검증 뒤 다시 승인 물음).

## 판정 — 뿌리
- 서버 검사기 다수가 BC 를 `rglob("application")`(어느 깊이든)으로 찾고 전역 인벤토리 · 어휘도 저장소 전체를 본다 → 자매 플러그인이 소유한 루트 `web/` · `web_test/` · `.dddjango-web/` 를 서버 BC · 서버 코드로 잰다. 두 플러그인이 같은 폴더에 반대를 요구(web 표준 `infra_layer` ↔ 서버 #324). 평소엔 «옛 빚»으로 세여 조용하다가 main 을 합쳐 새 web BC 가 들어오면 귀속이 된다.
- 폴더 · 없는 파일 꼴 지적을 승인 유입으로 증명하지 않고 귀속으로 남기는 것(registry_gate 비-blob)은 설계대로 — 바꾸지 않는다.

## 길 — 셋째 안
- r1(검사기 25곳이 대상에서 web 을 늘 뺌): 설계 점검 반려 — 이름만으로 늘 빼면 dddjango-web 을 안 쓰는 프로젝트의 서버 코드까지 숨김 · BC 목록에서 web 을 지우면 서버 파일이 web 을 import 하는 위반까지 사라짐.
- r2(검사기는 그대로 · 멈춤 판정 두 곳에서만 가름): 점검 «보완한 r2 권고» → 보완(소유 판정 · 측정 실패 우선 · 주어 칸만 · pre-gate 전달) 뒤 구현.

## 넣은 것
- `registry_gate.py` 귀속 분할 · `anchor_diff.partition_exit`(범위 렌더 #2 · #5 · #6 · #15 · #16): 소유가 확인된 저장소(루트 `.dddjango-web/` 실제 폴더 · `manage.py` 의 `DJANGO_SETTINGS_MODULE` 설정이 정확히 하나의 리터럴 · 그 프로젝트 패키지 실제 경로가 세 뿌리와 안 겹침 — 불명확하면 가르지 않음)에서 루트 직계 `web/` · `web_test/` · `.dddjango-web/` 를 **주어로 한 정상 측정 지적**을 `== 자매 플러그인 영역(dddjango-web 소유 — 서버 판정 밖 · 보고만) n건 ==` 절로 옮기고 exit · `introduced.json` · `contract.json` 에서 뺀다(지우지 않음).
- 측정 실패가 먼저(비정상 exit · 미파싱 합성 · 기준선 불능 · 승인 유입 측정 무효 · `[분석]` 표지 · 레코드 채널 실패 → 그대로 귀속). 판정 순서 빚 → 승인 유입 → 자매 → 남은 귀속.
- `design_pregate.py`: 사본에서도 원 저장소 판정이 닿게 `DJR_SISTER_SOURCE_ROOT`.
- 새 규범 R-3617(Obligation · `command-dddjango` `s007/b60` · revision 2) · ISSUED · 배선 · 재투영(Coordinator 두 벌) · rulepack · LEDGER · 쿼리 골든 · 계층 계수 · 봉인.
- 바꾸지 않음: 검사기 27종 · BC 목록 · 어휘 · 인벤토리 · 로스터 · #74 · 비-blob 귀속 · 직접 실행 exit 1 · `--anchor` 없는 scope exit 2 · behavior_guard · pre-gate 최신성.

## 멈출 기준과 결과
| 기준 | 결과 |
|---|---|
| 실제 레인(admin-5-1 병합 `5717541c2` + 레인 미커밋 97파일 고정본 · 같은 입력 수리 전후) — registry_gate | 귀속 248 → **0** · exit 2 → 0 · 승인 유입 136 그대로 · 자매 절 248 · legacy 1,837 · ⓓ 131 그대로 |
| 레인 G2 명령 27종 | #6 exit 2 → **0**(신규분 7 → 0) · 나머지 26종 그대로 · 27종 모두 병합 앞 레인 기록과 같은 exit |
| 서버 쪽 출력 | web 줄을 빼면 수리 전후 글자까지 같음(서버 진단 973줄 · 범위 렌더 서버 줄 22) |
| 서버 판정 골든 | checker_baseline · findings_count 73/73 그대로 |
| 시험 | registry_gate_smoke 24 + 42 · anchor_diff_smoke 10 + 14 · 온톨로지 게이트 · 렌더 동기 · rulepack · 변이 · 쿼리 골든 |
| `make verify` · `make verify-mutation` | 5/5 green · 변이 12종 전건 red 검출(사본 · 커밋 · 봉인 뒤 · 10-09 21:34 ~ 21:40) |

## 알려진 한계
- 검사기를 직접 돌린 원 출력에는 web 지적이 «옛 빚»으로 계속 보인다(멈춤엔 안 쓰임).
- web 어휘가 서버 판정에 섞여 서버 경로에 나는 오탐(broker #518 류)은 이 판에서 안 고친다(관찰된 적 없음 — 나면 멈춤).
- 검사기 쪽 정리(주어 · 의존 분리 — r1 의 큰 정리)는 별도 범위 결정으로 남김.
- 작업 도중 판을 올리면 `dddjango/scripts/` digest 가 바뀌어 진행 레인은 pre-gate 재예보(G1 ~ G2 레인은 Phase 2 재발화)가 든다(`docs/DEVELOPMENT.md` §6). 레인이 명령에 박아 둔 `…/2.19.1/scripts/…` 경로를 그대로 쓰면 새 판이 적용되지 않는다.
- 미배포 2.20.0 패치는 다시 얹을 때 R-3617 ~ R-3651 을 한 칸 밀고(R-3618 ~ R-3652) `command-dddjango.ttl` Block 순서값 +1 을 보존한다. 새 전역 탐색(#653)은 이 가름과 별개.
