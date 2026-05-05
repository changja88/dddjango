지정된 fixture 경로 `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 작업 디렉터리 `/private/tmp/dddjango-codex-eval`도 비어 있었습니다. 그래서 빈 프로젝트 기준으로 FastAPI health check API를 추가하는 unified diff를 제안합니다.

```diff
diff --git a/app/__init__.py b/app/__init__.py
new file mode 100644
index 0000000..e69de29
diff --git a/app/main.py b/app/main.py
new file mode 100644
index 0000000..a1d5f2b
--- /dev/null
+++ b/app/main.py
@@ -0,0 +1,12 @@
+from fastapi import FastAPI
+
+
+app = FastAPI(title="Health Check API")
+
+
+@app.get("/health")
+def health_check() -> dict[str, str]:
+    return {"status": "ok"}
diff --git a/pyproject.toml b/pyproject.toml
new file mode 100644
index 0000000..c0f3a8a
--- /dev/null
+++ b/pyproject.toml
@@ -0,0 +1,16 @@
+[project]
+name = "health-check-api"
+version = "0.1.0"
+description = "Simple FastAPI health check API"
+requires-python = ">=3.11"
+dependencies = [
+    "fastapi>=0.115.0",
+    "uvicorn[standard]>=0.30.0",
+]
+
+[project.optional-dependencies]
+test = [
+    "pytest>=8.0.0",
+    "httpx>=0.27.0",
+]
diff --git a/tests/test_health.py b/tests/test_health.py
new file mode 100644
index 0000000..e037d7e
--- /dev/null
+++ b/tests/test_health.py
@@ -0,0 +1,10 @@
+from fastapi.testclient import TestClient
+
+from app.main import app
+
+
+def test_health_check_returns_ok() -> None:
+    client = TestClient(app)
+
+    response = client.get("/health")
+
+    assert response.status_code == 200
+    assert response.json() == {"status": "ok"}
```

실행은 `uvicorn app.main:app --reload`이고, health check는 `GET /health`입니다.