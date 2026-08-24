# 검사기 측정 결함 수리 v2.17.4 — kkebi 실물 인수 기록 (계획 §2 런북 완주)

- 실행: 2026-08-25 · 준거: `workspace/plan/2026-08-25-checker-measurement-fixes-plan.md` v2 §2.
- **판정: 인수 ⓐ~ⓖ 전건 충족 — 허용 밖 diff 0.**

## 재료

- 동결 사본: kkebi 3워크트리(billing·saju·tarot — `.git`/`.dddjango`/`__pycache__` 제외 rsync)
  · py 전수 manifest `8cf5b22979107c67e2e1ea92d197419d5f3c3e098e10f95466b6680dc5cf7acc`.
- 전(before) = git HEAD 검사기(= 릴리즈 v2.17.3 byte 동일) · 후(after) = 본 수리 작업본.
- 매트릭스: 27종 × 3사본 × 전/후 = **162런**, `DJR_FINDINGS_JSON` 레코드 + stdout + stderr + exit 수집
  (무anchor 전량 렌더·비-git 결정 모드 양측 동일). 원자료 `~/.claude/jobs/48c8a476/tmp/accept-*`.

## 최종 diff 25건 — 전수 분류

| 부류 | 건수 | 내용 |
|---|---|---|
| ⓐ 표적 소멸 | **17** | billing 15(#545×7·#365×3·#555·#197 import·#543·#33·#562) + saju #545×2 — R1 대차 그대로 |
| ⓕ 동류 정당 소멸 | 3 | tarot #545×2(비적용 전환 — 계획 예고분) · **saju #197 import_legacy_saju_charts**(헬퍼 사슬 실쓰기 `:172 save` — billing import 와 동일 측정-결함 부류·kkebi 통지 목록화) |
| ⓕ 후보 전환 | 3 | billing ⓓ#365×3(순수 스텁 — blocker→후보) |
| 귀결 exitΔ | 1 | billing × business-vocabulary 2→0(유일 발화 #562 소멸의 귀결) |
| ⓓ ㉯ 경고 | 1 | tarot × EC stderr 경고 1행(auto 비-placeholder 미검사 고지 — exit·stdout 불변) |
| **그 외** | **0** | |

**ⓑ 정당 잔존 확인**: `#545` billing_event_stream_repository.py:74 red 잔존 ✓ ·
`#197` reconcile_legacy_billing_use_case.py:28 red 잔존 ✓ (반송 대상 — 통지문 §3).

## ⓒ ㉮ 후행표 (error 계열 · tarot 사본 selector 판형)

| 검사기 | 전 | 후 |
|---|---|---|
| check-error-centralization (code 프로파일) | 사용 오류 exit 1 — «DYNAMIC_…REQUIRED + provenance 분석 불능 + noncanonical inventory»(정적 판정 0) | **exit 2 · 정적 판정 산출** — 잔여 red 1건: «common FrameworkErrorSchema must directly inherit ninja.Schema (현행 BaseModel)» — 동적 증명이 STOP 으로 승인했던 표준 편차의 의도된 회복(kkebi 결정 사안·통지 첨부) |
| 〃 (auto) | 무출력 exit 0(침묵) | exit 0 + stderr 경고 1행 |
| 변형 B 픽스처 레인(canonical_alt) | — | good exit 0 · bad exit 2 — 변형 B 전 구간 판정 실증 |

## 인수 중 발견·수리 1건 (원인 규명 회귀 이행)

after 1차에서 tarot `recover_tarot_readings_use_case` 에 **#197 신규 red(오탐)** — 쓰기가
`execute → _process_one → _recover_stuck(save)` **2단 헬퍼 사슬**이라 1단 도달이 못 봄.
도달을 self 헬퍼 **추이 폐쇄**로 확장(죽은 헬퍼 배제 불변 — audit_order 픽스처 red 유지 확인)
+ 2단 사슬 good 픽스처(recover_order) 고정 → 재실행에서 오탐 소멸·그 외 불변.

## 검증 환경

`make verify` 6그룹 전 green(최종 로그 verify-final2) · 게이트 90/90 · render-sync 539절 red 0 ·
corpus 11/11 in-sync · baseline/findings 74레인 · cross census 차이 0 · findings_smoke 15/15 ·
construct 골든 8/8 · bc_registry_smoke 3단언(순수 스텁 후보·통신 위장 blocker 유지).

## 추기 — 대조 리뷰 처분 (blocker 1·major 1·minor 8 → 전건 해소/문서화)

- **blocker 해소**: codex `SKILL.md` b6 의미 미러에 R-2918 rev2 개정문 반영(선례 ead402d 판형).
- **major 해소**: «정본 이중화 exit 1» 채널의 회귀 pin 을 `workspace/tools/canonical_dual_smoke.py`
  신설(3종 전수 — api 는 auto 프로파일로 파스 통과 후 도달)·`verify-base-cross` 배선으로 소유.
  fixture 레인이 exit {2} 판형이라 레인 pin 이 불가능했던 것이 신설 사유(계획 W9 문면의 «bad:
  이중 실재»는 이 스모크로 대체 이행).
- **minor 수리 5**: ⓐ acl 동적 import(`importlib`) red 픽스처(loanhub) ⓑ #555 파일형
  (port/**/exception.py) good 픽스처(dispatcher) ⓒ truthy 변형 `len(x) > 0`·`bool(x)` good 픽스처
  (meterlog·chartlog) ⓓ W1c «같은 BC» 대조 집행(`_is_declared_error_module(module, bc_name)`)
  ⓔ #543 부칙에 «repo 가드 조인은 #545 소관» 문구.
- **minor 문서화 갈음 4**: ① 계수 +2(계획 «+1» — R-2918(skill) 의미 미러 rule 도 rev2 필요·선례
  R-3401+R-2921 동형) ② 신설 레인 대신 기존 default 레인 합류(같은 검사기·같은 판형의 픽스처를
  같은 레인에 두는 기존 관례 우선 — EXPECTED 사유 주석으로 추적성 확보) ③ W1b 통신 축 상수는 계획
  열거의 상위집합(telnetlib 등 — fail-closed 방향 확장) ④ W1a 조회 표면 인정이 계획 협창보다 넓음
  (조인+극성 이중 방어로 커버 — 거짓 양성 3형 합본 픽스처 포함, 개별 분리는 후속 여지).
- 관찰 정정: 계획 W7 의 «W6 이후 kkebi 에서 auto 가 실제 해석에 성공» 문장은 오예측 — auto 는
  code 판정을 갖지 않는 구조라 경고가 정상 잔존한다(후행표 실측과 일치).

## 추기 2 — ⓒ 후행표 잔여 2종 (대조 리뷰 minor ⑧ 해소 · accept-matrix 원자료 실측)

| 검사기 | billing | saju | tarot |
|---|---|---|---|
| check-api-error-controller-contract | exit 0→0 · 전/후 byte 동일 | 〃 | 〃 |
| check-openapi-error-declaration | exit 0→0 · 전/후 byte 동일 | 〃 | 〃 |

positional+auto 판형에서는 두 검사기 모두 3사본 전/후 완전 동일(exit·stdout·stderr) —
후행표에 적을 변화 0. ㉮의 정적 판정 변화는 selector 판형의 EC 후행표(§ⓒ)가 소유한다.
