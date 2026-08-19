# 적대 검증 레인 R — 동작 보존 주장 반증 (T2-1)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only)에서 **«T2-1 개작이 stdout·stderr·exit를 byte 단위로 보존했다»는 주장을 깨뜨려라**. 칭찬·요약은 쓰지 마라 — 결함만 쓴다.

## 배경(사실)

검사기 27종(`dddjango/scripts/check-*.py` — 로스터는 `dddjango/scripts/checker_registry.py`의 REGISTRY)을 공용 모듈 `dddjango/scripts/findings.py`에 편입했다. 개작 직전 판은 커밋 `ca5635d`이고, 개작은 `bf5b211`..`5d2c995` 구간에 있다(주요: `1a32738` 기계 치환 15종 · `95b34d1` 자유 출력 5종 · `7d4424b`·`9f8a429`·`6f17c73`·`5ef3357`·`4c5bada` dataclass 5종 · `37d6bf6`·`e2816c5` findings.py 계약 변경).

저자의 검증 방법과 그 한계:
- red/green 픽스처(`workspace/eval/fixtures/<lane>/{good,bad_rules}`; skeleton은 `{good_bc,bad_legacy_flat}`)를 **임시 디렉터리로 복사(비-git)** 해 실행하고 stdout/stderr/exit의 SHA를 개작 전후 대조했다.
- `--error-profile auto`가 필요한 3종은 그 인자로 실행했다.
- 즉 **검증 표면은 «각 검사기 × 자기 레인 red/green × 무앵커 기본 프로필»에 한정**된다.

너의 임무는 이 표면 **밖**에서 동작이 바뀐 곳을 찾는 것이다.

## 검증 과제 (전부 실행 실측으로)

개작 전 판을 얻는 방법: `git worktree`는 쓸 수 없으므로(read-only 샌드박스) `git show ca5635d:dddjango/scripts/<파일> > /tmp/<임시>/…` 처럼 임시 디렉터리에 구판을 풀어 같은 입력에 돌리고 현재 판과 출력·exit를 대조하라. 구판 실행에는 같은 폴더에 `checker_target.py`·`standard_tree.py`·`anchor_diff.py`·`checker_registry.py` 등 의존 모듈도 함께 풀어야 한다(구판 findings.py는 필요 없다 — 구판 검사기는 지역 클래스를 쓴다).

1. **프로필 조합**: `--error-profile`의 값 공간 전부(각 검사기의 argparse·`ERROR_PROFILES` 상수 참조 — auto/preserve-established/dddjango-code-json 등)와 그 밖의 CLI 옵션(`--scope`·`--api-module`·`--urlconf-module`·`--registrar-module`·`--controller-module` 등)을 조합해 구판/신판 출력을 대조하라. 특히 `check-composition-root.py`의 selector 모드, `check-response-schema-bypass.py`의 `--controller-module` 모드.
2. **anchor 차분 모드**: `--anchor <ref>`를 쓰는 검사기(api-error·error-centralization·openapi·composition-root)에서 구판/신판을 대조하라. `anchor_diff`는 검사기를 **재실행**하므로 `DJR_FINDINGS_JSON`이 상속되어 레코드가 중복 적재되는지(그리고 그것이 stdout·exit에 영향을 주는지) 확인하라. **exit 1(analysis_pending) 경로**·«공허 차분» 경로도 태워라.
3. **사용 오류·분석 불능 경로**: 인자 없음·존재하지 않는 경로·파일을 TARGET으로·BC 모양 디렉터리(층 폴더 직계 보유 — `checker_target.bc_shaped_target_reason`)·파싱 불가 소스·권한 없는 파일 등에서 exit code와 stderr 문면이 구판과 같은가.
4. **픽스처가 안 닿는 코드 경로**: 각 검사기에서 개작이 손댄 함수 중 red/green 픽스처가 실행하지 않는 분기를 코드로 식별하고(예: `check-error-centralization.py`의 `[분석]` 파싱 실패 라인, `check-openapi-error-declaration.py`의 repo_scan 레인, `check-composition-root.py`의 DI V1~V3 레인·code-profile 레인, `check-api-error-controller-contract.py`의 필터·동적 category), 그 분기를 태우는 최소 입력을 임시 디렉터리에 합성해 구판/신판을 대조하라.
5. **`findings.py` 계약 변경의 파급**: `Findings.add`의 2번째 인자를 `str(where)`로 강제한 변경(`37d6bf6`)이 **Path를 넘기던 호출자**의 라인 문면을 바꾸지 않았는가(특히 Windows 스타일 구분자·상대/절대 경로·`as_posix()` 유무 차이). `check-db-table.py` 등 Path 호출자를 실측하라.
6. **레코드 채널의 부작용**: `DJR_FINDINGS_JSON`이 설정된 상태에서 stdout·stderr·exit가 설정되지 않은 상태와 완전히 같은가(27종 전수). 레코드 파일 쓰기 실패(존재하지 않는 디렉터리·읽기 전용 경로)일 때 검사기가 죽거나 exit가 바뀌지 않는가 — 그것이 의도된 설계인지도 판정하라.
7. **성능·자원**: 대형 검사기(6,891행 api-error 등)에서 레코드 방출이 파일을 매 건 열고 닫는 구조(`findings.py`의 `_emit`)라 위반 수천 건 입력에서 실행 시간·파일 디스크립터 문제가 생기는지 실측하라(합성 대형 입력 사용).

## 출력 형식

마크다운 표 1개 + 필요한 보충 문단. 각 발견 = 한 행:

| # | 심각도(blocker/major/minor) | 결함 | 근거(재현 명령 + 구판/신판 실측 출력 차이) | 수정 제안 |

- **재현 명령 없는 주장 금지**.
- 결함이 없는 영역은 «반증 실패»로 한 줄만(무엇을 몇 조합 태웠는지 수치만 적어라).
- 저장소 파일을 수정하지 마라(read-only). 임시 파일은 `/tmp` 아래에만.
