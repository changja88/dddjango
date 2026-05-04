작업 디렉터리가 비어 있고 현재 세션이 `read-only`라 파일 생성이 차단되어 실제 반영은 못 했습니다. 추가하려던 최소 구현은 아래와 같습니다.

`requirements.txt`
```txt
Flask==3.0.3
```

`app.py`
```python
from itertools import count

from flask import Flask, jsonify, request

app = Flask(__name__)

todos = []
todo_ids = count(1)


@app.post("/todos")
def create_todo():
    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required"}), 400

    todo = {
        "id": next(todo_ids),
        "title": title.strip(),
        "completed": False,
    }
    todos.append(todo)

    return jsonify(todo), 201


if __name__ == "__main__":
    app.run(debug=True)
```

실행:

```bash
pip install -r requirements.txt
python app.py
```

요청 예시:

```bash
curl -X POST http://127.0.0.1:5000/todos \
  -H 'Content-Type: application/json' \
  -d '{"title":"Buy milk"}'
```