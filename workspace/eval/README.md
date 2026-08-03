# workspace/eval — dddjango 평가 시스템 (v4 candidate)

> **상태**: `candidate` · **NOT ACTIVE** · **NOT FROZEN** · **SCORING PROHIBITED**.
> 사용자 명시 freeze 전에는 어떤 fixture도 이 기준으로 채점하거나 결과를 만들지 않는다.
> **후보 epoch/profile/version**: `2026-08-03-code-json` / `dddjango-code-json` /
> `v4-candidate`.

`/dddjango` 산출물의 규칙 준수(DDD·houserules·django-ninja)와 기능 정확성을
평가하기 위한 홈이다. 현재 working tree의 평가 문서는 새 code-json 표준을 검토하기 위한
v4 후보이며, 활성 채점 기준이 아니다.

## Epoch·재현·결과 식별

- v3 기준과 그 기준으로 작성된 결과의 재현 locator는 full SHA
  `d1fce5b43b13f8447b2a4b78f6c94e74efe8ff19`이다. v3 파일은 이 immutable Git
  commit에서 재현한다.
- `workspace/eval/results/`에는 historical v3 결과지 **14개가 실제로 존재**한다.
  이 파일들은 working tree에서 보존하며 삭제·재작성·v4 소급 채점하지 않는다.
- v4 결과 식별자는 반드시
  `epoch + error profile + rubric version + dimension ID`를 사용한다. 따라서 v3의
  `NJ-7 PASS`와 v4 후보의 `NJ-7 PASS`는 이름이 같아도 같은 의미로 집계하지 않는다.
- v4 후보는 사용자 freeze 전까지 **NOT ACTIVE / NOT FROZEN**이며 채점·집계가 금지된다.

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

`fixtures/api_error_contract/`는 v4 후보의 runtime 계약을 독립적으로 재현하는 실행
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

이 fixture는 runtime 계약의 실행 증거이며 **20번째 checker가 아니다**. 결정적 checker의
정본은 `dddjango/scripts/check-*.py`의 **19개**이고, Claude/Codex mirror도 같은 19개다.

## 후보 관리 규약

1. `RUBRIC.md`는 무엇을 볼지, `EVAL-METHOD.md`는 어떻게 판정·집계할지 정의하지만,
   두 문서 모두 사용자 freeze 전에는 채점에 사용할 수 없다.
2. 고정 입력과 FC mutation 후보는 `tools/FC-GOLDEN.md`에 두되, 그것 역시
   candidate이며 채점·mutation 실행 근거로 활성화하지 않는다.
3. 새 결과 파일을 만들거나 historical v3 결과 14개를 v4 의미로 재해석하지 않는다.
4. 적대 리뷰, 34-ID 기계 대조, candidate diff 검토 뒤 사용자가 명시적으로 freeze해야만
   별도 변경에서 상태를 활성·동결로 전환할 수 있다. 이 문서 변경 자체는 자기승인이 아니다.

플러그인 전체 작업 이력·DR 원장은 `workspace/DEVLOG.md`에 있다.
