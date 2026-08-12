# workspace/eval — dddjango 평가 시스템 (v5 frozen baseline)

> **상태**: `active` · **FROZEN** · **SCORING ENABLED**.
> 사용자 명시 승인(`2026-08-11T23:53:32+0900` — **v5 최소 개정 epoch**)으로 동결됐다. 승인 이후 새로
> 생산하는 v5 결과에만 이 기준을 사용하며 historical v3·v4 결과에는 소급 적용하지 않는다.
> **동결 epoch/profile/version**: `2026-08-08-tree-revision` / `dddjango-code-json` /
> `v5-candidate`.
> **v5 최소 개정 범위**: 구조 차원(SH 블록)의 판을 신 표준 정본(`dddjango/scripts/standard_tree.py`
> 140행 · houserules `references/final.md` §0~§4)과 registry **27종**에 위임 — 평가지가 구조 값을
> 중복 소유하지 않는다. SD·NJ·FC·Q 차원·치명 배정·차원 수(34)는 v4 그대로다.

`/dddjango` 산출물의 규칙 준수(DDD·houserules·django-ninja)와 기능 정확성을
평가하기 위한 홈이다. 현재 working tree의 평가 문서는 트리 개정 표준의 동결된 v5
채점 기준이다.

## Epoch·재현·결과 식별

- v4 기준(epoch `2026-08-03-code-json`/`v4-candidate`)의 재현 locator는 full SHA
  `3239773d87df60ab8c2f10c8b189f6793cab1a36`이다.
- v3 기준과 그 기준으로 작성된 결과의 재현 locator는 full SHA
  `d1fce5b43b13f8447b2a4b78f6c94e74efe8ff19`이다. v3 파일은 이 immutable Git
  commit에서 재현한다.
- `workspace/eval/results/`에는 historical v3 결과지 **14개가 실제로 존재**한다.
  이 파일들은 working tree에서 보존하며 삭제·재작성·v4 소급 채점하지 않는다.
- v5 결과 식별자는 반드시
  `epoch + error profile + rubric version + dimension ID`를 사용한다. v3·v4·v5의
  같은 dimension ID(특히 **SH-7 — v5에서 방향 반전**)는 이름이 같아도 같은 의미로 집계하지 않는다.
- v5는 **ACTIVE / FROZEN**이며 승인 이후 새 결과만 채점·집계한다. 기준 변경은 명시적
  unfreeze 또는 새 epoch 승인 없이는 금지한다.

## 구조

```text
eval/
├── README.md
├── fixtures/
│   └── api_error_contract/
│       ├── requirements.txt          # runtime 계약 fixture exact pins
│       └── test_api_error_contract.py # 14개 실행 계약 테스트
├── rubric/
│   ├── RUBRIC.md
│   ├── EVAL-METHOD.md
│   └── rubric-metrix.md
├── tools/
│   └── FC-GOLDEN.md
└── results/                           # historical v3 결과지 14개 — immutable
```

## API error runtime fixture

`fixtures/api_error_contract/`는 동결된 v4 runtime 계약을 독립적으로 재현하는 실행
fixture다. exact pins는 다음과 같다.

- `Django==6.0.7`
- `django-ninja==1.6.2`
- `django-ninja-extra==0.31.6`
- `pydantic==2.13.4`
- `pytest==9.1.1`

테스트는 정확히 14개다. 저장소 루트에서 다음 명령으로 격리 재현한다.

```bash
uv run --isolated --no-project \
  --with-requirements workspace/eval/fixtures/api_error_contract/requirements.txt \
  -- python -B -m pytest -q -p no:cacheprovider \
  workspace/eval/fixtures/api_error_contract/test_api_error_contract.py
```

이 fixture는 runtime 계약의 실행 증거이며 **또 하나의 checker가 아니다**. 결정적 checker의
정본은 `dddjango/scripts/check-*.py`의 **27개**(registry — `commands/dddjango.md`)이고,
Codex mirror(`codex-dddjango/skills/dddjango/scripts/`)는 byte-copy 로 같은 27개를 갖는다.

## checker 위반-fixture 결정 레인 (v5)

`fixtures/`의 검사기별 good/bad_rules fixture 와 `workspace/tools/fixture_matrix.py`(90케이스 —
호출 계약 레인 27·수정 사이클 결정 레인 3×2 포함·2026-08-12)가 「검사기마다 자기 위반 fixture 에서 exit 2 ·
BC 모양 TARGET 은 사용 오류 exit 1」을 전수 실측한다 — 실측표는
`workspace/plan/2026-08-11-fixture-matrix.md`(생성물). `workspace/tools/reverse_coverage.py`는
플러그인 전 파일의 규칙 커버리지(미설명 0)를 잰다. 옛 구조 판 `tools/check-structure.py`는
**v5에서 은퇴**했다(v4-era 판 — 구조 판정은 registry #4 `check-layer-skeleton`이 소유; 파일은
v4 재현용으로 보존).

## 동결 관리 규약

1. `RUBRIC.md`는 무엇을 볼지, `EVAL-METHOD.md`는 어떻게 판정·집계할지 정의하지만,
   승인 이후 새 v5 결과의 활성 채점 기준으로 사용한다.
2. 고정 입력과 FC mutation 계약은 동결된 `tools/FC-GOLDEN.md`를 사용한다.
3. historical v3 결과 14개를 수정하거나 v4 의미로 재해석·재채점하지 않는다.
4. 차원·판정 기준·FC 골든·mutation 계약을 바꾸려면 명시적 unfreeze 또는 새 epoch 승인이
   필요하다. 결과를 본 뒤 현 epoch의 기준을 조용히 바꾸지 않는다.

플러그인 전체 작업 이력·DR 원장은 `workspace/DEVLOG.md`에 있다.
