Fixture path `/Users/hyun/Desktop/dddjango/none` does not exist, and `/private/tmp/dddjango-codex-eval` is empty. Since the sandbox is read-only, here is a minimal unified diff you can apply:

```diff
diff --git a/requirements.txt b/requirements.txt
new file mode 100644
index 0000000..f9b8c14
--- /dev/null
+++ b/requirements.txt
@@ -0,0 +1,2 @@
+fastapi
+uvicorn[standard]
diff --git a/app/main.py b/app/main.py
new file mode 100644
index 0000000..7e4f7f3
--- /dev/null
+++ b/app/main.py
@@ -0,0 +1,13 @@
+from fastapi import FastAPI
+
+
+app = FastAPI(title="Health Check API")
+
+
+@app.get("/health")
+def health_check() -> dict[str, str]:
+    return {"status": "ok"}
diff --git a/app/__init__.py b/app/__init__.py
new file mode 100644
index 0000000..e69de29
```

Run it with:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check endpoint:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```