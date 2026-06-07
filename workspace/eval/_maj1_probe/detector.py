"""maj1 백스톱 정밀도 시제품 (STANDARD 아님 · workspace 임시 조사).

탐지 표적: API 경계에서 `OperationalError`/`DatabaseError`(transient 인프라 예외)를 처리하는
핸들러가 영구장애 변종을 구별하는 분기 없이 retryable status(503/409)로 *무조건* 매핑하는가
(= maj1 과잉매핑). 거짓양성 0 + known-bad 차단을 시험한다.

판정:
- 대상 판별: 함수가 (a) `@*.exception_handler(OperationalError|DatabaseError)` 데코를 갖거나
  (b) 파라미터에 `exc: OperationalError|DatabaseError` 어노테이션을 가짐(데코/register 방식 독립).
- 분기 신호(has_branch): If/IfExp, 또는 retryable/sqlstate/pgcode 호출, 또는 __cause__/__context__
  /sqlstate/pgcode 속성 접근(시그니처 판별).
- VIOLATION: retryable(503/409) 반환 ∧ 분기 부재. 그 외 PASS.
"""
import ast
import sys

RETRYABLE = {503, 409}
TARGET_EXC = {"OperationalError", "DatabaseError"}
BRANCH_CALL_HINTS = ("retryable", "sqlstate", "pgcode")
BRANCH_ATTRS = {"__cause__", "__context__", "sqlstate", "pgcode"}


def _exc_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def is_target_handler(func):
    # (a) 데코레이터 @*.exception_handler(OperationalError|DatabaseError)
    for dec in func.decorator_list:
        if isinstance(dec, ast.Call):
            fn = dec.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            if nm == "exception_handler":
                for a in dec.args:
                    if _exc_name(a) in TARGET_EXC:
                        return True
    # (b) 파라미터 exc: OperationalError|DatabaseError 어노테이션
    for arg in func.args.args:
        if arg.annotation is not None and _exc_name(arg.annotation) in TARGET_EXC:
            return True
    return False


def has_branch(func):
    for node in ast.walk(func):
        if isinstance(node, (ast.If, ast.IfExp)):
            return True
        if isinstance(node, ast.Call):
            fn = node.func
            nm = (fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")) or ""
            if any(h in nm.lower() for h in BRANCH_CALL_HINTS):
                return True
        if isinstance(node, ast.Attribute) and node.attr in BRANCH_ATTRS:
            return True
    return False


def returns_retryable(func):
    for node in ast.walk(func):
        if isinstance(node, ast.keyword) and node.arg in ("status", "status_code"):
            if isinstance(node.value, ast.Constant) and node.value.value in RETRYABLE:
                return True
        if isinstance(node, ast.Call):
            for a in node.args:
                if isinstance(a, ast.Constant) and a.value in RETRYABLE:
                    return True
    return False


def scan(path):
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    rows = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_target_handler(node):
            br = has_branch(node)
            rt = returns_retryable(node)
            verdict = "VIOLATION" if (rt and not br) else "PASS"
            rows.append((node.name, node.lineno, br, rt, verdict))
    return rows


if __name__ == "__main__":
    any_violation = False
    for path in sys.argv[1:]:
        rows = scan(path)
        print(f"\n# {path}")
        if not rows:
            print("  (대상 핸들러 없음)")
        for name, ln, br, rt, verdict in rows:
            mark = "❌" if verdict == "VIOLATION" else "✅"
            print(f"  {mark} {verdict:9} {name}:{ln}  branch={br} retryable={rt}")
            if verdict == "VIOLATION":
                any_violation = True
    sys.exit(2 if any_violation else 0)
