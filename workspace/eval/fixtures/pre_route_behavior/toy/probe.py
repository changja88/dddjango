"""경로 앞 응답 동작 탐침 — 장난감 프로젝트 안에서 `.venv-probe` 인터프리터로 돈다(pre_route_behavior_smoke 가 부른다).

입력 JSON(argv[1]): {"mode": "full" | "fail", "settings": {...}, "requests": [...], "out": <결과 JSON 경로>}.
full = 루트 API 넷의 마운트된 생성 문서(`/<ns>/openapi.json`)와 요청마다 실제 응답(status · 머리 · 몸통).
fail = 표가 틀렸을 때 — `manage.py check` · 보통 경로 요청은 서고, 문서를 만들 때만 실패하는지(예외 꼴 · 마운트 문서 status).
"""
import json
import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "toyproj.settings"

import django  # noqa: E402

django.setup()

from django.core.management import call_command  # noqa: E402
from django.test import Client, override_settings  # noqa: E402

NAMESPACES = ("api", "api2", "api3", "apib")


def _apis():
    from toyproj.api import api, api2, apib
    from toyproj.extra_api import api3
    return {"api": api, "api2": api2, "api3": api3, "apib": apib}


def _send(spec):
    client = Client(enforce_csrf_checks=spec.get("client") == "csrf", raise_request_exception=False)
    headers = dict(spec.get("headers", {}))
    method = getattr(client, spec["method"])
    kwargs = {}
    if "data" in spec:
        kwargs["data"] = spec["data"]
    if "content_type" in spec:
        kwargs["content_type"] = spec["content_type"]
    path = spec["path"] + (("?" + spec["query"]) if spec.get("query") else "")
    response = None
    with override_settings(**spec.get("settings", {})):
        for _ in range(int(spec.get("repeat", 1))):
            response = method(path, **kwargs, **headers)
    return {"status": response.status_code, "headers": dict(response.headers),
            "body": response.content.decode("utf-8", "replace")}


def full(plan):
    out = {"docs": {}, "responses": {}}
    for ns in NAMESPACES:
        response = Client(raise_request_exception=False).get(f"/{ns}/openapi.json")
        out["docs"][ns] = {"status": response.status_code,
                           "doc": json.loads(response.content) if response.status_code == 200 else None}
    for spec in plan["requests"]:
        out["responses"][spec["id"]] = _send(spec)
    return out


def fail(plan):
    out = {}
    try:
        call_command("check", verbosity=0)
        out["check"] = "ok"
    except Exception as exc:  # noqa: BLE001
        out["check"] = f"{type(exc).__name__}: {exc}"
    out["plain_request"] = Client(raise_request_exception=False).get("/api/health").status_code
    out["schema"] = {}
    for ns, api in _apis().items():
        try:
            api.get_openapi_schema()
            out["schema"][ns] = "ok"
        except Exception as exc:  # noqa: BLE001
            out["schema"][ns] = f"{type(exc).__name__}: {exc}"
        out.setdefault("mounted", {})[ns] = Client(raise_request_exception=False).get(f"/{ns}/openapi.json").status_code
    return out


def main():
    with open(sys.argv[1], encoding="utf-8") as fh:
        plan = json.load(fh)
    with override_settings(**plan.get("settings", {})):
        result = full(plan) if plan["mode"] == "full" else fail(plan)
    with open(plan["out"], "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False)


if __name__ == "__main__":
    main()
