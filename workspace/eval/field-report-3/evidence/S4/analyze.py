"""proto 결과 분석 — grep 대 proto 차분 · json.load 표본 · Mapping[str, object] 매개변수 · 오버라이드 · 조회표 이름 · 별표 인자."""
import json, re, sys, collections, subprocess
from pathlib import Path
S = Path("/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3")
label, repo, jsonl = sys.argv[1], S / sys.argv[2], S / "S4" / sys.argv[3]
recs = [json.loads(l) for l in open(jsonl, encoding="utf-8")]
hits = [r for r in recs if r["rule"] == "#647" and r["variant"] == "exact"]
jl = [r for r in recs if r["rule"] == "json-load"]
print(f"##### {label}")
# 1. grep(보고자 명령·framework+application·비테스트) 대 proto 줄 차분
roots = [d for d in ("framework", "application") if (repo / d).is_dir()]
out = subprocess.run(["grep", "-rnE", "--include=*.py", r"(dict|Mapping)\[str, (object|Any)\]", *roots], cwd=repo, capture_output=True, text=True).stdout
grep_lines = {}
for l in out.splitlines():
    f, ln, txt = l.split(":", 2)
    if "/test/" in f: continue
    grep_lines[(f, int(ln))] = txt
proto_lines = {(h["file"], h["own_line"]) for h in hits} | {(h["file"], h["line"]) for h in hits}
proto_fa = {k for k in proto_lines if k[0].split("/")[0] in ("framework", "application")}
only_grep = {k: v for k, v in grep_lines.items() if k not in proto_lines}
only_proto = sorted(k for k in proto_fa if k not in grep_lines)
cat = collections.Counter()
samples = collections.defaultdict(list)
for (f, ln), txt in only_grep.items():
    s = txt.strip()
    if s.startswith("#"): c = "주석(comment)"
    elif "cast(" in s: c = "cast(\"…\") 문자열"
    elif re.match(r"^(type\s+)?\w+\s*(:\s*TypeAlias\s*)?=\s*", s) and not re.match(r"^\w+\s*:\s*(?!TypeAlias)", s): c = "별칭 대입(Assign/type 문)"
    elif re.match(r'^("""|\'\'\'|\w)', s) and ("`" in s or s.endswith(".") or s.endswith("다")): c = "docstring/산문"
    elif "TypeAdapter" in s or "Protocol" in s or "isinstance" in s: c = "표현식 안(TypeAdapter/isinstance)"
    else: c = "기타"
    cat[c] += 1
    if len(samples[c]) < 4: samples[c].append(f"{f}:{ln}: {s[:110]}")
print(f"grep 줄 {len(grep_lines)} · proto 줄(framework+application) {len(proto_fa)} · grep에만 {len(only_grep)} · proto에만 {len(only_proto)}")
for c, n in cat.most_common(): print(f"  grep에만 — {c}: {n}"); [print("      ", s) for s in samples[c]]
print("  proto에만(예: 다중 행 시그니처·테스트 밖 factories 등) 표본:"); [print("      ", f"{f}:{ln}") for f, ln in only_proto[:6]]
# 2. json.load 표본
print(f"json.load(s) 호출 {len(jl)} · 후보 {sum(j['candidate'] for j in jl)}")
print("  소비자 분포:", dict(collections.Counter(j['consumer'] for j in jl).most_common(15)))
for j in jl[:10]: print(f"    {j['file']}:{j['line']} [{j['consumer']}] {j['src'][:120]}")
# 3. Mapping[str, object] top 매개변수
mp = [h for h in hits if h["site"] == "sig-param" and h["container"] == "Mapping" and h["value"] == "object" and h["position"] == "top"]
print(f"Mapping[str, object] top 매개변수 {len(mp)} — 함수명 분포:", dict(collections.Counter(h['fn'] for h in mp).most_common(20)))
for h in mp[:12]: print(f"    {h['file']}:{h['own_line']} {h['fn']}({h['label']}: {h['text']})")
# 4. 프레임워크 오버라이드 함수명
OVR = {"clean", "clean_fields", "get_context_data", "get_queryset", "get_form_kwargs", "formfield", "to_python", "from_db_value",
       "get_prep_value", "save_model", "save_related", "get_extra_context", "resolve", "json_schema_extra", "process_request",
       "process_response", "__call__", "get_form", "form_valid", "get_initial", "changelist_view", "change_view", "add_view",
       "render", "get_serializer_context", "deconstruct", "validate", "to_representation", "to_internal_value", "get_urls",
       "response_change", "get_fieldsets", "get_readonly_fields", "handle", "add_arguments", "__init__", "default", "dispatch"}
ov = [h for h in hits if h["fn"] in OVR and h["site"].startswith("sig")]
print(f"프레임워크 오버라이드로 보이는 시그니처 히트 {len(ov)}:", dict(collections.Counter((h['fn'], h['site'], h['value']) for h in ov).most_common(12)))
for h in ov[:8]: print(f"    {h['file']}:{h['line']} {h['fn']} {h['label']}: {h['text']}")
# 5. 조회표(키가 데이터) 이름 프록시
LOOK = re.compile(r"(by_|_by$|_by\b|index|map$|_map|registry|table|lookup|cache|counts?$|_of_|catalog|dispatch|handlers?|validators?|mergers?)", re.I)
top = [h for h in hits if h["position"] == "top"]
lk = [h for h in top if LOOK.search(h["label"] or "")]
print(f"top 히트 {len(top)} 중 라벨이 조회표 형(by_/index/map/registry/table/…) {len(lk)} ({len(lk)*100//max(1,len(top))}%) — 예:", [f"{h['label']}: {h['text']}" for h in lk[:6]])
# 6. **kwargs 주석 분포
kw = subprocess.run(["grep", "-rhoE", "--include=*.py", r"\*\*\w+: *[A-Za-z_\[\], |.]+", *roots], cwd=repo, capture_output=True, text=True).stdout
print("**kwargs 주석 분포(상위):", dict(collections.Counter(re.sub(r"\*\*\w+: *", "", l.strip()) for l in kw.splitlines()).most_common(6)))
# 7. dumps/serialize 계열 함수의 히트
ser = [h for h in hits if h["fn"] and re.search(r"dumps|serial|to_json|canonical|digest|payload|encode", h["fn"], re.I)]
print(f"직렬화 계열 함수(dumps/serial/to_json/canonical/digest/payload/encode) 시그니처 히트 {len(ser)} — 예:", [f"{h['fn']}:{h['text']}" for h in ser[:6]])
# 8. TypeIs/TypeGuard 안 (좁히기 도우미 — R-3448 취지)
tg = [h for h in hits if "TypeIs" in (h.get("text") or "") or True and h["site"] == "sig-return" and h["position"] == "nested"]
print(f"sig-return nested 히트 {len([h for h in hits if h['site']=='sig-return' and h['position']=='nested'])} — 반환 주석 원문 상위:", )
rets = subprocess.run(["grep", "-rhoE", "--include=*.py", r"-> *(TypeIs|TypeGuard)\[(Mapping|dict)\[str, *(object|Any)\]\]", *roots], cwd=repo, capture_output=True, text=True).stdout
print("   TypeIs/TypeGuard[Mapping|dict[str, object|Any]] 반환:", len(rets.splitlines()), collections.Counter(rets.splitlines()).most_common(3))
