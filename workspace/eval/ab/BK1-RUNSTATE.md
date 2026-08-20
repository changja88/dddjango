# BK1 실행 상태 — 첫 블록 (2026-08-20 기동)

> **이 파일은 compact 대비 재개 좌표다.** 세션이 끊겨도 herdr 에이전트 셋은 계속 돈다.

## 무엇을 돌리고 있나

O-7 표준 스모크 발주(«재고 부족하면 409, 충분하면 차감하고 주문 생성»)를 세 방식으로 **동시**
실행 중. 사전 등록 §11.1 로 병렬 개정 기록 완료(결과 관측 전).

| 런 | 암 | selector | herdr 에이전트 | 타깃 | run id |
|---|---|---|---|---|---|
| R01 | **A** | `—` | `t2ab-r01` | `/Users/hyun/Desktop/t2ab-R01` | `t2ab-R01` |
| R02 | **B** | `snapshot` | `t2ab-r02` | `/Users/hyun/Desktop/t2ab-R02` | `t2ab-R02` |
| R03 | **C** | `sparql` | `t2ab-r03` | `/Users/hyun/Desktop/t2ab-R03` | `t2ab-R03` |

## 공통 봉투 (기동 시 실측)

- 모델 **Opus 5 · xhigh** · 권한 `acceptEdits` · **브라우저 도구 off**(세 암 동일 — R02·R03 만
  물어봐서 R01 과 맞췄다)
- 요청문 3개 **byte 동일** `1141f2176a82e905`
- 시작 추적 트리 3개 **동일** `696c0df4aa8b826b`
- 앵커 `768d250` (마스터 `~/Desktop/dddjango-smoke-sample` · 이력 `9a5f9af` 에서 복원)
- 암 영수증 3개 기록 완료 (`<타깃>/arm.json`)

## 게이트 답 (묻거든 이대로)

BC 배치 **① 새 독립 영역** · lens **ddd+db+api** · 스코프 제안대로 · **plain Django** ·
**Django 기본 test** · G1/G2 **무수정 승인**

## 봉투 개정 1 — 플러그인 스킬 읽기 권한 (2026-08-21 00:21 · 결과 관측 전 기록)

**사건**: R01 이 설계 리뷰 진입 시 권한 프롬프트에서 정지했다 —
`Search("<설치본>/2.14.0/skills/**/references/*.md")`. `acceptEdits` 는 편집만 자동 승인하고
**작업 폴더 밖 읽기**는 여전히 묻는다. 약 4분간 R01 만 멈춰 있었고 R02·R03 은 계속 돌았다.

**처분**: 세 암 모두 **«2. 세션 동안 허용»** 으로 통일한다. R01 은 00:21 제출 완료. R02·R03 은
같은 프롬프트가 뜨면 **같은 답**을 준다.

**왜 «1. 한 번만» 이 아닌가**: 한 번만 허용하면 검색마다 다시 묻고, 그 정지 횟수가 암마다
달라진다. 내가 하나를 늦게 잡으면 그 암만 더 오래 멈춘다 — 처치가 아닌 이유로 암 사이에
차이가 생긴다. 세션 허용은 이후 프롬프트를 없애서 세 암을 같은 조건으로 만든다.

**왜 «3. 거부» 가 아닌가**: 리뷰어가 제 플러그인의 스킬 참조를 읽는 것은 파이프라인 정상
동작이다. 막으면 암과 무관한 이유로 런 품질이 내려간다.

**이것이 처치가 아닌 근거**: 읽기 대상은 설치본 스킬 문서이고 세 암이 **같은 설치본
2.14.0** 을 본다. 암 차등은 여전히 환경 스위치 둘뿐이다.

**남은 위험(자인)**: R01 만 약 4분 정지했다 — 벽시계 시간에 암 간 차이가 생겼다. 채점은
벽시계가 아니라 산출물 기준이라 판정 스칼라에는 들어가지 않지만, «세 런이 완전히 같은
조건이었다» 고는 말할 수 없다.

**감시 자동화**: 이후 정지를 사람이 발견하는 방식은 폐기한다. `herdr agent list` 의
`agent_status` 를 20초 주기로 읽어 **working 이 아닌 상태**를 즉시 이벤트로 올린다
(`$CLAUDE_JOB_DIR/tmp/watch-bk1.sh`).

## 런이 끝나면 (채점 — arm-blind)

```bash
cd /Users/hyun/Desktop/dddjango
for n in 01 02 03; do
  DJR_EXPERIMENT_RUN_ID=t2ab-R$n python3 workspace/tools/ab_score.py \
    /Users/hyun/Desktop/t2ab-R$n --anchor 768d250 --run t2ab-R$n \
    --allow-unsealed --out /Users/hyun/Desktop/t2ab-R$n/score.json
done
```

**주의**: `DJR_EXPERIMENT_RUN_ID` 는 **게이트 실행 시점**에 있어야 한다 — 검사기가 기록하는
값이라 나중에 주면 `null` 이 된다(배선 점검에서 실측으로 잡았다).

인수는 바깥 채점표로 별도 실행:
`workspace/eval/ab/acceptance/O-7/test_external_acceptance.py` 를 각 타깃에 복사 후
`.venv/bin/python manage.py test`.

## 상태 확인

```bash
for a in t2ab-r01 t2ab-r02 t2ab-r03; do herdr agent read $a | tail -6; done
```

## 이 블록이 답하는 것

첫 블록은 **판정이 아니라 노출 점검**이다(사전 등록 §10). `V_B,O-7,1` 과 루프 발화 회전 수가
**둘 다 0** 이면 즉시 보고하고 잔여 15런 전에 처분을 정한다.
