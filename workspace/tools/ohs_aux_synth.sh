#!/usr/bin/env bash
# OHS 보조 계약 타입 면제 — 합성 검증 8방향 (계획 v2 §3-E)
set -u
SRC=/Users/hyun/Desktop/dddjango/workspace/eval/fixtures/context_isolation/good
CHK=/Users/hyun/Desktop/dddjango/dddjango/scripts/check-context-isolation.py
T=$(mktemp -d)
RESP=application/orders/driving_layer/open_host_service/order_lookup/contract/response/get_order_response.py
REQ=application/orders/driving_layer/open_host_service/order_lookup/contract/request/get_order_request.py
PASS=0; FAIL=0

run_case() { # run_case <이름> <있어야|-> <없어야|->
  local name="$1" want="$2" unwant="$3"
  local out; out=$(python3 "$CHK" "$T/p" 2>&1); local ok=1
  [ "$want" != "-" ] && ! grep -q "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -qE "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name"; grep -E '#160|#157|#484|#455|#162' <<<"$out" | head -6 | sed 's/^/    /'
  fi
}
fresh() { rm -rf "$T/p"; cp -R "$SRC" "$T/p"; }

# 1. billing 판형 green — 인용 forward-ref·frozen/slots/kw_only·status:str·Response 뒤 정의
fresh; cat > "$T/p/$RESP" <<'EOF'
from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderResponse:
    code: str
    order_id: str
    evidences: tuple["OwnerMergeEvidence", ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class OwnerMergeEvidence:
    source_owner_id: str
    target_owner_id: str
    status: str
    created_at: str
EOF
run_case "1 billing 판형(인용 참조 aux) green" - '#160|#484|#455|#162'

# 2. 미참조 공개 aux → red
fresh; cat > "$T/p/$RESP" <<'EOF'
from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderResponse:
    code: str
    order_id: str


@dataclass(frozen=True)
class OrphanEvidence:
    x: str
EOF
run_case "2 미참조 aux red(#160+#484)" '#160' -
python3 "$CHK" "$T/p" 2>&1 | grep -q '#484' && { PASS=$((PASS+1)); echo "PASS 2b #484 동반"; } || { FAIL=$((FAIL+1)); echo "FAIL 2b"; }

# 3. Result 접미 참조 → red (#484 — R-0531 어휘 혼용)
fresh; cat > "$T/p/$RESP" <<'EOF'
from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderResponse:
    code: str
    extra: "GetOrderExtraResult"


@dataclass(frozen=True)
class GetOrderExtraResult:
    x: str
EOF
run_case "3 Result 접미 참조 red" '#484' -

# 4. 비-dataclass(Enum) 참조 → red
fresh; cat > "$T/p/$RESP" <<'EOF'
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class GetOrderResponse:
    code: str
    status: "MergeStatus"


class MergeStatus(Enum):
    DONE = "done"
EOF
run_case "4 Enum 참조 red(#484)" '#484' -

# 5. Response 접미 2개 → red (#160)
fresh; cat > "$T/p/$RESP" <<'EOF'
from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderResponse:
    code: str


@dataclass(frozen=True)
class OtherOrderResponse:
    code: str
EOF
run_case "5 Response 2개 red(#160)" '#160' -

# 6. 공개 클래스 0(비공개+alias) → 현행 그대로 무발화(강화 밀수 없음)
fresh; cat > "$T/p/$RESP" <<'EOF'
from dataclasses import dataclass


@dataclass(frozen=True)
class _GetOrderResponse:
    code: str


GetOrderResponse = _GetOrderResponse
EOF
run_case "6 공개 0개 파일 불변(무발화)" - '#160|#484'

# 7. request 갈래 aux green (갈래 중립)
fresh; cat > "$T/p/$REQ" <<'EOF'
from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderRequest:
    order_id: str
    filters: tuple["OrderFilter", ...]


@dataclass(frozen=True)
class OrderFilter:
    field: str
    value: str
EOF
run_case "7 request aux green" - '#157|#484'

# 8. aux 의 freeform 필드에 #455 불발화(주 계약 한정)
fresh; cat > "$T/p/$RESP" <<'EOF'
from dataclasses import dataclass


@dataclass(frozen=True)
class GetOrderResponse:
    code: str
    evidence: "AuditEvidence"


@dataclass(frozen=True)
class AuditEvidence:
    reason: str
EOF
run_case "8 aux freeform 필드 #455 불발화" - '#455'

echo "합계: PASS=$PASS FAIL=$FAIL"; rm -rf "$T"; [ $FAIL = 0 ]
