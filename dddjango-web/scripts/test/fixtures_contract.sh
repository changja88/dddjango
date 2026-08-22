#!/usr/bin/env bash
# extract_contract.py 픽스처 테스트 — 미니 OpenAPI 문서로 절단 동작을 검증한다.
# F1 정확 선별 / F2 $ref 전이 폐쇄 / F3 메서드 생략=전 메서드(F1의 positive-control 짝)
# F4 인용 path 부재 exit 1+근사 후보(짝: F1 exit 0) / F5 Swagger 2.0 거부+3.x 수용 짝
# F6 비JSON 파싱 실패 / F7 dangling ref [warn](짝: F1 무경고) / F8 webhooks 비복사 [warn]
# F9 결정론(2회 실행 바이트 동일) / F10 빈 paths-file exit 1
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
EX="$SCRIPTS/extract_contract.py"
PY="${PYTHON:-python3}"
PASS=0; FAIL=0

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

run() { # run <json> <paths-file> <out-file> — E/OUT/ERR 설정(stdout·stderr 분리 캡처)
  "$PY" "$EX" "$1" --paths "$2" --out "$3" >"$T/stdout.txt" 2>"$T/stderr.txt"; E=$?
  OUT=$(cat "$T/stdout.txt"); ERR=$(cat "$T/stderr.txt")
}

assert() { # assert <이름> <기대exit> <있어야 할 패턴|-> <없어야 할 패턴|-> <실제exit> <검사 대상 텍스트>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" text="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -q "$want" <<<"$text" && ok=0
  [ "$unwant" != "-" ] && grep -q "$unwant" <<<"$text" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$text" | head -20 | sed 's/^/    /'
  fi
}

# ---------- 공용 미니 동결본: 인용 path(2메서드+공유 parameters) + 비인용 path + 스키마 체인
P="$T/base"; mkdir -p "$P"
cat > "$P/openapi-full.json" <<'EOF'
{
  "openapi": "3.0.0",
  "info": {"title": "t", "version": "1"},
  "security": [{"bearer": []}],
  "paths": {
    "/api/v1/members/{id}": {
      "parameters": [{"name": "id", "in": "path", "required": true, "schema": {"type": "string"}}],
      "get": {"responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Member"}}}}}},
      "delete": {"responses": {"204": {"description": "x"}}}
    },
    "/api/v1/other": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Other"}}}}}}}
  },
  "components": {
    "securitySchemes": {"bearer": {"type": "http", "scheme": "bearer"}},
    "schemas": {
      "Member": {"type": "object", "properties": {"photo": {"$ref": "#/components/schemas/Photo"}}},
      "Photo": {"type": "object", "properties": {"url": {"type": "string"}}},
      "Other": {"type": "object"}
    }
  }
}
EOF
echo "GET /api/v1/members/{id}" > "$P/cited.txt"

# ---------- F1: 정확 선별 — 인용 path+메서드만 남고 보존 목록은 유지, [warn] 0, 요약은 stdout
run "$P/openapi-full.json" "$P/cited.txt" "$P/server-contract.json"
C=$(cat "$P/server-contract.json" 2>/dev/null || echo "")
ok=1
[ "$E" = 0 ] || ok=0
grep -q '"/api/v1/members/{id}"' <<<"$C" || ok=0   # 인용 path 선별
grep -q '"parameters"' <<<"$C" || ok=0             # path item 공유 파라미터 보존
grep -q '"security"' <<<"$C" || ok=0               # 루트 security 보존
grep -q '"securitySchemes"' <<<"$C" || ok=0        # securitySchemes 전체 보존
grep -q '"/api/v1/other"' <<<"$C" && ok=0          # 비인용 path 미포함
grep -q '"delete"' <<<"$C" && ok=0                 # 비인용 메서드 제거
grep -q '\[warn\]' <<<"$ERR" && ok=0               # 무결 문서 — 경고 없음(F7의 positive-control 짝)
grep -q '\[extract-contract\] paths 1개' <<<"$OUT" || ok=0  # 요약 1줄은 stdout
if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS F1 정확 선별·보존·요약 stdout"; else
  FAIL=$((FAIL+1)); echo "FAIL F1 (exit=$E)"; { echo "$C" | head -30; echo "$ERR"; } | sed 's/^/    /'
fi

# ---------- F2: $ref 전이 폐쇄 — Member→Photo 체인 포함, 비인용 Other 미포함
ok=1
grep -q '"Member"' <<<"$C" || ok=0
grep -q '"Photo"' <<<"$C" || ok=0                  # 전이 폐쇄(Member가 참조)
grep -q '"Other"' <<<"$C" && ok=0                  # 비인용 스키마 미포함
if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS F2 \$ref 전이 폐쇄"; else
  FAIL=$((FAIL+1)); echo "FAIL F2"; echo "$C" | head -30 | sed 's/^/    /'
fi

# ---------- F3: 메서드 생략 = 그 path 전 메서드 — F1(메서드 지정 시 delete 제거)의 positive-control 짝
echo "/api/v1/members/{id}" > "$P/cited-bare.txt"
run "$P/openapi-full.json" "$P/cited-bare.txt" "$P/bare.json"
C=$(cat "$P/bare.json" 2>/dev/null || echo "")
ok=1
[ "$E" = 0 ] || ok=0
grep -q '"get"' <<<"$C" || ok=0
grep -q '"delete"' <<<"$C" || ok=0                 # 전 메서드 보존
if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS F3 메서드 생략=전 메서드"; else
  FAIL=$((FAIL+1)); echo "FAIL F3 (exit=$E)"; echo "$C" | head -30 | sed 's/^/    /'
fi

# ---------- F4: 인용 path 부재 — exit 1 + stderr «인용 path가 동결본에 없음» + 유사 path 근사 후보
#             (positive-control 짝: F1 — 같은 동결본에서 실존 path 인용은 exit 0)
echo "GET /api/v1/members/{memberId}" > "$P/cited-miss.txt"
run "$P/openapi-full.json" "$P/cited-miss.txt" "$P/x.json"
assert "F4a 인용 path 부재 exit 1" 1 "인용 path가 동결본에 없음" - "$E" "$ERR"
assert "F4b 근사 후보 병기(파라미터명 차이)" 1 "유사 path 존재: /api/v1/members/{id}" - "$E" "$ERR"

# ---------- F5: Swagger 2.0 거부 + 3.x 수용 positive-control 짝
P5="$T/f5"; mkdir -p "$P5"
cat > "$P5/swagger.json" <<'EOF'
{"swagger": "2.0", "info": {"title": "t", "version": "1"}, "paths": {"/api/v1/ping": {"get": {"responses": {"200": {"description": "ok"}}}}}}
EOF
echo "GET /api/v1/ping" > "$P5/cited.txt"
run "$P5/swagger.json" "$P5/cited.txt" "$P5/x.json"
assert "F5a Swagger 2.0 거부 exit 1" 1 "Swagger 2.0" - "$E" "$ERR"
cat > "$P5/openapi3.json" <<'EOF'
{"openapi": "3.0.0", "info": {"title": "t", "version": "1"}, "paths": {"/api/v1/ping": {"get": {"responses": {"200": {"description": "ok"}}}}}}
EOF
run "$P5/openapi3.json" "$P5/cited.txt" "$P5/ok.json"
assert "F5b 같은 문서 3.x는 수용(positive control)" 0 "paths 1개" - "$E" "$OUT"

# ---------- F6: 비JSON 파싱 실패 — exit 1 + stderr «파싱 실패»
P6="$T/f6"; mkdir -p "$P6"
echo "openapi: 3.0.0" > "$P6/openapi.yaml"
echo "GET /api/v1/ping" > "$P6/cited.txt"
run "$P6/openapi.yaml" "$P6/cited.txt" "$P6/x.json"
assert "F6 비JSON(YAML) 파싱 실패 exit 1" 1 "파싱 실패" - "$E" "$ERR"

# ---------- F7: dangling ref — exit 0 유지 + stderr [warn] (positive-control 짝: F1 무경고)
P7="$T/f7"; mkdir -p "$P7"
cat > "$P7/openapi-full.json" <<'EOF'
{
  "openapi": "3.0.0",
  "info": {"title": "t", "version": "1"},
  "paths": {
    "/api/v1/ghosts": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Ghost"}}}}}}}
  },
  "components": {"schemas": {"Real": {"type": "object"}}}
}
EOF
echo "GET /api/v1/ghosts" > "$P7/cited.txt"
run "$P7/openapi-full.json" "$P7/cited.txt" "$P7/out.json"
assert "F7a dangling ref [warn] stderr·exit 0 유지" 0 "\[warn\] dangling ref: #/components/schemas/Ghost" - "$E" "$ERR"
assert "F7b [warn]은 stdout 오염 없음(요약만)" 0 "\[extract-contract\] paths 1개" "\[warn\]" "$E" "$OUT"

# ---------- F8: 비복사 항목(webhooks) — exit 0 + stderr [warn]
P8="$T/f8"; mkdir -p "$P8"
cat > "$P8/openapi-full.json" <<'EOF'
{
  "openapi": "3.1.0",
  "info": {"title": "t", "version": "1"},
  "webhooks": {"newThing": {"post": {"responses": {"200": {"description": "ok"}}}}},
  "paths": {"/api/v1/ping": {"get": {"responses": {"200": {"description": "ok"}}}}}
}
EOF
echo "GET /api/v1/ping" > "$P8/cited.txt"
run "$P8/openapi-full.json" "$P8/cited.txt" "$P8/out.json"
assert "F8 webhooks 비복사 [warn]" 0 "\[warn\] webhooks 비복사" - "$E" "$ERR"

# ---------- F9: 결정론 — 같은 입력 2회 실행 산출 바이트 동일
run "$P/openapi-full.json" "$P/cited.txt" "$P/det-1.json"
run "$P/openapi-full.json" "$P/cited.txt" "$P/det-2.json"
if cmp -s "$P/det-1.json" "$P/det-2.json"; then PASS=$((PASS+1)); echo "PASS F9 결정론(2회 바이트 동일)"; else
  FAIL=$((FAIL+1)); echo "FAIL F9 결정론"; diff "$P/det-1.json" "$P/det-2.json" | head -10 | sed 's/^/    /'
fi

# ---------- F10: 빈 paths-file — exit 1 + «인용 path 0개»
: > "$P/empty.txt"
run "$P/openapi-full.json" "$P/empty.txt" "$P/x.json"
assert "F10 빈 paths-file exit 1" 1 "인용 path 0개" - "$E" "$ERR"

echo "---"
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ] || exit 1
