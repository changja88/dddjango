#!/usr/bin/env python3
"""findings/0 계수 골든 — 편입 검사기 × 레인 × {계수·13필드 oracle·stdout↔record 대조}.

T2-1 채점 하네스(D11 — t2-plan v1.1: «27종 전수 arm-blind red/green 계수 골든»)의
레코드 채널 축: 공용 findings 모듈로 편입된 검사기마다 red fixture 에서
{exit · severity별 레코드 수 · rule/sentinel 분포 · violation_id 집합 해시}를,
green fixture 에서 {exit 0 · 레코드 0}을 고정한다. byte 골든(findings_smoke·대표군)과
달리 stdout 문면이 아니라 **계수 의미**를 고정한다 — 개작이 계수를 바꾸면 여기서 red.

T2-1 보강 1단계(포매터 계약 §4-1) 확장:
- 레인 키 공간: checker_baseline_matrix 와 동일 — 기본 red 레인 `"<script>"` +
  git 3레인·위험 레인 `"<script>::<lane>"`(선언·로더·git 구성·커스텀 argv 전부
  그쪽 import — 단일 출처). 위험 레인은 자기 good/ 을 같은 argv 의 green 축으로 갖는다.
- findings/0 **13필드 전건 oracle**: 레코드마다 schema·checker(파일명 일치)·
  rule/sentinel/contract_ref 상호 배타·file 비어있지 않음·severity 값 공간·message
  비어있지 않음·expression null·ts UTC 형식·run_id 단일·record_id 유일+
  `{run_id}:{4자리 서수}` 연속 증가를 단언한다(위반 시 해당 행 red).
- stdout↔record 대조 2축: ⓐ 위반·후보 라인(`[#N]`/`[ⓓ#N]` 앵커)의 (severity, rule)
  열 양방향 대조 ⓑ **라인 재구성 대조**(M5 — 전 레코드를 포매터 판형(violation·
  candidate·계약·guard·센티널)으로 재구성해 stdout 실재·순서를 subsequence 게이트 —
  message·file·contract 문면 drift 검출·mutation stdout-message-drift 로 실증).
  기본은 **ordered** 대조다(V25 ⑤ — 순서 보존 방출 이행 전 검사기 완결로 기본
  전환. 기본화 첫 시도가 후보 채널 11종의 순서 불일치를 적발해 이행을 선행시킨
  뒤 전환했다. `--strict-order` 플래그는 호환 no-op). 잉여·누락·중복에 더해
  순서 위반도 게이트. 위험 레인 관찰 보류는 게이트 편입 완료.
- multiset fingerprint(구 열과 병기 — W6 5단계 정식 편입): `(rule|sentinel|contract_ref,
  file, symbol, message, occurrence_index)` — occurrence_index 는 동일 4-튜플 내 방출 순
  서수. `json.dumps(ensure_ascii=False)` 직렬화 sha16. EXPECTED 6번째 열로 게이트한다.
- `--scripts-dir/--fixtures-dir` 주입점(변조 self-test 는 checker_baseline_matrix
  `--self-test` 소유).

violation_id = (rule|sentinel|contract_ref, file, symbol) — 동결 §6 계수 규약의
«Work×대상 파일×심볼» 동일성의 레코드 층 대응(Work 조인 전이므로 rule 표기 사용).
file 은 hermetic 사본 절대 경로를 <FX> 로 정규화해 결정화한다.

EXPECTED 갱신 규율: 개작·픽스처 변경으로 수치가 바뀌면 같은 커밋에서
`--emit-expected` 로 갱신하되 검사기별 사유를 커밋 메시지에 전건 기록한다.

사용: python3 workspace/tools/findings_count_matrix.py [--emit-expected]
        [--strict-order] [--scripts-dir <dir>] [--fixtures-dir <dir>]
exit 0 = 전수 일치 / exit 2 = 불일치 / exit 1 = 재료 결손·사용 오류.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"

sys.path.insert(0, str(S))
sys.path.insert(0, str(ROOT / "workspace" / "tools"))
from checker_registry import REGISTRY  # noqa: E402
from fixture_matrix import AUTO_PAIRS, PLAIN_PAIRS  # noqa: E402

# 레인 선언·git 레인 구성·argv 판형은 checker_baseline_matrix 소유(단일 출처) — 동일
# `(script[::lane])` 키 공간을 두 하네스가 공유한다(포매터 계약 §4-1).
from checker_baseline_matrix import (  # noqa: E402
    GIT_LANES,
    GIT_AFFECTED,
    GUARD_LANE,
    GUARD_LANES,
    RISK_LANES,
    _RISK_DIRS,
    DEFAULT_LANE,
    lane_argv,
    prepare_lane_copy,
)

_LANE: "dict[str, tuple[str, str]]" = {"check-layer-skeleton.py": ("skeleton/bad_legacy_flat", "skeleton/good_bc")}
_LANE.update({s: (f"{fx}/bad_rules", f"{fx}/good") for s, fx in PLAIN_PAIRS})
_LANE.update({s: (f"{fx}/bad_rules", f"{fx}/good") for s, fx in AUTO_PAIRS})

# 공용 findings 모듈 편입 완료 로스터 = REGISTRY 전체(T2-1 완료 — 27/27 승격 2026-08-19).
# 로스터 이탈은 재료 결손으로 즉사한다(신설 검사기는 편입과 EXPECTED 등재가 동시 의무).
CONVERTED: "tuple[str, ...]" = tuple(sorted(script for script, _ in REGISTRY))

CHECKER_TIMEOUT_S: int = 300  # 무기한 verify 정지 방지(적대 검증 레인 S 9번)

# findings/0 의 13필드 전체(스키마 정본: dddjango/scripts/findings.py docstring).
_FIELDS: "tuple[str, ...]" = (
    "schema", "run_id", "ts", "record_id", "rule", "sentinel", "contract_ref",
    "checker", "file", "symbol", "severity", "message", "expression",
)
_TS_RE: "re.Pattern[str]" = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
_RULE_FORM: "re.Pattern[str]" = re.compile(r"#\d+\Z")
# stdout 라인 앵커 — 위반은 registry_gate `_FINDING_RE` 동형, 후보는 ⓓ 판형.
_VIOLATION_LINE: "re.Pattern[str]" = re.compile(r"^\s*\[(#\d+)\]")
_INFO_LINE: "re.Pattern[str]" = re.compile(r"^\s*\[ⓓ(#\d+)\]")

# 키 -> (red_exit, violation수, info수, rule/sentinel 분포 요약, violation_id 집합 sha16,
#        multiset fingerprint sha16 — W6 정식 병기(5단계): sorted[(rule|sentinel|
#        contract_ref, file, symbol, message, occurrence_index)] 직렬화 해시)
EXPECTED: "dict[str, tuple[int, int, int, str, str, str]]" = {
    "check-api-error-controller-contract.py": (2, 9, 1, "#120×1,#121×1,#123×1,#124×1,#125×1,#126×1,#131×1,#132×1,#474×1,#62×1", "218a6d81f576dda3", "4ff2ead3db93a9fa"),
    "check-app-container.py": (2, 1, 0, "contract:선행 규약(표준 트리 전신 — application/ 컨테이너 위치) 소유×1", "31240e8fe5840470", "44e58e3b16845aff"),
    "check-broker-contract.py": (2, 22, 5, "#442×2,#443×2,#444×1,#518×1,#520×3,#521×1,#523×1,#524×2,#525×1,#527×1,#528×1,#529×1,#531×1,#532×1,#533×2,#534×1,#603×5", "11deccf9f90c6592", "e9cf0a9f6de4a278"),
    "check-business-vocabulary.py": (2, 48, 5, "#119×1,#19×1,#294×1,#35×1,#39×1,#393×1,#395×1,#396×1,#398×1,#402×1,#407×2,#408×1,#412×1,#414×1,#415×1,#416×1,#417×1,#420×1,#423×1,#425×1,#426×1,#428×1,#434×1,#448×1,#46×2,#47×1,#52×1,#53×1,#560×1,#561×1,#562×2,#584×1,#585×2,#587×1,#606×2,#607×1,#615×2,#617×1,#618×1,#619×2,#620×1,#621×1,#622×1,#623×1,#624×2", "5d54270ca9386cdf", "34abc446bddb5f12"),
    "check-choices-literal-consumption.py": (2, 3, 0, "contract:선행 계약(2026-07-06 상수 승격) 소유×3", "6253365c1e25da21", "2f961c306ed061c0"),
    "check-common-container.py": (2, 2, 0, "contract:선행 규약(D38 승격/강등 — 루트 framework/ 배치) 소유×2", "7ddb14624648702f", "5b02b9878d9d83e0"),
    "check-composition-root.py": (2, 18, 2, "#101×1,#105×1,#107×1,#108×1,#109×1,#111×1,#112×1,#437×3,#440×1,#441×1,#497×1,#498×1,#500×1,#501×1,#511×1,#84×1,#85×1,#86×1", "fe484815e50a3068", "4a97d85dfb5d47b9"),
    "check-context-isolation.py": (2, 58, 4, "#102×1,#11×1,#110×1,#117×1,#13×1,#14×1,#146×1,#150×1,#151×1,#153×4,#154×1,#155×1,#157×1,#164×2,#166×1,#167×2,#168×1,#170×1,#185×1,#186×1,#2×2,#251×1,#288×1,#291×1,#292×1,#295×1,#312×1,#328×1,#347×1,#361×1,#363×1,#364×2,#431×2,#433×2,#450×2,#453×1,#455×1,#472×1,#473×2,#482×1,#483×2,#484×1,#51×1,#633×1,#634×1,#9×1,#93×1,#94×1,#95×1,#98×1", "1417df159b14cac7", "3e368604cf514e50"),
    "check-db-table.py": (2, 26, 0, "#318×1,#324×2,#325×1,#326×2,#329×1,#330×2,#331×2,#332×1,#334×1,#335×2,#467×1,#535×1,#536×1,#537×1,#538×2,#630×2,#631×2,#632×1", "5b85011e45235434", "239a377ed7ebf3eb"),
    "check-domain-model.py": (2, 48, 13, "#17×2,#249×1,#252×1,#253×1,#256×1,#257×2,#258×1,#259×1,#260×2,#261×1,#262×1,#263×1,#264×1,#266×1,#267×1,#268×2,#269×2,#270×1,#272×1,#275×1,#276×1,#289×1,#290×1,#298×1,#299×2,#300×1,#301×4,#302×1,#303×1,#304×1,#305×1,#307×1,#308×1,#310×1,#311×1,#315×1,#459×1,#505×1,#506×1,#542×1,#543×3,#546×1,#547×2,#548×2,#549×1,#550×1,#565×1,#8×1", "085ac733a6aa5b35", "f0f3e9ed0f41ec30"),
    "check-error-centralization.py": (2, 5, 0, "#114×1,#568×2,#572×1,#636×1", "c3da2a9e89c47951", "cacda249ec94d135"),
    "check-event-publish.py": (2, 20, 4, "#271×3,#279×1,#280×2,#502×1,#503×2,#504×1,#507×1,#508×1,#509×1,#564×2,#600×1,#601×1,#627×2,#7×2,#96×3", "06594a2b1253f981", "6027ffddfd7b2d9e"),
    "check-idempotency-scope-creep.py": (2, 1, 0, "contract:선행 계약(architecture-api §13 멱등 스코프) 소유×1", "46b04bd6bcc4b9e5", "0de6db90334e6f41"),
    "check-layer-skeleton.py": (2, 10, 0, "#488×7,#490×2,#81×1", "650a62bfa578c75d", "df23b4464c21dccb"),
    "check-mechanism-ownership.py": (2, 6, 0, "#336×1,#337×1,#338×1,#593×3", "667832904ba25a08", "67400faf82fc3e1e"),
    "check-missable-entrance.py": (2, 17, 4, "#172×1,#173×1,#174×2,#175×1,#179×2,#180×1,#181×2,#451×1,#512×2,#514×1,#515×2,#516×2,#517×2,#629×1", "2b604f3883227873", "85500a6f29199b00"),
    "check-naming.py": (2, 29, 5, "#118×1,#148×1,#169×1,#247×2,#28×2,#30×1,#309×1,#33×1,#34×1,#340×1,#341×1,#342×1,#343×1,#344×2,#345×1,#348×2,#36×3,#382×1,#41×1,#43×1,#44×1,#481×1,#588×1,#589×1,#590×2,#87×1,#97×1", "67c3b8f630ac2347", "d26da9f6a129e645"),
    "check-ninja-boundary-middleware.py": (2, 2, 0, "contract:선행 계약(08-04 API-error) 소유×2", "bcca745399dc645e", "fb84fc0e70f9f759"),
    "check-openapi-error-declaration.py": (2, 3, 0, "#63×3", "21e2961d8fb1eb4f", "9598eff4f473e0cc"),
    "check-port-adapter-pairing.py": (2, 79, 9, "#134×1,#212×2,#214×1,#215×1,#216×2,#218×1,#219×1,#220×2,#225×1,#227×1,#228×2,#231×1,#232×1,#233×2,#234×1,#235×1,#236×1,#238×1,#239×1,#240×1,#241×1,#242×1,#244×1,#245×1,#246×1,#313×1,#351×2,#352×1,#354×1,#356×1,#359×1,#367×1,#368×1,#369×1,#370×2,#373×1,#374×1,#376×1,#457×1,#460×1,#462×2,#464×1,#465×1,#476×2,#477×2,#480×1,#485×5,#545×2,#551×1,#552×4,#553×1,#554×1,#555×1,#556×1,#557×1,#566×1,#573×1,#574×1,#575×1,#576×1,#577×1,#578×1,#579×1,#580×1,#581×1,#582×1,#583×1,#594×2,#64×1", "1714fece63e1a322", "656bfbc7a87145dd"),
    "check-public-surface-annotation.py": (2, 10, 2, "#358×2,#456×1,#493×7,#69×2", "7f50607021907d7f", "39773b5c7f7364e3"),
    "check-response-schema-bypass.py": (2, 1, 0, "contract:선행 계약(08-04 API-error) 소유×1", "7425fefd479b2edc", "bfd73ca26e52466d"),
    "check-synthetic-infra-exc.py": (2, 2, 0, "#129×1,sentinel:합성×1", "2e7e2fb7cccbac27", "518f4f7518bb9711"),
    "check-test-config.py": (2, 14, 0, "#384×2,#385×1,#387×1,#388×1,#389×1,#390×2,#391×1,#392×1,#445×1,#446×1,#447×1,sentinel:바인딩×1", "3df1f227a35f1c83", "5467197844ea37d1"),
    "check-transaction-boundary.py": (2, 13, 2, "#195×1,#197×1,#200×1,#282×1,#283×1,#285×1,#287×2,#355×2,#4×1,#597×1,#599×3", "4a583ba210af44e8", "c14c4f1d4f0cc6f0"),
    "check-transient-overmapping.py": (2, 1, 0, "contract:선행 계약(08-04 API-error) 소유×1", "e4f6a367f28dd0d1", "849fa036f6fb55c8"),
    "check-usecase-dto-placement.py": (2, 35, 5, "#139×1,#140×1,#142×1,#144×2,#182×1,#183×1,#188×2,#189×1,#190×1,#191×1,#192×1,#193×1,#194×1,#196×1,#201×1,#202×2,#205×1,#208×1,#210×1,#211×1,#539×1,#540×1,#541×1,#567×1,#569×3,#570×2,#571×2,#635×3,#67×1,#68×2", "378ab736baa677df", "ed61289ac2348cc9"),
    "check-response-schema-bypass.py::git-clean": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-response-schema-bypass.py::git-modified": (2, 1, 0, "contract:선행 계약(08-04 API-error) 소유×1", "7425fefd479b2edc", "bfd73ca26e52466d"),
    "check-response-schema-bypass.py::git-untracked": (2, 1, 0, "contract:선행 계약(08-04 API-error) 소유×1", "7425fefd479b2edc", "bfd73ca26e52466d"),
    "check-app-container.py::git-clean": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-app-container.py::git-modified": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-app-container.py::git-untracked": (2, 1, 0, "contract:선행 규약(표준 트리 전신 — application/ 컨테이너 위치) 소유×1", "31240e8fe5840470", "44e58e3b16845aff"),
    "check-idempotency-scope-creep.py::git-clean": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-idempotency-scope-creep.py::git-modified": (2, 1, 0, "contract:선행 계약(architecture-api §13 멱등 스코프) 소유×1", "46b04bd6bcc4b9e5", "0de6db90334e6f41"),
    "check-idempotency-scope-creep.py::git-untracked": (2, 1, 0, "contract:선행 계약(architecture-api §13 멱등 스코프) 소유×1", "46b04bd6bcc4b9e5", "0de6db90334e6f41"),
    "check-transient-overmapping.py::git-clean": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-transient-overmapping.py::git-modified": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-transient-overmapping.py::git-untracked": (2, 1, 0, "contract:선행 계약(08-04 API-error) 소유×1", "e4f6a367f28dd0d1", "849fa036f6fb55c8"),
    "check-choices-literal-consumption.py::git-clean": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-choices-literal-consumption.py::git-modified": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-choices-literal-consumption.py::git-untracked": (0, 0, 0, "", "4f53cda18c2baa0c", "4f53cda18c2baa0c"),
    "check-synthetic-infra-exc.py::git-clean": (2, 1, 0, "#129×1", "cb5389627def38b8", "5310eb2801147b90"),
    "check-synthetic-infra-exc.py::git-modified": (2, 1, 0, "#129×1", "cb5389627def38b8", "5310eb2801147b90"),
    "check-synthetic-infra-exc.py::git-untracked": (2, 2, 0, "#129×1,sentinel:합성×1", "2e7e2fb7cccbac27", "518f4f7518bb9711"),
    "check-db-table.py::git-clean": (2, 24, 0, "#318×1,#324×2,#325×1,#326×2,#329×1,#330×2,#331×2,#332×1,#334×1,#335×2,#467×1,#535×1,#536×1,#537×1,#538×2,#631×2,#632×1", "c0a20513dc57285b", "60d814661bce27be"),
    "check-db-table.py::git-modified": (2, 24, 0, "#318×1,#324×2,#325×1,#326×2,#329×1,#330×2,#331×2,#332×1,#334×1,#335×2,#467×1,#535×1,#536×1,#537×1,#538×2,#631×2,#632×1", "c0a20513dc57285b", "60d814661bce27be"),
    "check-db-table.py::git-untracked": (2, 26, 0, "#318×1,#324×2,#325×1,#326×2,#329×1,#330×2,#331×2,#332×1,#334×1,#335×2,#467×1,#535×1,#536×1,#537×1,#538×2,#630×2,#631×2,#632×1", "5b85011e45235434", "239a377ed7ebf3eb"),
    "check-api-error-controller-contract.py::api_error_controller_code": (2, 3, 0, "#59×1,#62×2", "97ef7c202f1d48d0", "54e3a219e3e20466"),
    "check-composition-root.py::composition_root_single_file": (2, 1, 0, "#497×1", "2c43cc1deddc1a8c", "2fc253839f16eb6c"),
    "check-openapi-error-declaration.py::openapi_decl_missing": (2, 1, 0, "#63×1", "238f374c04cdbc00", "95363305293051ff"),
    "check-error-centralization.py::error_centralization_code": (2, 3, 0, "#572×1,contract:선행 계약(08-04 API-error) 소유×2", "ca07fbbfc15d97c8", "4c7001115cd355de"),
    "check-api-error-controller-contract.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "ff910566edd77355"),
    "check-error-centralization.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "dd0e053b943ade19"),
    "check-openapi-error-declaration.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "f2d1a02f508ad602"),
    "check-response-schema-bypass.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "a48e09bb1d2d8734"),
    "check-db-table.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "f74cd9a3af326bd2"),
    "check-domain-model.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "e5abbd3c9f18d0a2"),
    "check-event-publish.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "70efaa8b3073675d"),
    "check-idempotency-scope-creep.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "1c333ae23667db21"),
    "check-layer-skeleton.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "c8f6734063cabd64"),
    "check-mechanism-ownership.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "ec77f36e5d019139"),
    "check-missable-entrance.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "74ad02ff7de72a4e"),
    "check-naming.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "383fa0eac3be9402"),
    "check-ninja-boundary-middleware.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "cbe89ba066c8a5e4"),
    "check-port-adapter-pairing.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "373fa76a51f104a1"),
    "check-public-surface-annotation.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "598e021a96681874"),
    "check-synthetic-infra-exc.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "62d865bb7162735f"),
    "check-test-config.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "99873aba7f6ef8aa"),
    "check-transaction-boundary.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "85fd98555b364d2b"),
    "check-transient-overmapping.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "72512da19ab8fe60"),
    "check-usecase-dto-placement.py::guard-zero": (2, 1, 0, "sentinel:대상0×1", "a660897a690a1683", "68ef0b7cef2acf9a"),
}


def lane_plan(fixtures_dir: Path) -> "list[tuple[str, str, str, Path | None, Path | None]]":
    """(키, 검사기, 레인, red 원천, green 원천) — red None = 레인 대기(실패 아님).

    git 3레인은 red 축만 갖는다(«정당 exit 0»은 green 이 아니라 그 레인의 기대값이다).
    위험 레인은 자기 good/ 을 green 축으로 갖는다(같은 커스텀 argv 로 exit 0·레코드 0)."""
    plan: "list[tuple[str, str, str, Path | None, Path | None]]" = []
    for script in CONVERTED:
        red, green = _LANE[script]
        plan.append((script, script, DEFAULT_LANE, fixtures_dir / red, fixtures_dir / green))
    for script in GIT_AFFECTED:
        for lane in GIT_LANES:
            plan.append((f"{script}::{lane}", script, lane, fixtures_dir / _LANE[script][0], None))
    for script, lane_dir, _extra in RISK_LANES:
        red_src: Path = fixtures_dir / lane_dir / "bad_rules"
        green_src: Path = fixtures_dir / lane_dir / "good"
        plan.append((f"{script}::{lane_dir}", script, lane_dir,
                     red_src if red_src.is_dir() else None,
                     green_src if green_src.is_dir() else None))
    for script, guard_fx, _a in GUARD_LANES:
        # 가드 레인(A-5 골든)은 red 축뿐 — «대상 0» 픽스처 자체가 발화 조건이라 green 짝 없음.
        plan.append((f"{script}::{GUARD_LANE}", script, GUARD_LANE, fixtures_dir / guard_fx, None))
    return plan


def _measure_one(script: str, auto: bool, src: Path, lane: str, scripts_dir: Path,
                 ) -> "tuple[int, str, list[dict], list[str]]":
    """한 (검사기×레인) 실행 — (exit, stdout, 레코드 목록, 레코드 채널 결손 목록)."""
    issues: "list[str]" = []
    with tempfile.TemporaryDirectory() as td:
        fx = Path(td) / "fixture"
        prepare_lane_copy(src, fx, lane)
        rec_path = Path(td) / "rec.jsonl"
        env = dict(os.environ)
        env["DJR_FINDINGS_JSON"] = str(rec_path)
        proc = subprocess.run(
            lane_argv(script, auto, str(fx), scripts_dir, lane),
            capture_output=True, text=True, cwd=str(ROOT), env=env,
            timeout=CHECKER_TIMEOUT_S,
        )
        records: "list[dict]" = []
        if rec_path.exists():
            for line in rec_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    issues.append(f"레코드 JSON 파싱 불가: {line[:80]!r}")
                    continue
                if isinstance(obj.get("file"), str):
                    obj["file"] = obj["file"].replace(str(fx), "<FX>")
                records.append(obj)
        # 라인 재구성 대조(M5)의 대칭 정규화 — 레코드 file 과 같은 <FX> 좌표계.
        stdout_norm = proc.stdout.replace(str(fx), "<FX>")
    return proc.returncode, stdout_norm, records, issues


def _summarize(returncode: int, records: "list[dict]") -> "tuple[int, int, int, str, str]":
    vio = [r for r in records if r.get("severity") == "violation"]
    info = [r for r in records if r.get("severity") == "info"]
    dist: "dict[str, int]" = {}
    for r in records:
        key = r.get("rule") or (f"sentinel:{r.get('sentinel')}" if r.get("sentinel")
                                else f"contract:{r.get('contract_ref')}")
        dist[key] = dist.get(key, 0) + 1
    dist_s = ",".join(f"{k}×{v}" for k, v in sorted(dist.items()))
    ids = sorted(
        (r.get("rule") or r.get("sentinel") or r.get("contract_ref") or "",
         r.get("file", ""), r.get("symbol") or "")
        for r in vio
    )
    ids_sha = hashlib.sha256(json.dumps(ids, ensure_ascii=False).encode()).hexdigest()[:16]
    return returncode, len(vio), len(info), dist_s, ids_sha


def _fingerprint(records: "list[dict]") -> str:
    """multiset fingerprint(신 열 — W6): (rule|sentinel|contract_ref, file, symbol,
    message, occurrence_index). occurrence_index = 동일 4-튜플 내 «방출 순» 서수.
    원소 정렬 후 json.dumps(ensure_ascii=False) 직렬화 sha16 — 전체는 무순서
    multiset 이되 동일 4-튜플 내 중복은 서수로 보존된다."""
    seen: "dict[tuple, int]" = {}
    elems: "list[list]" = []
    for r in records:
        key = (r.get("rule") or r.get("sentinel") or r.get("contract_ref") or "",
               r.get("file", ""), r.get("symbol") or "", r.get("message", ""))
        occ = seen.get(key, 0)
        seen[key] = occ + 1
        elems.append([*key, occ])
    elems.sort()
    return hashlib.sha256(json.dumps(elems, ensure_ascii=False).encode()).hexdigest()[:16]


def _record_oracle(script: str, records: "list[dict]") -> "list[str]":
    """findings/0 13필드 전건 oracle — 위반 목록(비어 있으면 통과)."""
    issues: "list[str]" = []
    run_ids = {r.get("run_id") for r in records}
    if records and len(run_ids) != 1:
        issues.append(f"run_id 단일 위반: {sorted(map(str, run_ids))}")
    for i, r in enumerate(records, start=1):
        rid = str(r.get("record_id"))
        if set(r) != set(_FIELDS):
            issues.append(f"{rid}: 필드 집합 이탈 — 초과 {sorted(set(r) - set(_FIELDS))} · "
                          f"결손 {sorted(set(_FIELDS) - set(r))}")
            continue
        if r["schema"] != "findings/0":
            issues.append(f"{rid}: schema {r['schema']!r} ≠ findings/0")
        exclusive = [k for k in ("rule", "sentinel", "contract_ref") if r[k] is not None]
        if len(exclusive) != 1:
            issues.append(f"{rid}: rule/sentinel/contract_ref 상호 배타 위반 — {exclusive or '전부 null'}")
        if r["rule"] is not None and not _RULE_FORM.fullmatch(str(r["rule"])):
            issues.append(f"{rid}: rule 이 무접두 #N 꼴이 아님 — {r['rule']!r}")
        if r["checker"] != script:
            issues.append(f"{rid}: checker {r['checker']!r} ≠ 파일명 {script!r}")
        if not (isinstance(r["file"], str) and r["file"]):
            issues.append(f"{rid}: file 이 비어 있음")
        if not (r["symbol"] is None or isinstance(r["symbol"], str)):
            issues.append(f"{rid}: symbol 형 이탈 — {type(r['symbol']).__name__}")
        if r["severity"] not in ("violation", "warning", "info"):
            issues.append(f"{rid}: severity 값 공간 밖 — {r['severity']!r}")
        if not (isinstance(r["message"], str) and r["message"]):
            issues.append(f"{rid}: message 가 비어 있음")
        if r["expression"] is not None:
            issues.append(f"{rid}: expression null 예약 위반 — {r['expression']!r}")
        if not (isinstance(r["ts"], str) and _TS_RE.fullmatch(r["ts"])):
            issues.append(f"{rid}: ts UTC ISO 8601(Z) 형식 위반 — {r['ts']!r}")
        want_rid = f"{r['run_id']}:{i:04d}"
        if r["record_id"] != want_rid:
            issues.append(f"record_id 유일·연속 증가 위반: {r['record_id']!r} (기대 {want_rid!r})")
    return issues


def _stream_items(stdout: str) -> "list[tuple[str, str]]":
    items: "list[tuple[str, str]]" = []
    for raw in stdout.splitlines():
        m = _VIOLATION_LINE.match(raw)
        if m:
            items.append(("violation", m.group(1)))
            continue
        m = _INFO_LINE.match(raw)
        if m:
            items.append(("info", m.group(1)))
    return items


def _reconstruct(r: dict) -> str:
    """레코드 필드만으로 stdout 라인을 재구성(포매터 계약 §1 — 라인=필드의 순수 함수).
    혼성 패널 M5: (severity, rule) 열 대조만으로는 message·file·계약·guard 문면
    drift 를 못 잡는다(변이 실증) — 재구성 라인의 stdout 실재·순서를 게이트한다."""
    rule = r.get("rule")
    sev, f, m = r.get("severity"), r.get("file", ""), r.get("message", "")
    if rule is not None:
        return f"[ⓓ{rule}] {f}: {m}" if sev == "info" else f"[{rule}] {f}: {m}"
    sent = r.get("sentinel")
    if sent is not None:
        # guard(대상-0 — file 은 "(target)" 고정)만 msg 원문 라인, 그 외 센티널
        # («합성»·«바인딩»·«분석» — F0 격리)은 rule 자리 판형 그대로.
        return m if f == "(target)" else f"[{sent}] {f}: {m}"
    return f"- {f}: {m}"  # 계약(rule=null + contract_ref)


def _reconstruct_compare(stdout: str, records: "list[dict]") -> "list[str]":
    """레코드 전건의 재구성 라인이 stdout 에 «순서대로 실재»하는지(strip 비교·
    subsequence 소비 — 자체가 ordered 대조라 strict 플래그와 무관 상시 게이트)."""
    hay = [ln.strip() for ln in stdout.splitlines()]
    pos = 0
    missing: "list[str]" = []
    for r in records:
        want = _reconstruct(r)
        try:
            pos = hay.index(want, pos) + 1
        except ValueError:
            missing.append(want)
    if missing:
        head = "; ".join(m[:90] for m in missing[:3])
        tail = f" 외 {len(missing) - 3}건" if len(missing) > 3 else ""
        return [f"레코드 재구성 라인이 stdout 에 없거나 순서 이탈(문면 drift·유실): {head}{tail}"]
    return []


def _stream_compare(stdout: str, records: "list[dict]", strict_order: bool) -> "list[str]":
    """stdout 위반·후보 라인 ↔ rule 레코드의 (severity, rule) 양방향 대조.

    기본 = 무순서 multiset(잉여·누락·중복 각각 검출). --strict-order = ordered 대조
    (순서 위반도 검출 — 3단계 순서 보존 방출 이행 후 기본 전환)."""
    stream = _stream_items(stdout)
    recs = [(r.get("severity"), r.get("rule")) for r in records
            if r.get("rule") is not None and r.get("severity") in ("violation", "info")]
    issues: "list[str]" = []
    cs: "Counter" = Counter(stream)
    cr: "Counter" = Counter(recs)
    only_stdout = cs - cr
    only_rec = cr - cs
    if only_stdout:
        issues.append("stdout 에만 있는 위반·후보 라인(레코드 누락): "
                      + ", ".join(f"{k}×{v}" for k, v in sorted(only_stdout.items())))
    if only_rec:
        issues.append("레코드에만 있는 항목(잉여·중복): "
                      + ", ".join(f"{k}×{v}" for k, v in sorted(only_rec.items())))
    if strict_order and not issues and stream != recs:
        first = next(i for i, (a, b) in enumerate(zip(stream, recs)) if a != b)
        issues.append(f"순서 불일치(최초 위치 {first}): stdout {stream[first]} ↔ record {recs[first]}")
    return issues


def _usage() -> int:
    print("사용: findings_count_matrix.py [--emit-expected] [--strict-order] "
          "[--scripts-dir <dir>] [--fixtures-dir <dir>]", file=sys.stderr)
    return 1


def main(argv: "list[str]") -> int:
    emit_expected = False
    # ordered 대조가 기본이다(V25 ⑤ — 후보 채널 11종 순서 보존 이행(e8f4ce0) 완결로
    # 전환·--strict-order 플래그는 호환 no-op 존치).
    strict_order = True
    scripts_dir: Path = S
    fixtures_dir: Path = F
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--emit-expected":
            emit_expected = True
        elif a == "--strict-order":
            strict_order = True
        elif a in ("--scripts-dir", "--fixtures-dir"):
            if len(argv) < i + 2:
                return _usage()
            val = argv[i + 1]
            i += 1
            if a == "--scripts-dir":
                scripts_dir = Path(val).resolve()
            else:
                fixtures_dir = Path(val).resolve()
        else:
            return _usage()
        i += 1

    roster = dict(REGISTRY)
    # 로스터·기대표 양방향 런타임 검사(적대 검증 레인 S 10번 — assert 는 PYTHONOPTIMIZE 로 소거된다).
    if len(CONVERTED) != 27:
        print(f"재료 결손: REGISTRY 로스터 27종 가정 위반({len(CONVERTED)})", file=sys.stderr)
        return 1
    if not emit_expected:
        default_keys = {k for k in EXPECTED if "::" not in k}
        git_keys = {k for k in EXPECTED if "::" in k and k.split("::", 1)[1] in GIT_LANES}
        want_git = {f"{s}::{lane}" for s in GIT_AFFECTED for lane in GIT_LANES}
        guard_keys = {k for k in EXPECTED if k.endswith(f"::{GUARD_LANE}")}
        want_guard = {f"{s}::{GUARD_LANE}" for s, _fx, _a in GUARD_LANES}
        if guard_keys != want_guard:
            print(f"재료 결손: 가드 레인 키 불일치 — 선언만: {sorted(want_guard - guard_keys)} · "
                  f"기대표만: {sorted(guard_keys - want_guard)}", file=sys.stderr)
            return 1
        risk_keys = set(EXPECTED) - default_keys - git_keys - guard_keys
        want_risk = {f"{s}::{d}" for s, d, _a in RISK_LANES}
        if default_keys != set(CONVERTED):
            print(f"재료 결손: 로스터↔EXPECTED 키 불일치 — 로스터만: {sorted(set(CONVERTED) - default_keys)} · "
                  f"기대표만: {sorted(default_keys - set(CONVERTED))}", file=sys.stderr)
            return 1
        if git_keys != want_git:
            print(f"재료 결손: git 레인 키 불일치 — 선언만: {sorted(want_git - git_keys)} · "
                  f"기대표만: {sorted(git_keys - want_git)}", file=sys.stderr)
            return 1
        if not risk_keys <= want_risk:
            print(f"재료 결손: 미선언 레인 키 — {sorted(risk_keys - want_risk)}", file=sys.stderr)
            return 1

    got: "dict[str, tuple[int, int, int, str, str]]" = {}
    prints: "dict[str, str]" = {}
    problems: "dict[str, list[str]]" = {}
    waiting: "list[str]" = []
    plan = lane_plan(fixtures_dir)
    for key, script, lane, red_src, green_src in plan:
        if red_src is None:
            waiting.append(key)
            continue
        code, stdout, records, issues = _measure_one(script, roster[script], red_src, lane, scripts_dir)
        issues += _record_oracle(script, records)
        # 위험 레인 관찰 보류는 3단계 이행 완결로 게이트에 편입됐다(V25 ⑤ — 구 문면
        # 비앵커 라인이 전건 [#N]/계약 문법으로 정형화되어 전 레인 동일 대조).
        issues += _stream_compare(stdout, records, strict_order)
        issues += _reconstruct_compare(stdout, records)
        got[key] = _summarize(code, records)
        prints[key] = _fingerprint(records)
        if issues:
            problems[key] = issues
        if green_src is not None:
            # 위험 레인의 green 은 red 와 같은 커스텀 argv 다(lane 그대로 — good/ 만 교체).
            g_code, g_stdout, g_records, g_issues = _measure_one(
                script, roster[script], green_src, lane, scripts_dir)
            if g_code != 0 or g_records:
                g_issues.append(f"green: exit {g_code} · 레코드 {len(g_records)} (기대 0·0)")
            g_issues += _record_oracle(script, g_records)
            # green 축도 게이트(V25 ⑤ — red 와 동일: 관찰 보류 종료).
            g_issues += _stream_compare(g_stdout, g_records, strict_order)
            g_issues += _reconstruct_compare(g_stdout, g_records)
            if g_issues:
                problems.setdefault(key, []).extend(g_issues)

    if emit_expected:
        # 실패 상태 세탁 거부(적대 검증 레인 S 1번): 기본 red 레인은 exit 2·레코드≥1 이어야
        # 하고, git 레인은 정당 exit {0,2}(exit 2 면 레코드≥1) — «편입이 깨진 것»은 새 정답이
        # 아니다. oracle·대조 위반도 emit 을 막는다(위반을 기대표에 얼릴 수 없다).
        bad: "list[str]" = []
        for key, script, lane, red_src, _g in plan:
            if red_src is None:
                continue
            e, v, inf, _d, _h = got[key]
            if lane in GIT_LANES:
                ok = e in (0, 2) and (e != 2 or (v + inf) >= 1)
            else:
                ok = e == 2 and (v + inf) >= 1
            if not ok or key in problems:
                bad.append(key)
        if bad:
            print(f"거부: red 레인 요건(레인별 정당 exit·레코드·oracle)을 만족하지 않는 키 — "
                  f"{sorted(bad)}. 결함을 기대표로 세탁할 수 없다", file=sys.stderr)
            for key in sorted(bad):
                for msg in problems.get(key, []):
                    print(f"  {key}: {msg}", file=sys.stderr)
            return 1
        print('EXPECTED: "dict[str, tuple[int, int, int, str, str, str]]" = {')
        for key, _script, _lane, red_src, _g in plan:
            if red_src is None:
                continue
            e, v, inf, dist, sha = got[key]
            print(f'    "{key}": ({e}, {v}, {inf}, "{dist}", "{sha}", "{prints[key]}"),')
        print("}")
        for key in waiting:
            print(f"# 레인 대기(픽스처 병행 제작 — 실측 후 등재): {key}", file=sys.stderr)
        return 0

    mismatch = 0
    for key, _script, _lane, red_src, _g in plan:
        if red_src is None:
            print(f"| `{key}` | 레인 대기(픽스처 병행 제작 — 실패 아님) |")
            if key in EXPECTED:
                mismatch += 1
                print(f"  ✗ {key}: 기대 존재·재료 부재")
            continue
        cur = got[key] + (prints[key],)
        e, v, inf, dist, sha, fp = cur
        want = EXPECTED.get(key)
        ok = cur == want and key not in problems
        if not ok:
            mismatch += 1
        mark = "✓" if ok else (f"✗ 기대 {want}" if cur != want else "✗ oracle·대조 위반")
        print(f"| `{key}` | exit {e} | violation {v} | info {inf} | {sha} | {fp} | {mark} |")
        for msg in problems.get(key, []):
            print(f"    · {msg}")
    print(f"레인 {len(got)} · 일치 {len(got) - mismatch} · 불일치 {mismatch} · "
          f"대기 {len(waiting)} (green 축 전수 0레코드·13필드 oracle·"
          f"stdout↔record {'ordered' if strict_order else 'multiset'} 대조 포함)")
    return 0 if mismatch == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
