"""spring 사본에서 ninja OpenAPI JSON 을 덤프한다(DB 접속 없음 · get_openapi_schema 만)."""
import hashlib, json, os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spring_dream_server.settings.test")
sys.path.insert(0, os.getcwd())
import django
django.setup()
from spring_dream_server.api import api  # noqa: E402
schema = api.get_openapi_schema()
doc = json.loads(json.dumps(schema, default=str))
out = sys.argv[1]
with open(out, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1, sort_keys=True)
comps = doc.get("components", {}).get("schemas", {})
target = comps.get("EvidenceProvisionResponseSchema")
canon = json.dumps(target, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
print("EvidenceProvisionResponseSchema sha256", hashlib.sha256(canon).hexdigest(), "present" if target else "MISSING")
# 관련 6 컴포넌트(EvidencePrepared·Abstained 등) 묶음 sha
related = {k: v for k, v in comps.items() if k in {"EvidenceProvisionResponseSchema", "EvidencePrepared", "Abstained", "ProvisionTrace", "EvidenceExcerptView", "CalculationProjection"}}
print("related keys", sorted(related))
print("related sha256", hashlib.sha256(json.dumps(related, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest())
for path, item in doc.get("paths", {}).items():
    for method, op in item.items():
        if isinstance(op, dict) and op.get("operationId") == "fortune_reading_prepare_evidence_bundle":
            print("operation", method.upper(), path)
            for status, resp in sorted(op.get("responses", {}).items()):
                print("  ", status, json.dumps(resp.get("content", {}).get("application/json", {}).get("schema"), ensure_ascii=False, sort_keys=True))
print("discriminator in target:", json.dumps(target.get("discriminator") if target else None, ensure_ascii=False))
print("oneOf/anyOf in target:", [k for k in (target or {}) if k in ("oneOf", "anyOf")])
