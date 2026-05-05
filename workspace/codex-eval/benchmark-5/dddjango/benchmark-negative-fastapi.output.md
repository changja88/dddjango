지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리도 비어 있었습니다. 그래서 빈 프로젝트에 바로 적용 가능한 최소 FastAPI health check API diff로 제공합니다.

```diff
diff --git a/pyproject.toml b/pyproject.toml
new file mode 100644
index 0000000..d8d7c4a
--- /dev/null
+++ b/pyproject.toml
@@ -0,0 +1,15 @@
+[project]
+name = "fastapi-health-check"
+version = "0.1.0"
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
+
+[tool.pytest.ini_options]
+pythonpath = ["."]
diff --git a/app/__init__.py b/app/__init__.py
new file mode 100644
index 0000000..e69de29
--- /dev/null
+++ b/app/__init__.py
@@ -0,0 +1 @@
diff --git a/app/main.py b/app/main.py
new file mode 100644
index 0000000..a71b6f6
--- /dev/null
+++ b/app/main.py
@@ -0,0 +1,12 @@
+from fastapi import FastAPI
+
+
+app = FastAPI(title="Health Check API")
+
+
+@app.get("/health", tags=["health"])
+def health_check() -> dict[str, str]:
+    return {"status": "ok"}
+
+
+@app.get("/", tags=["health"])
+def root() -> dict[str, str]:
+    return health_check()
diff --git a/tests/test_health.py b/tests/test_health.py
new file mode 100644
index 0000000..98d6d90
--- /dev/null
+++ b/tests/test_health.py
@@ -0,0 +1,17 @@
+from fastapi.testclient import TestClient
+
+from app.main import app
+
+
+client = TestClient(app)
+
+
+def test_health_check_returns_ok() -> None:
+    response = client.get("/health")
+
+    assert response.status_code == 200
+    assert response.json() == {"status": "ok"}
+
+
+def test_root_returns_ok() -> None:
+    response = client.get("/")
+
+    assert response.status_code == 200
+    assert response.json() == {"status": "ok"}
```

실행은 예를 들어 다음처럼 하면 됩니다.

```bash
pip install -e ".[test]"
uvicorn app.main:app --reload
pytest
```

`GET /health`와 `GET /` 모두 `{"status": "ok"}`를 반환합니다.