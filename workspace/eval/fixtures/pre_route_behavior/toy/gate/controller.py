"""설정으로 뺀 경로 — 글자 목록(`.` 포함) · 정규식 목록(표 `exempt` · `exempt_pattern`)."""
from ninja import Router

router = Router()


@router.get("/open/{name}/status", response={200: dict})
def open_status(request, name: str):
    return {"name": name}


@router.get("/ping", response={200: dict})
def ping(request):
    return {"ok": True}


@router.get("/pong", response={200: dict})
def pong(request):
    return {"ok": True}


@router.get("/slot/{int:slot}", response={200: dict})
def slot_status(request, slot: int):
    return {"slot": slot}


@router.get("/number/{int:number}", response={200: dict})
def number_status(request, number: int):
    return {"number": number}


@router.get("/head/tail", response={200: dict})
def head_tail(request):
    return {"ok": True}


@router.get("/list.csv", response={200: dict})
def list_csv(request):
    return {"ok": True}


@router.get("/list-csv", response={200: dict})
def list_dash_csv(request):
    return {"ok": True}


@router.post("/hook/{kind}", response={200: dict})
def hook(request, kind: str):
    return {"kind": kind}


@router.put("/hook/{kind}", response={200: dict})
def hook_replace(request, kind: str):
    return {"kind": kind}
