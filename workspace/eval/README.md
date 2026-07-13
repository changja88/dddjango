# workspace/eval — dddjango 평가 시스템

`/dddjango` 플러그인이 낸 산출물을 **규칙 준수(DDD·houserules·django-ninja) + 기능 정확성** 기준으로 채점하는 평가 홈. 현행 기준은 **v4(2026-07-13)**이며 migration lifecycle 비소유와 현재 계약 테스트 수명을 포함한다.

> **역사 보존**: v3 이하 채점 결과지·라이브파이어 기록은 당시 기준의 결과이며 v4로 소급 재판정하지 않는다. 평가 *기준*(`rubric/`)과 고정 입력(`tools/FC-GOLDEN.md` 기능 프롬프트·골든 + `tools/Q6-CURRENT-CONTRACT.md` 테스트 수명 시나리오·oracle + `EVAL-METHOD §0.2` 게이트 답)이 평가 재개 시 출발점이다.

## 구조

```
eval/
├── README.md            # 이 인덱스
├── rubric/              # 평가 기준 (정본 — 채점의 단일 출처)
│   ├── RUBRIC.md            # 평가 *항목* (무엇을 보나): S-DDD·S-HR·S-NINJA·FC·TIER-Q
│   ├── EVAL-METHOD.md       # 평가 *방법* (어떻게 채점·집계·완료 판정하나)
│   └── rubric-metrix.md     # v4 결과지 작성 템플릿
├── tools/               # 평가 보조 (고정 oracle·텔레메트리·리포트)
│   ├── FC-GOLDEN.md         # FC 사전등록(골든 행위표·mutation) + 표준 기능 태스크 프롬프트
│   ├── Q6-CURRENT-CONTRACT.md # 현재 계약 테스트 수명 고정 7시나리오 + PASS/FAIL oracle
│   ├── q6_fixture_builder.py # runtime seed와 evaluator-only CRIB/oracle/manifest 분리 생성
│   └── check-structure.py   # baseline-aware 결정 레인 리포터(exit 0)
└── results/             # 채점 결과지 (<YYYYMMDD-HHMM>-<라운드>-<런타임>.md)
```

> 과거 채점 결과지(`<YYYYMMDD-HHMM>-<라운드>-<런타임>.md`)·라이브파이어·근본원인 분석은 2026-06-09 일단락 정리됨 — 결론은 `DEVLOG.md` 각 DR, 상세는 git 히스토리.

## 관리 규약 (평가 재개 시)

1. **채점 기준은 `rubric/`이 단일 출처.** `RUBRIC.md`(항목)로 보고 `EVAL-METHOD.md`(방법)로 채점·집계. 기준 변경은 *채점 전*에만(EVAL-METHOD §5 사전등록).
2. **고정 입력**: 표준 기능 태스크 프롬프트·FC 골든 행위표는 `tools/FC-GOLDEN.md`, 현재 계약 테스트 수명 일곱 시나리오·oracle은 `tools/Q6-CURRENT-CONTRACT.md`, 런 리셋·고정 게이트 답(BC배치·렌즈·API스택·G1/G2 승인)은 `EVAL-METHOD §0.2`. Q6 builder가 만든 `evaluator-control/`과 builder/doc source는 runtime에 노출하지 않고, 선택 fixture만 출력 루트 밖의 fresh workspace로 복사한다. *(구 `results/RETEST-HANDOFF.md`는 폴더 재구조화로 제거됨.)* 런 간 입력이 흔들리거나 oracle이 노출되면 비교가 오염된다.
3. **정직 경계**: 정적 채점은 "구조적 준수 + 기능 정확성"까지. "게이트 라이브 발화"는 fresh 위반-주입 런으로만(정적 통과 ≠ 라이브 발화·DR-21). baseline 대비 차별가치는 *안 잰다*.
4. **채점 결과지 형식**은 `EVAL-METHOD §6` 표준 템플릿(섹션 순서·칼럼 스키마·필수 단서).

## 전체 여정·결정 정본

플러그인 전체 작업 이력·DR 원장은 레포 `workspace/DEVLOG.md`. 과거 평가 결과·산출물·fixture(`~/Desktop/dddjango-*`)는 git 히스토리.
