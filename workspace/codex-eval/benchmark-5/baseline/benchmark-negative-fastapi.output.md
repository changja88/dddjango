지정된 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 현재 작업 디렉터리 `/private/tmp/dddjango-codex-eval`도 비어 있었습니다. 그래서 새 FastAPI health check 앱을 만드는 최소 diff를 제안합니다.

```diff
diff --git a/main.py b/main.py
new file mode 100644
index 0000000..7e94f89
--- /dev/null
+++ b/main.py
@@ -0,0 +1,11 @@
+from fastapi import FastAPI
+
+
+app = FastAPI(title="Health Check API")
+
+
+@app.get("/health")
+def health_check() -> dict[str, str]:
+    return {"status": "ok"}
+
+
diff --git a/pyproject.toml b/pyproject.toml
new file mode 100644
index 0000000..235f07f
--- /dev/null
+++ b/pyproject.toml
@@ -0,0 +1,17 @@
+[project]
+name = "health-check-api"
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
+testpaths = ["tests"]
diff --git a/tests/test_health.py b/tests/test_health.py
new file mode 100644
index 0000000..f0bcda2
--- /dev/null
+++ b/tests/test_health.py
@@ -0,0 +1,10 @@
+from fastapi.testclient import TestClient
+
+from main import app
+
+
+client = TestClient(app)
+
+
+def test_health_check_returns_ok() -> None:
+    response = client.get("/health")
+    assert response.status_code == 200
+    assert response.json() == {"status": "ok"}
```

실행은 다음처럼 하면 됩니다.

```bash
uvicorn main:app --reload
```

확인은 `GET /health`가 `{"status":"ok"}`를 반환하는지 보면 됩니다. 읽기 전용 sandbox라 테스트는 실행하지 않았습니다.